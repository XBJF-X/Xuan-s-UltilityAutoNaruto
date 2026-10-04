# -*- coding: utf-8 -*-
"""验证 BaseTask 任务执行日志与失败重试节流。

背景：任务执行的日志原先集中在 handle_task_exceptions / handle_transition_exceptions
两个装饰器里，存在这些问题——超时分支丢弃异常详情、未知异常没有 traceback、错误截图
原因未透传（走了"保存截图"开关且文件名不含原因）、跳过窗口与场景日志每轮循环重复刷屏、
步骤失败/未知异常后不重排期（按扫描间隔默认 1s 无限重试）。

本脚本覆盖（全部离线，不依赖设备/配置/模拟器）：
1. 装饰器保留函数名（functools.wraps）；
2. 开始日志：触发方式（正常排期 / 立即执行 / 预设顺序）+ 排期规则 + 最长执行时长；
3. 结束汇总：结果 / 详情 / 耗时 / 下次执行时间；
4. 步骤失败：ERROR 含类型+消息+位置+截图标记，清理并冷却重试；
5. 窗口超时 / 执行超时：ERROR 保留异常详情；
6. 未捕获异常：ERROR 含 traceback，且同样冷却重试；
7. 被停止：WARNING + 不写下次执行时间（被抢占任务按原排期继续）；
8. 未到执行时间：结果=未到执行时间 + 重排期；
9. 真实 _execute 循环：跳过窗口说明与场景日志去重（同一场景只输出一条 INFO）。
"""
import logging
import os
import sys
import threading
import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.core.legacy.Exceptions import (  # noqa: E402
    StepFailedError,
    Stop,
    TaskCompleted,
    TimeOutDeadLineError,
    TimeOutMaxDurationError,
    TooEarlyToRun,
)
from backend.core.legacy.Task.BaseTask import (  # noqa: E402
    BaseTask,
    handle_task_exceptions,
)
from backend.core.legacy.Task.schedule import AnyTime  # noqa: E402

TZ = ZoneInfo("Asia/Shanghai")


class _FakeConfig:
    """最小 Config 替身：下次执行时间记录在内存字典，便于断言是否被写入。"""

    def __init__(self, config_type="持久"):
        self.base = {"下次执行时间": 0}
        self.config_type = config_type
        self.execute_params = {}
        self.settings = {"用户名": "verify_user", "错误自动截图": True}

    def get_task_base_config(self, task_name, key, default=None):
        if key in self.base:
            return self.base[key]
        return default

    def set_task_base_config(self, task_name, key, value):
        self.base[key] = value

    def get_task_exe_param(self, task_name, param_name, default=None):
        return self.execute_params.get((task_name, param_name), default)

    def get_config(self, key, default=None):
        return self.settings.get(key, default)


class _FakeClicker:
    def __init__(self):
        self.stop_calls = 0

    def stop(self):
        self.stop_calls += 1


class _FakeOperationer:
    """仅含 BaseTask 需要的字段；save_recorder 记录 screen_save_func 的调用参数。"""

    def __init__(self, save_recorder=None):
        self.clicker = _FakeClicker()
        self.screen_save_func = save_recorder or (lambda *args: None)
        self.next_scene = None
        self.task_name = ""
        self.stop_event = threading.Event()


def _make_attrs(task, config=None, save_recorder=None, force=False, ignore=False):
    """给"不跑 __init__ 的任务实例"补齐装饰器/日志路径所需属性。"""
    task.task_name = "编号任务"
    task.tz_info = TZ
    task.config = config or _FakeConfig()
    task.logger = logging.getLogger("verify.task")
    task.last_run_time = datetime.now(TZ)
    task.create_time = datetime.now(TZ)
    task.current_status = 2
    task.bool_click = False
    task.force_execute_now = force
    task.ignore_time_window = ignore
    task.is_temp = False
    task.last_execute_error = None
    task.watchdog = None
    task.transition_return = ""
    task.last_unregistered_scene_time = None
    task.reset_calls = 0
    task.callback_calls = 0
    task.operationer = _FakeOperationer(save_recorder)


