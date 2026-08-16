# -*- coding: utf-8 -*-
"""
Xuan Release 构建脚本

流程：
  1. 前端构建   pnpm build -> frontend/dist
  2. 引导器打包 PyInstaller(launcher.spec) -> build/dist/Xuan（exe + _internal）
  3. 组装安装内容 -> build/release/（venv 内置环境 + backend + frontend/dist + src）
  4. Inno Setup 安装包  build/installer.iss -> build/out/XuanInstaller_<version>.exe

用法（在项目根执行）：
  .venv-build\\Scripts\\python.exe build\\build_release.py [all|frontend|launcher|assemble|inno]

注意：long-running，建议以分离后台方式运行并轮询 build/release.log。
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
RELEASE = BUILD / "release"
RUNTIME = BUILD / "runtime"
BUILD_VENV_PY = ROOT / ".venv-build" / "Scripts" / "python.exe"

# 随包分发的 src 必要文件（含场景资源数据库，供首次启动与热更新）
SRC_FILES = ["DefaultConfig.json", "DefaultSetting.ini", "ASDS.ico", "database.db", "README.md"]


def log(msg: str):
    print(msg, flush=True)


def run(cmd, cwd):
    log("RUN " + " ".join(str(c) for c in cmd))
    full_cmd = [str(c) for c in cmd]
    if os.name == "nt":
        # Windows 下 pnpm/npm 等为 .cmd shim，subprocess 直接 CreateProcess 找不到；
        # 用 shutil.which 解析到实际可执行文件（含 PATHEXT 后缀查找）
        resolved = shutil.which(full_cmd[0])
        if resolved:
            full_cmd[0] = resolved
    r = subprocess.run(
        full_cmd, cwd=str(cwd),
        capture_output=True, text=True, encoding="utf-8", errors="ignore",
    )
    if r.returncode != 0:
        log((r.stdout or "")[-3000:])
        log((r.stderr or "")[-1500:])
        raise SystemExit(f"命令失败: {cmd[0]}")
    return r


def step_runtime():
    """[0/5] 构造可移植 Python 运行时（build/runtime/）。

    从构建环境 .venv-build 的 pyvenv.cfg 读取 base 解释器目录，组装自包含目录：
      python.exe/pythonw.exe/python312.dll/python3.dll + base stdlib(Lib)
      + .venv-build 的 site-packages + base DLLs + VC 运行库
      + python312._pth（相对 exe 目录解析，无任何构建机硬编码路径）。
    随后由 launcher.spec 的 datas 打进 _internal/venv/，做到换电脑也能运行。
    """
    log("[0/5] 构造可移植 Python 运行时 ...")
    cfg = (ROOT / ".venv-build" / "pyvenv.cfg").read_text(encoding="utf-8")
    base = Path(next(l.split("=", 1)[1].strip() for l in cfg.splitlines()
                     if l.strip().startswith("home")))
    log(f"  base 解释器: {base}")

    if RUNTIME.exists():
        shutil.rmtree(RUNTIME)
    RUNTIME.mkdir(parents=True)

    # 1. 解释器本体 + 运行时 DLL（python3.dll 是 cv2 等扩展依赖的稳定 ABI 转发 DLL）
    for f in ("python.exe", "pythonw.exe", "python312.dll", "python3.dll"):
        src = base / f
        if src.exists():
            shutil.copy2(src, RUNTIME / f)
        else:
            log(f"  WARN 缺失 base 文件: {f}")

    # 2. base 的 stdlib（排除全局 site-packages 与缓存）
    def _ignore_base_lib(_src, names):
        return [n for n in names
                if n == "site-packages" or n == "__pycache__"
                or n.endswith((".pyc", ".pyo")) or n.endswith(".pyi")]
    shutil.copytree(base / "Lib", RUNTIME / "Lib", ignore=_ignore_base_lib)

    # 3. 干净构建环境 .venv-build 的 site-packages（覆盖 base 的全局包）
    sp = RUNTIME / "Lib" / "site-packages"
    if sp.exists():
        shutil.rmtree(sp)
    shutil.copytree(ROOT / ".venv-build" / "Lib" / "site-packages", sp,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))

    # 4. base 的 DLLs（_ctypes/_ssl/_decimal 等 C 扩展）
    shutil.copytree(base / "DLLs", RUNTIME / "DLLs")

    # 5. VC++ 运行库（cv2/onnxruntime/pywin32 等依赖，保证目标机无 VC redist 也可运行）
    for dll in ("vcruntime140.dll", "vcruntime140_1.dll",
                "msvcp140.dll", "msvcp140_1.dll", "msvcp140_2.dll"):
        src = Path("C:/Windows/System32") / dll
        if src.exists():
            shutil.copy2(src, RUNTIME / dll)

    # 6. embeddable 风格 _pth：相对 exe 目录解析，彻底摆脱注册表/环境变量/构建机路径
    (RUNTIME / "python312._pth").write_text(
        "Lib\nLib/site-packages\nDLLs\nimport site\n", encoding="utf-8")
    log("  可移植运行时完成 -> build/runtime")


def step_frontend():
    log("[1/5] 前端构建 ...")
    run(["pnpm", "build"], ROOT / "frontend")
    log("前端构建完成 -> frontend/dist")


def step_launcher():
    log("[2/5] PyInstaller 打包引导器 ...")
    if not RUNTIME.exists():
        raise SystemExit("缺少 build/runtime，请先执行 runtime 步骤")
    for d in (BUILD / "dist", BUILD / "work"):
        if d.exists():
            shutil.rmtree(d, ignore_errors=True)
    run([BUILD_VENV_PY, "-m", "PyInstaller",
         "build/launcher.spec", "--distpath", "build/dist", "--workpath", "build/work"],
        ROOT)
    log("引导器打包完成 -> build/dist/Xuan")


def step_assemble():
    log("[3/5] 组装安装内容 -> build/release ...")
    if RELEASE.exists():
        shutil.rmtree(RELEASE, ignore_errors=True)
    RELEASE.mkdir(parents=True, exist_ok=True)

    src_xuan = BUILD / "dist" / "Xuan"
    if not (src_xuan / "Xuan.exe").exists():
        raise SystemExit("缺少引导器产物，请先执行 launcher 步骤")

    # 1. 引导器产物（Xuan.exe + _internal，其中 _internal/venv 为可移植 Python 运行时）
    for item in src_xuan.iterdir():
        dst = RELEASE / item.name
        if item.is_dir():
            shutil.copytree(item, dst)
        else:
            shutil.copy2(item, dst)
    log("  复制引导器产物（含 _internal/venv 可移植运行时）")

    # 2. 后端源码（热更新）
    shutil.copytree(ROOT / "backend", RELEASE / "backend",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
    log("  复制 backend 源码")

    # 3. 前端构建产物（热更新）
    shutil.copytree(ROOT / "frontend" / "dist", RELEASE / "frontend" / "dist")
    log("  复制 frontend/dist")

    # 4. src 必要文件（热更新）
    dst_src = RELEASE / "src"
    dst_src.mkdir(parents=True, exist_ok=True)
    for name in SRC_FILES:
        p = ROOT / "src" / name
        if p.exists():
            shutil.copy2(p, dst_src / name)
    log("  复制 src 必要文件")

    # 5. OCR 模型（随包分发，避免热更新重复下载；不纳入 git）
    ocr_src = ROOT / "bin" / "ppocrv5"
    if ocr_src.exists():
        shutil.copytree(ocr_src, RELEASE / "bin" / "ppocrv5")
        log("  复制 OCR 模型")

    # 6. 版本号随包分发（大更新/版本对比用，后端读取 _version.py）
    src_version = ROOT / "_version.py"
    if src_version.exists():
        shutil.copy2(src_version, RELEASE / "_version.py")
        log("  复制 _version.py（版本号）")

    # 7. 用户数据目录（首次为空，运行后生成）
    (RELEASE / "config").mkdir(exist_ok=True)
    (RELEASE / "log").mkdir(exist_ok=True)
    log("组装完成 -> build/release")


def _read_version() -> str:
    """从 _version.py 读取版本号，失败时兜底 2.0.0。"""
    try:
        import re
        text = (ROOT / "_version.py").read_text(encoding="utf-8", errors="ignore")
        m = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
        if m:
            return m.group(1)
    except Exception:
        pass
    return "2.0.0"


def _sync_iss_version(iss: Path, version: str):
    """构建前将 installer.iss 内 MyAppVersion 自动替换为当前版本号（与 _version.py 保持一致）。

    以 UTF-8 BOM 读写：Inno Setup 6 编译器识别脚本中的中文需要 BOM。
    """
    import re
    try:
        text = iss.read_text(encoding="utf-8-sig", errors="ignore")
    except Exception:
        return
    new_text = re.sub(
        r'(#define\s+MyAppVersion\s+)"[^"]*"',
        rf'\1"{version}"',
        text,
    )
    if new_text != text:
        iss.write_text(new_text, encoding="utf-8-sig")
        log(f"installer.iss MyAppVersion 已同步为 {version}")


def _find_iscc() -> str:
    """定位 Inno Setup 编译器 ISCC.exe。

    查找顺序：环境变量 ISCC → 项目内 del/bin/InnoSetup6 → 系统默认安装路径 → PATH。
    """
    candidates = []
    env = os.environ.get("ISCC")
    if env:
        candidates.append(env)
    candidates.extend([
        str(ROOT / "del" / "bin" / "InnoSetup6" / "ISCC.exe"),
        r"D:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ])
    for c in candidates:
        if os.path.isfile(c):
            return c
    found = shutil.which("ISCC")
    if found:
        return found
    raise SystemExit(
        "未找到 Inno Setup 编译器（ISCC.exe）。\n"
        "请安装 Inno Setup 6（https://jrsoftware.org/isdl.php），\n"
        "或设置环境变量 ISCC 指向 ISCC.exe，或将便携版放入 del/bin/InnoSetup6/。"
    )


def step_inno():
    log("[4/5] Inno Setup 打包安装程序 ...")
    out_dir = BUILD / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    iss = BUILD / "installer.iss"
    if not iss.exists():
        raise SystemExit(f"缺少 Inno Setup 脚本: {iss}")
    version = _read_version()
    _sync_iss_version(iss, version)
    iscc = _find_iscc()
    out_name = f"XuanInstaller_V{version}"
    run([
        iscc,
        f"/DMyAppVersion={version}",
        f"/DReleaseDir={RELEASE}",
        f"/DMyAppIcon={ROOT / 'src' / 'ASDS.ico'}",
        f"/O{out_dir}",
        f"/F{out_name}",
        str(iss),
    ], ROOT)
    out_file = out_dir / f"{out_name}.exe"
    if not out_file.exists():
        raise SystemExit(f"Inno Setup 未生成安装包: {out_file}")
    log("Inno Setup 完成 -> " + str(out_file))


STEPS = {
    "all": ["step_runtime", "step_frontend", "step_launcher", "step_assemble", "step_inno"],
    "runtime": ["step_runtime"],
    "frontend": ["step_frontend"],
    "launcher": ["step_launcher"],
    "assemble": ["step_assemble"],
    "inno": ["step_inno"],
}
_FNS = {
    "step_runtime": step_runtime,
    "step_frontend": step_frontend,
    "step_launcher": step_launcher,
    "step_assemble": step_assemble,
    "step_inno": step_inno,
}

USAGE = """\
Xuan Release 构建脚本
用法:  python build_release.py [steps...]
steps:
  runtime   构造可移植 Python 运行时 -> build/runtime（PyInstaller datas 来源）
  frontend  仅构建前端  pnpm build -> frontend/dist（热更新补丁用，不发 Release）
  launcher  PyInstaller 打包引导器 -> build/dist/Xuan（exe + _internal/venv）
  assemble  组装安装内容 -> build/release/
  inno      Inno Setup 打包安装程序 -> build/out/XuanInstaller_<version>.exe
  all       以上全部（默认）
示例:
  python build_release.py frontend            # 只构建前端生成 dist
  python build_release.py runtime launcher assemble inno  # 增量重打（不改前端）
  python build_release.py                     # 完整 Release
"""


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        args = ["all"]
    if any(a in ("help", "--help", "-h") for a in args):
        print(USAGE)
        sys.exit(0)
    unknown = [a for a in args if a not in STEPS]
    if unknown:
        print(f"未知步骤: {unknown}\n")
        print(USAGE)
        sys.exit(1)
    for which in args:
        for step_name in STEPS[which]:
            _FNS[step_name]()
    log("BUILD_DONE")
