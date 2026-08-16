"""
Xuan 引导器（Release 打包入口）

职责：
  1. 单实例检查，杀死旧进程
  2. 以后台隐藏进程方式启动 Python 后端（uvicorn，自动选择空闲端口）
  3. 等待端口就绪
  4. 用 pywebview（Windows 走 WebView2）打开桌面窗口加载后端托管的 SPA
  5. 关闭窗口时结束后端进程

打包说明：
  - PyInstaller onedir 仅打包本文件 + Python 解释器 + 运行时依赖（不打包项目代码）
  - 项目代码（backend/frontend/src 等）以源码形式放在安装目录，支持热更新
  - 打包时需将 python.exe 复制进 _internal/，由本引导器用其运行外部后端源码

用法：
  python launcher.py            # 正常启动（后端 + WebView 窗口）
  python launcher.py --selftest # 无窗口自检：启动后端 → 等端口 → 退出（构建验证用）
"""
import json
import logging
import os
import socket
import subprocess
import sys
import threading
import time
import signal

DEFAULT_PORT = 4199
BACKEND_TIMEOUT = 60
MAX_PORT_ATTEMPTS = 10

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

    打包模式：使用 PyInstaller 打进 _internal/venv 的可移植 Python 环境
    （python.exe 与 python312.dll、Lib、DLLs 同目录，python312._pth 以相对
    路径指定 sys.path，无构建机硬编码，换电脑仍可运行）；
    兜底：冻结环境自身（仅打包错误时，无法运行外部源码）。
    """
    if getattr(sys, "frozen", False):
        internal = getattr(sys, "_MEIPASS", None) or os.path.join(base_dir, "_internal")
        venv_py = os.path.join(internal, "venv", "python.exe")
        if os.path.exists(venv_py):
            return venv_py, os.path.join(internal, "venv", "Lib", "site-packages")
        return sys.executable, internal
    return sys.executable, os.path.dirname(sys.executable)


def wait_port(port: int, timeout: float = BACKEND_TIMEOUT, proc: subprocess.Popen | None = None) -> bool:
    """等待端口就绪；若传入后端进程 proc，其提前退出时立即返回失败，避免干等满超时。"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc is not None and proc.poll() is not None:
            LOG.error("后端进程提前退出 (returncode=%s)", proc.poll())
            return False
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def find_available_port(start_port: int, max_attempts: int = MAX_PORT_ATTEMPTS) -> int | None:
    """从 start_port 开始查找第一个未被占用的端口，最多尝试 max_attempts 个。"""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:  # 端口空闲
                return port
    return None


def check_dependencies(py_exe: str, base_dir: str, internal: str) -> bool:
    """检查 Python 环境中是否包含运行后端所需的依赖。"""
    env = dict(os.environ)
    paths = [base_dir]
    if internal and os.path.isdir(internal):
        paths.append(internal)
    env["PYTHONPATH"] = os.pathsep.join(paths)

    check_cmd = [
        py_exe, "-c",
        "import uvicorn, fastapi; print('OK')"
    ]
    try:
        result = subprocess.run(
            check_cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
        )
        if result.returncode == 0 and "OK" in result.stdout:
            LOG.info("依赖检查通过 (uvicorn + fastapi)")
            return True
        else:
            LOG.error("依赖检查失败，返回码=%d, stderr=%s", result.returncode, result.stderr.strip())
            return False
    except Exception as e:
        LOG.error("依赖检查异常: %s", e)
        return False


def kill_process(pid: int):
    """强制终止指定 PID 的进程树（Windows 用 /T 连带子进程，避免 uvicorn 残留）。"""
    try:
        if sys.platform == "win32":
            # /T 结束整个进程树：旧实例启动的 uvicorn 后端子进程一并终止
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)],
                           check=False, capture_output=True)
        else:
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.3)
            # 如果还在，强制 kill
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    except Exception as e:
        LOG.warning("终止进程 %d 失败: %s", pid, e)


def _tasklist_image(pid: int) -> str | None:
    """返回 Windows 下 PID 对应的进程映像名；进程不存在或查询失败返回 None。"""
    if sys.platform != "win32" or pid <= 0:
        return None
    try:
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        r = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=10, creationflags=flags,
        )
        for line in r.stdout.splitlines():
            parts = line.strip().strip('"').split('","')
            if len(parts) >= 2 and parts[1].strip() == str(pid):
                return parts[0].strip()
        return None
    except Exception:
        return None


