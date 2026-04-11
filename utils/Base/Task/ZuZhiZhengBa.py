from utils.Base.Exceptions import TaskCompleted
from utils.Base.Task.BaseTask import BaseTask, handle_task_exceptions


# Todo：适配组织争霸
class ZuZhiZhengBa(BaseTask):
    @handle_task_exceptions
    def _execute(self):
        # 占位任务：当前无具体流程，按完成处理，保持调度链路一致。
        self.schedule_next_on_complete()
        raise TaskCompleted("组织争霸任务暂未实现")
