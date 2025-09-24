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

    @property
    def next_execute_time(self):
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")

        if next_exec_ts == 0:
            # 若初始值为0，设置为「这周周一中午12点」
            days_to_back_to_monday = current_time.weekday()

            this_monday = current_time - timedelta(days=days_to_back_to_monday)

            # 设置时间为“这周周一中午12:00:00”
            return datetime(
                this_monday.year, this_monday.month, this_monday.day,
                12, 0, 0,  # 固定12点
                tzinfo=china_tz
            )
        else:
            # 从时间戳转换为带时区的datetime对象（逻辑不变）
            return datetime.fromtimestamp(next_exec_ts, tz=china_tz)

    def update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        match flag:
            case 0:
                next_execute_time = self.next_execute_time

            case 1:
                days_ahead = (0 - current_time.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7
                next_monday = current_time + timedelta(days=days_ahead)
                next_execute_time = datetime(
                    next_monday.year, next_monday.month, next_monday.day,
                    12, 0, 0,
                    tzinfo=china_tz
                )

            case 2:  # 立刻执行（逻辑不变，保持当前时间）
                next_execute_time = datetime.now(china_tz)

            case 3:
                if delta is None:
                    self.logger.warning(f"update_next_execute_time传入的delta为空")
                    return False, None
                next_execute_time = current_time + delta

            case _:
                self.logger.warning(f"请检查update_next_execute_time传入的参数：flag={flag},delta={delta}")
                return False, None

        self.logger.info(f"下次执行时间为：{next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
        self.config.set_task_base_config(self.task_name, "下次执行时间", int(next_execute_time.timestamp()))
        return True, next_execute_time
