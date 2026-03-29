import abc
import logging

from PySide6.QtWidgets import QMessageBox
from enum import Enum

from utils.Base.Config import Config


class ScreenMode(Enum):
    DroidCastRaw = 0
    WindowCapture = 1
    U2 = 2
    MuMu = 3
    LD = 4


class Screen(abc.ABC):
    """
    截图类抽象基类，定义所有截图类必须实现的核心接口
    """

    def __init__(self, config: Config, parent_logger):
        self.config = config
        self.logger = parent_logger.getChild(self.__class__.__name__) if parent_logger else logging.getLogger(self.__class__.__name__)
        self._ready = False

    @property
    def ready(self):
        """通用属性：判断实例是否就绪"""
        return self._ready

    @abc.abstractmethod
    def init(self):
        """抽象方法：初始化截图实例（子类必须实现）"""
        pass

    @abc.abstractmethod
    def release(self):
        """抽象方法：释放截图实例资源（子类必须实现）"""
        pass

    @abc.abstractmethod
    def screencap(self):
        """抽象方法：执行截图（子类必须实现），返回截图数据"""
        pass

    def __del__(self):
        """通用析构方法：自动释放资源"""
        self.release()
