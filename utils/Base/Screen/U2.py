import cv2
import uiautomator2 as u2

from utils.Base.Config import Config


class U2:
    def __init__(self, config: Config, parent_logger):
        self.logger = parent_logger.getChild(self.__class__.__name__ + "_Screen")
        try:
            self.config = config
            self.serial = config.get_config("串口")
            self.u2_device: u2.Device = None
            self.screen_size = None
            self.ready = False

        except Exception as e:
            self.logger.error(e)

    def init(self):
        try:
            self.u2_device = u2.connect(self.serial)
            self.screen_size = self.u2_device.window_size()  # (width, height)
            self.ready = True
        except Exception as e:
            self.logger.error("[U2]实例化失败")
            self.ready = False

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
