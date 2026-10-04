"""连点器执行引擎（全局单例 + 长驻线程 + 集中批量提交）。

旧实现的三处浪费
----------------
1. **每个任务一个 Clicker、每次 start 新建线程**：``Operationer`` 各持一个
   ``Clicker``，``start()`` 起线程、``stop()`` join 线程。一个任务里
   ``start/stop`` 会调用几十次（见 ``Task/WuChaBieYuXuanSai.py`` 等），
   线程对象反复创建销毁，且每次都要重新进入循环、重新校验控制实例。
2. **设备端服务被反复杀掉重启**：``MiniTouch`` 的启停都会 ``pidof minitouch``
   + kill，一次 start/stop 就是一轮设备端进程与 socket 的建销。
3. **每个触点周期单独发包**：``multi_tap`` 一轮一个 ``publish``，而
   ``sendall + recv`` 每次都要一次 Python 侧往返，连点速度被往返次数限住。

本模块的做法
------------
* **全局单例**：按设备串口（``serial``）维护**唯一** ``ClickEngine``，
  同一台设备上的所有任务共享同一个连点执行体与同一条设备端 minitouch 连接
  （``get_click_engine`` / ``shutdown_device_clickers``）。
* **长驻线程**：每个引擎只有**一条**工作线程，跨越所有任务的 start/stop 存活，
  空闲时阻塞等待；任务切换不再创建/销毁线程。
* **会话语义**：每次 ``start()`` 注册一个 :class:`ClickerSession`，同一时刻只有
  一个"当前连点会话"在投递点击（后注册者接管，先前会话自动失效），因此
  "多个任务同时连点导致坐标互相打架"不会发生。
* **集中批量提交**：与设备端无关的构造逻辑放在
  :mod:`backend.core.legacy.Control.touch_batch`，一次 ``publish`` 投递多个
  点击周期，把 N 次往返压成 1 次；Python 侧按设备端实际耗时补偿，节奏更稳。
"""
import logging
import threading
import time
from typing import Dict, List, Optional, Sequence, Tuple

from backend.core.legacy.Control import touch_batch, touch_residue

# 设备端 minitouch 服务在连点状态下允许存活的最长时间（秒）。
# 超过后主动重建：MuMu 会清理长时间无交互的服务，且重建能顺带刷新 socket。
MINITOUCH_MAX_LIFETIME = 180

# 空闲等待轮询间隔（秒）：仅在没有连点会话时使用，开销可忽略
_IDLE_POLL_INTERVAL = 0.25

# 停止响应粒度（秒）：等待期间以该粒度检查停止信号，保证停止及时
_STOP_POLL_INTERVAL = 0.01

# 默认连点周期（秒）：与旧实现 time.sleep(0.15) + duration 0.08 的节奏一致
DEFAULT_TAP_INTERVAL_SECONDS = 0.23
_MIN_TAP_INTERVAL_SECONDS = 0.02
_MAX_TAP_INTERVAL_SECONDS = 2.0

# 单周期按下保持时长（毫秒）：与旧实现 multi_tap(duration=0.08) 等价
_TAP_HOLD_MS = 80

# 每批批量提交的目标设备端工作时长（秒）：越大则往返次数越少、停止延迟越大。
# 0.5s 是折中：往返次数比"一轮一发"少 1~2 个数量级，同时停止最多多等 0.5s。
_BATCH_TARGET_SECONDS = 0.5

# 全局设置项（[助手设置] 连点间隔），单位毫秒；留空/非法时用默认值
_SETTING_SECTION = "助手设置"
_SETTING_TAP_INTERVAL_MS = "连点间隔"

_engines_lock = threading.Lock()
_engines: Dict[str, "ClickEngine"] = {}

_logger = logging.getLogger("连点器")


def normalize_serial(serial) -> str:
    """串口归一化：全角冒号换半角，去首尾空白。"""
    return str(serial or "").strip().replace("：", ":")


