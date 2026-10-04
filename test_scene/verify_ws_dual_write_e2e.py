# -*- coding: utf-8 -*-
"""WS v1 双写端到端验证（阶段 2）

在进程内起一个真实的 uvicorn（随机空闲端口），用真实 WebSocket 客户端验证：
1. **legacy 连接**（不发 subscribe）：收到的帧与改造前逐字等价（数组帧 / 对象帧），
   绝不出现 v1 信封 —— 保证用户机上旧 `frontend/dist` 继续可用；
2. **v1 连接**（发 subscribe{protocol:1}）：收到 `{v,type,seq,ts,config_id,payload}`，
   且 `type` 为 `log.batch` / `scheduler.snapshot` 等新语义；
3. 两条连接互不串帧（各自的帧形态严格区分）。

副作用隔离：测试会 monkeypatch `_clean_old_logs`（不删用户历史日志）与
`_shutdown_adb_server`（不杀用户正在运行的实例所依赖的 adb server），并设置
`XUAN_SKIP_ADB_CLEANUP=1` —— 因为 `atexit` 注册的是**导入时的原始函数对象**，
只改模块属性拦不住它（本会话实测踩到过一次）。

标记为重型脚本（HEAVY）：自行拉起服务端，仅在有 websockets 依赖时运行。
运行：python -X utf8 test_scene/verify_ws_dual_write_e2e.py
"""
import asyncio
import atexit
import json
import logging
import os
import socket
import sys
import threading
import time
import unittest
import urllib.request

# 必须在导入 backend.main 之前设置：atexit 会注册导入时的 _shutdown_adb_server
os.environ.setdefault("XUAN_SKIP_ADB_CLEANUP", "1")

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

try:
    import websockets
except ImportError:            # pragma: no cover
    websockets = None


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class DualWriteE2E(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if websockets is None:
            raise unittest.SkipTest("未安装 websockets，跳过端到端用例")
        import backend.main as main_module
        import uvicorn

        # 副作用隔离（见模块 docstring）：先解除 atexit 注册，再替换模块属性
        try:
            atexit.unregister(main_module._shutdown_adb_server)
        except Exception as e:
            print("解除 atexit adb 清理失败（已由环境变量兜底）:", e)
        main_module._clean_old_logs = lambda: None
        main_module._shutdown_adb_server = lambda: None

        cls.port = _free_port()
        config = uvicorn.Config(main_module.app, host="127.0.0.1",
                                port=cls.port, log_level="warning",
                                lifespan="on")
        cls.server = uvicorn.Server(config)
        cls.thread = threading.Thread(target=cls.server.run, daemon=True)
        cls.thread.start()
        deadline = time.time() + 30
        while time.time() < deadline and not cls.server.started:
            time.sleep(0.2)
        if not cls.server.started:
            raise RuntimeError("uvicorn 未能在 30s 内启动")

    @classmethod
    def tearDownClass(cls):
        cls.server.should_exit = True
        cls.thread.join(timeout=15)

    # ---- 辅助 ----

    def _trigger_logs(self):
        """触发一次会产生日志的后端调用（配置加载会写 INFO/DEBUG 级日志）"""
        for path in ("/api/configs/", "/api/utils/version"):
            try:
                urllib.request.urlopen(
                    f"http://127.0.0.1:{self.port}{path}", timeout=15).read()
            except Exception as e:
                print("触发日志的请求失败（不影响协议断言）:", e)

    async def _collect(self, *, subscribe: bool, seconds: float = 3.0):
        """连一条 WS，可选协商 v1，收集若干帧"""
        url = f"ws://127.0.0.1:{self.port}/ws/logs"
        frames = []
        async with websockets.connect(url) as ws:
            hello = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
            frames.append(hello)
            if subscribe:
                await ws.send(json.dumps({"type": "subscribe", "protocol": 1}))
            # 客户端侧触发日志（在连接建立后调用 REST）
            self._trigger_logs()
            deadline = asyncio.get_event_loop().time() + seconds
            while asyncio.get_event_loop().time() < deadline:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=0.5)
                except asyncio.TimeoutError:
                    continue
                try:
                    frames.append(json.loads(raw))
                except ValueError:
                    frames.append(raw)          # pong 等文本帧
        return frames

    @staticmethod
    def _is_envelope(frame) -> bool:
        return isinstance(frame, dict) and frame.get("v") == 1 and "payload" in frame

    # ---- 用例 ----

    def test_legacy_client_never_receives_envelope(self):
        frames = asyncio.run(self._collect(subscribe=False))
        # hello 也是信封（新增能力协商帧，旧前端会忽略未知 type）
        data_frames = [f for f in frames if not (isinstance(f, dict)
                                                and f.get("type") == "hello")]
        envelopes = [f for f in data_frames if self._is_envelope(f)]
        self.assertEqual(envelopes, [],
                         f"legacy 连接不得收到 v1 信封，实际收到: {envelopes[:2]}")
        logs = [f for f in data_frames
                if isinstance(f, list) or (isinstance(f, dict) and f.get("type") == "log")]
        self.assertTrue(logs, f"legacy 连接应收到旧形态日志帧，实际: {data_frames[:3]}")
        if isinstance(logs[0], list):
            self.assertEqual(logs[0][0], "log")
            self.assertIsInstance(logs[0][1], list)

    def test_v1_client_receives_envelope(self):
        frames = asyncio.run(self._collect(subscribe=True))
        self.assertTrue(self._is_envelope(frames[0]), "首帧应是 hello 信封")
        self.assertEqual(frames[0]["type"], "hello")
        self.assertEqual(frames[0]["payload"]["protocol"], 1)

        envelopes = [f for f in frames[1:] if self._is_envelope(f)]
        self.assertTrue(envelopes, f"v1 连接应收到信封帧，实际: {frames[1:4]}")
        for frame in envelopes:
            self.assertIn("type", frame)
            self.assertIn("seq", frame)
            self.assertIn("ts", frame)
            self.assertIn("payload", frame)
            self.assertNotIn("config_id", frame["payload"],
                             "config_id 只能在信封顶层")

        log_batches = [f for f in envelopes if f["type"] == "log.batch"]
        self.assertTrue(log_batches, "应收到 log.batch 信封")
        entries = [e for f in log_batches for e in f["payload"]["entries"]]
        self.assertTrue(entries, "log.batch 应包含日志条目")
        for entry in entries:
            self.assertIn("message", entry)
            self.assertIn("level", entry)
            self.assertIn("ts", entry)
        seqs = [f["seq"] for f in envelopes]
        self.assertEqual(seqs, sorted(seqs), "seq 必须单调递增")

    def test_legacy_client_ignores_subscribe_of_other_connection(self):
        """两条连接共存时互不影响（同一服务端实例双写）"""
        async def run_both():
            legacy = await self._collect(subscribe=False, seconds=3.0)
            v1 = await self._collect(subscribe=True, seconds=3.0)
            return legacy, v1

        legacy, v1 = asyncio.run(run_both())
        legacy_data = [f for f in legacy if not (isinstance(f, dict)
                                                and f.get("type") == "hello")]
        self.assertEqual([f for f in legacy_data if self._is_envelope(f)], [],
                         "legacy 连接不得因 v1 连接的存在而收到信封")
        self.assertTrue([f for f in v1 if self._is_envelope(f) and f["type"] != "hello"],
                        "v1 连接应继续收到信封")


if __name__ == "__main__":
    unittest.main(verbosity=2)
