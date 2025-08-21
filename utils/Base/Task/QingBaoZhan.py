from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class QingBaoZhan(BaseTask):
    source_scene = "情报站-首页"
    task_max_duration = timedelta(minutes=5)
    juanzhou_browsed = False
    cunkou_browsed = False
    renzhezhan_browsed = False

    @TransitionOn()
    def _(self):
        if not self.juanzhou_browsed:
            self.operationer.next_scene = "情报站-卷轴"
            return False
        elif not self.cunkou_browsed:
            self.operationer.next_scene = "情报站-村口"
            return False
        elif not self.renzhezhan_browsed:
            self.operationer.next_scene = "情报站-忍者站"
            return False
        self.operationer.next_scene = "福利站"
        return False

    @TransitionOn("情报站-卷轴")
    def _(self):
        if not self.juanzhou_browsed:
            self.juanzhou_browsed = True
            self.operationer.next_scene = "情报站-村口"
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
                        self.operationer.current_scene.elements.get("点赞-未点"),
                        self.operationer.current_scene.elements.get("点赞-已点")
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
                    self.operationer.click_and_wait(
                        "点赞-未点",
                        wait_time=2
                    )
                    love_sum += 1
                    self.logger.info(f"已点赞❤帖子 {love_sum} 个")

                elif flag == 2:
                    self.logger.debug("发现已被点赞帖子")
                    self.operationer.click_and_wait(
                        "点赞-已点",
                        wait_time=2
                    )
                    self.operationer.click_and_wait(
                        "点赞-未点",
                        wait_time=2
                    )
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
                        duration=1
                    )
            self.cunkou_browsed = True
            self.operationer.next_scene = "情报站-首页"
            return False

    @TransitionOn("情报站-忍者站")
    def _(self):
        if not self.renzhezhan_browsed:
            self.renzhezhan_browsed = True
            self.operationer.next_scene = "福利站"
            return False

    @TransitionOn("福利站")
    def _(self):
        self.logger.info("福利站签到")
        # 点击福利站-一键签到
        if self.operationer.click_and_wait(
                "一键签到",
                wait_time=3,
                auto_raise=False
        ):
            self.logger.info("未自动弹出窗口，点击一键签到")
            self.operationer.click_and_wait(
                "立即签到",
                wait_time=3
            )
            # 签到成功，点击我知道了
            self.operationer.click_and_wait(
                "我知道了",
                wait_time=3
            )
        else:
            self.logger.warning("手动点击一键签到失败，可能已经签到过")
        # 确认福利站页面已出现
        self.operationer.detect_scene(
            "福利站",
            wait_time=2,
            max_time=4
        )
        self.logger.info("[福利站]页面出现")
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
                max_attempts=2
        ):
            self.logger.warning("进入金币助手失败，可能导致活跃度不足")
            self.operationer.swipe_and_wait((600, 290), (600, 850), duration=1)
            self.operationer.swipe_and_wait((600, 290), (600, 850), duration=1)
        else:
            # 一段时间后，直接输入返回指令（因为竖屏不好识别）
            self.logger.info("返回福利站")
            self.operationer.press_key("back", wait_time=7)
        self.logger.info("领取活跃度奖励")
        # 点击所有的领取按钮
        while self.operationer.click_and_wait(
                "活跃度任务-领取",
                wait_time=3,
                auto_raise=False
        ):
            continue

        # 点击40活跃度奖励
        self.handle_40_activity_reward()
        # 点击60活跃度奖励
        self.handle_60_activity_reward()
        # 点击100活跃度奖励
        self.handle_100_activity_reward()
        self.operationer.click_and_wait("X")
        self._update_next_execute_time()
        return True

    def handle_40_activity_reward(self):
        self.logger.info("领取40活跃度奖励")
        if self.operationer.click_and_wait(
                "活跃度任务-40",
                auto_raise=False
        ):
            if self.operationer.detect_element(
                    "活跃度任务-今日已领取过该奖励",
                    wait_time=3,
                    auto_raise=False
            ):
                self.logger.warning("40活跃度奖励已领取")
                return True

            # 点击40活跃度奖励-确定
            if not self.operationer.click_and_wait(
                    "活跃度任务-40-确定",
                    wait_time=2,
                    auto_raise=False
            ):
                self.logger.error("点击[活跃度-40-确定]失败")
                return False

            # 等待转盘结束之后点击 转盘抽奖-我知道了
            while not self.operationer.click_and_wait(
                    "活跃度任务-40-我知道了",
                    wait_time=1,
                    auto_raise=False
            ):
                continue
            self.logger.info("40活跃度奖励领取完成")
            return True
        self.logger.warning("40活跃度奖励领取失败，活跃度未达到要求")
        return False

    def handle_60_activity_reward(self):
        self.logger.info("领取60活跃度奖励")
        if self.operationer.click_and_wait(
                "活跃度任务-60",
                auto_raise=False
        ):
            if self.operationer.detect_element(
                    "活跃度任务-今日已领取过该奖励",
                    wait_time=3,
                    auto_raise=False
            ):
                self.logger.info("60活跃度奖励已领取")
                return True
            # 点击我知道了
            if not self.operationer.click_and_wait(
                    "活跃度任务-60-我知道了",
                    auto_raise=False
            ):
                self.logger.error("点击[活跃度-60-我知道了]失败")
                return False
            self.logger.info("60活跃度奖励领取完成")
            return True
        self.logger.warning("60活跃度奖励领取失败，活跃度未达到要求")
        return False

    def handle_100_activity_reward(self):
        self.logger.info("领取100活跃度奖励")
        if self.operationer.click_and_wait(
                "活跃度任务-100",
                auto_raise=False
        ):
            if self.operationer.detect_element(
                    "活跃度任务-今日已领取过该奖励",
                    auto_raise=False
            ):
                self.logger.info("100活跃度奖励已领取")
                return True
            # 点击确定
            if not self.operationer.click_and_wait(
                    "活跃度任务-100-确定",
                    auto_raise=False
            ):
                self.logger.error("点击[活跃度-100-确定]失败")
                return False
            # 点击我知道了
            self.operationer.click_and_wait("活跃度任务-100-我知道了")
            self.logger.info("100活跃度奖励领取完成")
            return True
        self.logger.warning("100活跃度奖励领取失败，活跃度未达到要求")
        return False

    def _update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        match flag:

            case 0:  # 创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                next_exec_ts = self.data.get('下次执行时间')
                if next_exec_ts == 0:
                    # 若初始值为0，设置为当前UTC时间（或其他合理时间）
                    self.next_execute_time = datetime.now(china_tz)
                else:
                    # 从时间戳转换为datetime对象（指定UTC时区避免歧义）
                    self.next_execute_time = datetime.fromtimestamp(next_exec_ts, tz=china_tz)

            case 1:  # 正常执行完毕，更新为下次执行的时间
                next_day = current_time + timedelta(days=1)
                # 新建时间时指定时区（与current_time一致）
                self.next_execute_time = datetime(
                    next_day.year, next_day.month, next_day.day, 5, 0,
                    tzinfo=china_tz  # 关键：添加时区信息
                )

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                self.next_execute_time = datetime.now(china_tz)

            case 3:  # 把执行时间推迟delta时间，要求 delta!=None
                if delta is None:
                    self.logger.warning(f"update_next_execute_time传入的delta为空")
                    return
                self.next_execute_time = current_time + delta

            case _:
                self.logger.warning(f"请检查update_next_execute_time传入的参数：flag={flag},delta={delta}")
                return

        self.logger.info(f"下次执行时间为：{self.next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
        self.config.set_task_config(self.task_name, "下次执行时间", int(self.next_execute_time.timestamp()))
