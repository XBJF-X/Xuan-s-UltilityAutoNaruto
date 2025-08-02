import enum
import logging
from PySide6.QtWidgets import QMessageBox

from utils.core.Base.Control.U2 import U2
from utils.core.Config import Config


class ControlMode(enum.IntEnum):
    """控制模式枚举"""
    U2 = 0


class Control:
    """
    根据用户选择的方案获取Control_instance
    总控所有控制方案，提供控制方案的初始化和切换
    只需要输入控制模式来初始化，调用控制即可得到规范的控制数据
    提供了控制模式切换的选择
    """

    def __init__(self, config: Config, initial=False):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        self.control_mode = ControlMode(self.config.get_config('控制模式'))
        self.control_instance = None
        self.control_instance_ready = False
        self.init_control_instance(initial)

    def __del__(self):
        if self.control_instance:
            self.control_instance.release()

    def init_control_instance(self, initial=False):
        self.logger.info(f"当前控制模式：[{self.control_mode.name}]")
        try:
            if self.control_mode == ControlMode.U2:
                self.control_instance = U2(self.config)
                if not initial:
                    QMessageBox.information(None, "", f"[U2]初始化控制实例初始化完毕", QMessageBox.StandardButton.Ok)
                self.logger.info("U2控制实例初始化完毕")
            self.control_instance_ready = True
            self.config.set_config('控制模式', self.control_mode)
        except Exception as e:
            QMessageBox.warning(None, "", f"[{self.control_mode.name}]初始化控制实例出错，将启用[U2]方案", QMessageBox.StandardButton.Ok)
            self.logger.error(f"[%s]初始化控制实例出错，将启用[U2]方案", self.control_mode.name)
            try:
                self.control_mode = ControlMode.U2
                self.control_instance = U2(self.config)
                self.control_instance_ready = True
                self.config.set_config('控制模式', self.control_mode)
            except Exception as e:
                self.logger.error("初始化U2控制实例依旧出错")

    def switch_control_mode(self, new_mode: ControlMode):
        self.logger.info(f"即将切换控制模式：[{new_mode.name}]")
        if new_mode == self.control_mode:
            QMessageBox.information(None, "", f"已经是[{new_mode.name}]模式了", QMessageBox.StandardButton.Ok)
            self.logger.info(f"已经是[{new_mode.name}]模式了")
            return
        self.control_mode = new_mode
        self.control_instance_ready = False
        self.release()
        # 再初始化新的实例
        self.init_control_instance()

    def release(self):
        # 先把原先的控制实例释放掉
        self.control_instance.release()
        self.logger.debug(f"[{self.control_mode.name}]实例已清除")

    def click(self, x, y):
        if self.control_instance_ready:
            self.control_instance.click(x, y)
            return True
        else:
            self.logger.warning("控制实例未初始化或切换未完成")
            return False

    def swipe(self, start_coordinate, end_coordinate, duration=0.5):
        if self.control_instance_ready:
            self.control_instance.swipe(start_coordinate, end_coordinate, duration=duration)
            return True
        else:
            self.logger.warning("控制实例未初始化或切换未完成")
            return False

    def app_stop(self, package_name):
        if self.control_instance_ready:
            self.control_instance.app_stop(package_name)
            return True
        else:
            self.logger.warning("控制实例未初始化或切换未完成")
            return False

    def app_start(self, package_name):
        if self.control_instance_ready:
            self.control_instance.app_start(package_name)
            return True
        else:
            self.logger.warning("控制实例未初始化或切换未完成")
            return False

    def input(self, input_text):
        self.control_instance.input(input_text)

    def press(self, key):
        self.control_instance.press(key)
