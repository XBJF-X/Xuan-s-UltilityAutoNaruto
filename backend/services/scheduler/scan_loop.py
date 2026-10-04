"""扫描循环（后台线程 + 一轮扫描的三态推进）

阶段 4.5：从 `SchedulerService`(1335 行) 抽出的第五块职责。

搬走：
- `start_scan_loop`（原 `_start_scan_loop`）：启动后台线程
- `run_loop`（原 `_scan_loop`）：按「扫描间隔」循环；间隔读取与换算**在 try 内**，
  非法值只降级为本轮默认等待，致命异常（BaseException）留痕并经
  `service._report_loop_death` 上报后退出
- `report_loop_death`（原 `_report_loop_death`）
- `scan`（原 `scan`）：等待队列(2) → 就绪队列(1) → 执行队列(0) 三态推进 + 抢占 + 空闲通知
- `scan_once`（原 `_scan_once`）：临时预设模式的顺序执行

本类持有 `scanning`（防重入标志）与 `thread`；服务侧以同名 property 暴露
（`_scanning` / `_scan_thread`）。`_lock` 仍由服务持有（`start()` / `stop()` 生命周期用）。

注意：`run_loop` 与 `scan_once` 需要回调服务方法（`service.scan()` /
`service._report_loop_death()` / `service._notify_preset_finished()` 等），
以保持"实例属性替换即可拦截"的既有测试/扩展点（`verify_phase0_hardening.py`
会替换 `sched._report_loop_death`）。
"""
from __future__ import annotations

import logging
import threading
import time
import traceback
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo


