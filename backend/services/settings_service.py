"""设置管理服务 - 封装 Setting 类（纯Python，无UI依赖）"""
import logging
from pathlib import Path
from typing import Any, Optional

from StaticFunctions import get_real_path
from utils.Base.Setting import Setting


class SettingsService:
    def __init__(self):
        self.logger = logging.getLogger("SettingsService")
        self._setting: Optional[Setting] = None

    def _get_setting(self) -> Setting:
        if self._setting is None:
            self._setting = Setting(
                parent_logger=self.logger,
                setting_path=Path(get_real_path("setting.ini")),
            )
        return self._setting

    def get(self, section: str, key: str) -> str:
        return self._get_setting().get(section, key, "")

    def getint(self, section: str, key: str, default: int = 0) -> int:
        return self._get_setting().getint(section, key, default)

    def getboolean(self, section: str, key: str, default: bool = False) -> bool:
        return self._get_setting().getboolean(section, key, default)

    def set(self, section: str, key: str, value: Any):
        self._get_setting().set(section, key, value)

    def get_all(self) -> dict:
        """获取所有设置"""
        s = self._get_setting()
        result = {}
        for section in s.config.sections():
            result[section] = dict(s.config.items(section))
        return result