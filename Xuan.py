import ctypes
import json
import logging
import os
import sys
import webbrowser
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import List

import cv2
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPainter, QBrush, QColor, QPainterPath, QAction
from PySide6.QtWidgets import QMainWindow, QApplication, QPushButton, QDialog, QButtonGroup, QMessageBox, \
    QMenu

from StaticFunctions import resource_path, get_real_path
from tool.ResourceManager.ResourceDBManager import ResourceDBManager
from utils.AddConfig import AddConfig
from utils.Base.Scene.SceneGraph import SceneGraph
from utils.Base.Setting import Setting
from utils.ui.SettingDialog import SettingDialog
from utils.Base.Updater import Updater
from utils.Servicer import Service
from utils.ui.Xuan_ui import Ui_Xuan

# 使用样式表
button_style = """
QPushButton {
    border: 0px;
    outline: 0px;
    background-color: transparent;
    color: #000000;
    padding: 5px;
    margin-right:3px;
    margin-left:3px;
    text-align: left;
}

QPushButton:hover {
    border: 1px solid #39C5BB;
    color: #39C5BB;
    background-color: rgba(57, 197, 187, 0.1);
}

QPushButton:checked {
    border: 1px solid #39C5BB;
    color: #39C5BB;
}

QPushButton:pressed {
    border: 1px solid #39C5BB;
    color: #2AA79E;
}
"""


