import abc
import logging
from enum import Enum

from backend.core.legacy.Config import Config


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

    def restart_emulator(self):
        """
        重启模拟器（子类按需重载）。
        基类默认实现：通过 adb 命令重启（适用于普通模拟器截图模式 0/1/2）。
        返回 True 表示重启指令已发出。
        """
        serial = self.config.get_config("串口", "")
        if not serial:
            self.logger.warning("未配置串口，无法通过 adb 重启模拟器")
            return False
        try:
            import subprocess
            self.logger.info(f"通过 adb 重启模拟器: {serial}")
            subprocess.run(
                ["adb", "-s", serial, "reboot"],
                capture_output=True, timeout=30)
            return True
        except Exception as e:
            self.logger.error(f"adb 重启模拟器失败: {e}")
            return False

    def __del__(self):
        """通用析构方法：自动释放资源"""
        self.release()
