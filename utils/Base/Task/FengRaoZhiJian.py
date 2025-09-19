from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from PySide6.QtCore import QThread

from utils.Base.Enums import KEY_INDEX
from utils.Base.Exceptions import EndEarly, StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class FengRaoZhiJian(BaseTask):
    source_scene = "丰饶之间"
    task_max_duration = timedelta(minutes=10)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.free_tryed = False
        self.finished = False
        self.operationer.clicker.update_coordinates([
            self.config.get_config("键位")[KEY_INDEX.BasicAttack],
            self.config.get_config("键位")[KEY_INDEX.FirstSkill],
            self.config.get_config("键位")[KEY_INDEX.SecondSkill],
            self.config.get_config("键位")[KEY_INDEX.UltimateSkill]
        ])

    @TransitionOn("丰饶之间")
    def _(self):
        if self.operationer.detect_element(
                "今日已完成挑战",
                max_time=0.3,
                auto_raise=False
        ):
            self.update_next_execute_time()
            return True
        if not self.free_tryed:
            self.operationer.click_and_wait("一键完成")
            return False
        if not self.finished:
            # 点击丰饶之间-挑战
            self.logger.info("无法免费完成，开始自动挑战")
            self.operationer.click_and_wait("挑战")
            return False
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        return True

    @TransitionOn("丰饶之间-一键完成")
    def _(self):
        if self.operationer.click_and_wait("超影免费", max_time=0.3, auto_raise=False):
            self.free_tryed = True
            return False
        self.free_tryed = True
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("丰饶之间-内部")
    def _(self):
        self.operationer.clicker.start()
        QThread.msleep(1000)
        return False

    @TransitionOn("副本结算-点击任意位置关闭界面")
    def _(self):
        self.logger.info("挑战[丰饶之间]成功")
        self.finished = True
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("点击任意位置关闭界面")
        return False

    @TransitionOn("未知场景")
    def _(self):
        self.operationer.clicker.stop()
        return False

    @TransitionOn("未注册场景")
    def _(self):
        self.operationer.clicker.stop()
        return False

