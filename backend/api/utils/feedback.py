"""反馈打包端点：日期/任务选项、打包、进度查询。

阶段 3.4：由 backend/api/utils.py 拆分而来；
阶段 3.4（后半）：业务逻辑下沉到 `backend/services/feedback_service.py`，本模块只做参数映射
（并再导出 `_do_feedback_package` / `_set_feedback_status`，保持 `backend.api.utils.*`
既有调用点与测试 patch 目标不变）。

模块级 logger 名为 "backend.api.utils"（与拆分前一致，保证日志连续性与
既有测试的 assertLogs("backend.api.utils") 继续有效）。"""
import logging

from backend.services.feedback_service import (
    collect_options,
    # 再导出给 backend/api/utils/__init__.py（本模块不直接使用，勿删）
    run_package as _do_feedback_package,  # noqa: F401
    set_status as _set_feedback_status,  # noqa: F401
    snapshot as _feedback_snapshot,
    start_package,
)

from fastapi import APIRouter

logger = logging.getLogger("backend.api.utils")

router = APIRouter()


# ============================================================
# 4. 反馈打包
# ============================================================
@router.get("/feedback/options")
def feedback_options(config_id: str = "", date: str = ""):
    """根据当前配置用户名的日志目录结构，生成反馈选择项（实现见 feedback_service）"""
    return collect_options(config_id, date)


@router.post("/feedback/package")
async def feedback_package(payload: dict):
    """后台打包反馈压缩包（实现见 feedback_service.start_package）

    body: {config_id, date, task_names: [str], save_path: str}
    """
    return start_package(
        payload.get("config_id", ""),
        payload.get("date", ""),
        payload.get("task_names") or [],
        payload.get("save_path", ""),
    )


@router.get("/feedback/package-status")
async def feedback_package_status():
    """查询反馈打包任务进度（实现见 feedback_service.snapshot）"""
    return _feedback_snapshot()
