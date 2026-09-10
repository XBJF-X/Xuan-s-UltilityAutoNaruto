"""超时监视器服务 —— 任务执行过程中的停滞/卡死检测框架

职责划分：
- SchedulerService 初始化并持有本监视器（每个调度器一个实例）；
  任务开始执行时通过 attach_task() 将监视器交给当前正在执行的任务；
- 正在执行的任务（BaseTask）在每轮场景识别后调用 heartbeat() 上报当前场景，
  监视器据此记录任务的执行轨迹（场景变化时间线）；**心跳失败时监视器自行留痕
  （首次 ERROR + traceback）并临时关闭"场景停滞"判定**——心跳是该项判定的唯一
  时间基准，失效后继续判定会导致误判卡死（进而停任务/重启游戏/重启模拟器），
  失败次数在任务结束时由 detach_task() 汇总报告；
- 监视器后台线程周期性截取游戏画面，进行三级检测：
    1. 场景停滞（SCENE_STUCK）：画面仍在变化，但任务长时间停留在同一场景；
    2. 游戏卡死（GAME_FROZEN）：画面长时间静止，探针点击设计坐标后依旧静止；
    3. 模拟器卡死（EMULATOR_FROZEN）：截图持续失败，或重启游戏后画面依旧静止
       （由游戏卡死事件升级）；
- 检测到问题后通过 on_freeze 回调向 SchedulerService 发信号，
  由调度器停止当前任务并执行对应的处理流程（场景自救 / 重启游戏 / 重启模拟器），
  处理完毕后调度器调用 notify_recovery_done() 解除告警挂起状态。

可配置项（Config.get_config，缺省使用默认值）：
    超时检测-启用            bool  默认 True
    超时检测-检测间隔秒      int   默认 5
    超时检测-场景停滞秒数    int   默认 180（同一场景超过该时长判定停滞）
    超时检测-画面静止秒数    int   默认 60（画面静止超过该时长进入探针验证）
    超时检测-静止阈值        float 默认 1.0（缩小灰度图的平均像素差，低于视为静止）
    超时检测-探针坐标        list  默认 None（如 [x, y]，用于卡死验证点击）
    超时检测-探针等待秒      int   默认 3（探针点击后等待画面反应的时间）
    超时检测-截图失败上限    int   默认 3（连续失败次数达到即判定模拟器卡死）
    超时检测-升级窗口秒      int   默认 300（重启游戏后该时长内再次卡死则升级为模拟器卡死）
    超时检测-恢复宽限秒      int   默认 60（处理流程执行完毕后的检测宽限期）
"""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Callable, List, Optional, TYPE_CHECKING

import cv2
import numpy as np

if TYPE_CHECKING:
    from backend.core.legacy.Config import Config
    from backend.core.legacy.Device import Device
    from backend.core.legacy.Operationer import Operationer
    from backend.core.legacy.Task.BaseTask import BaseTask


class FreezeLevel(IntEnum):
    """卡死级别"""
    SCENE_STUCK = 1      # 场景停滞：画面仍在动，但长时间停留在同一场景
    GAME_FROZEN = 2      # 游戏卡死：画面长时间静止，探针点击后依旧静止
    EMULATOR_FROZEN = 3  # 模拟器卡死：截图持续失败 / 重启游戏后画面仍静止


@dataclass
class FreezeEvent:
    """卡死事件：由监视器产生，通过 on_freeze 回调传递给调度器处理"""
    level: FreezeLevel
    task_name: str = ""
    scene_name: str = ""
    static_seconds: float = 0.0
    detail: str = ""
    timestamp: float = field(default_factory=time.time)


