import datetime
import time
from datetime import timedelta

from utils.Base.Enums import KEY_INDEX
from utils.Base.Exceptions import TaskCompleted
from utils.Base.Task.BaseTask import BaseTask, TransitionOn, debug_execute_window

choose_dic = ["天之战场", "地之战场"]


# Todo：修复天地战场第二次上人时选人失误的问题
class TianDiZhanChang(BaseTask):
    source_scene = "天地战场"
    task_max_duration = timedelta(minutes=30)

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
    
    @debug_execute_window
    def _get_execute_window(self,
                            dt: datetime.datetime | None = None):
        if dt is None:
            dt = self.last_run_time
        dt = self._ensure_tz_aware(dt)
        today = dt.date()
        if dt.time() < datetime.time(5, 0):
            today -= timedelta(days=1)

        # 计算today所在的周三
        this_wednesday = today - timedelta(days=today.weekday() - 2)

        start_dt = datetime.datetime.combine(this_wednesday,
                                             datetime.time(21, 0),
                                             tzinfo=self.tz_info)
        end_time = datetime.time(21, 30)
        if self.config.get_task_exe_param(self.task_name, "执行结束后是否有叛忍", False):
            running_time = self.config.get_task_exe_param(
                self.task_name, "本任务执行多少分钟后执行叛忍", 0)
            if running_time != 0:
                end_time = datetime.time(21, running_time)

        dead_dt = datetime.datetime.combine(this_wednesday,
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

    def reset_task_exe_prog(self) -> bool:
        self.config.set_task_exe_prog(self.task_name, "已战败角色数", 0)
        self.guwu_done = False
        self.fighted = False
        self.last_check_reward_time = time.perf_counter()
        return True
