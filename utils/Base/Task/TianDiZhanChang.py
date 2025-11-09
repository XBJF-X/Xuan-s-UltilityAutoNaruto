from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

from PySide6.QtCore import QThread

from utils.Base.Enums import KEY_INDEX
from utils.Base.Exceptions import EndEarly, StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn, handle_task_exceptions

choose_dic = ["天之战场", "地之战场"]


class TianDiZhanChang(BaseTask):
    source_scene = "天地战场"
    dead_line = time(21, 30)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.guwu_done = False
        self.pillar_took = False
        self.choose = self.config.get_task_exe_param(self.task_name, "选择战场", 0)
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
        self.operationer.click_and_wait(choose_dic[self.choose])
        return False

    @TransitionOn("天之战场")
    def _(self):
        current_time = datetime.now(tz=ZoneInfo("Asia/Shanghai"))
        if current_time > current_time.replace(hour=21, minute=30, second=0, microsecond=0):
            self.logger.info("天地战场时间已过，停止执行")
            self.update_next_execute_time()
            return True
        if not self.guwu_done:
            self.operationer.click_and_wait("组织鼓舞")
            self.guwu_done = True
            return False
        if not self.pillar_took:
            if self.operationer.click_and_wait("空闲柱子", max_time=20, auto_raise=False):
                self.pillar_took = True
        else:
            QThread.sleep(20)
        self.operationer.click_and_wait("战场奖励")
        return False

    @TransitionOn("地之战场")
    def _(self):
        current_time = datetime.now(tz=ZoneInfo("Asia/Shanghai"))
        if current_time > current_time.replace(hour=21, minute=30, second=0, microsecond=0):
            self.logger.info("天地战场时间已过，停止执行")
            self.update_next_execute_time()
            return True
        if not self.guwu_done:
            self.operationer.click_and_wait("组织鼓舞")
            self.guwu_done = True
            return False
        if not self.pillar_took:
            if self.operationer.click_and_wait("空闲柱子", max_time=20, auto_raise=False):
                self.pillar_took = True
        else:
            QThread.sleep(20)
        self.operationer.click_and_wait("战场奖励")
        return False

    @TransitionOn("天地战场-确定进入")
    def _(self):
        self.operationer.click_and_wait("确认")
        return False

    @TransitionOn("天地战场-确定进入")
    def _(self):
        self.operationer.click_and_wait("确认")
        return False

    @TransitionOn("天地战场-配置阵容")
    def _(self):
        defeated_ninja_num = max(self.config.get_task_exe_prog(self.task_name, "已战败角色数", 0), 2) + 1
        self.operationer.click_and_wait("忍者页")
        if not self.operationer.detect_element(f"默认点位-{defeated_ninja_num}-选中"):
            self.operationer.click_and_wait(f"默认点位-{defeated_ninja_num}", stable_max_time=0.5)
            self.config.set_task_exe_prog(self.task_name, "已战败角色数", defeated_ninja_num)

        self.operationer.click_and_wait("通灵兽页", stable_max_time=0.5)
        for i in range(1, 4):
            if not self.operationer.detect_element(f"默认点位-{i}-选中"):
                self.operationer.click_and_wait(f"默认点位-{i}", stable_max_time=0.5)

        self.operationer.click_and_wait("秘卷页", stable_max_time=0.5)
        if not self.operationer.detect_element("默认点位-1-选中"):
            self.operationer.click_and_wait("默认点位-1", stable_max_time=0.5)

        self.operationer.click_and_wait("确认", stable_max_time=0.5)
        return False

    @TransitionOn("天地战场-战场奖励")
    def _(self):
        while self.operationer.click_and_wait("领取", auto_raise=False):
            continue
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("天地战场-战场战斗已经结束")
    def _(self):
        self.operationer.click_and_wait("确认")
        self.update_next_execute_time()
        return True

    @TransitionOn("天地战场-确认退出")
    def _(self):
        self.operationer.click_and_wait("确认")
        return False

    @TransitionOn("恭喜你获得")
    def _(self):
        self.operationer.click_and_wait("")
        return False

    @TransitionOn("决斗场-结算")
    def _(self):
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("X")
        self.pillar_took = False
        return False

    @TransitionOn("决斗场-单局结算")
    def _(self):
        self.operationer.clicker.stop()
        self.pillar_took = False
        return False

    @TransitionOn("决斗场-战斗中")
    def _(self):
        self.operationer.clicker.start()
        self.pillar_took = False
        QThread.msleep(500)
        return False

    @TransitionOn("你的对手离开了游戏")
    def _(self):
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("未知场景")
    def _(self):
        self.operationer.clicker.stop()
        QThread.msleep(1000)
        return False

    def _handle_initialization(self, current_time: datetime) -> datetime:
        def get_this_wednesday_9pm(current_time, tz):
            days_ahead = (2 - current_time.weekday()) % 7
            next_time = current_time + timedelta(days=days_ahead)
            return next_time.replace(hour=21, minute=0, second=0, microsecond=0, tzinfo=tz)

        china_tz = current_time.tzinfo
        # 读取配置中的时间
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")

        # 本周周六下午8点的时间对象
        next_execute_time = get_this_wednesday_9pm(current_time, china_tz)

        if next_exec_ts == 0:
            return next_execute_time
        else:
            # 转换为带时区的datetime
            stored_time = datetime.fromtimestamp(next_exec_ts, tz=china_tz)
            if stored_time + timedelta(minutes=30) < current_time:
                return next_execute_time
            else:
                return stored_time

    def _handle_execution_completed(self, current_time: datetime) -> datetime:
        def get_this_wednesday_9pm(current_time, tz):
            days_ahead = (2 - current_time.weekday()) % 7
            next_time = current_time + timedelta(days=days_ahead)
            return next_time.replace(hour=21, minute=0, second=0, microsecond=0, tzinfo=tz)

        china_tz = current_time.tzinfo

        # 下周周六下午8点的时间对象
        next_execute_time = get_this_wednesday_9pm(current_time, china_tz) + timedelta(weeks=1)

        return next_execute_time

    def reset_prog_parmas(self) -> bool:
        self.config.set_task_exe_prog(self.task_name, "已战败角色数", 0)
        return True
