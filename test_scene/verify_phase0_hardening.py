# -*- coding: utf-8 -*-
"""阶段 0「失控型缺陷」加固回归（2026-09-17）

覆盖 4 项修复，全部离线、不触真实 setting.ini / 不连设备：

1. **setting.ini 读路径不写盘**：`Setting` 构造只在"磁盘内容与合并结果不一致"时写盘
   （旧实现无条件整文件重写 → 一次读 = 一次写；`SettingsService()` 每次调用都新建实例）。
2. **setting.ini 原子写**：`save_to_file()` 走 tmp + `os.replace`，失败不残留 .tmp，
   并用模块级锁串行化（旧实现 `open('w')` 截断式写入）。
3. **SettingsService 进程级单例**：`get_settings()`/`SettingsService()` 共用唯一实例，
   `path=` 参数保留测试隔离能力，`reset_settings_cache()` 可复位。
4. **后台循环健壮性**：`扫描间隔` / `超时检测-检测间隔秒` 填成非数字时，循环不再因
   `try` 块外的类型转换异常静默死亡；致命异常会置停机并上报。
5. **MiJingTanXian 单参数异常**：`TaskCompleted` 只接受 1 个参数，旧实现传 2 个会抛
   TypeError 被误判成"未捕获异常"。
"""
import configparser
import logging
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.core.setting_model import Setting          # noqa: E402
from backend.services import settings_service as ss_mod  # noqa: E402


def _read_ini(path: Path) -> dict:
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(path, encoding="utf-8")
    return {s: dict(parser.items(s)) for s in parser.sections()}


class SettingNoWriteOnReadTest(unittest.TestCase):
    """1 + 2：读路径不写盘；写盘为原子操作"""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="xuan_verify_hardening_"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_missing_file_is_created(self):
        """首次构造（文件不存在）仍要落盘默认配置——旧行为不能丢"""
        ini = self.tmp / "setting.ini"
        setting = Setting(parent_logger=logging.getLogger("verify"), setting_path=ini)
        self.assertTrue(ini.exists(), "文件不存在时应写出合并后的默认配置")
        self.assertIn("助手设置", _read_ini(ini))
        self.assertEqual(setting.get("助手设置", "启动提示", None), "True")

    def test_second_construction_does_not_write(self):
        """内容一致时第二次构造不得改写文件（mtime + 内容双重校验）"""
        ini = self.tmp / "setting.ini"
        Setting(parent_logger=logging.getLogger("verify"), setting_path=ini)
        before = ini.read_bytes()
        stat_before = ini.stat().st_mtime_ns

        Setting(parent_logger=logging.getLogger("verify"), setting_path=ini)
        self.assertEqual(ini.read_bytes(), before, "内容一致时不应改写文件")
        self.assertEqual(ini.stat().st_mtime_ns, stat_before,
                         "内容一致时不应触碰文件（旧实现每次构造都整文件重写）")

    def test_readonly_never_writes(self):
        """readonly=True（只读探测）即使文件缺失也不落盘"""
        ini = self.tmp / "setting.ini"
        setting = Setting(parent_logger=logging.getLogger("verify"),
                          setting_path=ini, readonly=True)
        self.assertFalse(ini.exists(), "readonly 构造不应写盘")
        self.assertEqual(setting.get("助手设置", "启动提示", None), "True",
                         "只读也应有合并后的默认值可用")

    def test_save_to_file_is_atomic_and_returns_bool(self):
        """原子写：成功返回 True、不残留 .tmp；内容可回读"""
        ini = self.tmp / "setting.ini"
        setting = Setting(parent_logger=logging.getLogger("verify"), setting_path=ini)
        self.assertIs(setting.save_to_file(), True)
        self.assertFalse((self.tmp / "setting.ini.tmp").exists(), "不应残留临时文件")

        setting.set("助手设置", "启动提示", "False")
        self.assertEqual(_read_ini(ini)["助手设置"]["启动提示"], "False")

    def test_save_failure_reports_and_leaves_no_tmp(self):
        """写盘失败：返回 False、不抛异常、不残留 .tmp（路径被目录占用）"""
        blocker = self.tmp / "setting.ini"
        blocker.mkdir()  # 让目标路径是目录 → os.replace 必然失败
        setting = Setting(parent_logger=logging.getLogger("verify"),
                          setting_path=self.tmp / "other.ini", readonly=True)
        setting.setting_path = blocker
        self.assertIs(setting.save_to_file(), False, "失败必须返回 False 供调用方感知")
        self.assertFalse((self.tmp / "setting.ini.tmp").exists(), "失败也不应残留 .tmp")


