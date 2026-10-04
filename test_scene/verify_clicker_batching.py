# -*- coding: utf-8 -*-
"""验证「U2 弃用路由」与「连点器全局单例 + 集中批量提交」。

覆盖三个改动点：

1. ``Control.resolve_control_mode``：控制模式归一化
   - 0 → MiniTouch；1（存量 U2）→ MiniTouch（路由，不重建 U2 实例）；
   - 非法值 / 空值 / None → MiniTouch；
   - 合法值原样返回，枚举实例同样可用。
2. ``touch_batch``：集中批量提交的命令流构造
   - 单周期命令流结构（d…/c/w/u…/c）；
   - N 个周期合并为**一条**命令流，且只出现一次投递（由假控制统计）；
   - hold/interval 的组合与 ``delay_ms`` 返回值；周期数夹到上限。
3. ``ClickEngine``：全局单例 + 长驻线程 + 会话语义
   - 同一设备多次 ``start/stop`` 只创建**一条**工作线程、**一个**引擎实例；
   - 停止后线程仍存活（长驻复用），会话立即停止投递；
   - 运行中 ``update_coordinates`` 立即生效（新坐标进入下一批）；
   - 后注册的会话接管当前连点（同一时刻只有一份坐标在投递）；
   - ``MINITOUCH_MAX_LIFETIME`` 到期触发一次重建。

全部使用假设备/假控制，不触碰真实 adb 与模拟器。

运行方式（**不要把 stdout 接进管道**，受限沙箱下子进程写管道会失败）::

    .\\.venv\\Scripts\\python.exe -X utf8 test_scene\\verify_clicker_batching.py > test_scene\\_clicker_result.txt 2>&1

结果同时写入 ``test_scene/verify_clicker_batching.out.txt``，便于直接读取。
"""
import io
import logging
import os
import sys
import threading
import time
import types
import unittest
from typing import List

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)


def _stub_heavy_deps():
    """屏蔽会在导入期启动外部进程的重依赖。

    ``backend.core.legacy.Control.MiniTouch`` 在模块级 ``from adbutils import adb``，
    而导入 adbutils 会去启动随包分发的 ``adb.exe``（受限沙箱下会弹
    "python application 无法正常启动" 并被拒绝）。本验证只测纯逻辑与引擎调度，
    因此注入哑模块替代 adbutils / minidevice，避免任何外部进程与设备访问。
    """
    if "adbutils" not in sys.modules:
        adbutils = types.ModuleType("adbutils")
        adbutils.adb = types.SimpleNamespace(
            device=lambda *a, **k: None, list=lambda *a, **k: [])
        sys.modules["adbutils"] = adbutils

    if "minidevice" not in sys.modules:
        minidevice = types.ModuleType("minidevice")

        class _FakeMiniTouchCore:  # pragma: no cover - 占位，测试不实例化
            def __init__(self, *a, **k):
                raise RuntimeError("测试环境不应实例化真实 minitouch 核心")

        minidevice.MiniTouch = _FakeMiniTouchCore
        sys.modules["minidevice"] = minidevice

    if "minidevice.utils.command_builder_utils" not in sys.modules:
        utils_mod = types.ModuleType("minidevice.utils")
        cb_mod = types.ModuleType("minidevice.utils.command_builder_utils")

        class _FakeCommandBuilder:  # pragma: no cover - 占位
            def __init__(self):
                self._content = ""

            def append(self, text):
                self._content += text + "\n"

            def commit(self):
                self.append("c")

            def down(self, i, x, y, p):
                self.append(f"d {i} {x} {y} {p}")

            def up(self, i):
                self.append(f"u {i}")

            def wait(self, ms):
                self.append(f"w {ms}")

            def move(self, i, x, y, p):
                self.append(f"m {i} {x} {y} {p}")

            def publish(self, connection):
                self.commit()

            def reset(self):
                self._content = ""

        cb_mod.CommandBuilder = _FakeCommandBuilder
        utils_mod.command_builder_utils = cb_mod
        sys.modules["minidevice.utils"] = utils_mod
        sys.modules["minidevice.utils.command_builder_utils"] = cb_mod


_stub_heavy_deps()

logging.basicConfig(level=logging.CRITICAL)

from backend.core.legacy.Control import (  # noqa: E402
    ControlMode,
    resolve_control_mode,
)
from backend.core.legacy.Control import touch_batch  # noqa: E402
from backend.core.legacy.Control import clicker_engine  # noqa: E402
from backend.core.legacy.Control.clicker_engine import (  # noqa: E402
    ClickEngine,
    ClickerSession,
    get_click_engine,
    shutdown_all_clickers,
)

_OUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "verify_clicker_batching.out.txt")


class _TeeStream(io.TextIOBase):
    """把 unittest 输出同时写到内存缓冲区与项目内结果文件。

    受限沙箱下"子进程 → 管道"不可用，因此结果**落盘**而不是依赖 stdout 被捕获。
    """

    def __init__(self, buffer):
        self._buffer = buffer
        self._file = open(_OUT_FILE, "w", encoding="utf-8", errors="replace")

    def write(self, text):
        self._buffer.write(text)
        self._file.write(text)
        self._file.flush()
        return len(text)

    def flush(self):
        self._file.flush()

    def close(self):
        try:
            self._file.close()
        except Exception:
            pass



class _FakeControl:
    """假 MiniTouch 控制实例：记录每一批被投递的命令流。"""

    def __init__(self, max_contacts=10, screen=(1600, 900)):
        self.ready = True
        self.max_contacts = max_contacts
        self._screen = screen
        self.batches: List[str] = []
        self.released = 0
        self.lifted = 0
        self._lock = threading.Lock()

    def convert_point(self, x, y):
        return x, y

    def tap_command_batch(self, raw_points, command):
        with self._lock:
            self.batches.append(command)
        return True

    def up_all_contacts(self):
        self.lifted += 1
        return True

    def release(self):
        self.released += 1

    @property
    def batch_count(self):
        with self._lock:
            return len(self.batches)

    def cycles_in_batches(self):
        """统计命令流里出现的 ``d 0 `` 次数 = 实际投递的点击周期数。"""
        with self._lock:
            return sum(b.count("d 0 ") for b in self.batches)


class _FakeControlManager:
    """假控制管理器：可替换当前控制实例（模拟刷新/模式切换）。"""

    def __init__(self, control):
        self._control = control
        self._lock = threading.Lock()
        self.create_calls = 0

    def get_current_control(self):
        with self._lock:
            return self._control

    def replace_current_control(self, control):
        with self._lock:
            old = self._control
            self._control = control
            return old

    def create_control_instance(self):
        self.create_calls += 1
        return _FakeControl()


class _FakeDevice:
    """假 Device：提供 regularize_coordinate 与控制管理器。"""

    def __init__(self, manager, scale=1.0):
        self.control_manager = manager
        self._scale = scale

    def regularize_coordinate(self, x, y):
        return int(x * self._scale), int(y * self._scale)


class TestResolveControlMode(unittest.TestCase):
    """控制模式归一化：U2 一律路由到 MiniTouch。"""

    def test_minitouch_kept(self):
        for raw in (0, "0", ControlMode.MiniTouch):
            self.assertIs(resolve_control_mode(raw), ControlMode.MiniTouch)

    def test_deprecated_u2_routed(self):
        # 存量配置里的 1（U2）必须路由到 MiniTouch，而不是重建 U2
        for raw in (1, "1", " 1 ", ControlMode.U2):
            self.assertIs(
                resolve_control_mode(raw), ControlMode.MiniTouch,
                msg=f"控制模式 {raw!r} 应路由到 MiniTouch")

    def test_invalid_falls_back_to_minitouch(self):
        for raw in (None, "", "  ", "abc", 7, -1, 99, True, False, [], {}):
            self.assertIs(
                resolve_control_mode(raw), ControlMode.MiniTouch,
                msg=f"控制模式 {raw!r} 应回退到 MiniTouch")

    def test_u2_still_importable(self):
        # 枚举成员保留，避免存量代码/数据引用报错
        self.assertEqual(int(ControlMode.U2), 1)
        self.assertEqual(int(ControlMode.MiniTouch), 0)


