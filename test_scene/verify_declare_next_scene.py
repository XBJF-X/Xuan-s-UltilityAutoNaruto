# -*- coding: utf-8 -*-
"""验证「场景处理函数返回场景名字符串 = 声明落点」约定（B 型，v0.17.57）。

约定（`BaseTask.declare_next_scene` / `_normalize_handler_result`）：

| 处理函数返回 | 框架行为 |
| --- | --- |
| ``True`` | **任务完成**（唯一"返回值完成"方式；另一种是抛 ``TaskCompleted``） |
| ``"场景名"`` | **声明落点** → ``operationer.next_scene``，本轮不算完成；下一轮由 `_pending_jump_path` 做"到达即清空 / 未到达按图纠偏 / 连续跳不动则放弃并截图" |
| ``False`` / ``None`` | 继续循环（旧行为） |
| 其它真值（如 ``1``） | 不视为完成 + WARNING 提示改用 ``return True``（不再静默完成） |

兼容性前提（已扫描确认）：`backend/core/legacy/Task/*.py` 里 23 处 ``return 字符串``
全部位于 helper 函数（`describe()`/`_format_*`/`_skip_window_reason`），**没有任何
`@TransitionOn` 处理函数返回过字符串**；`XiaoHaoTiLi.__set_next_scene()` 这类既有
"设 next_scene 再 return False" 的写法返回的是 ``False``，不受影响。

本脚本覆盖（全部离线，不依赖设备/配置/模拟器）：
  1. `_normalize_handler_result` 六类输入（True/str/False/None/假值/真值）；
  2. `declare_next_scene` 的校验与日志（非法值、未知场景名、无 scene_graph 的老式替身、
     desc、按场景去重）；
  3. 两个调用点都生效：已注册场景 handler 与「未注册场景」handler；
  4. 声明后的四种走向：到达 / 有路纠偏 / 无路保留 / 连续跳不动则放弃+截图；
  5. 端到端 `_execute`：返回字符串**不会**被当成完成，只有 True/TaskCompleted 才完成；
  6. 既有先例（XiaoHaoTiLi.__set_next_scene）行为不变。

运行：.venv\\Scripts\\python.exe -X utf8 test_scene\\verify_declare_next_scene.py
"""
import logging
import os
import sys
import threading
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.core.legacy.Exceptions import TaskCompleted  # noqa: E402
from backend.core.legacy.Task.BaseTask import (  # noqa: E402
    SCREENSHOT_REASON_JUMP_STALLED,
    BaseTask,
)
from backend.core.legacy.Task.XiaoHaoTiLi import XiaoHaoTiLi  # noqa: E402
from backend.core.legacy.Task.schedule import AnyTime  # noqa: E402

TZ = ZoneInfo("Asia/Shanghai")
LOG = "verify.declare_next_scene"
SCENE_A = "主场景-组织"
SCENE_B = "组织"
SCENE_C = "叛忍来袭-未开始"


class _ScriptedRecognizer:
    """按帧序列返回场景名（末项一直重复）。"""

    def __init__(self, names):
        self._names = list(names)
        self._index = 0

    def scene(self, screenshot, bool_debug=False, hint=None, allow_full_scan=True):
        name = self._names[self._index]
        if self._index < len(self._names) - 1:
            self._index += 1
        return SimpleNamespace(name=name)


class _Graph:
    def __init__(self, scenes):
        self.scenes = {name: object() for name in scenes}


class _Operationer:
    def __init__(self, names, scenes, with_graph=True):
        self.recognizer = _ScriptedRecognizer(names)
        self.current_scene = None
        self.next_scene = None
        self.stop_event = threading.Event()
        self.clicker = SimpleNamespace(running=False, stop=lambda: None)
        self.screen_save_func = lambda *args: None
        self.task_name = "编号任务"
        if with_graph:
            self.scene_graph = _Graph(scenes)

    def screen_cap(self):
        return object()


