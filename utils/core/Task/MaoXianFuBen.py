from utils.core.Task.BaseTask import BaseTask

class MaoXianFuBen(BaseTask):

    def _execute(self):
        self.logger.debug(f"开始执行")
        try:
            # 确定在主场景
            if not self.home():
                raise self.StepFailedError("无法回到[主场景]")

            self.logger.debug("进入[冒险]")
            if not self.click_and_wait({
                'type': "ELEMENT",
                'name': "冒险"
            }):
                raise self.StepFailedError("无法进入[冒险]")

            self.logger.debug("进入[精英副本]")
            if not self.click_and_wait({
                'type': "ELEMENT",
                'name': "冒险-精英副本"
            }):
                raise self.StepFailedError("无法进入[精英副本]")

            self.logger.debug("进入[便捷扫荡]")
            if not self.click_and_wait({
                'type': "ELEMENT",
                'name': "冒险-精英副本-便捷扫荡"
            }):
                raise self.StepFailedError("无法进入[便捷扫荡]")
            if not self.detect_and_wait({
                'type': "SCENE",
                'name': "冒险-精英副本-便捷扫荡"
            }):
                raise self.StepFailedError("[便捷扫荡]未出现")

            self.logger.debug("检查是否选择[勾选上次扫荡副本]")
            if not self.click_and_wait({
                'type': "ELEMENT",
                'name': "冒险-精英副本-便捷扫荡-勾选上次扫荡副本-未选中"
            }):
                self.logger.debug("未选中[勾选上次扫荡副本]，已自动选择")

            self.logger.debug("点击扫荡")
            if not self.click_and_wait({
                'type': "ELEMENT",
                'name': "冒险-精英副本-便捷扫荡-扫荡"
            }):
                raise self.StepFailedError("点击[扫荡]失败")
            if self.detect_and_wait({
                'type': "ELEMENT",
                'name': "冒险-精英副本-便捷扫荡-扫荡-勾选的副本都已经扫荡完毕"
            }, wait_time=0, max_time=0.3):
                raise self.EndEarly("勾选的副本都已经扫荡完毕，提前退出执行")
            if self.detect_and_wait({
                'type': "ELEMENT",
                'name': "冒险-精英副本-便捷扫荡-扫荡-请选中至少一个需要扫荡的副本"
            }, wait_time=0, max_time=0.3):
                self.logger.debug("未勾选需要扫荡的副本")
                if not self.click_and_wait({
                    'type': "ELEMENT",
                    'name': "冒险-精英副本-便捷扫荡-一键全选-未选中"
                }):
                    raise self.StepFailedError("全选失败，提前退出执行")
                if not self.click_and_wait({
                    'type': "ELEMENT",
                    'name': "冒险-精英副本-便捷扫荡-扫荡"
                }):
                    raise self.StepFailedError("全选后点击[扫荡]失败")

            if self.click_and_wait({
                'type': "ELEMENT",
                'name': "冒险-精英副本-便捷扫荡-扫荡-继续扫荡"
            }):
                self.logger.debug("确认继续扫荡")
            self.logger.debug("扫荡开始，等待扫荡结束")
            while not self.click_and_wait({
                'type': "ELEMENT",
                'name': "冒险-精英副本-便捷扫荡-扫荡结束-确定"
            }):
                # 处理体力不足的情况
                if self.detect_and_wait({
                    'type': "ELEMENT",
                    'name': "冒险-精英副本-便捷扫荡-体力不足"
                }):
                    self.logger.warning("精英副本便捷扫荡体力不足，提前退出执行")
                    # 点掉体力不足弹窗
                    self.click_and_wait({
                        "type": "COORDINATE",
                        'coordinate': [1364, 152]
                    })
                    break
            self.logger.debug("扫荡任务结束")
            # 点掉扫荡信息弹窗
            self.click_and_wait({
                "type": "COORDINATE",
                'coordinate': [1364, 152]
            })
            self._update_next_execute_time()
        except self.StepFailedError as e:
            self.logger.error(e)
        except self.EndEarly as e:
            self._update_next_execute_time()
            self.logger.warning(e)
        finally:
            self.home()
            self.logger.debug(f"执行完毕")
            self.callback(self)
