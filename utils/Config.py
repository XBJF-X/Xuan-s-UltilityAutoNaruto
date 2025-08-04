import copy
import json
import logging
import os
from typing import Dict, Any

from StaticFunctions import get_real_path


class Config:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config_path = get_real_path("config/Config.json")

        # 移除所有threading.Lock相关代码
        self.setting_dics: Dict[str, Any] = {}
        self.tasks: Dict[str, Any] = {}
        # 加载配置
        self._load_config()
        self.logger.debug(f"初始化完成...")

    def get_config(self, key: str, empty=None) -> Any:
        return self.setting_dics.get(key, empty)

    def set_config(self, key: str, value: Any):
        self.setting_dics[key] = value
        self.logger.debug(f"设置 {key} 为 {value}")
        self._save_config_to_file()

    def get_task_config(self, task_name: str, key: str):
        return self.tasks.get(task_name, {}).get(key, None)

    def set_task_config(self, task_name: str, key: str, value: Any):
        task = self.tasks.get(task_name, {})
        if task == {}:
            self.logger.warning(f"不存在[{task_name}]的配置信息")
            return
        if key not in task:
            self.logger.warning(f"不存在[{task_name}]的配置信息")
            return
        task[key] = value
        self.logger.debug(f"设置[{task_name}] {key} 为 {value}")
        self._save_config_to_file()

    def _load_config(self):
        """加载配置文件，不存在则创建"""
        # 确保配置目录存在
        config_dir = os.path.dirname(self.config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        # 如果配置文件不存在，创建默认配置
        if not os.path.exists(self.config_path):
            self.logger.error(f"不存在 {self.config_path} 配置文件")
            return False

        # 读取配置文件并更新设置
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.setting_dics = json.load(f)
                self.tasks = self.setting_dics.get("任务")

            self.logger.info(f"成功加载配置文件: {self.config_path}")
            return True

        except Exception as e:
            self.logger.error(f"加载配置文件失败: {str(e)}")
            return False

    def _save_config_to_file(self):
        try:
            config_data = copy.deepcopy(self.setting_dics)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.logger.error(f"保存配置失败: {str(e)}")
