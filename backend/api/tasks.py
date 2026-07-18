"""任务 schema API 路由 - 提供 DefaultConfig 中的任务定义"""
from fastapi import APIRouter
from backend.services.config_service import ConfigService

router = APIRouter()
config_service = ConfigService()


@router.get("/schema")
async def get_task_schema():
    """返回 DefaultConfig 中的完整任务定义（参数结构、枚举值等）"""
    return config_service.get_task_schema()