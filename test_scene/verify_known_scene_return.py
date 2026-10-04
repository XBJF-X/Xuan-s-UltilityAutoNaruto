# -*- coding: utf-8 -*-
"""验证「场景图已知但本任务未注册的公共中转页 → 立刻按图回源」与「未注册分支退避」。

背景（2026-09-16 21:10~21:12 叛忍来袭日志）：从「叛忍来袭-未开始」点 X 后落到「组织」——
该场景在场景图里存在，但叛忍任务没写它的处理函数，于是被当成"未注册场景"：
每轮白等 `UNREGISTER_SCENE_MAX_TIME`（15s，且期间高速空转：日志里一秒 20+ 轮）
→ 15s 后强回源走 `组织 -> 主场景 -> 忍界指引 -> 主场景-组织`（3 跳 ~13s）→ 又落到
「组织」→ 再循环。3 轮共浪费约 105s，且中途多次保存 UnregisteredSceneForceReturn 截图。

本脚本覆盖（全部离线，不依赖设备 / 配置 / 模拟器）：
1. 图内已知但未注册的场景：**连续确认 N 帧后立刻**按图回源（默认 N=2；单帧不算）；
2. 真未知画面（不在场景图里）→ 保持旧的 15s 等待语义，不立刻回源；
3. 开关 `graph_known_scene_immediate_return=False` → 回到旧行为；
4. 旧式替身（`operationer` 无 `scene_graph`）→ 不抛异常、行为同旧；
5. 任务已挂其它 `next_scene` → 不抢目标；已在 source_scene → 不回源；
6. 转移图无路 → 放弃本次回源（清空目标）并交回「未注册场景」处理函数；
7. 未注册分支调用处理函数前按 `unknown_scene_retreat_seconds` 退避一次（0 = 不退避）；
8. 回源提示日志按场景去重（`_log_once`），不刷屏；
9. 真实任务类的默认值（框架默认开启、确认 2 帧、退避 1s）。

运行：.venv\\Scripts\\python.exe -X utf8 test_scene\\verify_known_scene_return.py
"""
import logging
import os
import sys
import threading
import unittest
from unittest import mock
from zoneinfo import ZoneInfo

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.core.legacy.Task.BaseTask import BaseTask  # noqa: E402
from backend.core.legacy.Task.schedule import AnyTime  # noqa: E402

TZ = ZoneInfo("Asia/Shanghai")
LOG = "verify.known_scene"
SOURCE_SCENE = "主场景-组织"
TRANSIT_SCENE = "组织"
UNKNOWN_SCENE = "某个不认识的新画面"


class _Scene:
    def __init__(self, name):
        self.name = name


class _Recognizer:
    def __init__(self, name):
        self.name = name

    def scene(self, screenshot, bool_debug=False, hint=None, allow_full_scan=True):
        return _Scene(self.name)


class _Clicker:
    def stop(self):
        pass


class _Graph:
    def __init__(self, scenes):
        self.scenes = {name: object() for name in scenes}


class _Operationer:
    """最小 operationer 替身：场景名固定 + 可配置场景图 / 已挂目标。"""

    def __init__(self, scene_name, scenes=None, next_scene=None, with_graph=True):
        self.recognizer = _Recognizer(scene_name)
        self.current_scene = None
        self.next_scene = next_scene
        self.stop_event = threading.Event()
        self.clicker = _Clicker()
        self.screen_save_func = lambda *args: None
        self.task_name = "编号任务"
        if with_graph:
            self.scene_graph = _Graph(scenes or [])

    def screen_cap(self):
        return object()


class _TransitionManager:
    def __init__(self, path=None):
        self._path = list(path or [])
        self.bfs_calls = []
        self.transitions = []

    def bfs_shortest_path(self, start, goal):
        self.bfs_calls.append((start, goal))
        return list(self._path)

    def transition(self, operationer):
        self.transitions.append((operationer.next_scene,))
        return True


