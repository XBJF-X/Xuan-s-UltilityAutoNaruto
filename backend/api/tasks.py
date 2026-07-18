"""任务管理 API 路由"""
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/")
async def list_tasks():
    """获取所有任务列表及状态"""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/{task_name}")
async def get_task(task_name: str):
    """获取单个任务详情"""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/{task_name}/execute")
async def execute_task(task_name: str):
    """手动执行指定任务"""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.put("/{task_name}/activation")
async def toggle_task_activation(task_name: str):
    """启用/禁用任务"""
    raise HTTPException(status_code=501, detail="Not implemented yet")