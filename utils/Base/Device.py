import logging

from utils.Base.Config import Config
from utils.Base.Control.ControlManager import ControlManager
from utils.Base.Screen.ScreenManager import ScreenManager


class Device:
    resolution = (1600, 900)

    def __init__(self, config: Config, parent_logger=None):
        self.logger = parent_logger.getChild(self.__class__.__name__) if parent_logger else logging.getLogger(self.__class__.__name__)
        self.package_name = "com.tencent.KiHan"
        self.control_manager = ControlManager(config, self.logger)
        self.screen_manager = ScreenManager(config, self.logger)
        self.logger.debug("初始化完成...")

    @property
    def device_ready(self):
        return self.control_manager.ready and self.screen_manager.ready

    @property
    def screen_size(self):
        return self.control_manager.current_control.screen_size

    @property
    def rotated(self):
        return self.control_manager.rotated

    def regularize_coordinate(self, coordinate_x, coordinate_y):
        scale = self.screen_size[0] / self.resolution[0]
        x, y = int(scale * coordinate_x), int(scale * coordinate_y)

        # 确保坐标在屏幕范围内
        x = max(0, min(x, self.screen_size[0] - 1))  # 宽度最大为 screen_size[0]-1
        y = max(0, min(y, self.screen_size[1] - 1))  # 高度最大为 screen_size[1]-1

        return x, y

    def screen_cap(self):
        return self.screen_manager.screencap()

    def click(self, coordinate_x, coordinate_y, times=1):
        x, y = self.regularize_coordinate(coordinate_x, coordinate_y)
        self.logger.debug(f"[Click] ({coordinate_x},{coordinate_y})[{x},{y}]")
        for _ in range(times):
            self.control_manager.click(x, y)

    def swipe(self, start_coordinate, end_coordinate, duration=0.5, times=1):
        x1, y1 = self.regularize_coordinate(start_coordinate[0], start_coordinate[1])
        x2, y2 = self.regularize_coordinate(end_coordinate[0], end_coordinate[1])
        self.logger.debug(f"[Swipe] ({start_coordinate[0]},{start_coordinate[1]})->({end_coordinate[0]},{end_coordinate[1]}) [ ({x1},{y1})->({x2},{y2}) ]")
        for _ in range(times):
            self.control_manager.swipe(
                (x1, y1),
                (x2, y2),
                duration
            )

    def app_restart(self):
        # 停止应用
        self.app_stop()
        # 启动应用
        self.app_start()

    def app_start(self):
        # 启动应用
        self.control_manager.app_start(self.package_name)

    def app_stop(self):
        # 停止应用
        self.control_manager.app_stop(self.package_name)

    def current_app(self):
        return self.control_manager.current_app()

    def input(self, input_text):
        self.control_manager.input(input_text)

    def press_key(self, key):
        self.control_manager.press_key(key)

    def long_press(self, coordinate_x, coordinate_y, duration):
        x, y = self.regularize_coordinate(coordinate_x, coordinate_y)
        self.control_manager.long_press(x, y, duration)
