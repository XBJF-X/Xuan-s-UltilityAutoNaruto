"""调度器服务 - 严格遵循原版 Scheduler.py 逻辑，剥离 PySide6，衔接新版前端"""
import heapq
import logging
import threading
import time
import traceback
from datetime import datetime, timedelta
from typing import Optional, Callable, List, TypeVar, Generic, Dict
from zoneinfo import ZoneInfo

import cv2

from backend.utils import get_real_path
from backend.core.config_model import Config
from backend.core.scene_graph import SceneGraph
# 阶段 3.4：旁路日志 handler 走注册表（services 不再反向 import api.ws）
from backend.runtime.log_sinks import get_handlers
# 阶段 4.1：设备/连点引擎运行时协作者
from backend.services.scheduler.device_runtime import DeviceRuntime
# 阶段 4.2：临时预设运行器
from backend.services.scheduler.preset_runner import PresetRunner
# 阶段 4.3：桌面通知（空闲/预设完成）
from backend.services.scheduler.idle_notifier import IdleNotifier
# 阶段 4.4a：激活管理（临时启用登记/恢复、启用切换、手动执行窗口预检）
from backend.services.scheduler.activation_manager import ActivationManager
# 阶段 4.5：扫描循环（后台线程 + 三态推进 + 抢占）
from backend.services.scheduler.scan_loop import ScanLoop
# 阶段 4.6：卡死告警处理（先自救、后强制 + 兜底脱困）
from backend.services.scheduler.freeze_handler import FreezeIncidentHandler
# 阶段 4.7：任务状态存储（快照读写 + 推送 + 订阅）
from backend.services.scheduler.task_state_store import TaskStateStore
# 说明：`STOP_REASON_STUCK` / `STOP_REASON_FROZEN` / `Stop` 的使用点已随卡死处理搬到
# freeze_handler（阶段 4.6），本模块不再需要这些导入

T = TypeVar('T')

# ===== 配置模式名称映射（用于调度器启动横幅，便于反馈定位） =====
_CONTROL_MODE_NAMES = {0: "MiniTouch", 1: "U2"}
_SCREEN_MODE_NAMES = {0: "DroidCastRaw", 1: "WindowCapture", 2: "U2", 3: "MuMu", 4: "LD"}

# ===== 账号配置模式“告一段落”判定 =====
# 阈值常量的唯一实现已移至 services/scheduler/constants.py（阶段 4.3：避免
# "协作者 ← 服务"的循环导入）；此处保留同名引用，既有调用点与文档不受影响
from backend.services.scheduler.constants import IDLE_NOTIFY_THRESHOLD  # noqa: E402

# ===== 立即执行的触发来源 =====
# 常量唯一实现已移至 services/scheduler/constants.py（阶段 4.4b：ActivationManager 也要用）；
# 此处保留同名引用，3 个测试脚本 `from backend.services.scheduler_service import SOURCE_*`
# 与既有调用点不受影响
from backend.services.scheduler.constants import (  # noqa: E402
    SOURCE_ACTIVATION,
    SOURCE_MANUAL,
)


# ===== 全局共享 SceneGraph 单例 =====
# 所有配置的调度器复用同一个 SceneGraph（构建后只读，场景/元素识别不写库），
# 避免每个配置在首次访问调度器 API 时各自解码全部 ~845 张元素图（秒级成本）。
_shared_scene_graph: Optional[SceneGraph] = None
_shared_resource_db = None


def get_shared_scene_graph() -> SceneGraph:
    global _shared_scene_graph, _shared_resource_db
    if _shared_scene_graph is None:
        from pathlib import Path
        from backend.tools.resource_db import ResourceDBManager
        _shared_resource_db = ResourceDBManager(Path(get_real_path("src")))
        _shared_scene_graph = SceneGraph(_shared_resource_db)
    return _shared_scene_graph


def peek_shared_scene_graph() -> Optional[SceneGraph]:
    """取已构建的共享 SceneGraph；未构建时返回 None（**不触发构建**）。

    供"只需在已存在时做失效/清理"的场景使用（如资源管理器改边后失效候选集索引），
    避免为一次轻量操作付出全量解码（~1.3s）的代价。
    """
    return _shared_scene_graph


class PriorityQueue(Generic[T]):
    """基于 heapq 的优先级队列（最小堆：`__lt__` 决定优先级与下次执行时间顺序）

    阶段 3 清理：删除了 4 个全库无调用点的方法（`dequeue` / `peek` / `reheapify` /
    `refresh_task`）—— 任务出队由"三态扫描"改写 `current_status` 完成，从不真正 pop。
    """

    def __init__(self):
        self.heap: List[T] = []
        self.task_dic: Dict[str, T] = {}

    def enqueue(self, item: T):
        heapq.heappush(self.heap, item)
        self.task_dic[item.task_name] = item

    def is_empty(self) -> bool:
        return len(self.heap) == 0

    def get_task(self, task_name: str) -> Optional[T]:
        return self.task_dic.get(task_name)

    def update_task_status(self, task_name: str, new_status: int) -> bool:
        if task_name not in self.task_dic:
            return False
        task = self.task_dic[task_name]
        task.current_status = new_status
        self.heap.remove(task)
        heapq.heapify(self.heap)
        heapq.heappush(self.heap, task)
        return True

    def get_tasks_by_status(self, status: int) -> List[T]:
        return [task for task in self.heap if task.current_status == status]


