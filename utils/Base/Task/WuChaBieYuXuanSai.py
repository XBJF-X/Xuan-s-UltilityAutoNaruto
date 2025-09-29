from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

from PySide6.QtCore import QThread

from utils.Base.Enums import KEY_INDEX
from utils.Base.Task.BaseTask import BaseTask, TransitionOn, handle_task_exceptions


class WuChaBieYuXuanSai(BaseTask):
    source_scene = "火影格斗大赛-无差别"
    dead_line = time(22)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checked = False
        self.finished = False

    @TransitionOn()
    def _(self):
        if not self.checked:
            self.operationer.click_and_wait("成就奖励")
            return False
        if self.config.get_task_exe_param(self.task_name, "选择刷取方式", 0) == 1:
            if self.operationer.detect_element("场次-30", auto_raise=False):
                self.finished = True
        if not self.finished:
            self.operationer.click_and_wait("出战")
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
            return False
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        return True

    @TransitionOn("无差别-成就奖励")
    def _(self):
        if not self.checked:
            while self.operationer.click_and_wait("领取", auto_raise=False):
                continue
            if self.config.get_task_exe_param(self.task_name, "选择刷取方式", 0) == 0:
                if not self.operationer.detect_element("未达成", auto_raise=False):
                    self.finished = True
        self.operationer.click_and_wait("X")
        self.checked = True
        return False

    @TransitionOn("无差别-等待对方选择")
    def _(self):
        QThread.msleep(1000)
        return False

    @TransitionOn("无差别-禁用忍者选择")
    def _(self):
        if not self.operationer.detect_element("禁用", wait_time=0, auto_raise=False):
            QThread.msleep(1000)
            return False
        for i in range(1, 13):
            self.operationer.click_and_wait(f"忍者-{i}", wait_time=0.5)
            if not self.operationer.click_and_wait("禁用", wait_time=0.5, auto_raise=False):
                return False
        return False

    @TransitionOn("无差别-忍者选择")
    def _(self):
        if not self.operationer.detect_element("确定", wait_time=0, auto_raise=False):
            QThread.msleep(1000)
            return False
        for i in range(1, 13):
            self.operationer.click_and_wait(f"忍者-{i}", wait_time=0.5)
            if not self.operationer.click_and_wait("确定", wait_time=0.5, auto_raise=False):
                return False
        return False

    @TransitionOn("无差别-禁用秘卷选择")
    def _(self):
        if not self.operationer.detect_element("禁用", wait_time=0, auto_raise=False):
            QThread.msleep(1000)
            return False
        for i in range(1, 10):
            self.operationer.click_and_wait(f"秘卷-{i}", wait_time=0.5)
            if not self.operationer.click_and_wait("禁用", wait_time=0.5, auto_raise=False):
                return False
        return False

    @TransitionOn("无差别-秘卷选择")
    def _(self):
        if not self.operationer.detect_element("确定", wait_time=0, auto_raise=False):
            QThread.msleep(1000)
            return False
        for i in range(1, 10):
            self.operationer.click_and_wait(f"秘卷-{i}", wait_time=0.5)
            if not self.operationer.click_and_wait("确定", wait_time=0.5, auto_raise=False):
                return False
        return False

    @TransitionOn("决斗场-匹配中")
    def _(self):
        return False

    @TransitionOn("决斗场-战斗中")
    def _(self):
        self.checked = False
        QThread.msleep(500)
        self.operationer.next_scene = "火影格斗大赛-无差别"
        return False

    @TransitionOn("决斗场-单局结算")
    def _(self):
        self.checked = False
        self.operationer.next_scene = "火影格斗大赛-无差别"
        return False

    @TransitionOn("决斗场-结算")
    def _(self):
        self.checked = False
        self.operationer.click_and_wait("X")
        self.operationer.next_scene = "火影格斗大赛-无差别"
        return False

    @TransitionOn("你的对手离开了游戏")
    def _(self):
        self.checked = False
        self.operationer.click_and_wait("确定")
        self.operationer.next_scene = "火影格斗大赛-无差别"
        return False

    @TransitionOn("对手已经掉线了")
    def _(self):
        self.checked = False
        self.operationer.click_and_wait("确定")
        self.operationer.next_scene = "火影格斗大赛-无差别"
        return False

    @TransitionOn("未知场景")
    def _(self):
        QThread.msleep(1000)
        return False

    @TransitionOn("未注册场景")
    def _(self):
        QThread.msleep(1000)
        return False

    def _handle_initialization(self, current_time: datetime) -> datetime:
        """处理任务初始化时的时间设置（case0）"""
        china_tz = current_time.tzinfo
        # 读取配置中的时间
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")

        next_execute_time = datetime(
            current_time.year,
            current_time.month,
            current_time.day,
            18, 0, 0,
            tzinfo=china_tz
        )

        if next_exec_ts == 0:
            return next_execute_time
        else:
            # 转换为带时区的datetime
            stored_time = datetime.fromtimestamp(next_exec_ts, tz=china_tz)
            if stored_time+timedelta(hours=4) < current_time:
                return next_execute_time
            else:
                return stored_time

    def _handle_execution_completed(self, current_time: datetime) -> datetime:
        """处理任务执行完成后的时间更新（case1）"""
        china_tz = current_time.tzinfo
        next_day = current_time + timedelta(days=1)
        return datetime(
            next_day.year,
            next_day.month,
            next_day.day,
            18, 0, 0,
            tzinfo=china_tz
        )
