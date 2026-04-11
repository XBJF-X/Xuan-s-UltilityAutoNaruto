from datetime import timedelta, datetime,time

from utils.Base.Enums import KEY_INDEX
from utils.Base.Exceptions import TaskCompleted
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class GengDuoWanFa(BaseTask):
    source_scene = "更多玩法"
    task_max_duration = timedelta(hours=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checked = False
        self.finished = False
        
    def run(self):
        self.operationer.clicker.update_coordinates([
                    self.config.get_config("键位")[KEY_INDEX.BasicAttack],
                    self.config.get_config("键位")[KEY_INDEX.FirstSkill],
                    self.config.get_config("键位")[KEY_INDEX.SecondSkill],
                    self.config.get_config("键位")[KEY_INDEX.UltimateSkill],
                    self.config.get_config("键位")[KEY_INDEX.Substitution]
                ])
        super().run()

    @TransitionOn()
    def _(self):
        self.operationer.clicker.stop()
        self.bool_click=False
        if not self.checked:
            self.operationer.click_and_wait("任务")
            return False
        if not self.finished:
            if self.operationer.click_and_wait("大蛇丸试炼"):
                return False
            elif self.operationer.click_and_wait("绝迹战场"):
                return False
            if self.operationer.detect_element("集结团队战"):
                self.logger.warning("本周更多玩法为集结团队战，将推迟任务执行至下周")

        raise TaskCompleted("任务执行完成")
    @TransitionOn("绝迹战场")
    def _(self):
        self.operationer.clicker.stop()
        self.bool_click=False
        if not self.checked:
            self.operationer.click_and_wait("返回")
            return False
        if not self.finished:
            self.operationer.click_and_wait("开战")
            return False
        raise TaskCompleted("任务执行完成")
    @TransitionOn("大蛇丸试炼")
    def _(self):
        self.operationer.clicker.stop()
        self.bool_click=False
        if not self.checked:
            self.operationer.click_and_wait("返回")
            return False
        if not self.finished:
            self.operationer.click_and_wait("开战")
            return False
        raise TaskCompleted("任务执行完成")
    @TransitionOn("大蛇丸试炼-副本内")
    def _(self):
        self.checked = False
        self.bool_click = True
        self.operationer.clicker.start()
        self.operationer.next_scene = None
        return False

    @TransitionOn("绝迹战场-副本内")
    def _(self):
        self.checked = False
        self.bool_click = True
        self.operationer.clicker.start()
        self.operationer.next_scene = None
        return False

    @TransitionOn("更多玩法-任务")
    def _(self):
        self.operationer.clicker.stop()
        self.bool_click=False
        if not self.operationer.detect_element("未达成") and not self.finished:
            self.operationer.click_and_wait("2100")
            self.finished = True
            return False
        self.operationer.click_and_wait("X")
        self.checked = True
        return False

    @TransitionOn("更多玩法-匹配中")
    def _(self):
        self.bool_click = True
        self.operationer.clicker.stop()
        return False

    @TransitionOn("更多玩法-匹配成功")
    def _(self):
        self.bool_click = True
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("准备就绪")
        return False

    @TransitionOn("更多玩法-选择忍者")
    def _(self):
        self.bool_click = True
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
        self.bool_click = False
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("你的对手离开了游戏")
    def _(self):
        self.bool_click = False
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("决斗场-首页")
    def _(self):
        self.operationer.clicker.stop()
        self.bool_click=False
        self.operationer.click_and_wait("更多玩法")
        return False

    @TransitionOn("任务奖励-一键领取")
    def _(self):
        self.operationer.clicker.stop()
        self.bool_click=False
        self.operationer.click_and_wait("确定")
        self.finished = True
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
    
    def _get_execute_window(self,dt: datetime | None = None):
        if dt is None:
            dt=self.last_run_time
        today = dt.date()
        if dt.time() < time(5, 0):
            today -= timedelta(days=1)
        
        # 计算today所在的周一
        this_monday = today - timedelta(days=today.weekday())

        start_dt = datetime.combine(this_monday, time(5, 0), tzinfo=self.tz_info)
        dead_dt = datetime.combine(this_monday+timedelta(weeks=1), time(5, 0), tzinfo=self.tz_info)

        return [(start_dt, dead_dt)]
    
    def get_next_cycle_day(self, dt: datetime) -> datetime:
        return dt + timedelta(weeks=1)
    

    def reset_task_exe_prog(self) -> bool:
        self.checked = False
        self.finished = False
        return True