"""TaskExecutor - 执行层

负责"运行一个任务"的完整生命周期：接管/交还超时监视器、启停任务线程。
调度器扫描循环决定"执行哪个任务"后，交由 TaskExecutor 真正启动/停止任务；
任务完成信号仍由 BaseTask 的 callback 回到调度器（保持向后兼容）。
"""
from typing import Optional


class TaskExecutor:
    """封装单任务的启动/停止与超时监视器接管。"""

    def __init__(self, watchdog=None, logger=None):
        self.watchdog = watchdog
        self.logger = logger

    def set_watchdog(self, watchdog):
        self.watchdog = watchdog

    def start_task(self, task):
        """启动任务：将超时监视器交给任务后开始执行线程。"""
        if self.watchdog is not None:
            try:
                self.watchdog.attach_task(task)
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"watchdog attach 失败: {e}")
        task.run()

    def stop_task(self, task):
        """停止任务（抢占 / 调度器停止 / 卡死处理时调用）。"""
        if self.watchdog is not None:
            try:
                self.watchdog.detach_task(task)
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"watchdog detach 失败: {e}")
        task.stop()

    def finish_task(self, task):
        """任务结束（完成/停止/超时），交还超时监视器。"""
        if self.watchdog is not None:
            try:
                self.watchdog.detach_task(task)
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"watchdog detach 失败: {e}")
