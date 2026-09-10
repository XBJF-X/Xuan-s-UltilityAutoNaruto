# -*- coding: utf-8 -*-
"""任务可执行时间窗口 / 周期的声明式描述（Schedule）。

设计目标
--------
1. 任务只需声明"何时可执行 + 多久一个周期"，框架负责窗口校验与"下次执行时间"计算；
2. 声明是纯函数（给定基准时刻 → 确定的窗口表），可单测、可被前端"调度预演"复用；
3. 新增周期类型（每 N 周、每月多个日期、活动期等）只需新增一个 Schedule 子类或用
   组合子 ``Union`` / ``Custom``，**无需改动 BaseTask / 调度器 / 前端**。

统一约定
--------
- 时间一律为带时区的感知时间（由传入的 base 决定时区，生产环境为 Asia/Shanghai）；
- 窗口是半开区间 ``[start, end)``，多窗口之间取**并集**（``contains`` 为 any）；
- ``DAY_RESET = 5:01`` 是游戏每日 5:00 刷新后的统一日界，也是唯一的时间常量；
- 周期归一化（"几点之前算前一天"）以 ``boundary`` 为准（默认 ``DAY_RESET``），
  与窗口起点 ``at`` 解耦：例如冬日烟花季窗口为 19:00~22:00，但日界仍是 5:01。

扩展指引
--------
- 只需"多个星期/多个日期"时直接用参数：``Weekly(days=[Weekday.MON, ...])``、
  ``Monthly(days=[-2, -1])``（负索引 = 倒数第几天），不用新增类；
- 新的**周期语义**（如每 N 周）：继承 ``Schedule`` 实现 ``windows`` / ``next_cycle`` /
  ``describe`` 三个方法即可，窗口表自行组织（可以多窗口）；
- 窗口依赖任务参数（如叛忍来袭依赖"天地战场/要塞争夺战"的参数）：用 ``Custom``，
  其 ``fn(base, ctx)`` 中的 ``ctx`` 提供 ``param(task, name, default)`` 实时读取配置。
"""
from __future__ import annotations

import dataclasses
import datetime as _dt
from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Any, Callable, Iterable, List

DAY_RESET = _dt.time(5, 1)
"""游戏每日 5:00 刷新，留 1 分钟余量，作为统一日界常量"""


class Weekday(IntEnum):
    """星期枚举（与 ``datetime.date.weekday()`` 一致：周一 = 0）"""

    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6


@dataclasses.dataclass(frozen=True)
class Window:
    """一个可执行窗口（半开区间 ``[start, end)``；None 表示该侧无界）"""

    start: _dt.datetime | None
    end: _dt.datetime | None

    def contains(self, dt: _dt.datetime) -> bool:
        if self.start is not None and dt < self.start:
            return False
        if self.end is not None and dt >= self.end:
            return False
        return True

    @property
    def duration(self) -> _dt.timedelta | None:
        if self.start is None or self.end is None:
            return None
        return self.end - self.start

    def __str__(self) -> str:
        fmt = "%Y-%m-%d %H:%M:%S"

        def _f(value: _dt.datetime | None) -> str:
            return value.strftime(fmt) if value is not None else "-"

        return f"{_f(self.start)} ~ {_f(self.end)}"


@dataclasses.dataclass
class ScheduleContext:
    """Schedule 绑定任务后可用的上下文（读取任务参数 / 当前时间 / 时区）。

    自定义 Schedule 通过它读配置，无需继承 BaseTask，也不需要改动框架。
    """

    tz: _dt.tzinfo
    param: Callable[[str, str, Any], Any]
    """``param(task_name, param_name, default)`` → 读取任务执行参数"""

    now: Callable[[], _dt.datetime] = lambda: _dt.datetime.now()
    """返回当前时间（供需要"此刻"的排期使用）"""

    last_run_time: Callable[[], _dt.datetime | None] = lambda: None
    """返回任务本次运行的开始时间（可能为 None）"""


