import logging
import os.path
from logging.handlers import RotatingFileHandler

from PySide6.QtCore import Signal, QObject
from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor
from PySide6.QtWidgets import (QPlainTextEdit, QVBoxLayout, QWidget)

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
    """日志输出窗口（QPlainTextEdit实现，保留颜色和行数限制）"""

    def __init__(self, config: Config, max_lines=10000):  # 默认限制10000行
        super().__init__()
        self.config = config
        self.max_lines = max_lines  # 最大日志行数
        self.log_level = logging.DEBUG
        self.init_ui()
        # 初始化日志级别颜色格式
        self.init_log_formats()
        self.setup_logging()

    def init_ui(self):
        """初始化UI界面（使用QPlainTextEdit）"""
        layout = QVBoxLayout(self)

        # 日志输出区域（只读，使用QPlainTextEdit）
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)

        # 设置样式表（针对QPlainTextEdit优化）
        self.log_text.setStyleSheet("""
            QPlainTextEdit {
                font-family: "Consolas", "SimHei", sans-serif;
                font-size: 11pt;
                background-color: #f5f5f5;
                border: 1px solid gray;
                padding: 7px;
            }
            /* 垂直滚动条样式 */
            QPlainTextEdit QScrollBar:vertical {
                background-color: #f5f5f5;
                width: 10px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #8b8b8b;
                border-radius: 5px;
                margin: 0 0px 0 0px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover,
            QScrollBar::handle:vertical:pressed {
                background-color: #3c3f41;
                border-radius: 5px;
            }
            QScrollBar::sub-line:vertical,
            QScrollBar::add-line:vertical {
                border: none;
                height: 0px;
            }
        """)

        # 设置字体抗锯齿
        font = self.log_text.font()
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.log_text.setFont(font)

        layout.addWidget(self.log_text)

    def init_log_formats(self):
        """初始化不同日志级别的颜色格式"""
        self.formats = {
            'ERROR': self.create_format(QColor(255, 0, 0)),  # 红色
            'WARNING': self.create_format(QColor(255, 125, 0)),  # 橙色
            'DEBUG': self.create_format(QColor(136, 136, 136)),  # 灰色
            'INFO': self.create_format(QColor(0, 0, 0))  # 黑色
        }

    def create_format(self, color):
        """创建指定颜色的文本格式"""
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        return fmt

    def setup_logging(self):
        """配置logging，将日志定向到UI窗口"""
        # 创建自定义日志处理器
        self.log_handler = QtLogHandler()
        self.log_handler.signal.log_received.connect(self.append_log)

        formatter = logging.Formatter(
            '[%(levelname)s] %(name)s %(asctime)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.log_handler.setFormatter(formatter)

        # 配置root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_handler)
        root_logger.setLevel(logging.DEBUG if self.config.get_config('调试模式', 0) else logging.INFO)

        # 添加文件处理器
        if not os.path.exists(get_real_path("log")):
            os.makedirs(get_real_path("log"))

        file_handler = RotatingFileHandler(
            get_real_path("log/DailyQuestHelper.log"),
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=100,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        # 禁用指定logger的日志
        stop_logger = ["comtypes", "uiautomator2", "adbutils"]
        for logger in stop_logger:
            logger_instance = logging.getLogger(logger)
            logger_instance.setLevel(logging.WARNING)
            logger_instance.propagate = False

        root_logger.debug("根记录器初始化完成...")

    def get_log_level(self, log_msg):
        """从日志消息中提取日志级别"""
        if log_msg.startswith('['):
            end_idx = log_msg.find(']')
            if end_idx > 0:
                return log_msg[1:end_idx]
        return 'INFO'  # 默认级别

    def append_log(self, log_msg: str):
        """添加带颜色的日志到界面，超过最大行数时从顶部截断"""
        # 检查滚动条位置（是否在底部）
        scroll_bar = self.log_text.verticalScrollBar()
        scroll_bar_value = scroll_bar.value()
        # print(f"当前值：{scroll_bar_value}，滚动条最大值：{scroll_bar.maximum()}")
        is_at_bottom = scroll_bar_value >= scroll_bar.maximum() - 4

        # 获取日志级别和对应格式
        level = self.get_log_level(log_msg)
        if level == "DEBUG" and self.log_level > logging.DEBUG:
            return

        text_format = self.formats.get(level, self.formats['INFO'])

        # 处理覆盖行（\r结尾的日志）
        overwrite_line = log_msg.endswith('\r')

        # 直接使用文档的现有光标，避免重置视图位置
        cursor = self.log_text.textCursor()

        if overwrite_line:
            log_msg = log_msg.rstrip('\r')
            # 移动到最后一行并替换
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
            cursor.setCharFormat(text_format)
            cursor.insertText(log_msg)
            self.log_text.setTextCursor(cursor)
            self.log_text.ensureCursorVisible()
        else:
            # 追加新行（带颜色）
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.setCharFormat(text_format)
            # 提交光标更改（但不改变视图位置）
            self.log_text.setTextCursor(cursor)
            cursor.insertText(log_msg + '\n')  # 手动添加换行

        # 保持滚动位置（如果原本在底部则自动滚动）
        if is_at_bottom:
            scroll_bar.setValue(scroll_bar.maximum())
            self.log_text.ensureCursorVisible()
        else:
            scroll_bar.setValue(scroll_bar_value)

    def closeEvent(self, event):
        """窗口关闭时移除日志处理器"""
        root_logger = logging.getLogger()
        root_logger.removeHandler(self.log_handler)
        event.accept()
