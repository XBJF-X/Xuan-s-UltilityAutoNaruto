"""TaskExecutor - 执行层

负责"运行一个任务"的完整生命周期：接管/交还超时监视器、启停任务线程。
调度器扫描循环决定"执行哪个任务"后，交由 TaskExecutor 真正启动/停止任务；
任务完成信号仍由 BaseTask 的 callback 回到调度器（保持向后兼容）。
"""
import inspect
from typing import Optional


def _request_stop(task, reason: str) -> None:
    """请求任务停止；兼容只接受无参 ``stop()`` 的旧式对象（离线替身 / 第三方实现）。

    用签名判断而不是 ``try/except TypeError``：后者会掩盖任务 ``stop()`` 内部的
    真实 TypeError（那属于 bug，必须暴露）。
    """
    try:
        params = inspect.signature(task.stop).parameters
    except (TypeError, ValueError):
        params = {}
    accepts_reason = any(
        p.kind in (inspect.Parameter.POSITIONAL_ONLY,
                   inspect.Parameter.POSITIONAL_OR_KEYWORD)
        for p in params.values()
    ) or any(p.kind is inspect.Parameter.VAR_POSITIONAL for p in params.values())
    if accepts_reason:
        task.stop(reason)
    else:
        task.stop()


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

    def stop_task(self, task, reason: str = ""):
        """停止任务（抢占 / 调度器停止 / 卡死处理时调用）。

        ``reason`` 取 ``Exceptions.STOP_REASON_*``：任务侧 ``Stop`` 分支据此决定收尾
        动作（卡死类停止 → ``on_stuck`` 冷却重试，避免"下次执行时间仍是过去时刻"
        导致被调度器立刻重跑）。
        """
        if self.watchdog is not None:
            try:
                self.watchdog.detach_task(task)
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"watchdog detach 失败: {e}")
        _request_stop(task, reason)

    def finish_task(self, task):
        """任务结束（完成/停止/超时），交还超时监视器。"""
        if self.watchdog is not None:
            try:
                self.watchdog.detach_task(task)
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"watchdog detach 失败: {e}")
