from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class ZuZhiQiFu(BaseTask):
    source_scene = "组织祈福"
    task_max_duration = timedelta(minutes=3)

    @TransitionOn()
    def _(self):
        if not self.config.get_task_exe_prog(self.task_name, "祈福", False):
            # 点击组织祈福-超影免费
            if not self.operationer.click_and_wait(
                    "超影免费",
                    auto_raise=False,
                    wait_time=2
            ):
                self.logger.info("超影祈福不存在，点击焚香祈福")
                # 点击组织祈福-焚香祈福
                self.operationer.click_and_wait("焚香祈福")
                self.logger.info("[焚香祈福]成功")
            else:
                self.logger.info("点击超影祈福")
            self.config.set_task_exe_prog(self.task_name, "祈福", True)
            return False
        elif not self.config.get_task_exe_prog(self.task_name, "昨日奖励领取", False):
            # 点击昨日奖励
            if not self.operationer.click_and_wait("昨日奖励", max_time=3):
                self.logger.warning("昨日奖励已领取或昨日祈福人数不足15")
                self.config.set_task_exe_prog(self.task_name, "昨日奖励领取", True)
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
        self.config.set_task_exe_prog(self.task_name, "昨日奖励领取", True)
        return False

    @TransitionOn("恭喜你获得")
    def _(self):
        self.logger.info("祈福奖励领取成功")
        self.config.set_task_exe_prog(self.task_name, "祈福", True)
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("组织祈福-今日次数已达上限")
    def _(self):
        self.logger.info("今日祈福次数已达上限")
        self.config.set_task_exe_prog(self.task_name, "祈福", True)
        self.operationer.click_and_wait("确定")
        return False

    def reset_task_exe_proc(self) -> bool:
        self.config.set_task_exe_prog(self.task_name, "祈福", False)
        self.config.set_task_exe_prog(self.task_name, "昨日奖励领取", False)
        return True
