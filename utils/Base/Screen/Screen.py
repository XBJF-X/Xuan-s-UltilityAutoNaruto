import logging

from PySide6.QtWidgets import QMessageBox

from utils.Base.Enums import ScreenMode
from utils.Base.Screen.DroidCastRaw import DroidCastRaw
from utils.Base.Screen.LD import LD
from utils.Base.Screen.MuMu import MuMu
from utils.Base.Screen.U2 import U2
from utils.Base.Screen.WindowCapture import WindowCapture
from utils.Base.Config import Config


class Screen:
    """
    根据用户选择的方案获取Screen
    总控所有截图方案，提供截图方案的初始化和切换
    只需要输入截图模式来初始化，调用截图即可得到规范的截图数据
    提供了截图模式切换的选择
    """

    def __init__(self, config: Config, initial=False):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        self.screen_mode = ScreenMode(self.config.get_config('截图模式'))
        self.screen_instance = None
        self.screen_instance_ready = False
        self.init_screen_instance(initial)

    def __del__(self):
        if self.screen_instance:
            self.screen_instance.release()

    def init_screen_instance(self, initial=False):
        self.logger.info(f"当前截图模式：[{self.screen_mode.name}]")
        try:
            if self.screen_mode == ScreenMode.DroidCastRaw:
                self.screen_instance = DroidCastRaw(self.config)
            elif self.screen_mode == ScreenMode.MuMu:
                self.screen_instance = MuMu(self.config)
            elif self.screen_mode == ScreenMode.LD:
                self.screen_instance = LD(self.config)
            elif self.screen_mode == ScreenMode.WindowCapture:
                self.screen_instance = WindowCapture(self.config)
            elif self.screen_mode == ScreenMode.U2:
                self.screen_instance = U2(self.config)
            self.screen_instance.init()
            if not initial:
                QMessageBox.information(None, "", f"[{self.screen_mode.name}]截图实例初始化完毕", QMessageBox.StandardButton.Ok)
            self.logger.info(f"[{self.screen_mode.name}]截图实例初始化完毕")
            self.screen_instance_ready = True
            self.config.set_config('截图模式', self.screen_mode)
        except Exception as e:
            QMessageBox.warning(None, "", f"[{self.screen_mode.name}]初始化截图实例出错", QMessageBox.StandardButton.Ok)
            self.logger.error(f"[{self.screen_mode.name}]初始化截图实例出错{e}")

    def switch_screen_mode(self, new_mode: ScreenMode):
        self.logger.info(f"即将切换截图模式：[{new_mode.name}]")
        if new_mode == self.screen_mode:
            QMessageBox.information(None, "", f"已经是[{new_mode.name}]模式了", QMessageBox.StandardButton.Ok)
            self.logger.info(f"已经是[{new_mode.name}]模式了")
            return
        self.screen_mode = new_mode
        self.screen_instance_ready = False
        self.release()
        # 再初始化新的实例
        self.init_screen_instance()

    def release(self):
        # 先把原先的截图实例释放掉
        self.screen_instance.release()
        self.logger.debug(f"[{self.screen_mode.name}]实例已清除")

    def screencap(self):
        if self.screen_instance_ready:
            screen = self.screen_instance.screencap()
            # cv2.imshow("截图",screen)
            # cv2.waitKey(0)
            return screen
        else:
            self.logger.warning("截图实例未初始化或切换未完成")
            return None
