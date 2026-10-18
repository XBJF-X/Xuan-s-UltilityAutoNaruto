"""更新链路端点：版本、依赖检查、检查更新、热更新、大更新、进度查询。

阶段 3.4：由 backend/api/utils.py 拆分而来；
阶段 3.4（后半，第四批）：**业务逻辑已全部下沉** `backend/services/update_service.py`
（平台/PAT/更新源、检查更新、完整性校验、热更新与大更新的下载安装链路、进度状态），
本模块只剩路由适配与同名再导出。

模块级 logger 名为 "backend.api.utils"（与拆分前一致，保证日志连续性与
既有测试的 assertLogs("backend.api.utils") 继续有效）。"""
import logging

import requests  # noqa: F401  <- 保持 mock.patch("backend.api.utils.requests.get") 可用
from backend.api.schemas import VersionResponse
from backend.api.utils.common import (
    _github_pat_configured,
    _read_local_version,
)
from backend.api.utils.deps import (
    check_dependency,
)
from backend.services.update_service import (
    backup_for_hot_update as _backup_for_hot_update,
    check_full_update as _check_full_update,
    check_update as _service_check_update,
    do_apply_update as _do_apply_update,
    do_apply_release_update as _do_apply_release_update,
    get_latest_sha as _get_latest_sha,
    read_local_sha as _read_local_sha,
    set_update_status as _set_update_status,
    start_apply_release_update,
    start_apply_update,
    update_status_snapshot as _update_status_snapshot,
    verify_update_integrity as _verify_update_integrity,
    write_restart_request as _write_restart_request,
    UPDATE_EXCLUDE_DIRS as _UPDATE_EXCLUDE_DIRS,
    UPDATE_EXCLUDE_FILES as _UPDATE_EXCLUDE_FILES,
    UPDATE_STATUS as _UPDATE_STATUS,
    UPDATE_VERIFY_TLS as _UPDATE_VERIFY_TLS,
)

from fastapi import APIRouter, Body

logger = logging.getLogger("backend.api.utils")

router = APIRouter()


@router.get("/dependency-check")
def dependency_check():
    """依赖健康检查：版本是否满足 MIN_RELEASE_TAG + 关键模块是否缺失。

    前端启动时调用，发现异常时弹窗引导用户前往 Release 更新。
    另外附带 `github_pat_configured`（**只报"是否已配置"，不回传 token 本身**）：
    `GET /api/settings/` 会明文返回整段 `[助手设置]`（含 GithubPAT / 二级密码），
    因此状态展示不该依赖它（见 docs/refactor-plan-2026.md §7.7）。
    """
    result = check_dependency(include_ocr=True)
    # 汇总后端启动时导入失败的路由模块（main.py 逐个导入容错并写入登记表；
    # 阶段 3.4：不再 `import backend.main`，消除 api → main 的反向依赖）
    try:
        from backend.runtime import module_registry
        failed = module_registry.failed_modules()
        if failed:
            result["missing_modules"] = list(result["missing_modules"]) + list(failed)
            result["ok"] = False
    except Exception as e:
        logger.warning("汇总路由模块导入失败清单时出错: %s", e)
    # 更新源 PAT 配置状态（布尔值；token 本身绝不进入接口响应或日志）
    try:
        result["github_pat_configured"] = _github_pat_configured()
    except Exception as e:
        logger.warning("读取 GithubPAT 配置状态失败: %s", e)
        result["github_pat_configured"] = False
    return result


@router.get("/version", response_model=VersionResponse)
async def get_local_version():
    """读取随包分发的 _version.py 版本号（供前端展示"当前客户端版本"）。

    与 check-update 不同：本接口不访问外部更新源，网络异常（更新源不可达）时
    仍能返回本地版本，前端在"检查更新"弹窗中任何状态都能看到当前版本。
    """
    return {"ok": True, "version": _read_local_version()}


@router.get("/check-update")
def check_update():
    """检查更新：对比本地 version.json 与更新源分支，返回云端提交历史（实现见 update_service）"""
    return _service_check_update()


# ============================================================
# 3. 应用更新（后台线程 + 进度轮询；实现见 services/update_service.py）
# ============================================================
@router.post("/apply-update")
async def apply_update(payload: dict | None = Body(default=None)):
    """下载并应用更新（后台线程执行，进度通过 /utils/update-status 轮询）。

    请求体可选 ``{"sha": "<commit>"}``：指定后拉取该提交（即使当前已是最新也允许，
    用于更新窗口里逐条 commit 的「拉取」按钮）；不传则更新到分支最新提交。
    """
    target = ""
    if isinstance(payload, dict):
        target = str(payload.get("sha") or "").strip()
    return start_apply_update(target or None)


@router.post("/apply-release-update")
async def apply_release_update():
    """大更新：下载最新 Release 安装包并请求程序自动重启安装（后台执行）"""
    return start_apply_release_update()


@router.get("/update-status")
async def update_status():
    """查询更新任务进度（实现见 update_service.update_status_snapshot）"""
    return _update_status_snapshot()
