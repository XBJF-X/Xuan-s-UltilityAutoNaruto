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
_UPDATE_STATUS: dict = {
    "running": False,
    "phase": "",          # downloading / extracting / replacing / writing-version / done / error
    "percent": 0,
    "message": "",
    "error": "",
    "output": None,       # 更新解压根目录
}

_FEEDBACK_STATUS: dict = {
    "running": False,
    "percent": 0,
    "current": "",
    "message": "",
    "error": "",
    "output": None,       # 生成的 zip 文件路径
}

_STATUS_LOCK = threading.Lock()

# 更新链路必须校验 TLS 证书：旧实现全部 `verify=False`，而热更新会下载 zip →
# 解压 → 覆盖 backend/ 与 frontend/dist → 写 restart 请求触发重启；关闭证书校验
# 意味着任何能劫持 DNS/代理/局域网的人都能让客户端执行任意代码。
# 保留常量便于企业内网/自签代理场景显式调整（改这里即可，不要散落 verify=）。
_UPDATE_VERIFY_TLS = True


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


def _get_config_username(config_id: str) -> str:
    """根据 config_id 获取配置用户名（用于定位日志目录）"""
    try:
        data = shared_config_service.get_config_full(config_id)
        return data.get("username", "") if data else ""
    except Exception:
        return ""


def _read_tail(file_path, max_lines: int = 1000) -> str:
    """高效读取文件末尾最多 max_lines 行（大文件从尾部按块读取）"""
    try:
        size = os.path.getsize(file_path)
    except OSError:
        return ""
    if size == 0:
        return ""
    block_size = 8192
    with open(file_path, "rb") as f:
        data = b""
        pos = size
        # 从尾部读取直到攒够足够行或读完整文件
        while pos > 0 and data.count(b"\n") < max_lines + 1:
            read_size = min(block_size, pos)
            pos -= read_size
            f.seek(pos)
            chunk = f.read(read_size)
            data = chunk + data
            if len(data) > max_lines * 512:  # 防超长单行无限增长
                break
    text = data.decode("utf-8", errors="ignore")
    lines = text.splitlines()
    return "\n".join(lines[-max_lines:])


def parse_log_lines(text: str, default_config_id: str = "") -> list[dict]:
    """把日志文本解析为标准日志条目列表

    日志格式: 2026-08-01 18:52:18 [INFO] SchedulerService_Config_1 | message
    兼容无 logger 前缀的行（[INFO] message）。
    """
    # config_id 兜底正则（含副本后缀）：副本配置 id 形如 Config_1_副本 / Config_1_副本2，
    # 旧的非锚定 `(Config_\d+)` 会把副本日志错判成源配置（副本面板永远空白）
    from backend.log_setup import extract_config_id

    entries = []
    for line in text.splitlines():
        line = line.rstrip()
        if not line:
            continue
        m = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+\[(\w+)\]\s+(.*)$", line)
        if not m:
            continue
        ts_str, level, rest = m.group(1), m.group(2), m.group(3)
        # rest 可能为 "logger | message" 或直接 "message"
        if " | " in rest:
            logger_name, message = rest.split(" | ", 1)
        else:
            logger_name, message = "", rest
        try:
            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").timestamp() * 1000
        except ValueError:
            continue
        cid = extract_config_id(logger_name=logger_name) or default_config_id
        entries.append({
            "level": level,
            "message": message,
            "ts": int(ts),
            "config_id": cid,
            "logger_name": logger_name,
        })
    return entries


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

# ===== 更新源平台配置（GitHub + Gitee 双源） =====
# Gitee OpenAPI（gitee.com/api/v5）的 branches/commits 响应结构与 GitHub 兼容（已实测），
# releases/latest 在未发布时返回 404（按"无 release"处理）；zipball 走 archive 直链匿名下载。
_PLATFORM_GITHUB = {
    "key": "github",
    "label": "GitHub",
    "owner": _GITHUB_OWNER,
    "repo": _GITHUB_REPO,
    "api_base": "https://api.github.com/repos",
    "headers": {"Accept": "application/vnd.github+json"},
    "zip_url": "https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}",
    "releases_url": "https://github.com/{owner}/{repo}/releases",
}
_PLATFORM_GITEE = {
    "key": "gitee",
    "label": "Gitee",
    "owner": "xuan-bu-jiu-fei",
    "repo": "Xuan-s-UltilityAutoNaruto",
    "api_base": "https://gitee.com/api/v5/repos",
    "headers": {},
    "zip_url": "https://gitee.com/{owner}/{repo}/repository/archive/{branch}.zip",
    "releases_url": "https://gitee.com/{owner}/{repo}/releases",
}
_PLATFORMS = {"github": _PLATFORM_GITHUB, "gitee": _PLATFORM_GITEE}
# auto 时按此顺序尝试（github 优先；失败自动降级 gitee 兜底）
_AUTO_PLATFORM_ORDER = ("github", "gitee")


def _get_update_source() -> str:
    """读取 [助手设置] 更新源：github / gitee / auto（默认 auto）。"""
    try:
        from backend.services.settings_service import SettingsService
        v = (SettingsService().get("助手设置", "更新源") or "").strip().lower()
        if v in _PLATFORMS:
            return v
    except Exception:
        pass
    return "auto"


def _get_github_pat() -> str:
    """读取 [助手设置] GithubPAT（默认为空 = 匿名调用）。

    GitHub 对未认证请求限流很严（匿名 60 次/小时/IP），多人共用出口 IP 时
    「检查更新」很容易被 403 限流。填 PAT 后带 ``Authorization`` 头即可把额度
    提升到 5000 次/小时。空值/读取失败一律视为未配置。

    注意：本函数的返回值**绝不允许**写入日志或接口响应。
    """
    try:
        from backend.services.settings_service import SettingsService
        return (SettingsService().get("助手设置", "GithubPAT") or "").strip()
    except Exception:
        return ""


def _platform_headers(platform: dict) -> dict:
    """构造请求头：GitHub 平台在配置了 PAT 时附加认证头。

    Gitee 走匿名（其 OpenAPI 无需 token 即可读公开仓库），只有 GitHub 需要。
    """
    headers = dict(platform.get("headers") or {})
    if platform.get("key") == "github":
        pat = _get_github_pat()
        if pat:
            headers["Authorization"] = f"Bearer {pat}"
    return headers


def _github_pat_configured() -> bool:
    """当前是否已配置 GitHub PAT（供状态展示，不泄露 token 本身）。"""
    return bool(_get_github_pat())



def _select_platforms() -> list:
    """按优先级返回更新源平台列表（auto = github 优先、gitee 兜底）。"""
    src = _get_update_source()
    if src in _PLATFORMS:
        return [_PLATFORMS[src]]
    return [_PLATFORMS[k] for k in _AUTO_PLATFORM_ORDER if k in _PLATFORMS]


def _api_url(platform: dict, path: str) -> str:
    return f"{platform['api_base']}/{platform['owner']}/{platform['repo']}/{path}"


def _get_releases_url(platform: dict = None) -> str:
    pf = platform or _select_platforms()[0]
    return pf["releases_url"].format(owner=pf["owner"], repo=pf["repo"])


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
