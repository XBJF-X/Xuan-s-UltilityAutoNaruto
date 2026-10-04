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
import re
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

from backend.utils import get_real_path
from backend.runtime.paths import safe_component


# ===== 抑制嘈杂的第三方库日志 =====
SILENT_LOGGERS = ["comtypes", "uiautomator2", "adbutils", "urllib3", "requests"]

# ===== 日志格式 =====
DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ===== config_id 显式绑定 =====
# 旧实现只靠 `re.search(r'(Config_\d+)', logger_name)` 从 logger 名**猜** config_id：
# 副本配置的 logger 名是 `SchedulerService_Config_1_副本`（config_service.duplicate_config
# 生成的 id 形如 Config_1_副本 / Config_1_副本2），非锚定正则会把副本日志错判成 Config_1
# → 副本日志面板永远空白、源面板混入副本日志。现在由创建 logger 的一方显式打标
# （`record.config_id`），WebSocket 推送优先读取该字段，正则仅作旧路径兜底。
CONFIG_ID_ATTR = "config_id"
# 兜底正则：Config_N 及其副本后缀（仅用于未打标的记录 / 历史日志文件解析）
CONFIG_ID_PATTERN = re.compile(r"(Config_\d+(?:_副本\d*)?)")


def extract_config_id(*, explicit: str = "", logger_name: str = "") -> str:
    """取 config_id：显式绑定优先，其次从 logger 名兜底解析。"""
    if explicit:
        return str(explicit)
    match = CONFIG_ID_PATTERN.search(logger_name or "")
    return match.group(1) if match else ""


class _ConfigIdFilter(logging.Filter):
    """给经过该 logger 的记录打上 `config_id` 属性（供 WS 推送与日志归类使用）"""

    def __init__(self, config_id: str):
        super().__init__()
        self._config_id = config_id

    def filter(self, record: logging.LogRecord) -> bool:
        record.config_id = self._config_id
        return True


def bind_config_id(logger: logging.Logger, config_id: str) -> None:
    """把 config_id 显式绑定到 logger（幂等）。

    注意：只对该 logger 自身产生的记录生效；其子 logger（如 `.Device`）的记录会沿
    层级冒泡到父 logger 的 handler，不经过父 logger 的 filter —— 这类记录仍由
    `extract_config_id` 的正则兜底（logger 名包含 `Config_N`）。
    """
    if not config_id:
        return
    for existing in logger.filters:
        if isinstance(existing, _ConfigIdFilter) and existing._config_id == config_id:
            return
    logger.addFilter(_ConfigIdFilter(config_id))

# config 专属文件处理器缓存（log/<用户>/<日期>/Xuan.log -> handler）
_config_file_handler_cache: dict[str, RotatingFileHandler] = {}
# 多线程首次并发创建会得到两个 handler（同文件双写、句柄泄漏），故加锁
_CONFIG_HANDLER_LOCK = threading.Lock()


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


def flush_all_handlers():
    """
    手动 flush 所有 logger 的文件 handler，确保缓冲中的日志写回磁盘。
    在反馈打包等需要完整落盘日志的场景前调用，避免实时日志遗漏。
    """
    # 遍历 root 与所有已注册 logger
    names = ["root"] + list(logging.root.manager.loggerDict.keys())
    for name in names:
        logger = logging.getLogger(name if name != "root" else "")
        for handler in logger.handlers:
            try:
                handler.flush()
            except Exception:
                pass


def get_config_file_handler(username: str) -> RotatingFileHandler:
    """获取/创建 config 专属的文件处理器（按日期缓存，同日同文件复用同一实例）。

    路径: log/<用户名>/<日期>/Xuan.log，100MB 轮转。
    缓存可避免 SchedulerService 重复实例化时向同一 logger 重复挂接 handler。

    用户名来自配置（可经 `PUT /api/configs/{id}/rename` 改动）→ 进路径前统一清洗，
    否则 `..\\..` 之类的名字会把日志写到 log/ 之外。
    """
    log_root = Path(get_real_path("log"))
    user_dir = log_root / safe_component(username, fallback="unknown")
    date_str = datetime.now().strftime("%Y-%m-%d")
    date_dir = user_dir / date_str
    date_dir.mkdir(parents=True, exist_ok=True)

    key = str(date_dir / "Xuan.log")
    with _CONFIG_HANDLER_LOCK:
        handler = _config_file_handler_cache.get(key)
        if handler is None:
            handler = RotatingFileHandler(
                filename=key,
                maxBytes=100 * 1024 * 1024,  # 100MB
                backupCount=10,
                encoding="utf-8",
            )
            handler.setFormatter(logging.Formatter(DEFAULT_FORMAT, DATE_FORMAT))
            handler.setLevel(logging.DEBUG)
            _config_file_handler_cache[key] = handler
    return handler
