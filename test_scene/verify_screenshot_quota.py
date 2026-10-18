# -*- coding: utf-8 -*-
"""验证「每日截图上限」：配额清理、重复画面跳过、超限提醒与前端弹窗接线。

需求（2026-09-17，用户确认方案 A + C，见 memory-bank/activeContext.md）：
- R1/R2：每个配置**当天**日志文件夹 ``log/<用户名>/<日期>/screenshot`` 内最多保留 X 张
  自动截图，超出删除最早的（保留最新 X 张）；
- R3/R4：本次运行截图超过 X 张 → 弹窗提醒关闭日志面板右上角「截图」开关，弹窗只能手动关闭；
- R5：X 放全局设置 ``[助手设置] 每日截图上限``，默认 100、最小 100；
- R6：忘关截图时尽量少读写（内存索引 + 批量删除 + 完全相同画面跳过），但不得影响截图主流程。

覆盖：
1. `normalize_daily_limit` / `get_daily_limit`：默认值、最小值夹取、非法值回退；
2. `ScreenshotQuota`：删最早保留最新、批量一次删完、只扫一次目录、跨天重建、
   用户手动截图不统计不删除、删除失败容错、目录外文件跳过、并发无重复删除；
3. `ScreenshotGuard`：完全相同画面跳过写盘、不同画面照常保存、错误截图永不跳过、
   本次运行计数、超限只提醒一次、`reset_run` 复位；
4. `SchedulerService` 接线：真实 `_save_screenshot` 端到端（配额 + 计数 + 提醒 + 跳过）；
5. 前端接线（源码断言）：弹窗不可自动关闭、协议映射、Layout 订阅、设置页最小 100。
"""
import json
import logging
import os
import sys
import tempfile
import threading
import unittest
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

import numpy as np  # noqa: E402

from backend.services.screenshot_quota import (  # noqa: E402
    DEFAULT_DAILY_LIMIT,
    MIN_DAILY_LIMIT,
    ScreenshotQuota,
    get_daily_limit,
    normalize_daily_limit,
)
from backend.services.scheduler.screenshot_guard import (  # noqa: E402
    ScreenshotGuard,
    WS_EVENT_SCREENSHOT_LIMIT,
    frame_digest,
)

LOG = "verify_screenshot_quota"
logger = logging.getLogger(LOG)

FRONTEND = Path(_PROJECT_ROOT) / "frontend" / "src"


def _img(value=5, shape=(16, 16, 3)):
    """构造一张可控内容的 BGR 图（整幅同值便于制造"完全一致"的帧）"""
    return np.full(shape, value, dtype=np.uint8)


def _write_shot(directory: Path, name: str, *, value: int = 5,
                shape=(16, 16, 3), mtime_ns: int = None) -> Path:
    """在 directory 写一张真实 PNG（用于配额/指纹相关的文件级验证）"""
    import cv2
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    arr = _img(value, shape)
    cv2.imencode(".png", arr)[1].tofile(str(path))
    if mtime_ns is not None:
        os.utime(path, ns=(mtime_ns, mtime_ns))
    return path


class _FakeSettings:
    """SettingsService 替身：只实现 `get(section, key)`"""

    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    def get(self, section, key):
        if self.error is not None:
            raise self.error
        return self.value


