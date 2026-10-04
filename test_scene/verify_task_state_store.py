# -*- coding: utf-8 -*-
"""阶段 4.7 回归：TaskStateStore（内存快照读写 + 推送 + 订阅）

覆盖：
1. 服务侧 `state` / `get_status` / `get_tasks_status` / `_sync_task_state` /
   `_update_task_status` / `_push_snapshot` 全部转发到 TaskStateStore（含 `state` 可整体替换）；
2. 快照读写：`sync_task_state` 写入的字段、`update_task_status` 改队列后同步快照；
3. 推送顺序：先回调既有构造参数 `on_snapshot`（WS 契约不变），再通知订阅者；
4. 订阅式接口：`subscribe_snapshot` / `unsubscribe_snapshot` / `subscribe_status` /
   `subscribe_task_state`，单个订阅者抛异常不影响其它订阅者与调度流程；
5. **懒加载 + `object.__new__` 兼容**：绕过 `__init__` 构造的服务也能取到 store/state
   （HEAVY 脚本 `verify_touch_residue_fix.py` 就是这种构造方式）。
"""
import logging
import sys
import types
import unittest
from pathlib import Path

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT))

from backend.core.scheduler.state import SchedulerState  # noqa: E402
from backend.services.scheduler import TaskStateStore  # noqa: E402
from backend.services.scheduler_service import SchedulerService  # noqa: E402


class _FakeQueue:
    """最小任务队列替身（只实现 update_task_status / get_task）"""

    def __init__(self, tasks=None):
        self.tasks = dict(tasks or {})

    def update_task_status(self, task_name: str, new_status: int) -> bool:
        task = self.tasks.get(task_name)
        if task is None:
            return False
        task.current_status = new_status
        return True

    def get_task(self, task_name: str):
        return self.tasks.get(task_name)


def _bare_service(tasks=None) -> SchedulerService:
    """用 object.__new__ 构造（与 HEAVY 脚本同款），只补 store 需要的最小依赖"""
    svc = object.__new__(SchedulerService)
    svc.logger = logging.getLogger("verify_task_state_store")
    svc.task_queue = _FakeQueue(tasks)
    return svc


class StoreWiringTest(unittest.TestCase):

    def test_service_forwards_to_store(self):
        svc = _bare_service()
        self.assertIsInstance(svc.task_state_store, TaskStateStore)
        self.assertIsInstance(svc.state, SchedulerState)
        # state 整体替换（既有测试写法）
        replacement = SchedulerState()
        replacement.set_running(True, 3, mode="once")
        svc.state = replacement
        self.assertIs(svc.state, replacement)
        self.assertIs(svc.task_state_store.state, replacement)
        self.assertEqual(svc.get_status()["mode"], "once")
        self.assertEqual(svc.get_status()["task_count"], 3)

    def test_store_owns_state_after_lazy_creation(self):
        svc = _bare_service()
        store = svc.task_state_store
        self.assertIs(store.state, svc.state)
        self.assertIs(svc.task_state_store, store, "同一实例（懒加载只创建一次）")

    def test_sync_and_update_task_status(self):
        task = types.SimpleNamespace(
            task_name="任务A", current_status=2, current_priority=5,
            base_priority=1, is_activated=True, next_execute_time=None)
        svc = _bare_service({"任务A": task})
        svc._sync_task_state(task)
        entry = svc.get_tasks_status()[0]
        self.assertEqual(entry["name"], "任务A")
        self.assertEqual(entry["status"], 2)
        self.assertEqual(entry["priority"], 5)
        self.assertEqual(entry["base_priority"], 1)
        self.assertTrue(entry["activated"])
        self.assertIsNone(entry["next_execute"])

        self.assertTrue(svc._update_task_status("任务A", 0))
        self.assertEqual(svc.get_tasks_status()[0]["status"], 0)
        self.assertFalse(svc._update_task_status("不存在", 0),
                         "队列里没有该任务时返回 False 且不写快照")

    def test_sync_formats_next_execute_time(self):
        from datetime import datetime
        task = types.SimpleNamespace(
            task_name="任务B", current_status=1, current_priority=0,
            base_priority=0, is_activated=False,
            next_execute_time=datetime(2026, 10, 4, 21, 30, 0))
        svc = _bare_service({"任务B": task})
        svc._sync_task_state(task)
        self.assertEqual(svc.get_tasks_status()[0]["next_execute"],
                         "2026-10-04 21:30:00")


