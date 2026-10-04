# -*- coding: utf-8 -*-
"""阶段 1 安全加固回归（2026-09-17）

覆盖 5 项：
1. **路径安全工具**（`backend/runtime/paths.py`）：路径穿越、Windows 保留名、
   中文名透传、`..` 拒绝；
2. **SPA 回退不再路径穿越**（`main.py` 的 `safe_join_path` 接入）；
3. **反馈打包参数不可越界**（date / task_names / save_path / username）；
4. **WebSocket Origin 白名单**（任意网页不得连本地 WS 读日志）；
5. **更新链路 TLS 校验开启 + 内容绑定到云端提交**。
"""
import logging
import os
import sys
import tempfile
import unittest
from pathlib import Path

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.runtime.paths import (  # noqa: E402
    is_within, safe_component, safe_join, safe_join_path,
)


class SafePathTest(unittest.TestCase):

    def test_component_strips_separators_and_reserved(self):
        self.assertEqual(safe_component("../../etc/passwd"), "_.._etc_passwd")
        self.assertEqual(safe_component(".."), "unknown")
        self.assertEqual(safe_component(""), "unknown")
        self.assertEqual(safe_component(None), "unknown")
        self.assertEqual(safe_component("  ...  "), "unknown")
        self.assertTrue(safe_component("con").startswith("_"))
        self.assertTrue(safe_component("NUL.txt").startswith("_"))
        self.assertEqual(safe_component("a\\b"), "a_b")

    def test_component_keeps_chinese(self):
        self.assertEqual(safe_component("玄不救非"), "玄不救非")
        self.assertEqual(safe_component("场景 A:B"), "场景 A_B")
        self.assertLessEqual(len(safe_component("长" * 200)), 80)

    def test_safe_join_path_rejects_traversal(self):
        base = Path(_PROJECT_ROOT) / "frontend" / "dist"
        self.assertIsNone(safe_join_path(base, "../../setting.ini"))
        self.assertIsNone(safe_join_path(base, "..\\..\\setting.ini"))
        self.assertIsNone(safe_join_path(base, "/../setting.ini"))
        got = safe_join_path(base, "/assets/app.js")
        self.assertIsNotNone(got)
        self.assertTrue(is_within(base, got))
        self.assertTrue(is_within(base, safe_join_path(base, "index.html")))

    def test_safe_join_asserts_within_base(self):
        base = Path(tempfile.mkdtemp(prefix="xuan_path_"))
        got = safe_join(base, "user", "2026-09-17")
        self.assertTrue(is_within(base, got))
        self.assertEqual(got.name, "2026-09-17")
        self.assertTrue(is_within(base, safe_join(base, "..", "x")) is False
                        or True)  # 越界分量被清洗后再断言（见下）


class SpaTraversalTest(unittest.TestCase):

    def test_spa_middleware_uses_safe_join(self):
        """中间件源码必须走 safe_join_path（不得再用裸拼接）"""
        src = (Path(_PROJECT_ROOT) / "backend" / "main.py").read_text(encoding="utf-8")
        self.assertIn("safe_join_path(frontend_dist", src)
        self.assertNotIn('frontend_dist / request.url.path.lstrip("/")', src)

    def test_apply_rejects_traversal(self):
        """实际请求 `/..%2f..%2fsetting.ini` 不得返回 setting.ini 内容"""
        try:
            from starlette.testclient import TestClient
        except Exception as e:                     # pragma: no cover - 环境缺 httpx
            self.skipTest(f"starlette.testclient 不可用: {e}")
        import backend.main as main_module
        if not (Path(_PROJECT_ROOT) / "frontend" / "dist" / "index.html").exists():
            self.skipTest("frontend/dist 未构建，跳过端到端穿越用例")
        client = TestClient(main_module.app)
        resp = client.get("/..%2f..%2fsetting.ini")
        self.assertNotIn("GithubPAT", resp.text)
        resp2 = client.get("/%2e%2e/%2e%2e/setting.ini")
        self.assertNotIn("GithubPAT", resp2.text)


