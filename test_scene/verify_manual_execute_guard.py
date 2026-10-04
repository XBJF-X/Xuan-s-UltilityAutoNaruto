# -*- coding: utf-8 -*-
"""验证「手动立即执行同样受任务排期窗口约束」（2026-09-13，方案 C）。

背景：手动「执行」过去会给任务打上 `force_execute_now` 并**跳过窗口校验**。用户误触窄窗口
任务（天地战场 周三 21:00~21:30、要塞争夺战 周六 20:00~20:30、叛忍来袭…）时，任务会空跑
到最长执行时长（30~45 分钟）、抢占正在运行的任务，还可能级联激活叛忍再来一轮 → 表现为
"调度器卡死，只能关掉再开"。

修复（入口预检 + 强制逃生舱）：
- `SchedulerService.execute_task_now(name, enable_if_needed=False, *, source, ignore_window)`
  返回 `{ok, reason, window_state, schedule}`；
- `source=SOURCE_MANUAL`（默认）且未 `ignore_window` 时先做窗口预检：`已过期`/`未开始` →
  **拒绝且零副作用**（不写下次执行时间、不置 force、不启用），前端据此提示并允许二次确认
  「忽略窗口强制执行」（`ignore_window=True` 放行）；
- `source=SOURCE_ACTIVATION`（跨任务激活）沿用原有守卫，不做这道预检；
- 无 `probe_execute_window` 的旧任务对象 / 探测抛异常 → 不阻断，留痕后按原行为执行。

覆盖（全部离线，不依赖设备/模拟器）：
1. 窗口外（真实 BaseTask 子类的"已过期"排期）→ 拒绝 + 原因/排期回传 + 状态零改动；
2. 窗口内（"始终在窗口内"排期）→ 放行 + force 标记 + 写入下次执行时间；
3. 强制 `ignore_window=True` → 窗口外也放行；
4. `source=SOURCE_ACTIVATION` → 不做预检（窗口外也放行，交由 `_skip_expired_activation`）；
5. 兼容：无 `probe_execute_window` / 探测抛异常 → 按原行为执行并留痕；
6. 任务已禁用 → `ok=False` 且原因可读（顺带把过去静默的"已禁用"暴露给前端）；
7. API 层：`?force=true` 透传为 `ignore_window`，响应体原样返回后端结果；
8. 前端接线：`client.ts` 带 force 参数、`Dashboard.vue` 提示原因 + 二次确认。
"""
import asyncio
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
from backend.core.legacy.Task.schedule import Custom, Window  # noqa: E402
from backend.services.scheduler_service import (  # noqa: E402
    SOURCE_ACTIVATION,
    SchedulerService,
)

_TZ = ZoneInfo("Asia/Shanghai")

# 确定性排期（与真实时钟无关）：用于把"窗口已过期/窗口未开始/窗口内"变成可复现用例
EXPIRED_WINDOW = Custom(
    lambda base, ctx: [Window(base - timedelta(hours=2), base - timedelta(hours=1))],
    cycle=lambda base: base + timedelta(days=1),
    describe_text="测试-始终已过期",
)
OPEN_WINDOW = Custom(
    lambda base, ctx: [Window(base - timedelta(minutes=1), base + timedelta(hours=1))],
    cycle=lambda base: base + timedelta(days=1),
    describe_text="测试-始终在窗口内",
)
FUTURE_WINDOW = Custom(
    lambda base, ctx: [Window(base + timedelta(hours=1), base + timedelta(hours=2))],
    cycle=lambda base: base + timedelta(days=1),
    describe_text="测试-始终未开始",
)


class _ExpiredWindowTask(BaseTask):
    schedule = EXPIRED_WINDOW


class _OpenWindowTask(BaseTask):
    schedule = OPEN_WINDOW


class _FutureWindowTask(BaseTask):
    schedule = FUTURE_WINDOW


class _TaskConfig:
    """最小 Config 替身：启用状态与下次执行时间可读写（记录写入便于断言"零改动"）"""

    def __init__(self, enabled=True, next_ts=0):
        self.base = {"是否启用": enabled, "下次执行时间": next_ts}
        self.config_type = "持久"
        self.writes = []

    def get_task_base_config(self, task_name, key, default=None):
        return self.base.get(key, default)

    def set_task_base_config(self, task_name, key, value):
        self.base[key] = value
        self.writes.append((key, value))

    def get_task_exe_param(self, task_name, param_name, default=None):
        return default

    def get_config(self, key, default=None):
        return default


