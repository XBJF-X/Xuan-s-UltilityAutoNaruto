import logging
import os.path
from logging.handlers import RotatingFileHandler

from PySide6.QtCore import Signal, QObject
from PySide6.QtGui import QTextCursor, QFont
from PySide6.QtWidgets import (QTextEdit, QVBoxLayout, QWidget)

from StaticFunctions import get_real_path
from utils.core.Config import Config


# 自定义信号类，用于在日志处理器和UI之间传递消息
class LogSignal(QObject):
    log_received = Signal(str)  # 传递格式化后的日志字符串


class QtLogHandler(logging.Handler):
    """自定义日志处理器，将日志发送到PyQt界面"""

    def __init__(self):
        super().__init__()
        self.signal = LogSignal()  # 使用信号槽避免线程问题

    def emit(self, record):
        """重写emit方法，处理日志记录"""
        try:
            # 格式化日志（使用logger的格式器）
            msg = self.format(record)
            # 通过信号发送到UI线程（避免多线程问题）
            self.signal.log_received.emit(msg)
        except Exception:
            self.handleError(record)


class LogWindow(QWidget):
    """日志输出窗口（仅显示，无命令输入）"""

    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.init_ui()
        self.setup_logging()

    def init_ui(self):
        """初始化UI界面"""
        # self.setWindowFlags(
        #     Qt.FramelessWindowHint
        #     | Qt.WindowStaysOnTopHint
        #     | Qt.Tool
        # )
        layout = QVBoxLayout(self)
        # 日志输出区域（只读）
        self.log_text = QTextEdit()
        doc = self.log_text.document()
        # 设置全局样式表（对所有文本生效）
        doc.setDefaultStyleSheet("""
            p {
                line-height: 1.1;  /* 行距：1.8倍 */
            }
        """)
        self.log_text.setReadOnly(True)
        self.log_text.setAcceptRichText(True)  # 支持富文本（彩色、字体等）
        self.log_text.setFont(QFont("Consolas, 微软雅黑", 10))
        self.log_text.setStyleSheet("""
            QTextEdit {
                font-size:10pt;
                background-color: #f5f5f5;
                border: 1px solid gray;
                padding: 7px;
            }
            /* 垂直滚动条整体 */
            QTextEdit QScrollBar:vertical {
                background-color: #f5f5f5;  /* 滚动条背景 */
                width: 10px;                 /* 滚动条宽度 */
                margin: 0px;                /* 与边界的距离 */
                border-radius: 4px;         /* 滚动条圆角 */
            }
            QScrollBar::handle:vertical {
              background-color: #8b8b8b;  /* 滚动条背景 */
              border-radius: 5px;
              /*可以通过margin设置滑块小于QScrollBar width，再鼠标滑过滑块样式中再重新设置margin，达到鼠标滑过滑块变大的效果，但是圆角设置border-radius不生效了！！！*/
              margin: 0 0px 0 0px;
              min-height: 30px;
            }
            /* 鼠标滑过滑块样式 */
            QScrollBar::handle:vertical:hover,
            QScrollBar::handle:vertical:pressed {
              background-color: #3c3f41;  /* 滚动条背景 */
              border-radius: 5px;
              margin: 0 0px 0 0px;
            }
            /* 向上区域样式 */
            QScrollBar::sub-line:vertical {
              border: none;
              height: 0px;
            }
            
            /* 向下区域样式 */
            QScrollBar::add-line:vertical {
              border: none;
              height: 0px;
            }
            """)
        # self.log_text.verticalScrollBar().valueChanged.connect(self.on_scroll_changed)
        layout.addWidget(self.log_text)

    def setup_logging(self):
        """配置logging，将日志定向到UI窗口"""
        # 1. 创建自定义日志处理器
        self.log_handler = QtLogHandler()
        # 绑定信号：日志到来时，调用append_log方法显示
        self.log_handler.signal.log_received.connect(self.append_log)
        formatter = logging.Formatter(
            '[%(levelname)s] %(name)s %(asctime)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'  # 关键：设置日期格式，去除毫秒
        )
        self.log_handler.setFormatter(formatter)
        # 3. 配置root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_handler)
        root_logger.setLevel(logging.DEBUG)  # 设置日志级别（DEBUG及以上都显示）

        # 添加log文件处理器（参考旧项目）
        if not os.path.exists(get_real_path("log")):
            os.makedirs(get_real_path("log"))

        file_handler = RotatingFileHandler(
            get_real_path("log/log"),
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=100,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # 文件记录更详细

        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        stop_logger = ["comtypes", "uiautomator2", "adbutils"]
        for logger in stop_logger:
            # 禁用 comtypes 的日志
            comtypes_logger = logging.getLogger(logger)
            comtypes_logger.setLevel(logging.WARNING)  # 设置为 WARNING 或更高
            comtypes_logger.propagate = False  # 防止传播到根日志器

        root_logger.debug("根记录器初始化完成...")

    def append_log(self, log_msg: str):
        scroll_bar = self.log_text.verticalScrollBar()
        scroll_bar_value = scroll_bar.value()
        # print(f"当前值：{scroll_bar_value}，滚动条最大值：{scroll_bar.maximum()}")
        is_at_bottom = scroll_bar_value >= scroll_bar.maximum() - 4

        # 检查是否以\r结尾
        overwrite_line = log_msg.endswith('\r')
        if overwrite_line:
            log_msg = log_msg.rstrip('\r')  # 移除结尾的\r

        level = log_msg.split("] ")[0][1:]
        if level == "ERROR":
            style = 'color: #ff0000; margin: 0px; padding: 2px 0px;'
        elif level == "WARNING":
            style = 'color: #ff7d00; margin: 0px; padding: 2px 0px;'
        elif level == "DEBUG":
            style = 'color: #888888; margin: 0px; padding: 2px 0px;'
        else:
            style = 'color: #000000; margin: 0px; padding: 2px 0px;'
        # 覆盖模式：删除最后一行并插入新内容
        if overwrite_line:
            cursor = self.log_text.textCursor()

            # 移动到文档最后并选择最后一行
            cursor.movePosition(QTextCursor.End)
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)

            # 删除选中行并插入新内容
            cursor.removeSelectedText()
            html = f'<p style="{style}">{log_msg}</p>'
            cursor.insertHtml(html)

            # 确保光标可见
            self.log_text.setTextCursor(cursor)
            self.log_text.ensureCursorVisible()

        # 正常模式：追加新行
        else:
            log_msg += '<br>'
            html = f'<p style="{style}">{log_msg}</p>'
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.log_text.setTextCursor(cursor)
            self.log_text.insertHtml(html)

            # 滚动处理
            if is_at_bottom:
                self.log_text.ensureCursorVisible()
            else:
                scroll_bar.setValue(scroll_bar_value)

    def closeEvent(self, event):
        """窗口关闭时，移除日志处理器（可选）"""
        root_logger = logging.getLogger()
        root_logger.removeHandler(self.log_handler)
        event.accept()
