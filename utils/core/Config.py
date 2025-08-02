import json
import logging
import os
from typing import Dict, Any

from StaticFunctions import get_real_path


class Config:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config_path = get_real_path("config/Config.json")

        # 不需要更新到本地config文件的设置项
        self.temp_keys = []

        # 移除所有threading.Lock相关代码
        self.setting_dics: Dict[str, Any] = {
            "串口": "127.0.0.1:5555",
            "控制模式": 0,
            "截图模式": 1,
            "查找窗口": ['Qt5156QWindowIcon', 'LDPlayerMainFrame'],
            "默认分辨率": "1600x900",
            "默认分辨率_元组": [1600, 900],
            "默认截图间隔": 50,

            "视频流帧率": 30,
            "调试模式": 0,

            # MuMu模拟器截图实例可能用到的参数
            "MuMu安装路径": r"D:\Program Files (x86)\MuMuPlayer-12.0",
            "MuMu实例索引": 1,
            "MuMu操作应用包名": "com.tencent.KiHan",

            # 雷电模拟器截图实例可能用到的参数
            "雷电安装路径": r"D:\Program Files (x86)\leidian\LDPlayer9",
            "雷电实例索引": 0,
        }
        # 加载配置
        self._load_config()
        self.logger.debug(f"初始化完成...")

    def get_config(self, key: str) -> Any:
        return self.setting_dics.get(key, None)

    def set_config(self, key: str, value: Any):
        self.setting_dics[key] = value
        self.logger.debug(f"设置 {key} 为 {value}")
        if key not in self.temp_keys:
            self._save_config_to_file()

    def _load_config(self):
        """加载配置文件，不存在则创建"""
        # 确保配置目录存在
        config_dir = os.path.dirname(self.config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        # 如果配置文件不存在，创建默认配置
        if not os.path.exists(self.config_path):
            # 提取需要持久化的配置项（排除临时键）
            default_config = self.setting_dics.copy()
            # 保存默认配置到文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=4)
            self.logger.info(f"创建默认配置文件: {self.config_path}")

        # 读取配置文件并更新设置
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # 遍历所有设置项
            for key, value in self.setting_dics.items():
                # 跳过临时键（不需要从配置文件加载）
                if key in self.temp_keys:
                    continue
                # 如果配置文件中有此键，更新内存中的值
                if key in config_data.keys():
                    # 保留原始数据类型
                    if isinstance(value, int):
                        self.setting_dics[key] = int(config_data[key])
                    elif isinstance(value, float):
                        self.setting_dics[key] = float(config_data[key])
                    elif isinstance(value, bool):
                        # 处理布尔值（JSON保存为bool，但可能被读取为int）
                        if isinstance(config_data[key], bool):
                            self.setting_dics[key] = config_data[key]
                        else:
                            self.setting_dics[key] = bool(int(config_data[key]))
                    else:
                        self.setting_dics[key] = config_data[key]

            self.logger.info(f"成功加载配置文件: {self.config_path}")

        except Exception as e:
            self.logger.error(f"加载配置文件失败: {str(e)}")

    def _save_config_to_file(self):
        try:
            config_data = {
                k: self.setting_dics[k]
                for k in self.setting_dics
                if k not in self.temp_keys
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.logger.error(f"保存配置失败: {str(e)}")
