# -*- coding: utf-8 -*-
"""离线回滚：用 ``update_packages/`` 里保留的归档恢复代码。

**刻意与 ``update_service`` 解耦**：本模块不 import 它，也不复用它的解压/替换/
校验函数 —— 要救的场景正是「更新链路（拉取/解压/替换）被改坏」，若回滚复用同一套
实现会一起失效。代价是排除清单与少量工具函数存在一份副本，由
``test_scene/verify_update_rollback.py`` 断言两边一致（防漂移）。

回滚全程**不访问网络**；成功后写 ``version.json`` / ``_build_info.py`` 并写重启请求，
由 launcher 完成热重启。
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import shutil
import threading
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from backend.services import update_packages as packages
from backend.utils import get_real_path

logger = logging.getLogger("RollbackService")

# 与 update_service.UPDATE_EXCLUDE_DIRS / UPDATE_EXCLUDE_FILES 保持一致：
# 这里保留**副本**，这样即使更新链路被改坏（甚至导入失败），回滚仍能独立工作。
# 一致性由 test_scene/verify_update_rollback.py 锁定。
ROLLBACK_EXCLUDE_DIRS = {
    ".git", "log", "config", "frontend_node_modules", ".venv", "__pycache__",
    "release", "test_scene", "image", ".idea", "node_modules",
    "del", ".update_tmp", ".update_backup", ".rollback_tmp", packages.PACKAGE_DIR_NAME,
}
ROLLBACK_EXCLUDE_FILES = {".clineignore"}

# 回滚临时目录（与更新用的 .update_tmp 分开，互不影响）
ROLLBACK_TMP_DIR = ".rollback_tmp"
# 与 update_service.BRANCH 一致（仅用于刷新 _build_info.py；测试锁定）
DEFAULT_BRANCH = "v17"

_SHA_SUFFIX_RE = re.compile(r"-(?P<sha>[0-9a-f]{7,40})$")

_STATUS_LOCK = threading.Lock()
_STATUS: dict = {
    "running": False,
    "mode": "rollback",
    "target_sha": "",
    "phase": "",
    "percent": 0,
    "message": "",
    "error": "",
    "output": None,
}


# ============================================================
# 状态（优先复用 update_service 的字典，前端已有轮询）
# ============================================================

def _shared_status() -> tuple[Optional[dict], Optional[object]]:
    """返回 update_service 的状态字典与写函数；该模块不可用时返回 (None, None)。"""
    try:
        from backend.services import update_service as us
        return us.UPDATE_STATUS, us.set_update_status
    except Exception as e:  # 更新链路被改坏/导入失败时，回滚仍要能跑
        logger.debug("update_service 不可用，回滚使用独立状态: %s", e)
        return None, None


def _set_status(**kwargs) -> None:
    """更新本模块状态，并尽量同步给 update_service（前端轮询 /update-status 可见）。"""
    with _STATUS_LOCK:
        _STATUS.update(kwargs)
    _shared, setter = _shared_status()
    if setter is not None:
        try:
            setter(**kwargs)
        except Exception as e:
            logger.debug("同步回滚状态到 update_service 失败: %s", e)


def status_snapshot() -> dict:
    """回滚进度快照（recovery 接口用；兼容 update_service 不可用的情况）。"""
    shared, _ = _shared_status()
    if shared is not None and shared.get("mode") == "rollback":
        return dict(shared)
    with _STATUS_LOCK:
        return dict(_STATUS)


def _is_running() -> bool:
    shared, _ = _shared_status()
    with _STATUS_LOCK:
        local = bool(_STATUS["running"])
    return local or bool(shared and shared.get("running"))


# ============================================================
# 基础工具（自带实现，不依赖更新链路）
# ============================================================

def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _extract_package(zip_path: Path, work_dir: Path) -> tuple[Path, list[tuple[Path, Path]]]:
    """解压回滚包并返回 ``(源目录, [(相对路径, 源文件)])``（只接受单一顶层目录）。"""
    extract_dir = work_dir / "extract"
    if extract_dir.exists():
        shutil.rmtree(extract_dir, ignore_errors=True)
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)
    top_dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
    if len(top_dirs) != 1:
        raise RuntimeError(f"回滚包结构异常：顶层目录数={len(top_dirs)}（应为 1）")
    src_dir = top_dirs[0]
    planned: list[tuple[Path, Path]] = []
    for src_file in sorted(p for p in src_dir.rglob("*") if p.is_file()):
        rel_path = src_file.relative_to(src_dir)
        if any(part in ROLLBACK_EXCLUDE_DIRS for part in rel_path.parts):
            continue
        if rel_path.name in ROLLBACK_EXCLUDE_FILES:
            continue
        planned.append((rel_path, src_file))
    return src_dir, planned


def _verify_package_identity(src_dir: Path, target_sha: str) -> None:
    """包内顶层目录名带 SHA 后缀时必须与目标一致（GitHub 归档 / 本地快照）。"""
    match = _SHA_SUFFIX_RE.search(src_dir.name)
    if not match:
        return  # Gitee 的 repo-v17 等不带 SHA，仅依赖文件名与 sidecar
    got = match.group("sha").lower()
    if not (got.startswith(target_sha[:7]) or target_sha.startswith(got[:7])):
        raise RuntimeError(
            f"回滚包与目标提交不一致（包内 {got[:7]}，目标 {target_sha[:7]}），已中止")


def _release_database(project_root: Path) -> None:
    """Windows 下 SQLite 连接会锁文件，覆盖 src/database.db 前先释放。"""
    try:
        from backend.tools.resource_db import ResourceDBManager
        inst = ResourceDBManager._instance
        if inst is not None and getattr(inst, "engine", None) is not None:
            inst.engine.dispose()
            logger.info("已释放 ResourceDBManager 数据库连接（回滚前）")
    except Exception as e:
        logger.warning("释放数据库连接失败（继续回滚）：%s", e)


def _replace_files(project_root: Path, planned: list[tuple[Path, Path]]) -> tuple[int, dict[str, str]]:
    """把包内文件复制回项目根，返回 ``(已复制数, {相对路径: 源文件 sha256})``。"""
    copied = 0
    failed: list[str] = []
    expected: dict[str, str] = {}
    total = len(planned)
    for index, (rel, src_file) in enumerate(planned):
        rel_posix = rel.as_posix()
        dst = project_root / rel
        # 场景资源数据库覆盖前自动备份（保护用户本地编辑）
        if rel_posix == "src/database.db" and dst.exists():
            try:
                shutil.copy2(dst, dst.with_name("database.db.bak"))
            except Exception as e:
                logger.warning("备份 database.db 失败（继续回滚）：%s", e)
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            expected[rel_posix] = _file_sha256(src_file)
            shutil.copy2(src_file, dst)
            copied += 1
        except Exception as e:
            failed.append(f"{rel_posix}（{type(e).__name__}: {e}）")
        percent = 20 + int((index + 1) / max(total, 1) * 65)
        _set_status(phase="replacing", percent=percent,
                    message=f"正在回滚文件 {index + 1}/{total}：{rel_posix}")
    if failed:
        raise RuntimeError(
            f"有 {len(failed)} 个文件回滚失败（version.json 未更新）：" + "；".join(failed[:5]))
    return copied, expected


def _verify_replaced(project_root: Path, expected: dict[str, str]) -> None:
    """逐个校验落盘文件存在且 sha256 与源一致（不通过则不得写 version.json）。"""
    missing: list[str] = []
    mismatched: list[str] = []
    for rel, want in expected.items():
        dst = project_root / rel
        if not dst.is_file():
            missing.append(rel)
            continue
        try:
            got = _file_sha256(dst)
        except Exception as e:
            mismatched.append(f"{rel}（读取失败：{e}）")
            continue
        if got != want:
            mismatched.append(f"{rel}（期望 {want[:8]}，实际 {got[:8]}）")
    if missing or mismatched:
        detail = []
        if missing:
            detail.append(f"缺失 {len(missing)} 个：" + "、".join(missing[:5]))
        if mismatched:
            detail.append(f"内容不一致 {len(mismatched)} 个：" + "、".join(mismatched[:5]))
        raise RuntimeError("回滚文件校验失败（version.json 未更新）：" + "；".join(detail))
    logger.info("回滚文件校验通过：%d 个文件内容一致", len(expected))


def _write_version_json(project_root: Path, commit_sha: str,
                        rolled_back_from: Optional[str]) -> None:
    """写 version.json（``updated_by=rollback``，runtime_info 据此信任该提交）。"""
    payload = {
        "commit": {"sha": commit_sha},
        "updated_by": "rollback",
        "rolled_back_from": rolled_back_from or "",
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    vf = project_root / "version.json"
    tmp = vf.with_name("version.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(tmp, vf)
    logger.info("version.json 已更新为回滚目标提交 %s（原 %s）",
                commit_sha[:7], (rolled_back_from or "未知")[:7])


def _refresh_build_info(project_root: Path, commit_sha: str) -> None:
    """安装版存在 ``_build_info.py`` 时刷新其 commit（否则横幅仍显示构建快照）。"""
    try:
        path = project_root / "_build_info.py"
        if not path.exists():
            return
        branch = DEFAULT_BRANCH
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            match = re.search(r'__branch__\s*=\s*["\']([^"\']*)["\']', text)
            if match and match.group(1).strip():
                branch = match.group(1).strip()
        except OSError as e:
            logger.debug("读取原 _build_info.py 的 branch 失败: %s", e)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        path.write_text(
            "# 由 build_release.py 自动生成，请勿手动修改\n"
            f'__build_time__ = "{now}"\n'
            f'__commit__ = "{commit_sha}"\n'
            f'__branch__ = "{branch}"\n',
            encoding="utf-8",
        )
        logger.info("_build_info.py 已刷新为回滚目标提交 %s", commit_sha[:7])
    except Exception as e:
        logger.warning("刷新 _build_info.py 失败（不影响回滚）：%s", e)


def _write_restart_request(project_root: Path) -> bool:
    """写 log/restart_request.json（launcher 轮询到后热重启）。"""
    try:
        log_dir = project_root / "log"
        log_dir.mkdir(parents=True, exist_ok=True)
        req = {
            "mode": "hot",
            "installer": "",
            "reason": "rollback",
            "ts": datetime.now().isoformat(timespec="seconds"),
        }
        with open(log_dir / "restart_request.json", "w", encoding="utf-8") as f:
            json.dump(req, f, ensure_ascii=False, indent=2)
        logger.info("已写入热重启请求（回滚完成）")
        return True
    except Exception as e:
        logger.warning("写入重启请求失败: %s", e)
        return False


# ============================================================
# 对外接口
# ============================================================

def list_packages() -> list[dict]:
    """本地保留的更新包（结构见 update_packages.list_packages）。"""
    return packages.list_packages()


def packages_snapshot() -> dict:
    """供 ``GET /api/utils/update-packages`` 使用。"""
    return packages.packages_snapshot()


def start_rollback(target_sha, project_root=None) -> dict:
    """校验并启动回滚后台线程（返回 ``{ok, message}``，与 apply-update 同形）。

    :param project_root: 仅测试/脚本注入用；默认取 ``get_real_path("")``。
    """
    target = packages.normalize_sha(target_sha)
    if target is None:
        return {"ok": False, "message": f"非法的提交 SHA：{str(target_sha)[:40]}"}
    pkg = packages.find_package(target, project_root)
    if pkg is None:
        return {"ok": False, "message": "本地没有该提交的更新包，无法回滚"}
    if not zipfile.is_zipfile(pkg):
        return {"ok": False, "message": "本地更新包已损坏（不是有效 zip），无法回滚"}
    current = packages.read_version_sha(project_root)
    if current and current == target:
        return {"ok": False, "message": "当前已运行该版本，无需回滚"}
    if _is_running():
        return {"ok": False, "message": "更新或回滚已在执行中"}

    _set_status(running=True, mode="rollback", target_sha=target, phase="",
                percent=0, message=f"正在准备回滚到 {target[:7]}...", error="", output=None)
    threading.Thread(target=do_rollback, args=(target, project_root), daemon=True).start()
    return {"ok": True, "message": "回滚任务已启动"}


def do_rollback(target_sha, project_root=None) -> None:
    """回滚线程体：解压本地包 → 替换 → 校验 → 写版本标识 → 请求热重启。**不联网**。

    :param project_root: 仅测试/脚本注入用；默认取 ``get_real_path("")``。
    """
    target = packages.normalize_sha(target_sha)
    root = Path(project_root) if project_root is not None else Path(get_real_path(""))
    work_dir = root / ROLLBACK_TMP_DIR
    try:
        if target is None:
            raise RuntimeError(f"非法的提交 SHA：{str(target_sha)[:40]}")
        pkg = packages.find_package(target, root)
        if pkg is None:
            raise RuntimeError("本地没有该提交的更新包，无法回滚")

        _set_status(running=True, mode="rollback", target_sha=target,
                    phase="extracting", percent=5,
                    message=f"正在解压回滚包 {target[:7]}...")
        src_dir, planned = _extract_package(pkg, work_dir)
        _verify_package_identity(src_dir, target)
        if not planned:
            raise RuntimeError("回滚包中没有可替换的文件（排除目录/文件后为空）")

        _release_database(root)
        previous_sha = packages.read_version_sha(root)

        _set_status(phase="replacing", percent=20, message="正在回滚文件...")
        copied, expected = _replace_files(root, planned)

        _set_status(phase="verifying-files", percent=90, message="正在校验回滚文件覆盖情况...")
        _verify_replaced(root, expected)

        _set_status(phase="writing-version", percent=94, message="正在更新版本记录...")
        _write_version_json(root, target, previous_sha)
        _refresh_build_info(root, target)
        try:  # 目标版本改为"当前"，避免它被当作旧包裁掉
            packages.prune_packages(root, protect_sha=target)
        except Exception as e:
            logger.warning("清理更新包失败（不影响回滚）：%s", e)

        if not _write_restart_request(root):
            _set_status(running=False, phase="done", percent=100,
                        message=f"已回滚到 {target[:7]}（{copied} 个文件），"
                                f"但写入重启请求失败，请手动重启程序。",
                        output=str(root))
            return
        _set_status(
            running=False, phase="done", percent=100,
            message=f"已回滚到 {target[:7]}（{copied} 个文件），程序即将自动重启生效。",
            output=str(root),
        )
    except Exception as e:
        logger.error("回滚失败: %s", e, exc_info=e)
        _set_status(running=False, phase="error", percent=0,
                    message=f"回滚失败：{e}", error=str(e))
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


__all__ = [
    "ROLLBACK_EXCLUDE_DIRS", "ROLLBACK_EXCLUDE_FILES", "ROLLBACK_TMP_DIR",
    "DEFAULT_BRANCH",
    "list_packages", "packages_snapshot", "status_snapshot",
    "start_rollback", "do_rollback",
]
