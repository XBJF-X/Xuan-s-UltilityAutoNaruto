from utils.core.Task.BaseTask import BaseTask

class MeiZhouShengChang(BaseTask):

    def _execute(self):
        self.logger.debug(f"开始执行")
        try:
            # 确定在主场景
            if not self.home():
                raise self.StepFailedError("无法回到[主场景]")
            self.logger.debug("进入[决斗场-首页]")
            if not self.click_and_search(
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
            self.logger.debug("进入[决斗场-忍术对战-单人模式]")
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
            self.logger.debug("查看[决斗场-忍术对战-单人模式-决斗任务]")
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
            self.logger.debug("领取所有待领取的决斗任务宝箱")
            while self.click_and_wait({
                'type': "ELEMENT",
                'name': "决斗任务-宝箱-待领取"
            }):
                continue

            # 假如周胜场没满，则继续挂周胜
            while not self.detect_and_wait({
                'type': "ELEMENT",
                'name': "决斗任务-满胜场"
            }):
                self.logger.debug("周胜场未满，继续执行")
                # 点掉决斗任务窗口
                self.click_and_wait({
                    'type': "COORDINATE",
                    'coordinate': [1523, 45]
                })
                if self.click_and_wait({
                    'type': "ELEMENT",
                    'name': "决斗场-忍术对战-单人模式-开战"
                }):
                    self.click_and_wait({
                        'type': "ELEMENT",
                        'name': "决斗场-忍术对战-单人模式-开战"
                    })
                    self.logger.debug("开始检测倒计时60s出现")
                    while not self.detect_and_wait({
                        'type': "ELEMENT",
                        'name': "决斗场-60"
                    }, wait_time=0):
                        self.logger.debug("未出现倒计时60s")
                        continue
                    self.logger.debug("倒计时60s出现，连点执行中...")
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
                    self.logger.debug("对局结束，返回[单人模式-首页]")
                    # 先回到单人模式首页，看看有没有宝箱能领的，能领的都领掉
                    if not self.detect_and_search(
                            [
                                {'type': "SCENE", 'name': "决斗场-忍术对战-单人模式"}
                            ],
                            [
                                {'click': {'type': "COORDINATE", 'coordinate': [800, 745]}},
                                {'click': {'type': "COORDINATE", 'coordinate': [800, 569]}}
                            ],
                            999
                    ):
                        raise self.StepFailedError("战斗结束后无法退回[忍术对战-单人模式]")

                    self.logger.debug("查看[决斗场-忍术对战-单人模式-决斗任务]")
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
                    self.logger.debug("领取所有待领取的决斗任务宝箱")
                    while self.click_and_wait({
                        'type': "ELEMENT",
                        'name': "决斗任务-宝箱-待领取"
                    }):
                        continue
            self.logger.debug("周胜场已满")
            # 点掉决斗任务弹窗
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
            self.logger.debug(f"执行完毕")
            self.callback(self)
