from datetime import timedelta

from utils.Task.BaseTask import BaseTask


class PuTongRenZheZhaoMu(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")

        self.logger.info("进入[招募]界面")
        # 点击招募图标
        self.click_and_wait({"type": "ELEMENT", "name": "主场景-招募"})
        # 确认招募界面出现
        self.detect_and_wait({"type": "SCENE", "name": "招募"})
        self.logger.info("切换普通招募")
        # 切换普通招募
        self.click_and_wait({"type": "COORDINATE", "coordinate": [117, 426]})
        self.logger.info("进行免费普通招募")
        # 点击普通招募-免费
        if self.click_and_wait(
                {"type": "ELEMENT", "name": "普通招募-免费"},
                auto_raise=False
        ):
            self.logger.info("免费普通招募成功")
            # 点击普通招募-确定
            while not self.search_and_click(
                    [
                        {"type": "ELEMENT", "name": "普通招募-确定"}
                    ],
                    [
                        {
                            "click": {
                                "type": "COORDINATE",
                                "coordinate": [800, 730]
                            }
                        }
                    ],
                    max_attempts=2,
                    once_max_time=5
            ):
                continue
        else:
            self.logger.warning("免费普通招募失败")
            self._update_next_execute_time(delta=timedelta(hours=3))
        self._update_next_execute_time()
