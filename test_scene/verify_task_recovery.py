# -*- coding: utf-8 -*-
"""验证「卡死恢复职责下沉任务线程 + 停止原因驱动的重排期」。

背景（2026-09-16 21:10~21:15 叛忍来袭现场日志）：
1. 任务在「叛忍来袭-即将开始」合法等待活动开启，超过全局 180 秒被判 [SCENE_STUCK]；
2. 调度器收到告警后**先** `stop_task`（置 operationer.stop_event）**再**调用
   `_handle_scene_stuck` 去点 X 脱困 —— 而 `Operationer._search_loop` 首轮就
   `if self._should_stop(): raise Stop`，救援 100% 失败，且每次告警都留下一条
   ERROR traceback（"场景停滞处理失败"）；
3. 任务被停止后"下次执行时间"仍停在过去时刻（结果=被停止 | 下次执行=21:10:06），
   只要任务仍处于启用状态就会被调度器按扫描间隔立刻重跑。

本脚本覆盖（全部离线，不依赖设备 / 配置 / 模拟器）：
1. 停止原因透传：`TaskExecutor.stop_task(task, reason)` → `BaseTask.stop(reason)`，
   旧式只接受无参 `stop()` 的对象兼容；
2. `Operationer.ignoring_stop()`：救援期间停止检查不触发，退出后**原样恢复**；
3. `SchedulerService._handle_scene_stuck`：停止标志已置位时仍能真正执行脱困点击，
   且 `Stop` 只记 INFO、不再记 ERROR traceback；
4. 监视器恢复契约：`_raise` 挂恢复请求 → 任务线程 `consume_recovery_request` 取走；
   `wait_recovery_done` 在任务应答后返回 True、未应答时按宽限超时返回 False；
   `detach_task` 清理残留请求；`task_recovery_grace` 读配置 / 非法值回退并告警一次；
5. `BaseTask._handle_recovery_request`：自救成功 → 应答监视器并继续执行；
   自救失败/异常 → 应答监视器后抛 `Stop`（交给 on_stuck 重排期）；
   无监视器 / 无告警 → 零副作用直接返回；
6. `BaseTask.recover_from_stuck` 默认实现：场景图有路 → 按图回源；无路 → 通用退出
   点击（X / 返回）；都不可行 → False；
7. 卡死类停止原因 → `on_stuck` 冷却重试（写入下次执行时间），普通停止保持原排期；
8. 端到端：真实 `_execute` 循环里消费恢复请求 → 自救成功后任务继续跑到完成。

运行：.venv\\Scripts\\python.exe -X utf8 test_scene\\verify_task_recovery.py
"""
import logging
import os
import sys
import threading
import time
import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.core.legacy.Exceptions import (  # noqa: E402
    STOP_REASON_FROZEN,
    STOP_REASON_STUCK,
    Stop,
    TaskCompleted,
)
from backend.core.legacy.Operationer import Operationer  # noqa: E402
from backend.core.legacy.Task.BaseTask import (  # noqa: E402
    BaseTask,
    handle_task_exceptions,
)
from backend.core.legacy.Task.schedule import AnyTime  # noqa: E402
from backend.core.scheduler.executor import TaskExecutor, _request_stop  # noqa: E402
from backend.services.scheduler_service import SchedulerService  # noqa: E402
from backend.services.watchdog_service import (  # noqa: E402
    DEFAULT_TASK_RECOVERY_GRACE_SECONDS,
    FreezeLevel,
    TimeoutWatchdog,
)

TZ = ZoneInfo("Asia/Shanghai")
LOG = "verify.recovery"
STUCK_SCENE = "叛忍来袭-即将开始"
SOURCE_SCENE = "主场景-组织"


