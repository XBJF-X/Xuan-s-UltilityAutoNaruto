import uiautomator2 as u2
from PySide6.QtCore import QThread

from utils.Config import Config


class U2:
    """
    使用uiautomator2进行控制的控制方案
    """

    def __init__(self, config: Config):
        try:
            self.config = config
            self.serial = config.get_config("串口")
            self.screen_size = None
            self.u2_device: u2.Device = None
            self.u2_device = u2.connect(self.serial)
            self.screen_size = self.u2_device.window_size()  # (width, height)
        except Exception as e:
            print(e)

    def click(self, x, y, duration=200):
        self.u2_device.touch.down(x, y)
        QThread.msleep(duration)
        self.u2_device.touch.up(x, y)
        # self.u2_device.click(x, y)

    def swipe(self, start_coordinate, end_coordinate, duration=0.5):
        self.u2_device.swipe(
            start_coordinate[0], start_coordinate[1], end_coordinate[0], end_coordinate[1], duration)

    def app_stop(self, package_name: str):
        self.u2_device.app_stop(package_name)

    def app_start(self, package_name: str):
        self.u2_device.app_start(package_name)

    def input(self, input_text):
        self.u2_device.shell(f"input text {input_text}")

    def press(self, key):
        self.u2_device.press(key)

    def release(self):
        pass

    def touch_down(self, x, y):
        self.u2_device.touch.down(x, y)

    def touch_up(self, x, y):
        self.u2_device.touch.up(x, y)
