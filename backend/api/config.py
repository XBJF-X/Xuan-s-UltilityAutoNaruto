"""配置管理 API 路由"""
from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.config_service import shared_config_service as config_service

router = APIRouter()


class ConfigSummary(BaseModel):
    id: str
    username: str
    path: str
    config_type: str = "持久"


class ConfigDetail(BaseModel):
    id: str
    username: str
    config_type: str = "持久"
    setting_dics: dict
    tasks: dict


class CreateConfigRequest(BaseModel):
    username: str
    config_type: str = "持久"  # 持久（账号配置）/ 临时（任务预设）


class UpdateConfigRequest(BaseModel):
    key: str
    value: Any


class UpdateTaskPrioritiesRequest(BaseModel):
    tasks: list[str]


class UpdateTaskOrderRequest(BaseModel):
    tasks: list[str]


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
    if req.config_type not in ("持久", "临时"):
        raise HTTPException(status_code=400, detail="config_type 只能为 持久/临时")
    config_id = config_service.create_config(req.username, req.config_type)
    if not config_id:
        raise HTTPException(status_code=500, detail="创建配置失败")
    data = config_service.get_config_full(config_id)
    return ConfigSummary(id=config_id, username=data["username"], path=str(config_service._config_path(config_id)), config_type=data["config_type"])


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


@router.put("/{config_id}/task-priorities")
async def update_task_priorities(config_id: str, req: UpdateTaskPrioritiesRequest):
    """批量更新任务优先级（按传入顺序分配优先级值）"""
    ok = config_service.set_task_priorities(config_id, req.tasks)
    if not ok:
        raise HTTPException(status_code=400, detail="更新失败")
    return {"ok": True}


@router.put("/{config_id}/task-order")
async def update_task_order(config_id: str, req: UpdateTaskOrderRequest):
    """保存任务执行顺序（临时预设的拖拽排序结果）"""
    ok = config_service.set_task_order(config_id, req.tasks)
    if not ok:
        raise HTTPException(status_code=400, detail="保存任务执行顺序失败")
    return {"ok": True}


@router.post("/{config_id}/duplicate")
async def duplicate_config(config_id: str):
    """复制配置：用户名加 _副本 后缀，其余参数全部照抄"""
    new_id = config_service.duplicate_config(config_id)
    if not new_id:
        raise HTTPException(status_code=400, detail="复制配置失败")
    data = config_service.get_config_full(new_id)
    return ConfigSummary(id=new_id, username=data["username"], path=str(config_service._config_path(new_id)), config_type=data["config_type"])


@router.put("/{config_id}/rename")
async def rename_config(config_id: str, req: UpdateConfigRequest):
    """重命名配置（修改用户名）"""
    ok = config_service.rename_config(config_id, str(req.value))
    if not ok:
        raise HTTPException(status_code=400, detail="重命名失败")
    return {"ok": True}


@router.delete("/{config_id}")
async def delete_config(config_id: str):
    config_service.delete_config(config_id)
    return {"ok": True}
