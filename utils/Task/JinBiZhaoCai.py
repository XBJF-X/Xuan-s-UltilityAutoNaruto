from utils.Task.BaseTask import BaseTask


class JinBiZhaoCai(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        if self.config.get_config("已金币招财次数") >= self.data.get("招财次数", 0):
            self._update_next_execute_time()
            self.config.set_config("已金币招财次数", 0)
            raise self.EndEarly("已招满金币招财")
        self.logger.info("进入金币招财界面")
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
        if self.detect_and_wait({
            "type": "ELEMENT",
            "name": "招财-免费一次"
        }):
            # 点击两次招财-免费一次
            if self.click_and_wait({
                "type": "ELEMENT",
                "name": "招财-免费一次"
            }):
                self.logger.info(f"已招财 1 次")
            if self.click_and_wait({
                "type": "ELEMENT",
                "name": "招财-免费一次"
            }):
                self.logger.info(f"已招财 2 次")
        else:
            self.logger.debug("不存在免费招财次数")
        self.config.set_config("已金币招财次数", 2)
        times = self.config.get_config("已金币招财次数")
        while times < self.data.get("招财次数", 2):
            if self.click_and_wait({
                'type': "ELEMENT",
                "name": "招财-付费"
            }):
                if not self.pass_secondary_password():
                    times += 1
                    self.config.set_config("已金币招财次数", times)
                    self.logger.info(f"已招财 {times} 次")
            else:
                raise self.StepFailedError("付费金币招财失败")
        self._update_next_execute_time()
        self.config.set_config("已金币招财次数", 0)
