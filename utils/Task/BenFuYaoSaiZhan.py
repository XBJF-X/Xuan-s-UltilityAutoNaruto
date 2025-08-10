from datetime import datetime

from utils.KeyMapConfiguration import KEY_INDEX
from utils.Task.BaseTask import BaseTask


class BenFuYaoSaiZhan(BaseTask):
    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        self.logger.info("进入[组织]")
        if not self.search_and_click(
                [
                    {"type": "ELEMENT", "name": "主场景-组织"}
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
                        {"type": "ELEMENT", "name": "主场景-组织"}
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
                raise self.StepFailedError("无法进入[组织]")
        # 确认进入主场景中的组织界面了
        self.detect_and_wait({'type': "SCENE", 'name': "主场景-组织"})
        # 进入玩法界面
        self.click_and_wait({'type': "COORDINATE", 'coordinate': (159, 550)})
        # 搜索要塞争夺战
        if not self.search_and_click(
                [
                    {"type": "ELEMENT", "name": "主场景-组织-要塞争夺战-前往"}
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
            raise self.StepFailedError("无法进入[要塞争夺战]")
        # 进入本服要塞战
        self.click_and_wait({"type": "ELEMENT", "name": "组织-要塞争夺战-本服要塞战"})
        target_fortress = self.config.get_task_config("本服要塞战", "目标要塞")
        # 滑动到左上角
        self.swipe_and_wait()
        # 搜索，搜不到右滑
        # 搜索，搜不到下滑
        # 搜索，搜不到左滑
        # 搜索，搜不到raise
        # 找到后点击攻击进入要塞内
        # 检查有无匹配中的字样，没有的话就按摇杆右移
        while datetime.now() <= 1:
            while not self.detect_and_wait(
                    {"type": "ELEMENT", "name": "组织-要塞争夺战-本服要塞战-匹配中"},
                    auto_raise=False
            ):
                joystick_coordinate = self.config.get_config("键位")[KEY_INDEX.JoyStick]
                self.long_press(joystick_coordinate[0], joystick_coordinate[1], 2)
            self._handle_fight()
        self.logger.info("战斗结束，退回主场景")
        self._update_next_execute_time()

    def _handle_fight(self):
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
                        {"type": "ELEMENT", "name": "决斗场-胜者"},
                        {"type": "ELEMENT", "name": "决斗场-忍术对战-单人模式-你的对手离开了游戏"},
                    ],
                    max_workers=7
                )
                self.logger.info("对局结束，返回[单人模式-首页]")
        # 先回到单人模式首页
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
