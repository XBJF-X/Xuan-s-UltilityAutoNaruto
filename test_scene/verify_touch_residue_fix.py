# -*- coding: utf-8 -*-
"""验证「连点中途被杀 → 设备端残留触点」修复（P0 清理能力 + P1 释放顺序 + P2 自检自愈）。

覆盖：
1. `touch_residue`：getevent 解析 / dumpsys input 解析 / 清理命令生成 /
   清理入口 / 自检入口（仅在存在未结束手势时才清理）/ **挂起清理**
   （`mark_pending_cleanup` / `has_pending_cleanup` / `flush_pending_cleanup`：
   热路径只挂标记、任务边界才执行、同串口最小间隔节流、无挂起零开销）；
2. `MiniTouch`：release 与 up_all_contacts 在锁内「先抬起 → 再关 socket/杀进程」、
   抬起失败走裸 evdev 兜底、`_reconnect` 顺序 = 「先抬旧连接 → 停旧核心 →
   再建新核心」（v0.17.49：设备端只有一个 minitouch 进程，先建后停会把新进程
   一起杀掉 → 每次点击 10053 → 每点一次重连一次），且重连热路径不再跑秒级
   evdev 清理，只挂起标记；
3. `Clicker`：刷新顺序「先抬起并释放旧实例 → 再新建实例」、抬起失败依赖
   `up_all_contacts` 内部兜底（不重复清理）、连点启动前补清理挂起残留、
   连点线程收尾无条件抬起、`wait_stopped`；
4. `ControlManager.switch_control_mode` 切换前先抬并释放旧实例、创建失败回滚并尝试恢复；
5. `SchedulerService`：启动前自检（含补清理挂起残留）、停止时「先停任务 →
   等连点线程退出 → 释放控制实例 → 再自检」。

全部使用假 adb / 假 minitouch 核心，不连接真实设备。
"""
import logging
import os
import sys
import threading
import time
import types
import unittest

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.core.legacy.Control import ControlMode, touch_residue
from backend.core.legacy.Control import MiniTouch as mt_module
from backend.core.legacy.Clicker import Clicker
from backend.core.legacy.Control.ControlManager import ControlManager
from backend.services.scheduler_service import PriorityQueue, SchedulerService

LOG = logging.getLogger("verify.touch_residue")

GETEVENT_SAMPLE = """add device 1: /dev/input/event4
  name:     "mouse"
add device 2: /dev/input/event3
  name:     "gpio"
add device 3: /dev/input/event2
  name:     "input"
    Events:
      ABS (0003): ABS_MT_SLOT           : value 0, min 0, max 15, fuzz 0, flat 0, resolution 0
                  ABS_MT_POSITION_X     : value 0, min 0, max 1599, fuzz 0, flat 0, resolution 0
                  ABS_MT_TRACKING_ID    : value 0, min 0, max 65535, fuzz 0, flat 0, resolution 0
add device 4: /dev/input/event0
  name:     "Power Button"
"""

GETEVENT_SAMPLE_NO_SLOT = """add device 1: /dev/input/event2
  name:     "input"
    Events:
      ABS (0003): ABS_MT_POSITION_X     : value 0, min 0, max 1599, fuzz 0, flat 0, resolution 0
                  ABS_MT_TRACKING_ID    : value 0, min 0, max 65535, fuzz 0, flat 0, resolution 0
"""

DUMPSYS_RESIDUAL = """Input Reader State:
  Device 3: input
      Last Raw Touch: pointerCount=4
        [0]: id=0, x=1200, y=700, pressure=100, touchMajor=0, toolType=1, isHovering=false
        [1]: id=1, x=1300, y=750, pressure=100, touchMajor=0, toolType=1, isHovering=false
        [2]: id=2, x=1100, y=760, pressure=100, touchMajor=0, toolType=1, isHovering=false
        [3]: id=3, x=1350, y=650, pressure=100, touchMajor=0, toolType=1, isHovering=false
Input Dispatcher State:
  TouchStatesByDisplay:
    0: down=true, split=true, deviceId=3, source=0x00001002
      Windows:
        0: name='Window{abc u0 com.tencent.KiHan}', pointerIds=0xf0000000, targetFlags=0x105
"""

DUMPSYS_CLEAN = """Input Reader State:
  Device 3: input
      Last Raw Touch: pointerCount=0
Input Dispatcher State:
  TouchStates: <no displays touched>
    Windows:
"""