class ScanLoop:
    """后台扫描循环与单轮扫描"""

    def __init__(self, service: Any):
        self.service = service
        # 防重入标志：`scan()` 正在执行时再次进入直接返回（`activation_manager`
        # 会在任务完成回调里回调 `service.scan()`，靠此标志避免重入）
        self.scanning = False
        self.thread = None

    @property
    def logger(self) -> logging.Logger:
        return self.service.logger

    @property
    def config(self):
        return getattr(self.service, "config", None)

    # ---------------- 后台线程 ----------------

    def start_scan_loop(self) -> None:
        """启动后台扫描循环线程"""
        self.thread = threading.Thread(target=self.run_loop, daemon=True)
        self.thread.start()

    def run_loop(self) -> None:
        """后台扫描循环（和原版 Scheduler 一样持续循环，按间隔等待）

        健壮性：间隔的**读取与换算也在 try 内**。旧实现把它们放在 try 之外，用户把
        「扫描间隔」填成非数字时 `scan_interval / 1000.0` 会抛 TypeError 让扫描线程
        静默死亡——而 `running` 仍为 True，表现为"界面显示运行中、却永远不执行任务、
        无任何报错"。现在：非法间隔只降级为本轮默认等待；致命异常留痕 + 上报 + 停机。
        """
        service = self.service
        while service.running:
            try:
                service.scan()
                # 等待下一个扫描周期（用短循环代替 sleep 以支持快速退出）
                scan_interval = self.config.get_config("扫描间隔", 1000)
                try:
                    wait_time = max(0.1, float(scan_interval) / 1000.0)
                except (TypeError, ValueError):
                    self.logger.warning(
                        "扫描间隔配置非法（%r），本轮按默认 1000ms 处理", scan_interval)
                    wait_time = 1.0
                deadline = time.time() + wait_time
                while service.running and time.time() < deadline:
                    time.sleep(0.05)
            except Exception:
                self.logger.error("扫描异常:\n%s", traceback.format_exc())
            except BaseException:
                # 非 Exception 的致命异常（BaseException）绝不允许静默终结扫描循环；
                # 经服务方法上报，保持既有 monkeypatch 扩展点有效
                self.logger.error("扫描循环致命异常，调度器转为停止:\n%s",
                                  traceback.format_exc())
                service._report_loop_death("扫描循环")
                return

    def report_loop_death(self, loop_name: str) -> None:
        """后台循环因致命异常退出时置停机并上报，避免"显示运行中却永不干活"。"""
        service = self.service
        service.running = False
        self.logger.error("%s 已退出，调度器状态置为停止", loop_name)
        try:
            if service.on_status_change:
                service.on_status_change({
                    "running": False,
                    "task_count": len(service.task_queue.heap),
                    "error": f"{loop_name}异常退出，调度器已停止",
                })
        except Exception as e:
            # 上报失败不能再次抛出（否则异常会吞掉循环死亡的现场）
            self.logger.warning("上报 %s 异常退出失败: %s", loop_name, e)

    # ---------------- 单轮扫描 ----------------

    def scan(self) -> None:
        """改进的扫描方法，避免快速重入（与原版 scan 逻辑一致）"""
        service = self.service
        if not service.running:
            return
        if self.scanning:
            return

        self.scanning = True
        try:
            if service.run_once:
                self.scan_once()
                return
            # ---- 1. 扫描等待队列(2) → 就绪队列(1) ----
            waiting_tasks = service.task_queue.get_tasks_by_status(2)
            now = datetime.now(ZoneInfo("Asia/Shanghai"))
            for task in waiting_tasks:
                # TaskPlanner 纯逻辑判断：已启用且下次执行时间已到
                if not service.planner.is_due(task, now):
                    continue
                if service._update_task_status(task.task_name, 1):
                    self.logger.info(
                        f"[{task.task_name}]-[{task.base_priority}] 进入就绪队列"
                    )

            # ---- 2. 就绪队列(1) → 执行(0) ----
            ready_tasks = service.task_queue.get_tasks_by_status(1)
            # TaskPlanner 选择：优先立即执行标记，否则按优先级取最高
            next_task = service.planner.pick_next(ready_tasks)
            if next_task is not None:
                running_tasks = service.task_queue.get_tasks_by_status(0)
                if not running_tasks:
                    # 没有正在执行的任务 → 直接执行。
                    # 注意：不在进入执行队列时清除 force_execute_now（"立即执行"）标记，
                    # 标记保留到任务完成回调统一清除——使 should_preempt 能识别
                    # "立即执行启动"的任务，保护其不被普通任务抢占（见 TaskPlanner）。
                    if service._update_task_status(next_task.task_name, 0):
                        self.logger.info(
                            f"[{next_task.task_name}]-[{next_task.base_priority}] 进入执行队列"
                        )
                        if service.on_task_state_change:
                            service.on_task_state_change({
                                "name": next_task.task_name,
                                "status": 0,
                                "action": "start",
                            })
                        # 通过执行层启动：接管超时监视器 + 开始执行线程
                        service.executor.start_task(next_task)
                        service._push_snapshot()
                else:
                    # 有正在执行的任务 → 检查抢占（更高优先级，或被选中的任务带"立即执行"标记）
                    running_task = running_tasks[0]
                    if service.planner.should_preempt(running_task, next_task):
                        self.logger.info(
                            f"[{running_task.task_name}] 被 [{next_task.task_name}] 抢占"
                        )
                        # 执行层停止被抢占任务（交还超时监视器 + 停止线程）
                        service.executor.stop_task(running_task)

            # ---- 3. 空闲判定：执行告一段落时通知用户（仅账号配置模式）----
            service._notify_account_idle(now)
        finally:
            self.scanning = False

    def scan_once(self) -> None:
        """临时预设模式：按任务执行顺序逐一执行，失败/超时也跳过继续，全部跑完后自动关闭调度器"""
        service = self.service
        if service.task_queue.get_tasks_by_status(0):
            return  # 当前有任务在执行，等待其结束

        while service.preset_runner.has_pending():
            task_name = service.preset_runner.pop_next()
            task = service.task_queue.get_task(task_name)
            if task is None:
                continue
            if not task.is_activated:
                self.logger.info(f"预设任务未勾选，跳过: {task_name}")
                continue
            # 预设任务按顺序立即执行：置位"忽略时间窗口"标记（不走窗口校验）
            task.ignore_time_window = True
            if task.current_status == 2:
                service._update_task_status(task_name, 1)
            if task.current_status == 1:
                service._update_task_status(task_name, 0)
                task.force_execute_now = False  # 预设顺序执行，无需立即执行标记
                self.logger.info(f"[预设顺序执行] 开始任务: {task_name}")
                if service.on_task_state_change:
                    service.on_task_state_change({
                        "name": task_name,
                        "status": 0,
                        "action": "start",
                    })
                service.executor.start_task(task)
                service._push_snapshot()
            return

        # 待执行列表耗尽 → 通知用户后自动关闭调度器
        if service.running:
            self.logger.info("预设任务全部执行完毕，自动关闭调度器")
            service._notify_preset_finished()
            threading.Thread(target=service.stop,
                             kwargs={"reason": "预设任务全部执行完毕"},
                             daemon=True).start()
