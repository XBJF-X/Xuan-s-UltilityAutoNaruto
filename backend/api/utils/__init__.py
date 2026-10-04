"""工具类 API 路由（阶段 3.4 拆分后的门面）

原 `backend/api/utils.py`(1550 行) 按职责拆为：
- `common.py`   共享基础设施（状态字典/日志解析/平台与版本/依赖探测）
- `deps.py`     依赖与 OCR 加速探测
- `logs.py`     `/log-history`
- `update.py`   `/version` `/dependency-check` `/check-update` `/apply-*` `/update-status`
- `feedback.py` `/feedback/*`
- `system.py`   `/browse-folder` `/open-log-dir`

本模块保留**原有模块路径与全部名字**（`router` 聚合、其余逐一再导出），
因此 `backend.api.utils.<name>`、`mock.patch("backend.api.utils.requests.get")`、
`utils_mod.os.startfile`（测试 patch）、`assertLogs("backend.api.utils")`
等既有用法无需改动。
"""
import requests  # noqa: F401  <- 保持 mock.patch("backend.api.utils.requests.get") 可用

import importlib  # noqa: F401
import json  # noqa: F401
import logging  # noqa: F401
import os  # noqa: F401
import re  # noqa: F401
import shutil  # noqa: F401
import subprocess  # noqa: F401
import threading  # noqa: F401
import zipfile  # noqa: F401
from collections import deque  # noqa: F401
from datetime import datetime  # noqa: F401
from pathlib import Path  # noqa: F401
from typing import Optional  # noqa: F401
from backend.utils import get_real_path  # noqa: F401
from backend.services.config_service import shared_config_service  # noqa: F401
from backend.runtime.paths import is_within, safe_component  # noqa: F401
from backend.api.schemas import VersionResponse  # noqa: F401
logger = logging.getLogger("backend.api.utils")

from fastapi import APIRouter

from backend.api.utils.common import (
    _AUTO_PLATFORM_ORDER,
    _BRANCH,
    _DATE_DIR_RE,
    _DEPENDENCY_PROBE_MODULES,
    _FEEDBACK_STATUS,
    _GITHUB_OWNER,
    _GITHUB_REPO,
    _INSTALLER_ASSET_PREFIX,
    _MIN_RELEASE_TAG_FILE,
    _PLATFORMS,
    _PLATFORM_GITEE,
    _PLATFORM_GITHUB,
    _STATUS_LOCK,
    _UPDATE_STATUS,
    _UPDATE_VERIFY_TLS,
    _api_url,
    _browse_folder,
    _extract_browse_pidl,
    _get_config_username,
    _get_github_pat,
    _get_releases_url,
    _get_update_source,
    _github_pat_configured,
    _is_major_minor_update,
    _parse_version,
    _platform_headers,
    _read_local_version,
    _read_min_release_tag,
    _read_tail,
    _select_platforms,
    _version_gt,
    parse_log_lines,
)
from backend.api.utils import common  # noqa: F401

from backend.api.utils.deps import (
    _OCR_ACCEL_CACHE,
    _OCR_ACCEL_HINT,
    _OCR_ACCEL_LOCK,
    _OCR_ACCEL_MIN_TAG,
    _copy_accel_result,
    _ocr_accel_enabled,
    _probe_onnxruntime_providers,
    check_dependency,
    check_ocr_accel,
)
from backend.api.utils import deps  # noqa: F401

from backend.api.utils.system import (
    _latest_log_date_dir,
    browse_folder,
    open_log_dir,
)
from backend.api.utils import system  # noqa: F401

from backend.api.utils.logs import (
    get_log_history,
)
from backend.api.utils import logs  # noqa: F401

from backend.api.utils.update import (
    _SHA_SUFFIX_RE,
    _UPDATE_EXCLUDE_DIRS,
    _UPDATE_EXCLUDE_FILES,
    _backup_for_hot_update,
    _check_full_update,
    _do_apply_release_update,
    _do_apply_update,
    _get_latest_sha,
    _read_local_sha,
    _set_update_status,
    _verify_update_integrity,
    _write_restart_request,
    apply_release_update,
    apply_update,
    check_update,
    dependency_check,
    get_local_version,
    update_status,
)
from backend.api.utils import update  # noqa: F401

from backend.api.utils.feedback import (
    _do_feedback_package,
    _set_feedback_status,
    feedback_options,
    feedback_package,
    feedback_package_status,
)
from backend.api.utils import feedback  # noqa: F401

router = APIRouter()
router.include_router(logs.router)
router.include_router(update.router)
router.include_router(feedback.router)
router.include_router(system.router)