class TouchResidueTest(unittest.TestCase):
    """P0：裸 evdev 残留触点检测/清理模块"""

    def setUp(self):
        self.calls = []
        self._saved_shell = touch_residue._adb_shell
        self._saved_pending = (set(touch_residue._pending_serials),
                               dict(touch_residue._last_pending_clean_at))

        def fake_shell(serial, command):
            self.calls.append((serial, command))
            if command.startswith("getevent"):
                return GETEVENT_SAMPLE
            if command.startswith("dumpsys input"):
                return DUMPSYS_RESIDUAL
            return ""

        touch_residue._adb_shell = fake_shell

    def tearDown(self):
        touch_residue._adb_shell = self._saved_shell
        touch_residue._pending_serials, touch_residue._last_pending_clean_at = (
            self._saved_pending[0], self._saved_pending[1])

    def test_parse_touch_devices_only_mt_device(self):
        devices = touch_residue.parse_touch_devices(GETEVENT_SAMPLE)
        self.assertEqual(devices, [("/dev/input/event2", 15)],
                         "只应认出带 ABS_MT_TRACKING_ID 的多点触摸设备")

    def test_parse_touch_devices_without_slot_max_uses_default(self):
        devices = touch_residue.parse_touch_devices(GETEVENT_SAMPLE_NO_SLOT)
        self.assertEqual(devices, [("/dev/input/event2", touch_residue.DEFAULT_MAX_SLOT)])

    def test_build_clean_commands_covers_all_slots(self):
        cmd = touch_residue.build_clean_commands("/dev/input/event2", 15)
        self.assertEqual(cmd.count("sendevent"), 16 * 3, "每个 slot 应写 SLOT/TRACKING_ID/SYN")
        self.assertIn("sendevent /dev/input/event2 3 47 0", cmd)
        self.assertIn("sendevent /dev/input/event2 3 47 15", cmd)
        self.assertIn("sendevent /dev/input/event2 3 57 -1", cmd)
        self.assertIn("sendevent /dev/input/event2 0 0 0", cmd)

    def test_parse_touch_state_residual(self):
        state = touch_residue.parse_touch_state(DUMPSYS_RESIDUAL)
        self.assertTrue(state["available"])
        self.assertTrue(state["active"], "TouchStatesByDisplay 出现 = 有未结束手势")
        self.assertEqual(state["raw_pointer_count"], 4)
        self.assertEqual(state["points"],
                         [(1200, 700), (1300, 750), (1100, 760), (1350, 650)])
        self.assertIn("f0000000", state["pointer_ids"])

    def test_parse_touch_state_clean(self):
        state = touch_residue.parse_touch_state(DUMPSYS_CLEAN)
        self.assertFalse(state["active"])
        self.assertEqual(state["raw_pointer_count"], 0)

    def test_clean_stale_contacts_writes_evdev_up(self):
        ok = touch_residue.clean_stale_contacts("emulator-5560", logger=LOG, reason="单测")
        self.assertTrue(ok)
        self.assertEqual(len(self.calls), 2, "应只有 getevent + sendevent 两条命令")
        self.assertEqual(self.calls[0][1], "getevent -pl")
        self.assertTrue(self.calls[1][1].startswith("sendevent /dev/input/event2"))

    def test_clean_stale_contacts_without_device_returns_false(self):
        touch_residue._adb_shell = lambda serial, command: 'add device 1: /dev/input/event4\n  name: "mouse"'
        self.assertFalse(touch_residue.clean_stale_contacts("emulator-5560", logger=LOG))

    def test_clean_stale_contacts_empty_serial(self):
        self.assertFalse(touch_residue.clean_stale_contacts("", logger=LOG))
        self.assertEqual(self.calls, [], "串口为空不应触碰设备")

    def test_clean_stale_contacts_adb_error_returns_false(self):
        def boom(serial, command):
            raise RuntimeError("device not found")
        touch_residue._adb_shell = boom
        self.assertFalse(touch_residue.clean_stale_contacts("emulator-5560", logger=LOG))

    def test_ensure_no_stale_contacts_cleans_when_active(self):
        cleaned = touch_residue.ensure_no_stale_contacts("emulator-5560", logger=LOG, reason="单测")
        self.assertTrue(cleaned)
        commands = [c for _, c in self.calls]
        self.assertEqual(commands[0], "dumpsys input")
        self.assertEqual(commands[1], "getevent -pl")
        self.assertTrue(commands[2].startswith("sendevent"))

    def test_ensure_no_stale_contacts_skips_clean_device(self):
        def fake_shell(serial, command):
            self.calls.append((serial, command))
            return DUMPSYS_CLEAN if command.startswith("dumpsys") else GETEVENT_SAMPLE
        touch_residue._adb_shell = fake_shell
        self.assertFalse(touch_residue.ensure_no_stale_contacts("emulator-5560", logger=LOG))
        self.assertEqual([c for _, c in self.calls], ["dumpsys input"],
                         "无未结束手势时不应写 evdev 事件")

    # ---------------- 挂起清理（v0.17.49：热路径不清理，任务边界才清理）----------------

    def test_mark_pending_cleanup_is_idempotent_and_normalizes_serial(self):
        self.assertTrue(touch_residue.mark_pending_cleanup("emulator：5560", logger=LOG))
        self.assertFalse(touch_residue.mark_pending_cleanup("emulator:5560", logger=LOG),
                         "重复挂起（含全角冒号写法）应返回 False，调用方据此只告警一次")
        self.assertEqual(self.calls, [], "挂起阶段不应触碰设备")

    def test_mark_pending_cleanup_empty_serial(self):
        self.assertFalse(touch_residue.mark_pending_cleanup("", logger=LOG))
        self.assertFalse(touch_residue.has_pending_cleanup(""))
        self.assertFalse(touch_residue.flush_pending_cleanup("", logger=LOG))

    def test_flush_pending_cleanup_without_pending_touches_nothing(self):
        self.assertFalse(touch_residue.flush_pending_cleanup("emulator-5560", logger=LOG))
        self.assertEqual(self.calls, [], "无挂起时不应访问设备（零开销）")

    def test_flush_pending_cleanup_runs_once_and_consumes_mark(self):
        touch_residue.mark_pending_cleanup("emulator-5560", logger=LOG)
        self.assertTrue(touch_residue.flush_pending_cleanup(
            "emulator-5560", logger=LOG, reason="连点启动前补清理挂起的残留触点"))
        self.assertEqual(len(self.calls), 2, "应只有 getevent + sendevent 两条命令")
        self.assertTrue(self.calls[1][1].startswith("sendevent /dev/input/event2"))
        self.assertFalse(touch_residue.has_pending_cleanup("emulator-5560"),
                         "清理成功后应消费掉挂起标记")
        self.calls.clear()
        self.assertFalse(touch_residue.flush_pending_cleanup("emulator-5560", logger=LOG))
        self.assertEqual(self.calls, [], "标记已消费，不应重复清理")

    def test_flush_pending_cleanup_is_throttled(self):
        touch_residue.mark_pending_cleanup("emulator-5560", logger=LOG)
        self.assertTrue(touch_residue.flush_pending_cleanup("emulator-5560", logger=LOG))
        touch_residue.mark_pending_cleanup("emulator-5560", logger=LOG)
        self.calls.clear()
        self.assertFalse(touch_residue.flush_pending_cleanup("emulator-5560", logger=LOG),
                         f"距上次清理不足 {touch_residue._PENDING_CLEAN_MIN_INTERVAL:.0f}s 应节流")
        self.assertEqual(self.calls, [], "节流时不应访问设备")
        self.assertTrue(touch_residue.has_pending_cleanup("emulator-5560"),
                        "节流时应保留挂起标记，等下一次任务边界再清")

    def test_flush_pending_cleanup_failure_does_not_remark(self):
        def boom(serial, command):
            raise RuntimeError("device not found")
        touch_residue._adb_shell = boom
        touch_residue.mark_pending_cleanup("emulator-5560", logger=LOG)
        self.assertFalse(touch_residue.flush_pending_cleanup("emulator-5560", logger=LOG))
        self.assertFalse(touch_residue.has_pending_cleanup("emulator-5560"),
                         "清理失败也不重挂，避免每个边界都跑几秒 adb 命令拖慢任务")

    def test_successful_clean_clears_pending_mark(self):
        touch_residue.mark_pending_cleanup("emulator-5560", logger=LOG)
        self.assertTrue(touch_residue.clean_stale_contacts("emulator-5560", logger=LOG))
        self.assertFalse(touch_residue.has_pending_cleanup("emulator-5560"),
                         "手动清理/启停自检成功后挂起标记应一并清除")


