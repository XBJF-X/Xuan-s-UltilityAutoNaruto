from datetime import timedelta

from utils.Task.BaseTask import BaseTask


class PaiHangBangDianZan(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        self.logger.info("进入[排行榜]")
        if not self.search_and_click(
                [
                    {"type": "ELEMENT", "name": "主场景-排行榜"}
                ],
                [
                    {
                        "swipe": {
                            "start_coordinate": [1400, 340],
                            "end_coordinate": [344, 340],
                            "duration": 1
                        }
                    }
                ],
                max_attempts=2

        ):
            if not self.search_and_click(
                [
                    {"type": "ELEMENT", "name": "主场景-排行榜"}
                ],
                [
                    {
                        "swipe": {
                            "start_coordinate": [344, 340],
                            "end_coordinate": [1400, 340],
                            "duration": 1
                        }
                    }
                ],
                max_attempts=2
            ):
                raise self.StepFailedError("无法进入[排行榜]")
        self.detect_and_wait({'type': "SCENE",'name': "排行榜"})
        self.logger.info("点赞")
        self.click_and_wait({'type': "ELEMENT",'name': "排行榜-点赞"})
        self.logger.info("点赞成功")
        self._update_next_execute_time(time_offset=timedelta(hours=8))
