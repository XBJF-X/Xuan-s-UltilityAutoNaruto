# -*- coding: utf-8 -*-
"""更新包存储：保存 / 列举 / 裁剪 ``update_packages/`` 下的热更新归档。

设计要点（与「离线回滚」配套）：

- **只做文件系统操作**（zip 读写、sha256、目录扫描），不 import ``requests``，
  也不 import ``update_service``。这样即使更新链路（下载/解压/替换）被改坏，
  包存储与回滚链路仍然可用。
- 归档不重写（不统一顶层目录名）：GitHub 归档顶层是 ``repo-<sha>``，Gitee 是
  ``repo-v17``，重命名要整份重写上百 MB 且可能损坏。实际顶层目录名记录在
  sidecar 里，回滚时只要求"唯一顶层目录"即可。
- 两类包共用一个配额：
    ``kind="download"``  更新成功后保留下来的原始下载包
    ``kind="snapshot"``  更新前对「即将被覆盖的当前文件」打的增量快照
  这样"上一版"永远有一份可回滚的归档（安装版基线也能退回）。

目录结构与元数据：

    <项目根>/update_packages/<sha>.zip    归档
    <项目根>/update_packages/<sha>.json   {sha, short_sha, kind, saved_at, source,
                                           message, top_dir, size}
"""
from __future__ import annotations

import json
import logging
import os
import re
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

logger = logging.getLogger(__name__)

PACKAGE_DIR_NAME = "update_packages"
MAX_PACKAGES = 5

_SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")
_PACKAGE_FILE_RE = re.compile(r"^(?P<sha>[0-9a-fA-F]{7,40})\.zip$")


# ============================================================
# 基础工具
# ============================================================

def normalize_sha(value) -> Optional[str]:
    """校验并规范化提交 SHA（只允许 7~40 位十六进制；该值会拼进文件名与 URL）。"""
    text = str(value or "").strip()
    if not text or not _SHA_RE.fullmatch(text):
        return None
    return text.lower()


def package_root(project_root=None) -> Path:
    """更新包目录（默认取项目根）。"""
    root = Path(project_root) if project_root is not None else _project_root()
    return root / PACKAGE_DIR_NAME


def _project_root() -> Path:
    from backend.utils import get_real_path  # 延迟导入：本模块本身仍不依赖其他服务
    return Path(get_real_path(""))


def _sidecar_path(zip_path: Path) -> Path:
    return zip_path.with_suffix(".json")


def _read_sidecar(zip_path: Path) -> dict:
    try:
        path = _sidecar_path(zip_path)
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
            if isinstance(data, dict):
                return data
    except Exception as e:
        logger.debug("读取更新包元数据失败 %s: %s", zip_path.name, e)
    return {}


def _write_sidecar(zip_path: Path, meta: dict) -> None:
    path = _sidecar_path(zip_path)
    tmp = path.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def read_version_sha(project_root=None) -> Optional[str]:
    """读取 version.json 里的本地提交 SHA（供 ``is_current`` 判定与回滚前置检查）。"""
    try:
        root = Path(project_root) if project_root is not None else _project_root()
        vf = root / "version.json"
        if not vf.exists():
            return None
        data = json.loads(vf.read_text(encoding="utf-8", errors="ignore"))
        sha = str((data.get("commit") or {}).get("sha") or "").strip()
        return sha.lower() if _SHA_RE.fullmatch(sha) else None
    except Exception as e:
        logger.debug("读取 version.json 提交失败: %s", e)
        return None


def zip_top_dirs(zip_path: Path) -> list[str]:
    """返回归档内的顶层条目（目录名）。损坏的归档会抛 ``zipfile.BadZipFile``。"""
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
    tops = sorted({n.split("/", 1)[0] for n in names if n and not n.startswith(("/", "\\"))})
    return tops



# ============================================================
# 保存
# ============================================================

def save_package(zip_path, sha, *, kind="download", source="", message="",
                 project_root=None) -> Path:
    """把归档保存到 ``update_packages/<sha>.zip``（同 sha 覆盖并刷新时间）。

    :raises ValueError: sha 非法 / 不是有效 zip / 顶层目录不唯一
    """
    norm = normalize_sha(sha)
    if norm is None:
        raise ValueError(f"非法的提交 SHA: {str(sha)[:40]}")
    src = Path(zip_path)
    if not src.is_file() or not zipfile.is_zipfile(src):
        raise ValueError(f"不是有效的 zip 归档: {src}")
    tops = zip_top_dirs(src)
    if len(tops) != 1:
        raise ValueError(f"归档结构异常：顶层目录数={len(tops)}（应为 1）")

    root = package_root(project_root)
    root.mkdir(parents=True, exist_ok=True)
    dest = root / f"{norm}.zip"
    tmp = dest.with_name(dest.name + ".tmp")
    try:
        shutil.copyfile(src, tmp)
        os.replace(tmp, dest)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)

    _write_sidecar(dest, {
        "sha": norm,
        "short_sha": norm[:7],
        "kind": kind,
        "source": source or "",
        "message": message or "",
        "top_dir": tops[0],
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "size": dest.stat().st_size,
    })
    logger.info("更新包已保存: %s（%s，%.1f MB）",
                dest.name, kind, dest.stat().st_size / 1024 / 1024)
    return dest


