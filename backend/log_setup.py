"""
后端日志系统配置 - 分层日志 + 文件轮转 + WebSocket 推送

日志层级:
  1. Main.log（根）       — 程序全局日志，含启动/崩溃/退出，最大 10MB
  2. log/<用户名>/<日期>/Xuan.log — 每个 config 的日志，最大 100MB

传播规则:
  - SchedulerService_Config_* → 写入 Main.log + config 专属文件
  - 其他（WebSocket, API 等）→ 仅写入 Main.log
  - 前端 LogPanel 通过 WebSocketLogHandler 接收（已按 config_id 隔离）
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

from backend.utils import get_real_path


# ===== 抑制嘈杂的第三方库日志 =====
SILENT_LOGGERS = ["comtypes", "uiautomator2", "adbutils", "urllib3", "requests"]

# ===== 日志格式 =====
DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_backend_logging():
    """
    初始化后端日志系统（由 lifespan 启动时调用一次）。
    返回 root logger，供后续添加 WebSocket handler。
    """
    log_root = Path(get_real_path("log"))
    log_root.mkdir(exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # ---------- 1. Main.log：程序全局日志（10MB 轮转） ----------
    main_handler = RotatingFileHandler(
        filename=str(log_root / "Main.log"),
        maxBytes=10 * 1024 * 1024,   # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    main_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT, DATE_FORMAT))
    main_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(main_handler)

    # ---------- 2. 抑制第三方库的冗杂日志 ----------
    for name in SILENT_LOGGERS:
        lgr = logging.getLogger(name)
        lgr.setLevel(logging.WARNING)
        lgr.propagate = False

    return root_logger


def get_config_file_handler(username: str) -> RotatingFileHandler:
    """
    获取/创建 config 专属的文件处理器。
    路径: log/<用户名>/<日期>/Xuan.log，100MB 轮转。
    """
    log_root = Path(get_real_path("log"))
    user_dir = log_root / (username or "unknown")
    date_str = datetime.now().strftime("%Y-%m-%d")
    date_dir = user_dir / date_str
    date_dir.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        filename=str(date_dir / "Xuan.log"),
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=10,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter(DEFAULT_FORMAT, DATE_FORMAT))
    handler.setLevel(logging.DEBUG)
    return handler
