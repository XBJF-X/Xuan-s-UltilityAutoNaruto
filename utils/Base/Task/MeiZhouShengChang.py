from datetime import datetime, timedelta, time

from utils.Base.Enums import KEY_INDEX
from utils.Base.Task import MeiRiShengChang
from utils.Base.Exceptions import TaskCompleted
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
        self.bool_click = False
        if not self.checked:
            self.operationer.click_and_wait("决斗任务")
            return False
        if not self.finished:
            self.operationer.click_and_wait("开战")
            self.operationer.click_and_wait("开战")
            self.bool_click = True
            return False
        self.operationer.click_and_wait("X")
        self.logger.info("结束执行")
        raise TaskCompleted("任务执行完成")

    @TransitionOn("忍术对战-决斗任务")
    def _(self):
        self.bool_click = False
        self.operationer.clicker.stop()
        if self.operationer.detect_element("满胜场"):
            self.logger.debug("每周胜场已满")
            self.checked = True
            self.finished = True
            for i in ["2", "5", "7", "10"]:
                self.operationer.click_and_wait(f"胜场{i}场", wait_time=0.5)
                self.operationer.click_and_wait(f"胜场{i}场", wait_time=0.5)
            self.logger.info("每周胜场奖励已领取")
            self.operationer.click_and_wait("X", click_times=2)
            raise TaskCompleted("任务执行完成")
        self.checked = True
        self.operationer.click_and_wait("X")
        return False

    def _get_execute_window(self, dt: datetime | None = None):
        if dt is None:
            dt = self.last_run_time
        today = dt.date()
        if dt.time() < time(5, 0):
            today -= timedelta(days=1)

        # 计算today所在的周一
        this_monday = today - timedelta(days=today.weekday())

        start_dt = datetime.combine(this_monday, time(5, 0), tzinfo=self.tz_info)
        dead_dt = datetime.combine(this_monday + timedelta(weeks=1),
                                   time(5, 0),
                                   tzinfo=self.tz_info)

        return [(start_dt, dead_dt)]

    def get_next_cycle_day(self, dt: datetime) -> datetime:
        return dt + timedelta(weeks=1)

    def reset_task_exe_prog(self) -> bool:
        self.checked = False
        self.finished = False
        return True
