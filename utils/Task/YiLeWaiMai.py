from datetime import timedelta

from utils.Task.BaseTask import BaseTask

class YiLeWaiMai(BaseTask):

    def _execute(self):
        self.logger.info(f"开始执行")
        try:
            # 确定在主场景
            if not self.home():
                raise self.StepFailedError("无法回到[主场景]")
            self.logger.info("进入[活动]")
            if not self.click_and_wait({
                'type': "ELEMENT",
                'name': "主场景-活动"
            }):
                raise self.StepFailedError("进入[活动]失败")
            if not self.detect_and_wait({
                'type': "SCENE",
                'name': "活动"
            }):
                raise self.StepFailedError("[活动]未出现")
            self.logger.info("进入[一乐外卖]")
            if not self.click_and_wait({
                'type': "ELEMENT",
                'name': "活动-一乐外卖-选中"
            }):
                if not self.click_and_wait({
                    'type': "ELEMENT",
                    'name': "活动-一乐外卖-选中"
                }):
                    raise self.StepFailedError("进入[一乐外卖]失败")
            self.logger.info("开始领取[一乐外卖]")
            takeout_sum = 0
            while self.click_and_wait({
                'type': "ELEMENT",
                'name': "活动-一乐外卖-待领取"
            }):
                takeout_sum += 1
                self.logger.info(f"已领取了 {takeout_sum} 份外卖")
                continue
            if takeout_sum == 0:
                self._update_next_execute_time(delta=timedelta(hours=1))
            else:
                self._update_next_execute_time(time_offset=timedelta(hours=11))
        except self.StepFailedError as e:
            self.logger.error(e)
        except self.EndEarly as e:
            self._update_next_execute_time()
            self.logger.warning(e)
        except self.Stop as e:
            self.logger.warning("线程被要求停止")
        finally:
            self.home()
            self.logger.info(f"执行完毕")
            self.callback(self)
