from utils.Task.BaseTask import BaseTask


class HuoYueDuJiangLi(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        self.logger.info("进入奖励界面")
        # 点击奖励图标
        self.click_and_wait({"type": "ELEMENT", "name": "主场景-奖励"})
        # 确认奖励界面出现
        self.detect_and_wait({"type": "SCENE", "name": "奖励"})
        # 领取每日活跃度宝箱
        self._handle_daily_activity_reward(10)
        self._handle_daily_activity_reward(40)
        self._handle_daily_activity_reward(80)
        self._handle_daily_activity_reward(100)

        # 领取每周活跃度奖励
        self._handle_weekly_acticity_reward()
        self._update_next_execute_time()

    def _handle_daily_activity_reward(self, num):
        # 点击待领取的宝箱
        self.logger.info(f"[{num}活跃度宝箱] 开始领取")
        if not self.click_and_wait(
                {'type': "ELEMENT", 'name': f"每日活跃度-{num}-待领取"},
                wait_time=2,
                max_time=2,
                auto_raise=False
        ):
            if self.detect_and_wait(
                    {'type': "ELEMENT", 'name': f"每日活跃度-{num}-未领取"},
                    auto_raise=False
            ):
                self.logger.info(f"[{num}活跃度宝箱] 活跃度不足")
                return False
            if self.detect_and_wait(
                    {'type': "ELEMENT", 'name': f"每日活跃度-{num}-已领取"},
                    auto_raise=False
            ):
                self.logger.info(f"[{num}活跃度宝箱] 已被领取")
                return True
        self.logger.info(f"[{num}活跃度宝箱] 领取完成")
        return True

    def _handle_weekly_acticity_reward(self):
        if self.click_and_wait(
                {'type': "ELEMENT", 'name': "奖励-周活跃礼-有红点"},
                auto_raise=False
        ):
            self.logger.info("周活跃已满")
            if self.click_and_wait(
                    {'type': "ELEMENT", 'name': "奖励-周活跃大礼-领取"},
                    auto_raise=False
            ):
                self.logger.info("周活跃奖励领取成功")
            self.click_and_wait({'type': "COORDINATE", 'coordinate': [1248, 177]})
        else:
            self.logger.warning("周活跃未满")
