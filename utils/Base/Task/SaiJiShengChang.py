from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

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
        self.operationer.clicker.stop()
        if not self.checked:
            while self.operationer.click_and_wait(
                    "领取",
                    auto_raise=False,
                    max_time=1
            ):
                continue
            if not self.operationer.detect_element(
                    "决斗场内获得N次胜利-已领",
                    wait_time=2,
                    max_time=1,
                    auto_raise=False
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
        self.operationer.clicker.stop()
        if self.checked:
            self.operationer.click_and_wait("忍术对战")
        else:
            self.operationer.click_and_wait("赛季任务")
        return False

    @TransitionOn("忍术对战")
    def _(self):
        self.operationer.clicker.stop()
        if not self.finished:
            self.operationer.click_and_wait("开战")
            self.operationer.click_and_wait("开战")
            return False
        self.update_next_execute_time()
        return True

    def _handle_initialization(self, current_time: datetime) -> datetime:
        def get_last_day_of_month(dt: datetime) -> datetime:
            # 如果是12月，下个月是1月，年份加1
            if dt.month == 12:
                next_month = 1
                next_year = dt.year + 1
            else:
                next_month = dt.month + 1
                next_year = dt.year
            # 下个月第一天减去一天就是当月最后一天
            first_day_of_next_month = datetime(next_year, next_month, 1, tzinfo=dt.tzinfo)
            last_day_of_current_month = first_day_of_next_month - timedelta(days=1)
            return datetime(
                last_day_of_current_month.year, last_day_of_current_month.month,
                last_day_of_current_month.day, 5, 0, tzinfo=dt.tzinfo
            )

        china_tz = current_time.tzinfo
        # 读取配置中的时间
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")
        next_execute_time = get_last_day_of_month(current_time)

        if next_exec_ts == 0:
            return next_execute_time
        else:
            # 转换为带时区的datetime
            stored_time = datetime.fromtimestamp(next_exec_ts, tz=china_tz)
            if stored_time + timedelta(days=1) < current_time:
                return next_execute_time
            else:
                return stored_time

    def _handle_execution_completed(self, current_time: datetime) -> datetime:
        def get_last_day_of_next_month(dt: datetime) -> datetime:
            """得到下个月的最后一天，保留原有时区信息"""
            # 计算下个月的年份和月份
            if dt.month == 12:
                next_year = dt.year + 1
                next_month = 1
            else:
                next_year = dt.year
                next_month = dt.month + 1

            # 构造下个月的第一天
            first_day_next_month = dt.replace(
                year=next_year,
                month=next_month,
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

            # 计算下下个月的第一天
            if next_month == 12:
                first_day_after_next = first_day_next_month.replace(
                    year=next_year + 1,
                    month=1,
                    day=1
                )
            else:
                first_day_after_next = first_day_next_month.replace(
                    month=next_month + 1,
                    day=1
                )

            # 下下个月的第一天减去1天，即为下个月的最后一天
            last_day_next_month = first_day_after_next - timedelta(days=1)
            return datetime(
                last_day_next_month.year, last_day_next_month.month,
                last_day_next_month.day, 5, 0, tzinfo=dt.tzinfo
            )

        # 计算并返回下个月的最后一天
        next_execute_time = get_last_day_of_next_month(current_time)
        return next_execute_time
