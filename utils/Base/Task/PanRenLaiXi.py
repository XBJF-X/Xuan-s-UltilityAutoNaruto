import datetime
import time
from zoneinfo import ZoneInfo

from utils.Base.Enums import KEY_INDEX
from utils.Base.Exceptions import TaskCompleted, TooEarlyToRun
from utils.Base.Task.BaseTask import BaseTask, TransitionOn, debug_execute_window


class PanRenLaiXi(BaseTask):
    source_scene = "主场景-组织"
    task_max_duration = datetime.timedelta(minutes=45)

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
            if self.operationer.detect_element("自动参战-0金币"):
                self.operationer.click_and_wait("自动参战")
                self.logger.info("自动参战已开启")
                self.auto = True
            else:
                self.logger.info("无法自动参战，将手动挑战")
            self.check = True
        if not self.auto:
            if not self.operationer.click_and_wait(difficulty, wait_time=2):
                self.logger.info(f"未发现 {difficulty}，将移动寻找")
                x, y = self.config.get_config("键位")[KEY_INDEX.JoyStick]
                self.operationer.long_press(x + 50 * self.find_direction, y, duration=1)
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
    
    def _get_task_trigger_time(self, base_time: datetime.time, task_name: str) -> datetime.time:
        stop_minute = self.config.get_task_exe_param(task_name, "本任务执行多少分钟后执行叛忍", 0)
        if stop_minute == 0:
            stop_minute = 30
        return base_time.replace(minute=stop_minute, second=0, microsecond=0)
    
    @debug_execute_window
    def _get_execute_window(self,dt: datetime.datetime | None = None):
        windows=[]
        if dt is None:
            dt=self.last_run_time
        dt = self._ensure_tz_aware(dt)
        today= dt.date()
        match today.weekday():
            case 0|1|2:
                if self.config.get_task_exe_param("天地战场", "执行结束后是否有叛忍", False):
                    wednesday = today + datetime.timedelta(days=(2 - today.weekday()))
                    start_dt = datetime.datetime.combine(wednesday, datetime.time(21, 0), tzinfo=self.tz_info)
                    end_dt = datetime.datetime.combine(
                        wednesday, 
                        self._get_task_trigger_time(datetime.time(21, 0), "天地战场"), 
                        tzinfo=self.tz_info)
                    windows.append((start_dt, end_dt + datetime.timedelta(minutes=30)))
            case 3|4|5:
                if self.config.get_task_exe_param("要塞争夺战", "执行结束后是否有叛忍", False):
                    saturday = today + datetime.timedelta(days=(5 - today.weekday()))
                    start_dt = datetime.datetime.combine(saturday, datetime.time(20, 0), tzinfo=self.tz_info)
                    end_dt = datetime.datetime.combine(
                        saturday,
                        self._get_task_trigger_time(datetime.time(20, 0), "要塞争夺战"),
                        tzinfo=self.tz_info)
                    windows.append((start_dt, end_dt + datetime.timedelta(minutes=30)))
        next_wednesday = today + datetime.timedelta(days=(2 - today.weekday()) % 7)
        start_dt = datetime.datetime.combine(next_wednesday, datetime.time(21, 0), tzinfo=self.tz_info)
        end_dt = start_dt + datetime.timedelta(minutes=60)
        windows.append((start_dt, end_dt))
        windows.sort(key=lambda x: x[0])
        return windows
    
    def get_next_cycle_day(self, dt: datetime.datetime) -> datetime.datetime:
        return dt + datetime.timedelta(weeks=1)

    def _handle_timeout_max_duration(self, current_time: datetime.datetime) -> datetime.datetime:
        return self._handle_execution_completed(current_time)

    def reset_task_exe_prog(self) -> bool:
        self.check = False
        self.auto = False
        self.decrease_difficulty = True
        self.find_time = 0
        self.find_direction = 1
        return True