def _resolve_tap_interval_seconds() -> float:
    """读取全局设置里的连点间隔（毫秒），失败/非法时用默认值并夹到安全区间。"""
    ms: Optional[float] = None
    try:
        from backend.core.settings_store import SettingsService
        raw = SettingsService().get(_SETTING_SECTION, _SETTING_TAP_INTERVAL_MS) or ""
        value = float(str(raw).strip())
        # 兼容"填成秒"的写法：< 5 视为秒（例如填 0.3 秒），否则视为毫秒
        ms = value * 1000.0 if 0 < value < 5 else value
    except Exception:
        ms = None
    seconds = DEFAULT_TAP_INTERVAL_SECONDS if ms is None else ms / 1000.0
    return max(_MIN_TAP_INTERVAL_SECONDS, min(seconds, _MAX_TAP_INTERVAL_SECONDS))


def get_click_engine(device, serial: str, logger=None) -> "ClickEngine":
    """取（或创建）某设备的全局连点引擎。

    :param device: ``Device`` 实例（引擎据此取控制实例、转换坐标）
    :param serial: 设备串口（引擎单例的键）
    :param logger: 可选日志器
    """
    key = normalize_serial(serial)
    if not key:
        raise ValueError("设备串口为空，无法创建连点引擎")
    with _engines_lock:
        engine = _engines.get(key)
        if engine is None or not engine.alive:
            engine = ClickEngine(device, key, logger)
            _engines[key] = engine
        else:
            # 同一串口复用引擎：只更新设备引用（调度器重建 Device 后仍指向新实例）
            engine.device = device
        return engine


def shutdown_device_clickers(serial: str, logger=None):
    """关闭并移除某设备的连点引擎（设备/调度器释放时调用）。

    只应在对应设备的任务确实停下后调用；调用后该串口的连点会话全部失效。
    """
    key = normalize_serial(serial)
    with _engines_lock:
        engine = _engines.pop(key, None)
    if engine is not None:
        engine.shutdown()
        (logger or _logger).debug(f"[{key}] 连点引擎已关闭")


def shutdown_all_clickers(logger=None):
    """关闭所有连点引擎（程序/调度器整体停止时调用）。"""
    with _engines_lock:
        engines = list(_engines.values())
        _engines.clear()
    for engine in engines:
        engine.shutdown()


class ClickerSession:
    """一次连点会话（``Clicker.start()`` ~ ``Clicker.stop()``）。

    坐标与"是否仍在连点"由会话自己持有，引擎只负责挑选当前会话并投递点击，
    因此任务侧的 ``update_coordinates`` / ``running`` 语义与旧实现一致。
    """

    __slots__ = ("coords", "stop_event", "running", "_coords_lock")

    def __init__(self):
        self.coords: List[Tuple[int, int]] = []
        self.stop_event = threading.Event()
        self.running = False
        self._coords_lock = threading.Lock()

    def set_coordinates(self, coords: Sequence[Tuple[int, int]]):
        with self._coords_lock:
            self.coords = [(int(x), int(y)) for x, y in coords]

    def snapshot(self) -> List[Tuple[int, int]]:
        with self._coords_lock:
            return list(self.coords)

    def begin(self, coords: Optional[Sequence[Tuple[int, int]]] = None):
        """开始（或延续）连点：清掉旧的停止信号并置为运行中。"""
        if coords is not None:
            self.set_coordinates(coords)
        self.stop_event.clear()
        self.running = True

    def stop(self):
        """停止连点：置停止信号并立即失效（引擎下一轮不再投递本会话）。"""
        self.stop_event.set()
        self.running = False