class _FakeCore:
    """假 minitouch 核心：记录 send/stop 顺序，可选让抬起命令失败。"""

    def __init__(self, name="core", fail_lift=False, log=None):
        self.name = name
        self.fail_lift = fail_lift
        self.max_contacts = 4
        self.max_pressure = 2
        self.stopped = False
        self.log = log if log is not None else []

    def send(self, content):
        text = content.strip()
        self.log.append(("send", self.name, text))
        if self.fail_lift and text.startswith("u"):
            raise ConnectionAbortedError(10053, "你的主机中的软件中止了一个已建立的连接")

    def stop(self):
        self.stopped = True
        self.log.append(("stop", self.name, ""))


def _make_minitouch(core=None, serial="emulator-5560", max_contacts=4):
    """构造不经真实设备初始化的 MiniTouch 实例"""
    mt = object.__new__(mt_module.MiniTouch)
    mt.logger = LOG
    mt.serial = serial
    mt.max_contacts = max_contacts
    mt.max_pressure = 2
    mt._released = False
    mt._mt_core = core
    mt._core_lock = threading.RLock()
    mt._shutdown_requested = threading.Event()
    return mt


class MiniTouchResidueTest(unittest.TestCase):
    """P1：MiniTouch 释放/抬起/重连顺序"""

    _clean_result = True

    def setUp(self):
        self._saved_settle = mt_module._RELEASE_LIFT_SETTLE
        mt_module._RELEASE_LIFT_SETTLE = 0.0
        self._saved_clean = touch_residue.clean_stale_contacts
        self._saved_core_cls = mt_module.MiniTouchCore
        self._saved_pending = (set(touch_residue._pending_serials),
                               dict(touch_residue._last_pending_clean_at))
        touch_residue._pending_serials.clear()
        touch_residue._last_pending_clean_at.clear()
        self.clean_calls = []
        self.log = []
        touch_residue.clean_stale_contacts = self._fake_clean

    def tearDown(self):
        mt_module._RELEASE_LIFT_SETTLE = self._saved_settle
        touch_residue.clean_stale_contacts = self._saved_clean
        mt_module.MiniTouchCore = self._saved_core_cls
        touch_residue._pending_serials, touch_residue._last_pending_clean_at = (
            self._saved_pending[0], self._saved_pending[1])

    def _fake_clean(self, serial, logger=None, reason=""):
        self.clean_calls.append((serial, reason))
        return self._clean_result

    def _install_core_factory(self):
        outer = self

        def factory(serial):
            outer.log.append(("new_core", serial, ""))
            return _FakeCore(name="new", log=outer.log)

        mt_module.MiniTouchCore = factory

    def test_release_lifts_before_stop_and_settles(self):
        core = _FakeCore(log=self.log)
        mt = _make_minitouch(core)
        mt.release()
        kinds = [e[0] for e in self.log]
        self.assertEqual(kinds[:4], ["send"] * 4, "应先逐 slot 发 u")
        self.assertEqual(self.log[4][2], "c", "抬起后应提交一次 commit")
        self.assertEqual(kinds[-1], "stop", "关 socket/杀进程必须在抬起之后")
        self.assertTrue(mt._released)
        self.assertIsNone(mt._mt_core)
        self.assertEqual(self.clean_calls, [], "抬起成功时不应触发裸 evdev 兜底")

    def test_release_fallback_cleanup_when_lift_fails(self):
        core = _FakeCore(fail_lift=True, log=self.log)
        mt = _make_minitouch(core)
        mt.release()
        self.assertTrue(core.stopped, "即使抬起失败也必须终止设备端进程")
        self.assertEqual(self.clean_calls,
                         [("emulator-5560", "释放控制实例时抬起失败")])

    def test_release_is_idempotent(self):
        core = _FakeCore(log=self.log)
        mt = _make_minitouch(core)
        mt.release()
        before = len(self.log)
        mt.release()
        self.assertEqual(len(self.log), before, "重复 release 不应再发命令")

    def test_release_without_core_skips_cleanup(self):
        mt = _make_minitouch(None)
        mt.release()
        self.assertEqual(self.log, [])
        self.assertEqual(self.clean_calls, [], "无核心时无需兜底清理")

    def test_up_all_contacts_success(self):
        core = _FakeCore(log=self.log)
        mt = _make_minitouch(core)
        self.assertTrue(mt.up_all_contacts())
        self.assertEqual(self.clean_calls, [])

    def test_up_all_contacts_fallback_on_failure(self):
        core = _FakeCore(fail_lift=True, log=self.log)
        mt = _make_minitouch(core)
        self.assertTrue(mt.up_all_contacts(), "兜底清理成功时仍应返回 True")
        self.assertEqual(self.clean_calls, [("emulator-5560", "抬起全部触点失败")])

    def test_up_all_contacts_returns_false_when_fallback_fails(self):
        core = _FakeCore(fail_lift=True, log=self.log)
        self._clean_result = False
        mt = _make_minitouch(core)
        self.assertFalse(mt.up_all_contacts())

    def test_up_all_contacts_without_core(self):
        mt = _make_minitouch(None)
        self.assertTrue(mt.up_all_contacts())
        self.assertEqual(self.clean_calls, [])

    def test_reconnect_stops_old_core_before_building_new(self):
        self._install_core_factory()
        old = _FakeCore(name="old", log=self.log)
        mt = _make_minitouch(old)
        self.assertTrue(mt._reconnect())
        kinds = [(e[0], e[1]) for e in self.log]
        first_new = kinds.index(("new_core", "emulator-5560"))
        first_stop = kinds.index(("stop", "old"))
        self.assertTrue(all(k == "send" for k, _ in kinds[:first_stop]),
                        "抬起旧连接（发 u/c）必须先于停旧核心")
        self.assertLess(first_stop, first_new,
                        "必须先停旧核心再建新核心：旧核心 stop() 会 pidof minitouch "
                        "杀掉设备端进程，若在新核心之后调用会把新进程一起杀掉 → "
                        "下一次点击 WinError 10053 → 每点一次重连一次")
        self.assertEqual(self.clean_calls, [])
        self.assertTrue(mt.ready, "重连后应可继续使用")

    def test_reconnect_defers_cleanup_when_old_lift_fails(self):
        self._install_core_factory()
        old = _FakeCore(name="old", fail_lift=True, log=self.log)
        mt = _make_minitouch(old)
        self.assertTrue(mt._reconnect())
        self.assertEqual(self.clean_calls, [],
                         "重连热路径不得跑秒级 evdev 清理（会把连点拖成点一次卡几秒）")
        self.assertTrue(touch_residue.has_pending_cleanup("emulator-5560"),
                        "抬起失败应挂起清理诉求，等任务边界执行")

    def test_repeated_reconnect_never_stops_the_new_core(self):
        """回归：连续重连（现场每 6~7 秒一轮）绝不能把新核心停掉。"""
        created = []

        def factory(serial):
            core = _FakeCore(name=f"core{len(created) + 1}", log=self.log)
            created.append(core)
            return core

        mt_module.MiniTouchCore = factory
        old = _FakeCore(name="core0", log=self.log)
        mt = _make_minitouch(old)
        for _ in range(3):
            self.assertTrue(mt._reconnect())
        self.assertFalse(mt._mt_core.stopped,
                         "重连后当前核心必须是活的（旧实现会被旧核心的 stop() 杀掉）")
        self.assertEqual([c.name for c in [old] + created if c.stopped],
                         ["core0", "core1", "core2"],
                         "只应停掉每一轮的旧核心")

    def test_release_flushes_pending_cleanup(self):
        core = _FakeCore(log=self.log)
        mt = _make_minitouch(core)
        touch_residue.mark_pending_cleanup("emulator-5560", logger=LOG)
        mt.release()
        self.assertEqual(
            self.clean_calls,
            [("emulator-5560", "释放控制实例时补清理挂起的残留触点")],
            "释放控制实例（任务结束边界）应补清理重连时挂起的残留")
        self.assertFalse(touch_residue.has_pending_cleanup("emulator-5560"))

    def test_reconnect_skipped_after_release(self):
        mt = _make_minitouch(_FakeCore(log=self.log))
        mt.release()
        self.assertFalse(mt._reconnect())


