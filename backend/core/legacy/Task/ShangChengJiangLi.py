from datetime import timedelta
import time

from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn


class ShangChengJiangLi(BaseTask):
    source_scene = "商城"
    task_max_duration = timedelta(minutes=3)

    def run(self):
        self.attempt_times=0
        self.max_attempt_time=3
        super().run()

    # @TransitionOn()
    # def _(self):
    #     self.operationer.click_and_wait("特权商店")
    #     self.operationer.click_and_wait("特权商店-特权积分")
    #     if self.operationer.click_and_wait("特权商店-特权积分-领取"):
    #         self.logger.info("特权商店15000铜币领取成功")
    #     else:
    #         self.logger.warning("特权商店15000铜币领取失败，可能已经被领取")
    #     self.operationer.click_and_wait("X")
    #     raise TaskCompleted("任务执行完成")

    @TransitionOn()
    def _(self):
        time.sleep(0.5)
        self.operationer.search_and_click(
            ["商店"],
            [{
                "swipe": {
                    "start_coordinate": [137, 733],
                    "end_coordinate": [137, 224],
                    "duration": 0.5
                }
            }],
            max_attempts=2,
        )
        self.operationer.swipe_and_wait(
                        (137, 224),
                        (137, 733),
                        duration=0.2,
                        wait_time=0,
                        times=2
                    )
        if not self.operationer.search_and_click(
                    ["商店列表"],
                    [{
                        "swipe": {
                            "start_coordinate": [137, 733],
                            "end_coordinate": [137, 224],
                            "duration": 0.5
                        }
                    }],
                    match_text="特权商店",
                    max_attempts=3,
                ):
            if self.attempt_times<self.max_attempt_time:
                self.attempt_times+=1
                return False
        self.operationer.click_and_wait("特权积分")
        if self.operationer.click_and_wait("铜币领取","领取"):
            self.logger.info("特权商店15000铜币领取成功")
        else:
            self.logger.warning("特权商店15000铜币领取失败，可能已经被领取")
        self.operationer.click_and_wait("X")
        raise TaskCompleted("任务执行完成")