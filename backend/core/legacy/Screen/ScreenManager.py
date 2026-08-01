import logging

from backend.core.legacy.Config import Config
from backend.core.legacy.Screen import Screen, ScreenMode
from backend.core.legacy.Screen.DroidCastRaw import DroidCastRaw
from backend.core.legacy.Screen.LD import LD
from backend.core.legacy.Screen.MuMu import MuMu
from backend.core.legacy.Screen.U2 import U2
from backend.core.legacy.Screen.WindowCapture import WindowCapture


class ScreenManager:
    """截图实例管理器"""

    def __init__(self, config: Config, parent_logger=None):
        self.config = config
        self.logger = parent_logger.getChild(self.__class__.__name__) if parent_logger else logging.getLogger(self.__class__.__name__)
        self.control_mode = ScreenMode(self.config.get_config('截图模式'))
        self.current_screen: Screen | None = self.create_screen_instance()

    @property
    def ready(self):
        return (self.current_screen is not None) and self.current_screen.ready

    def create_screen_instance(self):
        """根据模式创建对应的截图实例（含自动回退）"""
        try:
            screen = self._try_create(self.control_mode)
            if screen and screen.ready:
                return screen

            # 配置的模式初始化失败，自动回退到 U2
            self.logger.warning(
                f"[{self.control_mode.name}] 初始化失败，自动回退到 U2 截图模式"
            )
            self.control_mode = ScreenMode.U2
            screen = self._try_create(ScreenMode.U2)
            return screen
        except Exception as e:
            self.logger.error(f"创建截图实例失败: {e}")
            return None

    def _try_create(self, mode: ScreenMode):
        """尝试创建指定模式的截图实例"""
        if mode == ScreenMode.DroidCastRaw:
            screen = DroidCastRaw(self.config, self.logger)
        elif mode == ScreenMode.MuMu:
            screen = MuMu(self.config, self.logger)
        elif mode == ScreenMode.LD:
            screen = LD(self.config, self.logger)
        elif mode == ScreenMode.WindowCapture:
            screen = WindowCapture(self.config, self.logger)
        elif mode == ScreenMode.U2:
            screen = U2(self.config, self.logger)
        else:
            screen = U2(self.config, self.logger)
        screen.init()
        if screen.ready:
            self.logger.info(f"[{mode.name}] 截图实例创建并初始化完成")
        else:
            self.logger.warning(f"[{mode.name}] 初始化失败（ready=False）")
        return screen

    def screencap(self):
        """统一对外提供截图接口（含自动回退）"""
        if self.current_screen and self.current_screen.ready:
            try:
                return self.current_screen.screencap()
            except Exception as e:
                self.logger.warning(f"当前截图实例执行失败，尝试创建新实例: {e}")
                self.current_screen = self.create_screen_instance()
                if self.current_screen and self.current_screen.ready:
                    return self.current_screen.screencap()
                return None
        self.logger.warning("截图实例未初始化或未就绪，尝试重新创建")
        self.current_screen = self.create_screen_instance()
        if self.current_screen and self.current_screen.ready:
            return self.current_screen.screencap()
        return None

    def release(self):
        """释放当前截图实例"""
        if self.current_screen:
            self.current_screen.release()
            self.current_screen = None
