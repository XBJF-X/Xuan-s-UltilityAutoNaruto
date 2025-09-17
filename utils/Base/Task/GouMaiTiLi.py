from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Base.Exceptions import EndEarly, StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class GouMaiTiLi(BaseTask):
    source_scene = "购买体力"
    task_max_duration = timedelta(minutes=3)

    @TransitionOn()
    def _(self):
        times = self.config.get_task_exe_prog("购买体力", "已购买体力次数")
        if times < self.config.get_task_exe_param("购买体力", "购买体力次数"):
            self.operationer.click_and_wait("购买", wait_time=1)
            times += 1
            self.config.set_task_exe_prog("购买体力", "已购买体力次数", times)
            self.logger.info(f"已购买体力 {times} 次")
            return False
        self.operationer.click_and_wait("X")
        self.config.set_task_exe_prog("购买体力", "已购买体力次数", 0)
        self.activate_another_task_signal.emit("装备合成")
        self.update_next_execute_time()
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
        times = self.config.get_task_exe_prog("购买体力", "已购买体力次数")
        times -= 1
        self.config.set_task_exe_prog("购买体力", "已购买体力次数", times)
        return False

