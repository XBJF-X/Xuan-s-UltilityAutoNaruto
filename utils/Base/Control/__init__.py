import abc
import logging
from enum import IntEnum
from typing import Tuple

from utils.Base.Config import Config


class ControlMode(IntEnum):
    """控制模式枚举"""
    MiniTouch = 0
    U2 = 1


class InvalidResolution(Exception):
    pass


class Control(abc.ABC):
    """
    控制模块抽象基类
    """

    def __init__(self, config: Config, parent_logger=None):
        self.config = config
        self.logger = parent_logger.getChild(self.__class__.__name__) if parent_logger else logging.getLogger(self.__class__.__name__)
        self._ready = False  # 实例就绪状态

    @property
    def ready(self):
        """统一的就绪状态判断（子类重写）"""
        return self._ready

    @property
    @abc.abstractmethod
    def screen_size(self) -> Tuple[int, int]:
        """获取屏幕尺寸"""
        pass

    @abc.abstractmethod
    def get_device_info(self):
        """获取硬件信息"""
        pass

    @abc.abstractmethod
    def check_resolution(self):
        """获取硬件信息"""
        pass

    # ------------------- 抽象方法（子类必须实现）-------------------

    @abc.abstractmethod
    def release(self):
        """释放资源"""
        pass

    @abc.abstractmethod
    def click(self, x, y):
        """点击"""
        pass

    @abc.abstractmethod
    def swipe(self, start_coordinate, end_coordinate, duration=0.5):
        """滑动"""
        pass

    @abc.abstractmethod
    def app_stop(self, package_name):
        """停止应用"""
        pass

    @abc.abstractmethod
    def app_start(self, package_name):
        """启动应用"""
        pass

    @abc.abstractmethod
    def current_app(self):
        """获取当前应用"""
        pass

    @abc.abstractmethod
    def input(self, input_text):
        """输入文字"""
        pass

    @abc.abstractmethod
    def press_key(self, key):
        """按键"""
        pass

    @abc.abstractmethod
    def touch_down(self, x, y):
        """按下"""
        pass

    @abc.abstractmethod
    def touch_up(self, x, y):
        """抬起"""
        pass

    @abc.abstractmethod
    def long_press(self, x, y, duration):
        """长按"""
        pass

    @property
    @abc.abstractmethod
    def rotated(self):
        """是否旋转"""
        pass
