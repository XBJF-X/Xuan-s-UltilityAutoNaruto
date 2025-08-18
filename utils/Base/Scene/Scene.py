import json
import logging
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from utils.Base.Scene.Element import Element


class Scene:
    """
    场景有向图中的场景节点
    """

    def __init__(self,
                 id: str,
                 elements: Optional[Dict[str, Element]] = None,
                 **kwargs):
        self.logger = logging.getLogger(f"[SCENE-{id}]")
        self.id = id  # 唯一标识
        self.elements = elements or {}
        """该场景中所有的元素"""
        self.dir: Path = kwargs.get('dir')
        """场景相关的所有资源存放的文件夹"""
        self.gray = kwargs.get('gray', None)
        """场景的灰度图，在资源管理器中不使用"""
        self.mask = kwargs.get('mask', None)
        """场景的蒙版，用于忽略不需要的部分，在资源管理器中不使用"""
        self.rgb: Tuple[float, float, float] | None = kwargs.get('rgb', None)
        """图像在蒙版有效范围内的RGB均色"""

        # 自此以下是JSON中会存储的信息（不包括elements）

        self.edges: List[str] = kwargs.get('edges', [])
        """存储所有出边的场景ID"""
        self.threshold: float = kwargs.get('threshold', 0.8)
        """场景识别的阈值"""
