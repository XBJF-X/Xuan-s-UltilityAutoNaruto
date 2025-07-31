from utils.core.Task.BaseTask import BaseTask


class FengRaoZhiJian(BaseTask):
    def _execute(self):
        self.logger.debug(f"开始执行")
        try:
            # 确定在主场景
            if not self.home():
                raise self.StepFailedError("无法回到[主场景]")
            self.logger.debug("进入[奖励]界面")
            # 点击奖励图标
            self.click_and_wait({
                "type": "ELEMENT",
                "name": "主场景-奖励"
            })
            # 确认奖励界面出现
            if not self.detect_and_wait({
                "type": "SCENE",
                "name": "奖励"
            }):
                raise self.StepFailedError("进入[奖励]界面失败")
            self.logger.debug("跳转至[丰饶之间]")
            # 点击挑战丰饶之间-立刻前往
            if not self.click_and_search(
                    [
                        {"type": "ELEMENT", "name": "挑战丰饶之间-立刻前往"}
                    ],
                    [
                        {
                            "swipe": {
                                "start_coordinate": [1506, 340],
                                "end_coordinate": [340, 340],
                                "duration": 1
                            }
                        }
                    ],
                    3
            ):
                raise self.EndEarly("无法跳转至[丰饶之间]，可能已经完成")
            # 确认丰饶之间界面出现
            if not self.detect_and_wait({
                "type": "SCENE",
                "name": "丰饶之间"
            }):
                raise self.StepFailedError("[丰饶之间]未出现")

            # 先看看能不能用超影直接过
            if self.click_and_wait({
                "type": "ELEMENT",
                "name": "丰饶之间-一键完成"
            }):
                # 点击丰饶之间-超影免费
                if self.click_and_wait({
                    "type": "ELEMENT",
                    "name": "丰饶之间-超影免费"
                }, wait_time=3):
                    self.logger.debug("领取丰饶之间奖励")
                    # 使用连点器过丰饶之间
                    self.auto_clicker(
                        [
                            (942, 319),
                            (955, 234),
                            (1040, 190),
                            (1033, 291)
                        ],
                        stop_conditions=[
                            {"type": "SCENE", "name": "丰饶之间"}
                        ],
                        max_workers=4
                    )
                    raise self.EndEarly("免费完成，提前结束执行")
                else:
                    self.logger.debug("没有超影，返回[丰饶之间]界面")
                    # 随便点下退出一键完成界面
                    self.click_and_wait({
                        "type": "COORDINATE",
                        "coordinate": [800, 800]
                    })
            else:
                self.logger.warning("点击一键完成失败")

            # 点击丰饶之间-挑战
            if self.click_and_wait({
                "type": "ELEMENT",
                "name": "丰饶之间-挑战"
            }, wait_time=4):
                self.logger.debug("无法免费完成，开始手动挑战")
                # 使用连点器过丰饶之间
                self.auto_clicker(
                    [
                        (942, 319),
                        (955, 234),
                        (1040, 190),
                        (1033, 291)
                    ],
                    stop_conditions=[
                        {"type": "SCENE", "name": "丰饶之间"}
                    ],
                    max_workers=4
                )
                self.logger.debug("挑战[丰饶之间]成功")
            else:
                raise self.StepFailedError("挑战[丰饶之间]失败，提前退出执行")
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