class _FakeSwitchableControl:
    """带 up_all_contacts/release 的假控制实例（供 Clicker/ControlManager 测试）"""

    def __init__(self, name, lift_result=True, log=None):
        self.name = name
        self.lift_result = lift_result
        self.up_calls = 0
        self.released = False
        self.log = log if log is not None else []

    def up_all_contacts(self):
        self.up_calls += 1
        self.log.append(("up_all", self.name))
        return self.lift_result

    def release(self):
        self.released = True
        self.log.append(("release", self.name))


class _FakeControlManagerForClicker:
    def __init__(self, current, new_control=None, log=None):
        self.current = current
        self._new = new_control
        self.log = log if log is not None else []

    def get_current_control(self):
        return self.current

    def create_control_instance(self):
        self.log.append(("create", None))
        return self._new

    def replace_current_control(self, new_control):
        self.log.append(("replace", None))
        old = self.current
        self.current = new_control
        return old


def _make_clicker():
    clicker = object.__new__(Clicker)
    clicker.logger = LOG
    clicker.device_serial = "emulator-5560"
    clicker.last_minitouch_create_time = time.perf_counter()
    clicker.running = False
    clicker._stop_event = threading.Event()
    clicker._threads = []
    clicker._threads_lock = threading.Lock()
    clicker._coordinates = []
    clicker._coord_lock = threading.Lock()
    return clicker


