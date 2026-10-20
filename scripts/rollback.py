# -*- coding: utf-8 -*-
"""离线回滚脚本（**纯标准库**，不 import 任何 backend 模块）。

为什么单独写一份：要救的场景是「更新链路（拉取/解压/替换）被改坏」，此时
`backend/services/update_service.py`、甚至整个后端都可能起不来。本脚本只依赖
Python 标准库 + 本地 `update_packages/<sha>.zip`，双击 `rollback.bat` 即可把代码
退回上一版，然后正常更新到修复版。

用法：
    python -X utf8 scripts/rollback.py --list          # 列出本机保留的更新包
    python -X utf8 scripts/rollback.py --last          # 回滚到最近一个非当前版本
    python -X utf8 scripts/rollback.py --to <sha>      # 回滚到指定提交
    python -X utf8 scripts/rollback.py --to <sha> --yes  # 跳过确认

完成后会写 `version.json`（updated_by=rollback）、刷新 `_build_info.py`，并写
`log/restart_request.json` 让 launcher 热重启；若程序没在运行，手动启动即可。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
PACKAGE_DIR = ROOT / "update_packages"
TMP_DIR = ROOT / ".rollback_tmp"

_SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")
_PACKAGE_RE = re.compile(r"^(?P<sha>[0-9a-fA-F]{7,40})\.zip$")
_SHA_SUFFIX_RE = re.compile(r"-(?P<sha>[0-9a-f]{7,40})$")

# 与 backend/services/rollback_service.py 保持一致（test_scene 里有一致性断言）
EXCLUDE_DIRS = {
    ".git", "log", "config", "frontend_node_modules", ".venv", "__pycache__",
    "release", "test_scene", "image", ".idea", "node_modules",
    "del", ".update_tmp", ".update_backup", ".rollback_tmp", "update_packages",
}
EXCLUDE_FILES = {".clineignore"}
DEFAULT_BRANCH = "v17"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_local_sha() -> str:
    try:
        data = json.loads((ROOT / "version.json").read_text(encoding="utf-8"))
        sha = str((data.get("commit") or {}).get("sha") or "").strip().lower()
        return sha if _SHA_RE.fullmatch(sha) else ""
    except Exception:
        return ""


def list_packages() -> list[dict]:
    """扫描本地包：[(sha, saved_at, size, path)]，按保存时间倒序。"""
    if not PACKAGE_DIR.is_dir():
        return []
    items = []
    for path in PACKAGE_DIR.glob("*.zip"):
        match = _PACKAGE_RE.match(path.name)
        if not match:
            continue
        sha = match.group("sha").lower()
        saved_at = ""
        try:
            sidecar = path.with_suffix(".json")
            if sidecar.exists():
                meta = json.loads(sidecar.read_text(encoding="utf-8", errors="ignore"))
                saved_at = str(meta.get("saved_at") or "")
            if not saved_at:
                saved_at = datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")
            size = path.stat().st_size
        except OSError as e:
            print(f"[warn] 读取 {path.name} 失败：{e}")
            continue
        items.append({"sha": sha, "saved_at": saved_at, "size": size, "path": path})
    items.sort(key=lambda item: item["saved_at"], reverse=True)
    return items


def extract_package(zip_path: Path) -> tuple[Path, list[tuple[Path, Path]]]:
    extract_dir = TMP_DIR / "extract"
    if extract_dir.exists():
        shutil.rmtree(extract_dir, ignore_errors=True)
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)
    top_dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
    if len(top_dirs) != 1:
        raise RuntimeError(f"回滚包结构异常：顶层目录数={len(top_dirs)}（应为 1）")
    src_dir = top_dirs[0]
    planned = []
    for src_file in sorted(p for p in src_dir.rglob("*") if p.is_file()):
        rel = src_file.relative_to(src_dir)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if rel.name in EXCLUDE_FILES:
            continue
        planned.append((rel, src_file))
    return src_dir, planned


def verify_identity(src_dir: Path, target: str) -> None:
    match = _SHA_SUFFIX_RE.search(src_dir.name)
    if not match:
        return
    got = match.group("sha").lower()
    if not (got.startswith(target[:7]) or target.startswith(got[:7])):
        raise RuntimeError(f"回滚包与目标提交不一致（包内 {got[:7]}，目标 {target[:7]}）")


def replace_files(planned: list[tuple[Path, Path]]) -> dict[str, str]:
    expected: dict[str, str] = {}
    for rel, src in planned:
        rel_posix = rel.as_posix()
        dst = ROOT / rel
        if rel_posix == "src/database.db" and dst.exists():
            try:
                shutil.copy2(dst, dst.with_name("database.db.bak"))
            except Exception as e:
                print(f"[warn] 备份 database.db 失败（继续）：{e}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        expected[rel_posix] = _sha256(src)
        shutil.copy2(src, dst)
    return expected


def verify_replaced(expected: dict[str, str]) -> None:
    bad = []
    for rel, want in expected.items():
        dst = ROOT / rel
        if not dst.is_file():
            bad.append(f"{rel}（缺失）")
        elif _sha256(dst) != want:
            bad.append(f"{rel}（内容不一致）")
    if bad:
        raise RuntimeError(f"回滚文件校验失败（{len(bad)} 个）：" + "；".join(bad[:5]))


def write_version_json(target: str, previous: str) -> None:
    payload = {
        "commit": {"sha": target},
        "updated_by": "rollback",
        "rolled_back_from": previous or "",
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    vf = ROOT / "version.json"
    tmp = vf.with_name("version.json.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, vf)


def refresh_build_info(target: str) -> None:
    path = ROOT / "_build_info.py"
    if not path.exists():
        return
    branch = DEFAULT_BRANCH
    try:
        match = re.search(r'__branch__\s*=\s*["\']([^"\']*)["\']',
                          path.read_text(encoding="utf-8", errors="ignore"))
        if match and match.group(1).strip():
            branch = match.group(1).strip()
    except OSError as e:
        print(f"[warn] 读取 _build_info.py 失败（沿用默认分支）：{e}")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    path.write_text(
        "# 由 build_release.py 自动生成，请勿手动修改\n"
        f'__build_time__ = "{now}"\n'
        f'__commit__ = "{target}"\n'
        f'__branch__ = "{branch}"\n',
        encoding="utf-8",
    )


def write_restart_request() -> bool:
    try:
        log_dir = ROOT / "log"
        log_dir.mkdir(parents=True, exist_ok=True)
        req = {
            "mode": "hot", "installer": "", "reason": "rollback",
            "ts": datetime.now().isoformat(timespec="seconds"),
        }
        (log_dir / "restart_request.json").write_text(
            json.dumps(req, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception as e:
        print(f"[warn] 写入重启请求失败：{e}")
        return False


def print_packages(items: list[dict], current: str) -> None:
    if not items:
        print(f"没有找到任何更新包（目录：{PACKAGE_DIR}）")
        return
    print("本机保留的更新包：")
    for index, item in enumerate(items, 1):
        mark = "  <- 当前版本" if item["sha"] == current else ""
        print(f"  {index}. {item['sha'][:7]}  {item['saved_at']}  "
              f"{item['size'] / 1024 / 1024:.1f} MB{mark}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Xuan 离线回滚（不联网）")
    parser.add_argument("--list", action="store_true", help="只列出本地更新包")
    parser.add_argument("--to", metavar="SHA", help="回滚到指定提交（7~40 位十六进制）")
    parser.add_argument("--last", action="store_true", help="回滚到最近一个非当前版本")
    parser.add_argument("--yes", action="store_true", help="跳过确认提示")
    args = parser.parse_args()

    current = read_local_sha()
    items = list_packages()
    if args.list or (not args.to and not args.last):
        print_packages(items, current)
        if not args.list:
            print("\n用法：--to <sha> / --last（详见脚本头部说明）")
        return 0

    if args.to:
        target = args.to.strip().lower()
        if not _SHA_RE.fullmatch(target):
            print(f"[error] 非法的提交 SHA：{args.to}")
            return 2
        matches = [item for item in items if item["sha"].startswith(target)]
        if not matches:
            print(f"[error] 本地没有该提交的更新包：{args.to}")
            return 1
        chosen = matches[0]
    else:
        candidates = [item for item in items if item["sha"] != current]
        if not candidates:
            print("[error] 没有可回滚的更新包（当前版本之外没有其它包）")
            return 1
        chosen = candidates[0]

    target = chosen["sha"]
    if current and target == current:
        print("[error] 当前已经是该版本，无需回滚")
        return 1
    print(f"即将回滚：{current[:7] or '未知'} -> {target[:7]}（包 {chosen['path'].name}）")
    if not args.yes:
        answer = input("确认回滚？会覆盖本地代码并请求热重启 [y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            print("已取消")
            return 1

    try:
        src_dir, planned = extract_package(chosen["path"])
        verify_identity(src_dir, target)
        if not planned:
            raise RuntimeError("回滚包中没有可替换的文件")
        print(f"正在替换 {len(planned)} 个文件...")
        expected = replace_files(planned)
        verify_replaced(expected)
        write_version_json(target, current)
        refresh_build_info(target)
        restarted = write_restart_request()
        print(f"回滚完成：{target[:7]}")
        print("程序正在运行时会自动热重启；未运行请手动启动程序。" if restarted
              else "请手动启动程序使回滚生效。")
        return 0
    except Exception as e:
        print(f"[error] 回滚失败：{e}")
        return 1
    finally:
        shutil.rmtree(TMP_DIR, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())

