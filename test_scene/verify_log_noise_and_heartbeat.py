# -*- coding: utf-8 -*-
"""验证日志降噪与超时监视器心跳健壮性。

背景（两项遗留问题）：
1. `Operationer` 的点击/搜索日志按"次"输出且为 INFO——一次 `search_and_click` 会先
   dump 整份搜索清单（1+N 条），`_search_loop` 每轮又对列表每项调一次 `click_and_wait`
   （每项每轮再一条 `[Click]`）；长循环（如 `while not search_and_click(...)`）会把日志
   刷满（单配置单日 Xuan.log 可达 2MB+）。此外 `LD.py` 把同一句配置提示连续打印 5 次。
2. `BaseTask.transition()` 里 `watchdog.heartbeat()` 的异常被 `except: pass` 静默吞掉，
   而心跳是"场景停滞"判定的唯一时间基准——静默失败会导致误判卡死（进而停任务/重启
   游戏/重启模拟器），且日志里没有任何线索。

本脚本覆盖（全部离线，不依赖设备/模拟器）：
A. 日志降噪
 1. `_log_click`：同一任务连续点击同一元素只首条 INFO，其余 DEBUG；换元素/换任务重新 INFO；
 2. `search_and_click` / `search_and_detect` 的搜索清单降为 DEBUG（INFO 不再出现）；
 3. `LD.py` 的配置提示不再 5 连发（源码级断言，防回退）。
B. 心跳健壮性
 4. `heartbeat` 失败不外抛：首次失败记 ERROR（含 traceback）并临时关闭场景停滞判定；
 5. 后续失败只计数（不重复刷屏）；`detach_task` 汇总 WARNING；
 6. 心跳失效后跳过场景停滞判定（不误报卡死），画面静止类判定不受影响；
 7. `attach_task` 重置心跳健康状态；
 8. `BaseTask.transition()` 的心跳兜底只提示一次，且不影响任务流程（不静默）。
"""
import logging
import os
import sys
import time
import unittest
import unittest.mock
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.core.legacy.Operationer import Operationer  # noqa: E402
from backend.core.legacy.Task.BaseTask import BaseTask  # noqa: E402
from backend.services.watchdog_service import (  # noqa: E402
    FreezeLevel,
    TimeoutWatchdog,
)

TZ = ZoneInfo("Asia/Shanghai")
LOG = "verify.lognoise"


class _FakeConfig:
    """最小 Config 替身：仅提供 get_config（监视器只读配置项）。"""

    def __init__(self, **overrides):
        self.values = overrides

    def get_config(self, key, default=None):
        return self.values.get(key, default)


class _FakeTask:
    """供监视器 attach/detach 使用的最小任务替身。"""

    def __init__(self, name="编号任务"):
        self.task_name = name

    def attach_watchdog(self, watchdog):
        self.watchdog = watchdog

    def detach_watchdog(self):
        self.watchdog = None


def _make_operationer():
    op = object.__new__(Operationer)
    op.logger = logging.getLogger(LOG)
    op.task_name = "编号任务"
    return op


class OperationerLogNoiseTest(unittest.TestCase):
    """A. 点击/搜索日志降噪"""

    def test_log_click_dedups_consecutive_click(self):
        op = _make_operationer()
        with self.assertLogs(LOG, level=logging.DEBUG) as cm:
            for _ in range(3):
                op._log_click("确定")
            op._log_click("取消")
            op._log_click("取消")
        info = [r.getMessage() for r in cm.records if r.levelno == logging.INFO]
        debug = [r.getMessage() for r in cm.records if r.levelno == logging.DEBUG]
        self.assertEqual(info, ["[Click] [确定]", "[Click] [取消]"],
                         "连续点击同一元素只首条 INFO，换元素再 INFO")
        self.assertEqual(len(debug), 3, "重复点击降为 DEBUG，文件日志仍留完整明细")

    def test_log_click_resets_on_task_change(self):
        op = _make_operationer()
        with self.assertLogs(LOG, level=logging.INFO) as cm:
            op._log_click("确定")
            op.task_name = "另一个任务"
            op._log_click("确定")
        self.assertEqual(len(cm.records), 2, "换任务后同一元素应重新输出 INFO")

    def test_search_dump_is_debug(self):
        op = _make_operationer()
        op._search_loop = lambda *a, **k: 0     # 只验证清单输出，不跑真实搜索
        with self.assertLogs(LOG, level=logging.DEBUG) as cm:
            op.search_and_click(["元素A", "元素B"], [])
            op.search_and_detect(["元素C"], [])
        self.assertEqual([r.getMessage() for r in cm.records
                          if r.levelno == logging.INFO], [],
                         "搜索清单不再以 INFO 输出")
        messages = [r.getMessage() for r in cm.records]
        self.assertIn("元素点击搜索内容：", messages)
        self.assertIn("元素检测搜索内容：", messages)
        self.assertEqual(len(messages), 5, "标题 2 条 + 清单项 3 条，全部 DEBUG")

    def test_ld_hint_not_repeated(self):
        """LD.py 的两处配置提示原为 5 连发，现应各只 1 条（源码级防回退）"""
        source = (Path(_PROJECT_ROOT)
                  / "backend/core/legacy/Screen/LD.py").read_text(encoding="utf-8")
        self.assertEqual(source.count("请仔细检查LD安装路径配置"), 1)
        self.assertEqual(source.count("请仔细检查雷电实例索引配置"), 1)


