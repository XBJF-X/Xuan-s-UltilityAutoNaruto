from datetime import timedelta, datetime

from utils.Base.Exceptions import EndEarly
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
        if self.operationer.detect_element("当前没有可扫荡关卡了"):
            self.operationer.click_and_wait("重置", wait_time=0)
            if self.operationer.detect_element("每周只能重置1次"):
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
        if self.operationer.click_and_wait("超影免费"):
            return False
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

    def _handle_initialization(self, current_time: datetime) -> datetime:
        def get_this_monday_5am(current_time, tz):
            next_monday = current_time - timedelta(days=current_time.weekday())
            return next_monday.replace(hour=5, minute=0, second=0, microsecond=0, tzinfo=tz)

        china_tz = current_time.tzinfo
        # 读取配置中的时间
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")
        next_execute_time = get_this_monday_5am(current_time, china_tz)

        if next_exec_ts == 0:
            return next_execute_time
        else:
            return datetime.fromtimestamp(next_exec_ts, tz=china_tz)

    def _handle_execution_completed(self, current_time: datetime) -> datetime:
        def get_this_monday_5am(dt: datetime) -> datetime:
            """返回 dt 所在周的周一 05:00:00（保留时区）"""
            days_ahead = (0 - dt.weekday()) % 7
            this_monday = dt + timedelta(days=days_ahead)
            return this_monday.replace(hour=5, minute=0, second=0, microsecond=0)

        # 先得到本周一的 5:00（保留 current_time 的时区属性）
        this_monday_5am = get_this_monday_5am(current_time)

        # 如果当前时刻 < 本周一 5:00，则返回本周一 5:00；否则返回下周一 5:00
        if current_time < this_monday_5am:
            return this_monday_5am
        else:
            return this_monday_5am + timedelta(weeks=1)