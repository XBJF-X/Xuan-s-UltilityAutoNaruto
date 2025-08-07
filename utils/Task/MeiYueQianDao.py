from utils.Task.BaseTask import BaseTask


class MeiYueQianDao(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")

        self.logger.info("进入[活动]")
        self.click_and_wait({'type': "ELEMENT", 'name': "主场景-活动"})
        self.detect_and_wait({'type': "SCENE", 'name': "活动"})
        self.logger.info("进入[每月签到]")

        if not self.search_and_click(
                [
                    {'type': "ELEMENT", 'name': "活动-每月签到-未选中"},
                    {'type': "ELEMENT", 'name': "活动-每月签到-选中"},
                ],
                [
                    {
                        "swipe": {
                            "start_coordinate": [107, 846],
                            "end_coordinate": [107, 213],
                            "duration": 1
                        }
                    }
                ],
                max_attempts=2
        ):
            raise self.StepFailedError("未找到[活动-每月签到]")

        self.logger.info("开始每月签到")
        if not self.click_and_wait(
                {'type': "ELEMENT", 'name': "活动-每月签到-签到"},
                auto_raise=False
        ):
            self._update_next_execute_time()
            raise self.EndEarly("签到失败，可能已签到")
        else:
            self.logger.info("每月签到成功")
        self._update_next_execute_time()
