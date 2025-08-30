from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Base.Exceptions import EndEarly
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class MaoXianFuBen(BaseTask):
    source_scene = "精英副本-便捷扫荡"
    task_max_duration = timedelta(minutes=3)

    @TransitionOn()
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
                self.operationer.current_scene.elements.get("勾选的副本都已经扫荡完毕"),
                self.operationer.current_scene.elements.get("扫荡-请选中至少一个需要扫荡的副本"),
                self.operationer.current_scene.elements.get("体力不足"),
            ],
            [],
            search_max_time=1,
            once_max_time=0.2,
            wait_time=0
        )
        match flag:
            case 1:
                self.update_next_execute_time()
                raise EndEarly("勾选的副本都已经扫荡完毕，提前退出执行")
            case 2:
                self.logger.warning("未勾选需要扫荡的副本，即将全选")
                self.operationer.click_and_wait("一键全选-未选中")
                self.operationer.click_and_wait("扫荡")
            case 3:
                self.logger.warning("精英副本便捷扫荡体力不足，提前退出执行")
                # 点掉体力不足弹窗
                self.operationer.click_and_wait("X")
                self.logger.info("扫荡任务结束")
                # 点掉扫荡信息弹窗
                self.operationer.click_and_wait("X")
                self._activate_another_task("装备合成")
                self.update_next_execute_time()
                return True

        if self.operationer.click_and_wait("扫荡-继续扫荡"):
            self.logger.info("确认继续扫荡")
        self.logger.info("扫荡开始，等待扫荡结束")
        while not self.operationer.click_and_wait(
                "扫荡结束-确定",
                max_time=0.3,
                auto_raise=False
        ):
            # 处理体力不足的情况
            if self.operationer.detect_element(
                    "体力不足",
                    max_time=0.3,
                    auto_raise=False
            ):
                self.logger.warning("精英副本便捷扫荡体力不足，提前退出执行")
                # 点掉体力不足弹窗
                self.operationer.click_and_wait("X")
                break
        self.logger.info("扫荡任务结束")
        # 点掉扫荡信息弹窗
        self.operationer.click_and_wait("X")
        self._activate_another_task("装备合成")
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
                    self.next_execute_time = datetime.now(ZoneInfo("Asia/Shanghai"))
                else:
                    # 从时间戳转换为datetime对象（指定UTC时区避免歧义）
                    self.next_execute_time = datetime.fromtimestamp(next_exec_ts, tz=ZoneInfo("Asia/Shanghai"))

            case 1:  # 正常执行完毕，更新为下次执行的时间
                next_day = current_time + timedelta(days=1)
                # 新建时间时指定时区（与current_time一致）
                self.next_execute_time = datetime(
                    next_day.year, next_day.month, next_day.day, 5, 0,
                    tzinfo=china_tz  # 关键：添加时区信息
                )

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                self.next_execute_time = datetime.now(ZoneInfo("Asia/Shanghai"))

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