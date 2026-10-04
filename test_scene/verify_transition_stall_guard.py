# -*- coding: utf-8 -*-
"""验证 BaseTask 的「pending 跳转未推进保护」与更多玩法未注册场景的回源收敛。

背景（2026-09-14 实机日志，雷电2号模拟器 2026-09-14/Xuan.log 61740 起）：
更多玩法任务进入【绝迹战场-副本内】后整局没有连点，日志每 ~1s 循环：
    识别到场景: 绝迹战场-副本内
    TransitionManager | 绝迹战场-副本内->更多玩法
    TransitionManager | 直接跳转成功
链路：对局入口的加载/过场画面被误判为未注册场景 → 任务的
@TransitionOn("未注册场景")（GengDuoWanFa）挂上 next_scene="更多玩法" →
只要「当前画面 → 目标」在转移图上有路，BaseTask 就每轮优先跳转并 return，
抢占了当前场景的处理函数（"副本内"是唯一会 clicker.start() 的地方）；
而该跳转的首跳（绝迹战场-副本内 -> 更多玩法-结算）注册函数只是 time.sleep(1)
（空操作）、TransitionManager._execute_transition 又恒返回 True，于是
「跳一次 → 回到原画面 → 再跳一次」永不终结，直到对局结束画面变成结算才自愈。

本脚本覆盖（全部离线，不依赖设备 / 配置 / 模拟器）：
1. 同一 (场景, 目标) 连续 3 次后第 4 次放弃目标：清空 next_scene + WARNING +
   JumpStalled 截图 + 交回当前场景处理函数（连点由此启动）；
2. 到达目标（next_scene == 识别场景）→ 清空且不跳转（原行为回归）；
3. 逐跳推进的正常寻路不被打断（场景变化 → 计数重置），到达后清空；
4. 转移图无路径 → 不跳转、保留 next_scene，交由"未注册场景"处理函数兜底；
5. 15s 强制回源纳入同一保护：最多跳 3 次，之后放弃 + 重置计时 + 交回处理函数；
6. 15s 强制回源且无路径：不再 KeyError（旧实现会取 transition_func[未知画面名]）；
7. 更多玩法：对局流程中（bool_click=True）未注册场景不回源，未进入对局才回源。
"""
import logging
import os
import sys
import time
import unittest

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.core.legacy.Task.BaseTask import (  # noqa: E402
    SCREENSHOT_REASON_JUMP_STALLED,
    SCREENSHOT_REASON_UNREGISTERED_SCENE,
    BaseTask,
)
from backend.core.legacy.Task.GengDuoWanFa import GengDuoWanFa  # noqa: E402

LOG = "verify.transition_stall_guard"


class _Scene:
    def __init__(self, name):
        self.name = name


class _ScriptedRecognizer:
    """按脚本返回识别结果（末项会一直重复）；advance_to 模拟跳转落地后的画面变化。"""

    def __init__(self, names):
        self._names = list(names)
        self._current = self._names.pop(0)

    def scene(self, screenshot, bool_debug=False, hint=None, allow_full_scan=True):
        return _Scene(self._current)

    def advance_to(self, name):
        self._current = name


class _FakeClicker:
    def __init__(self):
        self.started = 0
        self.stopped = 0

    def start(self):
        self.started += 1

    def stop(self):
        self.stopped += 1


class _FakeOperationer:
    def __init__(self, scene_names):
        self.next_scene = None
        self.current_scene = None
        self.recognizer = _ScriptedRecognizer(scene_names)
        self.clicker = _FakeClicker()

    def screen_cap(self):
        return object()


class _FakeTransitionManager:
    """最小转移管理器：BFS 与 TransitionManager.bfs_shortest_path 同语义。

    transition() 只记录调用（真实实现里可能是空操作，因此不会改变画面），
    需要模拟"落地成功"时通过 on_transition 回调推进识别场景。
    """

    def __init__(self, edges, on_transition=None):
        self.edges = {k: list(v) for k, v in edges.items()}
        self.calls = []
        self.on_transition = on_transition

    def bfs_shortest_path(self, start_id, end_id):
        queue = [(start_id, [start_id])]
        visited = {start_id}
        while queue:
            current, path = queue.pop(0)
            if current == end_id:
                return path
            for neighbor in self.edges.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return []

    def transition(self, operationer):
        source = getattr(operationer.current_scene, "name", None)
        self.calls.append((source, operationer.next_scene))
        if self.on_transition:
            self.on_transition(operationer)
        return None


