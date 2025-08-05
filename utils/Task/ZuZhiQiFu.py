from utils.Task.BaseTask import BaseTask


class ZuZhiQiFu(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        self.logger.info("进入奖励界面")
        # 点击奖励图标
        self.click_and_wait({
            "type": "ELEMENT",
            "name": "主场景-奖励"
        })
        # 确认奖励界面出现
        self.detect_and_wait({
            "type": "SCENE",
            "name": "奖励"
        })
        self.logger.info("跳转至[组织祈福]")
        # 点击组织祈福-立即前往
        if not self.search_and_click(
                [
                    {"type": "ELEMENT", "name": "组织祈福-立刻前往"}
                ],
                [
                    {
                        "swipe": {
                            "start_coordinate": [1506, 340],
                            "end_coordinate": [344, 340],
                            "duration": 1
                        }
                    }
                ],
                max_attempts=4,
                wait_time=3
        ):
            self._update_next_execute_time()
            raise self.EndEarly("无法跳转到[组织祈福]，可能已经完成祈福")
        # 确认组织祈福界面出现
        if not self.detect_and_wait({
            "type": "SCENE",
            "name": "组织祈福"
        }, max_time=5, wait_time=3):
            raise self.StepFailedError("[组织祈福]界面未出现")

        # 点击组织祈福-超影免费
        if not self.click_and_wait({
            "type": "ELEMENT",
            "name": "组织祈福-超影免费"
        }, wait_time=2):
            self.logger.info("超影祈福不存在，点击焚香祈福")
            # 点击组织祈福-焚香祈福
            if not self.click_and_wait({
                "type": "ELEMENT",
                "name": "组织祈福-焚香祈福"
            }, wait_time=2):
                raise self.StepFailedError("[焚香祈福]失败")
            else:
                self.logger.info("[焚香祈福]成功")
        else:
            self.logger.info("点击超影祈福")
        # 点掉上限弹窗
        if self.click_and_wait({
            "type": "ELEMENT",
            "name": "组织祈福-今日次数已达上限-确定"
        }, wait_time=2):
            self.logger.info("已经焚香祈福过了")
        self.logger.info("领取祈福奖励")
        # 确认祈福成功
        if self.detect_and_wait({
            "type": "ELEMENT",
            "name": "组织祈福-恭喜你获得"
        }):
            self.logger.info("祈福奖励领取成功")
            # 随便点下关掉弹窗
            self.click_and_wait({
                "type": "COORDINATE",
                "coordinate": [1525, 45]}, wait_time=3)
        self.logger.info("领取昨日奖励")
        # 点击昨日奖励
        if self.click_and_wait({
            'type': "ELEMENT",
            'name': "组织祈福-昨日奖励"
        }, wait_time=2):
            # 点击所有的领取按钮
            while self.click_and_wait({
                'type': "ELEMENT",
                'name': "组织祈福-昨日奖励-领取"
            }, wait_time=2):
                continue
            # 随便点下关掉弹窗
            self.detect_and_wait({
                "type": "COORDINATE",
                "coordinate": [1525, 45]})
            self.logger.info("昨日奖励领取成功")
        else:
            self.logger.warning("昨日奖励已领取或昨日祈福人数不足15")
        self._update_next_execute_time()
