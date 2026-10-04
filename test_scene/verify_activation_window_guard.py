# -*- coding: utf-8 -*-
"""验证「跨任务立即激活前的窗口守卫」（2026-09-13）。

背景：【要塞争夺战/天地战场】执行结束（含超窗口 / 超最长时长被强制结束）后会自动
激活【叛忍来袭】，而"立即执行/被激活"按设计会跳过窗口校验
（`BaseTask._should_skip_window_check`）。若这两个任务自己就拖到了叛忍窗口
（周三 21:00~22:00 / 周六 20:00~21:00）之后，叛忍来袭会被临时启用并带着执行意图空转
——游戏里已无叛忍入口，任务会一直重试到最长执行时长（45 分钟），期间调度器无法执行
其它任务（用户感知为"卡死"）。

修复：
- `BaseTask.probe_execute_window(now)`：窗口基准取 **now**（不是陈旧的 last_run_time），
  返回 ``(是否可执行, 状态)``；
- `SchedulerService._skip_expired_activation(task, now)`：当前不在窗口内 → 不启用、
  不登记立即执行，只记一条 WARNING 交由任务自身排期处理。

覆盖（全部离线，不依赖设备/模拟器）：
1. 叛忍来袭：周三 21:30 窗口内 / 22:30 已过期 / 20:00 未开始；
2. 叛忍来袭：周六 20:30（要塞路径）窗口内 / 21:30 已过期
   —— 下周三兜底窗口永远在未来，因此不能用"所有窗口终点都早于 now"判断；
3. 判定基准是 now：last_run_time 停在上周也不能改变本周结论；
4. 不受影响：消耗体力（Daily 整日窗口）任意时刻可执行；AnyTime 任务"不限时间"；
5. 调度器守卫：不可执行 → 不调用 execute_task_now、不写启用、记 WARNING；
   可执行 → 原行为（execute_task_now(enable_if_needed=True) + 继续扫描）；
6. 兼容：任务对象无 probe_execute_window（旧 stub）/ 探测抛异常 → 按原行为激活并留痕；
7. 真实整合：PanRenLaiXi + 天地战场"21:N 后执行叛忍"参数在周三 21:30 / 22:30 的结论。
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

from backend.core.legacy.Task.BaseTask import BaseTask  # noqa: E402
from backend.core.legacy.Task.PanRenLaiXi import PanRenLaiXi  # noqa: E402
from backend.core.legacy.Task.XiaoHaoTiLi import XiaoHaoTiLi  # noqa: E402
from backend.core.legacy.Task.schedule import AnyTime  # noqa: E402
from backend.services.scheduler_service import (  # noqa: E402
    SOURCE_ACTIVATION,
    SOURCE_MANUAL,
)

_TZ = ZoneInfo("Asia/Shanghai")
# 2026-09-07 是周一（基准日），周三 = 09-09，周六 = 09-12
_MONDAY = datetime(2026, 9, 7, 0, 0, tzinfo=_TZ)

WED, THU, SAT = 2, 3, 5


def _day(offset_days: int, hour: int = 0, minute: int = 0) -> datetime:
    """基准周一 + 偏移天数 + 时刻（2026-09-07 为周一）"""
    return _MONDAY + timedelta(days=offset_days, hours=hour, minutes=minute)


class _FakeConfig:
    """排期只读"叛忍联动参数"：让 天地战场/要塞争夺战 返回同一组值即可。"""

    def __init__(self, has_panren: bool = True, panren_minute: int = 30):
        self.has_panren = has_panren
        self.panren_minute = panren_minute

    def get_task_exe_param(self, task_name, param_name, default=None):
        if param_name == "执行结束后是否有叛忍":
            return self.has_panren
        if param_name == "本任务执行多少分钟后执行叛忍":
            return self.panren_minute
        return default

    def get_config(self, key, default=None):
        return default


class _AnyTimeTask(BaseTask):
    """不限时间任务（窗口无边界）"""
    schedule = AnyTime()


def _bare_task(cls, config=None, last_run_time=None):
    """构造"只跑排期逻辑"的任务对象（不执行 __init__，避免设备/配置等重依赖）。"""
    task = object.__new__(cls)
    task.tz_info = _TZ
    task.config = config or _FakeConfig()
    task.last_run_time = last_run_time or _day(0, 12, 0)
    task.__dict__["_bound_schedule"] = type(task).schedule.bind(
        task._build_schedule_context())
    return task


class ProbeExecuteWindowTest(unittest.TestCase):
    """`BaseTask.probe_execute_window` 的窗口判定（不涉及调度器）"""

    def setUp(self):
        self.assertEqual(_day(0).weekday(), 0, "基准日 2026-09-07 应为周一")

    def _panren(self, last_run_time=None, has_panren=True, minute=30):
        return _bare_task(
            PanRenLaiXi,
            config=_FakeConfig(has_panren=has_panren, panren_minute=minute),
            last_run_time=last_run_time)

    # ---- 1. 周三（天地战场路径：21:00 ~ 21:N + 30min） ----

    def test_wednesday_inside_window(self):
        runnable, state = self._panren().probe_execute_window(_day(WED, 21, 30))
        self.assertTrue(runnable, f"周三 21:30 应可执行（实际 {state}）")
        self.assertEqual(state, "窗口内")

    def test_wednesday_expired(self):
        runnable, state = self._panren().probe_execute_window(_day(WED, 22, 30))
        self.assertFalse(runnable, "周三 22:30 叛忍窗口（~22:00）已过期，不应激活")
        self.assertEqual(state, "窗口已过期")

    def test_wednesday_not_started(self):
        runnable, state = self._panren().probe_execute_window(_day(WED, 20, 0))
        self.assertFalse(runnable, "周三 20:00 尚未到叛忍窗口，不应激活")
        self.assertEqual(state, "窗口未开始")

    # ---- 2. 周六（要塞争夺战路径：20:00 ~ 21:00） ----

    def test_saturday_inside_window(self):
        runnable, state = self._panren().probe_execute_window(_day(SAT, 20, 30))
        self.assertTrue(runnable, f"周六 20:30 应可执行（实际 {state}）")
        self.assertEqual(state, "窗口内")

    def test_saturday_expired_despite_next_week_window(self):
        """下周三兜底窗口在未来，但本次（周六）机会已过期 → 仍应判为不可执行"""
        runnable, state = self._panren().probe_execute_window(_day(SAT, 21, 30))
        self.assertFalse(runnable, "周六 21:30 本次叛忍已结束，不应激活")
        self.assertEqual(state, "窗口已过期")

    def test_thursday_before_saturday_window(self):
        runnable, state = self._panren().probe_execute_window(_day(THU, 12, 0))
        self.assertFalse(runnable, "周四离周六/下周三窗口都还早，不应激活")
        self.assertEqual(state, "窗口未开始")

    # ---- 3. 判定基准是 now（陈旧 last_run_time 不参与） ----

    def test_baseline_is_now_not_last_run_time(self):
        stale = _day(WED - 7, 21, 0)      # 上周三执行过
        runnable, _state = self._panren(
            last_run_time=stale).probe_execute_window(_day(WED, 21, 30))
        self.assertTrue(runnable, "上周执行过不影响本周三窗口内的判定")
        runnable, state = self._panren(
            last_run_time=stale).probe_execute_window(_day(WED, 22, 30))
        self.assertFalse(runnable)
        self.assertEqual(state, "窗口已过期")

    def test_panren_disabled_falls_back_to_next_wednesday(self):
        """天地/要塞都未开"执行结束后有叛忍" → 只剩兜底窗口（下周三），周六任意时刻都不可激活"""
        runnable, state = self._panren(has_panren=False).probe_execute_window(
            _day(SAT, 20, 30))
        self.assertFalse(runnable)
        self.assertEqual(state, "窗口未开始")

    # ---- 4. 不受影响的任务 ----

    def test_consume_stamina_daily_window_always_runnable(self):
        """消耗体力（Daily 整日窗口）跨日界都应在窗口内 → 原激活行为不变"""
        for hour in (0, 3, 12, 23):
            runnable, state = _bare_task(XiaoHaoTiLi).probe_execute_window(
                _day(1, hour, 0))
            self.assertTrue(runnable, f"{hour} 点消耗体力应可执行（{state}）")
            self.assertEqual(state, "窗口内")

    def test_anytime_task_unlimited(self):
        runnable, state = _bare_task(_AnyTimeTask).probe_execute_window(
            _day(0, 3, 0))
        self.assertTrue(runnable)
        self.assertEqual(state, "不限时间")


class _GuardedTask:
    """最小任务替身：probe_execute_window 返回预设结论（模拟真实任务的排期）。"""

    def __init__(self, name, runnable=True, state="窗口已过期", raises=False):
        self.task_name = name
        self.current_status = 2
        self.is_activated = runnable
        self.is_temp = False
        self.probe_calls = []
        self._runnable = runnable
        self._state = state
        self._raises = raises

    def probe_execute_window(self, now=None):
        self.probe_calls.append(now)
        if self._raises:
            raise ValueError("模拟排期计算异常")
        return self._runnable, self._state

    def __lt__(self, other):
        return self.task_name < other.task_name


class _LegacyTask:
    """旧任务对象：没有 probe_execute_window（兼容性）"""

    def __init__(self, name):
        self.task_name = name
        self.current_status = 2
        self.is_activated = False
        self.is_temp = False

    def __lt__(self, other):
        return self.task_name < other.task_name


def _patch_settings(ini_path):
    import backend.services.settings_service as ss_mod
    from backend.core.setting_model import Setting

    setting = Setting(parent_logger=logging.getLogger("verify"),
                      setting_path=ini_path)
    orig = ss_mod.SettingsService._get_setting
    ss_mod.SettingsService._get_setting = lambda self: setting
    return orig


class _CaptureHandler(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


class ActivationGuardTest(unittest.TestCase):
    """`SchedulerService._process_pending_activations` 的窗口守卫"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="xuan_verify_guard_")
        ini_path = Path(self.tmp) / "setting.ini"
        ini_path.write_text("[助手设置]\r\n", encoding="utf-8")
        self._orig = _patch_settings(ini_path)
        cfg_path = Path(self.tmp) / "Config_Test.json"
        cfg_path.write_text(json.dumps({
            "配置文件版本": "V3",
            "用户名": "verify_user",
            "配置类型": "持久",
            "任务": {
                "叛忍来袭": {"是否启用": False, "下次执行时间": 0, "是否临时": False,
                             "基础优先级": 0, "连点优先级": 0, "类型": 0,
                             "执行参数": {}, "执行进度": {}},
                "天地战场": {"是否启用": True, "下次执行时间": 0, "是否临时": False,
                             "基础优先级": 0, "连点优先级": 0, "类型": 0,
                             "执行参数": {}, "执行进度": {}},
            },
        }, ensure_ascii=False), encoding="utf-8")
        from backend.core.config_model import Config
        from backend.services.scheduler_service import SchedulerService
        self.cfg = Config(parent_logger=logging.getLogger("verify"),
                          config_path=cfg_path)
        self.sched = SchedulerService(config=self.cfg)
        self.sched.running = True
        self.sched.run_once = False
        self.sched.execute_task_now = unittest.mock.Mock()
        self.sched.scan = unittest.mock.Mock()
        # basicConfig(CRITICAL) 会把根 logger 级别压到 CRITICAL，从而在 emit 之前
        # 就过滤掉 WARNING → 测试内显式把调度器 logger 打开
        self.sched.logger.setLevel(logging.DEBUG)
        self.captured = _CaptureHandler()
        self.sched.logger.addHandler(self.captured)

    def tearDown(self):
        self.sched.logger.removeHandler(self.captured)
        import backend.services.settings_service as ss_mod
        ss_mod.SettingsService._get_setting = self._orig
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _enqueue(self, task):
        self.sched.task_queue.enqueue(task)
        self.sched._pending_activate_tasks.append(task.task_name)
        return task

    def test_expired_window_skips_activation(self):
        """叛忍来袭窗口已过期 → 不激活、不启用，只记 WARNING"""
        task = self._enqueue(_GuardedTask("叛忍来袭", runnable=False,
                                          state="窗口已过期"))
        self.sched._process_pending_activations()
        self.sched.execute_task_now.assert_not_called()
        self.assertFalse(self.cfg.get_task_base_config("叛忍来袭", "是否启用"),
                         "跳过激活时不应临时启用任务")
        self.assertFalse(task.is_activated)
        self.assertTrue(task.probe_calls, "应探测目标任务的可执行窗口")
        self.assertEqual(self.sched._pending_activate_tasks, [])
        self.assertTrue(any("窗口已过期" in m and "跳过本次激活" in m
                            for m in self.captured.messages),
                        f"缺少跳过提示: {self.captured.messages}")

    def test_not_started_window_also_skips(self):
        self._enqueue(_GuardedTask("叛忍来袭", runnable=False, state="窗口未开始"))
        self.sched._process_pending_activations()
        self.sched.execute_task_now.assert_not_called()
        self.assertTrue(any("窗口未开始" in m for m in self.captured.messages))

    def test_runnable_window_keeps_original_behavior(self):
        self._enqueue(_GuardedTask("叛忍来袭", runnable=True, state="窗口内"))
        self.sched._process_pending_activations()
        self.sched.execute_task_now.assert_called_once_with(
            "叛忍来袭", enable_if_needed=True, source=SOURCE_ACTIVATION)
        self.sched.scan.assert_called_once()

    def test_legacy_task_without_probe_keeps_original_behavior(self):
        """旧任务对象（无 probe_execute_window）→ 按原行为激活"""
        self._enqueue(_LegacyTask("叛忍来袭"))
        self.sched._process_pending_activations()
        self.sched.execute_task_now.assert_called_once_with(
            "叛忍来袭", enable_if_needed=True, source=SOURCE_ACTIVATION)

    def test_probe_error_keeps_original_behavior(self):
        """探测抛异常（排期计算异常）→ 不阻断激活，留痕后按原行为继续"""
        self._enqueue(_GuardedTask("叛忍来袭", raises=True))
        self.sched._process_pending_activations()
        self.sched.execute_task_now.assert_called_once_with(
            "叛忍来袭", enable_if_needed=True, source=SOURCE_ACTIVATION)
        self.assertTrue(any("探测" in m and "失败" in m
                            for m in self.captured.messages))


if __name__ == "__main__":
    unittest.main(verbosity=2)
