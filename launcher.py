"""
Xuan 引导器（Release 打包入口）

职责：
  1. 以后台隐藏进程方式启动 Python 后端（uvicorn，127.0.0.1:4199）
  2. 等待端口就绪
  3. 用 pywebview（Windows 走 WebView2）打开桌面窗口加载后端托管的 SPA
  4. 关闭窗口时结束后端进程

打包说明：
  - PyInstaller onedir 仅打包本文件 + Python 解释器 + 运行时依赖（不打包项目代码）
  - 项目代码（backend/frontend/src 等）以源码形式放在安装目录，支持热更新
  - 打包时需将 python.exe 复制进 _internal/，由本引导器用其运行外部后端源码

用法：
  python launcher.py            # 正常启动（后端 + WebView 窗口）
  python launcher.py --selftest # 无窗口自检：启动后端 → 等端口 → 退出（构建验证用）
"""
import logging
import os
import socket
import subprocess
import sys
import threading
import time

BACKEND_PORT = 4199
BACKEND_TIMEOUT = 60

LOG = logging.getLogger("Launcher")


def _setup_logging(log_path: str):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler(log_path, encoding="utf-8")],
    )


def get_base_dir() -> str:
    """运行根目录：打包后为 exe 所在目录；开发模式为项目根。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_python_and_internal(base_dir: str):
    """返回 (python 可执行文件, site-packages 路径)。

    打包模式：使用随安装包分发的内置 Python 环境（base_dir/venv）；
    兜底：冻结环境自身（仅打包错误时，无法运行外部源码）。
    """
    if getattr(sys, "frozen", False):
        venv_py = os.path.join(base_dir, "venv", "Scripts", "python.exe")
        if os.path.exists(venv_py):
            return venv_py, os.path.join(base_dir, "venv", "Lib", "site-packages")
        internal = os.path.join(base_dir, "_internal")
        return sys.executable, internal
    return sys.executable, os.path.dirname(sys.executable)


def wait_port(port: int, timeout: float = BACKEND_TIMEOUT) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def start_backend(base_dir: str, py_exe: str, internal: str):
    """隐藏窗口启动后端子进程（外部 python 解释器运行源码，代码可热更新）。"""
    env = dict(os.environ)
    paths = [base_dir]
    if internal and os.path.isdir(internal):
        paths.append(internal)
    env["PYTHONPATH"] = os.pathsep.join(paths)
    flags = 0
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        flags |= getattr(subprocess, "CREATE_NO_WINDOW")
    LOG.info("启动后端: %s -m uvicorn backend.main:app (cwd=%s)", py_exe, base_dir)
    return subprocess.Popen(
        [py_exe, "-m", "uvicorn", "backend.main:app",
         "--host", "127.0.0.1", "--port", str(BACKEND_PORT)],
        cwd=base_dir,
        env=env,
        creationflags=flags,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _schedule_autoclose(window, seconds: int):
    """测试/演示用：N 秒后自动关闭窗口（正常使用不传 --autoclose）。"""
    if seconds and seconds > 0:
        def _closer():
            time.sleep(seconds)
            try:
                window.destroy()
            except Exception:
                pass
        threading.Thread(target=_closer, daemon=True).start()


def _run(show_window: bool, autoclose: int = 0) -> int:
    base_dir = get_base_dir()
    log_dir = os.path.join(base_dir, "log")
    os.makedirs(log_dir, exist_ok=True)
    _setup_logging(os.path.join(log_dir, "launcher.log"))

    py_exe, internal = get_python_and_internal(base_dir)
    LOG.info("base_dir=%s python=%s", base_dir, py_exe)

    proc = start_backend(base_dir, py_exe, internal)
    if not wait_port(BACKEND_PORT, timeout=BACKEND_TIMEOUT):
        LOG.error("后端在 %s 秒内未能就绪", BACKEND_TIMEOUT)
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        return 1
    LOG.info("后端已就绪 http://127.0.0.1:%d", BACKEND_PORT)

    if not show_window:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        LOG.info("自检完成")
        return 0

    import webview

    window = webview.create_window(
        "Xuan 火影忍者日常助手",
        f"http://127.0.0.1:{BACKEND_PORT}",
        width=1300,
        height=600,
        min_size=(900, 500),
    )
    _schedule_autoclose(window, autoclose)
    webview.start()

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    LOG.info("已退出")
    return 0


def main():
    args = sys.argv[1:]
    autoclose = 0
    for i, a in enumerate(args):
        if a == "--autoclose" and i + 1 < len(args):
            try:
                autoclose = int(args[i + 1])
            except ValueError:
                pass
    return _run(show_window="--selftest" not in args, autoclose=autoclose)


if __name__ == "__main__":
    sys.exit(main())
