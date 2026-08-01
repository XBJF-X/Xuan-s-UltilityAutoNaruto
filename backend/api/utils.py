"""工具类 API 路由"""
import subprocess

from fastapi import APIRouter

router = APIRouter()


@router.get("/serial-list")
async def get_serial_list():
    """通过 adb devices 枚举当前连接的设备串口列表"""
    try:
        result = subprocess.run(
            ["adb", "devices"], capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="ignore",
        )
        output = result.stdout or ""
        serials = []
        for line in output.strip().splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 2 and parts[-1] == "device":
                serials.append(parts[0])
        return {"serials": serials}
    except Exception:
        return {"serials": []}