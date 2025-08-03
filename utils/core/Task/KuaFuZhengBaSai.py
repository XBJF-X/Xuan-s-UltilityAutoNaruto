from utils.core.Task.BaseTask import BaseTask


class KuaFuZhengBaSai(BaseTask):
    def _execute(self):
        self.logger.info(f"开始执行")
        try:
            # 确定在主场景
            if not self.home():
                raise self.StepFailedError("无法回到[主场景]")

            # 执行逻辑部分

            self._update_next_execute_time()
        except self.StepFailedError as e:
            self.logger.error(e)
        except self.EndEarly as e:
            self._update_next_execute_time()
            self.logger.warning(e)
        finally:
            self.home()
            self.callback(self)
