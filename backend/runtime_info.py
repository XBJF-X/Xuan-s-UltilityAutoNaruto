"""运行时信息 - 版本号 / Commit / 构建时间，供日志启动横幅与问题定位使用

数据来源（按优先级）：
  1. git rev-parse   - 开发模式下直接读取本地仓库 HEAD（实时）
  2. version.json    - 热更新成功后写入的目标提交 SHA（安装版实时的唯一来源）
  3. _build_info.py  - build_release.py 构建安装包时生成的**构建快照**（仅兜底）
  4. _version.py     - 随包分发的客户端版本号（commitizen 维护）

⚠ `_build_info.py` 只在打包那一刻生成，热更新不会重写它。此前把它放在最高
优先级，导致安装版每次启动横幅都显示同一个构建 commit（例如 `9f747da4`）。
现在改为「实时来源优先、构建快照兜底」。

典型用途：
  - log/Main.log / backend.log 的程序启动/退出横幅
  - log/<用户名>/<日期>/Xuan.log 的调度器启动横幅
"""
import json
import logging
import re
import subprocess
from datetime import datetime
from pathlib import Path

from backend.utils import get_real_path

_logger = logging.getLogger(__name__)


def get_client_version() -> str:
    """读取 _version.py 中的客户端版本号；失败返回 'unknown'。

    阶段 3.4：解析逻辑的唯一实现是 `core/version_info.read_client_version`
    （原先本函数与 `api/utils` 里的实现是两份重复代码）。
    """
    from backend.core.version_info import read_client_version
    return read_client_version() or "unknown"


def get_build_info() -> dict:
    """读取 _build_info.py（构建时生成）中的构建信息。

    返回 {"build_time": str, "commit": str, "branch": str}，缺失字段为空串。
    """
    info = {"build_time": "", "commit": "", "branch": ""}
    try:
        bf = Path(get_real_path("_build_info.py"))
        if not bf.exists():
            return info
        text = bf.read_text(encoding="utf-8", errors="ignore")

        def _extract(key: str) -> str:
            m = re.search(rf'{key}\s*=\s*["\']([^"\']*)["\']', text)
            return m.group(1).strip() if m else ""

        info["build_time"] = _extract("__build_time__")
        info["commit"] = _extract("__commit__")
        info["branch"] = _extract("__branch__")
    except Exception as e:
        _logger.debug("读取 _build_info.py 失败: %s", e)
    return info


def read_version_json_commit() -> str:
    """读取 version.json 中记录的提交 SHA（热更新成功后的实时版本）。

    只信任**热更新写入**或**比构建快照更新**的记录：
    - 带 ``updated_by: hot-update`` → 直接信任；
    - 否则若存在 ``_build_info.py``，要求 version.json 的 mtime 不早于它
      （安装目录可能残留旧版/旧分支遗留的 version.json，不能拿来当实时版本）；
    - 缺失 / 结构异常 / 内容不是 7~40 位十六进制时返回空串。
    """
    try:
        vf = Path(get_real_path("version.json"))
        if not vf.exists():
            return ""
        data = json.loads(vf.read_text(encoding="utf-8", errors="ignore"))
        sha = str((data.get("commit") or {}).get("sha") or "").strip()
        if not re.fullmatch(r"[0-9a-fA-F]{7,40}", sha):
            return ""
        if data.get("updated_by") == "hot-update":
            return sha
        bf = Path(get_real_path("_build_info.py"))
        if bf.exists():
            try:
                if vf.stat().st_mtime < bf.stat().st_mtime:
                    _logger.debug(
                        "version.json 早于 _build_info.py，判定为遗留记录，忽略: %s", sha[:7])
                    return ""
            except OSError as e:
                _logger.debug("比较 version.json/_build_info.py 时间失败: %s", e)
        return sha
    except Exception as e:
        _logger.debug("读取 version.json 提交信息失败: %s", e)
    return ""


def _git_head_commit() -> str:
    """开发模式读取 ``git rev-parse --short HEAD``；失败返回空串。"""
    try:
        root = Path(get_real_path(""))
        if (root / ".git").exists():
            r = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=str(root), capture_output=True, text=True,
                timeout=5, encoding="utf-8", errors="ignore",
            )
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip()[:12]
    except Exception as e:
        _logger.debug("git rev-parse 失败: %s", e)
    return ""


def get_runtime_commit() -> str:
    """获取本次运行**实时**的 commit。

    优先级：git HEAD（开发模式）→ version.json（热更新后的安装版）→
    _build_info.py（构建快照，仅兜底）→ 'unknown'。

    `_build_info.py` 是打包时的静态快照，热更新不会重写；把它放在最高优先级
    会让安装版横幅永远显示构建时的 commit（用户报障：每次都是 9f747da4）。
    """
    commit = _git_head_commit()
    if commit:
        return commit
    commit = read_version_json_commit()
    if commit:
        return commit[:12]
    info = get_build_info()
    if info["commit"]:
        return info["commit"]
    return "unknown"



def build_start_banner(component: str, extra_lines: list[str] | None = None) -> str:
    """生成程序/组件启动横幅（启动时间 / 客户端版本 / Commit / 构建时间）。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    info = get_build_info()
    lines = [
        f"==================== {component} 启动 ====================",
        f"启动时间: {now}",
        f"客户端版本: {get_client_version()}",
        f"Commit: {get_runtime_commit()}",
    ]
    if info.get("build_time"):
        lines.append(f"构建时间: {info['build_time']}")
    for ln in (extra_lines or []):
        lines.append(ln)
    width = max(len(l) for l in lines)
    lines.append("=" * width)
    return "\n".join(lines)


def build_exit_banner(component: str, reason: str = "") -> str:
    """生成程序/组件退出横幅（退出时间 / 退出原因）。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"==================== {component} 退出 ====================",
        f"退出时间: {now}",
    ]
    if reason:
        lines.append(f"退出原因: {reason}")
    width = max(len(l) for l in lines)
    lines.append("=" * width)
    return "\n".join(lines)
