from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Base.Exceptions import StepFailedError, EndEarly
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class XiuXingZhiLu(BaseTask):
    source_scene = "试炼之地"
    task_max_duration = timedelta(minutes=3)

    @TransitionOn()
    def _(self):
        self.operationer.click_and_wait("修行之路")
        return False

    @TransitionOn("修行之路")
    def _(self):
        self.operationer.click_and_wait("扫荡", wait_time=0)
        # 先点击扫荡看看能不能扫荡
        if self.operationer.detect_element("当前没有可扫荡关卡了", auto_raise=False):
            self.operationer.click_and_wait("重置", wait_time=0)
            if self.operationer.detect_element("每周只能重置1次", auto_raise=False):
                self.operationer.click_and_wait("X")
                self.update_next_execute_time()
                raise EndEarly("本周修行之路已完成，提前退出执行")
            return False

    @TransitionOn("修行之路-重置")
    def _(self):
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("修行之路-扫荡")
    def _(self):
        self.operationer.click_and_wait("扫荡")
        return False

    @TransitionOn("修行之路-正在扫荡")
    def _(self):
        if self.operationer.click_and_wait("超影免费", auto_raise=False):
            return False
        self.config.set_task_config("修行之路", "修行之路状态", 1)
        self.operationer.click_and_wait("X")
        self.update_next_execute_time(3, timedelta(hours=1, minutes=20))
        return True

    @TransitionOn("修行之路-扫荡完成")
    def _(self):
        self.operationer.click_and_wait("领取奖励")
        return False

    @TransitionOn("恭喜你获得")
    def _(self):
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        return True

    def update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        match flag:

            case 0:  # 创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                next_exec_ts = self.data.get('下次执行时间')
                if next_exec_ts == 0:
                    # 若初始值为0，设置为当前UTC时间（或其他合理时间）
                    self.next_execute_time = datetime.now(ZoneInfo("Asia/Shanghai"))
                else:
                    # 从时间戳转换为datetime对象（指定UTC时区避免歧义）
                    self.next_execute_time = datetime.fromtimestamp(next_exec_ts, tz=china_tz)

            case 1:  # 正常执行完毕，更新为下次执行的时间
                days_ahead = (7 - current_time.weekday()) % 7 or 7
                next_monday = current_time + timedelta(days=days_ahead)
                self.next_execute_time = datetime(
                    next_monday.year, next_monday.month, next_monday.day, 5, 0,
                    tzinfo=china_tz
                )

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                self.next_execute_time = datetime.now(ZoneInfo("Asia/Shanghai"))

            case 3:  # 把执行时间推迟delta时间，要求 delta!=None
                if delta is None:
                    self.logger.warning(f"update_next_execute_time传入的delta为空")
                    return False, None
                self.next_execute_time = current_time + delta

            case _:
                self.logger.warning(f"请检查update_next_execute_time传入的参数：flag={flag},delta={delta}")
                return False, None

        self.logger.info(f"下次执行时间为：{self.next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
        self.config.set_task_config(self.task_name, "下次执行时间", int(self.next_execute_time.timestamp()))
        return True, self.next_execute_time
