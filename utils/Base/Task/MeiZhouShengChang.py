from datetime import datetime, timedelta

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
        self.bool_click=False
        if not self.checked:
            self.operationer.click_and_wait("决斗任务")
            return False
        if not self.finished:
            self.operationer.click_and_wait("开战")
            self.operationer.click_and_wait("开战")
            self.bool_click=True
            return False
        self.operationer.click_and_wait("X")
        self.logger.info("结束执行")
        self.update_next_execute_time()
        return True

    @TransitionOn("忍术对战-决斗任务")
    def _(self):
        self.bool_click=False
        self.operationer.clicker.stop()
        if self.operationer.detect_element("满胜场"):
            self.logger.debug("每周胜场已满")
            self.checked = True
            self.finished = True
            for i in ["2", "5", "7", "10"]:
                self.operationer.click_and_wait(f"胜场{i}场",wait_time=0.5)
                self.operationer.click_and_wait(f"胜场{i}场",wait_time=0.5)
            self.logger.info("每周胜场奖励已领取")
            self.operationer.click_and_wait("X", click_times=2)
            self.update_next_execute_time()
            return True
        self.checked = True
        self.operationer.click_and_wait("X")
        return False

    def get_cycle_execute_time(self,dt: datetime) -> datetime:
        """返回 dt 所属执行周期的任务执行时间"""
        cycle_execute_time = (dt - timedelta(days=dt.weekday())).replace(
            hour=5,
            minute=0,
            second=0,
            microsecond=0,
        )
        if dt < cycle_execute_time:
            return cycle_execute_time - timedelta(weeks=1)
        return cycle_execute_time
    
    def _handle_initialization(self, current_time: datetime) -> datetime:
        china_tz = current_time.tzinfo
        # 读取配置中的时间
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")
        next_execute_time = self.get_cycle_execute_time(current_time)

        if not next_exec_ts:
            return next_execute_time

        try:
            next_exec_dt = datetime.fromtimestamp(next_exec_ts, tz=china_tz)
        except Exception as e:
            self.logger.warning(f"解析下次执行时间戳失败: {next_exec_ts}, 错误: {e}")
            return next_execute_time

        if next_exec_dt < current_time:
            return next_execute_time
        else:
            return next_exec_dt
    def get_next_cycle_execute_time(self, dt: datetime) -> datetime:
        """返回下一个周期的执行时间"""
        return self.get_cycle_execute_time(dt) + timedelta(weeks=1)
