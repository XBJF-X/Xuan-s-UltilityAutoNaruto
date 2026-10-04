"""历史日志恢复端点（`GET /api/utils/log-history`）。

阶段 3.4：由 backend/api/utils.py 拆分而来；
模块级 logger 名为 "backend.api.utils"（与拆分前一致，保证日志连续性与
既有测试的 assertLogs("backend.api.utils") 继续有效）。"""
import logging

from backend.api.utils.common import (
    _get_config_username,
    _read_tail,
    parse_log_lines,
)
from backend.utils import get_real_path
from pathlib import Path

from fastapi import APIRouter

logger = logging.getLogger("backend.api.utils")

router = APIRouter()


# ============================================================
# 1. 历史日志恢复
# ============================================================
@router.get("/log-history")
def get_log_history(config_id: str = "", limit: int = 500):
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
