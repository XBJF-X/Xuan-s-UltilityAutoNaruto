"""
Xuan Backend - FastAPI 服务入口

以子进程方式启动，由 Electron 主进程管理生命周期。
开发阶段可直接通过 `uvicorn backend.main:app` 运行。
"""
import os
import sys
from pathlib import Path

# 将项目根目录加入 sys.path，以便直接引用现有代码
_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import config, scenes, elements, tasks, scheduler, recognize, ws

app = FastAPI(
    title="Xuan Backend",
    version="2.0.0",
    description="火影忍者日常助手 - 后端 API 服务",
)

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
app.include_router(scenes.router, prefix="/api/scenes", tags=["场景管理"])
app.include_router(elements.router, prefix="/api/elements", tags=["元素管理"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["任务管理"])
app.include_router(scheduler.router, prefix="/api/scheduler", tags=["调度器"])
app.include_router(recognize.router, prefix="/api", tags=["场景识别"])
app.include_router(ws.router, prefix="/ws", tags=["WebSocket"])


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": "2.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=4199, reload=True)