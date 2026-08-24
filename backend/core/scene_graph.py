"""场景有向图 - 从 utils/Base/Scene/SceneGraph.py 迁移"""
import logging
import time
from typing import Dict

import cv2
import numpy as np

from backend.tools.resource_db import ResourceDBManager
from backend.tools.resource_model import Scene, Element
from backend.core.enums import ElementType


class SceneGraph:
    """场景有向图管理类，负责维护场景和跳转关系"""

    def __init__(self, resource_db_manager: ResourceDBManager, parent_logger: logging.Logger | str = ""):
        if isinstance(parent_logger, str) or not parent_logger:
            self.logger = logging.getLogger(self.__class__.__name__)
        else:
            self.logger = parent_logger.getChild(self.__class__.__name__)
        self.scenes: Dict[str, Scene] = {}
        template_sum = 0
        start = time.perf_counter()

        for scene in resource_db_manager.get_all_scenes():
            for element in scene.elements:
                if element.type == ElementType.IMG:
                    template_sum += 1
                    if element.bgra:
                        try:
                            bgra_buf = np.frombuffer(element.bgra, dtype=np.uint8)
                            bgra = cv2.imdecode(bgra_buf, cv2.IMREAD_UNCHANGED)
                            if bgra is not None:
                                # 从 bgra 推导 gray/mask（原 gray/mask 列已废弃删除）
                                # 注：SQLModel extra="allow" 下 __pydantic_extra__ 可能为 None，
                                # 直接赋值会触发 item assignment 错误，用 object.__setattr__ 绕过
                                gray = cv2.cvtColor(
                                    bgra[:, :, :3], cv2.COLOR_BGR2GRAY).astype(np.uint8)
                                object.__setattr__(element, "gray", gray)
                                if bgra.shape[-1] == 4:
                                    mask = (bgra[:, :, 3] > 0).astype(np.uint8) * 255
                                else:
                                    mask = np.ones_like(gray, dtype=np.uint8) * 255
                                object.__setattr__(element, "mask", mask)
                                # 内存优化：识别链（template_match/sift_match）仅用 gray/mask，
                                # 解码后的 4 通道 bgra numpy 是最大的一块，立即释放（不持有）。
                                # 前端绘制/元素图片走 API 从数据库重新读取原始 bytes，不依赖此对象。
                                element.bgra = None
                            else:
                                self.logger.warning(f"场景{scene.name}的元素{element.name} BGRA图像解码失败")
                        except Exception as e:
                            self.logger.error(f"处理BGRA出错: {str(e)}")

            self.scenes[scene.name] = scene
        self.logger.debug(
            f"场景加载完成，共{len(self.scenes)}个场景,{template_sum}个图片元素,"
            f"耗时{time.perf_counter() - start:.2f}秒"
        )

    def get_scene(self, scene_name: str) -> Scene | None:
        return self.scenes.get(scene_name, None)

    def get_element(self, scene_name: str, element_name: str) -> Element | None:
        scene = self.get_scene(scene_name)
        if scene:
            element = scene.element_dict.get(element_name, None)
            if element:
                return element
            self.logger.error(f"获取[{scene_name}]的[{element_name}]元素失败")
            return None
        self.logger.error("场景不存在，无法获取元素")
        return None
