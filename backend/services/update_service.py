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

import hashlib
import json
import logging
import re
import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional
import zipfile

import requests

from backend.core.version_info import (
    is_major_minor_update,
    read_client_version,
    read_min_release_tag,
    version_gt,
)
from backend.utils import get_real_path

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
    "zip_commit_url": "https://codeload.github.com/{owner}/{repo}/zip/{ref}",
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
    "zip_commit_url": "https://gitee.com/{owner}/{repo}/repository/archive/{ref}.zip",
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


# ============================================================
# 检查更新（版本比对 + 云端提交历史）
# ============================================================

def check_full_update(local_version: str, platform: dict = None) -> dict:
    """查询更新源最新 Release，判断是否存在需要走安装包的大更新。

    按更新源配置依次尝试平台；某平台未发布 Release（404）时降级到下一个平台；
    全部平台均无 Release 时视为"无大更新"（has_update=False），不阻塞热更新检查。
    """
    platforms = [platform] if platform else select_platforms()
    tried = []
    for pf in platforms:
        tried.append(pf["label"])
        try:
            resp = requests.get(
                api_url(pf, "releases/latest"),
                headers=platform_headers(pf), verify=UPDATE_VERIFY_TLS, timeout=15,
            )
            if resp.status_code == 404:
                continue  # 该平台尚未发布 Release，降级尝试下一个平台
            if resp.status_code != 200:
                continue
            rel = json.loads(resp.content.decode("utf-8"))
            tag = str(rel.get("tag_name", ""))
            version = tag.lstrip("vV")
            asset = None
            for a in rel.get("assets", []) or []:
                name = str(a.get("name", ""))
                if name.lower().startswith(INSTALLER_ASSET_PREFIX.lower()) and name.lower().endswith(".exe"):
                    asset = a
                    break
            # 仅 major/minor 提升才触发大更新；同 minor 的 PATCH 级 Release 走热更新
            has_update = (
                bool(asset)
                and bool(local_version)
                and version_gt(version, local_version)
                and is_major_minor_update(version, local_version)
            )
            return {
                "ok": True,
                "has_update": has_update,
                "tag": tag,
                "version": version,
                "name": str(rel.get("name") or tag),
                "published_at": rel.get("published_at"),
                "body": (rel.get("body") or "").strip(),
                "local_version": local_version,
                "asset": {
                    "name": str(asset.get("name")),
                    "size": int(asset.get("size") or 0),
                    "download_url": str(asset.get("browser_download_url")
                                        or asset.get("download_url") or ""),
                    "digest": str(asset.get("digest") or ""),
                } if asset else None,
                "source": pf["label"],
            }
        except Exception as e:
            logger.debug("查询 %s Release 失败（尝试下一个平台）: %s", pf.get("label"), e)
            continue
    return {
        "ok": True, "has_update": False,
        "tag": "", "version": "", "name": "",
        "published_at": "", "body": "", "local_version": local_version,
        "asset": None, "source": " / ".join(tried) or "none",
    }


