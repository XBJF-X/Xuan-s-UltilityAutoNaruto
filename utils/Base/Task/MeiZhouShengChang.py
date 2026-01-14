from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Enums import KEY_INDEX
from utils.Base.Task import MeiRiShengChang
from utils.Base.Task.BaseTask import TransitionOn


class MeiZhouShengChang(MeiRiShengChang):
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
            self.operationer.click_and_wait("决斗任务")
            return False
        if not self.finished:
            self.operationer.click_and_wait("开战")
            self.operationer.click_and_wait("开战")
            return False
        self.operationer.click_and_wait("X")
        self.logger.info("结束执行")
        self.update_next_execute_time()
        return True

    @TransitionOn("忍术对战-决斗任务")
    def _(self):
        self.operationer.clicker.stop()
        if self.operationer.detect_element("满胜场", auto_raise=False):
            self.logger.debug("每周胜场已满")
            self.checked = True
            self.finished = True
            for i in ["2", "5", "7", "10"]:
                self.operationer.click_and_wait(f"胜场{i}场", click_times=3)
            self.logger.info("每周胜场奖励已领取")
            self.operationer.click_and_wait("X", click_times=2)
            self.update_next_execute_time()
            return True
        self.checked = True
        self.operationer.click_and_wait("X")
        return False

    def _handle_initialization(self, current_time: datetime) -> datetime:
        def get_this_monday_5am(current_time, tz):
            days_ahead = (0 - current_time.weekday()) % 7
            next_monday = current_time + timedelta(days=days_ahead)
            return next_monday.replace(hour=5, minute=0, second=0, microsecond=0, tzinfo=tz)

        china_tz = current_time.tzinfo
        # 读取配置中的时间
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")
        next_execute_time = get_this_monday_5am(current_time, china_tz)

        if next_exec_ts == 0:
            return next_execute_time
        else:
            # 转换为带时区的datetime
            stored_time = datetime.fromtimestamp(next_exec_ts, tz=china_tz)
            if stored_time + timedelta(weeks=1) < current_time:
                return next_execute_time
            else:
                return stored_time

    def _handle_execution_completed(self, current_time: datetime) -> datetime:
        def get_this_monday_5am(current_time, tz):
            days_ahead = (0 - current_time.weekday()) % 7
            next_monday = current_time + timedelta(days=days_ahead)
            return next_monday.replace(hour=5, minute=0, second=0, microsecond=0, tzinfo=tz)

        china_tz = current_time.tzinfo

        next_execute_time = get_this_monday_5am(current_time, china_tz) + timedelta(weeks=1)
        return next_execute_time
