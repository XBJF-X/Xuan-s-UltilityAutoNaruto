from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from PySide6.QtCore import QThread

from utils.Base.Enums import KEY_INDEX
from utils.Base.Exceptions import EndEarly, StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class TianDiZhanChang(BaseTask):
    source_scene = "天地战场"
    task_max_duration = timedelta(minutes=31)
    pillar_took = False

    @TransitionOn()
    def _(self):
        self.operationer.click_and_wait("地之战场")
        self.operationer.click_and_wait("确定进入-确认", max_time=0.5, stable_max_time=0.5, auto_raise=False)
        self.operationer.click_and_wait("出战忍者-忍者")
        self.operationer.click_and_wait("出战忍者-默认选择-1", stable_max_time=0.5)
        self.operationer.click_and_wait("出战忍者-通灵兽", stable_max_time=0.5)
        self.operationer.click_and_wait("出战忍者-默认选择-1", stable_max_time=0.5)
        self.operationer.click_and_wait("出战忍者-默认选择-2", stable_max_time=0.5)
        self.operationer.click_and_wait("出战忍者-默认选择-3", stable_max_time=0.5)
        self.operationer.click_and_wait("出战忍者-秘卷", stable_max_time=0.5)
        self.operationer.click_and_wait("出战忍者-默认选择-1", stable_max_time=0.5)
        self.operationer.click_and_wait("出战忍者-确认", stable_max_time=0.5)
        self.operationer.detect_element("地之战场-标识", max_time=10)
        self.operationer.click_and_wait("组织鼓舞")
        while datetime.now(tz=ZoneInfo("Asia/Shanghai")) <= self.dead_line:
            if self.operationer.click_and_wait("战场战斗已经结束-确认", max_time=0.5, auto_raise=False):
                # 领取所有战场奖励
                self.operationer.click_and_wait("战场奖励")
                while self.operationer.click_and_wait("战场奖励-领取", max_time=0.5, stable_max_time=0.5, auto_raise=False):
                    if self.operationer.detect_element("战场奖励-恭喜你获得", stable_max_time=0.5, auto_raise=False):
                        self.operationer.click_and_wait("空白点")
                self.operationer.click_and_wait("空白点")
                self.operationer.click_and_wait("X")
                self.operationer.click_and_wait("确认退出天地战场-确认")
                self.update_next_execute_time()
                raise EndEarly("天地战场战斗已经结束")

            if self.pillar_took:
                # 检测是否进入战斗
                flag = self.operationer.search_and_detect(
                    [
                        self.operationer.current_scene.elements.get("60"),
                        self.operationer.current_scene.elements.get("你的对手离开了游戏")
                    ],
                    [
                        {'click': "你的对手离开了游戏-确定"}
                    ],
                    search_max_time=60,
                )
                match flag:
                    case 0:
                        self.logger.info("无人攻击...")
                    case 1:
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
                        # 输连点器之后需要重新选角色，按系统默认的来
                        self.operationer.click_and_wait(
                            "出战忍者-确认",
                            max_time=30,
                            wait_time=0.5,
                            auto_raise=False)
                        self.pillar_took = False
                    case 2:
                        self.logger.warning("对手退出游戏，即将返回[地之战场]")
                        self.pillar_took = True
                # 先回到单人模式首页
                if not self.operationer.search_and_detect(
                        [
                            self.operationer.current_scene.elements.get("地之战场-标识")
                        ],
                        [
                            {'click': "空白点"},
                            {'click': "你的对手离开了游戏-确定"}
                        ],
                        search_max_time=30
                ):
                    raise StepFailedError("战斗结束后无法退回[地之战场]")
            else:
                if self.operationer.click_and_wait("空闲柱子", max_time=60, auto_raise=False):
                    self.pillar_took = True

        self.operationer.click_and_wait("X")
        self.operationer.click_and_wait("确认退出天地战场-确认")
        self.update_next_execute_time()
        return True

    def update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        # 辅助函数：计算下次周三9点的时间
        def get_next_wednesday_9pm(current_time, tz):
            current_weekday = current_time.weekday()
            days_ahead = (2 - current_weekday) % 7
            if days_ahead == 0 and current_time.hour >= 21:
                days_ahead = 7
            next_time = current_time + timedelta(days=days_ahead)
            return next_time.replace(hour=21, minute=0, second=0, microsecond=0, tzinfo=tz)

        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        match flag:

            case 0:  # 创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                next_exec_ts = self.data.get('下次执行时间')
                if next_exec_ts == 0:
                    self.next_execute_time = get_next_wednesday_9pm(current_time, china_tz)
                else:
                    # 从时间戳转换为datetime对象（指定UTC时区避免歧义）
                    self.next_execute_time = datetime.fromtimestamp(next_exec_ts, tz=ZoneInfo("Asia/Shanghai"))

            case 1:  # 正常执行完毕，更新为下次执行的时间
                self.next_execute_time = get_next_wednesday_9pm(current_time, china_tz)

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                self.next_execute_time = get_next_wednesday_9pm(current_time, china_tz)

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
