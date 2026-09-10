from datetime import timedelta

from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn
from backend.core.legacy.Task.schedule import Weekday, Weekly


class XiuXingZhiLu(BaseTask):
    source_scene = "试炼之地"
    task_max_duration = timedelta(minutes=3)
    # 每周任务：窗口 [本周一 5:01, 下周一 5:01)
    schedule = Weekly(Weekday.MON)

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
