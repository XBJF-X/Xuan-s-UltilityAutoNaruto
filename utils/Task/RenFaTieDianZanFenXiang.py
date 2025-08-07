from utils.Task.BaseTask import BaseTask


class RenFaTieDianZanFenXiang(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        self.logger.info("进入[忍法帖]")
        self.click_and_wait({'type': "ELEMENT",'name': "主场景-忍法帖"})
        self.detect_and_wait({'type': "SCENE", 'name': "忍法帖"})
        self.logger.info("进入[忍法帖-排行榜]")
        self.click_and_wait({'type': "ELEMENT",'name': "忍法帖-排行榜"})
        self.detect_and_wait({'type': "SCENE", 'name': "忍法帖-排行榜"})
        self.logger.debug("点赞")
        self.click_and_wait({'type': "ELEMENT",'name': "忍法帖-排行榜-点赞"})
        self.logger.info("分享")
        self.click_and_wait({'type': "ELEMENT",'name': "忍法帖-排行榜-分享"})
        self.logger.info("进入[忍法帖-分享]")
        self.detect_and_wait({'type': "SCENE",'name': "忍法帖-分享"})
        self.logger.info("发给好友")
        self.click_and_wait({'type': "ELEMENT",'name': "忍法帖-排行榜-分享-发给好友"}, wait_time=7)
        self.logger.info("返回游戏")
        # 返回游戏
        self.press_key("back", wait_time=3)
        self._update_next_execute_time()
