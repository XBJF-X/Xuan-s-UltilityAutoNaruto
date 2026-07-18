"""调度器管理 API 路由"""
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/start")
async def start_scheduler():
    """启动调度器"""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/stop")
async def stop_scheduler():
    """停止调度器"""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/status")
async def get_scheduler_status():
    """获取调度器状态"""
    raise HTTPException(status_code=501, detail="Not implemented yet")