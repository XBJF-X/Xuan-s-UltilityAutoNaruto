import ctypes
import json
import logging
import os
import sys
from typing import Dict

import cv2
import numpy as np
import win32gui

from PySide6.QtCore import Qt, QFile, QTextStream
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QApplication

from ui.DailyQuestsHelper_ui import Ui_DailyQuestsHelper
from StaticFunctions import resource_path, get_real_path
from utils.core.Base.Recognizer import Recognizer
from utils.core.Device import Device
from utils.core.Logger import LogWindow
from utils.core.Scheduler import Scheduler
from utils.core.Config import Config
from utils.core.Task import TREE_INDEX_DIC


class DailyQuestsHelper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.UI = Ui_DailyQuestsHelper()
        self.UI.setupUi(self)
        self.config = Config()
        self.log_window = LogWindow(self.config)
        self.logger = logging.getLogger("日常助手")
        self.init_environment()
        self.alloc_ui_ref_map()
        self.connect_ui2function()
        self.scene_templates = self.preprocess_templates("src/SceneInfo.json")
        self.element_templates = self.preprocess_templates("src/ElementInfo.json")
        self.recognizer = Recognizer(self.scene_templates, self.element_templates)
        self.device = Device(self.config, self.recognizer)
        self.scheduler = Scheduler(self.UI, self.device, self.config)

        self.logger.debug("初始化完成...")

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
        self.resize(1400, 600)
        # self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def alloc_ui_ref_map(self):
        # 假设你在 UI 文件中有一个 QWidget 用于放置日志窗口，这里命名为 logs_container
        layout = QVBoxLayout(self.UI.logs_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.log_window)
        self.UI.stackedWidget.setCurrentIndex(0)

    def connect_ui2function(self):
        self.UI.start_schedule_button.clicked.connect(self._on_start_schedule_button_clicked)
        self.UI.overview_panel_button.clicked.connect(lambda _: self.UI.stackedWidget.setCurrentIndex(0))
        self.UI.treeWidget.itemClicked.connect(self._on_tree_item_clicked)

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
            self.scheduler.running = True
            self.scheduler.timer_thread.trigger(1000)
            self.UI.start_schedule_button.setText("暂停")
            self.logger.debug("[调度器]已启动")
        else:
            self.scheduler.running = False
            self.scheduler.timer_thread.trigger(1000)
            self.UI.start_schedule_button.setText("启动")
            self.logger.debug("[调度器]已暂停")

    def _on_tree_item_clicked(self, item, column):
        text = item.text(column)
        if TREE_INDEX_DIC.get(text, 0):
            self.UI.stackedWidget.setCurrentIndex(TREE_INDEX_DIC[text])


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
