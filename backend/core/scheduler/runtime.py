"""RuntimeContext - 任务运行时上下文

聚合任务执行所需的全部依赖，替代 BaseTask 旧的 7 参数构造注入
（task_name/config/transition_manager/operationer/activate_another_task_func/callback/parent_logger）。
调度器在实例化任务时组装一个 RuntimeContext 传入，任务内部仍以 self.xxx 访问。
"""
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class RuntimeContext:
    """任务运行时依赖集合。"""

    task_name: str
    config: Any
    transition_manager: Any
    operationer: Any
    # 任务请求立即执行 / 激活其他任务的回调（调度器注入）
    # 调用形式：func(task_name, next_execute_time=None)——
    # next_execute_time 为 None 表示立即执行，否则指定被激活任务的下次执行时间
    activate_another_task_func: Callable
    # 任务完成回调（调度器注入，原 BaseTask.callback）
    callback: Callable
    parent_logger: Any