# --------------------------------------------------------------------------- #
#                    1. 上限读取与夹取（R5）                                    #
# --------------------------------------------------------------------------- #
class DailyLimitTest(unittest.TestCase):
    def test_default_and_min_clamp(self):
        self.assertEqual(normalize_daily_limit(None), DEFAULT_DAILY_LIMIT)
        self.assertEqual(normalize_daily_limit(""), DEFAULT_DAILY_LIMIT)
        self.assertEqual(normalize_daily_limit("abc"), DEFAULT_DAILY_LIMIT)
        self.assertEqual(normalize_daily_limit(0), MIN_DAILY_LIMIT)
        self.assertEqual(normalize_daily_limit(5), MIN_DAILY_LIMIT)
        self.assertEqual(normalize_daily_limit("99"), MIN_DAILY_LIMIT)
        self.assertEqual(normalize_daily_limit(100), 100)
        self.assertEqual(normalize_daily_limit("250"), 250)
        self.assertEqual(DEFAULT_DAILY_LIMIT, 100)
        self.assertEqual(MIN_DAILY_LIMIT, 100)

    def test_get_daily_limit_uses_settings(self):
        self.assertEqual(get_daily_limit(_FakeSettings("150")), 150)
        self.assertEqual(get_daily_limit(_FakeSettings(None)), DEFAULT_DAILY_LIMIT)
        self.assertEqual(get_daily_limit(_FakeSettings("3")), MIN_DAILY_LIMIT)

    def test_get_daily_limit_falls_back_on_error(self):
        """读取失败不得抛异常（截图主流程优先），按默认值处理"""
        self.assertEqual(get_daily_limit(_FakeSettings(error=RuntimeError("boom"))),
                         DEFAULT_DAILY_LIMIT)

    def test_default_setting_ini_declares_key(self):
        ini = Path(_PROJECT_ROOT) / "src" / "DefaultSetting.ini"
        text = ini.read_text(encoding="utf-8")
        self.assertIn("每日截图上限", text)
        self.assertIn("每日截图上限 = 100", text)


