"""调度器内部协作者（阶段 4 从 `SchedulerService` 拆分）

设计约定：每个协作者持有 `service` 回指，**每次调用时**从 service 上取运行时状态
（`config` / `device` / `operationer` / `logger`），不做构造期缓存 —— 因为生产环境这些属性
在 `start()` 时才就绪，测试里还会被整体替换成替身（如 `svc.config = SimpleNamespace(...)`）。

`SchedulerService` 侧保留同名转发方法，使 13 个私有方法/7 个公开方法的既有调用点
（API 与 14 个测试脚本）无需改动；协作者稳定后再在收尾步骤删除转发。
"""
from backend.services.scheduler.constants import IDLE_NOTIFY_THRESHOLD
from backend.services.scheduler.device_runtime import DeviceRuntime
from backend.services.scheduler.idle_notifier import IdleNotifier
from backend.services.scheduler.preset_runner import PresetRunner

__all__ = ["DeviceRuntime", "IdleNotifier", "PresetRunner", "IDLE_NOTIFY_THRESHOLD"]
