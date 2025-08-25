from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class TianDiZhanChang(BaseTask):
    source_scene = "天地战场"
    task_max_duration = timedelta(minutes=30)

    @TransitionOn()
    def _(self):
        self.operationer.click_and_wait("地之战场")
        self.operationer.click_and_wait("确定进入-确认", wait_time=4)
        self.operationer.click_and_wait("出战忍者-忍者")
        self.operationer.click_and_wait("出战忍者-默认选择-1")
        self.operationer.click_and_wait("出战忍者-通灵兽")
        self.operationer.click_and_wait("出战忍者-默认选择-1")
        self.operationer.click_and_wait("出战忍者-默认选择-2")
        self.operationer.click_and_wait("出战忍者-默认选择-3")
        self.operationer.click_and_wait("出战忍者-秘卷")
        self.operationer.click_and_wait("出战忍者-默认选择-1")
        self.operationer.click_and_wait("出战忍者-确认")
        self.operationer.detect_element("地之战场-标识", max_time=10)
        self.operationer.click_and_wait("组织鼓舞")
        while datetime.now(tz=ZoneInfo("Asia/Shanghai")) <= self.dead_line:
            self.operationer.click_and_wait("战场奖励")
            while self.operationer.click_and_wait("战场奖励-领取"):
                if self.operationer.detect_element("战场奖励-恭喜你获得", auto_raise=False):
                    self.operationer.click_and_wait("X")
            self.operationer.click_and_wait("X", wait_time=480)
        self.operationer.click_and_wait("X")
        self.operationer.click_and_wait("X")
        return True

    def _update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
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
                self.next_execute_time = datetime.now(ZoneInfo("Asia/Shanghai"))

            case 3:  # 把执行时间推迟delta时间，要求 delta!=None
                if delta is None:
                    self.logger.warning(f"update_next_execute_time传入的delta为空")
                    return
                self.next_execute_time = current_time + delta

            case _:
                self.logger.warning(f"请检查update_next_execute_time传入的参数：flag={flag},delta={delta}")
                return

        self.logger.info(f"下次执行时间为：{self.next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
        self.config.set_task_config(self.task_name, "下次执行时间", int(self.next_execute_time.timestamp()))
