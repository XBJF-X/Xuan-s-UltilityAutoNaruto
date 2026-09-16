import datetime
import functools
import inspect
import logging
import threading
import time
from datetime import timedelta
from enum import IntEnum
from logging import Logger
from pathlib import Path
from typing import Dict, Callable, List, Optional, Tuple
from zoneinfo import ZoneInfo

from backend.utils import get_real_path
from backend.core.legacy.Config import Config
from backend.core.legacy.Exceptions import (
    StepFailedError,
    TimeOutDeadLineError,
    TimeOutMaxDurationError,
    Stop,
    TaskCompleted,
    TooEarlyToRun,
    STUCK_STOP_REASONS,
)
from backend.core.legacy.Operationer import Operationer
from backend.core.legacy.Scene.TransitionManager import TransitionManager
from backend.core.legacy.Task.schedule import Daily, Schedule, ScheduleContext
from backend.core.scheduler.runtime import RuntimeContext


# --------------------------------------------------------------------------- #
#                 执行日志 / 错误截图的公共常量与格式化助手（模块级）              #
# --------------------------------------------------------------------------- #
# 错误自动截图的原因标记：写入截图文件名，便于区分错误类型（也是反馈打包的筛选依据）。
# 取值沿用历史约定，避免既有截图命名规则失效。
SCREENSHOT_REASON_STEP_FAILED = "StepFailedError"
SCREENSHOT_REASON_DEADLINE = "TimeOutDeadLineError"
SCREENSHOT_REASON_MAX_DURATION = "TimeOutMaxDurationError"
SCREENSHOT_REASON_UNKNOWN = "UnknownError"
SCREENSHOT_REASON_UNREGISTERED_SCENE = "UnregisteredSceneForceReturn"
# 待跳转目标连续多次未推进（跳转函数不改变画面 / 目标在当前画面不可达）
SCREENSHOT_REASON_JUMP_STALLED = "JumpStalled"


def _format_duration(seconds: float) -> str:
    """秒数 → 日志用可读时长（12.3s / 10m00s / 1h05m）。"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    if seconds < 3600:
        return f"{int(seconds // 60)}m{int(seconds % 60):02d}s"
    return f"{int(seconds // 3600)}h{int(seconds % 3600 // 60):02d}m"


def _format_datetime(dt: datetime.datetime) -> str:
    """时间 → 日志统一格式（与配置中"下次执行时间"的可读形式一致）。"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _format_exception(e: BaseException) -> str:
    """异常 →"类型: 消息"（无消息时只留类型），便于日志检索定位。"""
    return f"{type(e).__name__}: {e}" if str(e) else type(e).__name__


class TaskType(IntEnum):
    """任务类型枚举（「临时」类别已取消，改为每个任务独立的「是否临时」布尔属性）"""
    DAILY = 0
    WEEKLY = 1
    MONTHLY = 2
    PERIODIC = 3
    ACTIVITY = 4


class TransitionOn:
    scenes = []
    funcs = []

    def __init__(self, scene: str | list[str] | None = None):
        self.__class__.scenes.append(scene)

    def __call__(self, func):
        if func.__name__ != "_":
            self.__class__.scenes = []
            self.__class__.funcs = []
            raise Exception('TransitionOn装饰的函数名必须是"_"')
        self.__class__.funcs.append(func)

        return self

    def __set_name__(self, owner, name):
        if not hasattr(owner, "source_scene"):
            raise Exception(f"{owner.__name__}没有设置source_scene属性")
        owner.transition_func = {}
        for scene, func in zip(self.scenes, self.funcs):
            if scene is None:
                scene = owner.source_scene
            if not isinstance(scene, list):
                scene = [scene]
            for s in scene:
                owner.transition_func[s] = func
        self.__class__.scenes = []
        self.__class__.funcs = []


def handle_transition_exceptions(func):
    """transition 装饰器：输出本轮 transition 的返回位置（DEBUG），便于定位步骤。

    返回位置由 ``BaseTask._record_transition_source`` 在调用场景处理函数时静态取得；
    不再使用 ``sys.settrace`` 全程跟踪——旧实现会为整个任务执行线程开启 tracing，
    开销大，且记录的是"最后一条 return 事件"，位置并不精确。
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        self.transition_return = ""
        result = func(self, *args, **kwargs)
        if self.transition_return:
            self.logger.debug(f"transition 返回位置: {self.transition_return}")
        return result

    return wrapper


def handle_task_exceptions(func):
    """任务执行装饰器：统一"开始 → 分类处理 → 结束汇总"的执行日志与收尾动作。

    每次执行固定输出：一行开始摘要（INFO）→ 按需的分支日志 → 一行结束汇总（INFO）。

    异常 → 结果 / 级别 / 收尾动作：

    - TaskCompleted        完成         INFO  清理 + 重排期（任务未自行写入时）
    - TooEarlyToRun        未到执行时间  INFO  清理 + 重排期
    - StepFailedError      步骤失败     ERROR 错误截图 + 清理 + 冷却重试
    - Stop                 被停止       WARN  仅清理（被抢占任务按原下次执行时间继续）
    - TimeOutDeadLineError 窗口超时     ERROR 错误截图 + 清理 + 重排期
    - TimeOutMaxDuration   执行超时     ERROR 错误截图 + 清理 + 重排期
    - Exception            未捕获异常   ERROR 错误截图（含 traceback）+ 清理 + 冷却重试

    说明：StepFailedError / 未捕获异常过去既不清理也不重排期，而"下次执行时间"仍是
    过期时刻、会被调度器立刻判为到期，导致按扫描间隔（默认 1s）无限重试；现改为
    冷却重试（``error_retry_delay``，任务类可覆盖）。

    场景处理函数的返回值约定（见 `BaseTask.declare_next_scene`）：

    - 返回 ``True`` 或抛 ``TaskCompleted`` → **任务完成**；
    - 返回**场景名字符串** → 声明落点（``operationer.next_scene``），本轮**不算完成**，
      下一轮由 `_pending_jump_path` 做"到达即清空 / 未到达按图纠偏 / 连续跳不动则放弃"；
    - 返回 ``False`` / ``None`` → 继续循环（旧行为，逐字不变）。
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        started_at = time.perf_counter()
        self._reset_execute_log_state()
        self.logger.info(self._describe_execute_start())
        self.last_execute_error = None
        before_next_execute_ts = self.config.get_task_base_config(
            self.task_name, "下次执行时间")
        reason, detail = "结束", ""
        try:
            func(self, *args, **kwargs)
        except TaskCompleted as e:
            reason = "完成"
            # 完成消息可能带业务说明（如"组织争霸任务暂未实现"），需保留到汇总日志
            if str(e) and str(e) != "任务执行完成":
                detail = str(e)
            self._cleanup_on_complete()
            after_next_execute_ts = self.config.get_task_base_config(
                self.task_name, "下次执行时间")
            if after_next_execute_ts == before_next_execute_ts:
                self.schedule_next_on_complete()
            if getattr(self, "is_temp", False):
                # 临时任务不持久化启用状态，避免污染预设文件
                if self.config.config_type != "临时":
                    self.config.set_task_base_config(self.task_name, "是否启用", False)
        except TooEarlyToRun as e:
            reason = "未到执行时间"
            detail = str(e) or "任务当前时间不在任何可执行窗口内"
            self._cleanup_on_too_early()
            self.schedule_next_on_too_early()
        except StepFailedError as e:
            reason = "步骤失败"
            self.last_execute_error = str(e)
            self._log_execute_error(
                "步骤执行失败", e,
                self._auto_screenshot(SCREENSHOT_REASON_STEP_FAILED),
                self._describe_retry())
            self._cleanup_on_error()
            self.schedule_next_with_delay(self.error_retry_delay)
        except Stop:
            reason = "被停止"
            if getattr(self, "stop_reason", "") in STUCK_STOP_REASONS:
                # 卡死类停止（任务自救失败 / 监视器兜底后强制停止）：
                # 必须重新排期，否则"下次执行时间"仍停在过去时刻，会被调度器按扫描
                # 间隔立刻重跑并反复截图。默认与步骤失败一致（冷却重试），任务可覆盖 on_stuck。
                reason = "卡死停止"
                self.logger.warning(
                    "收到卡死类停止请求（自救失败），按 on_stuck 重新排期")
                self._cleanup_on_stop()
                self.schedule_next_on_stuck()
            else:
                self.logger.warning(
                    "收到停止请求，正在清理（被抢占/被停止的任务按原下次执行时间继续）")
                self._cleanup_on_stop()
        except TimeOutDeadLineError as e:
            reason = "窗口超时"
            self.last_execute_error = str(e)
            self._log_execute_error(
                "窗口超时（已到达可执行窗口截止时间）", e,
                self._auto_screenshot(SCREENSHOT_REASON_DEADLINE))
            self._cleanup_on_timeout()
            self.schedule_next_on_timeout_deadline()
        except TimeOutMaxDurationError as e:
            reason = "执行超时"
            self.last_execute_error = str(e)
            max_duration = _format_duration(self.task_max_duration.total_seconds())
            self._log_execute_error(
                f"执行超时（超过最长执行时长 {max_duration}）", e,
                self._auto_screenshot(SCREENSHOT_REASON_MAX_DURATION))
            self._cleanup_on_timeout()
            self.schedule_next_on_timeout_max_duration()
        except Exception as e:
            reason = "未捕获异常"
            self.last_execute_error = str(e)
            self._log_execute_error(
                "未捕获异常", e,
                self._auto_screenshot(SCREENSHOT_REASON_UNKNOWN),
                self._describe_retry(), with_traceback=True)
            self._cleanup_on_error()
            self.schedule_next_with_delay(self.error_retry_delay)
        finally:
            try:
                self.bool_click = False
                self.logger.debug("任务结束回调执行")
                self.callback(self)
            except Exception as e:
                self.logger.error(f"✖ 调度回调失败: {_format_exception(e)}",
                                  exc_info=True)
            self.logger.info(
                self._describe_execute_summary(reason, started_at, detail))

    return wrapper


