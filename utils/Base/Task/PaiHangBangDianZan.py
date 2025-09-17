from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class PaiHangBangDianZan(BaseTask):
    source_scene = "排行榜"
    task_max_duration = timedelta(minutes=2)

    @TransitionOn()
    def _(self):
        self.logger.info("点赞")
        self.operationer.click_and_wait("点赞")
        self.logger.info("点赞成功")
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        return True

    @property
    def next_execute_time(self):
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")
        if next_exec_ts == 0:
            # 若初始值为0，设置为当前UTC时间（或其他合理时间）
            return datetime(
                current_time.year, current_time.month, current_time.day, 8, 0,
                tzinfo=china_tz  # 关键：添加时区信息
            )
        else:
            # 从时间戳转换为datetime对象
            return datetime.fromtimestamp(next_exec_ts, tz=china_tz)

    def update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        """
        用于更新本任务的下次执行时间，默认为更新到第二天五点（也就是火影服务器任务刷新的时间）

        Args:
            flag: 更新下次执行时间的模式
                0：创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                1：正常执行完毕，更新为下次执行的时间
                2：立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                3：把执行时间推迟delta时间，要求 delta!=None
            delta: 延迟的时长
        Returns:

        """
        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)
        next_execute_time = current_time
        match flag:

            case 0:  # 创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                next_execute_time = self.next_execute_time

            case 1:  # 正常执行完毕，更新为下次执行的时间
                next_day = current_time + timedelta(days=1)
                next_execute_time = datetime(
                    next_day.year, next_day.month, next_day.day, 8, 0,
                    tzinfo=china_tz
                )

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                next_execute_time = current_time

            case 3:  # 把执行时间推迟delta时间，要求 delta!=None
                if delta is None:
                    self.logger.warning(f"update_next_execute_time传入的delta为空")
                    return False, None
                next_execute_time = current_time + delta

        self.logger.info(f"下次执行时间为：{next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
        self.config.set_task_base_config(self.task_name, "下次执行时间", int(next_execute_time.timestamp()))
        return True, next_execute_time
