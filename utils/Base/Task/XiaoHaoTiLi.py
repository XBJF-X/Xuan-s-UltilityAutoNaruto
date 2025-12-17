from datetime import timedelta, datetime, time, date
from zoneinfo import ZoneInfo

from utils.Base.Exceptions import EndEarly
from utils.Base.Task.BaseTask import BaseTask, TransitionOn

armor_coodinates = [
    "武器",
    "头盔",
    "胸甲",
    "忍之书",
    "项链",
    "戒指"
]

# Todo：增加刷修罗副本的功能
class XiaoHaoTiLi(BaseTask):
    source_scene = "主场景"
    task_max_duration = timedelta(minutes=3)

    @TransitionOn()
    def _(self):
        if not self.config.get_task_exe_param(self.task_name, "体力消耗方式", 0):
            self.operationer.next_scene = "装备"
        else:
            self.operationer.next_scene = "精英副本-便捷扫荡"
        return False

    @TransitionOn("装备")
    def _(self):
        # 点击配置设置中选中的装备
        self.operationer.click_and_wait(
            armor_coodinates[self.config.get_task_exe_param(self.task_name, "合成目标装备", 0)])
        # 先看看当前装备能不能进阶，毕竟进阶说明没有能扫荡的了
        if self.operationer.click_and_wait(
                "进阶",
                auto_raise=False,
                max_time=0.5
        ):
            self.logger.info("当前装备可进阶，已点击进阶")
        if self.operationer.click_and_wait("可装备", auto_raise=False):
            self.operationer.click_and_wait("一键添加")
            self.logger.warning("存在[可装备]装备，已一键添加")
        elif self.operationer.click_and_wait("可合成", auto_raise=False):
            self.logger.debug("存在[可合成]装备，将合成")
        elif self.operationer.click_and_wait("可扫荡", auto_raise=False):
            self.logger.debug("点击[装备]")
        return False

    @TransitionOn("装备-材料详情")
    def _(self):
        if self.operationer.click_and_wait("一键扫荡", auto_raise=False):
            self.logger.debug("点击[一键扫荡]")
        elif self.operationer.click_and_wait("合成", auto_raise=False):
            self.logger.debug("点击[合成]")
        elif self.operationer.click_and_wait("装备", auto_raise=False):
            self.logger.debug("点击[装备]")
        return False

    @TransitionOn("材料详情-扫荡")
    def _(self):
        # 勾选自动停止
        if self.operationer.click_and_wait("材料足够后自动停止-未选中", auto_raise=False):
            self.logger.warning("未勾选自动停止，已经勾选")
        self.operationer.click_and_wait("开始扫荡")
        return False

    @TransitionOn("扫荡-继续扫荡")
    def _(self):
        self.operationer.click_and_wait("继续扫荡")
        return False

    @TransitionOn("扫荡-已足够")
    def _(self):
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("精英副本-便捷扫荡")
    def _(self):
        self.logger.info("检查是否选择[勾选上次扫荡副本]")
        if self.operationer.click_and_wait(
                "勾选上次扫荡副本-未选中",
                auto_raise=False
        ):
            self.logger.warning("未选中[勾选上次扫荡副本]，已自动选择")

        self.logger.info("点击扫荡")
        self.operationer.click_and_wait("扫荡")
        flag = self.operationer.search_and_detect(
            [
                self.operationer.get_element("勾选的副本都已经扫荡完毕"),
                self.operationer.get_element("扫荡-请选中至少一个需要扫荡的副本")
            ],
            [],
            search_max_time=1,
            once_max_time=0.2,
            wait_time=0
        )
        match flag:
            case 1:
                if not self.config.get_task_exe_prog(self.task_name, "任务1执行结束", False):
                    if not self.config.get_task_exe_param(self.task_name, "体力消耗方式", 0):
                        self.operationer.next_scene = "精英副本-便捷扫荡"
                    else:
                        self.operationer.next_scene = "装备"
                    self.config.set_task_exe_prog(self.task_name, "任务1执行结束", True)
                    return False
                self.update_next_execute_time()
                self.config.set_task_exe_prog(self.task_name, "任务1执行结束", False)
                return True
            case 2:
                self.logger.warning("未勾选需要扫荡的副本，即将全选")
                self.operationer.click_and_wait("一键全选-未选中")
                self.operationer.click_and_wait("扫荡")
                return False

    @TransitionOn("便捷扫荡-扫荡结束")
    def _(self):
        self.operationer.click_and_wait("确定")
        if not self.config.get_task_exe_prog(self.task_name, "任务1执行结束", False):
            if not self.config.get_task_exe_param(self.task_name, "体力消耗方式", 0):
                self.operationer.next_scene = "精英副本-便捷扫荡"
            else:
                self.operationer.next_scene = "装备"
            self.config.set_task_exe_prog(self.task_name, "任务1执行结束", True)
            return False
        self.update_next_execute_time()
        self.config.set_task_exe_prog(self.task_name, "任务1执行结束", False)
        return True

    @TransitionOn("便捷扫荡-继续扫荡")
    def _(self):
        self.operationer.click_and_wait("继续扫荡")
        self.logger.info("扫荡开始，等待扫荡结束")
        return False

    @TransitionOn("体力不足")
    def _(self):
        self.operationer.click_and_wait("X")
        self.config.set_task_exe_prog(self.task_name, "任务1执行结束", False)
        self.update_next_execute_time()
        return True

    def _handle_execution_completed(self, current_time: datetime) -> datetime:
        """处理任务执行完成后的时间更新（case1）"""
        china_tz = current_time.tzinfo
        today = date.today()

        # 创建今天5点和16点的datetime对象
        today_5am = datetime.combine(today, time(5, 0), tzinfo=china_tz)
        today_16pm = datetime.combine(today, time(16, 0), tzinfo=china_tz)

        # 情况1：当前时间小于今天5点
        if current_time < today_5am:
            # 新建时间时指定时区（与current_time一致）
            next_execute_time = datetime(
                current_time.year, current_time.month, current_time.day, 5, 0,
                tzinfo=china_tz  # 关键：添加时区信息
            )

        # 情况2：当前时间在今天5点到16点之间
        elif today_5am <= current_time < today_16pm:
            to_16pm = today_16pm - current_time
            next_execute_time = current_time + min(to_16pm, timedelta(hours=3))

        # 情况3：当前时间过了今天16点
        else:  # now >= today_16pm
            next_day = current_time + timedelta(days=1)
            # 新建时间时指定时区（与current_time一致）
            next_execute_time = datetime(
                next_day.year, next_day.month, next_day.day, 5, 0,
                tzinfo=china_tz  # 关键：添加时区信息
            )
        return next_execute_time
