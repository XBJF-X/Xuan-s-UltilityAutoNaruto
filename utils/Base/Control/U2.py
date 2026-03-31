import threading
import time
from typing import Tuple

import uiautomator2 as u2

from utils.Base.Config import Config
from utils.Base.Control import Control


class U2(Control):
    """
    使用uiautomator2进行控制的控制方案
    """

    def __init__(self, config: Config, parent_logger, serial=None):
        super().__init__(config, parent_logger)
        if serial:
            self.serial = serial
        else:
            self.serial = config.get_config("串口")
        self.u2_device: u2.Device | None = None
        self._lock = threading.Lock()  # 新增：设备操作锁，避免多线程竞争
        try:
            self.u2_device = u2.connect(self.serial)
            self.get_device_info()
            self.logger.info(f"成功连接设备 {self.serial}")
        except Exception as e:
            self.u2_device = None
            self.logger.error(f"连接设备失败: {e}")

    @property
    def ready(self):
        return self.u2_device is not None

    @property
    def rotated(self) -> bool:
        """获取设备旋转状态，False表示竖屏，True表示横屏"""
        with self._lock:
            if self.u2_device is None:
                self.logger.error("设备未连接，无法执行点击")
                return True
            rotation = self.u2_device.info.get('displayRotation', 0)
            self.logger.debug(f"旋转状态：{rotation}")
            # return rotation in [1, 3]
            return rotation

    @property
    def screen_size(self) -> Tuple[int, int]:
        width, height = self.window_size[0], self.window_size[1]
        if width < height:
            return height, width
        return width, height

    def get_device_info(self):
        """获取硬件信息"""
        print(self.u2_device.info)
        self.abi = self.u2_device.shell('getprop ro.product.cpu.abi').output.strip()
        self.sdk = self.u2_device.info.get('sdkInt', 32)  # 获取设备sdk
        self.orientation = self.u2_device.info.get('displayRotation', 0)
        self.window_size = self.u2_device.window_size()
        self.width = self.window_size[0]
        self.height = self.window_size[1]
        self.logger.debug(f"\n屏幕方向:{self.orientation}\n屏幕宽度:{self.width}\n屏幕高度:{self.height}")

    def click(self, x: int, y: int, duration: float = 0.03):
        if not self.u2_device:
            self.logger.error("设备未连接，无法执行点击")
            return
        with self._lock:  # 加锁：同一时间仅一个线程操作设备
            try:
                self.logger.debug(f"执行点击: ({x}, {y})")
                self.u2_device.touch.down(x, y)
                # self.logger.debug(f"[PressDown] ({x},{y})")
                time.sleep(duration)
                self.u2_device.touch.up(x, y)
                # self.logger.debug(f"[PressUp] ({x},{y})")
                # self.u2_device.click(x, y)
            except Exception as e:
                self.logger.error(f"点击失败 ({x},{y}): {e}")
                self._reconnect()  # 连接异常时重连

    def swipe(self, start_coordinate, end_coordinate, duration=0.5):
        def direction_judge():
            if abs(start_coordinate[0] - end_coordinate[0]) >= abs(
                    start_coordinate[1] - end_coordinate[1]):
                if start_coordinate[0] - end_coordinate[0] > 0:
                    return "left"
                else:
                    return "right"
            else:
                if start_coordinate[1] - end_coordinate[1] > 0:
                    return "up"
                else:
                    return "down"

        def get_bounding_box():
            """
            计算包含起点和终点的最小矩形框。

            Returns:
                tuple: (left, top, right, bottom) 矩形边界坐标
            """
            x1, y1 = start_coordinate
            x2, y2 = end_coordinate
            left = min(x1, x2)
            top = min(y1, y2)
            right = max(x1, x2)
            bottom = max(y1, y2)

            padding = 0
            return left - padding, top - padding, right + padding, bottom + padding

        direction = direction_judge()

        def get_scale():
            if direction in ["up", "down"]:
                return abs(start_coordinate[1] - end_coordinate[1]) / 900
            else:
                return abs(start_coordinate[0] - end_coordinate[0]) / 1600

        if not self.u2_device:
            self.logger.error("设备未连接，无法执行滑动")
            return
        with self._lock:
            try:
                # self.u2_device.swipe_ext(
                #     direction,
                #     box=get_bounding_box(),
                #     scale=1.0,
                #     duration=duration
                # )
                self.u2_device.swipe(
                    start_coordinate[0], start_coordinate[1],
                    end_coordinate[0], end_coordinate[1],
                    duration
                )
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
            self.get_screen_size = self.u2_device.window_size()
            self.logger.info("重连设备成功")
        except Exception as e:
            self.u2_device = None
            self.logger.error(f"重连设备失败: {e}")


if __name__ == "__main__":
    c = U2(None, None, "127.0.0.1:16448")
    print(c.current_app())
