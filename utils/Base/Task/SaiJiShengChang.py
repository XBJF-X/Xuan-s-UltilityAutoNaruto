from datetime import datetime, timedelta,time

from utils.Base.Enums import KEY_INDEX
from utils.Base.Task import MeiRiShengChang
from utils.Base.Exceptions import TaskCompleted
from utils.Base.Task.BaseTask import TransitionOn


class SaiJiShengChang(MeiRiShengChang):
    source_scene = "赛季任务"
    task_max_duration = None

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
        self.bool_click = False
        self.operationer.clicker.stop()
        if not self.checked:
            while self.operationer.click_and_wait(
                    "领取",
                    max_time=1
            ):
                continue
            if not self.operationer.detect_element(
                    "决斗场内获得N次胜利-已领",
                    wait_time=2,
                    max_time=1
            ):
                self.checked = True
                self.operationer.click_and_wait("X")
                return False
            else:
                self.checked = True
                self.finished = True
                self.operationer.clicker.stop()
                self.logger.warning("已打完所有赛季胜场")
                self.operationer.click_and_wait("X")
                raise TaskCompleted("任务执行完成")
        if not self.finished:
            self.operationer.click_and_wait("X")
            return False

    @TransitionOn("决斗场-首页")
    def _(self):
        self.bool_click = False
        self.operationer.clicker.stop()
        if self.checked:
            self.operationer.click_and_wait("忍术对战")
        else:
            self.operationer.click_and_wait("赛季任务")
        return False

    @TransitionOn("忍术对战")
    def _(self):
        self.bool_click = False
        self.operationer.clicker.stop()

        if not self.checked:
            self.operationer.click_and_wait("X")
            return False

        if not self.finished:
            self.operationer.click_and_wait("开战")
            self.operationer.click_and_wait("开战")
            self.bool_click = True
            return False
        raise TaskCompleted("任务执行完成")

    def _get_execute_window(self,dt: datetime | None = None):
        if dt is None:
            dt=self.last_run_time
        dt = self._ensure_tz_aware(dt)
        today = dt.date()
        if dt.time() < time(5, 0):
            today -= timedelta(days=1)
        
        # 计算start_dt为today所在月的倒数第二天的凌晨五点，dead_dt为today所在月的倒数第二天的两天后的凌晨五点
        next_month = today.replace(day=28) + timedelta(days=4)  # this will never fail
        last_day_of_month = next_month - timedelta(days=next_month.day)     
        second_last_day_of_month = last_day_of_month - timedelta(days=1)
        start_dt = datetime.combine(second_last_day_of_month, time(5, 0), tzinfo=self.tz_info)
        dead_dt = start_dt + timedelta(days=2)

        return [(start_dt, dead_dt)]
    
    def get_next_cycle_day(self, dt:datetime) -> datetime:
        return dt.replace(day=28) + timedelta(days=4)