class ClickEngine:
    """单设备的连点执行体：一条长驻线程 + 多个会话。

    线程生命周期与"连点是否在跑"解耦——引擎只在设备/调度器释放时退出，
    任务反复 start/stop 不再付出线程与设备端服务的启停代价。
    """

    def __init__(self, device, serial: str, logger=None):
        self.device = device
        self.serial = normalize_serial(serial)
        self.logger = (logger or _logger).getChild("ClickEngine")
        self._lock = threading.RLock()
        self._sessions: List[ClickerSession] = []
        self._current: Optional[ClickerSession] = None
        self._shutdown_event = threading.Event()
        # 当前控制实例的"首次见到"时刻，用于 MINITOUCH_MAX_LIFETIME 刷新判定
        self._control_seen: Optional[object] = None
        self._control_seen_at: float = 0.0
        self._thread = threading.Thread(
            target=self._run, name=f"click-engine-{self.serial}", daemon=True)
        self._thread.start()

    # ------------------------- 生命周期 -------------------------
    @property
    def alive(self) -> bool:
        return not self._shutdown_event.is_set() and self._thread.is_alive()

    def shutdown(self, timeout: float = 3.0):
        """停止引擎：发出退出信号、失效全部会话并等待线程收尾。"""
        self._shutdown_event.set()
        self._current = None
        with self._lock:
            for session in self._sessions:
                session.stop()
            self._sessions.clear()
        # 线程在设备端批量命令执行完（最多一个批次的保持时长）后退出
        self._thread.join(timeout=timeout)
        if self._thread.is_alive():
            self.logger.warning("连点引擎线程未在超时内退出，将在其自然结束后回收")

    # ------------------------- 会话管理 -------------------------
    def register(self) -> ClickerSession:
        """注册新会话并接管为当前连点会话。"""
        session = ClickerSession()
        with self._lock:
            self._sessions.append(session)
            self._current = session
        return session

    def unregister(self, session: ClickerSession):
        """注销会话；若是当前会话则同时让出当前会话位置。"""
        with self._lock:
            if session in self._sessions:
                self._sessions.remove(session)
            if self._current is session:
                self._current = None
                self._promote_next_locked()

    def promote(self, session: ClickerSession):
        """把某会话提升为当前连点会话（后 start 的任务接管）。"""
        with self._lock:
            if session not in self._sessions:
                self._sessions.append(session)
            self._current = session

    def _promote_next_locked(self):
        """当前会话让出后，把还在运行的会话（最近注册的）扶正。"""
        for session in reversed(self._sessions):
            if session.running:
                self._current = session
                return
        self._current = None

    def current_session(self) -> Optional[ClickerSession]:
        with self._lock:
            session = self._current
            if session is not None and not session.running:
                self._promote_next_locked()
                session = self._current
            return session

    # ------------------------- 工作线程 -------------------------
    def _run(self):
        self.logger.debug(f"[{self.serial}] 连点引擎线程已启动（长驻，跨任务复用）")
        try:
            while not self._shutdown_event.is_set():
                session = self.current_session()
                if session is None:
                    self._shutdown_event.wait(_IDLE_POLL_INTERVAL)
                    continue
                try:
                    self._run_session(session)
                except Exception as e:
                    self.logger.error(f"连点执行异常: {e}")
                    self._sleep_interruptible(0.1)
        finally:
            self.logger.debug(f"[{self.serial}] 连点引擎线程已退出")

    def _run_session(self, session: ClickerSession):
        """把某个会话的坐标持续连点到会话停止为止。"""
        control = self._resolve_control()
        if control is None:
            self.logger.error("MiniTouch 实例未就绪，无法启动多点连点")
            session.running = False
            return
        self._note_control(control)
        if self._maybe_refresh(control):
            control = self._resolve_control()
            if control is None:
                self.logger.error("MiniTouch 刷新后仍不可用，结束本次连点")
                session.running = False
                return
        self.logger.debug(f"MiniTouch 多点连点开始，坐标数量: {len(session.snapshot())}")
        try:
            self._click_loop(session, control)
        finally:
            # 无条件尝试抬起：实例可能已被 release/替换（ready=False），旧实现会
            # 直接跳过这一步，触点就永久留在设备端（v0.17.46 修复）
            try:
                active = self._resolve_control() or control
                if hasattr(active, "up_all_contacts"):
                    if not active.up_all_contacts():
                        self.logger.warning(
                            "抬起全部触点未成功，设备端可能残留按下中的触点；"
                            "若出现「一次点击触发多个坐标」的异常，请重启模拟器后再反馈")
            except Exception as e:
                self.logger.warning(f"抬起所有触点失败: {e}")
            self.logger.debug("本次连点会话结束")

    def _click_loop(self, session: ClickerSession, control):
        """批量投递点击周期的主循环。

        一个批次 = ``cycles`` 个点击周期拼成的单条命令流（一次 ``send``），
        批次内由设备端顺序执行；批次之间按 ``interval`` 扣除设备端已耗时后的
        余量休眠，保持连点节奏。
        """
        interval = _resolve_tap_interval_seconds()
        # 简化模型：一个周期 = 保持 hold + 间隔 interval，取整为毫秒
        interval_ms = max(0, int(round(interval * 1000)))
        # 批量大小由"目标批量时长"决定（而不是由间隔反推）：间隔越小、批量越大，
        # 这样无论用户把间隔调快调慢，每批的设备端工作量都稳定在 BATCH_TARGET 附近，
        # 停止响应延迟可控；同时保证每批至少 2 个周期，"集中批量提交"始终生效。
        cycles = max(
            2,
            min(int(round(_BATCH_TARGET_SECONDS / max(interval, 1e-3))),
                touch_batch.MAX_CYCLES_PER_PUBLISH),
        )
        batch_span_seconds = cycles * interval
        expected_control = control
        last_refresh = time.perf_counter()
        last_tap_start = time.perf_counter()
        self.logger.debug(
            f"连点参数：周期 {interval * 1000:.0f}ms（保持 {_TAP_HOLD_MS}ms），"
            f"每批 {cycles} 个周期，每批耗时约 {batch_span_seconds * 1000:.0f}ms")

        while not session.stop_event.is_set() and not self._shutdown_event.is_set():
            control, last_refresh, tapped = self._tap_once(
                session, expected_control, last_refresh, cycles, interval_ms)
            expected_control = control
            if not tapped:
                self._sleep_interruptible(0.1)
                continue
            # 扣除本批设备端已执行的时间，补足剩余间隔
            remaining = batch_span_seconds - (time.perf_counter() - last_tap_start)
            if remaining > 0:
                self._sleep_interruptible(remaining)
            last_tap_start = time.perf_counter()

    def _tap_once(self, session: ClickerSession, control, last_refresh: float,
                  cycles: int, interval_ms: int):
        """投递一个批次。返回 ``(control, last_refresh, 是否已投递)``。"""
        active = self._resolve_control()
        if active is None:
            self.logger.warning("MiniTouch 实例已失效，结束多点连点")
            session.running = False
            return control, last_refresh, False
        if active is not control:
            # 控制实例被替换（连点刷新 / 模式切换）：按新实例继续
            self._note_control(active)
            control = active
            last_refresh = time.perf_counter()

        if not (hasattr(control, "tap_command_batch") and hasattr(control, "convert_point")):
            # 防御：控制实例可能被替换为非 MiniTouch（如历史遗留 U2），
            # 其不具备批量提交/坐标转换能力，直接调用会抛 AttributeError 刷屏
            self.logger.error(
                f"当前控制实例({type(control).__name__})不支持多点连点批量提交，结束连点")
            session.running = False
            return control, last_refresh, False

        points = self._prepare_points(control, session)
        if not points:
            self.logger.warning("坐标列表为空，暂停连点等待新坐标")
            self._sleep_interruptible(0.1)
            return control, last_refresh, False

        command, _delay_ms = touch_batch.build_tap_batch(
            points, pressure=100, hold_ms=_TAP_HOLD_MS,
            cycles=cycles, interval_ms=interval_ms)
        try:
            ok = control.tap_command_batch(session.snapshot(), command)
        except Exception as e:
            self.logger.error(f"MiniTouch 多点点击失败: {e}")
            self._sleep_interruptible(0.1)
            return control, last_refresh, False
        if not ok:
            # 连接断开（tap_command_batch 内部已尝试重建），下一轮按新实例继续
            return control, last_refresh, False
        return control, last_refresh, True

    def _prepare_points(self, control, session: ClickerSession) -> List[List[int]]:
        """取当前坐标 → 正则化 → 旋转转换 → 按最大触点数裁剪。"""
        raw = session.snapshot()
        if not raw:
            return []
        device = self.device
        if device is None:
            return []
        converted: List[List[int]] = []
        for x, y in raw:
            try:
                rx, ry = device.regularize_coordinate(x, y)
                cx, cy = control.convert_point(rx, ry)
            except Exception as e:
                self.logger.debug(f"坐标转换失败({x},{y})，跳过: {e}")
                continue
            converted.append([int(cx), int(cy)])
        if not converted:
            return []
        return converted[:max(1, int(getattr(control, "max_contacts", 1) or 1))]

    def _resolve_control(self):
        """取当前可用的 MiniTouch 控制实例（未就绪返回 None）。"""
        device = self.device
        if device is None:
            return None
        manager = getattr(device, "control_manager", None)
        if manager is None:
            return None
        control = manager.get_current_control()
        if control is None or not getattr(control, "ready", False):
            return None
        return control

    def _maybe_refresh(self, control) -> bool:
        """按存活上限主动重建 minitouch 服务（防 MuMu 清理长闲服务）。

        沿用旧的刷新顺序铁律（v0.17.49）：**先抬起并释放旧实例，再新建**，否则
        旧实例释放会把新实例刚启动的设备端进程一起杀掉，之后每点一次就重连一次。
        """
        if control is None:
            return False
        self._note_control(control)
        elapsed = time.perf_counter() - self._control_seen_at
        if elapsed <= MINITOUCH_MAX_LIFETIME:
            return False

        manager = getattr(self.device, "control_manager", None)
        if manager is None:
            return False
        self.logger.info(
            f"MiniTouch 已存活 {elapsed:.0f}s（上限 {MINITOUCH_MAX_LIFETIME}s），重建服务")
        lifted = True
        if hasattr(control, "up_all_contacts"):
            try:
                lifted = bool(control.up_all_contacts())
            except Exception as e:
                lifted = False
                self.logger.warning(f"刷新前抬起触点失败: {e}")
        else:
            lifted = False
        try:
            control.release()
        except Exception as e:
            self.logger.warning(f"释放旧 MiniTouch 实例失败: {e}")

        new_control = manager.create_control_instance()
        if new_control is None:
            self.logger.warning("MiniTouch 刷新失败（旧实例已释放），等待调度器重启")
            self._control_seen = None
        else:
            manager.replace_current_control(new_control)
            self._note_control(new_control)

        if not lifted:
            if not touch_residue.clean_stale_contacts(
                    self.serial, logger=self.logger,
                    reason="MiniTouch 刷新前抬起失败"):
                self.logger.warning(
                    "刷新前抬起触点失败且兜底清理未成功，设备端可能残留按下中的触点")
        return True

    def _note_control(self, control):
        """记录"当前控制实例首次被本引擎见到"的时刻。

        实例被替换（刷新/模式切换/调度器重建）时重置计时，避免对刚建好的实例
        立刻再触发一次重建。
        """
        if control is self._control_seen:
            return
        self._control_seen = control
        self._control_seen_at = time.perf_counter()

    def _sleep_interruptible(self, seconds: float):
        """可被停止信号打断的休眠（保证 stop 后立即不再点击）。"""
        remaining = max(0.0, float(seconds))
        while remaining > 0:
            if self._shutdown_event.is_set():
                return
            session = self.current_session()
            if session is None or session.stop_event.is_set():
                return
            step = min(_STOP_POLL_INTERVAL, remaining)
            time.sleep(step)
            remaining -= step
