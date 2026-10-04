# -*- coding: utf-8 -*-
"""验证「显式等待 / 进展信号 → 卡死判据改为无进展」与任务级阈值补丁的撤销。

背景（2026-09-16 21:10~21:15 叛忍来袭日志）：
    任务在「叛忍来袭-即将开始」合法等待活动开启，停在同一个场景超过 180 秒 →
    被判 [SCENE_STUCK] → 停任务 + 救援（救援本身还必然失败）。当时的临时办法是把
    整任务的 scene_stuck_seconds 抬到 350s（更多玩法 600s），粒度粗、靠人工调参，
    且真实卡死也要等 350/600 秒才发现。

现在的判据是**无进展**而非"场景名未变"：
    - 任务显式声明等待（`declare_waiting` / `wait_for`，作用域限于该场景）；
    - 或**连点进行中**（连点＝任务在持续操作，画面在变而场景名不变，如整局对局）；
    以上两种情形改用「超时检测-等待超时秒」（默认 1800s）；其余情况仍按任务/全局
    停滞阈值（默认 180s）——
    因此"合法等待"不再被误杀，真实卡死的发现时间也回到 180s。

本脚本覆盖（全部离线，不依赖设备/配置/模拟器）：
  1. 等待状态下 1799s 不告警、1801s 告警（告警详情写明"等待「…」"）；
  2. 「超时检测-等待超时秒」可配、非法值回退默认并告警一次；
  3. 非等待状态仍按 180s（回归）；等待期间画面静止仍判 GAME_FROZEN（真卡死不漏）；
  4. 场景切换 / end_wait / 告警处理完毕 / attach / detach / stop 都会清除等待声明；
  5. `BaseTask.declare_waiting` 上报等待并限定作用域；离开该场景自动失效；
  6. **连点进行中**自动视为等待，连点停止后恢复普通判定；
  7. `wait_for`：条件满足 / 超时 / 条件异常不打死任务 / 停止信号抛 Stop；
  8. 旧式监视器（heartbeat 只接受场景名）→ 自动退回旧调用、不抛异常；
  9. 真实任务类：更多玩法（匹配中/匹配成功）与叛忍来袭（即将开始）声明了等待，
     且两者都不再设置任务级 scene_stuck_seconds。

运行：.venv\\Scripts\\python.exe -X utf8 test_scene\\verify_wait_and_progress.py
"""
import logging
import os
import sys
import threading
import time
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest import mock
from zoneinfo import ZoneInfo

import numpy as np

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.core.legacy.Exceptions import Stop  # noqa: E402
from backend.core.legacy.Task.BaseTask import BaseTask  # noqa: E402
from backend.core.legacy.Task.GengDuoWanFa import GengDuoWanFa  # noqa: E402
from backend.core.legacy.Task.PanRenLaiXi import PanRenLaiXi  # noqa: E402
from backend.core.legacy.Task.schedule import AnyTime  # noqa: E402
from backend.services.watchdog_service import (  # noqa: E402
    DEFAULT_SCENE_STUCK_SECONDS,
    DEFAULT_WAIT_TIMEOUT_SECONDS,
    FreezeLevel,
    TimeoutWatchdog,
)

TZ = ZoneInfo("Asia/Shanghai")
LOG = "verify.wait"
SCENE = "叛忍来袭-即将开始"


class _FakeConfig:
    def __init__(self, **values):
        self.values = values

    def get_config(self, key, default=None):
        return self.values.get(key, default)


def _watchdog(**values):
    values.setdefault("超时检测-启用", True)
    return TimeoutWatchdog(
        config=_FakeConfig(**values), device=None, operationer=None,
        logger=logging.getLogger(LOG))


