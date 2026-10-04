"""
Xuan Backend - FastAPI 服务入口

以子进程方式启动，由 Electron 主进程管理生命周期。
开发阶段可直接通过 `uvicorn backend.main:app` 运行。
"""
import atexit
import os
import subprocess
import sys
import threading
import traceback
import logging
from datetime import datetime
from pathlib import Path

# 将项目根目录加入 sys.path，以便直接引用现有代码
_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root))

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from backend.runtime.paths import safe_join_path
from backend.api.schemas import HealthResponse

# 逐个导入 API 路由模块并容错：任一模块因依赖缺失（如热更新后缺少新版安装包中的依赖）
# 导入失败时，跳过该模块并记录，保证应用仍能启动（前端界面可显示、检查更新可用）。
import importlib

# (模块名, 路由前缀, 标签)；顺序与原先一致
_API_ROUTERS_SPEC = [
    ("config", "/api/configs", "配置管理"),
    ("tasks", "/api/tasks", "任务管理"),
    ("scheduler", "/api/scheduler", "调度器"),
    ("settings", "/api/settings", "全局设置"),
    ("utils", "/api/utils", "工具"),
    ("validate", "/api/utils", "工具"),
    ("device", "/api/device", "设备"),
    ("resource", "/api/resource", "资源管理"),
    ("ws", "/ws", "WebSocket"),
]

# 各路由模块导入结果（导入失败为 None）
_API_MODULES: dict[str, object] = {}
# 导入失败的模块及原因（供 /api/utils/dependency-check 汇总展示）
_FAILED_API_MODULES: list[str] = []

for _mod_name, _prefix, _tag in _API_ROUTERS_SPEC:
    try:
        _API_MODULES[_mod_name] = importlib.import_module(f"backend.api.{_mod_name}")
    except Exception as _e:
        _API_MODULES[_mod_name] = None
        _FAILED_API_MODULES.append(f"{_mod_name}: {_e}")

# ===== 全局崩溃捕获 =====
# 将未捕获的异常也通过 logging 发送到 WebSocket（而不只是 stderr）
_original_excepthook = sys.excepthook


def _websocket_excepthook(exc_type, exc_value, exc_tb):
    """将未捕获异常通过 logging.error 发送（WebSocketLogHandler 会自动捕获）"""
    tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logging.getLogger("CRASH").error(f"[程序异常退出] 未捕获的异常:\n{tb_text}")
    if _original_excepthook is not None:
        _original_excepthook(exc_type, exc_value, exc_tb)


sys.excepthook = _websocket_excepthook

# 捕获后台线程的未处理异常
_original_thread_excepthook = threading.excepthook if hasattr(threading, 'excepthook') else None


def _websocket_thread_excepthook(args):
    tb_text = "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback))
    logging.getLogger("CRASH").error(f"[程序异常退出] 后台线程异常:\n{tb_text}")
    if _original_thread_excepthook:
        _original_thread_excepthook(args)