class _BodyTask(BaseTask):
    """把 _execute 的"任务体"换成用例给定函数，其余（装饰器/日志/收尾）走真实逻辑。"""

    source_scene = "主场景"
    schedule = AnyTime()
    task_max_duration = timedelta(minutes=10)

    def __init__(self, body, config=None, save_recorder=None, force=False,
                 ignore=False):
        _make_attrs(self, config, save_recorder, force, ignore)
        self._body = body

    @handle_task_exceptions
    def _execute(self):
        return self._body(self)

    def reset_task_exe_prog(self):
        self.reset_calls += 1
        return True

    def callback(self, task):
        self.callback_calls += 1


def _raise(exc):
    """构造一个直接抛出指定异常的"任务体"。"""

    def _body(task):
        raise exc

    return _body


class ExecutionLogTest(unittest.TestCase):
    """各异常分支的日志与收尾动作"""

    def _run(self, body, **kwargs):
        task = _BodyTask(body, **kwargs)
        with self.assertLogs("verify.task", level=logging.DEBUG) as cm:
            task._execute()
        return task, "\n".join(cm.output)

    def test_start_and_summary_on_complete(self):
        """正常完成：开始摘要 + 结束汇总，并复位进度 / 回调调度器 / 写入下次执行时间"""
        task, logs = self._run(_raise(TaskCompleted("任务执行完成")))
        self.assertIn("▶ 开始执行", logs)
        self.assertIn("触发=正常排期", logs)
        self.assertIn("排期=不限时间", logs)
        self.assertIn("最长执行=10m00s", logs)
        self.assertIn("■ 执行结束", logs)
        self.assertIn("结果=完成", logs)
        self.assertIn("耗时=", logs)
        self.assertIn("下次执行=", logs)
        self.assertEqual(task.reset_calls, 1, "完成时应复位任务执行进度")
        self.assertEqual(task.callback_calls, 1, "结束必须回调调度器")
        self.assertGreater(task.config.base["下次执行时间"], 0,
                           "完成后应写入下次执行时间")

    def test_force_trigger_in_start_log(self):
        """立即执行/被激活：开始日志标注触发方式与"跳过窗口校验"（不再每轮重复）"""
        task, logs = self._run(_raise(TaskCompleted("任务执行完成")), force=True)
        self.assertEqual(logs.count("跳过窗口校验"), 1,
                         "跳过窗口校验只应出现在开始日志里")
        self.assertIn("触发=立即执行/被激活（跳过窗口校验）", logs)

    def test_complete_message_kept_in_summary(self):
        """完成的业务说明（如未实现的占位任务）保留在结束汇总里"""
        task, logs = self._run(_raise(TaskCompleted("组织争霸任务暂未实现")))
        self.assertIn("结果=完成", logs)
        self.assertIn("详情=组织争霸任务暂未实现", logs)

    def test_step_failed_error_and_cooldown(self):
        """步骤失败：ERROR 带类型/消息/截图标记，清理并冷却重试（不再 1s 级无限重试）"""
        shots = []

        def recorder(task_name, reason=""):
            shots.append((task_name, reason))

        task, logs = self._run(_raise(StepFailedError("元素 [确定] 未定义")),
                               save_recorder=recorder)
        self.assertIn("✖ 步骤执行失败: StepFailedError: 元素 [确定] 未定义", logs)
        self.assertIn("错误截图=已保存", logs)
        self.assertIn("冷却重试=5m00s后", logs)
        self.assertEqual(shots, [("编号任务", "StepFailedError")],
                         "错误截图必须透传 reason（决定开关与文件名）")
        self.assertEqual(task.last_execute_error, "元素 [确定] 未定义")
        self.assertEqual(task.reset_calls, 1, "失败时应复位进度")
        delay = task.config.base["下次执行时间"] - datetime.now(TZ).timestamp()
        self.assertAlmostEqual(delay, 300, delta=10,
                               msg="失败后应写入约 5 分钟的冷却重试时间")
        self.assertIn("结果=步骤失败", logs)

    def test_deadline_timeout_keeps_detail(self):
        """窗口超时：ERROR 必须保留异常里的 DDL 时刻（旧实现丢弃了 e）"""
        msg = "[DeadLine]任务执行超时:2026-09-10 22:00:00"
        task, logs = self._run(_raise(TimeOutDeadLineError(msg)))
        self.assertIn("✖ 窗口超时（已到达可执行窗口截止时间）: "
                      f"TimeOutDeadLineError: {msg}", logs)
        self.assertIn("结果=窗口超时", logs)
        self.assertEqual(task.callback_calls, 1)
        self.assertGreater(task.config.base["下次执行时间"], 0)

    def test_max_duration_timeout_keeps_detail(self):
        """执行超时：ERROR 必须保留异常里的当前时刻"""
        msg = "[MaxDuration]任务执行超时:2026-09-10 14:00:00"
        task, logs = self._run(_raise(TimeOutMaxDurationError(msg)))
        self.assertIn("✖ 执行超时（超过最长执行时长 10m00s）: "
                      f"TimeOutMaxDurationError: {msg}", logs)
        self.assertIn("结果=执行超时", logs)
        self.assertEqual(task.last_execute_error, msg)

    def test_unknown_exception_has_traceback(self):
        """未捕获异常：ERROR 必须带 traceback（旧实现只有一行"未知错误"）"""
        task, logs = self._run(_raise(ValueError("boom")))
        self.assertIn("✖ 未捕获异常: ValueError: boom", logs)
        self.assertIn("Traceback (most recent call last)", logs)
        self.assertIn("冷却重试=5m00s后", logs)
        self.assertEqual(task.last_execute_error, "boom")
        self.assertEqual(task.reset_calls, 1, "未捕获异常也应复位进度")
        delay = task.config.base["下次执行时间"] - datetime.now(TZ).timestamp()
        self.assertAlmostEqual(delay, 300, delta=10)

    def test_stop_warns_and_keeps_schedule(self):
        """被停止（抢占/调度器停止/卡死处理）：只清理，不写下次执行时间"""
        task, logs = self._run(_raise(Stop("任务被停止")))
        self.assertIn("收到停止请求", logs)
        self.assertIn("结果=被停止", logs)
        self.assertEqual(task.reset_calls, 1)
        self.assertEqual(task.config.base["下次执行时间"], 0,
                         "被停止不应改写下次执行时间（按原排期继续）")
        self.assertIsNone(task.last_execute_error)

    def test_too_early_reschedules(self):
        msg = "[StartLine]未到任务可执行时间:2026-09-12 19:00:00"
        task, logs = self._run(_raise(TooEarlyToRun(msg)))
        self.assertIn("结果=未到执行时间", logs)
        self.assertIn(f"详情={msg}", logs)
        self.assertGreater(task.config.base["下次执行时间"], 0)


