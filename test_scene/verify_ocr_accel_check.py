# -*- coding: utf-8 -*-
"""验证 OCR GPU(DirectML) 加速可用性检查（前端启动弹窗提示的判定来源）。

背景（用户反馈）：调度器启动后 CPU 占用呈尖峰状偏高，其中一类用户是**本地依赖库仍是
标准 onnxruntime（不含 DmlExecutionProvider）**，OCR 静默回退 CPU 推理导致占用升高。
修复：`backend/api/utils.py` 新增 `check_ocr_accel()`，`/api/utils/dependency-check`
附带 `ocr_accel` 字段，前端 `Layout.vue` 启动时据此弹窗提示覆盖安装 v0.17.17+ Release。

说明：`check_ocr_accel()` 的探测会 import onnxruntime（实测 ~0.3s，结果缓存），
因此只有在 `include_ocr=True` 时才附带，避免拖慢调度器启动拦截路径。
"""
import logging
import os
import sys
import unittest

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.api import utils as api_utils


def _probe(providers, version="1.24.4", package="onnxruntime", error=""):
    return {"providers": list(providers), "version": version,
            "package": package, "error": error}


class OcrAccelCheckTest(unittest.TestCase):
    """OCR 加速探测：四种判定分支 + 缓存 + dependency-check 的可选附带"""

    def setUp(self):
        self._orig_probe = api_utils._probe_onnxruntime_providers
        self._orig_enabled = api_utils._ocr_accel_enabled
        self._orig_cache = api_utils._OCR_ACCEL_CACHE
        api_utils._OCR_ACCEL_CACHE = None
        self.probe_calls = 0

    def tearDown(self):
        api_utils._probe_onnxruntime_providers = self._orig_probe
        api_utils._ocr_accel_enabled = self._orig_enabled
        api_utils._OCR_ACCEL_CACHE = self._orig_cache

    def _patch(self, probe, enabled=True):
        def fake_probe():
            self.probe_calls += 1
            return probe
        api_utils._probe_onnxruntime_providers = fake_probe
        api_utils._ocr_accel_enabled = lambda: enabled

    # ---- 判定分支 ----
    def test_no_dml_provider_needs_notice(self):
        """标准 onnxruntime（无 DML）→ 需要提示覆盖安装"""
        self._patch(_probe(["CPUExecutionProvider"], package="onnxruntime"))
        r = api_utils.check_ocr_accel()
        self.assertFalse(r["supported"])
        self.assertTrue(r["needs_notice"])
        self.assertEqual(r["reason"], "no_dml_provider")
        self.assertIn("当前依赖库不支持Ocr GPU加速", r["message"])
        self.assertIn("v0.17.17", r["message"])
        self.assertEqual(r["min_release_tag"], "v0.17.17")
        self.assertEqual(r["package"], "onnxruntime")
        self.assertEqual(r["providers"], ["CPUExecutionProvider"])

    def test_dml_available_ok(self):
        """onnxruntime-directml（含 DML）→ 不提示"""
        self._patch(_probe(["DmlExecutionProvider", "CPUExecutionProvider"],
                           package="onnxruntime-directml"))
        r = api_utils.check_ocr_accel()
        self.assertTrue(r["supported"])
        self.assertFalse(r["needs_notice"])
        self.assertEqual(r["reason"], "ok")
        self.assertEqual(r["message"], "")

    def test_dml_available_but_switch_off(self):
        """用户主动关闭 [助手设置] OCR加速 → 不提示（属用户选择）"""
        self._patch(_probe(["DmlExecutionProvider", "CPUExecutionProvider"],
                           package="onnxruntime-directml"), enabled=False)
        r = api_utils.check_ocr_accel()
        self.assertTrue(r["supported"])
        self.assertFalse(r["enabled"])
        self.assertEqual(r["reason"], "disabled_by_setting")
        self.assertFalse(r["needs_notice"])

    def test_probe_error_not_installed(self):
        """onnxruntime 缺失/导入失败 → 交给「依赖库不完整」弹窗，不单独提示加速"""
        self._patch(_probe([], error="onnxruntime 未安装"))
        r = api_utils.check_ocr_accel()
        self.assertFalse(r["supported"])
        self.assertFalse(r["needs_notice"])
        self.assertEqual(r["reason"], "not_installed")
        self.assertEqual(r["message"], "")

    # ---- 缓存 ----
    def test_result_cached_until_refresh(self):
        self._patch(_probe(["CPUExecutionProvider"]))
        first = api_utils.check_ocr_accel()
        second = api_utils.check_ocr_accel()
        self.assertEqual(self.probe_calls, 1, "重复调用应命中缓存（避免重复 import onnxruntime）")
        self.assertEqual(first, second)
        api_utils.check_ocr_accel(refresh=True)
        self.assertEqual(self.probe_calls, 2, "refresh=True 应重新探测")

    def test_cached_dict_is_a_copy(self):
        self._patch(_probe(["CPUExecutionProvider"]))
        r = api_utils.check_ocr_accel()
        r["providers"].append("MUTATED")
        self.assertNotIn("MUTATED", api_utils.check_ocr_accel()["providers"],
                         "返回副本，外部修改不应污染缓存")

    # ---- dependency-check 集成 ----
    def test_dependency_check_optional_ocr(self):
        self._patch(_probe(["CPUExecutionProvider"]))
        plain = api_utils.check_dependency()
        self.assertNotIn("ocr_accel", plain,
                         "默认（调度器启动拦截路径）不附带 OCR 探测，避免多余重型导入")
        with_ocr = api_utils.check_dependency(include_ocr=True)
        self.assertIn("ocr_accel", with_ocr)
        self.assertEqual(with_ocr["ok"], plain["ok"], "OCR 结果不参与 ok 判定")
        self.assertTrue(with_ocr["ocr_accel"]["needs_notice"])
        self.assertTrue(with_ocr["release_url"], "release_url 供弹窗跳转")

    # ---- 真实探测（本机 .venv 装了 onnxruntime-directml，应报可用）----
    def test_real_probe_on_dev_machine(self):
        info = self._orig_probe()
        if info["error"]:
            self.skipTest("本机 onnxruntime 不可用: %s" % info["error"])
        self.assertTrue(info["providers"], "providers 不应为空")
        self.assertTrue(info["version"])
        self.assertTrue(info["package"], "应能识别发行包名")


if __name__ == "__main__":
    unittest.main(verbosity=2)
