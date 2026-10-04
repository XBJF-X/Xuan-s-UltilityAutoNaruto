# -*- coding: utf-8 -*-
"""任务排期等价性基线（P2）。

用途：把**迁移前**各任务 ``_get_execute_window`` 的行为逐字复刻为基准函数，
断言任务实例（无论内部是旧的重写方法还是新的声明式 ``schedule``）产出同样的窗口。
因此本脚本在迁移前后都应全绿——迁移后它即成为"声明式排期与旧实现等价"的证明。

覆盖：情报站(0:00 日界)、冬日烟花季/无差别(限时)、一乐外卖(秒级起点)、
高级招募(2 天窗口)、修行之路/更多玩法/每周胜场/忍法帖族(周窗口)、追击晓组织(12:00 起)、
赛季胜场(月窗口)、巅峰对决/天地战场/要塞争夺战(周固定时段，受叛忍参数影响)、
叛忍来袭(多窗口，依赖其它任务参数)、消耗体力(默认日窗口)。
"""
import os
import sys
import unittest
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.core.legacy.Task import TASK_TYPE_MAP

TZ = ZoneInfo("Asia/Shanghai")

THU_1400 = datetime(2026, 9, 10, 14, 0, tzinfo=TZ)
THU_0300 = datetime(2026, 9, 10, 3, 0, tzinfo=TZ)
THU_0500 = datetime(2026, 9, 10, 5, 0, 30, tzinfo=TZ)
THU_0501 = datetime(2026, 9, 10, 5, 1, tzinfo=TZ)
THU_2359 = datetime(2026, 9, 10, 23, 59, tzinfo=TZ)
WED_2110 = datetime(2026, 9, 9, 21, 10, tzinfo=TZ)
WED_2200 = datetime(2026, 9, 9, 22, 0, tzinfo=TZ)
SAT_2010 = datetime(2026, 9, 12, 20, 10, tzinfo=TZ)
SUN_2100 = datetime(2026, 9, 13, 21, 0, tzinfo=TZ)
MON_1000 = datetime(2026, 9, 14, 10, 0, tzinfo=TZ)
MON_0300 = datetime(2026, 9, 14, 3, 0, tzinfo=TZ)
MONTH_END_0300 = datetime(2026, 9, 30, 3, 0, tzinfo=TZ)
NEXT_MONTH_0300 = datetime(2026, 10, 1, 3, 0, tzinfo=TZ)
FEB_1200 = datetime(2026, 2, 15, 12, 0, tzinfo=TZ)

BASES = [THU_1400, THU_0300, THU_0500, THU_0501, THU_2359,
         WED_2110, WED_2200, SAT_2010, SUN_2100, MON_1000, MON_0300]


class FakeConfig:
    """最小的 Config 替身：只提供排期需要的 get_task_exe_param / get_task_base_config。"""

    def __init__(self, params=None, base=None):
        self.params = params or {}
        self.base = base or {}

    def get_task_exe_param(self, task_name, param_name, default=None):
        return self.params.get((task_name, param_name), default)

    def get_task_base_config(self, task_name, key, default=None):
        # 未配置"下次执行时间"时返回 0（next_execute_time 会回落为当前时间）
        return self.base.get((task_name, key), default if default is not None else 0)


def make_task(task_cn_name, params=None, last_run=None):
    """构造只含排期所需属性的任务实例（不跑 __init__，避免设备/配置依赖）。"""
    cls = TASK_TYPE_MAP[task_cn_name]
    obj = object.__new__(cls)
    obj.tz_info = TZ
    obj.task_name = task_cn_name
    obj.config = FakeConfig(params)
    obj.last_run_time = last_run or THU_1400
    return obj


# --------------------------------------------------------------------------- #
#                       迁移前的行为复刻（等价性基准）                           #
# --------------------------------------------------------------------------- #
def legacy_daily(dt, start_line=None, dead_line=None):
    """旧 BaseTask._get_execute_window 默认实现"""
    today = dt.date()
    if dt.time() < time(5, 1):
        today -= timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    start = datetime.combine(today, start_line or time(5, 1), tzinfo=dt.tzinfo)
    end = (datetime.combine(today, dead_line, tzinfo=dt.tzinfo) if dead_line
           else datetime.combine(tomorrow, time(5, 1), tzinfo=dt.tzinfo))
    return [(start, end)]


