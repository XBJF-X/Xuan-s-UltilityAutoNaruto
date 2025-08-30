from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Enums import KEY_INDEX
from utils.Base.Exceptions import StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class BenFuYaoSaiZhan(BaseTask):
    source_scene = "X之要塞"
    task_max_duration = timedelta(minutes=30)

    @TransitionOn()
    def _(self):
        joystick = self.config.get_config("键位")[KEY_INDEX.JoyStick]
        fight_sum = 0

        while datetime.now(tz=ZoneInfo("Asia/Shanghai")) < self.dead_line:
            while not self.operationer.detect_element("正在寻找旗鼓相当的对手", max_time=0.5, auto_raise=False):
                self.operationer.long_press(joystick[0] + 30, joystick[1], 3)
            self._handle_fight()
            fight_sum += 1
        self.logger.info(f"本服要塞战结束，共战斗 {fight_sum} 次")
        return True

    def _handle_fight(self):
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
                self.logger.warning("对手退出游戏，即将返回[X之要塞]")
                if not self.operationer.search_and_detect(
                        [
                            self.scene_graph.scenes.get("X之要塞")
                        ],
                        [
                            {'click': "空白点"},
                            {'click': "你的对手离开了游戏-确定"}
                        ],
                        search_max_time=60
                ):
                    raise StepFailedError("战斗结束后无法退回[X之要塞]")
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
                        self.operationer.current_scene.elements.get("本局举报")
                    ],
                    max_workers=7
                )
                self.logger.info("对局结束，返回[X之要塞]")
        if not self.operationer.search_and_detect(
                [
                    self.scene_graph.scenes.get("X之要塞")
                ],
                [
                    {'click': "空白点"},
                    {'click': "你的对手离开了游戏-确定"}
                ],
                search_max_time=60,
                wait_time=0
        ):
            raise StepFailedError("战斗结束后无法退回[X之要塞]")

    def update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        # 辅助函数：计算下次周六8点的时间
        def get_next_saturday_8pm(current_time, tz):
            # Python中星期标识：0=周一, 1=周二, ..., 5=周六, 6=周日
            current_weekday = current_time.weekday()
            # 计算距离下周六的天数（周六是星期5）
            days_ahead = (5 - current_weekday) % 7
            # 如果今天就是周六且已过8点，则需要再加7天到下周六
            if days_ahead == 0 and current_time.hour >= 20:
                days_ahead = 7
            next_time = current_time + timedelta(days=days_ahead)
            # 设置时间为8点，清除分秒和微秒
            return next_time.replace(hour=20, minute=0, second=0, microsecond=0, tzinfo=tz)

        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        match flag:
            case 0:  # 创建任务时使用
                next_exec_ts = self.data.get('下次执行时间')
                if next_exec_ts == 0 or next_exec_ts is None:
                    # 为空时转用case 1的逻辑（下周六8点）
                    self.next_execute_time = get_next_saturday_8pm(current_time, china_tz)
                else:
                    # 从时间戳转换为datetime对象（指定中国时区）
                    self.next_execute_time = datetime.fromtimestamp(next_exec_ts, tz=china_tz)

            case 1:  # 正常执行完毕，更新为下周六8点
                self.next_execute_time = get_next_saturday_8pm(current_time, china_tz)

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                self.next_execute_time = get_next_saturday_8pm(current_time, china_tz)

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