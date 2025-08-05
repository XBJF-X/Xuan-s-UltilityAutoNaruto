from utils.Task.BaseTask import BaseTask

class RenFaTieDianZanFenXiang(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        self.logger.info("进入[忍法帖]")
        if not self.click_and_wait({
            'type': "ELEMENT",
            'name': "主场景-忍法帖"
        }):
            raise self.StepFailedError("进入[忍法帖]失败")
        if not self.detect_and_wait({
            'type': "SCENE",
            'name': "忍法帖"
        }):
            raise self.StepFailedError("未进入[忍法帖]")
        self.logger.info("进入[忍法帖-排行榜]")
        if not self.click_and_wait({
            'type': "ELEMENT",
            'name': "忍法帖-排行榜"
        }):
            raise self.StepFailedError("进入[忍法帖-排行榜]失败")
        if not self.detect_and_wait({
            'type': "SCENE",
            'name': "忍法帖-排行榜"
        }):
            raise self.StepFailedError("[忍法帖-排行榜]未出现")
        self.logger.debug("点赞")
        if not self.click_and_wait({
            'type': "ELEMENT",
            'name': "忍法帖-排行榜-点赞"
        }):
            raise self.StepFailedError("点赞失败")
        self.logger.info("分享")
        if not self.click_and_wait({
            'type': "ELEMENT",
            'name': "忍法帖-排行榜-分享"
        }):
            raise self.StepFailedError("分享失败")
        self.logger.info("进入[忍法帖-分享]")
        if not self.detect_and_wait({
            'type': "SCENE",
            'name': "忍法帖-分享"
        }):
            raise self.StepFailedError("[忍法帖-分享]未出现")
        self.logger.info("发给好友")
        if not self.click_and_wait({
            'type': "ELEMENT",
            'name': "忍法帖-排行榜-分享-发给好友"
        }, wait_time=7):
            raise self.StepFailedError("发给好友失败")
        self.logger.info("返回游戏")
        # 返回游戏
        self.press_key("back", wait_time=3)
        self._update_next_execute_time()