def legacy_qingbaozhan(dt):
    """旧情报站：窗口 [当日 0:00, 次日 0:00)"""
    today = dt.date()
    return [(datetime.combine(today, time(0, 0), tzinfo=dt.tzinfo),
             datetime.combine(today + timedelta(days=1), time(0, 0), tzinfo=dt.tzinfo))]


def legacy_weekly(dt, at=time(5, 1)):
    """旧周窗口：本周一 at ~ 下周一 5:01"""
    today = dt.date()
    if dt.time() < time(5, 1):
        today -= timedelta(days=1)
    monday = today - timedelta(days=today.weekday())
    return [(datetime.combine(monday, at, tzinfo=dt.tzinfo),
             datetime.combine(monday + timedelta(weeks=1), time(5, 1), tzinfo=dt.tzinfo))]


def legacy_saiji(dt):
    """旧赛季胜场：本月倒数第 2 天 5:01 起 2 天"""
    today = dt.date()
    if dt.time() < time(5, 1):
        today -= timedelta(days=1)
    next_month = today.replace(day=28) + timedelta(days=4)
    last_day = next_month - timedelta(days=next_month.day)
    start = datetime.combine(last_day - timedelta(days=1), time(5, 1), tzinfo=dt.tzinfo)
    return [(start, start + timedelta(days=2))]


def legacy_gaoji(dt):
    """旧高级招募：窗口 [当日 5:01, 当日+2 天 5:01)"""
    today = dt.date()
    if dt.time() < time(5, 1):
        today -= timedelta(days=1)
    return [(datetime.combine(today, time(5, 1), tzinfo=dt.tzinfo),
             datetime.combine(today + timedelta(days=2), time(5, 1), tzinfo=dt.tzinfo))]


def _windows(task, base):
    return [(w_start, w_end) for w_start, w_end in task._get_execute_window(base)]


def legacy_weekly_slot(dt, weekday, hour, default_minute, running_minute, has_panren):
    """旧巅峰对决/天地战场/要塞争夺战：hour:00 ~ hour:{minute}（受叛忍参数影响）"""
    today = dt.date()
    if dt.time() < time(5, 1):
        today -= timedelta(days=1)
    day = today - timedelta(days=today.weekday() - weekday)
    start = datetime.combine(day, time(hour, 0), tzinfo=dt.tzinfo)
    end_minute = default_minute
    if has_panren and running_minute != 0:
        end_minute = running_minute
    end = datetime.combine(day, time(hour, end_minute), tzinfo=dt.tzinfo)
    return [(start, end)]


def legacy_panren(dt, has_tiandi, has_yaosai, tiandi_minute, yaosai_minute):
    """旧叛忍来袭：周三/周六触发窗口（+30 分钟缓冲）+ 下周三兜底窗口"""
    windows = []
    today = dt.date()
    if today.weekday() in (0, 1, 2) and has_tiandi:
        wed = today + timedelta(days=2 - today.weekday())
        start = datetime.combine(wed, time(21, 0), tzinfo=dt.tzinfo)
        trigger = tiandi_minute or 30
        end = datetime.combine(wed, time(21, trigger), tzinfo=dt.tzinfo) + timedelta(minutes=30)
        windows.append((start, end))
    if today.weekday() in (3, 4, 5) and has_yaosai:
        sat = today + timedelta(days=5 - today.weekday())
        start = datetime.combine(sat, time(20, 0), tzinfo=dt.tzinfo)
        trigger = yaosai_minute or 30
        end = datetime.combine(sat, time(20, trigger), tzinfo=dt.tzinfo) + timedelta(minutes=30)
        windows.append((start, end))
    next_wed = today + timedelta(days=(2 - today.weekday()) % 7)
    start = datetime.combine(next_wed, time(21, 0), tzinfo=dt.tzinfo)
    windows.append((start, start + timedelta(minutes=60)))
    windows.sort(key=lambda w: w[0])
    return windows


