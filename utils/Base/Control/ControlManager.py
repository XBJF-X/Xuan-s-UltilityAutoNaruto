import logging
from typing import Any

from PySide6.QtWidgets import QMessageBox

from utils.Base.Config import Config
from utils.Base.Control import Control, ControlMode
from utils.Base.Control.MiniTouch import MiniTouch
from utils.Base.Control.U2 import U2


class ControlManager:
    """
    控制实例管理器
    负责：实例初始化、模式切换、统一调用控制接口
    """

    def __init__(self, config: Config, parent_logger=None):
        self.logger = parent_logger.getChild(self.__class__.__name__) if parent_logger else logging.getLogger(self.__class__.__name__)
        self.config = config
        self.control_mode = ControlMode(self.config.get_config('控制模式'))
        self.current_control: Control | Any = self.create_control_instance()

    def __del__(self):
        """析构函数：自动释放资源"""
        self.release()

    @property
    def ready(self):
        """统一的就绪判断（对外接口）"""
        return (self.current_control is not None) and self.current_control.ready

    def create_control_instance(self):
        """初始化控制实例"""
        self.logger.info(f"当前控制模式：[{self.control_mode.name}]")
        try:
            # 根据模式创建对应子类
            if self.control_mode == ControlMode.U2:
                control = U2(self.config, self.logger)
            elif self.control_mode == ControlMode.MiniTouch:
                control = MiniTouch(self.config, self.logger)
            else:
                control = U2(self.config, self.logger)

            # 初始化提示
            if control.ready:
                self.logger.info(f"[{self.control_mode.name}]控制实例初始化完成")
            self.config.set_config('控制模式', self.control_mode.value)
            return control

        except Exception as e:
            QMessageBox.warning(
                None, "", f"【{self.control_mode.name}】 初始化失败\n\n{e}\n\n请检查方案参数配置或尝试其他方案",
                QMessageBox.StandardButton.Ok
            )
            return None

    def switch_control_mode(self, new_mode: ControlMode):
        """切换控制模式（核心方法）"""
        self.logger.info(f"即将切换控制模式：[{new_mode.name}]")
        if new_mode == self.control_mode:
            QMessageBox.information(None, "", f"已经是[{new_mode.name}]模式", QMessageBox.StandardButton.Ok)
            return

        # 释放旧实例 → 创建新实例
        self.control_mode = new_mode
        self.release()
        self.current_control = self.create_control_instance()

    def release(self):
        """释放当前实例"""
        if self.current_control:
            self.current_control.release()
            self.current_control = None
            self.logger.debug("当前控制实例已释放")

    # ------------------- 统一对外控制接口 -------------------
    def click(self, x, y) -> bool:
        if not self.ready:
            self.logger.warning("控制实例未就绪")
            return False
        self.current_control.click(x, y)
        return True

    def swipe(self, start_coordinate, end_coordinate, duration=0.5) -> bool:
        if not self.ready:
            self.logger.warning("控制实例未就绪")
            return False
        self.current_control.swipe(start_coordinate, end_coordinate, duration)
        return True

    def app_stop(self, package_name) -> bool:
        if not self.ready:
            return False
        self.current_control.app_stop(package_name)
        return True

    def app_start(self, package_name) -> bool:
        if not self.ready:
            return False
        self.current_control.app_start(package_name)
        return True

    def current_app(self):
        return self.current_control.current_app() if self.ready else None

    def input(self, input_text):
        if self.ready:
            self.current_control.input(input_text)

    def press_key(self, key):
        if self.ready:
            self.current_control.press_key(key)

    def touch_down(self, x, y):
        if self.ready:
            self.current_control.touch_down(x, y)

    def touch_up(self, x, y):
        if self.ready:
            self.current_control.touch_up(x, y)

    def long_press(self, x, y, duration):
        if self.ready:
            self.current_control.long_press(x, y, duration)

    @property
    def rotated(self):
        if self.ready:
            return self.current_control.rotated
