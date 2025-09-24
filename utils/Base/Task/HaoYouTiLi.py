from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class HaoYouTiLi(BaseTask):
    source_scene = "好友"
    task_max_duration = timedelta(minutes=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flag_1 = False
        self.flag_2 = False

    @TransitionOn("好友")
    def _(self):
        if not self.flag_1:
            self.logger.info("开始领取游戏好友体力")
            # 切换到QQ好友界面
            self.operationer.click_and_wait("游戏好友")
            # 点击游戏好友一键赠送
            self.operationer.click_and_wait("一键赠送")
            # 点击游戏好友一键领取
            self.operationer.click_and_wait("一键领取")
            self.flag_1 = True
            return False
        elif not self.flag_2:
            self.logger.info("开始领取QQ好友体力")
            # 切换到QQ好友界面
            self.operationer.click_and_wait("QQ好友")
            # 点击QQ好友一键赠送
            self.operationer.click_and_wait("一键赠送")
            # 点击QQ好友一键领取
            self.operationer.click_and_wait("一键领取")
            self.flag_2 = True
            return False
        self.update_next_execute_time()
        self.operationer.click_and_wait("X")
        return True

    @TransitionOn("领取好友体力成功")
    def _(self):
        self.operationer.click_and_wait("确认")
        self.logger.info("好友体力领取成功")
        return True