from PySide6.QtCore import QThread

from utils.Base.Config import Config
from utils.Base.Control.Control import Control
from utils.Base.Screen.Screen import Screen


class Device:
    resolution = (1600, 900)

    def __init__(self, config: Config, parent_logger):
        self.logger = parent_logger.getChild(self.__class__.__name__)
        self.package_name = "com.tencent.KiHan"
        self.controller = Control(config, self.logger, initial=True)
        self.screener = Screen(config, self.logger, initial=True)
        self.screen_size = self.controller.control_instance.screen_size
        self.logger.debug("初始化完成...")

    def regularize_coordinate(self, coordinate_x, coordinate_y):
        scale = self.screen_size[0] / self.resolution[0]
        x, y = int(scale * coordinate_x), int(scale * coordinate_y)

        # 确保坐标在屏幕范围内
        x = max(0, min(x, self.screen_size[0] - 1))  # 宽度最大为 screen_size[0]-1
        y = max(0, min(y, self.screen_size[1] - 1))  # 高度最大为 screen_size[1]-1

        return x, y

    def screen_cap(self):
        return self.screener.screencap()

    def click(self, coordinate_x, coordinate_y, times=1):
        x, y = self.regularize_coordinate(coordinate_x, coordinate_y)
        for _ in range(times):
            self.controller.click(x, y)

    def swipe(self, start_coordinate, end_coordinate, duration=0.5, times=1):
        x1, y1 = self.regularize_coordinate(start_coordinate[0], start_coordinate[1])
        x2, y2 = self.regularize_coordinate(end_coordinate[0], end_coordinate[1])
        for _ in range(times):
            self.controller.swipe(
                (x1, y1),
                (x2, y2),
                duration
            )

    def restart(self):
        # 停止应用
        self.controller.app_stop(self.package_name)
        # 启动应用
        self.controller.app_start(self.package_name)

    def current_app(self):
        return self.controller.current_app()

    def input(self, input_text):
        self.controller.input(input_text)

    def press_key(self, key):
        self.controller.press_key(key)

    def long_press(self, coordinate_x, coordinate_y, duration):
        x, y = self.regularize_coordinate(coordinate_x, coordinate_y)
        self.controller.long_press(x, y, duration)
