from datetime import datetime, timedelta, time

from utils.Base.Exceptions import StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class DongRiYanHuaJi(BaseTask):
    source_scene = "冬日烟花季-主页"
    start_line = time(19, 0)
    dead_line = time(22, 0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bool_light_fireworks = False
        
    def run(self):
        receive_btn = self.operationer.get_element("领取", "冬日烟花季-主页")
        close_red_packet_btn = self.operationer.get_element("关闭红包", "冬日烟花季-主页")
        if receive_btn is None or close_red_packet_btn is None:
            raise StepFailedError("冬日烟花季关键元素缺失，无法初始化连点坐标")
        self.operationer.clicker.update_coordinates([
            (receive_btn.coordinate_x, receive_btn.coordinate_y),
            (close_red_packet_btn.coordinate_x, close_red_packet_btn.coordinate_y)
        ])
        super().run()
        

    @TransitionOn()
    def _(self):
        if not self.bool_light_fireworks:
            self.operationer.clicker.stop()
            self.operationer.click_and_wait("点燃烟火")
            self.operationer.click_and_wait("免费烟火")
            self.bool_light_fireworks = True
            return False
        self.operationer.clicker.start()
        return False

    @TransitionOn("冬日烟花季-点燃免费爆竹")
    def _(self):
        self.operationer.click_and_wait("是")
        return False

    def reset_task_exe_prog(self) -> bool:
        self.bool_light_fireworks = False
        return True
