import threading
import uiautomator2 as u2
from typing import List, Tuple
import logging


class Clicker:
    def __init__(self, operationer, parent_logger=None):
        self.logger = parent_logger.getChild("连点器") if parent_logger else logging.getLogger("连点器")
        self.operationer = operationer
        self.device_serial = self.operationer.config.get_config("串口")
        self._stop_event = threading.Event()
        self._threads: List[threading.Thread] = []
        self._threads_lock = threading.Lock()  # 保护线程列表
        self._coordinates: List[Tuple[int, int]] = []
        self._coord_lock = threading.Lock()  # 保护坐标列表

    def start(self):
        """启动所有坐标的独立点击线程（如果已有线程在运行，则忽略）"""
        with self._threads_lock:
            # 检查是否有任何线程还活着
            if any(t.is_alive() for t in self._threads):
                self.logger.debug("点击线程已启动，忽略重复启动请求")
                return

            # 停止并清理可能已经结束但未移除的线程
            self._threads.clear()

            # 获取当前坐标快照
            with self._coord_lock:
                coords = self._coordinates.copy()

            # 为每个坐标创建独立线程
            for x, y in coords:
                x_fixed, y_fixed = self.operationer.device.regularize_coordinate(x, y)
                thread = threading.Thread(target=self._click_worker, args=(x_fixed, y_fixed), daemon=True)
                thread.start()
                self._threads.append(thread)
            self.logger.debug(f"已启动 {len(coords)} 个点击线程")

    def stop(self):
        """停止所有点击线程"""
        self.logger.debug("正在停止所有点击线程...")
        self._stop_event.set()

        with self._threads_lock:
            for thread in self._threads:
                thread.join(timeout=1)
                if thread.is_alive():
                    self.logger.warning("某个点击线程未及时退出")
            self._threads.clear()
        self._stop_event.clear()
        self.logger.debug("所有点击线程已停止")

    def update_coordinates(self, coordinates: List[Tuple[int, int]]):
        """更新坐标列表（会重新启动线程）"""
        with self._coord_lock:
            self._coordinates = coordinates.copy()

    def _click_worker(self, x, y):
        """单个坐标的循环点击线程（实现不变）"""
        # 独立连接设备
        try:
            device = u2.connect(self.device_serial)
        except Exception as e:
            self.logger.error(f"无法连接设备 {self.device_serial}: {e}")
            return

        self.logger.debug(f"坐标 ({x},{y}) 的点击线程启动")
        try:
            while not self._stop_event.is_set():
                try:
                    device.click(x, y)
                except Exception as e:
                    self.logger.error(f"点击 ({x},{y}) 失败: {e}")
                    # 可根据需要短暂休眠，避免疯狂报错
                    # time.sleep(0.1)
        finally:
            self.logger.debug(f"坐标 ({x},{y}) 的点击线程结束")
