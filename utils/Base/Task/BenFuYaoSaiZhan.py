from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

from PySide6.QtCore import QThread

from utils.Base.Enums import KEY_INDEX
from utils.Base.Exceptions import StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn, handle_task_exceptions

YS_list = [
    "火之要塞",
    "水之要塞",
    "土之要塞",
    "风之要塞",
    "雷之要塞",
    "汤之要塞",
    "田之要塞",
    "铁之要塞",
    "熊之要塞",
    "草之要塞",
    "雨之要塞",
    "海之要塞",
    "川之要塞",
    "泷之要塞",
    "云之要塞",
    "鸟之要塞",
    "涡之要塞",
    "霜之要塞"
]


class BenFuYaoSaiZhan(BaseTask):
    source_scene = "要塞战略图"
    dead_line = time(20, 30)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fight_sum = 0
        self.joystick = self.config.get_config("键位")[KEY_INDEX.JoyStick]
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
        target = YS_list[self.config.get_task_exe_param(self.task_name, "目标要塞", 0)]
        move = None
        match target:
            case "田之要塞" | "铁之要塞" | "熊之要塞":
                move = [(100, 100), (1400, 800)]
            case "汤之要塞" | "涡之要塞" | "霜之要塞":
                move = [(1400, 100), (100, 800)]
            case "海之要塞" | "草之要塞" | "雨之要塞" | "川之要塞":
                move = [(100, 800), (1400, 100)]
            case "泷之要塞" | "云之要塞" | "鸟之要塞":
                move = [(1400, 800), (100, 100)]
        if move:
            self.operationer.swipe_and_wait(move[0], move[1], duration=0.4)
        self.operationer.click_and_wait(target)
        return False

    @TransitionOn("X之要塞")
    def _(self):
        self.operationer.click_and_wait("攻击")
        return False

    @TransitionOn("要塞内部")
    def _(self):
        if datetime.now(tz=ZoneInfo("Asia/Shanghai")) < self.running_deadline:
            self.operationer.long_press(self.joystick[0] + 60, self.joystick[1], 3)
            return False
        self.logger.info(f"本服要塞战结束，共战斗 {self.fight_sum} 次")
        self.update_next_execute_time()
        return True

    @TransitionOn("决斗场-匹配中")
    def _(self):
        QThread.msleep(1000)
        return False

    @TransitionOn("决斗场-结算")
    def _(self):
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("决斗场-战斗中")
    def _(self):
        self.operationer.clicker.start()
        QThread.msleep(1000)
        return False

    @TransitionOn("决斗场-单局结算")
    def _(self):
        self.fight_sum += 1
        self.operationer.clicker.stop()
        QThread.msleep(5000)
        return False

    @TransitionOn("你的对手离开了游戏")
    def _(self):
        self.fight_sum += 1
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

    def _handle_initialization(self, current_time: datetime) -> datetime:
        def is_in_skip_period(target_time, interval_weeks):
            base_date = datetime(2025, 9, 20, tzinfo=china_tz)
            delta_weeks = (target_time - base_date).days // 7
            return delta_weeks >= 0 and delta_weeks % interval_weeks == 0

        def get_this_saturday_8pm(current_time, tz):
            days_ahead = (5 - current_time.weekday()) % 7
            next_time = current_time + timedelta(days=days_ahead)
            return next_time.replace(hour=20, minute=0, second=15, microsecond=0, tzinfo=tz)

        china_tz = current_time.tzinfo

        # 本周周六下午8点的时间对象
        next_execute_time = get_this_saturday_8pm(current_time, china_tz)

        while is_in_skip_period(next_execute_time, 5):
            next_execute_time += timedelta(weeks=1)

        if current_time > next_execute_time + timedelta(minutes=30):
            next_execute_time += timedelta(days=7)
            while is_in_skip_period(next_execute_time, 5):
                next_execute_time += timedelta(weeks=1)

        return next_execute_time

    def _handle_execution_completed(self, current_time: datetime) -> datetime:
        def is_in_skip_period(target_time, interval_weeks):
            base_date = datetime(2025, 9, 20, tzinfo=china_tz)
            delta_weeks = (target_time - base_date).days // 7
            return delta_weeks >= 0 and delta_weeks % interval_weeks == 0

        def get_this_saturday_8pm(current_time, tz):
            days_ahead = (5 - current_time.weekday()) % 7
            next_time = current_time + timedelta(days=days_ahead)
            return next_time.replace(hour=20, minute=0, second=15, microsecond=0, tzinfo=tz)

        china_tz = current_time.tzinfo

        # 下周周六下午8点的时间对象
        next_execute_time = get_this_saturday_8pm(current_time, china_tz) + timedelta(weeks=1)

        while is_in_skip_period(next_execute_time, 5):
            next_execute_time += timedelta(weeks=1)

        return next_execute_time
