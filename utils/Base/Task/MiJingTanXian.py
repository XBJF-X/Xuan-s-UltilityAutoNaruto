from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from PySide6.QtCore import QThread

from utils.Base.Enums import KEY_INDEX
from utils.Base.Exceptions import StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


# Todo：增加根据配置文件决定是否翻牌功能
class MiJingTanXian(BaseTask):
    source_scene = "秘境探险-匹配"
    task_max_duration = timedelta(hours=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fighting = False
        self.operationer.clicker.update_coordinates([
            self.config.get_config("键位")[KEY_INDEX.BasicAttack],
            self.config.get_config("键位")[KEY_INDEX.FirstSkill],
            self.config.get_config("键位")[KEY_INDEX.SecondSkill],
            self.config.get_config("键位")[KEY_INDEX.Substitution],
            self.config.get_config("键位")[KEY_INDEX.UltimateSkill]])

    @TransitionOn()
    def _(self):
        self.fighting = False
        self.operationer.clicker.stop()
        if not self.operationer.detect_element(
                "剩余挑战券-0",
                max_time=0.7,
                wait_time=3,
                auto_raise=False
        ):
            self.operationer.click_and_wait("出战")
            self.logger.info("挑战券不为0，继续执行")
            return False
        self.update_next_execute_time()
        return True

    @TransitionOn("秘境奖励")
    def _(self):
        self.fighting = False
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("返回")
        return False

    @TransitionOn("恭喜你获得")
    def _(self):
        self.fighting = False
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("秘境探险-匹配-继续挑战确认")
    def _(self):
        self.operationer.click_and_wait("今日不再提示")
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("副本内")
    def _(self):
        if not self.fighting:
            flag = self.operationer.search_and_detect(
                [
                    self.operationer.get_element("落岩秘境"),
                    self.operationer.get_element("阴阳秘境"),
                    self.operationer.get_element("雷霆秘境"),
                    self.operationer.get_element("烈炎秘境"),
                    self.operationer.get_element("水牢秘境"),
                    self.operationer.get_element("毒风秘境"),
                    self.operationer.get_element("罡体秘境"),
                ],
                [],
                once_max_attempts=1,
                max_attempts=1,
                wait_time=0
            )
            # if flag == 1:
            #     self.logger.info("检测到落岩秘境，开始战斗")
            #     # 检测到[落岩秘境]，开始走两步开始连点，停止条件为[胜利/返回图标出现]
            #     joystick_coordinate = self.config.get_config("键位")[KEY_INDEX.JoyStick]
            #     self.operationer.long_press(joystick_coordinate[0] + 60, joystick_coordinate[1], 1.5)
            #     self.fighting = True
            #     self.operationer.clicker.start()
            if flag in [1, 3, 4, 5, 7]:
                self.logger.info("检测到可连点过的秘境，开始战斗")
                self.fighting = True
                self.operationer.clicker.start()
            else:
                self.logger.info("不是可连点过的秘境，退出战斗")
                # 点暂停，退出，确认
                self.operationer.clicker.stop()
                self.operationer.click_and_wait("暂停")
        return False

    @TransitionOn("副本内-暂停")
    def _(self):
        self.fighting = False
        self.operationer.click_and_wait("退出战斗")
        return False

    @TransitionOn("副本内-暂停-退出战斗确认")
    def _(self):
        self.fighting = False
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("未知场景")
    def _(self):
        self.fighting = False
        self.operationer.clicker.stop()
        return False

    @TransitionOn("未注册场景")
    def _(self):
        self.fighting = False
        self.operationer.clicker.stop()
        return False
