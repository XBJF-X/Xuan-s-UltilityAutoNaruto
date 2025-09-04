import copy
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any

from StaticFunctions import get_real_path


class Config:
    def __init__(self, parent_logger, config_path):
        self.logger = parent_logger.getChild(self.__class__.__name__)
        self.config_path: Path = config_path
        self.default_config_path = get_real_path("src/DefaultConfig.json")

        self.setting_dics: Dict[str, Any] = {}
        self.tasks: Dict[str, Any] = {}
        self.load_and_merge_config()  # 改为合并加载方法
        self.save_config_to_file()  # 初始化后立即保存合并后的配置
        self.logger.debug(f"初始化完成...")

    def get_config(self, key: str, empty=None) -> Any:
        return self.setting_dics.get(key, empty)

    def set_config(self, key: str, value: Any):
        self.setting_dics[key] = value
        self.logger.debug(f"设置 {key} 为 {value}")
        self.save_config_to_file()

    def get_task_config(self, task_name: str, key: str):
        return self.tasks.get(task_name, {}).get(key, None)

    def set_task_config(self, task_name: str, key: str, value: Any):
        if task_name not in self.tasks:
            self.logger.warning(f"不存在[{task_name}]的配置信息")
            return
        task = self.tasks[task_name]
        if key not in task:
            self.logger.warning(f"[{task_name}]不存在配置项 {key}")
            return
        task[key] = value
        self.logger.debug(f"设置[{task_name}] {key} 为 {value}")
        self.save_config_to_file()

    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        try:
            with open(self.default_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载默认配置失败: {str(e)}")
            # 如果默认配置文件加载失败，返回内置的最小默认配置
            return {
                "调试模式": 1,
                "控制模式": 1,
                "任务": {}
            }

    def _merge_configs(self, user_config: Dict[str, Any], default_config: Dict[str, Any]) -> Dict[
        str, Any]:
        """递归合并配置：用户配置覆盖默认配置，缺失项用默认配置补充"""
        merged = copy.deepcopy(default_config)
        for key, value in user_config.items():
            if key == "任务":  # 特殊处理"任务"字典
                if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                    # 对每个任务进行特殊合并
                    merged_tasks = {}
                    for task_name, task_config in value.items():
                        # 如果默认配置中存在同名任务
                        if task_name in merged[key]:
                            default_task = merged[key][task_name]
                            # 递归合并任务配置，确保用户配置中缺失的键从默认配置继承
                            merged_task = self._merge_configs(task_config, default_task)
                            # 强制同步特定字段（如果需要覆盖递归合并的结果）
                            merged_task["任务ID"] = default_task["任务ID"]
                            merged_task["任务名称"] = default_task["任务名称"]
                            merged_tasks[task_name] = merged_task
                        else:
                            # 默认配置中不存在的任务，直接使用用户配置
                            merged_tasks[task_name] = task_config
                    # 添加默认配置中存在但用户配置中不存在的任务
                    for task_name, task_config in merged[key].items():
                        if task_name not in merged_tasks:
                            merged_tasks[task_name] = task_config
                    merged[key] = merged_tasks
                else:
                    # 如果默认配置中没有"任务"键或不是字典，则使用用户配置
                    merged[key] = value
            elif isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                # 递归合并其他字典
                merged[key] = self._merge_configs(value, merged[key])
            else:
                # 非字典类型直接覆盖
                merged[key] = value
        return merged

    def load_and_merge_config(self):
        """加载用户配置并与默认配置合并"""
        # 确保配置目录存在
        config_dir = os.path.dirname(self.config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        # 加载默认配置
        default_config = self._load_default_config()

        # 加载用户配置（如果存在）
        user_config = {}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                self.logger.info(f"成功加载用户配置文件: {self.config_path}")
            except Exception as e:
                self.logger.error(f"加载用户配置失败，将使用默认配置: {str(e)}")
                user_config = {}

        # 合并配置
        self.setting_dics = self._merge_configs(user_config, default_config)
        self.tasks = self.setting_dics.get("任务", {})
        self.logger.info("配置合并完成")

    def save_config_to_file(self):
        try:
            config_data = copy.deepcopy(self.setting_dics)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
            self.logger.debug(f"配置已保存到 {self.config_path}")
        except Exception as e:
            self.logger.error(f"保存配置失败: {str(e)}")
