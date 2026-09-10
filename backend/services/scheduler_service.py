"""调度器服务 - 严格遵循原版 Scheduler.py 逻辑，剥离 PySide6，衔接新版前端"""
import heapq
import logging
import threading
import time
from datetime import datetime
from typing import Optional, Callable, List, TypeVar, Generic, Dict
from zoneinfo import ZoneInfo

import cv2

from backend.utils import get_real_path
from backend.core.config_model import Config
from backend.core.scene_graph import SceneGraph

T = TypeVar('T')

# ===== 配置模式名称映射（用于调度器启动横幅，便于反馈定位） =====
_CONTROL_MODE_NAMES = {0: "MiniTouch", 1: "U2"}
_SCREEN_MODE_NAMES = {0: "DroidCastRaw", 1: "WindowCapture", 2: "U2", 3: "MuMu", 4: "LD"}


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


class PriorityQueue(Generic[T]):
    """基于 heapq 的优先级队列"""

    def __init__(self):
        self.heap: List[T] = []
        self.task_dic: Dict[str, T] = {}

    def enqueue(self, item: T):
        heapq.heappush(self.heap, item)
        self.task_dic[item.task_name] = item

    def dequeue(self):
        if not self.is_empty():
            item = heapq.heappop(self.heap)
            del self.task_dic[item.task_name]
            return item
        return None

    def is_empty(self) -> bool:
        return len(self.heap) == 0

    def peek(self) -> List[T]:
        return self.heap.copy()

    def get_task(self, task_name: str) -> Optional[T]:
        return self.task_dic.get(task_name)

    def reheapify(self):
        tasks = self.heap.copy()
        self.heap = []
        for task in tasks:
            heapq.heappush(self.heap, task)

    def refresh_task(self, task_name: str) -> bool:
        if task_name not in self.task_dic:
            return False
        task = self.task_dic[task_name]
        self.heap.remove(task)
        heapq.heapify(self.heap)
        heapq.heappush(self.heap, task)
        return True

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
        self.state = SchedulerState()
        self.planner = TaskPlanner()
        self.executor = TaskExecutor(logger=self.logger)

        # 原版 PriorityQueue + 三态管理
        self.task_queue: PriorityQueue = PriorityQueue()

        self._scanning = False
        self._lock = threading.Lock()
        self._scan_thread: Optional[threading.Thread] = None

        # 临时预设（配置类型=临时）：只执行一遍、按顺序执行，跑完自动关闭调度器
        self.run_once = (config.config_type == "临时")
        self.pending_once_tasks: List[str] = []
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

        # 为当前 config 添加专属文件处理器（log/<用户名>/<日期>/Xuan.log）
        username = config.get_config("用户名", "unknown")
        from backend.log_setup import get_config_file_handler
        self._config_file_handler = get_config_file_handler(username)
        if self._config_file_handler not in self.logger.handlers:
            self.logger.addHandler(self._config_file_handler)
        # 前端实时日志推送（全局共享 handler，与 root logger 共用，避免重复创建）
        from backend.api.ws import get_ws_log_handler
        self._ws_handler = get_ws_log_handler()
        if self._ws_handler not in self.logger.handlers:
            self.logger.addHandler(self._ws_handler)
        # config 专属日志只写入专属文件（log/<用户>/<日期>/Xuan.log）并推送前端，
        # 不再传播到 root logger，避免大量 config 日志混入 Main.log（Main.log 只留主程序级日志）
        self.logger.propagate = False

        self.logger.info("SchedulerService 初始化完成")

    def _pre_start_environment_check(self):
        """
        启动前环境检测：截图路径文件 / 实例 / 分辨率16:9 / 后台保活。
        不通过时返回 (False, messages)，调度器提示并拒绝启动。
        """
        import os
        import subprocess
        messages = []
        mode = self.config.get_config("截图模式", 2)
        try:
            if mode == 3:  # MuMu
                base = self.config.get_config("MuMu安装路径", "")
                index = self.config.get_config("MuMu实例索引", 0)
                if not base:
                    return False, ["未配置 MuMu安装路径"]
                # 候选路径与 MuMu.py / validate.py 保持一致，任一存在即可
                manager = None
                for rel in ("MuMuManager.exe", "shell/MuMuManager.exe", "nx_main/MuMuManager.exe"):
                    candidate = os.path.join(base, rel)
                    if os.path.exists(candidate):
                        manager = candidate
                        break
                dll_candidates = (
                    "shell/sdk/external_renderer_ipc.dll",
                    "nx_device/12.0/shell/sdk/external_renderer_ipc.dll",
                    "nx_device/15.0/shell/sdk/external_renderer_ipc.dll",
                    "nx_main/sdk/external_renderer_ipc.dll",
                )
                missing = []
                if not any(os.path.exists(os.path.join(base, rel)) for rel in dll_candidates):
                    missing.append("external_renderer_ipc.dll (MuMu 动态库)")
                if manager is None:
                    missing.append("MuMuManager.exe")
                if missing:
                    return False, ["MuMu 截图路径缺少文件: " + ", ".join(missing)]
                messages.append("MuMu 截图路径文件检查通过")
                if manager is not None and os.path.exists(manager):
                    out = subprocess.run(
                        [manager, "info", "-v", str(index)],
                        capture_output=True, text=True, timeout=15,
                        encoding="utf-8", errors="ignore",
                    ).stdout or ""
                    if ("state=Running" not in out and "状态=运行" not in out):
                        messages.append("提示: MuMu 实例未运行（走后台保活）")
            elif mode == 4:  # LD 雷电
                base = self.config.get_config("雷电安装路径", "")
                index = self.config.get_config("雷电实例索引", 0)
                if not base:
                    return False, ["未配置 雷电安装路径"]
                missing = [rel for rel in ("ldconsole.exe", "ldopengl64.dll")
                           if not os.path.exists(os.path.join(base, rel))]
                if missing:
                    return False, ["雷电截图路径缺少文件: " + ", ".join(missing)]
                messages.append("雷电截图路径文件检查通过")
                ldconsole = os.path.join(base, "ldconsole.exe")
                if os.path.exists(ldconsole):
                    out = subprocess.run(
                        [ldconsole, "list2"],
                        capture_output=True, text=True, timeout=15,
                        encoding="utf-8", errors="ignore",
                    ).stdout or ""
                    found = False
                    for line in out.strip().splitlines():
                        parts = line.split(",")
                        if len(parts) >= 8 and parts[0].strip().isdigit() and int(parts[0]) == index:
                            found = True
                            sysboot = parts[4].strip()
                            rw, rh = int(parts[7]), int(parts[8])
                            is_16_9 = abs(max(rw, rh) * 9 - min(rw, rh) * 16) < 10
                            messages.append("雷电实例%d 分辨率 %dx%d（%s），状态 %s" % (
                                index, rw, rh,
                                "16:9 符合" if is_16_9 else "非16:9",
                                "运行中" if sysboot == "1" else "未运行(后台保活)"))
                            if not is_16_9:
                                return False, ["雷电实例%d 分辨率 %dx%d 不是16:9，请在模拟器设置中调整" % (index, rw, rh)]
                            if sysboot != "1":
                                messages.append("提示: 实例未运行，请确认已开启后台保活")
                            break
                    if not found:
                        return False, ["未在 ldconsole list2 中找到雷电实例索引 %d" % index]
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
                self.logger.info(f"保存截图到{filepath}")
            except Exception:
                pass  # 截图保存失败不影响主流程

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
            from backend.api.utils import _read_local_version, _read_min_release_tag, _version_gt
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
        # 更新内存快照并推送（前端据此零轮询）
        self.state.set_running(
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
        # 临时启用的任务在停机时不写回配置（避免停止过程产生额外写入），仅清除登记
        if self._temp_activated_tasks:
            self.logger.warning(
                f"调度器停止，以下临时启用的任务保持当前启用状态："
                f"{list(self._temp_activated_tasks)}")
        self._temp_activated_tasks.clear()

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
        for task in self.task_queue.get_tasks_by_status(0):
            self.executor.stop_task(task)

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
        # 更新内存快照并推送
        self.state.set_running(False)
        self.state.reset_tasks()
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
        # 直接读内存快照（O(1)，不遍历队列/不读 config）
        return self.state.get_status()

    def get_tasks_status(self) -> list[dict]:
        # 直接读内存快照（O(1)，不遍历 heap/不读 config）
        return self.state.get_tasks()

    # ================================================================
    # 状态快照同步（中间派 SchedulerState）
    # ================================================================

    def _sync_task_state(self, task):
        """把任务对象的关键字段写入内存快照。"""
        next_execute = getattr(task, "next_execute_time", None)
        self.state.upsert_task(
            task.task_name,
            status=getattr(task, "current_status", 2),
            priority=getattr(task, "current_priority", 0),
            base_priority=getattr(task, "base_priority", 0),
            activated=bool(getattr(task, "is_activated", False)),
            next_execute=next_execute.strftime("%Y-%m-%d %H:%M:%S")
            if next_execute else None,
        )

    def _update_task_status(self, task_name: str, new_status: int) -> bool:
        """更新队列中的任务状态并同步到内存快照。"""
        ok = self.task_queue.update_task_status(task_name, new_status)
        if ok:
            task = self.task_queue.get_task(task_name)
            if task:
                self._sync_task_state(task)
        return ok

    def _push_snapshot(self):
        """推送完整状态快照到前端（WS scheduler_snapshot，前端据此零轮询）。"""
        if self.on_snapshot:
            self.on_snapshot(self.state.get_snapshot())

    def toggle_task_activation(self, task_name: str, state: bool):
        """切换启用/禁用（与原版 toggle_task_activation 一致）"""
        self.config.set_task_base_config(task_name, "是否启用", state)
        # 用户手动设置优先：清除临时启用登记，避免任务结束后又被恢复为未激活
        self._temp_activated_tasks.pop(task_name, None)
        temp_task = self.task_queue.get_task(task_name)
        if temp_task:
            if not state and temp_task.current_status == 0:
                self.executor.stop_task(temp_task)
                self._update_task_status(task_name, 2)
            self.logger.info(f"任务 {task_name} {'已启用' if state else '已禁用'}")
            self._sync_task_state(temp_task)
        if self.on_task_state_change:
            self.on_task_state_change({"name": task_name, "activated": state})
        self._push_snapshot()

    def _ensure_task_runnable(self, task_name: str) -> bool:
        """确保任务可被调度：原本未启用时临时启用并登记，执行结束后恢复原状态。

        仅"本次因跨任务激活而启用"的任务会被登记（原本已启用则不做任何改动）。

        Returns:
            bool: 本次是否执行了临时启用
        """
        if self.config.get_task_base_config(task_name, "是否启用", False):
            return False
        self.config.set_task_base_config(task_name, "是否启用", True)
        # 记录原状态（False=未激活），供任务结束后恢复
        self._temp_activated_tasks[task_name] = False
        self.logger.info(
            f"{task_name} 原为未激活，已临时启用（任务执行结束后恢复原状态）")
        return True

    def _restore_temp_activation(self, task) -> None:
        """被跨任务激活的任务执行结束后，恢复其激活前的状态。

        仅处理登记过的任务（原本未激活 → 恢复未激活）；原本已启用的任务不受影响，
        用户中途手动启用（toggle_task_activation）会清除登记，同样不会被恢复。
        """
        task_name = task.task_name
        if task_name not in self._temp_activated_tasks:
            return
        originally_activated = self._temp_activated_tasks.pop(task_name)
        if originally_activated:
            return
        if self.config.config_type == "临时":
            # 临时预设模式不持久化启用状态，避免污染预设文件
            self.logger.info(
                f"[{task_name}] 执行结束，当前为临时预设模式，不写回启用状态")
            return
        self.config.set_task_base_config(task_name, "是否启用", False)
        task.force_execute_now = False
        if getattr(task, "current_status", 2) != 2:
            # 兜底：避免任务停留在就绪队列导致后续仍被扫描到
            self._update_task_status(task_name, 2)
        self._sync_task_state(task)
        self.logger.info(f"[{task_name}] 执行结束，已恢复为未激活状态")

    def execute_task_now(self, task_name: str, enable_if_needed: bool = False):
        """立即执行（与原版 request_task_execute_now 一致）

        enable_if_needed=True 时先启用任务（对齐 V1 原版 activate_another_task_implement
        传 enable_if_needed=True 的语义）：用于【要塞争夺战/天地战场】结束后自动激活
        叛忍来袭等临时任务——仅设置下次执行时间不足以让其执行，扫描循环会因
        is_activated=False 而跳过。
        """
        task = self.task_queue.get_task(task_name)
        if not task:
            self.logger.error(f"任务 {task_name} 不存在")
            return
        if enable_if_needed:
            # 原本未启用的任务会被临时启用，并在其执行结束后恢复原状态
            self._ensure_task_runnable(task_name)
        if not task.is_activated and not getattr(task, "is_temp", False):
            self.logger.warning(f"任务 {task_name} 已禁用")
            return
        ok, _ = task.schedule_execute_now()
        if ok:
            task.force_execute_now = True
        self.logger.info(f"任务 {task_name} 已请求立即执行")
        self._sync_task_state(task)
        self._push_snapshot()

    # ================================================================
    # 内部：静态扫描线程（替代原版 TimerThread，更简单可靠）
    # ================================================================

    def _start_scan_loop(self):
        """启动后台扫描循环线程"""
        self._scan_thread = threading.Thread(target=self._scan_loop,
                                             daemon=True)
        self._scan_thread.start()

    def _scan_loop(self):
        """后台扫描循环（和原版 Scheduler 一样持续循环，按间隔等待）"""
        while self.running:
            try:
                self.scan()
            except Exception as e:
                import traceback
                self.logger.error(f"扫描异常:\n{traceback.format_exc()}")
            # 等待下一个扫描周期
            scan_interval = self.config.get_config("扫描间隔", 1000)
            wait_time = max(0.1, scan_interval / 1000.0)
            # 用短循环代替 sleep 以支持快速退出
            deadline = time.time() + wait_time
            while self.running and time.time() < deadline:
                time.sleep(0.05)

    def _cancel_scan_loop(self):
        """停止扫描循环"""
        pass  # 线程是 daemon 的，退出时自动结束

    # ================================================================
    # 核心扫描逻辑（严格遵循原版 Scheduler.scan）
    # ================================================================

    def scan(self):
        """改进的扫描方法，避免快速重入（与原版 scan 逻辑一致）"""
        if not self.running:
            return
        if self._scanning:
            return

        self._scanning = True
        try:
            if self.run_once:
                self._scan_once()
                return
            # ---- 1. 扫描等待队列(2) → 就绪队列(1) ----
            waiting_tasks = self.task_queue.get_tasks_by_status(2)
            now = datetime.now(ZoneInfo("Asia/Shanghai"))
            for task in waiting_tasks:
                # TaskPlanner 纯逻辑判断：已启用且下次执行时间已到
                if not self.planner.is_due(task, now):
                    continue
                if self._update_task_status(task.task_name, 1):
                    self.logger.info(
                        f"[{task.task_name}]-[{task.base_priority}] 进入就绪队列"
                    )

            # ---- 2. 就绪队列(1) → 执行(0) ----
            ready_tasks = self.task_queue.get_tasks_by_status(1)
            # TaskPlanner 选择：优先立即执行标记，否则按优先级取最高
            next_task = self.planner.pick_next(ready_tasks)
            if next_task is not None:
                running_tasks = self.task_queue.get_tasks_by_status(0)
                if not running_tasks:
                    # 没有正在执行的任务 → 直接执行。
                    # 注意：不在进入执行队列时清除 force_execute_now（"立即执行"）标记，
                    # 标记保留到任务完成回调统一清除——使 should_preempt 能识别
                    # "立即执行启动"的任务，保护其不被普通任务抢占（见 TaskPlanner）。
                    if self._update_task_status(next_task.task_name, 0):
                        self.logger.info(
                            f"[{next_task.task_name}]-[{next_task.base_priority}] 进入执行队列"
                        )
                        if self.on_task_state_change:
                            self.on_task_state_change({
                                "name": next_task.task_name,
                                "status": 0,
                                "action": "start",
                            })
                        # 通过执行层启动：接管超时监视器 + 开始执行线程
                        self.executor.start_task(next_task)
                        self._push_snapshot()
                else:
                    # 有正在执行的任务 → 检查抢占（更高优先级，或被选中的任务带"立即执行"标记）
                    running_task = running_tasks[0]
                    if self.planner.should_preempt(running_task, next_task):
                        self.logger.info(
                            f"[{running_task.task_name}] 被 [{next_task.task_name}] 抢占"
                        )
                        # 执行层停止被抢占任务（交还超时监视器 + 停止线程）
                        self.executor.stop_task(running_task)
        finally:
            self._scanning = False

    def _init_once_pending(self):
        """临时预设：生成按序待执行任务列表（按 任务执行顺序 过滤已启用，顺序缺失的任务排到末尾）"""
        order = self.config.get_config("任务执行顺序", []) or []
        enabled = [t for t, info in self.config.tasks.items()
                   if info.get("是否启用", False)]
        if order:
            pending = [t for t in order if t in enabled]
            for t in enabled:
                if t not in pending:
                    pending.append(t)
        else:
            pending = list(enabled)
        self.pending_once_tasks = pending
        self.logger.info(f"预设待执行任务（按顺序）: {' -> '.join(pending) or '无'}")

    def _scan_once(self):
        """临时预设模式：按任务执行顺序逐一执行，失败/超时也跳过继续，全部跑完后自动关闭调度器"""
        if self.task_queue.get_tasks_by_status(0):
            return  # 当前有任务在执行，等待其结束

        while self.pending_once_tasks:
            task_name = self.pending_once_tasks.pop(0)
            task = self.task_queue.get_task(task_name)
            if task is None:
                continue
            if not task.is_activated:
                self.logger.info(f"预设任务未勾选，跳过: {task_name}")
                continue
            # 预设任务按顺序立即执行：置位"忽略时间窗口"标记（不走窗口校验）
            task.ignore_time_window = True
            if task.current_status == 2:
                self._update_task_status(task_name, 1)
            if task.current_status == 1:
                self._update_task_status(task_name, 0)
                task.force_execute_now = False  # 预设顺序执行，无需立即执行标记
                self.logger.info(f"[预设顺序执行] 开始任务: {task_name}")
                if self.on_task_state_change:
                    self.on_task_state_change({
                        "name": task_name,
                        "status": 0,
                        "action": "start",
                    })
                self.executor.start_task(task)
                self._push_snapshot()
            return

        # 待执行列表耗尽 → 自动关闭调度器
        if self.running:
            self.logger.info("预设任务全部执行完毕，自动关闭调度器")
            threading.Thread(target=self.stop, kwargs={"reason": "预设任务全部执行完毕"}, daemon=True).start()

    def _reset_once_progress(self):
        """临时预设运行结束后，将执行进度与下次执行时间重置为默认值，不持久化运行结果"""
        try:
            import json as _json
            with open(self.config.default_config_path, "r",
                      encoding="utf-8") as f:
                default_tasks = _json.load(f).get("任务", {})
            changed = False
            for task_name, task_info in self.config.tasks.items():
                default_task = default_tasks.get(task_name, {})
                if ("下次执行时间" in default_task
                        and task_info.get("下次执行时间", 0)
                        != default_task.get("下次执行时间", 0)):
                    task_info["下次执行时间"] = default_task.get("下次执行时间", 0)
                    changed = True
                default_prog = default_task.get("执行进度", {})
                cur_prog = task_info.get("执行进度", {})
                for k in list(cur_prog.keys()):
                    if k in default_prog and cur_prog[k] != default_prog[k]:
                        cur_prog[k] = default_prog[k]
                        changed = True
            if changed:
                self.config.save_config_to_file()
                self.logger.info("预设执行进度已重置为默认值")
        except Exception as e:
            self.logger.warning(f"重置预设执行进度失败: {e}")

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
        # 推送完整状态快照（任务回到等待态）
        self._push_snapshot()

    def _on_task_activate_request(self, task_name: str,
                                  next_execute_time=None):
        """其他任务请求激活指定任务。

        两种方式（由 next_execute_time 区分）：
        - 不传时间：登记到待激活列表，当前任务结束后统一激活并立即执行（原行为）；
        - 传时间：只把该任务的下次执行时间设为指定时刻（未启用时临时启用），
          当前任务不需要停留等待，到点后由扫描循环自然执行。

        登记式激活的原因：原先在执行线程中直接 execute_task_now，完全依赖扫描循环时序
        去捡起该任务（扫描可能恰好错过、且抢占判断可能将其延后），鲁棒性不足；临时预设
        模式下扫描只遍历预设列表，被激活的临时任务甚至永远不会执行。改为登记后在任务
        完成回调中统一处理，时机确定、无需与扫描线程竞争。
        """
        if next_execute_time is not None:
            self._schedule_task_activation(task_name, next_execute_time)
            return
        if task_name not in self._pending_activate_tasks:
            self._pending_activate_tasks.append(task_name)
            self.logger.info(f"{task_name} 已登记待激活（当前任务结束后立即执行）")
        else:
            self.logger.debug(f"{task_name} 已在待激活列表中，忽略重复激活请求")

    def _schedule_task_activation(self, task_name: str, next_execute_time) -> None:
        """指定被激活任务的下次执行时间（不登记立即执行，当前任务无需停留等待）。"""
        if next_execute_time.tzinfo is None:
            next_execute_time = next_execute_time.replace(
                tzinfo=ZoneInfo("Asia/Shanghai"))
        task = self.task_queue.get_task(task_name)
        if task is None:
            self.logger.warning(
                f"被激活任务 {task_name} 不在任务队列中，仅写入下次执行时间")
        # 未启用的任务会被扫描循环跳过（TaskPlanner.is_due 要求 is_activated），
        # 需临时启用才能到点执行；执行结束后会恢复原状态
        self._ensure_task_runnable(task_name)
        self.config.set_task_base_config(task_name, "下次执行时间",
                                        int(next_execute_time.timestamp()))
        self.logger.info(
            f"{task_name} 已指定下次执行时间："
            f"{next_execute_time.strftime('%Y-%m-%d %H:%M:%S')}"
            "（当前任务无需等待，到点自动执行）")
        if task is not None:
            self._sync_task_state(task)
        self._push_snapshot()
        # 指定时间已到/已过：立即触发一次扫描，让它尽快进入执行
        if next_execute_time <= datetime.now(ZoneInfo("Asia/Shanghai")):
            self.scan()

    def _process_pending_activations(self):
        """任务结束回调中处理待激活列表：激活登记的任务并立即尝试启动。"""
        if not self._pending_activate_tasks:
            return
        pending = list(self._pending_activate_tasks)
        self._pending_activate_tasks.clear()
        for task_name in pending:
            task = self.task_queue.get_task(task_name)
            if task is None:
                self.logger.warning(f"待激活任务 {task_name} 不在任务队列中，忽略")
                continue
            self.execute_task_now(task_name, enable_if_needed=True)
            if self.run_once:
                # 临时预设模式：被激活任务插入待执行列表最前，下一轮扫描优先执行
                if task_name in self.pending_once_tasks:
                    self.pending_once_tasks.remove(task_name)
                self.pending_once_tasks.insert(0, task_name)
        # 同步扫描一次：让被激活任务立即进入执行（_scanning 标志防重入，
        # 若扫描线程正在扫描则本次返回，由下一轮扫描兜底）
        self.scan()

    # ================================================================
    # 超时监视器：告警信号处理
    # ================================================================

    def _on_watchdog_freeze(self, event):
        """超时监视器告警回调（在监视器线程中触发，转独立线程处理避免阻塞检测）"""
        threading.Thread(target=self._process_freeze_event,
                         args=(event, ),
                         daemon=True).start()

    def _process_freeze_event(self, event):
        """
        处理超时监视器上报的卡死事件：
        1. 停止当前正在执行的任务（任务线程会在下一轮循环感知停止信号）；
        2. 按级别分发到对应的处理流程；
        3. 处理完毕后通知监视器解除告警挂起状态。
        """
        from backend.services.watchdog_service import FreezeLevel
        level_name = {
            FreezeLevel.SCENE_STUCK: "场景停滞",
            FreezeLevel.GAME_FROZEN: "游戏卡死",
            FreezeLevel.EMULATOR_FROZEN: "模拟器卡死",
        }.get(event.level, str(event.level))
        self.logger.warning(
            f"收到超时监视器告警 [{level_name}] "
            f"任务={event.task_name} 场景={event.scene_name} "
            f"静止={event.static_seconds:.0f}s 详情={event.detail}")
        try:
            # 0. 卡死/停滞告警触发时自动截图一次，便于排查（截图失败不阻断处理流程）
            try:
                if self._save_screenshot:
                    self._save_screenshot(event.task_name, "WatchdogFreeze")
            except Exception as _e:
                self.logger.warning(f"卡死告警截图失败: {_e}")
            # 1. 停止当前正在执行的任务
            for task in self.task_queue.get_tasks_by_status(0):
                self.executor.stop_task(task)
            # 2. 按级别分发处理流程
            if event.level == FreezeLevel.SCENE_STUCK:
                self._handle_scene_stuck(event)
            elif event.level == FreezeLevel.GAME_FROZEN:
                self._handle_game_frozen(event)
            elif event.level == FreezeLevel.EMULATOR_FROZEN:
                self._handle_emulator_frozen(event)
        except Exception as e:
            import traceback
            self.logger.error(f"卡死处理流程异常: {e}\n{traceback.format_exc()}")
        finally:
            # 3. 通知监视器处理完毕，进入恢复宽限期
            if self.watchdog:
                self.watchdog.notify_recovery_done(event.level)

    def _handle_scene_stuck(self, event):
        """
        场景停滞处理：尝试寻找 X / 返回 / 退出 等元素进行点击，使游戏脱离当前场景。
        TODO(用户): 按需完善查找的元素范围与点击策略（如返回键、退出按钮等）。
        """
        self.logger.info(f"执行场景停滞处理：尝试点击 X 类元素脱离场景 [{event.scene_name}]")
        if not self.operationer:
            return
        try:
            elements = []
            for name in ("X-普通", "X-广告-1", "X-广告-2"):
                el = self.operationer.get_element(name, "主场景")
                if el is not None:
                    elements.append(el)
            if elements and self.operationer.search_and_click(
                    elements, [], max_attempts=2):
                self.logger.info("场景停滞处理：已点击 X 元素")
                return
            else:
                self.logger.info("场景停滞处理：未找到可点击的 X 元素")

            # 任何可视元素都未找到，则直接点击可能的坐标
            x_coor_element= self.operationer.get_element("X", "主场景")
            self.operationer.click_and_wait(x_coor_element)
            back_coor_element= self.operationer.get_element("返回", "主场景")
            self.operationer.click_and_wait(back_coor_element)

        except Exception as e:
            import traceback
            self.logger.error(f"场景停滞处理失败: {e}\n{traceback.format_exc()}")

    def _handle_game_frozen(self, event):
        """
        游戏卡死处理：重启游戏。
        重启后等待前台应用恢复为火影忍者，避免在加载完成前被再次判定卡死。
        """
        self.logger.warning("执行游戏卡死处理：重启游戏")
        try:
            if not self.operationer:
                return
            self.operationer.app_restart()
            time.sleep(5)
            # 等待游戏回到前台（is_naruto_frontend 是方法，需加括号调用）
            max_wait = 120  # 最多等待 2 分钟
            waited = 0
            while waited < max_wait:
                if self.operationer.is_naruto_frontend:
                    self.logger.info("游戏已回到前台")
                    break
                time.sleep(5)
                waited += 5
            else:
                self.logger.warning("等待游戏恢复超时（120s），交由模拟器卡死检测升级处理")
        except Exception as e:
            self.logger.error(f"重启游戏失败: {e}")

    def _handle_emulator_frozen(self, event):
        """
        模拟器卡死处理：重启模拟器。
        根据截图模式分发：
            0/1/2（普通模拟器）→ Screen 基类 adb 重启
            3（MuMu）→ MuMu.restart_emulator（MuMuManager.exe）
            4（雷电）→ LD.restart_emulator（ldconsole.exe）
        重启完成后等待设备重新就绪，超时则发出错误日志交由上层处理。
        """
        self.logger.error(
            f"检测到模拟器卡死（{event.detail}），开始重启模拟器")
        screen = None
        if self.device and getattr(self.device, "screen_manager", None):
            screen = self.device.screen_manager.current_screen

        try:
            mode = self.config.get_config("截图模式")
            restarted = False
            match mode:
                case 0 | 1 | 2:
                    # 普通模拟器重启流程：adb reboot（Screen 基类默认实现）
                    self.logger.info("截图模式 0/1/2：通过 adb 重启模拟器")
                    if screen is not None and hasattr(screen, "restart_emulator"):
                        restarted = screen.restart_emulator()
                    else:
                        self.logger.warning("当前截图实例不可用，无法执行模拟器重启")
                case 3:
                    # MuMu模拟器重启流程：MuMuManager.exe
                    self.logger.info("截图模式 3：通过 MuMuManager 重启模拟器")
                    if screen is not None and hasattr(screen, "restart_emulator"):
                        restarted = screen.restart_emulator()
                    else:
                        self.logger.warning("当前截图实例不可用，无法执行 MuMu 模拟器重启")
                case 4:
                    # 雷电模拟器重启流程：ldconsole.exe
                    self.logger.info("截图模式 4：通过 ldconsole 重启模拟器")
                    if screen is not None and hasattr(screen, "restart_emulator"):
                        restarted = screen.restart_emulator()
                    else:
                        self.logger.warning("当前截图实例不可用，无法执行雷电模拟器重启")
                case _:
                    self.logger.warning(f"未知截图模式: {mode}，尝试使用默认 adb 重启")
                    if screen is not None and hasattr(screen, "restart_emulator"):
                        restarted = screen.restart_emulator()

            if not restarted:
                self.logger.error("模拟器重启指令执行失败，请检查模拟器路径与实例索引配置")

            # 等待设备重新就绪（等待屏幕管理器重新可截图）
            if self.device:
                self._wait_device_ready(120)
        except Exception as e:
            import traceback
            self.logger.error(f"模拟器重启流程异常: {e}\n{traceback.format_exc()}")

    def _wait_device_ready(self, timeout: int = 120):
        """等待设备重新就绪（轮询截图能力，间隔 5s）"""
        waited = 0
        while waited < timeout:
            try:
                if (self.device and self.device.device_ready
                        and self.device.screen_cap() is not None):
                    self.logger.info("设备已恢复就绪")
                    return True
            except Exception:
                pass
            time.sleep(5)
            waited += 5
        self.logger.warning(f"等待设备恢复超时（{timeout}s）")
        return False
