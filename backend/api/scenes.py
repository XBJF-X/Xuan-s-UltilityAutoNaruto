"""场景管理 API 路由"""
import logging
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.utils import get_real_path
from backend.tools.resource_db import ResourceDBManager

router = APIRouter()
logger = logging.getLogger("ScenesAPI")

_db_manager: Optional[ResourceDBManager] = None


def get_db() -> ResourceDBManager:
    global _db_manager
    if _db_manager is None:
        _db_manager = ResourceDBManager(
            db_dir=Path(get_real_path("src")),
            parent_logger=logger,
        )
    return _db_manager


class SceneSummary(BaseModel):
    id: str
    name: str
    element_count: int
    out_edge_count: int
    in_edge_count: int
    created_at: str
    updated_at: str


class SceneDetail(BaseModel):
    id: str
    name: str
    elements: List[dict]
    out_edges: List[dict]
    in_edges: List[dict]
    created_at: str
    updated_at: str


class CreateSceneRequest(BaseModel):
    name: str


class UpdateSceneRequest(BaseModel):
    name: Optional[str] = None
    new_name: Optional[str] = None  # 重命名时使用


class EdgeRequest(BaseModel):
    source: str
    target: str


def scene_to_summary(scene) -> dict:
    return {
        "id": scene.id,
        "name": scene.name,
        "element_count": len(scene.elements),
        "out_edge_count": len(scene.out_edges),
        "in_edge_count": len(scene.in_edges),
        "created_at": str(scene.created_at),
        "updated_at": str(scene.updated_at),
    }


def scene_to_detail(scene) -> dict:
    return {
        "id": scene.id,
        "name": scene.name,
        "elements": [
            {
                "id": e.id,
                "name": e.name,
                "type": e.type.value if hasattr(e.type, 'value') else str(e.type),
                "threshold": e.threshold,
            }
            for e in scene.elements
        ],
        "out_edges": [
            {
                "id": e.id,
                "source": e.source_scene.name,
                "target": e.target_scene.name,
            }
            for e in scene.out_edges
        ],
        "in_edges": [
            {
                "id": e.id,
                "source": e.source_scene.name,
                "target": e.target_scene.name,
            }
            for e in scene.in_edges
        ],
        "created_at": str(scene.created_at),
        "updated_at": str(scene.updated_at),
    }


@router.get("/")
async def list_scenes():
    """获取所有场景（含概要信息）"""
    db = get_db()
    scenes = db.get_all_scenes()
    return [scene_to_summary(s) for s in scenes]


@router.get("/{scene_id}")
async def get_scene(scene_id: str):
    """获取单个场景详情"""
    db = get_db()
    # 支持按 id 或 name 查找场景
    for scene in db.get_all_scenes():
        if scene.id == scene_id or scene.name == scene_id:
            return scene_to_detail(scene)
    raise HTTPException(status_code=404, detail="场景不存在")


@router.post("/")
async def create_scene(req: CreateSceneRequest):
    """新建场景"""
    db = get_db()
    ok = db.add_scene(req.name)
    if not ok:
        raise HTTPException(status_code=400, detail="创建场景失败，可能名称已存在")
    # 返回新场景
    for scene in db.get_all_scenes():
        if scene.name == req.name:
            return scene_to_detail(scene)
    raise HTTPException(status_code=500, detail="场景创建后无法读取")


@router.put("/{scene_id}")
async def update_scene(scene_id: str, req: UpdateSceneRequest):
    """更新场景（支持重命名）"""
    db = get_db()
    # 查找场景
    target_scene = None
    for scene in db.get_all_scenes():
        if scene.id == scene_id or scene.name == scene_id:
            target_scene = scene
            break
    if not target_scene:
        raise HTTPException(status_code=404, detail="场景不存在")
    if req.new_name:
        ok = db.rename_scene(target_scene.name, req.new_name)
        if not ok:
            raise HTTPException(status_code=400, detail="重命名失败")
    return {"ok": True}


@router.delete("/{scene_id}")
async def delete_scene(scene_id: str):
    """删除场景（含所有元素和边）"""
    db = get_db()
    for scene in db.get_all_scenes():
        if scene.id == scene_id or scene.name == scene_id:
            db.delete_scene(scene.name)
            return {"ok": True}
    raise HTTPException(status_code=404, detail="场景不存在")


@router.post("/edges")
async def add_edge(req: EdgeRequest):
    """添加场景间边关系"""
    db = get_db()
    ok = db.add_scene_edge(req.source, req.target)
    if not ok:
        raise HTTPException(status_code=400, detail="添加边失败")
    return {"ok": True}


@router.delete("/edges")
async def delete_edge(req: EdgeRequest):
    """删除场景间边关系"""
    db = get_db()
    ok = db.delete_scene_edge(req.source, req.target)
    if not ok:
        raise HTTPException(status_code=400, detail="删除边失败")
    return {"ok": True}


@router.get("/{scene_id}/image")
async def get_scene_image(scene_id: str):
    """获取场景截图（需要设备连接）"""
    raise HTTPException(status_code=503, detail="需要设备连接才能获取截图，请先启动调度器")