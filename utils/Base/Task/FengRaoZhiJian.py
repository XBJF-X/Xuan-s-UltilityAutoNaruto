from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Base.Enums import KEY_INDEX
from utils.Base.Exceptions import EndEarly, StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class FengRaoZhiJian(BaseTask):
    source_scene = "丰饶之间"
    task_max_duration = timedelta(minutes=10)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checked = False
        self.free_tryed = False
        self.finished = False
        self.operationer.clicker.update_coordinates([
            self.config.get_config("键位")[KEY_INDEX.BasicAttack],
            self.config.get_config("键位")[KEY_INDEX.FirstSkill],
            self.config.get_config("键位")[KEY_INDEX.SecondSkill],
            self.config.get_config("键位")[KEY_INDEX.UltimateSkill]
        ])

    @TransitionOn("丰饶之间")
    def _(self):
        if not self.checked:
            if self.operationer.detect_element(
                    "今日已完成挑战",
                    max_time=0.3,
                    auto_raise=False
            ):
                self.update_next_execute_time()
                raise EndEarly("已完成挑战，提前结束执行")
            self.checked = True
            return False
        if not self.free_tryed:
            self.operationer.click_and_wait("一键完成")
            return False
        if not self.finished:
            # 点击丰饶之间-挑战
            self.logger.info("无法免费完成，开始自动挑战")
            self.operationer.click_and_wait("挑战")
            self.operationer.clicker.start()
            return False
        self.finished = True
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        return True

    @TransitionOn("丰饶之间-一键完成")
    def _(self):
        if self.operationer.click_and_wait("超影免费", max_time=0.3, auto_raise=False):
            self.free_tryed = True
            return False
        self.free_tryed = True
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("副本结算-点击任意位置关闭界面")
    def _(self):
        self.logger.info("挑战[丰饶之间]成功")
        self.finished = True
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("点击任意位置关闭界面")
        return False

    @TransitionOn("未知场景")
    def _(self):
        self.operationer.clicker.stop()
        return False

    @TransitionOn("未注册场景")
    def _(self):
        self.operationer.clicker.stop()
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
