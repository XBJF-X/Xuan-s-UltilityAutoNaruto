from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Exceptions import EndEarly, StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class MeiYueQianDao(BaseTask):
    source_scene = "每月签到"
    task_max_duration = timedelta(minutes=3)

    @TransitionOn()
    def _(self):
        self.logger.info("开始每月签到")
        if not self.operationer.click_and_wait(
                "签到",
                auto_raise=False
        ):
            self.update_next_execute_time()
            raise EndEarly("签到失败，可能已签到")
        else:
            self.logger.info("每月签到成功")
        self.operationer.click_and_wait("持之以恒")
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        return True
