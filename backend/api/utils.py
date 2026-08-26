"""工具类 API 路由 - 历史日志 / 检查更新 / 应用更新 / 反馈打包"""
import importlib
import json
import logging
import os
import re
import shutil
import subprocess
import threading
import zipfile
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Optional


import requests
from fastapi import APIRouter

from backend.utils import get_real_path
from backend.services.config_service import shared_config_service

router = APIRouter()

logger = logging.getLogger(__name__)

# ============================================================
# 模块级后台任务状态（供前端轮询）
# ============================================================
_UPDATE_STATUS: dict = {
    "running": False,
    "phase": "",          # downloading / extracting / replacing / writing-version / done / error
    "percent": 0,
    "message": "",
    "error": "",
    "output": None,       # 更新解压根目录
}

_FEEDBACK_STATUS: dict = {
    "running": False,
    "percent": 0,
    "current": "",
    "message": "",
    "error": "",
    "output": None,       # 生成的 zip 文件路径
}

_STATUS_LOCK = threading.Lock()


# ============================================================
# 通用辅助
# ============================================================
def _browse_folder(title: str):
    import win32com.shell.shell as shell
    folder_selected = shell.SHBrowseForFolder()
    if folder_selected:
        # 将返回的 PIDL (项目标识符列表) 转换为实际的文件系统路径。
        # 优先使用 Unicode 版本（SHGetPathFromIDListW），直接返回 str，天然支持中文路径；
        # 回退到 ANSI 版本（SHGetPathFromIDList）时返回的是系统 ANSI 代码页
        # （中文系统为 GBK/cp936）编码的 bytes，必须按 mbcs（系统 ANSI 代码页）解码，
        # 不能按 utf-8 解码——否则含中文的路径（如 MuMu/雷电安装目录）会抛 UnicodeDecodeError。
        pidl = folder_selected[0]
        get_path = getattr(shell, "SHGetPathFromIDListW", None) or shell.SHGetPathFromIDList
        path = get_path(pidl)
        if isinstance(path, bytes):
            path = path.decode("mbcs")
        return path
    return None


def _get_config_username(config_id: str) -> str:
    """根据 config_id 获取配置用户名（用于定位日志目录）"""
    try:
        data = shared_config_service.get_config_full(config_id)
        return data.get("username", "") if data else ""
    except Exception:
        return ""


def _read_tail(file_path, max_lines: int = 1000) -> str:
    """高效读取文件末尾最多 max_lines 行（大文件从尾部按块读取）"""
    try:
        size = os.path.getsize(file_path)
    except OSError:
        return ""
    if size == 0:
        return ""
    block_size = 8192
    with open(file_path, "rb") as f:
        data = b""
        pos = size
        # 从尾部读取直到攒够足够行或读完整文件
        while pos > 0 and data.count(b"\n") < max_lines + 1:
            read_size = min(block_size, pos)
            pos -= read_size
            f.seek(pos)
            chunk = f.read(read_size)
            data = chunk + data
            if len(data) > max_lines * 512:  # 防超长单行无限增长
                break
    text = data.decode("utf-8", errors="ignore")
    lines = text.splitlines()
    return "\n".join(lines[-max_lines:])


_LOG_LINE_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
    r"\[(?P<level>\w+)\]\s+"
    r"(?P<logger>[^\s|]+(?:\s*\|\s*)?)?"
    r""
)


def parse_log_lines(text: str, default_config_id: str = "") -> list[dict]:
    """把日志文本解析为标准日志条目列表

    日志格式: 2026-08-01 18:52:18 [INFO] SchedulerService_Config_1 | message
    兼容无 logger 前缀的行（[INFO] message）。
    """
    entries = []
    for line in text.splitlines():
        line = line.rstrip()
        if not line:
            continue
        m = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+\[(\w+)\]\s+(.*)$", line)
        if not m:
            continue
        ts_str, level, rest = m.group(1), m.group(2), m.group(3)
        # rest 可能为 "logger | message" 或直接 "message"
        if " | " in rest:
            logger_name, message = rest.split(" | ", 1)
        else:
            logger_name, message = "", rest
        try:
            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").timestamp() * 1000
        except ValueError:
            continue
        cid = default_config_id
        m2 = re.search(r"(Config_\d+)", logger_name)
        if m2:
            cid = m2.group(1)
        entries.append({
            "level": level,
            "message": message,
            "ts": int(ts),
            "config_id": cid,
            "logger_name": logger_name,
        })
    return entries


