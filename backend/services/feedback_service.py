"""反馈打包服务：日志/截图收集、压缩、进度状态

阶段 3.4（后半）：把原先写在 `backend/api/utils/feedback.py` 里的业务逻辑下沉到服务层，
路由只做参数映射。

- `collect_options(config_id, date)`：`GET /feedback/options` 的逻辑（日期/任务选项）
- `start_package(...)`：`POST /feedback/package` 的逻辑（running 互斥 + 起后台线程）
- `run_package(...)`：真正的打包线程体（收集 log/ 内文件 → 压缩 → 进度）
- `FEEDBACK_STATUS` / `set_status` / `snapshot`：进度状态与读取（原 `_FEEDBACK_STATUS`、
  `_set_feedback_status`、`feedback_package_status` 的逻辑）

分层：`api → services` 允许，本模块不依赖 api；`api/utils/{common,feedback}.py` 以同名再导出
保持既有调用点与测试（`utils_api._FEEDBACK_STATUS.clear()`、
`utils_api._do_feedback_package(...)`）继续有效——状态字典是**同一个对象**。
"""
from __future__ import annotations

import logging
import os
import re
import threading
import zipfile
from datetime import datetime
from pathlib import Path

from backend.runtime.paths import is_within, safe_component
from backend.utils import get_real_path

logger = logging.getLogger("FeedbackService")

# 打包进度状态（api 层以 `_FEEDBACK_STATUS` 再导出同一对象）
FEEDBACK_STATUS: dict = {
    "running": False,
    "percent": 0,
    "current": "",
    "message": "",
    "error": "",
    "output": None,       # 生成的 zip 文件路径
}
_FEEDBACK_LOCK = threading.Lock()

# 日期目录名（YYYY-MM-DD）
_DATE_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def set_status(**kwargs) -> None:
    """更新打包进度（原 `_set_feedback_status`）"""
    with _FEEDBACK_LOCK:
        FEEDBACK_STATUS.update(kwargs)


def snapshot() -> dict:
    """读取打包进度快照（原 `/feedback/package-status` 的逻辑）"""
    with _FEEDBACK_LOCK:
        return dict(FEEDBACK_STATUS)


def _flush_logs() -> None:
    """打包/列选项前强制 flush 所有日志 handler，确保实时日志已落盘"""
    try:
        from backend.log_setup import flush_all_handlers
        flush_all_handlers()
    except Exception as e:
        # 日志模块不可用不应阻断反馈流程（外部依赖降级），仅留痕
        logger.debug("flush 日志 handler 失败（继续反馈流程）: %s", e)


def _config_username(config_id: str) -> str:
    from backend.services.log_service import get_config_username
    return get_config_username(config_id)


def collect_options(config_id: str = "", date: str = "") -> dict:
    """根据当前配置用户名的日志目录结构，生成反馈选择项

    进入反馈流程先强制 flush 所有日志 handler，确保实时日志写回本地硬盘，
    避免打包时遗漏尚未落盘的部分。

    返回：
      - dates: [{date, label, has_screenshot}]
      - screenshots: {date: [任务名, ...]}
      - date 不为空时额外返回 tasks: 该日期下的任务列表（无 screenshot 则为空）
    """
    # 点击反馈按键时先写回一次日志，保证后续打包内容完整
    _flush_logs()
    if not config_id:
        logger.warning("反馈选项请求缺少 config_id")
        return {"ok": False, "message": "缺少 config_id"}
    username = _config_username(config_id)
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


def start_package(config_id: str, date: str, task_names: list[str], save_path: str) -> dict:
    """启动后台打包（原 `POST /feedback/package` 的逻辑）

    打包内容：Main.log* + launcher.log* + backend.log* + log/<用户名>/<日期>/Xuan.log* +
    screenshot/<任务名>/*
    输出：XuanFeedBook_{用户名}_{YYYYMMDD}.zip
    """
    if not config_id or not date:
        logger.warning("反馈打包请求缺少 config_id 或日期")
        return {"ok": False, "message": "缺少 config_id 或日期"}
    if not save_path:
        logger.warning("反馈打包请求缺少保存位置")
        return {"ok": False, "message": "缺少保存位置"}

    with _FEEDBACK_LOCK:
        if FEEDBACK_STATUS["running"]:
            logger.info("反馈打包请求被忽略：打包已在执行中")
            return {"ok": False, "message": "打包已在执行中"}
        FEEDBACK_STATUS.update({
            "running": True, "percent": 0, "current": "",
            "message": "", "error": "", "output": None,
        })
    threading.Thread(
        target=run_package,
        args=(config_id, date, task_names, save_path),
        daemon=True,
    ).start()
    return {"ok": True, "message": "打包任务已启动"}


def run_package(config_id: str, date: str, task_names: list[str], save_path: str) -> None:
    """打包线程体（原 `_do_feedback_package`）"""
    try:
        # 打包前兜底写回所有日志 handler，确保实时日志落盘后一并打包
        _flush_logs()

        username = _config_username(config_id)
        log_root = Path(get_real_path("log"))
        # 路径安全：username 可经 PUT /api/configs/{id}/rename 被写成 `..\..` 之类，
        # date/task_names/save_path 也全部来自客户端 → 旧实现直接当路径分量，
        # 可收集 log/ 之外的文件（task_name="..\.."）并把 zip 写到任意位置。
        username = safe_component(username, fallback="unknown")
        date = safe_component(date, fallback="")
        if not _DATE_DIR_RE.match(date):
            set_status(phase="error", percent=0, running=False,
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
            set_status(phase="error", percent=0, running=False,
                       message="未找到任何可打包的日志文件", error="empty")
            return

        total = len(files)
        save_path = str(save_path or "").strip()
        if not save_path:
            set_status(phase="error", percent=0, running=False,
                       message="未选择保存位置", error="bad_save_path")
            return
        os.makedirs(save_path, exist_ok=True)
        date_compact = date.replace("-", "")
        zip_name = f"XuanFeedBook_{username}_{date_compact}.zip"
        zip_path = os.path.join(save_path, zip_name)

        set_status(phase="zipping", percent=0, message=f"正在压缩 {total} 个文件...")
        with zipfile.ZipFile(
            zip_path, "w", zipfile.ZIP_DEFLATED, allowZip64=True, compresslevel=9
        ) as zf:
            for i, (fp, arcname) in enumerate(files):
                try:
                    zf.write(str(fp), arcname)
                except Exception as e:
                    # 单个文件写入失败不应中断整包（可能是权限/占用），留痕后继续
                    logger.warning("打包跳过 %s: %s", fp, e)
                    continue
                pct = int((i + 1) / total * 100)
                set_status(phase="zipping", percent=pct, current=arcname,
                           message=f"压缩中 {i + 1}/{total}")

        set_status(
            phase="done", percent=100, running=False,
            message=f"反馈包已生成：{zip_path}", output=zip_path,
        )
    except Exception as e:
        logger.error("反馈打包失败: %s", e, exc_info=e)
        set_status(phase="error", percent=0, running=False, message=f"打包失败：{e}", error=str(e))


__all__ = ["FEEDBACK_STATUS", "set_status", "snapshot", "collect_options",
           "start_package", "run_package"]
