from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Base.Exceptions import TaskCompleted
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class HuoYueDuJiangLi(BaseTask):
    source_scene = "奖励"
    task_max_duration = timedelta(minutes=3)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.finished = False

    @TransitionOn()
    def _(self):
        if self.finished:
            if self.reset_task_exe_prog():
                raise TaskCompleted("活跃度奖励领取完成")
            else:
                self.schedule_next_with_delay(timedelta(hours=3))
                raise TaskCompleted("活跃度不足，延迟重试")

        if not self.config.get_task_exe_prog(self.task_name, f"10活跃度已领取", False):
            self._handle_daily_activity_reward(10)
            return False
        elif not self.config.get_task_exe_prog(self.task_name, f"40活跃度已领取", False):
            self._handle_daily_activity_reward(40)
            return False
        elif not self.config.get_task_exe_prog(self.task_name, f"80活跃度已领取", False):
            self._handle_daily_activity_reward(80)
            return False
        elif not self.config.get_task_exe_prog(self.task_name, f"100活跃度已领取", False):
            self._handle_daily_activity_reward(100)
            return False
        elif not self.config.get_task_exe_prog(self.task_name, f"周活跃度已领取", False):
            self.operationer.click_and_wait("周活跃礼")
            return False
        self.finished = True
        return False

    @TransitionOn("周活跃大礼")
    def _(self):
        if self.operationer.click_and_wait("领取"):
            self.config.set_task_exe_prog(self.task_name, f"周活跃礼已领取", True)
            self.logger.info("周活跃奖励领取成功")
        self.operationer.click_and_wait("X")
        self.finished = True
        return False

    def _handle_daily_activity_reward(self, num):
        # 点击待领取的宝箱
        self.logger.info(f"[{num}活跃度宝箱] 开始领取")
        if not self.operationer.detect_element(
                f"每日活跃度-{num}-已领取",
                wait_time=0,
                max_time=0.3
        ):
            if self.operationer.detect_element(
                    f"每日活跃度-{num}-待领取",
                    wait_time=1,
                    max_time=1
            ):
                try_times = 0
                # 检测到可以领取，则一直领取直到已领取的状态
                while not self.operationer.detect_element(
                        f"每日活跃度-{num}-已领取",
                        wait_time=0,
                        max_time=0.3
                ):
                    self.operationer.click_and_wait(
                        f"每日活跃度-{num}-待领取",
                        wait_time=1,
                        max_time=1
                    )
                    try_times += 1
                    if try_times >= 3:
                        self.logger.warning(f"{num}活跃度宝箱领取超过3次失败，将不再尝试")
                        return
                self.config.set_task_exe_prog(self.task_name, f"{num}活跃度已领取", True)
                self.logger.info(f"[{num}活跃度宝箱] 领取成功")

            else:
                # 如果没有检测到可以领取，则返回且报警告
                self.logger.info(f"[{num}活跃度宝箱] 活跃度不足")
                self.finished = True
            # if not self.operationer.click_and_wait(
            #         f"每日活跃度-{num}-待领取",
            #         wait_time=1,
            #         max_time=1,
            #         auto_raise=False
            # ):
            #     self.logger.info(f"[{num}活跃度宝箱] 活跃度不足")
            #     self.finished = True
            #     return
            # else:
            #     self.config.set_task_exe_prog(self.task_name, f"{num}活跃度已领取", True)
            #     self.logger.info(f"[{num}活跃度宝箱] 领取成功")
        else:
            self.config.set_task_exe_prog(self.task_name, f"{num}活跃度已领取", True)
            self.logger.info(f"[{num}活跃度宝箱] 已领取")

    def reset_task_exe_prog(self) -> bool:
        self.finished = False
        if (self.config.get_task_exe_prog(self.task_name, f"周活跃礼已领取", False) and
                datetime.now(ZoneInfo("Asia/Shanghai")).weekday() == 6):
            # 每周日重置周活跃领取状态
            self.config.set_task_exe_prog(self.task_name, f"周活跃礼已领取", False)
        flag = all([
            self.config.get_task_exe_prog(self.task_name, f"10活跃度已领取", False),
            self.config.get_task_exe_prog(self.task_name, f"40活跃度已领取", False),
            self.config.get_task_exe_prog(self.task_name, f"80活跃度已领取", False),
            self.config.get_task_exe_prog(self.task_name, f"100活跃度已领取", False)
        ])
        self.config.set_task_exe_prog(self.task_name, f"10活跃度已领取", False)
        self.config.set_task_exe_prog(self.task_name, f"40活跃度已领取", False)
        self.config.set_task_exe_prog(self.task_name, f"80活跃度已领取", False)
        self.config.set_task_exe_prog(self.task_name, f"100活跃度已领取", False)
        if flag:
            self.logger.debug("所有活跃度奖励已领取")
            return True
        else:
            self.logger.debug("存在未领取活跃度奖励")
            return False
