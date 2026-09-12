import logging
import time
from typing import Dict

import cv2
import numpy as np

from backend.tools.resource_db import ResourceDBManager
from backend.tools.resource_model import Scene, Element
from backend.core.legacy.Enums import ElementType


class SceneGraph:
    """场景有向图管理类，负责维护场景和跳转关系"""

    def __init__(self, resource_db_manager: ResourceDBManager, parent_logger: logging.Logger | str = ""):
        if isinstance(parent_logger, str):
            self.logger = logging.getLogger(self.__class__.__name__)
        else:
            self.logger = parent_logger.getChild(self.__class__.__name__)
        self.scenes: Dict[str, Scene] = {}  # 场景字典，键为场景名称
        # 保留 ResourceDBManager 引用：供 SceneIndex 在（重建时）读取最新场景转移边
        self._resource_db = resource_db_manager
        template_sum = 0
        start = time.perf_counter()

        for scene in resource_db_manager.get_all_scenes():
            for element in scene.elements:
                if element.type == ElementType.IMG:
                    template_sum += 1
                    # 处理BGRA图像（数据库仅存 4 通道 BGRA 原始字节，gray/mask 在运行时推导）
                    if element.bgra:
                        try:
                            bgra_buf = np.frombuffer(element.bgra, dtype=np.uint8)
                            bgra = cv2.imdecode(bgra_buf, cv2.IMREAD_UNCHANGED)
                            if bgra is None:
                                self.logger.warning(f"场景{scene.name}的元素{element.name} BGRA图像解码失败")
                            else:
                                element.bgra = np.ascontiguousarray(bgra)
                                # 从 BGRA 推导灰度图/掩码（gray/mask 已不入库，作为运行时附加属性）
                                # 注意：SQLModel extra="allow" 下 __pydantic_extra__ 可能为 None，
                                # 直接赋值会触发 item assignment 错误，故用 object.__setattr__ 绕过
                                gray = cv2.cvtColor(
                                    element.bgra[:, :, :3], cv2.COLOR_BGR2GRAY).astype(np.uint8)
                                object.__setattr__(element, "gray", gray)
                                if element.bgra.shape[-1] == 4:
                                    mask = (element.bgra[:, :, 3] > 0).astype(np.uint8) * 255
                                else:
                                    mask = np.ones_like(gray, dtype=np.uint8) * 255
                                object.__setattr__(element, "mask", mask)
                        except Exception as e:
                            self.logger.error(f"处理场景{scene.name}的元素{element.name} BGRA时出错: {str(e)}")

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
