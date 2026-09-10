# -*- coding: utf-8 -*-
"""桌面通知服务（当前仅支持 Windows）。

实现选择
--------
运行壳为 pywebview（Windows 走 WebView2），HTML5 ``Notification`` 需要额外处理
``PermissionRequested`` 且不保证可用；项目又未引入第三方通知库（winotify / plyer 等）。
因此直接调用系统 API：Windows PowerShell 5.1 自带 WinRT 投影，可用
``Windows.UI.Notifications.ToastNotificationManager`` 弹出原生 Toast 通知，
**零新增依赖**。

传参方式
--------
通知标题/正文含中文与任意标点，命令行传参极易被 cmd / PowerShell 的引号规则破坏；
统一改用 ``-EncodedCommand``（UTF-16LE + Base64）整体传参，脚本内部只出现
XML 转义后的单引号字面量。

降级说明
--------
PowerShell / WinRT 属外部不可控依赖（可能被组策略禁用、非 Windows 系统、非标准
系统目录等）：调用失败时返回 False 并记录 WARNING，由调用方在日志中留痕，
不抛异常打断调度循环。
"""
from __future__ import annotations

import base64
import logging
import os
import subprocess
import sys
import threading
from typing import Callable, Optional

__all__ = ["is_supported", "notify", "notify_async", "build_toast_xml"]

# 通知来源标识：使用 Windows PowerShell 自带的已注册 AUMID，无需为助手注册开始
# 菜单快捷方式即可弹出通知（Windows 10/11 实测可用）。
TOAST_AUMID = (r"{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}"
               r"\WindowsPowerShell\v1.0\powershell.exe")

# 单次 PowerShell 调用超时（秒）：正常 < 1s，这里仅作兜底
DEFAULT_TIMEOUT = 20.0
# Toast 正文最大长度（过长会被通知中心截断/破坏布局，先自行截断）
MAX_BODY_LENGTH = 200

_logger = logging.getLogger("NotifyService")

# 便于测试替换的 PowerShell 执行入口（签名与 subprocess.run 一致）
_runner: Callable[..., "subprocess.CompletedProcess"] = subprocess.run


def _powershell_path() -> Optional[str]:
    """定位 Windows PowerShell 5.1（WinRT 投影可用）；找不到返回 None。"""
    system_root = (os.environ.get("SystemRoot")
                   or os.environ.get("windir") or r"C:\Windows")
    path = os.path.join(system_root, "System32", "WindowsPowerShell",
                        "v1.0", "powershell.exe")
    return path if os.path.exists(path) else None


def is_supported() -> bool:
    """当前环境是否支持桌面通知（仅 Windows + 可用 Windows PowerShell）。"""
    if sys.platform != "win32" and os.name != "nt":
        return False
    return _powershell_path() is not None


def _xml_escape(text: str) -> str:
    """转义 XML 文本节点中的特殊字符。"""
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;")
            .replace("'", "&apos;"))


def build_toast_xml(title: str, message: str) -> str:
    """构造 ToastGeneric 模板 XML（标题 + 正文两行，长时间停留）。"""
    body = message
    if len(body) > MAX_BODY_LENGTH:
        body = body[:MAX_BODY_LENGTH - 1] + "…"
    return (
        '<toast duration="long"><visual><binding template="ToastGeneric">'
        f"<text>{_xml_escape(title)}</text>"
        f"<text>{_xml_escape(body)}</text>"
        "</binding></visual></toast>"
    )


def _build_script(title: str, message: str) -> str:
    """生成 PowerShell 脚本（XML 以单引号字面量内联，单引号需翻倍转义）。"""
    xml = build_toast_xml(title, message).replace("'", "''")
    return "\n".join([
        "$ErrorActionPreference = 'Stop'",
        "[void][Windows.UI.Notifications.ToastNotificationManager, "
        "Windows.UI.Notifications, ContentType = WindowsRuntime]",
        "[void][Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, "
        "ContentType = WindowsRuntime]",
        "$xml = New-Object Windows.Data.Xml.Dom.XmlDocument",
        f"$xml.LoadXml('{xml}')",
        "$toast = New-Object Windows.UI.Notifications.ToastNotification $xml",
        "[Windows.UI.Notifications.ToastNotificationManager]::"
        f"CreateToastNotifier('{TOAST_AUMID}').Show($toast)",
    ])


def _encode_script(script: str) -> str:
    """``-EncodedCommand`` 要求 UTF-16LE 编码后的 Base64 字符串。"""
    return base64.b64encode(script.encode("utf-16-le")).decode("ascii")


def notify(title: str, message: str, *, logger: Optional[logging.Logger] = None,
           timeout: float = DEFAULT_TIMEOUT) -> bool:
    """同步弹出一条 Windows 系统通知；成功返回 True。

    Args:
        title: 通知标题。
        message: 通知正文。
        logger: 记录日志用的 logger（缺省用模块 logger）。
        timeout: PowerShell 调用超时（秒）。
    """
    log = logger or _logger
    shell = _powershell_path()
    if shell is None or (sys.platform != "win32" and os.name != "nt"):
        log.debug(f"当前平台不支持桌面通知（仅 Windows），已跳过：{title}")
        return False
    cmd = [shell, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
           "-EncodedCommand", _encode_script(_build_script(title, message))]
    try:
        proc = _runner(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=timeout,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except Exception as e:
        log.warning(f"发送桌面通知失败（PowerShell 调用异常）: {e}")
        return False
    if proc.returncode != 0:
        detail = (proc.stderr or "").strip().replace("\n", " ")[:300]
        log.warning(
            f"发送桌面通知失败（PowerShell 退出码 {proc.returncode}）: {detail}")
        return False
    log.debug(f"桌面通知已发送：{title}")
    return True


def notify_async(title: str, message: str, *,
                 logger: Optional[logging.Logger] = None) -> threading.Thread:
    """异步发送通知（独立守护线程），避免阻塞调用方（如调度器扫描循环）。"""
    thread = threading.Thread(target=notify, args=(title, message),
                              kwargs={"logger": logger},
                              daemon=True, name="NotifyToast")
    thread.start()
    return thread
