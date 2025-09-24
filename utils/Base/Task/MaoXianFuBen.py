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
                self.update_next_execute_time()
                raise EndEarly("勾选的副本都已经扫荡完毕，提前退出执行")
            case 2:
                self.logger.warning("未勾选需要扫荡的副本，即将全选")
                self.operationer.click_and_wait("一键全选-未选中")
                self.operationer.click_and_wait("扫荡")
                return False

    @TransitionOn("便捷扫荡-扫荡结束")
    def _(self):
        self.operationer.click_and_wait("确定")
        return True

    @TransitionOn("便捷扫荡-继续扫荡")
    def _(self):
        self.operationer.click_and_wait("继续扫荡")
        self.logger.info("扫荡开始，等待扫荡结束")
        return False

    @TransitionOn("体力不足")
    def _(self):
        self.operationer.click_and_wait("X")
        self._activate_another_task("消耗体力")
        self.update_next_execute_time()
        return True