# --------------------------------------------------------------------------- #
#                    2. 配额清理（R1/R2/R6）                                    #
# --------------------------------------------------------------------------- #
class QuotaTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="xuan_quota_")
        self.root = Path(self.tmp.name) / "screenshot"
        self.quota = ScreenshotQuota(self.root, logger)
        self.base = 1_700_000_000_000_000_000  # 固定基准时间戳（ns）

    def tearDown(self):
        self.tmp.cleanup()

    # ---- 索引 ----

    def test_index_excludes_user_screenshots_and_non_png(self):
        _write_shot(self.root / "任务A", "a1.png")
        _write_shot(self.root / "用户截图", "manual.png")
        (self.root / "任务A" / "note.txt").write_text("x", encoding="utf-8")
        self.assertEqual(self.quota.build_index(), 1, "只应索引自动截图 *.png")
        self.assertEqual(self.quota.count(), 1)

    def test_index_scanned_only_once(self):
        _write_shot(self.root / "任务A", "a1.png")
        _write_shot(self.root / "任务A", "a2.png")
        self.quota.build_index()
        self.assertEqual(self.quota.scan_count, 1)
        self.quota.build_index()
        self.assertEqual(self.quota.scan_count, 1, "已构建的索引不应重复扫目录")
        self.assertEqual(self.quota.count(), 2)

    def test_concurrent_index_build_scans_once(self):
        for i in range(5):
            _write_shot(self.root / "任务A", f"a{i}.png")
        results = []
        threads = [threading.Thread(target=lambda: results.append(self.quota.build_index()))
                   for _ in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(self.quota.scan_count, 1, "并发构建只允许扫一次目录")
        self.assertTrue(all(r == 5 for r in results))

    # ---- 清理 ----

    def test_prune_keeps_newest_limit_files(self):
        names = [f"20240101_00000{i}.png" for i in range(4)]
        paths = [_write_shot(self.root / "任务A", n, value=i, mtime_ns=self.base + i)
                 for i, n in enumerate(names)]
        # 模拟"刚写入的新图"：全新路径 + 最新 mtime（生产路径必然如此）
        newest = _write_shot(self.root / "任务A", "20240101_000009.png", value=9,
                             mtime_ns=self.base + 100)
        # 绕过最小 100 的夹取，直接用内部方法验证"删最早、保留最新"（见
        # test_prune_batches_in_single_call 的同一约定）
        self.quota.build_index()
        result = self.quota._prune_locked(newest.resolve(), 2)
        self.assertEqual(result.deleted, 3, "5 张、上限 2 → 一次删掉最早的 3 张")
        self.assertEqual(result.total, 2)
        left = sorted(p.name for p in (self.root / "任务A").glob("*.png"))
        self.assertEqual(left, [names[3], newest.name], "必须删除最早的，保留最新的 2 张")
        self.assertTrue(newest.exists(), "刚写入的最新截图不得被删")

    def test_prune_normalizes_limit_to_minimum(self):
        """公开入口 `prune` 会把上限夹到最小值 100（设置侧的最小值约束）"""
        for i in range(5):
            _write_shot(self.root / "任务A", f"a{i}.png", value=i, mtime_ns=self.base + i)
        result = self.quota.prune(self.root / "任务A" / "a4.png", 1)
        self.assertEqual(result.deleted, 0, "夹取到 100 后 5 张不超限")
        self.assertEqual(result.total, 5)

    def test_prune_batches_in_single_call(self):
        """一次 prune 把所有超出项删完，且返回删除数（不是每保存一张删一张）"""
        names = [f"20240101_0001{i:02d}.png" for i in range(12)]
        paths = [_write_shot(self.root / "任务A", n, value=i, mtime_ns=self.base + i)
                 for i, n in enumerate(names)]
        newest = _write_shot(self.root / "任务A", "20240101_000199.png", value=99,
                             mtime_ns=self.base + 1000)
        # 绕过最小 100 的夹取：直接用内部方法验证"一次删完"
        self.quota.build_index()
        result = self.quota._prune_locked(newest.resolve(), 5)
        self.assertEqual(result.deleted, 8, "13 张、上限 5 → 一次删掉最早的 8 张")
        self.assertEqual(result.total, 5)
        left = sorted(p.name for p in (self.root / "任务A").glob("*.png"))
        self.assertEqual(left, names[-4:] + [newest.name])
        self.assertEqual(self.quota.prune_calls, 1)

    def test_user_screenshots_never_counted_or_deleted(self):
        (self.root / "用户截图").mkdir(parents=True)
        manual = []
        for i in range(3):
            p = self.root / "用户截图" / f"manual{i}.png"
            p.write_bytes(b"not-a-real-png")
            os.utime(p, ns=(self.base + i, self.base + i))
            manual.append(p)
        auto = [_write_shot(self.root / "任务A", f"a{i}.png", value=i,
                            mtime_ns=self.base + i) for i in range(2)]
        self.quota.build_index()
        self.assertEqual(self.quota.count(), 2, "用户手动截图不计入配额")
        result = self.quota.prune(auto[1], 100)
        self.assertEqual(result.deleted, 0)
        self.assertTrue(all(p.exists() for p in manual), "用户手动截图不得被删除")

    def test_prune_skips_user_dir_and_out_of_scope(self):
        (self.root / "用户截图").mkdir(parents=True)
        manual = self.root / "用户截图" / "m.png"
        manual.write_bytes(b"x")
        res = self.quota.prune(manual, 100)
        self.assertTrue(res.skipped)
        outside = Path(self.tmp.name) / "other" / "任务A" / "a.png"
        outside.parent.mkdir(parents=True)
        outside.write_bytes(b"x")
        self.assertTrue(self.quota.prune(outside, 100).skipped)

    def test_delete_failure_is_tolerated(self):
        """单个文件删除失败：只告警、继续处理，且失败项保留在索引中（截图主流程不受影响）"""
        paths = [_write_shot(self.root / "任务A", f"a{i}.png", value=i,
                             mtime_ns=self.base + i) for i in range(3)]
        newest = _write_shot(self.root / "任务A", "a_new.png", value=9,
                             mtime_ns=self.base + 100)
        real_remove = os.remove

        def fake_remove(target):
            if str(target) == str(paths[0]):
                raise OSError("locked")
            return real_remove(target)

        # 上限 100 时 4 张不会触发删除；用内部方法直接构造"超限"场景（上限 2）
        self.quota.build_index()
        self.quota.logger = logger
        os.remove = fake_remove
        try:
            with self.assertLogs(LOG, level=logging.WARNING) as cm:
                result = self.quota._prune_locked(newest.resolve(), 2)
        finally:
            os.remove = real_remove
        self.assertIn("删除最早截图失败", "\n".join(cm.output))
        self.assertEqual(result.deleted, 1, "失败 1 张只算删除成功的那张")
        self.assertTrue(paths[0].exists(), "删除失败的文件必须保留")
        self.assertTrue(paths[1].exists() is False, "其余最早截图应正常删除")
        self.assertEqual(self.quota.count(), 3, "失败项保留在索引中（不虚报已清理）")
        self.assertTrue(newest.exists(), "最新截图不得被删")

    def test_new_date_directory_uses_new_index(self):
        """跨天：目录不同 → 重新扫描（M1 只在同一天内复用索引）"""
        day1 = _write_shot(self.root / "任务A", "a1.png")
        q1 = ScreenshotQuota(self.root, logger)
        q1.prune(day1, MIN_DAILY_LIMIT)
        self.assertEqual(q1.scan_count, 1)
        root2 = Path(self.tmp.name) / "screenshot_nextday"
        day2 = _write_shot(root2 / "任务A", "b1.png")
        q2 = ScreenshotQuota(root2, logger)
        q2.prune(day2, MIN_DAILY_LIMIT)
        self.assertEqual(q2.scan_count, 1)
        self.assertEqual(q2.count(), 1)

    def test_reset_index_forces_rescan(self):
        _write_shot(self.root / "任务A", "a1.png")
        self.quota.build_index()
        self.quota.reset_index()
        self.assertEqual(self.quota.count(), 0)
        self.quota.build_index()
        self.assertEqual(self.quota.scan_count, 2, "reset 后应重新扫描")

    def test_stats_shape(self):
        _write_shot(self.root / "任务A", "a1.png")
        self.quota.build_index()
        stats = self.quota.stats()
        self.assertEqual(stats["indexed"], 1)
        self.assertIn("root", stats)


# --------------------------------------------------------------------------- #
#                    3. 运行守卫（R3/R6）                                       #
# --------------------------------------------------------------------------- #
class GuardTest(unittest.TestCase):
    def _guard(self, limit=100, callback=None):
        g = ScreenshotGuard("Config_1", logger, alert_callback=callback)
        g.set_limit(limit)
        return g

    def test_identical_frames_skipped(self):
        g = self._guard()
        a = _img(7)
        b = _img(7)
        self.assertFalse(g.should_skip("任务A", a), "第一张必须保存")
        self.assertTrue(g.should_skip("任务A", b), "与上一张完全相同 → 跳过写盘")
        self.assertEqual(g.skipped_count, 1)
        self.assertFalse(g.should_skip("任务A", _img(8)), "画面变化 → 照常保存")

    def test_different_tasks_do_not_share_digest(self):
        g = self._guard()
        self.assertFalse(g.should_skip("任务A", _img(7)))
        self.assertFalse(g.should_skip("任务B", _img(7)), "不同任务之间不互相跳过")

    def test_error_screenshots_never_skipped(self):
        g = self._guard()
        self.assertFalse(g.should_skip("任务A", _img(7), reason=""))
        self.assertFalse(g.should_skip("任务A", _img(7), reason="StepFailed"),
                         "错误截图即使画面完全相同也必须落盘")
        self.assertFalse(g.should_skip("任务A", _img(7), reason="WatchdogFreeze"))

    def test_frame_digest_sensitivity(self):
        self.assertEqual(frame_digest(_img(7), (16, 16, 3)), frame_digest(_img(7), (16, 16, 3)))
        self.assertNotEqual(frame_digest(_img(7), (16, 16, 3)),
                            frame_digest(_img(7, (16, 16, 4)), (16, 16, 4)),
                            "通道数不同必须区分")
        self.assertNotEqual(frame_digest(_img(7), (16, 16, 3)),
                            frame_digest(_img(7).astype(np.float32), (16, 16, 3)),
                            "dtype 不同必须区分")
        self.assertEqual(frame_digest(None, None), "", "非数组输入返回空指纹（不跳过）")

    def test_run_counter_and_single_alert(self):
        events = []
        g = self._guard(limit=100, callback=events.append)
        for _ in range(100):
            stats = g.note_saved()
            self.assertFalse(g.maybe_alert(run_count=stats["run_count"],
                                           limit=stats["limit"], today_count=100))
        self.assertEqual(events, [], "未超过上限不得提醒")
        stats = g.note_saved()  # 第 101 张 → 第一次超限
        self.assertTrue(g.maybe_alert(run_count=stats["run_count"],
                                      limit=stats["limit"], today_count=100))
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["config_id"], "Config_1")
        self.assertEqual(events[0]["run_count"], 101)
        self.assertEqual(events[0]["limit"], 100)
        self.assertEqual(WS_EVENT_SCREENSHOT_LIMIT, "screenshot.limit")
        stats = g.note_saved()
        self.assertFalse(g.maybe_alert(run_count=stats["run_count"],
                                       limit=stats["limit"], today_count=100),
                         "同一次运行只提醒一次")

    def test_reset_run_reenables_alert(self):
        events = []
        g = self._guard(limit=100, callback=events.append)
        for _ in range(101):
            g.note_saved()
        self.assertTrue(g.maybe_alert(run_count=101, limit=100, today_count=100))
        g.reset_run()
        self.assertEqual(g.run_count, 0)
        self.assertEqual(g.skipped_count, 0)
        self.assertFalse(g.alert_sent)
        for _ in range(101):
            g.note_saved()
        self.assertTrue(g.maybe_alert(run_count=101, limit=100, today_count=100),
                        "新的一次运行应可再次提醒")
        self.assertEqual(len(events), 2)

    def test_alert_callback_failure_does_not_raise(self):
        def boom(_payload):
            raise RuntimeError("ws down")

        g = self._guard(limit=100, callback=boom)
        for _ in range(101):
            g.note_saved()
        with self.assertLogs(LOG, level=logging.WARNING):
            self.assertTrue(g.maybe_alert(run_count=101, limit=100, today_count=101))

    def test_current_limit_reads_setting(self):
        """未注入固定上限时实时读全局设置（改设置立即生效）"""
        import backend.services.settings_service as ss_mod
        from backend.core.setting_model import Setting

        tmp = tempfile.TemporaryDirectory(prefix="xuan_guard_setting_")
        try:
            ini = Path(tmp.name) / "setting.ini"
            ini.write_text("[助手设置]\r\n每日截图上限 = 150\r\n", encoding="utf-8")
            setting = Setting(parent_logger=logging.getLogger(LOG), setting_path=ini)
            orig = ss_mod.SettingsService._get_setting
            ss_mod.SettingsService._get_setting = lambda self: setting
            try:
                g = ScreenshotGuard("Config_1", logger)
                self.assertEqual(g.current_limit(), 150)
                setting.set("助手设置", "每日截图上限", 30)
                self.assertEqual(g.current_limit(), MIN_DAILY_LIMIT, "低于最小值应夹取")
            finally:
                ss_mod.SettingsService._get_setting = orig
        finally:
            tmp.cleanup()


