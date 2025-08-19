from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Enums import KEY_INDEX
from utils.Base.Exceptions import StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class MiJingTanXian(BaseTask):
    source_scene = "秘境探险-匹配"
    task_max_duration = timedelta(hours=2)

    @TransitionOn()
    def _(self):
        self.mijingtanxian_implement()
        self._update_next_execute_time()
        return True

    def mijingtanxian_implement(self):
        # 剩余挑战券!=0的时候
        while not self.operationer.detect_element(
                "剩余挑战券-0",
                max_time=0.7,
                auto_raise=False
        ):
            self.logger.info("挑战券不为0，继续出战")
            # 点击出战
            self.operationer.click_and_wait("出战")
            if self.operationer.click_and_wait(
                    "出战-继续挑战-确定",
                    wait_time=3,
                    auto_raise=False
            ):
                self.logger.debug("确认出战")
            # 等待检测到[落岩秘境]，如果检测到别的就退
            flag = self.operationer.search_and_detect(
                [
                    self.operationer.current_scene.elements.get("落岩秘境"),
                    self.operationer.current_scene.elements.get("阴阳秘境"),
                    self.operationer.current_scene.elements.get("雷霆秘境"),
                    self.operationer.current_scene.elements.get("烈炎秘境"),
                    self.operationer.current_scene.elements.get("水牢秘境"),
                    self.operationer.current_scene.elements.get("毒风秘境"),
                    self.operationer.current_scene.elements.get("罡体秘境"),
                ],
                [],
                search_max_time=60,
                once_max_time=0.05,
                wait_time=2.0
            )
            if flag == 1:
                self.logger.info("检测到落岩秘境，开始战斗")
                # 检测到[落岩秘境]，开始走两步开始连点，停止条件为[胜利图标出现]
                joystick_coordinate = self.config.get_config("键位")[KEY_INDEX.JoyStick]
                self.operationer.long_press(joystick_coordinate[0] + 30, joystick_coordinate[1], 1.5)
                flag = self.operationer.auto_cycle_actioner(
                    [
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.BasicAttack]),
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.FirstSkill]),
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.SecondSkill]),
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.UltimateSkill]),
                    ],
                    stop_conditions=[
                        self.operationer.current_scene.elements.get("胜利"),
                        self.operationer.current_scene.elements.get("返回")
                    ],
                    max_workers=4,
                    max_time=600,
                    bool_debug=True
                )
                if flag == 0:
                    raise StepFailedError("落岩秘境未正常通过")
                elif flag == -1:
                    raise StepFailedError("落岩秘境通过超时")
                elif flag == 1:
                    if not self.operationer.search_and_detect(
                            [
                                self.scene_graph.scenes.get("秘境探险-匹配")
                            ],
                            [
                                {'click': "空白点"},
                                {'click': "返回"},
                            ],
                            search_max_time=60,
                            bool_debug=True
                    ):
                        raise StepFailedError("秘境胜利[无奖励]，回退匹配界面失败")
                elif flag == 2:
                    self.operationer.click_and_wait(
                        "返回",
                        max_time=3
                    )
                    if not self.operationer.search_and_detect(
                            [
                                self.scene_graph.scenes.get("秘境探险-匹配")
                            ],
                            [
                                {'click': "空白点"},
                                {'click': "返回"},
                            ],
                            search_max_time=60,
                            once_max_time=1,
                            bool_debug=True
                    ):
                        raise StepFailedError("秘境胜利，回退匹配界面失败")

            else:
                self.logger.info("不是落岩秘境，退出战斗")
                # 点暂停，退出，确认
                self.operationer.click_and_wait("暂停")
                self.operationer.click_and_wait("暂停-退出战斗")
                self.operationer.click_and_wait("暂停-退出战斗-确定")

            # 等待[秘境探险-匹配]界面出现，继续检测挑战券数量
            self.operationer.detect_scene(
                "秘境探险-匹配",
                max_time=30
            )
        self.logger.info("挑战券清空，结束执行")

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