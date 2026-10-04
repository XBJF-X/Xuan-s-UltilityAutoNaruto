# -*- coding: utf-8 -*-
"""验证声明式排期 schedule.py 的窗口/周期语义（P0）。

覆盖：
1. Daily：默认 5:01 日界、boundary=0:00（情报站）、限时窗口（冬日烟花季/无差别/一乐外卖）；
2. Weekly：整周窗口（周一 5:01 起）、自定义起点（追击晓组织 12:00）、多选星期（周一/三/五）；
3. WeeklySlot：周三 21:00~21:30 的边界（含 5:01 日界归一化后的"昨天归属"）；
4. Monthly：倒数第 2 天起 2 天（赛季胜场）、正数日/多日期/负索引；
5. Interval / AnyTime / Union / Custom / describe()；
6. 与旧实现逐点等价：直接复刻旧 BaseTask / GengDuoWanFa / SaiJiShengChang 的算法做比较。
"""
import os
import sys
import unittest
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.core.legacy.Task.schedule import (
    AnyTime,
    Custom,
    Daily,
    Interval,
    Monthly,
    ScheduleContext,
    Union,
    Weekday,
    Weekly,
    WeeklySlot,
    Window,
)

TZ = ZoneInfo("Asia/Shanghai")

# 固定日期基准：2026-09-10 周四、09-07 周一、09-09 周三、09-12 周六、09-14 下周一
THU_1400 = datetime(2026, 9, 10, 14, 0, tzinfo=TZ)
THU_0300 = datetime(2026, 9, 10, 3, 0, tzinfo=TZ)
THU_0500 = datetime(2026, 9, 10, 5, 0, 30, tzinfo=TZ)
THU_0501 = datetime(2026, 9, 10, 5, 1, tzinfo=TZ)
THU_2359 = datetime(2026, 9, 10, 23, 59, tzinfo=TZ)
MON_1000 = datetime(2026, 9, 14, 10, 0, tzinfo=TZ)
WED_2200 = datetime(2026, 9, 9, 22, 0, tzinfo=TZ)
WED_2110 = datetime(2026, 9, 9, 21, 10, tzinfo=TZ)

MON_0501 = datetime(2026, 9, 7, 5, 1, tzinfo=TZ)
NEXT_MON_0501 = datetime(2026, 9, 14, 5, 1, tzinfo=TZ)


# --------------------------------------------------------------------------- #
#                      旧实现复刻（作为等价性比较基准）                           #
# --------------------------------------------------------------------------- #
def legacy_daily_window(dt, start_line=None, dead_line=None):
    """复刻旧 BaseTask._get_execute_window 默认实现"""
    today = dt.date()
    if dt.time() < time(5, 1):
        today -= timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    start = datetime.combine(today, start_line or time(5, 1), tzinfo=dt.tzinfo)
    if dead_line:
        end = datetime.combine(today, dead_line, tzinfo=dt.tzinfo)
    else:
        end = datetime.combine(tomorrow, time(5, 1), tzinfo=dt.tzinfo)
    return [(start, end)]


def legacy_weekly_window(dt):
    """复刻旧 GengDuoWanFa / MeiZhouShengChang / XiuXingZhiLu 的周窗口"""
    today = dt.date()
    if dt.time() < time(5, 1):
        today -= timedelta(days=1)
    this_monday = today - timedelta(days=today.weekday())
    start = datetime.combine(this_monday, time(5, 1), tzinfo=dt.tzinfo)
    end = datetime.combine(this_monday + timedelta(weeks=1), time(5, 1), tzinfo=dt.tzinfo)
    return [(start, end)]


def legacy_weekly_start12_window(dt):
    """复刻旧 ZhuiJiXiaoZuZhi 的周窗口（起点 12:00）"""
    today = dt.date()
    if dt.time() < time(5, 1):
        today -= timedelta(days=1)
    this_monday = today - timedelta(days=today.weekday())
    start = datetime.combine(this_monday, time(12, 0), tzinfo=dt.tzinfo)
    end = datetime.combine(this_monday + timedelta(weeks=1), time(5, 1), tzinfo=dt.tzinfo)
    return [(start, end)]


