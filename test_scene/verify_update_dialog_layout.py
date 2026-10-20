# -*- coding: utf-8 -*-
"""更新弹窗布局优化回归（纯离线：不联网、不需要设备/模型）。

覆盖：
1. 后端 ``_commit_payload``：``message`` 取首行、``full_message`` 保留完整提交消息
2. ``check_update`` 返回的提交历史带 ``full_message``（前端悬浮提示数据源）
3. 前端：宽度随窗口拉伸、提交项悬浮完整消息、回滚包融合进提交列表、
   列表最多 50 行、断网（info 为空）时回滚入口仍可见
"""
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from backend.services import update_service as us  # noqa: E402

UPDATE_DIALOG = _PROJECT_ROOT / "frontend" / "src" / "components" / "UpdateDialog.vue"
MESSAGE = "feat(update): 更新窗口布局优化\n\n- 第一行说明\n- 第二行说明"


class _FakeResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self.content = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8")


class CommitPayloadTest(unittest.TestCase):
    def test_first_line_and_full_message(self):
        payload = us._commit_payload({
            "sha": "a" * 40,
            "commit": {
                "message": MESSAGE,
                "committer": {"date": "2026-10-20T00:00:00Z"},
                "author": {"name": "tester"},
            },
        })
        self.assertEqual(payload["message"], "feat(update): 更新窗口布局优化")
        self.assertEqual(payload["full_message"], MESSAGE)
        self.assertEqual(payload["short_sha"], "a" * 7)
        self.assertEqual(payload["author"], "tester")

    def test_missing_fields_tolerated(self):
        payload = us._commit_payload({"sha": "b" * 40, "commit": {}})
        self.assertEqual(payload["message"], "")
        self.assertEqual(payload["full_message"], "")
        self.assertEqual(payload["date"], "")

    def test_check_update_returns_full_message(self):
        def fake_get(url, **kwargs):
            if "/branches/" in url:
                return _FakeResponse(200, {"commit": {
                    "sha": "b" * 40, "commit": {"message": MESSAGE}}})
            if url.endswith("/commits"):
                return _FakeResponse(200, [{
                    "sha": "b" * 40,
                    "commit": {"message": MESSAGE,
                               "committer": {"date": "2026-10-20T00:00:00Z"},
                               "author": {"name": "tester"}},
                }])
            return _FakeResponse(404)

        with mock.patch.object(us, "select_platforms",
                               return_value=[us.PLATFORM_GITHUB]), \
                mock.patch.object(us, "read_local_sha", return_value="a" * 40), \
                mock.patch.object(us, "read_client_version", return_value="0.17.83"), \
                mock.patch.object(us, "check_full_update",
                                  return_value={"ok": True, "has_update": False,
                                                "asset": None}), \
                mock.patch.object(us.requests, "get", side_effect=fake_get):
            res = us.check_update()
        self.assertTrue(res["ok"], res)
        self.assertEqual(res["commits"][0]["message"], "feat(update): 更新窗口布局优化")
        self.assertEqual(res["commits"][0]["full_message"], MESSAGE)


class DialogLayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vue = UPDATE_DIALOG.read_text(encoding="utf-8")

    def test_width_follows_window(self):
        self.assertIn('style="width: min(1400px, calc(100vw - 32px))"', self.vue,
                      "弹窗宽度应随程序窗口拉伸（小窗口保留边距）")
        self.assertNotIn("width: min(640px", self.vue,
                         "不再使用固定 640px 宽度")

    def test_commit_tooltip_shows_full_message(self):
        self.assertIn("<n-tooltip", self.vue)
        self.assertIn("c.full_message || c.message", self.vue)
        self.assertIn("maxWidth: '720px'", self.vue)
        self.assertIn("white-space: pre-wrap", self.vue,
                      "完整消息需保留换行（多行提交说明）")

    def test_rollback_packages_merged_into_commit_list(self):
        # 独立的回滚包区块已移除，包作为列表行追加（云端历史未覆盖到的更早提交）
        self.assertNotIn("package-section", self.vue)
        self.assertNotIn("package-item", self.vue)
        self.assertIn("v-for=\"c in commitRows\"", self.vue)
        self.assertIn("v-for=\"p in orphanPackages\"", self.vue)
        self.assertIn("const commitRows = computed", self.vue)
        self.assertIn("const orphanPackages = computed", self.vue)
        # 回滚按钮在提交行内（同一列表），不在独立窗口/区块
        self.assertIn("packageMap.has(c.sha)", self.vue)

    def test_commit_list_limited_to_50_rows(self):
        self.assertIn("--commit-row-h: 28px", self.vue)
        self.assertIn("max-height: calc(var(--commit-row-h) * 50)", self.vue)
        self.assertIn("min-height: var(--commit-row-h)", self.vue)

    def test_rollback_visible_even_without_network(self):
        # 列表区只依赖 loading，不依赖 info/packages 是否为空 → 检查失败时仍能回滚
        self.assertIn('<div v-if="!loading" class="commit-section">', self.vue)
        self.assertIn("本地可用回滚包（离线可用，不依赖网络）", self.vue)


if __name__ == "__main__":
    unittest.main(verbosity=2)
