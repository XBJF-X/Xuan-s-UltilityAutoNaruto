from datetime import datetime, timedelta

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class ZhuiJiXiaoZuZhi(BaseTask):
    source_scene = "追击晓组织"
    task_max_duration = timedelta(minutes=3)

    @TransitionOn()
    def _(self):
        self.operationer.click_and_wait("奖励")
        return False

    @TransitionOn("追击晓组织-奖励")
    def _(self):
        if self.operationer.search_and_click(
            ["领取"],
            [
                {
                    "swipe": {
                        "start_coordinate": [1317, 744],
                        "end_coordinate": [1317, 271],
                        "duration": 0.5
                    }
                }
            ],
            max_attempts=1
        ):
            self.logger.info("存在可领取奖励，已点击领取")
            return False
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        return True

    @TransitionOn("任务奖励-一键领取")
    def _(self):
        self.operationer.click_and_wait("确定")
        return False

    def get_cycle_execute_time(self,dt: datetime) -> datetime:
        """返回 dt 所属执行周期的任务执行时间"""
        cycle_execute_time = (dt - timedelta(days=dt.weekday())).replace(
            hour=12,
            minute=0,
            second=0,
            microsecond=0,
        )
        this_monday_5am = dt.replace(
            hour=5,
            minute=0,
            second=0,
            microsecond=0,
        )

        if dt < this_monday_5am:
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