# --------------------------------------------------------------------------- #
#                                 基类与工具                                   #
# --------------------------------------------------------------------------- #
def _cycle_day(base: _dt.datetime, boundary: _dt.time) -> _dt.date:
    """按日界 boundary 归一化：早于日界视为前一天。"""
    day = base.date()
    if boundary is not None and base.time() < boundary:
        day -= _dt.timedelta(days=1)
    return day


def _combine(day: _dt.date, at: _dt.time, tz: _dt.tzinfo) -> _dt.datetime:
    return _dt.datetime.combine(day, at, tzinfo=tz)


def _fmt_time(value: _dt.time) -> str:
    return value.strftime("%H:%M" if value.second == 0 else "%H:%M:%S")


def _fmt_weekday(value: int) -> str:
    names = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")
    return names[int(value) % 7]


class Schedule(ABC):
    """可执行时间窗口 + 周期。所有实现必须是纯函数（无副作用）。"""

    # ---- 绑定任务上下文（需要读任务参数的自定义排期可覆盖） ----
    def bind(self, ctx: ScheduleContext) -> "Schedule":
        """默认返回自身；需要读配置的实现可在此保存 ctx 并返回新实例。"""
        return self

    # ---- 核心：窗口表 ----
    @abstractmethod
    def windows(self, base: _dt.datetime) -> List[Window]:
        """返回 base 所属周期内的所有窗口（按 start 升序，多窗口 = 并集）。"""

    def contains(self, dt: _dt.datetime, base: _dt.datetime) -> bool:
        """dt 是否落在 base 所属周期的任一窗口内（并集语义）。"""
        return any(w.contains(dt) for w in self.windows(base))

    # ---- 周期 ----
    @abstractmethod
    def next_cycle(self, base: _dt.datetime) -> _dt.datetime:
        """返回"下一个周期"的参考时刻（用于 completed / 跨周期排期校验）。"""

    def default_time(self, base: _dt.datetime,
                     *, after_cycle: bool = False) -> _dt.datetime:
        """本周期（``after_cycle=True`` 时为下一周期）的默认执行时刻。

        默认实现 = 该周期第一个窗口的起点，与原 ``get_cycle_execute_time`` 语义一致。
        """
        ref = self.next_cycle(base) if after_cycle else base
        wins = self.windows(ref)
        if not wins:
            raise ValueError(f"{type(self).__name__} 未产生任何窗口，无法计算默认执行时间")
        start = wins[0].start
        if start is None:
            raise ValueError(f"{type(self).__name__} 首个窗口无起点，无法计算默认执行时间")
        return start

    # ---- 展示 ----
    def describe(self) -> str:
        """人类可读描述（日志 / 前端任务详情展示）。"""
        return type(self).__name__

    # ---- 组合子 ----
    def __or__(self, other: "Schedule") -> "Schedule":
        return Union(self, other)


# --------------------------------------------------------------------------- #
#                                  内置排期                                    #
# --------------------------------------------------------------------------- #
class Daily(Schedule):
    """每日窗口。

    - ``at``：窗口起点（默认 = 日界 5:01）
    - ``until``：窗口终点（默认 = 次日日界，即窗口覆盖整个"游戏日"）
    - ``boundary``：日界（默认 5:01），只用于"几点之前算前一天"的归一化

    示例::

        Daily()                                  # 每日 5:01 ~ 次日 5:01
        Daily(boundary=time(0, 0))               # 每日 0:00 ~ 次日 0:00（情报站）
        Daily(at=time(19, 0), until=time(22, 0)) # 每日 19:00 ~ 22:00（冬日烟花季）
        Daily(at=time(11, 0, 20))                # 每日 11:00:20 ~ 次日 5:01（一乐外卖）
    """

    def __init__(self, at: _dt.time | None = None,
                 until: _dt.time | None = None,
                 *, boundary: _dt.time = DAY_RESET):
        self.boundary = boundary
        self.at = at if at is not None else boundary
        self.until = until

    def windows(self, base: _dt.datetime) -> List[Window]:
        day = _cycle_day(base, self.boundary)
        start = _combine(day, self.at, base.tzinfo)
        if self.until is None:
            end = _combine(day + _dt.timedelta(days=1), self.boundary, base.tzinfo)
        else:
            end = _combine(day, self.until, base.tzinfo)
            if end <= start:
                end += _dt.timedelta(days=1)
        return [Window(start, end)]

    def next_cycle(self, base: _dt.datetime) -> _dt.datetime:
        return base + _dt.timedelta(days=1)

    def describe(self) -> str:
        if self.at == self.boundary and self.until is None:
            return f"每日 {_fmt_time(self.boundary)}（日界）"
        if self.until is None:
            return f"每日 {_fmt_time(self.at)} ~ 次日 {_fmt_time(self.boundary)}"
        return f"每日 {_fmt_time(self.at)} ~ {_fmt_time(self.until)}"


