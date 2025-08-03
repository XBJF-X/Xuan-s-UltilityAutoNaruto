from utils.core.Task.BaseTask import BaseTask


class SaiJiShengChang(BaseTask):

    def _execute(self):
        self.logger.info(f"开始执行")
        try:
            # 确定在主场景
            if not self.home():
                raise self.StepFailedError("无法回到[主场景]")
            self.logger.info("进入[决斗场-首页]")
            if not self.click_and_search(
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
                    2
            ):
                if not self.click_and_search(
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
                        2
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
                if self.click_and_wait({
                    'type': "ELEMENT",
                    'name': "决斗场-忍术对战-单人模式-开战"
                }, wait_time=2
                ):
                    self.click_and_wait({
                        'type': "ELEMENT",
                        'name': "决斗场-忍术对战-单人模式-开战"
                    }, wait_time=2)
                    self.logger.info("连点执行中...")
                    # 使用连点器，结束的标志定为时刻
                    self.auto_clicker(
                        [
                            (1541, 832),
                            (1456, 862),
                            (1468, 774),
                            (1550, 735),
                            (1377, 860),
                            (1535, 640),
                            (1295, 861)
                        ],
                        stop_conditions=[
                            {"type": "ELEMENT", "name": "决斗场-举报反馈"},
                            {"type": "ELEMENT", "name": "决斗场-忍术对战-单人模式-你的对手离开了游戏"},
                        ],
                        max_workers=7
                    )
                    self.logger.info("对局结束，返回[单人模式-首页]")
                    # 先回到单人模式首页，看看有没有宝箱能领的，能领的都领掉
                    if not self.detect_and_search(
                            [
                                {'type': "SCENE", 'name': "决斗场-忍术对战-单人模式"}
                            ],
                            [
                                {'click': {'type': "COORDINATE", 'coordinate': [800, 745]}},
                                {'click': {'type': "COORDINATE", 'coordinate': [800, 569]}}
                            ],
                            30
                    ):
                        raise self.StepFailedError("战斗结束后无法退回[忍术对战-单人模式]")

                    self.logger.info("返回[决斗赛季]")
                    self.home(home_name="决斗场-首页")
                    if not self.detect_and_wait({
                        'type': "SCENE",
                        'name': "决斗场-首页"
                    }):
                        raise self.StepFailedError("未进入[决斗场-首页]")
                    self.click_and_wait({
                        'type': "COORDINATE",
                        'coordinate': [1506, 206]
                    }, wait_time=3)

                else:
                    raise self.StepFailedError("点击出战失败")

            self.logger.warning("已打完所有赛季胜场")
            self.click_and_wait({
                'type': "COORDINATE",
                'coordinate': [1523, 45]
            })

        except self.StepFailedError as e:
            self.logger.error(e)
        except self.EndEarly as e:
            self.logger.warning(e)
        finally:
            self.home()
            self.logger.info(f"执行完毕")
            self.callback(self)