def _handler(recorder, name):
    """场景处理函数替身：记录被执行的场景名。"""

    def _inner(task):
        recorder.append(name)
        return False

    return _inner


class _JumpGuardTask(BaseTask):
    """只跑 transition() 的任务壳（复用 BaseTask 的真实分支逻辑）。"""

    def __init__(self, scene_names, edges, transition_func, source_scene="更多玩法"):
        self.task_name = "跳转保护验证"
        self.logger = logging.getLogger(LOG)
        self.watchdog = None
        self.transition_return = ""
        self.source_scene = source_scene
        self.last_unregistered_scene_time = None
        self._jump_stall = None
        self.operationer = _FakeOperationer(scene_names)
        self.transition_manager = _FakeTransitionManager(edges)
        self.transition_func = transition_func
        self.screenshot_reasons = []

    def _auto_screenshot(self, reason):
        self.screenshot_reasons.append(reason)
        return True


def _start_clicker_handler(task):
    """「绝迹战场-副本内」式处理函数：启动连点并返回 False。"""
    task.operationer.clicker.start()
    return False


class JumpStallGuardTest(unittest.TestCase):
    """1-4：pending 跳转的「未推进保护」"""

    def test_stalled_jump_is_abandoned_and_handler_resumes(self):
        task = _JumpGuardTask(
            ["绝迹战场-副本内"],
            {"绝迹战场-副本内": ["更多玩法-结算"], "更多玩法-结算": ["更多玩法"]},
            {"绝迹战场-副本内": _start_clicker_handler},
            source_scene="更多玩法")
        task.operationer.next_scene = "更多玩法"
        with self.assertLogs(LOG, level=logging.WARNING) as cm:
            for _ in range(4):
                task.transition()
        self.assertEqual(len(task.transition_manager.calls), 3,
                         "前 3 轮保持原行为：优先执行 pending 跳转")
        self.assertIsNone(task.operationer.next_scene,
                          "第 4 轮判定跳转未生效 → 放弃目标")
        self.assertEqual(task.operationer.clicker.started, 1,
                         "放弃后必须执行当前场景处理函数（连点由此启动）")
        stalls = [r for r in cm.records if "未生效" in r.getMessage()]
        self.assertEqual(len(stalls), 1, "连续未生效只提示一次")
        self.assertIn(SCREENSHOT_REASON_JUMP_STALLED, task.screenshot_reasons)
        self.assertIsNone(task.last_unregistered_scene_time,
                          "场景已注册 → 计时被清空，不影响正常流程")
        self.assertIsNone(task._jump_stall, "放弃后计数一并重置")

    def test_arrival_clears_target_without_jump(self):
        handlers = []
        task = _JumpGuardTask(["更多玩法"], {"更多玩法": []},
                              {"更多玩法": _handler(handlers, "更多玩法")},
                              source_scene="更多玩法")
        task.operationer.next_scene = "更多玩法"
        task.transition()
        self.assertIsNone(task.operationer.next_scene, "到达目标即清空 next_scene")
        self.assertEqual(task.transition_manager.calls, [], "已到达不应再跳转")
        self.assertEqual(handlers, ["更多玩法"])

    def test_multi_hop_navigation_is_not_interrupted(self):
        handlers = []
        funcs = {name: _handler(handlers, name) for name in ("A", "B", "C")}
        task = _JumpGuardTask(["A"], {"A": ["B"], "B": ["C"]}, funcs, source_scene="C")
        task.operationer.next_scene = "C"
        task.transition_manager.on_transition = (
            lambda op: op.recognizer.advance_to("B"))
        task.transition()
        task.transition_manager.on_transition = (
            lambda op: op.recognizer.advance_to("C"))
        task.transition()
        task.transition()
        self.assertEqual([call[0] for call in task.transition_manager.calls],
                         ["A", "B"],
                         "逐跳推进（场景变化）应重置计数，不能被误判为未生效")
        self.assertIsNone(task.operationer.next_scene)
        self.assertEqual(handlers, ["C"], "只有真正到达后的场景处理函数被执行")
        self.assertIsNone(task._jump_stall)

    def test_no_path_keeps_target_and_falls_back(self):
        handlers = []
        task = _JumpGuardTask(["某个画面"], {},
                              {"未注册场景": _handler(handlers, "未注册场景")},
                              source_scene="更多玩法")
        task.operationer.next_scene = "更多玩法"
        task.transition()
        self.assertEqual(task.transition_manager.calls, [])
        self.assertEqual(task.operationer.next_scene, "更多玩法",
                         "无路可走时保持原行为（目标不由框架清除）")
        self.assertEqual(handlers, ["未注册场景"])


