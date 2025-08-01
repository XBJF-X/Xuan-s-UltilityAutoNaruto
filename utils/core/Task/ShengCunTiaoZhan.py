import time

from utils.core.Task.BaseTask import BaseTask


class ShengCunTiaoZhan(BaseTask):

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
            self.detect_and_wait({
                "type": "SCENE",
                "name": "奖励"
            })
            self.logger.debug("跳转至[生存挑战]")
            # 点击完成1关生存挑战-立刻前往
            if not self.click_and_search(
                    [
                        {"type": "ELEMENT", "name": "完成1关生存挑战-立刻前往"}
                    ],
                    [
                        {
                            "swipe": {
                                "start_coordinate": [1504, 340],
                                "end_coordinate": [344, 340],
                                "duration": 1
                            }
                        }
                    ],
                    3
            ):
                raise self.EndEarly("无法跳转到[生存挑战]，可能已经完成")
            # 确认生存挑战界面出现
            self.detect_and_wait({
                "type": "SCENE",
                "name": "生存挑战"
            })
            self.logger.debug("关闭系统自动打的弹窗")
            # 随便点一下把自动打的弹窗点掉
            self.click_and_wait({
                "type": "COORDINATE",
                "coordinate": [800, 750]})
            self.click_and_wait({
                "type": "COORDINATE",
                "coordinate": [800, 750]})
            self.logger.debug("开始扫荡")
            # 点击开始扫荡图标
            self.click_and_wait({
                'type': "ELEMENT",
                'name': "生存挑战-开始扫荡"
            })
            if self.detect_and_wait({
                'type': "ELEMENT",
                'name': "生存挑战-没有可以出战的忍者"
            }, max_time=2
            ):
                self.logger.debug("没有可出战的忍者，将进行重置")
                if self.click_and_wait({
                    'type': "ELEMENT",
                    'name': "生存挑战-重置"
                }):
                    if self.click_and_wait({
                        'type': "ELEMENT",
                        'name': "生存挑战-重置-确认"
                    }):
                        # 随便点一下把自动打的弹窗点掉
                        self.click_and_wait({
                            "type": "COORDINATE",
                            "coordinate": [800, 750]})
                        self.click_and_wait({
                            "type": "COORDINATE",
                            "coordinate": [800, 750]})
                    else:
                        raise self.StepFailedError("重置失败，将提前退出执行")

            # 点击准备就绪
            if self.click_and_wait({
                'type': "ELEMENT",
                'name': "生存挑战-准备就绪"
            }):
                self.logger.debug("准备就绪")
                # 点击确定
                if not self.click_and_wait({
                    'type': "ELEMENT",
                    'name': "生存挑战-准备就绪-确定"
                }, wait_time=3):
                    raise self.StepFailedError("第一次点击确定失败，提前退出执行")
                # 点击确定
                if not self.click_and_wait({
                    'type': "ELEMENT",
                    'name': "生存挑战-准备就绪-确定-确定"
                }, wait_time=3):
                    raise self.StepFailedError("第二次点击确定失败，提前退出执行")
                self.logger.debug("系统开始自动扫荡")

                # 等待生存挑战-已通过所有关卡出现
                while not self.detect_and_search(
                        [
                            {'type': "ELEMENT", 'name': "生存挑战-已通过所有关卡"}
                            # {'type': "ELEMENT",'name': "生存挑战-可出战的忍者不足"},
                        ],
                        [],
                        1,
                        0
                ):
                    continue
                self.logger.debug("系统自动扫荡结束")
            else:
                raise self.StepFailedError("准备就绪失败，提前退出执行")
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
