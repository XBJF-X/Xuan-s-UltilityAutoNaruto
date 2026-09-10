import datetime
import time
from datetime import timedelta

from backend.core.legacy.Enums import KEY_INDEX
from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn
from backend.core.legacy.Task.schedule import Custom, Weekday, WeeklySlot

PARAM_HAS_PANREN = "执行结束后是否有叛忍"
PARAM_PANREN_MINUTE = "本任务执行多少分钟后执行叛忍"


def _wednesday_slot(base, ctx):
    """每周三 21:00 起的窗口；开启"执行结束后有叛忍"时终点改为 21:{N}（默认 21:30）。"""
    minute = 30
    if ctx is not None and ctx.param("巅峰对决", PARAM_HAS_PANREN, False):
        running = ctx.param("巅峰对决", PARAM_PANREN_MINUTE, 0)
        if running:
            minute = running
    slot = WeeklySlot(Weekday.WED, datetime.time(21, 0), datetime.time(21, minute))
    return slot.windows(base)


# Todo：修复天地战场第二次上人时选人失误的问题
class DianFengDuiJue(BaseTask):
    source_scene = "巅峰对决"
    task_max_duration = timedelta(minutes=15)
    # 每周三 21:00 起的固定时段；窗口终点受"叛忍"联动参数影响
    schedule = Custom(_wednesday_slot,
                      cycle=lambda base: base + timedelta(weeks=1),
                      describe_text="每周三 21:00 起（终点受叛忍参数影响）")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.guwu_done = False
        self.fighted = False
        self.last_check_reward_time = time.perf_counter()
        self.choose = self.config.get_task_exe_param(self.task_name, "选择战场", 0)

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
        self.bool_click = False
        self.operationer.click_and_wait(choose_dic[self.choose])
        return False

    @TransitionOn("天之战场")
    def _(self):
        self.bool_click = False
        if not self.guwu_done:
            self.operationer.click_and_wait("组织鼓舞")
            self.guwu_done = True
            return False
        if self.operationer.detect_element("战场已提前结束"):
            self.logger.info("战场已提前结束，停止执行")
            raise TaskCompleted("战场已提前结束")
        self.operationer.click_and_wait("空闲柱子")
        if time.perf_counter() - self.last_check_reward_time > 10:
            self.operationer.click_and_wait("战场奖励")
            self.last_check_reward_time = time.perf_counter()
        return False

    @TransitionOn("地之战场")
    def _(self):
        self.bool_click = False
        if not self.guwu_done:
            self.operationer.click_and_wait("组织鼓舞")
            self.guwu_done = True
            return False
        if self.operationer.detect_element("战场已提前结束"):
            self.logger.info("战场已提前结束，停止执行")
            raise TaskCompleted("战场已提前结束")
        self.operationer.click_and_wait("空闲柱子", max_time=10)
        if time.perf_counter() - self.last_check_reward_time > 10:
            self.operationer.click_and_wait("战场奖励")
            self.last_check_reward_time = time.perf_counter()
        return False

    @TransitionOn("天地战场-确定进入")
    def _(self):
        self.bool_click = False
        self.operationer.click_and_wait("确认")
        return False

    @TransitionOn("天地战场-配置阵容")
    def _(self):
        self.bool_click = False
        defeated_ninja_num = max(
            self.config.get_task_exe_prog(self.task_name, "已战败角色数", 0), 2) + 1
        self.operationer.click_and_wait("忍者页",
                                        wait_time=0.2,
                                        stable_duration=0)
        if defeated_ninja_num >= 4:
            self.config.set_task_exe_prog(self.task_name, "已战败角色数", 0)
        else:
            if not self.operationer.detect_element(
                    f"默认点位-{defeated_ninja_num}-选中"):
                self.operationer.click_and_wait(f"默认点位-{defeated_ninja_num}",
                                                wait_time=0.2,
                                                stable_duration=0)
                self.config.set_task_exe_prog(self.task_name, "已战败角色数",
                                              defeated_ninja_num)
        if not self.fighted:
            self.operationer.click_and_wait("通灵兽页",
                                            wait_time=0.2,
                                            stable_duration=0)
            for i in range(1, 4):
                if not self.operationer.detect_element(f"默认点位-{i}-选中"):
                    self.operationer.click_and_wait(f"默认点位-{i}",
                                                    wait_time=0.2,
                                                    stable_duration=0)

            self.operationer.click_and_wait("秘卷页",
                                            wait_time=0.2,
                                            stable_duration=0)
            if not self.operationer.detect_element("默认点位-1-选中"):
                self.operationer.click_and_wait("默认点位-1",
                                                wait_time=0.2,
                                                stable_duration=0)

        self.operationer.click_and_wait("确认", stable_wait_for_new_scene=True)
        return False

    @TransitionOn("天地战场-战场奖励")
    def _(self):
        self.bool_click = False
        while self.operationer.click_and_wait("领取"):
            continue
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("天地战场-战场战斗已经结束")
    def _(self):
        self.bool_click = False
        self.operationer.click_and_wait("确认")
        raise TaskCompleted("天地战场战斗结束")

    @TransitionOn("天地战场-确认退出")
    def _(self):
        self.bool_click = False
        self.operationer.click_and_wait("确认")
        raise TaskCompleted("天地战场确认退出")

    @TransitionOn("恭喜你获得")
    def _(self):
        self.bool_click = False
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("决斗场-结算")
    def _(self):
        self.bool_click = False
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("X")
        self.fighted = True
        return False

    @TransitionOn("决斗场-单局结算")
    def _(self):
        self.bool_click = False
        self.operationer.clicker.stop()
        self.fighted = True
        return False

    @TransitionOn("决斗场-战斗中")
    def _(self):
        self.bool_click = True
        self.operationer.clicker.start()
        self.fighted = True
        return False

    @TransitionOn("你的对手离开了游戏")
    def _(self):
        self.bool_click = False
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("未知场景")
    def _(self):
        self.operationer.clicker.stop()
        time.sleep(1)
        return False
    
    def on_complete(self, current_time: datetime.datetime):
        if self.config.get_task_exe_param(self.task_name, "执行结束后是否有叛忍", True):
            self._activate_another_task("叛忍来袭")
        return self.get_cycle_execute_time(current_time, completed=True)

    def on_timeout(self, current_time: datetime.datetime):
        return self.on_complete(current_time)

    def reset_task_exe_prog(self) -> bool:
        self.config.set_task_exe_prog(self.task_name, "已战败角色数", 0)
        self.guwu_done = False
        self.fighted = False
        self.last_check_reward_time = time.perf_counter()
        return True