def legacy_saiji_window(dt):
    """复刻旧 SaiJiShengChang 的月窗口（倒数第 2 天 5:01 起 2 天）"""
    today = dt.date()
    if dt.time() < time(5, 1):
        today -= timedelta(days=1)
    next_month = today.replace(day=28) + timedelta(days=4)
    last_day = next_month - timedelta(days=next_month.day)
    second_last = last_day - timedelta(days=1)
    start = datetime.combine(second_last, time(5, 1), tzinfo=dt.tzinfo)
    return [(start, start + timedelta(days=2))]


DAILY_BASES = [THU_1400, THU_0300, THU_0500, THU_0501, THU_2359, MON_1000]


class WindowTest(unittest.TestCase):
    """Window 半开区间语义"""

    def test_semi_open_interval(self):
        win = Window(WED_2110, WED_2110 + timedelta(minutes=30))
        self.assertFalse(win.contains(WED_2110 - timedelta(seconds=1)))
        self.assertTrue(win.contains(WED_2110), "起点应包含")
        self.assertTrue(win.contains(WED_2110 + timedelta(minutes=29, seconds=59)))
        self.assertFalse(win.contains(WED_2110 + timedelta(minutes=30)), "终点不包含")

    def test_unbounded(self):
        win = Window(None, None)
        self.assertTrue(win.contains(THU_1400))
        self.assertIsNone(win.duration)


class DailyTest(unittest.TestCase):

    def test_matches_legacy_default(self):
        sched = Daily()
        for base in DAILY_BASES:
            with self.subTest(base=base):
                self.assertEqual(
                    [(w.start, w.end) for w in sched.windows(base)],
                    legacy_daily_window(base))

    def test_day_boundary_is_0501(self):
        sched = Daily()
        self.assertEqual(sched.windows(THU_0300)[0].start,
                         datetime(2026, 9, 9, 5, 1, tzinfo=TZ))
        self.assertEqual(sched.windows(THU_0501)[0].start,
                         datetime(2026, 9, 10, 5, 1, tzinfo=TZ))

    def test_zero_boundary_qingbaozhan(self):
        sched = Daily(boundary=time(0, 0))
        win = sched.windows(THU_1400)[0]
        self.assertEqual(win.start, datetime(2026, 9, 10, 0, 0, tzinfo=TZ))
        self.assertEqual(win.end, datetime(2026, 9, 11, 0, 0, tzinfo=TZ))
        # 凌晨 0:30 属于当天窗口
        win2 = sched.windows(datetime(2026, 9, 10, 0, 30, tzinfo=TZ))[0]
        self.assertEqual(win2.start, datetime(2026, 9, 10, 0, 0, tzinfo=TZ))

    def test_limited_window_matches_legacy(self):
        cases = [
            (time(19, 0), time(22, 0)),     # 冬日烟花季
            (time(18, 0), time(22, 0)),     # 无差别预选赛
            (time(11, 0, 20), None),        # 一乐外卖（起点精确到秒）
        ]
        for at, until in cases:
            sched = Daily(at=at, until=until)
            for base in DAILY_BASES:
                with self.subTest(at=at, until=until, base=base):
                    self.assertEqual(
                        [(w.start, w.end) for w in sched.windows(base)],
                        legacy_daily_window(base, at, until))

    def test_next_cycle_and_default_time(self):
        sched = Daily()
        self.assertEqual(sched.next_cycle(THU_1400), THU_1400 + timedelta(days=1))
        self.assertEqual(sched.default_time(THU_1400),
                         datetime(2026, 9, 10, 5, 1, tzinfo=TZ))
        self.assertEqual(sched.default_time(THU_1400, after_cycle=True),
                         datetime(2026, 9, 11, 5, 1, tzinfo=TZ))


