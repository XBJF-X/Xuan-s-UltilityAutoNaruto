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
                 scene_graph: SceneGraph,
                 on_status_change: Optional[Callable] = None,
                 on_task_state_change: Optional[Callable] = None):
        self.logger = logging.getLogger(
            f"SchedulerService_{config.config_path.stem}")
        self.config = config
        self.scene_graph = scene_graph
        self.running = False

        self.on_status_change = on_status_change
        self.on_task_state_change = on_task_state_change

        self.transition_manager = None
        self.operationer = None
        self.device = None

        # 原版 PriorityQueue + 三态管理
        self.task_queue: PriorityQueue = PriorityQueue()

        self._scanning = False
        self._lock = threading.Lock()
        self._scan_thread: Optional[threading.Thread] = None

        # 为当前 config 添加专属文件处理器（log/<用户名>/<日期>/Xuan.log）
        username = config.get_config("用户名", "unknown")
        from backend.log_setup import get_config_file_handler
        self._config_file_handler = get_config_file_handler(username)
        self.logger.addHandler(self._config_file_handler)
        self.logger.propagate = True  # 继续传播到 root logger（Main.log）

        self.logger.info("SchedulerService 初始化完成")

    def _lazy_init(self):
        """延迟导入重型依赖（与原版 Scheduler.start 中的初始化一致）"""
        from backend.core.legacy.Device import Device
        from backend.core.legacy.Operationer import Operationer
        from backend.core.legacy.Scene.TransitionManager import TransitionManager
        from backend.core.legacy.Task import TASK_TYPE_MAP
        from backend.core.legacy.Task.BaseTask import BaseTask, TaskType

        import os

        def _save_screenshot(task_name: str):
            """保存当前设备截图到 log/<用户名>/<日期>/screenshot/<任务名>/ 目录"""
            try:
                # self.logger.debug("截图")
                # 检查配置中是否启用了截图保存
                if not self.config.get_config("保存截图", 0):
                    # self.logger.debug("截图未开启")
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
                filepath = os.path.join(save_dir, f"{ts}.png")
                cv2.imencode('.png', arr)[1].tofile(filepath)
                self.logger.info(f"保存截图到{filepath}")
            except Exception:
                pass  # 截图保存失败不影响主流程

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
        return TASK_TYPE_MAP, BaseTask, TaskType

    # ================================================================
    # 公开接口
    # ================================================================

    def start(self) -> bool:
        with self._lock:
            if self.running:
                return False
            self.running = True

        self.logger.info("正在启动调度器...")
        try:
            TASK_TYPE_MAP, BaseTask, TaskType = self._lazy_init()
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            self.logger.error(f"设备初始化失败: {e}\n{tb}")
            self.running = False
            return False

        if not self.device.device_ready:
            self.logger.warning("设备未就绪，请检查[助手设置]中串口和截图模式方案设置")
            self.running = False
            return False

        # 与原版一致：将临时任务设置成禁用状态，避免无唤醒状态下被执行
        self.config.set_task_base_config("叛忍来袭", "是否启用", False)

        for task_name, task_info in self.config.tasks.items():
            task_class = TASK_TYPE_MAP.get(task_name)
            if not task_class:
                self.logger.warning(f"[{task_name}] 任务创建出错")
                continue
            task_instance = task_class(
                task_name,
                self.config,
                self.transition_manager,
                self.operationer,
                self._on_task_activate_request,
                self._execute_done_callback,
                parent_logger=self.logger,
            )
            self.task_queue.enqueue(task_instance)

        self.logger.info(f"调度器启动完成，共 {len(self.task_queue.heap)} 个任务")
        if self.on_status_change:
            self.on_status_change({
                "running": True,
                "task_count": len(self.task_queue.heap)
            })

        # 启动后台扫描循环（替代原版 TimerThread 的 trigger 机制）
        self._start_scan_loop()
        return True

    def stop(self) -> bool:
        with self._lock:
            if not self.running:
                return False
            self.running = False

        self.logger.info("正在停止调度器...")

        # 停止所有正在运行的任务（与原版一致）
        for task in self.task_queue.get_tasks_by_status(0):
            task.stop()

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
        self.logger.info("调度器已完全停止")
        if self.on_status_change:
            self.on_status_change({"running": False})
        return True

    def get_status(self) -> dict:
        return {
            "running": self.running,
            "task_count": len(self.task_queue.heap),
        }

    def get_tasks_status(self) -> list[dict]:
        results = []
        for task in self.task_queue.heap:
            results.append({
                "name":
                task.task_name,
                "status":
                getattr(task, 'current_status', 2),
                "priority":
                getattr(task, 'current_priority', 0),
                "base_priority":
                getattr(task, 'base_priority', 0),
                "activated":
                task.is_activated if hasattr(task, 'is_activated') else False,
                "next_execute":
                task.next_execute_time.strftime("%Y-%m-%d %H:%M:%S")
                if hasattr(task, 'next_execute_time')
                and task.next_execute_time else None,
            })
        return results

    def toggle_task_activation(self, task_name: str, state: bool):
        """切换启用/禁用（与原版 toggle_task_activation 一致）"""
        self.config.set_task_base_config(task_name, "是否启用", state)
        temp_task = self.task_queue.get_task(task_name)
        if temp_task:
            if not state and temp_task.current_status == 0:
                temp_task.stop()
                self.task_queue.update_task_status(task_name, 2)
            self.logger.info(f"任务 {task_name} {'已启用' if state else '已禁用'}")
        if self.on_task_state_change:
            self.on_task_state_change({"name": task_name, "activated": state})

    def execute_task_now(self, task_name: str):
        """立即执行（与原版 request_task_execute_now 一致）"""
        from backend.core.legacy.Task.BaseTask import TaskType
        task = self.task_queue.get_task(task_name)
        if not task:
            self.logger.error(f"任务 {task_name} 不存在")
            return
        if not task.is_activated and task.task_type != TaskType.TEMP:
            self.logger.warning(f"任务 {task_name} 已禁用")
            return
        task.schedule_execute_now()
        self.logger.info(f"任务 {task_name} 已请求立即执行")

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
            # ---- 1. 扫描等待队列(2) → 就绪队列(1) ----
            waiting_tasks = self.task_queue.get_tasks_by_status(2)
            for task in waiting_tasks:
                if not task.is_activated or task.current_status != 2:
                    continue
                if task.next_execute_time <= datetime.now(
                        ZoneInfo("Asia/Shanghai")):
                    success = self.task_queue.update_task_status(
                        task.task_name, 1)
                    if success:
                        self.logger.info(
                            f"[{task.task_name}]-[{task.base_priority}] 进入就绪队列"
                        )

            # ---- 2. 就绪队列(1) → 执行(0) ----
            ready_tasks = self.task_queue.get_tasks_by_status(1)
            if ready_tasks:
                next_task = min(ready_tasks)  # heapq 的 min 就是优先级最高的
                running_tasks = self.task_queue.get_tasks_by_status(0)
                if not running_tasks:
                    # 没有正在执行的任务 → 直接执行
                    success = self.task_queue.update_task_status(
                        next_task.task_name, 0)
                    if success:
                        self.logger.info(
                            f"[{next_task.task_name}]-[{next_task.base_priority}] 进入执行队列"
                        )
                        if self.on_task_state_change:
                            self.on_task_state_change({
                                "name": next_task.task_name,
                                "status": 0,
                                "action": "start",
                            })
                        next_task.run()
                else:
                    # 有正在执行的任务 → 检查优先级抢占
                    running_task = running_tasks[0]
                    if running_task > next_task:
                        self.logger.info(
                            f"[{running_task.task_name}] 被 [{next_task.task_name}] 抢占"
                        )
                        running_task.stop()
        finally:
            self._scanning = False

    # ================================================================
    # 回调：任务完成
    # ================================================================

    def _execute_done_callback(self, task):
        """任务完成回调（与原版 _on_task_finished 逻辑一致）"""
        if not self.running:
            self.logger.debug(f"调度器已停止，忽略任务 {task.task_name} 的完成信号")
            return

        # 更新队列状态回等待(2)
        self.task_queue.update_task_status(task.task_name, 2)

        # 处理 TEMP 类型任务
        if hasattr(task, 'task_type') and task.task_type == 5:  # TEMP
            self.config.set_task_base_config(task.task_name, "是否启用", False)

        self.logger.info(
            f"[{task.task_name}]-[{getattr(task, 'base_priority', '-')}] "
            f"移出执行队列，进入等待队列")

        if self.on_task_state_change:
            self.on_task_state_change({
                "name": task.task_name,
                "status": 2,
                "action": "complete",
            })

        # 标记最后运行时间
        task.last_run_time = datetime.now(ZoneInfo("Asia/Shanghai"))

    def _on_task_activate_request(self, task_name: str):
        """其他任务请求激活指定任务"""
        self.execute_task_now(task_name)