class TestTouchBatch(unittest.TestCase):
    """集中批量提交的命令流构造。"""

    def test_single_cycle_structure(self):
        cmd, delay = touch_batch.build_tap_batch(
            [[10, 20], [30, 40]], pressure=100, hold_ms=80, cycles=1)
        self.assertEqual(
            cmd,
            "d 0 10 20 100\nd 1 30 40 100\nc\nw 80\nu 0\nu 1\nc\n")
        self.assertEqual(delay, 80)

    def test_multi_cycle_is_one_command_stream(self):
        cycles = 5
        cmd, delay = touch_batch.build_tap_batch(
            [[1, 2]], pressure=100, hold_ms=80, cycles=cycles, interval_ms=150)
        # 5 个周期 → 5 组 down/up，说明"多点同时"语义按周期重复
        self.assertEqual(cmd.count("d 0 1 2 100"), cycles)
        self.assertEqual(cmd.count("u 0"), cycles)
        # 周期之间插入间隔，但最后一个周期后不追加等待
        self.assertEqual(cmd.count("w 150"), cycles - 1)
        self.assertEqual(cmd.count("w 80"), cycles)
        self.assertEqual(delay, 80 + 150)

    def test_cycles_clamped(self):
        cmd, _ = touch_batch.build_tap_batch(
            [[1, 2]], cycles=10_000, hold_ms=10)
        self.assertEqual(
            cmd.count("d 0 1 2 100"), touch_batch.MAX_CYCLES_PER_PUBLISH)

    def test_empty_points_rejected(self):
        with self.assertRaises(ValueError):
            touch_batch.build_tap_batch([], cycles=1)

    def test_hold_zero_omits_wait(self):
        cmd, delay = touch_batch.build_tap_batch(
            [[1, 2]], hold_ms=0, cycles=1)
        self.assertNotIn("w 0", cmd)
        self.assertEqual(delay, 0)


class TestClickEngine(unittest.TestCase):
    """连点引擎：线程/实例复用、会话语义、批量提交。"""

    def setUp(self):
        self.control = _FakeControl()
        self.manager = _FakeControlManager(self.control)
        self.device = _FakeDevice(self.manager)
        self.engines = []

    def tearDown(self):
        for engine in self.engines:
            engine.shutdown()
        shutdown_all_clickers()

    def _make_engine(self, serial="emulator-5558"):
        engine = ClickEngine(self.device, serial, logging.getLogger("test"))
        self.engines.append(engine)
        return engine

    def test_start_stop_reuses_single_thread(self):
        """多次 start/stop 不新建线程（"耗费线程"的核心问题）。"""
        engine = self._make_engine()
        thread = engine._thread
        thread_ids = set()

        session = engine.register()
        for _ in range(20):
            session.begin([(100, 200)])
            thread_ids.add(engine._thread.ident)
            time.sleep(0.02)
            session.stop()
            time.sleep(0.01)
        engine.unregister(session)

        self.assertIs(engine._thread, thread, "工作线程被重建")
        self.assertEqual(len(thread_ids), 1, "start/stop 期间线程发生了切换")
        self.assertTrue(engine.alive, "引擎线程应长驻，不随任务 stop 退出")

    def test_get_click_engine_is_singleton_per_serial(self):
        """同一串口返回同一个引擎实例（全局单例）。"""
        e1 = get_click_engine(self.device, "emulator-5558")
        e2 = get_click_engine(self.device, "emulator-5558")
        self.engines.append(e1)
        self.assertIs(e1, e2)

        e3 = get_click_engine(self.device, "emulator-5560")
        self.engines.append(e3)
        self.assertIsNot(e1, e3)

    def test_stop_halts_delivery_immediately(self):
        """stop() 后不再投递新的批次。"""
        engine = self._make_engine()
        session = engine.register()
        session.begin([(100, 200)])
        deadline = time.perf_counter() + 2.0
        while self.control.batch_count == 0 and time.perf_counter() < deadline:
            time.sleep(0.01)
        self.assertGreater(self.control.batch_count, 0, "连点未产生任何批次")

        session.stop()
        engine.unregister(session)
        # 等在途批次收尾，之后计数必须不再增长
        time.sleep(0.3)
        settled = self.control.batch_count
        time.sleep(0.5)
        self.assertEqual(self.control.batch_count, settled, "stop 后仍在投递点击")

    def test_batch_submission_is_concentrated(self):
        """集中批量提交：每批包含多个周期，往返次数远小于周期数。"""
        engine = self._make_engine()
        session = engine.register()
        session.begin([(100, 200)])
        deadline = time.perf_counter() + 3.0
        while self.control.batch_count < 2 and time.perf_counter() < deadline:
            time.sleep(0.01)
        session.stop()
        engine.unregister(session)

        cycles = self.control.cycles_in_batches()
        batches = self.control.batch_count
        self.assertGreater(batches, 0)
        self.assertGreaterEqual(
            cycles, batches * 2,
            f"批量提交未生效：{cycles} 个周期只用了 {batches} 次往返")

    def test_update_coordinates_takes_effect_live(self):
        """运行中更新坐标立即生效（旧实现需先 stop 再 start）。"""
        engine = self._make_engine()
        session = engine.register()
        session.begin([(111, 222)])
        deadline = time.perf_counter() + 2.0
        while self.control.batch_count == 0 and time.perf_counter() < deadline:
            time.sleep(0.01)

        session.set_coordinates([(333, 444)])
        deadline = time.perf_counter() + 2.0
        while "333" not in "".join(self.control.batches[-3:]) \
                and time.perf_counter() < deadline:
            time.sleep(0.01)
        session.stop()
        engine.unregister(session)
        self.assertIn("333 444", "".join(self.control.batches),
                      "更新后的坐标未被投递")

    def test_latest_session_takes_over(self):
        """后注册的会话接管，同一时刻只有一份坐标在投递。"""
        engine = self._make_engine()
        first = engine.register()
        first.begin([(10, 10)])
        second = engine.register()
        second.begin([(20, 20)])

        deadline = time.perf_counter() + 2.0
        while self.control.batch_count == 0 and time.perf_counter() < deadline:
            time.sleep(0.01)
        time.sleep(0.3)
        recent = "".join(self.control.batches[-4:])
        second.stop()
        first.stop()
        engine.unregister(first)
        engine.unregister(second)

        self.assertIn("20 20", recent, "接管后的会话未投递")
        self.assertNotIn("10 10", recent, "旧会话仍在投递（坐标互相打架）")

    def test_stale_control_is_refreshed(self):
        """超过存活上限时重建一次 minitouch 服务，并切换到新实例。"""
        engine = self._make_engine()
        session = engine.register()
        # 让引擎认为当前控制实例已存活超过上限
        engine._note_control(self.control)
        engine._control_seen_at = time.perf_counter() - (
            clicker_engine.MINITOUCH_MAX_LIFETIME + 1)

        session.begin([(100, 200)])
        deadline = time.perf_counter() + 3.0
        while self.manager.create_calls == 0 and time.perf_counter() < deadline:
            time.sleep(0.01)
        session.stop()
        engine.unregister(session)

        self.assertGreaterEqual(self.manager.create_calls, 1, "未触发重建")
        self.assertGreaterEqual(self.control.released, 1, "旧实例未被释放")
        self.assertGreaterEqual(self.control.lifted, 1, "重建前未抬起触点")

    def test_shutdown_stops_thread(self):
        """shutdown 后线程退出，引擎不再存活。"""
        engine = self._make_engine()
        self.assertTrue(engine.alive)
        engine.shutdown(timeout=3.0)
        self.assertFalse(engine.alive, "shutdown 后线程仍在运行")


