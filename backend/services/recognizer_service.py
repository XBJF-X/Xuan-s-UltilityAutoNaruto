"""场景识别服务 - 封装 Recognizer + SceneGraph"""
import logging
from pathlib import Path
from typing import Optional

from backend.utils import get_real_path
from backend.tools.resource_db import ResourceDBManager
from backend.core.scene_graph import SceneGraph
from backend.core.recognizer_engine import Recognizer


class RecognizerService:
    def __init__(self):
        self.logger = logging.getLogger("RecognizerService")
        self._scene_graph: Optional[SceneGraph] = None
        self._recognizer: Optional[Recognizer] = None
        self._db: Optional[ResourceDBManager] = None

    def _lazy_init(self):
        if self._recognizer is None:
            self._db = ResourceDBManager(Path(get_real_path("src")))
            self._scene_graph = SceneGraph(self._db)
            self._recognizer = Recognizer(self._scene_graph)

    def recognize(self, image_bytes: bytes) -> str:
        self._lazy_init()
        import cv2
        import numpy as np
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return "未知场景"
        result = self._recognizer.scene(img)
        if isinstance(result, str):
            return result
        return result.name if result else "未知场景"