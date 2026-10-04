# -*- coding: utf-8 -*-
"""验证"立即执行"任务能抢夺正在运行任务的执行机会。

背景：触发立即执行（用户手动 / 任务结束后激活另一任务）后，
调度器仅更新了任务的 next_execute_time 并打上 force_execute_now 标记；
但 scan() 的抢占判断 should_preempt 只看优先级，未考虑 force_execute_now，
导致正在运行的高/同级优先级任务不会被立即执行任务抢占——立即执行形同虚设。

修复（两部分）：
1. should_preempt 被选中的任务带 force_execute_now（"立即执行"请求）时，
   优先抢占正在运行的任务；
2. force_execute_now 标记保留到任务完成回调才清除（进入执行队列不清除），
   且正在运行的任务带该标记时普通任务不得抢占——避免"立即执行"刚启动就被
   更高优先级普通任务打断（如：消耗体力被激活执行后又被排行榜点赞抢占）。

本脚本覆盖：
1. should_preempt 单元级：force 抢占 / 非 force 按优先级 / 双 force 按优先级 /
   force 运行中保护（普通任务不得抢占）；
2. scan 集成级：任务 H 运行中，低优先级任务 L 被"立即执行" → L 必须抢占 H；
   force 任务执行中不被普通高优先级任务抢占；
3. 回归：非 force 的低优先级就绪任务不得抢占正在运行的高优先级任务；
4. 回归：无任务运行时 force 任务仍被 pick_next 优先选择并执行（force 标记保留至完成）。
"""
import datetime
import json
import logging
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from zoneinfo import ZoneInfo

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

_TZ = ZoneInfo("Asia/Shanghai")


class _FakeTask:
    """最小可入队任务：支持 is_due / pick_next / should_preempt / scan 全流程。"""

    def __init__(self, name, priority, *, activated=True,
                 next_execute_time=None, force=False):
        self.task_name = name
        self.base_priority = priority
        self.click_priority = priority
        self.bool_click = False
        self.current_status = 2  # 2=等待, 1=就绪, 0=执行
        self.is_activated = activated
        self.is_temp = False
        self.force_execute_now = force
        self.last_execute_error = None
        self.last_run_time = datetime.datetime.now(_TZ)
        self.create_time = datetime.datetime.now(_TZ)
        # 默认未来很久 → 仅当显式传入 next_execute_time 时才"到期"
        self.next_execute_time = (next_execute_time
                                  or datetime.datetime.now(_TZ)
                                  + datetime.timedelta(days=1))
        self.stopped = False
        self.run_called = False

    @property
    def current_priority(self):
        return self.click_priority if self.bool_click else self.base_priority

    def __lt__(self, other):
        if self.current_priority != other.current_priority:
            return self.current_priority < other.current_priority
        return self.create_time < other.create_time

    def __repr__(self):
        return (f"<{self.task_name} p={self.current_priority} "
                f"s={self.current_status} f={self.force_execute_now}>")

    def run(self):
        self.run_called = True

    def stop(self):
        self.stopped = True

    @staticmethod
    def _now():
        return datetime.datetime.now(_TZ)


