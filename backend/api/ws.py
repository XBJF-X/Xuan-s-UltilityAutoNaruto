"""WebSocket 实时通信 - 日志流 + 调度器状态推送"""
import asyncio
import json
import logging
import threading
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
logger = logging.getLogger("WebSocket")


class ConnectionManager:
    """WebSocket 连接管理器（单例）"""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket 客户端已连接，当前连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket 客户端已断开，当前连接数: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """广播 JSON 消息给所有连接的客户端"""
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        for conn in dead:
            self.disconnect(conn)

    async def broadcast_log(self, level: str, message: str, config_id: str = ""):
        """广播日志消息"""
        await self.broadcast({
            "type": "log",
            "level": level,
            "message": message,
            "config_id": config_id,
        })

    async def broadcast_status(self, status: dict):
        """广播调度器状态变更"""
        await self.broadcast({
            "type": "status",
            "data": status,
        })

    async def broadcast_task_state(self, task_data: dict):
        """广播任务状态变更"""
        await self.broadcast({
            "type": "task_state",
            "data": task_data,
        })


# 全局单例 - 其他模块通过 import 获取
manager = ConnectionManager()


class WebSocketLogHandler(logging.Handler):
    """将日志消息转发到 WebSocket 的 logging Handler（线程安全 + 批量发送）

    自动从 logger name 中提取 config_id（如 "SchedulerService_Config_1" → "Config_1"），
    前端可按 config_id 隔离显示不同配置的日志。
    """

    def __init__(self, level=logging.NOTSET):
        super().__init__(level)
        self._loop = None
        self._batch: list[dict] = []
        self._batch_lock = threading.Lock()
        self._flush_task = None

    @staticmethod
    def _extract_config_id(logger_name: str) -> str:
        """从 logger name 中提取 config_id"""
        # 匹配类似 Service_Config_1, SchedulerService_Config_10 等模式
        import re
        match = re.search(r'(Config_\d+)', logger_name)
        if match:
            return match.group(1)
        return ""

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        """设置主事件循环引用并启动批量刷新协程"""
        self._loop = loop
        if loop and loop.is_running():
            self._flush_task = asyncio.run_coroutine_threadsafe(
                self._periodic_flush(), loop
            )

    def emit(self, record):
        if self._loop is None or not self._loop.is_running():
            return
        try:
            msg = self.format(record)
            config_id = self._extract_config_id(record.name)
            with self._batch_lock:
                self._batch.append({
                    "type": "log",
                    "level": record.levelname,
                    "message": msg,
                    "config_id": config_id,
                    "logger_name": record.name,
                })
        except Exception:
            pass

    async def _periodic_flush(self):
        """每 30ms 刷新一次日志缓冲队列"""
        while True:
            await asyncio.sleep(0.03)
            try:
                await self._flush_batch()
            except Exception:
                pass

    async def _flush_batch(self):
        """将缓冲队列中的日志一次性广播出去"""
        with self._batch_lock:
            if not self._batch:
                return
            batch = self._batch[:]
            self._batch.clear()

        dead = []
        for conn in manager.active_connections:
            try:
                await conn.send_json(["log", batch] if len(batch) > 1 else batch[0])
            except Exception:
                dead.append(conn)
        for conn in dead:
            manager.disconnect(conn)


@router.websocket("/logs")
async def websocket_logs(websocket: WebSocket):
    """实时日志流"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 客户端可发送 ping 保持连接
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/status")
async def websocket_status(websocket: WebSocket):
    """任务/设备状态流"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# 全局共享的 WebSocket 日志推送 handler（单例）
_ws_log_handler = None


def get_ws_log_handler() -> WebSocketLogHandler:
    """获取全局共享的 WebSocket 日志推送 handler（单例）。

    root logger 与各 config 专属 logger 共用同一实例：
    - 避免每次创建 SchedulerService 时重复创建批处理协程/缓冲队列
    - 前端 LogPanel 依赖该 handler 接收实时日志（内部按 logger name 提取 config_id 隔离）
    """
    global _ws_log_handler
    if _ws_log_handler is None:
        _ws_log_handler = WebSocketLogHandler()
    return _ws_log_handler