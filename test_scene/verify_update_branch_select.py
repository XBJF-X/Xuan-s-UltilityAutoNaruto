# -*- coding: utf-8 -*-
"""更新分支自选（默认 v17 + 10 秒确认）回归（纯离线：不联网、不需要设备/模型）。

覆盖：
1. ``normalize_branch``：空值=默认、简单分支名放行、路径分隔符/``..``/``.lock`` 拒绝
2. ``check_update(branch)``：默认 v17、显式 dev 的请求 URL/参数、非法分支不发请求
3. ``start_apply_update``：分支透传到线程、非法分支直接拒绝且不启动线程
4. ``do_apply_update``：zipball 下载地址使用所选分支（不是硬编码 v17）
5. ``write_version_json`` / ``refresh_build_info``：记录本次拉取的分支
6. 路由层参数映射（check-update query / apply-update body）
7. 前端接线：默认 v17、10 秒倒计时、警告文案、check/apply 透传 branch
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from backend.api.utils import update as update_routes  # noqa: E402
from backend.services import rollback_service as rb  # noqa: E402
from backend.services import update_service as us  # noqa: E402

UPDATE_DIALOG = _PROJECT_ROOT / "frontend" / "src" / "components" / "UpdateDialog.vue"
SYSTEM_TS = _PROJECT_ROOT / "frontend" / "src" / "api" / "endpoints" / "system.ts"


class _FakeResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self.content = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8")


class NormalizeBranchTest(unittest.TestCase):
    def test_empty_means_default(self):
        for value in (None, "", "   "):
            with self.subTest(value=value):
                self.assertEqual(us.normalize_branch(value), "",
                                 "空值应表示「未指定」，由调用方回退默认分支")

    def test_simple_names_allowed(self):
        for value in ("v17", "dev", "master", "feature-1", "test_2.0"):
            with self.subTest(value=value):
                self.assertEqual(us.normalize_branch(value), value)

    def test_injection_rejected(self):
        for value in ("../v17", "dev/x", "dev\\x", "dev;rm", "v 17", "中国分支",
                      "dev..x", "dev.lock", "-dev", ".dev"):
            with self.subTest(value=value):
                self.assertIsNone(us.normalize_branch(value),
                                  f"{value!r} 应被拒绝（会拼进请求 URL）")


class CheckUpdateBranchTest(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.saved_status = dict(us.UPDATE_STATUS)

    def tearDown(self):
        us.UPDATE_STATUS.clear()
        us.UPDATE_STATUS.update(self.saved_status)

    def _fake_get(self, url, **kwargs):
        self.calls.append((url, kwargs.get("params")))
        if "/branches/" in url:
            return _FakeResponse(200, {"commit": {
                "sha": "b" * 40, "commit": {"message": "feat: fake"}}})
        if url.endswith("/commits"):
            return _FakeResponse(200, [{
                "sha": "b" * 40,
                "commit": {"message": "feat: fake",
                           "committer": {"date": "2026-10-20T00:00:00Z"},
                           "author": {"name": "tester"}},
            }])
        return _FakeResponse(404)

    def _run_check(self, *args):
        with mock.patch.object(us, "select_platforms",
                               return_value=[us.PLATFORM_GITHUB]), \
                mock.patch.object(us, "read_local_sha", return_value="a" * 40), \
                mock.patch.object(us, "read_client_version", return_value="0.17.82"), \
                mock.patch.object(us, "check_full_update",
                                  return_value={"ok": True, "has_update": False,
                                                "asset": None}), \
                mock.patch.object(us.requests, "get", side_effect=self._fake_get):
            return us.check_update(*args)

    def test_defaults_to_v17(self):
        res = self._run_check()
        self.assertTrue(res["ok"], res)
        self.assertEqual(res["branch"], "v17")
        self.assertTrue(any("/branches/v17" in url for url, _ in self.calls),
                        f"默认应请求 v17：{self.calls}")
        sha_params = [p for url, p in self.calls if url.endswith("/commits")]
        self.assertTrue(sha_params and sha_params[0]["sha"] == "v17",
                        f"提交历史应查 v17：{sha_params}")

    def test_explicit_dev_branch(self):
        res = self._run_check("dev")
        self.assertTrue(res["ok"], res)
        self.assertEqual(res["branch"], "dev")
        self.assertTrue(any("/branches/dev" in url for url, _ in self.calls),
                        f"应请求 dev：{self.calls}")
        self.assertFalse(any("/branches/v17" in url for url, _ in self.calls),
                         "显式 dev 时不应再查 v17")
        sha_params = [p for url, p in self.calls if url.endswith("/commits")]
        self.assertEqual(sha_params[0]["sha"], "dev")

    def test_invalid_branch_rejected_without_request(self):
        res = self._run_check("../../evil")
        self.assertFalse(res["ok"])
        self.assertIn("非法", res["message"])
        self.assertEqual(self.calls, [], "非法分支不得发出任何网络请求")
        self.assertEqual(res["local_version"], "0.17.82",
                         "失败分支也要带 local_version 供弹窗展示")


class ApplyUpdateBranchTest(unittest.TestCase):
    def setUp(self):
        self.saved_status = dict(us.UPDATE_STATUS)

    def tearDown(self):
        us.UPDATE_STATUS.clear()
        us.UPDATE_STATUS.update(self.saved_status)

    def _run_start(self, *args):
        captured = {}

        class _FakeThread:
            def __init__(self, target=None, args=(), daemon=None):
                captured["args"] = args

            def start(self):
                captured["started"] = True

        us.UPDATE_STATUS.update({"running": False})
        with mock.patch.object(us.threading, "Thread", _FakeThread):
            res = us.start_apply_update(*args)
        return res, captured

    def test_branch_passed_to_thread(self):
        res, captured = self._run_start("ABCDEF1", "dev")
        self.assertTrue(res["ok"], res)
        self.assertEqual(res["branch"], "dev")
        self.assertEqual(captured["args"], ("abcdef1", "dev"))
        self.assertTrue(captured.get("started"))
        self.assertEqual(us.UPDATE_STATUS["branch"], "dev")

    def test_default_branch_recorded(self):
        res, captured = self._run_start()
        self.assertTrue(res["ok"], res)
        self.assertEqual(captured["args"], (None, "v17"))

    def test_invalid_branch_rejected(self):
        us.UPDATE_STATUS.update({"running": False})
        with mock.patch.object(us.threading, "Thread") as thread_cls:
            res = us.start_apply_update(None, "dev/x")
        self.assertFalse(res["ok"])
        self.assertIn("非法", res["message"])
        thread_cls.assert_not_called()
        self.assertFalse(us.UPDATE_STATUS["running"])


class DownloadUrlBranchTest(unittest.TestCase):
    def setUp(self):
        self.saved_status = dict(us.UPDATE_STATUS)

    def tearDown(self):
        us.UPDATE_STATUS.clear()
        us.UPDATE_STATUS.update(self.saved_status)

    def test_zipball_uses_selected_branch(self):
        with tempfile.TemporaryDirectory() as td, \
                mock.patch.object(us, "get_real_path", return_value=td), \
                mock.patch.object(us, "select_platforms",
                                  return_value=[us.PLATFORM_GITHUB]), \
                mock.patch.object(us.requests, "get",
                                  side_effect=RuntimeError("offline")) as get:
            us.do_apply_update(None, "dev")
        url = get.call_args[0][0]
        self.assertIn("refs/heads/dev", url, f"下载地址应使用所选分支：{url}")
        self.assertNotIn("refs/heads/v17", url)
        self.assertEqual(us.UPDATE_STATUS["error"], "download_failed")

    def test_invalid_branch_fails_fast(self):
        with tempfile.TemporaryDirectory() as td, \
                mock.patch.object(us, "get_real_path", return_value=td), \
                mock.patch.object(us.requests, "get") as get:
            us.do_apply_update(None, "../evil")
        get.assert_not_called()
        self.assertEqual(us.UPDATE_STATUS["error"], "invalid_branch")


class VersionRecordBranchTest(unittest.TestCase):
    def _patched_root(self, td):
        return mock.patch.object(us, "get_real_path",
                                 side_effect=lambda name: str(Path(td) / name))

    def test_version_json_records_branch(self):
        with tempfile.TemporaryDirectory() as td, self._patched_root(td):
            us.write_version_json("d" * 40, "dev")
            payload = json.loads((Path(td) / "version.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["commit"]["sha"], "d" * 40)
        self.assertEqual(payload["branch"], "dev")
        self.assertEqual(payload["updated_by"], "hot-update")

    def test_version_json_default_branch(self):
        with tempfile.TemporaryDirectory() as td, self._patched_root(td):
            us.write_version_json("e" * 40)
            payload = json.loads((Path(td) / "version.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["branch"], "v17")

    def test_build_info_records_branch(self):
        with tempfile.TemporaryDirectory() as td:
            info = Path(td) / "_build_info.py"
            info.write_text('__branch__ = "v17"\n', encoding="utf-8")
            with self._patched_root(td):
                us.refresh_build_info("f" * 40, "dev")
            text = info.read_text(encoding="utf-8")
        self.assertIn('__branch__ = "dev"', text)
        self.assertIn('__commit__ = "' + "f" * 40 + '"', text)


class RouteAdapterTest(unittest.TestCase):
    def test_check_update_query_branch(self):
        with mock.patch.object(update_routes, "_service_check_update",
                               return_value={"ok": True}) as service:
            update_routes.check_update("dev")
            service.assert_called_once_with("dev")
            service.reset_mock()
            update_routes.check_update()
            service.assert_called_once_with(None)

    def test_apply_update_body_branch(self):
        import asyncio
        with mock.patch.object(update_routes, "start_apply_update",
                               return_value={"ok": True}) as start:
            asyncio.run(update_routes.apply_update({"sha": "abcdef1", "branch": "dev"}))
            start.assert_called_once_with("abcdef1", "dev")
            start.reset_mock()
            asyncio.run(update_routes.apply_update(None))
            start.assert_called_once_with(None, None)


class FrontendWiringTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vue = UPDATE_DIALOG.read_text(encoding="utf-8")
        cls.ts = SYSTEM_TS.read_text(encoding="utf-8")

    def test_default_branch_is_v17(self):
        self.assertIn("const DEFAULT_BRANCH = 'v17'", self.vue)
        self.assertIn("const branch = ref(DEFAULT_BRANCH)", self.vue)
        self.assertEqual(us.DEFAULT_BRANCH, "v17")
        self.assertEqual(rb.DEFAULT_BRANCH, us.DEFAULT_BRANCH,
                         "回滚脚本的默认分支必须与更新服务一致")

    def test_switch_requires_ten_seconds(self):
        self.assertIn("const BRANCH_CONFIRM_SECONDS = 10", self.vue)
        self.assertIn(":disabled=\"branchConfirm.countdown > 0\"", self.vue)
        # 倒计时结束前 confirm 也必须挡一次（防绕过按钮 disabled 直接调用）
        self.assertIn("if (branchConfirm.value.countdown > 0) return", self.vue)

    def test_warning_text_present(self):
        self.assertIn("开发者测试使用，普通用户使用v17稳定分支即可", self.vue)

    def test_branch_forwarded_to_api(self):
        self.assertIn("utilsApi.checkUpdate(branch.value)", self.vue)
        self.assertIn("utilsApi.applyUpdate(sha, branch.value)", self.vue)
        self.assertIn("utilsApi.applyUpdate(undefined, branch.value)", self.vue)
        self.assertIn("params: branch ? { branch } : {}", self.ts)
        self.assertIn("...(branch ? { branch } : {})", self.ts)

    def test_reset_restores_default_branch(self):
        reset_body = self.vue.split("function reset()", 1)[1].split("function close()", 1)[0]
        self.assertIn("branch.value = DEFAULT_BRANCH", reset_body,
                      "重新打开弹窗必须回到默认稳定分支")


if __name__ == "__main__":
    unittest.main(verbosity=2)


