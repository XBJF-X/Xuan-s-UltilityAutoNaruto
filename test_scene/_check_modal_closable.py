# -*- coding: utf-8 -*-
"""核对 naive-ui NModal 是否支持 `close-on-esc`（Esc 关闭）：若支持且默认 true，
启动引导弹窗必须显式关闭该行为，否则用户可在 10s 倒计时内按 Esc 关闭弹窗。

只读核查工具（不进入常规回归）。
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]

_MODAL_FILES = [
    "frontend/node_modules/naive-ui/es/modal/src/Modal.mjs",
    "frontend/node_modules/naive-ui/es/modal/src/Modal.d.ts",
    "frontend/node_modules/naive-ui/es/dialog/src/Dialog.mjs",
]


def main() -> int:
    for rel in _MODAL_FILES:
        path = Path(rel)
        if not path.exists():
            print(f"[SKIP] 缺少 {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        hits = [k for k in ("closeOnEsc", "maskClosable", "keyboard") if k in text]
        print(f"{rel}: {hits}")
        lines = text.splitlines()
        for idx, line in enumerate(lines):
            if "closeOnEsc" in line:
                for item in lines[idx: idx + 5]:
                    print(f"    {item.strip()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
