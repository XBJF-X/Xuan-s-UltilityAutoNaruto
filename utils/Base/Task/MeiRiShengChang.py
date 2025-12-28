from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from PySide6.QtCore import QThread

from utils.Base.Enums import KEY_INDEX
from utils.Base.Exceptions import StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class MeiRiShengChang(BaseTask):
    source_scene = "忍术对战"
    task_max_duration = timedelta(hours=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checked = False
        self.finished = False
        self.operationer.clicker.update_coordinates([
            self.config.get_config("键位")[KEY_INDEX.BasicAttack],
            self.config.get_config("键位")[KEY_INDEX.FirstSkill],
            self.config.get_config("键位")[KEY_INDEX.SecondSkill],
            self.config.get_config("键位")[KEY_INDEX.UltimateSkill],
            self.config.get_config("键位")[KEY_INDEX.SecretScroll],
            self.config.get_config("键位")[KEY_INDEX.Summon],
            self.config.get_config("键位")[KEY_INDEX.Substitution]
        ])

    @TransitionOn()
    def _(self):
        self.operationer.clicker.stop()
        if not self.checked:
            self.operationer.clicker.stop()
            self.operationer.click_and_wait("决斗任务")
            return False
        if not self.finished:
            self.operationer.click_and_wait("开战")
            self.operationer.click_and_wait("开战")
            self.operationer.clicker.start()
            return False
        self.operationer.click_and_wait("X")
        self.logger.info("结束执行")
        self.update_next_execute_time()
        return True

    @TransitionOn("决斗场-匹配中")
    def _(self):
        self.operationer.clicker.stop()
        QThread.msleep(1000)
        return False

    @TransitionOn("忍术对战-决斗任务")
    def _(self):
        self.operationer.clicker.stop()
        self.logger.info("领取所有待领取的决斗任务宝箱")
        while self.operationer.search_and_click(
                [
                    "宝箱-领取"
                ],
                [],
                max_attempts=1,
        ):
            continue
        # 检测有无可追回宝箱
        if self.operationer.click_and_wait("宝箱-追回"):
            self.logger.info("存在可追回每日胜场宝箱")
            self.checked = False
            return False
        if not self.operationer.search_and_detect(
                [
                    self.operationer.get_element("宝箱-未达成")
                ],
                [
                    {'swipe':
                        {"start_coordinate": [1095, 618], "end_coordinate": [1095, 167],
                            "duration": 0.7}}
                ],
                max_attempts=1,
                bool_debug=True
        ):
            self.checked = True
            self.finished = True
            self.operationer.click_and_wait("X")
            self.update_next_execute_time()
            return True
        self.checked = True
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("决斗任务-追回")
    def _(self):
        self.operationer.click_and_wait("追回", wait_time=0)
        if self.operationer.detect_element("道具不足", auto_raise=False):
            self.operationer.click_and_wait("X")
        return False

    @TransitionOn("决斗场-结算")
    def _(self):
        self.checked = False
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("决斗场-战斗中")
    def _(self):
        self.checked = False
        self.operationer.clicker.start()
        QThread.msleep(1000)
        return False

    @TransitionOn("决斗场-单局结算")
    def _(self):
        self.checked = False
        self.operationer.clicker.stop()
        QThread.msleep(5000)
        return False

    @TransitionOn("你的对手离开了游戏")
    def _(self):
        self.checked = False
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("未知场景")
    def _(self):
        self.operationer.clicker.stop()
        QThread.msleep(1000)
        return False

    @TransitionOn("未注册场景")
    def _(self):
        self.operationer.clicker.stop()
        QThread.msleep(1000)
        return False

