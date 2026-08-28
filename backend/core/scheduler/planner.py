"""TaskPlanner - 调度决策的纯逻辑部分

不持有设备/执行器/队列，只做"判断"，便于单测，未来也可被前端复制做调度预演。
"""
from datetime import datetime
from typing import List, Optional


class TaskPlanner:
    """纯逻辑调度决策。"""

    # ---- 到期判断 ----

    @staticmethod
    def is_due(task, now: datetime) -> bool:
        """任务是否到期：已启用且下次执行时间已到。"""
        return (bool(getattr(task, "is_activated", False))
                and task.next_execute_time <= now)

    # ---- 就绪队列选择 ----

    @staticmethod
    def pick_next(ready_tasks: List, prefer_force: bool = True) -> Optional[object]:
        """从就绪队列中选择下一个执行的任务。

        - prefer_force：优先执行带 force_execute_now 标记的任务（"立即执行"请求），
          否则低优先级任务会被高优先级就绪任务无限延后；
        - 无强制标记时按优先级取最高（heapq 最小堆的 min 即优先级最高）。
        """
        if not ready_tasks:
            return None
        if prefer_force:
            force_tasks = [t for t in ready_tasks
                           if getattr(t, "force_execute_now", False)]
            if force_tasks:
                return min(force_tasks)
        return min(ready_tasks)

    @staticmethod
    def should_preempt(running_task, candidate) -> bool:
        """candidate 是否应抢占 running_task。

        - candidate 带 force_execute_now（"立即执行"请求）时，优先抢占正在运行的任务：
          否则低优先级"立即执行"任务会被更高/同级优先级任务无限延后，立即执行形同虚设；
        - 正在运行的任务自身也是"立即执行"请求时，按优先级（__lt__ 更小即优先级更高）比较，
          避免连续"立即执行"请求互相无脑打断；
        - 无"立即执行"标记时保持原语义：仅更高优先级（__lt__ 更小）才抢占。
        """
        cand_force = bool(getattr(candidate, "force_execute_now", False))
        run_force = bool(getattr(running_task, "force_execute_now", False))
        if cand_force and not run_force:
            return True
        return running_task > candidate
