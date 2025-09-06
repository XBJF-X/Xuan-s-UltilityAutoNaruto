import uuid
from datetime import datetime
from typing import Optional, List
from zoneinfo import ZoneInfo

from sqlalchemy import Column, LargeBinary
from sqlmodel import SQLModel, Field, Relationship

from utils.Base.Enums import ElementType, MatchType


# 场景间边关系的关联模型（记录从一个场景到另一个场景的边）
class SceneEdge(SQLModel, table=True):
    """表示场景之间的出边关系"""
    id: Optional[int] = Field(default=None, primary_key=True)
    # 起点场景ID（外键）
    source_scene_id: str = Field(foreign_key="scene.id")
    # 终点场景ID（外键）
    target_scene_id: str = Field(foreign_key="scene.id")
    # 创建时间
    created_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Shanghai")))

    source_scene: "Scene" = Relationship(
        back_populates="out_edges",
        sa_relationship_kwargs={
            "foreign_keys": "[SceneEdge.source_scene_id]"  # 明确指定外键
        }
    )
    target_scene: "Scene" = Relationship(
        back_populates="in_edges",
        sa_relationship_kwargs={
            "foreign_keys": "[SceneEdge.target_scene_id]"  # 明确指定外键
        }
    )


class SceneElementLink(SQLModel, table=True):
    scene_id: int = Field(foreign_key="scene.id", primary_key=True)
    element_id: int = Field(foreign_key="element.id", primary_key=True)


class Element(SQLModel, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    name: str = Field(unique=True, index=True)
    type: ElementType = Field(default=ElementType.IMG)
    threshold: float = Field(default=0.8)
    ratio_x: float = Field(default=0.5)
    ratio_y: float = Field(default=0.5)
    match_type: MatchType = Field(default=MatchType.TEMPLATE)
    roi_x: int = Field(default=0)
    roi_y: int = Field(default=0)
    roi_width: int = Field(default=1600)
    roi_height: int = Field(default=900)
    coordinate_x: int = Field(default=0)
    coordinate_y: int = Field(default=0)
    bgra: Optional[bytes] = Field(sa_column=Column(LargeBinary))
    gray: Optional[bytes] = Field(sa_column=Column(LargeBinary))
    mask: Optional[bytes] = Field(sa_column=Column(LargeBinary))
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    channels: Optional[int] = Field(default=None)

    scenes: List["Scene"] = Relationship(back_populates="elements", link_model=SceneElementLink)

    # 使用 UTC 时间
    created_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Shanghai")))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Shanghai")))


class Scene(SQLModel, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    name: str = Field(unique=True, index=True)

    # 定义与 Element 的关系
    elements: List[Element] = Relationship(back_populates="scenes", link_model=SceneElementLink)

    # 新添加：出边（从当前场景指向其他场景的边）
    out_edges: List[SceneEdge] = Relationship(
        back_populates="source_scene",
        sa_relationship_kwargs={"foreign_keys": "SceneEdge.source_scene_id"}
    )

    # 新添加：入边（从其他场景指向当前场景的边）
    in_edges: List[SceneEdge] = Relationship(
        back_populates="target_scene",
        sa_relationship_kwargs={"foreign_keys": "SceneEdge.target_scene_id"}
    )

    # 使用 UTC 时间
    created_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Shanghai")))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Shanghai")))