class SettingsServiceSingletonTest(unittest.TestCase):
    """3：进程级单例 + 路径隔离"""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="xuan_verify_hardening_ss_"))
        ss_mod.reset_settings_cache()

    def tearDown(self):
        ss_mod.reset_settings_cache()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_get_settings_is_process_singleton(self):
        ini = self.tmp / "setting.ini"
        first = ss_mod.get_settings(path=ini)
        second = ss_mod.get_settings(path=self.tmp / "ignored.ini")
        self.assertIs(first, second, "get_settings 必须返回同一实例（含重复传参）")

    def test_service_without_args_uses_singleton(self):
        ini = self.tmp / "setting.ini"
        singleton = ss_mod.get_settings(path=ini)
        svc_a = ss_mod.SettingsService()
        svc_b = ss_mod.SettingsService()
        self.assertIs(svc_a._get_setting(), singleton)
        self.assertIs(svc_b._get_setting(), singleton,
                      "生产路径必须共用唯一 Setting（旧实现每次都新建 → 每次写盘）")

    def test_service_with_path_is_isolated(self):
        """path= 参数不污染单例（测试隔离能力必须保留）"""
        singleton = ss_mod.get_settings(path=self.tmp / "setting.ini")
        other = ss_mod.SettingsService(path=self.tmp / "isolated.ini")
        self.assertIsNot(other._get_setting(), singleton)
        self.assertTrue((self.tmp / "isolated.ini").exists())

    def test_injected_setting_wins(self):
        injected = Setting(parent_logger=logging.getLogger("verify"),
                           setting_path=self.tmp / "injected.ini", readonly=True)
        svc = ss_mod.SettingsService(injected)
        self.assertIs(svc._get_setting(), injected)