# --------------------------------------------------------------------------- #
#                                   公共替身                                    #
# --------------------------------------------------------------------------- #
class _FakeConfig:
    """最小 Config 替身：任务基础配置 + 全局设置。"""

    def __init__(self, **settings):
        self.base = {"下次执行时间": 0}
        self.settings = {"用户名": "verify_user", "错误自动截图": True}
        self.settings.update(settings)
        self.config_type = "持久"

    def get_task_base_config(self, task_name, key, default=None):
        return self.base.get(key, default)

    def set_task_base_config(self, task_name, key, value):
        self.base[key] = value

    def get_config(self, key, default=None):
        return self.settings.get(key, default)

    def get_task_exe_param(self, task_name, param, default=None):
        return default


class _FakeClicker:
    def __init__(self):
        self.stop_calls = 0

    def stop(self):
        self.stop_calls += 1


class _FakeOperationer:
    """BaseTask 侧所需字段的最小替身。"""

    def __init__(self):
        self.clicker = _FakeClicker()
        self.screen_save_func = lambda *args: None
        self.next_scene = None
        self.task_name = ""
        self.stop_event = threading.Event()


class _RecordingWatchdog:
    """只记录"被消费/被应答"的监视器替身。"""

    def __init__(self, event=None, consume_times=1):
        self._event = event
        self._consume_times = consume_times
        self.consume_calls = 0
        self.notified = []
        self.heartbeats = []

    def consume_recovery_request(self):
        self.consume_calls += 1
        if self._event is None or self.consume_calls > self._consume_times:
            return None
        return self._event

    def notify_recovery_done(self, level):
        self.notified.append(level)

    def heartbeat(self, scene_name=None):
        self.heartbeats.append(scene_name)


def _make_task_attrs(task, config=None):
    """补齐"不跑 __init__ 的任务实例"所需属性（沿用既有 verify 脚本约定）。"""
    task.task_name = "编号任务"
    task.tz_info = TZ
    task.config = config or _FakeConfig()
    task.logger = logging.getLogger("verify.task")
    task.last_run_time = datetime.now(TZ)
    task.create_time = datetime.now(TZ)
    task.current_status = 2
    task.bool_click = False
    task.force_execute_now = False
    task.ignore_time_window = True
    task.is_temp = False
    task.last_execute_error = None
    task.watchdog = None
    task.transition_return = ""
    task.last_unregistered_scene_time = None
    task.stop_reason = ""
    task._jump_stall = None
    task.operationer = _FakeOperationer()


# --------------------------------------------------------------------------- #
#              1. 停止原因透传（executor → task.stop(reason)）                   #
# --------------------------------------------------------------------------- #
class StopReasonPassingTest(unittest.TestCase):
    """停止原因必须能透传到任务；旧式无参 stop() 不能被签名差异打断。"""

    def test_reason_passed_to_modern_stop(self):
        task = SimpleNamespace()
        task.stop = lambda reason="": setattr(task, "seen", reason)
        _request_stop(task, STOP_REASON_STUCK)
        self.assertEqual(task.seen, STOP_REASON_STUCK)

    def test_legacy_stop_without_argument_still_called(self):
        calls = []

        class _Legacy:
            def stop(self):
                calls.append(True)

        _request_stop(_Legacy(), STOP_REASON_STUCK)
        self.assertEqual(calls, [True], "旧式 stop() 必须被调用（不抛 TypeError）")

    def test_executor_stop_task_passes_reason_and_detaches(self):
        seen = {}

        class _Task:
            def stop(self, reason=""):
                seen["reason"] = reason

        class _Watchdog:
            def detach_task(self, task):
                seen["detached"] = True

        executor = TaskExecutor(watchdog=_Watchdog(), logger=logging.getLogger(LOG))
        executor.stop_task(_Task(), reason=STOP_REASON_FROZEN)
        self.assertEqual(seen["reason"], STOP_REASON_FROZEN)
        self.assertTrue(seen.get("detached"), "停止时应收回答监视器")

    def test_base_task_stop_records_reason(self):
        task = object.__new__(BaseTask)
        _make_task_attrs(task)
        task.stop(STOP_REASON_STUCK)
        self.assertEqual(task.stop_reason, STOP_REASON_STUCK)
        self.assertTrue(task.operationer.stop_event.is_set())


