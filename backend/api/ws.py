"""WebSocket 实时通信 - 日志流 + 调度器状态推送

协议演进（阶段 2，2026-10-04）
=============================

背景：改前有 4 类消息 + 1 种"数组帧"（`["log", batch]`）+ 2 种字段位置（顶层字段
与 `data` 混用），前端只能靠 `Array.isArray` 特判 + 把 `data.config_id` 拍到顶层的
hack 兼容；且没有协议版本、没有连接级状态、慢客户端会阻塞整轮广播。

现在的约定（**v1 信封**）：:

    {"v":1,"type":"scheduler.snapshot","seq":118,"ts":1730000000000,
     "config_id":"Config_1","payload":{...}}

不变式：
- `config_id` 只在**顶层**（payload 内不再重复）；
- `payload` 的形状由 `type` 唯一决定；
- `seq` 每连接单调递增（前端据此丢弃乱序/过期帧）；
- 未知 `type` 必须被忽略（前向兼容）。

**兼容策略（热更新硬约束）**：后端源码可热更，但用户磁盘上的 `frontend/dist` 可能
仍是旧版（只认旧帧）。因此：
1. 连接默认处于 **legacy 模式**，收到的帧与改造前逐字等价（含 `["log", batch]`）；
2. 前端连上后发 `{"type":"subscribe","protocol":1}`，该连接才切到 v1 信封；
3. 旧帧至少保留 2 个 release，之后才清理（见 docs/refactor-plan-2026.md §7.9）。
"""
import asyncio
import json
import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Iterable, Optional
from urllib.parse import urlparse

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
logger = logging.getLogger("WebSocket")

# ===== 协议常量 =====
PROTOCOL_VERSION = 1
# 单帧日志条数上限（超出截断并在 payload.dropped 里报数，避免一帧过大压垮前端）
LOG_BATCH_MAX = 200
# 单次发送超时：超过即判定慢客户端并断开（旧实现串行 await 且无超时，
# 一个卡住的客户端会阻塞整轮广播）
SEND_TIMEOUT = 2.0

# 连接模式
PROTOCOL_LEGACY = 0
PROTOCOL_V1 = 1

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


def build_frame(frame_type: str, payload, *, config_id: str = "",
                seq: int = 0, ts: Optional[int] = None) -> dict:
    """构造 v1 统一信封（纯函数，便于单测与后续复用）"""
    return {
        "v": PROTOCOL_VERSION,
        "type": frame_type,
        "seq": seq,
        "ts": int(time.time() * 1000) if ts is None else int(ts),
        "config_id": config_id,
        "payload": payload,
    }


# legacy `type` → v1 `type` 的映射（新语义一律新增 type，不改旧 type 的含义）
_V1_TYPE_MAP = {
    "status": "status",
    "task_state": "task.state",
    "scheduler_snapshot": "scheduler.snapshot",
}


@dataclass
class ConnState:
    """单个连接的状态（协议版本 / 序列号 / 订阅）"""

    protocol: int = PROTOCOL_LEGACY
    seq: int = 0
    # 空集合 = 订阅全部（兼容旧前端：它们从不发送 subscribe）
    config_ids: set = field(default_factory=set)

    def next_seq(self) -> int:
        self.seq += 1
        return self.seq

    def accepts_config(self, config_id: str) -> bool:
        """该连接是否关心这个 config_id 的帧。

        - 空订阅集合 = 订阅全部（旧前端从不发送 subscribe）；
        - 无归属日志（`config_id == ""`，如 WS/API 自身日志）**始终放行**：它们不属于
          任何配置，按配置过滤会让"程序级日志"凭空消失。
        """
        if not self.config_ids:
            return True
        if not config_id:
            return True
        return config_id in self.config_ids