class ClickerResidueTest(unittest.TestCase):
    """P1：连点器刷新顺序 / 收尾抬起 / 等待线程退出"""

    def setUp(self):
        self.log = []
        self.clean_calls = []
        self._saved_clean = touch_residue.clean_stale_contacts
        self._saved_pending = (set(touch_residue._pending_serials),
                               dict(touch_residue._last_pending_clean_at))
        touch_residue._pending_serials.clear()
        touch_residue._last_pending_clean_at.clear()
        touch_residue.clean_stale_contacts = lambda serial, logger=None, reason="": (
            self.clean_calls.append((serial, reason)), True)[1]

    def tearDown(self):
        touch_residue.clean_stale_contacts = self._saved_clean
        touch_residue._pending_serials, touch_residue._last_pending_clean_at = (
            self._saved_pending[0], self._saved_pending[1])

    def test_refresh_lifts_and_releases_old_before_creating_new(self):
        old = _FakeSwitchableControl("old", log=self.log)
        new = _FakeSwitchableControl("new", log=self.log)
        cm = _FakeControlManagerForClicker(old, new, log=self.log)
        clicker = _make_clicker()
        self.assertTrue(clicker._refresh_minitouch_instance(cm))
        self.assertEqual(self.log[0], ("up_all", "old"),
                         "必须先把触点抬起")
        self.assertEqual(self.log[1], ("release", "old"),
                         "必须在新建实例之前释放旧实例：新实例构造会 kill 设备端 "
                         "minitouch，之后释放旧实例会把新实例的进程一起杀掉")
        self.assertEqual(self.log[2], ("create", None))
        self.assertTrue(old.released)
        self.assertIs(cm.current, new)
        self.assertEqual(self.clean_calls, [])
        self.assertGreater(clicker.last_minitouch_create_time, 0)

    def test_refresh_relies_on_up_all_contacts_fallback(self):
        old = _FakeSwitchableControl("old", lift_result=False, log=self.log)
        new = _FakeSwitchableControl("new", log=self.log)
        cm = _FakeControlManagerForClicker(old, new, log=self.log)
        clicker = _make_clicker()
        self.assertFalse(clicker._refresh_minitouch_instance(cm))
        self.assertEqual(self.clean_calls, [],
                         "up_all_contacts 内部已兜底清理，刷新路径不应重复跑一次 evdev 清理")
        self.assertTrue(old.released, "抬起失败也要释放旧实例")

    def test_refresh_without_up_all_interface_uses_evdev(self):
        old = types.SimpleNamespace()  # 没有 up_all_contacts / release
        cm = _FakeControlManagerForClicker(old, None, log=self.log)
        clicker = _make_clicker()
        self.assertFalse(clicker._refresh_minitouch_instance(cm))
        self.assertEqual(self.clean_calls, [("emulator-5560", "MiniTouch 刷新前抬起失败")])

    def test_refresh_create_failure_leaves_no_replacement(self):
        old = _FakeSwitchableControl("old", log=self.log)
        cm = _FakeControlManagerForClicker(old, None, log=self.log)
        clicker = _make_clicker()
        clicker._refresh_minitouch_instance(cm)
        self.assertIs(cm.current, old, "创建失败不应替换实例")
        self.assertEqual([e for e in self.log if e[0] == "replace"], [])
        self.assertTrue(old.released, "旧实例已按新顺序先释放（等待下一次重建）")

    def test_click_worker_flushes_pending_cleanup_before_clicking(self):
        clicker = _make_clicker()
        control = types.SimpleNamespace(ready=True, multi_taps=0, up_calls=0)

        def multi_tap(points, pressure=100, duration=0.1):
            control.multi_taps += 1
            clicker._stop_event.set()

        control.multi_tap = multi_tap
        control.up_all_contacts = lambda: True
        cm = _FakeControlManagerForClicker(control, log=self.log)
        clicker.operationer = types.SimpleNamespace(
            device=types.SimpleNamespace(control_manager=cm))

        touch_residue.mark_pending_cleanup("emulator-5560", logger=LOG)
        clicker._minitouch_click_worker([(10, 20)])

        self.assertEqual(
            self.clean_calls,
            [("emulator-5560", "连点启动前补清理挂起的残留触点")],
            "连点启动（任务启动边界）应补清理重连时挂起的残留触点")
        self.assertFalse(touch_residue.has_pending_cleanup("emulator-5560"))

    def test_click_worker_without_pending_does_not_touch_device(self):
        clicker = _make_clicker()
        control = types.SimpleNamespace(ready=True, multi_taps=0, up_calls=0)

        def multi_tap(points, pressure=100, duration=0.1):
            control.multi_taps += 1
            clicker._stop_event.set()

        control.multi_tap = multi_tap
        control.up_all_contacts = lambda: True
        cm = _FakeControlManagerForClicker(control, log=self.log)
        clicker.operationer = types.SimpleNamespace(
            device=types.SimpleNamespace(control_manager=cm))
        clicker._minitouch_click_worker([(10, 20)])
        self.assertEqual(self.clean_calls, [],
                         "无挂起时应零开销（连接点节奏都不该受影响）")

    def test_worker_finally_lifts_even_when_instance_invalidated(self):
        clicker = _make_clicker()
        control = types.SimpleNamespace(ready=True, multi_taps=0, up_calls=0)

        def multi_tap(points, pressure=100, duration=0.1):
            control.multi_taps += 1
            control.ready = False          # 模拟实例在连点期间被 release/替换
            clicker._stop_event.set()      # 让循环在下一轮判定前退出

        control.multi_tap = multi_tap

        def up_all_contacts():
            control.up_calls += 1
            return True

        control.up_all_contacts = up_all_contacts
        cm = _FakeControlManagerForClicker(control, log=self.log)
        clicker.operationer = types.SimpleNamespace(
            device=types.SimpleNamespace(control_manager=cm))
        clicker._minitouch_click_worker([(10, 20)])
        self.assertEqual(control.multi_taps, 1)
        self.assertEqual(control.up_calls, 1,
                         "实例失效（ready=False）也必须尝试抬起触点")

    def test_wait_stopped_returns_true_after_thread_exit(self):
        clicker = _make_clicker()
        thread = threading.Thread(target=clicker._stop_event.wait, args=(2.0,), daemon=True)
        clicker._threads = [thread]
        thread.start()
        clicker._stop_event.set()
        self.assertTrue(clicker.wait_stopped(timeout=2.0))

    def test_wait_stopped_returns_false_on_timeout(self):
        clicker = _make_clicker()
        blocker = threading.Event()
        thread = threading.Thread(target=blocker.wait, args=(1.0,), daemon=True)
        clicker._threads = [thread]
        thread.start()
        try:
            self.assertFalse(clicker.wait_stopped(timeout=0.2))
            self.assertTrue(clicker.running)
        finally:
            blocker.set()
            thread.join(timeout=1.0)