class Weekly(Schedule):
    """每周窗口。

    两种语义（由是否只给一个星期决定，可用 ``span`` 显式覆盖）：

    - **整周窗口**（单 weekday）：``[本周该日 at, 下周同日日界)``，
      本周内任何时间都可执行一次（周一错过可在周二~周日补跑）；
    - **按日窗口**（多 days）：每个选中日各自 ``[该日 at, 次日日界)``，窗口并集，
      完成一次后下次排到"下一个选中日"（如每周一/三/五）。

    示例::

        Weekly(Weekday.MON)                          # 每周一 5:01 起整周（修行之路等）
        Weekly(Weekday.MON, at=time(12, 0))          # 每周一 12:00 起整周（追击晓组织）
        Weekly(days=[Weekday.MON, Weekday.FRI])      # 每周一/五 各执行一次
        Weekly(Weekday.MON, span=timedelta(days=3))  # 每周一 5:01 起 3 天窗口
    """

    def __init__(self, weekday: int | None = None, *,
                 days: Iterable[int] | None = None,
                 at: _dt.time | None = None,
                 span: _dt.timedelta | None = None,
                 boundary: _dt.time = DAY_RESET):
        if days is not None:
            picked = [int(d) % 7 for d in days]
        elif weekday is not None:
            picked = [int(weekday) % 7]
        else:
            raise ValueError("Weekly 需要 weekday 或 days 指定星期几")
        if not picked:
            raise ValueError("Weekly 的 days 不能为空")
        self.days = sorted(set(picked))
        self.boundary = boundary
        self.at = at if at is not None else boundary
        self.span = span
        # 单 weekday 且未显式指定跨度 → 整周窗口；多天 → 各自按日窗口
        self.whole_week = span is None and len(self.days) == 1

    def windows(self, base: _dt.datetime) -> List[Window]:
        day = _cycle_day(base, self.boundary)
        week_start = day - _dt.timedelta(days=day.weekday())
        wins: List[Window] = []
        for target in self.days:
            win_day = week_start + _dt.timedelta(days=target)
            start = _combine(win_day, self.at, base.tzinfo)
            if self.span is not None:
                end = start + self.span
            elif self.whole_week:
                end = _combine(win_day + _dt.timedelta(days=7), self.boundary, base.tzinfo)
            else:
                end = _combine(win_day + _dt.timedelta(days=1), self.boundary, base.tzinfo)
            wins.append(Window(start, end))
        wins.sort(key=lambda w: w.start or base)
        return wins

    def next_cycle(self, base: _dt.datetime) -> _dt.datetime:
        if self.whole_week:
            return base + _dt.timedelta(weeks=1)
        # 多天模式：严格下一个选中日的窗口起点
        candidates: List[_dt.datetime] = []
        for target in self.days:
            delta = (target - base.weekday()) % 7
            cand = _combine(base.date() + _dt.timedelta(days=delta), self.at, base.tzinfo)
            if cand <= base:
                cand += _dt.timedelta(days=7)
            candidates.append(cand)
        return min(candidates)

    def describe(self) -> str:
        names = "/".join(_fmt_weekday(d) for d in self.days)
        if self.span is not None:
            return f"每{names} {_fmt_time(self.at)} 起 {self.span}"
        if self.whole_week:
            return f"每{names} {_fmt_time(self.at)} 起整周"
        return f"每{names} 各执行一次（{_fmt_time(self.at)} 起）"


