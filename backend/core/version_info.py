"""版本信息（客户端版本 / 最低依赖库版本 / 语义化版本比较）—— 唯一实现

阶段 3.4 分层修正：这些函数原先定义在 `backend/api/utils.py`，于是
`services/scheduler_service.py`（服务层）要通过 `from backend.api.utils import ...`
反向依赖 HTTP 层。现在下沉到 core，`api` 与 `services` 都从 core 取；
`api/utils/common.py` 保留同名别名（`_read_local_version` 等）以免既有调用点与
测试 patch 失效。

同时消除重复实现：`backend/runtime_info.py::get_client_version` 原先自己再解析一遍
`_version.py`，现委托 `read_client_version()`。

⚠ 逻辑与迁移前**逐字一致**（`parse_version` 返回 4 元组或 None）——版本比较直接决定
"走热更新还是走安装包"，不允许行为漂移。
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

from backend.utils import get_real_path

logger = logging.getLogger("VersionInfo")

# 本 commit 需要的最旧依赖库 ReleaseTag 文件名（随仓库分发）
MIN_RELEASE_TAG_FILE = "MIN_RELEASE_TAG"


def read_client_version() -> str:
    """读取随包分发的 _version.py 中的版本号（如 0.17.0）；读取失败返回空串。"""
    try:
        version_file = Path(get_real_path("_version.py"))
        if version_file.exists():
            text = version_file.read_text(encoding="utf-8", errors="ignore")
            match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
            if match:
                return match.group(1).strip()
    except Exception as e:
        logger.debug("读取 _version.py 失败: %s", e)
    return ""


def read_min_release_tag() -> tuple[str, str]:
    """读取根目录 MIN_RELEASE_TAG（本 commit 需要的最旧依赖库 ReleaseTag）。

    返回 (tag, version)，如 ("v0.17.17", "0.17.17")；文件缺失或无法解析返回 ("", "")。
    该文件随 commit 提交，标识当前代码依赖的安装包资源（OCR 模型/DLL 等）的最低版本。
    """
    try:
        path = Path(get_real_path(MIN_RELEASE_TAG_FILE))
        if not path.exists():
            return "", ""
        text = path.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"[vV]?(\d+\.\d+\.\d+(?:[-.][0-9A-Za-z.-]+)?)", text)
        if not match:
            return "", ""
        version = match.group(1)
        return f"v{version}", version
    except Exception as e:
        logger.debug("读取 %s 失败: %s", MIN_RELEASE_TAG_FILE, e)
        return "", ""


def parse_version(version: str) -> Optional[tuple[int, int, int, str]]:
    """解析语义化版本号 -> (major, minor, patch, prerelease)；无法解析返回 None。"""
    if not version:
        return None
    match = re.match(r"^[vV]?(\d+)\.(\d+)\.(\d+)(?:[-.]([0-9A-Za-z.-]+))?$",
                     version.strip())
    if not match:
        return None
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)),
            match.group(4) or "")


def version_gt(left: str, right: str) -> bool:
    """判断版本 left > right（语义化版本）；任一方无法解析时退化为字符串比较。"""
    parsed_left, parsed_right = parse_version(left), parse_version(right)
    if parsed_left is None or parsed_right is None:
        return left > right
    # 主版本段
    if parsed_left[:3] != parsed_right[:3]:
        return parsed_left[:3] > parsed_right[:3]
    # 预发布段：正式版（空）最大；两者非空时按 "." / "-" 分隔的标识符逐段比较
    if parsed_left[3] == parsed_right[3]:
        return False
    if not parsed_left[3]:
        return True   # left 为正式版，right 为预发布 → left 新
    if not parsed_right[3]:
        return False  # left 为预发布，right 为正式版 → left 旧

    def _pre_key(pre: str):
        return [int(seg) if seg.isdigit() else seg for seg in re.split(r"[.-]", pre)]

    return _pre_key(parsed_left[3]) > _pre_key(parsed_right[3])


def is_major_minor_update(remote_version: str, local_version: str) -> bool:
    """大更新判定：仅当 major/minor 有提升时才走 Release 安装包。

    同 minor 内的 PATCH 级差异默认走热更新（v17 系列内修复不打扰用户下载安装包）；
    版本无法解析时兜底用完整版本比较。
    """
    parsed_remote = parse_version(remote_version)
    parsed_local = parse_version(local_version)
    if parsed_remote is None or parsed_local is None:
        return version_gt(remote_version, local_version)
    return (parsed_remote[0], parsed_remote[1]) > (parsed_local[0], parsed_local[1])


__all__ = [
    "MIN_RELEASE_TAG_FILE", "read_client_version", "read_min_release_tag",
    "parse_version", "version_gt", "is_major_minor_update",
]
