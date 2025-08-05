from utils.Task.BaseTask import BaseTask


class Example(BaseTask):
    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")

        # 执行逻辑部分

        self._update_next_execute_time()
