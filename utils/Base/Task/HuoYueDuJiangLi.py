from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class HuoYueDuJiangLi(BaseTask):
    source_scene = "奖励"
    task_max_duration = timedelta(minutes=2)

    @TransitionOn("奖励")
    def _(self):
        # 领取每日活跃度宝箱
        self._handle_daily_activity_reward(10)
        self._handle_daily_activity_reward(40)
        self._handle_daily_activity_reward(80)
        self._handle_daily_activity_reward(100)

        # 领取每周活跃度奖励
        self._handle_weekly_acticity_reward()
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        return True

    def _handle_daily_activity_reward(self, num):
        # 点击待领取的宝箱
        self.logger.info(f"[{num}活跃度宝箱] 开始领取")
        if not self.operationer.detect_element(
                f"每日活跃度-{num}-已领取",
                wait_time=0,
                max_time=1,
                auto_raise=False
        ):
            if not self.operationer.click_and_wait(
                    f"每日活跃度-{num}-待领取",
                    wait_time=2,
                    max_time=1,
                    auto_raise=False
            ):
                self.logger.info(f"[{num}活跃度宝箱] 活跃度不足")
                return False
            else:
                self.logger.info(f"[{num}活跃度宝箱] 领取成功")
                return True
        else:
            self.logger.info(f"[{num}活跃度宝箱] 已领取")
            return True

    def _handle_weekly_acticity_reward(self):
        if self.operationer.click_and_wait(
                "周活跃礼-有红点",
                auto_raise=False
        ):
            self.logger.info("周活跃已满")
            if self.operationer.click_and_wait(
                    "周活跃大礼-领取",
                    auto_raise=False
            ):
                self.logger.info("周活跃奖励领取成功")
            self.operationer.click_and_wait("X")
        else:
            self.logger.warning("周活跃未满")

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