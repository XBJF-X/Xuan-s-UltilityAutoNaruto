from utils.core.Task.BaseTask import BaseTask


class DengLuJiangLi(BaseTask):
    def _execute(self):
        self.logger.info(f"开始执行")
        try:
            # 确定在登录奖励界面
            if self.home(home_name="登录奖励", max_attempts=5):
                # 点击领取
                self.click_and_wait({
                    "type": "ELEMENT",
                    "name": "登录奖励-领取"
                }, wait_time=3)
            else:
                self.logger.info(f"登录奖励已领取或由于没有重新登录导致未刷新")
            self._update_next_execute_time()
        except self.StepFailedError as e:
            self.logger.error(e)
        except self.EndEarly as e:
            self._update_next_execute_time()
            self.logger.warning(e)
        finally:
            self.home()
            self.logger.info(f"执行完毕")
            self.callback(self)
