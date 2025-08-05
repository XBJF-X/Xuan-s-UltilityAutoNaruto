from utils.KeyMapConfiguration import KEY_INDEX
from utils.Task import MeiRiShengChang
from utils.Task.BaseTask import BaseTask


class SaiJiShengChang(MeiRiShengChang):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        self.logger.info("进入[决斗场-首页]")
        if not self.search_and_click(
                [
                    {"type": "ELEMENT", "name": "主场景-决斗场"}
                ],
                [
                    {
                        "swipe": {
                            "start_coordinate": [1345, 340],
                            "end_coordinate": [462, 340],
                            "duration": 1
                        }
                    }
                ],
                max_attempts=2

        ):
            if not self.search_and_click(
                    [
                        {"type": "ELEMENT", "name": "主场景-决斗场"}
                    ],
                    [
                        {
                            "swipe": {
                                "start_coordinate": [462, 86],
                                "end_coordinate": [1345, 86],
                                "duration": 1
                            }
                        }
                    ],
                    max_attempts=2

            ):
                raise self.StepFailedError("无法进入[决斗场]")
        if not self.detect_and_wait({
            'type': "SCENE",
            'name': "决斗场-首页"
        }):
            raise self.StepFailedError("未进入[决斗场-首页]")

        self.logger.info("进入[决斗赛季]")
        self.click_and_wait({
            'type': "COORDINATE",
            'coordinate': [1506, 206]
        }, wait_time=3)

        while not self.detect_and_wait({
            'type': "ELEMENT",
            'name': "赛季-决斗场内获得N次胜利-已领"
        }, wait_time=2, max_time=1):
            self.esc()
            self.logger.info("进入[决斗场-忍术对战-单人模式]")
            if not self.click_and_wait({
                'type': "ELEMENT",
                'name': "决斗场-忍术对战"
            }):
                raise self.StepFailedError("未进入[决斗场-忍术对战-单人模式]")
            if not self.detect_and_wait({
                'type': "SCENE",
                'name': "决斗场-忍术对战-单人模式"
            }):
                raise self.StepFailedError("[决斗场-忍术对战-单人模式]未出现")
            self.logger.info("查看[决斗场-忍术对战-单人模式-决斗任务]")
            if not self.click_and_wait({
                'type': "ELEMENT",
                'name': "决斗场-忍术对战-单人模式-决斗任务"
            }):
                raise self.StepFailedError("未进入[决斗场-忍术对战-单人模式-决斗任务]")
            if not self.detect_and_wait({
                'type': "SCENE",
                'name': "决斗场-忍术对战-单人模式-决斗任务"
            }):
                raise self.StepFailedError("[决斗场-忍术对战-单人模式-决斗任务]未出现")
            self.logger.info("领取所有待领取的决斗任务宝箱")
            while self.click_and_wait({
                'type': "ELEMENT",
                'name': "决斗任务-宝箱-待领取"
            }):
                continue

            self.click_and_wait({
                'type': "COORDINATE",
                'coordinate': [1523, 45]
            })
            self.fight()
            self.logger.info("返回[决斗赛季]")
            self.home(home_name="决斗场-首页")
            if not self.detect_and_wait({
                'type': "SCENE",
                'name': "决斗场-首页"
            }, max_time=3):
                raise self.StepFailedError("未进入[决斗场-首页]")
            self.click_and_wait({
                'type': "COORDINATE",
                'coordinate': [1506, 206]
            }, wait_time=3)

        self.logger.warning("已打完所有赛季胜场")
        self.click_and_wait({
            'type': "COORDINATE",
            'coordinate': [1523, 45]
        })
        self._update_next_execute_time()
