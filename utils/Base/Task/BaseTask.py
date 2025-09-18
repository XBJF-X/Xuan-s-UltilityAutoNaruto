import inspect
import sys
import threading
from datetime import datetime, timedelta, time
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
            # self.logger.debug(f"装饰器接收的Result：{result}")
            return result
        except StepFailedError as e:
            self.logger.error(e)
            return True
        except EndEarly as e:
            self.logger.warning(e)
            return True
        except Stop as e:
            self.logger.warning("线程被要求停止")
            return True
        except TimeOut as e:
            self.logger.error(f"任务超时：{e}")
            return True
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
        except Stop as e:
            self.logger.warning("线程被要求停止")
        except TimeOut as e:
            self.logger.error(f"任务超时：{e}")
        except Exception as e:
            self.logger.error(f"未知错误：{e}")
        finally:
            _handle_callback(self)

    return wrapper


# 辅助函数：统一处理回调
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
    dead_line: time | datetime | None = None
    """任务截至的时间点（超过当天该时间点将强制结束任务）"""

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
        self.logger = parent_logger.getChild(self.task_name)
        self.task_id = config.get_task_base_config(self.task_name, "优先级")
        self.base_priority = 0  # 静态默认优先级
        self.temp_priority = None  # 临时优先级（None表示未启用）

        self.update_next_execute_time(0)
        self.transition_func = {}
        for cls in reversed(self.__class__.mro()):
            if hasattr(cls, "transition_func"):
                self.transition_func.update(cls.transition_func)
        for scene, func in self.transition_func.items():
            self.logger.debug(f"注册场景处理函数: {scene} -> {func.__qualname__}")

        self.transition_manager = transition_manager
        self.operationer = operationer
        self.activate_another_task_signal = activate_another_task_signal
        self.callback = callback

    @property
    def next_execute_time(self):
        china_tz = ZoneInfo("Asia/Shanghai")
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")
        if next_exec_ts == 0:
            # 若初始值为0，设置为当前UTC时间（或其他合理时间）
            return datetime.now(china_tz)
        else:
            # 从时间戳转换为datetime对象
            return datetime.fromtimestamp(next_exec_ts, tz=china_tz)

    @property
    def is_activated(self):
        return self.config.get_task_base_config(self.task_name, "是否启用")

    def __lt__(self, other):
        """
        优先级高的任务排在前面（值越大越优先）
        优先级相同时，再按task_id和创建时间排序
        """
        # # 优先比较当前有效优先级（逆序：高优先级在前）
        # if self.current_priority != other.current_priority:
        #     return self.current_priority > other.current_priority  # 注意这里是>，因为堆是最小堆
        # 优先级相同则比较task_id
        if self.task_id != other.task_id:
            return self.task_id < other.task_id
        # 最后比较创建时间
        return self.create_time < other.create_time

    def __repr__(self):
        info_text = (f"任务名称: {self.task_name},"
                     f"任务ID:{self.task_id},"
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
                self.dead_line = datetime.now(tz=ZoneInfo("Asia/Shanghai")) + self.task_max_duration
        else:
            self.dead_line = datetime.now(tz=ZoneInfo("Asia/Shanghai")).replace(
                hour=self.dead_line.hour,
                minute=self.dead_line.minute,
                second=self.dead_line.second,
                microsecond=self.dead_line.microsecond
            )
        self.operationer.next_scene = self.source_scene
        while True:
            if self.dead_line and datetime.now(tz=ZoneInfo("Asia/Shanghai")) > self.dead_line:
                self.logger.warning("任务达到最大执行时长，强制结束")
                self.update_next_execute_time()
                raise TimeOut(f"任务超时")
            if self._should_stop():
                raise Stop("任务被停止")

            result = self.transition()
            # self.logger.debug(f"Exe接收的Result：{result}")
            if result is not None:
                # self.logger.debug("结果非None")
                if result:
                    # self.logger.debug("任务执行完毕")
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
            scene_name = "未注册场景"

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

    def set_temp_priority(self, priority):
        """设置临时优先级（用于动态提高优先级）"""
        self.temp_priority = priority
        self.logger.debug(f"任务[{self.task_name}]临时优先级设为{priority}")

    def reset_priority(self):
        """重置临时优先级（恢复基础优先级）"""
        self.temp_priority = None
        self.logger.debug(f"任务[{self.task_name}]优先级已重置为基础值{self.base_priority}")

    def update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        """
        用于更新本任务的下次执行时间，默认为更新到第二天五点（也就是火影服务器任务刷新的时间）

        Args:
            flag: 更新下次执行时间的模式
                0：创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                1：正常执行完毕，更新为下次执行的时间
                2：立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                3：把执行时间推迟delta时间，要求 delta!=None
            delta: 延迟的时长
        Returns:

        """
        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)
        next_execute_time = current_time
        match flag:
            case 0:  # 创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                next_execute_time = self.next_execute_time

            case 1:  # 正常执行完毕，更新为下次执行的时间
                next_day = current_time + timedelta(days=1)
                next_execute_time = datetime(
                    next_day.year, next_day.month, next_day.day, 5, 0,
                    tzinfo=china_tz
                )

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                next_execute_time = current_time

            case 3:  # 把执行时间推迟delta时间，要求 delta!=None
                if delta is None:
                    self.logger.warning(f"update_next_execute_time传入的delta为空")
                    return False, None
                next_execute_time = current_time + delta

        self.logger.info(f"下次执行时间为：{next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
        self.config.set_task_base_config(self.task_name, "下次执行时间", int(next_execute_time.timestamp()))
        return True, next_execute_time

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

    @TransitionOn("公告")
    def _(self):
        self.operationer.click_and_wait("X")
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
