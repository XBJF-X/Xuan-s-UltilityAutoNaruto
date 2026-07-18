"""元素管理 API 路由"""
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/")
async def list_elements():
    """获取元素列表"""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/")
async def create_element():
    """新建元素（上传图片）"""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/{element_id}/image")
async def get_element_image(element_id: str):
    """获取元素图片（bgra/gray/mask）"""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.put("/{element_id}")
async def update_element(element_id: str):
    """更新元素"""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.delete("/{element_id}")
async def delete_element(element_id: str):
    """删除元素"""
    raise HTTPException(status_code=501, detail="Not implemented yet")