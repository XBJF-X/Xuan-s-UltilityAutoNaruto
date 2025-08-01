import ctypes
import logging
import os
import sys
import cv2
import win32gui

from PySide6.QtCore import Qt, QFile, QTextStream
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QApplication

from ui.DailyQuestsHelper_ui import Ui_DailyQuestsHelper
from StaticFunctions import resource_path, get_real_path
from utils.core.Controller import Controller
from utils.core.Logger import LogWindow
from utils.core.Scheduler import Scheduler
from utils.core.Config import Config


class DailyQuestsHelper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.UI = Ui_DailyQuestsHelper()
        self.UI.setupUi(self)
        self.config = Config()
        self.log_window = LogWindow(self.config)
        self.logger = logging.getLogger("日常助手")
        self.init_environment()
        # self.load_style_sheet()
        self.alloc_ui_ref_map()
        self.connect_ui2function()
        # self.controller = Controller(self.config, "127.0.0.1:16416")
        self.controller = Controller(self.config, "127.0.0.1:5555")
        self.scheduler = Scheduler(self.UI, self.controller, self.config)

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
        # self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def load_style_sheet(self):
        """加载全局QSS样式"""
        file = QFile(get_real_path("ui/Global.qss"))  # QSS文件路径
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            style_sheet = stream.readAll()
            QApplication.instance().setStyleSheet(style_sheet)  # 应用到整个应用
            file.close()
        else:
            print(f"无法加载QSS文件: {file.errorString()}")

    def alloc_ui_ref_map(self):
        # 假设你在 UI 文件中有一个 QWidget 用于放置日志窗口，这里命名为 logs_container
        layout = QVBoxLayout(self.UI.logs_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.log_window)

    def connect_ui2function(self):
        self.UI.start_schedule_button.clicked.connect(self._on_start_schedule_button_clicked)
        self.UI.overview_panel_button.clicked.connect(lambda _: self.UI.stackedWidget.setCurrentIndex(0))
        self.UI.treeWidget.itemClicked.connect(self._on_tree_item_clicked)

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
        tree_index_dic = {
            '日常助手设置': 1,
            '通用设置': 2,
            '每日日常': 3,
            '每周日常': 4,
            '活动': 5,
        }
        text = item.text(column)
        if tree_index_dic.get(text, 0):
            self.UI.stackedWidget.setCurrentIndex(tree_index_dic[text])


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