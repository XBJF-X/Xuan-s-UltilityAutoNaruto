import sys

import ctypes
import json
import logging
import os
import webbrowser
from collections import defaultdict
from datetime import datetime
from typing import Dict
from zoneinfo import ZoneInfo

import cv2
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPainter, QBrush, QColor, QRegion, QPainterPath
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QApplication, QWidget, QFileDialog

from StaticFunctions import resource_path, get_real_path
from utils.Base.Updater import Updater
from utils.Base.Recognizer import Recognizer
from utils.Base.Config import Config
from utils.Base.Device import Device
from utils.Base.Scene.SceneGraph import SceneGraph
from utils.KeyMapConfiguration import KeyMapConfiguration
from utils.Base.Logger import LogWindow
from utils.Scheduler import Scheduler
from utils.SerialChoose import SerialChoose
from utils.Base.Task import TREE_INDEX_DIC, TASK_NAME_CN2EN_MAP
from utils.ui.Xuan_ui import Ui_Xuan


class Xuan(QMainWindow):
    def __init__(self):
        super().__init__()
        self.UI = Ui_Xuan()
        self.UI.setupUi(self)
        self.log_window = LogWindow()
        self.logger = logging.getLogger("Xuan")
        self.logger.info("初始化配置...")
        self.config = Config()
        self.logger.info("初始化环境...")
        self.mouse_position = None
        self.init_environment()
        self.task_common_control_ref_map: Dict[str:Dict[str:QWidget]] = defaultdict(dict)  # 任务控制控件
        self.logger.info("初始化UI...")
        self.alloc_ui_ref_map()
        self.logger.info("初始化UI响应函数...")
        self.bind_signals()
        self.scene_graph = SceneGraph()
        self.recognizer = Recognizer(self.scene_graph)
        self.logger.info("初始化调度器...")
        self.scheduler = Scheduler(
            self.UI,
            self.config,
            self.scene_graph,
            self.recognizer,
            self.task_common_control_ref_map
        )
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
        self.UI.ZhuangBeiHeCheng_target_armor.setCurrentIndex(self.config.get_task_config("装备合成", "合成目标装备"))

    def bind_signals(self):
        self.UI.start_schedule_button.clicked.connect(self._on_start_schedule_button_clicked)
        self.UI.overview_panel_button.clicked.connect(lambda _: self.UI.stackedWidget.setCurrentIndex(0))
        self.UI.treeWidget.itemClicked.connect(self._on_tree_item_clicked)
        self.UI.bool_debug.toggled.connect(self._on_bool_debug_toggled)
        self.UI.screen_mode.currentIndexChanged.connect(self._on_screen_mode_change)
        self.UI.control_mode.currentIndexChanged.connect(self._on_control_mode_change)
        self.UI.serial.editingFinished.connect(lambda w=self.UI.serial: self.config.set_config("串口", w.text()))
        self.UI.LD_install_path.editingFinished.connect(lambda path: self.config.set_config('雷电安装路径', path))
        self.UI.LD_install_path_browse.clicked.connect(lambda: self._on_filepath_browse_clicked("雷电"))
        self.UI.LD_instance_index.valueChanged.connect(lambda index: self.config.set_config('雷电实例索引', index))
        self.UI.MuMu_install_path.editingFinished.connect(lambda path: self.config.set_config('MuMu安装路径', path))
        self.UI.MuMu_install_path_browse.clicked.connect(lambda: self._on_filepath_browse_clicked("MuMu"))
        self.UI.MuMu_instance_index.valueChanged.connect(lambda index: self.config.set_config('MuMu实例索引', index))
        self.UI.scan_inerval.valueChanged.connect(lambda index: self.config.set_config('扫描间隔', index))
        self.UI.secondary_password.editingFinished.connect(lambda w=self.UI.secondary_password: self.config.set_config("二级密码", w.text()))
        self.UI.key_map_configuration_button.clicked.connect(self._on_key_map_configuration_button_clicked)
        self.UI.serial_list_button.clicked.connect(self._on_serial_list_button_clicked)

        self.UI.go_to_github_btn.clicked.connect(self._on_go_to_github_btn_clicked)
        self.UI.update_btn.clicked.connect(self._on_update_btn_clicked)
        self.UI.exit_btn.clicked.connect(QApplication.quit)

        self.UI.XiaoDuiTuXi_4rewards_Enable.toggled.connect(lambda flag: self.config.set_task_config("小队突袭", "四倍奖励勾选", flag))
        self.UI.XiaoDuiTuXi_4rewards_times.valueChanged.connect(lambda value: self.config.set_task_config("小队突袭", "四倍奖励次数", value))
        self.UI.JinBiZhaoCai_times.valueChanged.connect(lambda value: self.config.set_task_config("金币招财", "招财次数", value))
        self.UI.GouMaiTiLi_times.valueChanged.connect(lambda value: self.config.set_task_config("购买体力", "购买体力次数", value))
        self.UI.ZhuangBeiHeCheng_target_armor.currentIndexChanged.connect(lambda index: self.config.set_task_config('装备合成', '合成目标装备', index))

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
            self.config = Config()
            self.scheduler.start()
        else:
            self.config = None
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
        # self.UI.screen_mode_settings_stackedWidget.setCurrentIndex(index)
        self.config.set_config("截图模式", index)

    def _on_control_mode_change(self, index):
        self.config.set_config("控制模式", index)

    def _on_key_map_configuration_button_clicked(self):
        if self.scheduler.device is not None:
            device = self.scheduler.device
        else:
            device = Device(self.config)
        editor = KeyMapConfiguration(self.config, device.screen_cap(), self)
        editor.exec()
        device = None

    def _on_serial_list_button_clicked(self):
        editor = SerialChoose(self.config, self.UI.serial, self)
        editor.exec()

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

    def _on_filepath_browse_clicked(self, name):
        folder = QFileDialog.getExistingDirectory(self, f"选择{name}模拟器安装目录")
        if folder:
            if name == "MuMu":
                self.UI.MuMu_install_path.setText(folder)
                self.config.set_config("MuMu安装路径", folder)
            elif name == "雷电":
                self.UI.LD_install_path.setText(folder)
                self.config.set_config("雷电安装路径", folder)

    def _on_about_to_quit(self):
        self.scheduler.timer_thread.stop()
        self.scheduler.stop()
        self.logger.debug("日常助手退出")


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
