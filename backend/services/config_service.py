"""配置管理服务 - 封装 Config 类（模块级单例）"""
import copy
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.utils import get_real_path
from backend.core.config_model import Config


class ConfigService:
    """管理多个配置实例"""

    def __init__(self, config_dir: str | None = None):
        self.logger = logging.getLogger("ConfigService")
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path(get_real_path("config"))
        self.config_dir.mkdir(exist_ok=True)
        self._instances: Dict[str, Config] = {}
        self._default_config_path = Path(get_real_path("src/DefaultConfig.json"))

    def _config_path(self, name: str) -> Path:
        return self.config_dir / f"{name}.json"

    def list_configs(self) -> List[dict]:
        results = []
        for item in sorted(self.config_dir.iterdir()):
            if item.is_file() and item.suffix.lower() == ".json" and item.name != "DefaultConfig.json":
                try:
                    cfg = self._load_or_create(item.stem)
                    results.append({
                        "id": item.stem,
                        "username": cfg.get_config("用户名", item.stem),
                        "path": str(item),
                        "config_type": cfg.config_type,
                    })
                except Exception as e:
                    self.logger.warning(f"加载配置 {item.name} 失败: {e}")
        return results

    def _load_or_create(self, config_id: str) -> Config:
        if config_id not in self._instances:
            cfg_path = self._config_path(config_id)
            self._instances[config_id] = Config(
                parent_logger=self.logger,
                config_path=cfg_path,
            )
        return self._instances[config_id]

    def get_config(self, config_id: str) -> Optional[Config]:
        try:
            return self._load_or_create(config_id)
        except Exception as e:
            self.logger.error(f"获取配置 {config_id} 失败: {e}")
            return None

    def get_config_full(self, config_id: str) -> Optional[dict]:
        cfg = self.get_config(config_id)
        if not cfg:
            return None
        # 安装路径键在 config JSON 中可能为空（已迁移至 setting.ini [助手设置]），
        # 用 get_config 兜底读取实际生效值，供前端展示与判断（避免误报"未设置"）
        setting_dics = copy.deepcopy(cfg.setting_dics)
        for key in ("MuMu安装路径", "雷电安装路径"):
            value = cfg.get_config(key)
            if value:
                setting_dics[key] = value
        return {
            "id": config_id,
            "config_type": cfg.config_type,
            "setting_dics": setting_dics,
            "tasks": cfg.tasks,
            "username": cfg.get_config("用户名", config_id),
        }

    def get_task_schema(self) -> dict:
        try:
            with open(self._default_config_path, "r", encoding="utf-8") as f:
                return json.load(f).get("任务", {})
        except Exception:
            return {}

    def set_config_value(self, config_id: str, key: str, value: Any) -> bool:
        cfg = self.get_config(config_id)
        if not cfg:
            return False
        cfg.set_config(key, value)
        return True

    def set_task_base(self, config_id: str, task_name: str, key: str, value: Any) -> bool:
        cfg = self.get_config(config_id)
        if not cfg:
            return False
        cfg.set_task_base_config(task_name, key, value)
        return True

    def set_task_exe_param(self, config_id: str, task_name: str, key: str, value: Any) -> bool:
        cfg = self.get_config(config_id)
        if not cfg:
            return False
        cfg.set_task_exe_param(task_name, key, value)
        return True

    def create_config(self, username: str, config_type: str = "持久") -> Optional[str]:
        existing = []
        for item in self.config_dir.iterdir():
            if item.is_file() and item.suffix.lower() == ".json":
                name = item.stem
                if name.startswith("Config_"):
                    num_str = name.split("_")[1]
                else:
                    num_str = name
                if num_str.isdigit():
                    existing.append(int(num_str))
        x = 1
        while x in existing:
            x += 1
        config_id = f"Config_{x}"
        cfg_path = self._config_path(config_id)
        try:
            with open(self._default_config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception:
            config_data = {"配置文件版本": "V3", "用户名": username, "任务": {}}
        config_data["用户名"] = username
        config_data["配置类型"] = config_type
        if config_type == "临时":
            # 任务预设：默认所有任务不启用、执行顺序为空，由前端勾选并拖拽排序后写入
            config_data["任务执行顺序"] = []
            for task in config_data.get("任务", {}).values():
                task["是否启用"] = False
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        self._instances[config_id] = Config(parent_logger=self.logger, config_path=cfg_path)
        return config_id

    def duplicate_config(self, config_id: str) -> Optional[str]:
        """复制配置：用户名加 _副本 后缀，其余（配置类型/任务勾选/执行参数/执行顺序）全部照抄"""
        cfg_path = self._config_path(config_id)
        if not cfg_path.exists():
            return None
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.logger.error(f"读取源配置 {config_id} 失败: {e}")
            return None

        # 生成不重名的副本配置 id（Config_N_副本 / Config_N_副本2 / ...）
        existing = set()
        for item in self.config_dir.iterdir():
            if item.is_file() and item.suffix.lower() == ".json":
                existing.add(item.stem)
        new_id = f"{config_id}_副本"
        n = 2
        while new_id in existing:
            new_id = f"{config_id}_副本{n}"
            n += 1

        username = str(data.get("用户名") or config_id)
        data["用户名"] = f"{username}_副本"
        new_path = self._config_path(new_id)
        try:
            with open(new_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"写入副本配置失败: {e}")
            return None
        self._instances[new_id] = Config(parent_logger=self.logger, config_path=new_path)
        self.logger.info(f"已复制配置 {config_id} → {new_id}")
        return new_id

    def set_task_priorities(self, config_id: str, ordered_task_names: list[str]) -> bool:
        """按传入顺序设置任务优先级（存储任务名列表到配置中）"""
        cfg = self.get_config(config_id)
        if not cfg:
            return False
        cfg.setting_dics["任务优先级顺序"] = ordered_task_names
        cfg.save_config_to_file()
        self.logger.debug(f"已更新配置 {config_id} 的任务优先级顺序: {ordered_task_names}")
        return True

    def get_task_priorities(self, config_id: str) -> list[str]:
        """获取任务优先级顺序列表"""
        cfg = self.get_config(config_id)
        if not cfg:
            return []
        return cfg.setting_dics.get("任务优先级顺序", [])

    def set_task_order(self, config_id: str, ordered_task_names: list[str]) -> bool:
        """按顺序保存任务执行顺序（临时预设使用）"""
        cfg = self.get_config(config_id)
        if not cfg:
            return False
        cfg.setting_dics["任务执行顺序"] = ordered_task_names
        cfg.save_config_to_file()
        self.logger.debug(f"已更新配置 {config_id} 的任务执行顺序: {ordered_task_names}")
        return True

    def get_task_order(self, config_id: str) -> list[str]:
        """获取任务执行顺序列表"""
        cfg = self.get_config(config_id)
        if not cfg:
            return []
        return cfg.setting_dics.get("任务执行顺序", [])

    def rename_config(self, config_id: str, new_username: str) -> bool:
        cfg = self.get_config(config_id)
        if not cfg:
            return False
        cfg.set_config("用户名", new_username)
        return True

    def delete_config(self, config_id: str) -> bool:
        cfg_path = self._config_path(config_id)
        if cfg_path.exists():
            cfg_path.unlink()
        self._instances.pop(config_id, None)
        return True


# ===== 模块级单例 =====
# 所有 API 模块共享同一个 ConfigService 实例，确保 Config 对象在内存中唯一
shared_config_service = ConfigService()