import inspect
import sys
import threading
from datetime import datetime, timedelta, time
from logging import Logger
from pathlib import Path
from types import FrameType
from typing import Dict, Callable
from zoneinfo import ZoneInfo

from PySide6.QtCore import Signal, QThread

from StaticFunctions import get_real_path
from utils.Base.Config import Config
from utils.Base.Exceptions import StepFailedError, TimeOut, Stop, EndEarly
from utils.Base.Operationer import Operationer
from utils.Base.Scene.TransitionManager import TransitionManager


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
        except StepFailedError as e:
            self.logger.error(e)
        except EndEarly as e:
            self.logger.warning(e)
            return True
        except Stop as e:
            self.logger.warning("线程被要求停止")
        except TimeOut as e:
            self.logger.error(f"任务超时：{e}")
        except Exception as e:
            self.logger.error(f"未知错误：{e}")
            return True
        finally:
            sys.settrace(old_trace)

    return wrapper


def handle_task_exceptions(func):
    def wrapper(self, *args, **kwargs):
        self.logger.debug("开始执行")
        try:
            func(self, *args, **kwargs)
        except StepFailedError as e:
            self.logger.error(e)
        except EndEarly as e:
            self.logger.warning(e)
            return True
        except Stop as e:
            self.logger.warning("线程被要求停止")
        except TimeOut as e:
            self.logger.error(f"任务超时：{e}")
        except Exception as e:
            self.logger.error(f"未知错误：{e}")
        finally:
            _handle_callback(self)

    return wrapper


def _handle_callback(self):
    try:
        self.logger.debug("回调函数执行")
        self.callback(self)
    except Exception as e:
        self.logger.error(f"callback执行出错: {e}")


