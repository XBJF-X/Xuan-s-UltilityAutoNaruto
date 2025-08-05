from utils.KeyMapConfiguration import KEY_INDEX
from utils.Task.BaseTask import BaseTask


class MeiRiShengChang(BaseTask):
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
        while self.search_and_click(
                [
                    {'type': "ELEMENT", 'name': "决斗任务-宝箱-待领取"}
                ],
                [
                    {'swipe':
                        {"start_coordinate": [462, 86], "end_coordinate": [1345, 86], "duration": 1}
                    }
                ],
                max_attempts=1,
        ):
            continue

        # 假如存在未达成的宝箱，则挂周胜
        while self.search_and_detect(
            [
                {'type': "ELEMENT",'name': "决斗任务-宝箱-未达成"}
            ],
            [
                {'swipe':{"start_coordinate": [462, 86],"end_coordinate": [1345, 86],"duration": 1}}
            ],
            max_attempts=1,
        ):
            self.logger.info("存在未达成的每日胜场任务，继续执行")
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
            while self.search_and_click(
                [
                    {'type': "ELEMENT", 'name': "决斗任务-宝箱-待领取"}
                ],
                [
                    {'swipe':
                        {"start_coordinate": [462, 86], "end_coordinate": [1345, 86],"duration": 1}
                    }
                ],
                max_attempts=1,
            ):
                continue

        self.logger.info("每日胜场宝箱已领完")
        self.click_and_wait({
            'type': "COORDINATE",
            'coordinate': [1523, 45]
        })
        self._update_next_execute_time()

    def fight(self):
        """
        通用的刷决斗场函数，周胜赛季胜等等都可以使用
        :return:
        """
        # 进入战斗
        if self.click_and_wait({
            'type': "ELEMENT",
            'name': "决斗场-忍术对战-单人模式-开战"
        }):
            self.click_and_wait({
                'type': "ELEMENT",
                'name': "决斗场-忍术对战-单人模式-开战"
            })
            flag = self.search_and_detect(
                [
                    {'type': "ELEMENT", 'name': "决斗场-60"},
                    {"type": "ELEMENT",
                        "name": "决斗场-忍术对战-单人模式-你的对手离开了游戏"},
                ],
                [
                    {'click': {'type': "COORDINATE", 'coordinate': [800, 569]}}
                ],
                search_max_time=100,
            )
            if not flag:
                raise self.StepFailedError("开始战斗超时")
            else:
                if flag == 2:
                    self.logger.warning("对手退出游戏，即将返回[忍术对战-单人模式]")
                    if not self.search_and_detect(
                            [
                                {'type': "SCENE", 'name': "决斗场-忍术对战-单人模式"}
                            ],
                            [
                                {'click': {'type': "COORDINATE", 'coordinate': [800, 745]}},
                                {'click': {'type': "COORDINATE", 'coordinate': [800, 569]}}
                            ],
                            search_max_time=30
                    ):
                        raise self.StepFailedError("战斗结束后无法退回[忍术对战-单人模式]")
                elif flag == 1:
                    self.logger.info("倒计时60s出现，连点执行中...")
                    # 使用连点器，结束的标志定为举报反馈
                    self.auto_cycle_actioner(
                        [
                            ("CLICK", self.config.get_config("键位")[KEY_INDEX.BasicAttack]),
                            ("CLICK", self.config.get_config("键位")[KEY_INDEX.FirstSkill]),
                            ("CLICK", self.config.get_config("键位")[KEY_INDEX.SecondSkill]),
                            ("CLICK", self.config.get_config("键位")[KEY_INDEX.UltimateSkill]),
                            ("CLICK", self.config.get_config("键位")[KEY_INDEX.SecretScroll]),
                            ("CLICK", self.config.get_config("键位")[KEY_INDEX.Summon]),
                            ("CLICK", self.config.get_config("键位")[KEY_INDEX.Substitution])
                        ],
                        stop_conditions=[
                            {"type": "ELEMENT", "name": "决斗场-举报反馈"},
                            {"type": "ELEMENT","name": "决斗场-忍术对战-单人模式-你的对手离开了游戏"},
                        ],
                        max_workers=7
                    )
                    self.logger.info("对局结束，返回[单人模式-首页]")
            # 先回到单人模式首页，看看有没有宝箱能领的，能领的都领掉
            if not self.search_and_detect(
                    [
                        {'type': "SCENE", 'name': "决斗场-忍术对战-单人模式"}
                    ],
                    [
                        {'click': {'type': "COORDINATE", 'coordinate': [800, 745]}},
                        {'click': {'type': "COORDINATE", 'coordinate': [800, 569]}}
                    ],
                    search_max_time=30
            ):
                raise self.StepFailedError("战斗结束后无法退回[忍术对战-单人模式]")
        else:
            raise self.StepFailedError("点击出战失败")
