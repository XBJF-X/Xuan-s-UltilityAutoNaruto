# -*- coding: utf-8 -*-
"""静态检查：backend/ 里「函数体引用了但没定义的名字」（≈ pyflakes F821）。

为什么需要它：
    `python -m compileall` 只做语法编译、**不做名字解析**；「关键模块导入」也只跑
    模块级代码。漏掉 import 的名字只有在**函数被调用且执行到那一行**时才抛
    NameError，编译期与导入期都是绿的。

    2026-10 的真实事故：`backend/services/update_service.py` 从 api 层下沉时漏了
    `import zipfile`，热更新下载校验 `zipfile.is_zipfile()` 抛 NameError，被
    `except` 吞成「下载更新包失败」→ 双更新源全部失败 → 热更新整体不可用，
    而 CI（compileall + 回归批 + 模块导入）全绿。

覆盖边界（重要）：
    - 只查**函数体**里的 Name 读取。模块级/类体的未定义名会在 import 时报错，
      由 `.github/workflows/ci.yml` 的「关键模块导入」步骤覆盖。
    - `from x import *` 无法静态判定 → 整文件跳过，并在跳过清单里显式列出；
      新增这类文件必须先确认（测试会断言跳过清单不变）。
    - 装饰器注入、`globals()`/`eval` 动态定义的名字识别不到。
    - 名字在同一函数的嵌套子函数里赋值时，本检查按「已定义」处理（保守取向：
      宁可漏报，也不制造误报把门槛废掉）。

用法：
    .venv\\Scripts\\python.exe -X utf8 test_scene/verify_undefined_names.py
    在 `_run_verify_batch.py` 快速集里按 `verify_*.py` 自动发现。

与 ruff 的关系：
    CI 的门槛是 `ruff check backend`（根目录 ruff.toml，规则 `F/E722/B006`），它覆盖
    本脚本的全部检查并更精确。本脚本保留为**零依赖兜底**：本地没装 ruff、或想在不跑
    CI 的环境里快速自检时仍可用，同时额外锁住「`from x import *` 跳过清单不得随新增文件
    悄悄扩大」。
"""
import ast
import builtins
import os
import sys
import unittest
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 允许跳过静态扫描的文件（`from x import *`）：新增项必须写明原因，
# 因为星号导入会让整文件失去保护。
STAR_IMPORT_ALLOWED = {
    "backend/core/legacy/OnnxOcr/imaug.py",  # 第三方 OCR 前/后处理代码，保持上游写法
}

# 已知未定义名（修复前不得删）：键为 `相对路径:名字`，值为原因与跟进方式。
KNOWN_UNDEFINED = {}

_BUILTINS = set(dir(builtins)) | {
    "__name__", "__file__", "__doc__", "__package__", "__spec__",
    "__loader__", "__builtins__",
}


def _arg_names(args):
    """函数 / lambda 的形参名（含 *args / **kwargs / keyword-only）。"""
    if args is None:
        return set()
    names = {a.arg for a in list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)}
    if args.vararg:
        names.add(args.vararg.arg)
    if args.kwarg:
        names.add(args.kwarg.arg)
    return names


