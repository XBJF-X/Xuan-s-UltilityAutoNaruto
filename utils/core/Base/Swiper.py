from typing import Dict, Tuple

from utils.core.Controller import Controller


class Swiper:
    def __init__(self, controller: Controller):
        self.controller = controller

    def swipe(self, params: Dict, resolution: Tuple):
        self.controller.swipe(
            params['start_coordinate'], params['end_coordinate'], params['duration'], resolution)
        return True
