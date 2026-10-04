# -*- coding: utf-8 -*-
"""验证 [调度器] 被跨任务激活的任务，若原本未激活，执行结束后恢复原状态。

覆盖：
1. 原本未启用 → 临时启用（立即执行路径）→ 任务结束后恢复为未启用；
2. 原本已启用 → 不受影响（保持启用）；
3. 用户中途手动启用（toggle_task_activation）→ 结束后保持启用；
4. 未登记的任务正常结束 → 不写启用状态（无副作用）；
5. 临时预设模式（配置类型=临时）→ 不写回配置，避免污染预设文件；
6. 指定下次执行时间（③）同样登记并在结束后恢复；
7. 调度器 stop() 清空登记，并把「临时启用」恢复为原值（未勾选 → 未启用）；
8. 临时预设模式（配置类型=临时）停机时不写回配置。
"""
import json
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


class TempActivationRestoreTest(unittest.TestCase):

    class _FakeTask:
        """最小任务假对象（供 task_queue / 完成回调使用）"""

        def __init__(self, name, activated=False):
            self.task_name = name
            self.current_status = 2
            self.is_activated = activated
            self.is_temp = False
            self.current_priority = 0
            self.base_priority = 0
            self.next_execute_time = None
            self.force_execute_now = False
            self.last_run_time = None
            self.last_execute_error = None

        def __lt__(self, other):
            return self.task_name < other.task_name

        def schedule_execute_now(self):
            return True, None

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="xuan_verify_sched4_")
        ini_path = Path(self.tmp) / "setting.ini"
        ini_path.write_text("[助手设置]\r\n", encoding="utf-8")
        self._orig = _patch_settings(ini_path)
        self.sched, self.cfg = self._make_scheduler("Config_Test.json", "持久")

    def tearDown(self):
        _restore_settings(self._orig)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _make_scheduler(self, file_name, config_type):
        cfg_path = Path(self.tmp) / file_name
        cfg_path.write_text(self._cfg_json(config_type), encoding="utf-8")
        from backend.core.config_model import Config
        from backend.services.scheduler_service import SchedulerService
        cfg = Config(parent_logger=logging.getLogger("verify"),
                     config_path=cfg_path)
        sched = SchedulerService(config=cfg)
        sched.running = True
        sched.run_once = False
        # 通知为外部副作用（Windows Toast）：测试中屏蔽，避免弹窗与不必要的进程
        sched._notify_user = lambda title, message: None
        for name, activated in (("消耗体力", False), ("一乐外卖", True),
                                ("叛忍来袭", False)):
            sched.task_queue.enqueue(self._FakeTask(name, activated))
        return sched, cfg

    @staticmethod
    def _cfg_json(config_type):
        def task(activated):
            return {"是否启用": activated, "下次执行时间": 0, "是否临时": False,
                    "基础优先级": 0, "连点优先级": 0, "类型": 0,
                    "执行参数": {}, "执行进度": {}}
        return json.dumps({
            "配置文件版本": "V3",
            "用户名": "verify_user",
            "配置类型": config_type,
            "任务": {"一乐外卖": task(True), "消耗体力": task(False),
                     "叛忍来袭": task(False)},
        }, ensure_ascii=False)

    def _enabled(self, task_name, cfg=None):
        return (cfg or self.cfg).get_task_base_config(task_name, "是否启用")

    def _task(self, task_name):
        return self.sched.task_queue.get_task(task_name)

    def _finish(self, task):
        task.current_status = 0
        self.sched._execute_done_callback(task)

    def test_disabled_task_restored_after_completion(self):
        self.sched.execute_task_now("消耗体力", enable_if_needed=True)
        self.assertTrue(self._enabled("消耗体力"))
        self.assertIn("消耗体力", self.sched._temp_activated_tasks)
        task = self._task("消耗体力")
        self._finish(task)
        self.assertFalse(self._enabled("消耗体力"), "结束后应恢复为未激活")
        self.assertFalse(task.force_execute_now)
        self.assertNotIn("消耗体力", self.sched._temp_activated_tasks,
                         "恢复后应清除登记")

    def test_enabled_task_not_affected(self):
        self.sched.execute_task_now("一乐外卖", enable_if_needed=True)
        self.assertNotIn("一乐外卖", self.sched._temp_activated_tasks,
                         "原本已启用的任务不应登记")
        self._finish(self._task("一乐外卖"))
        self.assertTrue(self._enabled("一乐外卖"))

    def test_manual_enable_clears_registration(self):
        self.sched.execute_task_now("消耗体力", enable_if_needed=True)
        self.sched.toggle_task_activation("消耗体力", True)
        self.assertNotIn("消耗体力", self.sched._temp_activated_tasks)
        self._finish(self._task("消耗体力"))
        self.assertTrue(self._enabled("消耗体力"),
                        "用户手动启用后不应被恢复为未激活")

    def test_normal_completion_writes_nothing(self):
        self._finish(self._task("叛忍来袭"))
        self.assertFalse(self._enabled("叛忍来袭"),
                         "未登记的任务正常结束不应改动启用状态")

    def test_temp_preset_mode_skips_write(self):
        sched, cfg = self._make_scheduler("Config_Temp.json", "临时")
        sched.execute_task_now("消耗体力", enable_if_needed=True)
        self.assertTrue(self._enabled("消耗体力", cfg))
        task = sched.task_queue.get_task("消耗体力")
        task.current_status = 0
        sched._execute_done_callback(task)
        self.assertTrue(self._enabled("消耗体力", cfg),
                        "临时预设模式不应写回启用状态（避免污染预设文件）")
        self.assertNotIn("消耗体力", sched._temp_activated_tasks)

    def test_scheduled_activation_registers_and_restores(self):
        self.sched.scan = unittest.mock.Mock()
        future = datetime.now(_TZ) + timedelta(hours=1)
        self.sched._on_task_activate_request("叛忍来袭",
                                             next_execute_time=future)
        self.assertIn("叛忍来袭", self.sched._temp_activated_tasks)
        self.assertTrue(self._enabled("叛忍来袭"))
        self._finish(self._task("叛忍来袭"))
        self.assertFalse(self._enabled("叛忍来袭"),
                         "指定时间激活的任务结束后同样要恢复原状态")

    def test_stop_clears_registration(self):
        self.sched.execute_task_now("消耗体力", enable_if_needed=True)
        self.sched.stop()
        self.assertEqual(self.sched._temp_activated_tasks, {})

    def test_stop_restores_temp_activation(self):
        """停机时必须把「临时启用」恢复原值：否则原本未勾选的任务被永久写为启用"""
        self.sched.execute_task_now("消耗体力", enable_if_needed=True)
        self.assertTrue(self._enabled("消耗体力"), "临时启用应已写入配置")
        self.sched.stop()
        self.assertFalse(self._enabled("消耗体力"),
                         "停机后应恢复为未激活（旧实现只清登记、不写回 → 永久启用）")

    def test_stop_in_temp_preset_mode_skips_write(self):
        """临时预设模式停机同样不写回（避免污染预设文件）"""
        sched, cfg = self._make_scheduler("Config_Temp2.json", "临时")
        sched.execute_task_now("消耗体力", enable_if_needed=True)
        sched.stop()
        self.assertTrue(self._enabled("消耗体力", cfg),
                        "临时预设模式停机不应写回启用状态")
        self.assertEqual(sched._temp_activated_tasks, {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
