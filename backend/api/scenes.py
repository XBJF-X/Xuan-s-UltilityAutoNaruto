"""场景管理 API 路由"""
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/")
async def list_scenes():
    """获取所有场景（含图数据）"""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/{scene_id}")
async def get_scene(scene_id: str):
    """获取单个场景详情"""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/")
async def create_scene():
    """新建场景"""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.put("/{scene_id}")
async def update_scene(scene_id: str):
    """更新场景"""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.delete("/{scene_id}")
async def delete_scene(scene_id: str):
    """删除场景"""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/{scene_id}/image")
async def get_scene_image(scene_id: str):
    """获取场景截图"""
    raise HTTPException(status_code=501, detail="Not implemented yet")