class _Task(BaseTask):
    source_scene = SOURCE_SCENE
    schedule = AnyTime()

    def reset_task_exe_prog(self):
        return True

    def callback(self, task):
        pass


def _make_task(scene_name, scenes=(TRANSIT_SCENE, SOURCE_SCENE), path=None,
               next_scene=None, with_graph=True, **attrs):
    task = object.__new__(_Task)
    task.task_name = "编号任务"
    task.tz_info = TZ
    task.logger = logging.getLogger(LOG)
    task.last_run_time = None
    task.last_unregistered_scene_time = None
    task.watchdog = None
    task.transition_return = ""
    task.operationer = _Operationer(scene_name, scenes, next_scene, with_graph)
    task.transition_manager = _TransitionManager(path)
    task.handlers = []
    task.transition_func = {
        "未注册场景": lambda t: t.handlers.append("未注册场景") or False,
        SOURCE_SCENE: lambda t: t.handlers.append(SOURCE_SCENE) or False,
    }
    task.__dict__["_logged_once_keys"] = set()
    # 除退避专项用例外默认关掉退避，避免离线用例里真的 sleep 1s（拖慢整个 verify 套件）
    task.unknown_scene_retreat_seconds = 0
    for key, value in attrs.items():
        setattr(task, key, value)
    return task


class GraphKnownSceneReturnTest(unittest.TestCase):
    """图内已知但未注册的公共中转页：确认后立刻回源，不再白等 15s。"""

    def test_confirm_frames_then_return(self):
        """默认连续确认 2 帧：首帧不跳，第二帧立刻按图回源。"""
        task = _make_task(TRANSIT_SCENE, path=[TRANSIT_SCENE, SOURCE_SCENE])
        task.transition()
        self.assertEqual(task.transition_manager.transitions, [],
                         "单帧不确认（防加载/过场误判）")
        self.assertEqual(task.operationer.next_scene, None)
        task.transition()
        self.assertEqual(task.transition_manager.transitions, [(SOURCE_SCENE,)],
                         "连续 2 帧确认后必须立刻回源")
        self.assertEqual(task.operationer.next_scene, SOURCE_SCENE)
        self.assertIsNone(task.last_unregistered_scene_time,
                          "回源成功应重置未注册计时")

    def test_confirm_one_frame_jumps_immediately(self):
        task = _make_task(TRANSIT_SCENE, path=[TRANSIT_SCENE, SOURCE_SCENE],
                          graph_known_scene_confirm_frames=1)
        task.transition()
        self.assertEqual(task.transition_manager.transitions, [(SOURCE_SCENE,)],
                         "确认帧数=1 时首帧即回源")

    def test_unknown_scene_keeps_old_wait(self):
        task = _make_task(UNKNOWN_SCENE, scenes=(SOURCE_SCENE,),
                          path=[UNKNOWN_SCENE, SOURCE_SCENE])
        task.transition()
        self.assertEqual(task.transition_manager.transitions, [],
                         "真未知画面保持 15s 等待语义，不立刻回源")
        self.assertEqual(task.handlers, ["未注册场景"])
        self.assertIsNotNone(task.last_unregistered_scene_time)

    def test_switch_off_restores_old_behaviour(self):
        task = _make_task(TRANSIT_SCENE, path=[TRANSIT_SCENE, SOURCE_SCENE],
                          graph_known_scene_immediate_return=False)
        for _ in range(3):
            task.transition()
        self.assertEqual(task.transition_manager.transitions, [],
                         "关闭开关后必须回到旧行为（等满 15s 才回源）")
        self.assertEqual(task.handlers, ["未注册场景"] * 3)

    def test_no_scene_graph_is_safe(self):
        task = _make_task(TRANSIT_SCENE, with_graph=False,
                          path=[TRANSIT_SCENE, SOURCE_SCENE])
        task.transition()
        self.assertEqual(task.transition_manager.transitions, [],
                         "旧式替身无 scene_graph 时不得回源（也不得抛异常）")
        self.assertEqual(task.handlers, ["未注册场景"])

    def test_pending_target_not_stolen(self):
        task = _make_task(TRANSIT_SCENE, path=[TRANSIT_SCENE, SOURCE_SCENE],
                          next_scene="别的目标")
        task.transition()
        self.assertEqual(task.operationer.next_scene, "别的目标",
                         "任务已挂目标时不得被回源逻辑改写")
        self.assertEqual(task.transition_manager.transitions, [("别的目标",)],
                         "跳的是任务自己的目标，不得被换成 source_scene")

    def test_skip_when_already_at_source(self):
        task = _make_task(SOURCE_SCENE, path=[SOURCE_SCENE, TRANSIT_SCENE])
        task.transition()
        self.assertEqual(task.transition_manager.transitions, [],
                         "已在 source_scene 时不需要回源")
        self.assertEqual(task.handlers, [SOURCE_SCENE])

    def test_no_path_falls_back_to_handler(self):
        task = _make_task(TRANSIT_SCENE, path=[])      # 转移图无路
        task.transition()
        task.transition()
        self.assertEqual(task.transition_manager.transitions, [],
                         "无路可走时交回「未注册场景」处理函数")
        self.assertIsNone(task.operationer.next_scene,
                          "无路时必须清掉刚挂上的回源目标")
        self.assertEqual(task.handlers, ["未注册场景"] * 2)

    def test_return_hint_logged_once_per_scene(self):
        task = _make_task(TRANSIT_SCENE, path=[TRANSIT_SCENE, SOURCE_SCENE],
                          graph_known_scene_confirm_frames=1)
        with self.assertLogs(LOG, level=logging.DEBUG) as cm:
            task.transition()
            task.transition()
        logs = "\n".join(cm.output)
        self.assertEqual(logs.count("立即按图回源"), 1,
                         "同一场景的回源提示每次执行只输出一次（避免刷屏）")


