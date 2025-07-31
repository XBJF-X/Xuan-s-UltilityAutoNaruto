from utils.core.Task.BaseTask import BaseTask

class JinBiZhaoCai(BaseTask):

    def _execute(self):
        self.logger.debug(f"开始执行")
        try:
            # 确定在主场景
            if not self.home():
                raise self.StepFailedError("无法回到[主场景]")
            self.logger.debug("进入金币招财界面")
            # 点击金币招财图标
            self.click_and_wait({
                "type": "COORDINATE",
                "coordinate": [950, 50]
            })
            # 确认招财界面出现
            self.detect_and_wait({
                "type": "SCENE",
                "name": "招财"
            })
            # 确认免费招财按钮出现
            if not self.detect_and_wait({
                "type": "ELEMENT",
                "name": "招财-免费一次"
            }):
                raise self.EndEarly("不存在免费招财次数")

            # 点击两次招财-免费一次
            if self.click_and_wait({
                "type": "ELEMENT",
                "name": "招财-免费一次"
            }):
                self.logger.debug("金币招财一次")
            if self.click_and_wait({
                "type": "ELEMENT",
                "name": "招财-免费一次"
            }):
                self.logger.debug("金币招财两次")
            self._update_next_execute_time()
        except self.StepFailedError as e:
            self.logger.error(e)
        except self.EndEarly as e:
            self._update_next_execute_time()
            self.logger.warning(e)
        finally:
            self.home()
            self.logger.debug(f"执行完毕")
            self.callback(self)
