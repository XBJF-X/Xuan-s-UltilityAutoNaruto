"""调度器管理 API 路由 - 延迟初始化，接入 WebSocket 状态推送"""
import asyncio
import logging
import os
import re
import time
from fastapi import APIRouter, HTTPException
from backend.services.config_service import shared_config_service as _config_service
from backend.api.utils import _read_local_version, _read_min_release_tag, _version_gt

router = APIRouter()
_schedulers: dict[str, object] = {}

# precheck 结果 TTL 缓存（秒）：避免短时间内重复启动触发多次 adb 查询
_PRECheck_TTL = 5.0
_precheck_cache: dict[str, tuple[float, dict]] = {}

# 存储主线程事件循环引用（用于后台线程安全地推送异步事件）
_main_loop: asyncio.AbstractEventLoop | None = None

_logger = logging.getLogger("SchedulerAPI")

# 串口格式：127.0.0.1:xxxxx 或 emulator-xxxx
_SERIAL_RE = re.compile(r"^(\d{1,3}\.){3}\d{1,3}:\d+$|^emulator-\d+$", re.IGNORECASE)


def _get_main_loop() -> asyncio.AbstractEventLoop:
    global _main_loop
    if _main_loop is None or _main_loop.is_closed():
        _main_loop = asyncio.get_event_loop()
    return _main_loop


def _get_scheduler(config_id: str):
    if config_id not in _schedulers:
        from backend.services.scheduler_service import SchedulerService
        from backend.api.ws import manager

        cfg = _config_service.get_config(config_id)
        if not cfg:
            raise HTTPException(status_code=404, detail="配置不存在")
        # 注意：不再在此构建 SceneGraph（解码全部元素图，秒级）。
        # SceneGraph 延迟到调度器 start() 时构建，且为全局共享单例（跨配置复用）。

        # 状态变更回调：通过 WebSocket 推送（线程安全版）
        async def on_status_change(status: dict):
            status["config_id"] = config_id
            await manager.broadcast_status(status)

        async def on_task_state_change(task_data: dict):
            task_data["config_id"] = config_id
            await manager.broadcast_task_state(task_data)

        async def on_snapshot(snapshot: dict):
            msg = dict(snapshot)
            msg["config_id"] = config_id
            await manager.broadcast_snapshot(msg)

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

        def sync_on_snapshot(snapshot: dict):
            loop = _get_main_loop()
            asyncio.run_coroutine_threadsafe(
                on_snapshot(snapshot), loop
            )

        _schedulers[config_id] = SchedulerService(
            cfg,
            on_status_change=sync_on_status,
            on_task_state_change=sync_on_task,
            on_snapshot=sync_on_snapshot,
        )
    return _schedulers[config_id]


def destroy_scheduler(config_id: str):
    """停止并销毁指定配置的调度器实例（删除配置时调用）。

    调度器持有设备/控制/截图连接（含串口占用），若只删配置文件不销毁调度器，
    旧连接不会被释放，导致后续使用同一串口的配置无法连接。
    """
    sched = _schedulers.pop(config_id, None)
    if sched is None:
        return
    try:
        if getattr(sched, "running", False):
            sched.stop()
        _logger.info(f"已销毁配置 {config_id} 的调度器实例")
    except Exception as e:
        _logger.error(f"销毁配置 {config_id} 的调度器实例失败: {e}")


def _precheck_serial(cfg) -> tuple[list[str], list[str]]:
    """串口预检：已配置 / 格式 / 是否被其他运行中的调度器占用 / adb 设备在线。"""
    errors: list[str] = []
    warnings: list[str] = []

    serial = str(cfg.get_config("串口", "") or "").strip().replace("：", ":")
    if not serial:
        errors.append("未配置串口（请在助手设置中填写或选择串口）")
        return errors, warnings

    if not _SERIAL_RE.match(serial):
        errors.append(
            f"串口格式不正确：{serial}（应为 127.0.0.1:5555 或 emulator-5554 形式）")
        return errors, warnings

    # 同一个串口只能被一个调度器连接：检查其他运行中调度器是否占用同一串口
    for other_id, other in _schedulers.items():
        if other_id == cfg.config_path.stem or not getattr(other, "running", False):
            continue
        other_serial = str(
            other.config.get_config("串口", "") or "").strip().replace("：", ":")
        if other_serial and other_serial.lower() == serial.lower():
            errors.append(
                f"串口 {serial} 已被配置「{other_id}」的调度器占用，"
                f"请先停止对应调度器或改用其他串口")
            break

    if errors:
        return errors, warnings

    # 设备在线检查：仅当 adb 能枚举到该串口才算在线（MuMu/雷电 可能不出现，降级为警告）
    try:
        from backend.api.device import get_adb_serials
        serials = get_adb_serials()
        if serial not in serials:
            msg = f"串口 {serial} 未在 adb 设备列表中发现（当前已连接：{', '.join(serials) or '无'}）"
            mode = cfg.get_config("截图模式", 2)
            if mode in (3, 4):
                warnings.append(msg + "（MuMu/雷电 设备可能不会出现在 adb devices 中，将继续尝试连接）")
            else:
                errors.append(msg)
    except Exception as e:
        warnings.append(f"adb 设备列表查询失败（不影响本次连接尝试）: {e}")

    return errors, warnings


