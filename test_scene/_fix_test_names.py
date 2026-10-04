# -*- coding: utf-8 -*-
"""一次性替换：把测试脚本里的旧钩子名改为新 on_* 名，并删除 start_line/dead_line 赋值。

用法：.venv\\Scripts\\python.exe test_scene\\_fix_test_names.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGETS = ["verify_renfatijiangli_time.py", "verify_task_schedules.py"]

REPLACEMENTS = [
    ("task._handle_execution_completed(", "task.on_complete("),
    ("task._handle_timeout_deadline(", "task.on_deadline("),
    ("task._handle_delay(", "task.on_delay("),
    ("        task.start_line = None\n", ""),
    ("        task.dead_line = None\n", ""),
]


def main() -> int:
    for name in TARGETS:
        path = os.path.join(HERE, name)
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        before = text
        stats = []
        for old, new in REPLACEMENTS:
            count = before.count(old)
            if count:
                stats.append(f"{old.strip()!r} x{count}")
            before = before.replace(old, new)
        if before != text:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(before)
            print(f"{name}: 已更新 -> {', '.join(stats)}")
        else:
            print(f"{name}: 无需修改")
    return 0


if __name__ == "__main__":
    sys.exit(main())
