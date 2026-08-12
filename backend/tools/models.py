"""独立的 SQLModel 定义 - 从 tool/ResourceManager/model/__init__.py 迁移
剥离 PySide6 依赖，移除 element_to_qpixmap 函数（仅前端需要）。
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict
from zoneinfo import ZoneInfo
from functools import cached_property

from sqlalchemy import Column, LargeBinary, UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship

from backend.core.enums import ElementType, MatchType


# 场景间边关系的关联模型
class SceneEdge(SQLModel, table=True):
    """表示场景之间的出边关系"""
    id: Optional[int] = Field(default=None, primary_key=True)
    source_scene_id: str = Field(foreign_key="scene.id")
    target_scene_id: str = Field(foreign_key="scene.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Shanghai")))

    source_scene: "Scene" = Relationship(
        back_populates="out_edges",
        sa_relationship_kwargs={
            "foreign_keys": "[SceneEdge.source_scene_id]"
        }
    )
    target_scene: "Scene" = Relationship(
        back_populates="in_edges",
        sa_relationship_kwargs={
            "foreign_keys": "[SceneEdge.target_scene_id]"
        }
    )


class Element(SQLModel, table=True):
    # extra="allow" 允许运行时附加 gray/mask 推导属性（不入库），
    # 以便 SceneGraph 从 bgra 推导灰度图/掩码后挂载到元素对象上供 Recognizer 使用
    model_config = {"arbitrary_types_allowed": True, "extra": "allow"}

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    name: str = Field(index=True)
    scene_id: str = Field(foreign_key="scene.id")
    symbol: bool = Field(default=False)
    type: ElementType = Field(default=ElementType.IMG)
    threshold: float = Field(default=0.8)
    ratio_x: float = Field(default=0.5)
    ratio_y: float = Field(default=0.5)
    match_type: MatchType = Field(default=MatchType.TEMPLATE)
    roi_x: int = Field(default=0)
    roi_y: int = Field(default=0)
    roi_width: int = Field(default=1600)
    roi_height: int = Field(default=900)
    ocr_min_score: float = Field(default=0.5)
    coordinate_x: int = Field(default=0)
    coordinate_y: int = Field(default=0)
    # 仅存储 4 通道 BGRA 原始字节（PNG 压缩），灰度图/掩码在 SceneGraph 初始化时从 bgra 推导
    bgra: Optional[bytes] = Field(sa_column=Column(LargeBinary))

    scene: "Scene" = Relationship(back_populates="elements")

    created_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Shanghai")))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Shanghai")))

    __table_args__ = (UniqueConstraint('scene_id', 'name', name='_scene_element_uc'),)


class Scene(SQLModel, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    name: str = Field(unique=True, index=True)

    elements: List[Element] = Relationship(back_populates="scene")

    out_edges: List[SceneEdge] = Relationship(
        back_populates="source_scene",
        sa_relationship_kwargs={"foreign_keys": "SceneEdge.source_scene_id"}
    )

    in_edges: List[SceneEdge] = Relationship(
        back_populates="target_scene",
        sa_relationship_kwargs={"foreign_keys": "SceneEdge.target_scene_id"}
    )

    created_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Shanghai")))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Shanghai")))

    @cached_property
    def element_dict(self) -> Dict[str, Element]:
        return {elem.name: elem for elem in self.elements}