class ForceReturnGuardTest(unittest.TestCase):
    """5-6：15s 强制回源纳入同一保护"""

    def test_force_return_stalled_gives_back_control(self):
        handlers = []
        task = _JumpGuardTask(
            ["某个画面"],
            {"某个画面": ["中转"], "中转": ["更多玩法"]},
            {"未注册场景": _handler(handlers, "未注册场景")},
            source_scene="更多玩法")
        task.last_unregistered_scene_time = time.perf_counter() - 100
        with self.assertLogs(LOG, level=logging.WARNING) as cm:
            for _ in range(4):
                task.transition()
        self.assertEqual(len(task.transition_manager.calls), 3,
                         "强制回源同样最多跳 JUMP_STALL_LIMIT 次")
        self.assertIsNone(task.operationer.next_scene)
        self.assertEqual(handlers, ["未注册场景"],
                         "放弃回源后交回「未注册场景」处理函数")
        self.assertIn(SCREENSHOT_REASON_UNREGISTERED_SCENE, task.screenshot_reasons)
        self.assertIn(SCREENSHOT_REASON_JUMP_STALLED, task.screenshot_reasons)
        self.assertTrue(any("长时间未识别到注册场景" in r.getMessage()
                            for r in cm.records))
        self.assertTrue(any("未生效" in r.getMessage() for r in cm.records))
        self.assertGreater(task.last_unregistered_scene_time,
                           time.perf_counter() - 5,
                           "放弃后重置计时，给任务一段自主恢复窗口")

    def test_force_return_without_path_does_not_raise(self):
        handlers = []
        task = _JumpGuardTask(["某个画面"], {},
                              {"未注册场景": _handler(handlers, "未注册场景")},
                              source_scene="更多玩法")
        task.last_unregistered_scene_time = time.perf_counter() - 100
        # 旧实现在此会把 scene_name 留在"某个画面"上，随后取
        # transition_func[scene_name] 直接 KeyError（未捕获异常 → 冷却重试）；
        # 现应回退到"未注册场景"处理函数
        task.transition()
        self.assertEqual(task.transition_manager.calls, [])
        self.assertIsNone(task.operationer.next_scene, "回源失败要清掉刚挂上的目标")
        self.assertEqual(handlers, ["未注册场景"])
        self.assertGreater(task.last_unregistered_scene_time,
                           time.perf_counter() - 5,
                           "回源失败后重置计时，避免每帧重复回源")


class GengDuoWanFaUnregisteredSceneTest(unittest.TestCase):
    """7：更多玩法的未注册场景只在未进入对局流程时回源"""

    def _handler(self):
        self.assertIn("未注册场景", GengDuoWanFa.transition_func)
        return GengDuoWanFa.transition_func["未注册场景"]

    def _make_task(self, bool_click):
        task = GengDuoWanFa.__new__(GengDuoWanFa)
        task.task_name = "更多玩法"
        task.logger = logging.getLogger(LOG)
        task.operationer = _FakeOperationer(["更多玩法"])
        task.bool_click = bool_click
        return task

    def test_in_match_does_not_return_to_source(self):
        task = self._make_task(True)
        self._handler()(task)
        self.assertIsNone(
            task.operationer.next_scene,
            "对局流程中的加载/过场误判不得挂上回源目标（会抢占副本内处理函数）")
        self.assertEqual(task.operationer.clicker.stopped, 1, "仍应停连点")

    def test_out_of_match_returns_to_source(self):
        task = self._make_task(False)
        self._handler()(task)
        self.assertEqual(task.operationer.next_scene, "更多玩法",
                         "未进入对局流程（如卡在陌生界面）仍要回源重跑流程")


if __name__ == "__main__":
    unittest.main(verbosity=2)


