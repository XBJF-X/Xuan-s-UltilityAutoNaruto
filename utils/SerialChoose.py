import logging
import subprocess
from typing import List

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QDialog, QListWidgetItem, QAbstractItemView, QLineEdit

from utils.ui.SerialChoose_ui import Ui_SerialChoose
from utils.Base.Config import Config


class SerialChoose(QDialog):
    def __init__(self, config: Config, lineedit:QLineEdit, parent=None):
        super().__init__(parent)
        self.UI = Ui_SerialChoose()
        self.UI.setupUi(self)
        self.config = config
        self.logger = logging.getLogger("串口列表")
        self.lineedit=lineedit
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

        # # 默认选择第一项（如果有）
        # if serial_list:
        #     self.UI.serial_listWidget.setCurrentRow(0)
        #     self.selected_serial = serial_list[0]

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
        执行 adb devices 命令并返回连接的设备列表

        返回:
            List[str]: 已连接的设备序列号列表
        """
        # 创建命令列表（推荐使用列表形式，避免shell注入风险）
        command = ["adb", "devices"]

        try:
            # 执行命令并捕获输出
            self.logger.info(f"执行命令: {' '.join(command)}")
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,  # 捕获标准输出
                stderr=subprocess.PIPE,  # 捕获标准错误
                text=True,  # 以文本形式返回结果
                timeout=15,  # 设置超时时间（秒）
                check=True,  # 检查命令是否成功执行
                encoding='utf-8'
            )
            # # 记录完整输出（调试用）
            # self.logger.debug(f"完整输出:\n{result.stdout}")

            # 解析输出，提取设备序列号
            devices = []
            for line in result.stdout.splitlines():
                # 跳过空行和标题行
                if not line.strip() or line.strip().startswith("List of devices attached"):
                    continue

                # 提取设备序列号（格式：<serial>\t<status>）
                parts = line.split()
                if len(parts) >= 2:
                    serial = parts[0]
                    status = parts[1]

                    # 只添加状态为 "device" 的设备（已授权）
                    if status == "device":
                        devices.append(serial)
                        self.logger.info(f"找到设备: {serial} (状态: {status})")
                    else:
                        self.logger.warning(f"设备 {serial} 状态异常: {status}")

            if not devices:
                self.logger.warning("未找到任何已连接的ADB设备")

            return devices

        except subprocess.CalledProcessError as e:
            # 命令执行失败
            self.logger.error(f"命令执行失败，退出码: {e.returncode}")
            self.logger.error(f"错误输出:\n{e.stderr}")
            return []

        except subprocess.TimeoutExpired:
            # 命令执行超时
            self.logger.error("命令执行超时，请检查ADB服务是否正常")
            return []

        except FileNotFoundError:
            # ADB命令未找到
            self.logger.error("未找到adb命令，请确保ADB已安装并添加到PATH环境变量")
            return []

        except Exception as e:
            # 其他未知异常
            self.logger.exception(f"执行adb devices时发生未知错误: {str(e)}")
            return []

    def kill_adb_server(self):
        """终止ADB服务"""
        command = ["adb", "kill-server"]

        try:
            self.logger.info(f"执行命令: {' '.join(command)}")
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=15,
                check=True,
                encoding='utf-8'
            )

            # 记录命令执行成功
            self.logger.info("ADB服务已成功终止")

        except subprocess.CalledProcessError as e:
            self.logger.error(f"终止ADB服务失败，退出码: {e.returncode}")
            self.logger.error(f"错误输出:\n{e.stderr}")

        except subprocess.TimeoutExpired:
            self.logger.error("终止ADB服务超时，请检查ADB服务状态")

        except FileNotFoundError:
            self.logger.error("未找到adb命令，请确保ADB已安装并添加到PATH环境变量")

        except Exception as e:
            self.logger.exception(f"终止ADB服务时发生未知错误: {str(e)}")

    def restart_adb_server(self):
        """重启ADB服务"""
        # 先终止服务
        self.kill_adb_server()

        # 再启动服务
        command = ["adb", "start-server"]

        try:
            self.logger.info(f"执行命令: {' '.join(command)}")
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=15,
                check=True,
                encoding='utf-8'
            )

            # 解析输出确认服务启动成功
            if "daemon started successfully" in result.stdout or "daemon started successfully" in result.stderr:
                self.logger.info("ADB服务已成功启动")
            else:
                self.logger.info("ADB服务启动命令已执行")
                self.logger.debug(f"ADB启动输出:\n{result.stdout}")

        except subprocess.CalledProcessError as e:
            self.logger.error(f"启动ADB服务失败，退出码: {e.returncode}")
            self.logger.error(f"错误输出:\n{e.stderr}")

        except subprocess.TimeoutExpired:
            self.logger.error("启动ADB服务超时，请检查ADB服务状态")

        except FileNotFoundError:
            self.logger.error("未找到adb命令，请确保ADB已安装并添加到PATH环境变量")

        except Exception as e:
            self.logger.exception(f"启动ADB服务时发生未知错误: {str(e)}")