class WeeklyTest(unittest.TestCase):

    def test_whole_week_matches_legacy(self):
        sched = Weekly(Weekday.MON)
        for base in DAILY_BASES:
            with self.subTest(base=base):
                self.assertEqual(
                    [(w.start, w.end) for w in sched.windows(base)],
                    legacy_weekly_window(base))

    def test_whole_week_keeps_previous_week_before_boundary(self):
        """周一 03:00 仍属上一周（与旧归一化一致）"""
        sched = Weekly(Weekday.MON)
        base = datetime(2026, 9, 14, 3, 0, tzinfo=TZ)
        win = sched.windows(base)[0]
        self.assertEqual(win.start, MON_0501)
        self.assertEqual(win.end, NEXT_MON_0501)

    def test_custom_start_time_matches_legacy(self):
        sched = Weekly(Weekday.MON, at=time(12, 0))
        for base in DAILY_BASES:
            with self.subTest(base=base):
                self.assertEqual(
                    [(w.start, w.end) for w in sched.windows(base)],
                    legacy_weekly_start12_window(base))

    def test_multi_days_windows(self):
        sched = Weekly(days=[Weekday.MON, Weekday.WED, Weekday.FRI])
        wins = sched.windows(THU_1400)          # 周四 → 本周一/三 已过，周五在未来
        self.assertEqual(
            [w.start for w in wins],
            [datetime(2026, 9, 7, 5, 1, tzinfo=TZ),
             datetime(2026, 9, 9, 5, 1, tzinfo=TZ),
             datetime(2026, 9, 11, 5, 1, tzinfo=TZ)])
        self.assertFalse(sched.contains(THU_1400, THU_1400))
        self.assertTrue(sched.contains(datetime(2026, 9, 11, 9, 0, tzinfo=TZ), THU_1400))

    def test_multi_days_next_cycle_is_next_selected_day(self):
        sched = Weekly(days=[Weekday.MON, Weekday.WED, Weekday.FRI])
        mon = datetime(2026, 9, 7, 6, 0, tzinfo=TZ)
        self.assertEqual(sched.next_cycle(mon), datetime(2026, 9, 9, 5, 1, tzinfo=TZ))
        fri = datetime(2026, 9, 11, 6, 0, tzinfo=TZ)
        self.assertEqual(sched.next_cycle(fri), NEXT_MON_0501)

    def test_span_override(self):
        sched = Weekly(Weekday.MON, span=timedelta(days=3))
        win = sched.windows(THU_1400)[0]
        self.assertEqual(win.start, MON_0501)
        self.assertEqual(win.end, MON_0501 + timedelta(days=3))

    def test_requires_weekday(self):
        with self.assertRaises(ValueError):
            Weekly()
        with self.assertRaises(ValueError):
            Weekly(days=[])


class WeeklySlotTest(unittest.TestCase):

    def setUp(self):
        self.sched = WeeklySlot(Weekday.WED, time(21, 0), time(21, 30))

    def test_window_shape(self):
        win = self.sched.windows(WED_2110)[0]
        self.assertEqual(win.start, datetime(2026, 9, 9, 21, 0, tzinfo=TZ))
        self.assertEqual(win.end, datetime(2026, 9, 9, 21, 30, tzinfo=TZ))

    def test_after_0501_uses_this_week(self):
        """周三 22:00（已过窗口）仍归属本周三"""
        win = self.sched.windows(WED_2200)[0]
        self.assertEqual(win.start, datetime(2026, 9, 9, 21, 0, tzinfo=TZ))
        self.assertFalse(win.contains(WED_2200))

    def test_before_0501_belongs_to_yesterday(self):
        """周四 03:00 → 归属周三（与旧实现一致）"""
        win = self.sched.windows(THU_0300)[0]
        self.assertEqual(win.start, datetime(2026, 9, 9, 21, 0, tzinfo=TZ))

    def test_next_slot_is_next_week(self):
        win = self.sched.windows(MON_1000)[0]
        self.assertEqual(win.start, datetime(2026, 9, 16, 21, 0, tzinfo=TZ))
        self.assertEqual(win.end, datetime(2026, 9, 16, 21, 30, tzinfo=TZ))

    def test_contains_with_stale_base(self):
        """base 已过窗口时，仍能判定"当时是否在窗口内"（与旧 _check_window_invalid 一致）"""
        self.assertTrue(self.sched.contains(WED_2110, WED_2200))
        self.assertFalse(self.sched.contains(WED_2200, WED_2200))

    def test_span_mode(self):
        sched = WeeklySlot(Weekday.WED, time(21, 0), span=timedelta(minutes=45))
        win = sched.windows(WED_2110)[0]
        self.assertEqual(win.end, datetime(2026, 9, 9, 21, 45, tzinfo=TZ))

    def test_next_cycle_is_one_week(self):
        self.assertEqual(self.sched.next_cycle(WED_2110), WED_2110 + timedelta(weeks=1))

    def test_requires_end(self):
        with self.assertRaises(ValueError):
            WeeklySlot(Weekday.WED, time(21, 0))


