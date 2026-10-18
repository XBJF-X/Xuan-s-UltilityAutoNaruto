"""设备相关 API 路由：截图、串口列表等"""
import base64
import logging

from fastapi import APIRouter, HTTPException

from backend.services.config_service import shared_config_service as config_service
from backend.api.schemas import (
    AdbRestartResponse,
    SerialListResponse,
    StaleContactsResponse,
)
from backend.runtime.adb_env import ensure_bundled_adb

# 本模块是 adb 查询的公共入口：导入即固定为依赖库自带的 adb，避免与用户
# 本机 adb 争用同一个 adb server。
ensure_bundled_adb()

router = APIRouter()
logger = logging.getLogger("DeviceAPI")


def _capture_frame(config_id: str, cfg=None):
    """获取模拟器截图帧：优先复用调度器的 device，未启动时新建 ScreenManager"""
    if cfg is None:
        cfg = config_service.get_config(config_id)
        if cfg is None:
            return None
    frame = None
    try:
        # 若调度器已启动，直接复用其 device 截图，避免重复建立截图连接
        from backend.api.scheduler import _schedulers
        sched = _schedulers.get(config_id)
        if (sched is not None and getattr(sched, "running", False)
                and sched.device is not None):
            frame = sched.device.screen_cap()
    except Exception as e:
        logger.warning(f"从调度器取截图失败，回退到独立截图: {e}")
        frame = None

    # 未启动调度器（或调度器截图失败）时，临时实例化 Device 取出截图。
    # Device 会同时创建 ControlManager 与 ScreenManager，部分截图模式（如
    # MuMu/LD/ADB）依赖 ControlManager 建立连接并保证初始化，单独创建
    # ScreenManager 会导致 screencap() 返回 None，进而让接口报 500。
    # 使用 backend.core.legacy.Device（已剥离 V1 utils/Base 依赖），
    # 与 scheduler_service._lazy_init 的实例化方式保持一致。
    if frame is None:
        from backend.core.legacy.Device import Device

        device = None
        try:
            # Device 类型标注指向 legacy Config，但实际仅使用 get_config 等
            # backend Config 同样具备的方法；scheduler_service 亦以相同方式
            # （backend Config 实例化 Device）工作，运行时兼容。
            device = Device(cfg, logger)  # type: ignore[arg-type]
            sm = getattr(device, "screen_manager", None)
            if sm is not None:
                frame = sm.screencap()
        finally:
            # 释放临时设备持有的截图/控制连接资源
            if device is not None:
                for m in (getattr(device, "screen_manager", None),
                          getattr(device, "control_manager", None)):
                    release = getattr(m, "release", None)
                    if callable(release):
                        try:
                            release()
                        except Exception:
                            pass
    return frame


def get_adb_serials() -> list[str]:
    """通过 adbutils 获取已连接的 ADB 设备序列号列表"""
    try:
        from adbutils import adb, AdbError
    except ImportError:
        logger.warning("adbutils 未安装，无法枚举设备")
        return []
    try:
        devices = adb.device_list()
        serials = []
        for device in devices:
            try:
                state = device.get_state()
            except Exception:
                state = "unknown"
            if state == "device":
                serials.append(device.serial)
        return serials
    except AdbError as e:
        logger.error(f"ADB命令执行失败: {e}")
        return []
    except Exception as e:
        logger.exception(f"获取ADB设备列表时发生未知错误: {e}")
        return []


def restart_adb_server():
    """重启 ADB 服务"""
    try:
        from adbutils import adb
        adb.server_kill()
        return True
    except Exception as e:
        logger.exception(f"重启ADB服务失败: {e}")
        return False


def _frame_to_png_base64(frame) -> str:
    """将截图帧编码为 data URL base64 字符串"""
    import cv2

    ok, buf = cv2.imencode(".png", frame)
    if not ok:
        raise HTTPException(status_code=500, detail="截图编码失败")
    image_base64 = base64.b64encode(buf.tobytes()).decode("utf-8")
    return f"data:image/png;base64,{image_base64}"


