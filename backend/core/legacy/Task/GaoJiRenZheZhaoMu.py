from datetime import timedelta

from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn
from backend.core.legacy.Task.schedule import Interval


class GaoJiRenZheZhaoMu(BaseTask):
    source_scene = "高级招募"
    task_max_duration = timedelta(minutes=3)
    # 冷却型：窗口 [当日 5:01, +2 天)，完成后按冷却延后（成功 2 天 / 失败 10 分钟）
    schedule = Interval(timedelta(days=2), window_span=timedelta(days=2))

    @TransitionOn()
    def _(self):
        self.logger.info("进行免费高级招募")
        # 点击高级招募-免费
        if self.operationer.click_and_wait("免费"):
            self.logger.info("免费高级招募成功")
            return False
        else:
            self.logger.warning("免费高级招募失败")
            self.schedule_next_with_delay(timedelta(minutes=10))
        self.operationer.click_and_wait("X")
        raise TaskCompleted("免费高级招募失败，延迟重试")

    @TransitionOn("招募结果")
    def _(self):
        while not self.operationer.search_and_click(["确定"], [{
                "click": {
                    "type": "COORDINATE",
                    "coordinate": [800, 730]
                }
        }],
                                                    max_attempts=2,
                                                    once_max_time=5):
            continue
        self.schedule_next_with_delay(timedelta(days=2))
        raise TaskCompleted("高级招募完成，按冷却时间延迟")

    @TransitionOn("招募忍者已拥有")
    def _(self):
        self.operationer.click_and_wait("确定")
        return False
