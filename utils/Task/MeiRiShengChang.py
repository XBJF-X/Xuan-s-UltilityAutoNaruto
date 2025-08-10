from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.KeyMapConfiguration import KEY_INDEX
from utils.Task.BaseTask import BaseTask


class MeiRiShengChang(BaseTask):
    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        self.logger.info("进入[决斗场-首页]")
        if not self.search_and_click(
                [
                    {"type": "ELEMENT", "name": "主场景-决斗场"}
                ],
                [
                    {
                        "swipe": {
                            "start_coordinate": [1345, 340],
                            "end_coordinate": [462, 340],
                            "duration": 1
                        }
                    }
                ],
                max_attempts=2
        ):
            if not self.search_and_click(
                    [
                        {"type": "ELEMENT", "name": "主场景-决斗场"}
                    ],
                    [
                        {
                            "swipe": {
                                "start_coordinate": [462, 86],
                                "end_coordinate": [1345, 86],
                                "duration": 1
                            }
                        }
                    ],
                    max_attempts=2
            ):
                raise self.StepFailedError("无法进入[决斗场]")
        self.detect_and_wait({'type': "SCENE", 'name': "决斗场-首页"})
        self.logger.info("进入[决斗场-忍术对战-单人模式]")
        self.click_and_wait({'type': "ELEMENT", 'name': "决斗场-忍术对战"})
        self.detect_and_wait({'type': "SCENE", 'name': "决斗场-忍术对战-单人模式"})
        self.logger.info("查看[决斗场-忍术对战-单人模式-决斗任务]")
        self.click_and_wait({'type': "ELEMENT", 'name': "决斗场-忍术对战-单人模式-决斗任务"})
        self.detect_and_wait({'type': "SCENE", 'name': "决斗场-忍术对战-单人模式-决斗任务"})

        self.logger.info("领取所有待领取的决斗任务宝箱")
        while self.search_and_click(
                [
                    {'type': "ELEMENT", 'name': "决斗任务-宝箱-待领取"}
                ],
                [
                    {'swipe':
                        {"start_coordinate": [1095, 618], "end_coordinate": [1095, 167], "duration": 1}
                    }
                ],
                max_attempts=1,
        ):
            continue

        # 假如存在未达成的宝箱，则挂周胜
        while self.search_and_detect(
                [
                    {'type': "ELEMENT", 'name': "决斗任务-宝箱-未达成"}
                ],
                [
                    {'swipe':
                        {"start_coordinate": [1095, 618], "end_coordinate": [1095, 167], "duration": 1}}
                ],
                max_attempts=1,
                bool_debug=True
        ):
            self.logger.info("存在未达成的每日胜场任务，继续执行")
            self.click_and_wait({'type': "COORDINATE", 'coordinate': [1523, 45]})
            self.fight()
            self.logger.info("查看[决斗场-忍术对战-单人模式-决斗任务]")
            self.click_and_wait(
                {'type': "ELEMENT", 'name': "决斗场-忍术对战-单人模式-决斗任务"},
                max_time=3
            )
            self.detect_and_wait(
                {'type': "SCENE", 'name': "决斗场-忍术对战-单人模式-决斗任务"},
                max_time=5
            )
            self.logger.info("领取所有待领取的决斗任务宝箱")
            while self.search_and_click(
                    [
                        {'type': "ELEMENT", 'name': "决斗任务-宝箱-待领取"}
                    ],
                    [
                        {'swipe':
                            {"start_coordinate": [1095, 618], "end_coordinate": [1095, 167],
                                "duration": 1}
                        }
                    ],
                    max_attempts=1,
            ):
                continue

        self.logger.info("每日胜场宝箱已领完")
        self.click_and_wait({'type': "COORDINATE", 'coordinate': [1523, 45]})
        self._update_next_execute_time()

    def fight(self):
        """
        通用的刷决斗场函数，周胜赛季胜等等都可以使用
        """
        # 进入战斗
        self.click_and_wait({'type': "ELEMENT", 'name': "决斗场-忍术对战-单人模式-开战"})
        self.click_and_wait(
            {'type': "ELEMENT", 'name': "决斗场-忍术对战-单人模式-开战"},
            auto_raise=False
        )
        flag = self.search_and_detect(
            [
                {'type': "ELEMENT", 'name': "决斗场-60"},
                {"type": "ELEMENT",
                    "name": "决斗场-忍术对战-单人模式-你的对手离开了游戏"},
            ],
            [
                {'click': {'type': "COORDINATE", 'coordinate': [800, 569]}}
            ],
            search_max_time=100,
        )
        if not flag:
            raise self.StepFailedError("开始战斗超时")
        else:
            if flag == 2:
                self.logger.warning("对手退出游戏，即将返回[忍术对战-单人模式]")
                if not self.search_and_detect(
                        [
                            {'type': "SCENE", 'name': "决斗场-忍术对战-单人模式"}
                        ],
                        [
                            {'click': {'type': "COORDINATE", 'coordinate': [800, 745]}},
                            {'click': {'type': "COORDINATE", 'coordinate': [800, 569]}}
                        ],
                        search_max_time=30
                ):
                    raise self.StepFailedError("战斗结束后无法退回[忍术对战-单人模式]")
            elif flag == 1:
                self.logger.info("倒计时60s出现，连点执行中...")
                # 使用连点器，结束的标志定为举报反馈
                self.auto_cycle_actioner(
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
                        {"type": "ELEMENT", "name": "决斗场-举报反馈"},
                        {"type": "ELEMENT", "name": "决斗场-忍术对战-单人模式-你的对手离开了游戏"},
                    ],
                    max_workers=7
                )
                self.logger.info("对局结束，返回[单人模式-首页]")
        # 先回到单人模式首页
        if not self.search_and_detect(
                [
                    {'type': "SCENE", 'name': "决斗场-忍术对战-单人模式"}
                ],
                [
                    {'click': {'type': "COORDINATE", 'coordinate': [800, 745]}},
                    {'click': {'type': "COORDINATE", 'coordinate': [800, 569]}}
                ],
                search_max_time=30
        ):
            raise self.StepFailedError("战斗结束后无法退回[忍术对战-单人模式]")

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