class WatchdogHeartbeatTest(unittest.TestCase):
    """B. 超时监视器心跳健壮性"""

    def setUp(self):
        self.watchdog = TimeoutWatchdog(
            config=_FakeConfig(**{"超时检测-启用": True}),
            device=None,
            operationer=None,
            logger=logging.getLogger(LOG),
        )
        self.task = _FakeTask()

    def _fail_heartbeat(self):
        """让 heartbeat 内部抛错（模拟监视器状态异常）"""
        with unittest.mock.patch(
                "backend.services.watchdog_service.time.monotonic",
                side_effect=RuntimeError("monotonic 故障")):
            return self.watchdog.heartbeat("主场景")

    def test_first_failure_logs_error_and_disables_scene_stuck(self):
        self.watchdog.attach_task(self.task)
        with self.assertLogs(LOG, level=logging.ERROR) as cm:
            self._fail_heartbeat()          # 不外抛（不破坏任务流程）
        self.assertIn("心跳上报失败", "\n".join(cm.output))
        self.assertEqual(self.watchdog._heartbeat_fail_count, 1)
        self.assertFalse(self.watchdog._scene_stuck_enabled,
                         "心跳失效后必须关闭场景停滞判定（避免误判卡死）")

    def test_repeated_failures_do_not_spam(self):
        self.watchdog.attach_task(self.task)
        with self.assertLogs(LOG, level=logging.ERROR):
            self._fail_heartbeat()
        with self.assertNoLogs(LOG, level=logging.DEBUG):
            self._fail_heartbeat()
            self._fail_heartbeat()
        self.assertEqual(self.watchdog._heartbeat_fail_count, 3,
                         "后续失败只计数，不重复输出日志（避免刷屏）")

    def test_detach_reports_failure_summary(self):
        self.watchdog.attach_task(self.task)
        with self.assertLogs(LOG, level=logging.ERROR):
            self._fail_heartbeat()
        with self.assertLogs(LOG, level=logging.WARNING) as cm:
            self.watchdog.detach_task(self.task)
        self.assertIn("心跳上报失败 1 次", "\n".join(cm.output))

    def test_attach_resets_heartbeat_state(self):
        self.watchdog.attach_task(self.task)
        with self.assertLogs(LOG, level=logging.ERROR):
            self._fail_heartbeat()
        self.watchdog.attach_task(self.task)
        self.assertEqual(self.watchdog._heartbeat_fail_count, 0)
        self.assertTrue(self.watchdog._scene_stuck_enabled)

    def test_scene_stuck_skipped_when_heartbeat_failed(self):
        """心跳失效后跳过场景停滞判定；画面静止类判定不受影响"""
        frame = np.zeros((10, 10, 3), dtype=np.uint8)
        self.watchdog._capture_frame = lambda: frame
        events = []
        self.watchdog._raise = lambda level, detail="": events.append(level)

        def _prepare(enabled: bool):
            now = time.monotonic()
            with self.watchdog._lock:
                self.watchdog._current_task = self.task
                self.watchdog._awaiting_recovery = False
                self.watchdog._grace_until = 0.0
                self.watchdog._last_scene = "主场景"
                self.watchdog._scene_since = now - 1000     # 远超 180s 阈值
                self.watchdog._last_frame = None            # 首帧 → 静止秒数 0
                self.watchdog._static_since = now
                self.watchdog._scene_stuck_enabled = enabled

        _prepare(True)
        self.watchdog._check_once()
        self.assertEqual(events, [FreezeLevel.SCENE_STUCK],
                         "正常情况应能判定场景停滞")

        events.clear()
        _prepare(False)
        self.watchdog._check_once()
        self.assertEqual(events, [],
                         "心跳失效后不得再判定场景停滞（避免误判卡死→重启游戏/模拟器）")


class _FailingWatchdog:
    """心跳固定失败，用于验证 BaseTask 侧的兜底提示"""

    def __init__(self):
        self.calls = 0

    def heartbeat(self, scene_name=None):
        self.calls += 1
        raise RuntimeError("心跳故障")


class _Scene:
    def __init__(self, name):
        self.name = name


class _FakeRecognizer:
    def scene(self, screenshot, bool_debug=False, hint=None, allow_full_scan=True):
        return _Scene("主场景")


class _TransitionOperationer:
    def __init__(self):
        self.next_scene = None
        self.current_scene = None
        self.recognizer = _FakeRecognizer()

    def screen_cap(self):
        return object()


def _transition_handler(task):
    return False


class _TransitionTask(BaseTask):
    """只跑 transition() 的任务壳（验证心跳兜底）"""

    source_scene = "主场景"

    def __init__(self):
        self.task_name = "编号任务"
        self.logger = logging.getLogger(LOG)
        self.watchdog = _FailingWatchdog()
        self.operationer = _TransitionOperationer()
        self.transition_func = {"主场景": _transition_handler}
        self.last_unregistered_scene_time = None
        self.transition_return = ""


class TransitionHeartbeatFallbackTest(unittest.TestCase):
    """B8. transition() 的心跳兜底不再静默，且只提示一次"""

    def test_fallback_warns_once_and_keeps_task_running(self):
        task = _TransitionTask()
        with self.assertLogs(LOG, level=logging.DEBUG) as cm:
            task.transition()
            task.transition()
        warnings = [r for r in cm.records if r.levelno == logging.WARNING
                    and "心跳上报失败" in r.getMessage()]
        self.assertEqual(len(warnings), 1, "心跳每轮调用，兜底提示必须去重")
        self.assertEqual(task.watchdog.calls, 2, "兜底不影响任务流程（仍每轮上报）")


if __name__ == "__main__":
    unittest.main(verbosity=2)
