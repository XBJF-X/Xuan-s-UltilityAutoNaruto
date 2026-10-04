# -*- coding: utf-8 -*-
"""阶段 4 收尾回归：扫描循环的 `plan → execute(commands)` 拆分

`ScanLoop.scan()` 原先把"决策"与"执行"混在一段代码里（先改状态、再挑任务、再启动/抢占），
因此无法单独验证决策。现在拆成：

- `plan(now)`：**不改任何状态**，只返回命令列表
  （`mark_ready` / `start` / `preempt` / `notify_idle`）
- `execute(commands)`：依序落状态、记日志、回调、启动/抢占

等价性要点（本脚本重点覆盖）：
1. 本 tick 刚转就绪的任务**也会参与本轮挑选**（`plan` 用局部集合模拟状态迁移）；
2. `plan` 不得改动队列状态 / 不得调用 executor（纯决策）；
3. `execute` 的事件顺序：mark_ready → start/preempt → notify_idle；
4. 抢占用同样输入给出一致命令（由 `planner.should_preempt` 决定）。
"""
import logging
import sys
import types
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT))

from backend.services.scheduler.scan_loop import ScanLoop  # noqa: E402

NOW = datetime(2026, 10, 4, 21, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
LOG = logging.getLogger("verify_scan_plan_execute")


class _Task:
    def __init__(self, name, status=2, priority=10, activated=True,
                 next_execute_time=NOW - timedelta(minutes=1),
                 force_execute_now=False):
        self.task_name = name
        self.current_status = status
        self.current_priority = priority
        self.base_priority = priority
        self.is_activated = activated
        self.next_execute_time = next_execute_time
        self.force_execute_now = force_execute_now

    def __repr__(self):
        return f"<Task {self.task_name} st={self.current_status} p={self.current_priority}>"


class _Queue:
    """最小任务队列替身：按状态过滤 + 状态更新（模拟 heap.task_dic 行为）"""

    def __init__(self, tasks):
        self.tasks = {t.task_name: t for t in tasks}
        self.status_updates = []

    def get_tasks_by_status(self, status):
        return [t for t in self.tasks.values() if t.current_status == status]

    def update_task_status(self, task_name, new_status):
        task = self.tasks.get(task_name)
        if task is None:
            return False
        task.current_status = new_status
        self.status_updates.append((task_name, new_status))
        return True

    def get_task(self, task_name):
        return self.tasks.get(task_name)


class _Planner:
    """最小 TaskPlanner 替身：is_due 按 next_execute_time；pick_next 取优先级最小"""

    def __init__(self, preempt=False):
        self.preempt = preempt
        self.pick_calls = []

    def is_due(self, task, now):
        return bool(task.is_activated and task.next_execute_time
                    and task.next_execute_time <= now)

    def pick_next(self, ready_tasks):
        self.pick_calls.append(list(ready_tasks))
        if not ready_tasks:
            return None
        return min(ready_tasks, key=lambda t: t.current_priority)

    def should_preempt(self, running_task, next_task):
        return self.preempt


class _Executor:
    def __init__(self):
        self.started = []
        self.stopped = []

    def start_task(self, task):
        self.started.append(task.task_name)

    def stop_task(self, task, *args):
        self.stopped.append(task.task_name)


def _service(tasks, preempt=False, running_flag=True):
    svc = types.SimpleNamespace()
    svc.logger = LOG
    svc.running = running_flag
    svc.run_once = False
    svc.task_queue = _Queue(tasks)
    svc.planner = _Planner(preempt=preempt)
    svc.executor = _Executor()
    svc.on_task_state_change = None
    svc.idle_notified = []
    svc._notify_account_idle = lambda now: svc.idle_notified.append(now)
    svc._push_snapshot = lambda: None
    svc._update_task_status = svc.task_queue.update_task_status
    return svc


class PlanIsPureTest(unittest.TestCase):

    def test_plan_does_not_mutate_state(self):
        due = _Task("到点任务")
        svc = _service([due])
        loop = ScanLoop(svc)
        commands = loop.plan(NOW)
        self.assertEqual([c[0] for c in commands], ["mark_ready", "start", "notify_idle"])
        # 纯决策：状态、executor、通知都不该被触碰
        self.assertEqual(svc.task_queue.status_updates, [], "plan 不得修改队列状态")
        self.assertEqual(due.current_status, 2, "plan 不得改动任务状态")
        self.assertEqual(svc.executor.started, [])
        self.assertEqual(svc.executor.stopped, [])
        self.assertEqual(svc.idle_notified, [])

    def test_freshly_ready_task_participates_in_same_tick(self):
        """关键等价性：本 tick 刚转就绪的任务必须参与本轮挑选（否则会晚一个周期启动）"""
        fresh = _Task("刚就绪", status=2, priority=1)
        old_ready = _Task("早已就绪", status=1, priority=5)
        svc = _service([fresh, old_ready])
        loop = ScanLoop(svc)
        commands = loop.plan(NOW)
        pick_args = svc.planner.pick_calls[0]
        self.assertIn(fresh, pick_args, "刚转就绪的任务必须进入 pick_next 候选")
        self.assertIn(old_ready, pick_args)
        start = [c for c in commands if c[0] == "start"]
        self.assertEqual(len(start), 1)
        self.assertIs(start[0][1], fresh, "优先级更高的刚就绪任务应被选中")

    def test_not_due_task_produces_no_ready_command(self):
        not_due = _Task("未到点", status=2,
                        next_execute_time=NOW + timedelta(hours=1))
        svc = _service([not_due])
        commands = ScanLoop(svc).plan(NOW)
        self.assertEqual([c[0] for c in commands], ["notify_idle"])

    def test_preempt_command_when_running_task_exists(self):
        running = _Task("执行中", status=0, priority=10)
        ready = _Task("就绪", status=1, priority=1)
        svc = _service([running, ready], preempt=True)
        commands = ScanLoop(svc).plan(NOW)
        kinds = [c[0] for c in commands]
        self.assertIn("preempt", kinds)
        preempt = [c for c in commands if c[0] == "preempt"][0]
        self.assertIs(preempt[1], running)
        self.assertIs(preempt[2], ready)

    def test_no_preempt_when_planner_says_no(self):
        running = _Task("执行中", status=0, priority=1)
        ready = _Task("就绪", status=1, priority=9)
        svc = _service([running, ready], preempt=False)
        kinds = [c[0] for c in ScanLoop(svc).plan(NOW)]
        self.assertNotIn("preempt", kinds)
        self.assertNotIn("start", kinds, "有任务在执行时不得再启动")


class ExecuteAppliesCommandsTest(unittest.TestCase):

    def test_execute_event_order_and_effects(self):
        fresh = _Task("刚就绪", status=2, priority=1)
        svc = _service([fresh])
        loop = ScanLoop(svc)
        commands = loop.plan(NOW)
        loop.execute(commands)
        # 状态：2 → 1 → 0；执行层收到 start；空闲通知收到 now
        self.assertEqual(svc.task_queue.status_updates,
                         [("刚就绪", 1), ("刚就绪", 0)])
        self.assertEqual(svc.executor.started, ["刚就绪"])
        self.assertEqual(svc.idle_notified, [NOW])

    def test_execute_logs_queue_transitions(self):
        task = _Task("任务A", status=2, priority=3)
        svc = _service([task])
        loop = ScanLoop(svc)
        with self.assertLogs(LOG, level=logging.INFO) as cm:
            loop.execute(loop.plan(NOW))
        logs = "\n".join(cm.output)
        self.assertIn("进入就绪队列", logs)
        self.assertIn("进入执行队列", logs)

    def test_execute_reports_unknown_command(self):
        svc = _service([])
        with self.assertRaises(ValueError):
            ScanLoop(svc).execute([("不存在的命令", None)])

    def test_execute_preempt_stops_running_task(self):
        running = _Task("执行中", status=0, priority=10)
        ready = _Task("就绪", status=1, priority=1)
        svc = _service([running, ready], preempt=True)
        loop = ScanLoop(svc)
        loop.execute(loop.plan(NOW))
        self.assertEqual(svc.executor.stopped, ["执行中"])
        self.assertEqual(svc.executor.started, [], "抢占流程不启动新任务")


class ScanWiringTest(unittest.TestCase):

    def test_scan_uses_plan_then_execute(self):
        """scan() 必须走 plan→execute（源码级防回退：不得再内联三态逻辑）"""
        src = (_PROJECT_ROOT / "backend" / "services" / "scheduler"
               / "scan_loop.py").read_text(encoding="utf-8")
        self.assertIn("self.execute(self.plan(now))", src)
        self.assertIn("def plan(self, now: datetime)", src)
        self.assertIn("def execute(self, commands: list[tuple]) -> None", src)
        self.assertNotIn("# ---- 2. 就绪队列(1) → 执行(0) ----", src,
                         "旧的内联三态逻辑应已移入 plan/execute")

    def test_scan_still_guards_reentry_and_run_once(self):
        task = _Task("任务A", status=2)
        svc = _service([task])
        loop = ScanLoop(svc)
        loop.scanning = True
        loop.scan()
        self.assertEqual(svc.task_queue.status_updates, [], "重入时必须直接返回")
        loop.scanning = False
        svc.run_once = True
        called = []
        loop.scan_once = lambda: called.append(True)
        loop.scan()
        self.assertEqual(called, [True], "预设模式必须走 scan_once")

    def test_scan_resets_flag_on_error(self):
        svc = _service([])
        loop = ScanLoop(svc)
        loop.plan = lambda now: (_ for _ in ()).throw(RuntimeError("boom"))
        with self.assertRaises(RuntimeError):
            loop.scan()
        self.assertFalse(loop.scanning, "异常后防重入标志必须复位")


if __name__ == "__main__":
    unittest.main(verbosity=2)