class UnregisteredRetreatTest(unittest.TestCase):
    """未注册分支的循环退避：调用处理函数前等一次，避免高速空转。"""

    def test_retreats_once_before_handler(self):
        task = _make_task(UNKNOWN_SCENE, scenes=(SOURCE_SCENE,),
                          unknown_scene_retreat_seconds=1.0)
        with mock.patch("time.sleep") as sleeper:
            task.transition()
        self.assertEqual(sleeper.call_args_list, [mock.call(1.0)],
                         "默认退避 1s（旧实现在未注册分支完全不等待）")
        self.assertEqual(task.handlers, ["未注册场景"])

    def test_zero_retreat_disables_wait(self):
        task = _make_task(UNKNOWN_SCENE, scenes=(SOURCE_SCENE,),
                          unknown_scene_retreat_seconds=0)
        with mock.patch("time.sleep") as sleeper:
            task.transition()
        self.assertEqual(sleeper.call_args_list, [],
                         "置 0 时回到旧行为（不等待）")

    def test_known_scene_return_does_not_retreat(self):
        task = _make_task(TRANSIT_SCENE, path=[TRANSIT_SCENE, SOURCE_SCENE],
                          graph_known_scene_confirm_frames=1,
                          unknown_scene_retreat_seconds=1.0)
        with mock.patch("time.sleep") as sleeper:
            task.transition()
        self.assertEqual(sleeper.call_args_list, [],
                         "立刻回源路径不应额外等待（每轮开销降到最低）")


class FrameworkDefaultsTest(unittest.TestCase):
    def test_defaults(self):
        self.assertTrue(BaseTask.graph_known_scene_immediate_return)
        self.assertEqual(BaseTask.graph_known_scene_confirm_frames, 2)
        self.assertEqual(BaseTask.unknown_scene_retreat_seconds, 1.0)
        self.assertEqual(BaseTask.UNREGISTER_SCENE_MAX_TIME, 15)


if __name__ == "__main__":
    unittest.main(verbosity=2)
