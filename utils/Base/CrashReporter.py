import atexit
import faulthandler
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path


class CrashReporter:
    """统一的崩溃报告与处理模块，所有日志记录至 Main.log"""

    def __init__(self, log_dir="log", auto_restart=True, show_dialog=True):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.main_log_path = self.log_dir / "Main.log"
        self.auto_restart = auto_restart
        self.show_dialog = show_dialog
        self._original_excepthook = sys.excepthook
        self._qt_app = None
        self._monitor_timer = None
        self.setup()

    def _log_to_main(self, content, category="General"):
        """将内容写入 main.log，自动添加分隔符和时间戳"""
        try:
            with open(self.main_log_path, "a", encoding="utf-8") as f:
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"时间: {datetime.now()}\n")
                f.write(f"类型: {category}\n")
                f.write("=" * 80 + "\n")
                f.write(content)
                f.write("\n" + "=" * 80 + "\n\n")
        except Exception as e:
            # 如果连日志写入都失败，至少尝试输出到控制台
            print(f"写入日志失败: {e}")

    def setup(self):
        """设置全局异常处理器和崩溃检测"""
        # Python 异常钩子
        sys.excepthook = self._python_exception_hook

        # C 层崩溃（段错误等）——重定向到 main.log
        faulthandler.enable(file=open(self.main_log_path, "a"))

        # Windows 未处理异常
        if sys.platform == "win32":
            self._setup_windows_exception_handler()

        # 程序退出回调
        atexit.register(self._on_exit)

    def _python_exception_hook(self, exc_type, exc_value, exc_traceback):
        """处理未捕获的 Python 异常"""
        if exc_type is KeyboardInterrupt:
            if self._original_excepthook:
                self._original_excepthook(exc_type, exc_value, exc_traceback)
            return

        # 记录异常
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self._log_to_main(error_msg, category="Python Exception")

        # 针对 ModuleNotFoundError 输出友好提示
        if exc_type is ModuleNotFoundError:
            missing_module = getattr(exc_value, 'name', str(exc_value))
            print(f"\n[错误] 缺少必要模块: {missing_module}")
            print(f"请前往项目主页 https://github.com/XBJF-X/Xuan-s-UltilityAutoNaruto 的Release页检查是否存在新版本更新安装包")
            input("输入任意键退出程序...")

        # 显示崩溃对话框
        if self.show_dialog:
            self._show_crash_dialog(error_msg)

        # 调用原始钩子（可能显示系统错误对话框）
        if self._original_excepthook:
            self._original_excepthook(exc_type, exc_value, exc_traceback)

    def _show_crash_dialog(self, error_msg):
        """显示控制台交互对话框"""
        try:
            error_preview = "\n".join(error_msg.split("\n")[:10])
            print("\n" + "=" * 50)
            print("程序崩溃")
            print(f"错误信息:\n{error_preview}")
            print(f"详细日志已保存到: {self.main_log_path}")
            if self.auto_restart:
                print("是否尝试重新启动程序？(y/n): ", end="")
                choice = input().strip().lower()
                if choice in ('y', 'yes'):
                    self._restart_program()
        except Exception as e:
            print(f"无法显示崩溃对话框: {e}")

    def _restart_program(self):
        """重启当前程序"""
        python = sys.executable
        subprocess.Popen([python] + sys.argv)
        sys.exit(0)

    def _setup_windows_exception_handler(self):
        """Windows 原生异常处理器（处理 Access Violation 等）"""
        try:
            import ctypes
            import ctypes.wintypes

            @ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p)
            def exception_handler(exception_info):
                try:
                    exc_code = ctypes.c_uint.from_address(exception_info + 4).value
                    # 构建错误信息
                    content = f"Windows异常代码: 0x{exc_code:08X}\n"
                    content += "=" * 80 + "\n"
                    import threading
                    for thread in threading.enumerate():
                        content += f"线程: {thread.name} (ID: {thread.ident})\n"
                    # 添加堆栈（简化版）
                    content += "\n[堆栈跟踪] 需要安装调试器获取详细信息\n"
                    self._log_to_main(content, category="Windows Unhandled Exception")
                except:
                    pass
                return 1  # EXCEPTION_EXECUTE_HANDLER

            ctypes.windll.kernel32.SetUnhandledExceptionFilter(exception_handler)
        except Exception as e:
            self._log_to_main(f"Windows异常处理器设置失败: {e}", category="Setup Error")

    def _on_exit(self):
        """程序退出时的钩子"""
        self._log_to_main("程序退出 (正常或异常)", category="Exit")

    # -------------------- Qt 相关辅助功能 --------------------
    def setup_qt_handlers(self, app):
        """安装 Qt 消息处理器和监控定时器（需要 PySide6）"""
        try:
            from PySide6.QtCore import qInstallMessageHandler, QTimer
            self._qt_app = app
            qInstallMessageHandler(self._qt_message_handler)
            self._start_monitor_timer()
        except ImportError as e:
            self._log_to_main(f"无法设置 Qt 处理器: {e}", category="Qt Setup Error")

    def _qt_message_handler(self, mode, context, message):
        """Qt 日志处理器"""
        from PySide6.QtCore import QtMsgType
        if mode == QtMsgType.QtFatalMsg:
            content = f"Qt致命错误: {message}\n文件: {context.file}, 行: {context.line}\n函数: {context.function}"
            self._log_to_main(content, category="Qt Fatal")
        elif mode == QtMsgType.QtCriticalMsg:
            content = f"Qt关键错误: {message}"
            self._log_to_main(content, category="Qt Critical")

    def _start_monitor_timer(self):
        """启动监控定时器，检查应用状态"""
        try:
            from PySide6.QtCore import QTimer
            self._monitor_timer = QTimer()
            self._monitor_timer.timeout.connect(self._check_app_state)
            self._monitor_timer.start(5000)  # 每5秒检查一次
        except Exception as e:
            self._log_to_main(f"监控定时器启动失败: {e}", category="Monitor Error")

    def _check_app_state(self):
        """检查 QApplication 实例是否还存在"""
        try:
            from PySide6.QtWidgets import QApplication
            if not QApplication.instance():
                self._log_to_main("QApplication实例丢失", category="App State")
        except Exception as e:
            self._log_to_main(f"监控异常: {e}", category="Monitor Error")