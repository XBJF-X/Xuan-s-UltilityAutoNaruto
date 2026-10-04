# -*- coding: utf-8 -*-
"""验证 [调度器] 激活另一任务时支持"指定下次执行时间"。

覆盖：
1. 不传时间 → 维持原有"登记待激活、当前任务结束后立即执行"语义（回归）；
2. 传未来时间 → 只写下次执行时间 + 临时启用，不登记待激活、不立即执行、不 scan；
3. 传已过去时间 → 立即触发一次 scan；
4. 已启用的任务被指定时间 → 启用状态不被改动；
5. 朴素时间（无 tzinfo）按 Asia/Shanghai 解释；
6. 不在队列中的任务被指定时间 → 仅告警、不抛异常；
7. BaseTask._activate_another_task 的 next_execute_time/delay 透传与默认立即执行。
"""
import logging
import os
import shutil
import sys
import tempfile
import unittest
import unittest.mock
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

_TZ = ZoneInfo("Asia/Shanghai")


def _patch_settings(ini_path):
    import backend.services.settings_service as ss_mod
    from backend.core.setting_model import Setting

    setting = Setting(parent_logger=logging.getLogger("verify"),
                      setting_path=ini_path)
    orig = ss_mod.SettingsService._get_setting
    ss_mod.SettingsService._get_setting = lambda self: setting
    return orig


def _restore_settings(orig):
    import backend.services.settings_service as ss_mod
    ss_mod.SettingsService._get_setting = orig


