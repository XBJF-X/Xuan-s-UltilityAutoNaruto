from utils.Task.BaseTask import BaseTask


class ShengCunTiaoZhan(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        self.logger.info("进入[奖励]界面")
        # 点击奖励图标
        self.click_and_wait({"type": "ELEMENT", "name": "主场景-奖励"})
        # 确认奖励界面出现
        self.detect_and_wait({"type": "SCENE", "name": "奖励"})
        self.logger.info("跳转至[生存挑战]")
        # 点击完成1关生存挑战-立刻前往
        if not self.search_and_click(
                [
                    {"type": "ELEMENT", "name": "完成1关生存挑战-立刻前往"}
                ],
                [
                    {
                        "swipe": {
                            "start_coordinate": [1504, 340],
                            "end_coordinate": [344, 340],
                            "duration": 1
                        }
                    }
                ],
                max_attempts=3
        ):
            raise self.EndEarly("无法跳转到[生存挑战]，可能已经完成")
        # 确认生存挑战界面出现
        self.detect_and_wait({"type": "SCENE", "name": "生存挑战"})
        self.logger.info("关闭系统自动打的弹窗")
        # 随便点一下把自动打的弹窗点掉
        self.click_and_wait({"type": "COORDINATE", "coordinate": [800, 750]})
        self.click_and_wait({"type": "COORDINATE", "coordinate": [800, 750]})
        self.logger.info("开始扫荡")
        # 点击开始扫荡图标
        self.click_and_wait({'type': "ELEMENT", 'name': "生存挑战-开始扫荡"})
        self.detect_and_wait(
            {'type': "ELEMENT", 'name': "生存挑战-没有可以出战的忍者"},
            max_time=2
        )
        self.logger.warning("没有可出战的忍者，将进行重置")
        if self.click_and_wait({'type': "ELEMENT", 'name': "生存挑战-重置"}):
            self.click_and_wait({'type': "ELEMENT", 'name': "生存挑战-重置-确认"})
            # 随便点一下把自动打的弹窗点掉
            self.click_and_wait({"type": "COORDINATE", "coordinate": [800, 750]})
            self.click_and_wait({"type": "COORDINATE", "coordinate": [800, 750]})

        # 点击准备就绪
        self.click_and_wait({'type': "ELEMENT", 'name': "生存挑战-准备就绪"})
        self.logger.info("准备就绪")
        # 点击确定
        self.click_and_wait(
            {'type': "ELEMENT", 'name': "生存挑战-准备就绪-确定"},
            wait_time=3
        )
        # 点击确定
        self.click_and_wait(
            {'type': "ELEMENT", 'name': "生存挑战-准备就绪-确定-确定"},
            wait_time=3
        )
        self.logger.info("系统开始自动扫荡")

        # 等待生存挑战-已通过所有关卡出现
        if not self.search_and_detect(
                [
                    {'type': "ELEMENT", 'name': "生存挑战-已通过所有关卡"}
                    # {'type': "ELEMENT",'name': "生存挑战-可出战的忍者不足"},
                ],
                [],
                search_max_time=100
        ):
            raise self.StepFailedError("检测[生存挑战-已通过所有关卡]超时")
        self.logger.info("系统自动扫荡结束")
        self._update_next_execute_time()