class WeeklySlot(Schedule):
    """每周固定时段的窗口（错过等下一周），如"每周三 21:00~21:30"。

    示例::

        WeeklySlot(Weekday.WED, time(21, 0), time(21, 30))   # 巅峰对决/天地战场
        WeeklySlot(Weekday.SAT, time(20, 0), time(20, 30))   # 要塞争夺战
        WeeklySlot(Weekday.WED, time(21, 0), span=timedelta(minutes=45))
    """

    def __init__(self, weekday: int, start: _dt.time,
                 end: _dt.time | None = None, *,
                 span: _dt.timedelta | None = None,
                 boundary: _dt.time = DAY_RESET):
        if end is None and span is None:
            raise ValueError("WeeklySlot 需要 end 或 span 指定窗口终点")
        self.weekday = int(weekday) % 7
        self.start = start
        self.end = end
        self.span = span
        self.boundary = boundary

    def windows(self, base: _dt.datetime) -> List[Window]:
        day = _cycle_day(base, self.boundary)
        week_start = day - _dt.timedelta(days=day.weekday())
        win_day = week_start + _dt.timedelta(days=self.weekday)
        start = _combine(win_day, self.start, base.tzinfo)
        if self.span is not None:
            end = start + self.span
        else:
            assert self.end is not None  # 构造时已校验
            end = _combine(win_day, self.end, base.tzinfo)
            if end <= start:
                end += _dt.timedelta(days=1)
        return [Window(start, end)]

    def next_cycle(self, base: _dt.datetime) -> _dt.datetime:
        return base + _dt.timedelta(weeks=1)

    def describe(self) -> str:
        if self.span is not None:
            end_text = str(self.span)
        elif self.end is not None:
            end_text = _fmt_time(self.end)
        else:
            end_text = "-"
        return f"每周{_fmt_weekday(self.weekday)} {_fmt_time(self.start)} ~ {end_text}"