class _Scene:
    def __init__(self, name):
        self.name = name


class _FakeRecognizer:
    def scene(self, screenshot, bool_debug=False, hint=None, allow_full_scan=True):
        return _Scene("主场景")


class _FakeTransitionManager:
    def bfs_shortest_path(self, start, goal):
        return []

    def transition(self, operationer):
        return False


class _LoopOperationer(_FakeOperationer):
    def __init__(self, save_recorder=None):
        super().__init__(save_recorder)
        self.recognizer = _FakeRecognizer()
        self.current_scene = None

    def screen_cap(self):
        return object()


class _LoopTask(BaseTask):
    """跑真实 _execute 循环（transition → 场景处理函数）的任务壳"""

    source_scene = "主场景"
    schedule = AnyTime()
    task_max_duration = timedelta(minutes=10)

    def reset_task_exe_prog(self):
        self.reset_calls += 1
        return True

    def callback(self, task):
        self.callback_calls += 1


def _handler_complete_after(task):
    task.handler_calls += 1
    return task.handler_calls >= task.succeed_after


def _handler_step_failed(task):
    task.handler_calls += 1
    raise StepFailedError("元素 [确定] 未定义")


class LoopExecutionLogTest(unittest.TestCase):
    """真实 _execute 循环：日志去重 + 错误日志带处理函数位置"""

    def _make_task(self, handler, succeed_after=3, ignore=True, force=False):
        task = object.__new__(_LoopTask)
        _make_attrs(task, force=force, ignore=ignore)
        task.operationer = _LoopOperationer()
        task.transition_manager = _FakeTransitionManager()
        task.transition_func = {"主场景": handler}
        task.handler_calls = 0
        task.succeed_after = succeed_after
        return task

    def test_skip_window_and_scene_logged_once(self):
        """跳过窗口说明 + 同场景识别日志都只输出一次（旧实现每轮循环重复）"""
        task = self._make_task(_handler_complete_after)
        with self.assertLogs("verify.task", level=logging.DEBUG) as cm:
            task._execute()
        logs = "\n".join(cm.output)
        self.assertEqual(logs.count("跳过窗口校验"), 1,
                         "3 轮循环只应输出一次跳过窗口说明")
        self.assertEqual(logs.count("识别到场景"), 3, "每轮 transition 各一条")
        scene_info = [r for r in cm.records if r.levelno == logging.INFO
                      and "识别到场景" in r.getMessage()]
        self.assertEqual(len(scene_info), 1,
                         "持续停留同一场景只输出一条 INFO（其余降为 DEBUG）")
        self.assertIn("结果=完成", logs)
        self.assertIn("■ 执行结束", logs)

    def test_error_log_contains_handler_location(self):
        """步骤失败日志给出出错场景处理函数的源码位置，便于直接定位"""
        task = self._make_task(_handler_step_failed)
        with self.assertLogs("verify.task", level=logging.DEBUG) as cm:
            task._execute()
        logs = "\n".join(cm.output)
        self.assertIn("✖ 步骤执行失败: StepFailedError: 元素 [确定] 未定义", logs)
        self.assertIn("位置=", logs)
        self.assertIn("verify_task_execution_logging.py", logs)
        self.assertIn("冷却重试=5m00s后", logs)