class WatchdogWaitThresholdTest(unittest.TestCase):
    """等待状态的停滞判定：阈值、可配性、与画面静止判定的关系。"""

    def setUp(self):
        self.frame = np.zeros((10, 10, 3), dtype=np.uint8)

    def _watchdog(self, **values):
        watchdog = _watchdog(**values)
        events = []
        watchdog._raise = lambda level, detail="", _e=events: _e.append((level, detail))
        watchdog._probe_and_still_static = lambda reference: True
        watchdog._capture_frame = lambda: self.frame
        watchdog._events = events
        return watchdog

    def _prepare(self, watchdog, scene_age, static_age=0.0, waiting=False,
                 desc="", scene=SCENE):
        now = time.monotonic()
        with watchdog._lock:
            watchdog._current_task = SimpleNamespace(task_name="叛忍来袭")
            watchdog._awaiting_recovery = False
            watchdog._grace_until = 0.0
            watchdog._last_scene = scene
            watchdog._scene_since = now - scene_age
            watchdog._last_frame = watchdog._normalize_frame(self.frame)
            watchdog._static_since = now - static_age
            watchdog._scene_stuck_enabled = True
            watchdog._last_game_restart = 0.0
            watchdog._capture_fail_count = 0
            watchdog._waiting = waiting
            watchdog._waiting_desc = desc
            watchdog._waiting_since = now
        watchdog._events.clear()
        return watchdog

    def _levels(self, watchdog):
        return [level for level, _ in watchdog._events]

    def test_waiting_uses_wait_timeout(self):
        watchdog = self._prepare(self._watchdog(), scene_age=181,
                                 waiting=True, desc="叛忍来袭即将开启")
        watchdog._check_once()
        self.assertEqual(self._levels(watchdog), [],
                         "等待声明期间不得按 180s 判场景停滞")

        self._prepare(watchdog, scene_age=DEFAULT_WAIT_TIMEOUT_SECONDS + 1,
                      waiting=True, desc="叛忍来袭即将开启")
        watchdog._check_once()
        self.assertEqual(self._levels(watchdog), [FreezeLevel.SCENE_STUCK],
                         "等待超过「等待超时」仍要告警（等待不是无限豁免）")
        self.assertIn("等待「叛忍来袭即将开启」", watchdog._events[-1][1])

    def test_wait_timeout_configurable_and_invalid_fallback(self):
        watchdog = self._prepare(self._watchdog(**{"超时检测-等待超时秒": 60}),
                                 scene_age=61, waiting=True, desc="等匹配")
        watchdog._check_once()
        self.assertEqual(self._levels(watchdog), [FreezeLevel.SCENE_STUCK])
        self.assertIn("60 秒", watchdog._events[-1][1])

        watchdog = _watchdog(**{"超时检测-等待超时秒": "abc"})
        with self.assertLogs(LOG, level=logging.WARNING) as cm:
            self.assertEqual(watchdog._wait_timeout_seconds(),
                             DEFAULT_WAIT_TIMEOUT_SECONDS)
        self.assertTrue([r for r in cm.records
                         if "超时检测-等待超时秒" in r.getMessage()],
                        "非法配置必须留痕（不静默回退）")

    def test_non_waiting_keeps_180_seconds(self):
        watchdog = self._prepare(self._watchdog(), scene_age=181)
        watchdog._check_once()
        self.assertEqual(self._levels(watchdog), [FreezeLevel.SCENE_STUCK],
                         "未声明等待时恢复默认 180s 判定（真卡死发现时间不再被延后）")
        self.assertIn(f"任务停滞在场景 [{SCENE}]", watchdog._events[-1][1])
        self.assertEqual(DEFAULT_SCENE_STUCK_SECONDS, 180.0)

    def test_waiting_still_detects_frozen_screen(self):
        watchdog = self._prepare(self._watchdog(), scene_age=2000,
                                 static_age=120, waiting=True, desc="等匹配")
        watchdog._check_once()
        self.assertEqual(self._levels(watchdog), [FreezeLevel.GAME_FROZEN],
                         "等待期间画面彻底静止 → 仍按游戏卡死处置")


class WatchdogWaitLifecycleTest(unittest.TestCase):
    """等待声明的清除时机：场景切换 / end_wait / 告警完毕 / attach / detach / stop。"""

    def _attached(self, name="叛忍来袭"):
        watchdog = _watchdog()
        task = SimpleNamespace(task_name=name, watchdog=None)
        task.attach_watchdog = lambda wd: setattr(task, "watchdog", wd)
        task.detach_watchdog = lambda: setattr(task, "watchdog", None)
        watchdog.attach_task(task)
        return watchdog, task

    def test_scene_change_ends_wait(self):
        watchdog, _ = self._attached()
        watchdog.heartbeat(SCENE, waiting=True, desc="等活动开启")
        with watchdog._lock:
            self.assertTrue(watchdog._waiting)
        watchdog.heartbeat("叛忍来袭-进行中")      # 场景切换 → 等待结束
        with watchdog._lock:
            self.assertFalse(watchdog._waiting)
            self.assertEqual(watchdog._waiting_desc, "")

    def test_end_wait_and_notify_clear_state(self):
        watchdog, _ = self._attached()
        watchdog.heartbeat(SCENE, waiting=True, desc="等活动开启")
        watchdog.end_wait()
        with watchdog._lock:
            self.assertFalse(watchdog._waiting)

        watchdog.heartbeat(SCENE, waiting=True, desc="等活动开启")
        watchdog.notify_recovery_done(FreezeLevel.SCENE_STUCK)
        with watchdog._lock:
            self.assertFalse(watchdog._waiting,
                             "告警处理完毕必须清除等待声明（重新计时）")

    def test_detach_and_stop_clear_state(self):
        watchdog, task = self._attached()
        watchdog.heartbeat(SCENE, waiting=True, desc="等活动开启")
        watchdog.detach_task(task)
        with watchdog._lock:
            self.assertFalse(watchdog._waiting)

        watchdog.heartbeat(SCENE, waiting=True, desc="等活动开启")
        watchdog.stop()
        with watchdog._lock:
            self.assertFalse(watchdog._waiting)

    def test_attach_resets_state(self):
        watchdog, _ = self._attached()
        watchdog.heartbeat(SCENE, waiting=True, desc="等活动开启")
        other = SimpleNamespace(task_name="其它任务", watchdog=None)
        other.attach_watchdog = lambda wd: setattr(other, "watchdog", wd)
        other.detach_watchdog = lambda: setattr(other, "watchdog", None)
        watchdog.attach_task(other)
        with watchdog._lock:
            self.assertFalse(watchdog._waiting, "新任务不得继承上个任务的等待声明")

    def test_legacy_heartbeat_signature_is_tolerated(self):
        class _LegacyWatchdog:
            def __init__(self):
                self.scenes = []

            def heartbeat(self, scene_name=None):
                self.scenes.append(scene_name)

        task = object.__new__(_WaitTask)
        _task_attrs(task)
        task.watchdog = _LegacyWatchdog()
        task.declare_waiting("等活动开启")     # 不得抛异常
        self.assertEqual(task.watchdog.scenes, [None],
                         "旧式监视器退回只上报场景名的调用形态")
        self.assertFalse(task._watchdog_accepts_waiting())


