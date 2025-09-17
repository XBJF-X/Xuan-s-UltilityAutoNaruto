from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class ZhuiJiXiaoZuZhi(BaseTask):
    source_scene = "追击晓组织"
    task_max_duration = timedelta(minutes=10)

    @TransitionOn()
    def _(self):
        self.operationer.click_and_wait("")

    @property
    def next_execute_time(self):
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")
        if next_exec_ts == 0:
            # 若初始值为0，设置为本周日12点
            # 计算下一个周日的日期
            # weekday() 返回：0=周一, 1=周二, ..., 6=周日
            days_until_sunday = (6 - current_time.weekday()) % 7
            next_sunday = current_time + timedelta(days=days_until_sunday)

            # 设置时间为本周日12:00:00
            return datetime(
                next_sunday.year, next_sunday.month, next_sunday.day, 5, 0, 0,
                tzinfo=china_tz
            )
        else:
            # 从时间戳转换为datetime对象
            return datetime.fromtimestamp(next_exec_ts, tz=china_tz)

    def update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        match flag:

            case 0:  # 创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                next_execute_time = self.next_execute_time

            case 1:  # 正常执行完毕，更新为下次执行的时间
                # 计算下一个周日的日期
                # weekday() 返回：0=周一, 1=周二, ..., 6=周日
                days_until_sunday = (6 - current_time.weekday()) % 7
                next_sunday = current_time + timedelta(days=days_until_sunday + 7)

                # 设置时间为下周日5:00:00
                next_execute_time = datetime(
                    next_sunday.year, next_sunday.month, next_sunday.day, 5, 0, 0,
                    tzinfo=china_tz
                )

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                next_execute_time = datetime.now(china_tz)

            case 3:  # 把执行时间推迟delta时间，要求 delta!=None
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
