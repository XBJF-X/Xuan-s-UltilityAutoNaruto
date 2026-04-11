import datetime
import time
from datetime import timedelta

from utils.Base.Exceptions import TaskCompleted
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class WuChaBieYuXuanSai(BaseTask):
    source_scene = "火影格斗大赛-无差别"
    start_line= datetime.time(18, 0)
    dead_line = datetime.time(22, 0)

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
        raise TaskCompleted("任务执行完成")
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
        raise TaskCompleted("任务执行完成")
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
