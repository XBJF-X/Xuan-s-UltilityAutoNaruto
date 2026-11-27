# -*- coding: utf-8 -*-
"""验证「消耗体力」材料详情分支在低等级账号下能识别「扫荡」按钮。

Issue #6：低等级账号材料详情按钮文案为「扫荡」，高等级账号为「一键扫荡」。
原实现只做 IMG 模板匹配「一键扫荡」，低等级界面匹配失败后落到「合成/装备」。
修复保留原模板优先，失败后用同一元素的 ROI 构造 OCR 区域并匹配「扫荡」。

断言：
1. 材料详情分支保留原「一键扫荡」模板调用；
2. 模板失败后走 OCR 兜底，且兜底使用原元素 ROI 与 match_text="扫荡"；
3. 「超影扫荡」分支未被改动；
4. 未引入固定坐标/账号等级判断。
"""
import ast
import logging
import types
import unittest
from pathlib import Path

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

TASK_FILE = _PROJECT_ROOT / "backend" / "core" / "legacy" / "Task" / "XiaoHaoTiLi.py"


class XiaoHaoTiLiSweepTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = TASK_FILE.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_material_detail_keeps_template_first(self):
        self.assertIn('click_and_wait("一键扫荡")', self.source)
        self.assertLess(
            self.source.index('click_and_wait("一键扫荡")'),
            self.source.index("_click_material_sweep_by_ocr()"),
            "模板匹配必须优先于 OCR 兜底",
        )

    def test_material_detail_has_ocr_fallback(self):
        self.assertIn("def _click_material_sweep_by_ocr", self.source)
        for snippet in (
            'self.operationer.get_element("一键扫荡")',
            "type=ElementType.OCR_AREA",
            "roi_x=source.roi_x",
            "roi_y=source.roi_y",
            "roi_width=source.roi_width",
            "roi_height=source.roi_height",
            'match_text="扫荡"',
        ):
            self.assertIn(snippet, self.source, f"OCR 兜底缺少: {snippet}")

    def test_ocr_fallback_builds_region_from_template(self):
        func = next(
            node for node in ast.walk(self.tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "_click_material_sweep_by_ocr"
        )
        source = types.SimpleNamespace(
            scene_id="scene-1",
            ratio_x=0.5,
            ratio_y=0.5,
            roi_x=391,
            roi_y=630,
            roi_width=325,
            roi_height=136,
            ocr_min_score=0.8,
        )
        clicks = []

        class FakeOperationer:
            def get_element(self, name):
                assert name == "一键扫荡"
                return source

            def click_and_wait(self, element, match_text=""):
                clicks.append((element, match_text))
                return True

        namespace = {
            "Element": lambda **kwargs: types.SimpleNamespace(**kwargs),
            "ElementType": types.SimpleNamespace(OCR_AREA=2),
        }
        exec(
            compile(
                ast.Module(body=[func], type_ignores=[]),
                str(TASK_FILE),
                "exec",
            ),
            namespace,
        )

        task = types.SimpleNamespace(operationer=FakeOperationer())
        self.assertTrue(namespace["_click_material_sweep_by_ocr"](task))

        self.assertEqual(clicks[-1][1], "扫荡")
        element = clicks[-1][0]
        self.assertEqual(element.type, 2)
        self.assertEqual(element.roi_x, 391)
        self.assertEqual(element.roi_y, 630)
        self.assertEqual(element.roi_width, 325)
        self.assertEqual(element.roi_height, 136)
        self.assertEqual(element.ocr_min_score, 0.8)

    def test_super_shadow_branch_unchanged(self):
        self.assertIn('click_and_wait("超影扫荡")', self.source)
        self.assertNotIn('click_and_wait("超影扫荡", match_text="扫荡")', self.source)

    def test_no_hardcoded_level_or_device(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                self.assertNotRegex(
                    node.value,
                    r"(?i)(level|等级|分辨率|机型)",
                    "任务文件不应写入账号等级/设备判断",
                )

    def test_other_equipment_calls_unchanged(self):
        for call in (
            'click_and_wait("可装备")',
            'click_and_wait("一键添加")',
            'click_and_wait("可合成")',
            'click_and_wait("可扫荡")',
            'click_and_wait("进阶",max_time=0.5)',
            'click_and_wait("合成")',
            'click_and_wait("装备")',
        ):
            self.assertIn(call, self.source, f"原逻辑调用被改动: {call}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
