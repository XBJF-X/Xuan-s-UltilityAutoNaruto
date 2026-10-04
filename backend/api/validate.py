"""安装路径校验 API 路由 - 仅检查路径下关键文件存在性（不检查实例/分辨率）"""
import logging
import os
from typing import Literal, List

from fastapi import APIRouter
from pydantic import BaseModel

from backend.core.emulator_env import (
    LD_CONSOLE_NAME, LD_DLL_NAME, MUMU_DLL_CANDIDATES, MUMU_MANAGER_CANDIDATES,
)

router = APIRouter()
logger = logging.getLogger("ValidateAPI")


class InstallPathRequest(BaseModel):
    mode: Literal["mumu", "ld"]
    path: str


# 候选清单的唯一实现已迁至 backend/core/emulator_env.py（阶段 3 单点化）；
# 这里保留同名别名以兼容既有 import（api/scheduler.py 曾从此处导入）。
__all__ = [
    "router", "InstallPathRequest", "validate_install_path",
    "MUMU_DLL_CANDIDATES", "MUMU_MANAGER_CANDIDATES", "LD_CONSOLE_NAME", "LD_DLL_NAME",
]


@router.post("/install-path")
async def validate_install_path(req: InstallPathRequest):
    path = (req.path or "").strip()
    if not path:
        logger.warning("安装路径校验请求缺少路径（mode=%s）", req.mode)
        return {"ok": False, "dll_ok": False, "manager_ok": False, "missing": [""]}

    if req.mode == "mumu":
        # 动态库 / MuMuManager.exe：各自候选任一存在即可（候选清单见 core/emulator_env）
        dll_ok = any(os.path.exists(os.path.join(path, rel)) for rel in MUMU_DLL_CANDIDATES)
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
    ldconsole_ok = os.path.exists(os.path.join(path, LD_CONSOLE_NAME))
    ldopengl_ok = os.path.exists(os.path.join(path, LD_DLL_NAME))
    missing = []
    if not ldconsole_ok:
        missing.append(LD_CONSOLE_NAME)
    if not ldopengl_ok:
        missing.append(LD_DLL_NAME)
    return {
        "ok": ldconsole_ok and ldopengl_ok,
        "dll_ok": ldopengl_ok,
        "manager_ok": ldconsole_ok,
        "missing": missing,
    }