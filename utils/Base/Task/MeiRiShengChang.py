from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Base.Enums import KEY_INDEX
from utils.Base.Exceptions import StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class MeiRiShengChang(BaseTask):
    source_scene = "忍术对战-单人模式"
    task_max_duration = timedelta(hours=2)

    @TransitionOn()
    def _(self):
        self.logger.info("领取所有待领取的决斗任务宝箱")
        self.operationer.click_and_wait("决斗任务")
        self.collect_and_recover()

        while self.operationer.search_and_detect(
                [
                    self.operationer.current_scene.elements.get("宝箱-未达成")
                ],
                [
                    {'swipe':
                        {"start_coordinate": [1095, 618], "end_coordinate": [1095, 167],
                            "duration": 0.7}}
                ],
                max_attempts=1,
                bool_debug=True
        ):
            self.operationer.click_and_wait("X")
            self.fight()
            self.operationer.click_and_wait("决斗任务")
            self.collect_and_recover()
        self.operationer.click_and_wait("X")
        self.logger.info("没有未达成的宝箱，结束执行")
        self.update_next_execute_time()
        return True

    def collect_and_recover(self):
        """
        领取战斗宝箱以及追回，自动处理道具不足的情况
        """
        while self.operationer.search_and_click(
                [
                    "宝箱-领取"
                ],
                [],
                max_attempts=1,
        ):
            continue
        # 检测有无可追回宝箱
        if self.operationer.click_and_wait(
                "宝箱-追回",
                auto_raise=False
        ):
            self.operationer.click_and_wait("宝箱-追回-追回", wait_time=0)
            if self.operationer.detect_element("追回-道具不足", auto_raise=False):
                self.operationer.click_and_wait("追回-X")

    def fight(self):
        """
        通用的刷决斗场函数，周胜赛季胜等等都可以使用
        """
        # 进入战斗
        self.operationer.click_and_wait("开战")
        self.operationer.click_and_wait("开战", auto_raise=False)
        flag = self.operationer.search_and_detect(
            [
                self.operationer.current_scene.elements.get("60"),
                self.operationer.current_scene.elements.get("你的对手离开了游戏")
            ],
            [
                {'click': "你的对手离开了游戏-确定"}
            ],
            search_max_time=100,
        )
        if not flag:
            raise StepFailedError("开始战斗超时")
        else:
            if flag == 2:
                self.logger.warning("对手退出游戏，即将返回[忍术对战-单人模式]")
                if not self.operationer.search_and_detect(
                        [
                            self.scene_graph.scenes.get("忍术对战-单人模式")
                        ],
                        [
                            {'click': "空白点"},
                            {'click': "你的对手离开了游戏-确定"}
                        ],
                        search_max_time=30
                ):
                    raise StepFailedError("战斗结束后无法退回[忍术对战-单人模式]")
            elif flag == 1:
                self.logger.info("倒计时60s出现，连点执行中...")
                # 使用连点器，结束的标志定为举报反馈
                self.operationer.auto_cycle_actioner(
                    [
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.BasicAttack]),
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.FirstSkill]),
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.SecondSkill]),
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.UltimateSkill]),
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.SecretScroll]),
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.Summon]),
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.Substitution])
                    ],
                    stop_conditions=[
                        self.operationer.current_scene.elements.get("你的对手离开了游戏"),
                        self.operationer.current_scene.elements.get("举报反馈")
                    ],
                    max_workers=7
                )
                self.logger.info("对局结束，返回[单人模式-首页]")
        # 先回到单人模式首页
        if not self.operationer.search_and_detect(
                [
                    self.scene_graph.scenes.get("忍术对战-单人模式")
                ],
                [
                    {'click': "空白点"},
                    {'click': "你的对手离开了游戏-确定"}
                ],
                search_max_time=30
        ):
            raise StepFailedError("战斗结束后无法退回[忍术对战-单人模式]")

    def update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
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
                    return False, None
                self.next_execute_time = current_time + delta

            case _:
                self.logger.warning(f"请检查update_next_execute_time传入的参数：flag={flag},delta={delta}")
                return False, None

        self.logger.info(f"下次执行时间为：{self.next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
        self.config.set_task_config(self.task_name, "下次执行时间", int(self.next_execute_time.timestamp()))
        return True, self.next_execute_time
