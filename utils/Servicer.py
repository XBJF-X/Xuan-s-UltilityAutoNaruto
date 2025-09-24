import json
import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict
from zoneinfo import ZoneInfo

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QTreeWidgetItem

from StaticFunctions import get_real_path, setup_logging
from utils.Base.Config import Config
from utils.Base.Device import Device
from utils.Base.LogWindow import LogWindow
from utils.Base.Scheduler import Scheduler
from utils.KeyMapConfiguration import KeyMapConfiguration
from utils.SerialChoose import SerialChoose
from utils.ui.Service_ui import Ui_Service
from utils.ui.TaskConfigWidget import TaskConfigWidget


class Service(QWidget):
    def __init__(self, config_path, scene_graph):
        super().__init__()
        self.config_path = config_path
        self.logger = logging.getLogger(f"{self.__class__.__name__}_{self.config_path.stem}")
        self.UI = Ui_Service()
        self.UI.setupUi(self)
        self.logger.info("初始化配置...")
        self.config = Config(config_path=self.config_path, parent_logger=self.logger)
        self.log_window = LogWindow(
            user_name=self.config.get_config("用户名"),
            logger_name=self.logger.name
        )
        self.task_common_control_ref_map: Dict[str:Dict[str:QWidget]] = defaultdict(dict)  # 任务控制控件
        self.task_index_dic: Dict[str, int] = {"助手设置": 1}
        self.tree_items = {}
        self.logger.info("初始化UI...")
        self.alloc_ui_ref_map()
        self.logger.info("初始化UI响应函数...")
        self.bind_signals()
        self.logger.info("初始化调度器...")
        self.scheduler = Scheduler(
            self.UI,
            self.config,
            scene_graph,
            self.task_common_control_ref_map,
            parent_logger=self.logger
        )
        self.logger.info("初始化完成...")

    def alloc_ui_ref_map(self):
        # 日志窗口设置
        layout = QVBoxLayout(self.UI.logs_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.log_window)
        # 确保首页为总览面板
        self.UI.stackedWidget.setCurrentIndex(1)
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

        model = QStandardItemModel(0, 1, self)
        roots = []
        for root in ["每日任务", "每周任务", "每月任务", "周期任务", "活动任务", "助手设置"]:
            temp_root = QStandardItem(root)
            model.appendRow(temp_root)
            roots.append(temp_root)

        task_config = json.load(open(get_real_path("src/DefaultConfig.json"), encoding="utf-8"))["任务"]
        start_index = 2
        for task_name, task in task_config.items():
            child = QStandardItem(task_name)
            self.tree_items[task_name] = child
            if self.config.get_task_base_config(task_name, "是否启用"):
                child.setData(QColor("#779977"), Qt.ItemDataRole.ForegroundRole)
            else:
                child.setData(QColor("#000000"), Qt.ItemDataRole.ForegroundRole)
            roots[task["类型"]].appendRow(child)
            temp_task_widget = TaskConfigWidget(task_name, task, self)
            self.UI.stackedWidget.addWidget(temp_task_widget)
            # 保存任务配置控件引用
            temp_widget = temp_task_widget.task_widget_dic["是否启用"]
            self.task_common_control_ref_map[task_name]["CheckBox"] = temp_widget
            temp_widget.setChecked(self.config.get_task_base_config(task_name, "是否启用"))
            temp_widget.toggled.connect(
                lambda state, tn=task_name: self._on_task_activation_toggled(state, tn))
            temp_widget = temp_task_widget.task_widget_dic["下次执行时间"]
            self.task_common_control_ref_map[task_name]["LineEdit"] = temp_widget
            temp_widget.setText(
                datetime.fromtimestamp(self.config.get_task_base_config(task_name, "下次执行时间"),
                                       tz=ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S"))
            temp_widget.editingFinished.connect(
                lambda tn=task_name: self.scheduler.task_next_execute_time_editfinished(tn))
            if temp_task_widget.task_widget_dic["执行参数"]:
                for param_name, param_info in temp_task_widget.task_widget_dic["执行参数"].items():
                    param_widget = param_info["控件"]
                    match param_info["类型"]:
                        case "INT":
                            param_widget.valueChanged.connect(
                                lambda value, tn=task_name, pn=param_name:
                                self.config.set_task_exe_param(tn, pn, value))
                            param_widget.setValue(self.config.get_task_exe_param(task_name, param_name))
                        case "COMBOX":
                            param_widget.currentIndexChanged.connect(
                                lambda value, tn=task_name, pn=param_name:
                                self.config.set_task_exe_param(tn, pn, value))
                            param_widget.setCurrentIndex(
                                self.config.get_task_exe_param(task_name, param_name))

            self.task_index_dic[task_name] = start_index
            start_index += 1
        self.UI.treeView.setModel(model)
        self.UI.stackedWidget.setCurrentIndex(0)

    def bind_signals(self):
        self.UI.start_schedule_button.clicked.connect(self._on_start_schedule_button_clicked)
        self.UI.overview_panel_button.clicked.connect(lambda _: self.UI.stackedWidget.setCurrentIndex(0))
        self.UI.treeView.clicked.connect(self._on_tree_item_clicked)
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

    def _on_task_activation_toggled(self, state, tn):
        item = self.tree_items.get(tn)
        if item is not None:
            if state:
                item.setData(QColor("#779977"), Qt.ItemDataRole.ForegroundRole)
            else:
                item.setData(QColor("#000000"), Qt.ItemDataRole.ForegroundRole)
        self.scheduler.toggle_task_activation(state, tn)

    def _on_start_schedule_button_clicked(self):
        if not self.scheduler.running:
            self.scheduler.start()
        else:
            self.scheduler.stop()

    def _on_tree_item_clicked(self, index):
        # 获取模型和项目
        model = self.UI.treeView.model()
        item = model.itemFromIndex(index)
        text = item.text()

        if self.task_index_dic.get(text, 0):
            self.UI.stackedWidget.setCurrentIndex(self.task_index_dic[text])

    def _on_bool_debug_toggled(self, flag):
        self.log_window.log_level = logging.DEBUG if flag else logging.INFO
        self.logger.debug(f"日志窗口显示等级已经调为[{"DEBUG" if flag else "INFO"}]")
        self.config.set_config('调试模式', int(flag))

    def _on_screen_mode_change(self, index):
        self.config.set_config("截图模式", index)

    def _on_control_mode_change(self, index):
        self.config.set_config("控制模式", index)


    def _on_key_map_configuration_button_clicked(self):
        if self.scheduler.device is not None:
            device = self.scheduler.device
        else:
            device = Device(self.config, self.logger)
        editor = KeyMapConfiguration(self.config, device.screen_cap(), self.logger, self)
        editor.exec()
        device = None

    def _on_serial_list_button_clicked(self):
        editor = SerialChoose(self.config, self.UI.serial, self.logger, self)
        editor.exec()

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
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    setup_logging()

    widget = Service(config_path=Path(get_real_path("config/Config_1.json")), scene_graph=None)
    widget.show()

    sys.exit(app.exec())
