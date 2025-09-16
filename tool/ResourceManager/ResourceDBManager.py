from logging import Logger
from pathlib import Path
from typing import Optional, List

import cv2
import numpy as np
from sqlalchemy import create_engine, exc, text
from sqlalchemy.orm import joinedload
from sqlmodel import SQLModel, Session, select

from StaticFunctions import get_real_path
from tool.ResourceManager.model import Scene, Element, SceneEdge
from utils.Base.Enums import ElementType


class ResourceDBManager:
    _instance: Optional["ResourceDBManager"] = None
    connect_args = {
        "check_same_thread": False,
        "isolation_level": None
    }

    # 禁止通过 __init__ 重复创建实例
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # 首次创建实例时，调用 __init__ 初始化
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_dir: Path = Path(get_real_path("src")), parent_logger: Logger | str = ""):
        # 防止单例重复初始化（__new__ 会多次返回同一实例，__init__ 可能被多次调用）
        if hasattr(self, "_initialized") and self._initialized:
            return

        if isinstance(parent_logger, str):
            self.logger = logging.getLogger("资源管理器")
        else:
            self.logger = parent_logger.getChild("资源管理器")
        self.db_dir = db_dir
        self.db_file_path = db_dir / "database.db"
        self.sqlite_url = f"sqlite:///{self.db_file_path}"
        self.engine = create_engine(self.sqlite_url, connect_args=self.connect_args)
        self.create_db_and_tables()

    def create_db_and_tables(self):
        """创建数据库表结构"""
        try:
            SQLModel.metadata.create_all(self.engine)
            self.logger.info(f"数据库表结构已创建或更新，路径: {self.db_file_path}")
        except Exception as e:
            self.logger.error(f"创建数据库表结构失败: {str(e)}")
            raise

    def add_scene(self, name: str) -> bool:
        """
        添加新场景

        Args:
            name: 场景名称

        Returns: 操作是否成功
        """
        if not name or not isinstance(name, str):
            self.logger.error("场景名称不能为空且必须是字符串")
            return False

        try:
            with Session(self.engine) as session:
                # 检查场景是否已存在
                existing_scene = session.exec(select(Scene).where(Scene.name == name)).first()
                if existing_scene:
                    self.logger.warning(f"场景 '{name}' 已存在，无法重复添加")
                    return False

                # 创建并添加新场景
                scene = Scene(name=name)
                session.add(scene)
                session.commit()
                self.logger.info(f"场景 '{name}' 添加成功")
                return True

        except exc.SQLAlchemyError as e:
            self.logger.error(f"添加场景 '{name}' 失败: {str(e)}")
            return False

    def delete_scene(self, name: str) -> bool:
        """删除场景及其所有关联资源（包括边关系和元素）"""
        if not name:
            self.logger.error("场景名称不能为空")
            return False

        try:
            with Session(self.engine) as session:
                # 查找场景
                scene = session.exec(select(Scene).where(Scene.name == name)).first()
                if not scene:
                    self.logger.warning(f"删除失败，场景 '{name}' 不存在")
                    return False

                # 删除关联的边（出边和入边）
                outgoing_edges = session.exec(
                    select(SceneEdge).where(SceneEdge.source_scene_id == scene.id)
                ).all()
                incoming_edges = session.exec(
                    select(SceneEdge).where(SceneEdge.target_scene_id == scene.id)
                ).all()

                for edge in outgoing_edges + incoming_edges:
                    session.delete(edge)

                # 删除场景的所有元素
                elements = session.exec(
                    select(Element).where(Element.scene_id == scene.id)
                ).all()

                for element in elements:
                    session.delete(element)

                # 删除场景
                session.delete(scene)
                session.commit()
                self.logger.info(f"场景 '{name}' 及其所有元素和边关系已删除")
                return True

        except exc.SQLAlchemyError as e:
            self.logger.error(f"删除场景 '{name}' 失败: {str(e)}")
            return False

    def update_scene_info(self, name: str, **kwargs) -> bool:
        """
        更新场景信息

        Args:
            name: 场景名称
           ** kwargs: 要更新的字段，可包含: created_at, updated_at 等

        Returns: 操作是否成功
        """
        if not name:
            self.logger.error("场景名称不能为空")
            return False

        if not kwargs:
            self.logger.warning("没有提供任何要更新的字段")
            return True

        try:
            with Session(self.engine) as session:
                scene = session.exec(select(Scene).where(Scene.name == name)).first()
                if not scene:
                    self.logger.warning(f"更新失败，场景 '{name}' 不存在")
                    return False

                # 更新字段
                for key, value in kwargs.items():
                    if hasattr(scene, key):
                        setattr(scene, key, value)
                    else:
                        self.logger.warning(f"场景没有字段 '{key}'，将忽略该更新")

                session.commit()
                self.logger.info(f"场景 '{name}' 信息已更新")
                return True

        except exc.SQLAlchemyError as e:
            self.logger.error(f"更新场景 '{name}' 失败: {str(e)}")
            return False

    def rename_scene(self, old_name: str, new_name: str) -> bool:
        """
        场景更名

        Args:
            old_name: 原场景名称
            new_name: 新场景名称

        Returns: 操作是否成功
        """
        if not old_name or not new_name:
            self.logger.error("原场景名称和新场景名称不能为空")
            return False

        if old_name == new_name:
            self.logger.info("新名称与原名称相同，无需修改")
            return True

        try:
            with Session(self.engine) as session:
                # 检查原场景是否存在
                scene = session.exec(select(Scene).where(Scene.name == old_name)).first()
                if not scene:
                    self.logger.warning(f"更名失败，原场景 '{old_name}' 不存在")
                    return False

                # 检查新名称是否已被使用
                existing_scene = session.exec(select(Scene).where(Scene.name == new_name)).first()
                if existing_scene:
                    self.logger.warning(f"更名失败，新名称 '{new_name}' 已被使用")
                    return False

                # 执行更名
                scene.name = new_name
                session.commit()
                self.logger.info(f"场景已从 '{old_name}' 更名为 '{new_name}'")
                return True

        except exc.SQLAlchemyError as e:
            self.logger.error(f"场景更名失败: {str(e)}")
            return False

    def add_element_to_scene(self, scene_name: str, element_name: str, **kwargs) -> bool:
        """
        添加新元素到场景

        Args:
            scene_name: 场景名称
            element_name: 元素名称
           ** kwargs: 元素其他属性，如: type, threshold, ratio_x 等

        Returns: 操作是否成功
        """
        if not scene_name or not element_name:
            self.logger.error("场景名称和元素名称不能为空")
            return False

        try:
            with Session(self.engine) as session:
                # 检查场景是否存在
                scene = session.exec(select(Scene).where(Scene.name == scene_name)).first()
                if not scene:
                    self.logger.warning(f"添加元素失败，场景 '{scene_name}' 不存在")
                    return False

                # 检查元素是否已存在于该场景
                existing_element = session.exec(
                    select(Element)
                    .where(
                        Element.scene_id == scene.id,
                        Element.name == element_name
                    )
                ).first()

                if existing_element:
                    self.logger.warning(f"元素 '{element_name}' 已存在于场景 '{scene_name}' 中")
                    return False

                # 创建新元素
                element_kwargs = {
                    "name": element_name,
                    "scene_id": scene.id  # 添加场景ID
                }
                element_kwargs.update(kwargs)

                # 过滤掉元素模型中不存在的字段
                valid_fields = [field_name for field_name in Element.__fields__ if field_name != "id"]
                element_kwargs = {k: v for k, v in element_kwargs.items() if k in valid_fields}
                element = Element(**element_kwargs)

                session.add(element)
                session.commit()

                self.logger.info(f"元素 '{element_name}' 已添加到场景 '{scene_name}'")
                return True

        except exc.SQLAlchemyError as e:
            self.logger.error(f"添加元素到场景失败: {str(e)}")
            return False

    def delete_element_from_scene(self, scene_name: str, element_name: str) -> bool:
        """
        从场景中删除元素

        Args:
            scene_name: 场景名称
            element_name: 元素名称

        Returns: 操作是否成功
        """
        if not scene_name or not element_name:
            self.logger.error("场景名称和元素名称不能为空")
            return False

        try:
            with Session(self.engine) as session:
                # 查找场景
                scene = session.exec(select(Scene).where(Scene.name == scene_name)).first()
                if not scene:
                    self.logger.warning(f"删除元素失败，场景 '{scene_name}' 不存在")
                    return False

                # 查找元素
                element = session.exec(
                    select(Element)
                    .where(
                        Element.scene_id == scene.id,
                        Element.name == element_name
                    )
                ).first()

                if not element:
                    self.logger.warning(f"删除元素失败，元素 '{element_name}' 不存在于场景 '{scene_name}' 中")
                    return False

                # 直接删除元素
                session.delete(element)
                session.commit()

                self.logger.info(f"元素 '{element_name}' 已从场景 '{scene_name}' 中删除")
                return True

        except exc.SQLAlchemyError as e:
            self.logger.error(f"从场景删除元素失败: {str(e)}")
            return False

    def update_element_info(self, scene_name: str, element_name: str, **kwargs) -> bool:
        """
        更新场景中的元素信息

        Args:
            scene_name: 场景名称
            element_name: 元素名称
           ** kwargs: 要更新的字段，如: threshold, ratio_x, ratio_y 等

        Returns: 操作是否成功
        """
        if not scene_name or not element_name:
            self.logger.error("场景名称和元素名称不能为空")
            return False

        if not kwargs:
            self.logger.warning("没有提供任何要更新的字段")
            return True

        try:
            with Session(self.engine) as session:
                # 查找场景
                scene = session.exec(select(Scene).where(Scene.name == scene_name)).first()
                if not scene:
                    self.logger.warning(f"更新元素失败，场景 '{scene_name}' 不存在")
                    return False

                # 查找元素
                element = session.exec(
                    select(Element)
                    .where(
                        Element.scene_id == scene.id,
                        Element.name == element_name
                    )
                ).first()

                if not element:
                    self.logger.warning(f"更新元素失败，元素 '{element_name}' 不存在于场景 '{scene_name}' 中")
                    return False

                # 更新字段
                for key, value in kwargs.items():
                    if hasattr(element, key) and key != "id" and key != "name" and key != "scene_id":  # 不允许修改id、name和scene_id
                        setattr(element, key, value)
                    else:
                        self.logger.warning(f"元素没有字段 '{key}' 或该字段不允许更新，将忽略")

                session.commit()
                self.logger.info(f"场景 '{scene_name}' 中的元素 '{element_name}' 已更新")
                return True

        except exc.SQLAlchemyError as e:
            self.logger.error(f"更新元素信息失败: {str(e)}")
            return False

    def rename_element(self, scene_name: str, old_name: str, new_name: str) -> bool:
        """
        重命名场景中的元素

        Args:
            scene_name: 场景名称
            old_name: 元素原名称
            new_name: 元素新名称

        Returns: 操作是否成功
        """
        if not scene_name or not old_name or not new_name:
            self.logger.error("场景名称、元素原名称和新名称不能为空")
            return False

        if old_name == new_name:
            self.logger.info("元素新名称与原名称相同，无需修改")
            return True

        try:
            with Session(self.engine) as session:
                # 查找场景
                scene = session.exec(select(Scene).where(Scene.name == scene_name)).first()
                if not scene:
                    self.logger.warning(f"重命名元素失败，场景 '{scene_name}' 不存在")
                    return False

                # 查找元素
                element = session.exec(
                    select(Element)
                    .where(
                        Element.scene_id == scene.id,
                        Element.name == old_name
                    )
                ).first()

                if not element:
                    self.logger.warning(f"重命名元素失败，元素 '{old_name}' 不存在于场景 '{scene_name}' 中")
                    return False

                # 检查新名称是否已存在于该场景
                existing_element = session.exec(
                    select(Element)
                    .where(
                        Element.scene_id == scene.id,
                        Element.name == new_name
                    )
                ).first()

                if existing_element:
                    self.logger.warning(f"重命名元素失败，场景 '{scene_name}' 中已存在名为 '{new_name}' 的元素")
                    return False

                # 执行重命名
                element.name = new_name
                session.commit()
                self.logger.info(f"场景 '{scene_name}' 中的元素已从 '{old_name}' 更名为 '{new_name}'")
                return True

        except exc.SQLAlchemyError as e:
            self.logger.error(f"元素重命名失败: {str(e)}")
            return False

    def get_all_scenes(self) -> List[Scene]:
        """读取所有场景实例（包含元素和边信息）"""
        try:
            with Session(self.engine) as session:
                scenes = session.exec(
                    select(Scene)
                    .options(
                        joinedload(Scene.elements),
                        joinedload(Scene.out_edges).joinedload(SceneEdge.target_scene),
                        joinedload(Scene.in_edges).joinedload(SceneEdge.source_scene)
                    )
                ).unique().all()
                self.logger.info(f"成功查询到 {len(scenes)} 个场景")
                return scenes
        except exc.SQLAlchemyError as e:
            self.logger.error(f"查询所有场景失败: {str(e)}")
            return []

    def get_scene_by_name(self, scene_name: str) -> Optional[Scene]:
        """通过场景名称读取单个场景实例（包含元素和边信息）"""
        if not scene_name:
            self.logger.error("场景名称不能为空")
            return None

        try:
            with Session(self.engine) as session:
                scene = session.exec(
                    select(Scene)
                    .where(Scene.name == scene_name)
                    .options(
                        joinedload(Scene.elements),
                        joinedload(Scene.out_edges).joinedload(SceneEdge.target_scene),
                        joinedload(Scene.in_edges).joinedload(SceneEdge.source_scene)
                    )
                ).unique().first()

                if scene:
                    self.logger.info(f"成功查询到场景: {scene_name}")
                else:
                    self.logger.warning(f"未找到场景: {scene_name}")
                return scene
        except exc.SQLAlchemyError as e:
            self.logger.error(f"查询场景 {scene_name} 失败: {str(e)}")
            return None

    def get_scene_elements(self, scene_name: str) -> List[Element]:
        """
        读取指定场景下的所有元素实例

        Args:
            scene_name: 场景名称

        Returns:
            该场景下所有Element实例的列表，若场景不存在或查询失败返回空列表
        """
        if not scene_name:
            self.logger.error("场景名称不能为空")
            return []

        try:
            with Session(self.engine) as session:
                # 先查询场景是否存在
                scene = session.exec(
                    select(Scene)
                    .where(Scene.name == scene_name)
                    .options(joinedload(Scene.elements))
                ).first()

                if not scene:
                    self.logger.warning(f"未找到场景: {scene_name}，无法获取元素")
                    return []

                elements = scene.elements
                self.logger.info(f"场景 {scene_name} 下共有 {len(elements)} 个元素")
                return elements
        except exc.SQLAlchemyError as e:
            self.logger.error(f"查询场景 {scene_name} 的元素失败: {str(e)}")
            return []

    def get_scene_element(self, scene_name: str, element_name: str) -> Optional[Element]:
        """
        读取指定场景下的单个元素实例

        Args:
            scene_name: 场景名称
            element_name: 元素名称

        Returns:
            匹配的Element实例，若不存在或查询失败返回None
        """
        if not scene_name or not element_name:
            self.logger.error("场景名称和元素名称不能为空")
            return None

        try:
            with Session(self.engine) as session:
                # 直接查询元素
                element = session.exec(
                    select(Element)
                    .join(Scene)
                    .where(
                        Scene.name == scene_name,
                        Element.name == element_name
                    )
                ).first()

                if element:
                    self.logger.info(f"在场景 {scene_name} 中找到元素: {element_name}")
                    return element
                else:
                    self.logger.warning(f"场景 {scene_name} 中未找到元素: {element_name}")
                    return None
        except exc.SQLAlchemyError as e:
            self.logger.error(f"查询场景 {scene_name} 中的元素 {element_name} 失败: {str(e)}")
            return None

    def add_scene_edge(self, source_scene_name: str, target_scene_name: str) -> bool:
        """
        添加场景间的边关系

        Args:
            source_scene_name: 起点场景名称
            target_scene_name: 终点场景名称

        Returns: 操作是否成功
        """
        if not source_scene_name or not target_scene_name:
            self.logger.error("起点和终点场景名称不能为空")
            return False

        if source_scene_name == target_scene_name:
            self.logger.error("不能添加场景到自身的边")
            return False

        try:
            with Session(self.engine) as session:
                # 查找源场景和目标场景
                source_scene = session.exec(
                    select(Scene).where(Scene.name == source_scene_name)
                ).first()
                target_scene = session.exec(
                    select(Scene).where(Scene.name == target_scene_name)
                ).first()

                if not source_scene:
                    self.logger.warning(f"添加边失败，起点场景 '{source_scene_name}' 不存在")
                    return False
                if not target_scene:
                    self.logger.warning(f"添加边失败，终点场景 '{target_scene_name}' 不存在")
                    return False

                # 检查边是否已存在
                existing_edge = session.exec(
                    select(SceneEdge)
                    .where(
                        SceneEdge.source_scene_id == source_scene.id,
                        SceneEdge.target_scene_id == target_scene.id
                    )
                ).first()

                if existing_edge:
                    self.logger.warning(f"边 {source_scene_name} -> {target_scene_name} 已存在")
                    return False

                # 创建新边
                edge = SceneEdge(
                    source_scene_id=source_scene.id,
                    target_scene_id=target_scene.id
                )
                session.add(edge)
                session.commit()
                self.logger.info(f"已添加边: {source_scene_name} -> {target_scene_name}")
                return True

        except exc.SQLAlchemyError as e:
            self.logger.error(f"添加场景边失败: {str(e)}")
            return False

    def delete_scene_edge(self, source_scene_name: str, target_scene_name: str) -> bool:
        """
        删除场景间的边关系

        Args:
            source_scene_name: 起点场景名称
            target_scene_name: 终点场景名称

        Returns: 操作是否成功
        """
        if not source_scene_name or not target_scene_name:
            self.logger.error("起点和终点场景名称不能为空")
            return False

        try:
            with Session(self.engine) as session:
                # 查找源场景和目标场景
                source_scene = session.exec(
                    select(Scene).where(Scene.name == source_scene_name)
                ).first()
                target_scene = session.exec(
                    select(Scene).where(Scene.name == target_scene_name)
                ).first()

                if not source_scene:
                    self.logger.warning(f"删除边失败，起点场景 '{source_scene_name}' 不存在")
                    return False
                if not target_scene:
                    self.logger.warning(f"删除边失败，终点场景 '{target_scene_name}' 不存在")
                    return False

                # 查找边并删除
                edge = session.exec(
                    select(SceneEdge)
                    .where(
                        SceneEdge.source_scene_id == source_scene.id,
                        SceneEdge.target_scene_id == target_scene.id
                    )
                ).first()

                if not edge:
                    self.logger.warning(f"边 {source_scene_name} -> {target_scene_name} 不存在")
                    return False

                session.delete(edge)
                session.commit()
                self.logger.info(f"已删除边: {source_scene_name} -> {target_scene_name}")
                return True

        except exc.SQLAlchemyError as e:
            self.logger.error(f"删除场景边失败: {str(e)}")
            return False

    def get_all_scene_edges(self) -> List[SceneEdge]:
        """
        查询所有场景间的边关系

        Returns: 所有边关系的列表
        """
        try:
            with Session(self.engine) as session:
                edges = session.exec(
                    select(SceneEdge)
                    .options(
                        joinedload(SceneEdge.source_scene),
                        joinedload(SceneEdge.target_scene)
                    )
                ).all()
                self.logger.info(f"成功查询到 {len(edges)} 条场景边")
                return edges
        except exc.SQLAlchemyError as e:
            self.logger.error(f"查询所有场景边失败: {str(e)}")
            return []

    def get_scene_edges(self, scene_name: str, is_outgoing: bool = True) -> List[SceneEdge]:
        """
        查询指定场景的出边或入边

        Args:
            scene_name: 场景名称
            is_outgoing: True查询出边，False查询入边

        Returns: 边关系列表
        """
        if not scene_name:
            self.logger.error("场景名称不能为空")
            return []

        try:
            with Session(self.engine) as session:
                scene = session.exec(
                    select(Scene).where(Scene.name == scene_name)
                ).first()
                if not scene:
                    self.logger.warning(f"查询边失败，场景 '{scene_name}' 不存在")
                    return []

                if is_outgoing:
                    edges = session.exec(
                        select(SceneEdge)
                        .where(SceneEdge.source_scene_id == scene.id)
                        .options(joinedload(SceneEdge.target_scene))
                    ).all()
                    edge_type = "出边"
                else:
                    edges = session.exec(
                        select(SceneEdge)
                        .where(SceneEdge.target_scene_id == scene.id)
                        .options(joinedload(SceneEdge.source_scene))
                    ).all()
                    edge_type = "入边"

                self.logger.info(f"场景 '{scene_name}' 共有 {len(edges)} 条{edge_type}")
                return edges
        except exc.SQLAlchemyError as e:
            self.logger.error(f"查询场景边失败: {str(e)}")
            return []


