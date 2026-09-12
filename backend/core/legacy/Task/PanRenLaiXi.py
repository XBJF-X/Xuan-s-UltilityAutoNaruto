import datetime
import time

from backend.core.legacy.Enums import KEY_INDEX
from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn
from backend.core.legacy.Task.schedule import Custom, Window

PARAM_HAS_PANREN = "执行结束后是否有叛忍"
PARAM_PANREN_MINUTE = "本任务执行多少分钟后执行叛忍"


def _panren_windows(base, ctx):
    """叛忍来袭的多窗口排期：

    - 周一~周三：若"天地战场"执行后会召唤叛忍 → 周三 21:00 触发窗口（+30 分钟缓冲）；
    - 周四~周六：若"要塞争夺战"执行后会召唤叛忍 → 周六 20:00 触发窗口（+30 分钟缓冲）；
    - 兜底：下一个周三 21:00 ~ 22:00。
    """
    tz = base.tzinfo
    weekday = base.date().weekday()
    windows = []
    if ctx is not None:
        if weekday in (0, 1, 2) and ctx.param("天地战场", PARAM_HAS_PANREN, False):
            wed = base.date() + datetime.timedelta(days=2 - weekday)
            minute = ctx.param("天地战场", PARAM_PANREN_MINUTE, 0) or 30
            start = datetime.datetime.combine(wed, datetime.time(21, 0), tzinfo=tz)
            end = datetime.datetime.combine(
                wed, datetime.time(21, minute), tzinfo=tz) + datetime.timedelta(minutes=30)
            windows.append(Window(start, end))
        if weekday in (3, 4, 5) and ctx.param("要塞争夺战", PARAM_HAS_PANREN, False):
            sat = base.date() + datetime.timedelta(days=5 - weekday)
            minute = ctx.param("要塞争夺战", PARAM_PANREN_MINUTE, 0) or 30
            start = datetime.datetime.combine(sat, datetime.time(20, 0), tzinfo=tz)
            end = datetime.datetime.combine(
                sat, datetime.time(20, minute), tzinfo=tz) + datetime.timedelta(minutes=30)
            windows.append(Window(start, end))
    next_wed = base.date() + datetime.timedelta(days=(2 - weekday) % 7)
    start = datetime.datetime.combine(next_wed, datetime.time(21, 0), tzinfo=tz)
    windows.append(Window(start, start + datetime.timedelta(minutes=60)))
    return windows


