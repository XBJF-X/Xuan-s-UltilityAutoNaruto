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
        # logger 名必须包含 Config_N（如 ConfigService.Config_1），
        # 供 WebSocketLogHandler 按 config_id 归类到前端对应配置
        config_id = config_path.stem
        if isinstance(parent_logger, str):
            self.logger = logging.getLogger(f"{self.__class__.__name__}.{config_id}")
        else:
            self.logger = parent_logger.getChild(config_id)
        self.config_path: Path = config_path
        self.default_config_path = get_real_path("src/DefaultConfig.json")
        self.setting_dics: Dict[str, Any] = {}
        self.tasks: Dict[str, Any] = {}
        self.load_and_merge_config()
        self.save_config_to_file()
        self._attach_config_log_handler()
        self.logger.debug("初始化完成...")

    def _attach_config_log_handler(self):
        """为 Config 挂载 config 专属文件 handler + WebSocket handler，并切断向 root 的传播。

        配置对象的日志（加载/保存/设置参数等）应归入该配置专属日志
        （log/<用户名>/<日期>/Xuan.log），而非写入 Main.log。
        logger 名含 Config_N（parent_logger.getChild(config_id)），
        供 WebSocketLogHandler 按 config_id 归类。
        """
        from backend.log_setup import get_config_file_handler
        from backend.api.ws import get_ws_log_handler

        username = self.setting_dics.get("用户名") or "unknown"
        file_handler = get_config_file_handler(username)
        if file_handler not in self.logger.handlers:
            self.logger.addHandler(file_handler)
        ws_handler = get_ws_log_handler()
        if ws_handler not in self.logger.handlers:
            self.logger.addHandler(ws_handler)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

    @property
    def config_type(self) -> str:
        """配置类型：持久（账号配置，跟踪进度）/ 临时（任务预设，只执行一遍不保存进度）"""
        return self.setting_dics.get("配置类型", "持久")

    # 安装路径相关键已迁移至 setting.ini [助手设置] 段
    _PATH_KEYS = ("MuMu安装路径", "雷电安装路径")
    # 全局布尔键：已迁移至 setting.ini [助手设置]，全局生效（不按配置隔离）
    _GLOBAL_BOOL_KEYS = ("错误自动截图",)

    def get_config(self, key: str, empty=None) -> Any:
        if empty is None:
            empty = {}
        if key in self._GLOBAL_BOOL_KEYS:
            # 全局键统一从 setting.ini [助手设置] 读取，不读 config JSON
            try:
                from backend.services.settings_service import SettingsService
                return SettingsService().getboolean("助手设置", key, default=bool(empty))
            except Exception as e:
                self.logger.warning(f"读取 setting.ini 中 {key} 失败: {e}")
                return empty
        if key in self._PATH_KEYS:
            # 安装路径只从 setting.ini [助手设置] 读取，不读 config JSON
            # （参数迁移后旧 JSON 参数不再支持，避免残留旧路径覆盖设置中的新路径）
            try:
                from backend.services.settings_service import SettingsService
                value = SettingsService().get("助手设置", key)
                return value if value else empty
            except Exception as e:
                self.logger.warning(f"读取 setting.ini 中 {key} 失败: {e}")
                return empty
        return self.setting_dics.get(key, empty)

    def set_config(self, key: str, value: Any):
        if key in self._GLOBAL_BOOL_KEYS:
            # 全局布尔键：只写 setting.ini，不落 config JSON
            try:
                from backend.services.settings_service import SettingsService
                SettingsService().set("助手设置", key, bool(value))
            except Exception as e:
                self.logger.warning(f"写入 setting.ini 中 {key} 失败: {e}")
            self.logger.debug(f"设置全局 {key} 为 {bool(value)}")
            return
        if key in self._PATH_KEYS:
            # 安装路径只写 setting.ini [助手设置]，不落 config JSON
            try:
                from backend.services.settings_service import SettingsService
                SettingsService().set("助手设置", key, value)
            except Exception as e:
                self.logger.warning(f"写入 setting.ini 中 {key} 失败: {e}")
            self.logger.debug(f"设置全局 {key} 为 {value}")
            return
        self.setting_dics[key] = value
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
                self.logger.debug(f"成功加载用户配置文件: {self.config_path}")

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
        # 安装路径键已迁移至 setting.ini [助手设置]，从内存/JSON 移除，
        # 避免旧 JSON 残留参数回写或经 setting_dics 被其他消费方读到
        for key in self._PATH_KEYS:
            self.setting_dics.pop(key, None)
        self.logger.debug("配置合并完成")

    def save_config_to_file(self):
        try:
            config_data = copy.deepcopy(self.setting_dics)
            new_content = json.dumps(config_data, ensure_ascii=False, indent=4)
            # 免写盘：内容与磁盘一致时不写文件，避免每次加载配置都触发磁盘 I/O
            if self.config_path.exists():
                try:
                    with open(self.config_path, 'r', encoding='utf-8') as f:
                        if f.read() == new_content:
                            return
                except Exception:
                    pass
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        except Exception as e:
            self.logger.error(f"保存配置失败: {str(e)}")
