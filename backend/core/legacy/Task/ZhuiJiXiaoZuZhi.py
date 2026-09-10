from datetime import time, timedelta

from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn
from backend.core.legacy.Task.schedule import Weekday, Weekly


class ZhuiJiXiaoZuZhi(BaseTask):
    source_scene = "追击晓组织"
    task_max_duration = timedelta(minutes=3)
    # 每周任务：窗口 [本周一 12:00, 下周一 5:01)
    schedule = Weekly(Weekday.MON, at=time(12, 0))

    @TransitionOn()
    def _(self):
        self.operationer.click_and_wait("奖励")
        return False

    @TransitionOn("追击晓组织-奖励")
    def _(self):
        if self.operationer.search_and_click(
            ["领取"],
            [
                {
                    "swipe": {
                        "start_coordinate": [1317, 744],
                        "end_coordinate": [1317, 271],
                        "duration": 0.5
                    }
                }
            ],
            max_attempts=1
        ):
            self.logger.info("存在可领取奖励，已点击领取")
            return False
        self.operationer.click_and_wait("X")
        raise TaskCompleted("任务执行完成")
    @TransitionOn("任务奖励-一键领取")
    def _(self):
        self.operationer.click_and_wait("确定")
        return False

