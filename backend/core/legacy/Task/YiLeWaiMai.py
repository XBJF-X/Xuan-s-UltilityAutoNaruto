from datetime import time, timedelta

from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn
from backend.core.legacy.Task.schedule import Daily

PARAM_CONSUME_STAMINA = "领取后消耗体力"


class YiLeWaiMai(BaseTask):
    source_scene = "一乐外卖"
    task_max_duration = timedelta(minutes=2)
    # 每日窗口：11:00:20 起（外卖刷新之后），至次日 5:01
    schedule = Daily(at=time(11, 0, 20))

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
            # 参数缺省视为开启：保持"领到外卖才激活消耗体力"的既有语义
            if self.config.get_task_exe_param(
                    self.task_name, PARAM_CONSUME_STAMINA, True):
                self._activate_another_task("消耗体力")
            else:
                self.logger.info("已按参数设置跳过[消耗体力]任务")
        raise TaskCompleted("一乐外卖领取完成")


