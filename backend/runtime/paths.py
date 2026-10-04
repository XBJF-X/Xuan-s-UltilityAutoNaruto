"""路径安全工具：把"用户/前端可控的字符串"安全地拼进文件路径。

背景（2026-09-17 审查）：
- `backend/main.py` 的 SPA 回退中间件把 `request.url.path`（含 `%2f` 解码后的 `..`）
  直接参与拼接 → 可读到 `frontend/dist` 之外的 `setting.ini`（内含 GithubPAT）、
  `config/*.json`、`src/database.db`；
- 反馈打包接口把客户端传入的 `date` / `task_names` 当路径分量，`save_path` 任意
  → 可收集 `log/` 之外的文件并写到任意位置；
- 用户名经 `PUT /api/configs/{id}/rename` 可控，而 `log_setup` / 反馈打包直接
  `log_root / username` 拼接。

因此所有"名字进路径"的地方统一走 `safe_component`，所有"相对路径进基准目录"的
地方统一走 `safe_join`（内部用 `resolve()` + `is_relative_to` 判定，Windows 上
对不存在的路径同样安全）。
"""
from __future__ import annotations

import re
from pathlib import Path, PurePath

# Windows 非法字符 + 控制字符 + 路径分隔符（含全角变体）
_INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f\uFF0F\uFF3C\uFF1C\uFF1E]')
# Windows 保留设备名（不区分大小写，带扩展名也保留）
_RESERVED_NAMES = {
    "con", "prn", "aux", "nul",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}
_MAX_COMPONENT_LEN = 80


def safe_component(name: object, *, fallback: str = "unknown") -> str:
    """把任意字符串收敛为**单个**安全的路径分量。

    - 去掉路径分隔符与 Windows 非法字符（替换为 `_`）
    - 去掉首尾空白与点（`.` / `..` / `...` → fallback）
    - 规避 Windows 保留设备名（`con` / `nul` / `com1` …）
    - 截断到 80 字符，避免超出路径长度限制
    """
    text = str(name or "").strip()
    text = _INVALID_CHARS.sub("_", text)
    text = text.strip(" .")
    if not text or set(text) <= {"_", "."}:
        return fallback
    if text.split(".")[0].lower() in _RESERVED_NAMES:
        text = f"_{text}"
    if len(text) > _MAX_COMPONENT_LEN:
        text = text[:_MAX_COMPONENT_LEN].strip(" .") or fallback
    return text


def is_within(base: Path | str, target: Path | str) -> bool:
    """target 解析后是否位于 base 之内（含 base 自身）"""
    base_path = Path(base).resolve()
    try:
        target_path = Path(target).resolve()
    except OSError:
        return False
    return target_path == base_path or base_path in target_path.parents


def safe_join(base: Path | str, *parts: object, fallback: str = "unknown") -> Path:
    """把若干"名字"安全拼到 base 下，并断言结果仍在 base 内。

    任一分量被清洗后仍越界（例如符号链接指向外部）时抛 ValueError，由调用方转成
    404/400 —— 绝不静默返回越界路径。
    """
    base_path = Path(base)
    cleaned = [safe_component(p, fallback=fallback) for p in parts if str(p or "")]
    result = base_path.joinpath(*cleaned) if cleaned else base_path
    if not is_within(base_path, result):
        raise ValueError(f"路径越界: {parts!r}")
    return result


def safe_join_path(base: Path | str, relative: str) -> Path | None:
    """把**相对路径**（如 HTTP path）安全拼到 base 下；越界或含 `..` 时返回 None。"""
    rel = str(relative or "").replace("\\", "/").lstrip("/")
    if not rel:
        return Path(base)
    if any(part in ("..", "") for part in PurePath(rel).parts if part != ""):
        # 允许中间的空段（`a//b`），但拒绝 `..`
        if any(part == ".." for part in PurePath(rel).parts):
            return None
    candidate = Path(base) / rel
    if not is_within(base, candidate):
        return None
    return candidate
