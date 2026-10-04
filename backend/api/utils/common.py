"""共享基础设施：轮询状态字典与锁、日志文件解析、更新源平台与版本工具。

阶段 3.4：由 backend/api/utils.py 拆分而来；
模块级 logger 名为 "backend.api.utils"（与拆分前一致，保证日志连续性与
既有测试的 assertLogs("backend.api.utils") 继续有效）。"""

import logging
import os
import re
import threading
from datetime import datetime

from backend.services.config_service import shared_config_service

# 版本工具的唯一实现已下沉到 core/version_info（阶段 3.4：服务层不再反向依赖 api 层）。
# 这里保留同名别名，`backend.api.utils._read_local_version` 等既有调用点与测试 patch 不变。
from backend.core.version_info import (  # noqa: F401
    MIN_RELEASE_TAG_FILE as _MIN_RELEASE_TAG_FILE,
    is_major_minor_update as _is_major_minor_update,
    parse_version as _parse_version,
    read_client_version as _read_local_version,
    read_min_release_tag as _read_min_release_tag,
    version_gt as _version_gt,
)

logger = logging.getLogger("backend.api.utils")


# ============================================================
# 模块级后台任务状态（供前端轮询）
# ============================================================
# 更新链路的状态字典/平台与 PAT 知识自阶段 3.4（后半）起由 services/update_service.py 持有：
# 这里以同名再导出（状态字典为**同一对象**），既有调用点与测试
# （`utils_api._UPDATE_STATUS`、`utils_api._UPDATE_VERIFY_TLS`、`_github_pat_configured` 等）
# 全部不受影响。
from backend.services.update_service import (  # noqa: E402,F401
    AUTO_PLATFORM_ORDER as _AUTO_PLATFORM_ORDER,
    BRANCH as _BRANCH,
    GITHUB_OWNER as _GITHUB_OWNER,
    GITHUB_REPO as _GITHUB_REPO,
    INSTALLER_ASSET_PREFIX as _INSTALLER_ASSET_PREFIX,
    PLATFORMS as _PLATFORMS,
    PLATFORM_GITHUB as _PLATFORM_GITHUB,
    PLATFORM_GITEE as _PLATFORM_GITEE,
    STATUS_LOCK as _STATUS_LOCK,
    UPDATE_STATUS as _UPDATE_STATUS,
    UPDATE_VERIFY_TLS as _UPDATE_VERIFY_TLS,
    api_url as _api_url,
    get_github_pat as _get_github_pat,
    get_releases_url as _get_releases_url,
    get_update_source as _get_update_source,
    github_pat_configured as _github_pat_configured,
    platform_headers as _platform_headers,
    select_platforms as _select_platforms,
)

# 反馈打包进度自阶段 3.4（后半）起由 services/feedback_service.py 持有：
# 这里再导出**同一个字典对象**，因此 `utils_api._FEEDBACK_STATUS.clear()/update()/.get()`
# 等既有测试写法继续作用于服务侧真实状态。
from backend.services.feedback_service import (  # noqa: F401
    FEEDBACK_STATUS as _FEEDBACK_STATUS,
)


# ============================================================
# 通用辅助
# ============================================================
def _extract_browse_pidl(result):
    """从 SHBrowseForFolder 的返回值中取出 PIDL；取消/无效时返回 None。

    pywin32 的 `SHBrowseForFolder` 返回 `(pidl, displayName, iImage)` 三元组，
    但**用户取消或直接关闭对话框时 pidl 为 None，而容器本身仍是真值元组**。
    旧实现只判断 `if folder_selected:` 就把 None 当 PIDL 传给
    `SHGetPathFromIDListW`，抛
    `TypeError: None is not a valid ITEMIDLIST in this context`
    （用户只是取消了选择，却被记成"打开文件夹选择对话框失败"）。
    这里统一收敛三种形态：None / PIDL 单值 / (pidl, ...) 序列。
    """
    if result is None:
        return None
    if isinstance(result, (tuple, list)):
        return result[0] if result else None
    return result


