from datetime import timedelta, datetime, time, date
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn

armor_coodinates = [
    "武器",
    "头盔",
    "胸甲",
    "忍之书",
    "项链",
    "戒指"
]


class ZhuangBeiHeCheng(BaseTask):
    source_scene = "装备"
    task_max_duration = timedelta(minutes=3)

    @TransitionOn()
    def _(self):
        # 点击配置设置中选中的装备
        self.operationer.click_and_wait(armor_coodinates[self.data.get("合成目标装备", 0)])
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

    @TransitionOn("体力不足")
    def _(self):
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        return True

    def update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        match flag:

            case 0:  # 创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                next_exec_ts = self.data.get('下次执行时间')
                if next_exec_ts == 0:
                    # 若初始值为0，设置为当前UTC时间（或其他合理时间）
                    self.next_execute_time = datetime.now(china_tz)
                else:
                    # 从时间戳转换为datetime对象（指定UTC时区避免歧义）
                    self.next_execute_time = datetime.fromtimestamp(next_exec_ts, tz=china_tz)

            case 1:  # 正常执行完毕，更新为下次执行的时间
                today = date.today()

                # 创建今天5点和16点的datetime对象
                today_5am = datetime.combine(today, time(5, 0), tzinfo=china_tz)
                today_16pm = datetime.combine(today, time(16, 0), tzinfo=china_tz)

                # 情况1：当前时间小于今天5点
                if current_time < today_5am:
                    # 新建时间时指定时区（与current_time一致）
                    self.next_execute_time = datetime(
                        current_time.year, current_time.month, current_time.day, 5, 0,
                        tzinfo=china_tz  # 关键：添加时区信息
                    )

                # 情况2：当前时间在今天5点到16点之间
                elif today_5am <= current_time < today_16pm:
                    to_16pm = today_16pm - current_time
                    self.next_execute_time = current_time + min(to_16pm, timedelta(hours=3))

                # 情况3：当前时间过了今天16点
                else:  # now >= today_16pm
                    next_day = current_time + timedelta(days=1)
                    # 新建时间时指定时区（与current_time一致）
                    self.next_execute_time = datetime(
                        next_day.year, next_day.month, next_day.day, 5, 0,
                        tzinfo=china_tz  # 关键：添加时区信息
                    )

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                self.next_execute_time = datetime.now(china_tz)

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
