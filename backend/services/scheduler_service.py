"""调度器服务 - 剥离 UI 依赖的纯后端调度器"""
import logging
import threading
import time
from datetime import datetime
from typing import Optional, Callable
from zoneinfo import ZoneInfo

from utils.Base.Config import Config
from utils.Base.Scene.SceneGraph import SceneGraph


class SchedulerService:
    """
    无头调度器 - 剥离所有 PySide6 UI 引用
    Device/Operationer 等使用延迟导入避免启动依赖
    """

    def __init__(self, config: Config, scene_graph: SceneGraph,
                 on_status_change: Optional[Callable] = None,
                 on_task_state_change: Optional[Callable] = None):
        self.logger = logging.getLogger(f"SchedulerService_{config.config_path.stem}")
        self.config = config
        self.scene_graph = scene_graph
        self.running = False

        self.on_status_change = on_status_change
        self.on_task_state_change = on_task_state_change

        self.transition_manager = None
        self.operationer = None
        self.device = None
        self._task_queue_dict: dict[str, 'BaseTask'] = {}
        self._scanning = False
        self._lock = threading.Lock()

        self.logger.info("SchedulerService 初始化完成")

    def _lazy_init(self):
        """延迟导入重型依赖"""
        from utils.Base.Device import Device
        from utils.Base.Operationer import Operationer
        from utils.Base.Scene.TransitionManager import TransitionManager
        from utils.Base.Task import TASK_TYPE_MAP
        from utils.Base.Task.BaseTask import BaseTask, TaskType

        self.transition_manager = TransitionManager(self.config, self.logger)
        self.device = Device(self.config, parent_logger=self.logger)
        self.operationer = Operationer(
            "", self.config, self.device, self.scene_graph,
            None, parent_logger=self.logger,
        )
        return TASK_TYPE_MAP, BaseTask, TaskType

    def start(self) -> bool:
        with self._lock:
            if self.running:
                return False
            self.running = True

        self.logger.info("正在启动调度器...")
        try:
            TASK_TYPE_MAP, BaseTask, TaskType = self._lazy_init()
        except Exception as e:
            self.logger.error(f"设备初始化失败: {e}")
            self.running = False
            return False

        if not self.device.device_ready:
            self.logger.warning("设备未就绪，请检查设置")
            self.running = False
            return False

        self.config.set_task_base_config("叛忍来袭", "是否启用", False)

        for task_name, task_info in self.config.tasks.items():
            task_class = TASK_TYPE_MAP.get(task_name)
            if not task_class:
                self.logger.warning(f"[{task_name}] 任务创建出错")
                continue
            task_instance = task_class(
                task_name, self.config, self.transition_manager,
                self.operationer, self._on_task_activate_request,
                self._execute_done_callback, parent_logger=self.logger,
            )
            self._task_queue_dict[task_name] = task_instance

        self.logger.info("调度器启动完成")
        if self.on_status_change:
            self.on_status_change({"running": True})

        self._scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
        self._scan_thread.start()
        return True

    def stop(self) -> bool:
        with self._lock:
            if not self.running:
                return False
            self.running = False

        self.logger.info("正在停止调度器...")
        for task in self._task_queue_dict.values():
            if hasattr(task, 'current_status') and task.current_status == 0:
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

        self._task_queue_dict.clear()
        self.logger.info("调度器已停止")
        if self.on_status_change:
            self.on_status_change({"running": False})
        return True

    def get_status(self) -> dict:
        return {
            "running": self.running,
            "task_count": len(self._task_queue_dict),
        }

    def get_tasks_status(self) -> list[dict]:
        results = []
        for name, task in self._task_queue_dict.items():
            results.append({
                "name": name,
                "status": getattr(task, 'current_status', 2),
                "priority": getattr(task, 'current_priority', 0),
                "base_priority": getattr(task, 'base_priority', 0),
                "activated": task.is_activated if hasattr(task, 'is_activated') else False,
                "next_execute": task.next_execute_time.strftime("%Y-%m-%d %H:%M:%S") if hasattr(task, 'next_execute_time') and task.next_execute_time else None,
            })
        return results

    def toggle_task_activation(self, task_name: str, state: bool):
        self.config.set_task_base_config(task_name, "是否启用", state)
        task = self._task_queue_dict.get(task_name)
        if task and not state and getattr(task, 'current_status', None) == 0:
            task.stop()
        if self.on_task_state_change:
            self.on_task_state_change({"name": task_name, "activated": state})

    def execute_task_now(self, task_name: str):
        from utils.Base.Task.BaseTask import TaskType
        task = self._task_queue_dict.get(task_name)
        if not task:
            self.logger.error(f"任务 {task_name} 不存在")
            return
        if not task.is_activated and task.task_type != TaskType.TEMP:
            self.logger.warning(f"任务 {task_name} 已禁用")
            return
        task.schedule_execute_now()

    def _on_task_activate_request(self, task_name: str):
        self.execute_task_now(task_name)

    def _execute_done_callback(self, task):
        if not self.running:
            return
        self.config.set_task_base_config(task.task_name, "下次执行时间",
                                         int(task.next_execute_time.timestamp()))
        if hasattr(task, 'task_type') and task.task_type == 5:  # TEMP
            self.config.set_task_base_config(task.task_name, "是否启用", False)
        self.logger.info(f"[{task.task_name}] 任务完成")

    def _scan_loop(self):
        while self.running:
            self._do_scan()
            wait_ms = self.config.get_config("扫描间隔", 1000)
            time.sleep(wait_ms / 1000.0)

    def _do_scan(self):
        if not self.running or self._scanning:
            return
        self._scanning = True
        try:
            now = datetime.now(ZoneInfo("Asia/Shanghai"))
            ready_task = None
            for task_name, task in self._task_queue_dict.items():
                if not task.is_activated:
                    continue
                if task.next_execute_time <= now:
                    if ready_task is None or task < ready_task:
                        ready_task = task

            if ready_task:
                if not self._is_running_task():
                    ready_task.run()
        finally:
            self._scanning = False

    def _is_running_task(self) -> bool:
        for task in self._task_queue_dict.values():
            if getattr(task, 'current_status', None) == 0:
                return True
        return False