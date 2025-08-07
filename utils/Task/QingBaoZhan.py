from utils.Task.BaseTask import BaseTask


class QingBaoZhan(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        self.logger.info("进入情报站")
        # 点击情报站图标
        self.click_and_wait(
            {'type': 'COORDINATE', 'coordinate': [71, 433]},
            wait_time=10
        )
        # 确认情报站首页出现
        self.detect_and_wait(
            {'type': 'SCENE', 'name': "情报站-首页"},
            wait_time=2,
            max_time=10
        )

        self.logger.info("切换到卷轴界面")
        # 切换到卷轴界面+20活跃度
        self.click_and_wait(
            {'type': 'COORDINATE', 'coordinate': [1477, 356]},
            wait_time=3
        )
        # 确认情报站卷轴出现
        self.detect_and_wait(
            {'type': 'SCENE', 'name': "情报站-卷轴"},
            wait_time=2,
            max_time=10
        )
        self.logger.info("切换到村口界面")
        # 切换到村口界面+20活跃度
        self.click_and_wait(
            {'type': 'COORDINATE', 'coordinate': [1476, 567]},
            wait_time=3
        )
        # 确认情报站村口出现
        self.detect_and_wait(
            {'type': 'SCENE', 'name': "情报站-村口"},
            wait_time=2,
            max_time=10
        )
        self.logger.info("开始点赞帖子")
        love_sum = 0
        retry_time = 0
        while love_sum < 3:
            retry_time += 1
            flag = self.search_and_detect(
                [
                    {"type": "ELEMENT", "name": "情报站-点赞-未点"},
                    {"type": "ELEMENT", "name": "情报站-点赞-已点"}
                ],
                [
                    {
                        "swipe": {
                            "start_coordinate": [760, 870],
                            "end_coordinate": [760, 80],
                            "duration": 1
                        }
                    }
                ],
                wait_time=0,
                bool_debug=True
            )
            if flag == 1:
                self.logger.debug("发现未被点赞帖子")
                self.click_and_wait(
                    {"type": "ELEMENT", "name": "情报站-点赞-未点"},
                    wait_time=2
                )
                love_sum += 1
                self.logger.info(f"已点赞❤帖子 {love_sum} 个")

            elif flag == 2:
                self.logger.debug("发现已被点赞帖子")
                self.click_and_wait(
                    {"type": "ELEMENT", "name": "情报站-点赞-已点"},
                    wait_time=2
                )
                self.click_and_wait(
                    {"type": "ELEMENT", "name": "情报站-点赞-未点"},
                    wait_time=2
                )
                love_sum += 1
                self.logger.info(f"已点赞❤帖子 {love_sum} 个")

            if retry_time > 30:
                self.logger.warning("点赞帖子三次失败，可能导致活跃度不足100")
                break
            if love_sum < 3:
                self.swipe_and_wait(
                    (760, 870),
                    (760, 80),
                    wait_time=0,
                    duration=1
                )
        self.logger.info("返回情报站首页")
        # 返回情报站首页
        self.click_and_wait(
            {'type': 'COORDINATE', 'coordinate': [1476, 156]},
            wait_time=3
        )
        # 确认情报站首页出现
        if not self.search_and_detect(
                [
                    {'type': 'SCENE', 'name': "情报站-首页"}
                ],
                [
                    {'click': {'type': 'COORDINATE', 'coordinate': [1526, 47]}}
                ],
                search_max_time=60,
                bool_debug=True
        ):
            raise self.StepFailedError("情报站-首页未出现")
        self.logger.info("切换到忍者站界面")
        # 切换到忍者站界面+10活跃度
        self.click_and_wait(
            {'type': 'COORDINATE', 'coordinate': [408, 34]},
            wait_time=10
        )
        # 确认情报站-忍者站出现
        self.detect_and_wait(
            {'type': 'SCENE', 'name': "情报站-忍者站"},
            wait_time=2,
            max_time=4
        )
        self.logger.info("返回情报站首页")
        # 切换回情报站首页
        self.click_and_wait(
            {'type': 'COORDINATE', 'coordinate': [277, 37]},
            wait_time=6
        )
        # 确认情报站-首页出现
        self.detect_and_wait(
            {'type': 'SCENE', 'name': "情报站-首页"},
            wait_time=3,
            max_time=4
        )
        self.logger.info("进入福利站")
        # 点击福利站图标
        self.click_and_wait(
            {'type': "ELEMENT", 'name': "情报站-首页-福利站"},
            wait_time=4
        )
        self.logger.info("福利站签到")
        # 点击福利站-立即签到
        if not self.click_and_wait(
                {'type': "ELEMENT", 'name': "福利站-立即签到"},
                wait_time=3,
                max_time=5,
                auto_raise=False
        ):
            # 点击福利站-一键签到
            if self.click_and_wait(
                    {'type': "ELEMENT", 'name': "福利站-一键签到"},
                    wait_time=3,
                    max_time=5,
                    auto_raise=False
            ):
                self.logger.info("未自动弹出窗口，点击一键签到")
                self.click_and_wait(
                    {'type': "ELEMENT", 'name': "福利站-立即签到"},
                    wait_time=3
                )
            else:
                self.logger.warning("手动点击一键签到失败，可能已经签到过")
        else:
            self.logger.info("自动弹出窗口，点击立即签到")
        # 签到成功，点击我知道了
        self.click_and_wait(
            {'type': "ELEMENT", 'name': "福利站-我知道了"},
            wait_time=3
        )
        # 确认福利站页面已出现
        self.detect_and_wait(
            {'type': "SCENE", 'name': "福利站"},
            wait_time=2,
            max_time=4
        )
        self.logger.info("[福利站]页面出现")
        self.logger.info("进入金币助手")
        # 点击[福利站-今日查看金币助手-去完成]
        if not self.search_and_click(
                [
                    {'type': "ELEMENT", 'name': "福利站-今日查看金币助手-去完成"}
                ],
                [
                    {
                        "swipe": {
                            "start_coordinate": [600, 850],
                            "end_coordinate": [600, 290],
                            "duration": 1
                        }
                    }
                ],
                max_attempts=5
        ):
            raise self.StepFailedError("未找到[福利站-今日查看金币助手-去完成]，进入金币助手失败")

        # 一段时间后，直接输入返回指令（因为竖屏不好识别）
        self.logger.info("返回福利站")
        self.press_key("back", wait_time=7)
        self.logger.info("领取活跃度奖励")
        # 点击所有的领取按钮
        while self.click_and_wait(
                {'type': "ELEMENT", 'name': "福利站-活跃度任务-领取"},
                wait_time=3,
                auto_raise=False
        ):
            continue

        # 点击40活跃度奖励
        self.handle_40_activity_reward()
        # 点击60活跃度奖励
        self.handle_60_activity_reward()
        # 点击100活跃度奖励
        self.handle_100_activity_reward()

        self._update_next_execute_time()

    def handle_40_activity_reward(self):
        self.logger.info("领取40活跃度奖励")
        if self.click_and_wait(
                {'type': "ELEMENT", 'name': "福利站-活跃度任务-40"},
                auto_raise=False
        ):
            if self.detect_and_wait(
                    {'type': "ELEMENT", 'name': "福利站-活跃度任务-今日已领取过该奖励"},
                    wait_time=3,
                    auto_raise=False
            ):
                self.logger.warning("40活跃度奖励已领取")
                return True

            # 点击40活跃度奖励-确定
            if not self.click_and_wait(
                    {'type': "ELEMENT", 'name': "福利站-活跃度任务-40-确定"},
                    wait_time=2,
                    auto_raise=False
            ):
                self.logger.error("点击[活跃度-40-确定]失败")
                return False

            # 等待转盘结束之后点击 转盘抽奖-我知道了
            while not self.click_and_wait(
                    {'type': "ELEMENT", 'name': "福利站-活跃度任务-40-我知道了"},
                    wait_time=1,
                    auto_raise=False
            ):
                continue
            self.logger.info("40活跃度奖励领取完成")
            return True
        self.logger.warning("40活跃度奖励领取失败，活跃度未达到要求")
        return False

    def handle_60_activity_reward(self):
        self.logger.info("领取60活跃度奖励")
        if self.click_and_wait(
                {'type': "ELEMENT", 'name': "福利站-活跃度任务-60"},
                auto_raise=False
        ):
            if self.detect_and_wait(
                    {'type': "ELEMENT", 'name': "福利站-活跃度任务-今日已领取过该奖励"},
                    wait_time=3,
                    auto_raise=False
            ):
                self.logger.info("60活跃度奖励已领取")
                return True
            # 点击我知道了
            if not self.click_and_wait(
                    {'type': "ELEMENT", 'name': "福利站-活跃度任务-60-我知道了"},
                    auto_raise=False
            ):
                self.logger.error("点击[活跃度-60-我知道了]失败")
                return False
            self.logger.info("60活跃度奖励领取完成")
            return True
        self.logger.warning("60活跃度奖励领取失败，活跃度未达到要求")
        return False

    def handle_100_activity_reward(self):
        self.logger.info("领取100活跃度奖励")
        if self.click_and_wait(
                {'type': "ELEMENT", 'name': "福利站-活跃度任务-100"},
                auto_raise=False
        ):
            if self.detect_and_wait(
                    {'type': "ELEMENT", 'name': "福利站-活跃度任务-今日已领取过该奖励"},
                    auto_raise=False
            ):
                self.logger.info("100活跃度奖励已领取")
                return True
            # 点击确定
            if not self.click_and_wait(
                    {'type': "ELEMENT", 'name': "福利站-活跃度任务-100-确定"},
                    auto_raise=False
            ):
                self.logger.error("点击[活跃度-100-确定]失败")
                return False
            # 点击我知道了
            self.click_and_wait({'type': "ELEMENT", 'name': "福利站-活跃度任务-100-我知道了"})
            self.logger.info("100活跃度奖励领取完成")
            return True
        self.logger.warning("100活跃度奖励领取失败，活跃度未达到要求")
        return False
