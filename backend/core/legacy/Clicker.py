"""连点器门面（对外 API 保持不变）。

重构要点（v0.17.60）
-------------------
旧实现每个 ``Operationer`` 各持一个 ``Clicker``，``start()`` 新建线程、
``stop()`` join 线程，并且每次 start 都可能重建设备端 minitouch 服务。
任务里 ``start/stop`` 会被调用几十次，于是"线程 + 设备端进程"被反复建销，
每个触点周期还各自发包一次——这正是"性能弱、耗线程"的来源。

现在 ``Clicker`` 只是**门面**：真正的执行体是按设备串口全局唯一的
:class:`~backend.core.legacy.Control.clicker_engine.ClickEngine`（一条长驻
线程、集中批量提交）。本类保持 ``update_coordinates`` / ``start`` / ``stop`` /
``wait_stopped`` / ``running`` 的原有语义，因此所有任务代码无需改动。
"""
import logging
import threading
import time
from typing import List, Optional, Tuple

from backend.core.legacy.Control import resolve_control_mode
from backend.core.legacy.Control.clicker_engine import (
    ClickerSession,
    get_click_engine,
)


class Clicker:
    """连点器门面：把调用转交给按设备全局唯一的连点引擎。"""

    def __init__(self, operationer, parent_logger=None):
        """
        初始化连点器
        :param operationer: 操作器实例
        :param parent_logger: 父日志器
        """
        self.logger = parent_logger.getChild("连点器") if parent_logger else logging.getLogger("连点器")
        self.operationer = operationer
        self.config = operationer.config
        # U2 已弃用：存量配置里的 1 归一化为 MiniTouch（见 resolve_control_mode）
        self.control_mode = resolve_control_mode(
            self.config.get_config('控制模式'), self.logger)
        self.device_serial = self.config.get_config("串口")

        self.running = False

        self._engine = None
        self._session: Optional[ClickerSession] = None
        self._state_lock = threading.Lock()
        self._coordinates: List[Tuple[int, int]] = []
        self._coord_lock = threading.Lock()
        # 停止等待：引擎线程长驻，会话失效即视为"已停止"
        self._stopped_event = threading.Event()
        self._stopped_event.set()

    # ------------------------- 引擎与会话 -------------------------
    def _get_engine(self):
        """取（或创建）本设备共享的连点引擎。"""
        device = getattr(self.operationer, "device", None)
        if device is None:
            raise RuntimeError("操作器未持有设备实例，无法启动连点")
        return get_click_engine(device, self.device_serial, self.logger)

    def _current_session(self) -> Optional[ClickerSession]:
        with self._state_lock:
            return self._session

    # ------------------------- 对外 API -------------------------
    def start(self):
        """启动连点（注册/接管全局引擎的当前连点会话）。"""
        with self._coord_lock:
            coords_copy = self._coordinates.copy()
        if not coords_copy:
            self.logger.warning("坐标列表为空，无法启动点击线程")
            return

        with self._state_lock:
            existing = self._session
            if existing is not None and existing.running:
                self.logger.debug("点击线程已启动，忽略重复启动请求")
                return
            try:
                engine = self._get_engine()
            except Exception as e:
                self.logger.error(f"获取连点引擎失败: {e}")
                return
            self._engine = engine
            if existing is None:
                session = engine.register()
                self._session = session
            else:
                session = existing
                engine.promote(session)
            session.begin(coords_copy)
            self._stopped_event.clear()
            self.running = True
        self.logger.debug(
            f"已启动 MiniTouch 多点连点（共享引擎），共 {len(coords_copy)} 个坐标")

    def stop(self):
        """停止连点：会话立即失效，引擎线程保留待下次复用。"""
        with self._state_lock:
            session = self._session
            if session is None:
                self.running = False
                self._stopped_event.set()
                return
            session.stop()
            engine = self._engine
            self.running = False
            self._stopped_event.set()
        if engine is not None:
            engine.unregister(session)
        self.logger.debug("连点已停止（引擎线程保留复用）")

    def wait_stopped(self, timeout: float = 3.0) -> bool:
        """等待连点真正停下（不再发包）。

        引擎线程长驻，因此这里等待的是"本会话不再投递点击"而不是线程退出；
        会话失效是即时的，唯一的延迟来自在途批次（设备端已在执行的命令流，
        上限见 ``_BATCH_TARGET_SECONDS``）。

        :param timeout: 最长等待秒数
        :return: True=已停止
        """
        deadline = time.perf_counter() + max(float(timeout), 0.0)
        while time.perf_counter() < deadline:
            if self._stopped_event.is_set():
                self.running = False
                return True
            time.sleep(0.02)
        if self._stopped_event.is_set():
            self.running = False
            return True
        self.running = True
        self.logger.warning("等待连点停止超时")
        return False

    def update_coordinates(self, coordinates: List[Tuple[int, int]]):
        """更新坐标列表。

        与旧实现不同：**运行中更新会立即生效**（旧实现需要先 stop 再 start）。
        当前会话直接替换坐标，引擎下一批即按新坐标投递。
        """
        coords = [(int(x), int(y)) for x, y in coordinates]
        with self._coord_lock:
            self._coordinates = coords
        session = self._current_session()
        if session is not None:
            session.set_coordinates(coords)
