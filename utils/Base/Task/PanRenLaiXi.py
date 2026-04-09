import datetime
import time

from utils.Base.Enums import KEY_INDEX
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class PanRenLaiXi(BaseTask):
    source_scene = "主场景-组织"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auto = False
        self.check = False
        self.decrease_difficulty = True
        self.find_time = 0
        self.find_direction = 1
        match datetime.datetime.now().weekday():
            case 0|1|2:
                self.dead_line = datetime.time(hour=22)
            case 3|4|5|6:
                self.dead_line = datetime.time(hour=21)

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
        if (datetime.datetime.now()+datetime.timedelta(hours=1)).time() <self.dead_line: # type: ignore
            self.logger.info("叛忍来袭启动时间过早，将关闭并等待下一次执行...")
            self.update_next_execute_time()
            return True
        
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
        self.update_next_execute_time()
        return True

    @TransitionOn("叛忍来袭-今日叛忍已结束")
    def _(self):
        self.logger.info("今日叛忍来袭已结束")
        self.update_next_execute_time()
        return True

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

    def _cleanup_on_timeout(self):
        """超时时的清理"""
        self.operationer.clicker.stop()
        self.update_next_execute_time()
        self.reset_task_exe_prog()

    def _handle_initialization(self, current_time: datetime.datetime) -> datetime.datetime:
        """处理任务初始化时的时间设置（case0）"""
        china_tz = current_time.tzinfo
        # 读取配置中的时间
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")

        # 取得当前执行周期的任务执行时间
        next_execute_time = self.get_cycle_execute_time(current_time)

        if not next_exec_ts:
            # 配置中未设置下次执行时间，返回默认时间
            return next_execute_time

        try:
            next_exec_dt = datetime.datetime.fromtimestamp(next_exec_ts, tz=china_tz)
        except Exception as e:
            self.logger.warning(f"解析下次执行时间戳失败: {next_exec_ts}, 错误: {e}")
            return next_execute_time

        # 判断下次执行时间是否过期
        if next_exec_dt < current_time:
            return next_execute_time

        # 配置中的下次执行时间未过期，直接返回
        return next_exec_dt
    
    def _handle_execution_completed(self, current_time: datetime.datetime) -> datetime.datetime:
        """返回下一个执行周期的任务执行时间"""
        return self.get_next_cycle_execute_time(current_time)

    def reset_task_exe_prog(self) -> bool:
        self.check = False
        self.auto = False
        self.decrease_difficulty = True
        self.find_time = 0
        self.find_direction = 1
        return True
