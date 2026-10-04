# -*- coding: utf-8 -*-
"""只读检查：列出指定文件中若干名字的"非 import 使用行"，用于确认 import 是否可删。

用法：.venv\\Scripts\\python.exe test_scene\\_check_names.py
"""
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASK_DIR = os.path.join(ROOT, "backend", "core", "legacy", "Task")

TARGET_FILES = [
    "DongRiYanHuaJi.py", "GengDuoWanFa.py", "MeiZhouShengChang.py",
    "QingBaoZhan.py", "RenFaTieJiangLi.py", "SaiJiShengChang.py",
    "XiuXingZhiLu.py", "YiLeWaiMai.py", "ZhuiJiXiaoZuZhi.py",
    "GaoJiRenZheZhaoMu.py", "PanRenLaiXi.py", "PaiHangBangDianZan.py",
    "BaseTask.py",
]
NAMES = ["datetime", "time", "timedelta", "ZoneInfo", "TooEarlyToRun",
         "TaskCompleted", "List", "Weekday", "Weekly", "Monthly", "Daily",
         "DAY_RESET", "Window", "Custom", "KEY_INDEX"]


def _import_lines(tree: ast.AST) -> set:
    lines = set()
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for ln in range(node.lineno, (node.end_lineno or node.lineno) + 1):
                lines.add(ln)
    return lines


def main() -> int:
    for name in TARGET_FILES:
        path = os.path.join(TASK_DIR, name)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            source = fh.read()
            lines = source.splitlines()
        tree = ast.parse(source)
        import_lines = _import_lines(tree)
        used = {}
        for node in ast.walk(tree):
            target = None
            if isinstance(node, ast.Name):
                target = node.id
            elif isinstance(node, ast.Attribute):
                value = node
                while isinstance(value, ast.Attribute):
                    value = value.value
                if isinstance(value, ast.Name):
                    target = value.id
            if target in NAMES and node.lineno not in import_lines:
                used.setdefault(target, []).append(node.lineno)
        print(f"=== {name} ===")
        if not used:
            print("    （无）")
        for key in sorted(used):
            show = sorted(set(used[key]))[:8]
            print(f"    {key}: 行 {show}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
