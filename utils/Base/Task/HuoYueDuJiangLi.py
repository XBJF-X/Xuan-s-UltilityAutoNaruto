from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class HuoYueDuJiangLi(BaseTask):
    source_scene = "奖励"
    task_max_duration = timedelta(minutes=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reward_10 = False
        self.reward_40 = False
        self.reward_80 = False
        self.reward_100 = False
        self.week_reward = False

    @TransitionOn()
    def _(self):
        if (not self.reward_10 and
                not self.config.get_task_exe_prog(self.task_name, f"10活跃度已领取", False)):
            self._handle_daily_activity_reward(10)
            return False
        elif (not self.reward_40 and
              not self.config.get_task_exe_prog(self.task_name, f"40活跃度已领取", False)):
            self._handle_daily_activity_reward(40)
            return False
        elif (not self.reward_80 and
              not self.config.get_task_exe_prog(self.task_name, f"80活跃度已领取", False)):
            self._handle_daily_activity_reward(80)
            return False
        elif (not self.reward_100 and
              not self.config.get_task_exe_prog(self.task_name, f"100活跃度已领取", False)):
            self._handle_daily_activity_reward(100)
            return False
        elif (not self.week_reward and
              not self.config.get_task_exe_prog(self.task_name, f"周活跃度已领取", False)):
            if self.operationer.click_and_wait(
                    "周活跃礼-有红点",
                    auto_raise=False
            ):
                self.logger.info("周活跃已满")
                return False
            else:
                self.logger.warning("周活跃未满")
        if self.reset_prog_parmas():
            self.update_next_execute_time()
            return True
        else:
            self.update_next_execute_time(3, timedelta(hours=3))
            return True

    @TransitionOn("周活跃大礼")
    def _(self):
        if self.operationer.click_and_wait(
                "领取",
                auto_raise=False
        ):
            self.config.set_task_exe_prog(self.task_name, f"周活跃礼已领取", True)
            self.logger.info("周活跃奖励领取成功")
        self.operationer.click_and_wait("X")
        self.week_reward = True
        return False

    def _handle_daily_activity_reward(self, num):
        # 点击待领取的宝箱
        self.logger.info(f"[{num}活跃度宝箱] 开始领取")
        if not self.operationer.detect_element(
                f"每日活跃度-{num}-已领取",
                wait_time=0,
                max_time=0.3,
                auto_raise=False
        ):
            if not self.operationer.click_and_wait(
                    f"每日活跃度-{num}-待领取",
                    wait_time=1,
                    max_time=1,
                    auto_raise=False
            ):
                self.logger.info(f"[{num}活跃度宝箱] 活跃度不足")
            else:
                self.config.set_task_exe_prog(self.task_name, f"{num}活跃度已领取", True)
                self.logger.info(f"[{num}活跃度宝箱] 领取成功")
        else:
            self.config.set_task_exe_prog(self.task_name, f"{num}活跃度已领取", True)
            self.logger.info(f"[{num}活跃度宝箱] 已领取")
        setattr(self, f"reward_{num}", True)

    def reset_prog_parmas(self) -> bool:
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
        if flag:
            self.logger.debug("所有活跃度奖励已领取")
            self.config.set_task_exe_prog(self.task_name, f"10活跃度已领取", False),
            self.config.set_task_exe_prog(self.task_name, f"40活跃度已领取", False),
            self.config.set_task_exe_prog(self.task_name, f"80活跃度已领取", False),
            self.config.set_task_exe_prog(self.task_name, f"100活跃度已领取", False)
            return True
        else:
            self.logger.debug("存在未领取活跃度奖励")
            return False
