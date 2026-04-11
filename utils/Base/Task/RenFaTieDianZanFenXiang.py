import time
import datetime


from utils.Base.Exceptions import TaskCompleted
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


# Todo：添加自动收集周活跃度奖励和周任务奖励

class RenFaTieDianZanFenXiang(BaseTask):
    source_scene = "忍法帖-排行榜"
    task_max_duration = datetime.timedelta(minutes=2)

    @TransitionOn()
    def _(self):
        self.logger.debug("点赞")
        if not self.operationer.click_and_wait("点赞"):
            self.logger.warning("点赞失败，可能已点赞")
        self.operationer.click_and_wait("分享")
        return False

    @TransitionOn("忍法帖-分享")
    def _(self):
        self.operationer.click_and_wait("发给好友", wait_time=0)
        timeout = 30
        start_time = time.perf_counter()
        while self.operationer.is_naruto_frontend:
            self.logger.debug("火影忍者仍处于前台...")
            time.sleep(2)
            if time.perf_counter() - start_time > timeout:
                self.logger.debug("跳转分享失败，未能跳出游戏，请检查是否安装QQ/微信(与游戏账号对应)")
                raise
        start_time = time.perf_counter()
        while not self.operationer.is_naruto_frontend:
            self.logger.debug("跳转成功，将返回游戏...")
            time.sleep(2)
            self.operationer.app_start()
            time.sleep(2)
            if not self.operationer.is_naruto_frontend:
                self.logger.debug("返回游戏失败，将尝试点击[Esc]键")
                self.operationer.press_key("BACK")
                time.sleep(1)

            if time.perf_counter() - start_time > timeout:
                self.logger.debug("返回游戏失败，请自行检查...")
                raise
        raise TaskCompleted("任务执行完成")
    def _get_execute_window(self,dt: datetime.datetime | None = None):
        if dt is None:
            dt=self.last_run_time
        today = dt.date()
        if dt.time() < datetime.time(5, 0):
            today -= datetime.timedelta(days=1)
        
        # 计算today所在的周一
        this_monday = today - datetime.timedelta(days=today.weekday())

        start_dt = datetime.datetime.combine(this_monday, datetime.time(5, 0), tzinfo=self.tz_info)
        dead_dt = datetime.datetime.combine(this_monday+datetime.timedelta(weeks=1), datetime.time(5, 0), tzinfo=self.tz_info)

        return [(start_dt, dead_dt)]
    
    def get_next_cycle_day(self, dt: datetime.datetime) -> datetime.datetime:
        return dt + datetime.timedelta(weeks=1)