# --------------------------------------------------------------------------- #
#              4. SchedulerService 端到端接线（真实 _save_screenshot）           #
# --------------------------------------------------------------------------- #
class _DeviceStub:
    def __init__(self, frames):
        self.frames = list(frames)

    def screen_cap(self):
        return self.frames.pop(0) if self.frames else None


class ServiceIntegrationTest(unittest.TestCase):
    """真实 SchedulerService._save_screenshot：配额 + 跳过 + 计数 + 提醒"""

    def setUp(self):
        import backend.services.settings_service as ss_mod
        from backend.core.setting_model import Setting
        from backend.core.config_model import Config
        from backend.services.scheduler_service import SchedulerService

        self.tmp = tempfile.TemporaryDirectory(prefix="xuan_shot_service_")
        self.dir = Path(self.tmp.name)
        self.ini = self.dir / "setting.ini"
        self.ini.write_text(
            "[助手设置]\r\n每日截图上限 = 100\r\n错误自动截图 = True\r\n",
            encoding="utf-8")
        self.setting = Setting(parent_logger=logging.getLogger(LOG),
                               setting_path=self.ini)
        self._ss_mod = ss_mod
        self._orig_get_setting = ss_mod.SettingsService._get_setting
        ss_mod.SettingsService._get_setting = lambda self: self.setting

        # 日志根目录指向临时目录：所有脚本自动截图落在临时目录内（不污染真实 log/）
        import backend.utils as utils_mod
        self._orig_real_path = utils_mod.get_real_path
        utils_mod.get_real_path = lambda *parts: str(self.dir.joinpath(*parts))
        import backend.services.scheduler_service as sched_mod
        self._sched_get_real_path = sched_mod.get_real_path
        sched_mod.get_real_path = lambda *parts: str(self.dir.joinpath(*parts))

        cfg_path = self.dir / "Config_Test.json"
        cfg_path.write_text(json.dumps({
            "配置文件版本": "V3",
            "用户名": "verify_user",
            "配置类型": "持久",
            "保存截图": 1,
            "任务": {},
        }, ensure_ascii=False), encoding="utf-8")
        cfg = Config(parent_logger=logging.getLogger(LOG), config_path=cfg_path)
        self.alerts = []
        self.sched = SchedulerService(config=cfg,
                                      on_screenshot_limit=self.alerts.append)
        # 直接构造真实保存回调（生产路径由 _lazy_init 注入；这里跳过设备初始化）
        self.sched._save_screenshot = self.sched._build_save_screenshot_callback()
        self.screenshot_root = self.dir / "log" / "verify_user" / \
            datetime.now().strftime("%Y-%m-%d") / "screenshot"

    def tearDown(self):
        self._ss_mod.SettingsService._get_setting = self._orig_get_setting
        import backend.utils as utils_mod
        utils_mod.get_real_path = self._orig_real_path
        import backend.services.scheduler_service as sched_mod
        sched_mod.get_real_path = self._sched_get_real_path
        # Windows 上日志文件仍被 handler 持有 → 不摘除会 PermissionError 导致临时目录清理失败
        try:
            from backend.log_setup import get_config_file_handler
            handler = get_config_file_handler("verify_user")
            if handler is not None:
                handler.close()
                self.sched.logger.removeHandler(handler)
                self.sched.config.logger.removeHandler(handler)
        except Exception:
            pass
        self.tmp.cleanup()

    def _set_device(self, frames):
        self.sched.device = _DeviceStub(frames)

    def _count_files(self):
        return len(list(self.screenshot_root.glob("*/*.png")))

    def test_save_prunes_to_limit_and_skips_duplicates(self):
        """老图 3 张 + 3 帧（重复、变化、重复）→ 上限 100 不删；同帧跳过不落盘"""
        task_dir = self.screenshot_root / "任务A"
        for i in range(3):
            _write_shot(task_dir, f"old{i}.png", value=i)
        self._set_device([_img(7), _img(7), _img(9)])
        self.sched._save_screenshot("任务A")
        self.sched._save_screenshot("任务A")
        self.sched._save_screenshot("任务A")
        self.assertEqual(self._count_files(), 5, "3 张老图 + 2 张新图（中间重复帧被跳过）")
        self.assertEqual(self.sched.screenshot_guard.run_count, 2, "跳过的帧不计入本次运行")
        self.assertEqual(self.sched.screenshot_guard.skipped_count, 1)

    def test_limit_prunes_oldest_and_alerts_once(self):
        """构造"已超限"局面：101 张（超出上限 1 张）→ 删最早的 1 张，保留最新 100 张"""
        task_dir = self.screenshot_root / "任务A"
        for i in range(101):
            _write_shot(task_dir, f"old{i:03d}.png", value=i % 200,
                        mtime_ns=1_700_000_000_000_000_000 + i)
        self.assertEqual(self._count_files(), 101)
        # 以最新的一张（old100）作为"刚写入的截图"触发配额检查
        result = self.sched._enforce_screenshot_quota(
            str(self.screenshot_root), str(task_dir / "old100.png"))
        self.assertEqual(result["deleted"], 1, "超过上限 1 张 → 删除最早的 1 张")
        self.assertEqual(result["total"], 100)
        self.assertEqual(result["limit"], 100)
        self.assertFalse((task_dir / "old000.png").exists(), "最早的截图应被删除")
        self.assertTrue((task_dir / "old100.png").exists(), "刚写入的最新截图必须保留")

    def test_run_counter_and_alert_end_to_end(self):
        """真实保存 101 张（上限 100）→ 第 101 张触发一次提醒（每个配置每次运行一次）"""
        self.sched.screenshot_guard.set_limit(100)
        frames = [_img(1 + (i % 50)) for i in range(110)]
        self._set_device(frames)
        for _ in range(101):
            self.sched._save_screenshot("任务A")
        self.assertEqual(self.sched.screenshot_guard.run_count, 101)
        self.assertEqual(len(self.alerts), 1, "超限提醒只广播一次")
        self.assertEqual(self.alerts[0]["config_id"], "Config_Test")
        self.assertEqual(self.alerts[0]["limit"], 100)
        self.assertEqual(self.alerts[0]["run_count"], 101)
        self.assertLessEqual(self.alerts[0]["today_count"], 100, "今日截图数不超过上限")

    def test_error_screenshot_not_skipped(self):
        self._set_device([_img(7), _img(7)])
        self.sched._save_screenshot("任务A")
        self.sched._save_screenshot("任务A", "StepFailed")
        self.assertEqual(self._count_files(), 2, "错误截图即使画面相同也必须落盘")
        self.assertEqual(self.sched.screenshot_guard.run_count, 2)

    def test_quota_cache_reuse_and_eviction(self):
        q = self.sched._quota_for(str(self.screenshot_root))
        self.assertIs(q, self.sched._quota_for(str(self.screenshot_root)),
                      "同目录应复用配额实例（内存索引得以复用）")
        other1 = self.sched._quota_for(str(self.dir / "log" / "u1" / "d1" / "screenshot"))
        other2 = self.sched._quota_for(str(self.dir / "log" / "u2" / "d2" / "screenshot"))
        self.assertIsNot(q, other1)
        self.assertLessEqual(len(self.sched._quota_cache), 2, "缓存只保留最近的两个目录")

    def test_save_disabled_switch_blocks_saving(self):
        self.sched.config.set_config("保存截图", 0)
        self._set_device([_img(7)])
        self.sched._save_screenshot("任务A")
        self.assertEqual(self._count_files(), 0, "开关关闭时不得写盘")
        # 错误截图由「错误自动截图」控制，与「保存截图」独立
        self._set_device([_img(7)])
        self.sched._save_screenshot("任务A", "StepFailed")
        self.assertEqual(self._count_files(), 1)

    def test_same_millisecond_screenshot_does_not_overwrite(self):
        """同一毫秒内的第二张截图必须换名保存（快机器/CI 上曾经互相覆盖）"""
        import backend.services.scheduler_service as sched_mod

        d = Path(self.tmp.name) / "same_ms"
        d.mkdir()
        first = d / "20240101_000000_000.png"
        first.write_bytes(b"first")
        second = sched_mod.SchedulerService._unique_screenshot_path(str(first))
        self.assertNotEqual(second, str(first))
        self.assertTrue(second.endswith("_1.png"), second)
        Path(second).write_bytes(b"second")
        third = sched_mod.SchedulerService._unique_screenshot_path(str(first))
        self.assertTrue(third.endswith("_2.png"), third)
        self.assertEqual(first.read_bytes(), b"first", "原文件绝不能被覆盖")

    def test_source_wiring(self):
        """源码接线防回退：配额/计数/提醒/跳过四处调用点必须在位"""
        src = (Path(_PROJECT_ROOT) / "backend" / "services" /
               "scheduler_service.py").read_text(encoding="utf-8")
        self.assertIn("self.screenshot_guard.reset_run()", src)
        self.assertIn("self.screenshot_guard.should_skip(", src)
        self.assertIn("self._enforce_screenshot_quota(screenshot_root, filepath)", src)
        self.assertIn("quota.prune(filepath, limit)", src)
        self.assertIn("self._unique_screenshot_path(filepath)", src)
        self.assertIn("_save_screenshot = self._build_save_screenshot_callback()", src)
        api_src = (Path(_PROJECT_ROOT) / "backend" / "api" /
                   "scheduler.py").read_text(encoding="utf-8")
        self.assertIn("on_screenshot_limit=sync_on_screenshot_limit", api_src)
        self.assertIn('"screenshot.limit"', api_src)