@router.get("/{config_id}/screenshot")
def get_screenshot(config_id: str):
    """获取模拟器截图，返回 base64 PNG 图片数据（供键位配置使用）

    同步路由：`_capture_frame` 走 adb/模拟器截图（数百 ms~数秒）再 base64 编码，
    不能跑在事件循环线程上（会冻结 WS 日志推送与其它接口）。
    """
    cfg = config_service.get_config(config_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="配置不存在")

    try:
        frame = _capture_frame(config_id, cfg)
        if frame is None:
            raise HTTPException(status_code=500, detail="截图失败，请检查模拟器连接与截图模式设置")
        return {"image": _frame_to_png_base64(frame)}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("截图失败")
        raise HTTPException(status_code=500, detail=f"截图失败: {e}")


@router.post("/{config_id}/save-screenshot")
def save_screenshot(config_id: str):
    """截图并保存到 log/<用户名>/<日期>/screenshot/用户截图/<时间戳>.png（同步路由：含截图与落盘）"""
    cfg = config_service.get_config(config_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="配置不存在")

    try:
        frame = _capture_frame(config_id, cfg)
        if frame is None:
            raise HTTPException(status_code=500, detail="截图失败，请检查模拟器连接与截图模式设置")

        from datetime import datetime
        import os

        from backend.utils import get_real_path

        username = cfg.get_config("用户名", "unknown") or "unknown"
        date_str = datetime.now().strftime("%Y-%m-%d")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        safe_name = username.replace("/", "_").replace("\\", "_")
        save_dir = os.path.join(get_real_path("log"), safe_name, date_str, "screenshot","用户截图")
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, f"{ts}.png")
        import cv2

        ok, buf = cv2.imencode(".png", frame)
        if not ok:
            raise HTTPException(status_code=500, detail="截图编码失败")
        buf.tofile(filepath)
        logger.info(f"保存截图为 {filepath}")
        return {"ok": True, "path": filepath}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("截图保存失败")
        raise HTTPException(status_code=500, detail=f"截图保存失败: {e}")


@router.post("/{config_id}/check-environment")
def check_environment(config_id: str):
    """检测模拟器运行环境（截图路径文件 / 实例状态 / 分辨率16:9 / 后台保活）

    同步路由：内部有 `MuMuManager info -v` / `ldconsole list2` 子进程调用（timeout=15s）。
    """
    cfg = config_service.get_config(config_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="配置不存在")

    import os
    result: dict = {
        "screenshot_mode": cfg.get_config("截图模式", 2),
        "path_ok": False,
        "missing_files": [],
        "instance_ok": False,
        "running": False,
        "resolution_ok": False,
        "resolution": [],
        "is_16_9": None,
    }

    mode = result["screenshot_mode"]
    if mode == 3:  # MuMu
        from backend.core.emulator_env import (
            MUMU_DLL_CANDIDATES, check_mumu_files, find_mumu_manager,
            probe_mumu_instance,
        )
        base = cfg.get_config("MuMu安装路径", "")
        index = cfg.get_config("MuMu实例索引", 0)
        # 候选路径/探测解析统一由 core/emulator_env.py 提供（阶段 3 单点化）
        dll_ok, manager_ok = check_mumu_files(base)
        manager = find_mumu_manager(base)
        missing = [] if base else ["（未配置安装路径）"]
        if base and not dll_ok:
            missing.append("external_renderer_ipc.dll（MuMu 动态库，安装根目录/shell/nx_device/nx_main 下）")
        if base and not manager_ok:
            missing.append("MuMuManager.exe（安装根目录或 shell/、nx_main/ 下）")
        result["path_ok"] = not missing
        result["missing_files"] = missing
        if manager is not None:
            info = probe_mumu_instance(manager, index)
            if info is not None:
                result["instance_ok"] = info.running
                if info.resolution:
                    result["resolution"] = list(info.resolution)
                    result["is_16_9"] = info.is_16_9
                    result["resolution_ok"] = bool(info.is_16_9)
        result["keep_alive_hint"] = (
            "MuMu：无直接后台保活命令，建议在 MuMu 多开器设置中开启"
            "『关闭游戏后保持后台运行』；运行中实例 info -v 输出 state=Running。"
        )
    elif mode == 4:  # LD 雷电
        from backend.core.emulator_env import (
            LD_REQUIRED_FILES, find_ld_console, missing_files, probe_ld_instances,
        )
        base = cfg.get_config("雷电安装路径", "")
        index = cfg.get_config("雷电实例索引", 0)
        missing = missing_files(base, LD_REQUIRED_FILES) if base else ["（未配置安装路径）"]
        result["path_ok"] = not missing
        result["missing_files"] = missing
        console = find_ld_console(base)
        if console is not None:
            instance = probe_ld_instances(console).get(index)
            if instance is not None:
                result["instance_ok"] = True
                result["running"] = instance.running
                if instance.resolution:
                    result["resolution"] = list(instance.resolution)
                    result["is_16_9"] = instance.is_16_9
                    result["resolution_ok"] = bool(instance.is_16_9)
        result["keep_alive_hint"] = (
            "雷电：ldconsole list2 第5列(sysboot) 为 1 表示实例运行中（含后台保活）；"
            "若需确认『后台保活』设置，请打开雷电多开器 → 设置 → 其他 → 勾选『关闭模拟器(后台)时保持运行』。"
        )
    else:
        result["path_ok"] = True
        result["missing_files"] = []
        result["instance_ok"] = True
        result["keep_alive_hint"] = "当前截图模式无需检测安装路径与后台保活。"

    return result


