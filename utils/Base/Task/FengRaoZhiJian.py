from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Base.Enums import KEY_INDEX
from utils.Base.Exceptions import EndEarly, StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class FengRaoZhiJian(BaseTask):
    source_scene = "丰饶之间"
    task_max_duration = timedelta(minutes=10)

    @TransitionOn("丰饶之间")
    def _(self):
        if self.operationer.detect_element(
                "今日已完成挑战",
                auto_raise=False
        ):
            self._update_next_execute_time()
            raise EndEarly("已完成挑战，提前结束执行")
        # 先看看能不能用超影直接过
        if self.operationer.click_and_wait(
                "一键完成",
                auto_raise=False
        ):
            # 点击丰饶之间-超影免费
            if self.operationer.click_and_wait(
                    "超影免费",
                    wait_time=3,
                    auto_raise=False
            ):
                self.logger.info("领取丰饶之间奖励")
                # 使用连点器过丰饶之间
                self.operationer.auto_cycle_actioner(
                    [
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.BasicAttack]),
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.FirstSkill]),
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.SecondSkill]),
                        ("CLICK", self.config.get_config("键位")[KEY_INDEX.UltimateSkill]),
                    ],
                    stop_conditions=[
                        self.scene_graph.scenes.get("丰饶之间")
                    ],
                    max_workers=4
                )
                self._update_next_execute_time()
                raise EndEarly("免费完成，提前结束执行")
            else:
                self.logger.info("没有超影，返回[丰饶之间]界面")
                # 随便点下退出一键完成界面
                self.operationer.click_and_wait("X")
        else:
            self.logger.warning("点击一键完成失败")

        # 点击丰饶之间-挑战
        self.operationer.click_and_wait(
            "挑战",
            wait_time=4
        )
        self.logger.info("无法免费完成，开始自动挑战")
        # 使用连点器过丰饶之间
        self.operationer.auto_cycle_actioner(
            [
                ("CLICK", self.config.get_config("键位")[KEY_INDEX.BasicAttack]),
                ("CLICK", self.config.get_config("键位")[KEY_INDEX.FirstSkill]),
                ("CLICK", self.config.get_config("键位")[KEY_INDEX.SecondSkill]),
                ("CLICK", self.config.get_config("键位")[KEY_INDEX.UltimateSkill]),
            ],
            stop_conditions=[
                self.operationer.current_scene.elements.get("点击任意位置关闭界面")
            ],
            max_workers=4
        )
        self.logger.info("挑战[丰饶之间]成功")

        if not self.operationer.search_and_detect(
                [
                    self.operationer.current_scene
                ],
                [
                    {'click': "空白点"}
                ],
                search_max_time=180
        ):
            raise StepFailedError("退出[丰饶之间]失败")
        self._update_next_execute_time()

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
