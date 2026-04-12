import datetime
import time

from utils.Base.Enums import KEY_INDEX
from utils.Base.Task.BaseTask import BaseTask, TransitionOn

YS_list = [
    "火之要塞", "水之要塞", "土之要塞", "风之要塞", "雷之要塞", "汤之要塞", "田之要塞", "铁之要塞", "熊之要塞",
    "草之要塞", "雨之要塞", "海之要塞", "川之要塞", "泷之要塞", "云之要塞", "鸟之要塞", "涡之要塞", "霜之要塞"
]


# Todo：适配跨服要塞战部分
class YaoSaiZhengDuoZhan(BaseTask):
    source_scene = "主场景-组织"
    task_max_duration=datetime.timedelta(minutes=30)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fight_sum = 0
        self.joystick = self.config.get_config("键位")[KEY_INDEX.JoyStick]

    def run(self):
        self.operationer.clicker.update_coordinates([
            self.config.get_config("键位")[KEY_INDEX.BasicAttack],
            self.config.get_config("键位")[KEY_INDEX.FirstSkill],
            self.config.get_config("键位")[KEY_INDEX.SecondSkill],
            self.config.get_config("键位")[KEY_INDEX.UltimateSkill],
            self.config.get_config("键位")[KEY_INDEX.SecretScroll],
            self.config.get_config("键位")[KEY_INDEX.Summon],
            self.config.get_config("键位")[KEY_INDEX.Substitution]
        ])
        super().run()

    @TransitionOn()
    def _(self):
        self.operationer.click_and_wait("玩法")
        self.operationer.search_and_click([f"要塞争夺战-前往"], [{
            "swipe": {
                "start_coordinate": [1000, 464],
                "end_coordinate": [350, 464],
                "duration": 0.5
            }
        }],
        max_attempts=3,
        wait_time=5)
        return False

    # =========================本服要塞战部分==========================
    @TransitionOn("要塞战略图")
    def _(self):
        target = YS_list[self.config.get_task_exe_param(
            self.task_name, "[本服要塞战]目标要塞", 0)]
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
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("攻击")
        return False

    @TransitionOn("要塞内部")
    def _(self):
        self.operationer.clicker.stop()
        self.operationer.long_press(self.joystick[0] + 60, self.joystick[1], 1)
        self.logger.info(f"[本服要塞战]已战斗 {self.fight_sum} 次")
        return False

    @TransitionOn("决斗场-匹配中")
    def _(self):
        self.operationer.clicker.stop()
        return False

    @TransitionOn("决斗场-结算")
    def _(self):
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("决斗场-战斗中")
    def _(self):
        self.operationer.clicker.start()
        return False

    @TransitionOn("决斗场-单局结算")
    def _(self):
        self.fight_sum += 1
        self.operationer.clicker.stop()
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
        time.sleep(1)
        return False

    @TransitionOn("未注册场景")
    def _(self):
        self.operationer.clicker.stop()
        time.sleep(1)
        return False

    def _get_execute_window(self, dt: datetime.datetime | None = None):
        if dt is None:
            dt = self.last_run_time
        today = dt.date()
        if dt.time() < datetime.time(5, 0):
            today -= datetime.timedelta(days=1)

        # 计算today所在的周六
        this_saturday = today - datetime.timedelta(days=today.weekday() - 5)

        start_dt = datetime.datetime.combine(this_saturday,
                                             datetime.time(20, 0),
                                             tzinfo=self.tz_info)
        end_time = datetime.time(20, 30)
        if self.config.get_task_exe_param(self.task_name, "执行结束后是否有叛忍", False):
            running_time = self.config.get_task_exe_param(
                self.task_name, "本任务执行多少分钟后执行叛忍", 0)
            if running_time != 0:
                end_time = datetime.time(20, running_time)

        dead_dt = datetime.datetime.combine(this_saturday,
                                            end_time,
                                            tzinfo=self.tz_info)

        return [(start_dt, dead_dt)]

    def get_next_cycle_day(self, dt: datetime.datetime) -> datetime.datetime:
        return dt + datetime.timedelta(weeks=1)

    def _handle_execution_completed(self, current_time: datetime.datetime):
        if self.config.get_task_exe_param(self.task_name, "执行结束后是否有叛忍", True):
            self._activate_another_task("叛忍来袭")
        return self.get_cycle_execute_time(current_time, completed=True)

    def _handle_timeout_max_duration(self, current_time: datetime.datetime):
        return self._handle_execution_completed(current_time)
