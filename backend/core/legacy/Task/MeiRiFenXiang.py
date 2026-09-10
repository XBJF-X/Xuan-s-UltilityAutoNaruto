import time
from datetime import timedelta

from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn


class MeiRiFenXiang(BaseTask):
    source_scene = "个人信息-分享"
    task_max_duration = timedelta(minutes=3)

    @TransitionOn()
    def _(self):
        # 点击发给好友
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