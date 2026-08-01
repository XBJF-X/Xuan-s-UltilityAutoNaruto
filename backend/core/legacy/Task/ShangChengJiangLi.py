from datetime import timedelta

from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn


class ShangChengJiangLi(BaseTask):
    source_scene = "商城-商店"
    task_max_duration = timedelta(minutes=2)

    @TransitionOn()
    def _(self):
        self.operationer.click_and_wait("特权商店")
        self.operationer.click_and_wait("特权商店-特权积分")
        if self.operationer.click_and_wait("特权商店-特权积分-领取"):
            self.logger.info("特权商店15000铜币领取成功")
        else:
            self.logger.warning("特权商店15000铜币领取失败，可能已经被领取")
        self.operationer.click_and_wait("X")
        raise TaskCompleted("任务执行完成")