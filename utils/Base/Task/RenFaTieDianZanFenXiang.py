from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class RenFaTieDianZanFenXiang(BaseTask):
    source_scene = "忍法帖-排行榜"
    task_max_duration = timedelta(minutes=2)

    @TransitionOn()
    def _(self):
        self.logger.debug("点赞")
        if not self.operationer.click_and_wait("点赞", auto_raise=False):
            self.logger.warning("点赞失败，可能已点赞")
        self.operationer.click_and_wait("分享")
        return False

    @TransitionOn("忍法帖-分享")
    def _(self):
        self.operationer.click_and_wait("发给好友",wait_time=5)
        self.logger.info("返回游戏")
        self.operationer.back_to_naruto()
        self.update_next_execute_time()
        return True

    def update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        match flag:

            case 0:  # 创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                next_exec_ts = self.data.get('下次执行时间')
                if next_exec_ts == 0:
                    # 若初始值为0，设置为当前UTC时间（或其他合理时间）
                    self.next_execute_time = datetime.now(ZoneInfo("Asia/Shanghai"))
                else:
                    # 从时间戳转换为datetime对象（指定UTC时区避免歧义）
                    self.next_execute_time = datetime.fromtimestamp(next_exec_ts, tz=china_tz)

            case 1:  # 正常执行完毕，更新为下次执行的时间
                days_ahead = (7 - current_time.weekday()) % 7 or 7
                next_monday = current_time + timedelta(days=days_ahead)
                self.next_execute_time = datetime(
                    next_monday.year, next_monday.month, next_monday.day, 5, 0,
                    tzinfo=china_tz
                )

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                self.next_execute_time = datetime.now(ZoneInfo("Asia/Shanghai"))

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
