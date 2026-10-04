"""设置管理服务（**实现已移至 `backend/core/settings_store.py`**，此处仅再导出）

阶段 3.4 分层修正：`core/config_model.py` 需要读 setting.ini 的路径键与全局开关，
若实现放在 services 层就形成 `core → services` 反向依赖。实现搬去 core 后，本模块
保留原有 import 路径与全部名字（`SettingsService` / `get_settings` /
`reset_settings_cache`），因此 9 个测试脚本对
`backend.services.settings_service.SettingsService._get_setting` 的 patch 继续有效
（patch 的是同一个类对象）。
"""
from backend.core.settings_store import (  # noqa: F401
    SettingsService,
    get_settings,
    reset_settings_cache,
)

__all__ = ["SettingsService", "get_settings", "reset_settings_cache"]