def _make_task(cls, name="天地战场", enabled=True, next_ts=0):
    """构造只跑排期/调度逻辑的真实任务对象（不执行 __init__，避免设备等重依赖）"""
    task = object.__new__(cls)
    task.task_name = name
    task.logger = logging.getLogger("verify.task")
    task.tz_info = _TZ
    task.config = _TaskConfig(enabled=enabled, next_ts=next_ts)
    task.last_run_time = datetime.now(_TZ)
    task.create_time = datetime.now(_TZ)
    task.__dict__["_bound_schedule"] = type(task).schedule.bind(
        task._build_schedule_context())
    task.current_status = 2
    task.bool_click = False
    task.base_priority = 0
    task.click_priority = 0
    task.force_execute_now = False
    task.is_temp = False
    task.last_execute_error = None
    return task


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


class ManualExecuteGuardTest(unittest.TestCase):
    """`execute_task_now` 的手动窗口预检（真实 BaseTask 排期 + 最小 Config）"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="xuan_verify_manual_")
        ini_path = Path(self.tmp) / "setting.ini"
        ini_path.write_text("[助手设置]\r\n", encoding="utf-8")
        self._orig = _patch_settings(ini_path)
        cfg_path = Path(self.tmp) / "Config_Test.json"
        cfg_path.write_text(json.dumps({
            "配置文件版本": "V3",
            "用户名": "verify_user",
            "配置类型": "持久",
            "任务": {},
        }, ensure_ascii=False), encoding="utf-8")
        from backend.core.config_model import Config
        cfg = Config(parent_logger=logging.getLogger("verify"),
                     config_path=cfg_path)
        self.sched = SchedulerService(config=cfg)
        self.sched.running = True
        self.sched.run_once = False
        self.sched.scan = unittest.mock.Mock()
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
        return task

    # ---- 1. 窗口外拒绝（零副作用） ----

    def test_expired_window_rejected_without_side_effects(self):
        task = self._enqueue(_make_task(_ExpiredWindowTask))
        result = self.sched.execute_task_now(task.task_name)
        self.assertFalse(result["ok"], result)
        self.assertEqual(result["window_state"], "窗口已过期")
        self.assertIn("窗口已过期", result["reason"])
        self.assertEqual(result["schedule"], "测试-始终已过期")
        # 零副作用：不写下次执行时间、不置 force、状态与启用状态不变
        self.assertEqual(task.config.base["下次执行时间"], 0)
        self.assertEqual(task.config.writes, [])
        self.assertFalse(task.force_execute_now)
        self.assertEqual(task.current_status, 2)
        self.assertTrue(task.config.base["是否启用"])
        self.assertTrue(any("手动立即执行被拒绝" in m
                            for m in self.captured.messages))

    def test_not_started_window_rejected(self):
        task = self._enqueue(_make_task(_FutureWindowTask, name="要塞争夺战"))
        result = self.sched.execute_task_now("要塞争夺战")
        self.assertFalse(result["ok"])
        self.assertEqual(result["window_state"], "窗口未开始")
        self.assertFalse(task.force_execute_now)

    # ---- 2. 窗口内放行 ----

    def test_open_window_allows_execute(self):
        task = self._enqueue(_make_task(_OpenWindowTask))
        before = datetime.now(_TZ)
        result = self.sched.execute_task_now(task.task_name)
        self.assertTrue(result["ok"], result)
        self.assertTrue(task.force_execute_now, "放行后应带立即执行标记")
        ts = task.config.base["下次执行时间"]
        self.assertGreaterEqual(ts, int(before.timestamp()) - 1,
                                "下次执行时间应写为当前时刻")
        self.assertEqual(task.config.writes, [("下次执行时间", ts)])

    # ---- 3. 强制忽略窗口（前端二次确认后） ----

    def test_ignore_window_forces_execute(self):
        task = self._enqueue(_make_task(_ExpiredWindowTask))
        result = self.sched.execute_task_now(task.task_name, ignore_window=True)
        self.assertTrue(result["ok"], result)
        self.assertTrue(task.force_execute_now)
        self.assertGreater(task.config.base["下次执行时间"], 0)

    # ---- 4. 跨任务激活不做手动预检 ----

    def test_activation_source_skips_manual_precheck(self):
        task = self._enqueue(_make_task(_ExpiredWindowTask, name="叛忍来袭"))
        result = self.sched.execute_task_now("叛忍来袭", enable_if_needed=True,
                                             source=SOURCE_ACTIVATION)
        self.assertTrue(result["ok"],
                        "跨任务激活走 _skip_expired_activation 守卫，不做手动预检")
        self.assertTrue(task.force_execute_now)

    # ---- 5. 兼容分支 ----

    def test_task_without_probe_passes(self):
        """旧任务对象没有 probe_execute_window → 不阻断（保持向后兼容）"""

        class _Legacy:
            def __init__(self, name):
                self.task_name = name
                self.current_status = 2
                self.is_activated = True
                self.is_temp = False
                self.force_execute_now = False
                self.calls = 0

            def schedule_execute_now(self):
                self.calls += 1
                return True, None

            def __lt__(self, other):
                return self.task_name < other.task_name

        task = self._enqueue(_Legacy("无探针任务"))
        result = self.sched.execute_task_now("无探针任务")
        self.assertTrue(result["ok"])
        self.assertEqual(task.calls, 1)
        self.assertTrue(task.force_execute_now)

    def test_probe_error_falls_back_to_execute(self):
        task = self._enqueue(_make_task(_ExpiredWindowTask))
        with unittest.mock.patch.object(task, "probe_execute_window",
                                        side_effect=ValueError("排期异常")):
            result = self.sched.execute_task_now(task.task_name)
        self.assertTrue(result["ok"])
        self.assertTrue(task.force_execute_now)
        self.assertTrue(any("探测" in m and "失败" in m
                            for m in self.captured.messages))

    # ---- 6. 可读的失败原因 ----

    def test_disabled_task_reports_reason(self):
        task = self._enqueue(_make_task(_OpenWindowTask, enabled=False))
        result = self.sched.execute_task_now(task.task_name)
        self.assertFalse(result["ok"])
        self.assertIn("已禁用", result["reason"])
        self.assertFalse(task.force_execute_now)

    def test_missing_task_reports_reason(self):
        result = self.sched.execute_task_now("不存在的任务")
        self.assertFalse(result["ok"])
        self.assertIn("不存在", result["reason"])


class _RecordingScheduler:
    """API 层替身：记录 execute_task_now 的调用参数并返回预设结果"""

    def __init__(self, result=None):
        self.calls = []
        self.result = result or {"ok": True, "reason": None,
                                 "window_state": None, "schedule": None}

    def execute_task_now(self, task_name, ignore_window=False):
        self.calls.append((task_name, ignore_window))
        if ignore_window:
            # 用户强制忽略窗口 → 后端放行（前端二次确认后走这条）
            return {"ok": True, "reason": None, "window_state": None,
                    "schedule": None}
        return self.result


class ExecuteApiTest(unittest.TestCase):
    """`POST /scheduler/tasks/{cid}/{task}/execute` 的 force 透传与响应体"""

    def test_force_flag_forwarded_and_result_returned(self):
        import backend.api.scheduler as api_mod
        rejected = {"ok": False, "reason": "窗口已过期，当前不在可执行窗口内",
                    "window_state": "窗口已过期", "schedule": "每周三 21:00 起"}
        fake = _RecordingScheduler(rejected)
        orig = api_mod._get_scheduler
        api_mod._get_scheduler = lambda config_id: fake
        try:
            # execute_task 现为**同步**端点（FastAPI 线程池执行，避免阻塞事件循环），
            # 不能再 asyncio.run（会抛 "a coroutine was expected"）
            rejected_resp = api_mod.execute_task("Config_1", "天地战场")
            forced_resp = api_mod.execute_task("Config_1", "天地战场", force=True)
        finally:
            api_mod._get_scheduler = orig
        self.assertEqual(fake.calls, [("天地战场", False), ("天地战场", True)],
                         "force 应透传为 ignore_window")
        self.assertFalse(rejected_resp["ok"])
        self.assertEqual(rejected_resp["window_state"], "窗口已过期")
        self.assertTrue(forced_resp["ok"])


class FrontendWiringTest(unittest.TestCase):
    """前端接线（源码级，零运行成本）"""

    @staticmethod
    def _read(rel: str) -> str:
        with open(os.path.join(_PROJECT_ROOT, rel), encoding="utf-8") as f:
            return f.read()

    def test_client_forwards_force(self):
        # 阶段 5：端点对象已拆到 frontend/src/api/endpoints/（client.ts 只做 barrel），
        # 断言读整个 api 层，保持"前端确实带 force 参数"的验证意图
        api_dir = os.path.join(_PROJECT_ROOT, "frontend", "src", "api")
        parts = [self._read(os.path.join("frontend", "src", "api", "client.ts"))]
        endpoints = os.path.join(api_dir, "endpoints")
        if os.path.isdir(endpoints):
            for name in sorted(os.listdir(endpoints)):
                if name.endswith(".ts"):
                    parts.append(self._read(os.path.join("frontend", "src", "api",
                                                         "endpoints", name)))
        src = "\n".join(parts)
        self.assertIn("force = false", src)
        self.assertIn("?force=true", src)

    def test_dashboard_prompts_and_confirms_force(self):
        src = self._read(os.path.join("frontend", "src", "views", "Dashboard.vue"))
        self.assertIn("useMessage", src)
        self.assertIn("useDialog", src)
        self.assertIn("FORCEABLE_WINDOW_STATES", src)
        self.assertIn("data.ok !== false", src)
        self.assertIn("handleExecuteNow(taskName, true)", src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