# ============================================================
# 1. 历史日志恢复
# ============================================================
@router.get("/log-history")
async def get_log_history(config_id: str = "", limit: int = 500):
    """读取历史日志文件供前端刷新/重连后恢复展示

    - config_id 为空或 "__global__"：读取 Main.log*，仅返回无归属(config_id=="")的程序日志
    - config_id = Config_N：读取 log/<用户名>/<日期>/Xuan.log*(轮转) + Main.log 中该配置行
    """
    try:
        limit = max(100, min(int(limit), 5000))
    except (TypeError, ValueError):
        limit = 500
    log_root = Path(get_real_path("log"))
    try:
        from backend.log_setup import DATE_FORMAT  # noqa: F401
    except Exception:
        pass

    if not config_id or config_id == "__global__":
        entries: list[dict] = []
        main_files = sorted(
            log_root.glob("Main.log*"),
            key=lambda p: p.name, reverse=True,
        )
        for fp in main_files[:6]:
            text = _read_tail(str(fp), limit)
            entries.extend(parse_log_lines(text, default_config_id=""))
        # 只保留无归属（程序本身）的日志
        entries = [e for e in entries if not e["config_id"]]
        entries.sort(key=lambda e: e["ts"])
        return {"ok": True, "config_id": "__global__", "entries": entries[-limit:]}

    # 指定配置：优先读取配置日志目录（今天的 + 轮转），再补 Main.log 中该配置行
    username = _get_config_username(config_id)
    candidate_files: list[Path] = []
    if username:
        user_dir = log_root / username
        if user_dir.exists():
            # 最近若干天目录下的 Xuan.log*（含日期目录），按日期倒序
            date_dirs = sorted(
                (d for d in user_dir.iterdir() if d.is_dir()),
                key=lambda d: d.name, reverse=True,
            )
            for date_dir in date_dirs[:3]:
                for fp in sorted(date_dir.glob("Xuan.log*"), key=lambda p: p.name, reverse=True):
                    candidate_files.append(fp)
    if not candidate_files:
        # 兜底：从 Main.log 提取该配置的日志
        for fp in sorted(log_root.glob("Main.log*"), key=lambda p: p.name, reverse=True)[:6]:
            text = _read_tail(str(fp), limit * 2)
            for e in parse_log_lines(text, default_config_id=""):
                if e["config_id"] == config_id:
                    candidate_files.append(fp)  # 仅用于占位计数
        entries = []
        for fp in candidate_files[:6]:
            text = _read_tail(str(fp), limit)
            entries.extend(parse_log_lines(text, default_config_id=config_id))
        entries = [e for e in entries if e["config_id"] == config_id]
        entries.sort(key=lambda e: e["ts"])
        return {"ok": True, "config_id": config_id, "entries": entries[-limit:]}

    entries = []
    seen = set()
    for fp in candidate_files[:10]:
        text = _read_tail(str(fp), limit)
        for e in parse_log_lines(text, default_config_id=config_id):
            key = (e["ts"], e["message"])
            if key in seen:
                continue
            seen.add(key)
            entries.append(e)
    # main.log 中该配置的行（可能日期目录被清理）
    for fp in sorted(log_root.glob("Main.log*"), key=lambda p: p.name, reverse=True)[:6]:
        text = _read_tail(str(fp), limit)
        for e in parse_log_lines(text, default_config_id=""):
            if e["config_id"] == config_id and (e["ts"], e["message"]) not in seen:
                seen.add((e["ts"], e["message"]))
                entries.append(e)
    entries.sort(key=lambda e: e["ts"])
    return {"ok": True, "config_id": config_id, "entries": entries[-limit:]}


# ============================================================
# 2. 检查更新（增强：提交历史）
# ============================================================
_GITHUB_OWNER = "XBJF-X"
_GITHUB_REPO = "Xuan-s-UltilityAutoNaruto"
_BRANCH = "v17"

# 大更新：GitHub Release 安装包资产名前缀
_INSTALLER_ASSET_PREFIX = "XuanInstaller_V"

# 本 commit 需要的最旧依赖库 ReleaseTag（根目录 MIN_RELEASE_TAG 文件，随 commit 提交）
# 依赖库（OCR 模型/DLL 等）随 Release 安装包分发、热更新不携带；本地 _version.py
# 低于该版本时，检查更新将提示用户前往 Release 下载完整安装包。
_MIN_RELEASE_TAG_FILE = "MIN_RELEASE_TAG"

