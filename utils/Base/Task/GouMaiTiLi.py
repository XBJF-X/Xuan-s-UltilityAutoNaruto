from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Base.Exceptions import EndEarly
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class GouMaiTiLi(BaseTask):
    source_scene = "主场景"
    task_max_duration = timedelta(minutes=3)

    def run(self):
        if self.config.get_config("已购买体力次数") >= self.data.get("购买体力次数", 0):
            self._update_next_execute_time()
            self.config.set_config("已购买体力次数", 0)
            raise EndEarly("已完成购买体力次数")
        super().run()

    @TransitionOn()
    def _(self):
        self.operationer.click_and_wait("体力购买")
        times = self.config.get_config('已购买体力次数')
        while times < self.data.get("购买体力次数", 0):
            self.operationer.click_and_wait("体力购买-购买")
            if not self.operationer.pass_secondary_password():
                times += 1
                self.config.set_config('已购买体力次数', times)
                self.logger.info(f"已购买体力 {times} 次")
        self.operationer.click_and_wait("体力购买-X")
        self.config.set_config('已购买体力次数', 0)
        self._update_next_execute_time()
        return True

    def _update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        match flag:

            case 0:  # 创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                next_exec_ts = self.data.get('下次执行时间')
                if next_exec_ts == 0:
                    # 若初始值为0，设置为当前UTC时间（或其他合理时间）
                    self.next_execute_time = datetime.now(china_tz)
                else:
                    # 从时间戳转换为datetime对象（指定UTC时区避免歧义）
                    self.next_execute_time = datetime.fromtimestamp(next_exec_ts, tz=china_tz)

            case 1:  # 正常执行完毕，更新为下次执行的时间
                next_day = current_time + timedelta(days=1)
                # 新建时间时指定时区（与current_time一致）
                self.next_execute_time = datetime(
                    next_day.year, next_day.month, next_day.day, 5, 0,
                    tzinfo=china_tz  # 关键：添加时区信息
                )

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                self.next_execute_time = datetime.now(china_tz)

            case 3:  # 把执行时间推迟delta时间，要求 delta!=None
                if delta is None:
                    self.logger.warning(f"update_next_execute_time传入的delta为空")
                    return
                self.next_execute_time = current_time + delta

            case _:
                self.logger.warning(f"请检查update_next_execute_time传入的参数：flag={flag},delta={delta}")
                return

        self.logger.info(f"下次执行时间为：{self.next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
        self.config.set_task_config(self.task_name, "下次执行时间", int(self.next_execute_time.timestamp()))