class ControlManagerSwitchTest(unittest.TestCase):
    """P1：切换控制模式前先抬起旧实例触点"""

    def _make_manager(self, current):
        cm = object.__new__(ControlManager)
        cm.logger = LOG
        cm.config = types.SimpleNamespace(set_config=lambda *a, **k: None)
        cm.control_mode = ControlMode.MiniTouch
        cm._control_lock = threading.RLock()
        cm.current_control = current
        return cm

    def test_switch_lifts_and_releases_old_control_first(self):
        log = []
        old = _FakeSwitchableControl("old", log=log)
        new = _FakeSwitchableControl("new", log=log)
        cm = self._make_manager(old)
        cm.create_control_instance = lambda: (log.append(("create", None)), new)[1]
        cm.switch_control_mode(ControlMode.U2)
        self.assertEqual(log[0], ("up_all", "old"), "切换前必须先抬起旧实例的触点")
        self.assertEqual(log[1], ("release", "old"),
                         "必须在创建新实例之前释放旧实例：旧实例 release() 会 kill "
                         "设备端 minitouch，在新实例之后释放会把新进程一起杀掉")
        self.assertEqual(log[2], ("create", None))
        self.assertTrue(old.released)
        self.assertIs(cm.current_control, new)

    def test_switch_restores_instance_when_new_create_fails(self):
        log = []
        old = _FakeSwitchableControl("old", log=log)
        restored = _FakeSwitchableControl("restored", log=log)
        cm = self._make_manager(old)
        calls = {"n": 0}

        def fake_create():
            calls["n"] += 1
            log.append(("create", calls["n"]))
            return None if calls["n"] == 1 else restored

        cm.create_control_instance = fake_create
        cm.switch_control_mode(ControlMode.U2)
        self.assertEqual(cm.control_mode, ControlMode.MiniTouch, "创建失败应回滚控制模式")
        self.assertIs(cm.current_control, restored, "应尝试恢复原模式的可用实例")
        self.assertTrue(old.released)

    def test_switch_leaves_no_control_when_restore_also_fails(self):
        log = []
        old = _FakeSwitchableControl("old", log=log)
        cm = self._make_manager(old)
        cm.create_control_instance = lambda: None
        cm.switch_control_mode(ControlMode.U2)
        self.assertEqual(cm.control_mode, ControlMode.MiniTouch, "创建失败应回滚控制模式")
        self.assertTrue(old.released, "旧实例在切换流程中已按新顺序释放")
        self.assertIsNone(cm.current_control, "恢复也失败时控制实例为空（日志已提示）")