def _pid_is_alive(pid: int) -> bool:
    """判断进程是否存在（跨平台）。"""
    if pid <= 0:
        return False
    if sys.platform == "win32":
        return _tasklist_image(pid) is not None
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _find_listener_pid(port: int) -> int | None:
    """返回监听 127.0.0.1:<port> 的进程 PID；无监听或出错返回 None。"""
    try:
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        r = subprocess.run(
            ["netstat", "-ano", "-p", "tcp"],
            capture_output=True, text=True, timeout=15, creationflags=flags,
        )
        needle = f"127.0.0.1:{port}"
        for line in r.stdout.splitlines():
            if "LISTENING" in line and needle in line:
                parts = line.split()
                if parts:
                    try:
                        return int(parts[-1])
                    except ValueError:
                        return None
        return None
    except Exception:
        return None


def _ensure_default_port_free():
    """清理占用默认端口的残留后端进程（launcher 崩溃后 uvicorn 孤儿），避免新实例端口漂移。"""
    listener = _find_listener_pid(DEFAULT_PORT)
    if listener is None:
        return
    image = _tasklist_image(listener) if sys.platform == "win32" else None
    if image is not None and image.lower() in ("python.exe", "pythonw.exe"):
        LOG.info("端口 %d 被残留后端占用 (PID=%d, %s)，正在终止...", DEFAULT_PORT, listener, image)
        kill_process(listener)
        time.sleep(0.5)
    else:
        LOG.warning("端口 %d 被其他程序占用 (PID=%d, %s)，本实例将改用空闲端口",
                    DEFAULT_PORT, listener, image or "?")


def _remove_pid_file(base_dir: str):
    """尽力删除 pid 文件（失败不报错，例如目录只读）。"""
    try:
        os.remove(os.path.join(base_dir, "xuan.pid"))
    except OSError:
        pass


def _ask_close_old_instance(old_pid: int, image: str | None) -> bool:
    """tk 弹窗询问：软件已在运行，是否关闭上一个进程后继续启动。

    返回 True = 关闭旧进程并继续；False = 用户选择退出（非交互环境默认关闭旧进程继续）。
    """
    try:
        import tkinter as tk
    except Exception:
        LOG.warning("无法创建提示窗口（缺少 tkinter），默认关闭旧进程继续")
        return True

    root = tk.Tk()
    root.title("Xuan - 软件已在运行")
    root.resizable(False, False)
    # 屏幕居中
    root.update_idletasks()
    w, h = 460, 180
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    result = {"kill": False}
    extra = f"，进程 PID={old_pid}" + (f"（{image}）" if image else "")

    tk.Label(
        root,
        text="软件已在运行" + extra,
        wraplength=420, justify="left",
        font=("Microsoft YaHei", 11, "bold"),
    ).pack(pady=(18, 4))
    tk.Label(
        root,
        text="如需重新启动，请先关闭上一个进程，或点击下方按钮关闭。",
        wraplength=420, justify="left",
        font=("Microsoft YaHei", 9),
    ).pack(pady=(0, 12))

    def _do_kill():
        result["kill"] = True
        root.destroy()

    def _do_exit():
        result["kill"] = False
        root.destroy()

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=12)
    tk.Button(btn_frame, text="关闭上一个进程", width=18, font=("Microsoft YaHei", 10),
              command=_do_kill).pack(side="left", padx=10)
    tk.Button(btn_frame, text="退出", width=10, font=("Microsoft YaHei", 10),
              command=_do_exit).pack(side="left", padx=10)

    root.protocol("WM_DELETE_WINDOW", _do_exit)  # 点窗口关闭视为退出
    root.mainloop()
    return result["kill"]


