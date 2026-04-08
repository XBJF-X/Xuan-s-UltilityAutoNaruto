from datetime import timedelta, datetime

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class YiLeWaiMai(BaseTask):
    source_scene = "一乐外卖"
    task_max_duration = timedelta(minutes=2)

    @TransitionOn()
    def _(self):
        self.logger.info("开始领取[一乐外卖]")
        takeout_sum = 0
        while self.operationer.click_and_wait(
                "待领取",
                max_time=3,
                wait_time=1
        ):
            takeout_sum += 1
            self.logger.debug(f"已领取了 {takeout_sum} 份外卖")
            continue
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        if takeout_sum:
            self._activate_another_task("消耗体力")
        return True

    def get_cycle_execute_time(self,dt: datetime) -> datetime:
        """返回 dt 所属执行周期的任务执行时间"""
        cycle_execute_time = dt.replace(
            hour=11,
            minute=0,
            second=20,
            microsecond=0,
        )
        today_5am = dt.replace(
            hour=5,
            minute=0,
            second=0,
            microsecond=0
        )

        if dt < today_5am:
            return cycle_execute_time - timedelta(days=1)
        return cycle_execute_time
    
    def _handle_initialization(self, current_time: datetime) -> datetime:
        """处理任务初始化时的时间设置（case0）"""
        china_tz = current_time.tzinfo
        # 读取配置中的时间
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")

        # 取得当前执行周期的任务执行时间
        next_execute_time = self.get_cycle_execute_time(current_time)

        if not next_exec_ts:
            # 配置中未设置下次执行时间，返回默认时间
            return next_execute_time

        try:
            next_exec_dt = datetime.fromtimestamp(next_exec_ts, tz=china_tz)
        except Exception as e:
            self.logger.warning(f"解析下次执行时间戳失败: {next_exec_ts}, 错误: {e}")
            return next_execute_time

        # 判断下次执行时间是否过期
        if next_exec_dt < current_time:
            return next_execute_time

        # 配置中的下次执行时间未过期，直接返回
        return next_exec_dt

