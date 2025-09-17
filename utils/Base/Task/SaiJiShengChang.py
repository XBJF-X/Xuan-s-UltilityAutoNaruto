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
                    max_time=0.3
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

    @property
    def next_execute_time(self):
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")

        # 辅助函数：获取指定月份的最后一天
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
            return last_day_of_current_month

        if next_exec_ts == 0:
            last_day = get_last_day_of_month(current_time)
            return datetime(
                last_day.year, last_day.month, last_day.day, 5, 0,
                tzinfo=china_tz
            )
        else:
            # 从时间戳转换为datetime对象
            return datetime.fromtimestamp(next_exec_ts, tz=china_tz)

    def update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        # 辅助函数：获取指定月份的最后一天
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
            return last_day_of_current_month

        match flag:
            case 0:  # 创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                next_execute_time = self.next_execute_time

            case 1:  # 正常执行完毕，更新为下次执行的时间
                # 计算当前时间的下个月
                if current_time.month == 12:
                    next_month = 1
                    next_year = current_time.year + 1
                else:
                    next_month = current_time.month + 1
                    next_year = current_time.year

                # 创建下个月1号的日期对象
                first_day_of_next_month = datetime(next_year, next_month, 1, tzinfo=china_tz)
                # 获取下个月的最后一天
                last_day_of_next_month = get_last_day_of_month(first_day_of_next_month)

                # 设置为下个月最后一天的5点
                next_execute_time = datetime(
                    last_day_of_next_month.year, last_day_of_next_month.month,
                    last_day_of_next_month.day, 5, 0, tzinfo=china_tz
                )

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                next_execute_time = datetime.now(china_tz)

            case 3:  # 把执行时间推迟delta时间，要求 delta!=None
                if delta is None:
                    self.logger.warning(f"update_next_execute_time传入的delta为空")
                    return False, None
                next_execute_time = current_time + delta

        self.logger.info(f"下次执行时间为：{next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
        self.config.set_task_base_config(self.task_name, "下次执行时间", int(next_execute_time.timestamp()))
        return True, next_execute_time
