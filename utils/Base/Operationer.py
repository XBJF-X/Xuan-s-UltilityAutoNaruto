import concurrent.futures
import logging
import threading
import time
from typing import Tuple, List

from PySide6.QtCore import QThread, Signal

from utils.Base.Config import Config
from utils.Base.Device import Device
from utils.Base.Enums import ElementType
from utils.Base.Exceptions import StepFailedError, Stop
from utils.Base.Recognizer import Recognizer
from utils.Base.Scene.Element import Element
from utils.Base.Scene.Scene import Scene
from utils.Base.Scene.SceneGraph import SceneGraph


class Operationer:
    current_scene: Scene | None = None
    next_scene: str | None = None

    def __init__(self,
                 task_name: str,
                 config: Config,
                 device: Device,
                 recognizer: Recognizer,
                 scene_graph: SceneGraph,
                 screen_save_signal: Signal(str),
                 parent_logger
                 ):
        self.stop_event = threading.Event()
        self.task_name = task_name
        self.config = config
        self.device = device
        self.recognizer = recognizer
        self.scene_graph = scene_graph
        self.screen_save_signal = screen_save_signal
        self.logger = parent_logger.getChild(self.__class__.__name__)

    def _should_stop(self):
        """检查是否收到停止请求"""
        return self.stop_event.is_set()

    def stop(self):
        """
        停止当前正在执行的任务
        """
        self.logger.info(f"正在停止任务: {self.task_name}")
        # 设置停止标志
        self.stop_event.set()

    def detect_element(self, element, **kwargs):
        """
        检测并等待一段时间
        Args:
            element(str|Element): 元素名
            ** kwargs: 可选参数：
            - interval: 检测的间隔，默认为80ms
            - auto_raise: 是否自动抛出异常，默认为True
            - wait_time: 检测到之后的等待时间
            - max_time: 最大尝试时间，默认为2.0
            - max_attempts: 最大尝试次数，如果定义则优先，不定义则按最大时间
            - bool_debug：是否打印调试日志（默认True）
            - bool_save_screen：是否保存截图（默认True）
        """
        if isinstance(element, str):
            element = self.current_scene.elements.get(element)
        interval: int = kwargs.get("interval", 80)
        auto_raise: bool = kwargs.get("auto_raise", True)
        wait_time: float = kwargs.get("wait_time", 1.0)
        max_time: float = kwargs.get("max_time", 2.0)
        max_attempts: int | None = kwargs.get("max_attempts")
        bool_debug: bool = kwargs.get("bool_debug", True)
        bool_save_screen: bool = kwargs.get("bool_save_screen", True)

        start_time = time.perf_counter()
        success = False
        if bool_save_screen:
            self.screen_save_signal.emit(self.task_name)
        if max_attempts is not None:
            for i in range(max_attempts):
                time_1 = time.perf_counter()
                coordinates = self.recognizer.element_match(self.device.screen_cap(), element, bool_debug)
                if len(coordinates) != 0:
                    if bool_save_screen:
                        self.screen_save_signal.emit(self.task_name)
                    QThread.msleep(int(wait_time * 1000))
                    success = True
                    break
                sleep_time = max(0, int(interval - (time.perf_counter() - time_1)))
                QThread.msleep(sleep_time)
        else:
            while time.perf_counter() - start_time < max_time:
                time_1 = time.perf_counter()
                coordinates = self.recognizer.element_match(self.device.screen_cap(), element, bool_debug)
                if len(coordinates) != 0:
                    if bool_save_screen:
                        self.screen_save_signal.emit(self.task_name)
                    QThread.msleep(int(wait_time * 1000))
                    success = True
                    break
                sleep_time = max(0, int(interval - (time.perf_counter() - time_1)))
                QThread.msleep(sleep_time)
        # 根据auto_raise参数决定是抛出异常还是返回结果
        if not success and auto_raise:
            raise StepFailedError(f"元素 [{element.id}] 未出现")

        return success

    def detect_scene(self, scene, **kwargs):
        """
            检测并等待一段时间
            Args:
                scene(str|Scene): 元素名
                ** kwargs: 可选参数：
                - interval: 检测的间隔，默认为80ms
                - auto_raise: 是否自动抛出异常，默认为True
                - wait_time: 检测到之后的等待时间
                - max_time: 最大尝试时间，默认为2.0
                - max_attempts: 最大尝试次数，如果定义则优先，不定义则按最大时间
                - bool_debug：是否打印调试日志（默认True）
                - bool_save_screen：是否保存截图（默认True）
            """
        if isinstance(scene, str):
            scene = self.scene_graph.scenes.get(scene)
        interval: int = kwargs.get("interval", 80)
        auto_raise: bool = kwargs.get("auto_raise", True)
        wait_time: float = kwargs.get("wait_time", 1.0)
        max_time: float = kwargs.get("max_time", 2.0)
        max_attempts: int | None = kwargs.get("max_attempts")
        bool_debug: bool = kwargs.get("bool_debug", True)
        bool_save_screen: bool = kwargs.get("bool_save_screen", True)

        start_time = time.perf_counter()
        success = False
        if bool_save_screen:
            self.screen_save_signal.emit(self.task_name)
        if max_attempts is not None:
            for i in range(max_attempts):
                time_1 = time.perf_counter()
                flag, confidence = self.recognizer.scene_match(self.device.screen_cap(), scene, bool_debug)
                if flag:
                    if bool_save_screen:
                        self.screen_save_signal.emit(self.task_name)
                    QThread.msleep(int(wait_time * 1000))
                    success = True
                    break
                sleep_time = max(0, int(interval - (time.perf_counter() - time_1)))
                QThread.msleep(sleep_time)
        else:
            while time.perf_counter() - start_time < max_time:
                time_1 = time.perf_counter()
                flag, confidence = self.recognizer.scene_match(self.device.screen_cap(), scene, bool_debug)
                if flag:
                    if bool_save_screen:
                        self.screen_save_signal.emit(self.task_name)
                    QThread.msleep(int(wait_time * 1000))
                    success = True
                    break
                sleep_time = max(0, int(interval - (time.perf_counter() - time_1)))
                QThread.msleep(sleep_time)
        # 根据auto_raise参数决定是抛出异常还是返回结果
        if not success and auto_raise:
            raise StepFailedError(f"场景 [{scene.id}] 未出现")

        return success

    def click_and_wait(self, element, **kwargs):
        """
        点击并等待一段时间
        Args:
            element(str|Element): 元素
            ** kwargs: 可选参数：
            - interval: 检测的间隔，默认为80ms
            - auto_raise: 是否自动抛出异常，默认为True,对于试探性的点击一定要设置成False
            - wait_time: 检测到之后的等待时间，默认为None,表示将等待画面稳定，支持自定义
            - max_time: 最大尝试时间，默认为2.0
            - max_attempts: 最大尝试次数，如果定义则优先，不定义则按最大时间
            - click_times：点击次数，默认为1
        """
        if isinstance(element, str):
            element = self.current_scene.elements.get(element)
        interval: int = kwargs.get("interval", 80)
        auto_raise: bool = kwargs.get("auto_raise", True)
        wait_time: float | None = kwargs.get("wait_time", None)
        max_time: float = kwargs.get("max_time", 1.0)
        max_attempts: int | None = kwargs.get("max_attempts")
        click_times: int = kwargs.get("click_times", 1)

        # wait_until_stable的参数
        stable_threshold = kwargs.get("stable_threshold", 0.1)  # 默认1%的像素变化
        stable_duration = kwargs.get("stable_duration", 1.0)  # 默认需要稳定1秒
        stable_check_interval = kwargs.get("stable_check_interval", 200)  # 默认每200ms检查一次
        stable_max_time = kwargs.get("stable_max_time", 10.0)  # 默认最多等待10秒
        stable_bool_debug = kwargs.get("stable_bool_debug", True)  # 默认不输出调试信息

        start_time = time.perf_counter()
        success = False
        self.screen_save_signal.emit(self.task_name)
        if max_attempts:
            for i in range(max_attempts):
                time_1 = time.perf_counter()
                if element.type == ElementType.COORDINATE:
                    self.device.click(element.coordinate, times=click_times)
                    self.screen_save_signal.emit(self.task_name)
                    if wait_time:
                        QThread.msleep(int(wait_time * 1000))
                    else:
                        self.wait_until_stable(
                            threshold=stable_threshold,
                            stable_duration=stable_duration,
                            check_interval=stable_check_interval,
                            max_time=stable_max_time,
                            bool_debug=stable_bool_debug
                        )
                    success = True
                    break
                elif element.type == ElementType.IMG:
                    coordinates = self.recognizer.element_match(self.device.screen_cap(), element)
                    if coordinates:
                        QThread.msleep(500)
                        coordinate = coordinates[0]
                        x_ratio, y_ratio = element.ratio
                        # 按照元素可点击位置相对于模版左上角，相对整体的比例确定点击坐标
                        x, y = (coordinate[0] * (1 - x_ratio) + coordinate[2] * x_ratio), (
                                coordinate[1] * (1 - y_ratio) + coordinate[3] * y_ratio)
                        self.logger.debug(f"[{element.id}] Click ({x},{y})")
                        self.device.click((x, y), times=click_times)
                        self.screen_save_signal.emit(self.task_name)
                        if wait_time:
                            QThread.msleep(int(wait_time * 1000))
                        else:
                            self.wait_until_stable(
                                threshold=stable_threshold,
                                stable_duration=stable_duration,
                                check_interval=stable_check_interval,
                                max_time=stable_max_time,
                                bool_debug=stable_bool_debug
                            )
                        success = True
                        break
                    sleep_time = max(0, int(interval - (time.perf_counter() - time_1)))
                    QThread.msleep(sleep_time)
        else:
            while time.perf_counter() - start_time < max_time:
                time_1 = time.perf_counter()
                if element.type == ElementType.COORDINATE:
                    self.device.click(element.coordinate, times=click_times)
                    self.screen_save_signal.emit(self.task_name)
                    if wait_time:
                        QThread.msleep(int(wait_time * 1000))
                    else:
                        self.wait_until_stable(
                            threshold=stable_threshold,
                            stable_duration=stable_duration,
                            check_interval=stable_check_interval,
                            max_time=stable_max_time,
                            bool_debug=stable_bool_debug
                        )
                    success = True
                    break
                elif element.type == ElementType.IMG:
                    coordinates = self.recognizer.element_match(self.device.screen_cap(), element)
                    if coordinates:
                        QThread.msleep(500)
                        coordinate = coordinates[0]
                        x_ratio, y_ratio = element.ratio
                        # 按照元素可点击位置相对于模版左上角，相对整体的比例确定点击坐标
                        x, y = (coordinate[0] * (1 - x_ratio) + coordinate[2] * x_ratio), (
                                coordinate[1] * (1 - y_ratio) + coordinate[3] * y_ratio)
                        self.logger.debug(f"[{element.id}] Click ({x},{y})")
                        self.device.click((x, y), times=click_times)
                        self.screen_save_signal.emit(self.task_name)
                        if wait_time:
                            QThread.msleep(int(wait_time * 1000))
                        else:
                            self.wait_until_stable(
                                threshold=stable_threshold,
                                stable_duration=stable_duration,
                                check_interval=stable_check_interval,
                                max_time=stable_max_time,
                                bool_debug=stable_bool_debug
                            )
                        success = True
                        break
                    sleep_time = max(0, int(interval - (time.perf_counter() - time_1)))
                    QThread.msleep(sleep_time)

        # 根据auto_raise参数决定是抛出异常还是返回结果
        if not success and auto_raise:
            if element.type == ElementType.IMG:
                raise StepFailedError(f"点击元素 [{element.id}] 失败")
            elif element.type == ElementType.COORDINATE:
                raise StepFailedError(f"点击坐标 {element.coordinate} 失败")

        return success

    def swipe_and_wait(self, start_coordinate, end_coordinate, **kwargs):
        """
        滑动并等待一段时间

        Args:
            start_coordinate(Tuple[int,int]): 滑动起始点
            end_coordinate(Tuple[int,int]): 滑动终点
            **kwargs:
            - wait_time: 检测到之后的等待时间
            - duration: 滑动过程时间
            - times: 滑动的次数

        Returns:
            bool
        """
        wait_time: float | None = kwargs.get("wait_time", None)
        duration: float = kwargs.get("duration", 1.0)
        times: int = kwargs.get("times", 1)
        self.screen_save_signal.emit(self.task_name)
        for _ in range(times):
            self.device.swipe(
                start_coordinate,
                end_coordinate,
                duration
            )
            if wait_time:
                QThread.msleep(int(wait_time * 1000))
            else:
                self.wait_until_stable()
        self.screen_save_signal.emit(self.task_name)
        return True

    def auto_cycle_actioner(self, actions: list[Tuple], **kwargs, ):
        """
        自动连点器 - 按坐标列表循环点击，支持两种停止条件

        Args:
            actions: 操作格式为[(action, (x1,y1)) , ...]
            **kwargs:
            - stop_conditions (List|None): 停止条件列表，用于传入判定的对象，Element或Scene
            - max_time(float|None): 最大点击时间
            - max_workers(int): 最大工作线程数，默认1
            - bool_debug(bool): 要不要输出日志（避免有的过程检测次数过多导致日志累积）

        Returns:
            int 因为哪种条件而停止，返回1-based停止条件索引
        """
        stop_conditions: List | None = kwargs.get("stop_conditions")
        max_time: float | None = kwargs.get("max_time")
        max_workers: int = kwargs.get("max_workers", 1)
        bool_debug: bool = kwargs.get("bool_debug", False)

        # 添加一个变量用于存储停止原因
        stop_result = 0  # 默认为0表示未正常停止

        # 检查参数
        if not actions:
            self.logger.warning("操作列表为空，无法执行")
            return 0

        # 检查停止条件
        if stop_conditions is None and max_time is None:
            self.logger.warning("未设置停止条件，将执行无限循环点击")

        start = time.perf_counter()
        stop_event = threading.Event()  # 用于通知停止的事件
        checker_thread = None
        self.screen_save_signal.emit(self.task_name)

        # 判定线程函数
        def check_stop_condition():
            nonlocal stop_event, stop_result  # 使用nonlocal关键字共享变量
            while not stop_event.is_set():
                # 执行检查
                if self._should_stop():
                    stop_event.set()
                    raise Stop
                if max_time is not None and time.perf_counter() - start >= max_time:
                    self.logger.debug(f"达到最大时长 {max_time}，操作停止")
                    stop_event.set()
                    stop_result = -1  # 标记为超时停止
                    return
                if stop_conditions is not None:
                    for index, stop_condition in enumerate(stop_conditions):
                        if self._should_stop():
                            stop_event.set()
                            raise Stop
                        if isinstance(stop_condition, Element):
                            if self.detect_element(
                                    stop_condition,
                                    wait_time=0,
                                    max_attempts=1,
                                    interval=0,
                                    bool_debug=bool_debug,
                                    bool_save_screen=False,
                                    auto_raise=False
                            ):
                                stop_event.set()
                                stop_result = index + 1  # 存储1-based索引
                                self.screen_save_signal.emit(self.task_name)
                                self.logger.debug(f"条件[{stop_condition.id}]成立，点击停止")
                                return
                        elif isinstance(stop_condition, Scene):
                            if self.detect_scene(
                                    stop_condition,
                                    wait_time=0,
                                    max_attempts=1,
                                    interval=0,
                                    bool_debug=bool_debug,
                                    bool_save_screen=False,
                                    auto_raise=False
                            ):
                                stop_event.set()
                                stop_result = index + 1  # 存储1-based索引
                                self.screen_save_signal.emit(self.task_name)
                                self.logger.debug(f"条件[{stop_condition.id}]成立，点击停止")
                                return
                QThread.msleep(10)

        # 点击工作函数（保持不变）
        def click_worker(coord):
            nonlocal stop_event
            x, y = coord
            while not stop_event.is_set():
                self.device.click((x, y))
            return x, y

        def press_worker(coord):
            nonlocal stop_event
            x, y = coord
            instance = self.device.controller.touch_down(x, y)
            while not stop_event.is_set():
                QThread.msleep(50)
                continue
            instance.touch_up(x, y)
            return x, y

        # 如果设置了停止条件，启动判定线程
        if stop_conditions is not None or max_time is not None:
            checker_thread = threading.Thread(target=check_stop_condition, daemon=True)
            checker_thread.start()

        try:
            # 创建线程池
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for action in actions:
                    futures.append(executor.submit(click_worker, action[1]))
                    # # 根据action类型选择不同的worker
                    # if action[0] == "CLICK":
                    #     futures.append(executor.submit(click_worker, action[1]))
                    # elif action[0] == "PRESS":
                    #     futures.append(executor.submit(press_worker, action[1]))
        except Exception as e:
            self.logger.error(f"操作过程中发生错误: {e}")

        # 等待判定线程结束（如果有）
        if stop_conditions is not None or max_time is not None:
            checker_thread.join(timeout=1.0)
        self.logger.debug(f"返回：{stop_result}")
        # 返回存储的停止原因
        return stop_result

    def search_and_click(self, element_list, search_actions, **kwargs, ):
        """
        循环执行元素点击搜索，支持多轮次、多位置尝试，并在过程中执行辅助操作（如点击或滑动）

        Args:
            element_list: (List[str]): 待点击的元素参数列表，每个元素是一个element_id
            search_actions: (List[Dict]): 搜索过程中执行的辅助动作列表，支持两种操作：
                    - {'click': 点击参数}：执行点击操作
                    - {'swipe': 滑动参数}：执行滑动操作
            **kwargs:
            - search_max_time:  (float): 搜索尝试的最大时间，默认None，即不限时间
            - max_attempts: (int):尝试搜索的最大次数，默认None，即不限次数
            - once_max_time: (float):单次搜索点击的最大时间
            - wait_time: (float): 点击后等待的时间

        Returns:
            int: 是否成功找到并点击了element_list中的1-based元素
        """
        search_max_time: float | None = kwargs.get("search_max_time")
        max_attempts: int | None = kwargs.get("max_attempts")
        once_max_time: float = kwargs.get("once_max_time", 1)
        wait_time: float | None = kwargs.get("wait_time", None)

        # wait_until_stable的参数
        stable_threshold = kwargs.get("stable_threshold", 0.1)  # 默认1%的像素变化
        stable_duration = kwargs.get("stable_duration", 1.0)  # 默认需要稳定1秒
        stable_check_interval = kwargs.get("stable_check_interval", 200)  # 默认每200ms检查一次
        stable_max_time = kwargs.get("stable_max_time", 10.0)  # 默认最多等待10秒
        stable_bool_debug = kwargs.get("stable_bool_debug", True)  # 默认不输出调试信息

        self.logger.debug(f"元素点击搜索内容：")
        self.logger.debug(element_list)
        for element_id in element_list:
            if isinstance(element_id, Element):
                self.logger.debug(f"[元素] {element_id.id}")
            else:
                self.logger.debug(f"[元素] {element_id}")
        start = time.perf_counter()
        attempts = 0
        while True:
            self.screen_save_signal.emit(self.task_name)
            if self._should_stop():
                raise Stop
            if search_max_time:
                if time.perf_counter() - start > search_max_time:
                    self.logger.warning(f"搜索超时：{time.perf_counter() - start:.1f}s")
                    return 0
            elif max_attempts:
                if attempts >= max_attempts:
                    self.logger.warning(f"搜索次数已达{max_attempts}次")
                    return 0
            for index, element_id in enumerate(element_list):
                if self._should_stop():
                    raise Stop
                if self.click_and_wait(
                        element_id,
                        wait_time=wait_time,
                        max_time=once_max_time,
                        auto_raise=False,
                        stable_threshold=stable_threshold,
                        stable_duration=stable_duration,
                        stable_check_interval=stable_check_interval,
                        stable_max_time=stable_max_time,
                        stable_bool_debug=stable_bool_debug
                ):
                    self.screen_save_signal.emit(self.task_name)
                    return index + 1
            for action in search_actions:
                if self._should_stop():
                    raise Stop
                if "click" in action:
                    self.click_and_wait(
                        action['click'],
                        max_time=1,
                        auto_raise=False
                    )
                elif "swipe" in action:
                    self.device.swipe(
                        action['swipe']['start_coordinate'],
                        action['swipe']['end_coordinate'],
                        action['swipe']['duration'])
            attempts += 1

    def search_and_detect(self, item_list, search_actions, **kwargs):
        """
        循环执行元素检测，支持多轮次、多位置尝试，并在过程中执行辅助操作（如点击或滑动）

        Args:
            item_list: (List): 搜索的对象列表，每个对象是Element或者Scene
            search_actions: (List[Dict]): 搜索过程中执行的辅助动作列表，支持两种操作：
                    - {'click': 点击参数}：执行点击操作
                    - {'swipe': 滑动参数}：执行滑动操作
            **kwargs:
            - search_max_time: (float): 搜索尝试的最大时间，默认None，即不限时间
            - max_attempts: (int):尝试搜索的最大次数，默认None，即不限次数
            - once_max_time: (float):单次搜索的最大时长，默认1.0，定义与detect_and_wait()一致
            - wait_time: (int): 如果寻找到了，要等待几秒，默认1.0
            - bool_debug: (bool): 是否输出调试日志，默认False

        Returns:
            int: 未找到返回0，找到返回1-based索引，表示找到了params_list中哪个元素
        """
        search_max_time: float | None = kwargs.get("search_max_time")
        max_attempts: int | None = kwargs.get("max_attempts")
        once_max_time: float = kwargs.get("once_max_time", 1.0)
        wait_time: float = kwargs.get("wait_time", 1.0)
        bool_debug: bool = kwargs.get("bool_debug", True)
        self.logger.debug(f"元素检测搜索内容：")
        for item in item_list:
            if isinstance(item, Scene):
                self.logger.debug(f"[场景] {item.id}")
            elif isinstance(item, Element):
                if item.type == ElementType.IMG:
                    self.logger.debug(f"[图像] {item.id}")
                elif item.type == ElementType.COORDINATE:
                    self.logger.debug(f"[坐标] {item.coordinate}")
        start = time.perf_counter()
        attempts = 0
        self.screen_save_signal.emit(self.task_name)
        while True:
            if self._should_stop():
                raise Stop
            for index, item in enumerate(item_list):
                if self._should_stop():
                    raise Stop
                if isinstance(item, Scene):
                    if self.detect_scene(
                            item,
                            wait_time=wait_time,
                            max_time=once_max_time,
                            bool_save_screen=False,
                            bool_debug=bool_debug,
                            auto_raise=False
                    ):
                        self.screen_save_signal.emit(self.task_name)
                        return index + 1
                elif isinstance(item, Element):
                    if self.detect_element(
                            item,
                            wait_time=wait_time,
                            max_time=once_max_time,
                            bool_save_screen=False,
                            bool_debug=bool_debug,
                            auto_raise=False
                    ):
                        self.screen_save_signal.emit(self.task_name)
                        return index + 1
            if search_max_time:
                if time.perf_counter() - start > search_max_time:
                    self.logger.warning(f"搜索超时：{time.perf_counter() - start:.1f}s")
                    self.screen_save_signal.emit(self.task_name)
                    return 0
            elif max_attempts:
                if attempts >= max_attempts:
                    self.logger.warning(f"搜索次数已达{max_attempts}次")
                    self.screen_save_signal.emit(self.task_name)
                    return 0
            for action in search_actions:
                if self._should_stop():
                    raise Stop
                if "click" in action:
                    self.click_and_wait(
                        action['click'],
                        max_time=1,
                        wait_time=2,
                        auto_raise=False
                    )
                elif "swipe" in action:
                    self.device.swipe(
                        action['swipe']['start_coordinate'],
                        action['swipe']['end_coordinate'],
                        action['swipe']['duration'])
            attempts += 1

    def click_and_input(self, input_edit: Element, input_text):
        """
        第一个参数为需要点击的输入框的对象，第二个为要输入的文字
        """
        self.screen_save_signal.emit(self.task_name)
        if self.click_and_wait(
                input_edit,
                auto_raise=False
        ):
            self.screen_save_signal.emit(self.task_name)
            self.device.input(input_text)
            self.screen_save_signal.emit(self.task_name)
            self.click_and_wait(
                input_edit,
                auto_raise=False
            )
            self.screen_save_signal.emit(self.task_name)
            return True
        return False

    def pass_secondary_password(self):
        """
        过二级密码的通用函数,返回True表示检测到了二级密码的弹窗,反之没有
        """
        self.screen_save_signal.emit(self.task_name)
        scene = self.scene_graph.scenes.get("二级密码")
        # 可能有二级密码，用户输入密码
        if self.detect_scene(
                "二级密码",
                auto_raise=False
        ):
            self.logger.debug("出现二级密码窗口")
            passward = self.config.get_config("二级密码")
            if len(passward) != 6:
                raise StepFailedError("请检查二级密码！")
            self.screen_save_signal.emit(self.task_name)
            # 输入操作
            self.click_and_input(
                scene.elements.get("输入框"),
                passward
            )
            self.screen_save_signal.emit(self.task_name)
            # 点击二级密码-确定
            if not self.click_and_wait(
                    scene.elements.get("确定"),
                    auto_raise=False
            ):
                raise StepFailedError("二级密码验证失败")
            self.screen_save_signal.emit(self.task_name)
            self.logger.debug("验证二级密码结束")
            return True
        self.logger.debug("未出现二级密码窗口")
        return False

    def press_key(self, key, wait_time=0):
        """
        模拟设备按键，输入key即为按键名称
        """
        self.device.press_key(key)
        if wait_time:
            QThread.msleep(int(wait_time * 1000))

    def long_press(self, x, y, duration=1):
        """
        长按

        Args:
            x(int): 长按位置的x坐标
            y(int): 长按位置的y坐标
            duration(float): 长按持续时间

        Returns:

        """
        self.screen_save_signal.emit(self.task_name)
        self.logger.debug(f"LongPress ({x},{y}) {duration}s")
        self.device.long_press(x, y, duration)
        self.screen_save_signal.emit(self.task_name)

    def restart(self):
        """
        重启火影忍者
        """
        self.logger.info("重启火影忍者")
        self.device.restart()

    def back_to_naruto(self):
        front_app = self.device.current_app()
        while front_app["package"] != self.device.package_name:
            self.press_key("back", wait_time=3)
            front_app = self.device.current_app()

    def screen_cap(self):
        return self.device.screen_cap()

    def wait_until_stable(self, **kwargs):
        """
        等待画面稳定（连续多帧变化小于阈值）

        Args:
            **kwargs: 可选参数：
                - threshold: 差异阈值（默认0.01，即1%的像素变化）
                - stable_duration: 需要稳定的持续时间（秒，默认1.0）
                - check_interval: 检查间隔（毫秒，默认200）
                - max_time: 最大等待时间（秒，默认10.0）
                - bool_debug: 是否输出调试信息（默认True）

        Returns:
            bool: 是否在最大时间内达到稳定
        """
        import cv2
        import numpy as np

        # 获取参数
        threshold = kwargs.get("threshold", 0.1)  # 默认1%的像素变化
        stable_duration = kwargs.get("stable_duration", 1.0)  # 默认需要稳定1秒
        check_interval = kwargs.get("check_interval", 100)  # 默认每200ms检查一次
        max_time = kwargs.get("max_time", 10.0)  # 默认最多等待10秒
        bool_debug = kwargs.get("bool_debug", True)  # 默认不输出调试信息

        start_time = time.perf_counter()
        stable_start_time = None
        last_frame = None

        # 将稳定持续时间转换为需要连续稳定的帧数
        stable_frames_needed = max(1, int(stable_duration * 1000 / check_interval))
        stable_frame_count = 0

        if bool_debug:
            self.logger.debug(f"等待画面稳定，阈值: {threshold}, 需要稳定帧数: {stable_frames_needed}")

        while time.perf_counter() - start_time < max_time:
            if self._should_stop():
                raise Stop("操作被用户中断")

            # 获取当前帧
            start_check_time = time.perf_counter()
            current_frame = self.device.screen_cap()

            # 转换为灰度图并调整大小以减少计算量
            current_gray = cv2.cvtColor(np.array(current_frame), cv2.COLOR_RGB2GRAY)
            current_gray = cv2.resize(current_gray, (300, 300))  # 调整到较小尺寸

            if last_frame is not None:
                # 计算帧间差异
                diff = cv2.absdiff(last_frame, current_gray)
                _, diff_thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

                # 计算变化比例
                change_ratio = np.count_nonzero(diff_thresh) / diff_thresh.size

                if bool_debug:
                    self.logger.debug(f"帧间变化比例: {change_ratio:.4f}")

                # 检查是否低于阈值
                if change_ratio < threshold:
                    stable_frame_count += 1
                    if stable_frame_count >= stable_frames_needed:
                        if bool_debug:
                            self.logger.debug("画面已稳定")
                        return True
                else:
                    stable_frame_count = 0  # 重置稳定计数

            last_frame = current_gray
            sleep_time = min(0, int(time.perf_counter() - start_check_time)) * 1000
            QThread.msleep(sleep_time)

        if bool_debug:
            self.logger.debug("等待画面稳定超时")
        return False
