import inspect
import logging
import sys
import threading
from datetime import datetime, timedelta
from pathlib import Path
from types import FrameType
from typing import Dict, Callable
from zoneinfo import ZoneInfo

from PySide6.QtCore import Signal

from StaticFunctions import get_real_path
from utils.Base.Config import Config
from utils.Base.Enums import CycleType
from utils.Base.Exceptions import StepFailedError, TimeOut, Stop, EndEarly
from utils.Base.Operationer import Operationer
from utils.Base.Recognizer import Recognizer, SceneGraph
from utils.Base.Scene.TransitionManager import TransitionManager


def handle_transition_exceptions(func):
    def wrapper(self, *args, **kwargs):
        old_trace = sys.gettrace()
        sys.settrace(self.trace_callback)
        try:
            result = func(self, *args, **kwargs)
            self.logger.debug(f"装饰器接收的Result：{result}")
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
    waiting_scene = [

    ]
    transition_return: str = ""
    transition_func = {}
    source_scene: str | None = None
    task_max_duration: timedelta | None = None

    def __init__(
        self,
        task_name: str,
        config: Config,
        scene_graph: SceneGraph,
        transition_manager: TransitionManager,
        recognizer: Recognizer,
        operationer: Operationer,
        activate_another_task_signal: Signal(str),
        callback: Callable
    ):
        # 任务信息
        self.create_time = datetime.now(ZoneInfo("Asia/Shanghai"))
        self.current_status = 2
        # 0 - 正在执行
        # 1 - 就绪状态，等待执行
        # 2 - 等待状态，等待就绪
        self.config = config
        self.data: Dict = config.tasks.get(task_name)
        self._execution_thread = None
        self.task_name = self.data.get('任务名称')
        self.logger = logging.getLogger(self.task_name)
        self.task_id = self.data.get('任务ID')
        self.is_activated = self.data.get('是否启用')
        self.cycle_type = CycleType(self.data.get('周期类型'))
        self._update_next_execute_time(0)

        # 任务执行需要的组件
        self.scene_graph = scene_graph
        self.transition_manager = transition_manager
        self.recognizer = recognizer
        self.operationer = operationer
        self.activate_another_task_signal = activate_another_task_signal
        self.callback = callback

    def __lt__(self, other):
        # 先比较task_id，若相同则比较时间戳（确保唯一性）
        if self.task_id != other.task_id:
            return self.task_id < other.task_id
        return self.create_time < other.create_time

    def __repr__(self):
        info_text = (f"任务名称: {self.task_name},"
                     f"任务ID:{self.task_id},"
                     f"是否启用:{self.is_activated},"
                     f"任务状态:{self.current_status},"
                     f"周期类型:{CycleType(self.cycle_type)},"
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
        if hasattr(self, '_execution_thread') and self._execution_thread.is_alive():
            self._execution_thread.join(timeout=5.0)
            if self._execution_thread.is_alive():
                self.logger.warning(f"任务 {self.task_name} 线程未能在5秒内停止")

    def _should_stop(self):
        """检查是否收到停止请求"""
        return self.operationer.stop_event.is_set()

    @handle_task_exceptions
    def _execute(self):
        """
        任务的处理逻辑，默认需要自己重载为所用的逻辑
        """
        if self.task_max_duration:
            self.dead_line = datetime.now(tz=ZoneInfo("Asia/Shanghai")) + self.task_max_duration
        self.operationer.next_scene = self.source_scene
        while True:
            if self.task_max_duration:
                if datetime.now(tz=ZoneInfo("Asia/Shanghai")) > self.dead_line:
                    raise TimeOut(f"任务超时")
            if self._should_stop():
                raise Stop("任务停止")

            result = self.transition()
            self.logger.debug(f"Exe接收的Result：{result}")
            if result is not None:
                self.logger.debug("结果非None")
                if result:
                    self.logger.debug("任务执行完毕")
                    return

    @handle_transition_exceptions
    def transition(self):
        # 检查默认函数
        if self.source_scene is None:
            self.logger.debug("未设置起始场景，检查是否注册Default函数")
            if "Default" in self.transition_func:
                self.logger.info(f"使用默认函数处理: {self.task_name}")
                return self.transition_func["Default"](self)

        # 获取当前屏幕截图并识别场景
        screenshot = self.operationer.screen_cap()
        current_scene_obj = self.recognizer.scene(screenshot)

        if isinstance(current_scene_obj, str) and current_scene_obj == "未知场景":
            self.logger.warning("未知场景，将尝试进入可识别场景")
            self.operationer.click_and_wait(self.scene_graph.scenes.get("主场景").elements.get("公告-X"))
            self.operationer.click_and_wait(self.scene_graph.scenes.get("主场景").elements.get("广告-X"))
            return None

        self.logger.debug(f"识别到：{current_scene_obj.id}")

        self.operationer.current_scene = current_scene_obj
        if self.operationer.next_scene:
            if self.operationer.next_scene == current_scene_obj.id:
                self.operationer.next_scene = None
            else:
                return self.transition_manager.transition(self.operationer)
        current_scene_id = self.operationer.current_scene.id
        # 优先使用注册的跳转函数（派生类逻辑）
        if current_scene_id in self.transition_func:
            self.logger.debug(f"寻找到{current_scene_id}注册函数")
            # 执行派生类的场景处理函数
            result = self.transition_func[current_scene_id](self)
            self.logger.debug(f"{current_scene_id}注册函数执行完毕")
            self.logger.debug(f"Transition的Result：{result}")
            self.logger.debug(f"Transition的next_scene：{self.operationer.next_scene}")
            return result
        return self.transition_manager.transition(self.operationer)

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

    def _update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        """
        用于更新本任务的下次执行时间，默认需要派生类自己重载

        Args:
            flag: 更新下次执行时间的模式
                0：创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                1：正常执行完毕，更新为下次执行的时间
                2：立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                3：把执行时间推迟delta时间，要求 delta!=None

        Returns:

        """
        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        match flag:

            case 0:  # 创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                next_exec_ts = self.data.get('下次执行时间')
                if next_exec_ts == 0:
                    # 若初始值为0，设置为当前UTC时间（或其他合理时间）
                    self.next_execute_time = datetime.now(china_tz)
                else:
                    # 从时间戳转换为datetime对象（指定UTC时区避免歧义）
                    self.next_execute_time = datetime.fromtimestamp(next_exec_ts, tz=china_tz)

            case 1:  # 正常执行完毕，更新为下次执行的时间
                pass

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                self.next_execute_time = datetime.now(china_tz)

            case 3:  # 把执行时间推迟delta时间，要求 delta!=None
                if delta is None:
                    self.logger.warning(f"update_next_execute_time传入的delta为空")
                    return
                self.next_execute_time = current_time + delta

            case _:
                self.logger.warning(f"请检查update_next_execute_time传入的参数：flag={flag},delta={delta}")
                return

        self.logger.info(f"下次执行时间为：{self.next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
        self.config.set_task_config(self.task_name, "下次执行时间", int(self.next_execute_time.timestamp()))


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
