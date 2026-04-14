from datetime import time, timedelta, datetime

from utils.Base.Exceptions import TaskCompleted
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
                raise TaskCompleted("本周修行之路已完成，提前退出执行")
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
        self.schedule_next_with_delay(timedelta(hours=1, minutes=20))
        raise TaskCompleted("修行之路冷却中，延迟重试")

    @TransitionOn("修行之路-扫荡完成")
    def _(self):
        self.operationer.click_and_wait("领取奖励")
        return False

    @TransitionOn("恭喜你获得")
    def _(self):
        self.operationer.click_and_wait("X")
        raise TaskCompleted("任务执行完成")
    def _get_execute_window(self,dt: datetime | None = None):
        if dt is None:
            dt=self.last_run_time
        dt = self._ensure_tz_aware(dt)
        today = dt.date()
        if dt.time() < time(5, 0):
            today -= timedelta(days=1)
        
        # 计算today所在的周一
        this_monday = today - timedelta(days=today.weekday())

        start_dt = datetime.combine(this_monday, time(5, 0), tzinfo=self.tz_info)
        dead_dt = datetime.combine(this_monday+timedelta(weeks=1), time(5, 0), tzinfo=self.tz_info)

        return [(start_dt, dead_dt)]
    def get_next_cycle_day(self, dt: datetime):
        return dt + timedelta(weeks=1)
