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

    def _handle_initialization(self, current_time: datetime) -> datetime:
        """处理任务初始化时的时间设置（case0）"""
        china_tz = current_time.tzinfo
        # 读取配置中的时间
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")

        next_execute_time = current_time.replace(hour=8, minute=0, second=0, microsecond=0)

        if next_exec_ts == 0:
            return next_execute_time
        else:
            return datetime.fromtimestamp(next_exec_ts, tz=china_tz)

    def _handle_execution_completed(self, current_time: datetime) -> datetime:
        """返回下一个 05:00（当天或次日）"""
        target_today = current_time.replace(hour=8, minute=0, second=0, microsecond=0)
        if current_time < target_today:
            return target_today
        else:
            return target_today + timedelta(days=1)