class Monthly(Schedule):
    """每月窗口。

    - ``day`` / ``days``：每月第几天（正数 1..31；**负索引 = 倒数第几天**，
      ``-1`` 为月末、``-2`` 为倒数第 2 天；负索引超出当月天数时收敛到当月 1 号，
      **不跨越当月界限**）；
    - ``at``：窗口起点（默认日界 5:01）；
    - ``span``：窗口长度（默认 1 天）；
    - ``boundary``：日界（默认 5:01），"几点之前算上个月"的归一化基准。

    示例::

        Monthly(day=-2, span=timedelta(days=2))   # 每月倒数第 2 天 5:01 起 2 天（赛季胜场）
        Monthly(days=[-2, -1])                    # 每月倒数第 2 天与最后一天各执行一次
        Monthly(day=15, until=time(22, 0))        # 每月 15 日 5:01 ~ 22:00
    """

    def __init__(self, day: int | None = None, *,
                 days: Iterable[int] | None = None,
                 at: _dt.time | None = None,
                 until: _dt.time | None = None,
                 span: _dt.timedelta | None = None,
                 boundary: _dt.time = DAY_RESET):
        if days is not None:
            picked = [int(d) for d in days]
        elif day is not None:
            picked = [int(day)]
        else:
            raise ValueError("Monthly 需要 day 或 days 指定每月第几天")
        if not picked:
            raise ValueError("Monthly 的 days 不能为空")
        if any(d == 0 for d in picked):
            raise ValueError("Monthly 的日期不支持 0（正数第几天或负数为倒数第几天）")
        self.days = sorted(set(picked))
        self.boundary = boundary
        self.at = at if at is not None else boundary
        self.until = until
        self.span = span

    @staticmethod
    def _last_day_of(month_day: _dt.date) -> _dt.date:
        """返回 month_day 所在月的最后一天（不依赖 calendar 模块）。"""
        next_month = month_day.replace(day=28) + _dt.timedelta(days=4)
        return next_month - _dt.timedelta(days=next_month.day)

    def _resolve(self, cycle_day: _dt.date, target: int) -> _dt.date:
        """把"每月第几天（支持负索引）"解析为具体日期。

        - 正数：超过当月天数时收敛到当月末；
        - 负数（倒数第几天）：超过当月天数时**不跨越当月界限**，收敛到当月 1 号
          （例如 2 月设为"倒数第 30 天" → 2 月 1 日，而不是 1 月 30 日）。
        """
        first_day = cycle_day.replace(day=1)
        if target > 0:
            try:
                return cycle_day.replace(day=target)
            except ValueError:
                return self._last_day_of(cycle_day)
        last_day = self._last_day_of(cycle_day)
        resolved = last_day - _dt.timedelta(days=abs(target) - 1)
        return max(resolved, first_day)

    def windows(self, base: _dt.datetime) -> List[Window]:
        cycle_day = _cycle_day(base, self.boundary)
        wins: List[Window] = []
        for target in self.days:
            win_day = self._resolve(cycle_day, target)
            start = _combine(win_day, self.at, base.tzinfo)
            if self.span is not None:
                end = start + self.span
            elif self.until is not None:
                end = _combine(win_day, self.until, base.tzinfo)
                if end <= start:
                    end += _dt.timedelta(days=1)
            else:
                end = _combine(win_day + _dt.timedelta(days=1), self.boundary, base.tzinfo)
            wins.append(Window(start, end))
        wins.sort(key=lambda w: w.start or base)
        return wins

    def next_cycle(self, base: _dt.datetime) -> _dt.datetime:
        # 与旧版 SaiJiShengChang.get_next_cycle_day 等价：推进到"下月月初"
        return base.replace(day=28) + _dt.timedelta(days=4)

    def describe(self) -> str:
        def _label(target: int) -> str:
            return (f"{target} 日" if target > 0 else f"倒数第 {abs(target)} 天")

        names = "/".join(_label(d) for d in self.days)
        if self.span is not None:
            tail = f"起 {self.span}"
        elif self.until is not None:
            tail = f"起至 {_fmt_time(self.until)}"
        else:
            tail = ""
        return f"每月{names} {_fmt_time(self.at)} {tail}".strip()


class Interval(Schedule):
    """固定间隔型（冷却 / 补领）：本次结束后 ``delta`` 再执行。

    - 窗口仍按日窗口校验（默认 ``[当日 at, 当日 at + window_span)``），
      保留旧任务"窗口外不执行"的行为；
    - ``default_time(..., after_cycle=True)`` 返回 ``base + delta``（而非周期起点），
      这是与其它排期唯一的语义差别；
    - 需要完全不受窗口限制时用 ``AnyTime``。

    示例::

        Interval(timedelta(days=2), window_span=timedelta(days=2))  # 高级招募
        Interval(timedelta(hours=3))                                # 活跃度奖励补领
    """

    def __init__(self, delta: _dt.timedelta, *,
                 at: _dt.time | None = None,
                 window_span: _dt.timedelta = _dt.timedelta(days=1),
                 boundary: _dt.time = DAY_RESET):
        self.delta = delta
        self.boundary = boundary
        self.at = at if at is not None else boundary
        self.window_span = window_span

    def windows(self, base: _dt.datetime) -> List[Window]:
        day = _cycle_day(base, self.boundary)
        start = _combine(day, self.at, base.tzinfo)
        return [Window(start, start + self.window_span)]

    def next_cycle(self, base: _dt.datetime) -> _dt.datetime:
        return base + self.delta

    def default_time(self, base: _dt.datetime,
                     *, after_cycle: bool = False) -> _dt.datetime:
        return base + self.delta if after_cycle else base

    def describe(self) -> str:
        return (f"间隔 {self.delta}"
                f"（窗口 {_fmt_time(self.at)} 起 {self.window_span}）")


