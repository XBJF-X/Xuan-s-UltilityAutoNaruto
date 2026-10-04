# -*- coding: utf-8 -*-
"""验证日志实时推送 payload 携带服务端时间戳（日志面板“同一行出现两次”的根因修复）。

问题现象：前端日志面板中同一条日志连续出现两次，而后端日志文件（Xuan.log）里每条
只出现一次 —— 即任务并没有执行两次，重复发生在前端展示环节。

根因：LogPanel 在挂载/切换配置/WebSocket 重连时会调用
``GET /api/utils/log-history`` 拉取历史日志并 ``mergeHistory`` 合并；实时日志此前用
``Date.now()``（浏览器接收时刻）作时间戳，历史日志用日志文件解析出的秒级时间戳，
两者不同源 → 去重键 ``(ts + message)`` 不匹配 → 已展示过的日志被历史条目再插一遍。

本脚本验证修复两端契约（前端去重逻辑见 test_scene/verify_log_dedupe.ts）：
1. ``WebSocketLogHandler.emit`` 的 payload 携带 ``ts``（= ``record.created`` 毫秒，服务端时间）；
2. 该 ts 与 ``parse_log_lines``（历史日志）解析出的秒级时间戳落在同一秒，
   即前端 ``mergeHistory`` 的「floor(ts/1000) + 级别 + logger + 消息」比对键完全一致。
"""
import logging
import os
import sys
import types
import unittest

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.api.ws import WebSocketLogHandler
from backend.api.utils import parse_log_lines
from backend.log_setup import DEFAULT_FORMAT, DATE_FORMAT

LOGGER_NAME = "SchedulerService_Config_2.秘境探险"


def _handler() -> WebSocketLogHandler:
    handler = WebSocketLogHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    # emit 只要求事件循环处于运行状态：单测用最小替身，避免真的起事件循环
    handler._loop = types.SimpleNamespace(is_running=lambda: True)
    return handler


def _record(msg="挑战券为 5 ，继续执行", name=LOGGER_NAME,
            level=logging.INFO) -> logging.LogRecord:
    return logging.LogRecord(name=name, level=level, pathname=__file__, lineno=1,
                             msg=msg, args=(), exc_info=None)


class WsLogPayloadTest(unittest.TestCase):
    """实时日志 payload：携带服务端时间戳，且与历史日志条目同秒对齐"""

    def test_emit_payload_carries_server_ts(self):
        handler = _handler()
        record = _record()
        handler.emit(record)
        self.assertEqual(len(handler._batch), 1)
        item = handler._batch[0]
        self.assertEqual(item["type"], "log")
        self.assertEqual(item["level"], "INFO")
        self.assertEqual(item["config_id"], "Config_2")
        self.assertEqual(item["logger_name"], LOGGER_NAME)
        self.assertEqual(item["ts"], int(record.created * 1000),
                         "payload 应携带 record.created 的毫秒时间戳")

    def test_emit_without_running_loop_keeps_batch_empty(self):
        handler = _handler()
        handler._loop = None
        handler.emit(_record())
        self.assertEqual(handler._batch, [], "无事件循环时不应缓存日志")

    def test_ts_aligns_with_history_log_second(self):
        """同一秒内：实时 ts 与历史日志解析 ts 的秒级比对键一致 → 前端去重可命中"""
        handler = _handler()
        record = _record()
        handler.emit(record)
        live_ts = handler._batch[0]["ts"]

        # 用与文件 handler 相同的格式/日期格式渲染该记录，模拟 Xuan.log 中的一行
        filed = logging.Formatter(DEFAULT_FORMAT, DATE_FORMAT).format(record)
        entries = parse_log_lines(filed)
        self.assertEqual(len(entries), 1)
        history = entries[0]
        self.assertEqual(history["level"], "INFO")
        self.assertEqual(history["logger_name"], LOGGER_NAME)
        self.assertEqual(history["message"], "挑战券为 5 ，继续执行")
        self.assertEqual(history["ts"] // 1000, live_ts // 1000,
                         "实时与历史时间戳应落在同一秒（前端 mergeHistory 比对键对齐）")

    def test_config_id_extraction(self):
        self.assertEqual(
            WebSocketLogHandler._extract_config_id("SchedulerService_Config_12"),
            "Config_12")
        self.assertEqual(
            WebSocketLogHandler._extract_config_id("Service_Config_1.Operationer"),
            "Config_1")
        self.assertEqual(WebSocketLogHandler._extract_config_id("WebSocket"), "")
        # 副本配置：id 形如 Config_1_副本 / Config_1_副本2（config_service.duplicate_config），
        # 旧的非锚定正则会把它们错判成 Config_1 → 副本日志串到源配置、副本面板空白
        self.assertEqual(
            WebSocketLogHandler._extract_config_id("SchedulerService_Config_1_副本"),
            "Config_1_副本")
        self.assertEqual(
            WebSocketLogHandler._extract_config_id("SchedulerService_Config_1_副本2"),
            "Config_1_副本2")
        self.assertEqual(
            WebSocketLogHandler._extract_config_id("ConfigService.Config_3_副本.Device"),
            "Config_3_副本")

    def test_config_id_explicit_binding_wins(self):
        """显式绑定（record.config_id）优先于 logger 名正则（含副本 id 的正确性保证）"""
        record = _record()
        record.config_id = "Config_9_副本"
        self.assertEqual(WebSocketLogHandler._extract_config_id(record), "Config_9_副本")

        handler = _handler()
        handler.emit(record)
        self.assertEqual(handler._batch[0]["config_id"], "Config_9_副本")

    def test_bind_config_id_marks_records(self):
        """bind_config_id 给经过该 logger 的记录打标（子 logger 走正则兜底）"""
        from backend.log_setup import bind_config_id

        logger = logging.getLogger("VerifyBind")
        logger.handlers = []
        logger.propagate = False
        logger.setLevel(logging.INFO)   # 根 logger 默认 WARNING，不设级别 INFO 会被丢弃
        bind_config_id(logger, "Config_5_副本")
        captured = []

        class _Capture(logging.Handler):
            def emit(self, r):
                captured.append(r)

        logger.addHandler(_Capture())
        logger.info("hello")
        self.assertEqual(getattr(captured[0], "config_id", ""), "Config_5_副本")


if __name__ == "__main__":
    unittest.main(verbosity=2)
