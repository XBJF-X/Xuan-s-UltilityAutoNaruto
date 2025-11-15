from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from PySide6.QtCore import QThread

from utils.Base.Enums import KEY_INDEX
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class GengDuoWanFa(BaseTask):
    source_scene = "更多玩法"
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
            self.config.get_config("键位")[KEY_INDEX.Substitution]
        ])

    @TransitionOn()
    def _(self):
        self.operationer.clicker.stop()
        if not self.checked:
            self.operationer.click_and_wait("任务")
            return False
        if not self.finished:
            self.operationer.click_and_wait("入口")
            return False
        self.update_next_execute_time()
        return True

    @TransitionOn("绝迹战场")
    def _(self):
        self.operationer.clicker.stop()
        if not self.checked:
            self.operationer.click_and_wait("返回")
            return False
        if not self.finished:
            self.operationer.click_and_wait("开战")
            return False
        self.update_next_execute_time()
        return True

    @TransitionOn("大蛇丸试炼")
    def _(self):
        self.operationer.clicker.stop()
        if not self.checked:
            self.operationer.click_and_wait("返回")
            return False
        if not self.finished:
            self.operationer.click_and_wait("开战")
            return False
        self.update_next_execute_time()
        return True

    @TransitionOn("大蛇丸试炼-副本内")
    def _(self):
        self.checked = False
        self.operationer.clicker.start()
        self.operationer.next_scene = None
        return False

    @TransitionOn("绝迹战场-副本内")
    def _(self):
        self.checked = False
        self.operationer.clicker.start()
        self.operationer.next_scene = None
        return False

    @TransitionOn("更多玩法-任务")
    def _(self):
        self.operationer.clicker.stop()
        if not self.operationer.detect_element("未达成", auto_raise=False):
            self.finished = True
            self.update_next_execute_time()
            return True
        self.operationer.click_and_wait("X")
        self.checked = True
        return False

    @TransitionOn("更多玩法-匹配中")
    def _(self):
        self.operationer.clicker.stop()
        return False

    @TransitionOn("更多玩法-匹配成功")
    def _(self):
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("准备就绪")
        return False

    @TransitionOn("更多玩法-选择忍者")
    def _(self):
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("默认忍者-1", wait_time=0)
        self.operationer.click_and_wait("确定", wait_time=0)
        self.operationer.click_and_wait("默认忍者-2", wait_time=0)
        self.operationer.click_and_wait("确定", wait_time=0)
        self.operationer.click_and_wait("默认忍者-3", wait_time=0)
        self.operationer.click_and_wait("确定", wait_time=0)
        self.operationer.click_and_wait("确定", wait_time=0)
        return False

    @TransitionOn("更多玩法-结算")
    def _(self):
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("你的对手离开了游戏")
    def _(self):
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("决斗场-首页")
    def _(self):
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("更多玩法")
        return False

    @TransitionOn("未知场景")
    def _(self):
        self.operationer.clicker.stop()
        return False

    @TransitionOn("未注册场景")
    def _(self):
        self.operationer.clicker.stop()
        self.operationer.next_scene = "更多玩法"
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