# ===== 更新源平台配置（GitHub + Gitee 双源） =====
# Gitee OpenAPI（gitee.com/api/v5）的 branches/commits 响应结构与 GitHub 兼容（已实测），
# releases/latest 在未发布时返回 404（按"无 release"处理）；zipball 走 archive 直链匿名下载。
_PLATFORM_GITHUB = {
    "key": "github",
    "label": "GitHub",
    "owner": _GITHUB_OWNER,
    "repo": _GITHUB_REPO,
    "api_base": "https://api.github.com/repos",
    "headers": {"Accept": "application/vnd.github+json"},
    "zip_url": "https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}",
    "releases_url": "https://github.com/{owner}/{repo}/releases",
}
_PLATFORM_GITEE = {
    "key": "gitee",
    "label": "Gitee",
    "owner": "xuan-bu-jiu-fei",
    "repo": "Xuan-s-UltilityAutoNaruto",
    "api_base": "https://gitee.com/api/v5/repos",
    "headers": {},
    "zip_url": "https://gitee.com/{owner}/{repo}/repository/archive/{branch}.zip",
    "releases_url": "https://gitee.com/{owner}/{repo}/releases",
}
_PLATFORMS = {"github": _PLATFORM_GITHUB, "gitee": _PLATFORM_GITEE}
# auto 时按此顺序尝试（github 优先；失败自动降级 gitee 兜底）
_AUTO_PLATFORM_ORDER = ("github", "gitee")

# 兼容旧引用（GitHub Releases 页面地址）
_RELEASES_URL = _PLATFORM_GITHUB["releases_url"]


def _get_update_source() -> str:
    """读取 [助手设置] 更新源：github / gitee / auto（默认 auto）。"""
    try:
        from backend.services.settings_service import SettingsService
        v = (SettingsService().get("助手设置", "更新源") or "").strip().lower()
        if v in _PLATFORMS:
            return v
    except Exception:
        pass
    return "auto"


def _select_platforms() -> list:
    """按优先级返回更新源平台列表（auto = github 优先、gitee 兜底）。"""
    src = _get_update_source()
    if src in _PLATFORMS:
        return [_PLATFORMS[src]]
    return [_PLATFORMS[k] for k in _AUTO_PLATFORM_ORDER if k in _PLATFORMS]


def _api_url(platform: dict, path: str) -> str:
    return f"{platform['api_base']}/{platform['owner']}/{platform['repo']}/{path}"


def _get_releases_url(platform: dict = None) -> str:
    pf = platform or _select_platforms()[0]
    return pf["releases_url"].format(owner=pf["owner"], repo=pf["repo"])


def _read_local_version() -> str:
    """读取随包分发的 _version.py 中的版本号（如 0.17.0）；读取失败返回空串。"""
    try:
        vf = Path(get_real_path("_version.py"))
        if vf.exists():
            text = vf.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
            if m:
                return m.group(1).strip()
    except Exception:
        pass
    return ""


def _read_min_release_tag() -> tuple[str, str]:
    """读取根目录 MIN_RELEASE_TAG（本 commit 需要的最旧依赖库 ReleaseTag）。

    返回 (tag, version)，如 ("v0.17.17", "0.17.17")；文件缺失或无法解析返回 ("", "")。
    该文件随 commit 提交，标识当前代码依赖的安装包资源（OCR 模型/DLL 等）的最低版本。
    """
    try:
        f = Path(get_real_path(_MIN_RELEASE_TAG_FILE))
        if not f.exists():
            return "", ""
        text = f.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"[vV]?(\d+\.\d+\.\d+(?:[-.][0-9A-Za-z.-]+)?)", text)
        if not m:
            return "", ""
        version = m.group(1)
        return f"v{version}", version
    except Exception:
        return "", ""


# 关键依赖模块探测清单（find_spec 仅查是否存在、不实际加载，避免触发重型初始化）
_DEPENDENCY_PROBE_MODULES = (
    "onnxruntime",
    "minidevice",
    "adbutils",
    "uiautomator2",
    "cv2",
    "numpy",
)


