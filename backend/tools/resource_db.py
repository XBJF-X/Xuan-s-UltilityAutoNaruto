"""资源数据库管理器 - 从 tool/ResourceManager/ResourceDBManager.py 迁移，剥离 StaticFunctions 依赖"""
import logging
from pathlib import Path
from typing import Optional, List

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import joinedload
from sqlmodel import SQLModel, Session, select

from backend.utils import get_real_path
from backend.tools.resource_model import Scene, Element, SceneEdge


class ResourceDBManager:
    _instance: Optional["ResourceDBManager"] = None
    connect_args = {
        "check_same_thread": False,
        "isolation_level": None
    }

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_dir: Path | None = None, parent_logger: logging.Logger | str = ""):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

        if isinstance(parent_logger, str) or not parent_logger:
            self.logger = logging.getLogger("ResourceDBManager")
        else:
            self.logger = parent_logger.getChild("ResourceDBManager")

        if db_dir is None:
            db_dir = Path(get_real_path("src"))
        self.db_dir = db_dir
        self.db_file_path = db_dir / "database.db"
        self.sqlite_url = f"sqlite:///{self.db_file_path}"
        self.engine = create_engine(self.sqlite_url, connect_args=self.connect_args)
        self.create_db_and_tables()

    def create_db_and_tables(self):
        try:
            SQLModel.metadata.create_all(self.engine)
            self.logger.info(f"数据库表结构已创建或更新，路径: {self.db_file_path}")
        except Exception as e:
            self.logger.error(f"创建数据库表结构失败: {str(e)}")
            raise

    # --- 场景 CRUD ---

    def add_scene(self, name: str) -> bool:
        if not name or not isinstance(name, str):
            self.logger.error("场景名称不能为空且必须是字符串")
            return False
        try:
            with Session(self.engine) as session:
                existing = session.exec(select(Scene).where(Scene.name == name)).first()
                if existing:
                    self.logger.warning(f"场景 '{name}' 已存在")
                    return False
                session.add(Scene(name=name))
                session.commit()
                self.logger.info(f"场景 '{name}' 添加成功")
                return True
        except exc.SQLAlchemyError as e:
            self.logger.error(f"添加场景 '{name}' 失败: {str(e)}")
            return False

    def delete_scene(self, name: str) -> bool:
        if not name:
            return False
        try:
            with Session(self.engine) as session:
                scene = session.exec(select(Scene).where(Scene.name == name)).first()
                if not scene:
                    return False
                for edge in session.exec(select(SceneEdge).where(
                    (SceneEdge.source_scene_id == scene.id) | (SceneEdge.target_scene_id == scene.id)
                )).all():
                    session.delete(edge)
                for elem in session.exec(select(Element).where(Element.scene_id == scene.id)).all():
                    session.delete(elem)
                session.delete(scene)
                session.commit()
                self.logger.info(f"场景 '{name}' 及其关联已删除")
                return True
        except exc.SQLAlchemyError as e:
            self.logger.error(f"删除场景 '{name}' 失败: {str(e)}")
            return False

    def rename_scene(self, old_name: str, new_name: str) -> bool:
        if not old_name or not new_name or old_name == new_name:
            return False
        try:
            with Session(self.engine) as session:
                scene = session.exec(select(Scene).where(Scene.name == old_name)).first()
                if not scene:
                    return False
                if session.exec(select(Scene).where(Scene.name == new_name)).first():
                    self.logger.warning(f"新名称 '{new_name}' 已被使用")
                    return False
                scene.name = new_name
                session.commit()
                self.logger.info(f"场景已从 '{old_name}' 更名为 '{new_name}'")
                return True
        except exc.SQLAlchemyError as e:
            self.logger.error(f"场景更名失败: {str(e)}")
            return False

    def get_all_scenes(self) -> List[Scene]:
        try:
            with Session(self.engine) as session:
                return session.exec(
                    select(Scene).options(
                        joinedload(Scene.elements),
                        joinedload(Scene.out_edges).joinedload(SceneEdge.target_scene),
                        joinedload(Scene.in_edges).joinedload(SceneEdge.source_scene)
                    )
                ).unique().all()
        except exc.SQLAlchemyError as e:
            self.logger.error(f"查询所有场景失败: {str(e)}")
            return []

    def get_scene_by_name(self, scene_name: str) -> Optional[Scene]:
        if not scene_name:
            return None
        try:
            with Session(self.engine) as session:
                return session.exec(
                    select(Scene).where(Scene.name == scene_name).options(
                        joinedload(Scene.elements),
                        joinedload(Scene.out_edges).joinedload(SceneEdge.target_scene),
                        joinedload(Scene.in_edges).joinedload(SceneEdge.source_scene)
                    )
                ).unique().first()
        except exc.SQLAlchemyError as e:
            self.logger.error(f"查询场景 {scene_name} 失败: {str(e)}")
            return None

    def get_scene_elements(self, scene_name: str) -> List[Element]:
        if not scene_name:
            return []
        try:
            with Session(self.engine) as session:
                scene = session.exec(
                    select(Scene).where(Scene.name == scene_name).options(joinedload(Scene.elements))
                ).first()
                return scene.elements if scene else []
        except exc.SQLAlchemyError as e:
            self.logger.error(f"查询场景 {scene_name} 元素失败: {str(e)}")
            return []

    def get_scene_element(self, scene_name: str, element_name: str) -> Optional[Element]:
        if not scene_name or not element_name:
            return None
        try:
            with Session(self.engine) as session:
                return session.exec(
                    select(Element).join(Scene).where(
                        Scene.name == scene_name, Element.name == element_name
                    )
                ).first()
        except exc.SQLAlchemyError as e:
            self.logger.error(f"查询元素失败: {str(e)}")
            return None

    # --- 元素 CRUD ---

    def add_element_to_scene(self, scene_name: str, element_name: str, **kwargs) -> bool:
        if not scene_name or not element_name:
            return False
        try:
            with Session(self.engine) as session:
                scene = session.exec(select(Scene).where(Scene.name == scene_name)).first()
                if not scene:
                    return False
                existing = session.exec(
                    select(Element).where(Element.scene_id == scene.id, Element.name == element_name)
                ).first()
                if existing:
                    return False
                valid_fields = {f for f in Element.__fields__ if f != "id"}
                element_kwargs = {"name": element_name, "scene_id": scene.id}
                element_kwargs.update({k: v for k, v in kwargs.items() if k in valid_fields})
                session.add(Element(**element_kwargs))
                session.commit()
                self.logger.info(f"元素 '{element_name}' 已添加到场景 '{scene_name}'")
                return True
        except exc.SQLAlchemyError as e:
            self.logger.error(f"添加元素失败: {str(e)}")
            return False

    def delete_element_from_scene(self, scene_name: str, element_name: str) -> bool:
        if not scene_name or not element_name:
            return False
        try:
            with Session(self.engine) as session:
                scene = session.exec(select(Scene).where(Scene.name == scene_name)).first()
                if not scene:
                    return False
                element = session.exec(
                    select(Element).where(Element.scene_id == scene.id, Element.name == element_name)
                ).first()
                if not element:
                    return False
                session.delete(element)
                session.commit()
                return True
        except exc.SQLAlchemyError as e:
            self.logger.error(f"删除元素失败: {str(e)}")
            return False

    def update_element_info(self, scene_name: str, element_name: str, **kwargs) -> bool:
        if not scene_name or not element_name or not kwargs:
            return False
        try:
            with Session(self.engine) as session:
                scene = session.exec(select(Scene).where(Scene.name == scene_name)).first()
                if not scene:
                    return False
                element = session.exec(
                    select(Element).where(Element.scene_id == scene.id, Element.name == element_name)
                ).first()
                if not element:
                    return False
                for key, value in kwargs.items():
                    if hasattr(element, key) and key not in ("id", "name", "scene_id"):
                        setattr(element, key, value)
                session.commit()
                return True
        except exc.SQLAlchemyError as e:
            self.logger.error(f"更新元素失败: {str(e)}")
            return False

    # --- 边关系 CRUD ---

    def add_scene_edge(self, source_scene_name: str, target_scene_name: str) -> bool:
        if not source_scene_name or not target_scene_name or source_scene_name == target_scene_name:
            return False
        try:
            with Session(self.engine) as session:
                src = session.exec(select(Scene).where(Scene.name == source_scene_name)).first()
                tgt = session.exec(select(Scene).where(Scene.name == target_scene_name)).first()
                if not src or not tgt:
                    return False
                existing = session.exec(
                    select(SceneEdge).where(
                        SceneEdge.source_scene_id == src.id,
                        SceneEdge.target_scene_id == tgt.id
                    )
                ).first()
                if existing:
                    return False
                session.add(SceneEdge(source_scene_id=src.id, target_scene_id=tgt.id))
                session.commit()
                return True
        except exc.SQLAlchemyError as e:
            self.logger.error(f"添加场景边失败: {str(e)}")
            return False

    def delete_scene_edge(self, source_scene_name: str, target_scene_name: str) -> bool:
        if not source_scene_name or not target_scene_name:
            return False
        try:
            with Session(self.engine) as session:
                src = session.exec(select(Scene).where(Scene.name == source_scene_name)).first()
                tgt = session.exec(select(Scene).where(Scene.name == target_scene_name)).first()
                if not src or not tgt:
                    return False
                edge = session.exec(
                    select(SceneEdge).where(
                        SceneEdge.source_scene_id == src.id,
                        SceneEdge.target_scene_id == tgt.id
                    )
                ).first()
                if not edge:
                    return False
                session.delete(edge)
                session.commit()
                return True
        except exc.SQLAlchemyError as e:
            self.logger.error(f"删除场景边失败: {str(e)}")
            return False

    def get_all_scene_edges(self) -> List[SceneEdge]:
        try:
            with Session(self.engine) as session:
                return session.exec(
                    select(SceneEdge).options(
                        joinedload(SceneEdge.source_scene),
                        joinedload(SceneEdge.target_scene)
                    )
                ).unique().all()
        except exc.SQLAlchemyError as e:
            self.logger.error(f"查询所有边失败: {str(e)}")
            return []
