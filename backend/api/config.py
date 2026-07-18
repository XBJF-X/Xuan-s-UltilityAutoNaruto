"""配置管理 API 路由"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class ConfigResponse(BaseModel):
    id: str
    username: str
    # TODO: 完整的配置模型


@router.get("/", response_model=list[ConfigResponse])
async def list_configs():
    """获取所有配置列表"""
    # TODO: 从 Config 模块读取
    return []


@router.get("/{config_id}", response_model=ConfigResponse)
async def get_config(config_id: str):
    """获取单个配置详情"""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.put("/{config_id}")
async def update_config(config_id: str):
    """更新配置"""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/")
async def create_config():
    """新建配置"""
    raise HTTPException(status_code=501, detail="Not implemented yet")