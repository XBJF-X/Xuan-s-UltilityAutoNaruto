from datetime import timedelta

from utils.Task.BaseTask import BaseTask

class GaoJiRenZheZhaoMu(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")

        self.logger.info("进入[招募]界面")
        # 点击招募图标
        self.click_and_wait({
            "type": "ELEMENT",
            "name": "主场景-招募"
        })
        # 确认招募界面出现
        self.detect_and_wait({
            "type": "SCENE",
            "name": "招募"
        })
        self.logger.info("进行免费高级招募")
        # 点击高级招募-免费
        if self.click_and_wait({
            "type": "ELEMENT",
            "name": "高级招募-免费"
        }):
            self.logger.info("免费高级招募成功")
            # 点击高级招募-确定
            self.click_and_wait({
                "type": "ELEMENT",
                "name": "高级招募-确定"
            })
            self._update_next_execute_time(delta=timedelta(days=2))
        else:
            self.logger.warning("免费高级招募失败")
            self._update_next_execute_time(delta=timedelta(minutes=10))
