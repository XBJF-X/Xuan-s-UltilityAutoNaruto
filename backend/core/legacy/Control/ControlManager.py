import logging
import threading
from typing import Any

from backend.core.legacy.Config import Config
from backend.core.legacy.Control import Control, ControlMode


class ControlManager:
    """
    控制实例管理器
    负责：实例初始化、模式切换、统一调用控制接口
    """

    def __init__(self, config: Config, parent_logger=None):
        self.logger = parent_logger.getChild(self.__class__.__name__) if parent_logger else logging.getLogger(self.__class__.__name__)
        self.config = config
        self.control_mode = ControlMode(self.config.get_config('控制模式'))
        self._control_lock = threading.RLock()
        self.current_control: Control | Any = self.create_control_instance()

    def __del__(self):
        """析构函数：自动释放资源"""
        self.release()

    @property
    def ready(self):
        """统一的就绪判断（对外接口）"""
        with self._control_lock:
            return (self.current_control is not None) and self.current_control.ready

    def create_control_instance(self):
        """初始化控制实例"""
        self.logger.info(f"当前控制模式：[{self.control_mode.name}]")
        try:
            # 根据模式创建对应子类（懒导入：避免未安装 minidevice 时阻塞调度器启动）
            if self.control_mode == ControlMode.U2:
                from backend.core.legacy.Control.U2 import U2
                control = U2(self.config, self.logger)
            else:
                # MiniTouch 模式：初始化失败时直接抛出，不降级到 U2——
                # 降级会导致"配置为 MiniTouch、实际实例为 U2"，Clicker 连点
                # 按配置走 MiniTouch 分支却拿到 U2 实例调用 multi_tap 崩溃刷屏；
                # 失败由上层 Device.device_ready / 调度器启动检测拦截，停止调度器。
                from backend.core.legacy.Control.MiniTouch import MiniTouch
                control = MiniTouch(self.config, self.logger)

            if control.ready:
                self.logger.info(f"[{self.control_mode.name}]控制实例初始化完成")
            self.config.set_config('控制模式', self.control_mode.value)
            return control

        except Exception as e:
            self.logger.error(f"【{self.control_mode.name}】 初始化失败: {e}")
            self.logger.error(
                "控制实例初始化失败，调度器将停止。请检查[助手设置]中的串口连接与模拟器状态。")
            return None

    def switch_control_mode(self, new_mode: ControlMode):
        """切换控制模式（核心方法）"""
        self.logger.info(f"即将切换控制模式：[{new_mode.name}]")
        if new_mode == self.control_mode:
            self.logger.info(f"已经是[{new_mode.name}]模式")
            return

        # 先创建新实例，再原子替换，避免 current_control 短暂为空
        old_mode = self.control_mode
        self.control_mode = new_mode
        new_control = self.create_control_instance()
        if new_control is None:
            self.control_mode = old_mode
            return

        with self._control_lock:
            old_control = self.current_control
            self.current_control = new_control

        self.config.set_config('控制模式', self.control_mode.value)
        if old_control:
            old_control.release()

    def release(self):
        """释放当前实例"""
        with self._control_lock:
            control = self.current_control
            self.current_control = None
        if control:
            control.release()
            self.logger.debug("当前控制实例已释放")

    def get_current_control(self):
        with self._control_lock:
            return self.current_control

    def replace_current_control(self, new_control: Control | Any):
        with self._control_lock:
            old_control = self.current_control
            self.current_control = new_control
            return old_control

    # ------------------- 统一对外控制接口 -------------------
    def click(self, x, y) -> bool:
        with self._control_lock:
            if not self.ready:
                self.logger.warning("控制实例未就绪")
                return False
            try:
                self.current_control.click(x, y)
                return True
            except Exception as e:
                self.logger.warning(f"控制点击失败: {e}")
                return False

    def swipe(self, start_coordinate, end_coordinate, duration=0.5) -> bool:
        with self._control_lock:
            if not self.ready:
                self.logger.warning("控制实例未就绪")
                return False
            try:
                self.current_control.swipe(start_coordinate, end_coordinate, duration)
                return True
            except Exception as e:
                self.logger.warning(f"控制滑动失败: {e}")
                return False

    def app_stop(self, package_name) -> bool:
        with self._control_lock:
            if not self.ready:
                return False
            self.current_control.app_stop(package_name)
            return True

    def app_start(self, package_name) -> bool:
        with self._control_lock:
            if not self.ready:
                return False
            self.current_control.app_start(package_name)
            return True

    def current_app(self):
        with self._control_lock:
            return self.current_control.current_app() if self.ready else None

    def input(self, input_text):
        with self._control_lock:
            if self.ready:
                self.current_control.input(input_text)

    def press_key(self, key):
        with self._control_lock:
            if self.ready:
                self.current_control.press_key(key)

    def touch_down(self, x, y):
        with self._control_lock:
            if self.ready:
                self.current_control.touch_down(x, y)

    def touch_up(self, x, y):
        with self._control_lock:
            if self.ready:
                self.current_control.touch_up(x, y)

    def long_press(self, x, y, duration):
        with self._control_lock:
            if self.ready:
                self.current_control.long_press(x, y, duration)

    @property
    def rotated(self):
        with self._control_lock:
            if self.ready:
                return self.current_control.rotated