class ScheduleBaselineTest(unittest.TestCase):
    """逐任务断言：当前窗口实现 == 迁移前行为复刻"""

    def assert_same(self, task_cn, legacy_fn, bases=None, params=None):
        task = make_task(task_cn, params=params)
        for base in (bases or BASES):
            with self.subTest(task=task_cn, base=base):
                self.assertEqual(_windows(task, base), legacy_fn(base))

    # ---- 每日族 ----
    def test_qingbaozhan(self):
        self.assert_same("情报站", legacy_qingbaozhan)

    def test_dongriyanhuaji(self):
        self.assert_same("冬日烟花季",
                         lambda base: legacy_daily(base, time(19, 0), time(22, 0)))

    def test_wuchabie(self):
        self.assert_same("无差别预选赛",
                         lambda base: legacy_daily(base, time(18, 0), time(22, 0)))

    def test_yilewaimai(self):
        self.assert_same("一乐外卖",
                         lambda base: legacy_daily(base, time(11, 0, 20), None))

    def test_gaojizhaomu(self):
        self.assert_same("高级忍者招募", legacy_gaoji)

    def test_xiaohaotili_keeps_daily_window(self):
        self.assert_same("消耗体力", legacy_daily)

    # ---- 周族 ----
    def test_weekly_tasks(self):
        for name in ["修行之路", "更多玩法", "每周胜场",
                     "忍法帖点赞分享", "忍法帖奖励"]:
            self.assert_same(name, legacy_weekly)

    def test_zhuijixiaozuzhi(self):
        self.assert_same("追击晓组织",
                         lambda base: legacy_weekly(base, time(12, 0)))

    # ---- 月族 ----
    def test_saijishengchang(self):
        self.assert_same("赛季胜场", legacy_saiji,
                         BASES + [MONTH_END_0300, NEXT_MONTH_0300, FEB_1200])

    # ---- 周固定时段族（受叛忍参数影响）----
    @staticmethod
    def _panren_params(task_cn, has_panren, minute):
        return {(task_cn, "执行结束后是否有叛忍"): has_panren,
                (task_cn, "本任务执行多少分钟后执行叛忍"): minute}

    def test_dianfengduijue(self):
        for has_panren, minute in [(False, 0), (True, 0), (True, 45)]:
            params = self._panren_params("巅峰对决", has_panren, minute)
            self.assert_same(
                "巅峰对决",
                lambda base: legacy_weekly_slot(base, 2, 21, 30, minute, has_panren),
                params=params)

    def test_tiandizhanchang(self):
        for has_panren, minute in [(False, 0), (True, 40)]:
            params = self._panren_params("天地战场", has_panren, minute)
            self.assert_same(
                "天地战场",
                lambda base: legacy_weekly_slot(base, 2, 21, 30, minute, has_panren),
                params=params)

    def test_yaosaizhengduozhan(self):
        for has_panren, minute in [(False, 0), (True, 40)]:
            params = self._panren_params("要塞争夺战", has_panren, minute)
            self.assert_same(
                "要塞争夺战",
                lambda base: legacy_weekly_slot(base, 5, 20, 30, minute, has_panren),
                params=params)

    # ---- 多窗口任务 ----
    def test_panrenlaixi(self):
        key_t = "执行结束后是否有叛忍"
        key_m = "本任务执行多少分钟后执行叛忍"
        cases = [
            ({}, False, False, 0, 0),
            ({("天地战场", key_t): True, ("天地战场", key_m): 45}, True, False, 45, 0),
            ({("要塞争夺战", key_t): True, ("要塞争夺战", key_m): 45}, False, True, 0, 45),
            ({("天地战场", key_t): True, ("要塞争夺战", key_t): True}, True, True, 0, 0),
        ]
        for params, has_t, has_y, tm, ym in cases:
            self.assert_same(
                "叛忍来袭",
                lambda base: legacy_panren(base, has_t, has_y, tm, ym),
                params=params)


class AllTasksScheduleTest(unittest.TestCase):
    """全量自检：每个注册任务都能给出排期描述与窗口（迁移后依然成立）"""

    def test_every_task_has_schedule(self):
        for name in TASK_TYPE_MAP:
            task = make_task(name)
            with self.subTest(task=name):
                self.assertTrue(task.schedule_description)
                self.assertTrue(task._get_execute_window(THU_1400),
                                f"{name} 未产生任何可执行窗口")

    def test_custom_schedule_instances_are_independent(self):
        """带参数的排期在实例间互相独立（bind 不污染类属性）"""
        plain = make_task("叛忍来袭")
        enabled = make_task("叛忍来袭", params={
            ("天地战场", "执行结束后是否有叛忍"): True,
        })
        # 周三 21:10：开启天地战场叛忍时命中"周三触发窗口"，否则只剩兜底窗口
        self.assertNotEqual(_windows(plain, WED_2110), _windows(enabled, WED_2110))


