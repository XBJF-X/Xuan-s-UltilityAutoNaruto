# -*- coding: utf-8 -*-
"""验证 [忍法帖奖励]（RenFaTieJiangLi）的执行时间更新逻辑：

- all_tasks 与 all_activations 均为 True（周任务经验 + 周活跃度奖励都已领完）
  → 下一次执行时间 = 下一周周一 5:01；
- 否则按日周期补领 → 今天未过 5:01 则今天 5:01，已过则明天 5:01；
- 周维度窗口必须保留：BaseTask._handle_initialization 会用 _get_execute_window 校验
  配置里的下次执行时间，"下周一 5:01" 只能在下一周期窗口内被判为合法，否则会被清掉。
"""
import logging
import os
import sys
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.core.legacy.Task.RenFaTieJiangLi import RenFaTieJiangLi

_TZ = ZoneInfo("Asia/Shanghai")

# 固定日期基准：2026-09-10 为周四，09-07 为周一，09-14 为下周一
THU_1400 = datetime(2026, 9, 10, 14, 0, tzinfo=_TZ)
THU_0300 = datetime(2026, 9, 10, 3, 0, tzinfo=_TZ)
THU_0500 = datetime(2026, 9, 10, 5, 0, 30, tzinfo=_TZ)
THU_0501 = datetime(2026, 9, 10, 5, 1, 0, tzinfo=_TZ)
FRI_0501 = datetime(2026, 9, 11, 5, 1, tzinfo=_TZ)
THU_0501_SAME = datetime(2026, 9, 10, 5, 1, tzinfo=_TZ)
MON_0501 = datetime(2026, 9, 14, 5, 1, tzinfo=_TZ)
MON2_0501 = datetime(2026, 9, 21, 5, 1, tzinfo=_TZ)


def _make_task(all_tasks=False, all_activations=False):
    """构造只含时间计算所需属性的任务实例（不跑 __init__）"""
    task = object.__new__(RenFaTieJiangLi)
    task.logger = logging.getLogger("verify.rftjl")
    task.tz_info = _TZ
    task.last_run_time = THU_1400
    task.start_line = None
    task.dead_line = None
    task.all_tasks = all_tasks
    task.all_activations = all_activations
    return task


class FixtureSanityTest(unittest.TestCase):
    """固定日期基准自检，避免测试用错星期"""

    def test_weekdays(self):
        self.assertEqual(datetime(2026, 9, 10).weekday(), 3, "2026-09-10 应为周四")
        self.assertEqual(datetime(2026, 9, 7).weekday(), 0, "2026-09-07 应为周一")
        self.assertEqual(datetime(2026, 9, 14).weekday(), 0, "2026-09-14 应为周一")

    def test_weekly_window_shape(self):
        task = _make_task()
        start, end = task._get_execute_window(THU_1400)[0]
        self.assertEqual(start, datetime(2026, 9, 7, 5, 1, tzinfo=_TZ))
        self.assertEqual(end, MON_0501, "周窗口终点即下一周周一 5:01")


class DailyCycleTest(unittest.TestCase):
    """未全部领完 → 日周期：今天/明天 5:01"""

    def test_after_0501_goes_tomorrow(self):
        task = _make_task()
        self.assertEqual(task.on_complete(THU_1400), FRI_0501)

    def test_before_0501_goes_today(self):
        task = _make_task()
        self.assertEqual(task.on_complete(THU_0300), THU_0501_SAME)

    def test_before_0501_but_close_goes_today(self):
        task = _make_task()
        self.assertEqual(task.on_complete(THU_0500), THU_0501_SAME)

    def test_exactly_0501_goes_tomorrow(self):
        task = _make_task()
        self.assertEqual(task.on_complete(THU_0501), FRI_0501)

    def test_only_all_tasks_true_is_still_daily(self):
        task = _make_task(all_tasks=True, all_activations=False)
        self.assertEqual(task.on_complete(THU_1400), FRI_0501)

    def test_only_all_activations_true_is_still_daily(self):
        task = _make_task(all_tasks=False, all_activations=True)
        self.assertEqual(task.on_complete(THU_1400), FRI_0501)


class WeeklyCycleTest(unittest.TestCase):
    """全部领完 → 下一周周一 5:01"""

    def test_thursday_goes_next_monday(self):
        task = _make_task(all_tasks=True, all_activations=True)
        self.assertEqual(task.on_complete(THU_1400), MON_0501)

    def test_monday_before_0501_goes_same_monday(self):
        """周一 03:00 仍属上一周周期（5:01 换周），下一周起点即当天 05:01"""
        task = _make_task(all_tasks=True, all_activations=True)
        now = datetime(2026, 9, 14, 3, 0, tzinfo=_TZ)
        self.assertEqual(task.on_complete(now), MON_0501)

    def test_monday_after_0501_goes_next_week(self):
        task = _make_task(all_tasks=True, all_activations=True)
        now = datetime(2026, 9, 14, 6, 0, tzinfo=_TZ)
        self.assertEqual(task.on_complete(now), MON2_0501)

    def test_sunday_night_goes_next_monday(self):
        task = _make_task(all_tasks=True, all_activations=True)
        now = datetime(2026, 9, 13, 23, 0, tzinfo=_TZ)
        self.assertEqual(task.on_complete(now), MON_0501)

    def test_result_is_tz_aware(self):
        task = _make_task(all_tasks=True, all_activations=True)
        self.assertEqual(task.on_complete(THU_1400).tzinfo, _TZ)


class FlagsDefaultTest(unittest.TestCase):
    """未执行过 run() 的路径：类属性默认 False → 日周期，且不报 AttributeError"""

    def test_flags_default_to_false_before_run(self):
        task = object.__new__(RenFaTieJiangLi)
        task.logger = logging.getLogger("verify.rftjl")
        task.tz_info = _TZ
        task.last_run_time = THU_1400
        self.assertEqual(task.on_complete(THU_1400), FRI_0501)


class WindowAcceptanceTest(unittest.TestCase):
    """窗口校验：排期必须能被 BaseTask._handle_initialization 接受（否则会被重置）"""

    def test_weekly_schedule_accepted_by_next_cycle_window(self):
        task = _make_task(all_tasks=True, all_activations=True)
        nxt = task.on_complete(THU_1400)
        self.assertEqual(nxt, MON_0501)
        # 复刻 _handle_initialization 的双重校验：本周期窗口外 + 下一周期窗口内 → 保留
        self.assertTrue(task._check_window_invalid(nxt),
                        "下周一 5:01 不在本周窗口内（预期）")
        self.assertFalse(task._check_window_invalid(nxt,
                                                   task.get_next_cycle_day(THU_1400)),
                         "下周一 5:01 在下一周期窗口内，配置值应被保留")

    def test_daily_schedule_accepted_by_current_window(self):
        task = _make_task()
        nxt = task.on_complete(THU_1400)
        self.assertEqual(nxt, FRI_0501)
        self.assertFalse(task._check_window_invalid(nxt),
                         "明天 5:01 落在本周窗口内，配置值应被保留")


if __name__ == "__main__":
    unittest.main(verbosity=2)