class AnyTime(Schedule):
    """不受时间窗口限制（占位 / 纯手动触发的任务）。"""

    def windows(self, base: _dt.datetime) -> List[Window]:
        return [Window(None, None)]

    def next_cycle(self, base: _dt.datetime) -> _dt.datetime:
        return base + _dt.timedelta(days=1)

    def default_time(self, base: _dt.datetime,
                     *, after_cycle: bool = False) -> _dt.datetime:
        return base

    def describe(self) -> str:
        return "不限时间"


class Union(Schedule):
    """多个排期的并集（任一窗口可执行），用于多窗口任务（如叛忍来袭）。

    示例::

        Union(WeeklySlot(Weekday.WED, time(21, 0), time(21, 30)),
              WeeklySlot(Weekday.SAT, time(20, 0), time(20, 30)))
    """

    def __init__(self, *schedules: Schedule):
        if not schedules:
            raise ValueError("Union 至少需要一个排期")
        self.schedules: List[Schedule] = list(schedules)

    def bind(self, ctx: ScheduleContext) -> "Schedule":
        return Union(*[s.bind(ctx) for s in self.schedules])

    def windows(self, base: _dt.datetime) -> List[Window]:
        wins: List[Window] = []
        for sched in self.schedules:
            wins.extend(sched.windows(base))
        wins.sort(key=lambda w: w.start or base)
        return wins

    def next_cycle(self, base: _dt.datetime) -> _dt.datetime:
        return min(s.next_cycle(base) for s in self.schedules)

    def default_time(self, base: _dt.datetime,
                     *, after_cycle: bool = False) -> _dt.datetime:
        if after_cycle:
            return min(s.default_time(base, after_cycle=True) for s in self.schedules)
        starts = [w.start for w in self.windows(base) if w.start is not None]
        if not starts:
            raise ValueError("Union 未产生任何带起点的窗口")
        return min(starts)

    def describe(self) -> str:
        return " 或 ".join(s.describe() for s in self.schedules)


class Custom(Schedule):
    """逃生舱：窗口/周期完全自定义，可读取任务参数。

    ``fn(base, ctx)`` 返回窗口列表；``ctx`` 为 :class:`ScheduleContext`（未绑定时为 None），
    通过 ``ctx.param("其它任务名", "参数名", 默认值)`` 即可实现"窗口取决于别的任务参数"。
    """

    def __init__(self, fn: Callable[[_dt.datetime, ScheduleContext | None], Iterable[Window]],
                 *, cycle: Callable[[_dt.datetime], _dt.datetime] | None = None,
                 describe_text: str = "自定义窗口"):
        self.fn = fn
        self.cycle = cycle
        self.describe_text = describe_text
        self._ctx: ScheduleContext | None = None

    def bind(self, ctx: ScheduleContext) -> "Schedule":
        bound = Custom(self.fn, cycle=self.cycle, describe_text=self.describe_text)
        bound._ctx = ctx
        return bound

    def windows(self, base: _dt.datetime) -> List[Window]:
        wins = list(self.fn(base, self._ctx))
        wins.sort(key=lambda w: w.start or base)
        return wins

    def next_cycle(self, base: _dt.datetime) -> _dt.datetime:
        if self.cycle is not None:
            return self.cycle(base)
        return base + _dt.timedelta(days=1)

    def describe(self) -> str:
        return self.describe_text


__all__ = [
    "DAY_RESET",
    "Weekday",
    "Window",
    "ScheduleContext",
    "Schedule",
    "Daily",
    "Weekly",
    "WeeklySlot",
    "Monthly",
    "Interval",
    "AnyTime",
    "Union",
    "Custom",
]
