from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class KuaFuYaoSaiZhan(BaseTask):
    source_scene = "要塞战略图"
    task_max_duration = timedelta(minutes=30)

    @TransitionOn()
    def _(self):
        return False

    def _handle_initialization(self, current_time: datetime) -> datetime:
        def is_in_skip_period(target_time, interval_weeks):
            base_date = datetime(2025, 9, 20, tzinfo=china_tz)
            delta_weeks = (target_time - base_date).days // 7
            return delta_weeks >= 0 and delta_weeks % interval_weeks == 0

        def get_this_saturday_8pm(current_time, tz):
            days_ahead = (5 - current_time.weekday()) % 7
            next_time = current_time + timedelta(days=days_ahead)
            return next_time.replace(hour=20, minute=0, second=0, microsecond=0, tzinfo=tz)

        china_tz = current_time.tzinfo
        # 读取配置中的时间
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")

        # 本周周六下午8点的时间对象
        next_execute_time = get_this_saturday_8pm(current_time, china_tz)

        while not is_in_skip_period(next_execute_time, 5):
            next_execute_time += timedelta(weeks=1)

        if next_exec_ts == 0:
            return next_execute_time
        else:
            # 转换为带时区的datetime
            stored_time = datetime.fromtimestamp(next_exec_ts, tz=china_tz)
            if stored_time + timedelta(minutes=30) < current_time:
                return next_execute_time
            else:
                return stored_time

    def _handle_execution_completed(self, current_time: datetime) -> datetime:
        def is_in_skip_period(target_time, interval_weeks):
            base_date = datetime(2025, 9, 20, tzinfo=china_tz)
            delta_weeks = (target_time - base_date).days // 7
            return delta_weeks >= 0 and delta_weeks % interval_weeks == 0

        def get_this_saturday_8pm(current_time, tz):
            days_ahead = (5 - current_time.weekday()) % 7
            next_time = current_time + timedelta(days=days_ahead)
            return next_time.replace(hour=20, minute=0, second=0, microsecond=0, tzinfo=tz)

        china_tz = current_time.tzinfo

        # 本周周六下午8点的时间对象
        next_execute_time = get_this_saturday_8pm(current_time, china_tz)

        while not is_in_skip_period(next_execute_time, 5):
            next_execute_time += timedelta(weeks=1)
        return next_execute_time
