import configparser
import os
from pathlib import Path
from typing import Any, Optional

from StaticFunctions import get_real_path


class Setting:
    def __init__(self, parent_logger, setting_path: Path):
        self.logger = parent_logger.getChild(self.__class__.__name__)
        self.setting_path = setting_path
        self.default_setting_path = Path(get_real_path("src/DefaultSetting.ini"))
        self.config = configparser.ConfigParser()  # 存储合并后的配置
        self.load_and_merge_config()
        self.save_to_file()  # 初始化后立即保存合并后的配置
        self.logger.debug("初始化完成...")

    def get(self, section: str, key: str, default: Optional[Any] = None) -> Any:
        """获取配置项，不存在时返回默认值"""
        if self.config.has_section(section) and self.config.has_option(section, key):
            return self.config.get(section, key)
        self.logger.warning(f"配置项 [{section}] {key} 不存在，返回默认值 {default}")
        return default

    def getint(self, section: str, key: str, default: int = 0) -> int:
        """获取整数类型配置项"""
        try:
            return self.config.getint(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            self.logger.warning(f"整数配置项 [{section}] {key} 不存在，返回默认值 {default}")
            return default

    def getboolean(self, section: str, key: str, default: bool = False) -> bool:
        """获取布尔类型配置项"""
        try:
            return self.config.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            self.logger.warning(f"布尔配置项 [{section}] {key} 不存在，返回默认值 {default}")
            return default

    def set(self, section: str, key: str, value: Any):
        """设置配置项，实时保存到文件"""
        if not self.config.has_section(section):
            self.config.add_section(section)
            self.logger.debug(f"新增配置节: [{section}]")
        self.config.set(section, key, str(value))  # ini格式值均以字符串存储
        self.logger.debug(f"设置 [{section}] {key} 为 {value}")
        self.save_to_file()

    def _load_default_config(self) -> configparser.ConfigParser:
        """加载默认配置文件"""
        default_config = configparser.ConfigParser()
        try:
            if default_config.read(self.default_setting_path, encoding='utf-8'):
                self.logger.info(f"成功加载默认配置: {self.default_setting_path}")
            else:
                self.logger.error(f"默认配置文件不存在: {self.default_setting_path}")
        except Exception as e:
            self.logger.error(f"加载默认配置失败: {str(e)}")
        return default_config

    def _load_user_config(self) -> configparser.ConfigParser:
        """加载用户配置文件"""
        user_config = configparser.ConfigParser()
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
        """合并配置：用户配置覆盖默认配置，缺失项补充默认值"""
        # 以默认配置为基础
        merged = configparser.ConfigParser()

        # 复制默认配置的所有节和键值对
        for section in default_config.sections():
            merged.add_section(section)
            for key, value in default_config.items(section):
                merged.set(section, key, value)

        # 合并用户配置（覆盖默认值）
        for section in user_config.sections():
            # 若用户配置包含新节，添加到合并结果
            if not merged.has_section(section):
                merged.add_section(section)
            # 覆盖已有键值对
            for key, value in user_config.items(section):
                merged.set(section, key, value)

        return merged

    def load_and_merge_config(self):
        """加载并合并默认配置与用户配置"""
        # 确保配置目录存在
        config_dir = os.path.dirname(self.setting_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        # 加载默认配置和用户配置
        default_config = self._load_default_config()
        user_config = self._load_user_config()

        # 合并配置
        self.config = self._merge_configs(user_config, default_config)
        self.logger.info("配置合并完成")

    def save_to_file(self):
        """保存当前配置到用户文件"""
        try:
            with open(self.setting_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
            self.logger.debug(f"配置已保存到: {self.setting_path}")
        except Exception as e:
            self.logger.error(f"保存配置失败: {str(e)}")