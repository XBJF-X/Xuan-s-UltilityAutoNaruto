# 任务排期（Schedule）开发指南

> 适用版本：v0.17.28+（声明式排期重构）
> 相关代码：`backend/core/legacy/Task/schedule.py`、`backend/core/legacy/Task/BaseTask.py`
> 相关测试：`test_scene/verify_schedule.py`、`test_scene/verify_task_schedules.py`

---

## 1. 一分钟上手

新任务只需在类上声明 `schedule`（一行），**不需要**再重写 `_get_execute_window` /
`get_next_cycle_day` / `_handle_*`：

```python
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn
from backend.core.legacy.Task.schedule import Weekday, Weekly


class XiuXingZhiLu(BaseTask):
    source_scene = "试炼之地"
    task_max_duration = timedelta(minutes=3)
    schedule = Weekly(Weekday.MON)          # ← 全部时间意图都在这
```

框架据它自动完成三件事：

| 关注点 | 由谁负责 |
| --- | --- |
| 现在能不能执行（窗口校验，每轮检查） | `BaseTask._check_execute_window` → `schedule.windows()` |
| 完成后下次什么时候执行（周期） | `on_complete` → `schedule.default_time(after_cycle=True)` |
| 调度器何时算"到期" | 配置项 `下次执行时间`（由上面的结果写入，调度器只读它） |

### 统一约定

- 窗口是**半开区间** `[start, end)`，多窗口之间是**并集**（任一命中即可执行）；
- `DAY_RESET = 5:01` 是唯一日界常量（游戏 5:00 刷新后留 1 分钟余量）；
- 时间一律 `Asia/Shanghai`；`schedule` 是纯函数，因此可单测、可被前端复制做"调度预演"。

---

## 2. 内置排期对照表

| 类 | 语义 | 现有任务示例 |
| --- | --- | --- |
| `Daily()` | 每日 `[5:01, 次日 5:01)` | 绝大多数日常任务（排行榜点赞、购买体力、每日分享…） |
| `Daily(boundary=time(0,0))` | 每日 0:00 日界 | 情报站 |
| `Daily(at=…, until=…)` | 每日限时窗口 | 冬日烟花季 `19:00~22:00`、无差别预选赛 `18:00~22:00` |
| `Daily(at=time(11,0,20))` | 起点精确到秒、终点为次日日界 | 一乐外卖 |
| `Weekly(Weekday.MON)` | 每周 `[本周一 5:01, 下周一 5:01)`（本周内可补跑） | 修行之路、更多玩法、每周胜场、忍法帖族 |
| `Weekly(Weekday.MON, at=time(12,0))` | 周窗口、自定义起点 | 追击晓组织 |
| `Weekly(days=[…])` | 每周多天各执行一次 | （新需求）每周一/三/五 |
| `WeeklySlot(Weekday.WED, time(21,0), time(21,30))` | 每周固定时段（错过等下周） | （可用）周中限时活动 |
| `Monthly(day=-2, span=timedelta(days=2))` | 每月倒数第 2 天 5:01 起 2 天 | 赛季胜场 |
| `Monthly(days=[-2, -1])` | 每月多个日期（支持负索引） | （新需求）月末两天 |
| `Interval(timedelta(days=2), window_span=timedelta(days=2))` | 冷却 / 补领型 | 高级忍者招募 |
| `AnyTime()` | 不受时间限制 | 占位 / 纯手动任务 |
| `Union(a, b)` / `a \| b` | 多窗口并集 | （可用）多个时段 |
| `Custom(fn, cycle=…)` | 逃生舱：窗口依赖任务参数 | 叛忍来袭、巅峰对决、天地战场、要塞争夺战 |

`task.schedule_description`（= `schedule.describe()`）用于日志与调试输出（例如
"跳过窗口校验（排期规则: 每周一 05:01 起整周）"）；前端**不展示**排期信息。

---

## 3. 常见写法

```python
# 每周一/三/五 各执行一次（完成一次后排到下一个选中日）
schedule = Weekly(days=[Weekday.MON, Weekday.WED, Weekday.FRI])

# 每月倒数第 2 天与最后一天各执行一次
schedule = Monthly(days=[-2, -1])

# 每月 15 日 5:01 ~ 22:00
schedule = Monthly(day=15, until=time(22, 0))

# 多窗口并集（周三 + 周六）
schedule = (WeeklySlot(Weekday.WED, time(21, 0), time(21, 30))
            | WeeklySlot(Weekday.SAT, time(20, 0), time(20, 30)))
```

---

## 4. 需要读任务参数时（层 3）

窗口若取决于**本任务或其他任务**的参数，用 `Custom`：

```python
from backend.core.legacy.Task.schedule import Custom, Weekday, WeeklySlot

PARAM_HAS_PANREN = "执行结束后是否有叛忍"
PARAM_PANREN_MINUTE = "本任务执行多少分钟后执行叛忍"


def _wednesday_slot(base, ctx):
    minute = 30
    if ctx is not None and ctx.param("天地战场", PARAM_HAS_PANREN, False):
        running = ctx.param("天地战场", PARAM_PANREN_MINUTE, 0)
        if running:
            minute = running
    return WeeklySlot(Weekday.WED, time(21, 0), time(21, minute)).windows(base)


class TianDiZhanChang(BaseTask):
    schedule = Custom(_wednesday_slot,
                      cycle=lambda base: base + timedelta(weeks=1),
                      describe_text="每周三 21:00 起（终点受叛忍参数影响）")
```