class BaseTask:
    transition_func: Dict[str, Callable] = {}
    """场景名到处理函数的映射，由TransitionOn装饰器填充"""
    transition_return: str | None = ""
    """记录transition返回的位置，方便调试"""
    source_scene: str | None = None
    """任务的初始场景"""
    task_max_duration: timedelta | None = None
    """任务最长执行时间（无DDL的情况下生效）"""
    task_once_transition_on_max_duration: timedelta | None = None
    """预估单个TransitionOn最大执行时间，用于调度器计算是否应提前停止任务"""
    dead_line: datetime | time | None = None
    """任务截至的时间点（超过当天该时间点将强制结束任务）"""
    temp_dead_line: datetime | None = None
    """每次任务执行时根据上述时间参数计算出来的临时DeadLine，结束后自动置空"""

    def __init__(
        self,
        task_name: str,
        config: Config,
        transition_manager: TransitionManager,
        operationer: Operationer,
        activate_another_task_signal: Signal(str),
        callback: Callable,
        parent_logger
    ):
        # 任务信息
        self.create_time = datetime.now(ZoneInfo("Asia/Shanghai"))
        self.current_status = 2
        # 0 - 正在执行
        # 1 - 就绪状态，等待执行
        # 2 - 等待状态，等待就绪
        self.config = config
        self._execution_thread = None
        self.task_name = task_name
        self.logger: Logger = parent_logger.getChild(self.task_name)
        self.base_priority = config.get_task_base_config(self.task_name, "优先级")

        self.update_next_execute_time(0)
        self.transition_func = {}
        for cls in reversed(self.__class__.mro()):
            if hasattr(cls, "transition_func"):
                self.transition_func.update(cls.transition_func)
        # for scene, func in self.transition_func.items():
        #     self.logger.debug(f"注册场景处理函数: {scene} -> {func.__qualname__}")

        self.transition_manager = transition_manager
        self.operationer = operationer
        self.activate_another_task_signal = activate_another_task_signal
        self.callback = callback

    @property
    def is_activated(self):
        return self.config.get_task_base_config(self.task_name, "是否启用")

    @property
    def temp_priority(self):
        return self.config.get_task_base_config(self.task_name, "临时提权")

    def __lt__(self, other):
        """
        任务比较规则：
        1. temp_priority=True的任务优先级更高（值更大）
        2. temp_priority相同的情况下，base_priority小的优先级更高
        3. 如果base_priority也相同，create_time小的优先级更高

        注意：由于堆是最小堆，我们需要让优先级高的任务"更小"
        """
        # 1. 比较临时提权状态
        if self.temp_priority != other.temp_priority:
            # 有临时提权的任务优先级更高，在最小堆中应该排在前面（值更小）
            return self.temp_priority > other.temp_priority

        # 2. 比较基础优先级
        if self.base_priority != other.base_priority:
            # base_priority大的优先级更高，在最小堆中应该排在前面（值更小）
            return self.base_priority < other.base_priority

        # 3. 比较创建时间
        # create_time小的优先级更高，在最小堆中应该排在前面（值更小）
        return self.create_time < other.create_time

    def __repr__(self):
        info_text = (f"任务名称: {self.task_name},"
                     f"任务ID:{self.base_priority},"
                     f"是否启用:{self.is_activated},"
                     f"任务状态:{self.current_status},"
                     f"下次执行时间:{self.next_execute_time}"
                     )
        return info_text

    def run(self):
        """
        启动新线程执行execute避免阻塞进程
        """
        # 重置停止标志
        self.operationer.stop_event.clear()  # 重置停止标志
        # 保存线程对象以便后续停止
        self._execution_thread = threading.Thread(target=self._execute, daemon=True)
        self._execution_thread.start()

    def stop(self):
        """
        停止当前正在执行的任务
        """
        self.logger.info(f"正在停止任务: {self.task_name}")
        # 设置停止标志
        self.operationer.stop_event.set()
        # 如果任务线程正在运行，等待其结束
        if (hasattr(self, '_execution_thread') and self._execution_thread
                and self._execution_thread.is_alive()):
            self._execution_thread.join(timeout=5.0)
            if self._execution_thread.is_alive():
                self.logger.warning(f"任务 {self.task_name} 线程未能在5秒内停止")
        self.operationer.clicker.stop()

    def _should_stop(self):
        """检查是否收到停止请求"""
        return self.operationer.stop_event.is_set()

    @handle_task_exceptions
    def _execute(self):
        if not self.dead_line:
            if self.task_max_duration:
                self.temp_dead_line = datetime.now(tz=ZoneInfo("Asia/Shanghai")) + self.task_max_duration
        else:
            self.temp_dead_line = datetime.now(tz=ZoneInfo("Asia/Shanghai")).replace(
                hour=self.dead_line.hour,
                minute=self.dead_line.minute,
                second=self.dead_line.second,
                microsecond=self.dead_line.microsecond
            )
        self.operationer.next_scene = self.source_scene
        while True:
            if self.temp_dead_line and datetime.now(tz=ZoneInfo("Asia/Shanghai")) > self.temp_dead_line:
                self.logger.warning("任务达到最大执行时长，强制结束")
                self.operationer.clicker.stop()
                self.update_next_execute_time()
                return
            if self._should_stop():
                self.logger.warning("任务被停止")
                return

            result = self.transition()
            if result is not None:
                if result:
                    self.logger.debug("重置任务执行进度")
                    self.reset_task_exe_proc()
                    return

    @handle_transition_exceptions
    def transition(self):
        # 获取当前屏幕截图并识别场景
        screenshot = self.operationer.screen_cap()
        scene = self.operationer.recognizer.scene(screenshot)

        # 确保待调用的场景名为str
        if isinstance(scene, str):
            self.logger.debug(f"识别到场景: [Str] {scene}")
            scene_name = scene
        else:
            self.logger.debug(f"识别到场景: [Scene] {scene.name}")
            self.operationer.current_scene = scene
            scene_name = scene.name

        # 确保跳转的时候不是未知场景
        if scene_name in ["未知含X场景", "未知场景"]:
            func = self.transition_func[scene_name]
            self.logger.debug(f"场景{scene_name}绑定的函数：{func.__qualname__}")
            result = self.transition_func[scene_name](self)
            return result

        if scene.name not in self.transition_func:
            # 如果设置了next_scene，优先跳转
            if self.operationer.next_scene:
                if self.operationer.next_scene == scene_name:
                    self.operationer.next_scene = None
                else:
                    return self.transition_manager.transition(self.operationer)

            # 自动寻找从当前场景到任意已注册场景的路径
            registered_scenes = list(self.transition_func.keys())
            shortest_path = None

            # 寻找最短路径
            for target_scene in registered_scenes:
                path = self.transition_manager.bfs_shortest_path(scene_name, target_scene)
                if path and (shortest_path is None or len(path) < len(shortest_path)):
                    shortest_path = path

            if shortest_path and len(shortest_path) >= 2:
                # 执行第一段路径跳转
                next_scene_in_path = shortest_path[1]
                self.logger.info(f"自动跳转: 从 {scene_name} 到 {next_scene_in_path} (路径: {' -> '.join(shortest_path)})")
                self.operationer.next_scene = next_scene_in_path
                return self.transition_manager.transition(self.operationer)
            else:
                # 如果找不到路径，回退到原来的处理方式
                scene_name = "未注册场景"
        # 如果设置了next_scene，优先跳转
        if self.operationer.next_scene:
            if self.operationer.next_scene == scene_name:
                self.operationer.next_scene = None
            else:
                return self.transition_manager.transition(self.operationer)
        # # 正常执行注册函数
        # self.logger.debug(f"寻找注册函数: {scene_name}")
        func = self.transition_func[scene_name]
        self.logger.debug(f"场景{scene_name}绑定的函数：{func.__qualname__}")
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
            relative_path = Path(inspect.getsourcefile(frame))
            try:
                relative_path = relative_path.relative_to(get_real_path())
            except ValueError:
                pass
            self.transition_return = f"{relative_path}:{frame.f_lineno}"
            self.logger.debug(self.transition_return)

    def _activate_another_task(self, task_name: str):
        """
        立即执行某一任务
        Args:
            task_name(str):需要立即执行的任务名称

        Returns:

        """
        self.logger.debug(f"{task_name}被激活，将立即执行")
        self.activate_another_task_signal.emit(task_name)

    @property
    def current_priority(self):
        """返回当前有效优先级（临时优先级优先于基础优先级）"""
        return self.temp_priority if self.temp_priority is not None else self.base_priority

    @property
    def next_execute_time(self):
        china_tz = ZoneInfo("Asia/Shanghai")
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")
        if next_exec_ts == 0:
            # 若初始值为0，设置为当前中国时区时间
            return datetime.now(china_tz)
        else:
            # 从时间戳转换为datetime对象
            return datetime.fromtimestamp(next_exec_ts, tz=china_tz)

    def update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        """
        用于更新本任务的下次执行时间

        Args:
            flag: 更新下次执行时间的模式
                0：创建任务时初始化时间
                1：正常执行完毕，更新为下次执行时间
                3：把执行时间推迟delta时间，要求 delta!=None
            delta: 延迟的时长（仅flag=3时有效）
        Returns:
            tuple: (是否成功, 下次执行时间datetime对象)
        """
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        try:
            match flag:
                case 0:
                    next_execute_time = self._handle_initialization(current_time)
                case 1:
                    next_execute_time = self._handle_execution_completed(current_time)
                case 2:
                    next_execute_time = current_time
                case 3:
                    next_execute_time = self._handle_delay(current_time, delta)
                case _:
                    self.logger.warning(f"不支持的更新模式: {flag}")
                    return False, None

            if next_execute_time is None:
                return False, None

            self.logger.info(f"下次执行时间为：{next_execute_time.strftime('%Y-%m-%d %H:%M:%S')}")
            self.config.set_task_base_config(
                self.task_name,
                "下次执行时间",
                int(next_execute_time.timestamp())
            )
            return True, next_execute_time

        except Exception as e:
            self.logger.error(f"更新下次执行时间失败: {str(e)}")
            return False, None

    def _handle_initialization(self, current_time: datetime) -> datetime:
        """处理任务初始化时的时间设置（case0）"""
        china_tz = current_time.tzinfo
        # 读取配置中的时间
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")

        next_execute_time = datetime(
            current_time.year,
            current_time.month,
            current_time.day,
            5, 0, 20,
            tzinfo=china_tz
        )

        if next_exec_ts == 0:
            return next_execute_time
        else:
            # 转换为带时区的datetime
            stored_time = datetime.fromtimestamp(next_exec_ts, tz=china_tz)
            if stored_time + timedelta(days=1) < current_time:
                return next_execute_time
            else:
                return stored_time

    def _handle_execution_completed(self, current_time: datetime) -> datetime:
        """处理任务执行完成后的时间更新（case1）"""
        china_tz = current_time.tzinfo
        next_day = current_time + timedelta(days=1)
        return datetime(
            next_day.year,
            next_day.month,
            next_day.day,
            5, 0, 20,
            tzinfo=china_tz
        )

    def _handle_delay(self, current_time: datetime, delta: timedelta) -> datetime:
        """处理时间延迟更新（case3）"""
        if delta is None:
            self.logger.warning("延迟更新时间时delta不能为空")
            return None
        return current_time + delta

    def reset_task_exe_proc(self) -> bool:
        """重置任务执行进度参数"""
        return True

    @TransitionOn("二级密码")
    def _(self):
        self.logger.debug("出现二级密码窗口")
        passward = self.config.get_config("二级密码")
        if len(passward) != 6:
            raise StepFailedError("请检查二级密码！")
        # 输入操作
        self.operationer.click_and_input(
            self.operationer.get_element("输入框"),
            passward
        )
        # 点击二级密码-确定
        if not self.operationer.click_and_wait(
                self.operationer.get_element("确定"),
                auto_raise=False
        ):
            raise StepFailedError("二级密码验证失败")
        return False

    @TransitionOn("好友排名至X位")
    def _(self):
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("升级")
    def _(self):
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("公告")
    def _(self):
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("版本更新1")
    def _(self):
        self.operationer.click_and_wait("下次再说")
        self.logger.warning("游戏出现版本更新，请重启游戏更新")
        return False

    @TransitionOn("决斗场-网络连接失败")
    def _(self):
        self.operationer.click_and_wait("确定")
        self.logger.warning("决斗场网络连接失败，已退出战斗")
        return False

    @TransitionOn("未知含X场景")
    def _(self):
        if self.operationer.search_and_click(
                [
                    self.operationer.get_element("X-普通", "主场景"),
                    self.operationer.get_element("X-广告-1", "主场景"),
                    self.operationer.get_element("X-广告-2", "主场景")
                ],
                [],
                once_max_attempts=1,
                max_attempts=1
        ):
            self.logger.info("点击X关闭")
        return False

    @TransitionOn("未知场景")
    def _(self):
        QThread.msleep(1000)
        return False

    @TransitionOn("未注册场景")
    def _(self):
        return False
