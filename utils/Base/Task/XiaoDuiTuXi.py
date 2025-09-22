import logging
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from PySide6.QtCore import QThread

from utils.Base.Config import Config
from utils.Base.Exceptions import EndEarly, StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class XiaoDuiTuXi(BaseTask):
    source_scene = "小队突袭"
    task_max_duration = timedelta(minutes=10)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zhuzhan_reward_collected = False
        self.four_reward_times = self.config.get_task_exe_param(self.task_name, "四倍奖励次数")
        self.four_reward_collected_times = 0
        self.finished = False

    @TransitionOn("小队突袭")
    def _(self):
        self.operationer.click_and_wait("组织助战")
        return False

    @TransitionOn("小队突袭-组织助战")
    def _(self):
        if not self.zhuzhan_reward_collected:
            self.operationer.click_and_wait("我的助战")
            return False
        if not self.operationer.detect_element(
                "今日收益次数已达上限",
                auto_raise=False
        ):
            self._select_four_rewards()
            self.logger.info("出战")
            self.operationer.click_and_wait("出战",wait_time=3)
            return False
        self.update_next_execute_time()
        self.logger.info("小队突袭次数已用尽")
        return True

    @TransitionOn("组织助战-助战忍者")
    def _(self):
        self.logger.info("领取助战奖励")
        # 点击领取
        if self.operationer.click_and_wait(
                "领取",
                auto_raise=False
        ):
            self.logger.info("助战奖励领取成功")
        self.zhuzhan_reward_collected = True
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("离开队伍-确认")
    def _(self):
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("副本结算-点击任意位置关闭界面")
    def _(self):
        self.operationer.click_and_wait("点击任意位置关闭界面")
        self.four_reward_collected_times += 1
        return False

    @TransitionOn("副本内")
    def _(self):
        QThread.msleep(1000)
        return False

    @TransitionOn("副本内-暂停")
    def _(self):
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("副本内-暂停-退出战斗确认")
    def _(self):
        self.operationer.click_and_wait("X")
        return False

    def _select_four_rewards(self):
        if ((self.four_reward_times == 2) or
                (self.four_reward_times == 1 and not self.four_reward_collected_times)):
            self.logger.info("勾选四倍奖励")
            if not self.operationer.detect_element(
                    "四倍奖励-选中",
                    auto_raise=False
            ):
                if not self.operationer.click_and_wait(
                        "四倍奖励-未选中",
                        auto_raise=False
                ):
                    self.logger.warning("小队突袭四倍奖励选中失败")
                    return False
        else:
            self.logger.info("取消勾选四倍奖励")
            if not self.operationer.detect_element(
                    "四倍奖励-未选中",
                    auto_raise=False
            ):
                if not self.operationer.click_and_wait(
                        "四倍奖励-选中",
                        auto_raise=False
                ):
                    self.logger.warning("小队突袭四倍奖励取消选中失败")
                    return False
        return True

