from datetime import timedelta, datetime

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class PaiHangBangDianZan(BaseTask):
    source_scene = "排行榜"
    task_max_duration = timedelta(minutes=3)

    @TransitionOn()
    def _(self):
        self.logger.info("点赞")
        self.operationer.click_and_wait("点赞")
        self.logger.info("点赞成功")
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        return True

    def get_cycle_execute_time(self,dt: datetime) -> datetime:
        """返回 dt 所属执行周期的任务执行时间"""
        cycle_execute_time = dt.replace(
            hour=8,
            minute=0,
            second=0,
            microsecond=0,
        )
        today_5am = dt.replace(
            hour=5,
            minute=0,
            second=0,
            microsecond=0,
        )
        if dt < today_5am:
            return cycle_execute_time - timedelta(days=1)
        return cycle_execute_time
