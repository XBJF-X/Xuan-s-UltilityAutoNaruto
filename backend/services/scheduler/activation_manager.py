"""激活管理（临时启用登记/恢复、启用切换、手动执行窗口预检）

阶段 4.4a：从 `SchedulerService`(1476 行) 抽出的第四块职责。

本步搬走"临时启用"这一族逻辑：
- `ensure_runnable`（原 `_ensure_task_runnable`）：原本未启用的任务被跨任务激活时临时启用并登记
- `restore_one`（原 `_restore_temp_activation`）：任务执行结束后恢复原激活状态
- `restore_all`（原 `_restore_all_temp_activations`）：调度器停机时按登记整体恢复
- `toggle`（原 `toggle_task_activation`）：用户手动启用/禁用（会清除登记）
- `reject_manual_execute_outside_window`（原 `_reject_manual_execute_outside_window`）：
  手动「执行」的窗口预检

状态 `_temp_activated_tasks` 由本类持有；服务侧以同名 property（含 setter）暴露，
既有 6 处读写点与测试的直接赋值（`svc._temp_activated_tasks = {}`）继续有效。
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from backend.services.scheduler.constants import SOURCE_ACTIVATION


class ActivationManager:
    """临时启用登记与手动执行窗口预检"""

    def __init__(self, service: Any):
        self.service = service
        # 跨任务临时启用登记：{任务名: 激活前是否已启用}
        # 仅登记"原本未激活、被其他任务临时启用"的任务，执行结束后恢复其原状态
        self.temp_activated_tasks: Dict[str, bool] = {}
        # 待激活任务列表：任务执行期间通过 on_task_activate_request 登记，
        # 待当前任务结束后（服务侧 `_execute_done_callback`）统一激活并立即执行，
        # 避免在任务执行线程中直接激活对扫描循环时序的依赖（更稳定）
        self.pending_activate_tasks: List[str] = []

    @property
    def logger(self) -> logging.Logger:
        return self.service.logger

    @property
    def config(self):
        return getattr(self.service, "config", None)

    # ---------------- 临时启用 ----------------

    def ensure_runnable(self, task_name: str) -> bool:
        """确保任务可被调度：原本未启用时临时启用并登记，执行结束后恢复原状态。

        仅"本次因跨任务激活而启用"的任务会被登记（原本已启用则不做任何改动）。

        Returns:
            bool: 本次是否执行了临时启用
        """
        if self.config.get_task_base_config(task_name, "是否启用", False):
            return False
        self.config.set_task_base_config(task_name, "是否启用", True)
        # 记录原状态（False=未激活），供任务结束后恢复
        self.temp_activated_tasks[task_name] = False
        self.logger.info(
            f"{task_name} 原为未激活，已临时启用（任务执行结束后恢复原状态）")
        return True

    def restore_one(self, task) -> None:
        """被跨任务激活的任务执行结束后，恢复其激活前的状态。

        仅处理登记过的任务（原本未激活 → 恢复未激活）；原本已启用的任务不受影响，
        用户中途手动启用（toggle）会清除登记，同样不会被恢复。
        """
        service = self.service
        task_name = task.task_name
        if task_name not in self.temp_activated_tasks:
            return
        originally_activated = self.temp_activated_tasks.pop(task_name)
        if originally_activated:
            return
        if self.config.config_type == "临时":
            # 临时预设模式不持久化启用状态，避免污染预设文件
            self.logger.info(
                f"[{task_name}] 执行结束，当前为临时预设模式，不写回启用状态")
            return
        self.config.set_task_base_config(task_name, "是否启用", False)
        task.force_execute_now = False
        if getattr(task, "current_status", 2) != 2:
            # 兜底：避免任务停留在就绪队列导致后续仍被扫描到
            service._update_task_status(task_name, 2)
        service._sync_task_state(task)
        self.logger.info(f"[{task_name}] 执行结束，已恢复为未激活状态")

    def restore_all(self) -> None:
        """停机时恢复全部"临时启用"任务的原激活状态（清空登记）。

        与 `restore_one` 的区别：这里不依赖任务对象（调度器停机后队列已被清空/
        任务线程正在收尾），只按登记写回配置并同步快照；临时预设模式
        （`config_type == "临时"`）不写盘，避免污染预设文件。
        """
        service = self.service
        if not self.temp_activated_tasks:
            return
        pending = dict(self.temp_activated_tasks)
        self.temp_activated_tasks.clear()
        if self.config.config_type == "临时":
            self.logger.info(
                "调度器停止：临时预设模式，不写回以下任务的启用状态：%s",
                list(pending))
            return
        restored: list[str] = []
        for task_name, originally_activated in pending.items():
            if originally_activated:
                # 原本就是启用的（不应出现，登记只记录"原本未激活"）→ 保持不动
                continue
            self.config.set_task_base_config(task_name, "是否启用", False)
            task = service.task_queue.get_task(task_name)
            if task is not None:
                task.force_execute_now = False
                if getattr(task, "current_status", 2) != 2:
                    service._update_task_status(task_name, 2)
                service._sync_task_state(task)
            restored.append(task_name)
        if restored:
            self.logger.info(
                "调度器停止：已把临时启用的任务恢复为未激活（原为未勾选）：%s", restored)

    # ---------------- 用户手动启用/禁用 ----------------

    def toggle(self, task_name: str, state: bool) -> None:
        """切换启用/禁用（与原版 toggle_task_activation 一致）"""
        service = self.service
        self.config.set_task_base_config(task_name, "是否启用", state)
        # 用户手动设置优先：清除临时启用登记，避免任务结束后又被恢复为未激活
        self.temp_activated_tasks.pop(task_name, None)
        temp_task = service.task_queue.get_task(task_name)
        if temp_task:
            if not state and temp_task.current_status == 0:
                service.executor.stop_task(temp_task)
                service._update_task_status(task_name, 2)
            self.logger.info(f"任务 {task_name} {'已启用' if state else '已禁用'}")
            service._sync_task_state(temp_task)
        if service.on_task_state_change:
            service.on_task_state_change({"name": task_name, "activated": state})
        service._push_snapshot()

    # ---------------- 待激活登记与调度（阶段 4.4b） ----------------

    def on_task_activate_request(self, task_name: str, next_execute_time=None) -> None:
        """其他任务请求激活指定任务。

        两种方式（由 next_execute_time 区分）：
        - 不传时间：登记到待激活列表，当前任务结束后统一激活并立即执行（原行为）；
        - 传时间：只把该任务的下次执行时间设为指定时刻（未启用时临时启用），
          当前任务不需要停留等待，到点后由扫描循环自然执行。

        登记式激活的原因：原先在执行线程中直接 execute_task_now，完全依赖扫描循环时序
        去捡起该任务（扫描可能恰好错过、且抢占判断可能将其延后），鲁棒性不足；临时预设
        模式下扫描只遍历预设列表，被激活的临时任务甚至永远不会执行。改为登记后在任务
        完成回调中统一处理，时机确定、无需与扫描线程竞争。
        """
        if next_execute_time is not None:
            self.schedule_task_activation(task_name, next_execute_time)
            return
        if task_name not in self.pending_activate_tasks:
            self.pending_activate_tasks.append(task_name)
            self.logger.info(f"{task_name} 已登记待激活（当前任务结束后立即执行）")
        else:
            self.logger.debug(f"{task_name} 已在待激活列表中，忽略重复激活请求")

    def schedule_task_activation(self, task_name: str, next_execute_time) -> None:
        """指定被激活任务的下次执行时间（不登记立即执行，当前任务无需停留等待）。"""
        service = self.service
        if next_execute_time.tzinfo is None:
            next_execute_time = next_execute_time.replace(
                tzinfo=ZoneInfo("Asia/Shanghai"))
        task = service.task_queue.get_task(task_name)
        if task is None:
            self.logger.warning(
                f"被激活任务 {task_name} 不在任务队列中，仅写入下次执行时间")
        # 未启用的任务会被扫描循环跳过（TaskPlanner.is_due 要求 is_activated），
        # 需临时启用才能到点执行；执行结束后会恢复原状态
        self.ensure_runnable(task_name)
        self.config.set_task_base_config(task_name, "下次执行时间",
                                        int(next_execute_time.timestamp()))
        self.logger.info(
            f"{task_name} 已指定下次执行时间："
            f"{next_execute_time.strftime('%Y-%m-%d %H:%M:%S')}"
            "（当前任务无需等待，到点自动执行）")
        if task is not None:
            service._sync_task_state(task)
        service._push_snapshot()
        # 指定时间已到/已过：立即触发一次扫描，让它尽快进入执行
        if next_execute_time <= datetime.now(ZoneInfo("Asia/Shanghai")):
            service.scan()

    def process_pending_activations(self) -> None:
        """任务结束回调中处理待激活列表：激活登记的任务并立即尝试启动。"""
        service = self.service
        if not self.pending_activate_tasks:
            return
        pending = list(self.pending_activate_tasks)
        self.pending_activate_tasks.clear()
        now = datetime.now(ZoneInfo("Asia/Shanghai"))
        for task_name in pending:
            task = service.task_queue.get_task(task_name)
            if task is None:
                self.logger.warning(f"待激活任务 {task_name} 不在任务队列中，忽略")
                continue
            # 窗口守卫：目标任务的可执行窗口已过期时不激活（否则会被临时启用并空转到
            # 最长执行时长，期间调度器无法执行其它任务，见 skip_expired_activation）
            if self.skip_expired_activation(task, now):
                continue
            service.execute_task_now(task_name, enable_if_needed=True,
                                     source=SOURCE_ACTIVATION)
            if service.run_once:
                # 临时预设模式：被激活任务插入待执行列表最前，下一轮扫描优先执行
                service.preset_runner.move_to_front(task_name)
        # 同步扫描一次：让被激活任务立即进入执行（_scanning 标志防重入，
        # 若扫描线程正在扫描则本次返回，由下一轮扫描兜底）
        service.scan()

    def skip_expired_activation(self, task, now: datetime) -> bool:
        """跨任务"立即激活"前的窗口守卫：目标任务当前不可执行则跳过激活。

        【要塞争夺战/天地战场】执行结束（含超窗口/超最长时长被强制结束）后会自动
        激活【叛忍来袭】，而"立即执行/被激活"按设计会跳过窗口校验
        （`BaseTask._should_skip_window_check`）。若这两个任务自己就拖到了叛忍窗口
        （周三 21:00~22:00 / 周六 20:00~21:00）之后，照旧激活会让叛忍来袭被临时启用
        并带着执行意图空转——游戏里已无叛忍入口，任务会一直重试到最长执行时长
        （45 分钟），期间调度器无法执行其它任务（表现为"卡死"）。

        因此这里先用 `BaseTask.probe_execute_window(now)` 探测目标任务的排期窗口：
        不在窗口内（已过期 / 还没开始）→ 不启用、不登记立即执行，交由任务自身的排期
        在下一个周期处理，并记一条 WARNING 说明原因。

        Returns:
            bool: True 表示因窗口不可执行跳过了本次激活
        """
        probe = getattr(task, "probe_execute_window", None)
        if not callable(probe):
            return False
        try:
            runnable, state = probe(now)
        except Exception as e:
            # 排期计算异常（任务参数/资源缺失等）不应阻断激活：留痕后按原行为继续
            self.logger.warning(
                f"探测 {task.task_name} 可执行窗口失败，按原行为激活: {e}")
            return False
        if runnable:
            return False
        self.logger.warning(
            f"[{task.task_name}] {state}"
            f"（{getattr(task, 'schedule_description', '未知排期')}），"
            "跳过本次激活（不启用、不立即执行）")
        return True

    # ---------------- 手动执行窗口预检 ----------------

    def reject_manual_execute_outside_window(self, task) -> Optional[dict]:
        """手动「执行」的窗口预检：不在可执行窗口内 → 返回拒绝结果（可执行则返回 None）。

        与跨任务激活守卫（`_skip_expired_activation`）同源：都用
        `BaseTask.probe_execute_window(now)`（窗口基准取 now，而不是陈旧的 last_run_time）。
        区别在于这里**返回原因**给前端提示，并允许用户二次确认后带 `ignore_window=True`
        强制执行；拒绝时绝不改动任务状态（不写下次执行时间 / 不置 force / 不启用）。

        探测不可用（旧任务对象无该接口）或抛异常（排期计算异常）时不阻断执行，只留痕。
        """
        probe = getattr(task, "probe_execute_window", None)
        if not callable(probe):
            return None
        try:
            runnable, state = probe(datetime.now(ZoneInfo("Asia/Shanghai")))
        except Exception as e:
            self.logger.warning(
                f"探测 {task.task_name} 可执行窗口失败，按原行为立即执行: {e}")
            return None
        if runnable:
            return None
        schedule = getattr(task, "schedule_description", "") or None
        self.logger.warning(
            f"[{task.task_name}] 手动立即执行被拒绝：{state}"
            f"（{schedule or '未知排期'}）→ 当前不在可执行窗口内")
        return {
            "ok": False,
            "reason": f"{state}，当前不在可执行窗口内（如需强行执行请选择「强制执行」）",
            "window_state": state,
            "schedule": schedule,
        }
