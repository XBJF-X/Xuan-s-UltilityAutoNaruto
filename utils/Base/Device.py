import logging

from PySide6.QtCore import QThread

from utils.Base.Control.Control import Control
from utils.Base.Screen.Screen import Screen
from utils.Base.Config import Config


class Device:
    resolution = (1600, 900)

    def __init__(self, config: Config):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.package_name = "com.tencent.KiHan"
        self.controller = Control(config, initial=True)
        self.screener = Screen(config, initial=True)
        self.screen_size = self.controller.control_instance.screen_size
        self.logger.debug("初始化完成...")

    def screen_cap(self):
        return self.screener.screencap()

    def click(self, coordinate, times=1):
        scale = self.screen_size[0] / self.resolution[0]
        x, y = int(scale * coordinate[0]), int(scale * coordinate[1])
        for _ in range(times):
            self.controller.click(x, y)

    def swipe(self, start_coordinate, end_coordinate, duration=0.5, times=1):
        scale = self.screen_size[0] / self.resolution[0]
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

    def press_key(self, key):
        self.controller.press_key(key)

    def long_press(self, x, y, duration):
        self.controller.long_press(x, y, duration)
