# -*- coding: utf-8 -*-
"""dev/v17 分支任务回归（离线：在临时 git 仓库里跑真实脚本，不触碰工作区与远端）。

覆盖：
1. ``scripts/git_push_dev.py``：推送 dev、非 dev 分支自动切换、脏工作区拒绝
2. ``scripts/git_merge_dev_into_v17.py``：快进合并 + 推送 v17 + 保留 dev + 切回原分支、
   未推送 dev 拒绝、非快进关系拒绝、脏工作区拒绝
3. VS Code 任务与规则文件接线（.vscode/tasks.json、.clinerules/08-branch-workflow.md）
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
PUSH_SCRIPT = _PROJECT_ROOT / "scripts" / "git_push_dev.py"
MERGE_SCRIPT = _PROJECT_ROOT / "scripts" / "git_merge_dev_into_v17.py"
TASKS_JSON = _PROJECT_ROOT / ".vscode" / "tasks.json"
RULE_FILE = _PROJECT_ROOT / ".clinerules" / "08-branch-workflow.md"

_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "tester",
    "GIT_AUTHOR_EMAIL": "tester@example.com",
    "GIT_COMMITTER_NAME": "tester",
    "GIT_COMMITTER_EMAIL": "tester@example.com",
}


def strip_jsonc(text):
    """去掉 JSONC 行注释（本项目 tasks.json 允许 // 注释）。"""
    out = []
    in_str = False
    esc = False
    i = 0
    while i < len(text):
        ch = text[i]
        if in_str:
            out.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < len(text) and text[i + 1] == "/":
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def git(cwd, *args, check=True):
    r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=_ENV)
    if check and r.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} 失败：{r.stdout}\n{r.stderr}")
    return r


def commit_file(repo, name, text):
    (Path(repo) / name).write_text(text, encoding="utf-8")
    git(repo, "add", name)
    git(repo, "commit", "-m", f"add {name}")


def init_repo(tmp):
    """建 bare 远端 + 工作区：v17（基线）与 dev（领先一个提交），且已推送。"""
    tmp = Path(tmp)
    origin = tmp / "origin.git"
    work = tmp / "work"
    git(tmp, "init", "--bare", str(origin))
    git(tmp, "init", str(work))
    commit_file(work, "app.txt", "v17\n")
    git(work, "branch", "-m", "v17")
    git(work, "checkout", "-b", "dev")
    commit_file(work, "dev.txt", "dev\n")
    git(work, "remote", "add", "origin", str(origin))
    git(work, "push", "-u", "origin", "v17", "dev")
    return work, origin


def run_script(work, script):
    return subprocess.run([sys.executable, str(script)], cwd=str(work),
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=_ENV)


def sha(repo, ref):
    return git(repo, "rev-parse", ref).stdout.strip()


