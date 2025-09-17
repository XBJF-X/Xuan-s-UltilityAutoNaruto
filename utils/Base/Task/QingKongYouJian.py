from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class QingKongYouJian(BaseTask):
    source_scene = "邮件"
    task_max_duration = timedelta(minutes=2)

    @TransitionOn()
    def _(self):
        self.logger.info("进入[邮件]界面")
        # 点击邮件图标
        self.operationer.click_and_wait("一键提取")
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        return True
