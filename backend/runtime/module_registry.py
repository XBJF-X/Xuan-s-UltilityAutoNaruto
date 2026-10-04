"""模块导入结果登记表（进程内）

阶段 3.4 分层修正：改前 `/dependency-check`（位于 `backend/api/utils.py`）为了汇总
"路由模块导入失败清单"而 `import backend.main as _bm` —— `main → api.utils → main`
构成隐式循环（靠函数内延迟 import 才没炸）。

现在：`main.py` 在容错导入失败时写入本登记表，`api` 只读登记表，不再回头 import main。
"""
from __future__ import annotations

import threading

_failed: list[str] = []
_lock = threading.Lock()


def record_failed_module(entry: str) -> None:
    with _lock:
        _failed.append(entry)


def failed_modules() -> list[str]:
    """导入失败模块清单（返回副本）"""
    with _lock:
        return list(_failed)


def clear() -> None:
    with _lock:
        _failed.clear()
