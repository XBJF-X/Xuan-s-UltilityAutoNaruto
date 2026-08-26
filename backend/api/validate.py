"""安装路径校验 API 路由 - 仅检查路径下关键文件存在性（不检查实例/分辨率）"""
import logging
import os
from typing import Literal, List

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger("ValidateAPI")


class InstallPathRequest(BaseModel):
    mode: Literal["mumu", "ld"]
    path: str


# MuMu 候选动态库相对路径（任一存在即视为 dll 满足）
MUMU_DLL_CANDIDATES = [
    "shell/sdk/external_renderer_ipc.dll",
    "nx_device/12.0/shell/sdk/external_renderer_ipc.dll",
    "nx_device/15.0/shell/sdk/external_renderer_ipc.dll",
    "nx_main/sdk/external_renderer_ipc.dll",
]

# MuMuManager.exe 候选相对路径（任一存在即视为满足）
MUMU_MANAGER_CANDIDATES = [
    "MuMuManager.exe",
    "shell/MuMuManager.exe",
    "nx_main/MuMuManager.exe",
]


@router.post("/install-path")
async def validate_install_path(req: InstallPathRequest):
    path = (req.path or "").strip()
    if not path:
        logger.warning("安装路径校验请求缺少路径（mode=%s）", req.mode)
        return {"ok": False, "dll_ok": False, "manager_ok": False, "missing": [""]}

    if req.mode == "mumu":
        # 动态库：任一候选存在即可
        dll_ok = any(os.path.exists(os.path.join(path, rel)) for rel in MUMU_DLL_CANDIDATES)
        # MuMuManager.exe：安装根目录 / shell / nx_main 子目录（任一存在即可）
        manager_ok = any(os.path.exists(os.path.join(path, rel)) for rel in MUMU_MANAGER_CANDIDATES)
        missing: List[str] = []
        if not dll_ok:
            missing.append("external_renderer_ipc.dll (MuMu 动态库)")
        if not manager_ok:
            missing.append("MuMuManager.exe")
        return {
            "ok": dll_ok and manager_ok,
            "dll_ok": dll_ok,
            "manager_ok": manager_ok,
            "missing": missing,
        }

    # 雷电
    ldconsole_ok = os.path.exists(os.path.join(path, "ldconsole.exe"))
    ldopengl_ok = os.path.exists(os.path.join(path, "ldopengl64.dll"))
    missing = []
    if not ldconsole_ok:
        missing.append("ldconsole.exe")
    if not ldopengl_ok:
        missing.append("ldopengl64.dll")
    return {
        "ok": ldconsole_ok and ldopengl_ok,
        "dll_ok": ldopengl_ok,
        "manager_ok": ldconsole_ok,
        "missing": missing,
    }