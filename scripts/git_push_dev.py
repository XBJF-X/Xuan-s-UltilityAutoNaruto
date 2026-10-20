#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把本地 ``dev`` 分支推送到远端 origin（VS Code 任务调用）。

铁律：开发改动只提交在 dev 分支；v17 只接受 dev 的合并，
见 ``.clinerules/08-branch-workflow.md``。远端推送动作由用户手动触发本任务，
Cline 不代为执行 ``git push``。
"""
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def run(*args):
    print(f"\n>>> git {' '.join(args)}")
    r = subprocess.run(["git", *args])
    if r.returncode != 0:
        print(f"\n[失败] git {' '.join(args)} 返回码 {r.returncode}")
        sys.exit(r.returncode)


def get_output(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True,
                       encoding="utf-8", errors="ignore")
    return (r.stdout or "").strip()


def main():
    print("=" * 60)
    print("推送 dev 到远端 origin")
    print("=" * 60)

    # 未提交/未跟踪改动：中止，避免把半成品或未跟踪文件状态带进推送流程
    dirty = get_output("status", "--porcelain")
    if dirty:
        print("\n[中止] 存在未提交/未跟踪的本地改动，请先提交到 dev 后再推送：")
        for line in dirty.splitlines()[:15]:
            print("   ", line)
        if len(dirty.splitlines()) > 15:
            print(f"    ... 共 {len(dirty.splitlines())} 条")
        sys.exit(1)

    current = get_output("rev-parse", "--abbrev-ref", "HEAD")
    if not current or current == "HEAD":
        print("\n[错误] 当前处于 detached HEAD，无法确定分支；请先切到 dev")
        sys.exit(1)

    if current != "dev":
        if current == "v17":
            print("\n[提示] 当前在 v17：v17 不允许直接开发提交，将切到 dev 再推送")
        else:
            print(f"\n[提示] 当前分支是 {current}，将切到 dev 再推送")
        run("checkout", "dev")

    run("push", "-u", "origin", "dev")

    head = get_output("rev-parse", "--short", "dev")
    print("\n" + "=" * 60)
    print(f"完成：origin/dev 已更新到 {head}")
    print("提示：版本 tag 请用「推送 Tags 到 origin」任务单独推送。")
    print("=" * 60)


if __name__ == "__main__":
    main()
