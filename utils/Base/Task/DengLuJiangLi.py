from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class DengLuJiangLi(BaseTask):
    task_max_duration = timedelta(minutes=5)

    def run(self):
        if self.operationer.device.current_app() != self.operationer.device.package_name:

            self.operationer.restart()
        super().run()

    @TransitionOn("登录界面")
    def _(self):
        self.operationer.click_and_wait("开始游戏")
        return False

    @TransitionOn("登录奖励")
    def _(self):
        self.operationer.click_and_wait("领取")
        self.update_next_execute_time()
        return True