class Xuan(QMainWindow):
    def __init__(self):
        super().__init__()

        self.UI = Ui_Xuan()
        self.UI.setupUi(self)
        self.logger = self.setup_main_logger()
        self.logger.info("初始化配置...")
        self.config_path = Path(get_real_path("config"))
        self.setting = Setting(self.logger, Path(get_real_path("setting.ini")))
        self.scene_graph = SceneGraph(ResourceDBManager())
        self.logger.info("初始化环境...")
        self.mouse_position = None
        self.init_environment()
        self.services: List[Service] = []
        self.alloc_ui_ref_map()
        self.logger.info("初始化UI响应函数...")
        self.updater = Updater(parent_logger=self.logger)
        self.bind_signals()
        self.logger.info("初始化完成...")
        if self.setting.getboolean("Update", "自动更新"):
            self.logger.info("自动更新")
            self._on_update_btn_clicked()

    @staticmethod
    def setup_main_logger():
        """配置程序主日志"""
        main_logger = logging.getLogger("Main")
        main_logger.setLevel(logging.INFO)
        log_dir = Path(get_real_path("log"))
        log_dir.mkdir(exist_ok=True)

        # 主日志文件处理器
        main_handler = RotatingFileHandler(
            log_dir / "Main.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )

        formatter = logging.Formatter(
            '[%(levelname)s] %(name)s %(asctime)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        main_handler.setFormatter(formatter)
        main_logger.addHandler(main_handler)

        # 可选：控制台输出
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        main_logger.addHandler(console_handler)

        return main_logger

    def init_environment(self):
        """初始化环境设置"""
        self.setWindowIcon(QIcon(resource_path("src/ASDS.ico")))
        self.resize(1400, 600)
        app.aboutToQuit.connect(self._on_about_to_quit)
        # 设置窗口标志
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def alloc_ui_ref_map(self):
        self.UI.ServiceStackedWidget.setContentsMargins(0, 0, 0, 0)
        # 创建按钮组并设置互斥
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        # 确保配置目录存在
        if not os.path.exists(self.config_path):
            os.makedirs(self.config_path)
            self.logger.debug(f"创建配置目录: {self.config_path}")

        # 遍历目录下所有文件，筛选出JSON文件
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
                config_path=Path(get_real_path("config/Config_1.json")),
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

        # 生成配置切换按钮（核心逻辑）
        # 1. 获取容器布局
        container_layout = self.UI.config_switch_btn_container.layout()
        if not container_layout:
            self.logger.error("config_switch_btn_container未设置布局")
            return

        # 2. 先移除现有按钮（保留垂直弹簧和初始PushButton）
        # 遍历布局中的所有项目，记录弹簧的位置
        spring_item = None
        for i in range(container_layout.count()):
            item = container_layout.itemAt(i)
            widget = item.widget()
            # 判断是否为垂直弹簧（QSpacerItem）
            if not widget and item.spacerItem():
                spring_item = item

        # 4. 为每个service生成按钮，并插入到弹簧上方
        for idx, service in enumerate(self.services):
            # 按钮文本使用配置文件名（不含后缀）
            btn_text = service.config.get_config("用户名")  # 例如"Config_1"
            btn = QPushButton(btn_text)
            btn.setObjectName(f"config_switch_btn_{idx}")  # 设置唯一名称，便于调试
            btn.setStyleSheet(button_style)
            btn.setCheckable(True)
            # 绑定点击事件：切换到对应索引的page
            btn.clicked.connect(lambda checked, id=idx: self.UI.ServiceStackedWidget.setCurrentIndex(id))
            self.button_group.addButton(btn)
            # 插入到弹簧上方（弹簧在布局中的索引位置）
            if spring_item:
                spring_index = container_layout.indexOf(spring_item)
                container_layout.insertWidget(spring_index, btn)
            else:
                # 如果没有弹簧，直接添加到布局末尾
                container_layout.addWidget(btn)
        if self.services:  # 确保有服务存在
            first_btn = self.button_group.buttons()[0]
            first_btn.setChecked(True)
        # 确保首页为总览面板
        self.UI.ServiceStackedWidget.setCurrentIndex(0)

    def _create_menu(self):
        # 创建下拉菜单
        menu = QMenu(self)

        # 添加菜单选项
        update_action = QAction("更新", self)
        update_action.triggered.connect(self._on_update_btn_clicked)

        github_action = QAction("Github", self)
        github_action.triggered.connect(self._on_go_to_github_btn_clicked)

        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self._on_setting_btn_clicked)

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(QApplication.quit)

        # 将选项添加到菜单
        menu.addAction(update_action)
        menu.addSeparator()  # 添加分隔线
        menu.addAction(github_action)
        menu.addAction(settings_action)
        menu.addSeparator()  # 添加分隔线
        menu.addAction(exit_action)

        return menu

    def bind_signals(self):
        self.updater.update_message.connect(self.update_message)
        self.UI.menu_btn.setMenu(self._create_menu())

        self.UI.min_btn.clicked.connect(self.showMinimized)
        self.UI.add_config_btn.clicked.connect(self._on_add_config_btn_clicked)

    @staticmethod
    def _on_go_to_github_btn_clicked():
        webbrowser.open("https://github.com/XBJF-X/Xuan-s-UltilityAutoNaruto")

    def _on_setting_btn_clicked(self):
        dialog = SettingDialog(self, self.logger, self.setting)
        dialog.exec()

    def update_message(self, title, message):
        QMessageBox.information(self, title, message)

    def _on_update_btn_clicked(self):
        flag, new_version = self.updater.check_update()
        if flag:
            self.logger.info("检查到新版本！")
            self.updater.update(new_version)
        else:
            self.logger.debug("不存在新版本！")

    def _on_add_config_btn_clicked(self):
        self.logger.debug("新建用户配置窗口开启")
        dialog = AddConfig(parent=self)

        # 显示对话框并阻塞，直到用户关闭
        if dialog.exec() == QDialog.DialogCode.Accepted:
            username = dialog.get_username()
            if username:
                try:
                    # 1. 找到目录下不重复的最小数字x
                    config_dir = self.config_path
                    existing_numbers = []

                    # 遍历现有配置文件提取数字
                    for item in config_dir.iterdir():
                        if item.is_file() and item.suffix.lower() == ".json":
                            # 提取文件名中的数字部分（假设格式为 Config_x.json 或 x.json）
                            name = item.stem
                            if name.startswith("Config_"):
                                num_str = name.split("_")[1]
                            else:
                                num_str = name
                            if num_str.isdigit():
                                existing_numbers.append(int(num_str))

                    # 计算最小可用数字
                    x = 1
                    while x in existing_numbers:
                        x += 1

                    # 2. 创建新配置文件
                    new_config_name = f"Config_{x}.json"  # 生成文件名
                    new_config_path = config_dir / new_config_name

                    config_data = json.load(open(get_real_path("src/DefaultConfig.json"), encoding="utf-8"))
                    config_data["用户名"] = username

                    # 写入配置文件
                    with open(new_config_path, "w", encoding="utf-8") as f:
                        json.dump(config_data, f, ensure_ascii=False, indent=2)
                    self.logger.info(f"创建新配置文件: {new_config_path}")

                    # 3. 生成新的Service页面并添加到StackedWidget
                    new_service = Service(
                        config_path=new_config_path,
                        scene_graph=self.scene_graph
                    )
                    self.services.append(new_service)
                    self.UI.ServiceStackedWidget.addWidget(new_service)

                    # 4. 生成对应的切换按钮
                    container_layout = self.UI.config_switch_btn_container.layout()
                    if not container_layout:
                        self.logger.error("配置切换容器布局不存在")
                        return

                    # 找到弹簧位置
                    spring_item = None
                    for i in range(container_layout.count()):
                        item = container_layout.itemAt(i)
                        if not item.widget() and item.spacerItem():
                            spring_item = item
                            break

                    # 创建新按钮
                    new_btn_index = len(self.services) - 1  # 新服务在列表中的索引
                    btn = QPushButton(new_service.config.get_config("用户名"))  # 按钮文本为文件名（不含后缀）
                    btn.setObjectName(f"config_switch_btn_{new_btn_index}")
                    btn.setStyleSheet(button_style)
                    btn.setCheckable(True)
                    btn.clicked.connect(
                        lambda checked, idx=new_btn_index: self.UI.ServiceStackedWidget.setCurrentIndex(idx)
                    )
                    self.button_group.addButton(btn)

                    # 插入到弹簧上方
                    if spring_item:
                        spring_index = container_layout.indexOf(spring_item)
                        container_layout.insertWidget(spring_index, btn)
                    else:
                        container_layout.addWidget(btn)

                    # 切换到新创建的页面
                    self.UI.ServiceStackedWidget.setCurrentIndex(new_btn_index)
                    self.logger.debug(f"已添加新配置页面: {username} (索引: {new_btn_index})")

                except Exception as e:
                    self.logger.error(f"创建新配置失败: {str(e)}")
            else:
                self.logger.warning("用户输入的用户名为空")
        else:
            self.logger.debug("用户取消了配置添加")

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


def configure_dpi_awareness():
    """配置DPI感知"""
    if sys.platform == "win32":
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
        os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"

        try:
            awareness = ctypes.c_int(1)  # PROCESS_SYSTEM_DPI_AWARE
            ctypes.windll.shcore.SetProcessDpiAwareness(awareness)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception as e:
                print(f"Failed to set DPI awareness: {e}")

        # Remove conflicting environment variables
        os.environ.pop("QT_AUTO_SCREEN_SCALE_FACTOR", None)
        os.environ.pop("QT_SCALE_FACTOR", None)
        os.environ.pop("QT_SCREEN_SCALE_FACTORS", None)
        os.environ.pop("QT_DEVICE_PIXEL_RATIO", None)
        os.environ.pop("QT_DPI_OVERRIDE", None)
        os.environ.pop("QT_FONT_DPI", None)

    cv2.ocl.setUseOpenCL(True)
    # 临时把adb目录添加进环境目录
    os.environ['PATH'] = os.pathsep.join([get_real_path('bin/adb'), os.environ.get('PATH', '')])


if __name__ == "__main__":
    configure_dpi_awareness()
    app = QApplication(sys.argv)

    daily_quests_helper = Xuan()
    daily_quests_helper.show()
    sys.exit(app.exec())
