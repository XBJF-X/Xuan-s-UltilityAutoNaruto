# -*- coding: utf-8 -*-
"""验证 adb 就绪等待与 MiniTouch 冷启动重试（修复"首次启动调度器失败"）。

1. `backend/core/legacy/Control/adb_bootstrap.py` 的 `ensure_adb_device()`：
   - 设备在等待窗口内出现在 adb 设备列表 → True（不重启 adb server）；
   - 超时未出现 → False（日志给出当前设备列表与排查提示）；
   - `ip:port` 串口 → 额外调用一次 adb connect 兜底；
   - 本机模拟器串口（emulator-xxxx / 127.0.0.1:xxxx）长时间未出现 → 重启
     一次 adb server 强制重扫端口（只重启一次）；
   - adb 可执行文件缺失（FileNotFoundError）→ 立即 False，不空等超时。
2. `MiniTouch.__init__`：adb/设备瞬态失败时等待 + 重试，成功即 ready；
   全部失败抛异常且重试前清理半初始化核心；分辨率不符（InvalidResolution）
   不重试。

全部用假 adbutils / 假 minitouch 核心，不触碰真实 adb 与模拟器。
"""
import logging
import os
import sys
import types
import unittest
from types import SimpleNamespace

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.core.legacy.Control import adb_bootstrap
from backend.core.legacy.Control import MiniTouch as mt_module
from backend.core.legacy.Control import InvalidResolution


class _FakeAdbClient:
    """假 adbutils.adb：list / connect / server_kill 均可观察。"""

    def __init__(self, states_list=None, raise_exc=None, appear_after=0):
        # states_list: 每次 list() 取一个 dict 快照（按调用次序轮转，最后一组重复）
        self._states_list = list(states_list or [])
        self._raise_exc = raise_exc
        self._appear_after = appear_after
        self.list_calls = 0
        self.connect_calls = []
        self.kill_calls = 0

    def list(self):
        self.list_calls += 1
        if self._raise_exc is not None:
            raise self._raise_exc
        if self._appear_after and self.list_calls >= self._appear_after:
            return [SimpleNamespace(serial="emulator-5560", state="device")]
        idx = min(self.list_calls - 1, len(self._states_list) - 1)
        states = self._states_list[idx] if self._states_list else {}
        return [SimpleNamespace(serial=s, state=st) for s, st in states.items()]

    def connect(self, addr, timeout=None):
        self.connect_calls.append(addr)
        return f"connected to {addr}"

    def server_kill(self):
        self.kill_calls += 1
        self.list_calls = 0  # 重启后重新开始计数


def _fake_adbutils(adb):
    mod = types.ModuleType("adbutils")
    mod.adb = adb
    mod.AdbError = type("AdbError", (Exception,), {})
    return mod


