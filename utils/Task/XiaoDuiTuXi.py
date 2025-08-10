from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Task.BaseTask import BaseTask


class XiaoDuiTuXi(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        self.logger.info("进入奖励界面")
        # 点击奖励图标
        self.click_and_wait({"type": "ELEMENT", "name": "主场景-奖励"})
        # 确认奖励界面出现
        self.detect_and_wait({"type": "SCENE", "name": "奖励"})
        self.logger.info("跳转至[小队突袭]")
        # 点击小队突袭-立刻前往
        if not self.search_and_click(
                [
                    {"type": "ELEMENT", "name": "小队突袭-立刻前往"}
                ],
                [
                    {
                        "swipe": {
                            "start_coordinate": [1506, 340],
                            "end_coordinate": [340, 340],
                            "duration": 1
                        }
                    }
                ],
                max_attempts=3
        ):
            self._update_next_execute_time()
            raise self.EndEarly("无法跳转至[小队突袭]，可能已经完成")
        # 确认小队突袭界面出现
        self.detect_and_wait({"type": "SCENE", "name": "小队突袭"})
        self.logger.info("进入[组织助战]")
        # 点击小队突袭-组织助战
        self.click_and_wait(
            {"type": "ELEMENT", "name": "小队突袭-组织助战"},
            wait_time=2
        )

        # 确认小队突袭-组织助战界面
        self.detect_and_wait({"type": "SCENE", "name": "小队突袭-组织助战"})

        if self.detect_and_wait(
                {"type": "ELEMENT", "name": "小队突袭-今日收益次数已达上限"},
                auto_raise=False
        ):
            # Esc
            self.esc()
            # 点击小队突袭-离开队伍-确定
            self.click_and_wait({"type": "ELEMENT", "name": "小队突袭-离开队伍-确定"})
            self._update_next_execute_time()
            raise self.EndEarly("小队突袭次数已用尽")
        self.logger.info("进入[我的助战]")
        # 点击我的助战
        self.click_and_wait({"type": "ELEMENT", "name": "小队突袭-组织助战-我的助战"})
        self.logger.info("领取助战奖励")
        # 点击领取
        if self.click_and_wait(
                {"type": "ELEMENT", "name": "小队突袭-组织助战-我的助战-领取"},
                auto_raise=False
        ):
            self.logger.info("助战奖励领取成功")

        self.logger.info("返回[组织助战]")
        # 返回上级小队突袭-组织助战界面
        if not self.esc():
            raise self.StepFailedError("返回[组织助战]失败")
        if self.data.get("四倍奖励勾选"):
            four_reward_times = self.data.get("四倍奖励次数")
        else:
            four_reward_times = 0
        self.logger.info(f"收取四倍奖励次数：{four_reward_times}")
        if four_reward_times > 0:
            self.logger.info("勾选四倍奖励")
            if not self.detect_and_wait(
                    {"type": "ELEMENT", "name": "小队突袭-组织助战-四倍奖励-选中"},
                    auto_raise=False
            ):
                if not self.click_and_wait(
                        {"type": "ELEMENT", "name": "小队突袭-组织助战-四倍奖励-未选中"},
                        auto_raise=False
                ):
                    raise self.StepFailedError("小队突袭四倍奖励未选中")

        # 先看看能不能扫荡
        self._handle_sweep_through()
        # 不能就出站
        self.logger.info("出战")
        # 点击出战
        self.click_and_wait(
            {"type": "ELEMENT", "name": "小队突袭-组织助战-出战"},
            wait_time=4
        )
        # 可能有二级密码
        if self.pass_secondary_password():
            self.logger.info("再次出站")
            # 返回True说明检测到了二级密码的弹窗，则需要再次点击出战
            self.click_and_wait({
                "type": "ELEMENT", "name": "小队突袭-组织助战-出战"},
                wait_time=5
            )
        self.logger.info("进入自动战斗")
        # 使用连点器过小队突袭
        self.auto_cycle_actioner([
            ("CLICK", (800, 750))
        ],
            stop_conditions=[
                {"type": "SCENE", "name": "小队突袭"}
            ]
        )
        four_reward_times -= 1
        # 等待战斗结束，回到小队突袭界面
        # 确认回到小队突袭界面
        self.detect_and_wait({"type": "SCENE", "name": "小队突袭"})
        self.logger.info("战斗结束")

        if self.detect_and_wait(
                {"type": "ELEMENT", "name": "小队突袭-今日收益次数已达上限"},
                auto_raise=False
        ):
            self._update_next_execute_time()
            raise self.EndEarly("小队突袭次数已用尽")

        if four_reward_times > 0:
            self.logger.info("勾选四倍奖励")
            if not self.detect_and_wait(
                    {"type": "ELEMENT", "name": "小队突袭-组织助战-四倍奖励-选中"},
                    auto_raise=False
            ):
                if not self.click_and_wait(
                        {"type": "ELEMENT", "name": "小队突袭-组织助战-四倍奖励-未选中"},
                        auto_raise=False
                ):
                    raise self.StepFailedError("小队突袭四倍奖励未选中")
        # 再看看有没有扫荡
        self._handle_sweep_through()
        # 没有的话老老实实再打一局

        self.logger.info("进入[组织助战]")
        # 点击小队突袭-组织助战
        self.click_and_wait(
            {"type": "ELEMENT", "name": "小队突袭-组织助战"},
            wait_time=3
        )
        # 确认小队突袭-组织助战界面
        self.detect_and_wait(
            {"type": "SCENE", "name": "小队突袭-组织助战"},
            wait_time=3
        )
        self.logger.info("出战")
        # 点击出战
        self.click_and_wait(
            {"type": "ELEMENT", "name": "小队突袭-组织助战-出战"},
            wait_time=5
        )
        # 使用连点器过小队突袭
        self.auto_cycle_actioner([
            ("CLICK", (800, 750))
        ],
            stop_conditions=[
                {"type": "SCENE", "name": "小队突袭"}
            ]
        )
        # 确认小队突袭界面
        self.detect_and_wait({"type": "SCENE", "name": "小队突袭"})
        self.logger.info("战斗结束")
        self._update_next_execute_time()

    def _handle_sweep_through(self):
        # 假如有扫荡按钮的话，就点击并直接回退，因为扫荡按钮代表只用打一次
        if self.click_and_wait(
                {"type": "ELEMENT", "name": "小队突袭-扫荡"},
                auto_raise=False
        ):
            self.logger.info("存在扫荡按钮，有超影并且已经打过一次")
            # 直接开始点击，点到小队突袭界面出现
            self.logger.info("进入自动战斗")
            # 使用连点器过小队突袭
            self.auto_cycle_actioner(
                [
                    ("CLICK", (800, 750))
                ],
                stop_conditions=[
                    {"type": "SCENE", "name": "小队突袭"}
                ]
            )
            # 确认小队突袭界面
            self.detect_and_wait({"type": "SCENE", "name": "小队突袭"})
            self.logger.info("战斗结束")
            raise self.EndEarly("已扫荡完成，提前结束")

    def _update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        match flag:

            case 0:  # 创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                next_exec_ts = self.data.get('下次执行时间')
                if next_exec_ts == 0:
                    # 若初始值为0，设置为当前UTC时间（或其他合理时间）
                    self.next_execute_time = datetime.now(ZoneInfo("Asia/Shanghai"))
                else:
                    # 从时间戳转换为datetime对象（指定UTC时区避免歧义）
                    self.next_execute_time = datetime.fromtimestamp(next_exec_ts, tz=ZoneInfo("Asia/Shanghai"))

            case 1:  # 正常执行完毕，更新为下次执行的时间
                next_day = current_time + timedelta(days=1)
                # 新建时间时指定时区（与current_time一致）
                self.next_execute_time = datetime(
                    next_day.year, next_day.month, next_day.day, 5, 0,
                    tzinfo=china_tz  # 关键：添加时区信息
                )

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                self.next_execute_time = datetime.now(ZoneInfo("Asia/Shanghai"))

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
