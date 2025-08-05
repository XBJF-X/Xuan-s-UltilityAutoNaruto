from utils.KeyMapConfiguration import KEY_INDEX
from utils.Task import MeiRiShengChang
from utils.Task.BaseTask import BaseTask


class MeiZhouShengChang(MeiRiShengChang):

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
                            "start_coordinate": [1345, 86],
                            "end_coordinate": [462, 86],
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

        # 假如周胜场没满，则继续挂周胜
        while not self.detect_and_wait({
            'type': "ELEMENT",
            'name': "决斗任务-满胜场"
        }, max_time=5):
            self.logger.warning("周胜场未满，继续执行")
            # 点掉决斗任务窗口
            self.click_and_wait({
                'type': "COORDINATE",
                'coordinate': [1523, 45]
            })
            self.fight()
            self.logger.info("查看[决斗场-忍术对战-单人模式-决斗任务]")
            if not self.click_and_wait({
                'type': "ELEMENT",
                'name': "决斗场-忍术对战-单人模式-决斗任务"
            }, max_time=3):
                raise self.StepFailedError("未进入[决斗场-忍术对战-单人模式-决斗任务]")
            if not self.detect_and_wait({
                'type': "SCENE",
                'name': "决斗场-忍术对战-单人模式-决斗任务"
            }, max_time=5):
                raise self.StepFailedError("[决斗场-忍术对战-单人模式-决斗任务]未出现")
            self.logger.info("领取所有待领取的决斗任务宝箱")
            while self.click_and_wait({
                'type': "ELEMENT",
                'name': "决斗任务-宝箱-待领取"
            }, max_time=3):
                continue
        self.logger.warning("周胜场已满")
        # 点掉决斗任务弹窗
        self.click_and_wait({
            'type': "COORDINATE",
            'coordinate': [1523, 45]
        })
        self._update_next_execute_time()
