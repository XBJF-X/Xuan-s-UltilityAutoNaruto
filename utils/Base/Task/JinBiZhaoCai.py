from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Exceptions import EndEarly
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class JinBiZhaoCai(BaseTask):
    source_scene = "招财"
    task_max_duration = timedelta(minutes=3)

    @TransitionOn("招财")
    def _(self):
        if (self.config.get_task_exe_prog("金币招财", "已招财次数") >=
                self.config.get_task_exe_param("金币招财", "招财次数", 2)):
            self.update_next_execute_time()
            self.config.set_task_exe_prog("金币招财", "已招财次数", 0)
            raise EndEarly("已招满金币招财")
        # 确认免费招财按钮出现
        if self.operationer.detect_element(
                "免费一次",
                auto_raise=False
        ):
            # 点击两次招财-免费一次
            self.operationer.click_and_wait("免费一次")
            self.logger.info(f"已招财 1 次")
            self.operationer.click_and_wait("免费一次")
            self.logger.info(f"已招财 2 次")
        else:
            self.logger.debug("不存在免费招财次数")
        self.config.set_task_exe_param("金币招财", "已招财次数", 2)
        times = self.config.get_task_exe_prog("金币招财", "已招财次数")
        while times < self.config.get_task_exe_param("金币招财", "招财次数",):
            self.operationer.click_and_wait("金币招财")
            if not self.operationer.pass_secondary_password():
                times += 1
                self.config.set_task_exe_prog("金币招财", "已招财次数", times)
                self.logger.info(f"已招财 {times} 次")
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        self.config.set_task_exe_prog("金币招财", "已招财次数", 0)
        return True
