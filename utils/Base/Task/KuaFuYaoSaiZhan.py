from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class KuaFuYaoSaiZhan(BaseTask):
    source_scene = "要塞战略图"
    task_max_duration = timedelta(minutes=30)

    @TransitionOn()
    def _(self):
        return False

    @property
    def next_execute_time(self):
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")
        base_date = datetime(2025, 9, 20, tzinfo=china_tz)

        def get_this_saturday_8pm(current_time, tz):
            return current_time.replace(day=5, hour=20, minute=0, second=0, microsecond=0, tzinfo=tz)

        def is_in_skip_period(target_time, base_date, interval_weeks):
            delta_weeks = (target_time - base_date).days // 7
            # 仅当周数差为N*4时返回True
            return delta_weeks >= 0 and delta_weeks % interval_weeks == 0

        if next_exec_ts == 0:
            next_time = get_this_saturday_8pm(current_time, china_tz)
            while is_in_skip_period(next_time, base_date, 4):
                next_time += timedelta(weeks=1)
            return next_time
        else:
            # 从时间戳转换为datetime对象
            return datetime.fromtimestamp(next_exec_ts, tz=china_tz)

    def update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        def get_next_saturday_8pm(current_time, tz):
            current_weekday = current_time.weekday()
            days_ahead = (5 - current_weekday) % 7
            if days_ahead == 0 and current_time.hour >= 20:
                days_ahead = 7
            next_time = current_time + timedelta(days=days_ahead)
            return next_time.replace(hour=20, minute=0, second=0, microsecond=0, tzinfo=tz)

        def is_in_skip_period(target_time, base_date, interval_weeks):
            delta_weeks = (target_time - base_date).days // 7
            # 仅当周数差为N*4时返回True
            return delta_weeks >= 0 and delta_weeks % interval_weeks == 0

        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)
        base_date = datetime(2025, 9, 20, tzinfo=china_tz)

        match flag:
            case 0:
                next_execute_time = self.next_execute_time

            case 1:
                next_time = get_next_saturday_8pm(current_time, china_tz)
                while is_in_skip_period(next_time, base_date, 4):
                    next_time += timedelta(weeks=1)
                next_execute_time = next_time

            case 2:
                next_execute_time = current_time.replace(day=5, hour=20, minute=0, second=0, microsecond=0, tzinfo=china_tz)

            case 3:
                if delta is None:
                    self.logger.warning(f"update_next_execute_time传入的delta为空")
                    return False, None
                next_execute_time = current_time + delta

            case _:
                self.logger.warning(f"请检查update_next_execute_time传入的参数：flag={flag},delta={delta}")
                return False, None

        self.logger.info(f"下次执行时间为：{next_execute_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.config.set_task_base_config(self.task_name, "下次执行时间", int(next_execute_time.timestamp()))
        return True, next_execute_time
