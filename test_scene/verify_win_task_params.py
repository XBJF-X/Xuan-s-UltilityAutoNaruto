# -*- coding: utf-8 -*-
"""验证胜场任务新增的时间参数。

1. **每周胜场**：新增任务参数「每周几」（COMBOX 周一~周日，默认周一），
   窗口随所选星期变化，缺省/非法回退周一；
2. **赛季胜场**：新增任务参数「倒数第几天」（INT 1~31，默认 2），
   窗口起点 = 当月倒数第 N 天 5:01、窗口长 2 天，**且不跨越当月界限**
   （2 月设 31 天收敛到 2 月 1 日，而不是 1 月）；
3. 两个参数在 `src/DefaultConfig.json` 中的展示 schema（前端按此动态渲染）。
"""
import json
import os
import sys
import unittest
from datetime import datetime, timedelta, time as dtime
from pathlib import Path
from zoneinfo import ZoneInfo

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.core.legacy.Task.MeiZhouShengChang import _weekly_windows
from backend.core.legacy.Task.SaiJiShengChang import _monthly_windows
from backend.core.legacy.Task.schedule import Monthly, Weekly, Weekday

TZ = ZoneInfo("Asia/Shanghai")
DEFAULT_CONFIG = Path(_PROJECT_ROOT) / "src" / "DefaultConfig.json"

# 2026-09-10 是周四；2026-02 共 28 天；2026-04 共 30 天
THU_1400 = datetime(2026, 9, 10, 14, 0, tzinfo=TZ)


class _FakeCtx:
    """ScheduleContext 替身：只提供 param()。"""

    def __init__(self, params=None):
        self.params = params or {}

    def param(self, task_name, param_name, default=None):
        return self.params.get((task_name, param_name), default)


class WeeklyWinParamTest(unittest.TestCase):
    """每周胜场：'每周几' 参数驱动窗口"""

    def test_each_weekday_starts_that_day(self):
        for index in range(7):
            ctx = _FakeCtx({("每周胜场", "每周几"): index})
            win = _weekly_windows(THU_1400, ctx)[0]
            self.assertEqual(win.start.weekday(), index)
            self.assertEqual(win.start.time(), dtime(5, 1))
            self.assertEqual(win.end - win.start, timedelta(weeks=1))

    def test_matches_weekly_schedule(self):
        for index in range(7):
            ctx = _FakeCtx({("每周胜场", "每周几"): index})
            self.assertEqual(_weekly_windows(THU_1400, ctx),
                             Weekly(Weekday(index)).windows(THU_1400))

    def test_default_and_invalid_fall_back_to_monday(self):
        for params in (None, {("每周胜场", "每周几"): 99},
                       {("每周胜场", "每周几"): "x"}):
            for ctx in (None, _FakeCtx(params)):
                win = _weekly_windows(THU_1400, ctx)[0]
                self.assertEqual(win.start.weekday(), Weekday.MON.value)

    def test_default_config_schema(self):
        schema = json.loads(DEFAULT_CONFIG.read_text(encoding="utf-8"))
        param = schema["任务"]["每周胜场"]["执行参数"]["每周几"]
        self.assertEqual(param["类型"], "COMBOX")
        self.assertEqual(param["当前值"], 0, "默认应为周一")
        self.assertEqual(param["枚举列表"][0], "周一")
        self.assertEqual(len(param["枚举列表"]), 7)
        self.assertTrue(param["描述"])


class SeasonWinParamTest(unittest.TestCase):
    """赛季胜场：'倒数第几天' 参数驱动窗口，且不跨越当月界限"""

    def test_days_from_end_builds_expected_window(self):
        for days_from_end in (1, 2, 5, 10):
            ctx = _FakeCtx({("赛季胜场", "倒数第几天"): days_from_end})
            win = _monthly_windows(THU_1400, ctx)[0]
            last_day = datetime(2026, 9, 30).date()
            self.assertEqual(win.start.date(),
                             last_day - timedelta(days=days_from_end - 1))
            self.assertEqual(win.start.time(), dtime(5, 1))
            self.assertEqual(win.end - win.start, timedelta(days=2))

    def test_matches_monthly_schedule(self):
        for days_from_end in (1, 3, 7):
            ctx = _FakeCtx({("赛季胜场", "倒数第几天"): days_from_end})
            self.assertEqual(
                _monthly_windows(THU_1400, ctx),
                Monthly(day=-days_from_end,
                        span=timedelta(days=2)).windows(THU_1400))

    def test_default_and_invalid_fall_back_to_second_last(self):
        cases = [None, {("赛季胜场", "倒数第几天"): 0},
                 {("赛季胜场", "倒数第几天"): -3},
                 {("赛季胜场", "倒数第几天"): "abc"}]
        for params in cases:
            for ctx in (None, _FakeCtx(params)):
                win = _monthly_windows(THU_1400, ctx)[0]
                self.assertEqual(win.start.date(), datetime(2026, 9, 29).date(),
                                 f"非法/缺省参数应回退倒数第 2 天 (params={params})")

    def test_negative_index_never_crosses_month_boundary(self):
        feb = datetime(2026, 2, 15, 12, 0, tzinfo=TZ)
        # 2 月仅 28 天：倒数第 29/30/31 天都不允许跨到 1 月
        for target in (-29, -30, -31):
            win = Monthly(days=[target]).windows(feb)[0]
            self.assertEqual(win.start.date(), datetime(2026, 2, 1).date(),
                             f"倒数第 {abs(target)} 天不应跨越当月界限")
        # 30 天的月份：倒数第 31 天收敛到 1 号
        apr = datetime(2026, 4, 10, 12, 0, tzinfo=TZ)
        win = Monthly(days=[-31]).windows(apr)[0]
        self.assertEqual(win.start.date(), datetime(2026, 4, 1).date())
        # 正常范围内不受影响
        win = Monthly(days=[-2]).windows(feb)[0]
        self.assertEqual(win.start.date(), datetime(2026, 2, 27).date())

    def test_task_param_never_crosses_month(self):
        feb = datetime(2026, 2, 10, 12, 0, tzinfo=TZ)
        ctx = _FakeCtx({("赛季胜场", "倒数第几天"): 31})
        win = _monthly_windows(feb, ctx)[0]
        self.assertEqual(win.start.date(), datetime(2026, 2, 1).date())
        self.assertEqual(win.start.month, 2, "任务参数同样不能跨月")

    def test_cross_day_boundary_normalization(self):
        # 3 月 1 日 3:00（早于 5:01 日界）→ 仍归属 2 月，倒数第 2 天为 2 月 27 日
        base = datetime(2026, 3, 1, 3, 0, tzinfo=TZ)
        ctx = _FakeCtx({("赛季胜场", "倒数第几天"): 2})
        win = _monthly_windows(base, ctx)[0]
        self.assertEqual(win.start.date(), datetime(2026, 2, 27).date())

    def test_default_config_schema(self):
        schema = json.loads(DEFAULT_CONFIG.read_text(encoding="utf-8"))
        param = schema["任务"]["赛季胜场"]["执行参数"]["倒数第几天"]
        self.assertEqual(param["类型"], "INT")
        self.assertEqual(param["当前值"], 2, "默认应为倒数第 2 天")
        self.assertEqual(param["最小值"], 1)
        self.assertEqual(param["最大值"], 31)
        self.assertTrue(param["描述"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

