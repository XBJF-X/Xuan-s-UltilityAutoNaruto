"""调度器管理 API 路由 - 延迟初始化，接入 WebSocket 状态推送"""
import asyncio
import logging
import re
import threading
import time
from fastapi import APIRouter, HTTPException
from backend.services.config_service import shared_config_service as _config_service
# 阶段 3.4：版本工具的唯一实现在 core/version_info（不再经由 api.utils 中转）
from backend.core.version_info import (
    read_client_version as _read_local_version,
    read_min_release_tag as _read_min_release_tag,
    version_gt as _version_gt,
)
from backend.api.schemas import OkResponse, SchedulerStatus, TaskRuntimeItem

router = APIRouter()
_schedulers: dict[str, object] = {}
# 注册表锁：`_get_scheduler` 是 check-then-create，两个并发请求（Dashboard 轮询 +
# 用户点启动）会各建一个 SchedulerService → 两次设备/串口初始化，且后被覆盖者为
# 无法停止的孤儿（同串口双连接）。
_schedulers_lock = threading.RLock()

# precheck 结果 TTL 缓存（秒）：避免短时间内重复启动触发多次 adb 查询
_PRECheck_TTL = 5.0
_precheck_cache: dict[str, tuple[float, dict]] = {}

# 存储主循环事件循环引用（用于后台线程安全地推送异步事件）。
# 由 lifespan 在启动时显式注入（`bind_main_loop`）：把阻塞端点挪到线程池后，
# `asyncio.get_event_loop()` 在工作线程会抛 RuntimeError，必须走注入的 loop。
_main_loop: asyncio.AbstractEventLoop | None = None

_logger = logging.getLogger("SchedulerAPI")

# 串口格式：127.0.0.1:xxxxx 或 emulator-xxxx
_SERIAL_RE = re.compile(r"^(\d{1,3}\.){3}\d{1,3}:\d+$|^emulator-\d+$", re.IGNORECASE)

# 优雅停机预算（秒）：程序退出时等待各调度器停止并收尾的总时长
SHUTDOWN_TIMEOUT = 5.0


def bind_main_loop(loop: asyncio.AbstractEventLoop) -> None:
    """由 lifespan 注入主事件循环（后台线程推送状态的前提）"""
    global _main_loop
    _main_loop = loop
    _logger.debug("调度器事件循环已注入")


def _get_main_loop_or_none() -> asyncio.AbstractEventLoop | None:
    """取主事件循环；取不到返回 None（调用方丢弃该次推送，不抛异常）。

    正常路径由 lifespan 注入；`asyncio.get_running_loop()` 兜底覆盖"在事件循环线程内
    首次调用"的场景（旧实现在任意线程调 `get_event_loop()`，3.12 下工作线程会抛
    RuntimeError 并丢掉状态推送）。
    """
    global _main_loop
    if _main_loop is not None and not _main_loop.is_closed():
        return _main_loop
    try:
        _main_loop = asyncio.get_running_loop()
    except RuntimeError:
        return None
    return _main_loop


def peek_scheduler(config_id: str):
    """只读获取已创建的调度器实例（**不创建**，无副作用）。

    GET /status、GET /tasks 曾走 `_get_scheduler()`：一次「读状态」就会实例化
    SchedulerService（挂 logger handler、进注册表、构造 planner/executor），而
    Dashboard 5s 轮询会让每个被看过的配置常驻对象；销毁只在删配置时发生。
    """
    with _schedulers_lock:
        return _schedulers.get(config_id)


def _get_scheduler(config_id: str):
    """取（必要时创建）指定配置的调度器实例 —— 仅限有副作用的写/启动路径调用。"""
    with _schedulers_lock:
        sched = _schedulers.get(config_id)
        if sched is not None:
            return sched

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

        async def on_screenshot_limit(payload: dict):
            """本次运行截图数超过每日上限 → 提醒前端弹窗（提示关闭截图开关）。

            走 v1 信封 + legacy 双写：旧前端按未知 type 安全忽略，新前端展示不可自动关闭的弹窗。
            """
            data = dict(payload)
            data["config_id"] = config_id
            await manager.broadcast_dual(
                {"type": "screenshot_limit", "data": data},
                "screenshot.limit", data, config_id=config_id)

        def _submit(coro) -> None:
            """把状态推送投递到主事件循环（投递失败只告警，不影响任务执行）"""
            loop = _get_main_loop_or_none()
            if loop is None:
                _logger.warning("主事件循环未就绪，丢弃一次 WebSocket 状态推送")
                return
            try:
                asyncio.run_coroutine_threadsafe(coro, loop)
            except RuntimeError as e:
                _logger.warning("投递 WebSocket 状态推送失败: %s", e)

        def sync_on_status(status: dict):
            _submit(on_status_change(status))

        def sync_on_task(task_data: dict):
            _submit(on_task_state_change(task_data))

        def sync_on_snapshot(snapshot: dict):
            _submit(on_snapshot(snapshot))

        def sync_on_screenshot_limit(payload: dict):
            _submit(on_screenshot_limit(payload))

        _schedulers[config_id] = SchedulerService(
            cfg,
            on_status_change=sync_on_status,
            on_task_state_change=sync_on_task,
            on_snapshot=sync_on_snapshot,
            on_screenshot_limit=sync_on_screenshot_limit,
        )
        return _schedulers[config_id]