class ScheduledActivationTest(unittest.TestCase):

    class _FakeTask:
        """最小任务假对象（供 task_queue.get_task 命中）"""

        def __init__(self, name, activated=False):
            self.task_name = name
            self.current_status = 2
            self.is_activated = activated
            self.current_priority = 0
            self.base_priority = 0
            self.next_execute_time = None

        def __lt__(self, other):
            return self.task_name < other.task_name

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="xuan_verify_sched3_")
        ini_path = Path(self.tmp) / "setting.ini"
        ini_path.write_text("[助手设置]\r\n", encoding="utf-8")
        self._orig = _patch_settings(ini_path)

        cfg_path = Path(self.tmp) / "Config_Test.json"
        cfg_path.write_text(self._cfg_json(), encoding="utf-8")
        from backend.core.config_model import Config
        self.cfg = Config(parent_logger=logging.getLogger("verify"),
                          config_path=cfg_path)

        from backend.services.scheduler_service import SchedulerService
        self.sched = SchedulerService(config=self.cfg)
        self.sched.running = True
        self.sched.run_once = False
        for name, activated in (("消耗体力", False), ("叛忍来袭", False),
                                ("一乐外卖", True)):
            self.sched.task_queue.enqueue(self._FakeTask(name, activated))

    def tearDown(self):
        _restore_settings(self._orig)
        shutil.rmtree(self.tmp, ignore_errors=True)

    @staticmethod
    def _cfg_json():
        import json

        def task(activated):
            return {"是否启用": activated, "下次执行时间": 0, "是否临时": False,
                    "基础优先级": 0, "连点优先级": 0, "类型": 0,
                    "执行参数": {}, "执行进度": {}}
        return json.dumps({
            "配置文件版本": "V3",
            "用户名": "verify_user",
            "配置类型": "持久",
            "任务": {"一乐外卖": task(True), "消耗体力": task(False),
                     "叛忍来袭": task(False)},
        }, ensure_ascii=False)

    def _next_ts(self, task_name):
        return self.cfg.get_task_base_config(task_name, "下次执行时间")

    def _enabled(self, task_name):
        return self.cfg.get_task_base_config(task_name, "是否启用")

    # ---- 回归：不传时间仍是"登记待激活 + 结束后立即执行" ----

    def test_immediate_activation_regression(self):
        self.sched.execute_task_now = unittest.mock.Mock()
        self.sched.scan = unittest.mock.Mock()
        self.sched._on_task_activate_request("消耗体力")
        self.assertEqual(self.sched._pending_activate_tasks, ["消耗体力"])
        self.sched.execute_task_now.assert_not_called()
        self.assertEqual(self._next_ts("消耗体力"), 0,
                         "立即执行路径不应写入下次执行时间")

    # ---- 指定未来时间 ----

    def test_scheduled_future_time(self):
        self.sched.execute_task_now = unittest.mock.Mock()
        self.sched.scan = unittest.mock.Mock()
        future = datetime.now(_TZ) + timedelta(hours=2)
        self.sched._on_task_activate_request("叛忍来袭",
                                             next_execute_time=future)
        self.assertEqual(self.sched._pending_activate_tasks, [],
                         "指定时间不应登记待激活")
        self.sched.execute_task_now.assert_not_called()
        self.sched.scan.assert_not_called()
        self.assertEqual(self._next_ts("叛忍来袭"), int(future.timestamp()))
        self.assertTrue(self._enabled("叛忍来袭"),
                        "未启用任务被指定时间后应临时启用（否则扫描会跳过）")

    def test_scheduled_past_time_triggers_scan(self):
        self.sched.execute_task_now = unittest.mock.Mock()
        self.sched.scan = unittest.mock.Mock()
        past = datetime.now(_TZ) - timedelta(minutes=1)
        self.sched._on_task_activate_request("消耗体力",
                                             next_execute_time=past)
        self.sched.scan.assert_called_once()
        self.assertEqual(self.sched._pending_activate_tasks, [])

    def test_scheduled_keeps_already_enabled_task(self):
        self.sched.scan = unittest.mock.Mock()
        future = datetime.now(_TZ) + timedelta(minutes=30)
        self.sched._on_task_activate_request("一乐外卖",
                                             next_execute_time=future)
        self.assertTrue(self._enabled("一乐外卖"))
        self.assertEqual(self._next_ts("一乐外卖"), int(future.timestamp()))

    def test_naive_time_treated_as_china_tz(self):
        self.sched.scan = unittest.mock.Mock()
        naive = (datetime.now(_TZ) + timedelta(hours=3)).replace(tzinfo=None)
        self.sched._on_task_activate_request("消耗体力",
                                             next_execute_time=naive)
        expected = int(naive.replace(tzinfo=_TZ).timestamp())
        self.assertEqual(self._next_ts("消耗体力"), expected)

    def test_unknown_task_only_warns(self):
        self.sched.scan = unittest.mock.Mock()
        future = datetime.now(_TZ) + timedelta(hours=1)
        self.sched._on_task_activate_request("不存在任务",
                                             next_execute_time=future)
        self.sched.scan.assert_not_called()

    # ---- BaseTask 任务侧接口 ----

    def _make_task_stub(self):
        from backend.core.legacy.Task.MeiRiFenXiang import MeiRiFenXiang
        task = object.__new__(MeiRiFenXiang)
        task.logger = logging.getLogger("verify.task")
        task.tz_info = _TZ
        recorder = unittest.mock.Mock()
        task.activate_another_task_func = recorder
        return task, recorder

    def test_base_task_immediate_default(self):
        task, recorder = self._make_task_stub()
        task._activate_another_task("叛忍来袭")
        recorder.assert_called_once_with("叛忍来袭", next_execute_time=None)

    def test_base_task_delay_is_converted(self):
        task, recorder = self._make_task_stub()
        before = datetime.now(_TZ)
        task._activate_another_task("叛忍来袭", delay=timedelta(minutes=5))
        _args, kwargs = recorder.call_args
        next_execute_time = kwargs["next_execute_time"]
        self.assertIsNotNone(next_execute_time)
        delta = next_execute_time - before
        self.assertGreaterEqual(delta, timedelta(minutes=4, seconds=59))
        self.assertLessEqual(delta, timedelta(minutes=5, seconds=5))

    def test_base_task_both_args_prefers_explicit_time(self):
        task, recorder = self._make_task_stub()
        target = datetime.now(_TZ) + timedelta(hours=1)
        task._activate_another_task("叛忍来袭", next_execute_time=target,
                                    delay=timedelta(minutes=1))
        _args, kwargs = recorder.call_args
        self.assertEqual(kwargs["next_execute_time"], target)


if __name__ == "__main__":
    unittest.main(verbosity=2)
