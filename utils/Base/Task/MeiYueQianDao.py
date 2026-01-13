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
        remedy_times = 0
        while not (self.operationer.detect_element("已签到") or self.operationer.detect_element("可补签一次")):
            self.operationer.click_and_wait("签到")
            remedy_times += 1
            self.logger.info(f"每月签到{remedy_times}次")
        self.operationer.click_and_wait("持之以恒")
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        return True
