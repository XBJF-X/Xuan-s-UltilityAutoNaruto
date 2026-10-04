# -*- coding: utf-8 -*-
"""诊断：任务[忍法帖奖励]所需的场景与元素是否已存在于资源库（src/database.db）。"""
import os
import sqlite3
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DB = os.path.join(_ROOT, "src", "database.db")
_KEY = "忍法帖"
# 任务[忍法帖奖励]运行时按场景需要的元素
_NEED = {
    "忍法帖-周任务": ["领取", "周活跃"],
    "忍法帖-周活跃": ["已领", "本周活跃度值", "活跃度-50", "活跃度-100",
                  "活跃度-150", "活跃度-200", "活跃度-300"],
}

con = sqlite3.connect(f"file:{_DB}?mode=ro", uri=True)
cur = con.cursor()
scenes = cur.execute(
    "SELECT id, name FROM scene WHERE name LIKE ? ORDER BY name",
    (f"%{_KEY}%",)).fetchall()
ok = True
for scene_id, scene_name in scenes:
    elems = [r[0] for r in cur.execute(
        "SELECT name FROM element WHERE scene_id = ? ORDER BY name",
        (scene_id,))]
    print(f"场景[{scene_name}] 元素({len(elems)}): {elems}")
    for need in _NEED.get(scene_name, []):
        if need not in elems:
            ok = False
            print(f"    !! 缺失元素: {need}")
print("结论:", "所需场景/元素齐全" if ok else "存在缺失，请补齐资源")
con.close()
sys.exit(0)