class _TransitionManager:
    """最小转移管理器：bfs 返回配置路径，transition 只记录（真实实现同样返回 None）。"""

    def __init__(self, path=None):
        self._path = list(path or [])
        self.calls = []
        self.on_transition = None

    def bfs_shortest_path(self, start, goal):
        return list(self._path)

    def transition(self, operationer):
        self.calls.append((operationer.next_scene,))
        if self.on_transition:
            self.on_transition(operationer)
        return None


class _FakeConfig:
    def __init__(self):
        self.base = {"下次执行时间": 0}
        self.settings = {"错误自动截图": False}

    def get_task_base_config(self, task_name, key, default=None):
        return self.base.get(key, default)

    def set_task_base_config(self, task_name, key, value):
        self.base[key] = value

    def get_config(self, key, default=None):
        return self.settings.get(key, default)

    def get_task_exe_param(self, task_name, param, default=None):
        return default


class _Task(BaseTask):
    source_scene = SCENE_A
    schedule = AnyTime()
    task_max_duration = timedelta(minutes=10)

    def reset_task_exe_prog(self):
        return True

    def callback(self, task):
        pass


def _make_task(names, scenes=(SCENE_A, SCENE_B, SCENE_C), path=None,
               handlers=None, with_graph=True):
    task = object.__new__(_Task)
    task.task_name = "编号任务"
    task.tz_info = TZ
    task.logger = logging.getLogger(LOG)
    task.config = _FakeConfig()
    task.last_run_time = datetime.now(TZ)
    task.create_time = datetime.now(TZ)
    task.force_execute_now = False
    task.ignore_time_window = True
    task.is_temp = False
    task.last_execute_error = None
    task.watchdog = None
    task.transition_return = ""
    task.last_unregistered_scene_time = None
    task.stop_reason = ""
    task._jump_stall = None
    task.__dict__["_logged_once_keys"] = set()
    task.unknown_scene_retreat_seconds = 0        # 离线用例不做真实退避
    task.operationer = _Operationer(names, scenes, with_graph)
    task.transition_manager = _TransitionManager(path)
    task.screenshot_reasons = []
    task.transition_func = dict(handlers or {})
    return task


def _auto_screenshot(self, reason):
    self.screenshot_reasons.append(reason)
    return True


def _handler(recorder, name, result=False):
    """场景处理函数替身：记录执行、返回给定结果（可为字符串 = 声明落点）。"""

    def _inner(task):
        recorder.append(name)
        return result

    return _inner


class NormalizeResultTest(unittest.TestCase):
    """`_normalize_handler_result`：True / str / False / None / 假值 / 真值。"""

    def _task(self):
        return _make_task([SCENE_A])

    def test_true_means_completed(self):
        task = self._task()
        self.assertIs(task._normalize_handler_result(True), True,
                      "True 必须原样返回 → 由 _execute 判为完成")

    def test_string_declares_target_and_is_not_completed(self):
        task = self._task()
        with self.assertLogs(LOG, level=logging.DEBUG) as cm:
            result = task._normalize_handler_result(SCENE_C)
        self.assertIs(result, False, "返回字符串不得被当成完成")
        self.assertEqual(task.operationer.next_scene, SCENE_C)
        self.assertIn("声明落点", "\n".join(cm.output))

    def test_false_and_none_pass_through(self):
        task = self._task()
        self.assertIs(task._normalize_handler_result(False), False)
        self.assertIsNone(task._normalize_handler_result(None))

    def test_falsy_non_bool_passes_through(self):
        task = self._task()
        self.assertEqual(task._normalize_handler_result(0), 0,
                         "假值原样返回 → 继续循环")

    def test_truthy_non_true_is_not_completed_and_warns(self):
        task = self._task()
        with self.assertLogs(LOG, level=logging.WARNING) as cm:
            result = task._normalize_handler_result(123)
        self.assertIs(result, False, "非 True 的真值不再静默视为完成")
        self.assertIn("不视为任务完成", "\n".join(cm.output))
        self.assertIsNone(task.operationer.next_scene)


