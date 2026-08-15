"""设备相关 API 路由：截图、串口列表等"""
import base64
import logging

from fastapi import APIRouter, HTTPException

from backend.services.config_service import shared_config_service as config_service

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
async def get_screenshot(config_id: str):
    """获取模拟器截图，返回 base64 PNG 图片数据（供键位配置使用）"""
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
async def save_screenshot(config_id: str):
    """截图并保存到 log/<用户名>/<日期>/screenshot/用户截图/<时间戳>.png"""
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
async def check_environment(config_id: str):
    """检测模拟器运行环境（截图路径文件 / 实例状态 / 分辨率16:9 / 后台保活）"""
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

    def check_files(base: str, required: list[str]) -> list[str]:
        missing = []
        for rel in required:
            if not os.path.exists(os.path.join(base, rel)):
                missing.append(rel)
        return missing

    mode = result["screenshot_mode"]
    if mode == 3:  # MuMu
        base = cfg.get_config("MuMu安装路径", "")
        index = cfg.get_config("MuMu实例索引", 0)
        # 候选路径与 MuMu.py / validate.py / scheduler_service.py 保持一致，任一存在即可
        manager = None
        for rel in ("MuMuManager.exe", "shell/MuMuManager.exe", "nx_main/MuMuManager.exe"):
            candidate = os.path.join(base, rel)
            if os.path.exists(candidate):
                manager = candidate
                break
        dll_candidates = (
            "shell/sdk/external_renderer_ipc.dll",
            "nx_device/12.0/shell/sdk/external_renderer_ipc.dll",
            "nx_device/15.0/shell/sdk/external_renderer_ipc.dll",
            "nx_main/sdk/external_renderer_ipc.dll",
        )
        missing = [] if base else ["（未配置安装路径）"]
        if base and not any(os.path.exists(os.path.join(base, rel)) for rel in dll_candidates):
            missing.append("external_renderer_ipc.dll（MuMu 动态库，安装根目录/shell/nx_device/nx_main 下）")
        if manager is None and base:
            missing.append("MuMuManager.exe（安装根目录或 shell/、nx_main/ 下）")
        result["path_ok"] = not missing
        result["missing_files"] = missing
        if manager is not None and os.path.exists(manager):
            import subprocess
            try:
                out = subprocess.run(
                    [manager, "info", "-v", str(index)],
                    capture_output=True, text=True, timeout=15,
                    encoding="utf-8", errors="ignore",
                ).stdout or ""
                result["instance_ok"] = ("state=Running" in out or "状态=运行" in out)
                import re
                w = re.search(r"ScreenWidth=(\d+)", out)
                h = re.search(r"ScreenHeight=(\d+)", out)
                if w and h:
                    rw, rh = int(w.group(1)), int(h.group(1))
                    result["resolution"] = [rw, rh]
                    result["is_16_9"] = abs(max(rw, rh) * 9 - min(rw, rh) * 16) < 10
                    result["resolution_ok"] = bool(result["is_16_9"])
            except Exception:
                pass
        result["keep_alive_hint"] = (
            "MuMu：无直接后台保活命令，建议在 MuMu 多开器设置中开启"
            "『关闭游戏后保持后台运行』；运行中实例 info -v 输出 state=Running。"
        )
    elif mode == 4:  # LD 雷电
        base = cfg.get_config("雷电安装路径", "")
        index = cfg.get_config("雷电实例索引", 0)
        missing = check_files(base, ["ldconsole.exe", "ldopengl64.dll"]) if base else ["（未配置安装路径）"]
        result["path_ok"] = not missing
        result["missing_files"] = missing
        ldconsole = os.path.join(base, "ldconsole.exe")
        if os.path.exists(ldconsole):
            import subprocess
            try:
                out = subprocess.run(
                    [ldconsole, "list2"],
                    capture_output=True, text=True, timeout=15,
                    encoding="utf-8", errors="ignore",
                ).stdout or ""
                for line in out.strip().splitlines():
                    parts = line.split(",")
                    if len(parts) >= 8 and parts[0].strip().isdigit() and int(parts[0]) == index:
                        result["instance_ok"] = True
                        sysboot = parts[4].strip()  # 第5列 sysboot：1=运行(含后台保活)
                        result["running"] = sysboot == "1"
                        rw, rh = int(parts[7]), int(parts[8])
                        result["resolution"] = [rw, rh]
                        result["is_16_9"] = abs(max(rw, rh) * 9 - min(rw, rh) * 16) < 10
                        result["resolution_ok"] = bool(result["is_16_9"])
                        break
            except Exception:
                pass
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


@router.get("/{config_id}/serial-list")
async def get_serial_list(config_id: str):
    """获取已连接的 ADB 设备串口列表"""
    serials = get_adb_serials()
    return {"serials": serials}


@router.post("/{config_id}/adb-restart")
async def restart_adb(config_id: str):
    """重启 ADB 服务并重新枚举设备"""
    ok = restart_adb_server()
    serials = get_adb_serials()
    return {"ok": ok, "serials": serials}
