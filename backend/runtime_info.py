"""运行时信息 - 版本号 / Commit / 构建时间，供日志启动横幅与问题定位使用

数据来源（按优先级）：
  1. _build_info.py  - build_release.py 构建安装包时生成（含构建时刻的 commit/branch/时间）
  2. git rev-parse   - 开发模式下直接读取本地仓库 HEAD
  3. _version.py     - 随包分发的客户端版本号（commitizen 维护）

典型用途：
  - log/Main.log / backend.log 的程序启动/退出横幅
  - log/<用户名>/<日期>/Xuan.log 的调度器启动横幅
"""
import logging
import re
import subprocess
from datetime import datetime
from pathlib import Path

from backend.utils import get_real_path

_logger = logging.getLogger(__name__)


def get_client_version() -> str:
    """读取 _version.py 中的客户端版本号；失败返回 'unknown'。"""
    try:
        vf = Path(get_real_path("_version.py"))
        if vf.exists():
            text = vf.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
            if m:
                return m.group(1).strip()
    except Exception as e:
        _logger.debug("读取 _version.py 失败: %s", e)
    return "unknown"


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


def get_runtime_commit() -> str:
    """获取本次运行的 commit。

    优先级：
      1. _build_info.py（Release/热更新基础包构建时写入）
      2. 开发模式下 git rev-parse HEAD
      3. 兜底 'unknown'
    """
    info = get_build_info()
    if info["commit"]:
        return info["commit"]
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