# --------------------------------------------------------------------------- #
#                  2. Operationer.ignoring_stop（救援可用性）                    #
# --------------------------------------------------------------------------- #
class IgnoringStopTest(unittest.TestCase):
    """救援期间临时忽略停止标志，退出后原样恢复。"""

    def _operationer(self, already_set):
        op = object.__new__(Operationer)
        op.stop_event = threading.Event()
        if already_set:
            op.stop_event.set()
        return op

    def test_ignores_and_restores_when_set(self):
        op = self._operationer(True)
        with op.ignoring_stop():
            self.assertFalse(op._should_stop(), "救援期间停止检查必须不触发")
            # 模拟 _search_loop 的首轮检查：旧实现在这里 raise Stop，救援必然失败
            if op._should_stop():
                raise AssertionError("救援期间不应抛出 Stop")
        self.assertTrue(op.stop_event.is_set(), "退出后必须原样恢复停止标志")

    def test_keeps_clear_when_not_set(self):
        op = self._operationer(False)
        with op.ignoring_stop():
            pass
        self.assertFalse(op.stop_event.is_set(), "原本未置位时不得被置位")

    def test_restores_on_exception(self):
        op = self._operationer(True)
        with self.assertRaises(ValueError):
            with op.ignoring_stop():
                raise ValueError("boom")
        self.assertTrue(op.stop_event.is_set(), "异常退出也要恢复停止标志")


# --------------------------------------------------------------------------- #
#            3. 调度器兜底脱困（停止标志已置位时仍能执行）                       #
# --------------------------------------------------------------------------- #
class _SearchOperationer:
    """模拟 Operationer 的停止检查语义：首轮 stop 即 `raise Stop`（旧现象）。"""

    ignoring_stop = Operationer.ignoring_stop  # 借用真实实现

    def __init__(self, hit=True, x_elements=True):
        self.stop_event = threading.Event()
        self.stop_event.set()          # 救援发生时任务已被要求停止
        self.hit = hit
        self.x_elements = x_elements
        self.search_calls = 0
        self.click_calls = 0

    def _should_stop(self):
        return self.stop_event.is_set()

    def get_element(self, name, scene_name=None):
        if self.x_elements and name.startswith("X-"):
            return SimpleNamespace(name=name)
        return None

    def search_and_click(self, elements, actions, **kwargs):
        if self._should_stop():
            raise Stop
        self.search_calls += 1
        return 1 if self.hit else 0

    def click_and_wait(self, element, **kwargs):
        self.click_calls += 1
        return False


class SceneStuckFallbackTest(unittest.TestCase):
    """`_handle_scene_stuck`：救援动作必须真正执行，Stop 不再记 ERROR。"""

    def _service(self, operationer):
        service = object.__new__(SchedulerService)
        service.logger = logging.getLogger(LOG)
        service.operationer = operationer
        return service

    def test_fallback_executes_with_stop_flag_set(self):
        op = _SearchOperationer(hit=True)
        service = self._service(op)
        with self.assertLogs(LOG, level=logging.DEBUG) as cm:
            service._handle_scene_stuck(SimpleNamespace(scene_name=STUCK_SCENE))
        logs = "\n".join(cm.output)
        self.assertEqual(op.search_calls, 1,
                         "脱困点击必须真正执行（旧实现在此被 Stop 拦死）")
        self.assertIn("已点击 X 元素", logs)
        self.assertNotIn("场景停滞处理失败", logs, "Stop 不属于处理失败，不得记 ERROR")
        self.assertTrue(op.stop_event.is_set(), "救援结束必须恢复停止标志")

    def test_stop_inside_fallback_is_info_only(self):
        op = _SearchOperationer()

        def _raise_stop(*args, **kwargs):
            raise Stop

        op.search_and_click = _raise_stop
        service = self._service(op)
        with self.assertLogs(LOG, level=logging.DEBUG) as cm:
            service._handle_scene_stuck(SimpleNamespace(scene_name=STUCK_SCENE))
        logs = "\n".join(cm.output)
        self.assertIn("停止请求已置位，跳过兜底脱困", logs)
        self.assertNotIn("场景停滞处理失败", logs)


