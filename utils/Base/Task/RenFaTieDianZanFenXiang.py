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

    def get_cycle_execute_time(self,dt: datetime) -> datetime:
        """返回 dt 所属执行周期的周一 05:00:00"""
        this_monday_5am = (dt - timedelta(days=dt.weekday())).replace(
            hour=5,
            minute=0,
            second=0,
            microsecond=0,
        )
        if dt < this_monday_5am:
            return this_monday_5am - timedelta(weeks=1)
        return this_monday_5am
    
    def get_next_cycle_execute_time(self, dt: datetime) -> datetime:
        """返回下一个周期的执行时间"""
        return self.get_cycle_execute_time(dt) + timedelta(weeks=1)
    
    def _handle_initialization(self, current_time: datetime) -> datetime:
        china_tz = current_time.tzinfo
        # 读取配置中的时间
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")
        next_execute_time = self.get_cycle_execute_time(current_time)

        if not next_exec_ts:
            return next_execute_time

        try:
            next_exec_dt = datetime.fromtimestamp(next_exec_ts, tz=china_tz)
        except Exception as e:
            self.logger.warning(f"解析下次执行时间戳失败: {next_exec_ts}, 错误: {e}")
            return next_execute_time

        if next_exec_dt < current_time:
            return next_execute_time
        else:
            return next_exec_dt
