import logging
from typing import List

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QDialog, QListWidgetItem, QAbstractItemView

from ui.SerialChoose_ui import Ui_SerialChoose
from utils.Config import Config


class SerialChoose(QDialog):
    def __init__(self, config: Config, serial_list: List[str], parent=None):
        super().__init__(parent)
        self.UI = Ui_SerialChoose()
        self.UI.setupUi(self)
        self.config = config
        self.logger = logging.getLogger("串口列表")
        self.setModal(True)
        self.resize(394, 268)

        # 存储当前选择的串口名称
        self.selected_serial = ""

        # 初始化串口列表
        self._init_serial_list(serial_list)

        # 连接信号
        self.UI.ok.clicked.connect(self._on_finish)
        self.UI.serial_listWidget.itemSelectionChanged.connect(self._update_selection)

    def _init_serial_list(self, serial_list: List[str]):
        """填充串口列表控件"""
        self.UI.serial_listWidget.clear()

        # 设置选择模式为单选
        self.UI.serial_listWidget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # 添加串口项
        for serial in serial_list:
            item = QListWidgetItem(serial)
            item.setSizeHint(QSize(0, 40))  # 设置项高度
            self.UI.serial_listWidget.addItem(item)

        # 默认选择第一项（如果有）
        if serial_list:
            self.UI.serial_listWidget.setCurrentRow(0)
            self.selected_serial = serial_list[0]

    def _update_selection(self):
        """更新当前选择的串口"""
        selected_items = self.UI.serial_listWidget.selectedItems()
        if selected_items:
            self.selected_serial = selected_items[0].text()
            self.logger.debug(f"当前选择: {self.selected_serial}")

    def _on_finish(self):
        """确定按钮点击事件"""
        if not self.selected_serial:
            self.logger.warning("未选择任何串口")
            return
        self.logger.info(f"已选择串口: {self.selected_serial}")
        self.config.set_config("串口", self.selected_serial)
        # 关闭对话框
        self.accept()

    def get_selected_serial(self) -> str:
        """获取用户选择的串口名称"""
        return self.selected_serial
