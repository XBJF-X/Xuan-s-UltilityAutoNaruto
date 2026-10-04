# -*- coding: utf-8 -*-
"""构建产物核对：确认 dist 中包含启动引导弹窗与反馈界面版本检测的关键文案/行为。

用途：`vite build` 之后运行，验证新功能文案确实进入随包分发的 dist（backend SPA 托管 dist）。
不进入常规回归（dist 为构建产物），仅本机核对用。
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST = _PROJECT_ROOT / "frontend" / "dist"

CHECKS: list[tuple[str, str]] = [
    ("跳转反馈界面", "启动引导弹窗按钮"),
    ("不再提示", "启动引导弹窗复选框"),
    ("请阅读提示", "倒计时提示文案"),
    ("点击顶部栏右上角的文件夹图标", "引导文案（文件夹图标）"),
    ("将反馈包发送给开发者即可", "引导文案（尾句）"),
    ("当前代码非最新", "反馈界面非最新提示"),
    ("去更新", "反馈界面更新入口"),
    ("可忽略此提示直接生成反馈包", "检测失败降级提示"),
    ("启动提示", "全局设置键名"),
]


def main() -> int:
    if not DIST.exists():
        print(f"[SKIP] dist 不存在：{DIST}")
        return 0
    files = [p for p in DIST.rglob("*.js")]
    print(f"扫描 dist JS 文件：{len(files)} 个")
    failed = 0
    for text, desc in CHECKS:
        hit = ""
        for path in files:
            if text in path.read_text(encoding="utf-8"):
                hit = path.name
                break
        if hit:
            print(f"[PASS] {desc}: 「{text}」→ {hit}")
        else:
            failed += 1
            print(f"[FAIL] {desc}: 未在 dist 中找到「{text}」")
    print("=" * 60)
    print("全部通过" if failed == 0 else f"失败 {failed} 项")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
