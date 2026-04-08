import datetime
import time
from datetime import timedelta
from zoneinfo import ZoneInfo

from utils.Base.Enums import KEY_INDEX
from utils.Base.Task.BaseTask import BaseTask, TransitionOn

choose_dic = ["天之战场", "地之战场"]


# Todo：修复天地战场第二次上人时选人失误的问题
class TianDiZhanChang(BaseTask):
    source_scene = "天地战场"
    dead_line = datetime.time(21, 30)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.guwu_done = False
        self.fighted = False
        self.last_check_reward_time = time.perf_counter()
        self.choose = self.config.get_task_exe_param(self.task_name, "选择战场", 0)
        self.operationer.clicker.update_coordinates([
            self.config.get_config("键位")[KEY_INDEX.BasicAttack],
            self.config.get_config("键位")[KEY_INDEX.FirstSkill],
            self.config.get_config("键位")[KEY_INDEX.SecondSkill],
            self.config.get_config("键位")[KEY_INDEX.UltimateSkill],
            self.config.get_config("键位")[KEY_INDEX.SecretScroll],
            self.config.get_config("键位")[KEY_INDEX.Summon],
            self.config.get_config("键位")[KEY_INDEX.Substitution]
        ])
        stop_time = self.config.get_task_exe_param(self.task_name, "本任务执行多少分钟后执行叛忍", 0)
        if stop_time:
            self.dead_line = datetime.time(21, stop_time)

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
            self.update_next_execute_time()
            return True
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
            self.update_next_execute_time()
            return True
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
        defeated_ninja_num = max(self.config.get_task_exe_prog(self.task_name, "已战败角色数", 0), 2) + 1
        self.operationer.click_and_wait("忍者页", wait_time=0.2, stable_duration=0)
        if defeated_ninja_num >= 4:
            self.config.set_task_exe_prog(self.task_name, "已战败角色数", 0)
        else:
            if not self.operationer.detect_element(f"默认点位-{defeated_ninja_num}-选中"):
                self.operationer.click_and_wait(f"默认点位-{defeated_ninja_num}", wait_time=0.2, stable_duration=0)
                self.config.set_task_exe_prog(self.task_name, "已战败角色数", defeated_ninja_num)
        if not self.fighted:
            self.operationer.click_and_wait("通灵兽页", wait_time=0.2, stable_duration=0)
            for i in range(1, 4):
                if not self.operationer.detect_element(f"默认点位-{i}-选中"):
                    self.operationer.click_and_wait(f"默认点位-{i}", wait_time=0.2, stable_duration=0)

            self.operationer.click_and_wait("秘卷页", wait_time=0.2, stable_duration=0)
            if not self.operationer.detect_element("默认点位-1-选中"):
                self.operationer.click_and_wait("默认点位-1", wait_time=0.2, stable_duration=0)

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
        self.update_next_execute_time()
        return True

    @TransitionOn("天地战场-确认退出")
    def _(self):
        self.bool_click = False
        self.operationer.click_and_wait("确认")
        self.update_next_execute_time()
        return True

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

    def _cleanup_on_timeout(self):
        """超时时的清理"""
        self.operationer.clicker.stop()
        self.update_next_execute_time()
        self.reset_task_exe_prog()

    def update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        """
        用于更新本任务的下次执行时间

        Args:
            flag: 更新下次执行时间的模式
                0：创建任务时初始化时间
                1：正常执行完毕，更新为下次执行时间
                3：把执行时间推迟delta时间，要求 delta!=None
            delta: 延迟的时长（仅flag=3时有效）
        Returns:
            tuple: (是否成功, 下次执行时间datetime对象)
        """
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.datetime.now(china_tz)

        try:
            match flag:
                case 0 | 2:
                    next_execute_time = self._handle_initialization(current_time)
                case 1:
                    next_execute_time = self._handle_execution_completed(current_time)
                case 3:
                    next_execute_time = self._handle_delay(current_time, delta)
                case _:
                    self.logger.warning(f"不支持的更新模式: {flag}")
                    return False, None

            if next_execute_time is None:
                return False, None

            self.logger.info(f"下次执行时间为：{next_execute_time.strftime('%Y-%m-%d %H:%M:%S')}")
            self.config.set_task_base_config(
                self.task_name,
                "下次执行时间",
                int(next_execute_time.timestamp())
            )
            return True, next_execute_time

        except Exception as e:
            self.logger.error(f"更新下次执行时间失败: {str(e)}")
            return False, None

    def get_cycle_execute_time(self,dt: datetime.datetime) -> datetime.datetime:
        """返回 dt 所属执行周期的任务执行时间"""
        return (dt - timedelta(days=dt.weekday() - 2)).replace(
            hour=21,
            minute=0,
            second=0,
            microsecond=0,
        )
    def get_next_cycle_execute_time(self, dt: datetime.datetime) -> datetime.datetime:
        """返回下一个周期的执行时间"""
        return self.get_cycle_execute_time(dt) + timedelta(weeks=1)
    def _handle_initialization(self, current_time: datetime.datetime) -> datetime.datetime:
        china_tz = current_time.tzinfo
        # 读取配置中的时间
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")
        next_execute_time = self.get_cycle_execute_time(current_time)

        if not next_exec_ts:
            return next_execute_time

        try:
            next_exec_dt = datetime.datetime.fromtimestamp(next_exec_ts, tz=china_tz)
        except Exception as e:
            self.logger.warning(f"解析下次执行时间戳失败: {next_exec_ts}, 错误: {e}")
            return next_execute_time

        if next_exec_dt < current_time:
            return next_execute_time
        else:
            return next_exec_dt

    def _handle_execution_completed(self, current_time: datetime.datetime) -> datetime.datetime:
        if self.config.get_task_exe_param(self.task_name, "执行结束后是否有叛忍", True):
            self._activate_another_task("叛忍来袭")
        return self.get_next_cycle_execute_time(current_time)
    

    def reset_task_exe_prog(self) -> bool:
        self.config.set_task_exe_prog(self.task_name, "已战败角色数", 0)
        self.guwu_done = False
        self.fighted = False
        self.last_check_reward_time = time.perf_counter()
        return True
