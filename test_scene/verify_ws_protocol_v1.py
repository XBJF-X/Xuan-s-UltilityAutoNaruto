# -*- coding: utf-8 -*-
"""WS v1 统一信封回归（阶段 2）

覆盖 docs/refactor-plan-2026.md §7.9 的协议约定：
1. 信封不变式：`v/type/seq/ts/config_id/payload`，**config_id 只在顶层**；
2. `ConnState.seq` 每连接单调递增；
3. **双写兼容**：legacy 连接收到与改造前逐字等价的旧帧（含 `["log", batch]` 数组帧），
   只有协商过 `subscribe{protocol:1}` 的连接才收到信封；
4. `log.batch` 单帧上限（LOG_BATCH_MAX=200）与 `dropped` 计数；
5. 订阅过滤：带 `config_ids` 的 v1 连接只收对应配置的帧；
6. `subscribe` 客户端帧解析（含非法 JSON 不抛异常）；
7. 慢客户端：发送超时即断开（不阻塞整轮广播）。

全部离线：用假 WebSocket 对象替代真实连接。
"""
import asyncio
import json
import logging
import os
import sys
import unittest

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.api import ws as ws_mod  # noqa: E402


class FakeWebSocket:
    """最小 WebSocket 替身：记录 send_json 的帧，可模拟发送超时"""

    def __init__(self, *, hang: bool = False):
        self.frames: list = []
        self.texts: list[str] = []
        self.accepted = False
        self.closed_codes: list[int] = []
        self.headers: dict = {}
        self.hang = hang

    async def accept(self):
        self.accepted = True

    async def send_json(self, frame):
        if self.hang:
            await asyncio.sleep(30)      # 触发 SEND_TIMEOUT
        self.frames.append(frame)

    async def send_text(self, text):
        self.texts.append(text)

    async def close(self, code: int = 1000):
        self.closed_codes.append(code)


def run(coro):
    return asyncio.run(coro)


class BuildFrameTest(unittest.TestCase):

    def test_envelope_shape(self):
        frame = ws_mod.build_frame("scheduler.snapshot", {"running": True},
                                   config_id="Config_1", seq=7, ts=1234)
        self.assertEqual(set(frame), {"v", "type", "seq", "ts", "config_id", "payload"})
        self.assertEqual(frame["v"], 1)
        self.assertEqual(frame["seq"], 7)
        self.assertEqual(frame["ts"], 1234)
        self.assertEqual(frame["config_id"], "Config_1")
        self.assertEqual(frame["payload"], {"running": True})
        # config_id 不得出现在 payload 内（协议不变式）
        self.assertNotIn("config_id", frame["payload"])

    def test_ts_defaults_to_now(self):
        frame = ws_mod.build_frame("hello", {})
        self.assertGreater(frame["ts"], 1_600_000_000_000)

    def test_protocol_constants(self):
        self.assertEqual(ws_mod.PROTOCOL_VERSION, 1)
        self.assertEqual(ws_mod.PROTOCOL_LEGACY, 0)
        self.assertEqual(ws_mod.LOG_BATCH_MAX, 200)


class ConnStateTest(unittest.TestCase):

    def test_seq_monotonic_per_connection(self):
        state = ws_mod.ConnState()
        self.assertEqual([state.next_seq() for _ in range(3)], [1, 2, 3])

    def test_subscription_filter(self):
        state = ws_mod.ConnState()
        self.assertTrue(state.accepts_config("Config_1"), "空订阅=全部")
        state.config_ids = {"Config_2"}
        self.assertTrue(state.accepts_config("Config_2"))
        self.assertFalse(state.accepts_config("Config_1"))
        self.assertTrue(state.accepts_config(""),
                        "无归属（程序级）日志不属于任何配置，始终放行")


