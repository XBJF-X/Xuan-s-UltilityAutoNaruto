from datetime import datetime, timedelta, time

from backend.core.legacy.Exceptions import StepFailedError
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn


class GouWuTianXin(BaseTask):
    source_scene = "购物甜心"
    task_max_duration = timedelta(minutes=30)

    def run(self):
        buttons = []
        for i in range(1, 10):
            buttons.append(self.operationer.get_element(f"键位{i}", "购物甜心-内部"))
        self.operationer.clicker.update_coordinates([
            (button.coordinate_x, button.coordinate_y) for button in buttons
        ])
        super().run()

    @TransitionOn()
    def _(self):
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("成就奖励",wait_time=2)
        if not self.operationer.detect_element("领取",match_text="未完成"):
            self.logger.info("不存在未领取的奖励，结束执行")
            return True
        while self.operationer.search_and_click(
            ["领取"], 
            [{
            "swipe": {
                "start_coordinate": [1000, 680],
                "end_coordinate": [1000, 120],
                "duration": 0.5
            }
            }],
        max_attempts=3):
            continue
        self.operationer.click_and_wait("X")
        self.operationer.click_and_wait("开始游戏",wait_time=3.0)
        self.operationer.click_and_wait("开启购物",wait_time=3.0,stable_wait_for_new_scene=True)
        return False


    @TransitionOn("购物甜心-内部")
    def _(self):
        djs=self.operationer.ocr_recognize("倒计时")
        if djs and djs[0].extract_numbers()[0]<=2:
            self.operationer.clicker.stop()
            return False
        self.operationer.clicker.start()
        return False