# --------------------------------------------------------------------------- #
#                  4. 监视器恢复契约（请求 / 等待 / 清理）                       #
# --------------------------------------------------------------------------- #
class _WatchdogTask:
    """监视器 attach/detach 所需的最小任务替身。"""

    def __init__(self, name="叛忍来袭"):
        self.task_name = name
        self.watchdog = None

    def attach_watchdog(self, watchdog):
        self.watchdog = watchdog

    def detach_watchdog(self):
        self.watchdog = None


def _watchdog_with(**values):
    values = {"超时检测-启用": True, **values}

    def _get(key, default=None):
        return values.get(key, default)

    return TimeoutWatchdog(
        config=SimpleNamespace(get_config=_get),
        device=None,
        operationer=None,
        logger=logging.getLogger(LOG),
    )


class WatchdogRecoveryContractTest(unittest.TestCase):
    """告警 → 挂请求 → 任务取走 → 任务应答 → 解除；超时与残留清理。"""

    def test_raise_attaches_one_shot_request(self):
        watchdog = _watchdog_with()
        watchdog.attach_task(_WatchdogTask())
        watchdog._raise(FreezeLevel.SCENE_STUCK,
                        f"任务停滞在场景 [{STUCK_SCENE}] 已超过 180 秒")
        event = watchdog.consume_recovery_request()
        self.assertIsNotNone(event, "告警必须挂上恢复请求供任务线程消费")
        self.assertEqual(event.level, FreezeLevel.SCENE_STUCK)
        self.assertIsNone(watchdog.consume_recovery_request(), "请求是一次性的")

    def test_wait_recovery_done_after_task_ack(self):
        watchdog = _watchdog_with()
        watchdog.attach_task(_WatchdogTask())
        watchdog._raise(FreezeLevel.SCENE_STUCK, "detail")

        def _ack():
            time.sleep(0.1)
            watchdog.notify_recovery_done(FreezeLevel.SCENE_STUCK)

        threading.Thread(target=_ack, daemon=True).start()
        self.assertTrue(watchdog.wait_recovery_done(3.0),
                        "任务应答后必须立刻返回 True（无需等满宽限期）")

    def test_wait_recovery_done_times_out(self):
        watchdog = _watchdog_with()
        watchdog.attach_task(_WatchdogTask())
        watchdog._raise(FreezeLevel.SCENE_STUCK, "detail")
        started = time.monotonic()
        self.assertFalse(watchdog.wait_recovery_done(0.3),
                         "任务未应答时必须按宽限超时返回 False（交调度器强制停止）")
        self.assertGreaterEqual(time.monotonic() - started, 0.25)

    def test_detach_clears_pending_request(self):
        watchdog = _watchdog_with()
        task = _WatchdogTask()
        watchdog.attach_task(task)
        watchdog._raise(FreezeLevel.SCENE_STUCK, "detail")
        watchdog.detach_task(task)
        self.assertIsNone(watchdog.consume_recovery_request(),
                          "任务被收回后残留请求不得再被执行")

    def test_task_recovery_grace_reads_config_and_falls_back(self):
        self.assertEqual(_watchdog_with().task_recovery_grace(),
                         DEFAULT_TASK_RECOVERY_GRACE_SECONDS)
        self.assertEqual(
            _watchdog_with(**{"超时检测-任务自恢复宽限秒": 5}).task_recovery_grace(),
            5.0)
        watchdog = _watchdog_with(**{"超时检测-任务自恢复宽限秒": "abc"})
        with self.assertLogs(LOG, level=logging.WARNING) as cm:
            self.assertEqual(watchdog.task_recovery_grace(),
                             DEFAULT_TASK_RECOVERY_GRACE_SECONDS)
        self.assertTrue([r for r in cm.records
                         if "超时检测-任务自恢复宽限秒" in r.getMessage()],
                        "非法配置必须留痕（不静默回退）")


