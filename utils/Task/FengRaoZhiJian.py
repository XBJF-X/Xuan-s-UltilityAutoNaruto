from utils.KeyMapConfiguration import KEY_INDEX
from utils.Task.BaseTask import BaseTask


class FengRaoZhiJian(BaseTask):
    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        self.logger.info("进入[奖励]界面")
        # 点击奖励图标
        self.click_and_wait({"type": "ELEMENT", "name": "主场景-奖励"})
        # 确认奖励界面出现
        self.detect_and_wait({"type": "SCENE", "name": "奖励"})
        self.logger.info("跳转至[丰饶之间]")
        # 点击挑战丰饶之间-立刻前往
        if not self.search_and_click(
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
                max_attempts=3
        ):
            self._update_next_execute_time()
            raise self.EndEarly("无法跳转至[丰饶之间]，可能已经完成")
        # 确认丰饶之间界面出现
        self.detect_and_wait({"type": "SCENE", "name": "丰饶之间"})

        # 先看看能不能用超影直接过
        if self.click_and_wait(
                {"type": "ELEMENT", "name": "丰饶之间-一键完成"},
                auto_raise=False
        ):
            # 点击丰饶之间-超影免费
            if self.click_and_wait(
                    {"type": "ELEMENT", "name": "丰饶之间-超影免费"},
                    wait_time=3,
                    auto_raise=False
            ):
                self.logger.info("领取丰饶之间奖励")
                # 使用连点器过丰饶之间
                self.auto_cycle_actioner(
                    [
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.BasicAttack]),
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.FirstSkill]),
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.SecondSkill]),
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.UltimateSkill]),
                    ],
                    stop_conditions=[
                        {"type": "SCENE", "name": "丰饶之间"}
                    ],
                    max_workers=4
                )
                self._update_next_execute_time()
                raise self.EndEarly("免费完成，提前结束执行")
            else:
                self.logger.info("没有超影，返回[丰饶之间]界面")
                # 随便点下退出一键完成界面
                self.click_and_wait({"type": "COORDINATE", "coordinate": [800, 800]})
        else:
            self.logger.warning("点击一键完成失败")

        # 点击丰饶之间-挑战
        self.click_and_wait(
                {"type": "ELEMENT", "name": "丰饶之间-挑战"},
                wait_time=4
        )
        self.logger.info("无法免费完成，开始自动挑战")
        # 使用连点器过丰饶之间
        self.auto_cycle_actioner(
            [
                ("CLICK", self.config.get_config("键位")[KEY_INDEX.BasicAttack]),
                ("CLICK", self.config.get_config("键位")[KEY_INDEX.FirstSkill]),
                ("CLICK", self.config.get_config("键位")[KEY_INDEX.SecondSkill]),
                ("CLICK", self.config.get_config("键位")[KEY_INDEX.UltimateSkill]),
            ],
            stop_conditions=[
                {"type": "ELEMENT", "name": "丰饶之间-点击任意位置关闭界面"}
            ],
            max_workers=4
        )
        self.logger.info("挑战[丰饶之间]成功")

        if not self.search_and_detect(
                [
                    {"type": "SCENE", "name": "丰饶之间"}
                ],
                [
                    {'click': {'type': "COORDINATE", 'coordinate': (800, 854)}}
                ],
                search_max_time=180
        ):
            raise self.StepFailedError("退出[丰饶之间]失败")
        self._update_next_execute_time()
