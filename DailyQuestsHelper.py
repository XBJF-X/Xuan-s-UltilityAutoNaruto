import logging
import os
import sys
import cv2
import win32gui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout

from ui.DailyQuestsHelper import Ui_DailyQuestsHelper
from StaticFunctions import resource_path
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

        cv2.ocl.setUseOpenCL(True)

        self.setWindowIcon(QIcon(resource_path("src/ASDS.ico")))
        # self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

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
    from PyQt5.QtWidgets import QApplication

    # 创建应用
    app = QApplication(sys.argv)
    # 设置应用样式
    app.setStyle("Fusion")
    daily_quests_helper = DailyQuestsHelper()
    daily_quests_helper.show()
    sys.exit(app.exec_())