class PanRenLaiXi(BaseTask):
    source_scene = "主场景-组织"
    task_max_duration = datetime.timedelta(minutes=45)
    # 多窗口排期：周三/周六的叛忍触发窗口 + 下周三兜底（窗口受其它任务参数影响）
    schedule = Custom(_panren_windows,
                      cycle=lambda base: base + datetime.timedelta(weeks=1),
                      describe_text="周三/周六叛忍触发窗口 + 下周三兜底")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auto = False
        self.check = False
        self.decrease_difficulty = True
        self.find_time = 0
        self.find_direction = 1

    @TransitionOn()
    def _(self):
        self.operationer.click_and_wait("玩法")
        self.operationer.search_and_click(
            [
                f"叛忍来袭-前往"
            ],
            [
                {
                    "swipe": {
                        "start_coordinate": [1000, 464],
                        "end_coordinate": [350, 464],
                        "duration": 0.5
                    }
                }
            ],
            max_attempts=3,
            wait_time=5,
            stable_wait_for_new_scene=True
        )
        return False

    @TransitionOn("叛忍来袭-未开始")
    def _(self):
        self.logger.info("叛忍来袭还未开启...")
        
        if self.config.get_task_exe_param(self.task_name, "是否需要开启叛忍", True):
            self.operationer.click_and_wait("开启")
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("叛忍来袭-即将开始")
    def _(self):
        time.sleep(3)
        self.logger.info("叛忍来袭即将开始")
        return False

    @TransitionOn("叛忍来袭-进行中")
    def _(self):
        self.operationer.click_and_wait("前往参战")
        self.logger.info("正在前往参战")
        return False

    @TransitionOn("叛忍来袭-选择难度")
    def _(self):
        difficulty = ["普通模式", "困难模式"][
            self.config.get_task_exe_param(self.task_name, "开启叛忍难度", 0)]

        while not self.operationer.detect_element(f"{difficulty}-选中"):
            self.operationer.click_and_wait(difficulty)
        self.logger.info(f"叛忍难度选择为{difficulty}")

        if self.config.get_task_exe_param(self.task_name, "是否开启二倍奖励", True):
            if self.operationer.click_and_wait("开启双倍奖励-未选中"):
                self.logger.info("已自动勾选开启二倍奖励")
            else:
                self.logger.info("二倍奖励已开启，无需勾选")

        self.operationer.click_and_wait("确定", wait_time=4, stable_wait_for_new_scene=True)
        return False

    @TransitionOn("叛忍来袭-是否开启")
    def _(self):
        self.operationer.click_and_wait("确定", wait_time=4, stable_wait_for_new_scene=True)
        self.logger.info("确认开启 叛忍来袭")
        return False

    @TransitionOn("叛忍来袭-是否开启-双倍")
    def _(self):
        self.operationer.click_and_wait("确定", wait_time=3, stable_wait_for_new_scene=True)
        self.logger.info("确认开启 叛忍来袭[双倍奖励]")
        return False

    @TransitionOn("叛忍来袭-更换忍者")
    def _(self):
        ninjas = ["老三代", "须佐鼬", "老天道", "阿斯玛"]
        if not self.operationer.detect_element("选中"):
            self.logger.warning("未选中叛忍挑战忍者，将自动寻找是否有合适忍者，如果没有将使用默认忍者位（第一个）")
            flag = self.operationer.search_and_click(
                ninjas,
                []
            )
            if not flag:
                self.logger.info("将使用第一个忍者")
                self.operationer.click_and_wait("默认忍者")
            else:
                self.logger.info(f"叛忍挑战忍者选为{ninjas[flag]}")
        else:
            self.logger.info("已有默认选中忍者，将使用")
        self.operationer.click_and_wait("确定", wait_time=3,stable_wait_for_new_scene=True)
        return False

    @TransitionOn("叛忍来袭-内部")
    def _(self):
        difficulty = ["低级叛忍", "中级叛忍", "高级叛忍"][
            self.config.get_task_exe_param(self.task_name, "挑战叛忍类型")]
        if not self.check:
            if not self.operationer.detect_element("自动参战-50金币"):
                self.operationer.click_and_wait("自动参战")
                self.logger.info("自动参战已开启")
                self.auto = True
            else:
                if self.config.get_task_exe_param(self.task_name, "是否使用50金币自动参战", True):
                    self.operationer.click_and_wait("自动参战")
                    self.logger.info("自动参战已开启")
                    self.auto = True
                else:
                    self.logger.info("无法自动参战，将手动挑战")
            self.check = True
            # zdcz_jbs=self.operationer.ocr_recognize("自动参战金币数")
            # if zdcz_jbs:
            #     if zdcz_jbs.is_equal_to(0):
            #     # if zdcz_jbs[0].extract_numbers()[0]==0:
            #         self.operationer.click_and_wait("自动参战")
            #         self.logger.info("自动参战已开启")
            #         self.auto = True
            #     # if self.operationer.detect_element("自动参战-0金币"):
            #     #     self.operationer.click_and_wait("自动参战")
            #     #     self.logger.info("自动参战已开启")
            #     #     self.auto = True
            #     else:
            #         if self.config.get_task_exe_param(self.task_name, "是否使用50金币自动参战", True):
            #             self.operationer.click_and_wait("自动参战")
            #             self.logger.info("自动参战已开启")
            #             self.auto = True
            #         else:
            #             self.logger.info("无法自动参战，将手动挑战")
            # self.check = True
        if not self.auto:
            if not self.operationer.click_and_wait(difficulty, wait_time=2):
                self.logger.info(f"未发现 {difficulty}，将移动寻找")
                x, y = self.config.get_config("键位")[KEY_INDEX.JoyStick]
                self.operationer.long_press(x + 100 * self.find_direction, y, duration=1)
                self.find_time += 1
                if self.find_time >= 7:
                    self.logger.warning(f"寻找 {difficulty} 已经 {self.find_time} 次，将改变寻找方向后重试...")
                    self.find_time = 0
                    self.find_direction *= -1
                return False
        else:
            self.logger.info("正在自动参战叛忍...")
            time.sleep(1)
        return False

    @TransitionOn("叛忍来袭-战斗中")
    def _(self):
        if not self.operationer.detect_element("自动战斗中"):
            self.logger.info("启动自动战斗")
            self.operationer.click_and_wait("标志")
        time.sleep(1)
        self.decrease_difficulty = True
        return False

    @TransitionOn("叛忍来袭-单局结算")
    def _(self):
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("叛忍来袭-结束")
    def _(self):
        self.operationer.click_and_wait("确定")
        self.logger.info("叛忍来袭已结束")
        raise TaskCompleted("叛忍来袭已结束")

    @TransitionOn("叛忍来袭-今日叛忍已结束")
    def _(self):
        self.logger.info("今日叛忍来袭已结束")
        raise TaskCompleted("今日叛忍来袭已结束")

    @TransitionOn("叛忍来袭-确认挑战")
    def _(self):
        self.operationer.click_and_wait("确定", wait_time=3,stable_wait_for_new_scene=True)
        return False

    @TransitionOn("叛忍来袭-已获得2次奖励")
    def _(self):
        self.operationer.click_and_wait("确定", wait_time=3,stable_wait_for_new_scene=True)
        return False

    @TransitionOn("决斗场-匹配中")
    def _(self):
        if self.decrease_difficulty:
            difficulty_level = self.config.get_task_exe_param(self.task_name, "挑战叛忍类型")
            difficulty = ["低级叛忍", "中级叛忍", "高级叛忍"][difficulty_level]
            self.logger.warning(f"挑战[{difficulty}]失败，将自动降低难度")
            difficulty_level = max(0, difficulty_level - 1)
            self.config.set_task_exe_param(self.task_name, "挑战叛忍类型", difficulty_level)
            self.logger.warning(f"设置挑战叛忍类型为：{["低级叛忍", "中级叛忍", "高级叛忍"][difficulty_level]}")
            self.decrease_difficulty = False
        time.sleep(2)
        return False
    
    def on_timeout(self, current_time: datetime.datetime) -> datetime.datetime:
        return self.on_complete(current_time)

    def reset_task_exe_prog(self) -> bool:
        self.check = False
        self.auto = False
        self.decrease_difficulty = True
        self.find_time = 0
        self.find_direction = 1
        return True
