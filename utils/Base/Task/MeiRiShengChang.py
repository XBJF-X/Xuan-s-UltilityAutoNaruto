from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from PySide6.QtCore import QThread

from utils.Base.Enums import KEY_INDEX
from utils.Base.Exceptions import StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class MeiRiShengChang(BaseTask):
    source_scene = "忍术对战"
    task_max_duration = timedelta(hours=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checked = False
        self.finished = False
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
        if not self.checked:
            self.operationer.clicker.stop()
            self.operationer.click_and_wait("决斗任务")
            return False
        if not self.finished:
            self.operationer.click_and_wait("开战")
            self.operationer.click_and_wait("开战")
            self.operationer.clicker.start()
            return False
        self.operationer.click_and_wait("X")
        self.logger.info("结束执行")
        self.update_next_execute_time()
        return True

    @TransitionOn("决斗场-匹配中")
    def _(self):
        QThread.msleep(1000)
        return False

    @TransitionOn("忍术对战-决斗任务")
    def _(self):
        self.operationer.clicker.stop()
        self.logger.info("领取所有待领取的决斗任务宝箱")
        while self.operationer.search_and_click(
                [
                    "宝箱-领取"
                ],
                [],
                max_attempts=1,
        ):
            continue
        # 检测有无可追回宝箱
        self.operationer.click_and_wait(
            "宝箱-追回",
            auto_raise=False
        )
        if not self.operationer.search_and_detect(
                [
                    self.operationer.get_element("宝箱-未达成")
                ],
                [
                    {'swipe':
                        {"start_coordinate": [1095, 618], "end_coordinate": [1095, 167],
                            "duration": 0.7}}
                ],
                max_attempts=1,
                bool_debug=True
        ):
            self.checked = True
            self.finished = True
            self.operationer.click_and_wait("X")
            self.update_next_execute_time()
            return True
        self.checked = True
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("决斗任务-追回")
    def _(self):
        self.operationer.click_and_wait("追回", wait_time=0)
        if self.operationer.detect_element("道具不足", auto_raise=False):
            self.operationer.click_and_wait("X")
        return False

    @TransitionOn("决斗场-结算")
    def _(self):
        self.checked = False
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("决斗场-战斗中")
    def _(self):
        self.checked = False
        self.operationer.clicker.start()
        QThread.msleep(1000)
        return False

    @TransitionOn("决斗场-单局结算")
    def _(self):
        self.checked = False
        self.operationer.clicker.stop()
        QThread.msleep(5000)
        return False

    @TransitionOn("你的对手离开了游戏")
    def _(self):
        self.checked = False
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
        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        match flag:

            case 0:  # 创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                next_exec_ts = self.data.get('下次执行时间')
                if next_exec_ts == 0:
                    # 若初始值为0，设置为当前UTC时间（或其他合理时间）
                    self.next_execute_time = datetime.now(china_tz)
                else:
                    # 从时间戳转换为datetime对象（指定UTC时区避免歧义）
                    self.next_execute_time = datetime.fromtimestamp(next_exec_ts, tz=china_tz)

            case 1:  # 正常执行完毕，更新为下次执行的时间
                next_day = current_time + timedelta(days=1)
                # 新建时间时指定时区（与current_time一致）
                self.next_execute_time = datetime(
                    next_day.year, next_day.month, next_day.day, 5, 0,
                    tzinfo=china_tz  # 关键：添加时区信息
                )

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                self.next_execute_time = datetime.now(china_tz)

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