class PushAndSubscribeTest(unittest.TestCase):

    def test_push_calls_legacy_callback_then_subscribers(self):
        svc = _bare_service()
        order = []
        svc.on_snapshot = lambda snap: order.append(("callback", snap["running"]))
        svc.task_state_store.subscribe_snapshot(
            lambda snap: order.append(("subscriber", snap["running"])))
        svc._push_snapshot()
        self.assertEqual(order, [("callback", False), ("subscriber", False)],
                         "必须先走既有 on_snapshot（WS 契约与顺序不变）")

    def test_subscriber_exception_does_not_break_others(self):
        svc = _bare_service()
        received = []
        svc.task_state_store.subscribe_snapshot(
            lambda snap: (_ for _ in ()).throw(RuntimeError("boom")))
        svc.task_state_store.subscribe_snapshot(
            lambda snap: received.append(snap))
        svc._push_snapshot()   # 不得抛出
        self.assertEqual(len(received), 1, "前一个订阅者异常不应影响后续订阅者")

    def test_unsubscribe_and_idempotent_subscribe(self):
        svc = _bare_service()
        received = []

        def _cb(snap):
            received.append(snap)

        svc.task_state_store.subscribe_snapshot(_cb)
        svc.task_state_store.subscribe_snapshot(_cb)   # 幂等
        svc._push_snapshot()
        self.assertEqual(len(received), 1)
        svc.task_state_store.unsubscribe_snapshot(_cb)
        svc._push_snapshot()
        self.assertEqual(len(received), 1, "退订后不再收到")

    def test_emit_status_and_task_state_dual_channel(self):
        svc = _bare_service()
        events = []
        svc.on_status_change = lambda s: events.append(("cb_status", s))
        svc.on_task_state_change = lambda t: events.append(("cb_task", t))
        svc.task_state_store.subscribe_status(lambda s: events.append(("sub_status", s)))
        svc.task_state_store.subscribe_task_state(lambda t: events.append(("sub_task", t)))
        svc.task_state_store.emit_status({"running": True})
        svc.task_state_store.emit_task_state({"name": "任务A", "status": 0})
        self.assertEqual([kind for kind, _ in events],
                         ["cb_status", "sub_status", "cb_task", "sub_task"])

    def test_mark_running_and_reset_tasks(self):
        svc = _bare_service()
        svc.task_state_store.mark_running(True, 4, mode="once")
        self.assertEqual(svc.get_status(),
                         {"running": True, "task_count": 4, "mode": "once"})
        svc.task_state_store.sync_task_state(types.SimpleNamespace(
            task_name="任务A", current_status=2))
        self.assertEqual(len(svc.get_tasks_status()), 1)
        svc.task_state_store.reset_tasks()
        self.assertEqual(svc.get_tasks_status(), [])


class SourceGuardTest(unittest.TestCase):
    """防回退：状态读写不应再散落在服务里直接操作 SchedulerState"""

    def setUp(self):
        self.src = (_PROJECT_ROOT / "backend" / "services"
                    / "scheduler_service.py").read_text(encoding="utf-8")

    def test_service_does_not_touch_state_internals(self):
        for forbidden in ("self.state.set_running(", "self.state.reset_tasks(",
                          "self.state.upsert_task(", "self.state.get_snapshot()"):
            self.assertNotIn(forbidden, self.src,
                             f"{forbidden} 应改为经 TaskStateStore")

    def test_service_keeps_forwarding_methods(self):
        for name in ("get_status", "get_tasks_status", "_sync_task_state",
                     "_update_task_status", "_push_snapshot"):
            self.assertIn(f"task_state_store.", self.src)
        self.assertIn("def task_state_store(self) -> TaskStateStore", self.src)
        self.assertIn("def state(self) -> \"SchedulerState\"", self.src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
