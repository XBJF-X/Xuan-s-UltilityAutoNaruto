"""统一使用「依赖库自带」的 adb 可执行文件（避免与用户本机 adb 争用 server）。

背景
----
adbutils 的 ``adb_path()`` 查找顺序是：``ADBUTILS_ADB_PATH`` 环境变量 →
PATH 中的 ``adb`` → 自带的 ``adbutils/binaries/adb.exe``。用户机器上常装有
其他工具的 adb（版本不同），两者会争用同一个 adb server（默认 5037 端口），
表现为 MiniTouch 初始化时 socket 读不到内容、设备列表抖动、初始化概率失败。

本项目要求：**所有 adb 调用统一使用依赖库里的**
``Lib/site-packages/adbutils/binaries/adb.exe``。

使用方式
--------
1. 在**导入 adbutils / minidevice 之前**调用 :func:`ensure_bundled_adb`
   （设置 ``ADBUTILS_ADB_PATH``；若 minidevice 已导入则同步其
   ``config.ADB_EXECUTOR``，因为它在导入时就把路径存成了常量）。
2. 需要直接起子进程时用 :func:`get_adb_executable` 取路径，按列表参数传入；
   需要拼 shell 字符串时用 :func:`quoted_adb_executable` 取带引号的形式。
"""
from __future__ import annotations

import importlib.resources
import logging
import os
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger("ADBEnv")

_EXE_NAME = "adb.exe" if os.name == "nt" else "adb"
_cached_path: Optional[str] = None


def _iter_candidate_dirs():
    """按优先级产出可能含 ``adbutils/binaries`` 的目录。"""
    # 1) sys.path（开发模式 .venv、打包后的 _internal/venv 都会出现在这里）
    for entry in sys.path:
        if entry:
            yield Path(entry)
    # 2) 解释器自身位置（部分打包场景 sys.path 被 ._pth 限定）
    exe_dir = Path(sys.executable).resolve().parent
    yield exe_dir
    yield exe_dir / "_internal"
    yield exe_dir / "_internal" / "venv"
    yield exe_dir / "Lib" / "site-packages"


def find_bundled_adb() -> Optional[str]:
    """查找依赖库自带的 adb 可执行文件；找不到返回 None（不抛异常）。"""
    global _cached_path
    if _cached_path and Path(_cached_path).is_file():
        return _cached_path

    # 0) 已被本程序设置为自带路径（幂等）
    env_path = os.environ.get("ADBUTILS_ADB_PATH")
    if env_path and Path(env_path).is_file():
        _cached_path = env_path
        return env_path

    # 1) 纯路径扫描（不导入 adbutils，避免触发任何 adb 行为）
    seen = set()
    for base in _iter_candidate_dirs():
        try:
            key = str(base).lower()
        except Exception:
            key = str(base)
        if key in seen:
            continue
        seen.add(key)
        candidate = base / "adbutils" / "binaries" / _EXE_NAME
        if candidate.is_file():
            _cached_path = str(candidate.resolve())
            return _cached_path

    # 2) importlib.resources（常规 pip 安装布局的兜底）
    try:
        ref = importlib.resources.files("adbutils.binaries")
        candidate = Path(str(ref)) / _EXE_NAME
        if candidate.is_file():
            _cached_path = str(candidate.resolve())
            return _cached_path
    except Exception as e:
        logger.debug("通过 importlib.resources 定位 adbutils.binaries 失败: %s", e)
    return None


def get_adb_executable() -> str:
    """返回本项目应使用的 adb 可执行文件路径。

    找不到依赖库自带的 adb 时回退到 ``"adb"``（交给 PATH），并记录 WARNING，
    以保证「依赖文件缺失」不会让整个程序无法启动。
    """
    bundled = find_bundled_adb()
    if bundled:
        return bundled
    logger.warning(
        "未找到依赖库自带的 adb（adbutils/binaries/%s），回退使用 PATH 中的 adb；"
        "若与其他 adb 版本冲突，请检查安装包依赖是否完整", _EXE_NAME)
    return "adb"


def quoted_adb_executable() -> str:
    """返回带双引号的 adb 路径（供 ``shell=True`` 的字符串命令拼接）。"""
    exe = get_adb_executable()
    return f'"{exe}"' if " " in exe else exe


def build_adb_command(*args: str) -> list[str]:
    """构造 ``[adb, *args]`` 列表命令（调用方直接交给 subprocess）。"""
    return [get_adb_executable(), *args]


def ensure_bundled_adb() -> str:
    """把 adb 路径固定为依赖库自带版本（幂等）。

    - 设置 ``ADBUTILS_ADB_PATH``，让之后导入/使用的 adbutils 直接命中；
    - 若 ``minidevice`` 已经导入，同步它导入时缓存的 ``ADB_EXECUTOR``
      （minidevice 启动设备端 minitouch 时直接使用该常量）。
    """
    path = get_adb_executable()
    if path and path != "adb":
        os.environ["ADBUTILS_ADB_PATH"] = path
    # minidevice.config.ADB_EXECUTOR 在 import 时求值，必须显式覆盖
    cfg = sys.modules.get("minidevice.config")
    if cfg is not None and hasattr(cfg, "ADB_EXECUTOR"):
        if getattr(cfg, "ADB_EXECUTOR", "") != path:
            cfg.ADB_EXECUTOR = path
            logger.info("minidevice 已切换到项目自带 adb: %s", path)
    return path


__all__ = [
    "find_bundled_adb",
    "get_adb_executable",
    "quoted_adb_executable",
    "build_adb_command",
    "ensure_bundled_adb",
]