def _collect(nodes, *, enter_nested):
    """收集一组语句在本作用域内**绑定**的名字。

    :param enter_nested: True 时进入嵌套函数/类体（用于函数作用域：保守地认为
        「闭包引用外层局部变量」是合法的）；False 时只看本层（用于模块作用域：
        避免把函数里的局部变量误当成模块级全局）。
    """
    names = set()
    stack = list(nodes)
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
            # 装饰器/默认值在**外层**作用域求值，属于本层引用
            stack.extend(node.decorator_list)
            if enter_nested:
                names.update(_arg_names(getattr(node, "args", None)))
                stack.extend(node.body)
            continue
        if isinstance(node, ast.Lambda):
            if enter_nested:
                names.update(_arg_names(node.args))
                stack.append(node.body)
            continue
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add((alias.asname or alias.name).split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add("*" if alias.name == "*" else (alias.asname or alias.name))
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            names.add(node.id)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            names.update(node.names)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            names.add(node.name)
        elif isinstance(node, ast.MatchAs) and node.name:
            names.add(node.name)
        elif isinstance(node, ast.MatchStar) and node.name:
            names.add(node.name)
        elif isinstance(node, ast.MatchMapping) and node.rest:
            names.add(node.rest)
        stack.extend(ast.iter_child_nodes(node))
    return names


def _own_nodes(body):
    """产出属于**当前作用域**的节点：嵌套函数/类只取装饰器与默认值，不进入其函数体。"""
    stack = list(body)
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            stack.extend(node.decorator_list)
            args = getattr(node, "args", None)
            if args is not None:
                stack.extend(args.defaults)
                stack.extend(d for d in args.kw_defaults if d is not None)
            continue
        if isinstance(node, ast.Lambda):
            stack.extend(node.args.defaults)
            stack.extend(d for d in node.args.kw_defaults if d is not None)
            continue
        yield node
        stack.extend(ast.iter_child_nodes(node))


def _child_functions(body):
    """本作用域直接包含的函数（含类体里的方法；不含函数内的嵌套函数）。"""
    found, stack = [], list(body)
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            found.append(node)
            continue
        if isinstance(node, ast.ClassDef):
            # 类体不算闭包作用域（方法里裸写类属性确实是 NameError），但方法要继续检查
            stack.extend(node.body)
            continue
        if isinstance(node, ast.Lambda):
            continue
        stack.extend(ast.iter_child_nodes(node))
    return found


def _check_function(fn, enclosing, module_names, problems):
    local_names = _collect(fn.body, enter_nested=False) | _arg_names(fn.args)
    available = module_names | enclosing | local_names
    for node in _own_nodes(fn.body):
        if (isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
                and node.id not in available):
            problems.append((node.lineno, fn.name, node.id))
    for child in _child_functions(fn.body):
        _check_function(child, available, module_names, problems)


def collect_undefined_from_source(source, filename="<source>"):
    """返回 ``(problems, has_star_import)``；problems 为 ``(行号, 函数名, 名字)``。"""
    tree = ast.parse(source, filename)
    module_names = _collect(tree.body, enter_nested=False) | _BUILTINS
    if "*" in module_names:
        return [], True
    problems = []
    for fn in _child_functions(tree.body):
        _check_function(fn, set(), module_names, problems)
    return problems, False


def scan_backend(project_root):
    """扫描 ``<project_root>/backend`` 下全部 .py；返回 ``(problems, skipped)``。"""
    project_root = Path(project_root)
    problems, skipped = [], []
    for path in sorted((project_root / "backend").rglob("*.py")):
        rel = path.relative_to(project_root).as_posix()
        found, has_star = collect_undefined_from_source(
            path.read_text(encoding="utf-8"), rel)
        if has_star:
            skipped.append(rel)
            continue
        for lineno, func, name in found:
            if f"{rel}:{name}" in KNOWN_UNDEFINED:
                continue
            problems.append(f"{rel}:{lineno}: {func}() 使用了未定义的名字 {name!r}")
    return problems, skipped



class CheckerSensitivityTest(unittest.TestCase):
    """先证明检查器本身有效（防「扫描器静默失效 → 门槛形同虚设」）。"""

    def test_flags_missing_import(self):
        """复刻本次事故：用了 zipfile 却没 import。"""
        src = (
            "def apply(p):\n"
            "    if not zipfile.is_zipfile(p):\n"
            "        return None\n"
            "    with zipfile.ZipFile(p) as zf:\n"
            "        return zf.namelist()\n"
        )
        problems, has_star = collect_undefined_from_source(src)
        self.assertFalse(has_star)
        self.assertEqual([name for _, _, name in problems], ["zipfile", "zipfile"])

    def test_flags_function_local_leak(self):
        """只在别的函数里赋值的名字，不能当成模块级全局。"""
        src = (
            "def a():\n"
            "    shared = 1\n"
            "    return shared\n"
            "\n"
            "def b():\n"
            "    return shared\n"
        )
        problems, _ = collect_undefined_from_source(src)
        self.assertEqual([(name, func) for _, func, name in problems], [("shared", "b")])

    def test_no_false_positive_common_scopes(self):
        """常见写法（闭包/推导式/海象/match/except as/形参/TYPE_CHECKING）零误报。"""
        src = (
            "from typing import TYPE_CHECKING\n"
            "\n"
            "if TYPE_CHECKING:\n"
            "    from pathlib import Path\n"
            "\n"
            "def deco(fn):\n"
            "    return fn\n"
            "\n"
            "@deco\n"
            "def outer(items, *args, flag=False, **kwargs):\n"
            "    total = 0\n"
            "    for index, item in enumerate(items):\n"
            "        total += item + index\n"
            "    with open('x') as handle:\n"
            "        handle.read()\n"
            "    try:\n"
            "        raise ValueError('x')\n"
            "    except ValueError as exc:\n"
            "        print(exc)\n"
            "    mapping = {k: v for k, v in zip(args, kwargs)}\n"
            "    if (size := len(mapping)) > 0:\n"
            "        total += size\n"
            "    match total:\n"
            "        case [first, *rest]:\n"
            "            print(first, rest)\n"
            "        case {'k': value, **extra}:\n"
            "            print(value, extra)\n"
            "        case _:\n"
            "            print(Path, flag)\n"
            "\n"
            "    def inner(x=total):\n"
            "        return x, total\n"
            "\n"
            "    return inner\n"
        )
        problems, has_star = collect_undefined_from_source(src)
        self.assertFalse(has_star)
        self.assertEqual(problems, [])

    def test_star_import_file_is_skipped(self):
        src = (
            "from os.path import *\n"
            "\n"
            "def f():\n"
            "    return definitely_not_defined_anywhere\n"
        )
        problems, has_star = collect_undefined_from_source(src)
        self.assertTrue(has_star)
        self.assertEqual(problems, [])


class BackendScanTest(unittest.TestCase):

    def test_backend_has_no_undefined_names(self):
        problems, skipped = scan_backend(_PROJECT_ROOT)
        self.assertEqual(
            problems, [],
            "发现未定义的名字（通常是模块搬迁/复制时漏了 import）：\n"
            + "\n".join(problems)
            + "\n如确为动态注入，请加到本文件的 KNOWN_UNDEFINED 并写明原因。")
        unexpected = set(skipped) - STAR_IMPORT_ALLOWED
        self.assertEqual(
            unexpected, set(),
            f"新增了 `from x import *`，该文件不受静态检查保护：{sorted(unexpected)}")

    def test_star_import_allowlist_still_exists(self):
        """跳过清单必须仍然对得上（文件改名/删除后要同步，避免清单腐化）。"""
        existing = {
            p.relative_to(_PROJECT_ROOT).as_posix()
            for p in (Path(_PROJECT_ROOT) / "backend").rglob("*.py")
        }
        for rel in STAR_IMPORT_ALLOWED:
            self.assertIn(rel, existing, f"STAR_IMPORT_ALLOWED 里的文件已不存在：{rel}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
