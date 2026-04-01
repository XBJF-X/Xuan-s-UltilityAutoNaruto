import time
from datetime import timedelta

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class MeiRiFenXiang(BaseTask):
    source_scene = "个人信息-分享"
    task_max_duration = timedelta(minutes=3)

    @TransitionOn()
    def _(self):
        # 点击发给好友
        self.operationer.click_and_wait("发给好友", wait_time=0)

        timeout = 30
        start_time = time.perf_counter()
        while self.operationer.is_naruto_frontend:
            self.logger.debug("火影忍者仍处于前台...")
            time.sleep(1)
            if time.perf_counter() - start_time > timeout:
                self.logger.debug("跳转分享失败，未能跳出游戏，请检查是否安装QQ/微信(与游戏账号对应)")
                raise
        start_time = time.perf_counter()
        while not self.operationer.is_naruto_frontend:
            self.logger.debug("跳转成功，将返回游戏...")
            time.sleep(1)
            self.operationer.app_start()
            time.sleep(1)
            if not self.operationer.is_naruto_frontend:
                self.logger.debug("返回游戏失败，将尝试点击[Esc]键")
                self.operationer.press_key("BACK")

            if time.perf_counter() - start_time > timeout:
                self.logger.debug("返回游戏失败，请自行检查...")
                raise

        self.update_next_execute_time()
        return True
