from utils.Task.BaseTask import BaseTask


class QingBaoZhan(BaseTask):

    def _execute(self):
        self.logger.info(f"开始执行")
        try:
            # 确定在主场景
            if not self.home():
                raise self.StepFailedError("无法回到[主场景]")
            self.logger.info("进入情报站")
            # 点击情报站图标
            self.click_and_wait({
                'type': 'COORDINATE',
                'coordinate': [71, 433]
            }, wait_time=10)
            # 确认情报站首页出现
            self.detect_and_wait({
                'type': 'SCENE',
                'name': "情报站-首页"
            }, wait_time=2, max_time=10)

            self.logger.info("切换到卷轴界面")
            # 切换到卷轴界面+20活跃度
            self.click_and_wait({
                'type': 'COORDINATE',
                'coordinate': [1477, 356]
            }, wait_time=3)
            # 确认情报站卷轴出现
            self.detect_and_wait({
                'type': 'SCENE',
                'name': "情报站-卷轴"
            }, wait_time=2, max_time=10)
            self.logger.info("切换到村口界面")
            # 切换到村口界面+20活跃度
            self.click_and_wait({
                'type': 'COORDINATE',
                'coordinate': [1476, 567]
            }, wait_time=3)
            # 确认情报站村口出现
            self.detect_and_wait({
                'type': 'SCENE',
                'name': "情报站-村口"
            }, wait_time=2, max_time=10)
            self.logger.info("开始点赞帖子")
            love_sum = 0
            retry_time = 0
            while love_sum < 3:
                retry_time += 1
                if self.click_and_search(
                        [
                            {"type": "ELEMENT", "name": "情报站-点赞"}
                        ],
                        [
                            {
                                "swipe": {
                                    "start_coordinate": [760, 845],
                                    "end_coordinate": [760, 180],
                                    "duration": 1
                                }
                            }
                        ],
                        2,
                        wait_time=2
                ):
                    love_sum += 1
                    self.logger.info(f"已点赞❤帖子 {love_sum} 个")
                if retry_time > 20:
                    self.logger.warning("点赞帖子三次失败，可能导致活跃度不足100")
                    break
            self.logger.info("返回情报站首页")
            # 返回情报站首页
            self.click_and_wait({
                'type': 'COORDINATE',
                'coordinate': [1476, 156]
            }, wait_time=3)
            # 确认情报站首页出现
            if not self.detect_and_search(
                [
                    {'type': 'SCENE', 'name': "情报站-首页"}
                ],
                [
                    {'click': {'type': 'COORDINATE', 'coordinate': [1526, 47]}}
                ],
                60
            ):
                raise self.StepFailedError("情报站-首页未出现")
            self.logger.info("切换到忍者站界面")
            # 切换到忍者站界面+10活跃度
            self.click_and_wait({
                'type': 'COORDINATE',
                'coordinate': [408, 34]
            }, wait_time=10)
            # 确认情报站-忍者站出现
            self.detect_and_wait({
                'type': 'SCENE',
                'name': "情报站-忍者站"
            }, wait_time=2, max_time=4)
            self.logger.info("返回情报站首页")
            # 切换回情报站首页
            self.click_and_wait({
                'type': 'COORDINATE',
                'coordinate': [277, 37]
            }, wait_time=6)
            # 确认情报站-首页出现
            self.detect_and_wait({
                'type': 'SCENE',
                'name': "情报站-首页"
            }, wait_time=3, max_time=4)
            self.logger.info("进入福利站")
            # 点击福利站图标
            self.click_and_wait({
                'type': "ELEMENT",
                'name': "情报站-首页-福利站"
            }, wait_time=4)
            # 确认福利站页面已出现
            self.detect_and_wait({
                'type': "SCENE",
                'name': "福利站"
            }, wait_time=2, max_time=4)
            self.logger.info("福利站签到")
            # 点击福利站-立即签到
            if not self.click_and_wait({
                'type': "ELEMENT",
                'name': "福利站-立即签到"
            }, wait_time=3):
                # 点击福利站-一键签到
                if self.click_and_wait({
                    'type': "ELEMENT",
                    'name': "福利站-一键签到"
                }, wait_time=3):
                    self.logger.info("未自动弹出窗口，点击一键签到")
                else:
                    self.logger.warning("手动点击一键签到失败，可能已经签到过")
            else:
                self.logger.info("自动弹出窗口，点击立即签到")
            # 签到成功，点击我知道了
            self.click_and_wait({
                'type': "ELEMENT",
                'name': "福利站-我知道了"
            }, wait_time=3)
            self.logger.info("进入金币助手")
            # 点击[福利站-今日查看金币助手-去完成]
            if not self.click_and_search(
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
                    2,
                    5
            ):
                raise self.StepFailedError("未找到[福利站-今日查看金币助手-去完成]，进入金币助手失败")

            # 一段时间后，直接输入返回指令（因为竖屏不好识别）
            self.logger.info("返回福利站")
            self.press("back",wait_time=7)
            self.logger.info("领取活跃度奖励")
            # 点击所有的领取按钮
            while self.click_and_wait({
                'type': "ELEMENT",
                'name': "福利站-活跃度任务-领取"
            }, wait_time=3):
                continue

            # 点击40活跃度奖励
            self.handle_40_activity_reward()
            # 点击60活跃度奖励
            self.handle_60_activity_reward()
            # 点击100活跃度奖励
            self.handle_100_activity_reward()

            self._update_next_execute_time()
        except self.StepFailedError as e:
            self.logger.error(e)
        except self.EndEarly as e:
            self._update_next_execute_time()
            self.logger.warning(e)
        except self.Stop as e:
            self.logger.warning("线程被要求停止")
        finally:
            self.home()
            self.logger.info(f"执行完毕")
            self.callback(self)

    def handle_40_activity_reward(self):
        self.logger.info("领取40活跃度奖励")
        if self.click_and_wait({
            'type': "ELEMENT",
            'name': "福利站-活跃度任务-40"
        }):
            if self.detect_and_wait({
                'type': "ELEMENT",
                'name': "福利站-活跃度任务-今日已领取过该奖励"
            }, wait_time=3):
                self.logger.warning("40活跃度奖励已领取")
                return True

            # 点击40活跃度奖励-确定
            if not self.click_and_wait({
                'type': "ELEMENT",
                'name': "福利站-活跃度任务-40-确定"
            }, wait_time=2):
                self.logger.error("点击[活跃度-40-确定]失败")
                return False

            # 等待转盘结束之后点击 转盘抽奖-我知道了
            while not self.click_and_wait({
                'type': "ELEMENT",
                'name': "福利站-活跃度任务-40-我知道了"
            }, wait_time=1):
                continue
            self.logger.info("40活跃度奖励领取完成")
            return True
        self.logger.error("40活跃度奖励领取失败，活跃度未达到要求")
        return False

    def handle_60_activity_reward(self):
        self.logger.info("领取60活跃度奖励")
        if self.click_and_wait({
            'type': "ELEMENT",
            'name': "福利站-活跃度任务-60"
        }):
            if self.detect_and_wait({
                'type': "ELEMENT",
                'name': "福利站-活跃度任务-今日已领取过该奖励"
            }, wait_time=3):
                self.logger.info("60活跃度奖励已领取")
                return True
            # 点击我知道了
            if not self.click_and_wait({
                'type': "ELEMENT",
                'name': "福利站-活跃度任务-60-我知道了"
            }):
                self.logger.error("点击[活跃度-60-我知道了]失败")
                return False
            self.logger.info("60活跃度奖励领取完成")
            return True
        self.logger.error("60活跃度奖励领取失败，活跃度未达到要求")
        return False

    def handle_100_activity_reward(self):
        self.logger.info("领取100活跃度奖励")
        if self.click_and_wait({
            'type': "ELEMENT",
            'name': "福利站-活跃度任务-100"
        }):
            if self.detect_and_wait({
                'type': "ELEMENT",
                'name': "福利站-活跃度任务-今日已领取过该奖励"
            }):
                self.logger.info("100活跃度奖励已领取")
                return True
            # 点击确定
            if not self.click_and_wait({
                'type': "ELEMENT",
                'name': "福利站-活跃度任务-100-确定"
            }):
                self.logger.error("点击[活跃度-100-确定]失败")
                return False
            # 点击我知道了
            self.click_and_wait({
                'type': "ELEMENT",
                'name': "福利站-活跃度任务-100-我知道了"
            })
            self.logger.info("100活跃度奖励领取完成")
            return True
        self.logger.error("100活跃度奖励领取失败，活跃度未达到要求")
        return False