class EnsureAdbDeviceTest(unittest.TestCase):
    """adb_bootstrap.ensure_adb_device"""

    def setUp(self):
        self._saved = sys.modules.get("adbutils")
        self.logger = logging.getLogger("test.adb_bootstrap")

    def tearDown(self):
        if self._saved is not None:
            sys.modules["adbutils"] = self._saved
        else:
            sys.modules.pop("adbutils", None)

    def _install(self, client):
        sys.modules["adbutils"] = _fake_adbutils(client)
        return client

    def test_device_appears_returns_true(self):
        client = self._install(_FakeAdbClient(appear_after=3))
        ok = adb_bootstrap.ensure_adb_device(
            "emulator-5560", self.logger, timeout=3.0, poll_interval=0.05)
        self.assertTrue(ok)
        self.assertGreaterEqual(client.list_calls, 3)
        self.assertEqual(client.kill_calls, 0)

    def test_timeout_returns_false_and_reports_devices(self):
        self._install(_FakeAdbClient([{"emulator-5554": "device"}]))
        records = []

        class _Handler(logging.Handler):
            def emit(self, record):
                records.append(record.getMessage())

        self.logger.addHandler(_Handler())
        self.logger.setLevel(logging.ERROR)
        ok = adb_bootstrap.ensure_adb_device(
            "emulator-5560", self.logger, timeout=0.3, poll_interval=0.05)
        self.assertFalse(ok)
        self.assertTrue(
            any("未就绪" in r and "emulator-5554(device)" in r for r in records),
            f"日志缺少就绪失败详情: {records}")

    def test_ip_port_serial_triggers_connect(self):
        client = self._install(_FakeAdbClient([{"127.0.0.1:5555": "offline"}]))
        ok = adb_bootstrap.ensure_adb_device(
            "127.0.0.1:5555", self.logger, timeout=0.3, poll_interval=0.05)
        self.assertFalse(ok)
        self.assertTrue(client.connect_calls, "ip:port 串口应主动 adb connect")
        self.assertTrue(all(a == "127.0.0.1:5555" for a in client.connect_calls))

    def test_local_emulator_rescan_once(self):
        client = self._install(_FakeAdbClient([{"emulator-5554": "device"}]))
        old = adb_bootstrap.RESCAN_AFTER
        adb_bootstrap.RESCAN_AFTER = 0.15
        try:
            ok = adb_bootstrap.ensure_adb_device(
                "emulator-5560", self.logger, timeout=0.6, poll_interval=0.05)
        finally:
            adb_bootstrap.RESCAN_AFTER = old
        self.assertFalse(ok)
        self.assertEqual(client.kill_calls, 1, "本机模拟器串口应只重启一次 adb server")

    def test_local_emulator_rescan_disabled(self):
        client = self._install(_FakeAdbClient([{"emulator-5554": "device"}]))
        old = adb_bootstrap.RESCAN_AFTER
        adb_bootstrap.RESCAN_AFTER = 0.1
        try:
            ok = adb_bootstrap.ensure_adb_device(
                "emulator-5560", self.logger, timeout=0.4, poll_interval=0.05,
                allow_rescan=False)
        finally:
            adb_bootstrap.RESCAN_AFTER = old
        self.assertFalse(ok)
        self.assertEqual(client.kill_calls, 0, "allow_rescan=False 时不得重启 adb server")

    def test_missing_adb_fails_fast(self):
        client = self._install(_FakeAdbClient(raise_exc=FileNotFoundError("adb not found")))
        ok = adb_bootstrap.ensure_adb_device(
            "emulator-5560", self.logger, timeout=5.0, poll_interval=0.05)
        self.assertFalse(ok)
        self.assertEqual(client.list_calls, 1, "缺少 adb 时应立即返回，不空等超时")

    def test_normalize_serial_fullwidth_colon(self):
        self.assertEqual(adb_bootstrap.normalize_serial(" 127.0.0.1：5555 "), "127.0.0.1:5555")
        self.assertEqual(adb_bootstrap.normalize_serial(None), "")


    def test_empty_serial_returns_false(self):
        self.assertFalse(adb_bootstrap.ensure_adb_device("", self.logger, timeout=0.1))


class _FakeCore:
    """假的最小 minitouch 核心（模拟 minidevice.MiniTouch）。"""

    instances = []

    def __init__(self, serial, window_size=(1600, 900)):
        self.serial = serial
        self.max_contacts = 2
        self.max_pressure = 100
        self.stop_called = False
        self.send_calls = []
        _FakeCore.instances.append(self)

    def send(self, content):
        self.send_calls.append(content)

    def stop(self):
        self.stop_called = True


class _FakeAdbDevice:
    # adbutils 的 WindowSize 是 NamedTuple，既支持 .width 也支持 [0]（MiniTouch 两种都用了）
    class _WinSize(tuple):
        def __new__(cls, width, height):
            return super().__new__(cls, (width, height))

        width = property(lambda self: self[0])
        height = property(lambda self: self[1])

    def __init__(self, size=(1600, 900)):
        self._size = size

    def getprop(self, _name):
        return "x86_64"

    def rotation(self):
        return 0

    def window_size(self):
        return _FakeAdbDevice._WinSize(*self._size)


