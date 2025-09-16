from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class ZuZhiQiFu(BaseTask):
    source_scene = "组织祈福"
    task_max_duration = timedelta(minutes=3)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flag_1 = False
        self.flag_2 = False

    @TransitionOn()
    def _(self):
        if not self.flag_1:
            # 点击组织祈福-超影免费
            if not self.operationer.click_and_wait(
                    "超影免费",
                    auto_raise=False
            ):
                self.logger.info("超影祈福不存在，点击焚香祈福")
                # 点击组织祈福-焚香祈福
                self.operationer.click_and_wait("焚香祈福")
                self.logger.info("[焚香祈福]成功")
                self.flag_1 = True
            else:
                self.logger.info("点击超影祈福")
                self.flag_1 = True
            return False
        elif not self.flag_2:
            # 点击昨日奖励
            if not self.operationer.click_and_wait(
                    "昨日奖励",
                    auto_raise=False
            ):
                self.logger.warning("昨日奖励已领取或昨日祈福人数不足15")
                self.flag_2 = True
            return False
        self.update_next_execute_time()
        return True

    @TransitionOn("昨日奖励")
    def _(self):
        # 点击所有的领取按钮
        while self.operationer.click_and_wait(
                "领取",
                auto_raise=False
        ):
            continue
        # 随便点下关掉弹窗
        self.operationer.click_and_wait("X")
        self.logger.info("昨日奖励领取成功")
        self.flag_2 = True
        return False

    @TransitionOn("恭喜你获得")
    def _(self):
        self.logger.info("祈福奖励领取成功")
        self.flag_1 = True
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("组织祈福-今日次数已达上限")
    def _(self):
        self.logger.info("今日祈福次数已达上限")
        self.flag_1 = True
        self.operationer.click_and_wait("确定")
        return False

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
