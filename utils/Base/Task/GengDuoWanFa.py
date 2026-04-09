from datetime import timedelta, datetime

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

        self.update_next_execute_time()
        return True

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
        self.update_next_execute_time()
        return True

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
        self.update_next_execute_time()
        return True

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


    def reset_task_exe_prog(self) -> bool:
        self.checked = False
        self.finished = False
        return True