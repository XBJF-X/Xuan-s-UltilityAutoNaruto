from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class ZhuiJiXiaoZuZhi(BaseTask):
    source_scene = "追击晓组织"
    task_max_duration = timedelta(minutes=3)

    @TransitionOn()
    def _(self):
        self.operationer.click_and_wait("奖励")
        return False

    @TransitionOn("追击晓组织-奖励")
    def _(self):
        self.operationer.search_and_click(
            ["领取"],
            [
                {
                    "swipe": {
                        "start_coordinate": [1317, 744],
                        "end_coordinate": [1317, 271],
                        "duration": 0.5
                    }
                }
            ],
            max_attempts=1
        )
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        return True

    @TransitionOn("任务奖励-一键领取")
    def _(self):
        self.operationer.click_and_wait("确定")
        return False

    def _handle_initialization(self, current_time: datetime) -> datetime:
        def get_this_monday_12am(current_time, tz):
            days_ahead = (6 - current_time.weekday()) % 7
            next_time = current_time + timedelta(days=days_ahead)
            return next_time.replace(hour=12, minute=0, second=0, microsecond=0, tzinfo=tz)

        china_tz = current_time.tzinfo
        # 读取配置中的时间
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")
        next_execute_time = get_this_monday_12am(current_time, china_tz)

        if next_exec_ts == 0:
            return next_execute_time
        else:
            # 转换为带时区的datetime
            stored_time = datetime.fromtimestamp(next_exec_ts, tz=china_tz)
            if stored_time+timedelta(weeks=1) < current_time:
                return next_execute_time
            else:
                return stored_time

    def _handle_execution_completed(self, current_time: datetime) -> datetime:
        def get_this_monday_12am(current_time, tz):
            days_ahead = (6 - current_time.weekday()) % 7
            next_time = current_time + timedelta(days=days_ahead)
            return next_time.replace(hour=12, minute=0, second=0, microsecond=0, tzinfo=tz)

        china_tz = current_time.tzinfo

        next_execute_time = get_this_monday_12am(current_time, china_tz)+timedelta(weeks=1)
        return next_execute_time
