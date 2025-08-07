from datetime import timedelta

from utils.Task.BaseTask import BaseTask


class YiLeWaiMai(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        self.logger.info("进入[活动]")
        self.click_and_wait({'type': "ELEMENT", 'name': "主场景-活动"})
        self.detect_and_wait({'type': "SCENE", 'name': "活动"})
        self.logger.info("进入[一乐外卖]")
        if not self.click_and_wait(
                {'type': "ELEMENT", 'name': "活动-一乐外卖-选中"},
                auto_raise=False
        ):
            if not self.click_and_wait(
                    {'type': "ELEMENT", 'name': "活动-一乐外卖-选中"},
                    auto_raise=False
            ):
                raise self.StepFailedError("进入[一乐外卖]失败")
        self.logger.info("开始领取[一乐外卖]")
        takeout_sum = 0
        while self.click_and_wait(
                {'type': "ELEMENT", 'name': "活动-一乐外卖-待领取"},
                auto_raise=False
        ):
            takeout_sum += 1
            self.logger.info(f"已领取了 {takeout_sum} 份外卖")
            continue
        self._update_next_execute_time(time_offset=timedelta(hours=11))
