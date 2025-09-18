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

    @property
    def next_execute_time(self):
        china_tz = ZoneInfo("Asia/Shanghai")
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")
        if next_exec_ts == 0:
            # 若初始值为0，设置为当前UTC时间（或其他合理时间）
            return datetime.now(china_tz).replace(hour=18, minute=0, second=0, microsecond=0)
        else:
            # 从时间戳转换为datetime对象
            return datetime.fromtimestamp(next_exec_ts, tz=china_tz)

    def update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        """
        用于更新本任务的下次执行时间，默认为更新到第二天五点（也就是火影服务器任务刷新的时间）

        Args:
            flag: 更新下次执行时间的模式
                0：创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                1：正常执行完毕，更新为下次执行的时间
                2：立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                3：把执行时间推迟delta时间，要求 delta!=None
            delta: 延迟的时长
        Returns:

        """
        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)
        next_execute_time = current_time
        match flag:
            case 0:  # 创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                next_execute_time = self.next_execute_time

            case 1:  # 正常执行完毕，更新为下次执行的时间
                next_day = current_time + timedelta(days=1)
                next_execute_time = next_day.replace(hour=18, minute=0, second=0, microsecond=0)

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                next_execute_time = current_time

            case 3:  # 把执行时间推迟delta时间，要求 delta!=None
                if delta is None:
                    self.logger.warning(f"update_next_execute_time传入的delta为空")
                    return False, None
                next_execute_time = current_time + delta

        self.logger.info(f"下次执行时间为：{next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
        self.config.set_task_base_config(self.task_name, "下次执行时间", int(next_execute_time.timestamp()))
        return True, next_execute_time