# --------------------------------------------------------------------------- #
#                    5. 前端接线（R3/R4/R5）                                    #
# --------------------------------------------------------------------------- #
class FrontendWiringTest(unittest.TestCase):
    def _read(self, *parts) -> str:
        return (FRONTEND.joinpath(*parts)).read_text(encoding="utf-8")

    def test_dialog_cannot_close_automatically(self):
        src = self._read("components", "ScreenshotLimitDialog.vue")
        self.assertIn(':mask-closable="false"', src, "遮罩点击不得关闭")
        self.assertIn(':closable="false"', src, "不得出现右上角关闭叉")
        self.assertIn(':close-on-esc="false"', src, "Esc 不得关闭")
        self.assertNotIn("setTimeout", src, "不得有自动消失/倒计时")
        self.assertNotIn("setInterval", src, "不得有自动消失/倒计时")
        self.assertIn("我知道了", src, "唯一出口：用户手动点按钮")
        self.assertIn("一键关闭该配置的截图开关", src)
        self.assertIn("updateSetting(c.config_id, '保存截图', 0)", src)
        self.assertIn("日志面板右上角", src, "文案必须指向日志面板右上角的截图开关")

    def test_dialog_renders_backend_payload(self):
        src = self._read("components", "ScreenshotLimitDialog.vue")
        for field in ("run_count", "limit", "today_count"):
            self.assertIn(field, src)

    def test_protocol_maps_event(self):
        src = self._read("api", "ws", "protocol.ts")
        self.assertIn("'screenshot.limit': 'screenshot_limit'", src)
        self.assertIn("| 'screenshot_limit'", src)
        api_src = (Path(_PROJECT_ROOT) / "backend" / "api" /
                   "scheduler.py").read_text(encoding="utf-8")
        self.assertIn('"screenshot.limit", data', api_src)

    def test_layout_subscribes_and_mounts_dialog(self):
        src = self._read("views", "Layout.vue")
        self.assertIn("ScreenshotLimitDialog", src)
        self.assertIn('@consume="consumeScreenshotAlert"', src)
        self.assertIn("} = useScreenshotLimitAlerts()", src)
        # WS 订阅与退订必须在 composable 内（Layout 不得再直接 useWebSocket / onBeforeUnmount）
        self.assertNotIn("useWebSocket", src)
        self.assertNotIn("onBeforeUnmount", src)
        comp = self._read("composables", "useScreenshotLimitAlerts.ts")
        self.assertIn("onWsMessage('screenshot_limit', onScreenshotLimit)", comp)
        self.assertIn("onBeforeUnmount", comp, "卸载时必须取消订阅")

    def test_settings_min_limit_and_hint(self):
        src = self._read("views", "Settings.vue")
        self.assertIn("MIN_DAILY_SHOT_LIMIT = 100", src)
        self.assertIn("DAILY_SHOT_LIMIT_KEY = '每日截图上限'", src)
        self.assertIn(":min=\"MIN_DAILY_SHOT_LIMIT\"", src)
        self.assertIn("isDailyShotLimit(section, key)", src)
        self.assertIn("最小 {{ MIN_DAILY_SHOT_LIMIT }}", src, "应有说明文案")


if __name__ == "__main__":
    unittest.main(verbosity=2)