# --------------------------------------------------------------------------- #
#            5. BaseTask 自救消费（成功 / 失败 / 异常 / 无告警）                 #
# --------------------------------------------------------------------------- #
class _RecoveryTask(BaseTask):
    source_scene = SOURCE_SCENE
    schedule = AnyTime()

    def reset_task_exe_prog(self):
        return True

    def callback(self, task):
        pass


def _recovery_task(recover=None, watchdog=None):
    task = object.__new__(_RecoveryTask)
    _make_task_attrs(task)
    task.watchdog = watchdog
    if recover is not None:
        task.recover_from_stuck = recover
    return task


def _stuck_event():
    return SimpleNamespace(level=FreezeLevel.SCENE_STUCK, scene_name=STUCK_SCENE,
                           detail="任务停滞在场景 [叛忍来袭-即将开始] 已超过 180 秒")


class TaskSelfRecoveryTest(unittest.TestCase):
    """任务线程内的自救消费：应答监视器 + 成功继续 / 失败抛 Stop。"""

    def test_success_notifies_and_continues(self):
        watchdog = _RecordingWatchdog(event=_stuck_event())
        task = _recovery_task(recover=lambda scene: True, watchdog=watchdog)
        task.last_unregistered_scene_time = time.perf_counter() - 10
        task._jump_stall = {"key": ("a", "b"), "count": 2}
        with self.assertLogs("verify.task", level=logging.DEBUG) as cm:
            task._handle_recovery_request()
        logs = "\n".join(cm.output)
        self.assertIn("卡死自救成功", logs)
        self.assertEqual(watchdog.notified, [FreezeLevel.SCENE_STUCK],
                         "自救成功后必须应答监视器（解除告警挂起）")
        self.assertIsNone(task._jump_stall, "自救成功后应清空跳转未推进计数")
        self.assertIsNone(task.last_unregistered_scene_time)

    def test_failure_notifies_then_raises_stop(self):
        watchdog = _RecordingWatchdog(event=_stuck_event())
        task = _recovery_task(recover=lambda scene: False, watchdog=watchdog)
        with self.assertLogs("verify.task", level=logging.DEBUG) as cm:
            with self.assertRaises(Stop):
                task._handle_recovery_request()
        logs = "\n".join(cm.output)
        self.assertIn("卡死自救失败", logs)
        self.assertEqual(watchdog.notified, [FreezeLevel.SCENE_STUCK],
                         "失败也要应答（否则调度器白等满宽限期做重复兜底）")

    def test_exception_notifies_then_raises_stop(self):
        def _boom(scene):
            raise ValueError("boom")

        watchdog = _RecordingWatchdog(event=_stuck_event())
        task = _recovery_task(recover=_boom, watchdog=watchdog)
        with self.assertLogs("verify.task", level=logging.DEBUG) as cm:
            with self.assertRaises(Stop):
                task._handle_recovery_request()
        logs = "\n".join(cm.output)
        self.assertIn("卡死自救异常", logs)
        self.assertEqual(watchdog.notified, [FreezeLevel.SCENE_STUCK])

    def test_no_watchdog_or_no_event_is_noop(self):
        called = []
        task = _recovery_task(recover=lambda scene: called.append(scene) or True,
                              watchdog=None)
        task._handle_recovery_request()
        self.assertEqual(called, [], "无监视器时不得执行自救")

        watchdog = _RecordingWatchdog(event=None)
        task = _recovery_task(recover=lambda scene: called.append(scene) or True,
                              watchdog=watchdog)
        task._handle_recovery_request()
        self.assertEqual(called, [], "无告警时不得执行自救")
        self.assertEqual(watchdog.notified, [])


# --------------------------------------------------------------------------- #
#            6. 默认自救实现：按图回源 → 通用退出点击                           #
# --------------------------------------------------------------------------- #
class _RecoverOperationer:
    def __init__(self, x_hit=False, back_exists=False):
        self.next_scene = None
        self._x_hit = x_hit
        self._back_exists = back_exists
        self.search_calls = 0
        self.clicks = []

    def get_element(self, name, scene_name=None):
        if name.startswith("X-"):
            return SimpleNamespace(name=name)
        if name == "返回" and self._back_exists:
            return SimpleNamespace(name="返回")
        return None

    def search_and_click(self, elements, actions, **kwargs):
        self.search_calls += 1
        return 1 if self._x_hit else 0

    def click_and_wait(self, element, **kwargs):
        self.clicks.append(getattr(element, "name", element))
        return self._back_exists


