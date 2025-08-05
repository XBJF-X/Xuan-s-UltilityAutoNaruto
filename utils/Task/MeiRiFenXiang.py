from utils.Task.BaseTask import BaseTask

class MeiRiFenXiang(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        self.logger.info("进入[个人信息]界面")
        # 点击左上角头像
        self.click_and_wait({
            'type': "COORDINATE",
            'coordinate': [109, 65]
        }, wait_time=5)
        self.logger.info("开始分享")
        # 点击分享
        self.click_and_wait({
            'type': "ELEMENT",
            'name': "每日分享-分享"
        }, wait_time=5)
        self.logger.info("发给好友")
        # 点击发给好友
        self.click_and_wait({
            'type': "ELEMENT",
            'name': "每日分享-发给好友"
        }, wait_time=15)
        self.logger.info("返回游戏")
        # 返回游戏
        self.press_key("back", wait_time=5)
        self._update_next_execute_time()
