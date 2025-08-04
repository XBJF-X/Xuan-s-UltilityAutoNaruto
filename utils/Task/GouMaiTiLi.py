from utils.Task.BaseTask import BaseTask


class GouMaiTiLi(BaseTask):

    def _execute(self):
        self.logger.info(f"开始执行")
        try:
            # 确定在主场景
            if not self.home():
                raise self.StepFailedError("无法回到[主场景]")
            self.click_and_wait({
                'type': "COORDINATE",
                "coordinate": [675, 50]
            })
            if self.detect_and_wait({
                'type': "SCENE",
                'name': "购买体力"
            }):
                times = 0
                while times < self.data.get("购买体力次数", 0):
                    if self.click_and_wait({
                        'type': "ELEMENT",
                        "name": "购买体力-购买"
                    }):
                        if not self.pass_secondary_password():
                            times += 1
                            self.logger.info(f"已购买体力 {times} 次")
                # 随便点下返回主场景
                self.click_and_wait({
                    'type': "COORDINATE",
                    "coordinate": [1550, 50]
                })
            else:
                raise self.StepFailedError("[购买体力]未出现")
            self._update_next_execute_time()
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
