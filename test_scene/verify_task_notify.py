# -*- coding: utf-8 -*-
"""验证通知功能（仅 Windows）与调度器的两处通知时机。

1. **通知服务** `backend/services/notify_service.py`：Toast XML 生成（转义/截断）、
   PowerShell `-EncodedCommand`（UTF-16LE + Base64）传参、失败与不支持的平台降级；
2. **调度器** `backend/services/scheduler_service.py`：
   - 临时预设模式：待执行任务跑完 → 通知「预设执行完毕」；
   - 账号配置模式：执行/就绪队列均为空且最早的启用任务排期在 1 小时之后
     → 通知「任务告一段落」（同一段空闲只通知一次，有任务就绪即重新武装）。
"""
import base64
import json
import logging
import os
import shutil
import sys
import tempfile
import time
import unittest
import unittest.mock
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.services import notify_service

TZ = ZoneInfo("Asia/Shanghai")


class _FakeProc:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _decode_command(cmd):
    """取出 -EncodedCommand 的脚本明文。"""
    encoded = cmd[cmd.index("-EncodedCommand") + 1]
    return base64.b64decode(encoded).decode("utf-16-le")


class NotifyServiceTest(unittest.TestCase):
    """通知服务：Toast XML 生成 + PowerShell 调用与失败降级"""

    def test_toast_xml_escapes_and_truncates(self):
        xml = notify_service.build_toast_xml("A&B<C>", "引号'与\"引号")
        self.assertIn("A&amp;B&lt;C&gt;", xml)
        self.assertIn("&apos;", xml)
        self.assertIn("&quot;", xml)
        self.assertIn("ToastGeneric", xml)
        long_xml = notify_service.build_toast_xml(
            "T", "正" * (notify_service.MAX_BODY_LENGTH + 50))
        self.assertIn("…", long_xml)

    def test_script_is_encoded_as_utf16le_base64(self):
        script = notify_service._build_script("标题", "正文")
        self.assertIn("CreateToastNotifier", script)
        self.assertIn(notify_service.TOAST_AUMID, script)
        self.assertEqual(
            _decode_command(["-EncodedCommand",
                             notify_service._encode_script("测试")]), "测试")

    @unittest.skipUnless(sys.platform == "win32", "仅 Windows 有 PowerShell")
    def test_supported_on_windows(self):
        self.assertTrue(notify_service.is_supported())
        self.assertTrue(notify_service._powershell_path())

    def test_notify_sends_expected_command(self):
        calls = []

        def fake_runner(cmd, **kwargs):
            calls.append((cmd, kwargs))
            return _FakeProc(returncode=0, stdout="TOAST_OK")

        with unittest.mock.patch.object(notify_service, "_runner", fake_runner):
            ok = notify_service.notify("玄的日常助手", "任务告一段落")
        self.assertTrue(ok)
        self.assertEqual(len(calls), 1)
        cmd, kwargs = calls[0]
        self.assertIn("-NoProfile", cmd)
        self.assertIn("-NonInteractive", cmd)
        script = _decode_command(cmd)
        self.assertIn("玄的日常助手", script)
        self.assertIn("任务告一段落", script)
        self.assertEqual(kwargs.get("timeout"), notify_service.DEFAULT_TIMEOUT)

    def test_notify_returns_false_on_failure_and_exception(self):
        with unittest.mock.patch.object(
                notify_service, "_runner",
                lambda *a, **k: _FakeProc(returncode=1, stderr="boom")):
            self.assertFalse(notify_service.notify("T", "M"))

        def boom(*a, **k):
            raise OSError("powershell missing")

        with unittest.mock.patch.object(notify_service, "_runner", boom):
            self.assertFalse(notify_service.notify("T", "M"))

    def test_notify_skips_when_unsupported(self):
        calls = []
        with unittest.mock.patch.object(notify_service, "_powershell_path",
                                        lambda: None), \
                unittest.mock.patch.object(notify_service, "_runner",
                                           lambda *a, **k: calls.append(a)):
            self.assertFalse(notify_service.notify("T", "M"))
        self.assertEqual(calls, [], "不支持的平台不应调用 PowerShell")

    def test_notify_async_runs_notify(self):
        called = []
        with unittest.mock.patch.object(
                notify_service, "notify",
                lambda title, message, **kw:
                    called.append((title, message)) or True):
            thread = notify_service.notify_async("T", "M")
            thread.join(timeout=3)
        self.assertEqual(called, [("T", "M")])



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