class ConnectionManager:
    """WebSocket 连接管理器（单例）

    并发约定：所有方法都在**主事件循环内**调用（广播由 `run_coroutine_threadsafe`
    投递回该循环；连接/断开发生在 WS 处理方法里），因此不需要额外锁；但遍历连接
    时必须先取快照，否则 `await` 期间新增/移除连接会导致漏发或 RuntimeError。
    """

    def __init__(self):
        self._connections: dict[WebSocket, ConnState] = {}

    # ---- 兼容属性：旧代码/脚本读取 active_connections ----
    @property
    def active_connections(self) -> list:
        return list(self._connections.keys())

    def get_state(self, websocket: WebSocket) -> Optional[ConnState]:
        return self._connections.get(websocket)

    def connection_count(self) -> int:
        return len(self._connections)

    async def connect(self, websocket: WebSocket) -> ConnState:
        await websocket.accept()
        state = ConnState()
        self._connections[websocket] = state
        logger.info(f"WebSocket 客户端已连接，当前连接数: {len(self._connections)}")
        # 连接首帧告知服务端能力（旧前端会忽略未知 type）
        await self.send_hello(websocket)
        return state

    def disconnect(self, websocket: WebSocket):
        if self._connections.pop(websocket, None) is not None:
            logger.info(
                f"WebSocket 客户端已断开，当前连接数: {len(self._connections)}")
        else:
            logger.debug("WebSocket 断开一个未登记的连接（可能已被清理）")

    def set_protocol(self, websocket: WebSocket, protocol: int,
                     config_ids: Optional[Iterable[str]] = None) -> ConnState:
        """切换连接的协议版本（客户端 `subscribe` 帧调用）"""
        state = self._connections.get(websocket)
        if state is None:
            state = ConnState()
            self._connections[websocket] = state
        state.protocol = PROTOCOL_V1 if int(protocol or 0) >= PROTOCOL_V1 \
            else PROTOCOL_LEGACY
        if config_ids is not None:
            state.config_ids = {str(c) for c in config_ids if str(c or "")}
        logger.info(
            "WebSocket 连接切换协议：protocol=%d 订阅=%s",
            state.protocol, sorted(state.config_ids) or "全部")
        return state

    async def _send(self, websocket: WebSocket, frame) -> bool:
        """发送一帧；超时/异常返回 False（调用方据此断开该连接）"""
        try:
            await asyncio.wait_for(websocket.send_json(frame), timeout=SEND_TIMEOUT)
            return True
        except asyncio.TimeoutError:
            logger.warning("WebSocket 发送超时（%.1fs），判定为慢客户端并断开",
                           SEND_TIMEOUT)
            return False
        except Exception as e:
            logger.debug("WebSocket 发送失败: %s", e)
            return False

    async def broadcast(self, message: dict, *, config_id: str = ""):
        """广播 legacy 帧（与改造前逐字等价，供 legacy 连接使用）"""
        dead = []
        for websocket, state in list(self._connections.items()):
            if state.protocol != PROTOCOL_LEGACY:
                continue
            if config_id and not state.accepts_config(config_id):
                continue
            if not await self._send(websocket, message):
                dead.append(websocket)
        for conn in dead:
            self.disconnect(conn)

    async def broadcast_envelope(self, frame_type: str, payload: dict, *,
                                 config_id: str = ""):
        """广播 v1 信封（仅发给已协商 v1 的连接）"""
        dead = []
        for websocket, state in list(self._connections.items()):
            if state.protocol != PROTOCOL_V1:
                continue
            if config_id and not state.accepts_config(config_id):
                continue
            frame = build_frame(frame_type, payload,
                                config_id=config_id, seq=state.next_seq())
            if not await self._send(websocket, frame):
                dead.append(websocket)
        for conn in dead:
            self.disconnect(conn)

    async def broadcast_dual(self, legacy_message: dict, v1_type: str,
                             payload: dict, *, config_id: str = ""):
        """同一次事件按连接能力分别发 legacy 帧与 v1 信封（双写兼容）"""
        await self.broadcast(legacy_message, config_id=config_id)
        await self.broadcast_envelope(v1_type, payload, config_id=config_id)

    # ---- 既有语义的四个广播入口（现在都是双写） ----

    async def broadcast_log(self, level: str, message: str, config_id: str = ""):
        """广播日志消息（单条，非批处理路径使用）"""
        entry = {"type": "log", "level": level, "message": message,
                 "config_id": config_id}
        await self.broadcast_dual(
            entry, "log.batch", {"entries": [entry], "dropped": 0},
            config_id=config_id)

    async def broadcast_status(self, status: dict):
        """广播调度器状态变更"""
        config_id = status.get("config_id", "")
        await self.broadcast_dual(
            {"type": "status", "data": status}, "status", status,
            config_id=config_id)

    async def broadcast_task_state(self, task_data: dict):
        """广播任务状态变更"""
        config_id = task_data.get("config_id", "")
        await self.broadcast_dual(
            {"type": "task_state", "data": task_data}, "task.state", task_data,
            config_id=config_id)

    async def broadcast_snapshot(self, snapshot: dict):
        """广播调度器完整状态快照（合并 status + tasks，前端据此零轮询）"""
        config_id = snapshot.get("config_id", "")
        await self.broadcast_dual(
            {"type": "scheduler_snapshot", "data": snapshot},
            "scheduler.snapshot", snapshot, config_id=config_id)

    async def send_hello(self, websocket: WebSocket):
        """发送能力协商首帧（legacy 连接也会收到，未知 type 必须被忽略）"""
        from backend.runtime_info import get_client_version
        payload = {
            "server_version": get_client_version(),
            "protocol": PROTOCOL_VERSION,
            "caps": {"subscribe": True, "backpressure": True,
                     "log_batch_max": LOG_BATCH_MAX},
        }
        state = self._connections.get(websocket) or ConnState()
        frame = build_frame("hello", payload, seq=state.next_seq())
        await self._send(websocket, frame)

    async def send_error(self, websocket: WebSocket, code: str, message: str):
        state = self._connections.get(websocket) or ConnState()
        frame = build_frame("error", {"code": code, "message": message},
                            seq=state.next_seq())
        await self._send(websocket, frame)


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
        except Exception as e:
            # 不吞异常：日志投递失败必须留痕（旧实现 except: pass 会静默丢日志）
            logger.debug("WebSocket 日志入队失败: %s", e, exc_info=e)

    async def _periodic_flush(self):
        """每 30ms 刷新一次日志缓冲队列"""
        while True:
            await asyncio.sleep(0.03)
            try:
                await self._flush_batch()
            except Exception as e:
                logger.error("WebSocket 日志批量推送失败: %s", e, exc_info=e)

    async def _flush_batch(self):
        """将缓冲队列中的日志一次性广播出去（legacy 数组帧 + v1 信封双写）"""
        with self._batch_lock:
            if not self._batch:
                return
            batch = self._batch[:]
            self._batch.clear()

        # ---- legacy 帧：与改造前逐字等价 ----
        await manager.broadcast(["log", batch] if len(batch) > 1 else batch[0])

        # ---- v1 信封：单帧条数上限 + 丢弃计数（背压可见化）----
        entries = batch[:LOG_BATCH_MAX]
        dropped = len(batch) - len(entries)
        if dropped:
            logger.warning("单帧日志超过 %d 条，丢弃最旧的 %d 条（前端会收到 dropped 计数）",
                           LOG_BATCH_MAX, dropped)
        # 按 config_id 分组，便于连接级订阅过滤（同帧只含该连接关心的配置）
        grouped: dict[str, list[dict]] = {}
        for entry in entries:
            grouped.setdefault(entry.get("config_id", ""), []).append(entry)
        for config_id, items in grouped.items():
            await manager.broadcast_envelope(
                "log.batch", {"entries": items, "dropped": dropped},
                config_id=config_id)
        if not grouped:
            await manager.broadcast_envelope(
                "log.batch", {"entries": [], "dropped": dropped})


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