class DualWriteTest(unittest.TestCase):

    def setUp(self):
        self.manager = ws_mod.ConnectionManager()
        self.legacy = FakeWebSocket()
        self.v1 = FakeWebSocket()
        run(self._connect())

    async def _connect(self):
        await self.manager.connect(self.legacy)
        await self.manager.connect(self.v1)
        self.legacy.frames.clear()          # 丢弃 hello
        self.v1.frames.clear()
        self.manager.set_protocol(self.v1, 1)

    def test_legacy_gets_legacy_frame_only(self):
        run(self.manager.broadcast_snapshot({"running": True, "config_id": "Config_1"}))
        self.assertEqual(len(self.legacy.frames), 1)
        self.assertEqual(self.legacy.frames[0]["type"], "scheduler_snapshot")
        self.assertIn("data", self.legacy.frames[0])
        self.assertNotIn("v", self.legacy.frames[0])

    def test_v1_gets_envelope_only(self):
        run(self.manager.broadcast_snapshot({"running": True, "config_id": "Config_1"}))
        self.assertEqual(len(self.v1.frames), 1)
        frame = self.v1.frames[0]
        self.assertEqual(frame["v"], 1)
        self.assertEqual(frame["type"], "scheduler.snapshot")
        self.assertEqual(frame["config_id"], "Config_1")
        self.assertEqual(frame["payload"]["running"], True)
        self.assertGreaterEqual(frame["seq"], 1, "v1 帧必须带 seq")

    def test_task_state_type_mapping(self):
        run(self.manager.broadcast_task_state({"name": "消耗体力", "config_id": "Config_1"}))
        self.assertEqual(self.legacy.frames[0]["type"], "task_state")
        self.assertEqual(self.v1.frames[0]["type"], "task.state")

    def test_seq_increments_across_events(self):
        for _ in range(3):
            run(self.manager.broadcast_status({"running": True, "config_id": "Config_1"}))
        seqs = [f["seq"] for f in self.v1.frames]
        self.assertEqual(seqs, sorted(seqs), "seq 必须单调递增")
        self.assertEqual(len(set(seqs)), 3, "每帧一个新 seq（不得复用）")

    def test_legacy_log_frame_kept_verbatim(self):
        """legacy 连接必须仍收到 `["log", batch]` / 单条对象（旧 dist 依赖）"""
        handler = ws_mod.WebSocketLogHandler()
        handler._loop = _RunningLoopStub()
        for i in range(2):
            handler.emit(_record(f"第{i}条"))
        # 直接把当前全局 manager 换成本测试的实例（_flush_batch 用的是全局单例）
        original = ws_mod.manager
        ws_mod.manager = self.manager
        try:
            run(handler._flush_batch())
        finally:
            ws_mod.manager = original
        legacy_frame = self.legacy.frames[0]
        self.assertIsInstance(legacy_frame, list)
        self.assertEqual(legacy_frame[0], "log")
        self.assertEqual(len(legacy_frame[1]), 2)
        v1_frame = self.v1.frames[0]
        self.assertEqual(v1_frame["type"], "log.batch")
        self.assertEqual(len(v1_frame["payload"]["entries"]), 2)
        self.assertEqual(v1_frame["payload"]["dropped"], 0)

    def test_single_log_uses_object_frame_for_legacy(self):
        handler = ws_mod.WebSocketLogHandler()
        handler._loop = _RunningLoopStub()
        handler.emit(_record("单条"))
        original = ws_mod.manager
        ws_mod.manager = self.manager
        try:
            run(handler._flush_batch())
        finally:
            ws_mod.manager = original
        legacy_frame = self.legacy.frames[0]
        self.assertIsInstance(legacy_frame, dict)
        self.assertEqual(legacy_frame["type"], "log")

    def test_log_batch_truncates_with_dropped(self):
        handler = ws_mod.WebSocketLogHandler()
        handler._loop = _RunningLoopStub()
        for i in range(ws_mod.LOG_BATCH_MAX + 5):
            handler.emit(_record(f"第{i}条"))
        original = ws_mod.manager
        ws_mod.manager = self.manager
        try:
            run(handler._flush_batch())
        finally:
            ws_mod.manager = original
        total_entries = sum(len(f["payload"]["entries"]) for f in self.v1.frames
                            if f.get("type") == "log.batch")
        self.assertEqual(total_entries, ws_mod.LOG_BATCH_MAX, "单帧条数应被截断到上限")
        dropped = {f["payload"]["dropped"] for f in self.v1.frames
                   if f.get("type") == "log.batch"}
        self.assertEqual(dropped, {5}, "dropped 应报告被丢弃的条数")

    def test_subscription_filters_v1_frames(self):
        self.manager.set_protocol(self.v1, 1, ["Config_2"])
        run(self.manager.broadcast_snapshot({"running": True, "config_id": "Config_1"}))
        self.assertEqual(self.v1.frames, [], "订阅 Config_2 的连接不该收到 Config_1 的快照")
        run(self.manager.broadcast_snapshot({"running": True, "config_id": "Config_2"}))
        self.assertEqual(len(self.v1.frames), 1)

    def test_slow_client_is_disconnected(self):
        slow = FakeWebSocket(hang=True)
        run(self.manager.connect(slow))
        self.manager.set_protocol(slow, 1)
        original_timeout = ws_mod.SEND_TIMEOUT
        ws_mod.SEND_TIMEOUT = 0.05
        try:
            run(self.manager.broadcast_status({"running": True, "config_id": "Config_1"}))
        finally:
            ws_mod.SEND_TIMEOUT = original_timeout
        self.assertNotIn(slow, self.manager.active_connections,
                         "发送超时的慢客户端应被断开")
        self.assertEqual(self.manager.connection_count(), 2)


