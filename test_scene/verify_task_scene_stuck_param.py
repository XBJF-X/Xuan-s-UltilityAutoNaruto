# -*- coding: utf-8 -*-
"""验证任务级「场景停滞阈值」（BaseTask.scene_stuck_seconds）与监视器接入。

背景（用户反馈 2026-09-15 13:49:10）：
    任务「更多玩法」卡在场景「绝迹战场-副本内」超过 180 秒被判定 [SCENE_STUCK]：
    进入副本后一局可持续数分钟，期间连点让画面持续变化但场景名不变，全局默认的
    180 秒阈值会把正常对局误判为停滞（→ 停任务、存 WatchdogFreeze 截图、走自救）。
    需求：允许在**任务类里**（代码，不是用户可调配置）自定义该阈值，默认行为不变。

本脚本覆盖（全部离线，不依赖设备/模拟器/真实截图）：
  1. 未覆盖（BaseTask 默认 None）→ 沿用全局默认 180 秒，与旧行为逐字等价；
  2. 任务覆盖 600 → 300 秒不告警、601 秒告警（告警详情用任务阈值）；
  3. 任务覆盖 0 → 该任务不再判场景停滞，但画面静止类判定（GAME_FROZEN）不受影响；
  4. 非法值（"abc" / NaN）→ 回退默认并告警一次（去重，不刷屏）；
  5. 优先级：任务属性 > 全局配置项「超时检测-场景停滞秒数」 > 默认 180；
  6. `attach_task` 留痕：仅覆盖了全局值才 INFO（未覆盖不刷屏）；
  7. 真实任务类：`BaseTask.scene_stuck_seconds is None`、`GengDuoWanFa` / `PanRenLaiXi`
     不再抬任务级阈值（改由「连点进行中＝等待」与 declare_waiting 承担）；
  8. 旧式假任务（完全没有该属性，如既有 verify 脚本的替身）→ 不抛异常、按默认走；
  9. 源码级防回退（判定必须走 `_scene_stuck_seconds`，不得再硬编码读 180）。

运行：.venv\\Scripts\\python.exe -X utf8 test_scene\\verify_task_scene_stuck_param.py
"""
import logging
import os
import sys
import time
import unittest
from pathlib import Path

import numpy as np

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.core.legacy.Task.BaseTask import BaseTask  # noqa: E402
from backend.core.legacy.Task.GengDuoWanFa import GengDuoWanFa  # noqa: E402
from backend.core.legacy.Task.PanRenLaiXi import PanRenLaiXi  # noqa: E402
from backend.services.watchdog_service import (  # noqa: E402
    DEFAULT_SCENE_STUCK_SECONDS,
    FreezeLevel,
    TimeoutWatchdog,
)

LOG = "verify.scenestuck"
STUCK_SCENE = "绝迹战场-副本内"


class _FakeConfig:
    """最小 Config 替身：只提供 get_config（监视器只读全局配置项）。"""

    def __init__(self, **overrides):
        self.values = overrides

    def get_config(self, key, default=None):
        return self.values.get(key, default)


class _FakeTask:
    """旧式任务替身：**没有** scene_stuck_seconds 属性（回归保护用）。"""

    def __init__(self, name="编号任务"):
        self.task_name = name

    def attach_watchdog(self, watchdog):
        self.watchdog = watchdog

    def detach_watchdog(self):
        self.watchdog = None


def _task_with_threshold(value, name="更多玩法"):
    """带场景停滞阈值的任务替身（实例属性，getattr 同样可见）。"""
    task = _FakeTask(name)
    task.scene_stuck_seconds = value
    return task


