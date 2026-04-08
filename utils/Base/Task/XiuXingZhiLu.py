from datetime import timedelta, datetime

from utils.Base.Exceptions import EndEarly
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class XiuXingZhiLu(BaseTask):
    source_scene = "试炼之地"
    task_max_duration = timedelta(minutes=3)

    @TransitionOn()
    def _(self):
        self.operationer.click_and_wait("修行之路")
        return False

    @TransitionOn("修行之路")
    def _(self):
        self.operationer.click_and_wait("扫荡", wait_time=0)
        # 先点击扫荡看看能不能扫荡
        if self.operationer.detect_element("当前没有可扫荡关卡了"):
            self.operationer.click_and_wait("重置", wait_time=0)
            if self.operationer.detect_element("每周只能重置1次"):
                self.operationer.click_and_wait("X")
                self.update_next_execute_time()
                raise EndEarly("本周修行之路已完成，提前退出执行")
            return False

    @TransitionOn("修行之路-重置")
    def _(self):
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("修行之路-扫荡")
    def _(self):
        self.operationer.click_and_wait("扫荡")
        return False

    @TransitionOn("修行之路-正在扫荡")
    def _(self):
        if self.operationer.click_and_wait("超影免费"):
            return False
        self.operationer.click_and_wait("X")
        self.update_next_execute_time(3, timedelta(hours=1, minutes=20))
        return True

    @TransitionOn("修行之路-扫荡完成")
    def _(self):
        self.operationer.click_and_wait("领取奖励")
        return False

    @TransitionOn("恭喜你获得")
    def _(self):
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        return True

    def get_cycle_execute_time(self,dt: datetime) -> datetime:
        """返回 dt 所属执行周期的任务执行时间"""
        cycle_execute_time = (dt - timedelta(days=dt.weekday())).replace(
            hour=5,
            minute=0,
            second=0,
            microsecond=0,
        )
        if dt < cycle_execute_time:
            return cycle_execute_time - timedelta(weeks=1)
        return cycle_execute_time
    def get_next_cycle_execute_time(self, dt: datetime) -> datetime:
        """返回下一个周期的执行时间"""
        return self.get_cycle_execute_time(dt) + timedelta(weeks=1)
    def _handle_initialization(self, current_time: datetime) -> datetime:
        china_tz = current_time.tzinfo
        # 读取配置中的时间
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")
        next_execute_time = self.get_cycle_execute_time(current_time)

        if not next_exec_ts:
            return next_execute_time

        try:
            next_exec_dt = datetime.fromtimestamp(next_exec_ts, tz=china_tz)
        except Exception as e:
            self.logger.warning(f"解析下次执行时间戳失败: {next_exec_ts}, 错误: {e}")
            return next_execute_time

        if next_exec_dt < current_time:
            return next_execute_time
        else:
            return next_exec_dt
