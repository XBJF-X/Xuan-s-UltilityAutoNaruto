"""反馈打包端点：日期/任务选项、打包、进度查询。

阶段 3.4：由 backend/api/utils.py 拆分而来；
模块级 logger 名为 "backend.api.utils"（与拆分前一致，保证日志连续性与
既有测试的 assertLogs("backend.api.utils") 继续有效）。"""
import os
import threading
import time
import zipfile

import logging

from backend.api.utils.common import (
    _DATE_DIR_RE,
    _FEEDBACK_STATUS,
    _STATUS_LOCK,
    _get_config_username,
)
from backend.runtime.paths import is_within
from backend.runtime.paths import safe_component
from backend.utils import get_real_path
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter

logger = logging.getLogger("backend.api.utils")

router = APIRouter()


# ============================================================
# 4. 反馈打包
# ============================================================
@router.get("/feedback/options")
def feedback_options(config_id: str = "", date: str = ""):
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
        logger.warning("反馈选项请求缺少 config_id")
        return {"ok": False, "message": "缺少 config_id"}
    username = _get_config_username(config_id)
    if not username:
        logger.warning("反馈选项请求配置不存在（config_id=%s），无法定位日志目录", config_id)
        return {"ok": False, "message": "配置不存在，无法定位日志目录"}
    log_root = Path(get_real_path("log"))
    # 用户名进路径前统一清洗（防 `PUT /api/configs/{id}/rename` 写入越界名）
    username = safe_component(username, fallback="unknown")
    user_dir = log_root / username
    if not is_within(log_root, user_dir):
        logger.warning("反馈选项请求的用户名越界（config_id=%s）", config_id)
        return {"ok": False, "message": "配置用户名非法"}
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
        logger.warning("反馈打包请求缺少 config_id 或日期")
        return {"ok": False, "message": "缺少 config_id 或日期"}
    if not save_path:
        logger.warning("反馈打包请求缺少保存位置")
        return {"ok": False, "message": "缺少保存位置"}

    with _STATUS_LOCK:
        if _FEEDBACK_STATUS["running"]:
            logger.info("反馈打包请求被忽略：打包已在执行中")
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
        # 路径安全：username 可经 PUT /api/configs/{id}/rename 被写成 `..\..` 之类，
        # date/task_names/save_path 也全部来自客户端 → 旧实现直接当路径分量，
        # 可收集 log/ 之外的文件（task_name="..\.."）并把 zip 写到任意位置。
        username = safe_component(username, fallback="unknown")
        date = safe_component(date, fallback="")
        if not _DATE_DIR_RE.match(date):
            _set_feedback_status(phase="error", percent=0, running=False,
                                 message=f"日期格式非法: {date}", error="bad_date")
            return
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
            # 只接受"目录里真实存在"的任务名：客户端传 `..\..` 之类越界名时，
            # safe_component 清洗后已不可能逃出 shot_root，这里再与目录枚举求交集
            existing_tasks = {d.name for d in shot_root.iterdir() if d.is_dir()}
            for raw_name in task_names:
                task_name = safe_component(raw_name, fallback="")
                if not task_name or task_name not in existing_tasks:
                    continue
                task_dir = shot_root / task_name
                if not is_within(shot_root, task_dir):
                    continue
                for fp in sorted(task_dir.rglob("*")):
                    if fp.is_file():
                        files.append((fp, f"{username}/{date}/screenshot/{task_name}/{fp.name}"))

        # 3-1. 兜底断言：所有待打包文件必须位于 log/ 之内
        files = [(fp, arc) for fp, arc in files if is_within(log_root, fp)]

        if not files:
            _set_feedback_status(phase="error", percent=0, running=False, message="未找到任何可打包的日志文件", error="empty")
            return

        total = len(files)
        save_path = str(save_path or "").strip()
        if not save_path:
            _set_feedback_status(phase="error", percent=0, running=False,
                                 message="未选择保存位置", error="bad_save_path")
            return
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
        logger.error("反馈打包失败: %s", e, exc_info=e)
        _set_feedback_status(phase="error", percent=0, running=False, message=f"打包失败：{e}", error=str(e))


def _set_feedback_status(**kwargs):
    with _STATUS_LOCK:
        _FEEDBACK_STATUS.update(kwargs)


@router.get("/feedback/package-status")
async def feedback_package_status():
    """查询反馈打包任务进度"""
    with _STATUS_LOCK:
        return dict(_FEEDBACK_STATUS)