def ensure_single_instance(base_dir: str, interactive: bool = True):
    """检查并清理旧的 XUAN 进程，保证单实例运行。

    interactive=True：发现旧进程时用 tk 弹窗询问用户——关闭上一个进程后继续 / 退出；
    interactive=False（如 --selftest）：保持原有自动清理行为，不弹窗。

    两条防线：
      1. pid 文件记录的旧启动器进程（校验映像名，避免 PID 复用误杀其他程序）
      2. 默认端口被残留后端（python 进程）占用时清理，保证端口不漂移
    """
    pid_file = os.path.join(base_dir, "xuan.pid")
    if os.path.exists(pid_file):
        old_pid = None
        try:
            with open(pid_file, "r") as f:
                old_pid = int(f.read().strip())
        except (ValueError, OSError) as e:
            LOG.warning("pid 文件内容无效，将忽略: %s", e)
        if old_pid is not None and _pid_is_alive(old_pid):
            image = _tasklist_image(old_pid) if sys.platform == "win32" else None
            if image is None or "xuan" in image.lower():
                LOG.info("发现旧的 XUAN 进程 (PID=%d%s)...",
                         old_pid, f", {image}" if image else "")
                kill = True
                if interactive:
                    LOG.info("等待用户确认是否关闭旧进程 ...")
                    kill = _ask_close_old_instance(old_pid, image)
                if kill:
                    LOG.info("正在终止旧进程 (PID=%d) ...", old_pid)
                    kill_process(old_pid)
                    time.sleep(0.5)  # 等待进程完全退出
                else:
                    LOG.info("用户选择退出，程序退出")
                    _remove_pid_file(base_dir)
                    sys.exit(0)
            else:
                LOG.warning("PID %d 已被其他程序占用（%s），跳过终止", old_pid, image)
        _remove_pid_file(base_dir)
    # 端口占用兜底：清理残留的 uvicorn 孤儿进程（launcher 崩溃时 pid 文件无法记录）
    _ensure_default_port_free()
    # 写入当前进程 PID（失败不阻塞启动，例如安装在只读目录）
    try:
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))
    except OSError as e:
        LOG.warning("无法写入 pid 文件 %s: %s", pid_file, e)
    LOG.info("当前进程 PID=%d", os.getpid())


def start_backend(base_dir: str, py_exe: str, internal: str, log_dir: str):
    """隐藏窗口启动后端子进程，自动选择空闲端口，将 stdout/stderr 重定向到日志文件。"""
    used_port = find_available_port(DEFAULT_PORT)
    if used_port is None:
        LOG.error("无法找到可用端口 (从 %d 起尝试了 %d 个)", DEFAULT_PORT, MAX_PORT_ATTEMPTS)
        return None, None, None

    env = dict(os.environ)
    paths = [base_dir]
    if internal and os.path.isdir(internal):
        paths.append(internal)
    env["PYTHONPATH"] = os.pathsep.join(paths)

    flags = 0
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        flags |= getattr(subprocess, "CREATE_NO_WINDOW")

    backend_log = os.path.join(log_dir, "backend.log")
    log_file = open(backend_log, "w", encoding="utf-8", buffering=1)

    LOG.info("启动后端: %s -m uvicorn backend.main:app --port %d (cwd=%s)", py_exe, used_port, base_dir)
    proc = subprocess.Popen(
        [py_exe, "-m", "uvicorn", "backend.main:app",
         "--host", "127.0.0.1", "--port", str(used_port)],
        cwd=base_dir,
        env=env,
        creationflags=flags,
        stdout=log_file,
        stderr=log_file,
    )
    return proc, log_file, used_port


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


def _remove_restart_request(base_dir: str):
    """删除重启请求文件（log/restart_request.json）。"""
    try:
        req_path = os.path.join(base_dir, "log", "restart_request.json")
        if os.path.exists(req_path):
            os.remove(req_path)
            LOG.info("已移除重启请求文件")
    except Exception as e:
        LOG.warning("移除重启请求文件失败: %s", e)


def _relaunch_cmd(base_dir: str) -> list:
    """返回重启当前程序的命令：打包模式启动 Xuan.exe；开发模式重新运行 launcher.py。"""
    if getattr(sys, "frozen", False):
        return [os.path.join(base_dir, "Xuan.exe")]
    return [sys.executable, os.path.join(base_dir, "launcher.py")]


def stop_adb_server():
    """程序退出时停止全局 adb server，避免退出后残留 adb 进程（issue #4）。

    仅在程序使用过 adb（uiautomator2 / adb devices 等）时才有意义；
    清理失败不影响程序退出，但会记录日志供排查。
    """
    try:
        result = subprocess.run(
            ["adb", "kill-server"], capture_output=True, text=True, timeout=15,
            encoding="utf-8", errors="ignore",
        )
        if result.returncode == 0:
            LOG.info("adb server 已停止（adb kill-server）")
        else:
            LOG.warning(
                "adb kill-server 返回非零（%s）：%s", result.returncode,
                (result.stdout + result.stderr).strip()[:300],
            )
    except FileNotFoundError:
        LOG.info("未找到 adb，跳过 adb server 清理")
    except subprocess.TimeoutExpired:
        LOG.warning("adb kill-server 执行超时，可能仍有 adb 进程残留")
    except Exception as e:
        LOG.warning("adb kill-server 执行异常: %s", e)


