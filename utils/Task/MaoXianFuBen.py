from datetime import timedelta

from utils.Task.BaseTask import BaseTask


class MaoXianFuBen(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")

        self.logger.info("进入[冒险]")
        self.click_and_wait({'type': "ELEMENT", 'name': "冒险"})

        self.logger.info("进入[精英副本]")
        self.click_and_wait({'type': "ELEMENT", 'name': "冒险-精英副本"})

        self.logger.info("进入[便捷扫荡]")
        self.click_and_wait({'type': "ELEMENT", 'name': "冒险-精英副本-便捷扫荡"})
        self.detect_and_wait({'type': "SCENE", 'name': "冒险-精英副本-便捷扫荡"})

        self.logger.info("检查是否选择[勾选上次扫荡副本]")
        if self.click_and_wait(
                {'type': "ELEMENT", 'name': "冒险-精英副本-便捷扫荡-勾选上次扫荡副本-未选中"},
                auto_raise=False
        ):
            self.logger.warning("未选中[勾选上次扫荡副本]，已自动选择")

        self.logger.info("点击扫荡")
        self.click_and_wait({'type': "ELEMENT", 'name': "冒险-精英副本-便捷扫荡-扫荡"})
        if self.detect_and_wait(
                {'type': "ELEMENT", 'name': "冒险-精英副本-便捷扫荡-扫荡-勾选的副本都已经扫荡完毕"},
                wait_time=0,
                max_time=0.3,
                auto_raise=False
        ):
            self._update_next_execute_time()
            raise self.EndEarly("勾选的副本都已经扫荡完毕，提前退出执行")
        if self.detect_and_wait(
                {'type': "ELEMENT", 'name': "冒险-精英副本-便捷扫荡-扫荡-请选中至少一个需要扫荡的副本"},
                wait_time=0,
                max_time=0.3,
                auto_raise=False
        ):
            self.logger.warning("未勾选需要扫荡的副本，即将全选")
            self.click_and_wait({'type': "ELEMENT", 'name': "冒险-精英副本-便捷扫荡-一键全选-未选中"})
            self.click_and_wait({'type': "ELEMENT", 'name': "冒险-精英副本-便捷扫荡-扫荡"})

        if self.click_and_wait({'type': "ELEMENT", 'name': "冒险-精英副本-便捷扫荡-扫荡-继续扫荡"}):
            self.logger.info("确认继续扫荡")
        self.logger.info("扫荡开始，等待扫荡结束")
        while not self.click_and_wait(
                {'type': "ELEMENT", 'name': "冒险-精英副本-便捷扫荡-扫荡结束-确定"},
                auto_raise=False
        ):
            # 处理体力不足的情况
            if self.detect_and_wait(
                    {'type': "ELEMENT", 'name': "冒险-精英副本-便捷扫荡-体力不足"},
                    auto_raise=False
            ):
                self.logger.warning("精英副本便捷扫荡体力不足，提前退出执行")
                # 点掉体力不足弹窗
                self.click_and_wait({"type": "COORDINATE",'coordinate': [1364, 152]})
                break
        self.logger.info("扫荡任务结束")
        # 点掉扫荡信息弹窗
        self.click_and_wait({"type": "COORDINATE",'coordinate': [1364, 152]})
        self._update_next_execute_time()
