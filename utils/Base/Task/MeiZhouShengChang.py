from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Task import MeiRiShengChang
from utils.Base.Task.BaseTask import TransitionOn


class MeiZhouShengChang(MeiRiShengChang):
    source_scene = "忍术对战-单人模式"

    @TransitionOn()
    def _(self):
        self.logger.info("查看[决斗场-忍术对战-单人模式-决斗任务]")
        self.operationer.click_and_wait("忍术对战-单人模式-决斗任务")
        self.operationer.detect_scene("忍术对战-单人模式-决斗任务")
        self.logger.info("领取所有待领取的决斗任务宝箱")
        while self.operationer.click_and_wait(
                "宝箱-待领取",
                auto_raise=False
        ):
            continue

        # 假如周胜场没满，则继续挂周胜
        while not self.operationer.detect_element(
                "满胜场",
                max_time=1,
                auto_raise=False
        ):
            self.logger.warning("周胜场未满，继续执行")
            # 点掉决斗任务窗口
            self.operationer.click_and_wait("X")
            self.fight()
            self.logger.info("查看[决斗场-忍术对战-单人模式-决斗任务]")
            self.operationer.click_and_wait("决斗任务")
            self.operationer.detect_scene("忍术对战-单人模式-决斗任务")
            self.logger.info("领取所有待领取的决斗任务宝箱")
            while self.operationer.click_and_wait(
                    "宝箱-待领取",
                    max_time=3,
                    auto_raise=False
            ):
                continue
        self.logger.warning("周胜场已满")
        # 点掉决斗任务弹窗
        self.operationer.click_and_wait("X")
        self._update_next_execute_time()
        return True

    def _update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        match flag:

            case 0:  # 创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                next_exec_ts = self.data.get('下次执行时间')
                if next_exec_ts == 0:
                    # 若初始值为0，设置为本周日12点
                    # 计算下一个周日的日期
                    # weekday() 返回：0=周一, 1=周二, ..., 6=周日
                    days_until_sunday = (6 - current_time.weekday()) % 7
                    next_sunday = current_time + timedelta(days=days_until_sunday)

                    # 设置时间为本周日12:00:00
                    self.next_execute_time = datetime(
                        next_sunday.year, next_sunday.month, next_sunday.day, 12, 0, 0,
                        tzinfo=china_tz
                    )
                else:
                    # 从时间戳转换为datetime对象（指定UTC时区避免歧义）
                    self.next_execute_time = datetime.fromtimestamp(next_exec_ts, tz=china_tz)

            case 1:  # 正常执行完毕，更新为下次执行的时间
                # 计算下一个周日的日期
                # weekday() 返回：0=周一, 1=周二, ..., 6=周日
                days_until_sunday = (6 - current_time.weekday()) % 7
                next_sunday = current_time + timedelta(days=days_until_sunday+7)

                # 设置时间为下周日12:00:00
                self.next_execute_time = datetime(
                    next_sunday.year, next_sunday.month, next_sunday.day, 12, 0, 0,
                    tzinfo=china_tz
                )

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                self.next_execute_time = datetime.now(china_tz)

            case 3:  # 把执行时间推迟delta时间，要求 delta!=None
                if delta is None:
                    self.logger.warning(f"update_next_execute_time传入的delta为空")
                    return
                self.next_execute_time = current_time + delta

            case _:
                self.logger.warning(f"请检查update_next_execute_time传入的参数：flag={flag},delta={delta}")
                return

        self.logger.info(f"下次执行时间为：{self.next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
        self.config.set_task_config(self.task_name, "下次执行时间", int(self.next_execute_time.timestamp()))