def _poll_restart_request(window, base_dir: str, pending_restart: dict):
    """后台线程轮询 log/restart_request.json，检测到更新重启请求后关闭窗口。"""
    req_path = os.path.join(base_dir, "log", "restart_request.json")
    while True:
        try:
            if os.path.exists(req_path):
                with open(req_path, "r", encoding="utf-8") as f:
                    req = json.load(f)
                if req and req.get("mode") in ("hot", "full"):
                    LOG.info("检测到更新重启请求: %s", req)
                    pending_restart.update(req)
                    try:
                        window.destroy()
                    except Exception as e:
                        LOG.warning("关闭窗口失败: %s", e)
                    return
        except Exception:
            pass
        time.sleep(1)


def _run(show_window: bool, autoclose: int = 0) -> int:
    base_dir = get_base_dir()
    log_dir = os.path.join(base_dir, "log")
    os.makedirs(log_dir, exist_ok=True)
    _setup_logging(os.path.join(log_dir, "launcher.log"))

    # 单实例检测（必须在日志初始化之后，但要在其他操作之前）
    # 交互模式（有窗口）检测到旧进程时弹窗询问；--selftest 不弹窗，自动清理旧进程
    ensure_single_instance(base_dir, interactive=show_window)

    py_exe, internal = get_python_and_internal(base_dir)
    LOG.info("base_dir=%s python=%s", base_dir, py_exe)

    # 依赖检查
    if not check_dependencies(py_exe, base_dir, internal):
        LOG.error("Python 环境缺少必要依赖 (uvicorn / fastapi)，请确保已安装或打包正确。")
        _remove_pid_file(base_dir)
        return 1

    # 启动后端
    proc, log_file, used_port = start_backend(base_dir, py_exe, internal, log_dir)
    if proc is None:
        _remove_pid_file(base_dir)
        return 1

    # 等待端口就绪（后端进程提前退出时立即失败，避免干等满超时）
    if not wait_port(used_port, timeout=BACKEND_TIMEOUT, proc=proc):
        LOG.error("后端在 %s 秒内未能就绪 (端口 %d)，请查看 %s 获取详细错误",
                  BACKEND_TIMEOUT, used_port, os.path.join(log_dir, "backend.log"))
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        log_file.close()
        _remove_pid_file(base_dir)
        return 1

    LOG.info("后端已就绪 http://127.0.0.1:%d", used_port)

    if not show_window:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        log_file.close()
        _remove_pid_file(base_dir)
        # 自检也可能触发 adb server 启动（如 /serial-list），退出前统一清理
        stop_adb_server()
        LOG.info("自检完成")
        return 0

    # 正常模式：启动 WebView 窗口
    import webview

    window = webview.create_window(
        "Xuan 火影忍者日常助手",
        f"http://127.0.0.1:{used_port}",
        width=1300,
        height=600,
        min_size=(900, 500),
    )
    _schedule_autoclose(window, autoclose)

    # 后台轮询重启请求（更新完成后程序自动重启，无需用户手动操作）
    pending_restart: dict = {}
    threading.Thread(
        target=_poll_restart_request, args=(window, base_dir, pending_restart), daemon=True
    ).start()
    webview.start()

    # 窗口关闭后清理后端
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    log_file.close()
    _remove_pid_file(base_dir)

    # 程序退出时清理 adb server（issue #4：避免退出后残留 adb 进程）
    stop_adb_server()

    # 处理更新后的自动重启
    mode = pending_restart.get("mode")
    if mode:
        _remove_restart_request(base_dir)
        if mode == "hot":
            LOG.info("热更新完成，自动重启程序 ...")
            subprocess.Popen(_relaunch_cmd(base_dir))
        elif mode == "full":
            installer = pending_restart.get("installer")
            if installer and os.path.exists(installer):
                LOG.info("大更新：启动安装器静默安装并重启：%s", installer)
                # Inno Setup 静默参数（替代 NSIS /S）：/VERYSILENT 无界面、/SUPPRESSMSGBOXES
                # 抑制对话框、/NORESTART 不重启；/AUTOSTART 为自定义参数，安装完成后自动启动 Xuan
                subprocess.Popen([installer, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/AUTOSTART"])
            else:
                LOG.error("大更新安装包缺失，跳过自动重启（%s）", installer)
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