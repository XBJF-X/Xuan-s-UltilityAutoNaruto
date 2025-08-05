from utils.KeyMapConfiguration import KEY_INDEX
from utils.Task.BaseTask import BaseTask


class MiJingTanXian(BaseTask):
    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        self.logger.info("进入奖励界面")
        # 点击奖励图标
        self.click_and_wait({"type": "ELEMENT", "name": "主场景-奖励"})
        # 确认奖励界面出现
        self.detect_and_wait({"type": "SCENE", "name": "奖励"})
        self.logger.info("跳转至[秘境探险]")
        # 点击秘境探险-立即前往
        if not self.search_and_click(
                [
                    {"type": "ELEMENT", "name": "完成秘境探险-立刻前往"}
                ],
                [
                    {
                        "swipe": {
                            "start_coordinate": [1506, 340],
                            "end_coordinate": [344, 340],
                            "duration": 1
                        }
                    }
                ],
                max_attempts=4,
                wait_time=3
        ):
            self._update_next_execute_time()
            raise self.EndEarly("无法跳转到[秘境探险]，可能已经完成")

        # 确认[秘境探险-首页]界面出现
        if not self.detect_and_wait(
                {"type": "SCENE", "name": "秘境探险-首页"},
                max_time=5,
                wait_time=3
        ):
            raise self.StepFailedError("[秘境探险]界面未出现")

        # 点击创建房间，进入[秘境探险-匹配]
        if not self.click_and_wait(
                {"type": "ELEMENT", "name": "秘境探险-首页-创建房间"}
        ):
            raise self.StepFailedError("创建房间失败")
        if not self.detect_and_wait(
                {"type": "SCENE", "name": "秘境探险-匹配"}
        ):
            raise self.StepFailedError("[秘境探险-匹配]未出现")

        self.mijingtanxian_implement()

        self._update_next_execute_time()

    def mijingtanxian_implement(self):
        # 剩余挑战券!=0的时候
        while not self.detect_and_wait(
                {"type": "ELEMENT", "name": "秘境探险-匹配-剩余挑战券-0"},
                max_time=2
        ):
            self.logger.info("挑战券不为0，继续出战")
            # 点击出战
            if not self.click_and_wait(
                    {"type": "ELEMENT", "name": "秘境探险-匹配-出战"},
                    wait_time=5
            ):
                raise self.StepFailedError("出战失败")
            if self.click_and_wait(
                    {"type": "ELEMENT", "name": "秘境探险-匹配-出战"},
            ):
                self.logger.debug("确认出战")
            # 等待检测到[落岩秘境]，如果检测到别的就退
            flag = self.search_and_detect(
                [
                    {"type": "ELEMENT", "name": "秘境探险-匹配-落岩秘境"},
                    {"type": "ELEMENT", "name": "秘境探险-匹配-阴阳秘境"},
                    {"type": "ELEMENT", "name": "秘境探险-匹配-雷霆秘境"},
                    {"type": "ELEMENT", "name": "秘境探险-匹配-烈炎秘境"},
                    {"type": "ELEMENT", "name": "秘境探险-匹配-水牢秘境"},
                    {"type": "ELEMENT", "name": "秘境探险-匹配-毒风秘境"},
                    {"type": "ELEMENT", "name": "秘境探险-匹配-罡体秘境"},
                ],
                [],
                search_max_time=60,
                once_max_time=0.05
            )
            if flag == 1:
                self.logger.info("检测到落岩秘境，开始战斗")
                # 检测到[落岩秘境]，开始走两步开始连点，停止条件为[胜利图标出现]
                joystick_coordinate = self.config.get_config("键位")[KEY_INDEX.JoyStick]
                self.long_press(joystick_coordinate[0] + 30, joystick_coordinate[1], 1.5)
                flag = self.auto_cycle_actioner(
                    [
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.BasicAttack]),
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.FirstSkill]),
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.SecondSkill]),
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.UltimateSkill]),
                    ],
                    stop_conditions=[
                        {"type": "ELEMENT", "name": "秘境探险-匹配-胜利"},
                        {"type": "ELEMENT", "name": "秘境探险-匹配-返回"}
                    ],
                    max_workers=4,
                    max_time=600,
                    bool_debug=True
                )
                if flag == 0:
                    raise self.StepFailedError("落岩秘境未正常通过")
                elif flag == -1:
                    raise self.StepFailedError("落岩秘境通过超时")
                elif flag == 1:
                    if not self.search_and_detect(
                        [
                            {"type": "SCENE", "name": "秘境探险-匹配"}
                        ],
                        [
                            {'type': "COORDINATE", 'coordinate': (800, 854)}
                        ],
                        search_max_time=60
                    ):
                        raise self.StepFailedError("秘境胜利[无奖励]，回退匹配界面失败")
                elif flag == 2:
                    if not self.click_and_wait(
                        {"type": "ELEMENT", "name": "秘境探险-匹配-返回"},
                        wait_time=3,
                        max_time=3
                    ):
                        raise self.StepFailedError("[秘境探险-匹配-返回]点击失败")
                    if not self.search_and_detect(
                        [
                            {"type": "SCENE", "name": "秘境探险-匹配"}
                        ],
                        [
                            {'type': "COORDINATE", 'coordinate': (800, 854)}
                        ],
                        search_max_time=60
                    ):
                        raise self.StepFailedError("秘境胜利，回退匹配界面失败")

            else:
                self.logger.info("不是落岩秘境，退出战斗")
                # 点暂停，退出，确认
                if not self.click_and_wait({"type": "ELEMENT", "name": "秘境探险-匹配-暂停"}):
                    raise self.StepFailedError("点击[暂停]按钮失败")
                if not self.click_and_wait({"type": "ELEMENT", "name": "秘境探险-匹配-暂停-退出战斗"}):
                    raise self.StepFailedError("点击[暂停-退出战斗]按钮失败")
                if not self.click_and_wait({"type": "ELEMENT",
                                               "name": "秘境探险-匹配-暂停-退出战斗-确定"}):
                    raise self.StepFailedError("点击[暂停-退出战斗-确定]按钮失败")

            # 等待[秘境探险-匹配]界面出现，继续检测挑战券数量
            if not self.detect_and_wait(
                    {"type": "SCENE", "name": "秘境探险-匹配"},
                    max_time=30
            ):
                raise self.StepFailedError("退出战斗，[秘境探险-匹配]未出现")
            self.logger.info("挑战券清空，结束执行")
