from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Base.Exceptions import EndEarly, StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


# Todo：优化接取算法，只接取高质量任务
# Todo：解决推荐小队无法推荐的情况，比如人物不足
class RenWuJiHuiSuo(BaseTask):
    source_scene = "任务集会所"
    task_max_duration = timedelta(minutes=5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_sum = 0

    @TransitionOn()
    def _(self):
        self.logger.info("开始领取任务奖励")
        if self.operationer.click_and_wait("可领取"):
            return False

        self.logger.info("开始接取任务")
        # 先看看是不是已经领完了所有任务了
        if self.operationer.detect_element("今天所有任务已经领完"):
            self.update_next_execute_time()
            raise EndEarly("今日任务已经领完，提前退出执行")

        if not self.operationer.detect_element(
                "今天所有任务已经领完",
                max_time=0.5,
        ):
            if self.operationer.click_and_wait("接取"):
                return False
            if self.operationer.click_and_wait("超影免费"):
                self.logger.info("刷新任务列表")
                return False
            else:
                # 能接取的都接了，无法刷新，可以退出执行了
                self.operationer.click_and_wait("X")
                self.update_next_execute_time(3, timedelta(hours=1))
                raise EndEarly("无法刷新，提前退出执行")
        self.operationer.click_and_wait("X")
        self.update_next_execute_time(3, timedelta(hours=1))
        return True

    @TransitionOn("任务集会所-接取")
    def _(self):
        if not self.operationer.search_and_click(
                [
                    "推荐小队",
                    "默认忍者"
                ],
                [],
                max_attempts=2

        ):
            raise StepFailedError("安排任务忍者失败")
        # 出战
        self.operationer.click_and_wait(
            "出发",
            wait_time=0
        )
        if self.operationer.detect_element(
                "任务栏满了",
                max_time=0.7
        ):
            self.operationer.click_and_wait("X")
            self.update_next_execute_time(3, timedelta(hours=1))
            raise EndEarly("任务栏已满，等待下次检查")
        else:
            self.task_sum += 1
            self.logger.info(f"已接取 {self.task_sum} 个任务")
        return False

    @TransitionOn("任务奖励-一键领取")
    def _(self):
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("恭喜你获得")
    def _(self):
        self.operationer.click_and_wait("X")
        return False
