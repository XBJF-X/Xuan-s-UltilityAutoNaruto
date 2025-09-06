import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Union, List, Optional, Tuple

from StaticFunctions import split_gray_alpha, get_real_path
from tool.ResourceManager.SyncSrc import sync_directories
from utils.Base.Enums import ElementType, MatchType


class SceneResourceManager:
    def __init__(self, scenes_path: Path):
        self.logger = logging.getLogger("场景资源管理器")
        self.scenes_path = scenes_path
        self.scenes_info_path = scenes_path / "ScenesInfo.json"
        self.scenes: Dict[str, Scene] = {}
        self.global_info: Dict[str, Any] = {}  # 存储全局信息
        self._initialize_global_info()
        self._reload_scenes()

    def _initialize_global_info(self):
        """初始化全局场景信息文件"""
        if not self.scenes_info_path.exists():
            self.logger.info(f"创建全局场景信息文件: {self.scenes_info_path}")
            self.global_info = {}
            self.save_global_info()
        else:
            self.global_info = self._load_global_info()

    def _load_global_info(self) -> Dict[str, Any]:
        """加载全局场景信息"""
        try:
            with open(self.scenes_info_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.error(f"加载全局场景信息失败: {e}")
            return {}

    def save_global_info(self):
        """保存全局场景信息"""
        with open(self.scenes_info_path, 'w', encoding='utf-8') as f:
            json.dump(self.global_info, f, indent=4, ensure_ascii=False)
        sync_directories(
            Path(get_real_path("raw_src/Template/Scene")),
            Path(get_real_path("src/Template/Scene"))
        )

    def _reload_scenes(self):
        """重新加载所有场景资源"""
        self.scenes = self._load_scenes_resources()

    def _load_scenes_resources(self) -> Dict[str, Scene]:
        """加载所有场景资源"""
        self.logger.debug(f"加载{self.scenes_path}中的场景")
        scenes = {}

        # 确保场景根目录存在
        self.scenes_path.mkdir(parents=True, exist_ok=True)

        # 遍历场景目录
        for scene_dir in self.scenes_path.iterdir():
            if not scene_dir.is_dir() or scene_dir.name == "__pycache__":
                continue

            scene_id = scene_dir.name
            # self.logger.debug(f"处理场景: {scene_id}")

            # 获取或初始化场景信息
            scene_info = self.global_info.get(scene_id, {})
            if not scene_info:
                scene_info = self._create_default_scene_info()
                self.global_info[scene_id] = scene_info
                self.save_global_info()

            # 确保元素目录存在
            element_dir = scene_dir / "Element"
            element_dir.mkdir(parents=True, exist_ok=True)

            # 扫描元素图片并更新全局信息
            self._scan_and_update_elements(scene_id, element_dir)

            # 创建场景对象
            elements = {}
            for element_id, element_info in scene_info.get("elements", {}).items():
                elements[element_id] = Element(
                    id=element_id,
                    dir=element_dir,
                    type=element_info.get('type', ElementType.IMG.value),
                    threshold=element_info.get('threshold', 0.8),
                    ratio=element_info.get('ratio', [0.5, 0.5]),
                    match_type=element_info.get('match_type', MatchType.TEMPLATE.value),
                    roi=element_info.get('roi', [0, 0, 1600, 900]),
                    coordinate=element_info.get('coordinate', [0, 0])
                )
            scene_gray_dir = scene_dir / "GARY"
            scene_mask_dir = scene_dir / "MASK"

            # 确保场景图片目录存在
            scene_gray_dir.mkdir(parents=True, exist_ok=True)
            scene_mask_dir.mkdir(parents=True, exist_ok=True)

            scene_bgra_path = scene_dir / f"Scene.png"
            scene_gray_path = scene_gray_dir / f"Scene.png"
            scene_mask_path = scene_mask_dir / f"Scene.png"
            if scene_bgra_path.exists():
                if not scene_gray_path.exists() or not scene_mask_path.exists():
                    split_gray_alpha(
                        scene_bgra_path,
                        scene_bgra_path,
                        scene_gray_path,
                        scene_mask_path
                    )

            scenes[scene_id] = Scene(
                id=scene_id,
                elements=elements,
                dir=scene_dir,
                edges=scene_info.get('edges', []),
                threshold=scene_info.get('threshold', 0.8),
            )

        self.logger.info(f"场景加载完成，共加载{len(scenes)}个场景")
        return scenes

    @staticmethod
    def _create_default_scene_info() -> Dict[str, Any]:
        """创建默认场景信息结构"""
        return {
            "edges": [],
            "threshold": 0.8,
            "elements": {}
        }

    @staticmethod
    def _create_default_element_info() -> Dict[str, Any]:
        """创建默认元素信息结构"""
        return {
            "type": ElementType.IMG.value,
            "match_type": MatchType.TEMPLATE.value,
            "threshold": 0.8,
            "ratio": [0.5, 0.5],
            "roi": [0, 0, 1600, 900],
            "coordinate": [0, 0]
        }

    def _scan_and_update_elements(self, scene_id: str, element_dir: Path):
        """扫描元素目录并更新全局信息"""
        # 确保必要的目录结构存在
        gray_dir = element_dir / "GARY"
        mask_dir = element_dir / "MASK"
        gray_dir.mkdir(parents=True, exist_ok=True)
        mask_dir.mkdir(parents=True, exist_ok=True)

        # 扫描所有PNG文件
        element_ids = set()
        for item in element_dir.glob("*.png"):
            if item.is_file():
                element_ids.add(item.stem)

        # 获取当前场景的元素信息
        scene_info = self.global_info.get(scene_id, self._create_default_scene_info())
        elements_info = scene_info.get("elements", {})

        # 添加新元素到全局信息
        updated = False
        for element_id in element_ids:
            if element_id not in elements_info:
                elements_info[element_id] = self._create_default_element_info()
                updated = True
                self.logger.info(f"添加新元素到全局信息: {scene_id}/{element_id}")

        # 更新过时元素信息
        for element_id, info in elements_info.items():
            element_bgra_path = element_dir / f"{element_id}.png"
            element_gray_path = gray_dir / f"{element_id}.png"
            element_mask_path = mask_dir / f"{element_id}.png"
            if element_bgra_path.exists():
                if not element_gray_path.exists() or not element_mask_path.exists():
                    split_gray_alpha(
                        element_bgra_path,
                        element_bgra_path,
                        element_gray_path,
                        element_mask_path
                    )
            # 确保有默认值
            defaults = self._create_default_element_info()
            for key, default_val in defaults.items():
                if key not in info:
                    info[key] = default_val
                    updated = True
        # 如果有更新，保存全局信息
        if updated:
            scene_info["elements"] = elements_info
            self.global_info[scene_id] = scene_info
            self.save_global_info()

    def get_scene(self, scene_id: str) -> Optional[Scene]:
        """获取指定场景"""
        return self.scenes.get(scene_id)

    def add_scene(self,
                  scene_id: str,
                  threshold: float = 0.8
                  ):
        """添加新场景"""
        if scene_id in self.global_info:
            self.logger.warning(f"场景已存在: {scene_id}")
            return False

        scene_info = self._create_default_scene_info()
        scene_info["threshold"] = threshold
        self.global_info[scene_id] = scene_info
        self.save_global_info()

        # 创建场景目录结构
        scene_dir = self.scenes_path / scene_id
        scene_dir.mkdir(parents=True, exist_ok=True)
        (scene_dir / "GARY").mkdir(parents=True, exist_ok=True)
        (scene_dir / "MASK").mkdir(parents=True, exist_ok=True)
        (scene_dir / "Element" / "GARY").mkdir(parents=True, exist_ok=True)
        (scene_dir / "Element" / "MASK").mkdir(parents=True, exist_ok=True)

        # 重新加载场景
        self._reload_scenes()
        self.logger.info(f"成功添加场景: {scene_id}")
        return True

    def delete_scene(self, scene_id: str):
        """删除场景及其所有资源"""
        if scene_id not in self.global_info:
            self.logger.warning(f"场景不存在: {scene_id}")
            return False

        # 删除目录
        scene_dir = self.scenes_path / scene_id
        if scene_dir.exists():
            try:
                shutil.rmtree(scene_dir)
                self.logger.info(f"已删除场景目录: {scene_dir}")
            except Exception as e:
                self.logger.error(f"删除场景目录失败: {e}")
                return False
        # 清除其他节点到被删除节点的边
        for s_scene, _ in self.scenes.items():
            self.remove_edge(s_scene, scene_id)

        # 删除全局信息
        del self.global_info[scene_id]
        self.save_global_info()

        # 重新加载场景
        self._reload_scenes()
        self.logger.info(f"成功删除场景: {scene_id}")
        return True

    def update_scene_info(self, scene_id: str, **kwargs):
        """更新场景信息"""
        if scene_id not in self.global_info:
            self.logger.error(f"场景不存在: {scene_id}")
            return False

        scene_info = self.global_info[scene_id]
        valid_keys = ["edges", "threshold"]

        for key, value in kwargs.items():
            if key in valid_keys:
                scene_info[key] = value
            else:
                self.logger.warning(f"无效的场景信息字段: {key}")

        self.global_info[scene_id] = scene_info
        self.save_global_info()
        self._reload_scenes()
        self.logger.info(f"已更新场景信息: {scene_id}")
        return True

    def rename_scene(self, old_id: str, new_id: str) -> bool:
        """
        场景更名
        Args:
            old_id: 原场景ID
            new_id: 新场景ID

        Returns: 操作是否成功
        """
        if old_id not in self.global_info:
            self.logger.error(f"场景不存在: {old_id}")
            return False

        if new_id in self.global_info:
            self.logger.error(f"新场景ID已存在: {new_id}")
            return False

        # 1. 重命名场景目录
        old_scene_dir = self.scenes_path / old_id
        new_scene_dir = self.scenes_path / new_id
        try:
            old_scene_dir.rename(new_scene_dir)
            self.logger.debug(f"场景目录已重命名: {old_scene_dir} -> {new_scene_dir}")
        except Exception as e:
            self.logger.error(f"重命名场景目录失败: {e}")
            return False

        # 2. 更新全局信息中其他场景指向该场景的边
        for scene_id in self.global_info:
            scene_info = self.global_info[scene_id]
            # 替换边中的旧ID为新ID
            new_edges = [edge if edge != old_id else new_id for edge in scene_info.get("edges", [])]
            if new_edges != scene_info.get("edges", []):
                scene_info["edges"] = new_edges
                self.global_info[scene_id] = scene_info

        # 3. 迁移原场景信息到新ID
        self.global_info[new_id] = self.global_info.pop(old_id)
        self.save_global_info()

        # 4. 重新加载场景
        self._reload_scenes()
        self.logger.info(f"场景已重命名: {old_id} -> {new_id}")
        return True

    def update_element_info(self, scene_id: str, element_id: str, **kwargs):
        """更新元素信息"""
        if scene_id not in self.global_info:
            self.logger.error(f"场景不存在: {scene_id}")
            return False

        scene_info = self.global_info[scene_id]
        elements = scene_info.get("elements", {})

        if element_id not in elements:
            self.logger.error(f"元素不存在: {scene_id}/{element_id}")
            return False

        element_info = elements[element_id]
        valid_keys = ["type", "threshold", "match_type", "ratio", "roi", "coordinate"]

        for key, value in kwargs.items():
            if key in valid_keys:
                element_info[key] = value
            else:
                self.logger.warning(f"无效的元素信息字段: {key}")

        elements[element_id] = element_info
        scene_info["elements"] = elements
        self.global_info[scene_id] = scene_info
        self.save_global_info()
        self._reload_scenes()
        self.logger.info(f"已更新元素信息: {scene_id}/{element_id}")
        return True

    def rename_element(self, scene_id: str, old_id: str, new_id: str) -> bool:
        """
        元素更名
        Args:
            scene_id: 元素所属场景ID
            old_id: 原元素ID
            new_id: 新元素ID

        Returns: 操作是否成功
        """
        if scene_id not in self.global_info:
            self.logger.error(f"场景不存在: {scene_id}")
            return False

        scene_info = self.global_info[scene_id]
        elements_info = scene_info.get("elements", {})

        if old_id not in elements_info:
            self.logger.error(f"元素不存在: {scene_id}/{old_id}")
            return False

        if new_id in elements_info:
            self.logger.error(f"新元素ID已存在: {scene_id}/{new_id}")
            return False

        # 1. 如果是图像类型元素，重命名对应的图片文件
        element_type = elements_info[old_id].get("type", ElementType.IMG.value)
        if element_type == ElementType.IMG.value:
            element_dir = self.scenes_path / scene_id / "Element"
            # 原文件路径
            old_bgra_path = element_dir / f"{old_id}.png"
            old_gray_path = element_dir / "GARY" / f"{old_id}.png"
            old_mask_path = element_dir / "MASK" / f"{old_id}.png"
            # 新文件路径
            new_bgra_path = element_dir / f"{new_id}.png"
            new_gray_path = element_dir / "GARY" / f"{new_id}.png"
            new_mask_path = element_dir / "MASK" / f"{new_id}.png"

            # 重命名文件
            try:
                if old_bgra_path.exists():
                    old_bgra_path.rename(new_bgra_path)
                if old_gray_path.exists():
                    old_gray_path.rename(new_gray_path)
                if old_mask_path.exists():
                    old_mask_path.rename(new_mask_path)
                self.logger.debug(f"元素图片已重命名: {old_id} -> {new_id}")
            except Exception as e:
                self.logger.error(f"重命名元素图片失败: {e}")
                return False

        # 2. 更新全局信息中的元素ID
        elements_info[new_id] = elements_info.pop(old_id)
        scene_info["elements"] = elements_info
        self.global_info[scene_id] = scene_info
        self.save_global_info()

        # 3. 重新加载场景
        self._reload_scenes()
        self.logger.info(f"元素已重命名: {scene_id}/{old_id} -> {scene_id}/{new_id}")
        return True
    def add_element_to_scene(self, scene_id: str, element_id: str, **kwargs):
        """添加新元素到场景"""
        if scene_id not in self.global_info:
            self.logger.error(f"场景不存在: {scene_id}")
            return False

        scene_info = self.global_info[scene_id]
        elements_info = scene_info.get("elements", {})

        if element_id in elements_info:
            self.logger.warning(f"元素已存在: {scene_id}/{element_id}")
            return False
        element_info = self._create_default_element_info()
        valid_keys = ["type", "threshold", "match_type", "ratio", "roi", "coordinate"]

        for key, value in kwargs.items():
            if key in valid_keys:
                element_info[key] = value
            else:
                self.logger.warning(f"无效的元素信息字段: {key}")

        # 添加新元素信息
        elements_info[element_id] = element_info
        scene_info["elements"] = elements_info
        self.global_info[scene_id] = scene_info
        self.save_global_info()

        # 创建元素目录结构
        element_dir = self.scenes_path / scene_id / "Element"
        gray_dir = element_dir / "GARY"
        mask_dir = element_dir / "MASK"
        gray_dir.mkdir(parents=True, exist_ok=True)
        mask_dir.mkdir(parents=True, exist_ok=True)

        # 重新加载场景
        self._reload_scenes()
        return True

    def delete_element_from_scene(self, scene_id: str, element_id: str):
        """删除场景中的元素"""
        if scene_id not in self.global_info:
            self.logger.error(f"场景不存在: {scene_id}")
            return False

        scene_info = self.global_info[scene_id]
        elements = scene_info.get("elements", {})

        if element_id not in elements:
            self.logger.error(f"元素不存在: {scene_id}/{element_id}")
            return False

        # 删除图片文件
        element_dir = self.scenes_path / scene_id / "Element"
        bgra_path = element_dir / (element_id + ".png")
        gray_path = element_dir / "GARY" / (element_id + ".png")
        mask_path = element_dir / "MASK" / (element_id + ".png")

        try:
            bgra_path.unlink(missing_ok=True)
            gray_path.unlink(missing_ok=True)
            mask_path.unlink(missing_ok=True)
        except Exception as e:
            self.logger.error(f"删除元素图片失败: {e}")

        # 删除全局信息
        del elements[element_id]
        scene_info["elements"] = elements
        self.global_info[scene_id] = scene_info
        self.save_global_info()

        # 重新加载场景
        self._reload_scenes()
        self.logger.info(f"成功删除元素: {scene_id}/{element_id}")
        return True

    def add_edge(self, s_scene_id, t_scene_id):
        scene_info = self.global_info[s_scene_id]
        scene_info['edges'].append(t_scene_id)

        self.global_info[s_scene_id] = scene_info
        self.save_global_info()
        self._reload_scenes()
        self.logger.info(f"已连接边: [{s_scene_id}] -> [{t_scene_id}]")
        return True

    def remove_edge(self, s_scene_id, t_scene_id):
        scene_info = self.global_info[s_scene_id]
        if t_scene_id in scene_info['edges']:
            scene_info['edges'].remove(t_scene_id)
            self.global_info[s_scene_id] = scene_info
            self.logger.info(f"已移除边: [{s_scene_id}] -> [{t_scene_id}]")
            self.save_global_info()
            self._reload_scenes()
        return True