class SchedulerNotifyTest(unittest.TestCase):
    """调度器通知时机：预设跑完 / 账号配置模式告一段落"""

    class _FakeTask:
        def __init__(self, name, activated=True, next_execute_time=None,
                     status=2):
            self.task_name = name
            self.current_status = status
            self.is_activated = activated
            self.is_temp = False
            self.current_priority = 0
            self.base_priority = 0
            self.next_execute_time = next_execute_time
            self.force_execute_now = False
            self.last_run_time = None
            self.last_execute_error = None
            self.run_called = False

        def __lt__(self, other):
            return self.task_name < other.task_name

        def schedule_execute_now(self):
            return True, None

        def run(self):
            """被调度器选中后启动（扫描会调用），仅记录一次"""
            self.run_called = True

    @staticmethod
    def _task_cfg():
        return {"是否启用": True, "下次执行时间": 0, "是否临时": False,
                "基础优先级": 0, "连点优先级": 0, "类型": 0,
                "执行参数": {}, "执行进度": {}}

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="xuan_verify_notify_")
        self.ini_path = Path(self.tmp) / "setting.ini"
        self.ini_path.write_text("[助手设置]\r\n任务通知 = True\r\n",
                                 encoding="utf-8")
        self._orig = _patch_settings(self.ini_path)
        cfg_path = Path(self.tmp) / "Config_Test.json"
        cfg_path.write_text(json.dumps({
            "配置文件版本": "V3",
            "用户名": "verify_user",
            "配置类型": "持久",
            "任务": {"一乐外卖": self._task_cfg()},
        }, ensure_ascii=False), encoding="utf-8")
        from backend.core.config_model import Config
        from backend.services.scheduler_service import SchedulerService
        self.cfg = Config(parent_logger=logging.getLogger("verify"),
                          config_path=cfg_path)
        self.sched = SchedulerService(config=self.cfg)
        self.sched.running = True
        self.notifications = []
        self.sched._notify_user = (
            lambda title, message: self.notifications.append((title, message)))

    def tearDown(self):
        _restore_settings(self._orig)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _wait_notifications(self, count=1, timeout=3.0):
        deadline = time.time() + timeout
        while time.time() < deadline and len(self.notifications) < count:
            time.sleep(0.02)


    # ---- 预设模式 ----
    def test_preset_finished_notifies_once(self):
        self.sched.run_once = True
        self.sched._preset_total = 3
        self.sched._scan_once()
        self._wait_notifications()
        self.assertEqual(len(self.notifications), 1)
        title, message = self.notifications[0]
        self.assertIn("预设执行完毕", title)
        self.assertIn("3 个任务", message)
        self.assertIn("verify_user", message)

    def test_preset_finish_stops_scheduler(self):
        self.sched.run_once = True
        self.sched.pending_once_tasks = []
        self.sched.stop = unittest.mock.Mock()
        self.sched._scan_once()
        self._wait_notifications()
        deadline = time.time() + 3
        while time.time() < deadline and not self.sched.stop.called:
            time.sleep(0.02)
        self.sched.stop.assert_called_once()
        self.assertEqual(self.sched.stop.call_args.kwargs.get("reason"),
                         "预设任务全部执行完毕")

    # ---- 账号配置模式：告一段落 ----
    def test_idle_skipped_before_any_task_completed(self):
        self.sched.task_queue.enqueue(self._FakeTask(
            "一乐外卖", next_execute_time=datetime.now(TZ) + timedelta(hours=5)))
        self.sched.scan()
        self.assertEqual(self.notifications, [],
                         "本次启动尚未执行过任务时不应通知")

    def test_idle_notifies_when_next_task_beyond_one_hour(self):
        self.sched._completed_count = 1
        self.sched.task_queue.enqueue(self._FakeTask(
            "一乐外卖", next_execute_time=datetime.now(TZ) + timedelta(hours=5)))
        self.sched.scan()
        self.assertEqual(len(self.notifications), 1)
        title, message = self.notifications[0]
        self.assertIn("告一段落", title)
        self.assertIn("一乐外卖", message)
        self.assertIn("小时", message)
        # 去抖：同一段空闲只通知一次
        self.sched.scan()
        self.assertEqual(len(self.notifications), 1, "同一段空闲不应重复通知")

    def test_idle_notifies_when_no_upcoming_task(self):
        self.sched._completed_count = 2
        self.sched.task_queue.enqueue(self._FakeTask(
            "一乐外卖", activated=False, next_execute_time=None))
        self.sched.scan()
        self.assertEqual(len(self.notifications), 1)
        self.assertIn("没有待执行的任务", self.notifications[0][1])

    def test_idle_skipped_when_task_within_one_hour(self):
        self.sched._completed_count = 1
        self.sched.task_queue.enqueue(self._FakeTask(
            "一乐外卖",
            next_execute_time=datetime.now(TZ) + timedelta(minutes=30)))
        self.sched.scan()
        self.assertEqual(self.notifications, [], "1 小时内有任务时不算告一段落")
        self.assertFalse(self.sched._idle_notified)

    def test_idle_flag_rearmed_when_task_ready(self):
        sched = self.sched
        sched._completed_count = 1
        sched.task_queue.enqueue(self._FakeTask(
            "一乐外卖", next_execute_time=datetime.now(TZ) + timedelta(hours=5)))
        sched.scan()
        self.assertTrue(sched._idle_notified)
        # 任务进入就绪队列 → 重新武装通知标记
        sched._update_task_status("一乐外卖", 1)
        sched._notify_account_idle(datetime.now(TZ))
        self.assertFalse(sched._idle_notified, "有就绪任务时应重新武装通知")

    # ---- 通知时机：必须在完成回调激活其他任务之后判定 ----
    def test_idle_not_notified_while_activation_pending(self):
        """回调还有待激活任务未落地时，队列为空也不得判定"告一段落"。

        原问题：任务结束回到等待队列后、被登记激活的任务尚未在回调中激活执行，
        扫描看到执行/就绪队列为空便立刻发通知，下一刻任务又替补进队列。
        """
        sched = self.sched
        sched._completed_count = 1
        sched.task_queue.enqueue(self._FakeTask(
            "叛忍来袭", next_execute_time=datetime.now(TZ) + timedelta(hours=5)))
        sched._on_task_activate_request("叛忍来袭")
        sched.scan()
        self.assertEqual(self.notifications, [],
                         "待激活任务未落地前不得发告一段落通知")
        self.assertFalse(sched._idle_notified)
        # 登记处理完毕（此处无替补任务）→ 下一次扫描才允许通知
        sched._pending_activate_tasks.clear()
        sched.scan()
        self.assertEqual(len(self.notifications), 1)
        self.assertIn("告一段落", self.notifications[0][0])

    def test_idle_notify_runs_after_pending_activation(self):
        """完成回调：先激活替补任务（进入执行队列）再判空闲 → 不发"告一段落"。"""
        sched = self.sched
        sched._completed_count = 1
        current = self._FakeTask(
            "一乐外卖", next_execute_time=datetime.now(TZ) + timedelta(hours=5))
        activated = self._FakeTask(
            "叛忍来袭", next_execute_time=datetime.now(TZ))
        sched.task_queue.enqueue(current)
        sched.task_queue.enqueue(activated)
        sched._on_task_activate_request("叛忍来袭")
        current.current_status = 0
        sched._execute_done_callback(current)
        self.assertTrue(activated.force_execute_now, "被激活任务应带立即执行标记")
        self.assertTrue(activated.run_called, "被激活任务应已替补进执行队列")
        self.assertEqual(activated.current_status, 0)
        self.assertEqual(self.notifications, [],
                         "回调替补上任务后不得发出告一段落通知")


    def test_preset_mode_does_not_use_idle_notify(self):
        self.sched.run_once = True
        self.sched._completed_count = 1
        self.sched.task_queue.enqueue(self._FakeTask(
            "一乐外卖", next_execute_time=datetime.now(TZ) + timedelta(hours=5)))
        self.sched._notify_account_idle(datetime.now(TZ))
        self.assertEqual(self.notifications, [], "预设模式不走告一段落通知")

    def test_completed_count_increases_on_task_finish(self):
        task = self._FakeTask("一乐外卖")
        self.sched.task_queue.enqueue(task)
        self.assertEqual(self.sched._completed_count, 0)
        task.current_status = 0
        self.sched._execute_done_callback(task)
        self.assertEqual(self.sched._completed_count, 1)

    # ---- 通知开关 ----
    def test_notification_switch_off(self):
        ini_off = Path(self.tmp) / "setting_off.ini"
        ini_off.write_text("[助手设置]\r\n任务通知 = False\r\n", encoding="utf-8")
        _restore_settings(self._orig)
        orig2 = _patch_settings(ini_off)
        try:
            self.assertFalse(self.sched._notifications_enabled())
        finally:
            _restore_settings(orig2)
            self._orig = _patch_settings(self.ini_path)
        self.assertTrue(self.sched._notifications_enabled())

    def test_notification_switch_read_failure_defaults_on(self):
        with unittest.mock.patch(
                "backend.services.settings_service.SettingsService._get_setting",
                side_effect=RuntimeError("ini broken")):
            self.assertTrue(self.sched._notifications_enabled(),
                            "setting.ini 读取失败应按开启处理")

    def test_notify_user_sends_via_notify_service(self):
        received = []
        # setUp 中用实例属性替换了 _notify_user（用于捕获通知），此处直接调用类方法
        with unittest.mock.patch(
                "backend.services.notify_service.is_supported", lambda: True), \
                unittest.mock.patch(
                    "backend.services.notify_service.notify_async",
                    lambda t, m, **kw: received.append((t, m))):
            type(self.sched)._notify_user(self.sched, "标题", "正文")
        self.assertEqual(received, [("标题", "正文")])

    def test_notify_user_skips_when_platform_unsupported(self):
        received = []
        with unittest.mock.patch(
                "backend.services.notify_service.is_supported", lambda: False), \
                unittest.mock.patch(
                    "backend.services.notify_service.notify_async",
                    lambda t, m, **kw: received.append((t, m))):
            type(self.sched)._notify_user(self.sched, "标题", "正文")
        self.assertEqual(received, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
