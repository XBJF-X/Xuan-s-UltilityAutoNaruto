import time
from datetime import datetime, timedelta

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


# Todo：添加自动收集周活跃度奖励和周任务奖励

class RenFaTieDianZanFenXiang(BaseTask):
    source_scene = "忍法帖-排行榜"
    task_max_duration = timedelta(minutes=2)

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
        self.update_next_execute_time()
        return True

    def _handle_initialization(self, current_time: datetime) -> datetime:
        def get_this_monday_5am(current_time, tz):
            days_ahead = (0 - current_time.weekday()) % 7
            next_monday = current_time + timedelta(days=days_ahead)
            return next_monday.replace(hour=5, minute=0, second=0, microsecond=0, tzinfo=tz)

        china_tz = current_time.tzinfo
        # 读取配置中的时间
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")
        next_execute_time = get_this_monday_5am(current_time, china_tz)

        if next_exec_ts == 0:
            return next_execute_time
        else:
            return datetime.fromtimestamp(next_exec_ts, tz=china_tz)

    def _handle_execution_completed(self, current_time: datetime) -> datetime:
        def get_this_monday_5am(dt: datetime) -> datetime:
            """返回 dt 所在周的周一 05:00:00（保留时区）"""
            days_ahead = (0 - dt.weekday()) % 7
            this_monday = dt + timedelta(days=days_ahead)
            return this_monday.replace(hour=5, minute=0, second=0, microsecond=0)

        # 先得到本周一的 5:00（保留 current_time 的时区属性）
        this_monday_5am = get_this_monday_5am(current_time)

        # 如果当前时刻 < 本周一 5:00，则返回本周一 5:00；否则返回下周一 5:00
        if current_time < this_monday_5am:
            return this_monday_5am
        else:
            return this_monday_5am + timedelta(weeks=1)