class SceneStuckThresholdTest(unittest.TestCase):
    """任务级场景停滞阈值：取值规则、优先级、关闭语义与回归保护。"""

    def setUp(self):
        self.frame = np.zeros((10, 10, 3), dtype=np.uint8)

    # ---------------- 辅助 ----------------
    def _new_watchdog(self, **config_overrides):
        values = {"超时检测-启用": True}
        values.update(config_overrides)
        watchdog = TimeoutWatchdog(
            config=_FakeConfig(**values),
            device=None,
            operationer=None,
            logger=logging.getLogger(LOG),
        )
        events = []
        watchdog._raise = lambda level, detail="", _events=events: _events.append(
            (level, detail))
        # 探针验证会 sleep 并点击设备，这里直接视为"点击无反应"
        watchdog._probe_and_still_static = lambda reference: True
        watchdog._capture_frame = lambda: self.frame
        watchdog._events = events
        return watchdog

    def _prepare(self, watchdog, task, scene_age=0.0, static_age=0.0):
        """构造"同一场景停留 scene_age 秒、画面静止 static_age 秒"的检测前状态。"""
        now = time.monotonic()
        with watchdog._lock:
            watchdog._current_task = task
            watchdog._awaiting_recovery = False
            watchdog._grace_until = 0.0
            watchdog._last_scene = STUCK_SCENE
            watchdog._scene_since = now - scene_age
            # 上一帧必须是"归一化后的小图"（_normalize_frame 会缩放到 160x90），
            # 且与 _capture_frame 返回的帧一致 → 帧差 0 → 静止时长 = static_age
            watchdog._last_frame = watchdog._normalize_frame(self.frame)
            watchdog._static_since = now - static_age
            watchdog._scene_stuck_enabled = True
            watchdog._last_game_restart = 0.0
            watchdog._capture_fail_count = 0
        watchdog._events.clear()

    @staticmethod
    def _levels(watchdog):
        return [level for level, _ in watchdog._events]

    # ---------------- 1. 默认行为 ----------------
    def test_default_keeps_old_behaviour_at_180_seconds(self):
        """未覆盖（None / 无该属性）→ 沿用全局默认 180 秒，与旧行为逐字等价"""
        self.assertEqual(DEFAULT_SCENE_STUCK_SECONDS, 180.0)
        watchdog = self._new_watchdog()
        for task in (_FakeTask(), _task_with_threshold(None)):
            with self.subTest(task=task.task_name,
                              override=getattr(task, "scene_stuck_seconds", "无该属性")):
                self._prepare(watchdog, task, scene_age=179)
                watchdog._check_once()
                self.assertEqual(self._levels(watchdog), [], "179s 未达 180s 阈值，不应告警")
                self._prepare(watchdog, task, scene_age=181)
                watchdog._check_once()
                self.assertEqual(self._levels(watchdog), [FreezeLevel.SCENE_STUCK],
                                 "181s 必须按默认 180s 阈值告警")

    # ---------------- 2. 任务覆盖 ----------------
    def test_task_override_600(self):
        """更多玩法场景整局可达数分钟：覆盖为 600 秒后不得在 300s 误报"""
        watchdog = self._new_watchdog()
        task = _task_with_threshold(600)
        self._prepare(watchdog, task, scene_age=300)
        watchdog._check_once()
        self.assertEqual(self._levels(watchdog), [], "300s < 600s，不得告警")
        self._prepare(watchdog, task, scene_age=601)
        watchdog._check_once()
        self.assertEqual(self._levels(watchdog), [FreezeLevel.SCENE_STUCK])
        detail = watchdog._events[-1][1]
        self.assertIn("600 秒", detail, "告警详情必须使用任务阈值，便于排查")

    # ---------------- 3. 关闭语义 ----------------
    def test_zero_disables_scene_stuck_but_keeps_game_frozen(self):
        """0 = 该任务不做场景停滞判定；画面静止类判定（游戏卡死）不受影响"""
        watchdog = self._new_watchdog()
        task = _task_with_threshold(0)
        self._prepare(watchdog, task, scene_age=100000, static_age=0)
        watchdog._check_once()
        self.assertEqual(self._levels(watchdog), [], "任务显式关闭后不得再判场景停滞")
        # 画面静止 100s（> 全局 60s）+ 探针无反应 → 仍然要判游戏卡死
        self._prepare(watchdog, task, scene_age=100000, static_age=100)
        watchdog._check_once()
        self.assertEqual(self._levels(watchdog), [FreezeLevel.GAME_FROZEN],
                         "关闭场景停滞不得影响游戏卡死检测")
        # 负值语义与 0 相同（取 <= 0 关闭）
        watchdog = self._new_watchdog()
        self._prepare(watchdog, _task_with_threshold(-5), scene_age=100000)
        watchdog._check_once()
        self.assertEqual(self._levels(watchdog), [], "负值与 0 同为关闭")

    # ---------------- 4. 非法值 ----------------
    def test_invalid_task_value_falls_back_and_warns_once(self):
        for bad in ("abc", float("nan")):
            with self.subTest(value=bad):
                watchdog = self._new_watchdog()
                task = _task_with_threshold(bad)
                with self.assertLogs(LOG, level=logging.WARNING) as cm:
                    self._prepare(watchdog, task, scene_age=181)
                    watchdog._check_once()
                    self._prepare(watchdog, task, scene_age=181)
                    watchdog._check_once()
                warnings = [r.getMessage() for r in cm.records
                            if r.levelno == logging.WARNING]
                self.assertEqual(len(warnings), 1, "非法值告警必须去重（每轮检测都会读）")
                self.assertIn("scene_stuck_seconds", warnings[0])
                self.assertIn("更多玩法", warnings[0], "告警需标明是哪个任务")
                self.assertTrue(watchdog._events, "非法值回退默认 180s 后仍应告警")

    # ---------------- 5. 优先级 ----------------
    def test_task_value_overrides_global_config(self):
        # 全局配置 300：任务未覆盖 → 按 300 判定
        watchdog = self._new_watchdog(**{"超时检测-场景停滞秒数": 300})
        task = _FakeTask("每周胜场")
        self._prepare(watchdog, task, scene_age=181)
        watchdog._check_once()
        self.assertEqual(self._levels(watchdog), [], "全局 300s 生效：181s 不应告警")
        self._prepare(watchdog, task, scene_age=301)
        watchdog._check_once()
        self.assertEqual(self._levels(watchdog), [FreezeLevel.SCENE_STUCK])
        # 任务覆盖 600 优先于全局 300
        watchdog = self._new_watchdog(**{"超时检测-场景停滞秒数": 300})
        task = _task_with_threshold(600)
        self._prepare(watchdog, task, scene_age=301)
        watchdog._check_once()
        self.assertEqual(self._levels(watchdog), [], "任务阈值优先于全局配置")
        self._prepare(watchdog, task, scene_age=601)
        watchdog._check_once()
        self.assertEqual(self._levels(watchdog), [FreezeLevel.SCENE_STUCK])

    def test_invalid_global_config_falls_back_to_default(self):
        watchdog = self._new_watchdog(**{"超时检测-场景停滞秒数": "不是数字"})
        with self.assertLogs(LOG, level=logging.WARNING) as cm:
            self.assertAlmostEqual(watchdog._global_scene_stuck_seconds(), 180.0)
        self.assertTrue([r for r in cm.records if "超时检测-场景停滞秒数" in r.getMessage()])

    # ---------------- 6. attach 留痕 ----------------
    def test_attach_logs_threshold_override_only(self):
        watchdog = self._new_watchdog()
        with self.assertLogs(LOG, level=logging.INFO) as cm:
            watchdog.attach_task(_task_with_threshold(600))
        self.assertTrue(
            any("场景停滞阈值按任务设置设为 600 秒" in r.getMessage()
                for r in cm.records if r.levelno == logging.INFO),
            "覆盖了全局阈值必须在任务开始时 INFO 留痕")
        # 未覆盖的任务不打阈值 INFO（否则每个任务都多一行，属刷屏）
        watchdog = self._new_watchdog()
        with self.assertLogs(LOG, level=logging.DEBUG) as cm2:
            watchdog.attach_task(_FakeTask("每周胜场"))
        self.assertEqual(
            [r for r in cm2.records
             if r.levelno == logging.INFO and "场景停滞阈值" in r.getMessage()], [],
            "未覆盖全局值时不得输出阈值 INFO")
        # 关闭（<=0）也要留痕，避免"为什么这个任务不判停滞"无据可查
        watchdog = self._new_watchdog()
        with self.assertLogs(LOG, level=logging.INFO) as cm3:
            watchdog.attach_task(_task_with_threshold(0))
        self.assertTrue(
            any("已关闭场景停滞判定" in r.getMessage()
                for r in cm3.records if r.levelno == logging.INFO))

    # ---------------- 7. 真实任务类 ----------------
    def test_real_task_classes(self):
        self.assertIsNone(BaseTask.scene_stuck_seconds,
                          "框架默认必须为 None（沿用全局/默认 180 秒，行为不变）")
        self.assertIsNone(GengDuoWanFa.scene_stuck_seconds,
                          "更多玩法不再抬任务级阈值：改由「连点进行中＝等待」"
                          "与 declare_waiting 承担（见 verify_wait_and_progress.py）")
        self.assertIsNone(PanRenLaiXi.scene_stuck_seconds,
                          "叛忍来袭不再抬任务级阈值：改由 declare_waiting 声明等待")

        class _GengDuoLike:
            task_name = "更多玩法"
            scene_stuck_seconds = 600

        watchdog = self._new_watchdog()
        self.assertEqual(watchdog._scene_stuck_seconds(180.0), 180.0,
                         "无当前任务时按传入默认值")
        watchdog._current_task = _FakeTask("更多玩法")
        self.assertEqual(watchdog._scene_stuck_seconds(180.0), 180.0,
                         "旧式替身（无该属性）按默认值")
        watchdog._current_task = _GengDuoLike()
        self.assertEqual(watchdog._scene_stuck_seconds(180.0), 600.0,
                         "任务级覆盖本身的能力保留（仍可用于特殊任务）")

    # ---------------- 8. 旧式任务兼容 ----------------
    def test_legacy_task_without_attribute_is_supported(self):
        """既有 verify 脚本的假任务没有该属性：attach/检测都不得抛异常"""

        class _LegacyTask:
            def __init__(self):
                self.task_name = "旧式任务"

            def attach_watchdog(self, watchdog):
                self.watchdog = watchdog

            def detach_watchdog(self):
                self.watchdog = None

        watchdog = self._new_watchdog()
        task = _LegacyTask()
        watchdog.attach_task(task)
        self._prepare(watchdog, task, scene_age=181)
        watchdog._check_once()
        self.assertEqual(self._levels(watchdog), [FreezeLevel.SCENE_STUCK])

    # ---------------- 9. 源码级防回退 ----------------
    def test_source_uses_task_aware_threshold(self):
        source = (Path(_PROJECT_ROOT) / "backend" / "services"
                  / "watchdog_service.py").read_text(encoding="utf-8")
        self.assertIn("self._scene_stuck_seconds(", source,
                      "场景停滞判定必须走任务感知的阈值")
        self.assertIn("DEFAULT_SCENE_STUCK_SECONDS", source)
        self.assertNotIn('self._cfg("超时检测-场景停滞秒数", 180)', source,
                         "不得再硬编码读取 180（任务覆盖会失效）")


if __name__ == "__main__":
    unittest.main(verbosity=2)



