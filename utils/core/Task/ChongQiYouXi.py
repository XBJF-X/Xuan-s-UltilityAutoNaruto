from utils.core.Task.BaseTask import BaseTask


class ChongQiYouXi(BaseTask):
    def _execute(self):
        self.logger.debug(f"开始执行")
        try:
            self.restart()
            while not self.click_and_wait({
                'type': "ELEMENT",
                'name': "进入游戏-开始游戏"
            }):
                # 再处理遇到没有默认授权，需要登陆的情况
                continue
            self.logger.debug("点击开始游戏")
            while not self.detect_and_search(
                    [
                        {'type': "SCENE", 'name': "主场景"},
                        {'type': "ELEMENT", 'name': "X"}
                    ],
                    [],
                    1
            ):
                continue
            self.logger.debug("成功进入游戏")

        except self.StepFailedError as e:
            self.logger.error(e)
        except self.EndEarly as e:
            self.logger.warning(e)
        finally:
            self.logger.debug(f"执行完毕")
            self.callback(self)
