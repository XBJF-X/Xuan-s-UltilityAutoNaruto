from datetime import datetime, timedelta

from utils.Base.Enums import KEY_INDEX
from utils.Base.Task import MeiRiShengChang
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
                self.update_next_execute_time()
                return True
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
        if not self.finished:
            self.operationer.click_and_wait("开战")
            self.operationer.click_and_wait("开战")
            self.bool_click = True
            return False
        self.update_next_execute_time()
        return True

    def get_cycle_execute_time(self, dt: datetime) -> datetime:
        """返回 dt 所属周期的执行时间：当月最后一天 05:00:00"""
        if dt.month == 12:
            next_month = 1
            next_year = dt.year + 1
        else:
            next_month = dt.month + 1
            next_year = dt.year

        first_day_of_next_month = datetime(next_year, next_month, 1, tzinfo=dt.tzinfo)
        last_day_of_current_month = first_day_of_next_month - timedelta(days=1)
        return datetime(
            last_day_of_current_month.year,
            last_day_of_current_month.month,
            last_day_of_current_month.day,
            5,
            0,
            tzinfo=dt.tzinfo,
        )

    def get_next_cycle_execute_time(self, dt: datetime) -> datetime:
        """返回下一个周期的执行时间：下个月最后一天 05:00:00"""
        if dt.month == 12:
            next_year = dt.year + 1
            next_month = 1
        else:
            next_year = dt.year
            next_month = dt.month + 1

        first_day_next_month = dt.replace(
            year=next_year,
            month=next_month,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        if next_month == 12:
            first_day_after_next = first_day_next_month.replace(
                year=next_year + 1,
                month=1,
                day=1,
            )
        else:
            first_day_after_next = first_day_next_month.replace(
                month=next_month + 1,
                day=1,
            )

        last_day_next_month = first_day_after_next - timedelta(days=1)
        return datetime(
            last_day_next_month.year,
            last_day_next_month.month,
            last_day_next_month.day,
            5,
            0,
            tzinfo=dt.tzinfo,
        )

    def _handle_initialization(self, current_time: datetime) -> datetime:
        """处理任务初始化时的时间设置（case0）"""
        china_tz = current_time.tzinfo
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")
        next_execute_time = self.get_cycle_execute_time(current_time)

        if not next_exec_ts:
            return next_execute_time

        try:
            next_exec_dt = datetime.fromtimestamp(next_exec_ts, tz=china_tz)
        except Exception as e:
            self.logger.warning(f"解析下次执行时间戳失败: {next_exec_ts}, 错误: {e}")
            return next_execute_time

        # 保留原有逻辑：只要配置中有有效时间戳，初始化时直接沿用。
        return next_exec_dt

