from datetime import timedelta

from utils.core.Task.BaseTask import BaseTask


class PaiHangBangDianZan(BaseTask):

    def _execute(self):
        self.logger.debug(f"开始执行")
        try:
            # 确定在主场景
            if not self.home():
                raise self.StepFailedError("无法回到[主场景]")
            self.logger.debug("进入[排行榜]")
            if not self.click_and_search(
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
                    2
            ):
                if not self.click_and_search(
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
                        2
                ):
                    raise self.StepFailedError("无法进入[排行榜]")
            if not self.detect_and_wait({
                'type': "SCENE",
                'name': "排行榜"
            }):
                raise self.StepFailedError("未进入[排行榜]")
            self.logger.debug("点赞")
            if not self.click_and_wait({
                'type': "ELEMENT",
                'name': "排行榜-点赞"
            }):
                raise self.StepFailedError("点赞未成功，可能是已经点赞过了")
            else:
                self.logger.debug("点赞成功")
            self._update_next_execute_time(time_offset=timedelta(hours=11))

        except self.StepFailedError as e:
            self.logger.error(e)
        except self.EndEarly as e:
            self._update_next_execute_time(time_offset=timedelta(hours=11))
            self.logger.warning(e)
        finally:
            self.home()
            self.logger.debug(f"执行完毕")
            self.callback(self)