class _FakeTransitionManager:
    def __init__(self, path=None):
        self._path = list(path or [])
        self.transitions = []

    def bfs_shortest_path(self, start, goal):
        return list(self._path)

    def transition(self, operationer):
        self.transitions.append(operationer.next_scene)
        return True


class DefaultRecoverFromStuckTest(unittest.TestCase):
    """默认 `recover_from_stuck`：先按图回源，回不了才做通用退出点击。"""

    def _task(self, path=None, x_hit=False, back_exists=False):
        task = _recovery_task()
        task.operationer = _RecoverOperationer(x_hit=x_hit, back_exists=back_exists)
        task.transition_manager = _FakeTransitionManager(path)
        return task

    def test_graph_path_returns_to_source(self):
        task = self._task(path=["组织", "主场景", SOURCE_SCENE])
        with self.assertLogs("verify.task", level=logging.DEBUG) as cm:
            ok = task.recover_from_stuck("组织")
        self.assertTrue(ok)
        self.assertEqual(task.operationer.next_scene, SOURCE_SCENE,
                         "有路时必须挂上回源目标走按图寻路")
        self.assertEqual(task.transition_manager.transitions, [SOURCE_SCENE])
        self.assertIn("按图回源", "\n".join(cm.output))
        self.assertEqual(task.operationer.search_calls, 0,
                         "有路可走时不应退化为盲点 X")

    def test_no_path_falls_back_to_x_click(self):
        task = self._task(path=[], x_hit=True)
        with self.assertLogs("verify.task", level=logging.DEBUG) as cm:
            ok = task.recover_from_stuck("组织")
        self.assertTrue(ok)
        self.assertIn("已点击 X 元素", "\n".join(cm.output))
        self.assertEqual(task.transition_manager.transitions, [])

    def test_no_path_no_x_falls_back_to_back(self):
        task = self._task(path=[], x_hit=False, back_exists=True)
        with self.assertLogs("verify.task", level=logging.DEBUG) as cm:
            ok = task.recover_from_stuck("组织")
        self.assertTrue(ok)
        self.assertIn("已点击返回", "\n".join(cm.output))

    def test_nothing_available_returns_false(self):
        task = self._task(path=[], x_hit=False, back_exists=False)
        self.assertFalse(task.recover_from_stuck("组织"),
                         "既回不了源、也点不到退出元素 → 视为自救失败")

    def test_already_at_source_skips_graph_jump(self):
        task = self._task(path=["不应被使用"], x_hit=True)
        self.assertTrue(task.recover_from_stuck(SOURCE_SCENE))
        self.assertEqual(task.transition_manager.transitions, [],
                         "已在源场景时不应再触发回源跳转")


# --------------------------------------------------------------------------- #
#            7. 卡死类停止原因 → on_stuck 冷却重试（不再是过去时刻）            #
# --------------------------------------------------------------------------- #
class _StopTask(BaseTask):
    source_scene = SOURCE_SCENE
    schedule = AnyTime()
    task_max_duration = timedelta(minutes=10)

    def __init__(self, stop_reason=""):
        _make_task_attrs(self)
        self.stop_reason = stop_reason

    @handle_task_exceptions
    def _execute(self):
        raise Stop("任务被停止")

    def reset_task_exe_prog(self):
        return True

    def callback(self, task):
        pass


