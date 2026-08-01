from datetime import timedelta, datetime,time

from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn


class PaiHangBangDianZan(BaseTask):
    source_scene = "排行榜"
    task_max_duration = timedelta(minutes=3)
    start_line=time(8,0)

    @TransitionOn()
    def _(self):
        self.logger.info("点赞")
        self.operationer.click_and_wait("点赞")
        self.logger.info("点赞成功")
        self.operationer.click_and_wait("X")
        raise TaskCompleted("任务执行完成")