class ClientMessageTest(unittest.TestCase):

    def setUp(self):
        self.manager = ws_mod.ConnectionManager()
        self.original = ws_mod.manager
        ws_mod.manager = self.manager
        self.ws = FakeWebSocket()
        run(self.manager.connect(self.ws))

    def tearDown(self):
        ws_mod.manager = self.original

    def test_ping_pong(self):
        run(ws_mod._handle_client_message(self.ws, "ping"))
        self.assertEqual(self.ws.texts, ["pong"])

    def test_subscribe_switches_protocol(self):
        run(ws_mod._handle_client_message(
            self.ws, json.dumps({"type": "subscribe", "protocol": 1})))
        state = self.manager.get_state(self.ws)
        self.assertEqual(state.protocol, ws_mod.PROTOCOL_V1)
        self.assertEqual(self.ws.frames[-1]["type"], "hello", "协商后应回 hello 确认")

    def test_subscribe_with_config_ids(self):
        run(ws_mod._handle_client_message(
            self.ws, json.dumps({"type": "subscribe", "protocol": 1,
                                 "config_ids": ["Config_3"]})))
        self.assertEqual(self.manager.get_state(self.ws).config_ids, {"Config_3"})

    def test_invalid_json_is_ignored(self):
        run(ws_mod._handle_client_message(self.ws, "{not json"))
        self.assertEqual(self.manager.get_state(self.ws).protocol, ws_mod.PROTOCOL_LEGACY)

    def test_unknown_type_is_ignored(self):
        run(ws_mod._handle_client_message(self.ws, json.dumps({"type": "nope"})))
        self.assertEqual(self.manager.get_state(self.ws).protocol, ws_mod.PROTOCOL_LEGACY)

    def test_hello_send_failure_does_not_raise(self):
        broken = FakeWebSocket()
        broken.send_json = _raise_io
        run(self.manager.send_hello(broken))


class ServerSourceInvariantTest(unittest.TestCase):
    """源码级防回退：legacy 帧形态与双写路径不得被删"""

    def setUp(self):
        self.src = open(os.path.join(_PROJECT_ROOT, "backend", "api", "ws.py"),
                        encoding="utf-8").read()

    def test_legacy_array_frame_preserved(self):
        self.assertIn('["log", batch] if len(batch) > 1 else batch[0]', self.src)

    def test_dual_write_present(self):
        self.assertIn("broadcast_dual", self.src)
        self.assertIn("broadcast_envelope", self.src)

    def test_origin_guard_still_applied(self):
        # 两个端点统一走 _serve()，Origin 校验在 _serve 内（保持一处实现）
        self.assertEqual(self.src.count("if await _reject_if_origin_denied(websocket):"), 1)
        self.assertEqual(self.src.count("await _serve(websocket)"), 2)
        self.assertIn("await websocket.close(code=1008)", self.src)


# ---- 测试辅助 ----

class _RunningLoopStub:
    """让 WebSocketLogHandler.emit 认为事件循环可用（实际不发帧）"""

    def is_running(self):
        return True


async def _raise_io(_frame):
    raise OSError("connection reset")


def _record(message: str):
    record = logging.LogRecord(
        name="SchedulerService_Config_1.Operationer", level=logging.INFO,
        pathname=__file__, lineno=1, msg=message, args=(), exc_info=None)
    record.config_id = "Config_1"
    return record


if __name__ == "__main__":
    unittest.main(verbosity=2)
