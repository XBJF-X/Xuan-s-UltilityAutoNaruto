"""全局设置 API 路由"""
from typing import Dict

from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.settings_service import SettingsService
from backend.api.schemas import OkResponse, SettingValueResponse

router = APIRouter()
settings_service = SettingsService()


class SetSettingRequest(BaseModel):
    section: str
    key: str
    value: str


@router.get("/", response_model=Dict[str, Dict[str, str]])
async def get_all_settings():
    return settings_service.get_all()


@router.get("/{section}/{key}", response_model=SettingValueResponse)
async def get_setting(section: str, key: str):
    return {"value": settings_service.get(section, key)}


@router.put("/", response_model=OkResponse)
async def set_setting(req: SetSettingRequest):
    settings_service.set(req.section, req.key, req.value)
    return {"ok": True}