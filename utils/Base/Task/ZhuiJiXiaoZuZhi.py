from datetime import datetime, timedelta,time

from utils.Base.Exceptions import TaskCompleted
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class ZhuiJiXiaoZuZhi(BaseTask):
    source_scene = "追击晓组织"
    task_max_duration = timedelta(minutes=3)
    start_line=time(12, 0)

    @TransitionOn()
    def _(self):
        self.operationer.click_and_wait("奖励")
        return False

    @TransitionOn("追击晓组织-奖励")
    def _(self):
        if self.operationer.search_and_click(
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
        ):
            self.logger.info("存在可领取奖励，已点击领取")
            return False
        self.operationer.click_and_wait("X")
        raise TaskCompleted("任务执行完成")
    @TransitionOn("任务奖励-一键领取")
    def _(self):
        self.operationer.click_and_wait("确定")
        return False

    def _get_execute_window(self,dt: datetime | None = None):
        if dt is None:
            dt=self.last_run_time
        today = dt.date()
        if dt.time() < time(5, 0):
            today -= timedelta(days=1)
        
        # 计算today所在的周一
        this_monday = today - timedelta(days=today.weekday())

        start_dt = datetime.combine(this_monday, self.start_line, tzinfo=self.tz_info) # type: ignore
        dead_dt = datetime.combine(this_monday+timedelta(weeks=1), time(5, 0), tzinfo=self.tz_info)

        return [(start_dt, dead_dt)]
    def get_next_cycle_day(self, dt: datetime) :
        return dt + timedelta(weeks=1)