class MonthlyTest(unittest.TestCase):

    def test_saiji_matches_legacy(self):
        sched = Monthly(day=-2, span=timedelta(days=2))
        # 覆盖月末/月初/闰年附近
        for base in [THU_1400, datetime(2026, 9, 30, 3, 0, tzinfo=TZ),
                     datetime(2026, 10, 1, 3, 0, tzinfo=TZ),
                     datetime(2026, 2, 15, 12, 0, tzinfo=TZ),
                     datetime(2027, 2, 15, 12, 0, tzinfo=TZ),
                     datetime(2026, 12, 31, 23, 0, tzinfo=TZ)]:
            with self.subTest(base=base):
                self.assertEqual(
                    [(w.start, w.end) for w in sched.windows(base)],
                    legacy_saiji_window(base))

    def test_default_time_after_cycle_matches_legacy(self):
        sched = Monthly(day=-2, span=timedelta(days=2))
        for base in [THU_1400, datetime(2026, 9, 29, 6, 0, tzinfo=TZ)]:
            with self.subTest(base=base):
                legacy = legacy_saiji_window(
                    base.replace(day=28) + timedelta(days=4))[0][0]
                self.assertEqual(sched.default_time(base, after_cycle=True), legacy)

    def test_negative_index_multiple_days(self):
        sched = Monthly(days=[-1, -2])
        wins = sched.windows(THU_1400)
        self.assertEqual([w.start for w in wins],
                         [datetime(2026, 9, 29, 5, 1, tzinfo=TZ),
                          datetime(2026, 9, 30, 5, 1, tzinfo=TZ)])

    def test_positive_day(self):
        sched = Monthly(day=15)
        win = sched.windows(THU_1400)[0]
        self.assertEqual(win.start, datetime(2026, 9, 15, 5, 1, tzinfo=TZ))
        self.assertEqual(win.end, datetime(2026, 9, 16, 5, 1, tzinfo=TZ))

    def test_positive_day_with_until(self):
        sched = Monthly(day=15, until=time(22, 0))
        win = sched.windows(THU_1400)[0]
        self.assertEqual(win.end, datetime(2026, 9, 15, 22, 0, tzinfo=TZ))

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            Monthly()
        with self.assertRaises(ValueError):
            Monthly(day=0)


class IntervalAnyTimeTest(unittest.TestCase):

    def test_interval_default_window_is_daily(self):
        sched = Interval(timedelta(hours=3))
        win = sched.windows(THU_1400)[0]
        self.assertEqual(win.start, datetime(2026, 9, 10, 5, 1, tzinfo=TZ))
        self.assertEqual(win.end, datetime(2026, 9, 11, 5, 1, tzinfo=TZ))

    def test_interval_window_span_like_gaojizhaomu(self):
        """高级招募：窗口 [当日 5:01, 当日+2 天 5:01)"""
        sched = Interval(timedelta(days=2), window_span=timedelta(days=2))
        win = sched.windows(THU_1400)[0]
        self.assertEqual(win.start, datetime(2026, 9, 10, 5, 1, tzinfo=TZ))
        self.assertEqual(win.end, datetime(2026, 9, 12, 5, 1, tzinfo=TZ))

    def test_interval_default_time_after_cycle(self):
        sched = Interval(timedelta(hours=3))
        self.assertEqual(sched.default_time(THU_1400), THU_1400)
        self.assertEqual(sched.default_time(THU_1400, after_cycle=True),
                         THU_1400 + timedelta(hours=3))
        self.assertEqual(sched.next_cycle(THU_1400), THU_1400 + timedelta(hours=3))

    def test_anytime(self):
        sched = AnyTime()
        self.assertTrue(sched.contains(THU_1400, THU_1400))
        self.assertTrue(sched.contains(THU_0300, THU_1400))
        self.assertEqual(sched.default_time(THU_1400), THU_1400)