def snapshot_overwritten_files(project_root, sha, rel_paths: Iterable[str], *,
                               message="") -> Optional[Path]:
    """把「即将被覆盖且当前存在」的文件打成一个增量快照包（kind=snapshot）。

    只收录 ``rel_paths`` 中真实存在的文件，包内统一放在 ``repo-<sha>/`` 下，
    因此与远端归档的结构一致，回滚时走同一套解压逻辑。

    :return: 保存后的包路径；没有任何可打包文件时返回 None（不创建空包）
    """
    norm = normalize_sha(sha)
    if norm is None:
        logger.warning("更新前快照跳过：本地提交 SHA 非法: %r", str(sha)[:40])
        return None
    root = package_root(project_root)
    root.mkdir(parents=True, exist_ok=True)
    dest = root / f"{norm}.zip"
    if dest.exists():
        logger.info("更新前快照已存在，跳过: %s", dest.name)
        return dest

    tmp = dest.with_name(dest.name + ".tmp")
    count = 0
    try:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
            for rel in rel_paths:
                rel_posix = str(rel).replace("\\", "/")
                src = Path(project_root) / rel_posix
                if not src.is_file():
                    continue
                zf.write(src, arcname=f"repo-{norm}/{rel_posix}")
                count += 1
        if count == 0:
            tmp.unlink(missing_ok=True)
            logger.warning("更新前快照为空（没有任何被覆盖的现有文件），已跳过")
            return None
        os.replace(tmp, dest)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)

    _write_sidecar(dest, {
        "sha": norm,
        "short_sha": norm[:7],
        "kind": "snapshot",
        "source": "local",
        "message": message or "",
        "top_dir": f"repo-{norm}",
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "size": dest.stat().st_size,
    })
    logger.info("更新前快照已保存: %s（%d 个文件，%.1f MB）",
                dest.name, count, dest.stat().st_size / 1024 / 1024)
    return dest


# ============================================================
# 列出 / 裁剪
# ============================================================

def find_package(sha, project_root=None) -> Optional[Path]:
    """按 SHA 找本地包（不存在返回 None）。"""
    norm = normalize_sha(sha)
    if norm is None:
        return None
    path = package_root(project_root) / f"{norm}.zip"
    return path if path.is_file() else None


def list_packages(project_root=None) -> list[dict]:
    """列出本地保留的更新包（按 saved_at 倒序）。目录缺失/无包时返回空列表。"""
    root = package_root(project_root)
    if not root.is_dir():
        return []
    current = read_version_sha(project_root)
    items: list[dict] = []
    for path in root.glob("*.zip"):
        match = _PACKAGE_FILE_RE.match(path.name)
        if not match:
            continue  # 只认 <sha>.zip；其它文件（含 .tmp）一律忽略
        sha = match.group("sha").lower()
        meta = _read_sidecar(path)
        try:
            size = path.stat().st_size
            mtime = datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")
        except OSError as e:
            logger.warning("读取更新包信息失败 %s: %s", path.name, e)
            continue
        items.append({
            "sha": sha,
            "short_sha": sha[:7],
            "kind": str(meta.get("kind") or "unknown"),
            "source": str(meta.get("source") or ""),
            "message": str(meta.get("message") or ""),
            "saved_at": str(meta.get("saved_at") or mtime),
            "size": int(meta.get("size") or size),
            "is_current": bool(current and sha == current),
            "path": str(path),
        })
    items.sort(key=lambda item: (item["saved_at"], item["sha"]), reverse=True)
    return items


def prune_packages(project_root=None, *, keep: int = MAX_PACKAGES,
                   protect_sha=None) -> list[str]:
    """按保存时间删最旧的包，最多保留 ``keep`` 个；``protect_sha`` 永不删。

    :return: 被删除的 SHA 列表（便于日志/测试断言）
    """
    keep = max(int(keep), 1)
    protected = normalize_sha(protect_sha)
    items = sorted(list_packages(project_root), key=lambda item: (item["saved_at"], item["sha"]))
    removed: list[str] = []
    for item in items:  # 从最旧的开始删，直到数量不超过配额
        if len(items) - len(removed) <= keep:
            break
        if item["sha"] == protected or item["is_current"]:
            continue
        path = Path(item["path"])
        try:
            path.unlink(missing_ok=True)
            _sidecar_path(path).unlink(missing_ok=True)
            removed.append(item["sha"])
            logger.info("已清理旧更新包: %s", path.name)
        except OSError as e:
            logger.warning("删除旧更新包失败 %s: %s", path.name, e)
    return removed


def packages_snapshot(project_root=None) -> dict:
    """供接口使用：``{ok, current_sha, max_packages, total_size, packages}``。"""
    items = list_packages(project_root)
    return {
        "ok": True,
        "current_sha": read_version_sha(project_root),
        "max_packages": MAX_PACKAGES,
        "total_size": sum(int(item.get("size") or 0) for item in items),
        "packages": items,
    }
