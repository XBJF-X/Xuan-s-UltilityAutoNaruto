import logging
import threading
import time
from typing import List, Tuple

import uiautomator2

from utils.Base.Control import Control, ControlMode
from utils.Base.Control.MiniTouch import MiniTouch
from utils.Base.Control.U2 import U2


class Clicker:
    def __init__(self, operationer, parent_logger=None):
        """
        初始化连点器
        :param operationer: 操作器实例
        :param parent_logger: 父日志器
        """
        self.logger = parent_logger.getChild("连点器") if parent_logger else logging.getLogger("连点器")
        self.operationer = operationer
        self.config = operationer.config
        self.control_mode = ControlMode(self.config.get_config('控制模式'))
        self.device_serial = self.config.get_config("串口")

        self._stop_event = threading.Event()
        self._threads: List[threading.Thread] = []
        self._threads_lock = threading.Lock()
        self._coordinates: List[Tuple[int, int]] = []
        self._coord_lock = threading.Lock()

    def _create_control_instance(self) -> Control:
        """
        根据当前控制模式创建一个独立的 Control 实例
        :return: Control 子类实例
        :raises: 如果创建失败则抛出异常
        """
        if self.control_mode == ControlMode.MiniTouch:
            return MiniTouch(self.config, self.logger, self.device_serial)
        elif self.control_mode == ControlMode.U2:
            return U2(self.config, self.logger, self.device_serial)
        else:
            # 默认使用 MiniTouch
            return MiniTouch(self.config, self.logger, self.device_serial)

    def start(self):
        """启动点击线程（MiniTouch 使用多点模式，其他使用独立线程模式）"""
        with self._threads_lock:
            # 1. 检查是否存在存活线程
            if any(t.is_alive() for t in self._threads):
                self.logger.debug("点击线程已启动，忽略重复启动请求")
                return

            # 2. 确保停止事件已清除，避免新线程立即退出
            self._stop_event.clear()

            # 3. 清理已结束的线程对象（残留引用）
            self._threads.clear()

            # 4. 复制并正则化当前坐标列表
            with self._coord_lock:
                coords_copy = self._coordinates.copy()
            coords = [self.operationer.device.regularize_coordinate(coord[0], coord[1]) for coord in
                coords_copy]

            if not coords:
                self.logger.warning("坐标列表为空，无法启动点击线程")
                return

            # 5. 根据控制模式创建并启动线程
            if self.control_mode == ControlMode.MiniTouch:
                thread = threading.Thread(
                    target=self._minitouch_click_worker,
                    args=(coords,),
                    daemon=True
                )
                thread.start()
                self._threads.append(thread)
                self.logger.debug(f"已启动 MiniTouch 多点连点线程，共 {len(coords)} 个坐标")
            elif self.control_mode == ControlMode.U2:
                for x, y in coords:
                    thread = threading.Thread(
                        target=self._u2_worker,
                        args=(x, y),
                        daemon=True
                    )
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
        """更新坐标列表（需要外部先调用 stop，再调用 start 才能生效）"""
        with self._coord_lock:
            self._coordinates = coordinates.copy()

    def _u2_worker(self, x: int, y: int):
        """
        单个坐标的循环点击线程
        每个线程独立创建并管理自己的 Control 实例
        """
        try:
            control = uiautomator2.connect(self.device_serial)

            while not self._stop_event.is_set():
                try:
                    control.click(x, y)
                except Exception as e:
                    self.logger.error(f"点击 ({x},{y}) 失败: {e}")
        except Exception as e:
            self.logger.error(f"创建 Control 实例失败: {e}")
        finally:
            self.logger.debug(f"坐标 ({x},{y}) 的点击线程结束")

    def _minitouch_click_worker(self, coords: List[Tuple[int, int]]):
        """
        MiniTouch 专用：多点同时点击工作线程
        """
        control = None
        try:
            control = self.operationer.device.control_manager.current_control
            if not control.ready:
                self.logger.error("MiniTouch 实例未就绪，无法启动多点连点")
                return

            points = [[x, y] for x, y in coords]
            self.logger.debug(f"MiniTouch 多点连点线程启动，坐标数量: {len(points)}")

            while not self._stop_event.is_set():
                try:
                    control.multi_tap(points, pressure=100, duration=0.08)
                    time.sleep(0.12)
                except Exception as e:
                    self.logger.error(f"MiniTouch 多点点击失败: {e}")
                    time.sleep(0.1)
        except Exception as e:
            self.logger.error(f"创建 MiniTouch 实例失败: {e}")
        finally:
            try:
                control.up_all_contacts()
            except Exception as e:
                self.logger.warning(f"抬起所有触点失败: {e}")
            self.logger.debug("MiniTouch 多点连点线程结束")