class DeclareNextSceneTest(unittest.TestCase):
    """`declare_next_scene` 的校验、日志与去重。"""

    def test_valid_declaration(self):
        task = _make_task([SCENE_A])
        with self.assertLogs(LOG, level=logging.DEBUG) as cm:
            self.assertTrue(task.declare_next_scene(SCENE_C, desc="点X后回到新场景"))
        self.assertEqual(task.operationer.next_scene, SCENE_C)
        logs = "\n".join(cm.output)
        self.assertIn("声明落点: " + SCENE_C, logs)
        self.assertIn("点X后回到新场景", logs)

    def test_log_deduped_per_scene(self):
        task = _make_task([SCENE_A])
        with self.assertLogs(LOG, level=logging.DEBUG) as cm:
            task.declare_next_scene(SCENE_C)
            task.declare_next_scene(SCENE_C)
        self.assertEqual("\n".join(cm.output).count("声明落点"), 1,
                         "同一场景的声明日志只输出一次（避免每帧刷屏）")

    def test_invalid_value_ignored_and_keeps_existing_target(self):
        task = _make_task([SCENE_A])
        task.operationer.next_scene = SCENE_A          # 已有声明
        for bad in (None, 123, ["x"], "   "):
            # 重新武装"只记一次"（同一执行周期内非法值告警是去重的，见下一个用例）
            task.__dict__["_logged_once_keys"] = set()
            with self.assertLogs(LOG, level=logging.WARNING) as cm:
                self.assertFalse(task.declare_next_scene(bad))
            self.assertIn("取值非法", "\n".join(cm.output))
            self.assertEqual(task.operationer.next_scene, SCENE_A,
                             "非法声明不得覆盖已有目标")

    def test_invalid_value_warning_deduped(self):
        task = _make_task([SCENE_A])
        with self.assertLogs(LOG, level=logging.WARNING) as cm:
            task.declare_next_scene(None)
            task.declare_next_scene(123)
        self.assertEqual("\n".join(cm.output).count("取值非法"), 1,
                         "非法声明的 WARNING 同一执行周期只提示一次（不刷屏）")

    def test_unknown_scene_name_is_rejected(self):
        task = _make_task([SCENE_A])
        task.operationer.next_scene = SCENE_A
        with self.assertLogs(LOG, level=logging.WARNING) as cm:
            self.assertFalse(task.declare_next_scene("不存在的场景"))
        self.assertIn("不在场景库中", "\n".join(cm.output))
        self.assertEqual(task.operationer.next_scene, SCENE_A)

    def test_without_scene_graph_skips_validation(self):
        task = _make_task([SCENE_A], with_graph=False)
        self.assertTrue(task.declare_next_scene("任意场景名"),
                        "老式替身（无 scene_graph）不做事前校验，保持可用")
        self.assertEqual(task.operationer.next_scene, "任意场景名")


class TransitionContractTest(unittest.TestCase):
    """走真实 transition()：两个调用点都做归一化。"""

    def test_registered_handler_string_declares(self):
        calls = []
        task = _make_task([SCENE_A], handlers={SCENE_A: _handler(calls, SCENE_A, SCENE_C)})
        task.watchdog = None
        with self.assertLogs(LOG, level=logging.DEBUG) as cm:
            result = task.transition()
        self.assertIs(result, False, "返回字符串不算完成")
        self.assertEqual(task.operationer.next_scene, SCENE_C)
        self.assertEqual(calls, [SCENE_A])
        self.assertIn("声明落点", "\n".join(cm.output))

    def test_registered_handler_true_completes(self):
        calls = []
        task = _make_task([SCENE_A], handlers={SCENE_A: _handler(calls, SCENE_A, True)})
        self.assertIs(task.transition(), True, "True 仍是完成信号")

    def test_unregistered_scene_handler_string_declares(self):
        calls = []
        task = _make_task(["某个陌生画面"], scenes=(SCENE_A,),
                          handlers={"未注册场景": _handler(calls, "未注册场景", SCENE_A)})
        task.transition()
        self.assertEqual(calls, ["未注册场景"])
        self.assertEqual(task.operationer.next_scene, SCENE_A,
                         "「未注册场景」处理函数返回字符串同样生效")


