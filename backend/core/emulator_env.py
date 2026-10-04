"""模拟器环境知识（MuMu / 雷电）：候选路径、关键文件检查、实例探测与解析 —— **唯一实现**

阶段 3 单点化（2026-10-04）：改前同一份知识散落在 6 处，且候选清单出现**顺序不同**的
副本（改一处必漏一处）：
- ``api/validate.py``（候选常量 + 存在性校验）
- ``api/device.py::check_environment``（内联候选 + `MuMuManager info -v` / `ldconsole list2` 解析）
- ``api/scheduler.py::_precheck_screenshot_path``（复用 validate 常量 + 内联雷电检查）
- ``services/scheduler_service.py::_pre_start_environment_check``（内联候选 + 解析 + 16:9 判定）
- ``core/legacy/Screen/MuMu.py``（自有 DLL 候选，顺序与新层不同）
- ``core/legacy/Screen/LD.py``（内联 ldconsole / ldopengl64 文件名）

本模块只依赖标准库，供 api / services / core 共同使用（不反向依赖它们）。
**用户可见文案不在这里**：各调用点的提示文案保持原样（它们本就为不同界面定制），
这里只统一"事实性知识"（候选路径、探测命令、解析规则、16:9 判定）。
"""
from __future__ import annotations

import logging
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Sequence

logger = logging.getLogger("EmulatorEnv")

# ===== MuMu =====
# MuMuManager.exe 可能在安装根目录 / shell / nx_main 子目录（任一存在即可）
MUMU_MANAGER_CANDIDATES: tuple[str, ...] = (
    "MuMuManager.exe",
    "shell/MuMuManager.exe",
    "nx_main/MuMuManager.exe",
)
# external_renderer_ipc.dll 的候选相对路径（MuMu 各版本目录布局不同）
MUMU_DLL_CANDIDATES: tuple[str, ...] = (
    "shell/sdk/external_renderer_ipc.dll",
    "nx_device/12.0/shell/sdk/external_renderer_ipc.dll",
    "nx_device/15.0/shell/sdk/external_renderer_ipc.dll",
    "nx_main/sdk/external_renderer_ipc.dll",
)

# 判定"实例运行中"的 `MuMuManager info -v` 输出特征（中英文界面）
MUMU_RUNNING_MARKERS: tuple[str, ...] = ("state=Running", "状态=运行")

# ===== 雷电（LD） =====
LD_CONSOLE_NAME = "ldconsole.exe"
LD_DLL_NAME = "ldopengl64.dll"
LD_REQUIRED_FILES: tuple[str, ...] = (LD_CONSOLE_NAME, LD_DLL_NAME)

# 16:9 判定容差（像素级误差容忍）
_ASPECT_TOLERANCE = 10
_PROBE_TIMEOUT = 15


def is_16_9(width: int, height: int) -> bool:
    """分辨率是否满足 16:9（与各调用点原先的判定式逐字一致）"""
    return abs(max(width, height) * 9 - min(width, height) * 16) < _ASPECT_TOLERANCE


def find_first(base: str | os.PathLike, candidates: Sequence[str]) -> Optional[Path]:
    """返回 base 下第一个存在的候选项；都不存在返回 None。

    顺序即优先级（见模块 docstring：统一采用多数调用点的顺序）。
    """
    if not base:
        return None
    for rel in candidates:
        candidate = Path(base) / rel
        if candidate.exists():
            return candidate
    return None


def find_mumu_manager(base: str | os.PathLike) -> Optional[Path]:
    return find_first(base, MUMU_MANAGER_CANDIDATES)


def find_mumu_dll(base: str | os.PathLike) -> Optional[Path]:
    return find_first(base, MUMU_DLL_CANDIDATES)


def find_ld_console(base: str | os.PathLike) -> Optional[Path]:
    return find_first(base, (LD_CONSOLE_NAME,))


def missing_files(base: str | os.PathLike, required: Iterable[str]) -> list[str]:
    """返回 base 下缺失的相对路径清单（base 为空时返回全部 required）"""
    if not base:
        return list(required)
    return [rel for rel in required
            if not (Path(base) / rel).exists()]


