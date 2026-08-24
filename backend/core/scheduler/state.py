"""SchedulerState - 调度器内存状态快照

由调度器在状态变更时更新，API 层 get_status / get_tasks_status 直接读取快照（O(1)），
WS 层据此推送 scheduler_snapshot 给前端（前端零轮询）。
"""
import threading
from typing import Optional


class SchedulerState:
    """调度器运行状态与任务列表的内存快照（线程安全）。"""

    def __init__(self):
        self._lock = threading.Lock()
        self._running = False
        self._mode = "persistent"  # persistent（持久配置）/ once（临时预设）
        self._task_count = 0
        self._tasks: dict[str, dict] = {}

    # ---- 写 ----

    def set_running(self, running: bool, task_count: int = 0,
                    mode: str = "persistent"):
        with self._lock:
            self._running = running
            if running:
                self._task_count = task_count
                self._mode = mode

    def upsert_task(self, name: str, **fields):
        """新增或更新单个任务的状态字段。"""
        with self._lock:
            entry = self._tasks.setdefault(name, {"name": name})
            entry.update(fields)

    def remove_task(self, name: str):
        with self._lock:
            self._tasks.pop(name, None)

    def reset_tasks(self):
        with self._lock:
            self._tasks.clear()

    # ---- 读 ----

    def get_status(self) -> dict:
        with self._lock:
            return {
                "running": self._running,
                "task_count": self._task_count,
                "mode": self._mode,
            }

    def get_tasks(self) -> list[dict]:
        with self._lock:
            return list(self._tasks.values())

    def get_snapshot(self) -> dict:
        """合并 status + tasks 的完整快照，供 WS scheduler_snapshot 一次推送。"""
        with self._lock:
            return {
                "running": self._running,
                "mode": self._mode,
                "task_count": self._task_count,
                "tasks": list(self._tasks.values()),
            }