class BaseTask:

    transition_func: Dict[str, Callable] = {}
    """场景名到处理函数的映射，由TransitionOn装饰器填充"""
    transition_return: str = ""
    """最近一次 transition 内场景处理函数的源码位置（file:line），用于调试与错误定位"""
    source_scene: str | None = None
    """任务的初始场景，需要先寻路到此处才能正式开始执行任务"""

    base_priority: int
    """基础优先级，数值越小优先级越高"""
    click_priority: int
    """执行连点时的优先级，数值越小优先级越高"""

    schedule: Schedule = Daily()
    """任务的声明式时间排期（可执行窗口 + 周期）。

    新任务只需改这一行，例如 ``schedule = Weekly(Weekday.MON)``；
    框架据它计算窗口与"下次执行时间"，无需再写窗口/周期方法。
    窗口依赖任务参数时用 ``Custom``（bind 后经 ScheduleContext 实时读配置）。
    """

    ignore_time_window: bool = False
    """是否忽略可执行窗口校验（预设顺序执行等场景由调度器置 True；任务自身一般不用）"""

    task_max_duration: timedelta = timedelta(minutes=10)
    """任务最长执行时间（无DDL的情况下生效）"""

    error_retry_delay: timedelta = timedelta(minutes=5)
    """步骤失败 / 未捕获异常后的冷却重试间隔（任务类可覆盖）。

    过去这两类失败既不清理也不重排期，"下次执行时间"仍是过期时刻，会被调度器
    立刻判为到期 → 按扫描间隔（默认 1s）无限重试并反复截图；改为冷却重试。
    """

    scene_stuck_seconds: Optional[float] = None
    """场景停滞判定阈值（秒），由超时监视器（TimeoutWatchdog）读取，任务类可覆盖。

    优先用**更精确的** `declare_waiting` / `wait_for` 声明"我在等"（等待期间自动改用
    「超时检测-等待超时秒」，粒度到场景、且不会把真实卡死一起延后）；本属性只在需要
    整体放宽某任务的停滞判定时才用。

    - ``None``（默认）：沿用全局配置 ``超时检测-场景停滞秒数``（默认 180 秒），
      即与旧行为逐字等价；
    - ``> 0``：该任务在同一场景停留超过此秒数才判定「场景停滞」；
    - ``<= 0``：该任务不做「场景停滞」判定（心跳失效时的临时关闭语义一致）。

    仅作用于「场景停滞」，不影响画面静止类判定（游戏卡死/模拟器卡死），
    也不影响全局配置项本身的语义；非法值（非数字/NaN）由监视器回退默认并告警。
    """

    tz_info = ZoneInfo("Asia/Shanghai")

    UNREGISTER_SCENE_MAX_TIME = 15
    """识别不到注册场景（且不在转移图上）时，等待多久才强制回 source_scene。"""

    graph_known_scene_immediate_return = True
    """「场景图已知、但本任务没写处理函数」的画面是否**立刻**按图回源（默认开启）。

    这类画面是「公共中转页」（如点 X 之后落到的「组织」、「主场景」等），不是真不认识的
    画面。旧实现与"真未知画面"共用 ``UNREGISTER_SCENE_MAX_TIME``，于是每轮都要白等 15s
    再走一次多跳回源（2026-09-16 叛忍来袭日志：每轮 ~26s，连续循环 3 轮 ≈ 105s）。

    置 False 可回到旧语义（等满 ``UNREGISTER_SCENE_MAX_TIME`` 再回源）；
    任务若担心"加载画面被误判成已知场景"，可提高 ``graph_known_scene_confirm_frames``。
    """

    graph_known_scene_confirm_frames = 2
    """图内已知但未注册的画面需**连续确认**多少帧才触发立刻回源（默认 2）。

    单帧误判（加载/过场被识别成某个已知场景）不会立刻触发回源；填 1 = 首帧即回源。
    """

    unknown_scene_retreat_seconds = 1.0
    """未注册场景分支的循环退避秒数（默认 1s，0 = 不等待＝旧行为）。

    旧实现走"未注册场景"处理函数时不做任何等待，而默认处理函数立即返回 False →
    每轮都是"截图 + 识别 + 心跳"的高速空转（2026-09-16 日志一秒内 20+ 轮）。
    """

    JUMP_STALL_LIMIT = 3
    """同一「场景→目标」连续跳转的次数上限（超过即判定跳转未生效）。

    next_scene 只在「识别到的场景 == next_scene」时才被清除，一旦目标在实际画面上
    永远不可达（跳转函数是空操作，或当前画面下根本没有可走通的路径），任务每轮都在
    「跳一次 → 回到原画面 → 再跳一次」里空转，其场景处理函数会被永久抢占。
    超过该上限后框架放弃该目标（清空 next_scene + WARNING + 错误截图），把控制权
    交回当前场景的处理函数。逐跳推进的正常寻路（场景名会变化）不受影响。
    """

    def __init__(self, ctx: "RuntimeContext"):
        """构造注入收敛为单个 RuntimeContext（中间派重构）。

        任务派生类无需重写 __init__：调度器组装 RuntimeContext 后传入，
        内部仍以 self.xxx 访问各依赖，保持与旧版任务代码兼容。
        """
        task_name = ctx.task_name
        config = ctx.config
        transition_manager = ctx.transition_manager
        operationer = ctx.operationer
        activate_another_task_func = ctx.activate_another_task_func
        callback = ctx.callback
        parent_logger = ctx.parent_logger

        # 任务信息
        self.create_time = datetime.datetime.now(self.tz_info)
        self.last_run_time = datetime.datetime.now(self.tz_info)
        self.current_status = 2
        # 0 - 正在执行
        # 1 - 就绪状态，等待执行
        # 2 - 等待状态，等待就绪
        self.config = config
        self._execution_thread = None
        self.task_name = task_name
        self.logger: Logger = parent_logger.getChild(self.task_name)
        self.base_priority = config.get_task_base_config(
            self.task_name, "基础优先级")
        self.click_priority = config.get_task_base_config(
            self.task_name, "连点优先级")

        self.task_type = TaskType(
            config.get_task_base_config(self.task_name, "类型"))
        # 是否临时任务：启动时被禁用不自动执行，执行完后自动关闭，只允许立即执行或被其他任务激活
        self.is_temp = bool(
            config.get_task_base_config(self.task_name, "是否临时", False))

        self.bool_click = False
        # 立即执行标记：被请求"立即执行"后置 True，扫描选择时就绪队列中优先执行
        self.force_execute_now = False
        self.last_unregistered_scene_time = None
        # 「跳转未推进」计数（{key: (场景, 目标), count: 连续次数}），达上限即放弃该目标
        self._jump_stall = None
        # 最后一次执行是否出错（供调度器向前端透传失败标记）
        self.last_execute_error = None
        # 停止原因（Exceptions.STOP_REASON_*）：卡死类停止会让 Stop 分支走 on_stuck 重排期
        self.stop_reason = ""

        # 超时监视器（由调度器在任务开始执行前注入，任务结束后收回）
        self.watchdog = None

        # 提前绑定声明式排期（注入 ScheduleContext，供需要读任务参数的自定义排期使用）
        self._bound_schedule: Schedule = self._bind_schedule()

        self.schedule_next_on_initialization()
        self.transition_func = {}
        for cls in reversed(self.__class__.mro()):
            if hasattr(cls, "transition_func"):
                self.transition_func.update(cls.transition_func)
        # for scene, func in self.transition_func.items():
        #     self.logger.debug(f"注册场景处理函数: {scene} -> {func.__qualname__}")

        self.transition_manager = transition_manager
        self.operationer:Operationer = operationer
        self.activate_another_task_func = activate_another_task_func
        self.callback = callback

    def __lt__(self, other):
        """
        任务比较规则：
        1. current_priority小的优先级更高
        2. 如果current_priority也相同，create_time小的优先级更高

        注意：由于堆是最小堆，我们需要让优先级高的任务"更小"
        """

        # 1. 比较当前优先级
        if self.current_priority != other.current_priority:
            # current_priority小的优先级更高，在最小堆中应该排在前面（值更小）
            return self.current_priority < other.current_priority

        # 2. 比较创建时间
        # create_time小的优先级更高，在最小堆中应该排在前面（值更小）
        return self.create_time < other.create_time

    def __repr__(self):
        info_text = (f"任务名称: {self.task_name},"
                     f"任务基础优先级:{self.base_priority},"
                     f"任务连点优先级:{self.click_priority},"
                     f"任务当前优先级:{self.current_priority},"
                     f"是否启用:{self.is_activated},"
                     f"任务状态:{self.current_status},"
                     f"下次执行时间:{self.next_execute_time}")
        return info_text

    def attach_watchdog(self, watchdog):
        """由调度器在任务开始执行前注入超时监视器"""
        self.watchdog = watchdog

    def detach_watchdog(self):
        """任务结束/被停止后由调度器收回超时监视器"""
        self.watchdog = None

    # ------------------------------------------------------------------ #
    #                        声明式排期（Schedule）                        #
    # ------------------------------------------------------------------ #
    def _build_schedule_context(self) -> ScheduleContext:
        """构造排期上下文：让自定义 Schedule 能读取任务参数与当前时间。"""
        return ScheduleContext(
            tz=self.tz_info,
            param=lambda task, name, default: self.config.get_task_exe_param(
                task, name, default),
            now=lambda: datetime.datetime.now(self.tz_info),
            last_run_time=lambda: getattr(self, "last_run_time", None),
        )

    @property
    def _schedule(self) -> Schedule:
        """本任务绑定后的排期（懒解析：未走 ``__init__`` 的对象也能安全使用）。"""
        bound = self.__dict__.get("_bound_schedule")
        if bound is None:
            bound = self._bind_schedule()
            self.__dict__["_bound_schedule"] = bound
        return bound

    def _bind_schedule(self) -> Schedule:
        """绑定本任务的排期：注入 ScheduleContext，使 Custom 排期能读取任务参数。"""
        return type(self).schedule.bind(self._build_schedule_context())

    @property
    def schedule_description(self) -> str:
        """当前排期的人类可读描述（日志 / 前端展示）。"""
        return self._schedule.describe()

    @property
    def is_activated(self):
        return self.config.get_task_base_config(self.task_name, "是否启用")

    @property
    def current_priority(self):
        """返回当前有效优先级（连点状态下连点优先级优先于基础优先级）"""
        return self.click_priority if self.bool_click else self.base_priority

    @property
    def next_execute_time(self):
        china_tz = self.tz_info
        next_exec_ts = self.config.get_task_base_config(
            self.task_name, "下次执行时间")
        if next_exec_ts == 0:
            # 若初始值为0，设置为当前中国时区时间
            return datetime.datetime.now(china_tz)
        else:
            # 从时间戳转换为datetime对象
            return datetime.datetime.fromtimestamp(next_exec_ts, tz=china_tz)

    # ------------------------------------------------------------------ #
    #                 执行日志（开始 / 结束 / 错误，统一出口）               #
    # ------------------------------------------------------------------ #
    def _reset_execute_log_state(self) -> None:
        """每次执行开始时清空"只记一次"的日志键与场景日志去重状态。"""
        self.__dict__["_logged_once_keys"] = set()
        self.__dict__.pop("_last_logged_scene", None)
        self._clear_graph_known_streak()

    def _log_once(self, key: str, message: str,
                  level: int = logging.INFO) -> None:
        """同一任务执行周期内相同提示只输出一次（避免窗口类提示每轮刷屏）。"""
        logged = self.__dict__.setdefault("_logged_once_keys", set())
        if key in logged:
            return
        logged.add(key)
        self.logger.log(level, message)

    def _execute_trigger_reason(self) -> str:
        """执行触发方式："立即执行/被激活（跳过窗口校验）"、"预设顺序执行（跳过窗口校验）"或"正常排期"。"""
        if self._should_skip_window_check():
            return f"{self._skip_window_reason()}（跳过窗口校验）"
        return "正常排期"

    def _describe_execute_start(self) -> str:
        """执行开始摘要：触发方式 + 排期规则 + 最长执行时长（每次执行仅一行）。"""
        parts = [
            "▶ 开始执行",
            f"触发={self._execute_trigger_reason()}",
            f"排期={self.schedule_description}",
        ]
        if self.task_max_duration:
            parts.append("最长执行="
                         f"{_format_duration(self.task_max_duration.total_seconds())}")
        return " | ".join(parts)

    def _describe_next_execute(self) -> str:
        """下次执行时间文本（仅用于日志；读取失败降级为"未知"，不影响调度）。"""
        try:
            return _format_datetime(self.next_execute_time)
        except Exception as e:
            return f"未知（{_format_exception(e)}）"

    def _describe_execute_summary(self, reason: str, started_at: float,
                                  detail: str = "") -> str:
        """执行结束摘要：结果 + 详情 + 耗时 + 下次执行时间（每次执行仅一行）。"""
        parts = ["■ 执行结束", f"结果={reason}"]
        if detail:
            parts.append(f"详情={detail}")
        parts.append(f"耗时={_format_duration(time.perf_counter() - started_at)}")
        parts.append(f"下次执行={self._describe_next_execute()}")
        return " | ".join(parts)

    def _describe_retry(self) -> str:
        """冷却重试提示（与 error_retry_delay 对应，追加到错误日志）。"""
        delay = _format_duration(self.error_retry_delay.total_seconds())
        return f"冷却重试={delay}后"

    def _log_execute_error(self, title: str, exc: BaseException,
                           screenshot_saved: bool = False, extra: str = "",
                           with_traceback: bool = False) -> None:
        """错误日志统一出口：``✖ 标题: 类型: 消息 | 位置=… | 错误截图=已保存 | 附加信息``。

        - 位置取自 ``transition_return``（本轮场景处理函数的源码位置），便于直接定位
          出错步骤；
        - with_traceback=True 仅用于未捕获异常（业务异常如 StepFailedError 由任务
          主动抛出且消息明确，不需要 traceback）。
        """
        parts = [f"✖ {title}: {_format_exception(exc)}"]
        if self.transition_return:
            parts.append(f"位置={self.transition_return}")
        if screenshot_saved:
            parts.append("错误截图=已保存")
        if extra:
            parts.append(extra)
        self.logger.error(" | ".join(parts), exc_info=with_traceback)

    def _record_transition_source(self, func: Callable) -> str:
        """记录场景处理函数在源码中的位置（替代旧的 sys.settrace 方案，零运行时开销）。"""
        code = getattr(func, "__code__", None)
        if code is None:
            self.transition_return = getattr(func, "__qualname__", str(func))
            return self.transition_return
        path = Path(code.co_filename)
        try:
            path = path.relative_to(get_real_path())
        except ValueError:
            pass
        self.transition_return = f"{path}:{code.co_firstlineno}"
        return self.transition_return

    def run(self):
        """
        启动新线程执行execute避免阻塞进程
        """
        # 重置停止标志
        self.operationer.stop_event.clear()  # 重置停止标志
        # 保存线程对象以便后续停止
        self.last_run_time = datetime.datetime.now(self.tz_info)
        self.operationer.task_name=self.task_name
        self._execution_thread = threading.Thread(target=self._execute,
                                                  daemon=True)
        self._execution_thread.start()

    def stop(self, reason: str = ""):
        """发出停止请求（非阻塞）。

        ``reason`` 取 ``Exceptions.STOP_REASON_*``：卡死类停止（STUCK / FROZEN）会让
        ``Stop`` 分支改走 ``on_stuck`` 冷却重试，而不是把"下次执行时间"留在过去时刻
        （那会被调度器按扫描间隔立刻重跑）。
        """
        self.stop_reason = reason or ""
        self.logger.info(f"正在请求停止任务: {self.task_name}")
        self.operationer.stop_event.set()

    def _should_stop(self):
        """检查是否收到停止请求"""
        return self.operationer.stop_event.is_set()

    # ------------------------------------------------------------------ #
    #                 卡死自救（告警先交给任务线程，调度器不抢设备）          #
    # ------------------------------------------------------------------ #
    def _handle_recovery_request(self) -> None:
        """消费超时监视器的卡死告警：在**任务线程内**执行自救动作。

        分工原因：调度器线程直接操作设备会与任务线程争用同一个 Operationer/Device；
        旧实现还"先置停止标志再救援"，而 ``_search_loop`` 首轮就 ``raise Stop``，
        救援 100% 失败并每次留下一条 ERROR traceback。

        现在的协议：监视器只挂"恢复请求" → 任务在每轮循环开头取走并执行
        `recover_from_stuck` → **成功或失败都** `notify_recovery_done`（让调度器不必
        再等满宽限期）→ 成功则继续执行，失败则抛 ``Stop`` 交给 ``on_stuck`` 重排期。
        """
        watchdog = self.watchdog
        consume = getattr(watchdog, "consume_recovery_request", None)
        if not callable(consume):
            return
        event = consume()
        if event is None:
            return
        level_name = getattr(getattr(event, "level", None), "name", "?")
        scene_name = getattr(event, "scene_name", "") or ""
        detail = getattr(event, "detail", "")
        self.logger.warning(
            f"收到卡死告警 [{level_name}]（场景={scene_name or '未知'}"
            f"{'，' + detail if detail else ''}），尝试在任务内自行恢复")

        recovered = False
        failed = False
        try:
            recovered = bool(self.recover_from_stuck(scene_name))
        except Stop:
            # 停止请求优先（用户/调度器已要求停止），照常向上抛出
            raise
        except Exception as e:
            failed = True
            self.logger.error(f"✖ 卡死自救异常: {_format_exception(e)}",
                              exc_info=True)
        # 无论成功/失败/异常都要应答监视器，避免调度器白等满宽限期
        self._notify_recovery_done(event)

        if not failed and recovered:
            self.logger.info("卡死自救成功，继续执行任务")
            self._clear_jump_stall()
            self.last_unregistered_scene_time = None
            return
        reason = "自救异常" if failed else "自救未命中可退出元素"
        self.logger.warning(f"卡死自救失败（{reason}），停止任务并按 on_stuck 重排期")
        raise Stop(f"卡死自救失败（场景={scene_name or '未知'}）")

    def _notify_recovery_done(self, event) -> None:
        """应答监视器"本次告警已处理"（自救成功/失败都必须应答）。"""
        notify = getattr(self.watchdog, "notify_recovery_done", None)
        if not callable(notify):
            return
        try:
            notify(getattr(event, "level", None))
        except Exception as e:
            self.logger.warning(f"监视器恢复应答失败: {_format_exception(e)}")

    def recover_from_stuck(self, scene_name: str) -> bool:
        """卡死自救（默认实现：**按图回源 → 通用退出动作**）。

        任务类可覆盖以定制脱困方式（例如返回某个安全场景、点"退出战斗"）。
        返回 True 表示已执行脱困动作（监视器随即重新开始计时）；返回 False 表示
        本次未能执行任何有效动作（任务会被停止并按 ``on_stuck`` 重排期）。
        """
        source = self.source_scene
        if source and scene_name and scene_name != source:
            try:
                path = self.transition_manager.bfs_shortest_path(scene_name, source)
            except Exception as e:
                path = None
                self.logger.warning(
                    f"卡死自救：寻路失败（{_format_exception(e)}），改用通用退出动作")
            if path and len(path) >= 2:
                self.logger.warning(
                    f"卡死自救：按图回源 {scene_name} -> {source}"
                    f"（路径: {' -> '.join(path)}）")
                self.operationer.next_scene = source
                try:
                    self.transition_manager.transition(self.operationer)
                except Exception as e:
                    self.logger.warning(
                        f"卡死自救：回源跳转失败（{_format_exception(e)}），"
                        f"改用通用退出动作")
                    return self._escape_by_generic_clicks()
                return True
        return self._escape_by_generic_clicks()

    def _escape_by_generic_clicks(self) -> bool:
        """通用脱困：点 X / 返回（关闭卡住的弹窗或退出滞留界面），命中即视为已尝试。"""
        elements = []
        for name in ("X-普通", "X-广告-1", "X-广告-2"):
            try:
                element = self.operationer.get_element(name, "主场景")
            except Exception as e:
                # 元素表读取失败只影响这一个候选，继续尝试其余候选
                self.logger.debug(f"卡死自救：读取元素 [{name}] 失败: {_format_exception(e)}")
                element = None
            if element is not None:
                elements.append(element)
        try:
            if elements and self.operationer.search_and_click(
                    elements, [], once_max_attempts=1, max_attempts=1):
                self.logger.info("卡死自救：已点击 X 元素")
                return True
            back = self.operationer.get_element("返回", "主场景")
            if back is not None and self.operationer.click_and_wait(back):
                self.logger.info("卡死自救：已点击返回")
                return True
        except Stop:
            raise
        except Exception as e:
            self.logger.warning(f"卡死自救点击失败: {_format_exception(e)}")
        return False

    def on_stuck(self, current_time: datetime.datetime) -> datetime.datetime:
        """卡死自救失败被停止 → 返回下一次执行时间（默认：冷却重试，同步骤失败）。"""
        return self.on_delay(current_time, self.error_retry_delay)

    # ------------------------------------------------------------------ #
    #              显式等待（合法长等待不应被判"场景停滞"）                  #
    # ------------------------------------------------------------------ #
    def declare_waiting(self, desc: str = "") -> None:
        """声明"任务正在有意等待"：本场景内的等待按「等待超时」判定，不再算场景停滞。

        用于"等活动开启 / 等匹配 / 等对局结束"这类**合法长等待**——游戏何时响应不由任务
        决定，停在同一场景十几分钟是正常的；旧办法是把整个任务的
        ``scene_stuck_seconds`` 抬到几百秒，粒度粗且会一起延后真实卡死的发现。

        声明作用域**限于当前场景**：场景切换或 `end_wait()` 后自动失效（否则新场景会被
        一直当成"等待中"，反而漏判真卡死）。等待期间的阈值取全局配置
        ``超时检测-等待超时秒``（默认 1800 秒）；画面静止类判定不受影响，真卡死仍能发现。
        """
        scene = self.__dict__.get("_current_scene_name")
        text = desc or scene or "等待"
        self.__dict__["_declared_waiting"] = {"scene": scene, "desc": text}
        heartbeat = getattr(self.watchdog, "heartbeat", None)
        if not callable(heartbeat):
            return
        try:
            if self._watchdog_accepts_waiting():
                heartbeat(scene, waiting=True, desc=text)
            else:
                heartbeat(scene)
        except Exception as e:
            self._log_once("watchdog-declare-wait-failed",
                           f"等待声明上报失败: {_format_exception(e)}",
                           logging.WARNING)

    def end_wait(self) -> None:
        """结束"有意等待"声明，恢复普通场景停滞判定。"""
        self.__dict__.pop("_declared_waiting", None)
        end = getattr(self.watchdog, "end_wait", None)
        if not callable(end):
            return
        try:
            end()
        except Exception as e:
            self._log_once("watchdog-end-wait-failed",
                           f"等待结束上报失败: {_format_exception(e)}",
                           logging.WARNING)

    def wait_for(self, desc: str, condition, timeout: float | None = None,
                 interval: float = 1.0) -> bool:
        """显式等待原语：等 `condition()` 成立；期间声明等待，不会被判场景停滞。

        Args:
            desc: 等待说明（写入日志与监视器，便于排查"卡在哪一步"）。
            condition: 返回 True 表示等待目标达成。
            timeout: 最长等待秒数；``None`` = 不设上限（仍受任务的
                ``task_max_duration`` 与监视器的等待超时约束）。
            interval: 轮询间隔（默认 1s）。

        Returns:
            True = 条件满足；False = 超时。收到停止请求时抛 ``Stop``。

        场景轮询型等待（处理函数每轮都会被重新调用，如"叛忍来袭-即将开始"）只需在
        处理函数里调 `declare_waiting`，不必用本方法。
        """
        deadline = None if timeout is None else time.perf_counter() + float(timeout)
        while True:
            if self._should_stop():
                raise Stop("等待期间收到停止请求")
            self.declare_waiting(desc)
            try:
                if condition():
                    return True
            except Exception as e:
                # 条件检查失败不该把任务打死：记一条 WARNING 后继续等下一轮
                self.logger.warning(f"等待「{desc}」条件检查异常: {_format_exception(e)}")
            if deadline is not None and time.perf_counter() >= deadline:
                self.logger.info(f"等待「{desc}」超时（{float(timeout):.0f}s）")
                return False
            time.sleep(max(0.05, float(interval)))

    def _waiting_state(self, scene_name: str) -> tuple[bool, str]:
        """本轮是否处于"有意等待"：(是否等待, 说明)。

        - 任务显式声明（`declare_waiting`）：作用域限于声明时的场景，离开即失效；
        - **连点进行中**：连点本身就是"任务在持续操作、有进展"的证据（画面因连点不断
          变化、场景名却不变，如整局对局），同样按等待处理——否则一局几分钟的对局会被
          普通的 180s 停滞阈值判死（这正是"更多玩法"当初抬高到 600s 的原因）。
        """
        declared = self.__dict__.get("_declared_waiting")
        if declared:
            if declared.get("scene") in (None, scene_name):
                return True, declared.get("desc") or scene_name
            # 已离开声明等待时所在的场景 → 声明失效（避免新场景被一直当作等待中）
            self.__dict__.pop("_declared_waiting", None)
        if self._clicker_running():
            return True, "连点进行中"
        return False, ""

    def _clicker_running(self) -> bool:
        """连点线程是否在运行（兼容旧式 Clicker：无 ``running`` 时看线程存活）。"""
        clicker = getattr(self.operationer, "clicker", None)
        if clicker is None:
            return False
        running = getattr(clicker, "running", None)
        if running is not None:
            return bool(running)
        thread = getattr(clicker, "_thread", None)
        return bool(thread is not None and getattr(thread, "is_alive", lambda: False)())

    def _watchdog_accepts_waiting(self) -> bool:
        """监视器的 ``heartbeat`` 是否支持等待声明参数（旧式实现只接受场景名）。

        结果按方法对象缓存（每轮循环都会调用，避免重复解析签名）。
        """
        heartbeat = getattr(self.watchdog, "heartbeat", None)
        if not callable(heartbeat):
            return False
        cache = self.__dict__.get("_watchdog_waiting_support")
        if cache and cache[0] is heartbeat:
            return cache[1]
        try:
            params = inspect.signature(heartbeat).parameters
        except (TypeError, ValueError):
            params = {}
        supported = "waiting" in params or any(
            p.kind is inspect.Parameter.VAR_KEYWORD for p in params.values())
        self.__dict__["_watchdog_waiting_support"] = (heartbeat, supported)
        return supported

    def schedule_next_on_stuck(self) -> tuple[bool, datetime.datetime | None]:
        current_time = datetime.datetime.now(self.tz_info)
        next_execute_time = self.on_stuck(current_time)
        return self._save_next_execute_time(next_execute_time)

    def _ensure_tz_aware(self, dt: datetime.datetime) -> datetime.datetime:
        """将datetime标准化为任务时区的有时区对象。"""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=self.tz_info)
        return dt.astimezone(self.tz_info)

    def _check_window_invalid(self, dt: datetime.datetime, base: datetime.datetime|None=None) -> bool:
        """dt 是否**不在** base 所属周期的任一可执行窗口内（并集语义）。

        注：旧实现逐个窗口检查端点并"任一越界即判非法"，等价于要求 dt 落在所有窗口的
        交集里；对多窗口任务（如叛忍来袭）会误判，这里改为"命中任一窗口即合法"，
        与 ``_execute`` 的运行期判定保持一致。
        """
        dt = self._ensure_tz_aware(dt)
        base_dt = self._ensure_tz_aware(base) if base else self.last_run_time
        for start_dt, end_dt in self._get_execute_window(base_dt):
            if start_dt is not None:
                start_dt = self._ensure_tz_aware(start_dt)
            if end_dt is not None:
                end_dt = self._ensure_tz_aware(end_dt)
            if (start_dt is None or dt >= start_dt) and (end_dt is None or dt < end_dt):
                return False
        return True

    def _check_timeout(self, current_time: datetime.datetime) -> bool:
        """检查是否超过任务最大执行时间"""
        if self.task_max_duration:
            if current_time - self.last_run_time > self.task_max_duration:
                return True
        return False

    def _should_skip_window_check(self) -> bool:
        """是否跳过可执行窗口校验。

        显式意图优先：``force_execute_now``（用户点「执行」或被其它任务激活）与
        ``ignore_time_window``（临时预设顺序执行）都不受排期窗口限制，
        否则"立即执行"会被窗口压回起点、预设顺序执行会被窗口拦下。
        """
        return (bool(getattr(self, "force_execute_now", False))
                or bool(self.ignore_time_window))

    def _skip_window_reason(self) -> str:
        """跳过窗口校验的原因（写入日志）。"""
        if getattr(self, "force_execute_now", False):
            return "立即执行/被激活"
        return "预设顺序执行"

    def _check_execute_window(self, current_time: datetime.datetime) -> None:
        """校验 current_time 是否落在任一可执行窗口内。

        全部窗口都不满足时抛错（优先 DeadLine，其次 StartLine），与旧行为一致；
        至少一个窗口满足时只对其余不合规窗口记 warning。
        """
        windows = self._get_execute_window()
        valid_window_found = False
        too_early_windows: List[datetime.datetime] = []
        expired_windows: List[datetime.datetime] = []
        for start_dt, end_dt in windows:
            if start_dt:
                start_dt = self._ensure_tz_aware(start_dt)
            if end_dt:
                end_dt = self._ensure_tz_aware(end_dt)
            start_ok = (start_dt is None) or (current_time >= start_dt)
            end_ok = (end_dt is None) or (current_time < end_dt)
            if start_ok and end_ok:
                valid_window_found = True
            else:
                if start_dt and current_time < start_dt:
                    too_early_windows.append(start_dt)
                if end_dt and current_time >= end_dt:
                    expired_windows.append(end_dt)

        if valid_window_found:
            # 至少有一个窗口可执行 → 只警告其他不符合的窗口，不抛错。
            # 每次执行只提示一次：窗口校验在每轮循环都会跑，重复输出会刷屏
            for dt in too_early_windows:
                message = f"[StartLine]未到任务可执行时间:{_format_datetime(dt)}"
                self._log_once(f"window:{message}", message, logging.WARNING)
            for dt in expired_windows:
                message = f"[DeadLine]可执行窗口已过:{_format_datetime(dt)}"
                self._log_once(f"window:{message}", message, logging.WARNING)
            return
        # 所有窗口都不符合 → 抛出错误，尽量保留原有异常类型和信息
        if too_early_windows and not expired_windows:
            next_start = min(too_early_windows)
            raise TooEarlyToRun(
                f"[StartLine]未到任务可执行时间:{next_start.strftime('%Y-%m-%d %H:%M:%S')}")
        if expired_windows:
            last_deadline = max(expired_windows)
            raise TimeOutDeadLineError(
                f"[DeadLine]任务执行超时:{last_deadline.strftime('%Y-%m-%d %H:%M:%S')}")
        raise TooEarlyToRun("任务当前时间不在任何可执行窗口内")

    def probe_execute_window(
            self, now: datetime.datetime | None = None) -> tuple[bool, str]:
        """探测"现在是否处于可执行窗口内"，供跨任务"立即激活"前做守卫。

        返回 ``(是否可执行, 状态说明)``，状态取
        ``"窗口内" / "窗口已过期" / "窗口未开始" / "不限时间"``。

        与 `_check_execute_window` 的区别：窗口基准取 ``now``（缺省=此刻）而非
        ``last_run_time`` —— "激活时窗口是否可执行"必须看**当前周期**，用陈旧的
        ``last_run_time``（例如上一次执行在上周）会把窗口算成上一周期的，从而误判。

        注意"过期"判定**不能**只看"所有窗口的终点都早于 now"：像【叛忍来袭】这类
        多窗口排期（周三/周六触发窗口 + 下周三兜底），兜底窗口永远在未来，因此
        这里以"当前时刻是否落在任一窗口内"为准——不在窗口内（已过期或还没开始）
        就说明此刻激活只会空转（见 `SchedulerService._skip_expired_activation`）。
        """
        moment = (self._ensure_tz_aware(now) if now is not None
                  else datetime.datetime.now(self.tz_info))
        windows = list(self._get_execute_window(moment))
        if not windows or all(start is None and end is None
                              for start, end in windows):
            return True, "不限时间"
        if any((start is None or moment >= self._ensure_tz_aware(start))
               and (end is None or moment < self._ensure_tz_aware(end))
               for start, end in windows):
            return True, "窗口内"
        if all(end is None for _start, end in windows):
            return True, "不限时间"
        # 已有窗口结束（错过本周期这次机会）→ 过期；否则是还没到
        if any(end is not None and moment >= self._ensure_tz_aware(end)
               for _start, end in windows):
            return False, "窗口已过期"
        return False, "窗口未开始"

    @handle_task_exceptions
    def _execute(self):
        self.operationer.next_scene = self.source_scene
        # 每次执行重新开始：清空上一轮遗留的「跳转未推进」计数
        self._clear_jump_stall()
        # 是否跳过窗口校验、排期规则已由"开始日志"统一输出，循环内不再重复
        while True:
            # 检查停止信号
            if self._should_stop():
                raise Stop("任务被停止")

            # 卡死告警（若监视器已发出）：在**本线程内**自行脱困
            self._handle_recovery_request()

            current_time = datetime.datetime.now(self.tz_info)
            if not self._should_skip_window_check():
                self._check_execute_window(current_time)
            if self._check_timeout(current_time):
                raise TimeOutMaxDurationError(
                    f"[MaxDuration]任务执行超时:{_format_datetime(current_time)}")
            # 清空上一轮的处理函数位置：出错时 _log_execute_error 只展示本轮位置
            self.transition_return = ""

            # 执行步骤转换：**只有返回 True（或抛 TaskCompleted）才算任务完成**；
            # 处理函数返回场景名字符串 = 声明落点（由 transition() 归一化，见 declare_next_scene）
            if self.transition() is True:
                raise TaskCompleted("任务执行完成")

    @handle_transition_exceptions
    def transition(self):
        # 获取当前屏幕截图并识别场景
        screenshot = self.operationer.screen_cap()
        # hint=当前所在场景：启用「按转移图裁剪候选集」（只匹配入/出边邻居 + 弹窗，
        # 未命中会自动全量兜底，保证不漏判）；current_scene 由上一轮识别或
        # TransitionManager 跳转维护，取不到时退回 None（= 全量扫描）
        hint = getattr(self.operationer.current_scene, "name", None)
        scene = self.operationer.recognizer.scene(screenshot, bool_debug=False, hint=hint)

        # 确保待调用的场景名为str
        # 路由 = **本帧识别结果**（"看到什么画面就走哪个流程"）。
        # 注：2026-09-16 曾引入"识别结果多帧确认去抖"（scene_confirm_frames），2026-09-17 移除：
        # 去抖会让"路由场景"与 operationer.current_scene（本帧识别）不一致，而处理函数里的
        # click_and_wait / detect_element 只按 current_scene 解析元素 → 拿 A 场景的路由去
        # B 场景找元素，报 `StepFailedError: 元素 [X] 未定义`（消耗体力/情报站实机各中数次）。
        if isinstance(scene, str):
            scene_name = scene
        else:
            self.operationer.current_scene = scene
            scene_name = scene.name
        # 场景日志：切换场景时 INFO（用户关心流程走向），持续停留同一场景降为 DEBUG
        # （旧实现每轮循环都打 INFO，长时间任务会刷屏）
        if scene_name != self.__dict__.get("_last_logged_scene"):
            self.__dict__["_last_logged_scene"] = scene_name
            self.logger.info(f"识别到场景: {scene_name}")
        else:
            self.logger.debug(f"识别到场景: {scene_name}")
        # 向超时监视器上报当前场景（心跳），用于场景停滞/卡死检测。
        # 监视器内部已对心跳失败留痕并临时关闭"场景停滞"判定；这里仅做兜底，
        # 且必须提示（不再静默吞掉）——心跳失效会导致卡死判定失真。
        # 注意不在此丢弃 self.watchdog：丢掉了也阻止不了监视器误判，真正有效的降级
        # 在监视器侧（_scene_stuck_enabled），这里保留引用便于监视器继续被调度器收回。
        # 留档本次识别的场景名：处理函数里的 declare_waiting() 需要知道"在哪个场景等待"
        self.__dict__["_current_scene_name"] = scene_name
        if self.watchdog is not None:
            try:
                waiting, wait_desc = self._waiting_state(scene_name)
                if self._watchdog_accepts_waiting():
                    self.watchdog.heartbeat(scene_name, waiting=waiting,
                                            desc=wait_desc)
                else:
                    # 旧式监视器只接受场景名（无等待声明能力）→ 退回旧调用
                    self.watchdog.heartbeat(scene_name)
            except Exception as e:
                self._log_once(
                    "watchdog-heartbeat-failed",
                    "超时监视器心跳上报失败（场景停滞判定可能失真）: "
                    f"{_format_exception(e)}",
                    logging.WARNING)
        # 如果设置了next_scene，优先跳转；_pending_jump_path 内含「跳转未推进保护」——
        # 同一 (场景, 目标) 连续多次仍跳不动时会放弃该目标并把控制权交回场景处理函数
        if self._pending_jump_path(scene_name):
            return self.transition_manager.transition(self.operationer)

        if scene_name in self.transition_func:
            if self.last_unregistered_scene_time:
                self.last_unregistered_scene_time = None
            self._clear_graph_known_streak()
            func = self.transition_func[scene_name]
            # self.logger.debug(f"场景{scene_name}绑定的函数：{func.__qualname__}")
            # 记录处理函数源码位置（出错日志/调试日志据此定位步骤），异常也要记录
            try:
                result = func(self)
            finally:
                self._record_transition_source(func)
            return self._normalize_handler_result(result)
        else:
            # 场景图里存在、只是本任务没写处理函数的「公共中转页」（如点 X 后落到的
            # 「组织」「主场景」）：立刻按图回源，不再白等 UNREGISTER_SCENE_MAX_TIME。
            if self._try_graph_known_return(scene_name):
                return self.transition_manager.transition(self.operationer)

            if not self.last_unregistered_scene_time:
                self.last_unregistered_scene_time = time.perf_counter()
            if not self.source_scene:
                # 没有 source_scene，无法寻路，回退到未注册场景
                scene_name = "未注册场景"
            elif time.perf_counter() - self.last_unregistered_scene_time > self.UNREGISTER_SCENE_MAX_TIME:
                # 长时间未识别到注册场景 → 强制回源。这里同样走 _pending_jump_path 的
                # 「跳转未推进保护」：连续多次跳不动时它会清空 next_scene 并留 WARNING
                # （错误截图一并保存），本分支再重置计时，把控制权交给下面的
                # "未注册场景"处理函数——旧实现会在此每轮重复强行回源，同样可能空转。
                self.operationer.next_scene = self.source_scene
                path = self._pending_jump_path(scene_name)
                if path:
                    self.logger.warning(
                        f"长时间未识别到注册场景，强制跳转回 source_scene: {self.source_scene}")
                    self._auto_screenshot(SCREENSHOT_REASON_UNREGISTERED_SCENE)
                    # 执行第一段路径跳转
                    self.logger.info(
                        f"自动跳转回场景状态中: 从 {scene_name} 到 {path[1]} "
                        f"(路径: {' -> '.join(path)})")
                    return self.transition_manager.transition(self.operationer)
                # 回源失败（转移图无路径 / 跳转连续未生效）：重置计时并清掉刚挂上的目标，
                # 避免把"待回源"长期挂起（它会抢占后续场景的处理函数）或每帧重复回源
                self.last_unregistered_scene_time = time.perf_counter()
                self.operationer.next_scene = None
                scene_name = "未注册场景"
            else:
                # 未到强制回源时限，回退到原来的处理方式
                scene_name = "未注册场景"

        # 未注册场景分支：先退避再交给处理函数，避免"处理函数立即返回"造成高速空转
        if scene_name == "未注册场景":
            self._retreat_on_unregistered_scene()

        # 正常执行注册函数
        # self.logger.debug(f"寻找注册函数: {scene_name}")
        func = self.transition_func[scene_name]
        # self.logger.debug(f"场景{scene_name}绑定的函数：{func.__qualname__}")
        # 执行派生类的场景处理函数（异常也要记录位置，便于定位出错步骤）
        try:
            result = func(self)
        finally:
            self._record_transition_source(func)
        # self.logger.debug(f"[{scene_name}]注册函数执行完毕")
        # self.logger.debug(f"Transition的Result：{result}")
        # self.logger.debug(f"Transition的next_scene：{self.operationer.next_scene}")
        return self._normalize_handler_result(result)

    # ------------------------------------------------------------------ #
    #            处理函数返回值约定：True/异常 = 完成；字符串 = 落点         #
    # ------------------------------------------------------------------ #
    def _normalize_handler_result(self, result):
        """归一化场景处理函数的返回值（**唯一契约出口**）。

        - ``True`` → 原样返回，由 ``_execute`` 判为**任务完成**（唯一"返回值完成"方式，
          另一种是抛 ``TaskCompleted``）；
        - ``str``（场景名，非空白）→ 视为「**声明落点**」：转成
          ``operationer.next_scene``，并返回 ``False``（**本轮不作完成判定**）——
          下一轮由 `_pending_jump_path` 负责"到达即清空 / 未到达则按图纠偏 /
          连续跳不动则放弃并截图"；
        - ``False`` / ``None`` → 原样返回（继续循环）；
        - **其它真值**（历史写法如 ``return 1``）→ 按新约定**不视为完成**，记一条
          WARNING 提示作者改用 ``return True``（不再静默完成，避免"字符串/真值"语义混淆）。

        这样任务作者不用再写 ``self.operationer.next_scene = "X"; return False`` 两行，
        直接 ``return "X"`` 即可；抛 ``TaskCompleted`` 的完成路径不受影响。
        """
        if isinstance(result, str):
            self.declare_next_scene(result)
            return False
        if result is True or result is False or result is None:
            return result
        if result:
            self._log_once(
                f"handler-result-not-true:{type(result).__name__}",
                f"处理函数返回了非 True 的真值（{result!r}）：按当前约定**不视为任务完成**，"
                f"需要结束请改为 return True 或抛 TaskCompleted",
                logging.WARNING)
            return False
        return result

    def declare_next_scene(self, scene: str, desc: str = "") -> bool:
        """声明"本步结束后应当到达的场景"（落点），返回是否声明成功。

        也可由任务直接调用（等价于 ``return "场景名"``）：``self.declare_next_scene("X")``。

        语义与保障（全部基于既有的 ``operationer.next_scene`` + `_pending_jump_path`）：

        - **到达**：下一轮识别到该场景 → 自动清除声明并执行该场景的处理函数；
        - **未到达但有路**：按转移图寻路纠偏（逐跳执行，受 `JUMP_STALL_LIMIT` 保护）；
        - **连续跳不动**：放弃目标 + ``JumpStalled`` 错误截图 + 交回当前画面的处理函数；
        - **当前画面无路可达**：保留声明交给后续帧（画面变化后仍有机会跳过去）。

        安全校验（避免把 declare 写成"送死"）：

        - 非字符串 / 空字符串 → WARNING 并忽略（不改动已有声明）；
        - 场景名不在 ``scene_graph.scenes`` 里 → WARNING 并忽略：跳转校验会抛
          ``ValueError`` 走"未捕获异常 → 冷却重试"，比不声明更糟；老式替身
          （operationer 无 ``scene_graph``）跳过该校验。

        ``desc`` 仅用于日志补充说明（如 ``desc="点X后回到组织"``）。
        """
        if not isinstance(scene, str) or not scene.strip():
            self._log_once(
                "declare-next-scene-invalid",
                f"声明落点被忽略：取值非法（{scene!r}，应为非空场景名）",
                logging.WARNING)
            return False
        scene = scene.strip()
        graph = getattr(self.operationer, "scene_graph", None)
        scenes = getattr(graph, "scenes", None)
        if scenes and scene not in scenes:
            self._log_once(
                f"declare-next-scene-unknown:{scene}",
                f"声明落点被忽略：[{scene}] 不在场景库中（拼写错误或场景已改名）",
                logging.WARNING)
            return False
        # 不在声明时重置「跳转未推进」计数：同一 (画面, 目标) 连续跳不动时，计数会累加并
        # 在超过 JUMP_STALL_LIMIT 后触发放弃 + 截图——这是有意的保护，不能被 declare 洗掉。
        self.operationer.next_scene = scene
        suffix = f"（{desc}）" if desc else ""
        self._log_once(
            f"declare-next-scene:{scene}",
            f"声明落点: {scene}{suffix}")
        return True

    def _is_graph_known_scene(self, scene_name: str) -> bool:
        """场景名是否存在于场景图（含未被本任务注册处理函数的公共中转页）。"""
        graph = getattr(self.operationer, "scene_graph", None)
        scenes = getattr(graph, "scenes", None)
        if not scenes:
            return False
        return scene_name in scenes

    def _try_graph_known_return(self, scene_name: str) -> bool:
        """「图内已知但本任务未注册」→ 立刻按图回源；返回 True 表示调用方应执行跳转。

        与 15s 强制回源的区别只在**时机**：这类画面（公共中转页）不需要观望窗口，
        立刻寻路能让每轮从 ~26s 降到秒级；跳转本身仍受 `_pending_jump_path` 的
        「跳转未推进保护」约束（连续跳不动就放弃并交回场景处理函数）。

        单帧误判由 ``graph_known_scene_confirm_frames``（默认连续 2 帧）挡住；
        任务已挂其它目标（``next_scene``）时不抢；场景图不可用（旧式替身）时退化为旧行为。
        """
        if not getattr(self, "graph_known_scene_immediate_return", True):
            return False
        source = self.source_scene
        if not source or scene_name == source:
            self._clear_graph_known_streak()
            return False
        if self.operationer.next_scene and self.operationer.next_scene != source:
            # 任务之间/任务自身已声明了别的跳转目标，不抢
            self._clear_graph_known_streak()
            return False
        if not self._is_graph_known_scene(scene_name):
            self._clear_graph_known_streak()
            return False

        need = max(1, int(getattr(self, "graph_known_scene_confirm_frames", 1) or 1))
        streak = self.__dict__.get("_graph_known_streak") or {}
        count = streak.get("count", 0) + 1 if streak.get("scene") == scene_name else 1
        self.__dict__["_graph_known_streak"] = {"scene": scene_name, "count": count}
        if count < need:
            self.logger.debug(
                f"[{scene_name}] 场景图已知但本任务未注册，等待连续确认"
                f"（{count}/{need} 帧）后再回源 {source}")
            return False

        self.operationer.next_scene = source
        path = self._pending_jump_path(scene_name)
        if not path:
            # 转移图无路 / 跳转连续未生效：保持旧行为（清目标 + 走"未注册场景"兜底计时）
            self.operationer.next_scene = None
            return False
        self._log_once(
            f"graph-known-return:{scene_name}",
            f"[{scene_name}] 场景图已知但本任务未注册该场景，"
            f"立即按图回源 {source}（路径: {' -> '.join(path)}）")
        self.last_unregistered_scene_time = None
        return True

    def _clear_graph_known_streak(self) -> None:
        """清空「图内已知但未注册」的连续确认计数。"""
        self.__dict__.pop("_graph_known_streak", None)

    def _retreat_on_unregistered_scene(self) -> None:
        """未注册场景的循环退避：避免处理函数立即返回导致的高速空转（见类属性说明）。"""
        seconds = float(getattr(self, "unknown_scene_retreat_seconds", 0.0) or 0.0)
        if seconds > 0:
            time.sleep(seconds)

    def _clear_jump_stall(self):
        """清空「跳转未推进」计数（到达目标 / 放弃目标 / 每次执行开始时调用）。"""
        self._jump_stall = None

    def _note_jump_attempt(self, scene_name: str, target: str) -> int:
        """记录一次「场景→目标」跳转尝试，返回该组合的连续尝试次数。

        组合发生变化（场景名变了 / 目标变了）说明跳转确实在推进，计数重新从 1 开始。
        """
        key = (scene_name, target)
        stall = self.__dict__.get("_jump_stall")
        if stall and stall.get("key") == key:
            stall["count"] += 1
        else:
            stall = {"key": key, "count": 1}
            self._jump_stall = stall
        return stall["count"]

    def _pending_jump_path(self, scene_name: str) -> list[str] | None:
        """取本轮 pending（``operationer.next_scene``）跳转的路径；None 表示本轮不跳转。

        含「跳转未推进保护」，三类不跳转的情形：

        1. 已到达（``next_scene == 当前识别场景``）→ 清空 next_scene（原行为）；
        2. 转移图里没有可行路径 → 维持原行为，交由当前场景的处理函数兜底；
        3. **同一 (场景, 目标) 连续尝试超过 ``JUMP_STALL_LIMIT`` 次** → 判定跳转未生效
           （跳转函数不改变画面，或该目标在当前画面下根本到不了），清空 next_scene、
           记 WARNING + 错误截图，把控制权交回当前场景的处理函数。

        第 3 条是「任务被到不了的目标劫持」的兜底：``next_scene`` 过去只在
        「识别到的场景 == next_scene」时才清除，一旦目标在实际画面上永远不可达
        （例：【更多玩法】对局加载期画面被误判后挂上"回源"目标，而副本内的
        ``绝迹战场-副本内 -> 更多玩法-结算`` 跳转函数只是 sleep 等待），
        任务每轮都在「跳一次 → 回到原画面 → 再跳一次」里空转，
        连"副本内"里启动连点的处理函数都永远不会被执行。
        """
        target = self.operationer.next_scene
        if not target:
            return None
        if target == scene_name:
            self.operationer.next_scene = None
            self._clear_jump_stall()
            return None
        path = self.transition_manager.bfs_shortest_path(scene_name, target)
        if not (path and len(path) >= 2):
            return None
        count = self._note_jump_attempt(scene_name, target)
        if count > self.JUMP_STALL_LIMIT:
            self.logger.warning(
                f"跳转 {scene_name}->{target} 连续 {count} 次未生效，放弃该目标，"
                f"交由 [{scene_name}] 的处理函数继续"
                f"（目标在当前画面可能不可达，或跳转函数本身不改变画面）")
            self._auto_screenshot(SCREENSHOT_REASON_JUMP_STALLED)
            self.operationer.next_scene = None
            self._clear_jump_stall()
            # 顺带重启「长时间未识别到注册场景」的计时：放弃目标后给任务一段自主恢复
            # 的窗口，避免同一轮/下一轮又立刻强行回源（场景已注册时，registered 分支
            # 会立刻把该计时清空，不受影响）
            self.last_unregistered_scene_time = time.perf_counter()
            return None
        return path

    def _cleanup_on_stop(self):
        """停止请求时的清理"""
        self.operationer.clicker.stop()
        self.reset_task_exe_prog()

    def _cleanup_on_error(self):
        """步骤失败 / 未捕获异常时的清理（与超时一致：停止连点并复位进度，便于冷却后重试）"""
        self.operationer.clicker.stop()
        self.reset_task_exe_prog()

    def _auto_screenshot(self, reason: str) -> bool:
        """错误/超时/异常场景自动截图一次，保存到 log/<用户名>/<日期>/screenshot/<任务名>/，
        便于用户打包反馈后开发者排查。可通过配置"错误自动截图"关闭，任何异常不阻断任务流程。

        ``reason``（取 ``SCREENSHOT_REASON_*`` 常量）必须透传给配置的截图回调：
        调度器的回调据此走"错误自动截图"开关，并把原因写进截图文件名（区分错误类型）。
        返回是否已保存（供错误日志标注"错误截图=已保存"）。
        """
        try:
            if not self.config.get_config("错误自动截图", True):
                return False
            op = self.operationer
            if op is None:
                return False
            save_func = getattr(op, "screen_save_func", None)
            if callable(save_func):
                save_func(self.task_name, reason)
                self.logger.info(f"已自动保存错误截图（原因: {reason}）")
                return True
            # 兜底：直接截图保存（未配置截图回调的场景，如离线单测）
            frame = op.screen_cap()
            if frame is None:
                return False
            import os
            import cv2
            from datetime import datetime
            username = self.config.get_config("用户名", "unknown") or "unknown"
            safe_name = str(username).replace("/", "_").replace("\\", "_")
            date_str = datetime.now().strftime("%Y-%m-%d")
            save_dir = os.path.join(get_real_path("log"), safe_name, date_str,
                                    "screenshot", self.task_name)
            os.makedirs(save_dir, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filepath = os.path.join(save_dir, f"{ts}_{reason}.png")
            ok, buf = cv2.imencode(".png", frame)
            if not ok:
                return False
            buf.tofile(filepath)
            self.logger.info(f"已自动保存错误截图: {filepath}")
            return True
        except Exception as e:
            self.logger.warning(f"错误截图保存失败: {_format_exception(e)}")
            return False

    def _cleanup_on_timeout(self):
        """超时时的清理"""
        self.operationer.clicker.stop()
        self.reset_task_exe_prog()

    def _cleanup_on_complete(self):
        """任务正常完成时的清理"""
        self.operationer.clicker.stop()
        self.reset_task_exe_prog()

    def _cleanup_on_too_early(self):
        """过早执行时的清理"""
        self.operationer.clicker.stop()
        self.reset_task_exe_prog()

    def _activate_another_task(self, task_name: str,
                               next_execute_time: datetime.datetime | None = None,
                               delay: timedelta | None = None):
        """
        激活另一任务

        Args:
            task_name(str): 需要激活的任务名称
            next_execute_time(datetime|None): 指定被激活任务的下次执行时间；
                与 delay 同为 None 时表示"立即执行"（当前任务结束后立刻执行）
            delay(timedelta|None): 相对当前时间延后多久执行（与 next_execute_time 二选一）
        """
        if next_execute_time is not None and delay is not None:
            self.logger.warning("同时指定了 next_execute_time 与 delay，忽略 delay")
            delay = None
        if next_execute_time is None and delay is not None:
            next_execute_time = datetime.datetime.now(self.tz_info) + delay
        if next_execute_time is None:
            self.logger.info(f"{task_name}被激活，将立即执行")
        else:
            self.logger.info(
                f"{task_name}被激活，将于 "
                f"{next_execute_time.strftime('%Y-%m-%d %H:%M:%S')} 执行")
        # next_execute_time 为 None 时保持原有"立即执行"语义（调度器登记待激活）
        self.activate_another_task_func(task_name,
                                        next_execute_time=next_execute_time)

    def _save_next_execute_time(
        self, next_execute_time: datetime.datetime | None
    ) -> tuple[bool, datetime.datetime | None]:
        if next_execute_time is None:
            return False, None
        self.logger.debug(
            f"下次执行时间为：{next_execute_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.config.set_task_base_config(self.task_name, "下次执行时间",
                                         int(next_execute_time.timestamp()))
        return True, next_execute_time

    def schedule_next_on_initialization(
            self) -> tuple[bool, datetime.datetime | None]:
        current_time = datetime.datetime.now(self.tz_info)
        next_execute_time = self._handle_initialization(current_time)
        return self._save_next_execute_time(next_execute_time)

    def schedule_next_on_complete(
            self) -> tuple[bool, datetime.datetime | None]:
        current_time = datetime.datetime.now(self.tz_info)
        next_execute_time = self.on_complete(current_time)
        return self._save_next_execute_time(next_execute_time)

    def schedule_next_on_timeout_deadline(
            self) -> tuple[bool, datetime.datetime | None]:
        current_time = datetime.datetime.now(self.tz_info)
        next_execute_time = self.on_deadline(current_time)
        return self._save_next_execute_time(next_execute_time)
    
    def schedule_next_on_timeout_max_duration(
            self) -> tuple[bool, datetime.datetime | None]:
        current_time = datetime.datetime.now(self.tz_info)
        next_execute_time = self.on_timeout(current_time)
        return self._save_next_execute_time(next_execute_time)

    def schedule_next_on_too_early(
            self) -> tuple[bool, datetime.datetime | None]:
        current_time = datetime.datetime.now(self.tz_info)
        next_execute_time = self.on_too_early(current_time)
        return self._save_next_execute_time(next_execute_time)

    def schedule_next_with_delay(
            self, delta: timedelta) -> tuple[bool, datetime.datetime | None]:
        """延后 delta 再执行（业务重试 / 冷却）。

        这是任务的**显式排期意图**，不受可执行窗口限制：即便算出的时刻不在窗口内，
        也会写入"下次执行时间"并由调度器到点触发（窗口校验与排期是两件事）。
        """
        current_time = datetime.datetime.now(self.tz_info)
        next_execute_time = self.on_delay(current_time, delta)
        return self._save_next_execute_time(next_execute_time)

    def schedule_execute_now(self) -> tuple[bool, datetime.datetime | None]:
        current_time = datetime.datetime.now(self.tz_info)
        next_execute_time = self.on_execute_now(current_time)
        return self._save_next_execute_time(next_execute_time)

    ############################################################################################
    #                                和任务执行时间处理相关的函数                                 #
    ############################################################################################
    def _get_execute_window(
        self,
        dt: datetime.datetime | None = None
    ) -> List[Tuple[datetime.datetime | None, datetime.datetime | None]]:
        """返回可执行窗口列表（半开区间 ``[start, end)``，多窗口为并集）。

        默认由 ``self._schedule``（任务类上的声明式排期）计算；
        基准为 ``last_run_time``（不传 dt 时），避免执行中跨过窗口期导致异常。
        需要动态窗口（依赖任务参数 / 多窗口）时请用 ``Custom`` 排期表达。
        """
        base = self._ensure_tz_aware(dt) if dt is not None else self.last_run_time
        return [(w.start, w.end) for w in self._schedule.windows(base)]

    def get_next_cycle_day(self, dt: datetime.datetime) -> datetime.datetime:
        """返回 dt 所在周期的下一个周期参考时刻（由 schedule 决定：日=+1 天、周=+1 周…）"""
        return self._schedule.next_cycle(self._ensure_tz_aware(dt))

    def get_cycle_execute_time(self,
                               dt: datetime.datetime,
                               completed=False) -> datetime.datetime:
        """返回 dt 所属执行周期的任务执行时间（周期内第一个窗口的起点）"""
        base = self.get_next_cycle_day(self._ensure_tz_aware(dt)) if completed else None
        window = self._get_execute_window(base)
        start = window[0][0]
        if start is None:
            # 无界窗口（AnyTime 等）：回退到 schedule 的默认时间
            return self._schedule.default_time(self._ensure_tz_aware(dt),
                                               after_cycle=completed)
        return start

    def _handle_initialization(
            self, current_time: datetime.datetime) -> datetime.datetime:
        """处理任务初始化时的时间设置"""
        # 读取配置中的时间
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")

        if not next_exec_ts:
            # 配置中未设置下次执行时间，返回默认时间
            return self.get_cycle_execute_time(current_time)
        try:
            next_exec_dt = datetime.datetime.fromtimestamp(next_exec_ts, tz=self.tz_info)
        except Exception as e:
            self.logger.warning(f"解析下次执行时间戳失败: {next_exec_ts}, 错误: {e}")
            return self.get_cycle_execute_time(current_time)
        if self._check_window_invalid(next_exec_dt) and self._check_window_invalid(next_exec_dt,self.get_next_cycle_day(self.last_run_time)):
            self.logger.warning(f"配置中的下次执行时间 {next_exec_dt} 超前或已过期")
        else:
            return next_exec_dt
        return self.get_cycle_execute_time(current_time)

    # ------------------------------------------------------------------ #
    #                    时间钩子（新任务请覆盖 on_* 系列）                  #
    # ------------------------------------------------------------------ #
    def on_complete(self, current_time: datetime.datetime) -> datetime.datetime:
        """任务正常执行完成 → 返回下一次执行时间（默认：下一周期的窗口起点）。"""
        return self.get_cycle_execute_time(current_time, completed=True)

    def on_deadline(self, current_time: datetime.datetime) -> datetime.datetime:
        """到达窗口 DDL 被强制结束 → 返回下一次执行时间（默认与 on_complete 相同）。"""
        return self.on_complete(current_time)

    def on_timeout(self, current_time: datetime.datetime) -> datetime.datetime:
        """执行超过 task_max_duration → 返回下一次执行时间（默认：重新按配置排期）。"""
        return self._handle_initialization(current_time)

    def on_too_early(self, current_time: datetime.datetime) -> datetime.datetime:
        """被调度到时尚未进入窗口 → 返回下一次执行时间（默认：重新按配置排期）。"""
        return self._handle_initialization(current_time)

    def on_execute_now(self, current_time: datetime.datetime) -> datetime.datetime:
        """「立即执行」的排期（默认：当前时间，立即到期）。"""
        return current_time

    def on_delay(self, current_time: datetime.datetime,
                 delta: timedelta) -> datetime.datetime:
        """延后 delta 再执行（业务重试/冷却，**不受可执行窗口限制**）。"""
        return current_time + delta

    def reset_task_exe_prog(self) -> bool:
        """重置任务执行进度参数，需要的任务自行重载"""
        return True

    ############################################################################################
    #                                 某些弹窗或独立场景的处理                                   #
    ############################################################################################
    @TransitionOn("二级密码")
    def _(self):
        self.logger.info("出现二级密码窗口")
        password = self.config.get_config("二级密码")
        if len(password) != 6:
            raise StepFailedError("请检查二级密码！")
        # 输入操作
        input_el = self.operationer.get_element("输入框")
        if input_el is None:
            raise StepFailedError("未找到二级密码输入框")
        self.operationer.click_and_input(input_el, password)
        # 点击二级密码-确定
        confirm_el = self.operationer.get_element("确定")
        if confirm_el is None:
            self.logger.error("未找到二级密码确认按钮")
            return False
        if not self.operationer.click_and_wait(confirm_el):
            self.logger.error("二级密码验证失败")
        return False

    @TransitionOn("升级")
    def _(self):
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("公告")
    def _(self):
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("登录界面-开始游戏")
    def _(self):
        self.operationer.click_and_wait("开始游戏")
        return False

    @TransitionOn("登录奖励")
    def _(self):
        self.operationer.click_and_wait("领取")
        return False

    @TransitionOn("好友排名至X位")
    def _(self):
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("重连提示")
    def _(self):
        self.logger.warning("即将尝试网络重连...")
        self.operationer.click_and_wait("继续")
        return False

    @TransitionOn("响应超时")
    def _(self):
        self.operationer.click_and_wait("确定")
        self.logger.warning("响应超时！")
        return False

    @TransitionOn("安装包更新异常")
    def _(self):
        self.operationer.click_and_wait("重试")
        return False

    @TransitionOn("对方数据异常")
    def _(self):
        self.operationer.click_and_wait("确定")
        self.logger.warning("对方数据异常，即将退出战斗...")
        return False

    @TransitionOn("网络不畅通")
    def _(self):
        self.operationer.click_and_wait("确定")
        self.logger.warning("网络不通畅！")
        return False
    @TransitionOn("登录授权过期")
    def _(self):
        self.operationer.click_and_wait("忽略")
        self.logger.warning("登陆授权过期，已自动忽略并继续执行...")
        return False

    @TransitionOn("版本更新1")
    def _(self):
        self.operationer.click_and_wait("重启游戏")
        self.logger.warning("游戏出现版本更新，请重启游戏更新")
        return False

    @TransitionOn("版本更新2")
    def _(self):
        self.operationer.click_and_wait("重启")
        self.logger.warning("游戏出现版本更新，此更新必须重启")
        return False

    @TransitionOn("是否隐藏气泡")
    def _(self):
        self.operationer.click_and_wait("关闭所有气泡")
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("网络连接失败")
    def _(self):
        self.operationer.click_and_wait("确定")
        self.logger.warning("决斗场网络连接失败，已退出战斗")
        return False

    @TransitionOn("聊天频道")
    def _(self):
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("网络异常重连失败")
    def _(self):
        self.operationer.click_and_wait("确定")
        self.logger.warning("网络异常重连失败，已退出战斗")
        return False

    @TransitionOn("未知含X场景")
    def _(self):
        if self.operationer.search_and_click([
                self.operationer.get_element("X-普通", "主场景"),
                self.operationer.get_element("X-广告-1", "主场景"),
                self.operationer.get_element("X-广告-2", "主场景")
        ], [],
                                             once_max_attempts=1,
                                             max_attempts=1):
            self.logger.info("点击X关闭")
        return False

    @TransitionOn("未知场景")
    def _(self):
        time.sleep(1)
        return False

    @TransitionOn("未注册场景")
    def _(self):
        return False
