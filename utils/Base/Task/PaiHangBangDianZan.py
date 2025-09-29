from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class PaiHangBangDianZan(BaseTask):
    source_scene = "排行榜"
    task_max_duration = timedelta(minutes=2)

    @TransitionOn()
    def _(self):
        self.logger.info("点赞")
        self.operationer.click_and_wait("点赞")
        self.logger.info("点赞成功")
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        return True

    def _handle_initialization(self, current_time: datetime) -> datetime:
        """处理任务初始化时的时间设置（case0）"""
        china_tz = current_time.tzinfo
        # 读取配置中的时间
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")

        next_execute_time = datetime(
            current_time.year,
            current_time.month,
            current_time.day,
            8, 0, 0,
            tzinfo=china_tz
        )

        if next_exec_ts == 0:
            return next_execute_time
        else:
            # 转换为带时区的datetime
            stored_time = datetime.fromtimestamp(next_exec_ts, tz=china_tz)
            if stored_time+timedelta(days=1) < current_time:
                return next_execute_time
            else:
                return stored_time

    def _handle_execution_completed(self, current_time: datetime) -> datetime:
        """处理任务执行完成后的时间更新（case1）"""
        china_tz = current_time.tzinfo
        next_day = current_time + timedelta(days=1)
        return datetime(
            next_day.year,
            next_day.month,
            next_day.day,
            8, 0, 0,
            tzinfo=china_tz
        )