def check_update() -> dict:
    """检查更新：对比本地 version.json 与更新源分支，返回云端提交历史"""
    current_sha = read_local_sha()
    # 本地版本：既用于大更新/依赖库版本判定，也随响应返回供前端展示（各分支都要带上）
    local_version = read_client_version()
    try:
        # 按更新源配置依次尝试平台（auto = github 优先、gitee 兜底），分支请求成功即使用该平台
        used_platform = None
        latest_sha = latest_message = ""
        commits = []
        current_commit = None
        for pf in select_platforms():
            try:
                resp = requests.get(
                    api_url(pf, f"branches/{BRANCH}"),
                    headers=platform_headers(pf), verify=UPDATE_VERIFY_TLS, timeout=15,
                )
            except Exception as e:
                logger.debug("分支请求失败（尝试下一个平台）: %s", e)
                continue
            if resp.status_code != 200:
                continue
            used_platform = pf
            branch_data = json.loads(resp.content.decode("utf-8"))
            latest_sha = branch_data["commit"]["sha"]
            latest_message = branch_data["commit"]["commit"]["message"]

            # 提交历史
            try:
                commits_resp = requests.get(
                    api_url(pf, "commits"),
                    params={"sha": BRANCH, "per_page": 20},
                    headers=platform_headers(pf), verify=UPDATE_VERIFY_TLS, timeout=15,
                )
                if commits_resp.status_code == 200:
                    for c in json.loads(commits_resp.content.decode("utf-8")):
                        commits.append({
                            "sha": c["sha"],
                            "short_sha": c["sha"][:7],
                            "message": (c["commit"]["message"] or "").splitlines()[0],
                            "date": c["commit"]["committer"]["date"],
                            "author": (c["commit"]["author"].get("name") or ""),
                        })
            except Exception as e:
                # 提交历史属展示信息：失败不阻断检查更新，仅留痕
                logger.debug("拉取提交历史失败: %s", e)

            # 本地提交详情（云端历史中没有时按 sha 单独拉取）
            if current_sha:
                for c in commits:
                    if c["sha"] == current_sha:
                        current_commit = c
                        break
                if not current_commit:
                    try:
                        c_resp = requests.get(
                            api_url(pf, f"commits/{current_sha}"),
                            headers=platform_headers(pf), verify=UPDATE_VERIFY_TLS, timeout=15,
                        )
                        if c_resp.status_code == 200:
                            c = json.loads(c_resp.content.decode("utf-8"))
                            current_commit = {
                                "sha": c["sha"],
                                "short_sha": c["sha"][:7],
                                "message": (c["commit"]["message"] or "").splitlines()[0],
                                "date": c["commit"]["committer"]["date"],
                                "author": (c["commit"]["author"].get("name") or ""),
                            }
                    except Exception as e:
                        logger.debug("拉取本地提交详情失败: %s", e)
            break  # 分支请求成功即使用该平台

        if used_platform is None:
            logger.warning("检查更新失败：更新源（GitHub/Gitee）均不可达")
            return {"ok": False, "local_version": local_version,
                    "message": "检查更新失败：更新源（GitHub/Gitee）均不可达"}

        has_update = current_sha is None or current_sha != latest_sha

        # 大更新检查：更新源 Releases/latest 版本对比（依赖库/正式版本走安装包）
        full = check_full_update(local_version, used_platform)
        full_update = bool(full.get("ok") and full.get("has_update"))

        # 依赖库版本检查：本 commit 需要的最旧 ReleaseTag（根目录 MIN_RELEASE_TAG）
        # 热更新只替换代码、不替换 _version.py（随安装包分发）。若本地版本低于本 commit
        # 所需版本，说明缺少对应安装包中的依赖库（OCR 模型/DLL 等），必须走 Release 更新。
        required_tag, required_version = read_min_release_tag()
        deprecate = (
            bool(required_version)
            and bool(local_version)
            and version_gt(required_version, local_version)
        )
        if deprecate:
            full_update = True
            if full.get("ok"):
                full["has_update"] = True
                # 云端最新 Release 仍低于本 commit 所需版本时（所需 Release 尚未发布），
                # 置空 asset，前端改为引导用户前往 Release 页面手动下载
                if full.get("version") and version_gt(required_version, full["version"]):
                    full["asset"] = None
            else:
                full = {
                    "ok": True, "has_update": True, "tag": required_tag,
                    "version": required_version, "name": required_tag,
                    "published_at": "", "body": "", "local_version": local_version,
                    "asset": None,
                }
            full["deprecated"] = True
            full["required_tag"] = required_tag
            full["required_version"] = required_version
            full["release_url"] = get_releases_url(used_platform)

        # 有大更新时优先大更新（Release 包含全部变更）；否则走热更新
        update_type = "full" if full_update else ("hot" if has_update else "none")
        if full_update:
            if deprecate:
                message = (
                    f"当前版本 {local_version} 过低，本版本需要 {required_tag} 及以上的"
                    f"完整安装包（含依赖库），请前往 Release 更新"
                )
            else:
                message = f"检测到新版本 {full.get('version')}（正式版更新，需安装新版本）"
        elif has_update:
            message = f"检测到新版本：{latest_message}"
        else:
            message = "当前已是最新版本"
        return {
            "ok": True,
            "has_update": has_update or full_update,
            "update_type": update_type,
            "local_version": local_version,
            "current_sha": current_sha,
            "latest_sha": latest_sha,
            "latest_message": latest_message,
            "current_commit": current_commit,
            "commits": commits,
            "full": full,
            "message": message,
        }
    except Exception as e:
        logger.error("检查更新出错: %s", e, exc_info=e)
        return {"ok": False, "local_version": local_version,
                "message": f"检查更新出错：{e}"}


