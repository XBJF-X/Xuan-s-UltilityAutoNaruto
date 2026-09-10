import threading
import time
from typing import Tuple, Any, List

from backend.tools.resource_model import Scene, Element
from backend.core.legacy.Clicker import Clicker
from backend.core.legacy.Config import Config
from backend.core.legacy.Device import Device
from backend.core.legacy.Enums import ElementType
from backend.core.legacy.Exceptions import StepFailedError, Stop
from backend.core.legacy.OcrText import OcrResultList, OcrText
from backend.core.legacy.Recognizer import Recognizer
from backend.core.legacy.Scene.SceneGraph import SceneGraph


class Operationer:
    current_scene: Scene | None = None
    next_scene: str | None = None
    # 分享跳转常见的第三方应用包名（QQ / 微信），用于分享流程结束后清理后台
    SHARE_APP_PACKAGES = ("com.tencent.mobileqq", "com.tencent.mm")
    # 任务参数名：分享结束后是否关闭 QQ/微信后台（BOOL，参数缺失时视为开启）
    SHARE_APP_STOP_PARAM = "分享后关闭QQ微信后台"

    def __init__(self, task_name: str, config: Config, device: Device,
                 scene_graph: SceneGraph, screen_save_func: Any,
                 parent_logger):
        self.stop_event = threading.Event()
        self.task_name = task_name
        self.config = config
        self.device = device
        self.scene_graph = scene_graph
        self.screen_save_func = screen_save_func
        self.logger = parent_logger.getChild(self.__class__.__name__)
        self.recognizer = Recognizer(scene_graph, self.logger)
        self.clicker = Clicker(self, parent_logger=self.logger)

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

    def get_element(self, element_name, scene_name: str | None = None):
        if scene_name:
            return self.scene_graph.get_element(scene_name, element_name)
        if self.current_scene is None:
            raise StepFailedError(f"当前场景未设置，无法获取元素 [{element_name}]")
        return self.scene_graph.get_element(self.current_scene.name,
                                            element_name)

    def get_scene(self, scene_name):
        return self.scene_graph.get_scene(scene_name)

    def detect_element(self, element, match_text='', **kwargs):
        """
        检测并等待一段时间

        Args:
            element(str|Element): 元素（元素名或 Element 对象）
            match_text(str): OCR 匹配文本，为空时默认用 element.name
            **kwargs: 可选参数：
            - wait_time: 检测到之后的等待时间
            - max_time: 最大尝试时间，默认为2.0
            - max_attempts: 最大尝试次数，如果定义则优先，不定义则按最大时间
            - stable_duration：画面需要保持稳定多长时间
            - stable_max_time：最多等待画面稳定多长时间
            - stable_wait_for_new_scene：是否希望画面稳定至新场景出现
        """
        element = self._resolve_element(element)
        match_text = match_text or element.name

        wait_time: float = kwargs.get("wait_time", 1.0)
        max_time: float = kwargs.get("max_time", 1.0)
        max_attempts: int | None = kwargs.get("max_attempts")
        stable_kwargs = self._extract_stable_kwargs(kwargs)

        self.screen_save_func(self.task_name)
        return self._retry_until(
            lambda: self._match_element_once(element, match_text),
            wait_time=wait_time,
            max_time=max_time,
            max_attempts=max_attempts,
            stable_kwargs=stable_kwargs)

    def detect_scene(self, scene, **kwargs):
        """
            检测并等待一段时间
            Args:
                scene(str|Scene): 元素名
                ** kwargs: 可选参数：
                - wait_time: 检测到之后的等待时间
                - max_time: 最大尝试时间，默认为2.0
                - max_attempts: 最大尝试次数，如果定义则优先，不定义则按最大时间
                - stable_duration：画面需要保持稳定多长时间
                - stable_max_time：最多等待画面稳定多长时间
                - stable_wait_for_new_scene：是否希望画面稳定至新场景出现
            """
        if isinstance(scene, str):
            scene = self.scene_graph.get_scene(scene)

        wait_time: float = kwargs.get("wait_time", 1.0)
        max_time: float = kwargs.get("max_time", 1.0)
        max_attempts: int | None = kwargs.get("max_attempts")
        stable_kwargs = self._extract_stable_kwargs(kwargs)

        self.screen_save_func(self.task_name)

        def _match_scene_once():
            return self.recognizer.scene_match(self.device.screen_cap(),
                                               scene, False)

        return self._retry_until(
            _match_scene_once,
            wait_time=wait_time,
            max_time=max_time,
            max_attempts=max_attempts,
            stable_kwargs=stable_kwargs)

    def ocr_recognize(self, element, **kwargs) -> OcrResultList:
        """
        对指定 OcrArea 区域执行 OCR 识别，返回所有识别结果（按置信度降序排序）

        Args:
            element(str|Element): OcrArea 元素（可传元素名或 Element 对象）
            **kwargs: 可选参数：
                - bool_debug(bool): 是否回报日志，默认为 False

        Returns:
            List[OcrText]: 识别结果列表，按置信度从高到低排序；若无结果则返回空列表
        """
        results = self._ocr_results(element, **kwargs)
        if not results:
            return []
        # 按置信度降序排列
        return OcrResultList(sorted(results, key=lambda r: r.score, reverse=True))

    def _ocr_results(self, element, **kwargs) -> List[OcrText]:
        """
        对指定 OcrArea 区域执行 OCR 识别，返回全部结果

        Args:
            element(str|Element): OcrArea 元素（可传元素名或 Element 对象）
            **kwargs: 可选参数：
                - bool_debug(bool): 是否回报日志，默认为 False

        Returns:
            List[OcrText]: 识别结果列表，异常或非 OCR_AREA 类型返回 []
        """
        if isinstance(element, str):
            element_name = element
            element = self.get_element(element)
            if element is None:
                self.logger.warning(f"元素 [{element_name}] 不存在，无法执行 OCR 识别")
                return []

        if element.type != ElementType.OCR_AREA:
            self.logger.warning(
                f"[{element.name}] 不是 OCR_AREA 类型，无法执行 OCR 识别")
            return []

        bool_debug: bool = kwargs.get("bool_debug", False)
        try:
            results = self.recognizer.area_ocr(
                self.device.screen_cap(), element, bool_debug)
        except Exception as e:
            self.logger.error(f"[{element.name}] OCR 识别异常：{e}")
            return []

        ocr_texts = []
        self.logger.debug(f"{element.name}的识别结果：")
        for text, box, score in results:
            self.logger.debug(f'文本：{text}， 置信度：{score}，位置：{box}')
            ocr_texts.append(OcrText(text, box, score))
        return ocr_texts

    def click_and_wait(self, element, match_text='', **kwargs):
        """
        点击并等待一段时间

        Args:
            element(str|Element): 元素
            match_text(str): OCR 匹配文本，为空时默认用 element.name
            ** kwargs: 可选参数：
            - wait_time: 检测到之后的等待时间，默认为None,表示将等待画面稳定，支持自定义
            - max_time: 最大尝试时间，默认为2.0
            - max_attempts: 最大尝试次数，如果定义则优先，不定义则按最大时间
            - click_times：点击次数，默认为1
            - ratio_x/ratio_y: OCR_AREA 点击文本框内比例，默认取 element.ratio_x/ratio_y

            - stable_duration：画面需要保持稳定多长时间
            - stable_max_time：最多等待画面稳定多长时间
            - stable_wait_for_new_scene：是否希望画面稳定至新场景出现
        """
        element = self._resolve_element(element)
        match_text = match_text or element.name
        self.logger.info(f"[Click] [{element.name}]")

        wait_time: float | None = kwargs.get("wait_time", None)
        max_time: float = kwargs.get("max_time", 0.7)
        max_attempts: int | None = kwargs.get("max_attempts")
        click_times: int = kwargs.get("click_times", 1)
        ratio_x: float = kwargs.get("ratio_x", element.ratio_x)
        ratio_y: float = kwargs.get("ratio_y", element.ratio_y)
        stable_kwargs = self._extract_stable_kwargs(kwargs)

        self.screen_save_func(self.task_name)
        return self._retry_until(
            lambda: self._click_element_once(
                element, click_times, match_text, ratio_x, ratio_y),
            wait_time=wait_time,
            max_time=max_time,
            max_attempts=max_attempts,
            stable_kwargs=stable_kwargs)

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
            - stable_duration：画面需要保持稳定多长时间
            - stable_max_time：最多等待画面稳定多长时间
            - stable_wait_for_new_scene：是否希望画面稳定至新场景出现

        Returns:
            bool
        """
        wait_time: float | None = kwargs.get("wait_time", None)
        duration: float = kwargs.get("duration", 1.0)
        times: int = kwargs.get("times", 1)
        stable_kwargs = {
            k: v
            for k, v in kwargs.items() if k.startswith('stable_')
        }
        self.screen_save_func(self.task_name)
        for _ in range(times):
            if self._should_stop():
                raise Stop

            self.device.swipe(start_coordinate, end_coordinate, duration)
            if wait_time is not None:
                time.sleep(wait_time)
            else:
                self.wait_until_stable(**stable_kwargs)
        self.screen_save_func(self.task_name)
        return True

    def search_and_click(self, element_list, search_actions, match_text='',
                         **kwargs):
        """
        循环执行元素点击搜索，支持多轮次、多位置尝试，并在过程中执行辅助操作（如点击或滑动）

        Args:
            element_list: (List[str]): 待点击的元素参数列表，每个元素是一个element_id
            search_actions: (List[Dict]): 搜索过程中执行的辅助动作列表，支持两种操作：
                    - {'click': 点击参数}：执行点击操作
                    - {'swipe': 滑动参数}：执行滑动操作
            match_text(str): OCR 匹配文本，为空时默认用 element.name
            **kwargs:
            - search_max_time: (float): 搜索尝试的最大时间，默认None，即不限时间
            - max_attempts: (int):尝试搜索的最大次数，默认None，即不限次数
            - once_max_time: (float):单次搜索点击的最大时间
            - wait_time: (float): 点击后等待的时间

            - stable_duration：画面需要保持稳定多长时间
            - stable_max_time：最多等待画面稳定多长时间
            - stable_wait_for_new_scene：是否希望画面稳定至新场景出现

        Returns:
            int: 是否成功找到并点击了element_list中的1-based元素
        """
        self.logger.info(f"元素点击搜索内容：")
        for element_id in element_list:
            if isinstance(element_id, Element):
                self.logger.info(f"[元素] {element_id.name}")
            else:
                self.logger.info(f"[元素] {element_id}")

        def _check_once(item, **opt):
            return self.click_and_wait(item, match_text=match_text, **opt)

        # 辅助 click 未指定 wait_time 时等待画面稳定（与原逻辑一致）
        return self._search_loop(element_list, search_actions, _check_once,
                                 **kwargs)

    def search_and_detect(self, item_list, search_actions, match_text='',
                          **kwargs):
        """
        循环执行元素检测，支持多轮次、多位置尝试，并在过程中执行辅助操作（如点击或滑动）

        Args:
            item_list: (List): 搜索的对象列表，每个对象是Element/Str或者Scene
            search_actions: (List[Dict]): 搜索过程中执行的辅助动作列表，支持两种操作：
                    - {'click': 点击参数}：执行点击操作
                    - {'swipe': 滑动参数}：执行滑动操作
            match_text(str): OCR 匹配文本，为空时默认用 element.name
            **kwargs:
            - search_max_time: (float): 搜索尝试的最大时间，默认None，即不限时间
            - max_attempts: (int):尝试搜索的最大次数，默认None，即不限次数
            - once_max_time: (float):单次搜索的最大时长，默认1.0，定义与detect_and_wait()一致
            - wait_time: (int): 如果寻找到了，要等待几秒，默认1.0

            - stable_duration：画面需要保持稳定多长时间
            - stable_max_time：最多等待画面稳定多长时间
            - stable_wait_for_new_scene：是否希望画面稳定至新场景出现

        Returns:
            int: 未找到返回0，找到返回1-based索引，表示找到了params_list中哪个元素
        """
        # bool_debug: bool = kwargs.get("bool_debug", True)
        self.logger.info(f"元素检测搜索内容：")
        for item in item_list:
            if isinstance(item, Scene):
                self.logger.info(f"[场景] {item.name}")
            elif isinstance(item, Element):
                if item.type == ElementType.IMG:
                    self.logger.info(f"[图像] {item.name}")
                elif item.type == ElementType.COORDINATE:
                    self.logger.info(
                        f"[坐标] ({item.coordinate_x},{item.coordinate_y})")
            elif isinstance(item, str):
                self.logger.debug(f"[元素] {item}")

        def _check_once(item, **opt):
            if isinstance(item, Scene):
                return self.detect_scene(item, **opt)
            return self.detect_element(item, match_text=match_text, **opt)

        search_kwargs = dict(kwargs)
        search_kwargs.setdefault("wait_time", 1.0)
        return self._search_loop(item_list, search_actions, _check_once,
                                 action_click_wait_time=2, **search_kwargs)

    def click_and_input(self, input_edit: Element, input_text):
        """
        第一个参数为需要点击的输入框的对象，第二个为要输入的文字
        """
        self.screen_save_func(self.task_name)
        if self.click_and_wait(input_edit):
            self.screen_save_func(self.task_name)
            self.device.input(input_text)
            self.screen_save_func(self.task_name)
            self.click_and_wait(input_edit)
            self.screen_save_func(self.task_name)
            return True
        return False

    def press_key(self, key, wait_time=0):
        """
        模拟设备按键，输入key即为按键名称
        """
        self.logger.info(f"[Press] {key}")
        self.device.press_key(key)
        if wait_time:
            time.sleep(wait_time)

    def long_press(self, x, y, duration=1.0):
        """
        长按

        Args:
            x(int): 长按位置的x坐标
            y(int): 长按位置的y坐标
            duration(float): 长按持续时间

        Returns:

        """
        self.screen_save_func(self.task_name)
        self.logger.info(f"[LongPress] ({x},{y}) {duration}s")
        self.device.long_press(x, y, duration)
        self.screen_save_func(self.task_name)

    def app_restart(self):
        """
        重启火影忍者
        """
        self.logger.info("重启火影忍者")
        self.device.app_restart()

    def app_start(self):
        # 启动应用
        self.logger.info(f"[App Start]")
        self.device.app_start()

    def app_stop(self, package_name: str | None = None):
        self.logger.info(f"[App Stop] {package_name or self.device.package_name}")
        # 停止应用（默认停止游戏本体；传入包名时停止指定应用）
        self.device.app_stop(package_name)

    @property
    def is_naruto_frontend(self):
        front_app = self.device.current_app()
        if front_app:
            return front_app["package"] == self.device.package_name
        else:
            return False

    @property
    def current_app_package(self) -> str:
        """当前前台应用包名；取不到时返回空字符串"""
        return self.device.current_app_package

    def close_share_app_background(self, share_app_package: str) -> bool:
        """分享流程结束后关闭本次跳转使用的 QQ/微信后台。

        Args:
            share_app_package(str): 分享跳转期间记录到的前台应用包名

        Returns:
            bool: 是否实际执行了关闭操作

        说明：
        - 受任务参数 `分享后关闭QQ微信后台` 控制（BOOL，参数缺失时视为开启）；
        - 仅当包名属于 SHARE_APP_PACKAGES（QQ/微信）时才执行，未识别到目标应用时
          只告警跳过，避免对未安装应用盲发 `am force-stop` 刷错误日志。
        """
        if not self.config.get_task_exe_param(self.task_name,
                                              self.SHARE_APP_STOP_PARAM, True):
            self.logger.debug(
                f"任务参数[{self.SHARE_APP_STOP_PARAM}]已关闭，跳过关闭分享应用后台")
            return False
        if share_app_package not in self.SHARE_APP_PACKAGES:
            self.logger.warning(
                f"未识别到本次分享跳转的应用（前台包名: {share_app_package or '未知'}），跳过关闭后台")
            return False
        self.logger.info(f"分享结束，关闭分享应用后台: {share_app_package}")
        self.app_stop(share_app_package)
        return True

    @property
    def rotated(self):
        return self.device.rotated

    def screen_cap(self):
        return self.device.screen_cap()

    def wait_until_stable(self, **kwargs):
        """
        等待画面稳定（连续多帧变化小于阈值）

        Args:
            **kwargs: 可选参数：
                - stable_duration: 需要稳定的持续时间（秒，默认1.0）
                - stable_max_time: 最大等待时间（秒，默认10.0）
                - stable_wait_for_new_scene: 是否需要等待稳定后出现新场景（默认False）

        Returns:
            bool: 是否在最大时间内达到稳定
        """
        import cv2
        import numpy as np
        import time

        threshold = 0.2  # 默认20%的像素变化
        check_interval = 0.1  # 默认每0.1s检查一次
        invalid_threshold = 0.8  # 无效帧判断阈值
        # 获取参数
        stable_duration = kwargs.get("stable_duration", 1)  # 默认需要稳定1秒
        stable_max_time = kwargs.get("stable_max_time", 10.0)  # 默认最多等待10秒
        stable_wait_for_new_scene = kwargs.get("stable_wait_for_new_scene",
                                               False)  # 默认不需要等待稳定后出现新场景

        def is_invalid_frame(frame):
            """判断帧是否为无效帧（全黑、大部分黑、全白、大部分白）"""
            # 计算黑色像素比例（低于10的像素视为黑色）
            black_pixels = np.sum(frame < 10)
            black_ratio = black_pixels / frame.size

            # 计算白色像素比例（高于245的像素视为白色）
            white_pixels = np.sum(frame > 245)
            white_ratio = white_pixels / frame.size

            # 如果黑色或白色像素占比超过阈值，则视为无效帧
            if black_ratio > invalid_threshold or white_ratio > invalid_threshold:
                # self.logger.debug(f"检测到无效帧 - 黑色占比: {black_ratio:.4f}, 白色占比: {white_ratio:.4f}")
                return True
            return False

        start_time = time.perf_counter()
        stable_frame_count = 0
        last_valid_frame = None

        # 将稳定持续时间转换为需要连续稳定的帧数
        stable_frames_needed = max(1, int(stable_duration / check_interval))

        # self.logger.debug(f"等待画面稳定，阈值: {threshold}, 需要稳定帧数: {stable_frames_needed}")

        while time.perf_counter() - start_time < stable_max_time:
            if self._should_stop():
                raise Stop("操作被用户中断")

            # 获取当前帧
            start_check_time = time.perf_counter()
            current_frame = self.device.screen_cap()

            # 转换为灰度图并调整大小以减少计算量
            current_gray = cv2.cvtColor(np.array(current_frame),
                                        cv2.COLOR_RGB2GRAY)
            # current_gray = cv2.resize(current_gray, (300, 300))  # 调整到较小尺寸

            # 检查是否为无效帧
            if is_invalid_frame(current_gray):
                # 无效帧不参与稳定性判断，但仍需等待检查间隔
                pass
            else:
                if last_valid_frame is not None:
                    # 计算帧间差异
                    diff = cv2.absdiff(last_valid_frame, current_gray)
                    _, diff_thresh = cv2.threshold(diff, 10, 255,
                                                   cv2.THRESH_BINARY)

                    # 计算变化比例
                    change_ratio = np.count_nonzero(
                        diff_thresh) / diff_thresh.size

                    # self.logger.debug(f"帧间变化比例: {change_ratio:.4f}")

                    # 检查是否低于阈值
                    if change_ratio < threshold:
                        stable_frame_count += 1
                        if stable_frame_count >= stable_frames_needed:
                            if stable_wait_for_new_scene and self.detect_scene(
                                    self.current_scene):
                                stable_frame_count = 0  # 重置稳定计数
                                continue
                            self.logger.debug("画面已稳定")
                            return True
                    else:
                        stable_frame_count = 0  # 重置稳定计数

                # 更新上一帧为当前有效帧
                last_valid_frame = current_gray

            # 计算需要休眠的时间（确保检查间隔的准确性）
            elapsed = time.perf_counter() - start_check_time
            sleep_time = max(0.0, check_interval - elapsed)
            time.sleep(sleep_time)

        self.logger.warning("等待画面稳定超时")
        return False

    def _resolve_element(self, element) -> Element:
        """将元素名解析为 Element 对象；解析失败抛出 StepFailedError"""
        if isinstance(element, str):
            element_name = element
            element = self.get_element(element)
            if element is None:
                raise StepFailedError(f"元素 [{element_name}] 未定义")
        return element

    def _extract_stable_kwargs(self, kwargs) -> dict:
        """抽取 stable_ 前缀关键字，用于等待画面稳定"""
        return {k: v for k, v in kwargs.items() if k.startswith('stable_')}

    def _after_action(self, wait_time, stable_kwargs):
        """动作成功后的收尾：保存截图并按 wait_time 等待或等待画面稳定"""
        self.screen_save_func(self.task_name)
        if wait_time is not None:
            time.sleep(wait_time)
        else:
            self.wait_until_stable(**stable_kwargs)

    def _retry_until(self, attempt_once, wait_time, max_time, max_attempts,
                     stable_kwargs) -> bool:
        """
        统一重试循环：成功即返回，max_attempts 优先于 max_time。
        保持原 detect/click 语义：max_attempts 用 `is not None` 判断。
        """
        interval: float = 0.08
        start_time = time.perf_counter()

        if max_attempts is not None:
            for _ in range(max_attempts):
                if self._should_stop():
                    raise Stop
                time_1 = time.perf_counter()
                if attempt_once():
                    self._after_action(wait_time, stable_kwargs)
                    return True
                sleep_time = max(0.0,
                                 interval - (time.perf_counter() - time_1))
                time.sleep(sleep_time)
        else:
            while time.perf_counter() - start_time < max_time:
                if self._should_stop():
                    raise Stop
                time_1 = time.perf_counter()
                if attempt_once():
                    self._after_action(wait_time, stable_kwargs)
                    return True
                sleep_time = max(0.0,
                                 interval - (time.perf_counter() - time_1))
                time.sleep(sleep_time)
        return False

    def _click_element_once(self, element, click_times, match_text,
                            ratio_x, ratio_y) -> bool:
        """单次点击尝试：按 ElementType 分派 COORDINATE/IMG/OCR_AREA"""
        if element.type == ElementType.COORDINATE:
            return self.device.click(element.coordinate_x,
                                     element.coordinate_y,
                                     times=click_times)

        if element.type == ElementType.OCR_AREA:
            results = self._ocr_results(element)
            for r in results:
                if match_text in r.text:
                    x, y = r.get_inner_point(ratio_x, ratio_y)
                    return self.device.click(x, y, times=click_times)
            return False

        coordinates = self.recognizer.element_match(
            self.device.screen_cap(), element)
        if coordinates:
            coordinate = coordinates[0]
            x_ratio, y_ratio = element.ratio_x, element.ratio_y
            # 按照元素可点击位置相对于模版左上角，相对整体的比例确定点击坐标
            x, y = (coordinate[0] * (1 - x_ratio) +
                    coordinate[2] * x_ratio), (
                        coordinate[1] * (1 - y_ratio) +
                        coordinate[3] * y_ratio)
            return self.device.click(x, y, times=click_times)
        return False

    def _match_element_once(self, element, match_text) -> bool:
        """单次元素匹配：OCR_AREA 走 OCR 文本包含匹配，其余走模板匹配"""
        if element.type == ElementType.OCR_AREA:
            results = self._ocr_results(element)
            self.logger.debug(f"[{element.name}] OCR结果：{results}")
            if not results:
                return False
            return any(match_text in r.text for r in results)
        coordinates = self.recognizer.element_match(
            self.device.screen_cap(), element, False)
        return len(coordinates) != 0

    def _search_loop(self, item_list, search_actions, check_once,
                     action_click_wait_time=None, **kw) -> int:
        """统一的搜索重试循环骨架，返回 1-based 索引或 0"""
        search_max_time: float | None = kw.get("search_max_time")
        max_attempts: int | None = kw.get("max_attempts")
        once_max_time: float = kw.get("once_max_time", 1)
        once_max_attempts: int | None = kw.get("once_max_attempts")
        wait_time: float | None = kw.get("wait_time", None)
        stable_kwargs = self._extract_stable_kwargs(kw)

        start = time.perf_counter()
        attempts = 0
        while True:
            self.screen_save_func(self.task_name)
            if self._should_stop():
                raise Stop
            if search_max_time:
                if time.perf_counter() - start > search_max_time:
                    self.logger.warning(
                        f"搜索超时：{time.perf_counter() - start:.1f}s")
                    return 0
            elif max_attempts:
                if attempts >= max_attempts:
                    self.logger.warning(f"搜索次数已达{max_attempts}次")
                    return 0
            for index, item in enumerate(item_list):
                if self._should_stop():
                    raise Stop
                if check_once(
                        item,
                        wait_time=wait_time,
                        max_time=once_max_time,
                        max_attempts=once_max_attempts,
                        **stable_kwargs):
                    self.screen_save_func(self.task_name)
                    return index + 1
            for action in search_actions:
                if self._should_stop():
                    raise Stop
                if "click" in action:
                    self.click_and_wait(
                        action['click'],
                        max_time=1,
                        wait_time=action_click_wait_time,
                        **stable_kwargs)
                elif "swipe" in action:
                    self.swipe_and_wait(
                        action['swipe']['start_coordinate'],
                        action['swipe']['end_coordinate'],
                        duration=action['swipe']['duration'],
                        **stable_kwargs)
            attempts += 1