def destroy_scheduler(config_id: str):
    """停止并销毁指定配置的调度器实例（删除配置时调用）。

    调度器持有设备/控制/截图连接（含串口占用），若只删配置文件不销毁调度器，
    旧连接不会被释放，导致后续使用同一串口的配置无法连接。
    """
    with _schedulers_lock:
        sched = _schedulers.pop(config_id, None)
    if sched is None:
        return
    try:
        if getattr(sched, "running", False):
            sched.stop("配置删除")
        _logger.info(f"已销毁配置 {config_id} 的调度器实例")
    except Exception as e:
        _logger.error(f"销毁配置 {config_id} 的调度器实例失败: {e}")


def shutdown_all_schedulers(timeout: float = SHUTDOWN_TIMEOUT) -> list[str]:
    """停止全部调度器实例（程序退出路径），返回未能正常收尾的 config_id 列表。

    旧实现没有任何退出清理：带运行中调度器关闭程序时，任务线程被硬杀在 multi_tap
    半途 → 设备端 evdev MT slot 停在按下态（v0.17.46 记录的"残留触点"故障），只能
    靠下次启动时的自检兜底。
    """
    with _schedulers_lock:
        items = list(_schedulers.items())
    if not items:
        return []
    deadline = time.time() + max(0.0, timeout)
    failed: list[str] = []
    for config_id, sched in items:
        try:
            if getattr(sched, "running", False):
                sched.stop("程序退出")
            scan_thread = getattr(sched, "_scan_thread", None)
            while scan_thread is not None and scan_thread.is_alive() \
                    and time.time() < deadline:
                time.sleep(0.1)
            if scan_thread is not None and scan_thread.is_alive():
                failed.append(config_id)
        except Exception as e:
            _logger.error("停止配置 %s 的调度器失败: %s", config_id, e, exc_info=e)
            failed.append(config_id)
    if failed:
        _logger.warning("以下调度器未在 %.1fs 内完成收尾: %s", timeout, failed)
    else:
        _logger.info("已停止 %d 个调度器实例", len(items))
    return failed


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
        # 冷启动竞态：程序退出会 adb kill-server，下次首次查询时 adb server 刚启动、
        # 本机模拟器端口尚未扫描完，此时直接查询会把在线设备误报为"不在列表中"。
        # 这里短暂等待（不允许重启 server，避免影响其他运行中的配置）后再枚举。
        try:
            from backend.core.legacy.Control.adb_bootstrap import ensure_adb_device
            ensure_adb_device(serial, _logger, timeout=5.0, allow_rescan=False)
        except Exception as e:
            _logger.debug(f"adb 就绪等待失败（继续按当前设备列表判断）: {e}")
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
    """截图路径环境预检：MuMu/LD 安装路径下关键文件存在性。

    候选清单/存在性判定统一走 backend/core/emulator_env.py（阶段 3 单点化，
    与 device.py 的 check-environment、validate.py 的 install-path 共用同一份知识）。
    """
    from backend.core.emulator_env import (
        LD_CONSOLE_NAME, LD_DLL_NAME, check_mumu_files, check_ld_files,
    )

    mode = cfg.get_config("截图模式", 2)
    errors: list[str] = []
    if mode == 3:  # MuMu
        base = str(cfg.get_config("MuMu安装路径", "") or "").strip()

        if not base:
            errors.append("未配置 MuMu 安装路径（截图模式为 MuMu 时需要，请在全局设置中配置）")
            return errors
        dll_ok, manager_ok = check_mumu_files(base)
        if not dll_ok:
            errors.append(base)
            errors.append("MuMu 安装路径下未找到 external_renderer_ipc.dll（截图动态库）")
        if not manager_ok:
            errors.append(base)
            errors.append("MuMu 安装路径下未找到 MuMuManager.exe")
    elif mode == 4:  # LD 雷电
        base = str(cfg.get_config("雷电安装路径", "") or "").strip()
        if not base:
            errors.append("未配置 雷电安装路径（截图模式为 LD 时需要，请在全局设置中配置）")
            return errors
        dll_ok, console_ok = check_ld_files(base)
        if not console_ok:
            errors.append(base)
            errors.append(f"雷电安装路径下未找到 {LD_CONSOLE_NAME}")
        if not dll_ok:
            errors.append(base)
            errors.append(f"雷电安装路径下未找到 {LD_DLL_NAME}")
    return errors


