"""设备相关 API 路由：截图、串口列表等"""
import base64
import logging

from fastapi import APIRouter, HTTPException

from backend.services.config_service import ConfigService

router = APIRouter()
logger = logging.getLogger("DeviceAPI")
config_service = ConfigService()


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


@router.get("/{config_id}/screenshot")
async def get_screenshot(config_id: str):
    """获取模拟器截图，返回 base64 PNG 图片数据（供键位配置使用）"""
    cfg = config_service.get_config(config_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="配置不存在")

    try:
        # 使用纯 Python 截图管理器（无 Qt 依赖）
        from utils.Base.Screen.ScreenManager import ScreenManager

        screen_manager = ScreenManager(cfg, logger)
        frame = screen_manager.screencap()
        try:
            screen_manager.release()
        except Exception:
            pass

        if frame is None:
            raise HTTPException(status_code=500, detail="截图失败，请检查模拟器连接与截图模式设置")

        # 统一转 PNG 编码
        import cv2

        ok, buf = cv2.imencode(".png", frame)
        if not ok:
            raise HTTPException(status_code=500, detail="截图编码失败")
        image_base64 = base64.b64encode(buf.tobytes()).decode("utf-8")
        return {"image": f"data:image/png;base64,{image_base64}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("截图失败")
        raise HTTPException(status_code=500, detail=f"截图失败: {e}")


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