def read_local_sha() -> Optional[str]:
    """读取本地 version.json 的提交 sha（缺失/异常返回 None）"""
    try:
        vf = Path(get_real_path("version.json"))
        if vf.exists():
            with open(vf, "r", encoding="utf-8") as f:
                return json.load(f)["commit"]["sha"]
    except Exception as e:
        logger.debug("读取本地 version.json 失败: %s", e)
    return None


def write_restart_request(mode: str, installer: str = "") -> bool:
    """写重启请求文件（launcher 轮询识别），用于更新完成后程序自动重启。

    mode: hot  = 热更新完成，重启当前程序
          full = 大更新，使用安装包静默安装后重启
    """
    try:
        req = {
            "mode": mode,
            "installer": installer,
            "ts": datetime.now().isoformat(timespec="seconds"),
        }
        log_dir = Path(get_real_path("log"))
        log_dir.mkdir(parents=True, exist_ok=True)
        with open(log_dir / "restart_request.json", "w", encoding="utf-8") as f:
            json.dump(req, f, ensure_ascii=False, indent=2)
        logger.info("已写入重启请求: %s", req)
        return True
    except Exception as e:
        logger.warning("写入重启请求失败: %s", e)
        return False


def backup_for_hot_update(project_root: Path):
    """热更新替换前备份 backend + frontend/dist 到 .update_backup（失败可回滚）。"""
    try:
        backup_dir = project_root / ".update_backup"
        if backup_dir.exists():
            shutil.rmtree(backup_dir, ignore_errors=True)
        backup_dir.mkdir(parents=True, exist_ok=True)
        for rel in ("backend", "frontend/dist"):
            src = project_root / rel
            if src.exists():
                dst = backup_dir / rel
                if src.is_dir():
                    shutil.copytree(src, dst)
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
        logger.info("热更新前已备份 backend / frontend/dist 到 .update_backup")
        return backup_dir
    except Exception as e:
        logger.warning("热更新备份失败（继续更新，无回滚保护）: %s", e)
        return None


# ============================================================
# 应用更新（后台线程 + 进度轮询）
# ============================================================
UPDATE_EXCLUDE_DIRS = {
    ".git", "log", "config", "frontend_node_modules", ".venv", "__pycache__",
    "release", "test_scene", "image", ".idea", "node_modules",
    "del", ".update_tmp", ".update_backup",
}
UPDATE_EXCLUDE_FILES = {".clineignore"}

_SHA_SUFFIX_RE = re.compile(r"-(?P<sha>[0-9a-f]{7,40})$")
_COMMIT_SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")


def normalize_target_sha(value) -> Optional[str]:
    """校验并规范化前端传来的目标提交 SHA；非法值返回 None。

    只允许 7~40 位十六进制：该值会拼进下载 URL，必须严格校验（防注入/误传）。
    """
    text = str(value or "").strip()
    if not text:
        return None
    if not _COMMIT_SHA_RE.fullmatch(text):
        logger.warning("拒绝非法的目标提交 SHA: %r", text[:80])
        return None
    return text.lower()