@router.get("/{config_id}/serial-list", response_model=SerialListResponse)
def get_serial_list(config_id: str):
    """获取已连接的 ADB 设备串口列表（同步路由：adb 子进程调用）"""
    serials = get_adb_serials()
    return {"serials": serials}


@router.post("/{config_id}/adb-restart", response_model=AdbRestartResponse)
def restart_adb(config_id: str):
    """重启 ADB 服务并重新枚举设备（同步路由：重启 adb server 秒级阻塞）"""
    ok = restart_adb_server()
    serials = get_adb_serials()
    return {"ok": ok, "serials": serials}


@router.post("/{config_id}/clean-stale-contacts", response_model=StaleContactsResponse)
def clean_stale_contacts(config_id: str):
    """清理设备端残留触点（粘滞多点触摸）。

    连点过程中设备端 minitouch 进程若在「触点仍按下」时被终止（例如用户触摸屏幕
    后模拟器杀服务、或连点刷新时先杀进程后抬起），evdev 的 MT slot 不会自动抬起，
    之后任何一次点击都会把残留坐标一并上报——表现为「点一下屏幕就同时触发所有
    预设连点坐标」，且重启前一直存在。本接口用裸 evdev 抬起序列清除，无需重启
    模拟器（V0.17.46 起调度器启停也会自动做这件事）。
    """
    cfg = config_service.get_config(config_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="配置不存在")

    serial = str(cfg.get_config("串口", "") or "").strip().replace("：", ":")
    if not serial:
        raise HTTPException(status_code=400, detail="未配置串口，无法清理残留触点")

    from backend.core.legacy.Control import touch_residue

    before = touch_residue.detect_touch_state(serial, logger=logger)
    cleaned = touch_residue.clean_stale_contacts(
        serial, logger=logger, reason="用户手动清理残留触点")
    after = touch_residue.detect_touch_state(serial, logger=logger)

    if not cleaned:
        raise HTTPException(
            status_code=500,
            detail="清理失败：请确认模拟器已启动且 adb 连接正常（可先点「重启 Adb」）")

    return {
        "ok": True,
        "serial": serial,
        "had_stale": bool(before.get("active")),
        "before": before,
        "after": after,
    }

