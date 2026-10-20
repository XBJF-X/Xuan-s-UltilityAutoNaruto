"""恢复链路端点：本地更新包列表 + 离线回滚（不依赖更新链路）。

**刻意独立于 ``backend/api/utils`` 包**：`utils/__init__.py` 会 `include_router(
update.router)`，一旦更新链路被改坏（哪怕是导入失败），整个 `/api/utils` 路由都会
消失；本模块挂在 `_API_ROUTERS_SPEC` 里单独导入，更新层出问题时仍能给出回滚入口。

对应服务层：`backend/services/rollback_service.py`（自包含，不 import update_service）。
"""
import logging

from fastapi import APIRouter, Body

from backend.services import rollback_service

logger = logging.getLogger("backend.api.recovery")

router = APIRouter()


@router.get("/update-packages")
def update_packages():
    """本机保留的热更新包（回滚候选）。**不访问网络**，断网也可用。"""
    try:
        return rollback_service.packages_snapshot()
    except Exception as e:
        logger.error("读取更新包列表失败: %s", e, exc_info=e)
        return {"ok": False, "message": f"读取更新包列表失败：{e}", "packages": []}


@router.post("/rollback")
async def rollback(payload: dict | None = Body(default=None)):
    """回滚到指定提交（后台线程执行，进度见 /update-status 或 /rollback-status）。"""
    sha = ""
    if isinstance(payload, dict):
        sha = str(payload.get("sha") or "").strip()
    return rollback_service.start_rollback(sha)


@router.get("/rollback-status")
def rollback_status():
    """回滚进度（update_service 不可用时前端改轮询这个）。"""
    return rollback_service.status_snapshot()
