import time
import datetime
from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn
from backend.core.legacy.Task.schedule import Daily, Weekday, Weekly


class XinYueJuLeBu(BaseTask):
    source_scene = "心悦俱乐部"
    task_max_duration = datetime.timedelta(minutes=3)
    
    schedule = Weekly(Weekday.MON, at=datetime.time(0, 0))

    @TransitionOn()
    def _(self):
        if self.operationer.click_and_wait("立即抽奖"):
            self.logger.info("正在进行每周抽奖...")
            time.sleep(3)
            return False
        if self.operationer.click_and_wait("领取",full_match=True):
            self.logger.info("正在领取每周大礼...")
            time.sleep(1)
            return False
        self.logger.info("奖励已经领取完毕")
        return True

    @TransitionOn("心悦俱乐部-恭喜获得")
    def _(self):
        self.operationer.click_and_wait("X")
        return False