def _browse_folder(title: str):
    """弹出文件夹选择对话框并返回所选路径；取消或选中非文件系统项目时返回 None。"""
    import win32com.shell.shell as shell
    import win32com.shell.shellcon as shellcon
    try:
        import win32gui
        hwnd = win32gui.GetForegroundWindow() or 0
    except Exception as e:
        # 取不到前台窗口句柄不是致命问题：回退 0（桌面为 owner，等价旧行为）
        logger.debug("获取前台窗口句柄失败，文件夹对话框以桌面为 owner: %s", e)
        hwnd = 0
    # 显式传参：title 此前从未传给 API（标题一直不生效）；owner 取前台窗口，
    # 让对话框归属应用窗口并置于最前，避免"弹在应用窗口后面 → 用户以为没反应"。
    # flags 只保留 BIF_RETURNONLYFSDIRS（仅文件系统目录），不加 BIF_NEWDIALOGSTYLE，
    # 以免在 FastAPI 工作线程里额外要求 COM 以特定模式初始化。
    result = shell.SHBrowseForFolder(
        hwnd, None, title, shellcon.BIF_RETURNONLYFSDIRS)
    pidl = _extract_browse_pidl(result)
    if pidl is None:
        logger.debug("用户取消了文件夹选择")
        return None
    # 将返回的 PIDL (项目标识符列表) 转换为实际的文件系统路径。
    # 优先使用 Unicode 版本（SHGetPathFromIDListW），直接返回 str，天然支持中文路径；
    # 回退到 ANSI 版本（SHGetPathFromIDList）时返回的是系统 ANSI 代码页
    # （中文系统为 GBK/cp936）编码的 bytes，必须按 mbcs（系统 ANSI 代码页）解码，
    # 不能按 utf-8 解码——否则含中文的路径（如 MuMu/雷电安装目录）会抛 UnicodeDecodeError。
    get_path = getattr(shell, "SHGetPathFromIDListW", None) or shell.SHGetPathFromIDList
    try:
        path = get_path(pidl)
    except Exception as e:
        # pywin32 对"非文件系统项目"（如 此电脑/网络）会抛 shell.error
        logger.info("所选项目无法转换为文件系统路径，按取消处理: %s", e)
        return None
    if isinstance(path, bytes):
        path = path.decode("mbcs")
    if not path:
        logger.info("所选项目没有文件系统路径（如 此电脑/网络），按取消处理")
        return None
    return path


# 阶段 3.4（后半）：日志相关的业务逻辑已下沉到 services/log_service.py（路由只做参数映射；
# api → services 允许，反向不允许）。这里保留同名再导出，既有调用点与测试 import 路径不变。
from backend.services.log_service import (  # noqa: F401
    get_config_username as _get_config_username,
    parse_log_lines,
    read_tail as _read_tail,
)


# ============================================================
# 2. 检查更新（增强：提交历史）
# ============================================================
_GITHUB_OWNER = "XBJF-X"
_GITHUB_REPO = "Xuan-s-UltilityAutoNaruto"
_BRANCH = "v17"

# 大更新：GitHub Release 安装包资产名前缀
_INSTALLER_ASSET_PREFIX = "XuanInstaller_V"

# 本 commit 需要的最旧依赖库 ReleaseTag（根目录 MIN_RELEASE_TAG 文件，随 commit 提交）
# 依赖库（OCR 模型/DLL 等）随 Release 安装包分发、热更新不携带；本地 _version.py
# 低于该版本时，检查更新将提示用户前往 Release 下载完整安装包。
# 文件名常量的唯一实现见 core/version_info（本模块头部以别名导入 _MIN_RELEASE_TAG_FILE）。

# 关键依赖模块探测清单（find_spec 仅查是否存在、不实际加载，避免触发重型初始化）
_DEPENDENCY_PROBE_MODULES = (
    "onnxruntime",
    "minidevice",
    "adbutils",
    "uiautomator2",
    "cv2",
    "numpy",
)


_DATE_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
