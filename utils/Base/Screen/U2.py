import logging

import cv2
import numpy as np
import uiautomator2 as u2

from utils.Config import Config


class U2:
    def __init__(self, config: Config):
        try:
            self.logger = logging.getLogger(self.__class__.__name__ + "_Screen")
            self.config = config
            self.serial = config.get_config("串口")
            self.u2_device: u2.Device = None
            self.screen_size = None

        except Exception as e:
            print(e)

    def init(self):
        self.u2_device = u2.connect(self.serial)
        self.screen_size = self.u2_device.window_size()  # (width, height)

    def screencap(self):
        # 获取截图的二进制数据
        bgr = self.u2_device.screenshot(format='opencv')
        if bgr.shape[:2] < (900, 1600):
            bgr = cv2.resize(bgr, (1600, 900), interpolation=cv2.INTER_CUBIC)
        elif bgr.shape[:2] > (900, 1600):
            bgr = cv2.resize(bgr, (1600, 900), interpolation=cv2.INTER_AREA)
        return bgr

    def release(self):
        self.u2_device = None