class TimeHookTest(unittest.TestCase):
    """时间钩子语义：on_complete / on_deadline / on_delay 与窗口校验的关系"""

    def test_dianfeng_on_complete_activates_panren(self):
        task = make_task("巅峰对决")
        activated = []
        task._activate_another_task = lambda name, **kw: activated.append(name)
        nxt = task.on_complete(THU_1400)
        self.assertEqual(activated, ["叛忍来袭"])
        self.assertEqual(nxt, datetime(2026, 9, 16, 21, 0, tzinfo=TZ))

    def test_xiaohaotili_on_complete_three_segments(self):
        task = make_task("消耗体力")
        # 日界前 → 当天日界；日界~16:00 → 最多 3 小时；16:00 后 → 次日日界
        self.assertEqual(task.on_complete(datetime(2026, 9, 10, 3, 0, tzinfo=TZ)),
                         datetime(2026, 9, 10, 5, 1, tzinfo=TZ))
        self.assertEqual(task.on_complete(datetime(2026, 9, 10, 9, 0, tzinfo=TZ)),
                         datetime(2026, 9, 10, 12, 0, tzinfo=TZ))
        self.assertEqual(task.on_complete(datetime(2026, 9, 10, 18, 0, tzinfo=TZ)),
                         datetime(2026, 9, 11, 5, 1, tzinfo=TZ))

    def test_base_default_hooks(self):
        task = make_task("排行榜点赞")            # Daily(at=8:00)
        self.assertEqual(task.on_complete(THU_1400),
                         datetime(2026, 9, 11, 8, 0, tzinfo=TZ))
        self.assertEqual(task.on_deadline(THU_1400), task.on_complete(THU_1400))
        self.assertEqual(task.on_delay(THU_1400, timedelta(hours=1)),
                         THU_1400 + timedelta(hours=1))

    def test_skip_window_flags(self):
        """force_execute_now（立即执行/被激活）与 ignore_time_window（预设顺序执行）都跳过窗口校验"""
        task = make_task("修行之路")
        self.assertFalse(task._should_skip_window_check())
        task.force_execute_now = True
        self.assertTrue(task._should_skip_window_check())
        self.assertEqual(task._skip_window_reason(), "立即执行/被激活")
        task.force_execute_now = False
        task.ignore_time_window = True
        self.assertTrue(task._should_skip_window_check())
        self.assertEqual(task._skip_window_reason(), "预设顺序执行")

    def test_check_execute_window_raises(self):
        """窗口外抛错：未到 → TooEarlyToRun；已过 → TimeOutDeadLineError"""
        from backend.core.legacy.Exceptions import TimeOutDeadLineError, TooEarlyToRun

        evening_task = make_task("冬日烟花季")     # Daily(19:00~22:00)
        with self.assertRaises(TooEarlyToRun):
            evening_task._check_execute_window(THU_1400)                 # 14:00 未到
        with self.assertRaises(TimeOutDeadLineError):
            evening_task._check_execute_window(
                datetime(2026, 9, 10, 22, 30, tzinfo=TZ))                # 22:30 已过
        # 窗口内不抛错
        evening_task._check_execute_window(datetime(2026, 9, 10, 20, 0, tzinfo=TZ))

    def test_on_delay_is_window_free(self):
        """on_delay / schedule_next_with_delay 表示显式排期意图，不受窗口限制"""
        task = make_task("情报站")
        late_night = datetime(2026, 9, 10, 23, 30, tzinfo=TZ)
        delayed = task.on_delay(late_night, timedelta(hours=3))
        self.assertEqual(delayed, datetime(2026, 9, 11, 2, 30, tzinfo=TZ))
        self.assertTrue(task._check_window_invalid(
            delayed, late_night), "02:30 不在 0:00 日界窗口内（窗口校验与排期互不影响）")


class SchedulerSnapshotTest(unittest.TestCase):
    """调度器任务状态快照字段（前端总览用；排期描述不进入快照）"""

    def test_snapshot_fields(self):
        from backend.core.scheduler.state import SchedulerState
        from backend.services.scheduler_service import SchedulerService

        svc = object.__new__(SchedulerService)     # 不跑 __init__（避免设备初始化）
        svc.state = SchedulerState()
        svc._sync_task_state(make_task("修行之路"))
        entry = svc.state.get_tasks()[0]
        self.assertEqual(entry["name"], "修行之路")
        self.assertIn("status", entry)
        self.assertIn("priority", entry)
        self.assertTrue(entry["next_execute"])
        self.assertNotIn("schedule", entry, "排期描述不进快照（前端不再展示）")


if __name__ == "__main__":
    unittest.main(verbosity=2)
