from datetime import timedelta

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class JiFenSaiJiangLi(BaseTask):
    source_scene = "积分赛"
    task_max_duration = timedelta(minutes=2)

    @TransitionOn()
    def _(self):
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        return True

    @TransitionOn("积分赛-段位奖励")
    def _(self):
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("积分赛-排名奖励")
    def _(self):
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("恭喜你获得")
    def _(self):
        self.operationer.click_and_wait("X")
        return False