def check_dependency() -> dict:
    """依赖健康检查：本 commit 所需依赖库版本是否满足 + 关键 Python 依赖是否缺失。

    用于：①调度器启动前硬拦截（不满足禁止启动，防止因代码依赖新依赖库导致任务恶性 BUG）；
         ②前端启动时弹窗提示用户前往 Release 下载完整安装包。
    """
    import importlib.util

    local_version = _read_local_version()
    required_tag, required_version = _read_min_release_tag()
    deprecated = (
        bool(required_version)
        and bool(local_version)
        and _version_gt(required_version, local_version)
    )

    missing_modules = []
    for mod_name in _DEPENDENCY_PROBE_MODULES:
        try:
            spec = importlib.util.find_spec(mod_name)
            if spec is None:
                missing_modules.append(mod_name)
        except (ImportError, AttributeError):
            missing_modules.append(mod_name)
        except Exception:
            # 其余异常（模块自身初始化报错等）不归类为缺失，避免误报
            pass

    return {
        "ok": not deprecated and not missing_modules,
        "deprecated": deprecated,
        "local_version": local_version,
        "required_tag": required_tag,
        "required_version": required_version,
        "missing_modules": missing_modules,
        "release_url": _get_releases_url(),
    }


def _parse_version(v: str):
    """解析语义化版本号 -> (major, minor, patch, prerelease)；无法解析返回 None。"""
    if not v:
        return None
    m = re.match(r"^[vV]?(\d+)\.(\d+)\.(\d+)(?:[-.]([0-9A-Za-z.-]+))?$", v.strip())
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4) or "")


def _version_gt(a: str, b: str) -> bool:
    """判断版本 a > b（语义化版本）；任一方无法解析时退化为字符串比较。"""
    pa, pb = _parse_version(a), _parse_version(b)
    if pa is None or pb is None:
        return a > b
    # 主版本段
    if pa[:3] != pb[:3]:
        return pa[:3] > pb[:3]
    # 预发布段：正式版（空）最大；两者非空时按 "." / "-" 分隔的标识符逐段比较
    if pa[3] == pb[3]:
        return False
    if not pa[3]:
        return True   # a 为正式版，b 为预发布 → a 新
    if not pb[3]:
        return False  # a 为预发布，b 为正式版 → a 旧

    def _pre_key(pre: str):
        return [int(seg) if seg.isdigit() else seg for seg in re.split(r"[.-]", pre)]

    return _pre_key(pa[3]) > _pre_key(pb[3])


def _is_major_minor_update(remote_version: str, local_version: str) -> bool:
    """大更新判定：仅当 major/minor 有提升时才走 Release 安装包。

    同 minor 内的 PATCH 级差异默认走热更新（v17 系列内修复不打扰用户下载安装包）；
    版本无法解析时兜底用完整版本比较。
    """
    pr = _parse_version(remote_version)
    pl = _parse_version(local_version)
    if pr is None or pl is None:
        return _version_gt(remote_version, local_version)
    return (pr[0], pr[1]) > (pl[0], pl[1])


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
                headers=pf["headers"], verify=False, timeout=15,
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
async def dependency_check():
    """依赖健康检查：版本是否满足 MIN_RELEASE_TAG + 关键模块是否缺失。

    前端启动时调用，发现异常时弹窗引导用户前往 Release 更新。
    """
    result = check_dependency()
    # 汇总后端启动时导入失败的路由模块（main.py 逐个导入容错收集，保证界面可用）
    try:
        import backend.main as _bm
        failed = getattr(_bm, "_FAILED_API_MODULES", None) or []
        if failed:
            result["missing_modules"] = list(result["missing_modules"]) + list(failed)
            result["ok"] = False
    except Exception:
        pass
    return result


@router.get("/check-update")
async def check_update():
    """检查更新：对比本地 version.json 与 GitHub v17 分支，返回云端提交历史"""
    current_sha = _read_local_sha()
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
                    headers=pf["headers"], verify=False, timeout=15,
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
                    headers=pf["headers"], verify=False, timeout=15,
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
                            headers=pf["headers"], verify=False, timeout=15,
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
            return {"ok": False, "message": "检查更新失败：更新源（GitHub/Gitee）均不可达"}

        has_update = current_sha is None or current_sha != latest_sha

        # 大更新检查：更新源 Releases/latest 版本对比（依赖库/正式版本走安装包）
        local_version = _read_local_version()
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
            "current_sha": current_sha,
            "latest_sha": latest_sha,
            "latest_message": latest_message,
            "current_commit": current_commit,
            "commits": commits,
            "full": full,
            "message": message,
        }
    except Exception as e:
        return {"ok": False, "message": f"检查更新出错：{e}"}


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