`ctx`（`ScheduleContext`）提供：
`ctx.param(task_name, param_name, default)`、`ctx.now()`、`ctx.tz`、`ctx.last_run_time()`。
`Custom.bind(ctx)` 返回**新实例**，因此类属性不会被实例间污染。

---

## 5. 扩展一个全新的周期类型（层 2）

例如"每 N 周"，继承 `Schedule` 实现 3 个方法即可，框架/前端/配置都不用改：

```python
class EveryNWeeks(Schedule):
    def __init__(self, n: int, weekday: int, at: time = DAY_RESET,
                 anchor: date = date(2025, 9, 20)):
        ...
    def windows(self, base) -> list[Window]: ...        # 该周期的窗口表（可多个 = 并集）
    def next_cycle(self, base): ...                     # 下一周期参考时刻
    def describe(self) -> str: return f"每 {self.n} 周…"
```

同步清单：新增类 + 在 `test_scene/verify_schedule.py` 补表驱动用例 + 文档表格加一行。
（前端不感知排期；持久化格式不变，仍是 `下次执行时间` 时间戳。）

---

## 6. 时间钩子：需要"例外排期"时才覆盖

绝大多数任务**不需要**任何钩子。确实需要时覆盖 `on_*`（旧名 `_handle_*` 仍可用，基类会转发）：

| 钩子 | 触发时机 | 默认行为 |
| --- | --- | --- |
| `on_complete(now)` | 任务正常完成（`TaskCompleted`） | 下一周期的窗口起点 |
| `on_deadline(now)` | 到达窗口终点被强制结束 | 同 `on_complete` |
| `on_timeout(now)` | 超过 `task_max_duration` | 重新按配置排期（`_handle_initialization`） |
| `on_too_early(now)` | 被调度到时尚未进入窗口 | 重新按配置排期 |
| `on_execute_now(now)` | 「立即执行」 | 当前时间（立即到期） |
| `on_delay(now, delta)` | `schedule_next_with_delay(delta)` | `now + delta`（**不受窗口限制**：显式排期意图） |

示例（结束后联动激活另一个任务）：

```python
    def on_complete(self, current_time):
        if self.config.get_task_exe_param(self.task_name, "执行结束后是否有叛忍", True):
            self._activate_another_task("叛忍来袭")
        return self.get_cycle_execute_time(current_time, completed=True)
```

### 「立即执行 / 被激活 / 预设顺序执行」的窗口语义

`BaseTask._should_skip_window_check()` 为真时不走窗口校验（显式意图优先）：

- `force_execute_now`：用户在总览点「执行」，或被其它任务激活；
- `ignore_time_window`：临时预设模式按顺序执行时由调度器置位。

其余情况按声明式排期校验窗口，不合规抛 `TooEarlyToRun`（未到）/ `TimeOutDeadLineError`（已过）。

---

## 7. 迁移与清理状态

- **全部任务已迁移为声明式排期**（含曾用旧 `start_line` 写法的排行榜点赞/冬日烟花季/无差别预选赛/一乐外卖）：
  情报站、冬日烟花季、无差别预选赛、一乐外卖、排行榜点赞、高级忍者招募、修行之路、更多玩法、
  每周胜场、忍法帖点赞分享、忍法帖奖励、追击晓组织、赛季胜场、巅峰对决、天地战场、要塞争夺战、
  叛忍来袭、消耗体力（统一日界 5:01）。
- **旧兼容层已删除**：`start_line` / `dead_line` 类属性与自动映射、6 个 `_handle_*` 转发别名、
  弃用的 `@debug_execute_window` 装饰器全部移除；预设（临时预设）模式的"忽略时间窗口"
  改由显式的 `BaseTask.ignore_time_window` 标记表达（不再靠清空 `start_line` 的 hack）。
- **保留的框架入口**：`_get_execute_window` / `get_next_cycle_day` / `get_cycle_execute_time`
  由 `schedule` 驱动，任务侧无需重写、也不应重写。
- **顺带修复**：`_check_window_invalid` 由"交集判定"改为**并集判定**（多窗口任务不再被误判越界）。

---

## 8. 验证与调试

| 目的 | 命令 |
| --- | --- |
| 排期语义单测（窗口/周期/组合子/扩展示例） | `.venv\Scripts\python.exe test_scene\verify_schedule.py` |
| 全任务排期等价性 + 钩子别名 + 快照字段 | `.venv\Scripts\python.exe test_scene\verify_task_schedules.py` |
| 既有调度/激活回归 | `verify_force_preempt.py`、`verify_scheduled_activation.py`、`verify_activation_path_fix.py`、`verify_temp_activation_restore.py` |

新增任务的验收清单：

1. 声明 `schedule`（或确认默认日窗口正确），不重写窗口/周期方法；
2. `schedule.describe()` 文案能准确说明窗口与周期；
3. 在 `test_scene/verify_task_schedules.py` 加一条窗口断言（迁移前行为 = 迁移后行为）；
4. 跑 `test_scene` 下全部 `verify_*.py`。