# --------------------------------------------------------------------------- #
#                      任务侧：等待声明 / 连点进展 / wait_for                   #
# --------------------------------------------------------------------------- #
class _WaitTask(BaseTask):
    source_scene = "主场景-组织"
    schedule = AnyTime()

    def reset_task_exe_prog(self):
        return True

    def callback(self, task):
        pass


class _RecordingWatchdog:
    """支持等待声明的监视器替身。"""

    def __init__(self):
        self.calls = []
        self.ended = 0

    def heartbeat(self, scene_name=None, waiting=False, desc=""):
        self.calls.append((scene_name, waiting, desc))

    def end_wait(self):
        self.ended += 1


class _LoopRecognizer:
    def __init__(self, name):
        self.name = name

    def scene(self, screenshot, bool_debug=False, hint=None, allow_full_scan=True):
        return SimpleNamespace(name=self.name)


class _LoopOperationer:
    """跑真实 transition() 所需的最小替身。"""

    def __init__(self, scene_name, clicker_running=False):
        self.recognizer = _LoopRecognizer(scene_name)
        self.current_scene = None
        self.next_scene = None
        self.stop_event = threading.Event()
        self.clicker = SimpleNamespace(running=clicker_running, stop=lambda: None)
        self.screen_save_func = lambda *args: None
        self.task_name = "编号任务"

    def screen_cap(self):
        return object()


class _LoopTransitionManager:
    def bfs_shortest_path(self, start, goal):
        return []

    def transition(self, operationer):
        return True


def _task_attrs(task, clicker_running=False, scene_name=SCENE):
    task.task_name = "编号任务"
    task.tz_info = TZ
    task.logger = logging.getLogger(LOG)
    task.watchdog = None
    task.last_unregistered_scene_time = None
    task.transition_return = ""
    task.operationer = _LoopOperationer(scene_name, clicker_running)
    task.transition_manager = _LoopTransitionManager()
    task.transition_func = {scene_name: lambda t: False}
    task.__dict__["_logged_once_keys"] = set()
    return task


def _wait_task(clicker_running=False, watchdog=None, scene_name=SCENE):
    task = object.__new__(_WaitTask)
    _task_attrs(task, clicker_running, scene_name)
    task.watchdog = watchdog
    return task


