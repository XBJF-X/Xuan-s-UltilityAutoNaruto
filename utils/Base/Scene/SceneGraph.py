import logging
import time
from typing import Dict

import cv2
import numpy as np

from tool.ResourceManager.ResourceDBManager import ResourceDBManager
from tool.ResourceManager.model import Scene, Element
from utils.Base.Enums import ElementType


class SceneGraph:
    """场景有向图管理类，负责维护场景和跳转关系"""

    def __init__(self, resource_db_manager: ResourceDBManager, parent_logger: logging.Logger | str = ""):
        if isinstance(parent_logger, str):
            self.logger = logging.getLogger(self.__class__.__name__)
        else:
            self.logger = parent_logger.getChild(self.__class__.__name__)
        self.scenes: Dict[str, Scene] = {}  # 场景字典，键为场景名称
        template_sum = 0
        start = time.perf_counter()

        for scene in resource_db_manager.get_all_scenes():
            for element in scene.elements:
                if element.type == ElementType.IMG:
                    template_sum += 1
                    # 处理BGRA图像
                    if element.bgra:
                        try:
                            bgra_buf = np.frombuffer(element.bgra, dtype=np.uint8)
                            bgra = cv2.imdecode(bgra_buf, cv2.IMREAD_UNCHANGED)
                            if bgra is None:
                                self.logger.warning(f"场景{scene.name}的元素{element.name} BGRA图像解码失败")
                            else:
                                element.bgra = np.ascontiguousarray(bgra)
                        except Exception as e:
                            self.logger.error(f"处理场景{scene.name}的元素{element.name} BGRA时出错: {str(e)}")

                    # 处理mask图像
                    if element.mask:
                        try:
                            mask_buf = np.frombuffer(element.mask, dtype=np.uint8)
                            mask = cv2.imdecode(mask_buf, cv2.IMREAD_GRAYSCALE)
                            if mask is None:
                                self.logger.warning(f"场景{scene.name}的元素{element.name} MASK图像解码失败")
                            else:
                                element.mask = np.ascontiguousarray(mask)
                        except Exception as e:
                            self.logger.error(f"处理场景{scene.name}的元素{element.name} MASK时出错: {str(e)}")

                    # 处理gray图像
                    if element.gray:
                        try:
                            gray_buf = np.frombuffer(element.gray, dtype=np.uint8)
                            gray = cv2.imdecode(gray_buf, cv2.IMREAD_GRAYSCALE)
                            if gray is None:
                                self.logger.warning(f"场景{scene.name}的元素{element.name} GRAY图像解码失败")
                            else:
                                element.gray = np.ascontiguousarray(gray)
                        except Exception as e:
                            self.logger.error(f"处理场景{scene.name}的元素{element.name} GRAY时出错: {str(e)}")

            # 将场景添加到场景字典中，键为场景名称
            self.scenes[scene.name] = scene
        self.logger.debug(f"场景加载完成，共加载{len(self.scenes)}个场景,{template_sum}个图片元素,消耗{time.perf_counter() - start:.2f}秒")

    def get_scene(self, scene_name: str) -> Scene | None:
        """根据场景名称获取场景对象"""
        return self.scenes.get(scene_name, None)

    def get_element(self, scene_name: str, element_name: str) -> Element | None:
        """根据场景名称和元素名称获取元素对象"""
        scene = self.get_scene(scene_name)
        if scene:
            element = scene.element_dict.get(element_name, None)
            if element:
                return element
            self.logger.error(f"获取[{scene_name}]的[{element_name}]元素失败")
            return None
        self.logger.error("场景不存在，无法获取元素")
        return None


if __name__ == "__main__":
    s = SceneGraph(ResourceDBManager())