if hasattr(threading, 'excepthook'):
    threading.excepthook = _websocket_thread_excepthook

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化，关闭时清理"""
    import asyncio
    from backend.log_setup import setup_backend_logging

    # ---- 启动逻辑 ----
    # 1. 初始化文件日志系统（Main.log 10MB 轮转）
    setup_backend_logging()

    # 1-1. 记录启动横幅（启动时间/客户端版本/Commit/构建时间），
    #      写入 Main.log，并 print 到 stdout（生产环境由 launcher 重定向到 backend.log）
    from backend.runtime_info import build_start_banner
    root_logger = logging.getLogger()
    start_banner = build_start_banner("Xuan Backend")
    root_logger.info("\n" + start_banner)
    print(start_banner, flush=True)

    # 2. 添加 WebSocket 日志推送（全局共享实例，root 与 config logger 共用）
    #    模块导入失败时跳过，不阻塞应用启动（前端界面与检查更新仍可用）
    ws_module = _API_MODULES.get("ws")
    if ws_module is not None:
        try:
            ws_handler = ws_module.get_ws_log_handler()
            ws_handler.setFormatter(logging.Formatter("%(message)s"))
            ws_handler.set_loop(asyncio.get_running_loop())
            ws_handler.setLevel(logging.DEBUG)
            root_logger = logging.getLogger()
            if ws_handler not in root_logger.handlers:
                root_logger.addHandler(ws_handler)
            logging.getLogger("WebSocket").info("WebSocket 日志推送已启动")
        except Exception as e:
            logging.getLogger("WebSocket").warning("WebSocket 日志推送初始化失败: %s", e)
    else:
        logging.getLogger("WebSocket").warning("ws 模块导入失败，跳过 WebSocket 日志推送")

    # 2-1. 把主事件循环注入调度器 API 层：阻塞型端点（start/stop/precheck…）改由
    #      FastAPI 线程池执行后，后台线程推送状态必须用显式注入的 loop，不能再靠
    #      `asyncio.get_event_loop()`（3.12 下工作线程会抛 RuntimeError 并丢推送）。
    scheduler_module = _API_MODULES.get("scheduler")
    bind_loop = getattr(scheduler_module, "bind_main_loop", None)
    if bind_loop is not None:
        try:
            bind_loop(asyncio.get_running_loop())
        except Exception as e:
            logging.getLogger("WebSocket").warning("调度器事件循环注入失败: %s", e)

    # 3. 清理过期日志
    _clean_old_logs()

    yield  # 应用运行期间

    # ---- 关闭逻辑 ----
    # 先停调度器（停任务 → 等连点/任务线程收尾 → 释放设备并清残留触点），
    # 再释放数据库引擎；否则任务线程会被硬杀在连点批次中途，设备端 evdev MT slot
    # 停在按下态（表现为"之后点一下屏幕就同时触发所有预设坐标"）。
    _shutdown_schedulers()
    _dispose_resource_db()
    # 记录退出横幅（退出时间/原因），写入 Main.log 并 print 到 stdout（backend.log）
    from backend.runtime_info import build_exit_banner
    exit_banner = build_exit_banner("Xuan Backend", reason="正常退出")
    logging.getLogger("WebSocket").info("\n" + exit_banner)
    print(exit_banner, flush=True)
    logging.getLogger("WebSocket").info("应用关闭")
    # 程序退出时清理 adb server（issue #4：避免退出后残留 adb 进程）
    _shutdown_adb_server()


def _shutdown_schedulers():
    """停止全部调度器实例，返回未能正常收尾的 config_id 列表。

    兜底逻辑：launcher 关窗口时用 terminate 强杀后端，此处仅在优雅退出时生效。
    """
    sched_module = _API_MODULES.get("scheduler")
    shutdown = getattr(sched_module, "shutdown_all_schedulers", None)
    if shutdown is None:
        return []
    try:
        failed = shutdown()
        if failed:
            logging.getLogger("Shutdown").warning("未完成收尾的调度器: %s", failed)
        return failed
    except Exception as e:
        logging.getLogger("Shutdown").warning("停止调度器失败: %s", e, exc_info=e)
        return []


def _dispose_resource_db():
    """释放资源库 SQLAlchemy 引擎（否则热更新覆盖 src/database.db 时文件被占用）。

    过去这刀是在热更新流程里手工补的（见 api/utils.py 的 ResourceDBManager.engine
    释放），说明生命周期缺少统一出口。
    """
    try:
        from backend.tools.resource_db import ResourceDBManager
        engine = getattr(ResourceDBManager, "engine", None)
        if engine is not None:
            engine.dispose()
            logging.getLogger("Shutdown").info("资源库数据库引擎已释放")
    except Exception as e:
        logging.getLogger("Shutdown").warning("释放资源库引擎失败: %s", e)



def _shutdown_adb_server():
    """程序退出时停止全局 adb server，避免退出后残留 adb 进程（issue #4）。

    兜底逻辑：launcher 关闭窗口时用 terminate 强杀后端，atexit/lifespan
    仅在优雅退出时触发；主清理已由 launcher.stop_adb_server() 承担。
    清理失败不阻塞退出，但记录日志供排查。

    例外：`XUAN_SKIP_ADB_CLEANUP=1` 时跳过。用途是**测试/工具/临时实例**——
    它们退出时不应该杀掉用户正在运行的那个实例所依赖的 adb server
    （本会话的端到端冒烟就踩到过：临时实例退出把 adb server 带走了）。
    """
    if os.environ.get("XUAN_SKIP_ADB_CLEANUP"):
        logging.getLogger("Shutdown").info(
            "已按 XUAN_SKIP_ADB_CLEANUP 跳过 adb server 清理")
        return
    try:
        result = subprocess.run(
            ["adb", "kill-server"], capture_output=True, text=True, timeout=15,
            encoding="utf-8", errors="ignore",
        )
        if result.returncode == 0:
            logging.getLogger("Shutdown").info("adb server 已停止（adb kill-server）")
        else:
            logging.getLogger("Shutdown").warning(
                "adb kill-server 返回非零（%s）：%s", result.returncode,
                (result.stdout + result.stderr).strip()[:300],
            )
    except FileNotFoundError:
        logging.getLogger("Shutdown").info("未找到 adb，跳过 adb server 清理")
    except Exception as e:
        logging.getLogger("Shutdown").warning("adb kill-server 执行异常: %s", e)


# 进程退出兜底清理（覆盖开发模式等 launcher 不参与的场景）
atexit.register(_shutdown_adb_server)


app = FastAPI(
    title="Xuan Backend",
    version="2.0.0",
    description="火影忍者日常助手 - 后端 API 服务",
    lifespan=lifespan,
)

# ===== 全局 API 异常日志 =====
# 此前 API 中 raise 的 HTTPException / 未处理异常只返回 JSON 给前端、不落日志，
# 排查用户前端交互导致的错误时需要从日志回查，因此在此统一记录
# （含请求方法 / 路径 / 状态码 / 详情，按级别区分 4xx 与 5xx）。
_api_logger = logging.getLogger("API")


@app.exception_handler(StarletteHTTPException)
async def _api_http_exception_handler(request: Request, exc: StarletteHTTPException):
    # 仅记录 API/WebSocket 路径（前端交互产生）；静态资源 404 由 SPA 回退中间件接管，避免刷屏
    path = request.url.path
    if path.startswith("/api/") or path.startswith("/ws/"):
        if exc.status_code >= 500:
            _api_logger.error("API 错误: %s %s -> %d %s", request.method, path, exc.status_code, exc.detail)
        else:
            _api_logger.warning("API 错误: %s %s -> %d %s", request.method, path, exc.status_code, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def _api_validation_exception_handler(request: Request, exc: RequestValidationError):
    # 前端发送非法请求体/参数时 FastAPI 返回 422，默认同样不落日志
    _api_logger.warning("API 参数校验失败: %s %s -> %s", request.method, request.url.path, exc.errors())
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def _api_unhandled_exception_handler(request: Request, exc: Exception):
    # 端点未捕获异常：默认只由 uvicorn 写入 backend.log，这里补写 Main.log（含完整 traceback）
    _api_logger.error("API 未处理异常: %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": f"服务器内部错误: {exc}"})


def _clean_old_logs():
    """清理 log/ 下每个用户目录中超过 3 天的日期文件夹"""
    import shutil
    from datetime import timedelta
    from backend.utils import get_real_path

    log_root = Path(get_real_path("log"))
    if not log_root.exists():
        return

    now = datetime.now()
    cutoff = now - timedelta(days=3)
    removed = 0

    for user_dir in log_root.iterdir():
        if not user_dir.is_dir():
            continue
        for date_dir in user_dir.iterdir():
            if not date_dir.is_dir():
                continue
            # 尝试将目录名解析为日期
            try:
                dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
                if dir_date.date() < cutoff.date():
                    shutil.rmtree(date_dir, ignore_errors=True)
                    removed += 1
            except (ValueError, OSError):
                continue

    if removed:
        logging.getLogger("WebSocket").info(f"已清理 {removed} 个过期日志目录")

class JsSafeStaticFiles(StaticFiles):
    """StaticFiles 子类：强制 .js/.mjs/.cjs 返回 JavaScript MIME。

    背景：Windows 上 Python mimetypes 依赖注册表（HKCR\\.js 的 Content Type），
    部分机器将 .js 映射为 text/plain 或缺失，导致 starlette 返回 text/plain；
    而浏览器对 ES module（<script type="module">）强制要求 JavaScript MIME，
    否则拒绝执行，表现为页面白屏且不发起任何 JS/API 请求。
    """

    _JS_SUFFIXES = (".js", ".mjs", ".cjs")

    def file_response(self, full_path, stat_result, scope, status_code=200):
        response = super().file_response(full_path, stat_result, scope, status_code)
        path = str(full_path)
        if status_code == 200 and path.lower().endswith(self._JS_SUFFIXES):
            response.headers["content-type"] = "application/javascript; charset=utf-8"
        return response


# CORS - 仅放行本地开发服务器（Vite dev server 直连场景）。
# 生产由同一后端托管 SPA（同源），dev 走 vite proxy（同源），**都不需要 CORS**；
# 旧实现的 `allow_origins=["*"] + allow_credentials=True` 会被 starlette 回显任意
# Origin（实测 cors.py: "if allow_all_origins and allow_credentials: allow_explicit_origin"），
# 等于"任何网站都能调用本地 127.0.0.1:4199 的写接口"（apply-update / 删配置 / 启停调度器 /
# os.startfile 打开日志目录），WebSocket 还完全不受 CORS 约束。这里改为显式白名单。
_DEV_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4199",
    "http://127.0.0.1:4199",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_DEV_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 注册路由（导入失败的模块自动跳过，保证其余接口可用）
for _mod_name, _prefix, _tag in _API_ROUTERS_SPEC:
    _mod = _API_MODULES.get(_mod_name)
    if _mod is not None and getattr(_mod, "router", None) is not None:
        app.include_router(_mod.router, prefix=_prefix, tags=[_tag])
    elif _mod is not None:
        logging.getLogger("WebSocket").warning("模块 %s 导入成功但缺少 router，跳过注册", _mod_name)

# 生产环境：托管前端静态文件（使用中间件处理 SPA 回退，不拦截 API）
frontend_dist = _project_root / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", JsSafeStaticFiles(directory=frontend_dist / "assets"), name="assets")

    class SPAMiddleware(BaseHTTPMiddleware):
        """SPA 回退中间件 - 仅在无路由匹配时返回 index.html。
        中间件在所有路由之后执行，因此不会拦截 API 请求。"""

        async def dispatch(self, request: Request, call_next):
            response = await call_next(request)
            # 只有 GET/HEAD 请求且不是 API/WebSocket 路径且返回 404 时才回退到 SPA
            if (request.method in ("GET", "HEAD")
                    and response.status_code == 404
                    and not request.url.path.startswith("/api/")
                    and not request.url.path.startswith("/ws/")):
                # 路径穿越防护：`request.url.path` 已由 ASGI 层百分号解码，
                # 旧实现直接 `frontend_dist / path.lstrip("/")` → `/..%2f..%2fsetting.ini`
                # 可读到 dist 之外（含 GithubPAT 的 setting.ini、config/*.json、
                # src/database.db）。safe_join_path 越界时返回 None。
                file_path = safe_join_path(frontend_dist, request.url.path)
                if file_path is not None and file_path.is_file():
                    return FileResponse(file_path)
                return FileResponse(frontend_dist / "index.html")
            return response

    app.add_middleware(SPAMiddleware)


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": "2.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=4199, reload=True)