class _FakeClickerSync:
    def __init__(self, log):
        self.log = log

    def wait_stopped(self, timeout=3.0):
        self.log.append(("wait_stopped", timeout))
        return True


class _FakeExecutor:
    def __init__(self, log):
        self.log = log

    def stop_task(self, task):
        self.log.append(("stop_task", task.task_name))

    def set_watchdog(self, watchdog):
        self.log.append(("set_watchdog", watchdog))


class _FakeTaskQueue:
    def __init__(self, tasks):
        self.tasks = list(tasks)

    def get_tasks_by_status(self, status):
        return [t for t in self.tasks if t.current_status == status]


class SchedulerResidueTest(unittest.TestCase):
    """P1/P2：停止顺序（先等连点线程退出再释放控制实例）与启停自检接线"""

    def setUp(self):
        self.log = []

    def _make_service(self):
        svc = object.__new__(SchedulerService)
        svc.logger = LOG
        svc.config = types.SimpleNamespace(get_config=lambda key, default=None: "emulator-5560")
        svc._lock = threading.Lock()
        svc.running = True
        svc._pending_activate_tasks = []
        svc._temp_activated_tasks = {}
        svc._stop_reason = ""
        svc.run_once = False
        svc.started_at = None
        svc.watchdog = None
        svc.on_status_change = None
        svc.transition_manager = None
        svc._reset_once_progress = lambda: None
        svc._push_snapshot = lambda: None
        svc.state = types.SimpleNamespace(set_running=lambda *a, **k: None,
                                          reset_tasks=lambda: None)
        svc.device = types.SimpleNamespace(
            control_manager=types.SimpleNamespace(
                release=lambda: self.log.append(("release_control", None))),
            screen_manager=types.SimpleNamespace(
                release=lambda: self.log.append(("release_screen", None))),
        )
        svc.operationer = types.SimpleNamespace(
            stop=lambda: self.log.append(("operationer_stop", None)))
        svc.executor = _FakeExecutor(self.log)
        clicker = _FakeClickerSync(self.log)
        task = types.SimpleNamespace(
            task_name="任务A", current_status=0,
            operationer=types.SimpleNamespace(clicker=clicker))
        svc.task_queue = _FakeTaskQueue([task])
        # 自检会触碰设备，单测里只记录调用位置
        svc._ensure_no_stale_contacts = lambda reason: self.log.append(
            ("ensure_no_stale", reason)) or False
        return svc

    def test_stop_waits_clicker_before_releasing_control(self):
        svc = self._make_service()
        self.assertTrue(svc.stop("单测"))
        self.assertEqual(self.log, [
            ("stop_task", "任务A"),
            ("wait_stopped", 3.0),
            ("release_control", None),
            ("release_screen", None),
            ("ensure_no_stale", "调度器停止后自检"),
            ("operationer_stop", None),
            ("set_watchdog", None),
        ], "必须先等连点线程退出，再释放控制实例，最后兜底自检")

    def test_stop_without_running_tasks_still_self_checks(self):
        svc = self._make_service()
        svc.task_queue = _FakeTaskQueue([])
        svc.stop("单测")
        self.assertIn(("ensure_no_stale", "调度器停止后自检"), self.log)

    def test_ensure_no_stale_contacts_delegates_with_serial(self):
        svc = self._make_service()
        svc._ensure_no_stale_contacts = SchedulerService._ensure_no_stale_contacts.__get__(svc)
        calls = []
        flushed = []
        saved = touch_residue.ensure_no_stale_contacts
        saved_flush = touch_residue.flush_pending_cleanup
        touch_residue.ensure_no_stale_contacts = (
            lambda serial, logger=None, reason="": (calls.append((serial, reason)), True)[1])
        touch_residue.flush_pending_cleanup = (
            lambda serial, logger=None, reason="": (flushed.append((serial, reason)), False)[1])
        try:
            self.assertTrue(svc._ensure_no_stale_contacts("单测"))
        finally:
            touch_residue.ensure_no_stale_contacts = saved
            touch_residue.flush_pending_cleanup = saved_flush
        self.assertEqual(calls, [("emulator-5560", "单测")])
        self.assertEqual(flushed, [("emulator-5560", "单测｜补清理挂起的残留触点")],
                         "调度器启停是任务边界，应补清理连点期间挂起的残留")

    def test_device_serial_falls_back_to_control_and_normalizes(self):
        svc = self._make_service()
        svc.config = types.SimpleNamespace(get_config=lambda key, default=None: "")
        svc.device = types.SimpleNamespace(control_manager=types.SimpleNamespace(
            get_current_control=lambda: types.SimpleNamespace(serial="emulator：5560")))
        self.assertEqual(svc._device_serial(), "emulator:5560")

    def test_device_serial_empty_without_config_and_device(self):
        svc = self._make_service()
        svc.config = types.SimpleNamespace(get_config=lambda key, default=None: "")
        svc.device = None
        self.assertEqual(svc._device_serial(), "")

    def test_start_and_stop_wire_self_check(self):
        import inspect
        self.assertIn("调度器启动前自检", inspect.getsource(SchedulerService.start))
        stop_source = inspect.getsource(SchedulerService.stop)
        self.assertIn("调度器停止后自检", stop_source)
        self.assertIn("_wait_clicker_stopped", stop_source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
