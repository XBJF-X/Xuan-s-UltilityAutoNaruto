from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class MeiRiFenXiang(BaseTask):
    source_scene = "个人信息-分享"
    task_max_duration = timedelta(minutes=3)

    @TransitionOn()
    def _(self):
        # 点击发给好友
        self.operationer.click_and_wait("发给好友", wait_time=10)
        self.logger.info("返回游戏")
        # 返回游戏
        self.operationer.back_to_naruto()
        self.update_next_execute_time()
        return True

