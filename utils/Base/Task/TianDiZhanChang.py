from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

from PySide6.QtCore import QThread

from utils.Base.Enums import KEY_INDEX
from utils.Base.Exceptions import EndEarly, StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn, handle_task_exceptions

choose_dic = ["天之战场", "地之战场"]


# Todo：修复天地战场第二次上人时选人失误的问题
class TianDiZhanChang(BaseTask):
    source_scene = "天地战场"
    dead_line = time(21, 30)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.guwu_done = False
        self.pillar_took = False
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

    @TransitionOn()
    def _(self):
        self.operationer.click_and_wait(choose_dic[self.choose])
        return False

    @TransitionOn("天之战场")
    def _(self):
        current_time = datetime.now(tz=ZoneInfo("Asia/Shanghai"))
        if current_time > current_time.replace(hour=21, minute=30, second=0, microsecond=0):
            self.logger.info("天地战场时间已过，停止执行")
            self.update_next_execute_time()
            return True
        if not self.guwu_done:
            self.operationer.click_and_wait("组织鼓舞")
            self.guwu_done = True
            return False
        if self.operationer.detect_element("战场已提前结束"):
            self.logger.info("战场已提前结束，停止执行")
            self.update_next_execute_time()
            return True
        if not self.pillar_took:
            if self.operationer.click_and_wait("空闲柱子", max_time=20, auto_raise=False):
                self.pillar_took = True
        else:
            QThread.sleep(20)
        self.operationer.click_and_wait("战场奖励")
        return False

    @TransitionOn("地之战场")
    def _(self):
        current_time = datetime.now(tz=ZoneInfo("Asia/Shanghai"))
        if current_time > current_time.replace(hour=21, minute=30, second=0, microsecond=0):
            self.logger.info("天地战场时间已过，停止执行")
            self.update_next_execute_time()
            return True
        if not self.guwu_done:
            self.operationer.click_and_wait("组织鼓舞")
            self.guwu_done = True
            return False
        if self.operationer.detect_element("战场已提前结束"):
            self.logger.info("战场已提前结束，停止执行")
            self.update_next_execute_time()
            return True
        if not self.pillar_took:
            if self.operationer.click_and_wait("空闲柱子", max_time=20, auto_raise=False):
                self.pillar_took = True
        else:
            QThread.sleep(20)
        self.operationer.click_and_wait("战场奖励")
        return False

    @TransitionOn("天地战场-确定进入")
    def _(self):
        self.operationer.click_and_wait("确认")
        return False

    @TransitionOn("天地战场-确定进入")
    def _(self):
        self.operationer.click_and_wait("确认")
        return False

    @TransitionOn("天地战场-配置阵容")
    def _(self):
        defeated_ninja_num = max(self.config.get_task_exe_prog(self.task_name, "已战败角色数", 0), 2) + 1
        self.operationer.click_and_wait("忍者页")
        if not self.operationer.detect_element(f"默认点位-{defeated_ninja_num}-选中"):
            if defeated_ninja_num >= 4:
                self.config.set_task_exe_prog(self.task_name, "已战败角色数", 0)
            else:
                self.operationer.click_and_wait(f"默认点位-{defeated_ninja_num}", stable_max_time=0.5)
                self.config.set_task_exe_prog(self.task_name, "已战败角色数", defeated_ninja_num)

        self.operationer.click_and_wait("通灵兽页", stable_max_time=0.5)
        for i in range(1, 4):
            if not self.operationer.detect_element(f"默认点位-{i}-选中"):
                self.operationer.click_and_wait(f"默认点位-{i}", stable_max_time=0.5)

        self.operationer.click_and_wait("秘卷页", stable_max_time=0.5)
        if not self.operationer.detect_element("默认点位-1-选中"):
            self.operationer.click_and_wait("默认点位-1", stable_max_time=0.5)

        self.operationer.click_and_wait("确认", stable_max_time=0.5)
        return False

    @TransitionOn("天地战场-战场奖励")
    def _(self):
        while self.operationer.click_and_wait("领取", auto_raise=False):
            continue
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("天地战场-战场战斗已经结束")
    def _(self):
        self.operationer.click_and_wait("确认")
        self.update_next_execute_time()
        return True

    @TransitionOn("天地战场-确认退出")
    def _(self):
        self.operationer.click_and_wait("确认")
        return False

    @TransitionOn("恭喜你获得")
    def _(self):
        self.operationer.click_and_wait("")
        return False

    @TransitionOn("决斗场-结算")
    def _(self):
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("X")
        self.pillar_took = False
        return False

    @TransitionOn("决斗场-单局结算")
    def _(self):
        self.operationer.clicker.stop()
        self.pillar_took = False
        return False

    @TransitionOn("决斗场-战斗中")
    def _(self):
        self.operationer.clicker.start()
        self.pillar_took = False
        QThread.msleep(500)
        return False

    @TransitionOn("你的对手离开了游戏")
    def _(self):
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("未知场景")
    def _(self):
        self.operationer.clicker.stop()
        QThread.msleep(1000)
        return False

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
        current_time = datetime.now(china_tz)

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

    def _handle_initialization(self, current_time: datetime) -> datetime:
        def get_this_wednesday_9pm(current_time, tz):
            days_ahead = (2 - current_time.weekday()) % 7
            next_time = current_time + timedelta(days=days_ahead)
            return next_time.replace(hour=21, minute=0, second=0, microsecond=0, tzinfo=tz)

        china_tz = current_time.tzinfo

        # 本周周三下午9点的时间对象
        next_execute_time = get_this_wednesday_9pm(current_time, china_tz)

        if current_time > next_execute_time + timedelta(minutes=30):
            next_execute_time += timedelta(days=7)

        return next_execute_time

    def _handle_execution_completed(self, current_time: datetime) -> datetime:
        def get_this_wednesday_9pm(current_time, tz):
            days_ahead = (2 - current_time.weekday()) % 7
            next_time = current_time + timedelta(days=days_ahead)
            return next_time.replace(hour=21, minute=0, second=0, microsecond=0, tzinfo=tz)

        china_tz = current_time.tzinfo

        # 下周周六下午8点的时间对象
        next_execute_time = get_this_wednesday_9pm(current_time, china_tz) + timedelta(weeks=1)

        return next_execute_time

    def reset_task_exe_proc(self) -> bool:
        self.config.set_task_exe_prog(self.task_name, "已战败角色数", 0)
        return True
