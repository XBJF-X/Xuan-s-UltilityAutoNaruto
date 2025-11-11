from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from PySide6.QtCore import QThread

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class QingBaoZhan(BaseTask):
    source_scene = "情报站-首页"
    task_max_duration = timedelta(minutes=5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.activity_reward_40_done = False
        self.activity_reward_60_done = False
        self.activity_reward_100_done = False

    @TransitionOn()
    def _(self):
        if not self.config.get_task_exe_prog(self.task_name, "浏览卷轴", False):
            self.operationer.click_and_wait("卷轴")
            return False
        elif not self.config.get_task_exe_prog(self.task_name, "浏览村口", False) or \
                self.config.get_task_exe_prog(self.task_name, "点赞帖子", 0) < 3:
            self.operationer.click_and_wait("村口")
            return False
        elif not self.config.get_task_exe_prog(self.task_name, "浏览忍者站", False):
            self.operationer.click_and_wait("忍者站")
            return False
        self.operationer.click_and_wait("福利站")
        return False

    @TransitionOn("情报站-卷轴")
    def _(self):
        self.config.set_task_exe_prog(self.task_name, "浏览卷轴", True)
        self.operationer.click_and_wait("村口")
        return False

    @TransitionOn("情报站-村口")
    def _(self):
        self.config.set_task_exe_prog(self.task_name, "浏览村口", True)
        love_sum = self.config.get_task_exe_prog(self.task_name, "点赞帖子", 0)
        if love_sum < 3:
            flag = self.operationer.search_and_detect(
                [
                    self.operationer.get_element("点赞-未点"),
                    self.operationer.get_element("点赞-已点")
                ],
                [
                    {
                        "swipe": {
                            "start_coordinate": [760, 870],
                            "end_coordinate": [760, 80],
                            "duration": 1
                        }
                    }
                ],
                wait_time=0,
                bool_debug=True
            )
            if flag == 1:
                self.logger.debug("发现未被点赞帖子")
                self.operationer.click_and_wait("点赞-未点")
                love_sum += 1
                self.config.set_task_exe_prog(self.task_name, "点赞帖子", love_sum)
                self.logger.info(f"已点赞❤帖子 {love_sum} 个")
            elif flag == 2:
                self.logger.debug("发现已被点赞帖子")
                self.operationer.click_and_wait("点赞-已点")
                self.operationer.click_and_wait("点赞-未点")
                love_sum += 1
                self.config.set_task_exe_prog(self.task_name, "点赞帖子", love_sum)
                self.logger.info(f"已点赞❤帖子 {love_sum} 个")
            self.operationer.swipe_and_wait(
                    (760, 870),
                    (760, 80),
                    wait_time=0,
                    duration=0.7
                )
        else:
            self.operationer.click_and_wait("首页")
        return False

    @TransitionOn("忍者站")
    def _(self):
        self.config.set_task_exe_prog(self.task_name, "浏览忍者站", True)
        self.operationer.click_and_wait("推荐")
        return False

    @TransitionOn("福利站")
    def _(self):
        if not self.config.get_task_exe_prog(self.task_name, "情报站签到", False):
            self.logger.info("福利站签到")
            # 点击一键签到
            self.operationer.click_and_wait("一键签到", auto_raise=False, wait_time=3)
            self.config.set_task_exe_prog(self.task_name, "情报站签到", True)
            return False

        elif not self.config.get_task_exe_prog(self.task_name, "浏览金币助手", False):
            self.logger.info("进入金币助手")
            # 点击[福利站-今日查看金币助手-去完成]
            if not self.operationer.search_and_click(
                    ["今日查看金币助手-去完成"],
                    [
                        {
                            "swipe": {
                                "start_coordinate": [600, 850],
                                "end_coordinate": [600, 290],
                                "duration": 1
                            }
                        }
                    ],
                    max_attempts=2,
                    wait_time=5
            ):
                self.logger.warning("进入金币助手失败")
                self.operationer.swipe_and_wait((600, 290), (600, 850), duration=0.7)
                self.operationer.swipe_and_wait((600, 290), (600, 850), duration=0.7)
            else:
                self.logger.info("返回福利站")
                self.operationer.press_key("back", wait_time=7)
            self.config.set_task_exe_prog(self.task_name, "浏览金币助手", True)
            return False

        elif not self.config.get_task_exe_prog(self.task_name, "领取情报站活跃度", False):
            self.logger.info("领取活跃度奖励")
            # 点击所有的领取按钮
            while self.operationer.click_and_wait(
                    "活跃度任务-领取",
                    wait_time=3,
                    auto_raise=False
            ):
                continue
            self.config.set_task_exe_prog(self.task_name, "领取情报站活跃度", True)
            return False

        elif not self.config.get_task_exe_prog(self.task_name, "40活跃度奖励已领取", False):
            self.handle_activity_reward(40)
            return False
        elif not self.config.get_task_exe_prog(self.task_name, "60活跃度奖励已领取", False):
            self.handle_activity_reward(60)
            return False
        elif not self.config.get_task_exe_prog(self.task_name, "100活跃度奖励已领取", False):
            self.handle_activity_reward(100)
            return False
        self.operationer.click_and_wait("X")
        self.reset_task_exe_proc()
        self.update_next_execute_time()
        return True

    @TransitionOn("福利站-每日签到")
    def _(self):
        self.operationer.click_and_wait("立即签到", wait_time=5)
        self.config.set_task_exe_prog(self.task_name, "情报站签到", True)
        return False

    @TransitionOn("福利站-签到成功")
    def _(self):
        self.operationer.click_and_wait("我知道了", wait_time=3)
        return False

    @TransitionOn("福利站-活跃奖励-获得奖励")
    def _(self):
        self.operationer.click_and_wait("我知道了", wait_time=3)
        return False

    @TransitionOn("福利站-100活跃奖励-确认")
    def _(self):
        self.operationer.click_and_wait("确定", wait_time=3)
        return False

    @TransitionOn("福利站-40活跃奖励-抽取中")
    def _(self):
        QThread.msleep(1000)
        return False

    @TransitionOn("情报站-文章详情")
    def _(self):
        self.operationer.click_and_wait("后退")
        return False

    @TransitionOn("情报站-动态详情")
    def _(self):
        self.operationer.click_and_wait("后退")
        return False

    def handle_activity_reward(self, num):
        self.logger.info(f"领取{num}活跃度奖励")
        if self.operationer.click_and_wait(
                f"活跃度任务-{num}",
                auto_raise=False,
                wait_time=0
        ):
            if self.operationer.detect_element(
                    "活跃度任务-今日已领取过该奖励",
                    wait_time=2,
                    auto_raise=False
            ):
                self.logger.warning(f"{num}活跃度奖励已领取")
            self.config.set_task_exe_prog(self.task_name, f"{num}活跃度奖励已领取", True)
        else:
            self.logger.warning(f"{num}活跃度奖励领取失败，活跃度未达到要求")

    def reset_task_exe_proc(self) -> None:
        flag = all([
            self.config.get_task_exe_prog(self.task_name, f"40活跃度奖励已领取", False),
            self.config.get_task_exe_prog(self.task_name, f"60活跃度奖励已领取", False),
            self.config.get_task_exe_prog(self.task_name, f"100活跃度奖励已领取", False)
        ])

        self.logger.debug("所有活跃度奖励已领取" if flag else "所有活跃度奖励已领取")

        self.config.set_task_exe_prog(self.task_name, f"浏览卷轴", False)
        self.config.set_task_exe_prog(self.task_name, f"浏览村口", False)
        self.config.set_task_exe_prog(self.task_name, f"点赞帖子", 0)
        self.config.set_task_exe_prog(self.task_name, f"浏览忍者站", False)
        self.config.set_task_exe_prog(self.task_name, f"情报站签到", False)
        self.config.set_task_exe_prog(self.task_name, f"浏览金币助手", False)
        self.config.set_task_exe_prog(self.task_name, f"领取情报站活跃度", False)
        self.config.set_task_exe_prog(self.task_name, f"40活跃度奖励已领取", False)
        self.config.set_task_exe_prog(self.task_name, f"60活跃度奖励已领取", False)
        self.config.set_task_exe_prog(self.task_name, f"100活跃度奖励已领取", False)


