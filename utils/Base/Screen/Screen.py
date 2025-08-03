import enum
import logging

from PySide6.QtWidgets import QMessageBox

from utils.Base.Screen.Dxcam import Dxcam
from utils.Base.Screen.LD import LD
from utils.Base.Screen.MuMu import MuMu
from utils.Config import Config


class ScreenMode(enum.IntEnum):
    """截图模式枚举"""
    Dxcam = 0
    MuMu = 1
    LD = 2


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
            if self.screen_mode == ScreenMode.Dxcam:
                self.screen_instance = Dxcam(self.config)
                if not initial:
                    QMessageBox.information(None, "", f"[Common]初始化截图实例初始化完毕", QMessageBox.Ok)
                self.logger.info("Common截图实例初始化完毕")
            elif self.screen_mode == ScreenMode.MuMu:
                self.screen_instance = MuMu(self.config)
                self.screen_instance.init()
                if not initial:
                    QMessageBox.information(None, "", f"[MuMu]初始化截图实例初始化完毕", QMessageBox.Ok)
                self.logger.info("MuMu模拟器截图实例初始化完毕")
            elif self.screen_mode == ScreenMode.LD:
                self.screen_instance = LD(self.config)
                self.screen_instance.set_ld_path()
                self.screen_instance.connect_emu()
                if not initial:
                    QMessageBox.information(None, "", f"[LD]初始化截图实例初始化完毕", QMessageBox.Ok)
                self.logger.info("LD模拟器截图实例初始化完毕")
            self.screen_instance_ready = True
            self.config.set_config('截图模式', self.screen_mode)
        except Exception as e:
            QMessageBox.warning(None, "", f"[{self.screen_mode.name}]初始化截图实例出错，将启用[Common]方案", QMessageBox.Ok)
            self.logger.error(f"[%s]初始化截图实例出错，将启用[Common]方案", self.screen_mode.name)
            try:
                self.screen_mode = ScreenMode.Dxcam
                self.screen_instance = Dxcam(self.config)
                self.screen_instance_ready = True
                self.config.set_config('截图模式', self.screen_mode)
            except Exception as e:
                self.logger.error("初始化通用截图实例依旧出错")

    def switch_screen_mode(self, new_mode: ScreenMode):
        self.logger.info(f"即将切换截图模式：[{new_mode.name}]")
        if new_mode == self.screen_mode:
            QMessageBox.information(None, "", f"已经是[{new_mode.name}]模式了", QMessageBox.Ok)
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