class TimeoutWatchdog:
    """
    超时监视器

    生命周期（由 SchedulerService 管理）：
        start() ──► 后台检测线程运行
        attach_task(task) ──► 任务开始执行，重置检测状态并注入任务
        detach_task(task) ──► 任务结束/被停止，停止采集该任务心跳
        stop() ──► 调度器停止，检测线程退出
    """

    # 帧对比时统一缩放到的尺寸（足够小以降低开销，且保留画面结构差异）
    _FRAME_W, _FRAME_H = 160, 90

    def __init__(self,
                 config: "Config",
                 device: "Device",
                 operationer: "Operationer",
                 logger: logging.Logger,
                 on_freeze: Optional[Callable[[FreezeEvent], None]] = None):
        self.config = config
        self.device = device
        self.operationer = operationer
        self.logger = logger.getChild("Watchdog")
        self.on_freeze = on_freeze


        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # ---- 任务侧状态（心跳记录）----
        self._current_task: Optional["BaseTask"] = None
        self._last_scene: Optional[str] = None
        self._scene_since: float = time.monotonic()
        self._last_activity: float = time.monotonic()

        # ---- 心跳健康状态（任务侧上报）----
        # 心跳失败会让"场景停滞"判定的时间基准失真（可能误判卡死 → 停任务/重启游戏/
        # 重启模拟器），因此失败后临时关闭该判定，并在任务结束时汇总报告（不静默）。
        self._heartbeat_fail_count: int = 0
        self._scene_stuck_enabled: bool = True

        # ---- 画面侧状态（帧差检测）----
        self._last_frame: Optional[np.ndarray] = None
        self._static_since: float = time.monotonic()
        self._capture_fail_count: int = 0

        # ---- 告警状态机 ----
        self._awaiting_recovery = False  # 已发出告警，等待调度器处理完毕
        self._last_game_restart: float = 0.0  # 最近一次"重启游戏"处理完成的时间
        self._grace_until: float = 0.0  # 恢复宽限期截止时间

        # ---- 事件历史（供排查，仅保留最近 50 条）----
        self._event_history: List[FreezeEvent] = []

    # ================================================================
    # 配置读取（每次检测时读取，支持运行时调整）
    # ================================================================

    def _cfg(self, key: str, default):
        try:
            value = self.config.get_config(key, default)
            return default if value is None else value
        except Exception:
            return default

    # ================================================================
    # 生命周期
    # ================================================================

    def start(self):
        """启动后台检测线程（幂等）"""
        if self._running:
            return
        if not self._cfg("超时检测-启用", True):
            self.logger.info("超时监视器已在配置中禁用")
            return
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop,
                                        name="TimeoutWatchdog",
                                        daemon=True)
        self._thread.start()
        self.logger.info("超时监视器已启动")

    def stop(self):
        """停止后台检测线程"""
        self._running = False
        with self._lock:
            self._current_task = None
        self.logger.info("超时监视器已停止")

    def attach_task(self, task: "BaseTask"):
        """任务开始执行：将监视器交给任务，并重置全部检测状态"""
        with self._lock:
            self._current_task = task
            self._last_scene = None
            now = time.monotonic()
            self._scene_since = now
            self._last_activity = now
            self._static_since = now
            self._last_frame = None
            self._capture_fail_count = 0
            self._awaiting_recovery = False
            # 心跳健康状态随任务重置（上一个任务的失败不应影响本任务）
            self._heartbeat_fail_count = 0
            self._scene_stuck_enabled = True
        task.attach_watchdog(self)
        self.logger.debug(f"开始监视任务 [{task.task_name}]")

    def detach_task(self, task: "BaseTask"):
        """任务结束/被停止：收回监视器。
        若本任务执行期间出现过心跳上报失败，在这里汇总报告（心跳失败不静默）。
        """
        with self._lock:
            was_current = self._current_task is task
            if was_current:
                self._current_task = None
            fail_count = self._heartbeat_fail_count
        task.detach_watchdog()
        if was_current and fail_count:
            self.logger.warning(
                f"任务 [{task.task_name}] 执行期间心跳上报失败 {fail_count} 次，"
                f"已临时关闭场景停滞判定（游戏卡死/模拟器卡死检测不受影响）")
        self.logger.debug(f"停止监视任务 [{task.task_name}]")

    # ================================================================
    # 任务侧接口：心跳上报
    # ================================================================

    def heartbeat(self, scene_name: Optional[str] = None):
        """
        任务每轮场景识别后调用，上报当前场景。
        场景名变化会重置场景停滞计时；任何心跳都会刷新活动时间和截图失败计数关联。

        本方法**不向外抛异常**：心跳失败会破坏"场景停滞"判定的时间基准（可能导致误判
        卡死 → 停任务/重启游戏/重启模拟器），因此这里自行捕获并留痕——首次失败记录
        ERROR（含 traceback）并临时关闭场景停滞判定，后续失败只计数，任务结束时由
        detach_task() 汇总报告（避免每轮循环重复刷屏）。
        """
        try:
            with self._lock:
                if self._current_task is None:
                    return
                now = time.monotonic()
                if scene_name and scene_name != self._last_scene:
                    self.logger.debug(f"场景切换: {self._last_scene} -> {scene_name}")
                    self._last_scene = scene_name
                    self._scene_since = now
                self._last_activity = now
        except Exception as e:
            with self._lock:
                self._heartbeat_fail_count += 1
                first_failure = self._heartbeat_fail_count == 1
                self._scene_stuck_enabled = False
            if first_failure:
                self.logger.error(
                    f"心跳上报失败，已临时关闭场景停滞判定（避免误判卡死）: "
                    f"{type(e).__name__}: {e}", exc_info=True)

    # ================================================================
    # 调度器侧接口：恢复通知
    # ================================================================

    def notify_recovery_done(self, level: FreezeLevel):
        """调度器处理流程执行完毕后调用，解除告警挂起并进入宽限期"""
        now = time.monotonic()
        if level == FreezeLevel.GAME_FROZEN:
            self._last_game_restart = now
        with self._lock:
            self._awaiting_recovery = False
            self._last_frame = None
            self._capture_fail_count = 0
            self._static_since = now
            self._scene_since = now
            self._grace_until = now + float(self._cfg("超时检测-恢复宽限秒", 60))
        self.logger.info(f"告警 [{FreezeLevel(level).name}] 处理完毕，进入恢复宽限期")

    def get_status(self) -> dict:
        """当前监视状态（供 API/调试使用）"""
        now = time.monotonic()
        with self._lock:
            return {
                "running": self._running,
                "current_task": self._current_task.task_name
                if self._current_task else None,
                "last_scene": self._last_scene,
                "scene_seconds": round(now - self._scene_since, 1),
                "static_seconds": round(now - self._static_since, 1),
                "awaiting_recovery": self._awaiting_recovery,
                "recent_events": [{
                    "level": FreezeLevel(e.level).name,
                    "task": e.task_name,
                    "scene": e.scene_name,
                    "detail": e.detail,
                    "time": time.strftime("%H:%M:%S", time.localtime(e.timestamp)),
                } for e in self._event_history[-10:]],
            }

    # ================================================================
    # 内部：后台检测循环
    # ================================================================

    def _monitor_loop(self):
        """后台检测主循环"""
        while self._running:
            try:
                self._check_once()
            except Exception as e:
                self.logger.error(f"超时监视器检测异常: {e}")
            interval = max(1.0, float(self._cfg("超时检测-检测间隔秒", 5)))
            deadline = time.monotonic() + interval
            while self._running and time.monotonic() < deadline:
                time.sleep(0.2)

    def _check_once(self):
        """单轮检测：截图 → 帧差 → 场景停滞/游戏卡死/模拟器卡死判定"""
        now = time.monotonic()
        with self._lock:
            if self._current_task is None or self._awaiting_recovery:
                return
            if now < self._grace_until:
                return

        # ---- 1. 截图（连续失败判定模拟器卡死）----
        frame = self._capture_frame()
        if frame is None:
            self._capture_fail_count += 1
            fail_limit = int(self._cfg("超时检测-截图失败上限", 3))
            self.logger.warning(
                f"截图失败 ({self._capture_fail_count}/{fail_limit})")
            if self._capture_fail_count >= fail_limit:
                self._raise(FreezeLevel.EMULATOR_FROZEN,
                            detail=f"连续 {fail_limit} 次截图失败，模拟器可能已卡死")
            return
        self._capture_fail_count = 0

        # ---- 2. 帧差检测画面是否静止 ----
        small = self._normalize_frame(frame)
        static_seconds = self._update_static_state(small, now)

        # ---- 3. 场景停滞判定（画面仍在动，但场景长时间未变）----
        scene_stuck_seconds = float(self._cfg("超时检测-场景停滞秒数", 180))
        freeze_seconds = float(self._cfg("超时检测-画面静止秒数", 60))
        with self._lock:
            scene_unchanged = now - self._scene_since
            scene_name = self._last_scene
            scene_stuck_enabled = self._scene_stuck_enabled
        # 心跳失效时该判定的时间基准不可信（会误判卡死），故跳过；
        # 游戏卡死/模拟器卡死（画面静止）判定不受心跳影响，照常执行
        if (scene_stuck_enabled
                and scene_name is not None
                and scene_unchanged >= scene_stuck_seconds
                and static_seconds < freeze_seconds):
            self._raise(
                FreezeLevel.SCENE_STUCK,
                detail=f"任务停滞在场景 [{scene_name}] 已超过 {scene_stuck_seconds:.0f} 秒")
            return

        # ---- 4. 游戏卡死判定（画面静止超时 → 探针点击验证）----
        if static_seconds >= freeze_seconds:
            if self._probe_and_still_static(small):
                escalate_window = float(self._cfg("超时检测-升级窗口秒", 300))
                if (self._last_game_restart
                        and now - self._last_game_restart < escalate_window):
                    self._raise(
                        FreezeLevel.EMULATOR_FROZEN,
                        detail=f"重启游戏后 {now - self._last_game_restart:.0f} 秒内画面仍静止，"
                               f"判定模拟器卡死")
                else:
                    self._raise(
                        FreezeLevel.GAME_FROZEN,
                        detail=f"画面静止已超过 {static_seconds:.0f} 秒，探针点击无反应")

    # ================================================================
    # 内部：检测辅助
    # ================================================================

    def _capture_frame(self) -> Optional[np.ndarray]:
        """安全截图，失败返回 None"""
        try:
            if self.device is None:
                return None
            img = self.device.screen_cap()
            if img is None:
                return None
            return np.array(img)
        except Exception:
            return None

    def _normalize_frame(self, frame: np.ndarray) -> np.ndarray:
        """统一缩放为灰度小图，用于帧差对比"""
        if frame.ndim == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        return cv2.resize(frame, (self._FRAME_W, self._FRAME_H))

    def _frame_diff(self, a: np.ndarray, b: np.ndarray) -> float:
        """两帧的平均像素差"""
        diff = cv2.absdiff(np.asarray(a), np.asarray(b))
        return float(np.asarray(diff).mean())

    def _update_static_state(self, small: np.ndarray, now: float) -> float:
        """更新静止状态，返回当前画面已静止的秒数"""
        threshold = float(self._cfg("超时检测-静止阈值", 1.0))
        with self._lock:
            if self._last_frame is None:
                self._last_frame = small
                self._static_since = now
                return 0.0
            if self._frame_diff(small, self._last_frame) > threshold:
                # 画面发生变化，重置静止计时
                self._last_frame = small
                self._static_since = now
            return now - self._static_since

    def _probe_and_still_static(self, reference: np.ndarray) -> bool:
        """
        探针验证：点击设计好的坐标，等待后再次截图，判断画面是否依旧静止。
        未配置探针坐标时直接按静止判定。
        """
        # probe = self._cfg("超时检测-探针坐标", None)
        # if not probe or len(probe) != 2:
        #     self.logger.warning("未配置[超时检测-探针坐标]，跳过探针验证直接判定")
        #     return True
        try:
            for probe_name in ["X_探针1","X_探针2","返回"]:
                probe_element=self.operationer.scene_graph.get_element("主场景",probe_name)
                if probe_element is not None:
                    x,y=probe_element.coordinate_x,probe_element.coordinate_y
                    self.logger.debug(f"探针点击坐标: ({x},{y})")
                    self.device.click(int(x), int(y))
        except Exception as e:
            self.logger.error(f"探针点击失败: {e}")
            return True
        time.sleep(max(1.0, float(self._cfg("超时检测-探针等待秒", 3))))
        frame = self._capture_frame()
        if frame is None:
            return True
        small = self._normalize_frame(frame)
        threshold = float(self._cfg("超时检测-静止阈值", 1.0))
        if self._frame_diff(small, reference) <= threshold:
            return True
        # 探针点击后画面有变化：误报，重置静止计时
        with self._lock:
            self._last_frame = small
            self._static_since = time.monotonic()
        self.logger.debug("探针点击后画面恢复变化，解除卡死预警")
        return False

    # ================================================================
    # 内部：告警触发
    # ================================================================

    def _raise(self, level: FreezeLevel, detail: str):
        """产生卡死事件并通知调度器（边沿触发，处理完毕前不重复告警）"""
        with self._lock:
            if self._awaiting_recovery or self._current_task is None:
                return
            self._awaiting_recovery = True
            event = FreezeEvent(
                level=level,
                task_name=self._current_task.task_name,
                scene_name=self._last_scene or "",
                static_seconds=round(time.monotonic() - self._static_since, 1),
                detail=detail,
            )
            self._event_history.append(event)
            if len(self._event_history) > 50:
                self._event_history = self._event_history[-50:]
        self.logger.warning(f"[{FreezeLevel(level).name}] {detail}")
        if self.on_freeze:
            try:
                self.on_freeze(event)
            except Exception as e:
                self.logger.error(f"告警回调执行失败: {e}")
