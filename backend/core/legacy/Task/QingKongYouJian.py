from datetime import timedelta

from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn


class QingKongYouJian(BaseTask):
    source_scene = "邮件"
    task_max_duration = timedelta(minutes=2)

    @TransitionOn()
    def _(self):
        self.logger.info("进入[邮件]界面")
        # 点击邮件图标
        self.operationer.click_and_wait("一键提取")
        self.operationer.click_and_wait("X")
        raise TaskCompleted("任务执行完成")