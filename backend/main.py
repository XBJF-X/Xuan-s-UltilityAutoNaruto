"""
Xuan Backend - FastAPI 服务入口

以子进程方式启动，由 Electron 主进程管理生命周期。
开发阶段可直接通过 `uvicorn backend.main:app` 运行。
"""
import os
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
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.api import config, tasks, scheduler, settings as api_settings, ws, utils as api_utils, device as api_device, validate, resource

# ===== 全局崩溃捕获 =====
# 将未捕获的异常也通过 logging 发送到 WebSocket（而不只是 stderr）
_original_excepthook = sys.excepthook


def _websocket_excepthook(exc_type, exc_value, exc_tb):
    """将未捕获异常通过 logging.error 发送（WebSocketLogHandler 会自动捕获）"""
    tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logging.getLogger("CRASH").error(f"未捕获的异常:\n{tb_text}")
    if _original_excepthook is not None:
        _original_excepthook(exc_type, exc_value, exc_tb)


sys.excepthook = _websocket_excepthook

# 捕获后台线程的未处理异常
_original_thread_excepthook = threading.excepthook if hasattr(threading, 'excepthook') else None


def _websocket_thread_excepthook(args):
    tb_text = "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback))
    logging.getLogger("CRASH").error(f"后台线程异常:\n{tb_text}")
    if _original_thread_excepthook:
        _original_thread_excepthook(args)


if hasattr(threading, 'excepthook'):
    threading.excepthook = _websocket_thread_excepthook

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化，关闭时清理"""
    import asyncio
    from backend.api.ws import get_ws_log_handler
    from backend.log_setup import setup_backend_logging

    # ---- 启动逻辑 ----
    # 1. 初始化文件日志系统（Main.log 10MB 轮转）
    setup_backend_logging()

    # 2. 添加 WebSocket 日志推送（全局共享实例，root 与 config logger 共用）
    ws_handler = get_ws_log_handler()
    ws_handler.setFormatter(logging.Formatter("%(message)s"))
    ws_handler.set_loop(asyncio.get_event_loop())
    ws_handler.setLevel(logging.DEBUG)
    root_logger = logging.getLogger()
    if ws_handler not in root_logger.handlers:
        root_logger.addHandler(ws_handler)

    logging.getLogger("WebSocket").info("WebSocket 日志推送已启动")

    # 3. 清理过期日志
    _clean_old_logs()

    yield  # 应用运行期间

    # ---- 关闭逻辑 ----
    logging.getLogger("WebSocket").info("应用关闭")


app = FastAPI(
    title="Xuan Backend",
    version="2.0.0",
    description="火影忍者日常助手 - 后端 API 服务",
    lifespan=lifespan,
)


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


# CORS - 允许前端 localhost 开发服务器
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段放开，生产环境限定 localhost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(config.router, prefix="/api/configs", tags=["配置管理"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["任务管理"])
app.include_router(scheduler.router, prefix="/api/scheduler", tags=["调度器"])
app.include_router(api_settings.router, prefix="/api/settings", tags=["全局设置"])
app.include_router(api_utils.router, prefix="/api/utils", tags=["工具"])
app.include_router(validate.router, prefix="/api/utils", tags=["工具"])
app.include_router(api_device.router, prefix="/api/device", tags=["设备"])
app.include_router(resource.router, prefix="/api/resource", tags=["资源管理"])
app.include_router(ws.router, prefix="/ws", tags=["WebSocket"])

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
                file_path = frontend_dist / request.url.path.lstrip("/")
                if file_path.exists() and file_path.is_file():
                    return FileResponse(file_path)
                return FileResponse(frontend_dist / "index.html")
            return response

    app.add_middleware(SPAMiddleware)


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": "2.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=4199, reload=True)