def current_branch(repo):
    return git(repo, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()


class PushDevScriptTest(unittest.TestCase):
    def test_pushes_dev_and_switches_branch(self):
        with tempfile.TemporaryDirectory() as td:
            work, _ = init_repo(td)
            # 在 dev 上新增一个提交（未推送），再从 v17 触发任务
            commit_file(work, "feature.txt", "feature\n")
            local_dev = sha(work, "dev")
            git(work, "checkout", "v17")
            res = run_script(work, PUSH_SCRIPT)
            self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
            self.assertEqual(current_branch(work), "dev")
            self.assertEqual(sha(work, "origin/dev"), local_dev)

    def test_rejects_dirty_worktree(self):
        with tempfile.TemporaryDirectory() as td:
            work, _ = init_repo(td)
            (Path(work) / "dirty.txt").write_text("x\n", encoding="utf-8")
            before = sha(work, "origin/dev")
            res = run_script(work, PUSH_SCRIPT)
            self.assertNotEqual(res.returncode, 0)
            self.assertIn("未提交", res.stdout)
            self.assertEqual(sha(work, "origin/dev"), before)


class MergeDevIntoV17ScriptTest(unittest.TestCase):
    def test_fast_forward_merge_pushes_and_keeps_dev(self):
        with tempfile.TemporaryDirectory() as td:
            work, _ = init_repo(td)
            dev_sha = sha(work, "dev")
            res = run_script(work, MERGE_SCRIPT)
            self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
            self.assertEqual(sha(work, "v17"), dev_sha)
            self.assertEqual(sha(work, "origin/v17"), dev_sha)
            self.assertEqual(sha(work, "dev"), dev_sha, "dev 必须保留且指向同一提交")
            branches = git(work, "branch", "--list", "dev").stdout
            self.assertIn("dev", branches)
            self.assertEqual(current_branch(work), "dev", "完成后应切回原分支")

    def test_rejects_unpushed_dev(self):
        with tempfile.TemporaryDirectory() as td:
            work, _ = init_repo(td)
            commit_file(work, "local-only.txt", "x\n")
            v17_before = sha(work, "v17")
            res = run_script(work, MERGE_SCRIPT)
            self.assertNotEqual(res.returncode, 0)
            self.assertIn("origin/dev", res.stdout)
            self.assertEqual(sha(work, "v17"), v17_before)
            self.assertEqual(current_branch(work), "dev")

    def test_rejects_non_fast_forward_v17(self):
        with tempfile.TemporaryDirectory() as td:
            work, _ = init_repo(td)
            # 模拟 v17 上有 dev 之外的提交（例如别人直接改 v17）
            git(work, "checkout", "v17")
            commit_file(work, "v17-only.txt", "x\n")
            git(work, "push", "origin", "v17")
            git(work, "checkout", "dev")
            v17_sha = sha(work, "v17")
            res = run_script(work, MERGE_SCRIPT)
            self.assertNotEqual(res.returncode, 0)
            self.assertIn("非快进", res.stdout)
            self.assertEqual(sha(work, "v17"), v17_sha, "合并失败不得移动 v17")
            self.assertEqual(current_branch(work), "dev", "失败后也必须切回原分支")

    def test_rejects_dirty_worktree(self):
        with tempfile.TemporaryDirectory() as td:
            work, _ = init_repo(td)
            (Path(work) / "dirty.txt").write_text("x\n", encoding="utf-8")
            v17_before = sha(work, "v17")
            res = run_script(work, MERGE_SCRIPT)
            self.assertNotEqual(res.returncode, 0)
            self.assertIn("未提交", res.stdout)
            self.assertEqual(sha(work, "v17"), v17_before)


class WiringTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks_raw = TASKS_JSON.read_text(encoding="utf-8")
        cls.rule = RULE_FILE.read_text(encoding="utf-8")

    def test_tasks_registered(self):
        self.assertIn("scripts/git_push_dev.py", self.tasks_raw)
        self.assertIn("scripts/git_merge_dev_into_v17.py", self.tasks_raw)
        data = json.loads(strip_jsonc(self.tasks_raw))
        labels = [t.get("label") for t in data["tasks"]]
        for want in ("推送 dev 到 origin", "dev 合并进 v17（本地+远端，保留 dev）"):
            self.assertEqual(labels.count(want), 1, f"任务 {want} 应恰好注册一次：{labels}")

    def test_rule_requires_dev_branch(self):
        for text in ("开发修改一律在 `dev` 分支进行", "不动 `v17`", "`dev` 分支永远保留"):
            self.assertIn(text, self.rule)

    def test_scripts_never_force_push(self):
        for script in (PUSH_SCRIPT, MERGE_SCRIPT):
            with self.subTest(script=script.name):
                src = script.read_text(encoding="utf-8")
                self.assertNotIn("--force", src)
                self.assertNotIn('"-f"', src)

    def test_merge_script_uses_ff_only(self):
        src = MERGE_SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"merge", "--ff-only"', src)
        self.assertIn('"push", "origin", "v17"', src)


if __name__ == "__main__":
    unittest.main(verbosity=2)