class RealTaskCompatibilityTest(unittest.TestCase):
    """真实任务类：BaseTask.__init__（RuntimeContext 注入）+ 覆写 _execute 的装饰器用法"""

    def test_zuzhi_zhengba_override_execute(self):
        from backend.core.scheduler.runtime import RuntimeContext
        from backend.core.legacy.Task.ZuZhiZhengBa import ZuZhiZhengBa

        config = _FakeConfig()
        config.base.update({
            "基础优先级": 0, "连点优先级": 0, "类型": 0,
            "是否临时": False, "是否启用": True,
        })
        reports = []
        task = ZuZhiZhengBa(RuntimeContext(
            task_name="组织争霸",
            config=config,
            transition_manager=_FakeTransitionManager(),
            operationer=_LoopOperationer(),
            activate_another_task_func=lambda *a, **k: None,
            callback=reports.append,
            parent_logger=logging.getLogger("verify.task"),
        ))
        with self.assertLogs("verify.task", level=logging.INFO) as cm:
            task._execute()   # 覆写的 _execute 同样走 handle_task_exceptions
        logs = "\n".join(cm.output)
        self.assertIn("▶ 开始执行", logs)
        self.assertIn("■ 执行结束", logs)
        self.assertIn("结果=完成", logs)
        self.assertIn("详情=组织争霸任务暂未实现", logs)
        self.assertEqual(len(reports), 1, "任务结束必须回调调度器")


class DecoratorAndDedupTest(unittest.TestCase):
    """装饰器行为与"只记一次"助手"""

    def test_functools_wraps_keeps_names(self):
        self.assertEqual(BaseTask._execute.__name__, "_execute",
                         "装饰器需保留函数名（functools.wraps），便于调试定位")
        self.assertEqual(BaseTask.transition.__name__, "transition")

    def test_log_once_outputs_single_record(self):
        task = _BodyTask(lambda t: None)
        task._reset_execute_log_state()
        with self.assertLogs("verify.task", level=logging.WARNING) as cm:
            task._log_once("k", "同一提示", logging.WARNING)
            task._log_once("k", "同一提示", logging.WARNING)
            task._log_once("k2", "另一提示", logging.WARNING)
        self.assertEqual(len(cm.records), 2, "相同 key 只输出一次，不同 key 各自输出")
        task._reset_execute_log_state()
        with self.assertLogs("verify.task", level=logging.WARNING) as cm2:
            task._log_once("k", "同一提示", logging.WARNING)
        self.assertEqual(len(cm2.records), 1, "执行开始时去重状态应被清空")


if __name__ == "__main__":
    unittest.main(verbosity=2)


