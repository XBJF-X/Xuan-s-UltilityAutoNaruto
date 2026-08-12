"""配置管理模型 - 从 utils/Base/Config.py 迁移，剥离 PySide6 依赖"""
import copy
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any

from backend.utils import get_real_path


class Config:
    def __init__(self, parent_logger, config_path):
        if isinstance(parent_logger, str):
            self.logger = logging.getLogger(self.__class__.__name__)
        else:
            self.logger = parent_logger.getChild(self.__class__.__name__)
        self.config_path: Path = config_path
        self.default_config_path = get_real_path("src/DefaultConfig.json")
        self.setting_dics: Dict[str, Any] = {}
        self.tasks: Dict[str, Any] = {}
        self.load_and_merge_config()
        self.save_config_to_file()
        self.logger.debug("初始化完成...")

    @property
    def config_type(self) -> str:
        """配置类型：持久（账号配置，跟踪进度）/ 临时（任务预设，只执行一遍不保存进度）"""
        return self.setting_dics.get("配置类型", "持久")

    # 安装路径相关键已迁移至 setting.ini [助手设置] 段
    _PATH_KEYS = ("MuMu安装路径", "雷电安装路径")

    def get_config(self, key: str, empty=None) -> Any:
        if empty is None:
            empty = {}
        if key in self._PATH_KEYS:
            value = self.setting_dics.get(key)
            if value in (None, ""):
                # JSON 中为空时兜底读取 setting.ini [助手设置]
                try:
                    from backend.services.settings_service import SettingsService
                    fallback = SettingsService().get("助手设置", key)
                    if fallback:
                        return fallback
                except Exception as e:
                    self.logger.warning(f"读取 setting.ini 中 {key} 失败: {e}")
        return self.setting_dics.get(key, empty)

    def set_config(self, key: str, value: Any):
        self.setting_dics[key] = value
        if key in self._PATH_KEYS:
            # 安装路径已迁移至 setting.ini [助手设置]，保存时同步写入
            try:
                from backend.services.settings_service import SettingsService
                SettingsService().set("助手设置", key, value)
            except Exception as e:
                self.logger.warning(f"写入 setting.ini 中 {key} 失败: {e}")
        self.logger.debug(f"设置 {key} 为 {value}")
        self.save_config_to_file()

    def get_task_config(self, task_name: str):
        """获取任务所有的属性"""
        return self.tasks.get(task_name, {})

    def get_task_base_config(self, task_name: str, key: str, empty=None):
        """获取任务共有的属性"""
        return self.tasks.get(task_name, {}).get(key, empty)

    def get_task_exe_param(self, task_name: str, key: str, empty=None):
        """获取任务的执行参数"""
        return self.tasks.get(task_name, {}).get("执行参数", {}).get(key, {}).get("当前值", empty)

    def get_task_exe_prog(self, task_name: str, key: str, empty=None):
        """获取任务的执行进度"""
        return self.tasks.get(task_name, {}).get("执行进度", {}).get(key, empty)

    def set_task_base_config(self, task_name: str, key: str, value: Any):
        if task_name not in self.tasks:
            self.logger.warning(f"不存在[{task_name}]的配置信息")
            return
        task = self.tasks[task_name]
        if key not in task:
            self.logger.warning(f"[{task_name}]不存在配置 {key}")
            return
        task[key] = value
        self.logger.debug(f"设置[{task_name}] {key} 为 {value}")
        self.save_config_to_file()

    def set_task_exe_param(self, task_name: str, key: str, value: Any):
        if task_name not in self.tasks:
            self.logger.warning(f"不存在[{task_name}]的执行参数信息")
            return
        task = self.tasks[task_name]
        if key not in task["执行参数"]:
            self.logger.warning(f"[{task_name}]不存在执行参数 {key}")
            return
        task["执行参数"][key]["当前值"] = value
        self.logger.debug(f"设置[{task_name}] {key} 为 {value}")
        self.save_config_to_file()

    def set_task_exe_prog(self, task_name: str, key: str, value: Any):
        if task_name not in self.tasks:
            self.logger.warning(f"不存在[{task_name}]的执行进度信息")
            return
        task = self.tasks[task_name]
        if key not in task["执行进度"]:
            self.logger.warning(f"[{task_name}]不存在执行进度 {key}")
            return
        task["执行进度"][key] = value
        self.logger.debug(f"设置[{task_name}] {key} 为 {value}")
        self.save_config_to_file()

    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        try:
            with open(self.default_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载默认配置失败: {str(e)}")
            return {
                "配置文件版本": "V3",
                "调试模式": 1,
                "控制模式": 1,
                "任务": {}
            }

    def _merge_v3_configs(self, user_config: Dict[str, Any], default_config: Dict[str, Any]) -> Dict[str, Any]:
        """递归合并V3配置：用户配置覆盖默认配置，缺失项用默认配置补充"""
        merged = copy.deepcopy(default_config)

        for key, value in user_config.items():
            if key != "任务":
                if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                    merged[key] = self._merge_v3_configs(value, merged[key])
                else:
                    merged[key] = value

        if "任务" in user_config and "任务" in merged:
            user_tasks = user_config["任务"]
            default_tasks = merged["任务"]

            for task_name, user_task in user_tasks.items():
                if task_name in default_tasks:
                    default_task = default_tasks[task_name]
                    merged_task = copy.deepcopy(default_task)

                    if "是否启用" in user_task:
                        merged_task["是否启用"] = user_task["是否启用"]
                    if "下次执行时间" in user_task:
                        merged_task["下次执行时间"] = user_task["下次执行时间"]

                    if "执行参数" in user_task and "执行参数" in default_task:
                        for param_key, param_value in user_task["执行参数"].items():
                            if param_key in default_task["执行参数"]:
                                if "当前值" in param_value:
                                    merged_task["执行参数"][param_key]["当前值"] = param_value["当前值"]

                    if "执行进度" in user_task and "执行进度" in default_task:
                        for progress_key, progress_value in user_task["执行进度"].items():
                            if progress_key in default_task["执行进度"]:
                                merged_task["执行进度"][progress_key] = progress_value

                    default_tasks[task_name] = merged_task

        return merged

    def load_and_merge_config(self):
        """加载用户配置并与默认配置合并"""
        config_dir = os.path.dirname(self.config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        default_config = self._load_default_config()

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                self.logger.info(f"成功加载用户配置文件: {self.config_path}")

                if user_config.get("配置文件版本", None) == "V3":
                    self.setting_dics = self._merge_v3_configs(user_config, default_config)
                else:
                    self.logger.error("旧版本配置文件已不兼容，请删除旧版本配置文件并创建新配置文件")
                    return
            except Exception as e:
                self.logger.error(f"加载用户配置失败，将使用默认配置: {str(e)}")
        else:
            self.setting_dics = default_config

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