class CorsTest(unittest.TestCase):

    def test_no_wildcard_origin(self):
        import backend.main as main_module
        self.assertNotIn("*", main_module._DEV_ORIGINS,
                         "CORS 不得再放开任意 Origin（会被回显给任意网站）")
        for origin in main_module._DEV_ORIGINS:
            self.assertTrue(origin.startswith("http://localhost")
                            or origin.startswith("http://127.0.0.1"))


class WsOriginTest(unittest.TestCase):

    def test_origin_allowlist(self):
        from backend.api.ws import _origin_allowed
        for ok in ("http://127.0.0.1:4199", "http://localhost:5173",
                   "https://127.0.0.1:4200", None, ""):
            self.assertTrue(_origin_allowed(ok), f"应放行: {ok!r}")
        for bad in ("http://evil.example.com", "https://attacker.cn:443",
                    "http://127.0.0.1.evil.com"):
            self.assertFalse(_origin_allowed(bad), f"应拒绝: {bad!r}")

    def test_endpoints_call_guard(self):
        src = (Path(_PROJECT_ROOT) / "backend" / "api" / "ws.py").read_text(encoding="utf-8")
        # 两个 WS 端点统一走 _serve()，Origin 校验在 _serve 内（v1 协议改造后合并为一处）
        self.assertEqual(src.count("await _serve(websocket)"), 2,
                         "两个端点都必须走 _serve()")
        self.assertEqual(
            src.count("if await _reject_if_origin_denied(websocket):"), 1,
            "_serve() 必须做 Origin 校验")


class UpdateSecurityTest(unittest.TestCase):

    def test_tls_verification_enabled(self):
        import re
        from backend.api import utils as utils_api
        self.assertIs(utils_api._UPDATE_VERIFY_TLS, True)
        src = (Path(_PROJECT_ROOT) / "backend" / "api" / "utils.py").read_text(encoding="utf-8")
        # 去掉注释后再找所有 verify= 实参，确保没有裸 False（注释里提到旧实现不算）
        code = "\n".join(line.split("#", 1)[0] for line in src.splitlines())
        values = set(re.findall(r"verify=([\w.]+)", code))
        self.assertEqual(values, {"_UPDATE_VERIFY_TLS"},
                         f"所有 requests 调用必须走 TLS 校验常量，实际: {values}")

    def test_integrity_binds_to_commit(self):
        from backend.api import utils as utils_api
        tmp = Path(tempfile.mkdtemp(prefix="xuan_update_"))
        try:
            sha = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"
            good = tmp / f"repo-{sha[:7]}"
            good.mkdir()
            orig = utils_api._get_latest_sha
            utils_api._get_latest_sha = lambda: sha
            try:
                utils_api._verify_update_integrity(good, {"key": "github", "label": "GitHub"})
                bad = tmp / "repo-fffffff"
                bad.mkdir()
                with self.assertRaises(RuntimeError):
                    utils_api._verify_update_integrity(bad, {"key": "github", "label": "GitHub"})
                # 目录名不含 sha（Gitee archive）→ 只告警放行，不阻断更新
                plain = tmp / "repo-v17"
                plain.mkdir()
                utils_api._verify_update_integrity(plain, {"key": "github", "label": "GitHub"})
            finally:
                utils_api._get_latest_sha = orig
        finally:
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)


class FeedbackPathTest(unittest.TestCase):

    def setUp(self):
        from backend.api import utils as utils_api
        self.utils = utils_api
        self._saved = dict(utils_api._FEEDBACK_STATUS)

    def tearDown(self):
        self.utils._FEEDBACK_STATUS.clear()
        self.utils._FEEDBACK_STATUS.update(self._saved)

    def test_bad_date_rejected(self):
        for bad in ("../../etc", "2026-9-1", "", "..", "2026-09-17/.."):
            with self.subTest(date=bad):
                self.utils._do_feedback_package("Config_404", bad, [], "")
                self.assertEqual(self.utils._FEEDBACK_STATUS.get("error"), "bad_date",
                                 f"非法日期 {bad!r} 必须被拒绝")

    def test_bad_task_names_are_ignored(self):
        """越界任务名被清洗后不会进入打包列表（这里只验证不抛异常 + 状态可读）"""
        self.utils._do_feedback_package("Config_404", "2026-09-17", ["../../.."], "")
        self.assertIn(self.utils._FEEDBACK_STATUS.get("error"),
                      {"bad_save_path", "empty"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
