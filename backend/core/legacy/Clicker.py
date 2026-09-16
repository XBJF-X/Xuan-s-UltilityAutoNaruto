import logging
import threading
import time
from typing import List, Tuple

import uiautomator2

from backend.core.legacy.Control import Control, ControlMode
from backend.core.legacy.Control import touch_residue
from backend.core.legacy.Control.U2 import U2

MINITOUCH_MAX_LIFETIME = 180
"""
MiniTouch服务在连点器状态下能存活的最长时间，防止MuMu自动杀死服务
同时减少高频启动服务导致的性能浪费
"""


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

        self.last_minitouch_create_time = time.perf_counter()

        self.running = False

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
            # 懒导入：避免未安装 minidevice 时阻塞 Operationer/Clicker 导入链
            from backend.core.legacy.Control.MiniTouch import MiniTouch
            return MiniTouch(self.config, self.logger, self.device_serial)
        elif self.control_mode == ControlMode.U2:
            return U2(self.config, self.logger, self.device_serial)
        else:
            # 默认使用 MiniTouch
            from backend.core.legacy.Control.MiniTouch import MiniTouch
            return MiniTouch(self.config, self.logger, self.device_serial)

    def start(self):
        """启动点击线程（MiniTouch 使用多点模式，其他使用独立线程模式）"""
        with self._threads_lock:
            # 1. 检查是否存在存活线程
            if self.running:
                self._threads = [t for t in self._threads if t.is_alive()]
                self.running = len(self._threads) > 0
            if self.running:
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
            self.running = True

    def stop(self):
        """停止所有点击线程"""
        self.logger.debug("正在停止所有点击线程...")
        self._stop_event.set()

        with self._threads_lock:
            alive_threads: List[threading.Thread] = []
            for thread in self._threads:
                thread.join(timeout=2)
                if thread.is_alive():
                    self.logger.warning("某个点击线程未及时退出")
                    alive_threads.append(thread)

            # 若仍有线程存活，保持 stop 事件为 set，避免线程继续点击
            self._threads = alive_threads
            if alive_threads:
                self.running = True
                self.logger.warning(f"仍有 {len(alive_threads)} 个点击线程未退出，将继续等待其自行结束")
                return

            self._threads.clear()

        self._stop_event.clear()
        self.running = False
        self.logger.debug("所有点击线程已停止")

    def wait_stopped(self, timeout: float = 3.0) -> bool:
        """等待所有点击线程真正退出（不再发包）。

        停止调度器时必须先等连点线程收尾、再释放控制实例：否则在途的
        ``multi_tap`` 批次会被"抬起命令 + 杀进程"打断，设备端 slot 永久停在
        按下态（v0.17.46 修复的根因之一）。

        :param timeout: 最长等待秒数
        :return: True=线程已全部退出
        """
        deadline = time.perf_counter() + max(float(timeout), 0.0)
        while True:
            with self._threads_lock:
                self._threads = [t for t in self._threads if t.is_alive()]
                alive = len(self._threads)
            if alive == 0:
                self.running = False
                return True
            if time.perf_counter() >= deadline:
                self.running = True
                self.logger.warning(f"等待连点线程退出超时，仍有 {alive} 个线程在运行")
                return False
            time.sleep(0.05)

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

    def _refresh_minitouch_instance(self, control_manager) -> bool:
        """刷新 MiniTouch 实例（防模拟器杀服务 + 降低高频启停开销）。

        顺序至关重要（v0.17.49 修正）：**先抬起并释放旧实例，再新建实例**。
        设备端只有一个 minitouch 进程，新建实例（``MiniTouchCore.__init__``）与
        释放旧实例（``MiniTouchCore.stop``）都会 ``pidof minitouch`` 把它 kill；
        若先建新实例再释放旧实例，旧实例的释放会把**新实例刚启动**的设备端进程
        一起杀掉，下一次点击即 WinError 10053 → 每点一次就重建一次
        （现场日志：每 6~7 秒一轮「重连 + 残留清理」）。

        :return: True=实例已刷新且触点已确认抬起
        """
        old_control = control_manager.get_current_control()

        lift_supported = (old_control is not None
                          and hasattr(old_control, "up_all_contacts"))
        lifted = True
        if old_control is not None:
            if lift_supported:
                try:
                    # up_all_contacts() 内部已在抬起失败时走裸 evdev 兜底，
                    # 这里不再重复清理（否则一次刷新要跑两轮秒级 adb 命令）
                    lifted = bool(old_control.up_all_contacts())
                except Exception as e:
                    lifted = False
                    self.logger.warning(f"刷新前抬起触点失败: {e}")
            else:
                # 无法在旧实例上抬起（不支持该接口）→ 交给裸 evdev 兜底
                lifted = False
            try:
                old_control.release()
            except Exception as e:
                self.logger.warning(f"释放旧 MiniTouch 实例失败: {e}")

        new_control = control_manager.create_control_instance()
        if new_control is None:
            self.logger.warning(
                "MiniTouch 刷新失败（旧实例已释放），等待下一次重建或调度器重启")
        else:
            control_manager.replace_current_control(new_control)
            self.last_minitouch_create_time = time.perf_counter()

        if not lifted and not lift_supported:
            if not touch_residue.clean_stale_contacts(
                    self.device_serial, logger=self.logger,
                    reason="MiniTouch 刷新前抬起失败"):
                self.logger.warning(
                    "刷新前抬起触点失败且兜底清理未成功，设备端可能残留按下中的触点")
        return lifted

    def _minitouch_click_worker(self, coords: List[Tuple[int, int]]):
        """
        MiniTouch 专用：多点同时点击工作线程
        """
        control = None
        try:
            control_manager = self.operationer.device.control_manager
            # 任务启动边界：补执行此前挂起的残留清理（重连热路径为不阻塞连点而挂起，
            # v0.17.49）；无挂起时零开销、不访问设备，不影响连点节奏
            touch_residue.flush_pending_cleanup(
                self.device_serial, logger=self.logger,
                reason="连点启动前补清理挂起的残留触点")
            if time.perf_counter() - self.last_minitouch_create_time > MINITOUCH_MAX_LIFETIME:
                if not self._refresh_minitouch_instance(control_manager):
                    self.logger.warning("MiniTouch 刷新期间触点未确认抬起，继续执行连点")

            control = control_manager.get_current_control()
            if not control or not control.ready:
                self.logger.error("MiniTouch 实例未就绪，无法启动多点连点")
                return
            points = [[x, y] for x, y in coords]
            self.logger.debug(f"MiniTouch 多点连点线程启动，坐标数量: {len(points)}")

            while not self._stop_event.is_set():
                try:
                    active_control = control_manager.get_current_control()
                    if active_control and active_control is not control and active_control.ready:
                        control = active_control
                    if not control.ready:
                        self.logger.warning("MiniTouch 实例已失效，结束多点连点线程")
                        break
                    # 防御：当前控制实例可能被替换为非 MiniTouch（如 U2），
                    # 其不具备 multi_tap 方法，直接调用会抛 AttributeError 刷屏
                    if not hasattr(control, "multi_tap"):
                        self.logger.error(
                            f"当前控制实例({type(control).__name__})不支持多点连点(multi_tap)，结束连点线程")
                        break

                    control.multi_tap(points, pressure=100, duration=0.08)
                    time.sleep(0.15)
                except Exception as e:
                    self.logger.error(f"MiniTouch 多点点击失败: {e}")
                    time.sleep(0.1)
        except Exception as e:
            self.logger.error(f"创建 MiniTouch 实例失败: {e}")
        finally:
            # 无条件尝试抬起：实例可能已被 release/替换（ready=False），旧实现会
            # 直接跳过这一步，触点就永久留在设备端（v0.17.46 修复）
            try:
                if control is not None and hasattr(control, "up_all_contacts"):
                    if not control.up_all_contacts():
                        self.logger.warning(
                            "抬起全部触点未成功，设备端可能残留按下中的触点；"
                            "若出现「一次点击触发多个坐标」的异常，请重启模拟器后再反馈")
            except Exception as e:
                self.logger.warning(f"抬起所有触点失败: {e}")
            self.logger.debug("MiniTouch 多点连点线程结束")
