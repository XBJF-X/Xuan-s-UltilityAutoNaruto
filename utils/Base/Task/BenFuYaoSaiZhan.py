from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from PySide6.QtCore import QThread

from utils.Base.Enums import KEY_INDEX
from utils.Base.Exceptions import StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class BenFuYaoSaiZhan(BaseTask):
    source_scene = "要塞战略图"
    task_max_duration = timedelta(minutes=30)

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
        self.operationer.click_and_wait("火之要塞")
        return False

    @TransitionOn("X之要塞")
    def _(self):
        self.operationer.click_and_wait("攻击")
        return False

    @TransitionOn("要塞内部")
    def _(self):
        if not datetime.now(tz=ZoneInfo("Asia/Shanghai")) < self.dead_line:
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

    def update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        def get_next_saturday_8pm(current_time, tz):
            current_weekday = current_time.weekday()
            days_ahead = (5 - current_weekday) % 7
            if days_ahead == 0 and current_time.hour >= 20:
                days_ahead = 7
            next_time = current_time + timedelta(days=days_ahead)
            return next_time.replace(hour=20, minute=0, second=0, microsecond=0, tzinfo=tz)

        def is_in_skip_period(target_time, base_date, interval_weeks):
            delta_weeks = (target_time - base_date).days // 7
            return delta_weeks >= 0 and delta_weeks % interval_weeks == 0

        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)
        base_date = datetime(2025, 9, 20, tzinfo=china_tz)

        match flag:
            case 0:
                next_exec_ts = self.data.get('下次执行时间')
                if next_exec_ts == 0 or next_exec_ts is None:
                    self.next_execute_time = get_next_saturday_8pm(current_time, china_tz)
                else:
                    self.next_execute_time = datetime.fromtimestamp(next_exec_ts, tz=china_tz)

            case 1:
                next_time = get_next_saturday_8pm(current_time, china_tz)
                while is_in_skip_period(next_time, base_date, 4):
                    next_time += timedelta(weeks=1)
                self.next_execute_time = next_time

            case 2:
                self.next_execute_time = get_next_saturday_8pm(current_time, china_tz)

            case 3:
                if delta is None:
                    self.logger.warning(f"update_next_execute_time传入的delta为空")
                    return False, None
                self.next_execute_time = current_time + delta

            case _:
                self.logger.warning(f"请检查update_next_execute_time传入的参数：flag={flag},delta={delta}")
                return False, None

        self.logger.info(f"下次执行时间为：{self.next_execute_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.config.set_task_config(self.task_name, "下次执行时间", int(self.next_execute_time.timestamp()))
        return True, self.next_execute_time