def check_mumu_files(base: str | os.PathLike) -> tuple[bool, bool]:
    """MuMu 关键文件检查 → ``(dll_ok, manager_ok)``（任一候选存在即算满足）"""
    dll_ok = find_mumu_dll(base) is not None
    manager_ok = find_mumu_manager(base) is not None
    return dll_ok, manager_ok


def check_ld_files(base: str | os.PathLike) -> tuple[bool, bool]:
    """雷电关键文件检查 → ``(dll_ok, console_ok)``"""
    if not base:
        return False, False
    return ((Path(base) / LD_DLL_NAME).exists(),
            (Path(base) / LD_CONSOLE_NAME).exists())


# ===== 实例探测 =====

@dataclass
class MumuInstanceInfo:
    """`MuMuManager info -v <index>` 的解析结果"""

    running: bool = False
    resolution: Optional[tuple[int, int]] = None

    @property
    def is_16_9(self) -> Optional[bool]:
        if self.resolution is None:
            return None
        return is_16_9(*self.resolution)


@dataclass
class LdInstanceInfo:
    """`ldconsole list2` 单行（第 5 列 sysboot 表示运行/后台保活）"""

    index: int
    sysboot: str = ""
    resolution: Optional[tuple[int, int]] = None

    @property
    def running(self) -> bool:
        return self.sysboot == "1"

    @property
    def is_16_9(self) -> Optional[bool]:
        if self.resolution is None:
            return None
        return is_16_9(*self.resolution)


def parse_mumu_info(output: str) -> MumuInstanceInfo:
    """解析 `MuMuManager info -v` 输出（state / ScreenWidth / ScreenHeight）"""
    info = MumuInstanceInfo()
    text = output or ""
    info.running = any(marker in text for marker in MUMU_RUNNING_MARKERS)
    width = re.search(r"ScreenWidth=(\d+)", text)
    height = re.search(r"ScreenHeight=(\d+)", text)
    if width and height:
        info.resolution = (int(width.group(1)), int(height.group(1)))
    return info


def parse_ld_list2(output: str) -> dict[int, LdInstanceInfo]:
    """解析 `ldconsole list2` 输出 → {实例索引: LdInstanceInfo}

    行格式（逗号分隔，至少 9 列）：``索引,名称,顶层窗口句柄,绑定窗口句柄,是否运行,
    ... ,宽度,高度``。列数不足或首列非数字的行直接跳过（原实现同）。
    """
    instances: dict[int, LdInstanceInfo] = {}
    for line in (output or "").strip().splitlines():
        parts = line.split(",")
        if len(parts) < 9:
            continue
        head = parts[0].strip()
        if not head.isdigit():
            continue
        try:
            resolution = (int(parts[7]), int(parts[8]))
        except (TypeError, ValueError):
            resolution = None
        instances[int(head)] = LdInstanceInfo(
            index=int(head), sysboot=parts[4].strip(), resolution=resolution)
    return instances


def _run(cmd: Sequence[str], timeout: int = _PROBE_TIMEOUT) -> str:
    """执行探测命令并返回 stdout（失败返回空串，由调用方按"未探测到"处理）"""
    try:
        return subprocess.run(
            list(cmd), capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="ignore",
        ).stdout or ""
    except Exception as e:
        logger.debug("模拟器探测命令失败 %s: %s", cmd[:1], e)
        return ""


def probe_mumu_instance(manager: str | os.PathLike, index: int,
                        timeout: int = _PROBE_TIMEOUT) -> Optional[MumuInstanceInfo]:
    """探测 MuMu 实例（不可用/异常返回 None）"""
    if not manager:
        return None
    if not Path(manager).exists():
        return None
    output = _run([str(manager), "info", "-v", str(index)], timeout=timeout)
    if not output:
        return None
    return parse_mumu_info(output)


def probe_ld_instances(console: str | os.PathLike,
                       timeout: int = _PROBE_TIMEOUT) -> dict[int, LdInstanceInfo]:
    """探测雷电全部实例（不可用/异常返回空字典）"""
    if not console:
        return {}
    if not Path(console).exists():
        return {}
    return parse_ld_list2(_run([str(console), "list2"], timeout=timeout))