import logging


def setup_global_logging(level: int = logging.INFO):
    """
    配置全局日志：输出到控制台，包含时间、日志器名称、级别、内容
    """
    # 1. 创建日志器（如果已存在则获取，避免重复配置）
    root_logger = logging.getLogger()
    root_logger.setLevel(level)  # 全局日志级别（低于此级别的日志会被过滤）

    # 2. 避免重复添加处理器（单例多次初始化可能导致重复输出）
    if root_logger.handlers:
        return

    # 3. 创建控制台处理器（输出到控制台）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)  # 处理器级别（可单独设置，通常与全局一致）

    # 4. 设置日志格式（包含必要信息，便于调试）
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)

    # 5. 将处理器添加到日志器
    root_logger.addHandler(console_handler)


def convert_raw_bytes_to_png(resource_db_manager):
    """将数据库中的原始字节图像数据转换为PNG压缩格式"""
    params = [cv2.IMWRITE_PNG_COMPRESSION, 9]  # 最高压缩等级

    def get_data_size(data):
        return len(data) if data else 0

    with Session(resource_db_manager.engine) as session:
        for scene in session.exec(select(Scene)).all():
            for element in scene.elements:
                if element.type == ElementType.IMG:
                    try:
                        # 处理 BGRA
                        if element.bgra and element.width and element.height:
                            print(f"转换前: BGRA={get_data_size(element.bgra)} bytes")
                            bgra_buf = np.frombuffer(element.bgra, dtype=np.uint8)
                            bgra = bgra_buf.reshape(element.height, element.width, 4)
                            success, encoded_bgra = cv2.imencode('.png', bgra, params)
                            if success:
                                # 清除旧数据并设置新数据
                                element.bgra = None
                                session.flush()  # 强制刷新
                                element.bgra = encoded_bgra.tobytes()
                                print(f"转换后: BGRA={get_data_size(element.bgra)} bytes")

                        # 处理 gray
                        if element.gray and element.width and element.height:
                            print(f"转换前: GRAY={get_data_size(element.bgra)} bytes")
                            gray_buf = np.frombuffer(element.gray, dtype=np.uint8)
                            gray = gray_buf.reshape(element.height, element.width, 1)
                            success, encoded_gray = cv2.imencode('.png', gray, params)
                            if success:
                                element.gray = None
                                session.flush()
                                element.gray = encoded_gray.tobytes()
                                print(f"转换后: GRAY={get_data_size(element.bgra)} bytes")

                        # 处理 mask
                        if element.mask and element.width and element.height:
                            print(f"转换前: MASK={get_data_size(element.bgra)} bytes")
                            mask_buf = np.frombuffer(element.mask, dtype=np.uint8)
                            mask = mask_buf.reshape(element.height, element.width, 1)
                            success, encoded_mask = cv2.imencode('.png', mask, params)
                            if success:
                                element.mask = None
                                session.flush()
                                element.mask = encoded_mask.tobytes()
                                print(f"转换后: MASK={get_data_size(element.bgra)} bytes")

                        session.add(element)
                        session.commit()
                        print(f"转换成功: Scene[{scene.name}] Element[{element.name}]")

                    except Exception as e:
                        print(f"转换失败: Scene[{scene.name}] Element[{element.name}]: {str(e)}")
                        session.rollback()


if __name__ == "__main__":
    setup_global_logging()
    rdb = ResourceDBManager()
    # convert_raw_bytes_to_png(rdb)
    with rdb.engine.connect() as conn:
        conn.execute(text("VACUUM"))
