import logging

from utils.Base.Config import Config
from utils.Base.Screen import Screen, ScreenMode
from utils.Base.Screen.DroidCastRaw import DroidCastRaw
from utils.Base.Screen.LD import LD
from utils.Base.Screen.MuMu import MuMu
from utils.Base.Screen.U2 import U2
from utils.Base.Screen.WindowCapture import WindowCapture


class ScreenManager:
    """截图实例管理器"""

    def __init__(self, config: Config, parent_logger=None):
        self.config = config
        self.logger = parent_logger.getChild(self.__class__.__name__) if parent_logger else logging.getLogger(self.__class__.__name__)
        self.current_screen: Screen | None = None  # 当前生效的截图实例
        self.control_mode = ScreenMode(self.config.get_config('截图模式'))
        self.create_screen_instance()

    @property
    def ready(self):
        return self.current_screen.ready

    def create_screen_instance(self):
        """根据模式创建对应的截图实例"""
        # 先释放原有实例
        if self.current_screen:
            self.current_screen.release()

        # 根据模式创建子类实例
        if self.control_mode == ScreenMode.DroidCastRaw:
            self.current_screen = DroidCastRaw(self.config, self.logger)
        elif self.control_mode == ScreenMode.MuMu:
            self.current_screen = MuMu(self.config, self.logger)
        elif self.control_mode == ScreenMode.LD:
            self.current_screen = LD(self.config, self.logger)  # 需提前实现 LD 子类
        elif self.control_mode == ScreenMode.WindowCapture:
            self.current_screen = WindowCapture(self.config, self.logger)  # 需提前实现
        elif self.control_mode == ScreenMode.U2:
            self.current_screen = U2(self.config, self.logger)  # 需提前实现
        else:
            self.logger.error(f"不支持的截图模式：{self.control_mode.name}")
            return

        # 初始化新实例
        self.current_screen.init()
        # QMessageBox.information(None, "", f"[{self.control_mode.name}]截图实例初始化完毕", QMessageBox.StandardButton.Ok)
        self.logger.info(f"[{self.control_mode.name}] 截图实例创建并初始化完成")

    def screencap(self):
        """统一对外提供截图接口"""
        if self.current_screen and self.current_screen.ready:
            return self.current_screen.screencap()
        self.logger.warning("截图实例未初始化或未就绪")
        return None

    def release(self):
        """释放当前截图实例"""
        if self.current_screen:
            self.current_screen.release()
            self.current_screen = None
