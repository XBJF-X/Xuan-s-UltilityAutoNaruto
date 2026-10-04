import abc
import logging
from enum import IntEnum
from typing import Any, Dict, Optional, Tuple

from backend.core.legacy.Config import Config


class ControlMode(IntEnum):
    """控制模式枚举。

    .. deprecated:: U2 已弃用
        ``U2`` 不再作为可选控制方案（见 ``DEPRECATED_CONTROL_MODES``）。
        保留枚举成员仅为兼容存量配置里的数值 ``1``，读取时一律经由
        :meth:`from_config` 归一化路由到 ``MiniTouch``。
    """
    MiniTouch = 0
    U2 = 1


DEPRECATED_CONTROL_MODES = frozenset({ControlMode.U2})
"""已弃用的控制模式：这些模式的配置值会被路由到 :attr:`ControlMode.MiniTouch`。"""


def _mode_name(mode) -> str:
    """取枚举/整数的可读名称，供日志使用。"""
    return getattr(mode, "name", None) or str(mode)


def resolve_control_mode(raw: Any, logger: Optional[logging.Logger] = None) -> "ControlMode":
    """把配置里的「控制模式」值归一化为当前可用的控制模式。

    规则（U2 弃用后的统一入口）：

    1. ``0`` / MiniTouch → MiniTouch；
    2. ``1`` / U2 → **MiniTouch**（存量配置的旧值，静默路由，只记一次 info）；
    3. 其余非法值 / 缺失（``None``、空串、非数字）→ MiniTouch（控制模式只有一个可用项，
       不能再像以前那样静默退回 U2）。

    调用方不要直接 ``ControlMode(config.get_config('控制模式'))``——那样会在存量
    配置上重建出已弃用的 U2 实例。
    """
    mode: Optional[ControlMode] = None
    if isinstance(raw, ControlMode):
        mode = raw
    elif isinstance(raw, bool):
        # bool 是 int 的子类，但 True/False 不是合法的模式值
        mode = None
    elif isinstance(raw, int):
        try:
            mode = ControlMode(raw)
        except ValueError:
            mode = None
    elif isinstance(raw, str):
        text = raw.strip()
        if text:
            try:
                mode = ControlMode(int(text))
            except (ValueError, TypeError):
                mode = None

    if mode is not None and mode not in DEPRECATED_CONTROL_MODES:
        return mode

    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return ControlMode.MiniTouch

    # 弃用值或非法值：路由到 MiniTouch（只记一次，避免每次建实例都刷日志）
    # 注意：raw 可能是 list/dict 等不可哈希值，先归一化成可哈希的键再判断
    try:
        warn_key = ("value", raw)
        hash(warn_key)
    except TypeError:
        warn_key = ("repr", repr(raw))
    resolve_control_mode._warned = getattr(resolve_control_mode, "_warned", set())
    if warn_key not in resolve_control_mode._warned:
        resolve_control_mode._warned.add(warn_key)
        target = logger or logging.getLogger(__name__)
        if mode in DEPRECATED_CONTROL_MODES:
            target.info(
                f"控制模式 [{_mode_name(mode)}]({int(mode)}) 已弃用，"
                f"自动路由到 [{ControlMode.MiniTouch.name}]")
        else:
            target.warning(
                f"控制模式取值非法({raw!r})，回退到 [{ControlMode.MiniTouch.name}]")
    return ControlMode.MiniTouch


class InvalidResolution(Exception):
    pass


class Control(abc.ABC):
    """
    控制模块抽象基类
    """

    def __init__(self, config: Config, parent_logger=None):
        self.config = config
        self.logger = parent_logger.getChild(self.__class__.__name__) if parent_logger else logging.getLogger(self.__class__.__name__)
        self._ready = False  # 实例就绪状态

    @property
    def ready(self):
        """统一的就绪状态判断（子类重写）"""
        return self._ready

    @property
    @abc.abstractmethod
    def screen_size(self) -> Tuple[int, int]:
        """获取屏幕尺寸"""
        pass

    @abc.abstractmethod
    def get_device_info(self):
        """获取硬件信息"""
        pass

    @abc.abstractmethod
    def check_resolution(self)->bool:
        """获取硬件信息"""
        pass

    # ------------------- 抽象方法（子类必须实现）-------------------

    @abc.abstractmethod
    def release(self):
        """释放资源"""
        pass

    @abc.abstractmethod
    def click(self, x, y):
        """点击"""
        pass

    @abc.abstractmethod
    def swipe(self, start_coordinate, end_coordinate, duration=0.5):
        """滑动"""
        pass

    @abc.abstractmethod
    def app_stop(self, package_name):
        """停止应用"""
        pass

    @abc.abstractmethod
    def app_start(self, package_name):
        """启动应用"""
        pass

    @abc.abstractmethod
    def current_app(self)->Dict[str,Any]:
        """获取当前应用"""
        pass

    @abc.abstractmethod
    def input(self, input_text):
        """输入文字"""
        pass

    @abc.abstractmethod
    def press_key(self, key):
        """按键"""
        pass

    @abc.abstractmethod
    def touch_down(self, x, y):
        """按下"""
        pass

    @abc.abstractmethod
    def touch_up(self, x, y):
        """抬起"""
        pass

    @abc.abstractmethod
    def long_press(self, x, y, duration):
        """长按"""
        pass

    @property
    @abc.abstractmethod
    def rotated(self)-> int:
        """是否旋转"""
        pass