class _FakeConfig:
    def __init__(self, serial="emulator-5560"):
        self._serial = serial

    def get_config(self, key, default=None):
        return self._serial if key == "串口" else default


class MiniTouchInitRetryTest(unittest.TestCase):
    """MiniTouch.__init__ 的等待 + 重试链路"""

    def setUp(self):
        self.logger = logging.getLogger("test.MiniTouch")
        self._saved = (mt_module.MiniTouchCore, mt_module.adb,
                       mt_module.ensure_adb_device, mt_module._INIT_RETRY_INTERVAL,
                       mt_module._INIT_WAIT_TIMEOUTS)
        mt_module._INIT_RETRY_INTERVAL = 0.01
        mt_module._INIT_WAIT_TIMEOUTS = (0.05, 0.05, 0.05)
        self.ensure_calls = []
        mt_module.ensure_adb_device = self._fake_ensure
        _FakeCore.instances = []

    def tearDown(self):
        (mt_module.MiniTouchCore, mt_module.adb,
         mt_module.ensure_adb_device, mt_module._INIT_RETRY_INTERVAL,
         mt_module._INIT_WAIT_TIMEOUTS) = self._saved

    def _fake_ensure(self, serial, logger=None, timeout=None, poll_interval=None):
        self.ensure_calls.append((serial, timeout))
        return False  # 覆盖真实等待，只验证调用参数

    def _install_core(self, fail_times=0, size=(1600, 900)):
        """前 fail_times 次构造抛 `device 'xxx' not found`，之后成功。"""
        state = {"left": fail_times}

        class _Core(_FakeCore):
            def __init__(self, serial):
                if state["left"] > 0:
                    state["left"] -= 1
                    raise RuntimeError(f"device '{serial}' not found")
                super().__init__(serial, window_size=size)

        mt_module.MiniTouchCore = _Core
        mt_module.adb = SimpleNamespace(device=lambda serial: _FakeAdbDevice(size))

    def test_retry_then_success(self):
        self._install_core(fail_times=1)
        ctrl = mt_module.MiniTouch(_FakeConfig(), self.logger)
        self.assertTrue(ctrl.ready)
        self.assertEqual(len(self.ensure_calls), 2, "首次失败后应重试一次")
        self.assertTrue(all(c[0] == "emulator-5560" for c in self.ensure_calls))
        ctrl.release()
        self.assertFalse(ctrl.ready)

    def test_all_attempts_fail_raises(self):
        self._install_core(fail_times=99)
        with self.assertRaises(RuntimeError) as ctx:
            mt_module.MiniTouch(_FakeConfig(), self.logger)
        self.assertIn("not found", str(ctx.exception))
        self.assertEqual(len(self.ensure_calls), mt_module._INIT_ATTEMPTS)

    def test_invalid_resolution_not_retried(self):
        self._install_core(fail_times=0, size=(1600, 1000))
        with self.assertRaises(InvalidResolution):
            mt_module.MiniTouch(_FakeConfig(), self.logger)
        self.assertEqual(len(self.ensure_calls), 1, "分辨率不符不应重试")

    def test_half_initialized_core_is_discarded_on_retry(self):
        """核心已建立但设备命令失败时，重试前应 stop 该核心。"""
        state = {"n": 0}

        class _Core(_FakeCore):
            def __init__(self, serial):
                state["n"] += 1
                super().__init__(serial, window_size=(1600, 900))

        mt_module.MiniTouchCore = _Core

        class _BadAdbDevice(_FakeAdbDevice):
            def getprop(self, _name):
                raise RuntimeError("device 'emulator-5560' not found")

        mt_module.adb = SimpleNamespace(device=lambda serial: _BadAdbDevice())
        with self.assertRaises(RuntimeError):
            mt_module.MiniTouch(_FakeConfig(), self.logger)
        self.assertTrue(any(c.stop_called for c in _FakeCore.instances),
                        "重试前应 stop 半初始化核心")


if __name__ == "__main__":
    unittest.main(verbosity=2)