class DeclareWaitingTest(unittest.TestCase):
    """declare_waiting 的上报、作用域与连点进展信号。"""

    def test_declare_reports_and_is_scene_scoped(self):
        watchdog = _RecordingWatchdog()
        task = _wait_task(watchdog=watchdog, scene_name=SCENE)
        task.__dict__["_current_scene_name"] = SCENE
        task.declare_waiting("等活动开启")
        self.assertEqual(watchdog.calls, [(SCENE, True, "等活动开启")])
        self.assertEqual(task._waiting_state(SCENE), (True, "等活动开启"))
        # 离开声明时所在的场景 → 声明失效（否则新场景会被一直当作等待中）
        self.assertEqual(task._waiting_state("叛忍来袭-进行中"), (False, ""))
        self.assertIsNone(task.__dict__.get("_declared_waiting"))

    def test_end_wait_reports(self):
        watchdog = _RecordingWatchdog()
        task = _wait_task(watchdog=watchdog)
        task.declare_waiting("等匹配")
        task.end_wait()
        self.assertEqual(watchdog.ended, 1)
        self.assertIsNone(task.__dict__.get("_declared_waiting"))

    def test_clicker_running_is_progress_evidence(self):
        task = _wait_task(clicker_running=True)
        self.assertEqual(task._waiting_state(SCENE), (True, "连点进行中"))
        task.operationer.clicker.running = False
        self.assertEqual(task._waiting_state(SCENE), (False, ""))

    def test_clicker_without_running_flag_uses_thread(self):
        task = _wait_task()
        task.operationer.clicker = SimpleNamespace(
            _thread=SimpleNamespace(is_alive=lambda: True))
        self.assertTrue(task._clicker_running())
        task.operationer.clicker = SimpleNamespace(
            _thread=SimpleNamespace(is_alive=lambda: False))
        self.assertFalse(task._clicker_running())

    def test_transition_heartbeat_carries_waiting(self):
        watchdog = _RecordingWatchdog()
        task = _wait_task(clicker_running=True, watchdog=watchdog)
        task.transition()
        self.assertEqual(watchdog.calls, [(SCENE, True, "连点进行中")],
                         "连点进行中必须作为「有进展」上报给监视器")

    def test_transition_heartbeat_plain_when_idle(self):
        watchdog = _RecordingWatchdog()
        task = _wait_task(watchdog=watchdog)
        task.transition()
        self.assertEqual(watchdog.calls, [(SCENE, False, "")])


class WaitForTest(unittest.TestCase):
    """wait_for：条件满足 / 超时 / 条件异常 / 停止信号。"""

    def test_condition_met_returns_true_and_declares_waiting(self):
        watchdog = _RecordingWatchdog()
        task = _wait_task(watchdog=watchdog)
        state = {"n": 0}

        def condition():
            state["n"] += 1
            return state["n"] >= 2

        ok = task.wait_for("等匹配", condition, timeout=5, interval=0.01)
        self.assertTrue(ok)
        self.assertTrue(all(call[1] for call in watchdog.calls),
                        "等待期间每轮都要声明 waiting")

    def test_timeout_returns_false(self):
        task = _wait_task(watchdog=_RecordingWatchdog())
        with self.assertLogs(LOG, level=logging.DEBUG) as cm:
            ok = task.wait_for("等匹配", lambda: False, timeout=0.05, interval=0.01)
        self.assertFalse(ok)
        self.assertIn("等待「等匹配」超时", "\n".join(cm.output))

    def test_condition_exception_does_not_kill_task(self):
        task = _wait_task(watchdog=_RecordingWatchdog())

        def boom():
            raise ValueError("boom")

        with self.assertLogs(LOG, level=logging.DEBUG) as cm:
            ok = task.wait_for("等活动", boom, timeout=0.05, interval=0.01)
        logs = "\n".join(cm.output)
        self.assertFalse(ok)
        self.assertIn("条件检查异常", logs, "条件异常只记 WARNING 并继续等待")

    def test_stop_signal_raises(self):
        task = _wait_task(watchdog=_RecordingWatchdog())
        task.operationer.stop_event.set()
        with self.assertRaises(Stop):
            task.wait_for("等匹配", lambda: False, timeout=5, interval=0.01)


class RealTaskWaitingTest(unittest.TestCase):
    """真实任务类：等待点都有声明，且不再用任务级停滞阈值硬扛。"""

    def test_gengduowanfa_matching_declares_waiting(self):
        self.assertIsNone(GengDuoWanFa.scene_stuck_seconds,
                          "更多玩法不再覆盖任务级停滞阈值")
        calls = []
        task = object.__new__(GengDuoWanFa)
        task.bool_click = False
        task.operationer = SimpleNamespace(
            clicker=SimpleNamespace(stop=lambda: None),
            click_and_wait=lambda *a, **k: True,
            detect_element=lambda *a, **k: False,
        )
        task.declare_waiting = lambda desc="": calls.append(desc)
        GengDuoWanFa.transition_func["更多玩法-匹配中"](task)
        GengDuoWanFa.transition_func["更多玩法-匹配成功"](task)
        self.assertEqual(calls, ["更多玩法匹配中", "更多玩法匹配成功"])

    def test_panrenlaixi_about_to_start_declares_waiting(self):
        self.assertIsNone(PanRenLaiXi.scene_stuck_seconds,
                          "叛忍来袭不再覆盖任务级停滞阈值")
        calls = []
        task = object.__new__(PanRenLaiXi)
        task.logger = logging.getLogger(LOG)
        task.declare_waiting = lambda desc="": calls.append(desc)
        with mock.patch("time.sleep"):
            PanRenLaiXi.transition_func["叛忍来袭-即将开始"](task)
        self.assertEqual(calls, ["叛忍来袭即将开启"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
