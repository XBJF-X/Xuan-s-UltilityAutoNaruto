from abc import abstractmethod
import datetime
import inspect
import sys
import threading
import time
from datetime import timedelta
from enum import IntEnum
from logging import Logger
from pathlib import Path
from types import FrameType
from typing import Any, Dict, Callable, List, Tuple
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
)
from backend.core.legacy.Operationer import Operationer
from backend.core.legacy.Scene.TransitionManager import TransitionManager
from backend.core.scheduler.runtime import RuntimeContext


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

    def wrapper(self, *args, **kwargs):
        old_trace = sys.gettrace()
        sys.settrace(self.trace_callback)
        try:
            result = func(self, *args, **kwargs)
            return result
        finally:
            sys.settrace(old_trace)

    return wrapper
def debug_execute_window(func):

    def wrapper(self, *args, **kwargs):
        old_trace = sys.gettrace()
        sys.settrace(self.trace_callback)
        try:
            result = func(self, *args, **kwargs)
            # self.logger.debug(f"可执行时间窗口: {[f'{start_dt.strftime('%Y-%m-%d %H:%M:%S')} - {end_dt.strftime('%Y-%m-%d %H:%M:%S')}' for start_dt, end_dt in result]}")
            return result
        finally:
            sys.settrace(old_trace)

    return wrapper

def handle_task_exceptions(func):

    def wrapper(self, *args, **kwargs):
        old_trace = sys.gettrace()
        sys.settrace(self.trace_callback)
        self.logger.info("开始执行")
        self.last_execute_error = None
        before_next_execute_ts = self.config.get_task_base_config(
            self.task_name, "下次执行时间")
        try:
            func(self, *args, **kwargs)
        except TaskCompleted as e:
            self.logger.info(str(e) if str(e) else "任务执行完成")
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
            self.logger.info(str(e) if str(e) else "任务执行时间过早，推迟执行")
            self._cleanup_on_too_early()
            self.schedule_next_on_too_early()
        except StepFailedError as e:
            self.logger.error(e)
            self.last_execute_error = str(e)
            self._auto_screenshot("StepFailedError")
        except Stop as e:
            self.logger.warning("线程被要求停止")
            self._cleanup_on_stop()
        except TimeOutDeadLineError as e:
            self.logger.error(f"任务超时：已到达可执行窗口DeadLine")
            self.last_execute_error = str(e)
            self._auto_screenshot("TimeOutDeadLineError")
            self._cleanup_on_timeout()
            self.schedule_next_on_timeout_deadline()
        except  TimeOutMaxDurationError as e:
            self.logger.error(f"任务超时：超过任务最大执行时长")
            self.last_execute_error = str(e)
            self._auto_screenshot("TimeOutMaxDurationError")
            self._cleanup_on_timeout()
            self.schedule_next_on_timeout_max_duration()
        except Exception as e:
            self.logger.error(f"未知错误：{e}")
            self.last_execute_error = str(e)
            self._auto_screenshot("UnknownError")
        finally:
            sys.settrace(old_trace)
            try:
                self.bool_click = False
                self.logger.debug("回调函数执行")
                self.callback(self)
            except Exception as e:
                self.logger.error(f"callback执行出错: {e}")

    return wrapper






