from datetime import timedelta, time

from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn
from backend.core.legacy.Task.schedule import Daily


class PaiHangBangDianZan(BaseTask):
    source_scene = "排行榜"
    task_max_duration = timedelta(minutes=3)
    # 每日窗口：8:00 起（排行榜刷新后），至次日 5:01
    schedule = Daily(at=time(8, 0))

    @TransitionOn()
    def _(self):
        self.logger.info("点赞")
        self.operationer.click_and_wait("点赞")
        self.logger.info("点赞成功")
        self.operationer.click_and_wait("X")
        raise TaskCompleted("任务执行完成")