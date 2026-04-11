from datetime import time, timedelta, datetime

from utils.Base.Exceptions import TaskCompleted
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class YiLeWaiMai(BaseTask):
    source_scene = "一乐外卖"
    task_max_duration = timedelta(minutes=2)
    start_line = time(11, 0,20)

    @TransitionOn()
    def _(self):
        self.logger.info("开始领取[一乐外卖]")
        takeout_sum = 0
        while self.operationer.click_and_wait(
                "待领取",
                max_time=3,
                wait_time=1
        ):
            takeout_sum += 1
            self.logger.debug(f"已领取了 {takeout_sum} 份外卖")
            continue
        self.operationer.click_and_wait("X")
        if takeout_sum:
            self._activate_another_task("消耗体力")
        raise TaskCompleted("一乐外卖领取完成")