class PendingJumpSemanticsTest(unittest.TestCase):
    """声明落点之后的四种走向（全部复用既有 _pending_jump_path 语义）。"""

    def test_arrival_clears_declaration_and_runs_handler(self):
        calls = []
        task = _make_task([SCENE_A, SCENE_C],
                          handlers={SCENE_A: _handler(calls, SCENE_A, SCENE_C),
                                    SCENE_C: _handler(calls, SCENE_C, True)})
        task.transition()                       # 第 1 帧：A → 声明 C
        self.assertEqual(task.operationer.next_scene, SCENE_C)
        result = task.transition()              # 第 2 帧：识别到 C → 到达
        self.assertIs(result, True)
        self.assertIsNone(task.operationer.next_scene, "到达后自动清除声明")
        self.assertEqual(calls, [SCENE_A, SCENE_C])

    def test_not_arrived_with_path_jumps(self):
        calls = []
        task = _make_task([SCENE_A, SCENE_B], path=[SCENE_B, SCENE_C],
                          handlers={SCENE_A: _handler(calls, SCENE_A, SCENE_C)})
        task.transition()                       # 声明 C
        task.transition()                       # 识别到 B → 有路 → 按图纠偏
        self.assertEqual(task.transition_manager.calls, [(SCENE_C,)],
                         "未到达但图上有路 → 触发跳转纠偏")
        self.assertEqual(task.operationer.next_scene, SCENE_C, "纠偏期间保留声明")

    def test_no_path_keeps_declaration_and_runs_handler(self):
        calls = []
        task = _make_task([SCENE_A, SCENE_B], path=[],
                          handlers={SCENE_A: _handler(calls, SCENE_A, SCENE_C),
                                    SCENE_B: _handler(calls, SCENE_B, False)})
        task.transition()
        task.transition()
        self.assertEqual(task.transition_manager.calls, [], "无路不跳转")
        self.assertEqual(task.operationer.next_scene, SCENE_C,
                         "无路时保留声明（画面变化后仍有机会）")
        self.assertEqual(calls, [SCENE_A, SCENE_B], "交回当前画面的处理函数")

    def test_stalled_jump_is_abandoned_with_screenshot(self):
        calls = []
        task = _make_task([SCENE_A, SCENE_B], path=[SCENE_B, SCENE_C],
                          handlers={SCENE_A: _handler(calls, SCENE_A, SCENE_C),
                                    SCENE_B: _handler(calls, SCENE_B, False)})
        task._auto_screenshot = _auto_screenshot.__get__(task)
        with self.assertLogs(LOG, level=logging.WARNING) as cm:
            for _ in range(5):                  # 1 次声明 + 4 次跳转尝试
                task.transition()
        self.assertEqual(len(task.transition_manager.calls), 3,
                         "跳转未推进保护：最多尝试 JUMP_STALL_LIMIT(3) 次")
        self.assertIsNone(task.operationer.next_scene, "超限后放弃声明")
        self.assertIsNone(task._jump_stall, "放弃后计数清零")
        self.assertIn(SCREENSHOT_REASON_JUMP_STALLED, task.screenshot_reasons)
        self.assertIn("未生效", "\n".join(cm.output))
        self.assertIn(SCENE_B, calls, "放弃后把控制权交回当前画面处理函数")


