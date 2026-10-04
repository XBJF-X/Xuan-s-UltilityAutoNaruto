# -*- coding: utf-8 -*-
"""只读检查：扫出 backend/core/legacy/Task/*.py 中未被使用的 import（供清理用）。

用法：.venv\\Scripts\\python.exe test_scene\\_check_unused_imports.py
"""
import ast
import os
import sys

TASK_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "backend", "core", "legacy", "Task")


def collect_used_names(tree: ast.AST) -> set:
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            # 形如 module.attr 时把 module 记为已使用
            target = node
            while isinstance(target, ast.Attribute):
                target = target.value
            if isinstance(target, ast.Name):
                used.add(target.id)
    return used


def main() -> int:
    problems = 0
    for name in sorted(os.listdir(TASK_DIR)):
        if not name.endswith(".py"):
            continue
        path = os.path.join(TASK_DIR, name)
        with open(path, encoding="utf-8") as fh:
            source = fh.read()
        tree = ast.parse(source)
        used = collect_used_names(tree)
        imported = []
        for node in tree.body:                    # 只看模块顶层 import
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.append((alias.asname or alias.name.split(".")[0],
                                     f"import {alias.name}",
                                     node.lineno))
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    imported.append((alias.asname or alias.name,
                                     f"from {node.module} import {alias.name}",
                                     node.lineno))
        for local_name, text, lineno in imported:
            if local_name not in used:
                print(f"{name}:{lineno}: UNUSED -> {text}")
                problems += 1
    print(f"\n未使用 import 数：{problems}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
