#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把 dev 合并进 v17（本地快进 + 推送远端），并保留 dev 分支。

步骤（任一步失败即中止，并尽量把工作区切回原分支）：
1. 工作区必须干净（未提交/未跟踪改动会中止）
2. 拉取 origin/dev，要求本地 dev 与 origin/dev 一致（先执行「推送 dev 到 origin」任务）
3. 切到 v17，先快进到 origin/v17，再 ``git merge --ff-only dev``
4. 推送 v17 到 origin（远端完成同样的合并）
5. 切回原分支；dev 保留，不删除

铁律：v17 永不做功能开发提交，见 ``.clinerules/08-branch-workflow.md``。
"""
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class GitError(RuntimeError):
    pass


def run(*args):
    print(f"\n>>> git {' '.join(args)}")
    r = subprocess.run(["git", *args])
    if r.returncode != 0:
        raise GitError(f"git {' '.join(args)} 返回码 {r.returncode}")


def get_output(*args):
    """返回 (stdout.strip(), returncode)。"""
    r = subprocess.run(["git", *args], capture_output=True, text=True,
                       encoding="utf-8", errors="ignore")
    return (r.stdout or "").strip(), r.returncode


def main():
    print("=" * 60)
    print("dev 合并进 v17（本地 + 远端），保留 dev")
    print("=" * 60)

    original, code = get_output("rev-parse", "--abbrev-ref", "HEAD")
    if code != 0 or not original or original == "HEAD":
        print("\n[错误] 当前处于 detached HEAD，无法确定原分支；请先切到 dev")
        sys.exit(1)
    print(f"当前分支: {original}")

    # 1. 工作区必须干净（合并会改写工作树，脏工作区不可控）
    dirty, code = get_output("status", "--porcelain")
    if code != 0:
        print("\n[错误] git status 执行失败")
        sys.exit(1)
    if dirty:
        print("\n[中止] 存在未提交/未跟踪的本地改动，请先提交（dev）后再合并：")
        for line in dirty.splitlines()[:15]:
            print("   ", line)
        if len(dirty.splitlines()) > 15:
            print(f"    ... 共 {len(dirty.splitlines())} 条")
        sys.exit(1)

    # 2. 本地 dev 必须已推送，且与 origin/dev 一致（否则远端会缺提交）
    try:
        run("fetch", "origin", "dev", "v17")
    except GitError as e:
        print(f"\n[中止] 拉取远端失败：{e}")
        print("       若远端还没有 dev 分支，请先执行任务「推送 dev 到 origin」。")
        sys.exit(1)

    local_dev, code = get_output("rev-parse", "dev")
    if code != 0:
        print("\n[中止] 本地不存在 dev 分支")
        sys.exit(1)
    remote_dev, code = get_output("rev-parse", "origin/dev")
    if code != 0:
        print("\n[中止] 远端没有 dev 分支，请先执行任务「推送 dev 到 origin」")
        sys.exit(1)
    if local_dev != remote_dev:
        print("\n[中止] 本地 dev 与 origin/dev 不一致：")
        print(f"       本地     {local_dev[:7]}")
        print(f"       origin  {remote_dev[:7]}")
        print("       请先执行任务「推送 dev 到 origin」，确保测试环境拉到的就是当前代码。")
        sys.exit(1)

    switched = False
    ok = False
    try:
        # 3. 本地合并（v17 只走快进，绝不产生 merge commit 或直接提交）
        run("checkout", "v17")
        switched = True
        # 先对齐远端 v17，避免 push 时因落后被拒（分叉会在这里失败，交人工处理）
        run("merge", "--ff-only", "origin/v17")
        run("merge", "--ff-only", "dev")

        # 4. 远端合并（推送 v17）
        run("push", "origin", "v17")
        ok = True
    except GitError as e:
        print(f"\n[失败] {e}")
        print("       若提示非快进，说明 v17 有 dev 之外的新提交，请人工检查后重试。")
    finally:
        if switched:
            print(f"\n[清理] 切回原分支 {original}")
            subprocess.run(["git", "checkout", original])

    if not ok:
        sys.exit(1)

    dev_sha, _ = get_output("rev-parse", "--short", "dev")
    v17_sha, _ = get_output("rev-parse", "--short", "v17")
    print("\n" + "=" * 60)
    print("完成：dev 已合并进 v17（本地 + origin），dev 分支保留")
    print(f"  dev = {dev_sha}")
    print(f"  v17 = {v17_sha}")
    print("  后续开发继续在 dev 上进行；dev 再次领先后再重复本任务。")
    print("=" * 60)


if __name__ == "__main__":
    main()
