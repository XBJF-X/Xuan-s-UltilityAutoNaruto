from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class PuTongRenZheZhaoMu(BaseTask):
    source_scene = "普通招募"
    task_max_duration = timedelta(minutes=2)

    @TransitionOn()
    def _(self):
        self.logger.info("进行免费普通招募")
        # 点击普通招募-免费
        if self.operationer.click_and_wait(
                "免费",
                auto_raise=False
        ):
            self.logger.info("免费普通招募成功")
            return False
        else:
            self.logger.warning("免费普通招募失败")
            self.update_next_execute_time(delta=timedelta(hours=3))
            self.operationer.click_and_wait("X")
            return True

    @TransitionOn("招募结果")
    def _(self):
        while not self.operationer.search_and_click(
                [
                    "确定"
                ],
                [
                    {
                        "click": {
                            "type": "COORDINATE",
                            "coordinate": [800, 730]
                        }
                    }
                ],
                max_attempts=2,
                once_max_time=5
        ):
            continue
        self.update_next_execute_time()
        return True
