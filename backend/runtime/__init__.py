"""进程内基础设施：路径安全与（后续）事件总线、后台任务登记。

本包只依赖标准库，供 api / services / core 共同使用（不反向依赖它们）。
"""
from backend.runtime.paths import (  # noqa: F401
    is_within,
    safe_component,
    safe_join,
    safe_join_path,
)

__all__ = ["is_within", "safe_component", "safe_join", "safe_join_path"]
