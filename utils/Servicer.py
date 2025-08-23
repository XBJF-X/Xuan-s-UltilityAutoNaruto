import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict
from zoneinfo import ZoneInfo
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFileDialog
from utils.Base.Config import Config
from utils.Base.Device import Device
from utils.Base.LogWindow import LogWindow
from utils.Base.Recognizer import Recognizer
from utils.Base.Scene.SceneGraph import SceneGraph
from utils.Base.Task import TASK_NAME_CN2EN_MAP, TREE_INDEX_DIC
from utils.KeyMapConfiguration import KeyMapConfiguration
from utils.Base.Scheduler import Scheduler
from utils.SerialChoose import SerialChoose
from utils.ui.Service_ui import Ui_Service


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
        self.logger.info("初始化UI...")
        self.alloc_ui_ref_map()
        self.logger.info("初始化UI响应函数...")
        self.bind_signals()
        self.scene_graph: SceneGraph = scene_graph
        self.recognizer = Recognizer(self.scene_graph, parent_logger=self.logger)
        self.logger.info("初始化调度器...")
        self.scheduler = Scheduler(
            self.UI,
            self.config,
            self.scene_graph,
            self.recognizer,
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

    def _on_filepath_browse_clicked(self, name):
        folder = QFileDialog.getExistingDirectory(self, f"选择{name}模拟器安装目录")
        if folder:
            if name == "MuMu":
                self.UI.MuMu_install_path.setText(folder)
                self.config.set_config("MuMu安装路径", folder)
            elif name == "雷电":
                self.UI.LD_install_path.setText(folder)
                self.config.set_config("雷电安装路径", folder)