@router.post("/precheck/{config_id}")
def precheck_scheduler(config_id: str):
    """启动/键位配置前的快速预检：串口与 MuMu/LD 截图路径环境。

    目的：在进入耗时的设备连接前把常见参数问题暴露给用户，避免长时间阻塞界面。
    串口同一时刻只能被一个调度器连接（占用检查）。
    结果带 5s TTL 缓存，避免短时间内重复请求重复触发 adb 查询。

    同步路由：内部有 `ensure_adb_device(timeout=5.0)` 与 `adb devices` 子进程调用，
    不能跑在事件循环线程上。
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
    if errors:
        _logger.warning("调度器预检未通过（config_id=%s）: %s", config_id, errors)
    elif warnings:
        _logger.info("调度器预检有提示（config_id=%s）: %s", config_id, warnings)
    result = {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
    }
    _precheck_cache[config_id] = (now, result)
    return result


@router.post("/start/{config_id}", response_model=OkResponse)
def start_scheduler(config_id: str):
    """启动调度器。

    注意是**同步** `def`：`sched.start()` 会做秒级阻塞工作（`_lazy_init` 建设备、
    环境预检里的 `subprocess.run(timeout=15)`、adb 残留触点自检、共享 SceneGraph
    首次解码 ~845 张图）。旧的 `async def` 会把这些跑在事件循环线程上，冻结整个
    服务（含 WS 日志 30ms 批量推送）——用户感受为"点启动后界面卡死、日志停更"。
    同步路由由 FastAPI 自动投递到 anyio 线程池。
    """
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


@router.post("/stop/{config_id}", response_model=OkResponse)
def stop_scheduler(config_id: str):
    """停止调度器（同步路由：`stop()` 含连点线程等待、任务线程 join、adb 自检等阻塞动作）"""
    sched = _get_scheduler(config_id)
    sched.stop("用户手动停止")
    return {"ok": True}


@router.get("/status/{config_id}", response_model=SchedulerStatus)
async def get_scheduler_status(config_id: str):
    """调度器状态（只读，不创建调度器实例）"""
    sched = peek_scheduler(config_id)
    if sched is not None:
        return sched.get_status()
    cfg = _config_service.get_config(config_id)
    if not cfg:
        raise HTTPException(status_code=404, detail="配置不存在")
    # 未创建调度器：返回与 SchedulerState.get_status() 同形状的"未运行"快照
    return {"running": False, "task_count": 0,
            "mode": "once" if cfg.config_type == "临时" else "persistent"}


@router.get("/tasks/{config_id}", response_model=list[TaskRuntimeItem])
async def get_tasks(config_id: str):
    """任务状态快照（只读，不创建调度器实例）"""
    sched = peek_scheduler(config_id)
    if sched is None or not sched.running:
        return []
    return sched.get_tasks_status()


@router.post("/tasks/{config_id}/{task_name}/execute")
def execute_task(config_id: str, task_name: str, force: bool = False):
    """立即执行任务。

    - 默认受任务**自身排期窗口**约束：当前不在可执行窗口内（已过期/未开始）时不做任何
      改动，返回 `{ok: False, reason, window_state, schedule}` 供前端提示；
    - `force=True`：用户在二次确认弹窗中选择「忽略窗口强制执行」时传入。

    同步路由：可能触发一次 `scan()`（启动任务线程、写配置）与窗口探测（读 config）。
    """
    sched = _get_scheduler(config_id)
    return sched.execute_task_now(task_name, ignore_window=force)


@router.put("/tasks/{config_id}/{task_name}/activation", response_model=OkResponse)
def toggle_task_activation(config_id: str, task_name: str, state: bool):
    """切换任务启用状态（**「是否启用」的单一写端点**：持久化 + 运行中调度器同步）。

    阶段 5：改前这里走 `_get_scheduler()`（必要时创建 SchedulerService 实例），于是
    前端为了"调度器没运行时也能保存"又额外调了一次 `PUT /configs/{id}/task/{name}`——
    同一状态两个写入口，且点一下复选框就会常驻一个调度器对象（与 GET 端点当初的
    "读一次就建实例"是同类问题，见 `peek_scheduler` 的说明）。

    现在：**有实例** → 交给它同步队列与快照（它内部也会写配置）；**没有实例** → 只写配置，
    不创建实例。返回值 `synced` 标识是否走了运行中调度器同步。
    """
    sched = peek_scheduler(config_id)
    if sched is None:
        cfg = _config_service.get_config(config_id)
        if not cfg:
            raise HTTPException(status_code=404, detail="配置不存在")
        cfg.set_task_base_config(task_name, "是否启用", state)
        return {"ok": True, "synced": False}
    sched.toggle_task_activation(task_name, state)
    return {"ok": True, "synced": True}