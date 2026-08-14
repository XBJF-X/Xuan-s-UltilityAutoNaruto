"""工具类 API 路由 - 历史日志 / 检查更新 / 应用更新 / 反馈打包"""
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
        # 将返回的 PIDL (项目标识符列表) 转换为实际的文件系统路径
        path = shell.SHGetPathFromIDList(folder_selected[0])
        return path.decode("utf-8")
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


def _read_local_sha() -> Optional[str]:
    try:
        vf = Path(get_real_path("version.json"))
        if vf.exists():
            with open(vf, "r", encoding="utf-8") as f:
                return json.load(f)["commit"]["sha"]
    except Exception:
        pass
    return None


@router.get("/check-update")
async def check_update():
    """检查更新：对比本地 version.json 与 GitHub v17 分支，返回云端提交历史"""
    current_sha = _read_local_sha()
    try:
        headers = {"Accept": "application/vnd.github+json"}
        # 分支最新提交
        branch_url = f"https://api.github.com/repos/{_GITHUB_OWNER}/{_GITHUB_REPO}/branches/{_BRANCH}"
        resp = requests.get(branch_url, headers=headers, verify=False, timeout=15)
        if resp.status_code != 200:
            return {"ok": False, "message": f"GitHub API 请求失败（{resp.status_code}）"}
        branch_data = json.loads(resp.content.decode("utf-8"))
        latest_sha = branch_data["commit"]["sha"]
        latest_message = branch_data["commit"]["commit"]["message"]

        # 提交历史
        commits = []
        commits_resp = requests.get(
            f"https://api.github.com/repos/{_GITHUB_OWNER}/{_GITHUB_REPO}/commits",
            params={"sha": _BRANCH, "per_page": 20},
            headers=headers, verify=False, timeout=15,
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

        current_commit = None
        if current_sha:
            # 尝试从云端历史中找本地提交信息
            for c in commits:
                if c["sha"] == current_sha:
                    current_commit = c
                    break
            if not current_commit:
                try:
                    c_resp = requests.get(
                        f"https://api.github.com/repos/{_GITHUB_OWNER}/{_GITHUB_REPO}/commits/{current_sha}",
                        headers=headers, verify=False, timeout=15,
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

        has_update = current_sha is None or current_sha != latest_sha
        return {
            "ok": True,
            "has_update": has_update,
            "current_sha": current_sha,
            "latest_sha": latest_sha,
            "latest_message": latest_message,
            "current_commit": current_commit,
            "commits": commits,
            "message": f"检测到新版本：{latest_message}" if has_update else "当前已是最新版本",
        }
    except Exception as e:
        return {"ok": False, "message": f"检查更新出错：{e}"}


# ============================================================
# 3. 应用更新（后台线程 + 进度轮询）
# ============================================================
_UPDATE_EXCLUDE_DIRS = {
    ".git", "log", "config", "frontend_node_modules", ".venv", "__pycache__",
    "release", "test_scene", "image", ".idea", "node_modules",
    "del", ".update_tmp",
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

        # ---- 1. 下载 zipball ----
        _set_update_status(phase="downloading", percent=5, message="正在下载云端最新版本...")
        zip_url = f"https://codeload.github.com/{_GITHUB_OWNER}/{_GITHUB_REPO}/zip/refs/heads/{_BRANCH}"
        zip_path = tmp_root / "update.zip"
        with requests.get(zip_url, verify=False, timeout=60, stream=True) as r:
            r.raise_for_status()
            total = int(r.headers.get("Content-Length", 0))
            downloaded = 0
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 256):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = 5 + int(downloaded / total * 45)
                        _set_update_status(phase="downloading", percent=pct, message=f"下载中 {downloaded // 1024}KB / {total // 1024}KB")

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
        latest = _read_local_sha_from_github()
        vf = Path(get_real_path("version.json"))
        if latest:
            with open(vf, "w", encoding="utf-8") as f:
                json.dump({"commit": {"sha": latest}}, f, ensure_ascii=False, indent=2)

        # ---- 5. 清理 ----
        shutil.rmtree(tmp_root, ignore_errors=True)
        _set_update_status(
            phase="done", percent=100, running=False,
            message=f"更新完成，共更新 {copied} 个文件，请重启程序生效。",
            output=str(project_root),
        )
    except Exception as e:
        _set_update_status(phase="error", percent=0, running=False, message=f"更新失败：{e}", error=str(e))


def _read_local_sha_from_github() -> Optional[str]:
    try:
        headers = {"Accept": "application/vnd.github+json"}
        resp = requests.get(
            f"https://api.github.com/repos/{_GITHUB_OWNER}/{_GITHUB_REPO}/branches/{_BRANCH}",
            headers=headers, verify=False, timeout=15,
        )
        if resp.status_code == 200:
            return json.loads(resp.content.decode("utf-8"))["commit"]["sha"]
    except Exception:
        pass
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
    打包内容：Main.log* + log/<用户名>/<日期>/Xuan.log* + screenshot/<任务名>/*
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