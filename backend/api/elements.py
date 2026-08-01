"""元素管理 API 路由"""
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel

from backend.utils import get_real_path
from backend.tools.resource_db import ResourceDBManager

router = APIRouter()
logger = logging.getLogger("ElementsAPI")

# 全局单例 — 与原有 PySide6 代码共享数据库
_db_manager: Optional[ResourceDBManager] = None


def get_db() -> ResourceDBManager:
    global _db_manager
    if _db_manager is None:
        _db_manager = ResourceDBManager(
            db_dir=Path(get_real_path("src")),
            parent_logger=logger,
        )
    return _db_manager


class ElementResponse(BaseModel):
    id: str
    name: str
    scene_id: str
    scene_name: Optional[str] = None
    type: str
    threshold: float
    ratio_x: float
    ratio_y: float
    match_type: str
    roi_x: int
    roi_y: int
    roi_width: int
    roi_height: int
    coordinate_x: int
    coordinate_y: int
    has_bgra: bool = False
    has_gray: bool = False
    has_mask: bool = False
    created_at: str
    updated_at: str


class UpdateElementRequest(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    threshold: Optional[float] = None
    ratio_x: Optional[float] = None
    ratio_y: Optional[float] = None
    match_type: Optional[str] = None
    roi_x: Optional[int] = None
    roi_y: Optional[int] = None
    roi_width: Optional[int] = None
    roi_height: Optional[int] = None
    coordinate_x: Optional[int] = None
    coordinate_y: Optional[int] = None


def element_to_response(elem, scene_name: Optional[str] = None) -> dict:
    """将 Element ORM 对象转为 JSON 响应"""
    return {
        "id": elem.id,
        "name": elem.name,
        "scene_id": elem.scene_id,
        "scene_name": scene_name or (elem.scene.name if elem.scene else None),
        "type": elem.type.value if hasattr(elem.type, 'value') else str(elem.type),
        "threshold": elem.threshold,
        "ratio_x": elem.ratio_x,
        "ratio_y": elem.ratio_y,
        "match_type": elem.match_type.value if hasattr(elem.match_type, 'value') else str(elem.match_type),
        "roi_x": elem.roi_x,
        "roi_y": elem.roi_y,
        "roi_width": elem.roi_width,
        "roi_height": elem.roi_height,
        "coordinate_x": elem.coordinate_x,
        "coordinate_y": elem.coordinate_y,
        "has_bgra": elem.bgra is not None,
        "has_gray": elem.gray is not None,
        "has_mask": elem.mask is not None,
        "created_at": str(elem.created_at),
        "updated_at": str(elem.updated_at),
    }


@router.get("/")
async def list_elements(scene_name: Optional[str] = Query(None)):
    """获取元素列表，可按场景名称筛选"""
    db = get_db()
    scenes = db.get_all_scenes()
    result = []
    for scene in scenes:
        if scene_name and scene.name != scene_name:
            continue
        for elem in scene.elements:
            result.append(element_to_response(elem, scene.name))
    return result


@router.get("/{element_id}")
async def get_element(element_id: str):
    """获取单个元素详情"""
    db = get_db()
    for scene in db.get_all_scenes():
        for elem in scene.elements:
            if elem.id == element_id:
                return element_to_response(elem, scene.name)
    raise HTTPException(status_code=404, detail="元素不存在")


@router.post("/")
async def create_element(
    file: UploadFile = File(...),
    scene_name: str = Form(...),
    name: str = Form(...),
    type: str = Form("IMG"),
    threshold: float = Form(0.8),
    ratio_x: float = Form(0.5),
    ratio_y: float = Form(0.5),
    match_type: str = Form("TEMPLATE"),
    roi_x: int = Form(0),
    roi_y: int = Form(0),
    roi_width: int = Form(1600),
    roi_height: int = Form(900),
    coordinate_x: int = Form(0),
    coordinate_y: int = Form(0),
):
    """新建元素（上传图片）"""
    db = get_db()
    # 读取上传图片
    img_bytes = await file.read()
    import cv2
    import numpy as np
    img_array = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="无法解码上传的图片")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    # 检查场景是否存在，不存在则创建
    existing_scenes = [s.name for s in db.get_all_scenes()]
    if scene_name not in existing_scenes:
        db.add_scene(scene_name)

    # 添加到场景
    success = db.add_element_to_scene(
        scene_name, name,
        type=type, threshold=threshold,
        ratio_x=ratio_x, ratio_y=ratio_y,
        match_type=match_type,
        roi_x=roi_x, roi_y=roi_y,
        roi_width=roi_width, roi_height=roi_height,
        coordinate_x=coordinate_x, coordinate_y=coordinate_y,
    )
    if not success:
        raise HTTPException(status_code=400, detail="创建元素失败，可能名称冲突")

    # 写入图像数据
    from backend.core.enums import ElementType
    elem_type = ElementType(type) if hasattr(ElementType, type) else ElementType.IMG
    if elem_type == ElementType.IMG:
        success, img_png = cv2.imencode('.png', img, [cv2.IMWRITE_PNG_COMPRESSION, 9])
        if success:
            db.update_element_info(scene_name, name, bgra=img_png.tobytes())

    # 返回新创建的元素
    elem = db.get_scene_element(scene_name, name)
    if not elem:
        raise HTTPException(status_code=500, detail="元素创建后无法读取")
    return element_to_response(elem, scene_name)


@router.put("/{element_id}")
async def update_element(element_id: str, req: UpdateElementRequest):
    """更新元素属性"""
    db = get_db()
    # 查找元素所在的场景
    for scene in db.get_all_scenes():
        for elem in scene.elements:
            if elem.id == element_id:
                kwargs = req.model_dump(exclude_none=True)
                if kwargs:
                    db.update_element_info(scene.name, elem.name, **kwargs)
                return {"ok": True}
    raise HTTPException(status_code=404, detail="元素不存在")


@router.delete("/{element_id}")
async def delete_element(element_id: str):
    """删除元素"""
    db = get_db()
    for scene in db.get_all_scenes():
        for elem in scene.elements:
            if elem.id == element_id:
                db.delete_element_from_scene(scene.name, elem.name)
                return {"ok": True}
    raise HTTPException(status_code=404, detail="元素不存在")


@router.get("/{element_id}/image")
async def get_element_image(element_id: str, type: str = Query("bgra")):
    """获取元素图片"""
    from fastapi.responses import Response
    db = get_db()
    for scene in db.get_all_scenes():
        for elem in scene.elements:
            if elem.id == element_id:
                data = getattr(elem, type, None)
                if data is None:
                    raise HTTPException(status_code=404, detail=f"元素没有 {type} 图像数据")
                media_type = "image/png"
                return Response(content=data, media_type=media_type)
    raise HTTPException(status_code=404, detail="元素不存在")