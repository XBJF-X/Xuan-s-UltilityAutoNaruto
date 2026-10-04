"""配置日志 handler 注册表（进程内）

阶段 3.4 分层修正：改前 `core/config_model.py:43` 与 `services/scheduler_service.py:181`
都直接 `from backend.api.ws import get_ws_log_handler` —— 领域层/服务层反向依赖 HTTP 层，
导致"无法脱离 FastAPI 使用与单测"。

现在：需要把日志推给前端的 handler 由**组合根**（`main.py` lifespan）注册到这里，
`core` / `services` 只向注册表索取，不认识 `api.ws`。
"""
from __future__ import annotations

import logging
import threading

_handlers: list[logging.Handler] = []
_lock = threading.Lock()


def register_handler(handler: logging.Handler) -> None:
    """注册一个"旁路"日志 handler（幂等）"""
    if handler is None:
        return
    with _lock:
        if handler not in _handlers:
            _handlers.append(handler)


def unregister_handler(handler: logging.Handler) -> None:
    with _lock:
        if handler in _handlers:
            _handlers.remove(handler)


def get_handlers() -> tuple[logging.Handler, ...]:
    """当前已注册的旁路 handler（返回快照，调用方可安全遍历）"""
    with _lock:
        return tuple(_handlers)


def clear() -> None:
    """清空注册表（测试用）"""
    with _lock:
        _handlers.clear()
