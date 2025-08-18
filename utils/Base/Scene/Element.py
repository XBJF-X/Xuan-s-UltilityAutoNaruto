from pathlib import Path
from typing import Dict, Any, Tuple, List

from utils.Base.Enums import MatchType, ElementType


class Element:
    """
    场景中元素的抽象类
    """

    def __init__(self, id: str, **kwargs):
        self.id = id
        self.dir: Path = kwargs.get('dir')
        """元素图片存放的文件夹"""
        self.gray = kwargs.get('gray', None)
        """元素的灰度图，在资源管理器中不使用"""
        self.mask = kwargs.get('mask', None)
        """元素png的蒙版，用于忽略不需要的部分，在资源管理器中不使用"""

        # 自此以下是在JSON中会存储的信息

        self.type: ElementType = ElementType(kwargs.get('type', ElementType.IMG.value))
        """元素的类型：图片型/坐标型"""
        self.threshold: float = kwargs.get('threshold', 0.8)
        """元素识别的阈值"""
        self.ratio: List[float] = kwargs.get('ratio', [0.5, 0.5])
        """元素点击的位置在模版图中的比例"""
        self.match_type: MatchType = MatchType(kwargs.get('match_type', MatchType.TEMPLATE.value))
        """元素所用的匹配方式，默认模版匹配"""
        self.roi: List[int] = kwargs.get('roi', [0, 0, 1600, 900])
        """元素在图中的大致区域，格式为(x,y,width,height)"""
        self.coordinate: List[int] = kwargs.get('coordinate', [0, 0])
        """坐标型元素点击的坐标"""