class StuckStopRescheduleTest(unittest.TestCase):
    """卡死类停止必须重排期；普通停止保持原排期（回归保护）。"""

    def _run(self, stop_reason):
        task = _StopTask(stop_reason)
        with self.assertLogs("verify.task", level=logging.DEBUG) as cm:
            task._execute()
        return task, "\n".join(cm.output)

    def test_stuck_reason_reschedules_with_cooldown(self):
        for reason in (STOP_REASON_STUCK, STOP_REASON_FROZEN):
            with self.subTest(reason=reason):
                task, logs = self._run(reason)
                self.assertIn("结果=卡死停止", logs)
                self.assertIn("收到卡死类停止请求", logs)
                delay = (task.config.base["下次执行时间"]
                         - datetime.now(TZ).timestamp())
                self.assertAlmostEqual(
                    delay, task.error_retry_delay.total_seconds(), delta=10,
                    msg="卡死停止必须按 on_stuck 写入冷却重试时间"
                        "（否则下次执行时间留在过去 → 被立刻重跑）")

    def test_plain_stop_keeps_original_schedule(self):
        task, logs = self._run("")
        self.assertIn("结果=被停止", logs)
        self.assertIn("按原下次执行时间继续", logs)
        self.assertEqual(task.config.base["下次执行时间"], 0,
                         "普通停止（抢占/手动）不得改写下次执行时间")


# --------------------------------------------------------------------------- #
#            8. 端到端：真实 _execute 循环里自救成功 → 继续跑到完成             #
# --------------------------------------------------------------------------- #
class _LoopRecognizer:
    def scene(self, screenshot, bool_debug=False, hint=None, allow_full_scan=True):
        return SimpleNamespace(name="主场景")


class _LoopOperationer(_FakeOperationer):
    def __init__(self):
        super().__init__()
        self.recognizer = _LoopRecognizer()
        self.current_scene = None

    def screen_cap(self):
        return object()


class _LoopTask(BaseTask):
    source_scene = SOURCE_SCENE
    schedule = AnyTime()
    task_max_duration = timedelta(minutes=10)

    def reset_task_exe_prog(self):
        return True

    def callback(self, task):
        pass


class EndToEndRecoveryLoopTest(unittest.TestCase):
    """第一轮消费告警并自救成功 → 任务不被停止，继续执行到完成。"""

    def test_recovery_success_keeps_task_running(self):
        task = object.__new__(_LoopTask)
        _make_task_attrs(task)
        task.operationer = _LoopOperationer()
        task.transition_manager = _FakeTransitionManager([])
        recovered = []
        task.recover_from_stuck = lambda scene: (recovered.append(scene), True)[1]
        watchdog = _RecordingWatchdog(event=_stuck_event())
        task.watchdog = watchdog
        task.transition_func = {"主场景": lambda t: True}
        with self.assertLogs("verify.task", level=logging.DEBUG) as cm:
            task._execute()
        logs = "\n".join(cm.output)
        self.assertIn("收到卡死告警", logs)
        self.assertIn("卡死自救成功，继续执行任务", logs)
        self.assertIn("结果=完成", logs)
        self.assertEqual(recovered, [STUCK_SCENE])
        self.assertEqual(watchdog.notified, [FreezeLevel.SCENE_STUCK])
        self.assertFalse(task.operationer.stop_event.is_set(),
                         "自救成功不得顺带停止任务")

    def test_recovery_failure_stops_and_reschedules(self):
        task = object.__new__(_LoopTask)
        _make_task_attrs(task)
        task.operationer = _LoopOperationer()
        task.transition_manager = _FakeTransitionManager([])
        task.recover_from_stuck = lambda scene: False
        task.watchdog = _RecordingWatchdog(event=_stuck_event())
        # 自救失败会在循环里抛 Stop，此时 stop_reason 由调度器提前写入
        task.stop_reason = STOP_REASON_STUCK
        task.transition_func = {"主场景": lambda t: True}
        with self.assertLogs("verify.task", level=logging.DEBUG) as cm:
            task._execute()
        logs = "\n".join(cm.output)
        self.assertIn("卡死自救失败", logs)
        self.assertIn("结果=卡死停止", logs)
        self.assertGreater(task.config.base["下次执行时间"], 0,
                           "自救失败必须重排期，避免过去时刻被立刻重跑")


if __name__ == "__main__":
    unittest.main(verbosity=2)
