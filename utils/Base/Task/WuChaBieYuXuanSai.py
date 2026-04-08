import datetime
import time
from datetime import timedelta

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class WuChaBieYuXuanSai(BaseTask):
    source_scene = "火影格斗大赛-无差别"
    dead_line = datetime.time(22)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checked = False
        self.finished = False

    @TransitionOn()
    def _(self):
        self.bool_click = False
        if not self.checked:
            self.operationer.click_and_wait("成就奖励")
            return False
        if self.config.get_task_exe_param(self.task_name, "选择刷取方式", 0) == 1:
            if self.operationer.detect_element("场次-30"):
                self.finished = True
        if not self.finished:
            self.operationer.click_and_wait("出战")
            self.bool_click = True
            return False
        self.update_next_execute_time()
        return True

    @TransitionOn("无差别-继续出战")
    def _(self):
        if not self.checked:
            self.operationer.click_and_wait("X")
            return False
        if not self.finished:
            self.operationer.click_and_wait("继续出战")
            self.bool_click = True
            return False
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        return True

    @TransitionOn("无差别-成就奖励")
    def _(self):
        self.bool_click = False
        if not self.checked:
            while self.operationer.click_and_wait("领取"):
                continue
            if self.config.get_task_exe_param(self.task_name, "选择刷取方式", 0) == 0:
                if not self.operationer.detect_element("未达成"):
                    self.finished = True
        self.operationer.click_and_wait("X")
        self.checked = True
        return False

    @TransitionOn("无差别-等待对方选择")
    def _(self):
        self.bool_click = True
        time.sleep(1)
        return False

    @TransitionOn("无差别-禁用忍者选择")
    def _(self):
        self.bool_click = True
        if not self.operationer.detect_element("禁用", wait_time=0):
            time.sleep(1)
            return False
        for i in range(1, 13):
            self.operationer.click_and_wait(f"忍者-{i}", wait_time=0.5)
            if not self.operationer.click_and_wait("禁用", wait_time=0.5):
                return False
        return False

    @TransitionOn("无差别-忍者选择")
    def _(self):
        self.bool_click = True
        if not self.operationer.detect_element("确定", wait_time=0):
            time.sleep(1)
            return False
        for i in range(1, 13):
            self.operationer.click_and_wait(f"忍者-{i}", wait_time=0.5)
            if not self.operationer.click_and_wait("确定", wait_time=0.5):
                return False
        return False

    @TransitionOn("无差别-禁用秘卷选择")
    def _(self):
        self.bool_click = True

        if not self.operationer.detect_element("禁用", wait_time=0):
            time.sleep(1)
            return False
        for i in range(1, 10):
            self.operationer.click_and_wait(f"秘卷-{i}", wait_time=0.5)
            if not self.operationer.click_and_wait("禁用", wait_time=0.5):
                return False
        return False

    @TransitionOn("无差别-秘卷选择")
    def _(self):
        self.bool_click = True
        if not self.operationer.detect_element("确定", wait_time=0):
            time.sleep(1)
            return False
        for i in range(1, 10):
            self.operationer.click_and_wait(f"秘卷-{i}", wait_time=0.5)
            if not self.operationer.click_and_wait("确定", wait_time=0.5):
                return False
        return False

    @TransitionOn("决斗场-匹配中")
    def _(self):
        self.bool_click = True
        return False

    @TransitionOn("决斗场-战斗中")
    def _(self):
        self.checked = False
        self.bool_click = True
        time.sleep(0.5)
        self.operationer.next_scene = "火影格斗大赛-无差别"
        return False

    @TransitionOn("决斗场-单局结算")
    def _(self):
        self.checked = False
        self.bool_click = True
        self.operationer.next_scene = "火影格斗大赛-无差别"
        return False

    @TransitionOn("决斗场-结算")
    def _(self):
        self.checked = False
        self.bool_click = False
        self.operationer.click_and_wait("X")
        self.operationer.next_scene = "火影格斗大赛-无差别"
        return False

    @TransitionOn("你的对手离开了游戏")
    def _(self):
        self.checked = False
        self.bool_click = False
        self.operationer.click_and_wait("确定")
        self.operationer.next_scene = "火影格斗大赛-无差别"
        return False

    @TransitionOn("对手已经掉线了")
    def _(self):
        self.checked = False
        self.bool_click = False
        self.operationer.click_and_wait("确定")
        self.operationer.next_scene = "火影格斗大赛-无差别"
        return False

    @TransitionOn("未知场景")
    def _(self):
        time.sleep(1)
        return False

    @TransitionOn("未注册场景")
    def _(self):
        time.sleep(1)
        return False

    def _handle_initialization(self, current_time: datetime.datetime) -> datetime.datetime:
        """处理任务初始化时的时间设置（case0）"""
        china_tz = current_time.tzinfo
        # 读取配置中的时间
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")
        next_execute_time = current_time.replace(hour=18, minute=0, second=0, microsecond=0)

        if next_exec_ts == 0:
            return next_execute_time
        else:
            return datetime.datetime.fromtimestamp(next_exec_ts, tz=china_tz)

    def _handle_execution_completed(self, current_time: datetime.datetime) -> datetime.datetime:
        """处理任务执行完成后的时间更新（case1）"""
        next_execute_time = current_time.replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return next_execute_time
