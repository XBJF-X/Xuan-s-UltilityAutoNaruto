from utils.core.Task.BaseTask import BaseTask

class MeiYueQianDao(BaseTask):

    def _execute(self):
        self.logger.debug(f"开始执行")
        try:
            # 确定在主场景
            if not self.home():
                raise self.StepFailedError("无法回到[主场景]")

            self.logger.debug("进入[活动]")
            if not self.click_and_wait({
                'type': "ELEMENT",
                'name': "主场景-活动"
            }):
                raise self.StepFailedError("进入[活动]失败")
            if not self.detect_and_wait({
                'type': "SCENE",
                'name': "活动"
            }):
                raise self.StepFailedError("[活动]未出现")
            self.logger.debug("进入[每月签到]")

            if not self.click_and_search(
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
                3
            ):
                raise self.StepFailedError("未找到[活动-每月签到]")

            self.logger.debug("开始每月签到")
            if not self.click_and_wait({
                'type': "ELEMENT",
                'name': "活动-每月签到-签到"
            }):
                raise self.EndEarly("签到失败，可能已签到")
            else:
                self.logger.debug("每月签到成功")
            self._update_next_execute_time()

        except self.StepFailedError as e:
            self.logger.error(e)
        except self.EndEarly as e:
            self._update_next_execute_time()
            self.logger.warning(e)
        finally:
            self.home()
            self.logger.debug(f"执行完毕")
            self.callback(self)