def _make_scheduler():
    """构建一个 SchedulerService（持久配置），任务队列由测试自行入队。"""
    import backend.services.settings_service as ss_mod
    from backend.core.setting_model import Setting

    tmp = tempfile.mkdtemp(prefix="xuan_verify_preempt_")
    ini_path = Path(tmp) / "setting.ini"
    ini_path.write_text("[助手设置]\r\n", encoding="utf-8")
    setting = Setting(parent_logger=logging.getLogger("verify"),
                      setting_path=ini_path)
    orig = ss_mod.SettingsService._get_setting
    ss_mod.SettingsService._get_setting = lambda self: setting

    cfg_path = Path(tmp) / "Config_Test.json"
    cfg_path.write_text(json.dumps({
        "配置文件版本": "V3",
        "用户名": "verify_user",
        "配置类型": "持久",
        "任务": {
            "任务H": {"是否启用": True, "下次执行时间": 0, "是否临时": False,
                      "基础优先级": 1, "连点优先级": 1, "类型": 0,
                      "执行参数": {}, "执行进度": {}},
            "任务L": {"是否启用": True, "下次执行时间": 0, "是否临时": False,
                      "基础优先级": 10, "连点优先级": 10, "类型": 0,
                      "执行参数": {}, "执行进度": {}},
        },
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    from backend.core.config_model import Config
    from backend.services.scheduler_service import SchedulerService
    cfg = Config(parent_logger=logging.getLogger("verify"),
                 config_path=cfg_path)
    sched = SchedulerService(config=cfg)
    sched.running = True
    sched.run_once = False
    # 通知为外部副作用（Windows Toast）：测试中屏蔽，避免弹窗与不必要的进程
    sched._notify_user = lambda title, message: None
    return sched, tmp, orig, ss_mod


class ShouldPreemptUnitTest(unittest.TestCase):
    """TaskPlanner.should_preempt 单元级验证。"""

    def setUp(self):
        from backend.core.scheduler.planner import TaskPlanner
        self.planner = TaskPlanner()

    def test_force_task_preempts_running_higher_priority(self):
        """运行中高优先级任务，被低优先级"立即执行"任务抢占（本次修复核心）。"""
        running = _FakeTask("运行中-高优先级", priority=1, force=False)
        candidate = _FakeTask("立即执行-低优先级", priority=10, force=True)
        self.assertTrue(self.planner.should_preempt(running, candidate))

    def test_force_task_preempts_running_lower_priority(self):
        """运行中低优先级任务，被高优先级"立即执行"任务抢占。"""
        running = _FakeTask("运行中-低优先级", priority=10, force=False)
        candidate = _FakeTask("立即执行-高优先级", priority=1, force=True)
        self.assertTrue(self.planner.should_preempt(running, candidate))

    def test_non_force_keeps_priority_semantics(self):
        """无立即执行标记：仅更高优先级才抢占（回归原逻辑）。"""
        # 运行中高优先级(1) vs 就绪低优先级(10)：不抢占
        running = _FakeTask("运行中-高", priority=1, force=False)
        candidate = _FakeTask("就绪-低", priority=10, force=False)
        self.assertFalse(self.planner.should_preempt(running, candidate))
        # 运行中低优先级(10) vs 就绪高优先级(1)：抢占
        running = _FakeTask("运行中-低", priority=10, force=False)
        candidate = _FakeTask("就绪-高", priority=1, force=False)
        self.assertTrue(self.planner.should_preempt(running, candidate))

    def test_both_force_compares_by_priority(self):
        """两个任务都带立即执行标记时按优先级比较，避免互相无脑打断。"""
        # 运行中也是 force(1)，候选 force(10)：不抢占（避免连环打断）
        running = _FakeTask("运行中-force高", priority=1, force=True)
        candidate = _FakeTask("候选-force低", priority=10, force=True)
        self.assertFalse(self.planner.should_preempt(running, candidate))
    def test_force_running_protected_from_normal_preempt(self):
        """立即执行任务运行中：普通（无标记）更高优先级任务不得抢占它。"""
        running = _FakeTask("运行中-立即执行低优先级", priority=10, force=True)
        candidate = _FakeTask("就绪-普通高优先级", priority=1, force=False)
        self.assertFalse(self.planner.should_preempt(running, candidate),
                         "立即执行任务执行中不应被普通高优先级任务抢占")

    def test_force_running_protected_from_normal_same_priority(self):
        """立即执行任务运行中：普通同级任务也不得抢占。"""
        running = _FakeTask("运行中-立即执行", priority=5, force=True)
        candidate = _FakeTask("就绪-普通同级", priority=5, force=False)
        self.assertFalse(self.planner.should_preempt(running, candidate))


        # 运行中 force(10)，候选 force(1)：抢占
        running = _FakeTask("运行中-force低", priority=10, force=True)
        candidate = _FakeTask("候选-force高", priority=1, force=True)
        self.assertTrue(self.planner.should_preempt(running, candidate))

class ScanPreemptIntegrationTest(unittest.TestCase):
    """scan() 集成级验证：立即执行任务必须抢夺正在运行任务的执行机会。"""

    def setUp(self):
        self.sched, self.tmp, self._orig, self._ss_mod = _make_scheduler()

    def tearDown(self):
        self._ss_mod.SettingsService._get_setting = self._orig
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_force_task_preempts_running_task_in_scan(self):
        """用户立即执行低优先级任务 L：运行中的高优先级任务 H 必须被抢占停止。"""
        h = _FakeTask("任务H", priority=1)          # 正在运行
        h.current_status = 0
        l = _FakeTask("任务L", priority=10,          # 被立即执行
                      next_execute_time=_FakeTask._now(), force=True)
        l.current_status = 2
        for t in (h, l):
            self.sched.task_queue.enqueue(t)

        self.sched.scan()

        # 修复后：L 抢占 H，H 被 stop
        self.assertTrue(h.stopped, "运行中的高优先级任务应被立即执行任务抢占停止")
        # L 仍保持 force 标记，等待 H 结束后的下一轮扫描真正执行
        self.assertTrue(l.force_execute_now, "抢占后 force 标记应保留供下一轮扫描执行")

    def test_non_force_low_priority_does_not_preempt_running_high(self):
        """回归：普通低优先级就绪任务不得抢占运行中的高优先级任务。"""
        h = _FakeTask("任务H", priority=1)
        h.current_status = 0
        l = _FakeTask("任务L", priority=10,
                      next_execute_time=_FakeTask._now(), force=False)
        l.current_status = 2
        for t in (h, l):
            self.sched.task_queue.enqueue(t)

        self.sched.scan()

        self.assertFalse(h.stopped, "普通低优先级就绪任务不应抢占运行中的高优先级任务")

    def test_force_task_starts_when_nothing_running(self):
        """无任务运行时：force 任务被 pick_next 优先选中并执行，force 标记清除。"""
        h = _FakeTask("任务H", priority=1,           # 高优先级但未到期
                      next_execute_time=(_FakeTask._now()
                                         + datetime.timedelta(days=1)))
        l = _FakeTask("任务L", priority=10,
                      next_execute_time=_FakeTask._now(), force=True)
        l.current_status = 2
        for t in (h, l):
            self.sched.task_queue.enqueue(t)

        self.sched.scan()

        # L 应立即执行（run 被调用）；force 标记保留至任务完成回调，
        # 用于保护"立即执行启动"的任务在执行期间不被普通任务抢占
        self.assertTrue(l.run_called, "无任务运行时立即执行任务应直接开始执行")
        self.assertTrue(l.force_execute_now, "立即执行标记应保留至任务完成（保护执行）")
        self.assertEqual(l.current_status, 0)

    def test_force_task_picks_higher_force_first(self):
        """两个就绪任务中，force 任务优先于高优先级普通任务。"""
        h = _FakeTask("任务H", priority=1,           # 高优先级普通就绪
                      next_execute_time=_FakeTask._now(), force=False)
        l = _FakeTask("任务L", priority=10,
                      next_execute_time=_FakeTask._now(), force=True)
        for t in (h, l):
            self.sched.task_queue.enqueue(t)
            self.sched.task_queue.update_task_status(t.task_name, 1)

        next_task = self.sched.planner.pick_next(
            self.sched.task_queue.get_tasks_by_status(1))
        self.assertEqual(next_task.task_name, "任务L",
                         "立即执行标记任务应优先于高优先级普通任务")

    def test_force_running_not_preempted_by_normal_higher_priority(self):
        """立即执行任务执行中：普通更高优先级任务到期，不得抢占（用户日志场景）。"""
        l = _FakeTask("消耗体力", priority=10,       # 被激活的立即执行任务，正在运行
                      next_execute_time=_FakeTask._now(), force=True)
        l.current_status = 0                        # 已进入执行队列（force 标记保留）
        l.run_called = True
        h = _FakeTask("排行榜点赞", priority=1,      # 普通高优先级任务，自然到期
                      next_execute_time=_FakeTask._now(), force=False)
        h.current_status = 2
        for t in (l, h):
            self.sched.task_queue.enqueue(t)

        self.sched.scan()

        self.assertFalse(l.stopped,
                         "立即执行任务执行中不应被普通高优先级任务抢占")
        self.assertEqual(l.current_status, 0,
                         "立即执行任务应保持执行状态")
        # 普通高优先级任务留在就绪队列，等立即执行任务完成后再执行
        self.assertEqual(h.current_status, 1,
                         "普通高优先级任务应在就绪队列等待")

    def test_force_flag_cleared_on_task_complete(self):
        """force 标记在任务完成回调中被清除（任务结束后不再保护）。"""
        l = _FakeTask("消耗体力", priority=10, force=True)
        l.current_status = 0
        self.sched.task_queue.enqueue(l)

        self.sched._execute_done_callback(l)

        self.assertFalse(l.force_execute_now,
                         "任务完成后立即执行标记应清除，恢复普通调度")
        self.assertEqual(l.current_status, 2)



if __name__ == "__main__":
    unittest.main(verbosity=2)


