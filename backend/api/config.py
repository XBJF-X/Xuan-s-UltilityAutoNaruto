"""配置管理 API 路由"""
from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.config_service import ConfigService

router = APIRouter()
config_service = ConfigService()


class ConfigSummary(BaseModel):
    id: str
    username: str
    path: str


class ConfigDetail(BaseModel):
    id: str
    username: str
    setting_dics: dict
    tasks: dict


class CreateConfigRequest(BaseModel):
    username: str


class UpdateConfigRequest(BaseModel):
    key: str
    value: Any


@router.get("/", response_model=list[ConfigSummary])
async def list_configs():
    return config_service.list_configs()


@router.get("/{config_id}", response_model=ConfigDetail)
async def get_config(config_id: str):
    data = config_service.get_config_full(config_id)
    if not data:
        raise HTTPException(status_code=404, detail="配置不存在")
    return data


@router.post("/", response_model=ConfigSummary)
async def create_config(req: CreateConfigRequest):
    config_id = config_service.create_config(req.username)
    if not config_id:
        raise HTTPException(status_code=500, detail="创建配置失败")
    data = config_service.get_config_full(config_id)
    return ConfigSummary(id=config_id, username=data["username"], path=str(config_service._config_path(config_id)))


@router.put("/{config_id}/setting")
async def update_setting(config_id: str, req: UpdateConfigRequest):
    ok = config_service.set_config_value(config_id, req.key, req.value)
    if not ok:
        raise HTTPException(status_code=400, detail="更新失败")
    return {"ok": True}


@router.put("/{config_id}/task/{task_name}")
async def update_task(config_id: str, task_name: str, req: UpdateConfigRequest):
    ok = config_service.set_task_base(config_id, task_name, req.key, req.value)
    if not ok:
        raise HTTPException(status_code=400, detail="更新失败")
    return {"ok": True}


@router.put("/{config_id}/task/{task_name}/param/{param_name}")
async def update_task_param(config_id: str, task_name: str, param_name: str, req: UpdateConfigRequest):
    ok = config_service.set_task_exe_param(config_id, task_name, param_name, req.value)
    if not ok:
        raise HTTPException(status_code=400, detail="更新失败")
    return {"ok": True}


@router.get("/default-tasks")
async def get_default_tasks():
    """获取 DefaultConfig 中的任务schema"""
    return config_service.get_task_schema()


@router.delete("/{config_id}")
async def delete_config(config_id: str):
    config_service.delete_config(config_id)
    return {"ok": True}