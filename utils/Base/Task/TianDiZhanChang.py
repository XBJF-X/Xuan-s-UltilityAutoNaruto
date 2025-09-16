from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from PySide6.QtCore import QThread

from utils.Base.Enums import KEY_INDEX
from utils.Base.Exceptions import EndEarly, StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class TianDiZhanChang(BaseTask):
    source_scene = "天地战场"
    task_max_duration = timedelta(minutes=31)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.guwu_done = False
        self.pillar_took = False
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
        self.operationer.click_and_wait("地之战场")
        return False

    @TransitionOn("天之战场")
    def _(self):
        if datetime.now(tz=ZoneInfo("Asia/Shanghai")) > self.dead_line:
            self.update_next_execute_time()
            return True
        if not self.guwu_done:
            self.operationer.click_and_wait("组织鼓舞")
            self.guwu_done = True
            return False
        if self.operationer.click_and_wait("空闲柱子", auto_raise=False):
            self.pillar_took = True
            return False
        self.operationer.click_and_wait("战场奖励")
        return False

    @TransitionOn("地之战场")
    def _(self):
        if datetime.now(tz=ZoneInfo("Asia/Shanghai")) > self.dead_line:
            self.update_next_execute_time()
            return True
        if not self.guwu_done:
            self.operationer.click_and_wait("组织鼓舞")
            self.guwu_done = True
            return False
        if self.operationer.click_and_wait("空闲柱子", auto_raise=False):
            self.pillar_took = True
            return False
        self.operationer.click_and_wait("战场奖励")
        return False

    @TransitionOn("天地战场-确定进入")
    def _(self):
        self.operationer.click_and_wait("确认")
        return False

    @TransitionOn("天地战场-配置阵容")
    def _(self):
        self.operationer.click_and_wait("忍者页")
        self.operationer.click_and_wait("默认点位-1", stable_max_time=0.5)
        self.operationer.click_and_wait("通灵兽页", stable_max_time=0.5)
        self.operationer.click_and_wait("默认点位-1", stable_max_time=0.5)
        self.operationer.click_and_wait("默认点位-2", stable_max_time=0.5)
        self.operationer.click_and_wait("默认点位-3", stable_max_time=0.5)
        self.operationer.click_and_wait("秘卷页", stable_max_time=0.5)
        self.operationer.click_and_wait("默认点位-1", stable_max_time=0.5)
        self.operationer.click_and_wait("确认", stable_max_time=0.5)
        return False

    @TransitionOn("天地战场-战场奖励")
    def _(self):
        while not self.operationer.click_and_wait("领取", auto_raise=False):
            continue
        if not self.operationer.detect_element("未达成"):
            self.operationer.click_and_wait("X")
            self.update_next_execute_time()
            return True
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("天地战场-战场已提前结束")
    def _(self):
        self.operationer.click_and_wait("确定")
        return False

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
        # 辅助函数：计算下次周三9点的时间
        def get_next_wednesday_9pm(current_time, tz):
            current_weekday = current_time.weekday()
            days_ahead = (2 - current_weekday) % 7
            if days_ahead == 0 and current_time.hour >= 21:
                days_ahead = 7
            next_time = current_time + timedelta(days=days_ahead)
            return next_time.replace(hour=21, minute=0, second=0, microsecond=0, tzinfo=tz)

        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        match flag:

            case 0:  # 创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                next_exec_ts = self.data.get('下次执行时间')
                if next_exec_ts == 0:
                    self.next_execute_time = get_next_wednesday_9pm(current_time, china_tz)
                else:
                    # 从时间戳转换为datetime对象（指定UTC时区避免歧义）
                    self.next_execute_time = datetime.fromtimestamp(next_exec_ts, tz=ZoneInfo("Asia/Shanghai"))

            case 1:  # 正常执行完毕，更新为下次执行的时间
                self.next_execute_time = get_next_wednesday_9pm(current_time, china_tz)

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                self.next_execute_time = get_next_wednesday_9pm(current_time, china_tz)

            case 3:  # 把执行时间推迟delta时间，要求 delta!=None
                if delta is None:
                    self.logger.warning(f"update_next_execute_time传入的delta为空")
                    return False, None
                self.next_execute_time = current_time + delta

            case _:
                self.logger.warning(f"请检查update_next_execute_time传入的参数：flag={flag},delta={delta}")
                return False, None

        self.logger.info(f"下次执行时间为：{self.next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
        self.config.set_task_config(self.task_name, "下次执行时间", int(self.next_execute_time.timestamp()))
        return True, self.next_execute_time
