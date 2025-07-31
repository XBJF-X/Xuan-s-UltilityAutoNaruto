from typing import Dict

from utils.core.Base.Recognizer import Recognizer
from utils.core.Controller import Controller


class Detecter:
    def __init__(self, recognizer: Recognizer, controller: Controller):
        self.controller = controller
        self.recognizer = recognizer

    def detect(self, params: Dict) -> bool:
        """
        检测是否为某个Scene或者某个Element是否存在

        :param params:字典，包含type和name两个键
        :return:检测到与否
        """
        # start = time.perf_counter()
        screen = self.controller.screen_cap()
        # second = time.perf_counter()
        if params['type'] == "SCENE":
            flag, confidence = self.recognizer.scene_match(screen,params['name'])
            # print(f"[CAP]{(second - start) * 1000:.1f} ms [MATCH]{(time.perf_counter() - second) * 1000:.1f} ms")
            return flag
        elif params['type'] == "ELEMENT":
            coordinates = self.recognizer.element_match(screen, params['name'])
            # print(f"[CAP]{(second - start) * 1000:.1f} ms [MATCH]{(time.perf_counter() - second) * 1000:.1f} ms")
            return len(coordinates) != 0
