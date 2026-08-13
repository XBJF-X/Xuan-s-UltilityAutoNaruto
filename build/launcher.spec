# -*- mode: python ; coding: utf-8 -*-
"""
Xuan 引导器 PyInstaller spec

只打包引导器（launcher.py）+ WebView 窗口依赖（pywebview/pythonnet）。
后端运行时依赖随包分发：本 spec 通过 datas 将可移植 Python 运行时
（build/runtime/，含 python.exe、stdlib、site-packages，_pth 相对路径、
无构建机硬编码）打进 _internal/venv/；引导器用该内置 python.exe 以
子进程方式运行外部 backend 源码，从而支持热更新且换电脑可运行。
"""
import os

from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs

# PyInstaller 以 exec 方式执行 spec，无 __file__；用 SPECPATH（spec 所在目录）
try:
    _spec_dir = SPECPATH  # type: ignore[name-defined]
except NameError:
    _spec_dir = os.getcwd()
ROOT = os.path.abspath(os.path.join(_spec_dir, ".."))
RUNTIME_DIR = os.path.join(ROOT, "build", "runtime")

a = Analysis(
    [os.path.join(ROOT, "launcher.py")],
    pathex=[ROOT],
    binaries=collect_dynamic_libs("pythonnet") + collect_dynamic_libs("clr_loader"),
    datas=collect_data_files("webview") + [(RUNTIME_DIR, "venv")],
    hiddenimports=["clr", "pythonnet"] + collect_submodules("webview"),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 后端运行时依赖由内置 venv 提供，引导器不需要（排除以减小体积、加快打包）
        "fastapi", "uvicorn", "websockets", "python_multipart", "pydantic",
        "sqlmodel", "sqlalchemy", "cv2", "numpy", "aiofiles",
        "adbutils", "uiautomator2", "minidevice", "pyminitouch", "win32gui",
        "win32ui", "comtypes", "onnxruntime", "requests", "loguru",
        # 旧版 UI / 开发工具（确保不混入）
        "PySide6", "PySide6_Addons", "PySide6_Essentials", "shiboken6",
        "PyAutoGUI", "MouseInfo", "PyGetWindow", "PyMsgBox", "pyperclip",
        "PyRect", "PyScreeze", "pytweening", "retry2", "py_spy",
        "altgraph", "commitizen", "questionary", "prompt_toolkit", "decli",
        "tomlkit",
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Xuan",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(ROOT, "src", "ASDS.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Xuan",
)
