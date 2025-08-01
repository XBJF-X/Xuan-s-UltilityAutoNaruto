import logging
import time

import uiautomator2 as u2
from PySide6.QtCore import QThread

from utils.core.Base.GetScreen.GetScreen import GetScreen
from utils.core.Config import Config


class Controller:
    def __init__(self, config: Config, serial="127.0.0.1:16416"):
        self.serial = serial
        self.package_name = "com.tencent.KiHan"
        self.screen_size = None
        self.device: u2.Device = None
        self.screen_instance = GetScreen(config, initial=True)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.connect()
        self.logger.debug("初始化完成...")

    def connect(self):
        self.device = u2.connect(self.serial)
        self.screen_size = self.device.window_size()  # (width, height)

    def screen_cap(self):
        # # 1. 将PIL图像转换为NumPy数组（此时颜色空间为RGB）
        # rgb_array = np.array(self.device.screenshot())
        # # 2. 将RGB转换为BGR（OpenCV默认使用BGR格式）
        # bgr_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
        return self.screen_instance.screencap()

    def click_position(self, coordinate, resolution=(1600, 900), times=1):
        scale = self.screen_size[0] / resolution[0]
        x, y = int(scale * coordinate[0]), int(scale * coordinate[1])
        for _ in range(times):
            self.device.click(x, y)

    def swipe(self, start_coordinate, end_coordinate, duration=0.5, resolution=(
            1600, 900), times=1):
        scale = self.screen_size[0] / resolution[0]
        for _ in range(times):
            self.device.swipe(
                int(scale * start_coordinate[0]), int(scale * start_coordinate[1]),
                int(scale * end_coordinate[0]), int(scale * end_coordinate[1]), duration)
            QThread.msleep(int(duration*1000))

    def restart(self):
        # 停止应用
        self.device.app_stop(self.package_name)
        # 启动应用
        self.device.app_start(self.package_name)