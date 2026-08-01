"""调度器管理 API 路由 - 延迟初始化，接入 WebSocket 状态推送"""
import asyncio
from fastapi import APIRouter, HTTPException
from backend.services.config_service import shared_config_service as _config_service

router = APIRouter()
_schedulers: dict[str, object] = {}

# 存储主线程事件循环引用（用于后台线程安全地推送异步事件）
_main_loop: asyncio.AbstractEventLoop | None = None


def _get_main_loop() -> asyncio.AbstractEventLoop:
    global _main_loop
    if _main_loop is None or _main_loop.is_closed():
        _main_loop = asyncio.get_event_loop()
    return _main_loop


def _get_scheduler(config_id: str):
    if config_id not in _schedulers:
        from backend.services.scheduler_service import SchedulerService
        from backend.core.scene_graph import SceneGraph
        from backend.tools.resource_db import ResourceDBManager
        from backend.api.ws import manager
        from pathlib import Path
        from backend.utils import get_real_path

        cfg = _config_service.get_config(config_id)
        if not cfg:
            raise HTTPException(status_code=404, detail="配置不存在")
        db = ResourceDBManager(Path(get_real_path("src")))
        sg = SceneGraph(db)

        # 状态变更回调：通过 WebSocket 推送（线程安全版）
        async def on_status_change(status: dict):
            status["config_id"] = config_id
            await manager.broadcast_status(status)

        async def on_task_state_change(task_data: dict):
            task_data["config_id"] = config_id
            await manager.broadcast_task_state(task_data)

        def sync_on_status(status: dict):
            loop = _get_main_loop()
            asyncio.run_coroutine_threadsafe(
                on_status_change(status), loop
            )

        def sync_on_task(task_data: dict):
            loop = _get_main_loop()
            asyncio.run_coroutine_threadsafe(
                on_task_state_change(task_data), loop
            )

        _schedulers[config_id] = SchedulerService(
            cfg, sg,
            on_status_change=sync_on_status,
            on_task_state_change=sync_on_task,
        )
    return _schedulers[config_id]


@router.post("/start/{config_id}")
async def start_scheduler(config_id: str):
    sched = _get_scheduler(config_id)
    ok = sched.start()
    if not ok:
        raise HTTPException(status_code=400, detail="启动失败，请检查设备连接")
    return {"ok": True}


@router.post("/stop/{config_id}")
async def stop_scheduler(config_id: str):
    sched = _get_scheduler(config_id)
    sched.stop()
    return {"ok": True}


@router.get("/status/{config_id}")
async def get_scheduler_status(config_id: str):
    sched = _get_scheduler(config_id)
    return sched.get_status()


@router.get("/tasks/{config_id}")
async def get_tasks(config_id: str):
    sched = _get_scheduler(config_id)
    if not sched.running:
        return []
    return sched.get_tasks_status()


@router.post("/tasks/{config_id}/{task_name}/execute")
async def execute_task(config_id: str, task_name: str):
    sched = _get_scheduler(config_id)
    sched.execute_task_now(task_name)
    return {"ok": True}


@router.put("/tasks/{config_id}/{task_name}/activation")
async def toggle_task_activation(config_id: str, task_name: str, state: bool):
    sched = _get_scheduler(config_id)
    sched.toggle_task_activation(task_name, state)
    return {"ok": True}