def _file_sha256(path: Path) -> str:
    """计算文件 sha256（分块读取，避免大文件占用内存）。"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_replaced_files(project_root: Path, expected: dict[str, str]) -> None:
    """校验热更新是否真的覆盖了全部目标文件（内容一致、无遗漏）。

    :param project_root: 安装/开发根目录
    :param expected: ``{相对路径(posix): 源文件 sha256}``
    :raises RuntimeError: 任一文件缺失或 sha256 不一致（version.json 不得更新）

    只有本函数通过后调用方才允许写 version.json —— 这是「本地版本记录必须
    与实际文件一致」的保证：复制失败、被占用、被杀软拦截等情况下，宁可保留
    旧版本记录（下次仍会提示更新），也不能谎报已是最新。
    """
    missing: list[str] = []
    mismatched: list[str] = []
    for rel, expected_sha in expected.items():
        dst = project_root / rel
        if not dst.is_file():
            missing.append(rel)
            continue
        try:
            actual = _file_sha256(dst)
        except Exception as e:
            mismatched.append(f"{rel}（读取失败：{e}）")
            continue
        if actual != expected_sha:
            mismatched.append(f"{rel}（期望 {expected_sha[:8]}，实际 {actual[:8]}）")
    if missing or mismatched:
        problems = []
        if missing:
            problems.append(f"缺失 {len(missing)} 个：" + "、".join(missing[:5]))
        if mismatched:
            problems.append(f"内容不一致 {len(mismatched)} 个：" + "、".join(mismatched[:5]))
        raise RuntimeError(
            "更新文件校验失败（version.json 未更新）：" + "；".join(problems))
    logger.info("更新文件校验通过：%d 个文件均已覆盖且内容一致", len(expected))


def write_version_json(commit_sha: str) -> None:
    """写入 version.json（仅在文件替换与校验全部成功后调用）。

    额外写入 ``updated_by/updated_at``：安装目录里可能残留旧版遗留的
    version.json（例如切换分支前的 master SHA）。读取端据此判断该记录是否
    来自热更新，避免把过期 SHA 当成实时版本。
    """
    vf = Path(get_real_path("version.json"))
    payload = {
        "commit": {"sha": commit_sha},
        "updated_by": "hot-update",
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    with open(vf, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    logger.info("version.json 已更新为提交 %s", commit_sha[:7])


def refresh_build_info(commit_sha: str) -> None:
    """安装版存在 ``_build_info.py`` 时同步刷新其 commit/构建时间。

    ``_build_info.py`` 是打包快照，热更新不会自动重写；旧版启动横幅因此永远
    显示构建时的 commit。这里在更新成功后一并刷新（开发模式没有该文件，跳过）。
    """
    try:
        path = Path(get_real_path("_build_info.py"))
        if not path.exists():
            return
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        path.write_text(
            "# 由 build_release.py 自动生成，请勿手动修改\n"
            f'__build_time__ = "{now}"\n'
            f'__commit__ = "{commit_sha}"\n'
            f'__branch__ = "{BRANCH}"\n',
            encoding="utf-8",
        )
        logger.info("_build_info.py 已刷新为提交 %s", commit_sha[:7])
    except Exception as e:
        # 横幅信息不是更新成败的关键：记录 WARNING 并继续（version.json 已更新）
        logger.warning("刷新 _build_info.py 失败（不影响本次更新）: %s", e)



def get_latest_sha() -> Optional[str]:
    """获取更新源分支最新 SHA（按更新源配置依次尝试平台）。"""
    for pf in select_platforms():
        try:
            resp = requests.get(
                api_url(pf, f"branches/{BRANCH}"),
                headers=platform_headers(pf), verify=UPDATE_VERIFY_TLS, timeout=15,
            )
            if resp.status_code == 200:
                return json.loads(resp.content.decode("utf-8"))["commit"]["sha"]
        except Exception as e:
            logger.debug("查询 %s 最新 SHA 失败（尝试下一个平台）: %s", pf.get("label"), e)
            continue
    return None


def verify_update_integrity(src_dir: Path, platform: dict,
                            expected_sha: Optional[str] = None) -> None:
    """把解压出的源码目录钉到"已确认的云端提交 SHA"上。

    GitHub 的 zipball 顶层目录名为 ``{repo}-{commit_sha}``，因此可以用它做内容绑定：
    下载 → 解压后若目录名里的 sha 与目标提交不一致，说明
    （在已启用 TLS 校验的前提下）内容被替换或更新源发生了漂移 → 中止更新并保留
    `.update_backup`，绝不覆盖 backend/ 与 frontend/dist。

    :param expected_sha: 目标提交（按 commit 拉取时传入）；为空则查询分支最新 SHA。

    Gitee 的 archive 目录名可能不含 sha，只能依赖 TLS；目录名无法识别时记
    WARNING 放行，避免因命名差异把正常更新卡死。
    """
    match = _SHA_SUFFIX_RE.search(src_dir.name)
    if not match:
        logger.warning(
            "更新包目录名 %r 不含提交 SHA，跳过完整性绑定（依赖 TLS 校验）", src_dir.name)
        return
    got = match.group("sha")
    if expected_sha:
        expected = expected_sha
    elif platform.get("key") == "github":
        expected = get_latest_sha()
    else:
        logger.info("更新源 %s 的目录 SHA 前缀=%s（非 GitHub 且未指定目标提交，未做提交比对）",
                    platform.get("label"), got)
        return
    if not expected:
        logger.warning("无法获取目标提交 SHA，跳过完整性绑定（依赖 TLS 校验）")
        return
    if not expected.startswith(got) and not got.startswith(expected):
        raise RuntimeError(
            f"更新包完整性校验失败：下载内容的提交 {got} 与目标提交 "
            f"{expected[:7]} 不一致，已中止更新（未修改任何程序文件）")
    logger.info("更新包完整性校验通过（提交 %s）", got[:7])


def start_apply_update(target_sha: Optional[str] = None) -> dict:
    """启动热更新后台任务（原 `POST /apply-update` 的逻辑）。

    :param target_sha: 目标提交；为空表示更新到分支最新提交。传入任意云端提交
        时用于「拉取指定 commit」（即使当前已是最新也允许回退/重拉）。
    """
    raw = str(target_sha or "").strip()
    target = normalize_target_sha(raw) if raw else None
    if raw and target is None:
        return {"ok": False, "message": f"非法的提交 SHA：{raw[:40]}"}
    with STATUS_LOCK:
        if UPDATE_STATUS["running"]:
            logger.info("热更新请求被忽略：更新已在执行中")
            return {"ok": False, "message": "更新已在执行中"}
        UPDATE_STATUS.update({
            "running": True, "phase": "", "percent": 0,
            "message": "", "error": "", "output": None,
        })
    threading.Thread(target=do_apply_update, args=(target,), daemon=True).start()
    return {"ok": True, "message": "更新任务已启动"}


def start_apply_release_update() -> dict:
    """启动大更新后台任务（原 `POST /apply-release-update` 的逻辑）"""
    with STATUS_LOCK:
        if UPDATE_STATUS["running"]:
            logger.info("大更新请求被忽略：更新已在执行中")
            return {"ok": False, "message": "更新已在执行中"}
        UPDATE_STATUS.update({
            "running": True, "phase": "", "percent": 0,
            "message": "", "error": "", "output": None,
        })
    threading.Thread(target=do_apply_release_update, daemon=True).start()
    return {"ok": True, "message": "大更新任务已启动"}


def do_apply_update(target_sha: Optional[str] = None) -> None:
    """热更新线程体（原 `_do_apply_update`）：下载 zipball → 完整性绑定 → 备份 →
    替换文件 → **覆盖校验** → 写 version.json → 请求重启。

    :param target_sha: 目标提交；为空表示分支最新提交。指定后下载该 commit 的
        归档包（允许在当前已是最新时拉取任意历史 commit）。
    """
    target = normalize_target_sha(target_sha) if target_sha else None
    if target_sha and target is None:
        set_update_status(phase="error", percent=0, running=False,
                          message=f"更新失败：非法的提交 SHA {str(target_sha)[:40]}",
                          error="invalid_sha")
        return
    target_label = f"提交 {target[:7]}" if target else "云端最新版本"
    try:
        project_root = Path(get_real_path(""))
        tmp_root = project_root / ".update_tmp"
        if tmp_root.exists():
            shutil.rmtree(tmp_root, ignore_errors=True)
        tmp_root.mkdir(parents=True, exist_ok=True)

        # ---- 1. 下载 zipball（按更新源配置依次尝试平台）----
        set_update_status(phase="downloading", percent=5,
                          message=f"正在下载{target_label}...")
        zip_path = tmp_root / "update.zip"
        download_ok = False
        pf = None
        for pf in select_platforms():
            if target:
                zip_url = pf["zip_commit_url"].format(
                    owner=pf["owner"], repo=pf["repo"], ref=target)
            else:
                zip_url = pf["zip_url"].format(
                    owner=pf["owner"], repo=pf["repo"], branch=BRANCH)
            try:
                with requests.get(zip_url, verify=UPDATE_VERIFY_TLS, timeout=60, stream=True) as r:
                    r.raise_for_status()
                    # Gitee 匿名下载 archive 可能触发机器验证：返回 200 + HTML 验证页而非 zip。
                    # 先根据 Content-Type 识别非 zip 响应，直接降级到下一个平台（如 GitHub）。
                    ctype = (r.headers.get("Content-Type") or "").lower()
                    if "zip" not in ctype and ("html" in ctype or "json" in ctype or "text/plain" in ctype):
                        logger.warning(f"从 {pf['label']} 下载更新包被拦截（Content-Type={ctype or '未知'}，疑似人机验证页），降级下一个更新源")
                        continue
                    total = int(r.headers.get("Content-Length", 0))
                    downloaded = 0
                    with open(zip_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024 * 256):
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total:
                                pct = 5 + int(downloaded / total * 45)
                                set_update_status(phase="downloading", percent=pct, message=f"下载中 {downloaded // 1024}KB / {total // 1024}KB")
                    # 下载完成后校验文件确为 zip（部分验证页/代理未带正确 Content-Type 时的兜底判断）
                    if not zipfile.is_zipfile(zip_path):
                        logger.warning(f"从 {pf['label']} 下载的更新包不是有效 zip（可能返回了机器验证网页），降级下一个更新源")
                        continue
                    download_ok = True
                    break
            except Exception as e:
                logger.warning(f"从 {pf['label']} 下载更新包失败: {e}")
                continue
        if not download_ok:
            set_update_status(phase="error", percent=0, running=False,
                              message="更新包下载失败：所有更新源均不可达", error="download_failed")
            return

        # ---- 2. 解压 ----
        set_update_status(phase="extracting", percent=50, message="正在解压更新包...")
        extract_dir = tmp_root / "extract"
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)
        # 找到唯一顶层目录
        top_dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
        if not top_dirs:
            raise RuntimeError("更新包结构异常：未找到源码目录")
        src_dir = top_dirs[0]
        # ---- 2-1. 完整性绑定：把解压内容钉到"已确认的云端提交"上 ----
        verify_update_integrity(src_dir, pf, expected_sha=target)

        # ---- 2.4 热更新前备份 backend + frontend/dist（失败可回滚）----
        backup_for_hot_update(project_root)

        # ---- 2.5 释放数据库文件占用（Windows 下 SQLite 连接会锁定文件，覆盖前必须释放）----
        # 更新完成后提示用户重启程序；重启后 ResourceDBManager 会自动重建连接读取新库
        try:
            from backend.tools.resource_db import ResourceDBManager
            _db_inst = ResourceDBManager._instance
            if _db_inst is not None and getattr(_db_inst, "engine", None) is not None:
                _db_inst.engine.dispose()
                logger.info("已释放 ResourceDBManager 数据库连接，准备覆盖 src/database.db")
        except Exception as e:
            logger.warning(f"释放数据库连接失败（继续执行更新）：{e}")

        # ---- 3. 替换文件（先登记目标清单，替换后逐个校验）----
        all_files = sorted(p for p in src_dir.rglob("*") if p.is_file())
        planned: list[tuple[Path, Path]] = []
        for src_file in all_files:
            rel_path = src_file.relative_to(src_dir)
            if any(part in UPDATE_EXCLUDE_DIRS for part in rel_path.parts):
                continue
            if rel_path.name in UPDATE_EXCLUDE_FILES:
                continue
            planned.append((rel_path, src_file))
        total_files = len(planned)
        copied = 0
        failed_files: list[str] = []
        expected_files: dict[str, str] = {}
        for i, (rel, src_file) in enumerate(planned):
            dst = project_root / rel
            # 场景资源数据库覆盖前自动备份（保护用户本地编辑；同名 .bak 保留一份）
            if rel.as_posix() == "src/database.db" and dst.exists():
                try:
                    shutil.copy2(dst, dst.with_name("database.db.bak"))
                except Exception as e:
                    logger.warning(f"备份 database.db 失败（继续更新）：{e}")
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                src_sha = _file_sha256(src_file)
                shutil.copy2(src_file, dst)
                expected_files[rel.as_posix()] = src_sha
                copied += 1
            except Exception as e:
                failed_files.append(f"{rel.as_posix()}（{type(e).__name__}: {e}）")
                logger.warning("替换文件失败: %s -> %s: %s", src_file, dst, e)
            pct = 50 + int((i + 1) / max(total_files, 1) * 40)
            set_update_status(phase="replacing", percent=pct, message=f"正在替换文件 {i + 1}/{total_files}：{rel}")

        if total_files == 0:
            raise RuntimeError("更新包中没有可替换的文件（排除目录/文件后为空），已中止")
        if failed_files:
            raise RuntimeError(
                f"有 {len(failed_files)} 个文件替换失败（version.json 未更新）："
                + "；".join(failed_files[:5]))

        # ---- 3-1. 覆盖校验：每个目标文件都必须存在且内容一致（无遗漏）----
        set_update_status(phase="verifying-files", percent=91,
                          message="正在校验更新文件覆盖情况...")
        verify_replaced_files(project_root, expected_files)

        # ---- 4. 更新 version.json（仅在覆盖校验通过后）----
        set_update_status(phase="writing-version", percent=92, message="正在更新版本记录...")
        final_sha = target or get_latest_sha()
        if not final_sha:
            raise RuntimeError("无法获取本次更新的提交 SHA，version.json 未更新")
        write_version_json(final_sha)
        refresh_build_info(final_sha)

        # ---- 5. 清理 ----
        shutil.rmtree(tmp_root, ignore_errors=True)

        # ---- 6. 请求程序自动重启（launcher 检测到 restart_request.json 后自动重启）----
        write_restart_request(mode="hot")
        set_update_status(
            phase="done", percent=100, running=False,
            message=f"更新完成（{final_sha[:7]}），共更新 {copied} 个文件，程序即将自动重启生效。",
            output=str(project_root),
        )
    except Exception as e:
        logger.error("热更新失败: %s", e, exc_info=e)
        set_update_status(phase="error", percent=0, running=False, message=f"更新失败：{e}", error=str(e))


def do_apply_release_update() -> None:
    """大更新线程体（原 `_do_apply_release_update`）：下载安装包 → 校验 sha256 → 请求安装重启"""
    try:
        project_root = Path(get_real_path(""))
        local_version = read_client_version()
        info = check_full_update(local_version)
        if not info.get("ok"):
            set_update_status(phase="error", percent=0, running=False,
                              message=info.get("message", "检查大更新失败"), error="check_failed")
            return
        if not info.get("has_update") or not info.get("asset"):
            set_update_status(phase="error", percent=0, running=False,
                              message="当前已是最新正式版本，无需安装更新", error="no_update")
            return

        asset = info["asset"]
        download_url = asset["download_url"]
        expected_digest = asset.get("digest") or ""
        pending = project_root / "log" / "pending_update"
        pending.mkdir(parents=True, exist_ok=True)
        installer_path = pending / asset["name"]
        tmp_path = pending / (asset["name"] + ".part")

        # ---- 1. 下载安装包（stream + 进度）----
        set_update_status(phase="downloading-installer", percent=2, message="正在下载新版本安装包...")
        with requests.get(download_url, verify=UPDATE_VERIFY_TLS, timeout=60, stream=True) as r:
            r.raise_for_status()
            total = int(r.headers.get("Content-Length", 0))
            downloaded = 0
            with open(tmp_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 256):
                    if not chunk:
                        continue
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = 2 + int(downloaded / total * 90)
                        set_update_status(
                            phase="downloading-installer", percent=pct,
                            message=f"下载安装包中 {downloaded // 1024 // 1024}MB / {total // 1024 // 1024}MB",
                        )

        # ---- 2. 校验 sha256（GitHub asset digest 格式 sha256:<hex>）----
        set_update_status(phase="verifying", percent=94, message="正在校验安装包完整性...")
        if expected_digest and ":" in expected_digest:
            import hashlib
            h = hashlib.sha256()
            with open(tmp_path, "rb") as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    h.update(chunk)
            actual = f"sha256:{h.hexdigest()}"
            if actual.lower() != expected_digest.lower():
                tmp_path.unlink(missing_ok=True)
                set_update_status(phase="error", percent=0, running=False,
                                  message="安装包完整性校验失败，已中止", error="digest_mismatch")
                return
        tmp_path.replace(installer_path)

        # ---- 3. 请求程序退出并由 launcher 静默安装重启（full 模式）----
        if not write_restart_request(mode="full", installer=str(installer_path)):
            set_update_status(phase="error", percent=0, running=False,
                              message="无法写入重启请求", error="write_request")
            return
        set_update_status(
            phase="done", percent=100, running=False,
            message=f"安装包已就绪（{asset['name']}），程序即将自动重启完成升级。",
            output=str(installer_path),
        )
    except Exception as e:
        logger.error("大更新失败: %s", e, exc_info=e)
        set_update_status(phase="error", percent=0, running=False, message=f"大更新失败：{e}", error=str(e))


__all__ = [
    "GITHUB_OWNER", "GITHUB_REPO", "BRANCH", "INSTALLER_ASSET_PREFIX",
    "PLATFORM_GITHUB", "PLATFORM_GITEE", "PLATFORMS", "AUTO_PLATFORM_ORDER",
    "UPDATE_STATUS", "STATUS_LOCK", "UPDATE_VERIFY_TLS",
    "set_update_status", "update_status_snapshot", "get_update_source",
    "get_github_pat", "platform_headers", "github_pat_configured",
    "select_platforms", "api_url", "get_releases_url",
    "check_full_update", "check_update", "read_local_sha",
    "write_restart_request", "backup_for_hot_update",
    "UPDATE_EXCLUDE_DIRS", "UPDATE_EXCLUDE_FILES", "get_latest_sha",
    "normalize_target_sha", "verify_replaced_files", "write_version_json",
    "refresh_build_info",
    "verify_update_integrity", "start_apply_update", "start_apply_release_update",
    "do_apply_update", "do_apply_release_update",
]
