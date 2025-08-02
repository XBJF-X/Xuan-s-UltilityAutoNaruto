import logging
import time
from typing import Dict, Tuple

import uiautomator2 as u2
from PySide6.QtCore import QThread

from utils.core.Base.Control.Control import Control
from utils.core.Base.Recognizer import Recognizer
from utils.core.Base.Screen.Screen import Screen
from utils.core.Config import Config


class Device:
    def __init__(self, config: Config, recognizer: Recognizer):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.package_name = "com.tencent.KiHan"
        self.controller = Control(config, initial=True)
        self.screen_size = self.controller.control_instance.screen_size
        self.screener = Screen(config, initial=True)
        self.recognizer = recognizer
        self.logger.debug("初始化完成...")

    def screen_cap(self):
        return self.screener.screencap()

    def click(self, params: Dict, resolution: Tuple, times=1):
        # start = time.perf_counter()
        if params['type'] == "COORDINATE":
            x, y = params['coordinate']
            self.logger.debug(f"[COORDINATE] Click ({x},{y})")
            self.click_position(params['coordinate'], resolution, times)
            return True
        elif params['type'] == "ELEMENT":
            screen = self.screen_cap()
            second = time.perf_counter()
            coordinates = self.recognizer.element_match(screen, params['name'])
            # print(f"[CAP]{(second - start) * 1000:.1f} ms [MATCH]{(time.perf_counter() - second) * 1000:.1f}")
            if coordinates:
                coordinate = coordinates[0]
                x_ratio, y_ratio = self.recognizer.element_templates[params['name']]["ratio"]
                # 按照元素可点击位置相对于模版左上角，相对整体的比例确定点击坐标
                x, y = (coordinate[0] * (1 - x_ratio) + coordinate[2] * x_ratio), (
                        coordinate[1] * (1 - y_ratio) + coordinate[3] * y_ratio)
                self.logger.debug(f"[{params['name']}] Click ({x},{y})")
                self.click_position((x, y), resolution, times)
                return True
            else:
                return False

    def click_position(self, coordinate, resolution=(1600, 900), times=1):
        scale = self.screen_size[0] / resolution[0]
        x, y = int(scale * coordinate[0]), int(scale * coordinate[1])
        for _ in range(times):
            self.controller.click(x, y)

    def swipe(self, start_coordinate, end_coordinate, duration=0.5, resolution=(
            1600, 900), times=1):
        scale = self.screen_size[0] / resolution[0]
        for _ in range(times):
            self.controller.swipe(
                (int(scale * start_coordinate[0]), int(scale * start_coordinate[1])),
                (int(scale * end_coordinate[0]), int(scale * end_coordinate[1])),
                duration
            )
            QThread.msleep(int(duration * 1000))

    def restart(self):
        # 停止应用
        self.controller.app_stop(self.package_name)
        # 启动应用
        self.controller.app_start(self.package_name)

    def input(self, input_text):
        self.controller.input(input_text)
        pass

    def press(self, key):
        self.controller.press(key)
        pass

    def detect(self, params: Dict) -> bool:
        """
        检测是否为某个Scene或者某个Element是否存在

        :param params:字典，包含type和name两个键
        :return:检测到与否
        """
        # start = time.perf_counter()
        screen = self.screen_cap()
        # second = time.perf_counter()
        if params['type'] == "SCENE":
            flag, confidence = self.recognizer.scene_match(screen, params['name'])
            # print(f"[CAP]{(second - start) * 1000:.1f} ms [MATCH]{(time.perf_counter() - second) * 1000:.1f} ms")
            return flag
        elif params['type'] == "ELEMENT":
            coordinates = self.recognizer.element_match(screen, params['name'])
            # print(f"[CAP]{(second - start) * 1000:.1f} ms [MATCH]{(time.perf_counter() - second) * 1000:.1f} ms")
            return len(coordinates) != 0