class BaseTask:

    transition_func: Dict[str, Callable] = {}
    """场景名到处理函数的映射，由TransitionOn装饰器填充"""
    transition_return: str = ""
    """记录transition返回的位置，方便调试"""
    source_scene: str | None = None
    """任务的初始场景，需要先寻路到此处才能正式开始执行任务"""

    base_priority: int
    """基础优先级，数值越小优先级越高"""
    click_priority: int
    """执行连点时的优先级，数值越小优先级越高"""

    task_max_duration: timedelta = timedelta(minutes=10)
    """任务最长执行时间（无DDL的情况下生效）"""
    start_line: datetime.time | None = None
    """任务当天最早开始的时间点，如果早于该时间点将推迟到该时间点执行"""
    dead_line: datetime.time | None = None
    """任务当天截至的时间点（超过当天该时间点将强制结束任务）"""

    tz_info = ZoneInfo("Asia/Shanghai")

    UNREGISTER_SCENE_MAX_TIME = 15

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
        # 最后一次执行是否出错（供调度器向前端透传失败标记）
        self.last_execute_error = None

        # 超时监视器（由调度器在任务开始执行前注入，任务结束后收回）
        self.watchdog = None

        self.schedule_next_on_initialization()
        self.transition_func = {}
        for cls in reversed(self.__class__.mro()):
            if hasattr(cls, "transition_func"):
                self.transition_func.update(cls.transition_func)
        # for scene, func in self.transition_func.items():
        #     self.logger.debug(f"注册场景处理函数: {scene} -> {func.__qualname__}")

        self.transition_manager = transition_manager
        self.operationer = operationer
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

    def stop(self):
        """发出停止请求（非阻塞）"""
        self.logger.info(f"正在请求停止任务: {self.task_name}")
        self.operationer.stop_event.set()

    def _should_stop(self):
        """检查是否收到停止请求"""
        return self.operationer.stop_event.is_set()

    def _ensure_tz_aware(self, dt: datetime.datetime) -> datetime.datetime:
        """将datetime标准化为任务时区的有时区对象。"""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=self.tz_info)
        return dt.astimezone(self.tz_info)

    def _check_window_invalid(self, dt: datetime.datetime, base: datetime.datetime|None=None) -> bool:
        """检查时间是否在可执行窗口内"""
        dt = self._ensure_tz_aware(dt)
        windows = self._get_execute_window(self._ensure_tz_aware(base) if base else None)
        for start_dt, end_dt in windows:
            if start_dt:
                start_dt = self._ensure_tz_aware(start_dt)
            if end_dt:
                end_dt = self._ensure_tz_aware(end_dt)
            if start_dt and dt < start_dt:
                return True
            if end_dt and dt >= end_dt:
                return True
        return False

    def _check_timeout(self, current_time: datetime.datetime) -> bool:
        """检查是否超过任务最大执行时间"""
        if self.task_max_duration:
            if current_time - self.last_run_time > self.task_max_duration:
                return True
        return False

    @handle_task_exceptions
    def _execute(self):
        self.operationer.next_scene = self.source_scene
        while True:
            # 检查停止信号
            if self._should_stop():
                raise Stop("任务被停止")

            current_time = datetime.datetime.now(self.tz_info)
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
                # 如果至少有一个窗口可执行，则只警告其他不符合的窗口，不抛错
                for dt in too_early_windows:
                    self.logger.warning(f"[StartLine]未到任务可执行时间:{dt.strftime('%Y-%m-%d %H:%M:%S')}")
                for dt in expired_windows:
                    self.logger.warning(f"[DeadLine]可执行窗口已过:{dt.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                # 所有窗口都不符合时再抛出错误，尽量保留原有异常类型和信息
                if too_early_windows and not expired_windows:
                    next_start = min(too_early_windows)
                    raise TooEarlyToRun(f"[StartLine]未到任务可执行时间:{next_start.strftime('%Y-%m-%d %H:%M:%S')}")
                if expired_windows and not too_early_windows:
                    last_deadline = max(expired_windows)
                    raise TimeOutDeadLineError(f"[DeadLine]任务执行超时:{last_deadline.strftime('%Y-%m-%d %H:%M:%S')}")
                # 混合情况：优先按 DeadLine 抛错
                if expired_windows:
                    last_deadline = max(expired_windows)
                    raise TimeOutDeadLineError(f"[DeadLine]任务执行超时:{last_deadline.strftime('%Y-%m-%d %H:%M:%S')}")
                # 兜底
                raise TooEarlyToRun("任务当前时间不在任何可执行窗口内")
            if self._check_timeout(current_time):
                raise TimeOutMaxDurationError(f"[MaxDuration]任务执行超时:{current_time.strftime('%Y-%m-%d %H:%M:%S')}")

            # 执行步骤转换
            result = self.transition()
            if result is not None and result:
                raise TaskCompleted("任务执行完成")

    @handle_transition_exceptions
    def transition(self):
        # 获取当前屏幕截图并识别场景
        screenshot = self.operationer.screen_cap()
        scene = self.operationer.recognizer.scene(screenshot,bool_debug=False)

        # 确保待调用的场景名为str
        if isinstance(scene, str):
            self.logger.info(f"识别到场景: [Str] {scene}")
            scene_name = scene
        else:
            self.logger.info(f"识别到场景: [Scene] {scene.name}")
            self.operationer.current_scene = scene
            scene_name = scene.name
        # 向超时监视器上报当前场景（心跳），用于场景停滞/卡死检测
        if self.watchdog is not None:
            try:
                self.watchdog.heartbeat(scene_name)
            except Exception:
                pass
        # 如果设置了next_scene，优先跳转
        if self.operationer.next_scene:
            if self.operationer.next_scene == scene_name:
                self.operationer.next_scene = None
            else:
                path = self.transition_manager.bfs_shortest_path(
                    scene_name, self.operationer.next_scene)
                if path and len(path) >= 2:
                    return self.transition_manager.transition(self.operationer)

        if scene_name in self.transition_func:
            if self.last_unregistered_scene_time:
                self.last_unregistered_scene_time = None
            func = self.transition_func[scene_name]
            # self.logger.debug(f"场景{scene_name}绑定的函数：{func.__qualname__}")
            result = self.transition_func[scene_name](self)
            return result
        else:
            if not self.last_unregistered_scene_time:
                self.last_unregistered_scene_time=time.perf_counter()
            if not self.source_scene:
                # 没有 source_scene，无法寻路，回退到未注册场景
                scene_name = "未注册场景"
            else:
                if self.last_unregistered_scene_time and time.perf_counter() - self.last_unregistered_scene_time > self.UNREGISTER_SCENE_MAX_TIME:
                    self.logger.warning(f"长时间未识别到注册场景，强制跳转回 source_scene: {self.source_scene}")
                    self._auto_screenshot("UnregisteredSceneForceReturn")
                    self.operationer.next_scene = self.source_scene
                    shortest_path = self.transition_manager.bfs_shortest_path(
                        scene_name, self.source_scene)
                    if shortest_path and len(shortest_path) >= 2:
                        # 执行第一段路径跳转
                        next_scene_in_path = shortest_path[1]
                        self.logger.info(
                            f"自动跳转回场景状态中: 从 {scene_name} 到 {next_scene_in_path} (路径: {' -> '.join(shortest_path)})"
                        )
                        return self.transition_manager.transition(self.operationer)
                else:
                    # 如果找不到路径，回退到原来的处理方式
                    scene_name = "未注册场景"

        # 正常执行注册函数
        # self.logger.debug(f"寻找注册函数: {scene_name}")
        func = self.transition_func[scene_name]
        # self.logger.debug(f"场景{scene_name}绑定的函数：{func.__qualname__}")
        # 执行派生类的场景处理函数
        result = self.transition_func[scene_name](self)
        # self.logger.debug(f"[{scene_name}]注册函数执行完毕")
        # self.logger.debug(f"Transition的Result：{result}")
        # self.logger.debug(f"Transition的next_scene：{self.operationer.next_scene}")
        return result

    def trace_callback(self, frame: FrameType, event, arg):
        if event == "call":
            func_name = "_" if hasattr(self, "source_scene") else "transition"
            if frame.f_code.co_name == func_name:
                frame.f_trace_lines = False
                return self.trace_callback
        elif event == "return":
            try:
                srcfile = inspect.getsourcefile(frame) or inspect.getfile(
                    frame)
            except Exception:
                srcfile = None
            if srcfile is None:
                relative_path = Path("<unknown>")
            else:
                relative_path = Path(srcfile)
            try:
                relative_path = relative_path.relative_to(get_real_path())
            except ValueError:
                pass
            self.transition_return = f"{relative_path}:{frame.f_lineno}"
            self.logger.debug(self.transition_return)

    def _cleanup_on_stop(self):
        """停止请求时的清理"""
        self.operationer.clicker.stop()
        self.reset_task_exe_prog()

    def _auto_screenshot(self, reason: str):
        """错误/超时/异常场景自动截图一次，保存到 log/<用户名>/<日期>/screenshot/<任务名>/，
        便于用户打包反馈后开发者排查。可通过配置"错误自动截图"关闭，任何异常不阻断任务流程。
        """
        try:
            if not self.config.get_config("错误自动截图", True):
                return
            op = self.operationer
            if op is None:
                return
            save_func = getattr(op, "screen_save_func", None)
            if callable(save_func):
                save_func(self.task_name)
                self.logger.info(f"已自动保存错误截图（原因: {reason}）")
                return
            # 兜底：直接截图保存
            frame = op.screen_cap()
            if frame is None:
                return
            import os
            import cv2
            from datetime import datetime
            from backend.utils import get_real_path
            username = self.config.get_config("用户名", "unknown") or "unknown"
            safe_name = str(username).replace("/", "_").replace("\\", "_")
            date_str = datetime.now().strftime("%Y-%m-%d")
            save_dir = os.path.join(get_real_path("log"), safe_name, date_str,
                                    "screenshot", self.task_name)
            os.makedirs(save_dir, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filepath = os.path.join(save_dir, f"{ts}_{reason}.png")
            ok, buf = cv2.imencode(".png", frame)
            if ok:
                buf.tofile(filepath)
                self.logger.info(f"已自动保存错误截图: {filepath}")
        except Exception as e:
            self.logger.warning(f"错误截图保存失败: {e}")

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

    def _activate_another_task(self, task_name: str):
        """
        立即执行某一任务
        Args:
            task_name(str):需要立即执行的任务名称

        Returns:

        """
        self.logger.info(f"{task_name}被激活，将立即执行")
        self.activate_another_task_func(task_name)

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
        next_execute_time = self._handle_execution_completed(current_time)
        return self._save_next_execute_time(next_execute_time)

    def schedule_next_on_timeout_deadline(
            self) -> tuple[bool, datetime.datetime | None]:
        current_time = datetime.datetime.now(self.tz_info)
        next_execute_time = self._handle_timeout_deadline(current_time)
        return self._save_next_execute_time(next_execute_time)
    
    def schedule_next_on_timeout_max_duration(
            self) -> tuple[bool, datetime.datetime | None]:
        current_time = datetime.datetime.now(self.tz_info)
        next_execute_time = self._handle_timeout_max_duration(current_time)
        return self._save_next_execute_time(next_execute_time)

    def schedule_next_on_too_early(
            self) -> tuple[bool, datetime.datetime | None]:
        current_time = datetime.datetime.now(self.tz_info)
        next_execute_time = self._handle_too_early(current_time)
        return self._save_next_execute_time(next_execute_time)

    def schedule_next_with_delay(
            self, delta: timedelta) -> tuple[bool, datetime.datetime | None]:
        current_time = datetime.datetime.now(self.tz_info)
        next_execute_time = self._handle_delay(current_time, delta)
        return self._save_next_execute_time(next_execute_time)

    def schedule_execute_now(self) -> tuple[bool, datetime.datetime | None]:
        current_time = datetime.datetime.now(self.tz_info)
        next_execute_time = self._handle_execute_now(current_time)
        return self._save_next_execute_time(next_execute_time)

    ############################################################################################
    #                                和任务执行时间处理相关的函数                                 #
    ############################################################################################
    @debug_execute_window
    def _get_execute_window(
        self,
        dt: datetime.datetime | None = None
    ) -> List[Tuple[datetime.datetime, datetime.datetime]]:
        """
        返回一个列表，列表中的每个元素是一个二元组(start_dt, end_dt)，表示一个可执行窗口的开始和结束时间  
        执行检查时应以self.last_run_time为基准，避免执行时跨过窗口期导致的异常
        """
        if dt is None:
            dt=self.last_run_time
        dt = self._ensure_tz_aware(dt)
        today = dt.date()
        if dt.time() < datetime.time(5, 0):
            today -= timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        start_dt = datetime.datetime.combine(today, self.start_line or datetime.time(5, 0), tzinfo=self.tz_info)
        if self.dead_line:
            dead_dt = datetime.datetime.combine(today, self.dead_line, tzinfo=self.tz_info)
        else:
            dead_dt = datetime.datetime.combine(tomorrow, datetime.time(5, 0), tzinfo=self.tz_info)

        return [(start_dt, dead_dt)]

    def get_next_cycle_day(self, dt: datetime.datetime) -> datetime.datetime:
        """返回dt所在周期的下个周期的第一天"""
        return dt + timedelta(days=1)

    def get_cycle_execute_time(self,
                               dt: datetime.datetime,
                               completed=False) -> datetime.datetime:
        """返回 dt 所属执行周期的任务执行时间"""
        window=self._get_execute_window(self.get_next_cycle_day(self._ensure_tz_aware(dt)) if completed else None)
        return window[0][0]

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

    def _handle_execution_completed(
            self, current_time: datetime.datetime) -> datetime.datetime:
        """返回下一个执行周期的任务执行时间"""
        return self.get_cycle_execute_time(current_time, completed=True)

    def _handle_timeout_deadline(self,
                        current_time: datetime.datetime) -> datetime.datetime:
        """处理超时逻辑"""
        return self._handle_execution_completed(current_time)
    
    def _handle_timeout_max_duration(self,
                        current_time: datetime.datetime) -> datetime.datetime:
        """处理超时逻辑"""
        return self._handle_initialization(current_time)


    def _handle_too_early(
            self, current_time: datetime.datetime) -> datetime.datetime:
        """过早执行时默认推迟到周期窗口开始时间"""
        return self._handle_initialization(current_time)


    def _handle_execute_now(
            self, current_time: datetime.datetime) -> datetime.datetime:
        """立即执行时间计算"""
        return self._handle_delay(current_time, timedelta(0))

    def _handle_delay(self, current_time: datetime.datetime,
                      delta: timedelta) -> datetime.datetime:
        """处理时间延迟更新"""
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
