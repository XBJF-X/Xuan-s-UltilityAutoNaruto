"""调度器管理 API 路由 - 延迟初始化"""
from fastapi import APIRouter, HTTPException
from backend.services.config_service import ConfigService

router = APIRouter()
_config_service = ConfigService()
_schedulers: dict[str, object] = {}


def _get_scheduler(config_id: str):
    if config_id not in _schedulers:
        from backend.services.scheduler_service import SchedulerService
        from utils.Base.Scene.SceneGraph import SceneGraph
        from tool.ResourceManager.ResourceDBManager import ResourceDBManager
        from pathlib import Path
        from backend.utils import get_real_path

        cfg = _config_service.get_config(config_id)
        if not cfg:
            raise HTTPException(status_code=404, detail="配置不存在")
        db = ResourceDBManager(Path(get_real_path("src")))
        sg = SceneGraph(db)
        _schedulers[config_id] = SchedulerService(cfg, sg)
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