def _precheck_screenshot_path(cfg) -> list[str]:
    """截图路径环境预检：MuMu/LD 安装路径下关键文件存在性（参照 validate.py / device.py check-environment）。"""
    mode = cfg.get_config("截图模式", 2)
    errors: list[str] = []
    if mode == 3:  # MuMu
        base = str(cfg.get_config("MuMu安装路径", "") or "").strip()
        if not base:
            errors.append("未配置 MuMu 安装路径（截图模式为 MuMu 时需要，请在全局设置中配置）")
            return errors
        from backend.api.validate import MUMU_MANAGER_CANDIDATES, MUMU_DLL_CANDIDATES
        manager_ok = any(os.path.exists(os.path.join(base, rel)) for rel in MUMU_MANAGER_CANDIDATES)
        dll_ok = any(os.path.exists(os.path.join(base, rel)) for rel in MUMU_DLL_CANDIDATES)
        if not dll_ok:
            errors.append("MuMu 安装路径下未找到 external_renderer_ipc.dll（截图动态库）")
        if not manager_ok:
            errors.append("MuMu 安装路径下未找到 MuMuManager.exe")
    elif mode == 4:  # LD 雷电
        base = str(cfg.get_config("雷电安装路径", "") or "").strip()
        if not base:
            errors.append("未配置 雷电安装路径（截图模式为 LD 时需要，请在全局设置中配置）")
            return errors
        if not os.path.exists(os.path.join(base, "ldconsole.exe")):
            errors.append("雷电安装路径下未找到 ldconsole.exe")
        if not os.path.exists(os.path.join(base, "ldopengl64.dll")):
            errors.append("雷电安装路径下未找到 ldopengl64.dll")
    return errors


@router.post("/precheck/{config_id}")
async def precheck_scheduler(config_id: str):
    """启动/键位配置前的快速预检：串口与 MuMu/LD 截图路径环境。

    目的：在进入耗时的设备连接前把常见参数问题暴露给用户，避免长时间阻塞界面。
    串口同一时刻只能被一个调度器连接（占用检查）。
    结果带 5s TTL 缓存，避免短时间内重复请求重复触发 adb 查询。
    """
    now = time.monotonic()
    cached = _precheck_cache.get(config_id)
    if cached and now - cached[0] < _PRECheck_TTL:
        return cached[1]

    cfg = _config_service.get_config(config_id)
    if not cfg:
        raise HTTPException(status_code=404, detail="配置不存在")

    serial_errors, warnings = _precheck_serial(cfg)
    path_errors = _precheck_screenshot_path(cfg)
    errors = serial_errors + path_errors
    result = {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
    }
    _precheck_cache[config_id] = (now, result)
    return result


@router.post("/start/{config_id}")
async def start_scheduler(config_id: str):
    # 依赖库版本硬拦截：本 commit 需要的最旧依赖库 ReleaseTag（MIN_RELEASE_TAG）不满足时
    # 禁止启动调度器——热更新只替换代码、不携带依赖库（OCR 模型/DLL 等），若本地 _version.py
    # 低于所需版本，运行期可能因代码依赖新依赖库出现恶性 BUG，必须走 Release 完整安装包更新。
    local_version = _read_local_version()
    required_tag, required_version = _read_min_release_tag()
    if required_version and local_version and _version_gt(required_version, local_version):
        raise HTTPException(
            status_code=400,
            detail=(
                f"当前版本 {local_version} 低于本版本要求的最低版本 {required_tag}，"
                f"依赖库不完整，禁止启动调度器。请前往 Release 下载最新安装包更新。"
            ),
        )

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