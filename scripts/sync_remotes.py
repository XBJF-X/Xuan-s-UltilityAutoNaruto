#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""同时推送代码与 Tags 到 GitHub(origin) 与 Gitee（VS Code 任务调用）。

- origin: GitHub  (git@github.com:XBJF-X/Xuan-s-UltilityAutoNaruto.git)
- gitee:  Gitee   (https://gitee.com/xuan-bu-jiu-fei/Xuan-s-UltilityAutoNaruto.git)
- 首次运行若 gitee remote 未配置会自动添加；
- Gitee 首次推送需在系统凭据中配置账号（Git Credential Manager 会弹窗），失败会给出提示；
- Release 发布不在本脚本范围（GitHub/Gitee 需在网页端手动发布）。
"""
import subprocess
import sys

GITEE_URL = "https://gitee.com/xuan-bu-jiu-fei/Xuan-s-UltilityAutoNaruto.git"
REMOTES = [
    ("origin", "GitHub"),
    ("gitee", "Gitee"),
]


def run(*args):
    print(f"\n>>> git {' '.join(args)}")
    r = subprocess.run(["git", *args])
    if r.returncode != 0:
        print(f"\n[失败] git {' '.join(args)} 返回码 {r.returncode}")
        sys.exit(r.returncode)
    return r


def get_output(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True,
                       encoding="utf-8", errors="ignore")
    return (r.stdout or "").strip()


def main():
    print("=" * 60)
    print("同步代码与 Tags 到 GitHub + Gitee")
    print("=" * 60)

    branch = get_output("rev-parse", "--abbrev-ref", "HEAD")
    if not branch or branch == "HEAD":
        print("[错误] 无法确定当前分支（可能处于 detached HEAD 状态）")
        sys.exit(1)
    print(f"当前分支: {branch}")

    # 未提交/未跟踪改动检查：存在则中止，避免误推送
    dirty = get_output("status", "--porcelain")
    if dirty:
        print("\n[警告] 存在未提交/未跟踪的本地改动，请先提交后再同步：")
        for line in dirty.splitlines()[:15]:
            print("   ", line)
        if len(dirty.splitlines()) > 15:
            print(f"    ... 共 {len(dirty.splitlines())} 条")
        sys.exit(1)

    # 确保 gitee remote 存在
    remotes = set(get_output("remote").split())
    if "gitee" not in remotes:
        print(f"\n[提示] 未配置 gitee remote，自动添加: git remote add gitee {GITEE_URL}")
        run("remote", "add", "gitee", GITEE_URL)

    # 推送代码
    for name, label in REMOTES:
        print(f"\n=== 推送 {branch} 到 {label}({name}) ===")
        run("push", name, branch)

    # 推送 tags
    for name, label in REMOTES:
        print(f"\n=== 推送 Tags 到 {label}({name}) ===")
        run("push", name, "--tags")

    print("\n" + "=" * 60)
    print("同步完成！")
    print("· Release 请到 GitHub/Gitee 网页端手动发布（本脚本不自动发布）")
    print("=" * 60)


if __name__ == "__main__":
    main()
