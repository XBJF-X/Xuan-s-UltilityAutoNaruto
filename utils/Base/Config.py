import copy
import json
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
        if empty is None:
            empty = {}
        return self.setting_dics.get(key, empty)

    def set_config(self, key: str, value: Any):
        self.setting_dics[key] = value
        self.logger.debug(f"设置 {key} 为 {value}")
        self.save_config_to_file()

    def get_task_config(self, task_name: str):
        return self.tasks.get(task_name, {})

    def get_task_base_config(self, task_name: str, key: str, empty=None):
        return self.tasks.get(task_name, {}).get(key, empty)

    def get_task_exe_param(self, task_name: str, key: str, empty=None):
        return self.tasks.get(task_name, {}).get("执行参数", {}).get(key, {}).get("当前值", empty)

    def get_task_exe_prog(self, task_name: str, key: str, empty=None):
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
            # 如果默认配置文件加载失败，返回内置的最小默认配置
            return {
                "配置文件版本": "V3",
                "调试模式": 1,
                "控制模式": 1,
                "任务": {}
            }

    def _merge_v3_configs(self, user_config: Dict[str, Any], default_config: Dict[str, Any]) -> Dict[
        str, Any]:
        """递归合并V3配置：用户配置覆盖默认配置，缺失项用默认配置补充"""
        merged = copy.deepcopy(default_config)

        # 首先合并非任务部分
        for key, value in user_config.items():
            if key != "任务":  # 任务部分单独处理
                if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                    # 递归合并其他字典
                    merged[key] = self._merge_v3_configs(value, merged[key])
                else:
                    # 非字典类型直接覆盖
                    merged[key] = value

        # 处理任务部分
        if "任务" in user_config and "任务" in merged:
            user_tasks = user_config["任务"]
            default_tasks = merged["任务"]

            # 对每个任务进行合并
            for task_name, user_task in user_tasks.items():
                if task_name in default_tasks:
                    default_task = default_tasks[task_name]
                    merged_task = copy.deepcopy(default_task)

                    # 只从用户配置中读取特定字段
                    if "是否启用" in user_task:
                        merged_task["是否启用"] = user_task["是否启用"]
                    if "下次执行时间" in user_task:
                        merged_task["下次执行时间"] = user_task["下次执行时间"]

                    # 合并执行参数 - 只从用户配置中读取"当前值"
                    if "执行参数" in user_task and "执行参数" in default_task:
                        for param_key, param_value in user_task["执行参数"].items():
                            if param_key in default_task["执行参数"]:
                                # 只更新当前值，其他属性保持默认配置
                                if "当前值" in param_value:
                                    merged_task["执行参数"][param_key]["当前值"] = param_value["当前值"]

                    # 合并执行进度 - 完全使用用户配置
                    if "执行进度" in user_task and "执行进度" in default_task:
                        for progress_key, progress_value in user_task["执行进度"].items():
                            if progress_key in default_task["执行进度"]:
                                merged_task["执行进度"][progress_key] = progress_value

                    default_tasks[task_name] = merged_task

            # 添加用户配置中没有但默认配置中存在的任务
            for task_name, default_task in default_tasks.items():
                if task_name not in user_tasks:
                    # 保留默认配置中的任务
                    pass

        return merged

    def load_and_merge_config(self):
        """加载用户配置并与默认配置合并"""
        # 确保配置目录存在
        config_dir = os.path.dirname(self.config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        # 加载默认配置
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