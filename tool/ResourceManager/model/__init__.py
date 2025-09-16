import uuid
from datetime import datetime
from functools import cached_property
from typing import Optional, List, Union, Dict
from zoneinfo import ZoneInfo

import numpy as np
from PySide6.QtCore import QByteArray
from PySide6.QtGui import QImage, QPixmap
from pydantic import ConfigDict
from sqlalchemy import Column, LargeBinary, UniqueConstraint
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


class Element(SQLModel, table=True):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    name: str = Field(index=True)  # 移除了unique约束
    scene_id: str = Field(foreign_key="scene.id")  # 添加场景ID字段
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
    coordinate_x: int = Field(default=0)
    coordinate_y: int = Field(default=0)
    bgra: Optional[Union[bytes, np.ndarray]] = Field(sa_column=Column(LargeBinary))
    gray: Optional[Union[bytes, np.ndarray]] = Field(sa_column=Column(LargeBinary))
    mask: Optional[Union[bytes, np.ndarray]] = Field(sa_column=Column(LargeBinary))

    # 定义与场景的关系
    scene: "Scene" = Relationship(back_populates="elements")

    # 使用 UTC 时间
    created_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Shanghai")))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Shanghai")))

    # 使用复合唯一约束确保同一场景内元素名称唯一
    __table_args__ = (UniqueConstraint('scene_id', 'name', name='_scene_element_uc'),)


def element_to_qpixmap(element: Element, data_field: str = "bgra") -> Optional[QPixmap]:
    """将Element对象中的PNG压缩格式图像数据转换为QPixmap"""
    if not element:
        return None

    if data_field not in ["bgra", "gray", "mask"]:
        print(f"不支持的数据字段: {data_field}")
        return None

    image_data = getattr(element, data_field, None)
    if not image_data:
        print(f"元素的{data_field}字段数据为空")
        return None

    try:
        # 直接从压缩的字节数据创建QImage
        q_byte_array = QByteArray(image_data)
        q_image = QImage.fromData(q_byte_array, "PNG")

        if q_image and not q_image.isNull():
            # 根据数据类型转换格式
            if data_field in ["gray", "mask"]:
                if q_image.format() != QImage.Format.Format_Grayscale8:
                    q_image = q_image.convertToFormat(QImage.Format.Format_Grayscale8)
            elif data_field == "bgra":
                if q_image.format() != QImage.Format.Format_ARGB32:
                    q_image = q_image.convertToFormat(QImage.Format.Format_ARGB32)

            return QPixmap.fromImage(q_image)
        else:
            print(f"无法创建{data_field}类型的QImage")
            return None

    except Exception as e:
        print(f"图像转换失败 ({data_field}): {str(e)}")
        return None


class Scene(SQLModel, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    name: str = Field(unique=True, index=True)

    # 修改为直接的一对多关系
    elements: List[Element] = Relationship(back_populates="scene")

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

    @cached_property
    def element_dict(self) -> Dict[str, Element]:
        return {elem.name: elem for elem in self.elements}
