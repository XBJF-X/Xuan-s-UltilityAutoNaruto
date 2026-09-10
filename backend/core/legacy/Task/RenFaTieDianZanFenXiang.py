import time
import datetime


from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn
from backend.core.legacy.Task.schedule import Weekday, Weekly


# Todo：添加自动收集周活跃度奖励和周任务奖励

class RenFaTieDianZanFenXiang(BaseTask):
    source_scene = "忍法帖-排行榜"
    task_max_duration = datetime.timedelta(minutes=2)
    # 每周任务：窗口 [本周一 5:01, 下周一 5:01)
    schedule = Weekly(Weekday.MON)

    @TransitionOn()
    def _(self):
        self.logger.debug("点赞")
        if not self.operationer.click_and_wait("点赞"):
            self.logger.warning("点赞失败，可能已点赞")
        self.operationer.click_and_wait("分享")
        return False

    @TransitionOn("忍法帖-分享")
    def _(self):
        self.operationer.click_and_wait("发给好友", wait_time=2)
        timeout = 30
        start_time = time.perf_counter()
        while self.operationer.is_naruto_frontend:
            self.logger.debug("火影忍者仍处于前台...") 
            self.operationer.click_and_wait("发给好友", wait_time=0)
            time.sleep(2)
            if time.perf_counter() - start_time > timeout:
                self.logger.debug("跳转分享失败，未能跳出游戏，请检查是否安装QQ/微信(与游戏账号对应)")
                raise
        self.logger.debug("跳转分享成功，正在等待返回游戏...")
        start_time = time.perf_counter()
        share_app = ""
        while not self.operationer.is_naruto_frontend:
            # 采样前台包名（必须在 app_start 之前）：识别本次分享跳转到的 QQ/微信
            front_package = self.operationer.current_app_package
            if front_package in self.operationer.SHARE_APP_PACKAGES:
                share_app = front_package
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
        # 分享结束（游戏已回到前台）后关闭 QQ/微信后台，避免第三方应用常驻
        self.operationer.close_share_app_background(share_app)
        raise TaskCompleted("任务执行完成")
