from utils.Task.BaseTask import BaseTask

class HaoYouTiLi(BaseTask):

    def _execute(self):
        self.logger.info(f"开始执行")
        try:
            # 确定在主场景
            if not self.home():
                raise self.StepFailedError("无法回到[主场景]")
            self.logger.info("进入[好友]界面")
            # 点击好友按钮
            self.click_and_wait({
                "type": "ELEMENT",
                "name": "主场景-好友"
            })
            # 确认好友界面出现
            self.detect_and_wait({
                "type": "SCENE",
                "name": "好友"
            })
            self.logger.info("开始领取游戏好友体力")
            # 点击游戏好友一键赠送
            self.click_and_wait({
                "type": "ELEMENT",
                "name": "好友-一键赠送"
            })
            # 点击游戏好友一键领取
            self.click_and_wait({
                "type": "ELEMENT",
                "name": "好友-一键领取"
            })
            # 点击游戏好友-领取成功-确认
            if self.click_and_wait({
                "type": "ELEMENT",
                "name": "好友-领取成功-确认"
            }):
                self.logger.info("游戏好友体力领取成功")
            else:
                self.logger.warning("未能领取游戏好友体力")
            self.logger.info("开始领取QQ好友体力")
            # 切换到QQ好友界面
            self.click_and_wait({
                "type": "COORDINATE",
                "coordinate": [
                    301, 433
                ]
            })
            # 点击QQ好友一键赠送
            self.click_and_wait({
                "type": "ELEMENT",
                "name": "好友-一键赠送"
            })
            # 点击QQ好友一键领取
            self.click_and_wait({
                "type": "ELEMENT",
                "name": "好友-一键领取"
            })
            # 点击QQ好友-领取成功-确认
            if self.click_and_wait({
                "type": "ELEMENT",
                "name": "好友-领取成功-确认"
            }):
                self.logger.info("QQ好友体力领取成功")
            else:
                self.logger.warning("未能领取QQ好友体力")
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