class BackgroundLoopHardeningTest(unittest.TestCase):
    """4：后台循环不因配置类型错误静默死亡"""

    class _FakeConfig:
        def __init__(self, values):
            self._values = values

        def get_config(self, key, default=None):
            return self._values.get(key, default)

    def _scan_scheduler(self, scan_impl, scan_interval):
        from backend.services.scheduler_service import SchedulerService

        sched = object.__new__(SchedulerService)
        sched.running = True
        sched.logger = logging.getLogger("verify_scan_loop")
        sched.config = self._FakeConfig({"扫描间隔": scan_interval})
        sched.task_queue = type("Q", (), {"heap": []})()
        sched.scan = scan_impl
        sched._report_loop_death = lambda name: (
            setattr(sched, "death_reported", name), setattr(sched, "running", False))
        sched.death_reported = None
        return sched

    def test_illegal_scan_interval_does_not_kill_loop(self):
        """扫描间隔='abc'：不得抛异常，循环继续（本轮降级为默认等待）"""
        calls = []

        def scan():
            calls.append(1)
            sched.running = False      # 一轮后退出，避免测试等待

        sched = self._scan_scheduler(scan, "abc")
        sched._scan_loop()             # 旧实现：这里会抛 TypeError 让线程静默死亡
        self.assertEqual(len(calls), 1)
        self.assertIsNone(sched.death_reported)

    def test_fatal_exception_is_reported(self):
        """非 Exception 的致命异常：置停机 + 上报，绝不静默返回"""
        def scan():
            raise KeyboardInterrupt("boom")

        sched = self._scan_scheduler(scan, 1000)
        sched._scan_loop()
        self.assertFalse(sched.running)
        self.assertEqual(sched.death_reported, "扫描循环")

    def test_normal_exception_keeps_loop_alive(self):
        """普通异常只留痕，循环继续（保持既有语义）"""
        calls = []

        def scan():
            calls.append(1)
            if len(calls) >= 2:
                sched.running = False
            raise RuntimeError("transient")

        sched = self._scan_scheduler(scan, 100)
        sched._scan_loop()
        self.assertEqual(len(calls), 2, "普通异常不应终止循环")
        self.assertIsNone(sched.death_reported)

    def test_illegal_watchdog_interval_does_not_kill_loop(self):
        """超时监视器：检测间隔非法时降级默认值，不终止线程"""
        from backend.services.watchdog_service import TimeoutWatchdog

        dog = object.__new__(TimeoutWatchdog)
        dog.logger = logging.getLogger("verify_watchdog_loop")
        dog._running = True
        dog._lock = __import__("threading").Lock()
        dog.config = self._FakeConfig({"超时检测-检测间隔秒": "not-a-number"})

        def check_once():
            dog._running = False       # 一轮后退出

        dog._check_once = check_once
        dog._monitor_loop()            # 旧实现：这里会抛 ValueError 让线程静默死亡
        self.assertFalse(dog._running)


class MiJingTanXianRaiseTest(unittest.TestCase):
    """5：异常消息必须单参数（多参数不报错，但消息会渲染成元组、%d 不展开）

    更正（实测）：`Exception("msg", 3)` **不会**抛 TypeError —— args 是一个元组，
    因此旧实现不会导致"正常完成被误判为未捕获异常"，真实后果只是日志里出现
    `('识别剩余挑战券数量失败（已重试 %d 次）…', 3)` 这类元组文本、`%d` 保持字面量。
    属 P2 日志质量问题，修复后消息为格式化后的单条字符串。
    """

    def test_two_args_render_as_tuple(self):
        from backend.core.legacy.Exceptions import TaskCompleted

        exc = TaskCompleted("已重试 %d 次", 3)
        rendered = str(exc)
        self.assertNotEqual(rendered, "已重试 %d 次")
        self.assertIn("%d", rendered, "%d 仍是字面量（不会被格式化）")
        self.assertIn("3", rendered)
        self.assertEqual(exc.args, ("已重试 %d 次", 3), "多参数会被塞进 args 元组")

    def test_single_argument_renders_clean_text(self):
        from backend.core.legacy.Exceptions import TaskCompleted

        exc = TaskCompleted("已重试 3 次")
        self.assertEqual(str(exc), "已重试 3 次")

    def test_source_uses_single_argument(self):
        """源码级防回退：所有异常构造都必须单参数（多参数会渲染成元组、%d 不展开）

        `MiJingTanXian` 的 OCR 重试逻辑已重写（`TZQ_OCR_ATTEMPTS` 与旧日志文案均不存在），
        原先按文案断言的检查已失效。这里改为 AST 扫描：不依赖具体文案，任何
        `TaskCompleted(...)` / `StepFailedError(...)` 传入第二个参数都会被捕获。
        """
        import ast

        src = (Path(_PROJECT_ROOT) / "backend" / "core" / "legacy" / "Task"
               / "MiJingTanXian.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        exc_names = {"TaskCompleted", "StepFailedError", "TaskFailedError"}
        offenders = []
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id in exc_names and len(node.args) > 1):
                offenders.append((node.lineno, node.func.id, len(node.args)))
        self.assertEqual(offenders, [],
                         "异常消息必须是单参数字符串（多参数会渲染成元组）")


if __name__ == "__main__":
    unittest.main(verbosity=2)
