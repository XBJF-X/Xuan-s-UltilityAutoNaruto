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
        if not self.reward_10:
            self._handle_daily_activity_reward(10)
            return False
        elif not self.reward_40:
            self._handle_daily_activity_reward(40)
            return False
        elif not self.reward_80:
            self._handle_daily_activity_reward(80)
            return False
        elif not self.reward_100:
            self._handle_daily_activity_reward(100)
            return False
        elif not self.week_reward:
            if self.operationer.click_and_wait(
                    "周活跃礼-有红点",
                    auto_raise=False
            ):
                self.logger.info("周活跃已满")
                return False
            else:
                self.logger.warning("周活跃未满")
        self.update_next_execute_time()
        return True

    @TransitionOn("周活跃大礼")
    def _(self):
        if self.operationer.click_and_wait(
                "周活跃大礼-领取",
                auto_raise=False
        ):
            self.logger.info("周活跃奖励领取成功")
        self.operationer.click_and_wait("X")
        self.week_reward = True
        return True

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
                self.logger.info(f"[{num}活跃度宝箱] 领取成功")
        else:
            self.logger.info(f"[{num}活跃度宝箱] 已领取")
        setattr(self, f"reward_{num}", True)

