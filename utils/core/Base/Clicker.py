import logging
import time
from typing import Dict, Tuple

from utils.core.Base.Recognizer import Recognizer
from utils.core.Controller import Controller


class Clicker:
    def __init__(self, recognizer: Recognizer, controller: Controller, element_templates: Dict):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.controller = controller
        self.recognizer = recognizer
        self.element_templates = element_templates

    def click(self, params: Dict, resolution: Tuple, times=1):
        # start = time.perf_counter()
        if params['type'] == "COORDINATE":
            x, y = params['coordinate']
            self.logger.debug(f"[COORDINATE] Click ({x},{y})")
            self.controller.click_position(params['coordinate'], resolution, times)
            return True
        elif params['type'] == "ELEMENT":
            screen = self.controller.screen_cap()
            second = time.perf_counter()
            coordinates = self.recognizer.element_match(screen, params['name'])
            # print(f"[CAP]{(second - start) * 1000:.1f} ms [MATCH]{(time.perf_counter() - second) * 1000:.1f}")
            if coordinates:
                coordinate = coordinates[0]
                x_ratio, y_ratio = self.element_templates[params['name']]["ratio"]
                # 按照元素可点击位置相对于模版左上角，相对整体的比例确定点击坐标
                x, y = (coordinate[0] * (1 - x_ratio) + coordinate[2] * x_ratio), (
                        coordinate[1] * (1 - y_ratio) + coordinate[3] * y_ratio)
                self.logger.debug(f"[{params['name']}] Click ({x},{y})")
                self.controller.click_position((x, y), resolution, times)
                return True
            else:
                return False
