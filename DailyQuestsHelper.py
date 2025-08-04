import sys

import ctypes
import json
import logging
import os
from collections import defaultdict
from datetime import datetime
from typing import Dict
from zoneinfo import ZoneInfo

import cv2
import numpy as np
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QApplication, QWidget, QFileDialog

from StaticFunctions import resource_path, get_real_path
from ui.DailyQuestsHelper_ui import Ui_DailyQuestsHelper
from utils.Base.Recognizer import Recognizer
from utils.Config import Config
from utils.Device import Device
from utils.KeyMapConfiguration import KeyMapConfiguration
from utils.Logger import LogWindow
from utils.Scheduler import Scheduler
from utils.Task import TREE_INDEX_DIC, TASK_NAME_CN2EN_MAP


class DailyQuestsHelper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.UI = Ui_DailyQuestsHelper()
        self.UI.setupUi(self)
        self.config = Config()
        self.log_window = LogWindow(self.config)
        self.logger = logging.getLogger("日常助手")
        self.init_environment()
        self.task_common_control_ref_map: Dict[str:Dict[str:QWidget]] = defaultdict(dict)  # 任务控制控件
        self.alloc_ui_ref_map()
        self.connect_ui2function()
        self.scene_templates = self.preprocess_templates("src/SceneInfo.json")
        self.element_templates = self.preprocess_templates("src/ElementInfo.json")
        self.recognizer = Recognizer(self.scene_templates, self.element_templates)
        self.scheduler = Scheduler(self.UI, self.recognizer, self.config, self.task_common_control_ref_map)

        self.logger.info("初始化完成...")

    def init_environment(self):
        """初始化环境设置"""
        if sys.platform == 'win32':
            os.environ["PYTHONUTF8"] = "on"
            os.environ["PYTHONLEGACYWINDOWSFSENCODING"] = "1"
            os.environ["QT_LOGGING_RULES"] = "qt.qpa.fonts.warning=false"
            # 仅在DPI感知成功设置时执行
            try:
                # 使用兼容性更好的旧版API
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception as e:
                print(f"设置DPI感知失败: {e}")

        # 移除冲突的环境变量
        os.environ.pop("QT_AUTO_SCREEN_SCALE_FACTOR", None)
        os.environ.pop("QT_SCALE_FACTOR", None)
        os.environ.pop("QT_SCREEN_SCALE_FACTORS", None)
        os.environ.pop("QT_ENABLE_HIGHDPI_SCALING", None)
        os.environ.pop("QT_DEVICE_PIXEL_RATIO", None)
        os.environ.pop("QT_DPI_OVERRIDE", None)
        os.environ.pop("QT_FONT_DPI", None)

        cv2.ocl.setUseOpenCL(True)
        self.setWindowIcon(QIcon(resource_path("src/ASDS.ico")))
        self.resize(1400, 800)
        app.aboutToQuit.connect(self._on_about_to_quit)
        # self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def _on_about_to_quit(self):
        self.scheduler.timer_thread.stop()
        self.scheduler.stop()
        self.logger.debug("日常助手退出")

    def alloc_ui_ref_map(self):
        # 日志窗口设置
        layout = QVBoxLayout(self.UI.logs_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.log_window)
        # 确保首页为总览面板
        self.UI.stackedWidget.setCurrentIndex(0)
        # 加载日常助手设置项
        self.UI.bool_debug.setChecked(self.config.get_config('调试模式', 0))
        self.UI.control_mode.setCurrentIndex(self.config.get_config('控制模式', 0))
        self.UI.serial.setText(self.config.get_config('串口', "127.0.0.1:5555"))
        self.UI.screen_mode.setCurrentIndex(self.config.get_config('截图模式', 0))
        self.UI.screen_mode_settings_stackedWidget.setCurrentIndex(self.config.get_config('截图模式', 0))
        self.UI.resolution.setCurrentIndex(self.config.get_config('模拟器分辨率', 0))
        self.UI.video_fps.setValue(self.config.get_config('视频流帧率', 60))
        self.UI.LD_install_path.setText(self.config.get_config('雷电安装路径', ""))
        self.UI.LD_instance_index.setValue(self.config.get_config('雷电实例索引', 0))
        self.UI.MuMu_install_path.setText(self.config.get_config('MuMu安装路径', ""))
        self.UI.MuMu_instance_index.setValue(self.config.get_config('MuMu实例索引', 0))
        self.UI.scan_inerval.setValue(self.config.get_config('扫描间隔', 1000))
        self.UI.secondary_password.setText(self.config.get_config('二级密码', ""))
        # 加载各种任务设置项
        self.process_common_task_settings_control()
        self.UI.XiaoDuiTuXi_4rewards_Enable.setChecked(self.config.get_task_config("小队突袭", "四倍奖励勾选"))
        self.UI.XiaoDuiTuXi_4rewards_times.setValue(self.config.get_task_config("小队突袭", "四倍奖励次数"))
        self.UI.JinBiZhaoCai_times.setValue(self.config.get_task_config("金币招财", "招财次数"))
        self.UI.GouMaiTiLi_times.setValue(self.config.get_task_config("购买体力", "购买体力次数"))

    def connect_ui2function(self):
        self.UI.start_schedule_button.clicked.connect(self._on_start_schedule_button_clicked)
        self.UI.overview_panel_button.clicked.connect(lambda _: self.UI.stackedWidget.setCurrentIndex(0))
        self.UI.treeWidget.itemClicked.connect(self._on_tree_item_clicked)
        self.UI.bool_debug.toggled.connect(self._on_bool_debug_toggled)
        self.UI.screen_mode.currentIndexChanged.connect(self._on_screen_mode_change)
        self.UI.control_mode.currentIndexChanged.connect(self._on_control_mode_change)
        self.UI.serial.editingFinished.connect(lambda w=self.UI.secondary_password: self.config.set_config("串口", w.text()))
        self.UI.resolution.currentIndexChanged.connect(self._on_resolution_change)
        self.UI.video_fps.valueChanged.connect(lambda index: self.config.set_config('视频流帧率', index))
        self.UI.LD_install_path.editingFinished.connect(lambda path: self.config.set_config('雷电安装路径', path))
        self.UI.LD_install_path_browse.clicked.connect(lambda: self._on_filepath_browse_clicked("雷电"))
        self.UI.LD_instance_index.valueChanged.connect(lambda index: self.config.set_config('雷电实例索引', index))
        self.UI.MuMu_install_path.editingFinished.connect(lambda path: self.config.set_config('MuMu安装路径', path))
        self.UI.MuMu_install_path_browse.clicked.connect(lambda: self._on_filepath_browse_clicked("MuMu"))
        self.UI.MuMu_instance_index.valueChanged.connect(lambda index: self.config.set_config('MuMu实例索引', index))
        self.UI.scan_inerval.valueChanged.connect(lambda index: self.config.set_config('扫描间隔', index))
        self.UI.secondary_password.editingFinished.connect(lambda w=self.UI.secondary_password: self.config.set_config("二级密码", w.text()))
        self.UI.key_map_configuration_button.clicked.connect(self._on_key_map_configuration_button_clicked)

    def process_common_task_settings_control(self):
        # 处理所有任务相关的通用设置控件的响应
        all_widgets = self.findChildren(QWidget)
        for widget in all_widgets:
            # 尝试一些没有text()方法的控件（如布局管理器等）
            if not hasattr(widget, 'text'):
                continue

            try:
                # 获取控件文本
                widget_name = widget.objectName()
                for key, value in TASK_NAME_CN2EN_MAP.items():
                    if f"{value}_Enable" == widget_name:
                        self.task_common_control_ref_map[key]["CheckBox"] = widget
                        widget.setChecked(self.config.get_task_config(key, "是否启用"))
                        widget.toggled.connect(lambda state, task_name=key: self.scheduler.toggle_task_activation(state, task_name))
                        break
                    elif f"{value}_next_execute_time" == widget_name:
                        self.task_common_control_ref_map[key]["LineEdit"] = widget
                        widget.setText(
                            datetime.fromtimestamp(
                                self.config.get_task_config(key, "下次执行时间"),
                                tz=ZoneInfo("Asia/Shanghai")
                            ).strftime("%Y-%m-%d %H:%M:%S"))
                        widget.editingFinished.connect(
                            lambda task_name=key: self.scheduler.task_next_execute_time_editfinished(task_name)
                        )
                        break
            except Exception as e:
                # 某些控件的text()方法可能有特殊实现，跳过异常
                self.logger.warning(e)
                continue

    def preprocess_templates(self, info_path) -> Dict:
        """预处理模板图像"""
        # self.logger.debug("预处理模版图像：")
        templates_dic = {}
        with open(get_real_path(info_path), "r", encoding='utf-8') as f:
            templates = json.load(f)

        for key, template in templates.items():
            try:
                gray_path = get_real_path(os.path.join(template['path'], "Gray", f"{key}.png"))
                alpha_path = get_real_path(os.path.join(template['path'], "Alpha", f"{key}.png"))
                # self.logger.debug("模板路径：%s", template_path)
                with open(gray_path, 'rb') as f:
                    gray_array = np.frombuffer(f.read(), dtype=np.uint8)
                    gray = cv2.imdecode(gray_array, cv2.IMREAD_GRAYSCALE)
                    if gray is None:
                        raise FileNotFoundError(f"文件存在但无法读取: {gray_path}")
                    template['GRAY'] = gray.astype(np.uint8)
                with open(alpha_path, 'rb') as f:
                    alpha_array = np.frombuffer(f.read(), dtype=np.uint8)
                    alpha = cv2.imdecode(alpha_array, cv2.IMREAD_GRAYSCALE)
                    if alpha is None:
                        raise FileNotFoundError(f"文件存在但无法读取: {alpha_path}")
                    template['MASK'] = alpha.astype(np.uint8)

                templates_dic[key] = template
            except Exception as e:
                self.logger.error("模板预处理失败: %s", f"{template['path']}{key}.png")
        return templates_dic

    def _on_start_schedule_button_clicked(self):
        if not self.scheduler.running:
            self.scheduler.start()
        else:
            self.scheduler.stop()

    def _on_tree_item_clicked(self, item, column):
        text = item.text(column)
        if TREE_INDEX_DIC.get(text, 0):
            self.UI.stackedWidget.setCurrentIndex(TREE_INDEX_DIC[text])

    def _on_bool_debug_toggled(self, flag):
        self.log_window.log_level = logging.DEBUG if flag else logging.INFO
        self.logger.debug(f"日志窗口显示等级已经调为[{"DEBUG" if flag else "INFO"}]")
        self.config.set_config('调试模式', int(flag))

    def _on_screen_mode_change(self, index):
        self.UI.screen_mode_settings_stackedWidget.setCurrentIndex(index)
        self.config.set_config("截图模式", index)

    def _on_control_mode_change(self, index):
        self.config.set_config("控制模式", index)

    def _on_resolution_change(self, index):
        self.config.set_config("模拟器分辨率", index)

    def _on_key_map_configuration_button_clicked(self):
        if self.scheduler.device is not None:
            device = self.scheduler.device
        else:
            device = Device(self.config, self.recognizer)
        editor = KeyMapConfiguration(self.config, device.screen_cap(), self)
        editor.exec()
        device = None

    def _on_filepath_browse_clicked(self, name):
        folder = QFileDialog.getExistingDirectory(self, f"选择{name}模拟器安装目录")
        if folder:
            if name == "MuMu":
                self.UI.MuMu_install_path.setText(folder)
                self.config.set_config("MuMu安装路径", folder)
            elif name == "雷电":
                self.UI.LD_install_path.setText(folder)
                self.config.set_config("雷电安装路径", folder)


if __name__ == "__main__":
    # 1. 首先设置DPI感知 - 使用兼容性更好的旧版API
    if sys.platform == 'win32':
        try:
            # 使用兼容性更好的旧版API
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception as e:
            print(f"设置DPI感知失败: {e}")

    # 2. 创建应用实例前设置高DPI策略
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

    # 3. 创建应用实例
    app = QApplication(sys.argv)

    # 4. 设置高DPI缩放策略（可选）
    # 在PySide6 6.4+版本中，这步可能不需要
    # app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    daily_quests_helper = DailyQuestsHelper()
    daily_quests_helper.show()
    sys.exit(app.exec())