class UnionCustomTest(unittest.TestCase):

    def setUp(self):
        self.sched = Union(
            WeeklySlot(Weekday.WED, time(21, 0), time(21, 30)),
            WeeklySlot(Weekday.SAT, time(20, 0), time(20, 30)),
        )

    def test_windows_are_merged_and_sorted(self):
        wins = self.sched.windows(THU_1400)
        self.assertEqual([w.start for w in wins],
                         [datetime(2026, 9, 9, 21, 0, tzinfo=TZ),
                          datetime(2026, 9, 12, 20, 0, tzinfo=TZ)])

    def test_union_semantics_any_window_hits(self):
        """并集语义：任一窗口命中即为 True（修复旧 _check_window_invalid 的交集行为）"""
        self.assertTrue(self.sched.contains(WED_2110, THU_1400))
        self.assertTrue(self.sched.contains(
            datetime(2026, 9, 12, 20, 10, tzinfo=TZ), THU_1400))
        self.assertFalse(self.sched.contains(THU_1400, THU_1400))

    def test_default_time_takes_nearest_window(self):
        self.assertEqual(self.sched.default_time(THU_1400),
                         datetime(2026, 9, 9, 21, 0, tzinfo=TZ))
        self.assertEqual(self.sched.default_time(THU_1400, after_cycle=True),
                         datetime(2026, 9, 16, 21, 0, tzinfo=TZ))

    def test_or_operator(self):
        combined = WeeklySlot(Weekday.WED, time(21, 0), time(21, 30)) | \
            WeeklySlot(Weekday.SAT, time(20, 0), time(20, 30))
        self.assertIsInstance(combined, Union)
        self.assertEqual(len(combined.windows(THU_1400)), 2)

    def test_union_requires_schedules(self):
        with self.assertRaises(ValueError):
            Union()

    def test_custom_reads_task_params_after_bind(self):
        def fn(base, ctx):
            enabled = bool(ctx and ctx.param(
                "天地战场", "执行结束后是否有叛忍", False))
            if enabled:
                return [Window(base - timedelta(hours=1),
                               base + timedelta(minutes=30))]
            return [Window(base + timedelta(days=1),
                           base + timedelta(days=1, minutes=30))]

        sched = Custom(fn, cycle=lambda b: b + timedelta(weeks=1),
                       describe_text="叛忍来袭窗口")
        unbound = sched.windows(THU_1400)[0]
        self.assertEqual(unbound.start, THU_1400 + timedelta(days=1))

        ctx = ScheduleContext(
            tz=TZ,
            param=lambda task, name, default: True
            if (task, name) == ("天地战场", "执行结束后是否有叛忍") else default,
            now=lambda: THU_1400,
        )
        bound = sched.bind(ctx)
        self.assertEqual(bound.windows(THU_1400)[0].start,
                         THU_1400 - timedelta(hours=1))
        self.assertEqual(bound.next_cycle(THU_1400), THU_1400 + timedelta(weeks=1))
        self.assertEqual(bound.describe(), "叛忍来袭窗口")

    def test_custom_bind_does_not_mutate_original(self):
        def fn(base, ctx):
            return [Window(base, base + timedelta(minutes=1))]

        sched = Custom(fn)
        sched.bind(ScheduleContext(tz=TZ, param=lambda *a: None))
        self.assertIsNone(sched._ctx, "bind 不应污染原实例（类属性共享）")


class DescribeTest(unittest.TestCase):

    def test_descriptions(self):
        self.assertIn("每日", Daily().describe())
        self.assertIn("每周一", Weekly(Weekday.MON).describe())
        self.assertIn("周三", WeeklySlot(Weekday.WED, time(21, 0),
                                        time(21, 30)).describe())
        self.assertIn("倒数第 2 天",
                      Monthly(day=-2, span=timedelta(days=2)).describe())
        self.assertIn("间隔", Interval(timedelta(hours=3)).describe())
        self.assertEqual(AnyTime().describe(), "不限时间")
        self.assertIn("或", (WeeklySlot(Weekday.WED, time(21, 0), time(21, 30))
                            | WeeklySlot(Weekday.SAT, time(20, 0), time(20, 30))).describe())
        self.assertIn("每周一/周三/周五",
                      Weekly(days=[Weekday.MON, Weekday.WED, Weekday.FRI]).describe())


if __name__ == "__main__":
    unittest.main(verbosity=2)