@router.post("/apply-update")
async def apply_update():
    """下载并应用云端最新版本（后台线程执行，进度通过 /utils/update-status 轮询）"""
    with _STATUS_LOCK:
        if _UPDATE_STATUS["running"]:
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
                with requests.get(zip_url, verify=False, timeout=60, stream=True) as r:
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
        _set_update_status(phase="error", percent=0, running=False, message=f"更新失败：{e}", error=str(e))


@router.post("/apply-release-update")
async def apply_release_update():
    """大更新：下载最新 GitHub Release 安装包并请求程序自动重启安装（后台执行）。"""
    with _STATUS_LOCK:
        if _UPDATE_STATUS["running"]:
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
        with requests.get(download_url, verify=False, timeout=60, stream=True) as r:
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
        _set_update_status(phase="error", percent=0, running=False, message=f"大更新失败：{e}", error=str(e))


def _get_latest_sha() -> Optional[str]:
    """获取更新源分支最新 SHA（按更新源配置依次尝试平台）。"""
    for pf in _select_platforms():
        try:
            resp = requests.get(
                _api_url(pf, f"branches/{_BRANCH}"),
                headers=pf["headers"], verify=False, timeout=15,
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


# ============================================================
# 4. 反馈打包
# ============================================================
@router.get("/feedback/options")
async def feedback_options(config_id: str = "", date: str = ""):
    """根据当前配置用户名的日志目录结构，生成反馈选择项

    进入反馈流程先强制 flush 所有日志 handler，确保实时日志写回本地硬盘，
    避免打包时遗漏尚未落盘的部分。

    返回：
      - dates: [{date, label, has_screenshot}]
      - screenshots: {date: [任务名, ...]}
      - date 不为空时额外返回 tasks: 该日期下的任务列表（无 screenshot 则为空）
    """
    # 点击反馈按键时先写回一次日志，保证后续打包内容完整
    try:
        from backend.log_setup import flush_all_handlers
        flush_all_handlers()
    except Exception:
        pass
    if not config_id:
        return {"ok": False, "message": "缺少 config_id"}
    username = _get_config_username(config_id)
    if not username:
        return {"ok": False, "message": "配置不存在，无法定位日志目录"}
    log_root = Path(get_real_path("log"))
    user_dir = log_root / username
    if not user_dir.exists():
        return {"ok": True, "username": username, "dates": [], "screenshots": {}}

    dates = []
    screenshots: dict[str, list[str]] = {}
    for date_dir in sorted(user_dir.iterdir(), key=lambda d: d.name, reverse=True):
        if not date_dir.is_dir():
            continue
        try:
            datetime.strptime(date_dir.name, "%Y-%m-%d")
        except ValueError:
            continue
        shot_dir = date_dir / "screenshot"
        task_names: list[str] = []
        if shot_dir.exists() and shot_dir.is_dir():
            task_names = sorted(
                (d.name for d in shot_dir.iterdir() if d.is_dir()),
                key=str,
            )
        screenshots[date_dir.name] = task_names
        dates.append({
            "date": date_dir.name,
            "label": date_dir.name[5:],  # MM-DD
            "has_screenshot": bool(task_names),
        })

    result: dict = {"ok": True, "username": username, "dates": dates, "screenshots": screenshots}
    if date:
        result["tasks"] = screenshots.get(date, [])
    return result


@router.post("/feedback/package")
async def feedback_package(payload: dict):
    """后台打包反馈压缩包

    body: {config_id, date, task_names: [str], save_path: str}
    打包内容：Main.log* + launcher.log* + backend.log* + log/<用户名>/<日期>/Xuan.log* + screenshot/<任务名>/*
    输出：XuanFeedBook_{用户名}_{YYYYMMDD}.zip
    """
    config_id = payload.get("config_id", "")
    date = payload.get("date", "")
    task_names = payload.get("task_names") or []
    save_path = payload.get("save_path", "")
    if not config_id or not date:
        return {"ok": False, "message": "缺少 config_id 或日期"}
    if not save_path:
        return {"ok": False, "message": "缺少保存位置"}

    with _STATUS_LOCK:
        if _FEEDBACK_STATUS["running"]:
            return {"ok": False, "message": "打包已在执行中"}
        _FEEDBACK_STATUS.update({
            "running": True, "percent": 0, "current": "",
            "message": "", "error": "", "output": None,
        })
    threading.Thread(
        target=_do_feedback_package,
        args=(config_id, date, task_names, save_path),
        daemon=True,
    ).start()
    return {"ok": True, "message": "打包任务已启动"}


def _do_feedback_package(config_id: str, date: str, task_names: list[str], save_path: str):
    try:
        # 打包前兜底写回所有日志 handler，确保实时日志落盘后一并打包
        try:
            from backend.log_setup import flush_all_handlers
            flush_all_handlers()
        except Exception:
            pass

        username = _get_config_username(config_id)
        log_root = Path(get_real_path("log"))
        user_dir = log_root / username
        date_dir = user_dir / date

        # 收集要打包的文件
        files: list[tuple[Path, str]] = []  # (绝对路径, zip内相对路径)

        # 1. Main.log*
        for fp in sorted(log_root.glob("Main.log*"), key=lambda p: p.name):
            files.append((fp, fp.name))

        # 1-1. launcher.log* / backend.log*（引导器与后端原始输出，排查启动/崩溃/访问日志）
        for log_name in ("launcher.log", "backend.log"):
            for fp in sorted(log_root.glob(f"{log_name}*"), key=lambda p: p.name):
                files.append((fp, fp.name))

        # 2. 所选日期的 Xuan.log*
        if date_dir.exists():
            for fp in sorted(date_dir.glob("Xuan.log*"), key=lambda p: p.name):
                files.append((fp, f"{username}/{date}/{fp.name}"))

        # 3. screenshot/<任务名>/*
        shot_root = date_dir / "screenshot" if date_dir.exists() else None
        if shot_root and shot_root.exists():
            for task_name in task_names:
                task_dir = shot_root / task_name
                if not task_dir.exists() or not task_dir.is_dir():
                    continue
                for fp in sorted(task_dir.rglob("*")):
                    if fp.is_file():
                        files.append((fp, f"{username}/{date}/screenshot/{task_name}/{fp.name}"))

        if not files:
            _set_feedback_status(phase="error", percent=0, running=False, message="未找到任何可打包的日志文件", error="empty")
            return

        total = len(files)
        os.makedirs(save_path, exist_ok=True)
        date_compact = date.replace("-", "")
        zip_name = f"XuanFeedBook_{username}_{date_compact}.zip"
        zip_path = os.path.join(save_path, zip_name)

        _set_feedback_status(phase="zipping", percent=0, message=f"正在压缩 {total} 个文件...")
        with zipfile.ZipFile(
            zip_path, "w", zipfile.ZIP_DEFLATED, allowZip64=True, compresslevel=9
        ) as zf:
            for i, (fp, arcname) in enumerate(files):
                try:
                    zf.write(str(fp), arcname)
                except Exception:
                    continue
                pct = int((i + 1) / total * 100)
                _set_feedback_status(phase="zipping", percent=pct, current=arcname, message=f"压缩中 {i + 1}/{total}")

        _set_feedback_status(
            phase="done", percent=100, running=False,
            message=f"反馈包已生成：{zip_path}", output=zip_path,
        )
    except Exception as e:
        _set_feedback_status(phase="error", percent=0, running=False, message=f"打包失败：{e}", error=str(e))


def _set_feedback_status(**kwargs):
    with _STATUS_LOCK:
        _FEEDBACK_STATUS.update(kwargs)


@router.get("/feedback/package-status")
async def feedback_package_status():
    """查询反馈打包任务进度"""
    with _STATUS_LOCK:
        return dict(_FEEDBACK_STATUS)


# ============================================================
# 原有设备/文件夹接口
# ============================================================
@router.get("/serial-list")
async def get_serial_list():
    """通过 adb devices 枚举当前连接的设备串口列表"""
    try:
        result = subprocess.run(
            ["adb", "devices"], capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="ignore",
        )
        output = result.stdout or ""
        serials = []
        for line in output.strip().splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 2 and parts[-1] == "device":
                serials.append(parts[0])
        return {"serials": serials}
    except Exception:
        return {"serials": []}


@router.post("/browse-folder")
def browse_folder(payload: dict):
    """弹出文件夹选择对话框（pywin32），并把选取的文件夹路径返回给前端"""
    if os.name != "nt":
        return {"ok": False, "path": None, "message": "仅支持 Windows 系统"}
    title = (payload or {}).get("title", "选择文件夹")
    try:
        path = _browse_folder(title)
        return {"ok": path is not None, "path": path}
    except Exception as e:
        return {"ok": False, "path": None, "message": str(e)}