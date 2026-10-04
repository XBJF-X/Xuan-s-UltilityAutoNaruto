"""历史日志服务：日志文件尾部读取、行解析、按配置汇总

阶段 3.4（后半）：把原先写在 `backend/api/utils.py`（现 `api/utils/{common,logs}.py`）里的
**业务逻辑**下沉到服务层，路由只做参数映射：

- `read_tail` / `parse_log_lines`：日志尾部读取与行解析（原先在 api/utils/common.py）
- `get_config_username`：按 config_id 查用户名以定位日志目录（原先在 api/utils/common.py）
- `read_log_history`：`GET /api/utils/log-history` 的完整逻辑（原先写在路由函数里）

分层：`api` 依赖本模块（`api → services` 允许），本模块**不依赖 api**；
`api/utils/common.py` 以同名再导出保持既有调用点与测试的 import 路径不变。
"""
from __future__ import annotations

import logging
import os
import re
from datetime import datetime
from pathlib import Path

from backend.utils import get_real_path

logger = logging.getLogger("LogService")


def get_config_username(config_id: str) -> str:
    """根据 config_id 获取配置用户名（用于定位日志目录）"""
    try:
        from backend.services.config_service import shared_config_service
        data = shared_config_service.get_config_full(config_id)
        return data.get("username", "") if data else ""
    except Exception as e:
        logger.debug("查询配置 %s 的用户名失败: %s", config_id, e)
        return ""


def read_tail(file_path, max_lines: int = 1000) -> str:
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


def parse_log_lines(text: str, default_config_id: str = "") -> list[dict]:
    """把日志文本解析为标准日志条目列表

    日志格式: 2026-08-01 18:52:18 [INFO] SchedulerService_Config_1 | message
    兼容无 logger 前缀的行（[INFO] message）。
    """
    # config_id 兜底正则（含副本后缀）：副本配置 id 形如 Config_1_副本 / Config_1_副本2，
    # 旧的非锚定 `(Config_\d+)` 会把副本日志错判成源配置（副本面板永远空白）
    from backend.log_setup import extract_config_id

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
        cid = extract_config_id(logger_name=logger_name) or default_config_id
        entries.append({
            "level": level,
            "message": message,
            "ts": int(ts),
            "config_id": cid,
            "logger_name": logger_name,
        })
    return entries


def read_log_history(config_id: str = "", limit: int = 500) -> dict:
    """读取历史日志文件供前端刷新/重连后恢复展示

    - config_id 为空或 "__global__"：读取 Main.log*，仅返回无归属(config_id=="")的程序日志
    - config_id = Config_N：读取 log/<用户名>/<日期>/Xuan.log*(轮转) + Main.log 中该配置行
    """
    try:
        limit = max(100, min(int(limit), 5000))
    except (TypeError, ValueError):
        limit = 500
    log_root = Path(get_real_path("log"))

    if not config_id or config_id == "__global__":
        entries: list[dict] = []
        main_files = sorted(
            log_root.glob("Main.log*"),
            key=lambda p: p.name, reverse=True,
        )
        for fp in main_files[:6]:
            text = read_tail(str(fp), limit)
            entries.extend(parse_log_lines(text, default_config_id=""))
        # 只保留无归属（程序本身）的日志
        entries = [e for e in entries if not e["config_id"]]
        entries.sort(key=lambda e: e["ts"])
        return {"ok": True, "config_id": "__global__", "entries": entries[-limit:]}

    # 指定配置：优先读取配置日志目录（今天的 + 轮转），再补 Main.log 中该配置行
    username = get_config_username(config_id)
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
            text = read_tail(str(fp), limit * 2)
            for e in parse_log_lines(text, default_config_id=""):
                if e["config_id"] == config_id:
                    candidate_files.append(fp)  # 仅用于占位计数
        entries = []
        for fp in candidate_files[:6]:
            text = read_tail(str(fp), limit)
            entries.extend(parse_log_lines(text, default_config_id=config_id))
        entries = [e for e in entries if e["config_id"] == config_id]
        entries.sort(key=lambda e: e["ts"])
        return {"ok": True, "config_id": config_id, "entries": entries[-limit:]}

    entries = []
    seen = set()
    for fp in candidate_files[:10]:
        text = read_tail(str(fp), limit)
        for e in parse_log_lines(text, default_config_id=config_id):
            key = (e["ts"], e["message"])
            if key in seen:
                continue
            seen.add(key)
            entries.append(e)
    # main.log 中该配置的行（可能日期目录被清理）
    for fp in sorted(log_root.glob("Main.log*"), key=lambda p: p.name, reverse=True)[:6]:
        text = read_tail(str(fp), limit)
        for e in parse_log_lines(text, default_config_id=""):
            if e["config_id"] == config_id and (e["ts"], e["message"]) not in seen:
                seen.add((e["ts"], e["message"]))
                entries.append(e)
    entries.sort(key=lambda e: e["ts"])
    return {"ok": True, "config_id": config_id, "entries": entries[-limit:]}


__all__ = ["get_config_username", "read_tail", "parse_log_lines", "read_log_history"]
