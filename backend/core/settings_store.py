"""设置存储（Setting 的进程级单例门面）—— 领域层基础设施

阶段 3.4 分层修正：改前本类位于 `backend/services/settings_service.py`，而
`core/config_model.py`（领域层）需要读 setting.ini 的路径键与全局开关，于是形成
`core → services` 反向依赖。现把实现搬到 core（`Setting` 本来就在
`core/setting_model.py`），`services/settings_service.py` 改为再导出以保持既有 API。

进程级单例：改前 `SettingsService()` 每次调用都会 `new Setting(...)`，而 `Setting.__init__`
会在构造期整文件重写 `setting.ini`（"一次读 = 一次全量重写"）。`api/utils` 一次
/check-update 就会 new 出 2~3 个实例 → 多余磁盘写；且多实例各持一份内存快照，并发
`set()` 会互相覆盖（用户改设置"看起来成功却被回滚"）。
现在：生产路径共用唯一实例；`Setting` 仅在磁盘内容与内存不一致时才写盘，写盘为
tmp + `os.replace` 原子替换（见 core/setting_model.py）。
"""
import logging
import threading
from pathlib import Path
from typing import Any, Optional

from backend.utils import get_real_path
from backend.core.setting_model import Setting

logger = logging.getLogger("SettingsService")

# 进程级唯一实例（首次使用时构造）
_SETTINGS: Optional[Setting] = None
_SETTINGS_LOCK = threading.Lock()


def get_settings(*, path: Optional[Path] = None, readonly: bool = False) -> Setting:
    """获取进程级唯一的 Setting 实例。

    `readonly=True` 供只读探测/单测使用（构造时不写盘）。
    """
    global _SETTINGS
    if _SETTINGS is None:
        with _SETTINGS_LOCK:
            if _SETTINGS is None:
                _SETTINGS = Setting(
                    parent_logger=logger,
                    setting_path=Path(path or get_real_path("setting.ini")),
                    readonly=readonly,
                )
    return _SETTINGS


def reset_settings_cache() -> None:
    """清空单例（测试用：切换 setting.ini 路径或模拟进程重启）"""
    global _SETTINGS
    with _SETTINGS_LOCK:
        _SETTINGS = None


class SettingsService:
    """全局设置门面（薄封装）。

    - 不传参数：走进程级单例（生产路径）；
    - 传 `setting`：完全注入（测试/替换）；
    - 传 `path`：使用该路径的独立实例（测试隔离，不污染单例）。
    """

    def __init__(self, setting: Optional[Setting] = None, *,
                 path: Optional[Path] = None, readonly: bool = False):
        self.logger = logging.getLogger("SettingsService")
        self._injected = setting
        self._path = path
        self._readonly = readonly
        self._local: Optional[Setting] = None

    def _get_setting(self) -> Setting:
        if self._injected is not None:
            return self._injected
        if self._path is not None:
            if self._local is None:
                self._local = Setting(
                    parent_logger=self.logger, setting_path=Path(self._path),
                    readonly=self._readonly,
                )
            return self._local
        return get_settings()

    def get(self, section: str, key: str) -> str:
        return self._get_setting().get(section, key, "")

    def getint(self, section: str, key: str, default: int = 0) -> int:
        return self._get_setting().getint(section, key, default)

    def getboolean(self, section: str, key: str, default: bool = False) -> bool:
        return self._get_setting().getboolean(section, key, default)

    def set(self, section: str, key: str, value: Any) -> bool:
        """写入设置并落盘，返回是否成功（旧实现无返回值，调用方无法感知失败）"""
        setting = self._get_setting()
        setting.set(section, key, value)
        return True

    def get_all(self) -> dict:
        """获取所有设置"""
        s = self._get_setting()
        result = {}
        for section in s.config.sections():
            result[section] = dict(s.config.items(section))
        return result
