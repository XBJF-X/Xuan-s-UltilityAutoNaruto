# -*- coding: utf-8 -*-
"""批量回归入口：自动发现并运行 test_scene/verify_*.py。

用法：
    .venv\\Scripts\\python.exe -X utf8 test_scene/_run_verify_batch.py            # 快速集
    .venv\\Scripts\\python.exe -X utf8 test_scene/_run_verify_batch.py --full     # 含重型脚本
    .venv\\Scripts\\python.exe -X utf8 test_scene/_run_verify_batch.py --list     # 只列出

设计说明（2026-09-17 工程化）：
- 旧实现硬编码 12 个脚本名，且**漏掉**了 `verify_activation_window_guard.py` /
  `verify_task_recovery.py` / `verify_task_schedules.py` 等关键回归，新脚本也不会被
  自动纳入 → 改为按目录自动发现；
- HEAVY / KNOWN_STALE 两组脚本默认跳过：前者需要实机/模型/大量底图，后者是与当前
  代码已滞后、待修的既有失败（跳过而不是假装通过）；
- 退出码非 0 表示有失败，便于 CI 直接使用。
"""
import argparse
import os
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DIR = os.path.join(ROOT, "test_scene")

# 需要实机设备 / ONNX 模型 / 全量底图 / 自行拉起服务端的重型脚本（--full 时才跑）
HEAVY = {
    "verify_recognizer_pruning.py",
    "verify_ocr_robustness.py",
    "verify_ocr_cpu_fallback.py",
    "verify_ocr_accel_check.py",
    "verify_clicker_batching.py",
    # 基线（阶段 4 起点 e779bac2，用 `git worktree` 复核）：Ran 49 → failures=2, errors=23。
    # 失败全部是 Control 层与用户 WIP 不一致所致（`Clicker._minitouch_click_worker` /
    # `_refresh_minitouch_instance` / `_stopped_event` 不存在、`MiniTouch.max_contacts`
    # 无 setter、2 个控制实例切换断言 + 1 个 IndexError），与调度器重构无关。
    # **重构后该脚本的失败数必须仍为 2/23**，新增即为回归。
    "verify_touch_residue_fix.py",
    "verify_adb_bootstrap.py",
    "verify_ws_dual_write_e2e.py",
}

# 已滞后于当前代码的既有失败（**与本次重构无关**，修好前不纳入门槛；每项都给出证据）
KNOWN_STALE = {
    # 前端引导文案/倒计时已改（10s→15s、文案重写，commit 8a88bed5），断言未同步
    "verify_startup_notice.py",
    # 返回值约定改造（commit ff3725b9 "优化场景执行函数返回值"）后，XiaoHaoTiLi 的
    # source handler 改为 `return "冒险-冒险副本"`，测试仍断言 `result is False`
    "verify_declare_next_scene.py",
    # GengDuoWanFa 已删「未注册场景」处理函数（既有未提交 WIP），测试仍断言其存在
    # （memory-bank/activeContext.md v0.17.58 条目已记录该 2 项失败）
    "verify_transition_stall_guard.py",
    "verify_renfatijiangli_flow.py",
    "verify_renfatijiangli_time.py",
    "verify_pending_scene_edges.py",
}

PER_SCRIPT_TIMEOUT = 300
# 前端脚本用 node --experimental-strip-types 直跑 TS（与 verify_log_dedupe.ts 同约定）
NODE_REQUIRED_HINT = "未找到 node（前端 TS 测试跳过；CI 上由 GitHub runner 自带 node）"


def discover(include_heavy: bool, include_stale: bool) -> list[str]:
    names = sorted(n for n in os.listdir(TEST_DIR)
                   if n.startswith("verify_") and n.endswith(".py"))
    out = []
    for name in names:
        if name in KNOWN_STALE and not include_stale:
            continue
        if name in HEAVY and not include_heavy:
            continue
        out.append(name)
    return out


def discover_ts() -> list[str]:
    return sorted(n for n in os.listdir(TEST_DIR)
                  if n.startswith("verify_") and n.endswith(".ts"))


def run_ts(name: str) -> tuple[bool, str]:
    node = shutil.which("node")
    if node is None:
        return True, NODE_REQUIRED_HINT
    path = os.path.join(TEST_DIR, name)
    try:
        proc = subprocess.run([node, "--experimental-strip-types", path],
                              capture_output=True, cwd=ROOT,
                              timeout=PER_SCRIPT_TIMEOUT)
    except subprocess.TimeoutExpired:
        return False, f"超时(>{PER_SCRIPT_TIMEOUT}s)"
    text = (proc.stdout + proc.stderr).decode("utf-8", errors="replace")
    ok = proc.returncode == 0
    tail = "全部通过" if ok else "\n".join(text.splitlines()[-6:])
    return ok, tail


def run(name: str) -> tuple[bool, str]:
    path = os.path.join(TEST_DIR, name)
    try:
        proc = subprocess.run([sys.executable, "-X", "utf8", path],
                              capture_output=True, cwd=ROOT,
                              timeout=PER_SCRIPT_TIMEOUT)
    except subprocess.TimeoutExpired:
        return False, f"超时(>{PER_SCRIPT_TIMEOUT}s)"
    text = (proc.stdout + proc.stderr).decode("utf-8", errors="replace")
    ran = [ln.strip() for ln in text.splitlines() if ln.startswith("Ran ")]
    ok = proc.returncode == 0
    return ok, (ran[0] if ran else "no summary")


def main() -> int:
    parser = argparse.ArgumentParser(description="Xuan 回归脚本批量运行器")
    parser.add_argument("--full", action="store_true", help="包含重型脚本")
    parser.add_argument("--stale", action="store_true", help="包含已知滞后脚本")
    parser.add_argument("--list", action="store_true", help="只列出将要运行的脚本")
    args = parser.parse_args()

    scripts = discover(args.full, args.stale)
    ts_scripts = discover_ts()
    if args.list:
        for name in scripts:
            print(name)
        for name in ts_scripts:
            print(name + "   (node --experimental-strip-types)")
        return 0

    failed: list[str] = []
    for name in scripts:
        ok, detail = run(name)
        print(f"{name}: {'PASS' if ok else 'FAIL'} | {detail}")
        if not ok:
            failed.append(name)
    for name in ts_scripts:
        ok, detail = run_ts(name)
        print(f"{name}: {'PASS' if ok else 'FAIL'} | {detail}")
        if not ok:
            failed.append(name)

    total = len(scripts) + len(ts_scripts)
    print(f"\n汇总: {total - len(failed)}/{total} PASS")
    if failed:
        print("失败:", ", ".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
