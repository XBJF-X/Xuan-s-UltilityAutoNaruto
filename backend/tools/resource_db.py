"""资源数据库管理器 - 从 tool/ResourceManager/ResourceDBManager.py 迁移，剥离 StaticFunctions 依赖"""
import logging
from pathlib import Path
from typing import Optional, List

from sqlalchemy import create_engine, exc, inspect, text
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

    @staticmethod
    def _migrate_schema(engine):
        """SQLite 增量迁移：create_all 不会为已存在的表添加新列，这里手动补齐。

        当前迁移项：
        - element.ocr_min_score：新模型新增字段，旧库缺失导致查询报错。
        """
        try:
            inspector = inspect(engine)
            if "element" not in inspector.get_table_names():
                return
            columns = {c["name"] for c in inspector.get_columns("element")}
            if "ocr_min_score" not in columns:
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE element ADD COLUMN ocr_min_score FLOAT"))
                logging.getLogger("ResourceDBManager").info("迁移: element 表已添加 ocr_min_score 列")
            # 灰度图/掩码已废弃（仅存 bgra，运行时推导），旧库残留列尝试移除（SQLite 3.35+ 支持 DROP COLUMN）
            for old_col in ("gray", "mask"):
                if old_col in columns:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text(f"ALTER TABLE element DROP COLUMN {old_col}"))
                        logging.getLogger("ResourceDBManager").info(f"迁移: element 表已移除废弃列 {old_col}")
                    except Exception:
                        logging.getLogger("ResourceDBManager").warning(
                            f"迁移: 无法移除废弃列 {old_col}（旧库可能不支持 DROP COLUMN，忽略）")
        except Exception:
            logging.getLogger("ResourceDBManager").exception("执行数据库增量迁移失败")

    def create_db_and_tables(self):
        try:
            SQLModel.metadata.create_all(self.engine)
            self._migrate_schema(self.engine)
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

    def rename_element(self, scene_name: str, old_name: str, new_name: str) -> bool:
        """重命名场景中的元素（复刻原版 ResourceDBManager.rename_element）"""
        if not scene_name or not old_name or not new_name or old_name == new_name:
            return False
        try:
            with Session(self.engine) as session:
                scene = session.exec(select(Scene).where(Scene.name == scene_name)).first()
                if not scene:
                    return False
                element = session.exec(
                    select(Element).where(Element.scene_id == scene.id, Element.name == old_name)
                ).first()
                if not element:
                    return False
                existing = session.exec(
                    select(Element).where(Element.scene_id == scene.id, Element.name == new_name)
                ).first()
                if existing:
                    self.logger.warning(f"重命名元素失败，场景 '{scene_name}' 中已存在名为 '{new_name}' 的元素")
                    return False
                element.name = new_name
                session.commit()
                self.logger.info(f"元素已从 '{old_name}' 重命名为 '{new_name}'")
                return True
        except exc.SQLAlchemyError as e:
            self.logger.error(f"重命名元素失败: {str(e)}")
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

    # =======================================================================
    # 以下为按 id 定位的新版方法（供新前端 /api/resource 使用）
    # 旧版按名称定位的方法保留，确保后端核心逻辑调用不受影响
    # =======================================================================

    # --- 场景（按 id） ---

    def get_scene_by_id(self, scene_id: str) -> Optional[Scene]:
        """按 id 查询单个场景（含元素与边关系）"""
        try:
            with Session(self.engine) as session:
                return session.exec(
                    select(Scene).where(Scene.id == scene_id).options(
                        joinedload(Scene.elements),
                        joinedload(Scene.out_edges).joinedload(SceneEdge.target_scene),
                        joinedload(Scene.in_edges).joinedload(SceneEdge.source_scene)
                    )
                ).unique().first()
        except exc.SQLAlchemyError as e:
            self.logger.error(f"按 id 查询场景 {scene_id} 失败: {str(e)}")
            return None

    def get_scene_id_by_name(self, name: str) -> Optional[str]:
        """按名称查询场景 id（用于由名称转 id，兼容旧调用）"""
        try:
            with Session(self.engine) as session:
                scene = session.exec(select(Scene).where(Scene.name == name)).first()
                return scene.id if scene else None
        except exc.SQLAlchemyError as e:
            self.logger.error(f"按名称查询场景 id '{name}' 失败: {str(e)}")
            return None

    def rename_scene_by_id(self, scene_id: str, new_name: str) -> bool:
        """按 id 重命名场景"""
        if not scene_id or not new_name:
            return False
        try:
            with Session(self.engine) as session:
                scene = session.exec(select(Scene).where(Scene.id == scene_id)).first()
                if not scene:
                    return False
                if session.exec(select(Scene).where(Scene.name == new_name)).first():
                    self.logger.warning(f"新名称 '{new_name}' 已被使用")
                    return False
                scene.name = new_name
                session.commit()
                self.logger.info(f"场景 {scene_id} 已更名为 '{new_name}'")
                return True
        except exc.SQLAlchemyError as e:
            self.logger.error(f"场景 {scene_id} 更名失败: {str(e)}")
            return False

    def update_scene_by_id(self, scene_id: str, **kwargs) -> bool:
        """按 id 更新场景字段"""
        if not scene_id or not kwargs:
            return False
        try:
            with Session(self.engine) as session:
                scene = session.exec(select(Scene).where(Scene.id == scene_id)).first()
                if not scene:
                    return False
                for key, value in kwargs.items():
                    if hasattr(scene, key) and key not in ("id", "created_at", "updated_at"):
                        setattr(scene, key, value)
                session.commit()
                return True
        except exc.SQLAlchemyError as e:
            self.logger.error(f"更新场景 {scene_id} 失败: {str(e)}")
            return False

    def delete_scene_by_id(self, scene_id: str) -> bool:
        """按 id 删除场景及其所有元素、边关系"""
        if not scene_id:
            return False
        try:
            with Session(self.engine) as session:
                scene = session.exec(select(Scene).where(Scene.id == scene_id)).first()
                if not scene:
                    return False
                for edge in session.exec(select(SceneEdge).where(
                    (SceneEdge.source_scene_id == scene_id) | (SceneEdge.target_scene_id == scene_id)
                )).all():
                    session.delete(edge)
                for elem in session.exec(select(Element).where(Element.scene_id == scene_id)).all():
                    session.delete(elem)
                session.delete(scene)
                session.commit()
                self.logger.info(f"场景 {scene_id} 及其元素、边关系已删除")
                return True
        except exc.SQLAlchemyError as e:
            self.logger.error(f"删除场景 {scene_id} 失败: {str(e)}")
            return False

    # --- 元素（按 id） ---

    def get_element_by_id(self, element_id: str) -> Optional[Element]:
        """按 id 查询单个元素"""
        try:
            with Session(self.engine) as session:
                return session.exec(select(Element).where(Element.id == element_id)).first()
        except exc.SQLAlchemyError as e:
            self.logger.error(f"按 id 查询元素 {element_id} 失败: {str(e)}")
            return None

    def add_element(self, scene_id: str, name: str, **kwargs) -> Optional[Element]:
        """向指定场景（按 id）添加元素，返回新元素对象；失败返回 None"""
        if not scene_id or not name:
            return None
        try:
            with Session(self.engine) as session:
                scene = session.exec(select(Scene).where(Scene.id == scene_id)).first()
                if not scene:
                    self.logger.error(f"添加元素失败：场景 {scene_id} 不存在")
                    return None
                existing = session.exec(
                    select(Element).where(Element.scene_id == scene_id, Element.name == name)
                ).first()
                if existing:
                    self.logger.warning(f"场景 {scene_id} 中已存在元素 '{name}'")
                    return None
                valid_fields = {f for f in Element.__fields__ if f != "id"}
                element_kwargs = {"name": name, "scene_id": scene_id}
                element_kwargs.update({k: v for k, v in kwargs.items() if k in valid_fields})
                element = Element(**element_kwargs)
                session.add(element)
                session.commit()
                session.refresh(element)
                self.logger.info(f"元素 '{name}' 已添加到场景 {scene_id}")
                return element
        except exc.SQLAlchemyError as e:
            self.logger.error(f"添加元素失败: {str(e)}")
            return None

    def update_element_by_id(self, element_id: str, **kwargs) -> bool:
        """按 id 更新元素字段"""
        if not element_id or not kwargs:
            return False
        try:
            with Session(self.engine) as session:
                element = session.exec(select(Element).where(Element.id == element_id)).first()
                if not element:
                    return False
                for key, value in kwargs.items():
                    if hasattr(element, key) and key not in ("id", "scene_id", "created_at", "updated_at"):
                        setattr(element, key, value)
                session.commit()
                return True
        except exc.SQLAlchemyError as e:
            self.logger.error(f"更新元素 {element_id} 失败: {str(e)}")
            return False

    def delete_element_by_id(self, element_id: str) -> bool:
        """按 id 删除元素"""
        if not element_id:
            return False
        try:
            with Session(self.engine) as session:
                element = session.exec(select(Element).where(Element.id == element_id)).first()
                if not element:
                    return False
                session.delete(element)
                session.commit()
                self.logger.info(f"元素 {element_id} 已删除")
                return True
        except exc.SQLAlchemyError as e:
            self.logger.error(f"删除元素 {element_id} 失败: {str(e)}")
            return False

    def get_all_elements(self) -> List[Element]:
        """查询全部元素"""
        try:
            with Session(self.engine) as session:
                return session.exec(select(Element)).all()
        except exc.SQLAlchemyError as e:
            self.logger.error(f"查询全部元素失败: {str(e)}")
            return []

    def get_scene_elements_by_id(self, scene_id: str) -> List[Element]:
        """按场景 id 一次批量查询该场景全部元素"""
        if not scene_id:
            return []
        try:
            with Session(self.engine) as session:
                return session.exec(
                    select(Element).where(Element.scene_id == scene_id)
                ).all()
        except exc.SQLAlchemyError as e:
            self.logger.error(f"查询场景 {scene_id} 元素失败: {str(e)}")
            return []

    # --- 场景边关系（按 id） ---

    def add_scene_edge_by_ids(self, source_scene_id: str, target_scene_id: str) -> bool:
        """按 id 添加场景跳转边"""
        if not source_scene_id or not target_scene_id or source_scene_id == target_scene_id:
            return False
        try:
            with Session(self.engine) as session:
                src = session.exec(select(Scene).where(Scene.id == source_scene_id)).first()
                tgt = session.exec(select(Scene).where(Scene.id == target_scene_id)).first()
                if not src or not tgt:
                    return False
                existing = session.exec(
                    select(SceneEdge).where(
                        SceneEdge.source_scene_id == source_scene_id,
                        SceneEdge.target_scene_id == target_scene_id
                    )
                ).first()
                if existing:
                    return False
                session.add(SceneEdge(source_scene_id=source_scene_id, target_scene_id=target_scene_id))
                session.commit()
                return True
        except exc.SQLAlchemyError as e:
            self.logger.error(f"添加场景边失败: {str(e)}")
            return False

    def delete_scene_edge_by_ids(self, source_scene_id: str, target_scene_id: str) -> bool:
        """按 id 删除场景跳转边"""
        try:
            with Session(self.engine) as session:
                edge = session.exec(
                    select(SceneEdge).where(
                        SceneEdge.source_scene_id == source_scene_id,
                        SceneEdge.target_scene_id == target_scene_id
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
