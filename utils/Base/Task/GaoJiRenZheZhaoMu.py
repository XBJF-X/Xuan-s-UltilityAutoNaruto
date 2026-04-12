import datetime
from datetime import timedelta
from typing import List

from utils.Base.Exceptions import TaskCompleted
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class GaoJiRenZheZhaoMu(BaseTask):
    source_scene = "高级招募"
    task_max_duration = timedelta(minutes=3)

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
    def _get_execute_window(
        self,
        dt: datetime.datetime | None = None
    ):
        if dt is None:
            dt=self.last_run_time
        dt = self._ensure_tz_aware(dt)
        today = dt.date()
        if dt.time() < datetime.time(5, 0):
            today -= timedelta(days=1)
        after_2_day = today + timedelta(days=2)

        start_dt = datetime.datetime.combine(today, self.start_line or datetime.time(5, 0), tzinfo=self.tz_info)
        if self.dead_line:
            dead_dt = datetime.datetime.combine(today, self.dead_line, tzinfo=self.tz_info)
        else:
            dead_dt = datetime.datetime.combine(after_2_day, datetime.time(5, 0), tzinfo=self.tz_info)

        return [(start_dt, dead_dt)]