async def _handle_client_message(websocket: WebSocket, data: str) -> None:
    """处理客户端文本帧：`ping` 心跳与 `subscribe` 能力协商"""
    if data == "ping":
        await websocket.send_text("pong")
        return
    try:
        message = json.loads(data)
    except (TypeError, ValueError):
        logger.debug("忽略无法解析的客户端消息: %r", str(data)[:120])
        return
    if not isinstance(message, dict):
        return
    if message.get("type") == "subscribe":
        protocol = message.get("protocol", PROTOCOL_VERSION)
        config_ids = message.get("config_ids")
        manager.set_protocol(websocket, protocol, config_ids)
        # 协商完成后再发一次 hello，便于客户端确认服务端能力
        await manager.send_hello(websocket)
        return
    logger.debug("忽略未知客户端消息类型: %s", message.get("type"))


async def _serve(websocket: WebSocket) -> None:
    """两个 WS 端点的共同循环（Origin 校验 → 登记 → 收发 → 清理）"""
    if await _reject_if_origin_denied(websocket):
        return
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await _handle_client_message(websocket, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.warning("WebSocket 连接异常终止: %s", e, exc_info=e)
        manager.disconnect(websocket)


@router.websocket("/logs")
async def websocket_logs(websocket: WebSocket):
    """实时日志流"""
    await _serve(websocket)


@router.websocket("/status")
async def websocket_status(websocket: WebSocket):
    """任务/设备状态流"""
    await _serve(websocket)


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
