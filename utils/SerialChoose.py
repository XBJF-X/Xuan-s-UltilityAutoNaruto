import logging
import time
from typing import List

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QDialog, QListWidgetItem, QAbstractItemView, QLineEdit
from adbutils import adb, AdbError

from utils.Base.Config import Config
from utils.ui.SerialChoose_ui import Ui_SerialChoose


class SerialChoose(QDialog):
    def __init__(self, config: Config, lineedit: QLineEdit, parent_logger=None, parent=None):
        super().__init__(parent)
        self.UI = Ui_SerialChoose()
        self.UI.setupUi(self)
        self.config = config
        self.logger = parent_logger.getChild(self.__class__.__name__) if parent_logger else logging.getLogger(self.__class__.__name__)
        self.lineedit = lineedit
        self.setModal(True)
        self.resize(394, 268)

        # 存储当前选择的串口名称
        self.selected_serial = ""

        # 初始化串口列表
        self._init_serial_list()

        # 连接信号
        self.UI.ok.clicked.connect(self._on_finish)
        self.UI.kill_and_restart_adb.clicked.connect(self._on_kill_and_restart_adb)
        self.UI.serial_listWidget.itemSelectionChanged.connect(self._update_selection)

    def _init_serial_list(self):
        """填充串口列表控件"""
        serial_list = self.get_adb_devices()
        self.UI.serial_listWidget.clear()

        # 设置选择模式为单选
        self.UI.serial_listWidget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # 添加串口项
        for serial in serial_list:
            item = QListWidgetItem(serial)
            item.setSizeHint(QSize(0, 40))  # 设置项高度
            self.UI.serial_listWidget.addItem(item)

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
        self.lineedit.setText(self.selected_serial)
        self.config.set_config("串口", self.selected_serial)
        # 关闭对话框
        self.accept()

    def _on_kill_and_restart_adb(self):
        self.logger.info("重启 adb服务")
        self.restart_adb_server()
        self._init_serial_list()

    def get_selected_serial(self) -> str:
        """获取用户选择的串口名称"""
        return self.selected_serial

    def get_adb_devices(self) -> List[str]:
        """
        使用 adbutils 获取已连接的设备列表

        返回:
            List[str]: 状态为 'device' 的设备序列号列表
        """
        try:
            self.logger.info("正在获取ADB设备列表...")
            devices = adb.device_list()
            device_serials = []
            for device in devices:
                state = device.get_state()
                if state == 'device':
                    device_serials.append(device.serial)
                    self.logger.info(f"找到设备: {device.serial} (状态: {state})")
                else:
                    self.logger.warning(f"设备 {device.serial} 状态异常: {state}")

            if not device_serials:
                self.logger.warning("未找到任何已连接的ADB设备")

            return device_serials

        except AdbError as e:
            self.logger.error(f"ADB命令执行失败: {str(e)}")
            return []
        except Exception as e:
            self.logger.exception(f"获取ADB设备列表时发生未知错误: {str(e)}")
            return []

    def kill_adb_server(self):
        """终止ADB服务"""
        try:
            self.logger.info("正在终止ADB服务...")
            adb.server_kill()
            time.sleep(1)  # 必须加等待
            self.logger.info("ADB服务已成功终止")
        except AdbError as e:
            self.logger.error(f"终止ADB服务失败: {str(e)}")
        except Exception as e:
            self.logger.exception(f"终止ADB服务时发生未知错误: {str(e)}")

    def restart_adb_server(self):
        """重启ADB服务"""
        try:
            self.logger.info("正在重启ADB服务...")
            try:
                adb.server_kill()
            except Exception:
                pass
            time.sleep(1)
            adb.server_version()
            # 验证服务已重启
            self.logger.info("ADB server 已重启")
        except AdbError as e:
            self.logger.error(f"重启ADB服务失败: {str(e)}")
        except Exception as e:
            self.logger.exception(f"重启ADB服务时发生未知错误: {str(e)}")