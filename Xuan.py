import ctypes
import logging
import os
import sys
import webbrowser
from pathlib import Path
from typing import List

import cv2
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPainter, QBrush, QColor, QPainterPath
from PySide6.QtWidgets import QMainWindow, QApplication

from StaticFunctions import resource_path, get_real_path
from utils.Base.Scene.SceneGraph import SceneGraph
from utils.Base.Updater import Updater
from utils.Servicer import Service
from utils.ui.Xuan_ui import Ui_Xuan


class Xuan(QMainWindow):
    def __init__(self):
        super().__init__()

        self.UI = Ui_Xuan()
        self.UI.setupUi(self)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("初始化配置...")
        self.config_path = Path(get_real_path("config"))
        self.scene_graph = SceneGraph()
        self.logger.info("初始化环境...")
        self.mouse_position = None
        self.init_environment()
        self.services: List[Service] = []
        self.alloc_ui_ref_map()
        self.logger.info("初始化UI响应函数...")
        self.bind_signals()
        self.updater = Updater()
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
        # 临时把adb目录添加进环境目录
        os.environ['PATH'] = os.pathsep.join([get_real_path('bin/adb'), os.environ.get('PATH', '')])
        cv2.ocl.setUseOpenCL(True)
        self.setWindowIcon(QIcon(resource_path("src/ASDS.ico")))
        self.resize(1400, 800)
        app.aboutToQuit.connect(self._on_about_to_quit)
        # 设置窗口标志
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowIcon(QIcon(resource_path("src/ASDS.ico")))
        # self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def alloc_ui_ref_map(self):
        # 确保配置目录存在
        if not os.path.exists(self.config_path):
            os.makedirs(self.config_path)
            self.logger.debug(f"创建配置目录: {self.config_path}")

        # 遍历目录下所有文件，筛选出JSON文件并排除DefaultConfig.json
        config_files = []
        for item in Path(self.config_path).iterdir():
            # 检查是否为文件且后缀为.json，同时排除默认配置
            if item.is_file() and item.suffix.lower() == ".json" and item.name != "DefaultConfig.json":
                config_files.append(item)  # 添加Path类型的文件路径
        if len(config_files) != 0:
            for config_file in config_files:
                self.services.append(Service(
                    config_path=config_file,
                    scene_graph=self.scene_graph
                ))
        else:
            self.services.append(Service(
                config_path=Path(get_real_path("config/1.json")),
                scene_graph=self.scene_graph
            ))
        # 关键步骤：先清除ServiceStackedWidget中默认的空白page
        while self.UI.ServiceStackedWidget.count() > 0:
            # 移除并删除所有现有页面（避免内存泄漏）
            widget = self.UI.ServiceStackedWidget.widget(0)
            self.UI.ServiceStackedWidget.removeWidget(widget)
            widget.deleteLater()  # 彻底销毁控件
        # 关键步骤：将services按顺序添加到ServiceStackedWidget
        for service in self.services:
            self.UI.ServiceStackedWidget.addWidget(service)
        # 确保首页为总览面板
        self.UI.ServiceStackedWidget.setCurrentIndex(0)

    def bind_signals(self):
        self.UI.go_to_github_btn.clicked.connect(self._on_go_to_github_btn_clicked)
        self.UI.update_btn.clicked.connect(self._on_update_btn_clicked)
        self.UI.exit_btn.clicked.connect(QApplication.quit)
        self.UI.min_btn.clicked.connect(self.showMinimized)

    @staticmethod
    def _on_go_to_github_btn_clicked():
        webbrowser.open("https://github.com/XBJF-X/Xuan-s-UltilityAutoNaruto")

    def _on_update_btn_clicked(self):
        flag, new_version = self.updater.check_update()
        if flag:
            self.logger.info("检查到新版本！")
            self.updater.update(new_version)
        else:
            self.logger.debug("不存在新版本！")

    def _on_about_to_quit(self):
        for service in self.services:
            service.scheduler.timer_thread.stop()
            service.scheduler.stop()
        self.logger.debug("日常助手退出")

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 记录鼠标按下时的位置
            self.mouse_position = event.globalPosition().toPoint() - self.frameGeometry(
            ).topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.mouse_position is not None:
            # 计算新位置并移动窗口
            self.move(event.globalPosition().toPoint() - self.mouse_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 重置拖动位置
            self.mouse_position = None
            event.accept()

    def paintEvent(self, event):
        """重绘事件处理函数，绘制圆角窗口"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 启用抗锯齿

        # 创建圆角矩形路径
        path = QPainterPath()
        corner_radius = 10
        path.addRoundedRect(self.rect(), corner_radius, corner_radius)
        background_color = QColor(255, 255, 255)
        # 填充背景
        painter.fillPath(path, QBrush(background_color))


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

    daily_quests_helper = Xuan()
    daily_quests_helper.show()
    sys.exit(app.exec())
