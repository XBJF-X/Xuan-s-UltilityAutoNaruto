import enum
import logging

import cv2
from PySide6.QtWidgets import QMessageBox

from utils.core.Base.GetScreen.Commom import Common
from utils.core.Base.GetScreen.LD import LD
from utils.core.Base.GetScreen.MuMu import MuMu
from utils.core.Config import Config


class EmulatorType(enum.IntEnum):
    """模拟器类型枚举类，值从 0 到 2，对应不同模拟器类型"""
    Common = 0  # 通用类型，输入包含 region
    MuMu = 1  # MuMU模拟器，输入无特殊参数
    LD = 2  # 雷电模拟器，输入无特殊参数


class GetScreen:
    """
    根据用户选择的方案获取Screen
    提供截图方案的初始化和切换
    只需要输入截图模式来初始化，调用截图即可得到规范的截图数据
    提供了截图模式切换的选择
    """

    def __init__(self, config: Config, initial=False):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        self.screen_mode = EmulatorType(self.config.get_config('截图模式'))
        self.screen_instance = None
        self.screen_instance_ready = False
        self.init_screen_instance(initial)

    def __del__(self):
        if self.screen_instance:
            self.screen_instance.release()

    def init_screen_instance(self, initial=False):
        self.logger.info(f"当前截图模式：[{self.screen_mode.name}]")
        try:
            if self.screen_mode == EmulatorType.Common:
                self.screen_instance = Common(self.config)
                if not initial:
                    QMessageBox.information(None, "", f"[Common]初始化截图实例初始化完毕", QMessageBox.Ok)
                self.logger.info("Common截图实例初始化完毕")
            elif self.screen_mode == EmulatorType.MuMu:
                self.screen_instance = MuMu(self.config)
                self.screen_instance.init()
                if not initial:
                    QMessageBox.information(None, "", f"[MuMu]初始化截图实例初始化完毕", QMessageBox.Ok)
                self.logger.info("MuMu模拟器截图实例初始化完毕")
            elif self.screen_mode == EmulatorType.LD:
                self.screen_instance = LD(self.config)
                self.screen_instance.set_ld_path()
                emu_list = self.screen_instance.get_emu_list()
                self.logger.debug("找到以下模拟器实例:")
                for emu in emu_list:
                    self.logger.debug(f"索引: {emu.index}, 名称: {emu.name.decode('gbk')}, 分辨率: {emu.width}x{emu.height}, PID: {emu.playerpid}")
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
                self.screen_mode = EmulatorType.Common
                self.screen_instance = Common(self.config)
                self.screen_instance_ready = True
                self.config.set_config('截图模式', self.screen_mode)
            except Exception as e:
                self.logger.error("初始化通用截图实例依旧出错")

    def switch_screen_mode(self, new_mode: EmulatorType):
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
