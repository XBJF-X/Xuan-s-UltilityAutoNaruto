# -*- coding: utf-8 -*-
"""生成 ``_version.py``（被 ``.gitignore`` 忽略，干净检出/CI 没有该文件）。

为什么需要：
- ``backend/runtime_info.get_client_version()`` 与 ``/api/utils/version`` 直接读它；
- ``test_scene/verify_consume_stamina_params.py`` 把它当作独立版本来源；
- 安装包构建（``build/build_release.py``）也复制它。

版本号唯一来源是 ``.cz.toml``（commitizen 的 ``[tool.commitizen] version``）。

用法：
    python -X utf8 build/gen_version_file.py           # 写入 _version.py
    python -X utf8 build/gen_version_file.py --check   # 只校验，不一致时退出码 1
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CZ_TOML = ROOT / ".cz.toml"
TARGET = ROOT / "_version.py"
VERSION_RE = re.compile(r'(?m)^version\s*=\s*"([^"]+)"')


def read_version() -> str:
    if not CZ_TOML.exists():
        raise SystemExit(f"找不到 {CZ_TOML}（版本号的唯一来源）")
    text = CZ_TOML.read_text(encoding="utf-8")
    match = VERSION_RE.search(text)
    if match is None or not match.group(1).strip():
        raise SystemExit(f"无法从 {CZ_TOML} 解析 version")
    return match.group(1).strip()


def render(version: str) -> str:
    return f'__version__ = "{version}"\n'


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="从 .cz.toml 生成 _version.py")
    parser.add_argument("--check", action="store_true",
                        help="只校验 _version.py 是否与 .cz.toml 一致")
    args = parser.parse_args(argv)

    version = read_version()
    content = render(version)
    if args.check:
        current = TARGET.read_text(encoding="utf-8") if TARGET.exists() else ""
        if current != content:
            print(f"OUTDATED {TARGET}（期望 version={version}）")
            return 1
        print(f"OK version={version}")
        return 0

    TARGET.write_text(content, encoding="utf-8")
    print(f"WROTE {TARGET} version={version}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
