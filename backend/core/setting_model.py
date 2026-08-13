"""设置管理模型 - 从 utils/Base/Setting.py 迁移，剥离 StaticFunctions 依赖"""
import configparser
import logging
import os
from pathlib import Path
from typing import Any, Optional

from backend.utils import get_real_path


class Setting:
    def __init__(self, parent_logger, setting_path: Path):
        if isinstance(parent_logger, str):
            self.logger = logging.getLogger(self.__class__.__name__)
        else:
            self.logger = parent_logger.getChild(self.__class__.__name__)
        self.setting_path = setting_path
        self.default_setting_path = Path(get_real_path("src/DefaultSetting.ini"))
        self.config = self._new_parser()
        self.load_and_merge_config()
        self._normalize_legacy_keys()
        self.save_to_file()
        self.logger.debug("初始化完成...")

    # 历史遗留 key 别名：旧版 configparser 会把 MuMu安装路径 小写化为 mumu安装路径
    _LEGACY_ALIASES = {"mumu安装路径": "MuMu安装路径"}

    def _normalize_legacy_keys(self):
        """迁移历史遗留的小写 option key 为标准 key（一次性）"""
        for section in self.config.sections():
            for old_key, new_key in self._LEGACY_ALIASES.items():
                has_old = self.config.has_option(section, old_key)
                has_new = self.config.has_option(section, new_key)
                if has_old and not has_new:
                    self.config.set(section, new_key, self.config.get(section, old_key))
                    self.config.remove_option(section, old_key)
                    self.logger.info(f"迁移历史遗留配置键 [{section}] {old_key} -> {new_key}")
                elif has_old and has_new:
                    # 已有新键时删除冗余的小写键
                    self.config.remove_option(section, old_key)

    @staticmethod
    def _new_parser() -> "configparser.ConfigParser":
        """创建保留 option 原始大小写的 ConfigParser（configparser 默认会把 option key 小写化，
        导致 MuMu安装路径 被存成 mumu安装路径）"""
        parser = configparser.ConfigParser()
        parser.optionxform = str  # type: ignore[assignment]
        return parser

    def get(self, section: str, key: str, default: Optional[Any] = None) -> Any:
        if self.config.has_section(section) and self.config.has_option(section, key):
            return self.config.get(section, key)
        self.logger.warning(f"配置项 [{section}] {key} 不存在，返回默认值 {default}")
        return default

    def getint(self, section: str, key: str, default: int = 0) -> int:
        try:
            return self.config.getint(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            self.logger.warning(f"整数配置项 [{section}] {key} 不存在，返回默认值 {default}")
            return default

    def getboolean(self, section: str, key: str, default: bool = False) -> bool:
        try:
            return self.config.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            self.logger.warning(f"布尔配置项 [{section}] {key} 不存在，返回默认值 {default}")
            return default

    def set(self, section: str, key: str, value: Any):
        if not self.config.has_section(section):
            self.config.add_section(section)
            self.logger.debug(f"新增配置节: [{section}]")
        self.config.set(section, key, str(value))
        self.logger.debug(f"设置 [{section}] {key} 为 {value}")
        self.save_to_file()

    def _load_default_config(self) -> configparser.ConfigParser:
        default_config = self._new_parser()
        try:
            if default_config.read(self.default_setting_path, encoding='utf-8'):
                self.logger.info(f"成功加载默认配置: {self.default_setting_path}")
            else:
                self.logger.error(f"默认配置文件不存在: {self.default_setting_path}")
        except Exception as e:
            self.logger.error(f"加载默认配置失败: {str(e)}")
        return default_config

    def _load_user_config(self) -> configparser.ConfigParser:
        user_config = self._new_parser()
        if os.path.exists(self.setting_path):
            try:
                if user_config.read(self.setting_path, encoding='utf-8'):
                    self.logger.info(f"成功加载用户配置: {self.setting_path}")
                else:
                    self.logger.warning(f"用户配置文件为空: {self.setting_path}")
            except Exception as e:
                self.logger.error(f"加载用户配置失败: {str(e)}")
        return user_config

    def _merge_configs(self, user_config: configparser.ConfigParser, default_config: configparser.ConfigParser) -> configparser.ConfigParser:
        """合并：仅保留 DefaultSetting.ini 中定义的 section/key。

        用户 setting.ini 的值覆盖默认值；DefaultSetting 中不存在而用户文件里
        多余的段/键一律剔除（用于清理迁移后的旧配置残留，如已废弃的 [Update] 段）。
        """
        merged = self._new_parser()

        for section in default_config.sections():
            merged.add_section(section)
            for key, value in default_config.items(section):
                merged.set(section, key, value)

        # 用户覆盖仅对默认存在的键生效；默认中不存在的 section/key 不进入 merged
        for section in default_config.sections():
            if user_config.has_section(section):
                for key in default_config.options(section):
                    if user_config.has_option(section, key):
                        merged.set(section, key, user_config.get(section, key))

        return merged

    def load_and_merge_config(self):
        config_dir = os.path.dirname(self.setting_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        default_config = self._load_default_config()
        user_config = self._load_user_config()
        self.config = self._merge_configs(user_config, default_config)
        self.logger.info(f"设置加载并合并完成，共 {len(self.config.sections())} 个节")

    def save_to_file(self):
        try:
            config_dir = os.path.dirname(self.setting_path)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            with open(self.setting_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
            self.logger.debug(f"设置已保存到 {self.setting_path}")
        except Exception as e:
            self.logger.error(f"保存设置失败: {str(e)}")

    def sections(self):
        return self.config.sections()

    def items(self, section: str):
        if self.config.has_section(section):
            return self.config.items(section)
        return []
