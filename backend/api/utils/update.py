"""更新链路端点：版本、依赖检查、检查更新、热更新、大更新、进度查询。

阶段 3.4：由 backend/api/utils.py 拆分而来；
模块级 logger 名为 "backend.api.utils"（与拆分前一致，保证日志连续性与
既有测试的 assertLogs("backend.api.utils") 继续有效）。"""
import json
import re
import shutil
import threading
import time
import zipfile

import requests

import logging

from backend.api.schemas import VersionResponse
from backend.api.utils.common import (
    _BRANCH,
    _INSTALLER_ASSET_PREFIX,
    _STATUS_LOCK,
    _UPDATE_STATUS,
    _UPDATE_VERIFY_TLS,
    _api_url,
    _get_releases_url,
    _github_pat_configured,
    _is_major_minor_update,
    _platform_headers,
    _read_local_version,
    _read_min_release_tag,
    _select_platforms,
    _version_gt,
)
from backend.api.utils.deps import (
    check_dependency,
)
from backend.utils import get_real_path
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter

logger = logging.getLogger("backend.api.utils")

router = APIRouter()


def _check_full_update(local_version: str, platform: dict = None) -> dict:
    """查询更新源最新 Release，判断是否存在需要走安装包的大更新。

    按更新源配置依次尝试平台；某平台未发布 Release（404）时降级到下一个平台；
    全部平台均无 Release 时视为"无大更新"（has_update=False），不阻塞热更新检查。
    """
    platforms = [platform] if platform else _select_platforms()
    tried = []
    for pf in platforms:
        tried.append(pf["label"])
        try:
            resp = requests.get(
                _api_url(pf, "releases/latest"),
                headers=_platform_headers(pf), verify=_UPDATE_VERIFY_TLS, timeout=15,
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
                if name.lower().startswith(_INSTALLER_ASSET_PREFIX.lower()) and name.lower().endswith(".exe"):
                    asset = a
                    break
            # 仅 major/minor 提升才触发大更新；同 minor 的 PATCH 级 Release 走热更新
            has_update = (
                bool(asset)
                and bool(local_version)
                and _version_gt(version, local_version)
                and _is_major_minor_update(version, local_version)
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
        except Exception:
            continue
    return {
        "ok": True, "has_update": False,
        "tag": "", "version": "", "name": "",
        "published_at": "", "body": "", "local_version": local_version,
        "asset": None, "source": " / ".join(tried) or "none",
    }


def _write_restart_request(mode: str, installer: str = "") -> bool:
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


def _backup_for_hot_update(project_root: Path):
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


def _read_local_sha() -> Optional[str]:
    try:
        vf = Path(get_real_path("version.json"))
        if vf.exists():
            with open(vf, "r", encoding="utf-8") as f:
                return json.load(f)["commit"]["sha"]
    except Exception:
        pass
    return None


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
    """检查更新：对比本地 version.json 与 GitHub v17 分支，返回云端提交历史"""
    current_sha = _read_local_sha()
    # 本地版本：既用于大更新/依赖库版本判定，也随响应返回供前端展示（各分支都要带上）
    local_version = _read_local_version()
    try:
        # 按更新源配置依次尝试平台（auto = github 优先、gitee 兜底），分支请求成功即使用该平台
        used_platform = None
        latest_sha = latest_message = ""
        commits = []
        current_commit = None
        for pf in _select_platforms():
            try:
                resp = requests.get(
                    _api_url(pf, f"branches/{_BRANCH}"),
                    headers=_platform_headers(pf), verify=_UPDATE_VERIFY_TLS, timeout=15,
                )
            except Exception:
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
                    _api_url(pf, "commits"),
                    params={"sha": _BRANCH, "per_page": 20},
                    headers=_platform_headers(pf), verify=_UPDATE_VERIFY_TLS, timeout=15,
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
            except Exception:
                pass

            # 本地提交详情（云端历史中没有时按 sha 单独拉取）
            if current_sha:
                for c in commits:
                    if c["sha"] == current_sha:
                        current_commit = c
                        break
                if not current_commit:
                    try:
                        c_resp = requests.get(
                            _api_url(pf, f"commits/{current_sha}"),
                            headers=_platform_headers(pf), verify=_UPDATE_VERIFY_TLS, timeout=15,
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
                    except Exception:
                        pass
            break  # 分支请求成功即使用该平台

        if used_platform is None:
            logger.warning("检查更新失败：更新源（GitHub/Gitee）均不可达")
            return {"ok": False, "local_version": local_version,
                    "message": "检查更新失败：更新源（GitHub/Gitee）均不可达"}

        has_update = current_sha is None or current_sha != latest_sha

        # 大更新检查：更新源 Releases/latest 版本对比（依赖库/正式版本走安装包）
        full = _check_full_update(local_version, used_platform)
        full_update = bool(full.get("ok") and full.get("has_update"))

        # 依赖库版本检查：本 commit 需要的最旧 ReleaseTag（根目录 MIN_RELEASE_TAG）
        # 热更新只替换代码、不替换 _version.py（随安装包分发）。若本地版本低于本 commit
        # 所需版本，说明缺少对应安装包中的依赖库（OCR 模型/DLL 等），必须走 Release 更新。
        required_tag, required_version = _read_min_release_tag()
        deprecate = (
            bool(required_version)
            and bool(local_version)
            and _version_gt(required_version, local_version)
        )
        if deprecate:
            full_update = True
            if full.get("ok"):
                full["has_update"] = True
                # 云端最新 Release 仍低于本 commit 所需版本时（所需 Release 尚未发布），
                # 置空 asset，前端改为引导用户前往 Release 页面手动下载
                if full.get("version") and _version_gt(required_version, full["version"]):
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
            full["release_url"] = _get_releases_url(used_platform)

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


# ============================================================
# 3. 应用更新（后台线程 + 进度轮询）
# ============================================================
_UPDATE_EXCLUDE_DIRS = {
    ".git", "log", "config", "frontend_node_modules", ".venv", "__pycache__",
    "release", "test_scene", "image", ".idea", "node_modules",
    "del", ".update_tmp", ".update_backup",
}
_UPDATE_EXCLUDE_FILES = {".clineignore"}


def _set_update_status(**kwargs):
    with _STATUS_LOCK:
        _UPDATE_STATUS.update(kwargs)


_SHA_SUFFIX_RE = re.compile(r"-(?P<sha>[0-9a-f]{7,40})$")


def _verify_update_integrity(src_dir: Path, platform: dict) -> None:
    """把解压出的源码目录钉到"已确认的云端提交 SHA"上。

    GitHub 的 zipball 顶层目录名为 ``{repo}-{commit_sha}``，因此可以用它做内容绑定：
    下载 → 解压后若目录名里的 sha 与 `_get_latest_sha()` 查到的提交不一致，说明
    （在已启用 TLS 校验的前提下）内容被替换或更新源发生了漂移 → 中止更新并保留
    `.update_backup`，绝不覆盖 backend/ 与 frontend/dist。

    Gitee 的 archive 目录名是 ``{repo}-{branch}``（不含 sha），只能依赖 TLS；
    目录名无法识别时记 WARNING 放行，避免因命名差异把正常更新卡死。
    """
    match = _SHA_SUFFIX_RE.search(src_dir.name)
    if not match:
        logger.warning(
            "更新包目录名 %r 不含提交 SHA，跳过完整性绑定（依赖 TLS 校验）", src_dir.name)
        return
    got = match.group("sha")
    if platform.get("key") != "github":
        logger.info("更新源 %s 的目录 SHA 前缀=%s（非 GitHub，未做提交比对）",
                    platform.get("label"), got)
        return
    expected = _get_latest_sha()
    if not expected:
        logger.warning("无法获取云端最新提交 SHA，跳过完整性绑定（依赖 TLS 校验）")
        return
    if not expected.startswith(got) and not got.startswith(expected):
        raise RuntimeError(
            f"更新包完整性校验失败：下载内容的提交 {got} 与云端最新提交 "
            f"{expected[:7]} 不一致，已中止更新（未修改任何程序文件）")
    logger.info("更新包完整性校验通过（提交 %s）", got[:7])


@router.post("/apply-update")
async def apply_update():
    """下载并应用云端最新版本（后台线程执行，进度通过 /utils/update-status 轮询）"""
    with _STATUS_LOCK:
        if _UPDATE_STATUS["running"]:
            logger.info("热更新请求被忽略：更新已在执行中")
            return {"ok": False, "message": "更新已在执行中"}
        _UPDATE_STATUS.update({
            "running": True, "phase": "", "percent": 0,
            "message": "", "error": "", "output": None,
        })
    threading.Thread(target=_do_apply_update, daemon=True).start()
    return {"ok": True, "message": "更新任务已启动"}


def _do_apply_update():
    try:
        project_root = Path(get_real_path(""))
        tmp_root = project_root / ".update_tmp"
        if tmp_root.exists():
            shutil.rmtree(tmp_root, ignore_errors=True)
        tmp_root.mkdir(parents=True, exist_ok=True)

        # ---- 1. 下载 zipball（按更新源配置依次尝试平台）----
        _set_update_status(phase="downloading", percent=5, message="正在下载云端最新版本...")
        zip_path = tmp_root / "update.zip"
        download_ok = False
        for pf in _select_platforms():
            zip_url = pf["zip_url"].format(owner=pf["owner"], repo=pf["repo"], branch=_BRANCH)
            try:
                with requests.get(zip_url, verify=_UPDATE_VERIFY_TLS, timeout=60, stream=True) as r:
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
                                _set_update_status(phase="downloading", percent=pct, message=f"下载中 {downloaded // 1024}KB / {total // 1024}KB")
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
            _set_update_status(phase="error", percent=0, running=False,
                               message="更新包下载失败：所有更新源均不可达", error="download_failed")
            return

        # ---- 2. 解压 ----
        _set_update_status(phase="extracting", percent=50, message="正在解压更新包...")
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
        _verify_update_integrity(src_dir, pf)

        # ---- 2.4 热更新前备份 backend + frontend/dist（失败可回滚）----
        _backup_for_hot_update(project_root)

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

        # ---- 3. 替换文件 ----
        all_files = sorted(p for p in src_dir.rglob("*") if p.is_file())
        total_files = len(all_files)
        copied = 0
        skipped_files = []
        for i, src_file in enumerate(all_files):
            rel = src_file.relative_to(src_dir)
            parts = rel.parts
            if any(part in _UPDATE_EXCLUDE_DIRS for part in parts):
                continue
            if rel.name in _UPDATE_EXCLUDE_FILES:
                continue
            dst = project_root / rel
            # 场景资源数据库覆盖前自动备份（保护用户本地编辑；同名 .bak 保留多份仅最新）
            if rel.as_posix() == "src/database.db" and dst.exists():
                try:
                    shutil.copy2(dst, dst.with_name("database.db.bak"))
                except Exception:
                    pass
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst)
                copied += 1
            except Exception:
                skipped_files.append(str(rel))
            pct = 50 + int((i + 1) / total_files * 40)
            _set_update_status(phase="replacing", percent=pct, message=f"正在替换文件 {i + 1}/{total_files}：{rel}")

        # ---- 4. 更新 version.json ----
        _set_update_status(phase="writing-version", percent=92, message="正在更新版本记录...")
        latest = _get_latest_sha()
        vf = Path(get_real_path("version.json"))
        if latest:
            with open(vf, "w", encoding="utf-8") as f:
                json.dump({"commit": {"sha": latest}}, f, ensure_ascii=False, indent=2)

        # ---- 5. 清理 ----
        shutil.rmtree(tmp_root, ignore_errors=True)

        # ---- 6. 请求程序自动重启（launcher 检测到 restart_request.json 后自动重启）----
        _write_restart_request(mode="hot")
        _set_update_status(
            phase="done", percent=100, running=False,
            message=f"更新完成，共更新 {copied} 个文件，程序即将自动重启生效。",
            output=str(project_root),
        )
    except Exception as e:
        logger.error("热更新失败: %s", e, exc_info=e)
        _set_update_status(phase="error", percent=0, running=False, message=f"更新失败：{e}", error=str(e))


@router.post("/apply-release-update")
async def apply_release_update():
    """大更新：下载最新 GitHub Release 安装包并请求程序自动重启安装（后台执行）。"""
    with _STATUS_LOCK:
        if _UPDATE_STATUS["running"]:
            logger.info("大更新请求被忽略：更新已在执行中")
            return {"ok": False, "message": "更新已在执行中"}
        _UPDATE_STATUS.update({
            "running": True, "phase": "", "percent": 0,
            "message": "", "error": "", "output": None,
        })
    threading.Thread(target=_do_apply_release_update, daemon=True).start()
    return {"ok": True, "message": "大更新任务已启动"}


def _do_apply_release_update():
    try:
        project_root = Path(get_real_path(""))
        local_version = _read_local_version()
        info = _check_full_update(local_version)
        if not info.get("ok"):
            _set_update_status(phase="error", percent=0, running=False,
                               message=info.get("message", "检查大更新失败"), error="check_failed")
            return
        if not info.get("has_update") or not info.get("asset"):
            _set_update_status(phase="error", percent=0, running=False,
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
        _set_update_status(phase="downloading-installer", percent=2, message="正在下载新版本安装包...")
        with requests.get(download_url, verify=_UPDATE_VERIFY_TLS, timeout=60, stream=True) as r:
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
                        _set_update_status(
                            phase="downloading-installer", percent=pct,
                            message=f"下载安装包中 {downloaded // 1024 // 1024}MB / {total // 1024 // 1024}MB",
                        )

        # ---- 2. 校验 sha256（GitHub asset digest 格式 sha256:<hex>）----
        _set_update_status(phase="verifying", percent=94, message="正在校验安装包完整性...")
        if expected_digest and ":" in expected_digest:
            import hashlib
            h = hashlib.sha256()
            with open(tmp_path, "rb") as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    h.update(chunk)
            actual = f"sha256:{h.hexdigest()}"
            if actual.lower() != expected_digest.lower():
                tmp_path.unlink(missing_ok=True)
                _set_update_status(phase="error", percent=0, running=False,
                                   message="安装包完整性校验失败，已中止", error="digest_mismatch")
                return
        tmp_path.replace(installer_path)

        # ---- 3. 请求程序退出并由 launcher 静默安装重启（full 模式）----
        if not _write_restart_request(mode="full", installer=str(installer_path)):
            _set_update_status(phase="error", percent=0, running=False,
                               message="无法写入重启请求", error="write_request")
            return
        _set_update_status(
            phase="done", percent=100, running=False,
            message=f"安装包已就绪（{asset['name']}），程序即将自动重启完成升级。",
            output=str(installer_path),
        )
    except Exception as e:
        logger.error("大更新失败: %s", e, exc_info=e)
        _set_update_status(phase="error", percent=0, running=False, message=f"大更新失败：{e}", error=str(e))


def _get_latest_sha() -> Optional[str]:
    """获取更新源分支最新 SHA（按更新源配置依次尝试平台）。"""
    for pf in _select_platforms():
        try:
            resp = requests.get(
                _api_url(pf, f"branches/{_BRANCH}"),
                headers=_platform_headers(pf), verify=_UPDATE_VERIFY_TLS, timeout=15,
            )
            if resp.status_code == 200:
                return json.loads(resp.content.decode("utf-8"))["commit"]["sha"]
        except Exception:
            continue
    return None


@router.get("/update-status")
async def update_status():
    """查询更新任务进度"""
    with _STATUS_LOCK:
        return dict(_UPDATE_STATUS)
