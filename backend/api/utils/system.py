"""系统辅助端点：文件夹选择对话框、打开本地日志目录。

阶段 3.4：由 backend/api/utils.py 拆分而来；
模块级 logger 名为 "backend.api.utils"（与拆分前一致，保证日志连续性与
既有测试的 assertLogs("backend.api.utils") 继续有效）。"""
import os

import logging

from backend.api.utils.common import (
    _DATE_DIR_RE,
    _browse_folder,
    _get_config_username,
)
from backend.utils import get_real_path
from pathlib import Path
from typing import Optional

from fastapi import APIRouter

logger = logging.getLogger("backend.api.utils")

router = APIRouter()


# ============================================================
# 原有设备/文件夹接口
# ============================================================
# 说明：原 `GET /api/utils/serial-list` 已删除 —— 与 `GET /api/device/{config_id}/serial-list`
# 重复实现（后者走 adbutils 且前端实际只用它），且调用方会 `subprocess adb devices`
# 手工解析输出。串口枚举统一由 api/device.py 提供。
@router.post("/browse-folder")
def browse_folder(payload: dict):
    """弹出文件夹选择对话框（pywin32），并把选取的文件夹路径返回给前端"""
    if os.name != "nt":
        logger.warning("浏览文件夹请求被拒绝：仅支持 Windows 系统")
        return {"ok": False, "path": None, "message": "仅支持 Windows 系统"}
    title = (payload or {}).get("title", "选择文件夹")
    try:
        path = _browse_folder(title)
        if path is None:
            # 取消不是错误：不再记 ERROR（旧实现把取消当异常，
            # 用户日志里出现"打开文件夹选择对话框失败"却无从下手）。
            return {"ok": False, "cancelled": True, "path": None, "message": "已取消选择"}
        return {"ok": True, "cancelled": False, "path": path}
    except Exception as e:
        logger.error("打开文件夹选择对话框失败: %s", e, exc_info=e)
        return {"ok": False, "cancelled": False, "path": None, "message": str(e)}


def _latest_log_date_dir(user_dir: Path) -> Optional[Path]:
    """在 log/<用户名>/ 下定位最近一个含日志文件的日期目录（YYYY-MM-DD）"""
    try:
        date_dirs = sorted(
            (d for d in user_dir.iterdir()
             if d.is_dir() and _DATE_DIR_RE.match(d.name)),
            key=lambda d: d.name, reverse=True,
        )
        for date_dir in date_dirs:
            if any(date_dir.glob("*.log*")):
                return date_dir
    except Exception:
        pass
    return None


@router.get("/open-log-dir")
def open_log_dir(config_id: str = ""):
    """在系统文件管理器中打开本地日志目录（Windows os.startfile）

    - config_id 为空或 __global__：打开 log/ 根目录
    - config_id = Config_N：打开 log/<用户名>/ 下最近含日志的日期目录（YYYY-MM-DD）；
      无日期目录时退回 log/<用户名>/（不存在则创建），取不到用户名则退回 log/
    """
    if os.name != "nt":
        logger.warning("打开日志目录请求被拒绝：仅支持 Windows 系统")
        return {"ok": False, "message": "仅支持 Windows 系统"}
    try:
        log_root = Path(get_real_path("log"))
        log_root.mkdir(parents=True, exist_ok=True)
        target = log_root
        if config_id and config_id != "__global__":
            username = _get_config_username(config_id)
            if username:
                user_dir = log_root / username
                user_dir.mkdir(parents=True, exist_ok=True)
                target = _latest_log_date_dir(user_dir) or user_dir
        os.startfile(str(target))
        return {"ok": True, "path": str(target)}
    except Exception as e:
        logger.error("打开本地日志目录失败: %s", e, exc_info=e)
        return {"ok": False, "message": str(e)}
