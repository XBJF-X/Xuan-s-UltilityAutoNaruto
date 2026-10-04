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
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo


class ActivationManager:
    """临时启用登记与手动执行窗口预检"""

    def __init__(self, service: Any):
        self.service = service
        # 跨任务临时启用登记：{任务名: 激活前是否已启用}
        # 仅登记"原本未激活、被其他任务临时启用"的任务，执行结束后恢复其原状态
        self.temp_activated_tasks: Dict[str, bool] = {}

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
