import time
from enum import Enum
from typing import List, Tuple

from minidevice import MiniTouch as MiniTouchCore
from minidevice.utils.command_builder_utils import CommandBuilder

from utils.Base.Config import Config
from utils.Base.Control import Control
from utils.Base.Control.U2 import U2


class ArchType(Enum):
    ARM = "arm"
    ARM64 = "arm64"
    X86 = "x86"
    X86_64 = "x86_64"
    UNKNOWN = "unknown"


class MiniTouch(Control):
    """
    基于minidevice.MiniTouch封装的控制器
    严格遵循Control抽象类约束，兼容原有业务接口
    """

    def __init__(self, config: Config, parent_logger=None, device_serial: str = ""):
        super().__init__(config, parent_logger)
        self._released = False
        self._mt_core = None
        self.u2 = None
        try:
            self.device_serial = device_serial or self.config.get_config("串口", "")
            if not self.device_serial:
                raise RuntimeError("设备序列号不能为空")

            self._mt_core = MiniTouchCore(self.device_serial)
            self.max_contacts = int(self._mt_core.max_contacts)
            self.max_x = int(self._mt_core.max_x)
            self.max_y = int(self._mt_core.max_y)
            self.max_pressure = int(self._mt_core.max_pressure)

            self.u2 = U2(config, parent_logger, self.device_serial)
            self.screen_size = self.get_screen_size()
            self.logger.info(f"MiniTouch 初始化成功 | 分辨率:{self.screen_size[0]}x{self.screen_size[1]}")
        except Exception as e:
            self.logger.error(f"MiniTouch 初始化失败: {e}")
            self._released = True
            raise

    # ==================== 实现Control抽象基类必须方法 ====================
    @property
    def ready(self) -> bool:
        """Control约束：就绪状态"""
        return not self._released and self._mt_core is not None

    def get_screen_size(self) -> Tuple[int, int]:
        """Control约束：屏幕尺寸（兼容原有逻辑）"""
        return self.u2.screen_size

    def release(self):
        if self._released:
            return
        self._released = True
        if self._mt_core:
            try:
                self.up_all_contacts()
                self._mt_core.stop()
            except Exception as e:
                self.logger.warning(f"停止 MiniTouch 服务失败: {e}")
        if self.u2:
            self.u2.release()
        self.logger.info("MiniTouch 已完全释放")

    def up_all_contacts(self):
        if self._mt_core:
            try:
                # 发送抬起所有触点的命令
                for idx in range(self.max_contacts):
                    self._mt_core.send(f"u {idx}\n")
                self._mt_core.send("c\n")
            except Exception as e:
                self.logger.warning(f"停止 MiniTouch 服务失败: {e}")

    # ==================== 核心触摸方法（直接转发minidevice实现） ====================
    def click(self, x: int, y: int, duration: int = 100):
        """
        单点点击（满足Control约束 + 兼容原有接口）
        :param x: X坐标
        :param y: Y坐标
        :param duration: 点击时长(ms)，minidevice默认100
        """
        if not self.ready:
            return
        # 坐标边界保护
        x = max(0, min(self.max_x, x))
        y = max(0, min(self.max_y, y))
        # 直接调用minidevice官方点击
        self._mt_core.click(x, y, duration)

    def swipe(self, start_coordinate: Tuple[int, int], end_coordinate: Tuple[
        int, int], duration: float = 1.0):
        """
        单指滑动
        :param start_coordinate: 起点 (x1,y1)
        :param end_coordinate: 终点 (x2,y2)
        :param duration: 滑动总时长（秒！！！） 传1=1秒，传2=2秒
        """
        if not self.ready:
            return

        x1, y1 = start_coordinate
        x2, y2 = end_coordinate
        # 坐标边界校验
        x1 = max(0, min(self.max_x, x1))
        y1 = max(0, min(self.max_y, y1))
        x2 = max(0, min(self.max_x, x2))
        y2 = max(0, min(self.max_y, y2))

        total_ms = int(duration * 1000)
        TOTAL_STEPS = int(total_ms / 16)

        # 生成均匀滑动路径
        points = []
        for i in range(TOTAL_STEPS + 1):
            ratio = i / TOTAL_STEPS
            x = int(x1 + (x2 - x1) * ratio)
            y = int(y1 + (y2 - y1) * ratio)
            points.append((x, y))

        self._mt_core.swipe(points, total_ms)
        # self.logger.debug(f"滑动: {start_coordinate} -> {end_coordinate} | 总时长:{duration}s")
        time.sleep(duration * 1.2)

    # ==================== 复用ADB实现Control其他抽象方法 ====================
    def app_stop(self, package_name: str):
        self.u2.app_stop(package_name)

    def app_start(self, package_name: str):
        self.u2.app_start(package_name)

    def current_app(self) -> Tuple[str, str]:
        return self.u2.current_app()

    def input(self, input_text: str):
        self.u2.input(input_text)

    def press_key(self, key: int | str):
        self.u2.press_key(key)

    def touch_down(self, x: int, y: int):
        """Control约束：按下（基于minitouch指令封装）"""
        if not self.ready:
            return
        self._mt_core.send(f"d 0 {x} {y} {self.max_pressure}\nc")

    def touch_up(self, x: int, y: int):
        """Control约束：抬起"""
        if not self.ready:
            return
        self._mt_core.send(f"u 0\nc")

    def long_press(self, x: int, y: int, duration: float):
        """Control约束：长按"""
        self.click(x, y, duration=int(duration * 1000))

    def multi_tap(self, points: List[List[int]], pressure: int = 100, duration: float = 0.1):
        """
        多点同时点击（使用 CommandBuilder）
        :param points: 坐标列表 [[x1,y1], [x2,y2], ...]
        :param pressure: 按压力度（默认100）
        :param duration: 按下持续时间（秒）
        """
        if not self.ready:
            return

        # 限制触点数量并进行坐标边界保护
        points = points[:self.max_contacts]
        points = [(max(0, min(self.max_x, x)), max(0, min(self.max_y, y))) for x, y in points]

        builder = CommandBuilder()
        # 1. 同时按下所有点
        for idx, (x, y) in enumerate(points):
            builder.down(idx, x, y, pressure)
        builder.commit()  # 提交，使所有按下同时生效

        # 2. 等待指定时长
        builder.wait(int(duration * 1000))

        # 3. 同时抬起所有点
        for idx in range(len(points)):
            builder.up(idx)
        builder.commit()  # 提交，使所有抬起同时生效

        # 4. 发送命令到设备（self._mt_core 有 send 方法）
        builder.publish(self._mt_core)

    def __del__(self):
        if hasattr(self, '_released') and not self._released:
            self.release()
