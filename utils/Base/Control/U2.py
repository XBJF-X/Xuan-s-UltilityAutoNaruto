import logging
import threading
import time

import uiautomator2 as u2

from utils.Base.Config import Config


class U2:
    """
    使用uiautomator2进行控制的控制方案
    """

    def __init__(self, config: Config, parent_logger, serial=None):
        self.logger = parent_logger.getChild(self.__class__.__name__ + "_Control") if parent_logger else logging.getLogger(self.__class__.__name__ + "_Control")
        self.config = config
        if serial:
            self.serial = serial
        else:
            self.serial = config.get_config("串口")
        self.screen_size = None
        self.u2_device: u2.Device | None = None
        self._lock = threading.Lock()  # 新增：设备操作锁，避免多线程竞争
        try:
            self.u2_device = u2.connect(self.serial)
            self.screen_size = self.u2_device.window_size()  # (width, height)
            self.logger.info(f"成功连接设备 {self.serial}，屏幕尺寸 {self.screen_size}")
        except Exception as e:
            self.u2_device = None
            self.logger.error(f"连接设备失败: {e}")

    def click(self, x: int, y: int, duration: float = 0.03):
        if not self.u2_device:
            self.logger.error("设备未连接，无法执行点击")
            return
        with self._lock:  # 加锁：同一时间仅一个线程操作设备
            try:
                self.u2_device.touch.down(x, y)
                # self.logger.debug(f"[PressDown] ({x},{y})")
                time.sleep(duration)
                self.u2_device.touch.up(x, y)
                # self.logger.debug(f"[PressUp] ({x},{y})")
                # self.u2_device.click(x, y)
            except Exception as e:
                self.logger.error(f"点击失败 ({x},{y}): {e}")
                self._reconnect()  # 连接异常时重连

    def swipe(self, start_coordinate, end_coordinate, duration=0.5, wait_time=0.2):
        if not self.u2_device:
            self.logger.error("设备未连接，无法执行滑动")
            return
        with self._lock:
            try:
                self.u2_device.swipe(
                    start_coordinate[0], start_coordinate[1],
                    end_coordinate[0], end_coordinate[1],
                    duration
                )
                time.sleep(wait_time)
            except Exception as e:
                self.logger.error(f"滑动失败: {e}")
                self._reconnect()

    def app_stop(self, package_name: str):
        if not self.u2_device:
            self.logger.error("设备未连接，无法停止应用")
            return

        with self._lock:
            try:
                self.u2_device.app_stop(package_name)
            except Exception as e:
                self.logger.error(f"停止应用 {package_name} 失败: {e}")
                self._reconnect()

    def app_start(self, package_name: str):
        if not self.u2_device:
            self.logger.error("设备未连接，无法启动应用")
            return

        with self._lock:
            try:
                if self.u2_device.app_current()["package"] != package_name:
                    self.u2_device.app_start(package_name)
            except Exception as e:
                self.logger.error(f"启动应用 {package_name} 失败: {e}")
                self._reconnect()

    def current_app(self):
        front_app = self.u2_device.app_current()
        return {
            "package": front_app["package"],
            "activity": front_app["activity"]
        }

    def input(self, input_text):
        if not self.u2_device:
            self.logger.error("设备未连接，无法输入文本")
            return
        with self._lock:
            try:
                self.u2_device.shell(f"input text {input_text}")
            except Exception as e:
                self.logger.error(f"输入文本 {input_text} 失败: {e}")
                self._reconnect()

    def press_key(self, key):
        if not self.u2_device:
            self.logger.error("设备未连接，无法按下按键")
            return
        with self._lock:
            try:
                self.u2_device.press(key)
            except Exception as e:
                self.logger.error(f"按下按键 {key} 失败: {e}")
                self._reconnect()

    def release(self):
        """修复：释放设备资源"""
        pass

    def touch_down(self, x: int, y: int):
        if not self.u2_device:
            self.logger.error("设备未连接，无法按下")
            return
        with self._lock:
            try:
                self.u2_device.touch.down(x, y)
            except Exception as e:
                self.logger.error(f"按下 ({x},{y}) 失败: {e}")
                self._reconnect()

    def touch_up(self, x: int, y: int):
        if not self.u2_device:
            self.logger.error("设备未连接，无法抬起")
            return
        with self._lock:
            try:
                self.u2_device.touch.up(x, y)
            except Exception as e:
                self.logger.error(f"抬起 ({x},{y}) 失败: {e}")
                self._reconnect()

    def long_press(self, x: int, y: int, duration: float):
        if not self.u2_device:
            self.logger.error("设备未连接，无法执行长按")
            return
        with self._lock:
            try:
                self.u2_device.touch.down(x, y)
                time.sleep(duration)  # 替换QThread.msleep
                self.u2_device.touch.up(x, y)
            except Exception as e:
                self.logger.error(f"长按失败 ({x},{y}): {e}")
                self._reconnect()

    def _reconnect(self):
        """新增：连接异常时重连设备"""
        return
        try:
            self.logger.info("尝试重连设备...")
            self.u2_device = u2.connect(self.serial)
            self.screen_size = self.u2_device.window_size()
            self.logger.info("重连设备成功")
        except Exception as e:
            self.u2_device = None
            self.logger.error(f"重连设备失败: {e}")


if __name__ == "__main__":
    instance = U2(None, None, "emulator-5554")
    for _ in range(10):
        instance.swipe( [202, 150],[202, 763], duration=0.1)
    for _ in range(10):
        instance.swipe([202, 763], [202, 150], duration=0.6)
