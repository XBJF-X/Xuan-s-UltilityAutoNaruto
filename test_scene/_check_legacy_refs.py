# -*- coding: utf-8 -*-
"""只读检查：扫描 backend/ 下遗留的"旧兼容符号"引用（`del/`、`.venv*` 不在范围内）。

用法：.venv\\Scripts\\python.exe test_scene\\_check_legacy_refs.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN_DIR = os.path.join(ROOT, "backend")

PATTERNS = [
    "_handle_execution_completed",
    "_handle_timeout_deadline",
    "_handle_timeout_max_duration",
    "_handle_too_early",
    "_handle_execute_now",
    "_handle_delay",
    "start_line",
    "dead_line",
    "debug_execute_window",
]


def main() -> int:
    hits = {p: [] for p in PATTERNS}
    for dirpath, dirnames, filenames in os.walk(SCAN_DIR):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in filenames:
            if not name.endswith(".py"):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, ROOT)
            with open(path, encoding="utf-8", errors="replace") as fh:
                for lineno, line in enumerate(fh, 1):
                    for pattern in PATTERNS:
                        if pattern in line:
                            hits[pattern].append(f"{rel}:{lineno}: {line.strip()}")
    for pattern in PATTERNS:
        print(f"=== {pattern} （{len(hits[pattern])} 处） ===")
        for item in hits[pattern]:
            print("   ", item)
    return 0


if __name__ == "__main__":
    sys.exit(main())
