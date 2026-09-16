from datetime import timedelta
import time

from backend.core.legacy.Enums import KEY_INDEX
from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn
from backend.core.legacy.Task.schedule import Weekday, Weekly


class GengDuoWanFa(BaseTask):
    source_scene = "更多玩法"
    task_max_duration = timedelta(hours=2)
    # 每周任务：窗口 [本周一 5:01, 下周一 5:01)，本周内可补跑
    schedule = Weekly(Weekday.MON)

    # 注：绝迹战场 / 大蛇丸试炼是完整对局，进入「-副本内」后一局可持续数分钟，期间画面
    # 因连点持续变化但场景名不变。旧做法是把整任务的场景停滞阈值抬到 600s；现在由框架的
    # 「进展信号」接管——**连点进行中**即视为有意等待（改用「超时检测-等待超时秒」），
    # 匹配中/匹配成功另用 declare_waiting 显式声明，因此不再需要任务级覆盖。

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checked = False
        self.finished = False
        
    def run(self):
        self.operationer.clicker.update_coordinates([
                    self.config.get_config("键位")[KEY_INDEX.BasicAttack],
                    self.config.get_config("键位")[KEY_INDEX.FirstSkill],
                    self.config.get_config("键位")[KEY_INDEX.SecondSkill],
                    self.config.get_config("键位")[KEY_INDEX.UltimateSkill],
                    self.config.get_config("键位")[KEY_INDEX.Substitution]
                ])
        super().run()

    @TransitionOn()
    def _(self):
        self.operationer.clicker.stop()
        self.bool_click=False
        if not self.checked:
            self.operationer.click_and_wait("任务")
            return False
        if not self.finished:
            if self.operationer.click_and_wait("大蛇丸试炼"):
                return False
            elif self.operationer.click_and_wait("绝迹战场"):
                return False
            if self.operationer.detect_element("集结团队战"):
                self.logger.warning("本周更多玩法为集结团队战，将推迟任务执行至下周")

        raise TaskCompleted("任务执行完成")
    @TransitionOn("绝迹战场")
    def _(self):
        self.operationer.clicker.stop()
        self.bool_click=False
        if not self.checked:
            self.operationer.click_and_wait("返回")
            return False
        if not self.finished:
            self.operationer.click_and_wait("开战")
            return False
        raise TaskCompleted("任务执行完成")
    @TransitionOn("大蛇丸试炼")
    def _(self):
        self.operationer.clicker.stop()
        self.bool_click=False
        if not self.checked:
            self.operationer.click_and_wait("返回")
            return False
        if not self.finished:
            self.operationer.click_and_wait("开战")
            return False
        raise TaskCompleted("任务执行完成")
    @TransitionOn("大蛇丸试炼-副本内")
    def _(self):
        self.checked = False
        self.bool_click = True
        self.operationer.clicker.start()
        self.operationer.next_scene = None
        return False

    @TransitionOn("绝迹战场-副本内")
    def _(self):
        self.checked = False
        self.bool_click = True
        self.operationer.clicker.start()
        self.operationer.next_scene = None
        time.sleep(1)
        return False

    @TransitionOn("更多玩法-任务")
    def _(self):
        self.operationer.clicker.stop()
        self.bool_click=False
        if not self.operationer.detect_element("未达成") and not self.finished:
            self.operationer.click_and_wait("2100")
            self.finished = True
            return False
        self.operationer.click_and_wait("X")
        self.checked = True
        return False

    @TransitionOn("更多玩法-匹配中")
    def _(self):
        self.bool_click = True
        self.operationer.clicker.stop()
        # 匹配耗时不可控（等对手/等系统），显式声明等待，避免被停滞判定误杀
        self.declare_waiting("更多玩法匹配中")
        return False

    @TransitionOn("更多玩法-匹配成功")
    def _(self):
        self.bool_click = True
        self.operationer.clicker.stop()
        self.declare_waiting("更多玩法匹配成功")
        self.operationer.click_and_wait("准备就绪")
        return False

    @TransitionOn("更多玩法-选择忍者")
    def _(self):
        self.bool_click = True
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("默认忍者-1", wait_time=0.2)
        self.operationer.click_and_wait("确定", wait_time=0.3)
        self.operationer.click_and_wait("默认忍者-2", wait_time=0.2)
        self.operationer.click_and_wait("确定", wait_time=0.3)
        self.operationer.click_and_wait("默认忍者-3", wait_time=0.2)
        self.operationer.click_and_wait("确定", wait_time=0.3)
        self.operationer.click_and_wait("确定", wait_time=0.3)
        return False

    @TransitionOn("更多玩法-结算")
    def _(self):
        self.bool_click = False
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("你的对手离开了游戏")
    def _(self):
        self.bool_click = False
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("决斗场-首页")
    def _(self):
        self.operationer.clicker.stop()
        self.bool_click=False
        self.operationer.click_and_wait("更多玩法")
        return False

    @TransitionOn("任务奖励-一键领取")
    def _(self):
        self.operationer.clicker.stop()
        self.bool_click=False
        self.operationer.click_and_wait("确定")
        self.finished = True
        return False

    
    def reset_task_exe_prog(self) -> bool:
        self.checked = False
        self.finished = False
        return True