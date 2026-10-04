"""任务状态存储（`SchedulerState` 门面 + 快照订阅）

阶段 4.7：从 `SchedulerService`(1063 行) 抽出的第七块职责 —— 内存状态快照与它的读/写/推送。

搬走：
- `get_status` / `get_tasks_status`（O(1) 读快照，供 API）
- `sync_task_state`（原 `_sync_task_state`）
- `update_task_status`（原 `_update_task_status`：改队列状态后同步快照）
- `push_snapshot`（原 `_push_snapshot`：推完整快照给前端 WS）
- 持有 `SchedulerState` 实例

订阅化：除保留服务构造参数 `on_snapshot`（API 层传 `sync_on_snapshot`，既有契约不变）外，
本类额外提供 `subscribe_snapshot` / `unsubscribe_snapshot`（以及 status / task_state 两个
订阅位），让"谁关心状态变化"从"服务构造函数参数"变成可增删的订阅关系；
`push_snapshot` 先回调 `service.on_snapshot`（保持既有行为与顺序），再通知订阅者。

`SchedulerState` 仍是"状态真相"（`core/scheduler/state.py`，读写带锁）；本类不复制字段。
"""
from __future__ import annotations

import logging
from typing import Any, Callable, List, Optional

from backend.core.scheduler.state import SchedulerState


class TaskStateStore:
    """调度器内存状态（快照读写 + 推送 + 订阅）"""

    def __init__(self, service: Any, state: Optional[SchedulerState] = None):
        self.service = service
        self.state: SchedulerState = state if state is not None else SchedulerState()
        self._snapshot_subscribers: List[Callable[[dict], None]] = []
        self._status_subscribers: List[Callable[[dict], None]] = []
        self._task_state_subscribers: List[Callable[[dict], None]] = []

    @property
    def logger(self) -> logging.Logger:
        return self.service.logger

    # ---------------- 读（API 直读快照，O(1)） ----------------

    def get_status(self) -> dict:
        # 直接读内存快照（O(1)，不遍历队列/不读 config）
        return self.state.get_status()

    def get_tasks_status(self) -> list[dict]:
        # 直接读内存快照（O(1)，不遍历 heap/不读 config）
        return self.state.get_tasks()

    def get_snapshot(self) -> dict:
        return self.state.get_snapshot()

    # ---------------- 写（状态变更时同步快照） ----------------

    def sync_task_state(self, task) -> None:
        """把任务对象的关键字段写入内存快照。"""
        next_execute = getattr(task, "next_execute_time", None)
        self.state.upsert_task(
            task.task_name,
            status=getattr(task, "current_status", 2),
            priority=getattr(task, "current_priority", 0),
            base_priority=getattr(task, "base_priority", 0),
            activated=bool(getattr(task, "is_activated", False)),
            next_execute=next_execute.strftime("%Y-%m-%d %H:%M:%S")
            if next_execute else None,
        )

    def update_task_status(self, task_name: str, new_status: int) -> bool:
        """更新队列中的任务状态并同步到内存快照。"""
        ok = self.service.task_queue.update_task_status(task_name, new_status)
        if ok:
            task = self.service.task_queue.get_task(task_name)
            if task:
                self.sync_task_state(task)
        return ok

    def mark_running(self, running: bool, task_count: int = 0,
                     mode: str = "persistent") -> None:
        """调度器启停时更新"运行中"标志（原 `service.state.set_running(...)`）"""
        self.state.set_running(running, task_count=task_count, mode=mode)

    def reset_tasks(self) -> None:
        """清空任务快照（调度器停止时）"""
        self.state.reset_tasks()

    # ---------------- 推送与订阅 ----------------

    def push_snapshot(self) -> None:
        """推送完整状态快照到前端（WS scheduler_snapshot，前端据此零轮询）。

        顺序：先回调服务构造参数里的 `on_snapshot`（既有 WS 契约与顺序），再通知订阅者。
        """
        snapshot = self.state.get_snapshot()
        callback = getattr(self.service, "on_snapshot", None)
        if callback:
            callback(snapshot)
        for subscriber in list(self._snapshot_subscribers):
            try:
                subscriber(snapshot)
            except Exception as e:
                # 单个订阅者异常不得影响调度循环与其它订阅者
                self.logger.warning(f"快照订阅者回调失败（继续其它订阅者）: {e}")

    def subscribe_snapshot(self, callback: Callable[[dict], None]) -> Callable[[dict], None]:
        """订阅完整快照（返回 callback 便于链式/幂等注册）"""
        if callback not in self._snapshot_subscribers:
            self._snapshot_subscribers.append(callback)
        return callback

    def unsubscribe_snapshot(self, callback: Callable[[dict], None]) -> None:
        if callback in self._snapshot_subscribers:
            self._snapshot_subscribers.remove(callback)

    def subscribe_status(self, callback: Callable[[dict], None]) -> Callable[[dict], None]:
        """订阅"运行状态"变化（原 `service.on_status_change` 的订阅式替代）"""
        if callback not in self._status_subscribers:
            self._status_subscribers.append(callback)
        return callback

    def subscribe_task_state(self, callback: Callable[[dict], None]) -> Callable[[dict], None]:
        """订阅单个任务状态变化（原 `service.on_task_state_change` 的订阅式替代）"""
        if callback not in self._task_state_subscribers:
            self._task_state_subscribers.append(callback)
        return callback

    def emit_status(self, status: dict) -> None:
        """转发"运行状态"事件：先走既有 `service.on_status_change`，再通知订阅者"""
        callback = getattr(self.service, "on_status_change", None)
        if callback:
            callback(status)
        self._emit(self._status_subscribers, status, "运行状态")

    def emit_task_state(self, task_data: dict) -> None:
        """转发"任务状态"事件：先走既有 `service.on_task_state_change`，再通知订阅者"""
        callback = getattr(self.service, "on_task_state_change", None)
        if callback:
            callback(task_data)
        self._emit(self._task_state_subscribers, task_data, "任务状态")

    def _emit(self, subscribers: List[Callable[[dict], None]], payload: dict,
              kind: str) -> None:
        for subscriber in list(subscribers):
            try:
                subscriber(payload)
            except Exception as e:
                self.logger.warning(f"{kind}订阅者回调失败（继续其它订阅者）: {e}")
