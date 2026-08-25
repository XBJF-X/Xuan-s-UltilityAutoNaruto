from datetime import timedelta
import re

from backend.core.legacy.Exceptions import TaskCompleted, StepFailedError, TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn


class JinBiZhaoCai(BaseTask):
    source_scene = "招财"
    task_max_duration = timedelta(minutes=3)

    def run(self):
        self.target_times=self.config.get_task_exe_param("金币招财", "招财次数")
        self.process_times=0
        self.buy_times=0
        return super().run()

    @TransitionOn()
    def _(self):
        yzccs=self.operationer.ocr_recognize("已招财次数")
        if yzccs:
            pattern = re.compile(
                r'第\s*(\d+)\s*/\s*(\d+)\s*轮\s*[，,]\s*累积投币\s*[:：]\s*(\d+)\s*/\s*(\d+)'
            )
            match = pattern.search(yzccs[0].text)
            if match:
                current_round, total_round, current_coin, total_coin = map(int, match.groups())
                self.process_times = total_coin * (current_round - 1) + current_coin
                self.logger.info(f"识别到当前已金币招财 {self.process_times} 次")
            else:
                raise StepFailedError("识别已招财次数失败，自动退出执行")

        if self.process_times>=self.target_times:
            raise TaskCompleted("已招满金币招财")

        if self.process_times < self.target_times:
            self.operationer.click_and_wait("金币招财")
            # self.process_times += 1
            self.logger.info(f"已招财 {self.process_times+1} 次")
            return False

        self.operationer.click_and_wait("X")
        raise TaskCompleted("任务执行完成")
    

    # @TransitionOn("二级密码")
    # def _(self):
    #     self.logger.debug("出现二级密码窗口")
    #     passward = self.config.get_config("二级密码")
    #     if len(passward) != 6:
    #         raise StepFailedError("请检查二级密码是否留空或漏位！")
    #     # 输入操作
    #     self.operationer.click_and_input(
    #         self.operationer.get_element("输入框"),
    #         passward
    #     )
    #     # 点击二级密码-确定
    #     if not self.operationer.click_and_wait(self.operationer.get_element("确定")):
    #         raise StepFailedError("二级密码验证失败")

    #     self.process_times -= 1
    #     self.logger.info(f"招财次数回退，已招财 {self.process_times} 次")
    #     return False

    # def reset_task_exe_prog(self) -> bool:
    #     self.config.set_task_exe_prog("金币招财", "已招财次数", 0)
    #     return True
