from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from PySide6.QtCore import QThread

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class QingBaoZhan(BaseTask):
    source_scene = "情报站-首页"
    task_max_duration = timedelta(minutes=5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.juanzhou_browsed = False
        self.cunkou_browsed = False
        self.renzhezhan_browsed = False
        self.qiandao_done = False
        self.jinbizhushou_browsed_done = False
        self.activity_collected_done = False
        self.activity_reward_40_done = False
        self.activity_reward_60_done = False
        self.activity_reward_100_done = False

    @TransitionOn()
    def _(self):
        if not self.juanzhou_browsed:
            self.operationer.click_and_wait("卷轴")
            return False
        elif not self.cunkou_browsed:
            self.operationer.click_and_wait("村口")
            return False
        elif not self.renzhezhan_browsed:
            self.operationer.click_and_wait("忍者站")
            return False
        self.operationer.click_and_wait("福利站")
        return False

    @TransitionOn("情报站-卷轴")
    def _(self):
        if not self.juanzhou_browsed:
            self.juanzhou_browsed = True
        self.operationer.click_and_wait("村口")
        return False

    @TransitionOn("情报站-村口")
    def _(self):
        if not self.cunkou_browsed:
            self.logger.info("开始点赞帖子")
            love_sum = 0
            retry_time = 0
            while love_sum < 3:
                retry_time += 1
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
                    self.logger.info(f"已点赞❤帖子 {love_sum} 个")

                elif flag == 2:
                    self.logger.debug("发现已被点赞帖子")
                    self.operationer.click_and_wait("点赞-已点")
                    self.operationer.click_and_wait("点赞-未点")
                    love_sum += 1
                    self.logger.info(f"已点赞❤帖子 {love_sum} 个")

                if retry_time > 30:
                    self.logger.warning("点赞帖子三次失败，可能导致活跃度不足100")
                    break
                if love_sum < 3:
                    self.operationer.swipe_and_wait(
                        (760, 870),
                        (760, 80),
                        wait_time=0,
                        duration=0.7
                    )
            self.cunkou_browsed = True
        self.operationer.click_and_wait("首页")
        return False

    @TransitionOn("忍者站")
    def _(self):
        if not self.renzhezhan_browsed:
            self.renzhezhan_browsed = True
        self.operationer.click_and_wait("推荐")
        return False

    @TransitionOn("福利站")
    def _(self):
        if not self.qiandao_done:
            self.logger.info("福利站签到")
            # 点击一键签到
            if not self.operationer.click_and_wait(
                    "一键签到",
                    auto_raise=False
            ):
                self.qiandao_done = True
            return False

        elif not self.jinbizhushou_browsed_done:
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
                self.jinbizhushou_browsed_done = True
            return False
        elif not self.activity_collected_done:
            self.logger.info("领取活跃度奖励")
            # 点击所有的领取按钮
            while self.operationer.click_and_wait(
                    "活跃度任务-领取",
                    wait_time=3,
                    auto_raise=False
            ):
                continue
            self.activity_collected_done = True
            return False
        elif not self.activity_reward_40_done:
            self.handle_activity_reward(40)
            return False
        elif not self.activity_reward_60_done:
            self.handle_activity_reward(60)
            return False
        elif not self.activity_reward_100_done:
            self.handle_activity_reward(100)
            return False
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        return True

    @TransitionOn("福利站-每日签到")
    def _(self):
        self.operationer.click_and_wait("立即签到", wait_time=5)
        self.qiandao_done = True
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
        else:
            self.logger.warning(f"{num}活跃度奖励领取失败，活跃度未达到要求")
        setattr(self, f"activity_reward_{num}_done", True)