class SchedulerService:
    """
    无头调度器 — 严格遵循原版 Scheduler.py 的三态（等待→就绪→执行）扫描逻辑，
    剥离 PySide6/TimerThread，改用 threading.Timer 实现定时触发扫描。
    通过回调（on_status_change/on_task_state_change）与前端的 WebSocket 衔接。
    """

    def __init__(self,
                 config: Config,
                 scene_graph: Optional[SceneGraph] = None,
                 on_status_change: Optional[Callable] = None,
                 on_task_state_change: Optional[Callable] = None,
                 on_snapshot: Optional[Callable] = None):
        self.logger = logging.getLogger(
            f"SchedulerService_{config.config_path.stem}")
        # 显式绑定 config_id：副本配置（Config_N_副本）靠 logger 名正则会被错判成源配置，
        # 导致副本日志面板空白、源面板混入副本日志（见 backend/log_setup.bind_config_id）
        from backend.log_setup import bind_config_id
        bind_config_id(self.logger, config.config_path.stem)
        self.config = config
        # 场景图：可传入或为 None（为 None 时 _lazy_init 使用全局共享单例，
        # 避免每个配置重复解码全部元素图——场景图构建后只读，可安全共享）
        self.scene_graph = scene_graph
        self.running = False

        self.on_status_change = on_status_change
        self.on_task_state_change = on_task_state_change
        # 完整状态快照回调（WS scheduler_snapshot 推送，前端据此零轮询）
        self.on_snapshot = on_snapshot

        self.transition_manager = None
        self.operationer = None
        self.device = None
        # 超时监视器（_lazy_init 时创建，随调度器 start/stop 启停）
        self.watchdog = None

        # 中间派重构组件：状态快照 / 纯逻辑决策 / 执行层
        from backend.core.scheduler import SchedulerState, TaskPlanner, TaskExecutor
        # 内存状态快照自阶段 4.7 起由 TaskStateStore 持有（同名 property，含 setter）
        self.planner = TaskPlanner()
        self.executor = TaskExecutor(logger=self.logger)

        # 原版 PriorityQueue + 三态管理
        self.task_queue: PriorityQueue = PriorityQueue()

        # 扫描防重入标志与后台线程自阶段 4.5 起由 ScanLoop 持有（同名 property）
        self._lock = threading.Lock()

        # 临时预设（配置类型=临时）：只执行一遍、按顺序执行，跑完自动关闭调度器
        self.run_once = (config.config_type == "临时")
        # 阶段 4.2：预设状态（待执行队列/计数）由 PresetRunner 持有，
        # 本类以同名 property 暴露（见下方"临时预设"小节），既有调用点逐字不变
        # 待激活任务列表：任务执行期间通过 _on_task_activate_request 登记，
        # 待当前任务结束后（_execute_done_callback）统一激活并立即执行，
        # 避免在任务执行线程中直接激活对扫描循环时序的依赖（更稳定）。
        self._pending_activate_tasks: List[str] = []
        # 跨任务临时启用登记：{任务名: 激活前是否已启用}。
        # 仅登记"原本未激活、被其他任务临时启用"的任务，执行结束后恢复其原状态。
        self._temp_activated_tasks: dict[str, bool] = {}
        # 截图保存回调（_lazy_init 时注入，供卡死告警截图使用）
        self._save_screenshot = None
        # 调度器启动时间 / 停止原因（供停止横幅与问题定位）
        self.started_at: Optional[datetime] = None
        self._stop_reason = ""

        # 桌面通知（仅 Windows）：预设跑完 / 账号配置模式告一段落时提醒用户
        # 去抖标记 _idle_notified 自阶段 4.3 起由 IdleNotifier 持有（同名 property）
        # 已执行完任务数与预设任务总数：阶段 4.2 起由 PresetRunner 持有（同名 property）

        # 为当前 config 添加专属文件处理器（log/<用户名>/<日期>/Xuan.log）
        username = config.get_config("用户名", "unknown")
        from backend.log_setup import get_config_file_handler
        self._config_file_handler = get_config_file_handler(username)
        if self._config_file_handler not in self.logger.handlers:
            self.logger.addHandler(self._config_file_handler)
        # 前端实时日志推送：旁路 handler 由组合根 main.py 注册到 runtime.log_sinks
        # （阶段 3.4：services 不再反向 import api.ws）
        registered_sinks = get_handlers()
        self._ws_handler = registered_sinks[0] if registered_sinks else None
        for sink in registered_sinks:
            if sink not in self.logger.handlers:
                self.logger.addHandler(sink)
        # config 专属日志只写入专属文件（log/<用户>/<日期>/Xuan.log）并推送前端，
        # 不再传播到 root logger，避免大量 config 日志混入 Main.log（Main.log 只留主程序级日志）
        self.logger.propagate = False

        # 阶段 4：协作者（DeviceRuntime/PresetRunner/IdleNotifier）由属性**懒加载**创建，
        # 见下方"协作者访问器"——这样也能兼容用 object.__new__ 构造、绕过本 __init__ 的测试

        self.logger.info("SchedulerService 初始化完成")

    def _pre_start_environment_check(self):
        """
        启动前环境检测：截图路径文件 / 实例 / 分辨率16:9 / 后台保活。
        不通过时返回 (False, messages)，调度器提示并拒绝启动。
        """
        import os  # 仅用于下方日志/路径拼接（探测命令与解析已下沉 emulator_env）
        messages = []
        mode = self.config.get_config("截图模式", 2)
        try:
            if mode == 3:  # MuMu
                base = self.config.get_config("MuMu安装路径", "")
                index = self.config.get_config("MuMu实例索引", 0)
                if not base:
                    return False, ["未配置 MuMu安装路径"]
                # 候选路径与实例解析统一由 core/emulator_env.py 提供（阶段 3 单点化）
                from backend.core.emulator_env import (
                    check_mumu_files, find_mumu_manager, probe_mumu_instance,
                )
                dll_ok, manager_ok = check_mumu_files(base)
                manager = find_mumu_manager(base)
                missing = []
                if not dll_ok:
                    missing.append("external_renderer_ipc.dll (MuMu 动态库)")
                if not manager_ok:
                    missing.append("MuMuManager.exe")
                if missing:
                    return False, ["MuMu 截图路径缺少文件: " + ", ".join(missing)]
                messages.append("MuMu 截图路径文件检查通过")
                if manager is not None:
                    info = probe_mumu_instance(manager, index)
                    if info is not None and not info.running:
                        messages.append("提示: MuMu 实例未运行（走后台保活）")
            elif mode == 4:  # LD 雷电
                from backend.core.emulator_env import (
                    LD_CONSOLE_NAME, LD_DLL_NAME, find_ld_console,
                    missing_files, probe_ld_instances,
                )
                base = self.config.get_config("雷电安装路径", "")
                index = self.config.get_config("雷电实例索引", 0)
                if not base:
                    return False, ["未配置 雷电安装路径"]
                missing = missing_files(base, (LD_CONSOLE_NAME, LD_DLL_NAME))
                if missing:
                    return False, ["雷电截图路径缺少文件: " + ", ".join(missing)]
                messages.append("雷电截图路径文件检查通过")
                console = find_ld_console(base)
                if console is not None:
                    instance = probe_ld_instances(console).get(index)
                    if instance is None:
                        return False, ["未在 ldconsole list2 中找到雷电实例索引 %d" % index]
                    resolution = instance.resolution
                    if resolution:
                        rw, rh = resolution
                        messages.append("雷电实例%d 分辨率 %dx%d（%s），状态 %s" % (
                            index, rw, rh,
                            "16:9 符合" if instance.is_16_9 else "非16:9",
                            "运行中" if instance.running else "未运行(后台保活)"))
                        if not instance.is_16_9:
                            return False, ["雷电实例%d 分辨率 %dx%d 不是16:9，请在模拟器设置中调整" % (index, rw, rh)]
                    if not instance.running:
                        messages.append("提示: 实例未运行，请确认已开启后台保活")
            else:
                messages.append("截图模式 %d 无需路径/实例检测" % mode)
        except Exception as e:
            return False, ["环境检测异常: %s" % e]
        return True, messages

    def _lazy_init(self):
        """延迟导入重型依赖（与原版 Scheduler.start 中的初始化一致）"""
        # 未显式注入 SceneGraph 时使用全局共享单例（避免每个配置重复解码元素图）
        if self.scene_graph is None:
            self.scene_graph = get_shared_scene_graph()
        from backend.core.legacy.Device import Device
        from backend.core.legacy.Operationer import Operationer
        from backend.core.legacy.Scene.TransitionManager import TransitionManager
        from backend.core.legacy.Task import TASK_TYPE_MAP
        from backend.core.legacy.Task.BaseTask import BaseTask, TaskType

        import os

        def _save_screenshot(task_name: str, reason: str = ""):
            """保存当前设备截图到 log/<用户名>/<日期>/screenshot/<任务名>/ 目录。
            reason 非空表示错误/超时/卡死自动截图，由"错误自动截图"开关控制（与"保存截图"开关独立）。
            """
            try:
                if reason:
                    if not self.config.get_config("错误自动截图", True):
                        return
                else:
                    if not self.config.get_config("保存截图", 0):
                        return
                if self.device is None:
                    self.logger.warning("设备不存在")
                    return
                img = self.device.screen_cap()
                if img is None:
                    self.logger.warning("截图为空")
                    return
                import numpy as np
                arr = np.array(img)
                username = self.config.get_config("用户名", "unknown")
                date_str = datetime.now().strftime("%Y-%m-%d")
                ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                safe_name = task_name.replace("/", "_").replace(
                    "\\", "_") if task_name else "unknown"
                log_dir = get_real_path("log")
                save_dir = os.path.join(log_dir, username, date_str,
                                        "screenshot", safe_name)
                os.makedirs(save_dir, exist_ok=True)
                filepath = os.path.join(
                    save_dir, f"{ts}{('_' + reason) if reason else ''}.png")
                cv2.imencode('.png', arr)[1].tofile(filepath)
                self.logger.info(
                    f"保存截图到{filepath}" + (f"（原因: {reason}）" if reason else ""))
            except Exception as e:
                # 截图保存失败不影响任务主流程，但必须留痕（原实现静默吞掉异常）
                self.logger.warning(f"截图保存失败: {type(e).__name__}: {e}")

        self._save_screenshot = _save_screenshot

        self.transition_manager = TransitionManager(self.config, self.logger)
        self.device = Device(self.config, parent_logger=self.logger)
        self.operationer = Operationer(
            "",
            self.config,
            self.device,
            self.scene_graph,
            _save_screenshot,
            parent_logger=self.logger,
        )
        # 创建超时监视器：调度器持有，任务执行时通过 attach_task 交给任务
        from backend.services.watchdog_service import TimeoutWatchdog
        self.watchdog = TimeoutWatchdog(
            self.config,
            self.device,
            self.operationer,
            self.logger,
            on_freeze=self._on_watchdog_freeze,
        )
        self.executor.set_watchdog(self.watchdog)
        return TASK_TYPE_MAP, BaseTask, TaskType

    def _log_start_banner(self) -> None:
        """记录调度器启动横幅（启动时间 / 控制模式 / 截图模式 / 串口 / 版本等基本信息），
        写入 config 专属日志 log/<用户名>/<日期>/Xuan.log，便于反馈时定位筛选。"""
        from backend.runtime_info import get_client_version, get_runtime_commit
        cfg = self.config

        def _to_int(v):
            try:
                return int(v)
            except (TypeError, ValueError):
                return -1

        control_mode = _to_int(cfg.get_config("控制模式", 0))
        screen_mode = _to_int(cfg.get_config("截图模式", 0))
        width = 56
        lines = [
            "=" * width,
            "调度器启动",
            f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"配置: {self.config.config_path.stem}",
            f"用户名: {cfg.get_config('用户名', '')}",
            f"配置类型: {cfg.get_config('配置类型', '')}",
            f"控制模式: {_CONTROL_MODE_NAMES.get(control_mode, '未知')} ({control_mode})",
            f"截图模式: {_SCREEN_MODE_NAMES.get(screen_mode, '未知')} ({screen_mode})",
            f"串口: {cfg.get_config('串口', '')}",
            f"模拟器分辨率: {cfg.get_config('模拟器分辨率', '')}",
            f"调试模式: {cfg.get_config('调试模式', 0)}",
            f"执行模式: {'预设模式' if self.run_once else '持久模式'}",
            f"客户端版本: {get_client_version()}",
            f"Commit: {get_runtime_commit()}",
            "=" * width,
        ]
        self.logger.info("\n".join(lines))

    # ================================================================
    # 残留触点（粘滞多点触摸）自检 / 自愈
    # ================================================================

    def _join_task_threads(self, tasks, timeout: float = 5.0) -> list[str]:
        """等待任务执行线程退出（共享超时预算），返回未退出者任务名。

        `stop()` 过去完全不等任务线程：设备/控制实例被 release 并置 None 后，任务线程
        仍可能继续访问它们（脱困动作同理）。这里只保证"尽力等待 + 留痕"，不阻塞退出。
        """
        current = threading.current_thread()
        deadline = time.time() + max(0.0, timeout)
        pending: list[tuple[str, threading.Thread]] = []
        for task in tasks:
            thread = getattr(task, "_execution_thread", None)
            if isinstance(thread, threading.Thread) and thread.is_alive() \
                    and thread is not current:
                pending.append((getattr(task, "task_name", "?"), thread))
        still_alive: list[str] = []
        for name, thread in pending:
            remaining = deadline - time.time()
            if remaining <= 0:
                still_alive.append(name)
                continue
            thread.join(timeout=remaining)
            if thread.is_alive():
                still_alive.append(name)
        if still_alive:
            self.logger.warning(
                "以下任务线程在 %.1fs 内未退出（将随进程结束）: %s",
                timeout, still_alive)
        return still_alive

    # ================================================================
    # 协作者访问器（阶段 4）
    # 懒加载：既避免 __init__ 里堆积装配代码，也兼容测试用
    # `object.__new__(SchedulerService)` 绕过 __init__ 后直接调用被搬走的方法
    # ================================================================

    def _collaborator(self, attr: str, factory):
        instance = self.__dict__.get(attr)
        if instance is None:
            instance = factory(self)
            self.__dict__[attr] = instance
        return instance

    @property
    def device_runtime(self) -> DeviceRuntime:
        """设备/连点引擎运行时（阶段 4.1）"""
        return self._collaborator("_device_runtime_instance", DeviceRuntime)

    @property
    def preset_runner(self) -> PresetRunner:
        """临时预设运行器（阶段 4.2）"""
        return self._collaborator("_preset_runner_instance", PresetRunner)

    @property
    def idle_notifier(self) -> IdleNotifier:
        """桌面通知（阶段 4.3）"""
        return self._collaborator("_idle_notifier_instance", IdleNotifier)

    @property
    def activation_manager(self) -> ActivationManager:
        """激活管理：临时启用登记/恢复、启用切换、手动执行窗口预检（阶段 4.4a）"""
        return self._collaborator("_activation_manager_instance", ActivationManager)

    @property
    def task_state_store(self) -> TaskStateStore:
        """任务状态存储：快照读写 + 推送 + 订阅（阶段 4.7）"""
        return self._collaborator("_task_state_store_instance", TaskStateStore)

    @property
    def state(self) -> "SchedulerState":
        """内存状态快照（阶段 4.7 起由 TaskStateStore 持有；既有读写不变）"""
        return self.task_state_store.state

    @state.setter
    def state(self, value) -> None:
        # 既有测试会整体替换（verify_task_schedules / verify_touch_residue_fix）
        self.task_state_store.state = value

    @property
    def freeze_handler(self) -> FreezeIncidentHandler:
        """卡死告警处理（阶段 4.6）"""
        return self._collaborator("_freeze_handler_instance", FreezeIncidentHandler)

    @property
    def scan_loop(self) -> ScanLoop:
        """扫描循环：后台线程 + 三态推进 + 抢占（阶段 4.5）"""
        return self._collaborator("_scan_loop_instance", ScanLoop)

    @property
    def _scanning(self) -> bool:
        """扫描防重入标志（阶段 4.5 起由 ScanLoop 持有）"""
        return self.scan_loop.scanning

    @_scanning.setter
    def _scanning(self, value: bool) -> None:
        self.scan_loop.scanning = value

    @property
    def _scan_thread(self):
        """后台扫描线程（阶段 4.5 起由 ScanLoop 持有）"""
        return self.scan_loop.thread

    @_scan_thread.setter
    def _scan_thread(self, value) -> None:
        self.scan_loop.thread = value

    @property
    def _temp_activated_tasks(self) -> dict:
        """跨任务临时启用登记（阶段 4.4a 起由 ActivationManager 持有）"""
        return self.activation_manager.temp_activated_tasks

    @_temp_activated_tasks.setter
    def _temp_activated_tasks(self, value: dict) -> None:
        # 既有测试会直接整体替换（object.__new__ 构造的服务），故提供 setter
        self.activation_manager.temp_activated_tasks = dict(value)

    @property
    def _pending_activate_tasks(self) -> List[str]:
        """待激活任务登记（阶段 4.4b 起由 ActivationManager 持有）"""
        return self.activation_manager.pending_activate_tasks

    @_pending_activate_tasks.setter
    def _pending_activate_tasks(self, value: List[str]) -> None:
        self.activation_manager.pending_activate_tasks = list(value)

    # ================================================================
    # 设备运行时（实现见 services/scheduler/device_runtime.py，阶段 4.1 抽出）
    # 保留同名转发：API 与 14 个测试脚本的调用点无需改动
    # ================================================================

    def _shutdown_clicker_engine(self):
        """关闭本设备的长驻连点引擎（调度器停止路径专用）"""
        return self.device_runtime.shutdown_clicker_engine()

    def _device_serial(self) -> str:
        """当前配置的串口（供残留触点自检/清理使用，取不到时返回空串）。"""
        return self.device_runtime.device_serial()

    def _ensure_no_stale_contacts(self, reason: str) -> bool:
        """设备端残留触点自检 + 裸 evdev 兜底清理（v0.17.46）"""
        return self.device_runtime.ensure_no_stale_contacts(reason)

    def _wait_clicker_stopped(self, task, timeout: float = 3.0) -> bool:
        """等待任务内的连点线程真正退出"""
        return self.device_runtime.wait_clicker_stopped(task, timeout)

    # ================================================================
    # 公开接口
    # ================================================================

    def start(self) -> bool:
        with self._lock:
            if self.running:
                return False
            self.running = True

        # 依赖库版本拦截（兜底：API 层 start_scheduler 已拦截，这里防止绕过 API 直接调用，
        # 保证任何入口都不会在依赖库版本不满足时启动调度器）
        try:
            from backend.core.version_info import (  # 阶段 3.4：服务层不再依赖 api 层
    read_client_version as _read_local_version,
    read_min_release_tag as _read_min_release_tag,
    version_gt as _version_gt,
)
            local_version = _read_local_version()
            required_tag, required_version = _read_min_release_tag()
            if required_version and local_version and _version_gt(required_version, local_version):
                self.logger.error(
                    "当前版本 %s 低于本版本要求的最低版本 %s，依赖库不完整，禁止启动调度器。"
                    "请前往 Release 下载最新安装包更新。", local_version, required_tag)
                self.running = False
                return False
        except Exception:
            pass  # 版本检查异常不阻塞启动，避免误伤正常用户

        self.logger.info("正在启动调度器...")
        try:
            TASK_TYPE_MAP, BaseTask, TaskType = self._lazy_init()
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            self.logger.error(f"设备初始化失败: {e}\n{tb}")
            # 依赖模块缺失（如热更新后代码依赖新版安装包中的 Python 包/DLL）时给出明确指引
            if isinstance(e, (ModuleNotFoundError, ImportError)):
                self.logger.error(
                    "检测到依赖模块缺失（%s）：热更新只替换代码、不携带依赖库。"
                    "请前往 GitHub Release 下载最新安装包更新后再启动调度器。", e)
            self.running = False
            return False

        if not self.device.device_ready:
            self.logger.warning("设备未就绪，请检查[助手设置]中串口和截图模式方案设置")
            self.running = False
            return False

        # 残留触点自检/自愈（v0.17.46）：上一轮连点若在触点按下期间被终止，设备端
        # evdev 的 MT slot 会永久停在按下态（此后任何一次点击都会同时触发这些坐标，
        # 只能重启模拟器），启动前先检测并清理，避免异常状态被继承到本轮。
        self._ensure_no_stale_contacts("调度器启动前自检")

        # 启动前环境检测：截图路径文件 / 实例 / 分辨率16:9 / 后台保活，不通过则提示且不启动
        env_ok, env_msgs = self._pre_start_environment_check()
        if not env_ok:
            for msg in env_msgs:
                self.logger.error(msg)
            self.logger.error("环境检测未通过，调度器不启动。请先修正[助手设置]中的截图配置。")
            self.running = False
            return False
        for msg in env_msgs:
            self.logger.info(msg)

        # 记录调度器启动横幅（环境检测通过，即将真正启动），并记录启动时刻供停止横幅计算运行时长
        self.started_at = datetime.now()
        self._stop_reason = ""
        # 清空上次运行遗留的待激活任务登记（防止跨轮次残留导致误激活）
        self._pending_activate_tasks.clear()
        # 清空临时启用登记（跨轮次的临时启用不应影响本轮判定）
        self._temp_activated_tasks.clear()
        # 通知去抖标记与执行计数按本轮重置（避免上一轮的“已通知”状态影响本轮）；
        # 计数由 PresetRunner 持有（阶段 4.2），去抖标记由 IdleNotifier 持有（4.3）
        self.idle_notifier.idle_notified = False
        self.preset_runner.reset_counters()
        self._log_start_banner()

        # 临时任务启动时一律关闭不执行（临时预设除外，其由用户显式勾选），
        # 只允许立即执行或被其他任务激活后执行
        if not self.run_once:
            for task_name, task_info in self.config.tasks.items():
                if task_info.get("是否临时", False):
                    self.config.set_task_base_config(task_name, "是否启用", False)

        for task_name, task_info in self.config.tasks.items():
            task_class = TASK_TYPE_MAP.get(task_name)
            if not task_class:
                self.logger.warning(f"[{task_name}] 任务创建出错")
                continue
            # 中间派重构：依赖注入收敛为单个 RuntimeContext
            from backend.core.scheduler.runtime import RuntimeContext
            task_instance = task_class(RuntimeContext(
                task_name=task_name,
                config=self.config,
                transition_manager=self.transition_manager,
                operationer=self.operationer,
                activate_another_task_func=self._on_task_activate_request,
                callback=self._execute_done_callback,
                parent_logger=self.logger,
            ))
            self.task_queue.enqueue(task_instance)
            self._sync_task_state(task_instance)

        self.logger.info(f"调度器启动完成，共 {len(self.task_queue.heap)} 个任务")
        self.logger.debug(f"当前执行模式：[{"预设模式" if self.run_once else "持久模式"}]")
        # 临时预设：生成按序待执行任务列表；未勾选任何任务则不启动
        if self.run_once:
            self._init_once_pending()
            if not self.pending_once_tasks:
                self.logger.warning("预设未勾选任何任务，调度器不启动")
                self.stop("预设未勾选任何任务")
                return False
        if self.on_status_change:
            self.on_status_change({
                "running": True,
                "task_count": len(self.task_queue.heap)
            })
        # 更新内存快照并推送（前端据此零轮询）——状态写入统一走 TaskStateStore（阶段 4.7）
        self.task_state_store.mark_running(
            True, len(self.task_queue.heap),
            mode="once" if self.run_once else "persistent")
        self._push_snapshot()

        # 启动超时监视器（后台检测线程）
        if self.watchdog:
            self.watchdog.start()

        # 启动后台扫描循环
        self._start_scan_loop()
        return True

    def stop(self, reason: str = "") -> bool:
        with self._lock:
            if not self.running:
                return False
            self.running = False
        # 清空未处理的待激活任务登记（调度器已停止，无需再激活）
        self._pending_activate_tasks.clear()
        # 临时启用的任务必须在停机时**恢复原状态**：登记项 `False` 表示"原本未激活"，
        # 而 `_restore_temp_activation` 只在"任务执行结束"回调里被调用；若调度器在
        # 任务结束前被停止（用户手动停止 / 预设结束 / 程序退出），旧实现只 clear 登记
        # 就把「是否启用=True」永远留在配置文件里 → 用户下次启动时该任务被正常调度，
        # 属静默的配置副作用。这里在清登记前逐个恢复。
        self._restore_all_temp_activations()

        # 记录停止原因：显式传入优先；未传入时按执行模式给默认值
        if reason:
            self._stop_reason = reason
        elif not self._stop_reason:
            self._stop_reason = "预设执行完毕" if self.run_once else "用户手动停止"

        # 记录调度器停止横幅（停止时间 / 运行时长 / 停止原因），便于反馈筛选定位
        duration = ""
        if self.started_at:
            duration = str(datetime.now() - self.started_at)
        self.logger.info("\n".join([
            "=" * 56,
            "调度器停止",
            f"停止时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"运行时长: {duration}",
            f"停止原因: {self._stop_reason}",
            "=" * 56,
        ]))
        self.started_at = None
        self._stop_reason = ""

        self.logger.info("正在停止调度器...")

        # 停止所有正在运行的任务（与原版一致）
        running_tasks = self.task_queue.get_tasks_by_status(0)
        for task in running_tasks:
            self.executor.stop_task(task)
        # 先等连点线程真正退出，再释放控制实例（v0.17.46）：否则在途的 multi_tap
        # 批次会被「抬起命令 + 杀进程」打断，设备端 slot 永久停在按下态，
        # 之后任何一次点击都会同时触发所有预设连点坐标。
        for task in running_tasks:
            self._wait_clicker_stopped(task)

        # 再等任务执行线程收尾（v0.17.61）：旧实现从不 join，任务线程可能在
        # `operationer` 内继续跑，而下面已经把设备/控制实例 release 并置 None ——
        # 告警派生的脱困线程也会对已释放的设备继续下命令。这里给一个**共享预算**，
        # 超时只告警不阻塞退出（daemon 线程会随进程结束）。
        self._join_task_threads(running_tasks, timeout=5.0)

        # 连点引擎是按设备全局单例、线程长驻（v0.17.60），必须在释放控制实例
        # **之前**显式关闭：否则引擎线程会在 socket 被 release 后继续尝试投递，
        # 且该设备的下一次调度会复用一个持有已失效控制实例的引擎。
        self._shutdown_clicker_engine()

        # 停止超时监视器
        if self.watchdog:
            self.watchdog.stop()
            self.watchdog = None
            self.executor.set_watchdog(None)

        if self.device:
            if getattr(self.device, "control_manager", None):
                try:
                    self.device.control_manager.release()
                except Exception:
                    pass
            if getattr(self.device, "screen_manager", None):
                try:
                    self.device.screen_manager.release()
                except Exception:
                    pass
            self.device = None
        # 释放后再自检一次：释放过程中若抬起失败（连接已断/进程已死），
        # 这里用裸 evdev 兜底清除残留触点，避免残留被带到下一轮（v0.17.46）
        self._ensure_no_stale_contacts("调度器停止后自检")
        if self.operationer:
            self.operationer.stop()
            self.operationer = None

        # 原版：清空队列
        self.task_queue = PriorityQueue()
        # 临时预设：运行结束后重置执行进度/下次执行时间，避免污染预设文件
        if self.run_once:
            self._reset_once_progress()
        self.logger.info("调度器已完全停止")
        if self.on_status_change:
            self.on_status_change({"running": False})
        # 更新内存快照并推送（状态写入统一走 TaskStateStore，阶段 4.7）
        self.task_state_store.mark_running(False)
        self.task_state_store.reset_tasks()
        self._push_snapshot()
        # 内存优化：显式释放任务执行相关引用，便于 GC 回收任务对象与设备连接
        # （共享 SceneGraph / OnnxOcr 为全局单例，保留复用；截图接口已判空 sched.device）
        self.task_queue = PriorityQueue()
        self.transition_manager = None
        self.operationer = None
        self.device = None
        self.executor.set_watchdog(None)
        return True

    def get_status(self) -> dict:
        """直接读内存快照（O(1)，不遍历队列/不读 config）——实现见 TaskStateStore"""
        return self.task_state_store.get_status()

    def get_tasks_status(self) -> list[dict]:
        """直接读内存快照（O(1)，不遍历 heap/不读 config）——实现见 TaskStateStore"""
        return self.task_state_store.get_tasks_status()

    # ================================================================
    # 状态快照同步（中间派 SchedulerState；实现见 TaskStateStore，阶段 4.7）
    # ================================================================

    def _sync_task_state(self, task):
        """把任务对象的关键字段写入内存快照——实现见 TaskStateStore"""
        return self.task_state_store.sync_task_state(task)

    def _update_task_status(self, task_name: str, new_status: int) -> bool:
        """更新队列中的任务状态并同步到内存快照——实现见 TaskStateStore"""
        return self.task_state_store.update_task_status(task_name, new_status)

    def _push_snapshot(self):
        """推送完整状态快照到前端（WS scheduler_snapshot）——实现见 TaskStateStore"""
        return self.task_state_store.push_snapshot()

    def toggle_task_activation(self, task_name: str, state: bool):
        """切换启用/禁用——实现见 ActivationManager.toggle"""
        return self.activation_manager.toggle(task_name, state)

    def _ensure_task_runnable(self, task_name: str) -> bool:
        """原本未启用时临时启用并登记（执行结束后恢复）——实现见 ActivationManager"""
        return self.activation_manager.ensure_runnable(task_name)

    def _restore_all_temp_activations(self) -> None:
        """停机时恢复全部"临时启用"任务的原状态——实现见 ActivationManager"""
        return self.activation_manager.restore_all()

    def _restore_temp_activation(self, task) -> None:
        """任务执行结束后恢复其激活前状态——实现见 ActivationManager"""
        return self.activation_manager.restore_one(task)

    def execute_task_now(self, task_name: str, enable_if_needed: bool = False,
                         *, source: str = SOURCE_MANUAL,
                         ignore_window: bool = False) -> dict:
        """立即执行（与原版 request_task_execute_now 一致）

        Args:
            enable_if_needed(bool): 先启用任务（对齐 V1 原版
                `activate_another_task_implement` 传 enable_if_needed=True 的语义）：用于
                【要塞争夺战/天地战场】结束后自动激活叛忍来袭等临时任务——仅设置下次执行
                时间不足以让其执行，扫描循环会因 is_activated=False 而跳过。
            source(str): 触发来源，`SOURCE_MANUAL`（用户点「执行」）或
                `SOURCE_ACTIVATION`（跨任务激活）。手动来源默认先做**窗口预检**。
            ignore_window(bool): 手动来源是否显式忽略窗口（前端二次确认"强制执行"后传入）。

        Returns:
            dict: ``{"ok": bool, "reason": str|None, "window_state": str|None,
            "schedule": str|None}``。``ok=False`` 时**未改动任何状态**（不写下次执行时间、
            不置 force 标记、不临时启用），前端据此提示原因并可二次确认强制执行。

        手动「执行」默认受任务自身排期约束：用户误触窄窗口任务（天地战场 周三 21:00~21:30、
        要塞争夺战 周六 20:00~20:30、叛忍来袭 周三/周六窗口…）时，过去会带着
        `force_execute_now` 跳过窗口校验空跑到最长执行时长（30~45 分钟）、抢占正在运行的
        任务，并可能级联激活叛忍又来一轮，用户感受为"调度器卡死"。现在改为入口用
        `BaseTask.probe_execute_window(now)` 预检：已过期/未开始 → 直接拒绝；
        `ignore_window=True`（用户二次确认）仍可强制忽略。
        """
        task = self.task_queue.get_task(task_name)
        if not task:
            self.logger.error(f"任务 {task_name} 不存在")
            return {"ok": False, "reason": f"任务 {task_name} 不存在",
                    "window_state": None, "schedule": None}
        if source == SOURCE_MANUAL and not ignore_window:
            rejected = self._reject_manual_execute_outside_window(task)
            if rejected is not None:
                return rejected
        if enable_if_needed:
            # 原本未启用的任务会被临时启用，并在其执行结束后恢复原状态
            self._ensure_task_runnable(task_name)
        if not task.is_activated and not getattr(task, "is_temp", False):
            self.logger.warning(f"[{task_name}] 已禁用，忽略立即执行请求")
            return {"ok": False, "reason": "任务已禁用，请先启用再执行",
                    "window_state": None, "schedule": None}
        ok, _ = task.schedule_execute_now()
        if ok:
            task.force_execute_now = True
        self.logger.info(f"任务 {task_name} 已请求立即执行")
        self._sync_task_state(task)
        self._push_snapshot()
        return {"ok": True, "reason": None, "window_state": None, "schedule": None}

    def _reject_manual_execute_outside_window(self, task) -> Optional[dict]:
        """手动「执行」的窗口预检——实现见 ActivationManager"""
        return self.activation_manager.reject_manual_execute_outside_window(task)

    # ================================================================
    # 内部：静态扫描线程（替代原版 TimerThread，更简单可靠）
    # ================================================================

    def _start_scan_loop(self):
        """启动后台扫描循环线程——实现见 ScanLoop"""
        return self.scan_loop.start_scan_loop()

    def _scan_loop(self):
        """后台扫描循环——实现见 ScanLoop"""
        return self.scan_loop.run_loop()

    def _report_loop_death(self, loop_name: str) -> None:
        """后台循环因致命异常退出时置停机并上报——实现见 ScanLoop"""
        return self.scan_loop.report_loop_death(loop_name)

    # 阶段 3 清理：原 `_cancel_scan_loop()`（空实现、全库无调用点）已删除。
    # 扫描线程通过 `self.running = False` 退出（daemon 线程随进程结束）。

    # ================================================================
    # 核心扫描逻辑（严格遵循原版 Scheduler.scan）——实现见 ScanLoop（阶段 4.5）
    # ================================================================

    def scan(self):
        """改进的扫描方法，避免快速重入（与原版 scan 逻辑一致）"""
        return self.scan_loop.scan()

    def _init_once_pending(self):
        """临时预设：生成按序待执行任务列表（实现见 PresetRunner）"""
        return self.preset_runner.init_pending()

    def _scan_once(self):
        """临时预设模式：按任务执行顺序逐一执行——实现见 ScanLoop"""
        return self.scan_loop.scan_once()

    def _reset_once_progress(self):
        """临时预设运行结束后重置执行进度与下次执行时间（实现见 PresetRunner）"""
        return self.preset_runner.reset_progress()

    # ================================================================
    # 临时预设状态（阶段 4.2：由 PresetRunner 持有；同名 property 保证既有
    # 读写点逐字不变：start() / _scan_once / _on_task_activate_request /
    # _notify_preset_finished / _notify_account_idle / _execute_done_callback）
    # ================================================================

    @property
    def pending_once_tasks(self) -> List[str]:
        return self.preset_runner.pending_tasks

    @pending_once_tasks.setter
    def pending_once_tasks(self, value: List[str]) -> None:
        # 既有测试会直接写该属性（构造"预设待执行列表"场景），故提供 setter
        self.preset_runner.pending_tasks = list(value)

    @property
    def _preset_total(self) -> int:
        return self.preset_runner.preset_total

    @_preset_total.setter
    def _preset_total(self, value: int) -> None:
        self.preset_runner.preset_total = value

    @property
    def _completed_count(self) -> int:
        return self.preset_runner.completed_count

    @_completed_count.setter
    def _completed_count(self, value: int) -> None:
        self.preset_runner.completed_count = value

    # ================================================================
    # 桌面通知（仅 Windows）
    # ================================================================

    def _notifications_enabled(self) -> bool:
        """[助手设置] 任务通知 开关（默认开启）——实现见 IdleNotifier"""
        return self.idle_notifier.notifications_enabled()

    def _notify_user(self, title: str, message: str) -> None:
        """向用户发送桌面系统通知（仅 Windows）——底层实现在 IdleNotifier.send

        保留本方法作为**扩展点**：既有测试/调用方通过替换实例属性
        `sched._notify_user` 捕获通知，因此上层判定仍回调本方法。
        """
        return self.idle_notifier.send(title, message)

    def _notify_preset_finished(self) -> None:
        """临时预设模式：预设任务全部执行完毕后通知用户——实现见 IdleNotifier"""
        return self.idle_notifier.notify_preset_finished()

    def _notify_account_idle(self, now: datetime) -> None:
        """账号配置模式：执行告一段落时通知用户——实现见 IdleNotifier"""
        return self.idle_notifier.notify_account_idle(now)

    @property
    def _idle_notified(self) -> bool:
        """空闲通知去抖标记（阶段 4.3 起由 IdleNotifier 持有）"""
        return self.idle_notifier.idle_notified

    @_idle_notified.setter
    def _idle_notified(self, value: bool) -> None:
        self.idle_notifier.idle_notified = value

    # ================================================================
    # 回调：任务完成
    # ================================================================

    def _execute_done_callback(self, task):
        """任务完成回调（与原版 _on_task_finished 逻辑一致）"""
        # 任务已执行过（无论结果），清除"立即执行"标记
        task.force_execute_now = False
        # 任务结束（完成/停止/超时），交还超时监视器
        self.executor.finish_task(task)

        if not self.running:
            self.logger.debug(f"调度器已停止，忽略任务 {task.task_name} 的完成信号")
            return

        # 记一次“已执行完任务”，供账号配置模式的告一段落通知判定使用
        self._completed_count += 1

        # 更新队列状态回等待(2)
        self._update_task_status(task.task_name, 2)

        # 临时任务执行完自动关闭（临时预设不持久化启用状态，避免污染预设文件）
        if getattr(task, "is_temp", False):
            if self.config.config_type != "临时":
                self.config.set_task_base_config(task.task_name, "是否启用", False)

        self.logger.info(
            f"[{task.task_name}]-[{getattr(task, 'base_priority', '-')}] "
            f"移出执行队列，进入等待队列")

        if self.on_task_state_change:
            self.on_task_state_change({
                "name": task.task_name,
                "status": 2,
                "action": "complete",
                "error": getattr(task, "last_execute_error", None),
            })

        # 标记最后运行时间
        task.last_run_time = datetime.now(ZoneInfo("Asia/Shanghai"))
        # 跨任务临时启用的任务：结束后恢复其激活前状态（原本未激活 → 恢复未激活）
        self._restore_temp_activation(task)
        # 处理其他任务登记的待激活任务（当前任务已结束，激活并立即执行）
        self._process_pending_activations()
        # 空闲通知判定放在激活回调之后：被激活任务此刻已进入就绪/执行队列，
        # 避免"就绪队列刚空就发通知、下一刻又被替补任务填上"的误报
        self._notify_account_idle(datetime.now(ZoneInfo("Asia/Shanghai")))
        # 推送完整状态快照（任务回到等待态）
        self._push_snapshot()

    def _on_task_activate_request(self, task_name: str,
                                  next_execute_time=None):
        """其他任务请求激活指定任务——实现见 ActivationManager"""
        return self.activation_manager.on_task_activate_request(
            task_name, next_execute_time)

    def _schedule_task_activation(self, task_name: str, next_execute_time) -> None:
        """指定被激活任务的下次执行时间——实现见 ActivationManager"""
        return self.activation_manager.schedule_task_activation(
            task_name, next_execute_time)

    def _process_pending_activations(self):
        """任务结束回调中处理待激活列表——实现见 ActivationManager"""
        return self.activation_manager.process_pending_activations()

    def _skip_expired_activation(self, task, now: datetime) -> bool:
        """跨任务"立即激活"前的窗口守卫——实现见 ActivationManager"""
        return self.activation_manager.skip_expired_activation(task, now)

    # ================================================================
    # 超时监视器：告警信号处理
    # ================================================================

    # ================================================================
    # 超时监视器：告警信号处理（实现见 services/scheduler/freeze_handler.py，阶段 4.6 抽出）
    # ================================================================

    def _on_watchdog_freeze(self, event):
        """超时监视器告警回调（转独立线程处理）——实现见 FreezeIncidentHandler"""
        return self.freeze_handler.on_watchdog_freeze(event)

    def _process_freeze_event(self, event):
        """处理卡死事件（先自救、后强制 + 兜底脱困）——实现见 FreezeIncidentHandler"""
        return self.freeze_handler.process_freeze_event(event)

    def _handle_scene_stuck(self, event):
        """场景停滞兜底脱困——实现见 FreezeIncidentHandler"""
        return self.freeze_handler.handle_scene_stuck(event)

    def _handle_game_frozen(self, event):
        """游戏卡死处理：重启游戏——实现见 FreezeIncidentHandler"""
        return self.freeze_handler.handle_game_frozen(event)

    def _handle_emulator_frozen(self, event):
        """模拟器卡死处理：重启模拟器——实现见 FreezeIncidentHandler"""
        return self.freeze_handler.handle_emulator_frozen(event)

    def _wait_device_ready(self, timeout: int = 120):
        """等待设备重新就绪（轮询截图能力，间隔 5s）——实现见 DeviceRuntime"""
        return self.device_runtime.wait_device_ready(timeout)
