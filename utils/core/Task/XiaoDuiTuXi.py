from utils.core.Task.BaseTask import BaseTask


class XiaoDuiTuXi(BaseTask):

    def _execute(self):
        self.logger.info(f"开始执行")
        try:
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
            self.logger.info("跳转至[小队突袭]")
            # 点击小队突袭-立刻前往
            if not self.click_and_search(
                    [
                        {"type": "ELEMENT", "name": "小队突袭-立刻前往"}
                    ],
                    [
                        {
                            "swipe": {
                                "start_coordinate": [1506, 340],
                                "end_coordinate": [340, 340],
                                "duration": 1
                            }
                        }
                    ],
                    3
            ):
                raise self.EndEarly("无法跳转至[小队突袭]，可能已经完成")
            # 确认小队突袭界面出现
            if not self.detect_and_wait({
                "type": "SCENE",
                "name": "小队突袭"
            }):
                raise self.StepFailedError("未能进入[小队突袭-组织助战]")
            self.logger.info("进入[组织助战]")
            # 点击小队突袭-组织助战
            self.click_and_wait({
                "type": "ELEMENT",
                "name": "小队突袭-组织助战"
            }, wait_time=2)

            # 确认小队突袭-组织助战界面
            if not self.detect_and_wait({
                "type": "SCENE",
                "name": "小队突袭-组织助战"
            }):
                raise self.StepFailedError("未能进入[小队突袭-组织助战]")

            if self.detect_and_wait({
                "type": "ELEMENT",
                "name": "小队突袭-今日收益次数已达上限"
            }
            ):
                raise self.EndEarly("小队突袭次数已用尽")
            self.logger.info("进入[我的助战]")
            # 点击我的助战
            self.click_and_wait({
                "type": "ELEMENT",
                "name": "小队突袭-组织助战-我的助战"
            })
            self.logger.info("领取助战奖励")
            # 点击领取
            if self.click_and_wait({
                "type": "ELEMENT",
                "name": "小队突袭-组织助战-我的助战-领取"
            }):
                self.logger.info("助战奖励领取成功")

            self.logger.info("返回[组织助战]")
            # 返回上级小队突袭-组织助战界面
            if not self.esc():
                raise self.StepFailedError("返回[组织助战]失败")
            if self.data.get("四倍奖励勾选"):
                four_reward_times = self.data.get("四倍奖励次数")
            else:
                four_reward_times = 0
            self.logger.info(f"收取四倍奖励次数：{four_reward_times}")
            if four_reward_times > 0:
                self.logger.info("勾选四倍奖励")
                if not self.detect_and_wait({
                    "type": "ELEMENT",
                    "name": "小队突袭-组织助战-四倍奖励-选中"
                }):
                    if not self.click_and_wait({
                        "type": "ELEMENT",
                        "name": "小队突袭-组织助战-四倍奖励-未选中"
                    }):
                        raise self.StepFailedError("小队突袭四倍奖励未选中")

            # 先看看能不能扫荡
            self._handle_sweep_through()
            # 不能就出站
            self.logger.info("出战")
            # 点击出战
            self.click_and_wait({
                "type": "ELEMENT",
                "name": "小队突袭-组织助战-出战"
            }, wait_time=4)
            # 可能有二级密码
            if self.pass_secondary_password():
                self.logger.info("再次出站")
                # 返回True说明检测到了二级密码的弹窗，则需要再次点击出战
                self.click_and_wait({
                    "type": "ELEMENT",
                    "name": "小队突袭-组织助战-出战"
                }, wait_time=4)
            self.logger.info("进入自动战斗")
            # 使用连点器过小队突袭
            self.auto_clicker([
                (800, 750)
            ],
                stop_conditions=[
                    {"type": "SCENE", "name": "小队突袭"}
                ]
            )
            four_reward_times -= 1
            # 等待战斗结束，回到小队突袭界面
            # 确认小队突袭界面
            self.detect_and_wait({
                "type": "SCENE",
                "name": "小队突袭"
            })
            self.logger.info("战斗结束")

            if self.detect_and_wait({
                "type": "ELEMENT",
                "name": "小队突袭-今日收益次数已达上限"
            }):
                raise self.EndEarly("小队突袭次数已用尽")

            if four_reward_times > 0:
                self.logger.info("勾选四倍奖励")
                if not self.detect_and_wait({
                    "type": "ELEMENT",
                    "name": "小队突袭-组织助战-四倍奖励-选中"
                }):
                    if not self.click_and_wait({
                        "type": "ELEMENT",
                        "name": "小队突袭-组织助战-四倍奖励-未选中"
                    }):
                        raise self.StepFailedError("小队突袭四倍奖励未选中")
            # 再看看有没有扫荡
            self._handle_sweep_through()
            # 没有的话老老实实再打一局

            self.logger.info("进入[组织助战]")
            # 点击小队突袭-组织助战
            self.click_and_wait({
                "type": "ELEMENT",
                "name": "小队突袭-组织助战"
            }, wait_time=3)
            # 确认小队突袭-组织助战界面
            self.detect_and_wait({
                "type": "SCENE",
                "name": "小队突袭-组织助战"
            }, wait_time=3)
            self.logger.info("出战")
            # 点击出战
            self.click_and_wait({
                "type": "ELEMENT",
                "name": "小队突袭-组织助战-出战"
            }, wait_time=4)
            # 使用连点器过小队突袭
            self.auto_clicker([
                (800, 750)
            ],
                stop_conditions=[
                    {"type": "SCENE", "name": "小队突袭"}
                ]
            )
            four_reward_times -= 1
            # 确认小队突袭界面
            self.detect_and_wait({
                "type": "SCENE",
                "name": "小队突袭"
            })
            self.logger.info("战斗结束")
            self._update_next_execute_time()

        except self.StepFailedError as e:
            self.logger.error(e)
        except self.EndEarly as e:
            self._update_next_execute_time()
            self.logger.warning(e)
        finally:
            # Esc
            self.esc()
            # 点击小队突袭-离开队伍-确定
            self.click_and_wait({
                "type": "ELEMENT",
                "name": "小队突袭-离开队伍-确定"
            })
            # 返回初始位置
            self.home()
            self.logger.info(f"执行完毕")
            self.callback(self)

    def _handle_sweep_through(self):
        # 假如有扫荡按钮的话，就点击并直接回退，因为扫荡按钮代表只用打一次
        if self.click_and_wait({
            "type": "ELEMENT",
            "name": "小队突袭-扫荡"
        }
        ):
            self.logger.info("存在扫荡按钮，有超影并且已经打过一次")
            # 直接开始点击，点到小队突袭界面出现
            self.logger.info("进入自动战斗")
            # 使用连点器过小队突袭
            self.auto_clicker(
                [
                    (800, 750)
                ],
                stop_conditions=[
                    {"type": "SCENE", "name": "小队突袭"}
                ]
            )
            # 确认小队突袭界面
            self.detect_and_wait({
                "type": "SCENE",
                "name": "小队突袭"
            })
            self.logger.info("战斗结束")
            raise self.EndEarly("已扫荡完成，提前结束")
