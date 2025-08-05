from utils.Task.BaseTask import BaseTask

class QingKongYouJian(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        self.logger.info("进入[邮件]界面")
        # 点击邮件图标
        self.click_and_wait({
            'type': "COORDINATE",
            'coordinate': [70, 348]
        })
        # 确认邮件界面出现
        self.detect_and_wait({
            'type': "SCENE",
            'name': "邮件"
        })
        self.logger.info("一键领取邮件")
        # 点击邮件-一键领取
        self.click_and_wait({
            'type': "ELEMENT",
            'name': "邮件-一键提取"
        })
        self._update_next_execute_time()
