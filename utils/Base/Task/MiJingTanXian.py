from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from PySide6.QtCore import QThread

from utils.Base.Enums import KEY_INDEX
from utils.Base.Exceptions import StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class MiJingTanXian(BaseTask):
    source_scene = "秘境探险-匹配"
    task_max_duration = timedelta(hours=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fighting = False
        self.operationer.clicker.update_coordinates([
            self.config.get_config("键位")[KEY_INDEX.BasicAttack],
            self.config.get_config("键位")[KEY_INDEX.FirstSkill],
            self.config.get_config("键位")[KEY_INDEX.SecondSkill],
            self.config.get_config("键位")[KEY_INDEX.UltimateSkill]])

    @TransitionOn()
    def _(self):
        if not self.operationer.detect_element(
                "剩余挑战券-0",
                max_time=0.7,
                wait_time=3,
                auto_raise=False
        ):
            self.operationer.click_and_wait("出战")
            self.logger.info("挑战券不为0，继续执行")
            return False
        self.update_next_execute_time()
        return True

    @TransitionOn("秘境奖励")
    def _(self):
        self.fighting = False
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("返回")
        return False

    @TransitionOn("恭喜你获得")
    def _(self):
        self.fighting = False
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("秘境探险-匹配-继续挑战确认")
    def _(self):
        self.operationer.click_and_wait("今日不再提示")
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("副本内")
    def _(self):
        if not self.fighting:
            flag = self.operationer.search_and_detect(
                [
                    self.operationer.get_element("落岩秘境"),
                    self.operationer.get_element("阴阳秘境"),
                    self.operationer.get_element("雷霆秘境"),
                    self.operationer.get_element("烈炎秘境"),
                    self.operationer.get_element("水牢秘境"),
                    self.operationer.get_element("毒风秘境"),
                    self.operationer.get_element("罡体秘境"),
                ],
                [],
                search_max_time=60,
                max_attempts=1,
                wait_time=0
            )
            if flag == 1:
                self.logger.info("检测到落岩秘境，开始战斗")
                # 检测到[落岩秘境]，开始走两步开始连点，停止条件为[胜利/返回图标出现]
                joystick_coordinate = self.config.get_config("键位")[KEY_INDEX.JoyStick]
                self.operationer.long_press(joystick_coordinate[0] + 60, joystick_coordinate[1], 1.5)
                self.fighting = True
                self.operationer.clicker.start()
            elif flag in [3, 4, 5, 7]:
                self.logger.info("检测到非落岩，但高战力可连点过的秘境，开始战斗")
                self.fighting = True
                self.operationer.clicker.start()
            else:
                self.logger.info("不是可连点过的秘境，退出战斗")
                # 点暂停，退出，确认
                self.operationer.click_and_wait("暂停")
            return False
        self.operationer.clicker.start()
        return False

    @TransitionOn("副本内-暂停")
    def _(self):
        self.operationer.click_and_wait("退出战斗")
        return False

    @TransitionOn("副本内-暂停-退出战斗确认")
    def _(self):
        self.operationer.click_and_wait("确定")
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
