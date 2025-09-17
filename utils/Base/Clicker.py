import logging
import threading
from logging import Logger
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor


class Clicker:
    def __init__(self, operationer, max_workers=7, parent_logger: Logger | str = ""):
        if isinstance(parent_logger, str):
            self.logger = logging.getLogger("连点器")
        else:
            self.logger = parent_logger.getChild("连点器")
        self.operationer = operationer
        self.coordinates: List[Tuple[int, int]] = []
        self._stop_event = threading.Event()
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self._thread = None  # 初始化时不启动线程，等待start()调用

    def start(self):
        """Start the clicker (reinitialize executor if necessary)."""
        self.logger.debug("启动连点器")
        if self.executor._shutdown:
            self.executor = ThreadPoolExecutor(max_workers=self.max_workers)  # Reinitialize the executor
        if self._thread is not None and self._thread.is_alive():
            return  # Already running, do nothing
        self._stop_event.clear()  # Reset the stop signal
        self._thread = threading.Thread(target=self._click_loop, daemon=True)  # Create the thread
        self._thread.start()  # Start the thread

    def stop(self):
        """停止连点器（终止任务循环，取消未完成任务）"""
        self.logger.debug("停止连点器")
        self._stop_event.set()  # 触发停止信号
        # 等待任务循环线程终止
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=0.1)
            if self._thread.is_alive():
                self.logger.warning("任务循环线程未能正常终止")
        # 取消未完成的任务
        self.executor.shutdown(wait=False)
        self._thread = None

    def update_coordinates(self, coordinates: List[Tuple[int, int]]):
        """更新点击坐标（线程安全）"""
        self.logger.debug(f"更新点击坐标列表: {coordinates}")
        with threading.Lock():  # 加锁保护共享资源
            self.coordinates = coordinates.copy()

    def _click_worker(self, x, y):
        """单次点击任务（执行前检查停止信号）"""
        if self._stop_event.is_set():
            return
        # self.logger.debug("点击坐标: ({}, {})".format(x, y))
        self.operationer.device.click(x, y)

    def _click_loop(self):
        """点击循环（仅在运行状态下执行，退出后线程终止）"""
        while not self._stop_event.is_set():
            # 线程安全地读取坐标（避免迭代时被修改）
            with threading.Lock():
                coordinates = self.coordinates.copy()  # 复制一份用于迭代

            self.logger.debug(f"点击循环执行")

            for x, y in coordinates:
                if self._stop_event.is_set():
                    break  # 收到停止信号，终止本轮任务提交
                self.executor.submit(self._click_worker, x, y)

            # 控制循环频率（减少CPU占用，同时保证响应速度）
            if not self._stop_event.wait(0.2):
                continue
