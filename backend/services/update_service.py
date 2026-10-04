"""更新链路服务（阶段 3.4 后半）

本模块承载"更新"相关的**知识与非路由逻辑**，路由只做参数映射：

- 更新源平台配置（GitHub / Gitee 双源与 auto 降级顺序）
- PAT 读取与请求头构造（`platform_headers` / `github_pat_configured`）
- 版本/Release 地址工具（`api_url` / `get_releases_url`）
- 更新进度状态（`UPDATE_STATUS` + `set_update_status` / `update_status_snapshot`）
- TLS 校验开关常量 `UPDATE_VERIFY_TLS`

分层：`api → services` 允许；本模块不依赖 api。
`api/utils/common.py` 以同名再导出（状态字典为**同一对象**），
`api/utils/update.py` 的路由继续复用这些名字，既有测试 patch 目标不受影响。

后续（下一轮）：把 `check_update`（提交历史比对）、`_verify_update_integrity`、
`_do_apply_update` / `_do_apply_release_update`（下载安装链路）也迁到本模块。
"""
from __future__ import annotations

import logging
import os
import threading

logger = logging.getLogger("UpdateService")

# ===== 仓库与分支 =====
GITHUB_OWNER = "XBJF-X"
GITHUB_REPO = "Xuan-s-UltilityAutoNaruto"
BRANCH = "v17"

# 大更新：GitHub Release 安装包资产名前缀
INSTALLER_ASSET_PREFIX = "XuanInstaller_V"

# 本 commit 需要的最旧依赖库 ReleaseTag（根目录 MIN_RELEASE_TAG 文件，随 commit 提交）
# 依赖库（OCR 模型/DLL 等）随 Release 安装包分发、热更新不携带；本地 _version.py
# 低于该版本时，检查更新将提示用户前往 Release 下载完整安装包。
# 文件名常量的唯一实现见 core/version_info。

# ===== 更新源平台配置（GitHub + Gitee 双源） =====
# Gitee OpenAPI（gitee.com/api/v5）的 branches/commits 响应结构与 GitHub 兼容（已实测），
# releases/latest 在未发布时返回 404（按"无 release"处理）；zipball 走 archive 直链匿名下载。
PLATFORM_GITHUB = {
    "key": "github",
    "label": "GitHub",
    "owner": GITHUB_OWNER,
    "repo": GITHUB_REPO,
    "api_base": "https://api.github.com/repos",
    "headers": {"Accept": "application/vnd.github+json"},
    "zip_url": "https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}",
    "releases_url": "https://github.com/{owner}/{repo}/releases",
}
PLATFORM_GITEE = {
    "key": "gitee",
    "label": "Gitee",
    "owner": "xuan-bu-jiu-fei",
    "repo": "Xuan-s-UltilityAutoNaruto",
    "api_base": "https://gitee.com/api/v5/repos",
    "headers": {},
    "zip_url": "https://gitee.com/{owner}/{repo}/repository/archive/{branch}.zip",
    "releases_url": "https://gitee.com/{owner}/{repo}/releases",
}
PLATFORMS = {"github": PLATFORM_GITHUB, "gitee": PLATFORM_GITEE}
# auto 时按此顺序尝试（github 优先；失败自动降级 gitee 兜底）
AUTO_PLATFORM_ORDER = ("github", "gitee")

# ===== 更新进度状态（前端轮询） =====
UPDATE_STATUS: dict = {
    "running": False,
    "phase": "",          # downloading / extracting / replacing / writing-version / done / error
    "percent": 0,
    "message": "",
    "error": "",
    "output": None,       # 更新解压根目录
}
STATUS_LOCK = threading.Lock()

# 更新链路必须校验 TLS 证书：旧实现全部 `verify=False`，而热更新会下载 zip →
# 解压 → 覆盖 backend/ 与 frontend/dist → 写 restart 请求触发重启；关闭证书校验
# 意味着任何能劫持 DNS/代理/局域网的人都能让客户端执行任意代码。
# 保留常量便于企业内网/自签代理场景显式调整（改这里即可，不要散落 verify=）。
UPDATE_VERIFY_TLS = True


def set_update_status(**kwargs) -> None:
    """更新更新进度状态（原 `_set_update_status`）"""
    with STATUS_LOCK:
        UPDATE_STATUS.update(kwargs)


def update_status_snapshot() -> dict:
    """读取更新进度快照（`GET /update-status` 的逻辑）"""
    with STATUS_LOCK:
        return dict(UPDATE_STATUS)


def get_update_source() -> str:
    """读取 [助手设置] 更新源：github / gitee / auto（默认 auto）。"""
    try:
        from backend.services.settings_service import SettingsService
        value = (SettingsService().get("助手设置", "更新源") or "").strip().lower()
        if value in PLATFORMS:
            return value
    except Exception as e:
        logger.debug("读取更新源设置失败，按 auto 处理: %s", e)
    return "auto"


def get_github_pat() -> str:
    """读取 [助手设置] GithubPAT（默认为空 = 匿名调用）。

    GitHub 对未认证请求限流很严（匿名 60 次/小时/IP），多人共用出口 IP 时
    「检查更新」很容易被 403 限流。填 PAT 后带 ``Authorization`` 头即可把额度
    提升到 5000 次/小时。空值/读取失败一律视为未配置。

    注意：本函数的返回值**绝不允许**写入日志或接口响应。
    """
    try:
        from backend.services.settings_service import SettingsService
        return (SettingsService().get("助手设置", "GithubPAT") or "").strip()
    except Exception as e:
        logger.debug("读取 GithubPAT 失败，按未配置处理: %s", e)
        return ""


def platform_headers(platform: dict) -> dict:
    """构造请求头：GitHub 平台在配置了 PAT 时附加认证头。

    Gitee 走匿名（其 OpenAPI 无需 token 即可读公开仓库），只有 GitHub 需要。
    """
    headers = dict(platform.get("headers") or {})
    if platform.get("key") == "github":
        pat = get_github_pat()
        if pat:
            headers["Authorization"] = f"Bearer {pat}"
    return headers


def github_pat_configured() -> bool:
    """当前是否已配置 GitHub PAT（供状态展示，不泄露 token 本身）。"""
    return bool(get_github_pat())


def select_platforms() -> list:
    """按优先级返回更新源平台列表（auto = github 优先、gitee 兜底）。"""
    source = get_update_source()
    if source in PLATFORMS:
        return [PLATFORMS[source]]
    return [PLATFORMS[key] for key in AUTO_PLATFORM_ORDER if key in PLATFORMS]


def api_url(platform: dict, path: str) -> str:
    return f"{platform['api_base']}/{platform['owner']}/{platform['repo']}/{path}"


def get_releases_url(platform: dict = None) -> str:
    pf = platform or select_platforms()[0]
    return pf["releases_url"].format(owner=pf["owner"], repo=pf["repo"])


__all__ = [
    "GITHUB_OWNER", "GITHUB_REPO", "BRANCH", "INSTALLER_ASSET_PREFIX",
    "PLATFORM_GITHUB", "PLATFORM_GITEE", "PLATFORMS", "AUTO_PLATFORM_ORDER",
    "UPDATE_STATUS", "STATUS_LOCK", "UPDATE_VERIFY_TLS",
    "set_update_status", "update_status_snapshot", "get_update_source",
    "get_github_pat", "platform_headers", "github_pat_configured",
    "select_platforms", "api_url", "get_releases_url",
]
