# -*- coding: utf-8 -*-
"""阶段 5 回归：「是否启用」收敛为单一写端点

背景（改前）：
- 后端 `PUT /scheduler/tasks/{id}/{name}/activation` 走 `_get_scheduler()` —— **没有调度器
  实例时会创建一个**（注册 logger handler、进注册表、构造 planner/executor）。
- 于是前端为了"调度器没运行时也能保存"又额外调了 `PUT /configs/{id}/task/{name}`：
  同一状态两个写入口，且勾一下复选框就让配置常驻一个调度器对象。

改后：
- 端点用 `peek_scheduler()`：有实例 → 交给它同步队列/快照（其内部也写配置）；
  没有实例 → 只写配置并返回 `{"ok": True, "synced": False}`；
- 前端 `TaskConfigPanel.updateTaskField` 对 `是否启用` 只调 `schedulerApi.toggleActivation`，
  其余字段仍走 `configApi.updateTask`。

覆盖：后端"不创建实例/会落盘/404"、有实例时委托、源码级防回退（前后端各一条）。
"""
import logging
import sys
import unittest
from pathlib import Path
from unittest import mock

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT))


def _strip_python_comments_and_docstrings(code: str) -> str:
    """去掉 # 注释与三引号文档字符串（否则"说明里提到的旧写法"会误判为代码）"""
    parts = code.split('"""')
    code = "".join(parts[i] for i in range(0, len(parts), 2))
    return "\n".join(line.split("#", 1)[0] for line in code.splitlines())


def _strip_ts_comments(code: str) -> str:
    """去掉 // 行注释（同理：注释里提到 configApi 不代表真的调用）"""
    return "\n".join(line.split("//", 1)[0] for line in code.splitlines())


class ActivationEndpointTest(unittest.TestCase):
    """真实配置零写入：用替身 Config / 替身 scheduler 验证行为"""

    def setUp(self):
        from backend.api import scheduler as scheduler_api
        self.api = scheduler_api
        self.writes = {}

    def _fake_config_patch(self):
        api = self.api
        writes = self.writes

        class _FakeConfig:
            def set_task_base_config(self, task_name, key, value):
                writes[(task_name, key)] = value

        original = api._config_service.get_config
        patcher = mock.patch.object(
            api._config_service, "get_config",
            side_effect=lambda cid: _FakeConfig() if cid == "Temp" else original(cid))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_no_instance_does_not_create_scheduler_and_persists(self):
        import backend.api.scheduler as api
        self._fake_config_patch()
        before = dict(api._schedulers)
        result = api.toggle_task_activation("Temp", "任务A", True)
        self.assertEqual(result, {"ok": True, "synced": False})
        self.assertEqual(self.writes, {("任务A", "是否启用"): True},
                         "无实例时也必须落盘")
        self.assertEqual(dict(api._schedulers), before,
                         "不得因为没有实例而创建一个调度器")

    def test_missing_config_raises_404(self):
        from fastapi import HTTPException
        import backend.api.scheduler as api
        self._fake_config_patch()
        with self.assertRaises(HTTPException) as ctx:
            api.toggle_task_activation("不存在的配置", "任务A", True)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_running_instance_is_delegated(self):
        import backend.api.scheduler as api
        calls = []

        class _FakeScheduler:
            def toggle_task_activation(self, task_name, state):
                calls.append((task_name, state))

        with mock.patch.object(api, "peek_scheduler", return_value=_FakeScheduler()):
            result = api.toggle_task_activation("Config_x", "任务A", False)
        self.assertEqual(result, {"ok": True, "synced": True})
        self.assertEqual(calls, [("任务A", False)], "有实例时必须委托它同步队列/快照")

    def test_endpoint_source_uses_peek(self):
        src = (_PROJECT_ROOT / "backend" / "api" / "scheduler.py").read_text(
            encoding="utf-8")
        start = src.index("def toggle_task_activation")
        body = _strip_python_comments_and_docstrings(src[start:start + 1200])
        self.assertIn("peek_scheduler(", body)
        self.assertNotIn("_get_scheduler(", body,
                         "「是否启用」写端点不得再走会创建实例的 _get_scheduler")


class FrontendSingleWriteTest(unittest.TestCase):

    def setUp(self):
        self.src = (_PROJECT_ROOT / "frontend" / "src" / "components"
                    / "TaskConfigPanel.vue").read_text(encoding="utf-8")
        start = self.src.index("function updateTaskField")
        end = self.src.index("\nfunction ", start + 10)
        self.body = _strip_ts_comments(self.src[start:end])

    def test_enable_branch_returns_before_config_write(self):
        branch = self.body.index("if (field === '是否启用')")
        config_write = self.body.index("configApi")
        between = self.body[branch:config_write]
        self.assertIn("toggleActivation", between,
                      "「是否启用」分支必须调 toggleActivation（单一写端点）")
        self.assertIn("return", between,
                      "「是否启用」分支必须在 configApi 写入之前 return（否则又是双写）")

    def test_other_fields_still_write_config(self):
        self.assertIn("configApi", self.body, "其它字段仍需写配置文件")
        self.assertEqual(self.body.count("toggleActivation"), 1,
                         "启用状态只应有唯一一次写调用")
        self.assertEqual(self.body.count("configApi"), 1)

    def test_enable_single_write_keeps_error_logging(self):
        self.assertIn("errorMessage(e)", self.body,
                      "写入失败必须提示用户（不得静默吞掉）")


if __name__ == "__main__":
    unittest.main(verbosity=2)
