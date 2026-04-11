from utils.Base.Exceptions import TaskCompleted
from utils.Base.Task.BaseTask import BaseTask, handle_task_exceptions


# Todo：完成巅峰对决设计
class DianFengDuiJue(BaseTask):
    @handle_task_exceptions
    def _execute(self):
        # 占位任务：当前无具体流程，按完成处理，保持调度链路一致。
        self.schedule_next_on_complete()
        raise TaskCompleted("巅峰对决任务暂未实现")
