from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Exceptions import EndEarly, StepFailedError
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
        self.logger.info("进行免费招财")
        while self.operationer.click_and_wait("免费一次"):
            continue
        self.config.set_task_exe_prog("金币招财", "已招财次数", 2)

        times = self.config.get_task_exe_prog("金币招财", "已招财次数")
        while times < self.config.get_task_exe_param("金币招财", "招财次数"):
            self.operationer.click_and_wait("金币招财")
            if not self.operationer.pass_secondary_password():
                times += 1
                self.config.set_task_exe_prog("金币招财", "已招财次数", times)
                self.logger.info(f"已招财 {times} 次")
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        self.config.set_task_exe_prog("金币招财", "已招财次数", 0)
        return True

    @TransitionOn("二级密码")
    def _(self):
        self.logger.debug("出现二级密码窗口")
        passward = self.config.get_config("二级密码")
        if len(passward) != 6:
            raise StepFailedError("请检查二级密码！")
        # 输入操作
        self.operationer.click_and_input(
            self.operationer.get_element("输入框"),
            passward
        )
        # 点击二级密码-确定
        if not self.operationer.click_and_wait(
                self.operationer.get_element("确定"),
                auto_raise=False
        ):
            raise StepFailedError("二级密码验证失败")
        return False
