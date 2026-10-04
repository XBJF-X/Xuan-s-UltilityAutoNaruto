"""临时预设运行器（执行顺序、待执行队列、执行进度重置）

阶段 4.2：从 `SchedulerService`(1542 行) 抽出的第二块职责 —— "临时预设"（配置类型=临时）
的执行顺序与进度状态。原先这些状态散在服务实例上（`pending_once_tasks`、`_preset_total`、
`_completed_count`），被 8 处读取/写入（含通知文案与任务完成回调），本步把它们收拢到这里。

兼容策略：`SchedulerService` 侧保留同名转发方法，并为三个状态提供**同名 property**
（`pending_once_tasks` / `_preset_total` / `_completed_count`），因此 8 处既有读写点
（`start()`、`_scan_once`、`_on_task_activate_request`、`_notify_preset_finished`、
`_notify_account_idle`、`_execute_done_callback`）逐字不变。
"""
from __future__ import annotations

import logging
from typing import Any, List, Optional


class PresetRunner:
    """临时预设的执行顺序 / 待执行队列 / 进度计数"""

    def __init__(self, service: Any):
        self.service = service
        # 按序待执行任务（配置类型=临时时使用）
        self.pending_tasks: List[str] = []
        # 本次预设的任务总数（通知文案用）
        self.preset_total = 0
        # 已执行完的任务数（账号配置模式的"告一段落"通知判定用）
        self.completed_count = 0

    @property
    def logger(self) -> logging.Logger:
        return self.service.logger

    @property
    def config(self):
        return getattr(self.service, "config", None)

    def reset_counters(self) -> None:
        """调度器启动时清零计数（原 `start()` 中的两行赋值）"""
        self.completed_count = 0
        self.preset_total = 0

    def init_pending(self) -> None:
        """生成按序待执行任务列表（按 任务执行顺序 过滤已启用，顺序缺失的任务排到末尾）"""
        order = self.config.get_config("任务执行顺序", []) or []
        enabled = [task for task, info in self.config.tasks.items()
                   if info.get("是否启用", False)]
        if order:
            pending = [task for task in order if task in enabled]
            for task in enabled:
                if task not in pending:
                    pending.append(task)
        else:
            pending = list(enabled)
        self.pending_tasks = pending
        self.preset_total = len(pending)
        self.logger.info(f"预设待执行任务（按顺序）: {' -> '.join(pending) or '无'}")

    def has_pending(self) -> bool:
        return bool(self.pending_tasks)

    def pop_next(self) -> Optional[str]:
        """取下一个待执行任务（队列空返回 None）"""
        return self.pending_tasks.pop(0) if self.pending_tasks else None

    def move_to_front(self, task_name: str) -> None:
        """把任务移到待执行队列首位（其他任务请求插队时使用）"""
        if task_name in self.pending_tasks:
            self.pending_tasks.remove(task_name)
        self.pending_tasks.insert(0, task_name)

    def reset_progress(self) -> None:
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
