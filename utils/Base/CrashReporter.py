import sys
import os
import traceback
import faulthandler
import atexit
from datetime import datetime
from pathlib import Path
import subprocess
import ctypes


class CrashReporter:
    """崩溃报告器"""

    def __init__(self):
        self.log_dir = Path("log")
        self.log_dir.mkdir(exist_ok=True)
        self.setup()

    def setup(self):
        """设置崩溃处理器"""
        # 1. Python异常
        sys.excepthook = self._python_exception_hook

        # 2. C层崩溃（如段错误）
        faulthandler.enable(file=open(self.log_dir / "crash_dump.log", "a"))

        # 3. Windows特定：未处理的C++异常
        if sys.platform == "win32":
            self._setup_windows_exception_handler()

        # 4. 程序退出回调
        atexit.register(self._on_exit)

    def _python_exception_hook(self, exc_type, exc_value, exc_traceback):
        """Python异常处理器"""
        if exc_type is KeyboardInterrupt:
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # 记录异常信息
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self._write_crash_report("Python Exception", error_msg)

        # 显示崩溃对话框（可选）
        self._show_crash_dialog(error_msg)

        # 调用原始处理器
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    def _setup_windows_exception_handler(self):
        """Windows异常处理器（处理Access Violation等）"""
        try:
            import ctypes
            import ctypes.wintypes

            # 定义异常处理函数
            @ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p)
            def exception_handler(exception_info):
                try:
                    exc_code = ctypes.c_uint.from_address(
                        exception_info + 4
                    ).value

                    # 写入崩溃日志
                    with open(self.log_dir / "windows_crash.log", "a") as f:
                        f.write(f"[{datetime.now()}] Windows异常代码: 0x{exc_code:08X}\n")
                        f.write("=" * 80 + "\n")

                        # 获取线程信息
                        import threading
                        for thread in threading.enumerate():
                            f.write(f"线程: {thread.name} (ID: {thread.ident})\n")

                        # 获取堆栈（需要dbghelp.dll）
                        self._write_stack_trace(f)

                except:
                    pass

                return 1  # EXCEPTION_EXECUTE_HANDLER

            # 设置异常处理器
            ctypes.windll.kernel32.SetUnhandledExceptionFilter(exception_handler)
        except Exception as e:
            print(f"Windows异常处理器设置失败: {e}")

    def _write_stack_trace(self, file_handle):
        """写入堆栈跟踪（Windows）"""
        try:
            import ctypes
            from ctypes.wintypes import DWORD, HANDLE

            # 使用Win32 API获取堆栈
            process = ctypes.windll.kernel32.GetCurrentProcess()
            thread = ctypes.windll.kernel32.GetCurrentThread()

            # 这里可以扩展，使用StackWalk64等API获取详细堆栈
            file_handle.write("[堆栈跟踪] 需要安装调试器获取详细信息\n")

        except Exception as e:
            file_handle.write(f"获取堆栈失败: {e}\n")

    def _write_crash_report(self, crash_type, error_msg):
        """写入崩溃报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        crash_file = self.log_dir / f"crash_{timestamp}.log"

        with open(crash_file, "w", encoding="utf-8") as f:
            f.write(f"程序崩溃报告\n")
            f.write("=" * 80 + "\n")
            f.write(f"崩溃时间: {datetime.now()}\n")
            f.write(f"崩溃类型: {crash_type}\n")
            f.write("=" * 80 + "\n\n")
            f.write("异常信息:\n")
            f.write(error_msg)
            f.write("\n" + "=" * 80 + "\n\n")

            # 系统信息
            f.write("系统信息:\n")
            f.write(f"平台: {sys.platform}\n")
            f.write(f"Python版本: {sys.version}\n")
            f.write(f"工作目录: {os.getcwd()}\n")
            f.write(f"命令行: {' '.join(sys.argv)}\n")
            f.write(f"PYTHONPATH: {sys.path}\n")

            # 环境变量（部分）
            f.write("\n环境变量:\n")
            for key in ['PATH', 'PYTHONHOME', 'QT_QPA_PLATFORM_PLUGIN_PATH']:
                if key in os.environ:
                    f.write(f"{key}: {os.environ[key][:200]}...\n")

    def _show_crash_dialog(self, error_msg):
        """显示崩溃对话框"""
        try:
            # 使用tkinter显示简单对话框，避免依赖Qt
            import tkinter as tk
            from tkinter import messagebox

            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口

            # 截取错误前几行
            error_preview = "\n".join(error_msg.split("\n")[:10])

            result = messagebox.askyesno(
                "程序崩溃",
                f"程序发生意外错误:\n\n{error_preview}\n\n"
                f"详细日志已保存到: {self.log_dir}\n\n"
                "是否尝试重新启动程序？"
            )

            root.destroy()

            if result:
                self._restart_program()

        except Exception as e:
            print(f"无法显示崩溃对话框: {e}")

    def _restart_program(self):
        """重启程序"""
        python = sys.executable
        subprocess.Popen([python] + sys.argv)
        sys.exit(0)

    def _on_exit(self):
        """程序退出时调用"""
        with open(self.log_dir / "exit.log", "a") as f:
            f.write(f"[{datetime.now()}] 程序退出 (正常或异常)\n")


# 在主程序开头使用
crash_reporter = CrashReporter()