from utils.Task.BaseTask import BaseTask


class GouMaiTiLi(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        if self.config.get_config("已购买体力次数") >= self.data.get("购买体力次数", 0):
            self._update_next_execute_time()
            self.config.set_config("已购买体力次数", 0)
            raise self.EndEarly("已完成购买体力次数")
        self.click_and_wait({'type': "COORDINATE", "coordinate": [675, 50]})
        self.detect_and_wait({'type': "SCENE", 'name': "购买体力"})
        times = self.config.get_config('已购买体力次数')
        while times < self.data.get("购买体力次数", 0):
            self.click_and_wait({'type': "ELEMENT", "name": "购买体力-购买"})
            if not self.pass_secondary_password():
                times += 1
                self.config.set_config('已购买体力次数', times)
                self.logger.info(f"已购买体力 {times} 次")
        # 随便点下返回主场景
        self.click_and_wait({'type': "COORDINATE", "coordinate": [1550, 50]})
        self.config.set_config('已购买体力次数', 0)
        self._update_next_execute_time()
