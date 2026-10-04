"""WebSocket 实时通信 - 日志流 + 调度器状态推送"""
import asyncio
import json
import logging
import threading
from urllib.parse import urlparse

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
logger = logging.getLogger("WebSocket")

# ===== 连接来源校验 =====
# WebSocket **不受 CORS 约束**：旧实现无任何校验，任意网站都能
# `new WebSocket("ws://127.0.0.1:4199/ws/logs")` 读取全部日志（含用户名、串口、
# 安装路径、异常堆栈）。这里按 Origin 主机白名单放行（严格解析 host，避免
# `http://127.0.0.1.evil.com` 这类前缀欺骗）：
#   - 同源（生产：SPA 由后端自己托管，Origin 即 http://127.0.0.1:<端口>）
#   - 本地开发服务器（vite dev server 直连场景）
# 浏览器一定会带 Origin；无 Origin 的非浏览器客户端（测试脚本/CLI）放行但留痕。
_ALLOWED_ORIGIN_HOSTS = {"127.0.0.1", "localhost", "::1"}
_ALLOWED_ORIGIN_SCHEMES = {"http", "https"}


def _origin_allowed(origin: str | None) -> bool:
    if not origin:
        return True
    try:
        parts = urlparse(origin)
    except ValueError:
        return False
    if parts.scheme not in _ALLOWED_ORIGIN_SCHEMES:
        return False
    host = (parts.hostname or "").lower()
    return host in _ALLOWED_ORIGIN_HOSTS


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

    async def broadcast_snapshot(self, snapshot: dict):
        """广播调度器完整状态快照（合并 status + tasks，前端据此零轮询）"""
        await self.broadcast({
            "type": "scheduler_snapshot",
            "data": snapshot,
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
    def _extract_config_id(record_or_name) -> str:
        """取 config_id：显式绑定（record.config_id）优先，其次从 logger 名兜底解析。

        参数兼容两种形态：`logging.LogRecord`（emit 路径）或 logger 名字符串（旧调用形态）。
        兜底正则必须覆盖副本配置 id（`Config_1_副本` / `Config_1_副本2`），否则副本日志
        会被错判成源配置（详情见 backend/log_setup.py::extract_config_id）。
        """
        from backend.log_setup import extract_config_id
        if record_or_name is None:
            return ""
        if isinstance(record_or_name, str):
            return extract_config_id(logger_name=record_or_name)
        return extract_config_id(
            explicit=getattr(record_or_name, "config_id", "") or "",
            logger_name=getattr(record_or_name, "name", "") or "",
        )

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
            config_id = self._extract_config_id(record)
            with self._batch_lock:
                self._batch.append({
                    "type": "log",
                    "level": record.levelname,
                    "message": msg,
                    "config_id": config_id,
                    "logger_name": record.name,
                    # 日志记录生成时刻（服务端毫秒时间戳，取自 record.created，
                    # 与日志文件 asctime 同源）。前端据此展示时间并做历史日志去重：
                    # 若前端改用接收时刻，历史补齐时会因时间戳不一致而把同一条日志
                    # 重复展示一遍（详见 frontend/src/api/ws.ts 的 mergeHistory）。
                    "ts": int(record.created * 1000),
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


async def _reject_if_origin_denied(websocket: WebSocket) -> bool:
    """Origin 不在白名单时拒绝连接（返回 True=已拒绝）"""
    origin = websocket.headers.get("origin")
    if _origin_allowed(origin):
        if not origin:
            logger.debug("WebSocket 连接无 Origin 头（非浏览器客户端），按放行处理")
        return False
    logger.warning("拒绝非白名单 Origin 的 WebSocket 连接: %s", origin)
    await websocket.close(code=1008)
    return True


@router.websocket("/logs")
async def websocket_logs(websocket: WebSocket):
    """实时日志流"""
    if await _reject_if_origin_denied(websocket):
        return
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
    if await _reject_if_origin_denied(websocket):
        return
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