class TestSessionSemantics(unittest.TestCase):
    """会话状态机：running 与 stop 语义。"""

    def test_begin_and_stop(self):
        session = ClickerSession()
        self.assertFalse(session.running)
        session.begin([(1, 2)])
        self.assertTrue(session.running)
        self.assertFalse(session.stop_event.is_set())
        session.stop()
        self.assertFalse(session.running)
        self.assertTrue(session.stop_event.is_set())

    def test_begin_clears_stale_stop(self):
        session = ClickerSession()
        session.stop()
        session.begin([(1, 2)])
        self.assertFalse(session.stop_event.is_set(),
                         "复用会话时未清掉旧的停止信号")

    def test_snapshot_is_a_copy(self):
        session = ClickerSession()
        session.begin([(1, 2)])
        snap = session.snapshot()
        snap.append((9, 9))
        self.assertEqual(session.snapshot(), [(1, 2)])


if __name__ == "__main__":
    import traceback

    buffer = io.StringIO()
    tee = _TeeStream(buffer)
    original_stdout, original_stderr = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = tee
    exit_code = 1
    try:
        result = unittest.main(verbosity=2, exit=False)
        exit_code = 0 if result.result.wasSuccessful() else 1
    except BaseException:
        traceback.print_exc()
        exit_code = 2
    finally:
        sys.stdout, sys.stderr = original_stdout, original_stderr
        tee.flush()
        tee.close()

    summary = "RESULT: PASS" if exit_code == 0 else f"RESULT: FAIL(exit={exit_code})"
    # 同时落盘与尽力打印（打印失败不影响落盘结论）
    try:
        with open(_OUT_FILE, "a", encoding="utf-8") as f:
            f.write("\n" + summary + "\n")
    except Exception:
        pass
    try:
        print(summary)
    except Exception:
        pass
    sys.exit(exit_code)