class ExecuteLoopTest(unittest.TestCase):
    """端到端 `_execute`：返回字符串**不**完成任务；只有 True / TaskCompleted 才完成。"""

    def _run(self, task):
        with self.assertLogs(LOG, level=logging.DEBUG) as cm:
            task._execute()
        return "\n".join(cm.output)

    def test_declared_then_arrival_completes(self):
        calls = []
        task = _make_task([SCENE_A, SCENE_C],
                          handlers={SCENE_A: _handler(calls, SCENE_A, SCENE_C),
                                    SCENE_C: _handler(calls, SCENE_C, True)})
        logs = self._run(task)
        self.assertEqual(calls, [SCENE_A, SCENE_C],
                         "第 1 帧声明落点不算完成；第 2 帧到达后由 handler 返回 True 完成")
        self.assertIn("结果=完成", logs)
        self.assertIsNone(task.operationer.next_scene)

    def test_truthy_non_true_does_not_complete(self):
        calls = []
        state = {"n": 0}

        def handler(task):
            state["n"] += 1
            calls.append(state["n"])
            return 123 if state["n"] == 1 else True

        task = _make_task([SCENE_A, SCENE_A], handlers={SCENE_A: handler})
        logs = self._run(task)
        self.assertEqual(calls, [1, 2], "非 True 的真值不完成 → 任务继续循环")
        self.assertIn("不视为任务完成", logs)
        self.assertIn("结果=完成", logs)

    def test_true_completes_immediately(self):
        calls = []
        task = _make_task([SCENE_A], handlers={SCENE_A: _handler(calls, SCENE_A, True)})
        logs = self._run(task)
        self.assertIn("结果=完成", logs)
        self.assertEqual(calls, [SCENE_A])


class LegacyTaskRegressionTest(unittest.TestCase):
    """既有先例（XiaoHaoTiLi 的「设 next_scene 再 return False」）行为不变。"""

    def _task(self, order, progress, check=True):
        task = object.__new__(XiaoHaoTiLi)
        task.logger = logging.getLogger(LOG)
        task.execute_order = list(order)
        task.execute_progress = progress
        task.current_task = ""
        task.check = check
        task.operationer = SimpleNamespace(next_scene=None)
        return task

    def test_set_next_scene_declares_and_returns_false(self):
        task = self._task(["装备"], {"装备": {"是否完成": False, "场景": "装备"}})
        result = XiaoHaoTiLi._XiaoHaoTiLi__set_next_scene(task)
        self.assertIs(result, False, "返回 False → 不触发完成（旧语义保持）")
        self.assertEqual(task.operationer.next_scene, "装备")
        self.assertEqual(task.current_task, "装备")

    def test_set_next_scene_raises_when_finished(self):
        task = self._task(["装备"], {"装备": {"是否完成": True, "场景": "装备"}})
        with self.assertRaises(TaskCompleted):
            XiaoHaoTiLi._XiaoHaoTiLi__set_next_scene(task)

    def test_source_handler_old_style_still_works(self):
        task = self._task([], {}, check=False)
        result = XiaoHaoTiLi.transition_func[XiaoHaoTiLi.source_scene](task)
        self.assertIs(result, False)
        self.assertEqual(task.operationer.next_scene, "冒险-冒险副本")


class FrameworkInvariantTest(unittest.TestCase):
    """源码级防回退：完成判定与返回值归一化不能被改回旧写法。"""

    def test_source_invariants(self):
        source = (Path(_PROJECT_ROOT) / "backend" / "core" / "legacy" / "Task"
                  / "BaseTask.py").read_text(encoding="utf-8")
        self.assertIn("if self.transition() is True:", source,
                      "完成判定必须是 is True（只有 True/TaskCompleted 才算完成）")
        self.assertEqual(
            source.count("return self._normalize_handler_result(result)"), 2,
            "两个场景处理函数调用点都必须归一化返回值")


if __name__ == "__main__":
    unittest.main(verbosity=2)
