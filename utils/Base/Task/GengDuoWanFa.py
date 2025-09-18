from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from PySide6.QtCore import QThread

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
        if not self.checked:
            self.operationer.click_and_wait("任务")
            return False
        if not self.finished:
            self.operationer.click_and_wait("入口")
            return False
        self.update_next_execute_time()
        return True

    @TransitionOn("绝迹战场")
    def _(self):
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
        self.operationer.clicker.start()
        self.operationer.next_scene = "更多玩法"
        return False

    @TransitionOn("绝迹战场-副本内")
    def _(self):
        self.checked = False
        self.operationer.clicker.start()
        self.operationer.next_scene = "更多玩法"
        return False

    @TransitionOn("更多玩法-任务")
    def _(self):
        self.operationer.clicker.stop()
        if not self.operationer.detect_element("未达成", auto_raise=False):
            self.finished = True
            self.update_next_execute_time()
            return True
        self.operationer.click_and_wait("X")
        self.checked = True
        return False

    @TransitionOn("更多玩法-匹配中")
    def _(self):
        self.operationer.clicker.stop()
        return False

    @TransitionOn("更多玩法-匹配成功")
    def _(self):
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("准备就绪")
        return False

    @TransitionOn("更多玩法-选择忍者")
    def _(self):
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
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("你的对手离开了游戏")
    def _(self):
        self.operationer.clicker.stop()
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

    @property
    def next_execute_time(self):
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")
        if next_exec_ts == 0:
            # 若初始值为0，设置为本周日12点
            # 计算下一个周日的日期
            # weekday() 返回：0=周一, 1=周二, ..., 6=周日
            days_until_sunday = (6 - current_time.weekday()) % 7
            next_sunday = current_time + timedelta(days=days_until_sunday)

            # 设置时间为本周日12:00:00
            return datetime(
                next_sunday.year, next_sunday.month, next_sunday.day, 5, 0, 0,
                tzinfo=china_tz
            )
        else:
            # 从时间戳转换为datetime对象
            return datetime.fromtimestamp(next_exec_ts, tz=china_tz)

    def update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        match flag:

            case 0:  # 创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                next_execute_time = self.next_execute_time

            case 1:  # 正常执行完毕，更新为下次执行的时间
                # 计算下一个周日的日期
                # weekday() 返回：0=周一, 1=周二, ..., 6=周日
                days_until_sunday = (6 - current_time.weekday()) % 7
                next_sunday = current_time + timedelta(days=days_until_sunday + 7)

                # 设置时间为下周日5:00:00
                next_execute_time = datetime(
                    next_sunday.year, next_sunday.month, next_sunday.day, 5, 0, 0,
                    tzinfo=china_tz
                )

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                next_execute_time = datetime.now(china_tz)

            case 3:  # 把执行时间推迟delta时间，要求 delta!=None
                if delta is None:
                    self.logger.warning(f"update_next_execute_time传入的delta为空")
                    return False, None
                next_execute_time = current_time + delta

            case _:
                self.logger.warning(f"请检查update_next_execute_time传入的参数：flag={flag},delta={delta}")
                return False, None

        self.logger.info(f"下次执行时间为：{next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
        self.config.set_task_base_config(self.task_name, "下次执行时间", int(next_execute_time.timestamp()))
        return True, next_execute_time

