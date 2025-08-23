import json
import logging
from pathlib import Path
from typing import Dict, Any

import cv2
import numpy as np

from StaticFunctions import get_real_path, cv_imread
from utils.Base.Enums import ElementType, MatchType
from utils.Base.Scene.Element import Element
from utils.Base.Scene.Scene import Scene


class SceneGraph:
    """场景有向图管理类，负责维护场景和跳转关系"""

    def __init__(self, parent_logger, scenes_path=Path(get_real_path("src/Template/Scene"))):
        self.logger = parent_logger.getChild(self.__class__.__name__)
        self.scenes: Dict[str, Scene] = self.init_scenes(scenes_path)  # 场景ID到场景的映射

    def init_scenes(self, scenes_path):
        self.logger.debug(f"加载{scenes_path}中的场景")
        scenes = {}
        scenes_root = Path(scenes_path)
        scenes_info_path = scenes_root / "ScenesInfo.json"

        # 检查场景根目录是否存在
        if not scenes_root.exists() or not scenes_root.is_dir():
            self.logger.error(f"场景路径不存在或不是文件夹: {scenes_path}")
            return scenes
        if not scenes_info_path.exists():
            self.logger.error(f"场景信息文件不存在：{scenes_info_path}")
            return scenes

        scenes_info = self._load_json(scenes_info_path)
        for scene_id, scene_info in scenes_info.items():
            scene_dir = scenes_root / scene_id
            element_dir = scene_dir / "ELEMENT"
            element_gray_dir = element_dir / "GARY"
            element_mask_dir = element_dir / "MASK"
            elements = {}
            for element_id, element_info in scene_info.get('elements', {}).items():
                elements[element_id] = Element(
                    id=element_id,
                    dir=element_dir,
                    type=element_info.get('type', ElementType.IMG.value),
                    threshold=element_info.get('threshold', 0.8),
                    ratio=element_info.get('ratio', [0.5, 0.5]),
                    match_type=element_info.get('match_type', MatchType.TEMPLATE.value),
                    roi=element_info.get('roi', [0, 0, 1600, 900]),
                    coordinate=element_info.get('coordinate', [0, 0]),
                    gray=self._load_template(element_gray_dir / f"{element_id}.png"),
                    mask=self._load_template(element_mask_dir / f"{element_id}.png")
                )
            scene_gray_dir = scene_dir / "GARY"
            scene_mask_dir = scene_dir / "MASK"
            gray = self._load_template(scene_gray_dir / f"Scene.png")
            mask = self._load_template(scene_mask_dir / f"Scene.png")
            rgb = self._rgb_average(scene_dir / "Scene.png", mask)
            scenes[scene_id] = Scene(
                id=scene_id,
                elements=elements,
                dir=scene_dir,
                edges=scene_info.get('edges', []),
                threshold=scene_info.get('threshold', 0.8),
                gray=gray,
                mask=mask,
                rgb=rgb
            )

        self.logger.debug(f"场景加载完成，共加载{len(scenes)}个场景")
        return scenes

    def _load_template(self, path: Path):
        if not path.exists():
            # self.logger.warning(f"文件不存在: {path}，可能是坐标型元素")
            return None
        with open(path, 'rb') as f:
            array = np.frombuffer(f.read(), dtype=np.uint8)
            img = cv2.imdecode(array, cv2.IMREAD_GRAYSCALE)
            if img is None:
                self.logger.error(f"文件存在但无法读取: {path}")
                return None
            return img.astype(np.uint8)

    def _rgb_average(self, path: Path, mask=None):
        """
        计算图像在掩码有效区域内的RGB平均颜色

        参数:
            path: 图像文件路径
            mask: 外部掩码（可选），若无则使用图像自带的alpha通道

        返回:
            (r, g, b) 平均颜色元组，出错返回None
        """
        if not path.exists():
            # self.logger.warning(f"文件不存在: {path}，可能是坐标型元素")
            return None

        try:
            # 读取图像（保留alpha通道）
            with open(path, 'rb') as f:
                array = np.frombuffer(f.read(), dtype=np.uint8)
                img = cv2.imdecode(array, cv2.IMREAD_UNCHANGED)

            if img is None:
                self.logger.error(f"文件存在但无法读取: {path}")
                return None

            # 分离通道：OpenCV默认BGR(A)格式
            channels = cv2.split(img)
            b, g, r = channels[0:3]  # 提取BGR通道

            # 确定掩码
            if mask is not None:
                # 使用外部传入的掩码
                final_mask = mask
            elif img.shape[2] == 4:
                # 使用图像的alpha通道作为掩码
                _, final_mask = cv2.threshold(channels[3], 1, 255, cv2.THRESH_BINARY)
            else:
                # 无掩码时使用全白掩码
                final_mask = np.ones_like(b) * 255

            # 确保掩码是二值单通道
            if final_mask.ndim > 2:
                final_mask = cv2.cvtColor(final_mask, cv2.COLOR_BGR2GRAY)

            # 计算掩码区域内的平均颜色
            masked_pixels = final_mask > 0
            r_avg = int(np.mean(r[masked_pixels]))
            g_avg = int(np.mean(g[masked_pixels]))
            b_avg = int(np.mean(b[masked_pixels]))

            return r_avg, g_avg, b_avg

        except Exception as e:
            self.logger.error(f"计算平均颜色时出错: {str(e)}")
            return None

    def _load_json(self, json_path: Path) -> Dict[str, Any]:
        """辅助方法：读取JSON文件，处理异常"""
        if not json_path.exists() or not json_path.is_file():
            self.logger.warning(f"{json_path.name}不存在，返回空信息")
            return {}

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            self.logger.error(f"{json_path.name}格式错误，返回空信息")
            return {}
        except Exception as e:
            self.logger.error(f"读取{json_path.name}失败: {str(e)}")
            return {}


if __name__ == "__main__":
    sg = SceneGraph(get_real_path("refactor_src/Template/Scene"))
