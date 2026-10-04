# -*- coding: utf-8 -*-
"""验证 Operationer 的两项新增能力：

1. click 相关方法新增 all_coordinates（默认 False）：依次点击检测到的所有元素图标；
2. OCR 相关 match_text 新增 full_match（默认 False）：全字匹配（去首尾空白后完全相等）；
3. 两者需相互兼容（同一元素同时开启时都要生效）。
"""
import logging
import os
import sys
import threading
import types
import unittest
import unittest.mock

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.core.legacy.Enums import ElementType
from backend.core.legacy.Operationer import Operationer


class _ClickRecorder:

    def __init__(self):
        self.points = []

    def __call__(self, x, y, times=1):
        self.points.append((x, y, times))
        return True


class _CallRecorder:

    def __init__(self, result=True):
        self.calls = []
        self.result = result

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return self.result


def _img_element(name="测试图", ratio_x=0.5, ratio_y=0.5):
    return types.SimpleNamespace(type=ElementType.IMG, name=name,
                                 ratio_x=ratio_x, ratio_y=ratio_y)


def _ocr_element(name="已领取", ratio_x=0.5, ratio_y=0.5):
    return types.SimpleNamespace(type=ElementType.OCR_AREA, name=name,
                                 ratio_x=ratio_x, ratio_y=ratio_y)


def _coordinate_element(x=100, y=200):
    return types.SimpleNamespace(type=ElementType.COORDINATE, name="坐标",
                                 coordinate_x=x, coordinate_y=y,
                                 ratio_x=0.5, ratio_y=0.5)


def _make_operationer(match_coordinates=None, ocr_results=None):
    """构造仅含测试所需依赖的 Operationer（不跑 __init__）"""
    op = object.__new__(Operationer)
    op.task_name = "verify"
    op.logger = logging.getLogger("verify.operationer")
    op.stop_event = threading.Event()
    op.screen_save_func = lambda task_name: None
    op.current_scene = None
    click_recorder = _ClickRecorder()
    op.device = types.SimpleNamespace(
        click=click_recorder,
        screen_cap=lambda: None,
        package_name="com.tencent.KiHan")
    op.recognizer = types.SimpleNamespace(
        element_match=lambda img, el, *a: list(match_coordinates or []),
        # 自 v0.17.41 起 IMG 点击走"匹配 + 指标"接口（供一次查找汇总成一条日志）
        collect_element_match=lambda img, el, *a, **k: (
            list(match_coordinates or []),
            {"method": "TEMPLATE", "max_val": 0.9, "threshold": 0.8}),
        area_ocr=lambda img, el, bool_debug=False: list(ocr_results or []))
    return op, click_recorder


class ImgMultiCoordinateTest(unittest.TestCase):
    """IMG 元素：all_coordinates 控制是否点击全部匹配位置"""

    COORDS = [(0, 0, 100, 100), (200, 0, 300, 100), (0, 200, 100, 300)]

    def test_default_clicks_first_only(self):
        op, rec = _make_operationer(match_coordinates=self.COORDS)
        with unittest.mock.patch("time.sleep"):
            ok = op._click_element_once(_img_element(), 1, "", 0.5, 0.5)
        self.assertTrue(ok)
        self.assertEqual(rec.points, [(50, 50, 1)],
                         "默认 all_coordinates=False 应只点第一个命中位置")

    def test_all_coordinates_clicks_every_match(self):
        op, rec = _make_operationer(match_coordinates=self.COORDS)
        with unittest.mock.patch("time.sleep") as sleep_mock:
            ok = op._click_element_once(_img_element(), 1, "", 0.5, 0.5, True)
        self.assertTrue(ok)
        self.assertEqual(rec.points, [(50, 50, 1), (250, 50, 1), (50, 250, 1)])
        interval_calls = [c for c in sleep_mock.call_args_list
                          if c.args and c.args[0] == 0.5]
        self.assertEqual(len(interval_calls), 2,
                         "3 个坐标之间应有 2 次 click_interval 间隔")

    def test_no_match_returns_false(self):
        op, rec = _make_operationer(match_coordinates=[])
        ok = op._click_element_once(_img_element(), 1, "", 0.5, 0.5, True)
        self.assertFalse(ok)
        self.assertEqual(rec.points, [])

    def test_coordinate_element_ignores_all_coordinates(self):
        op, rec = _make_operationer()
        ok = op._click_element_once(_coordinate_element(), 2, "", 0.5, 0.5, True)
        self.assertTrue(ok)
        self.assertEqual(rec.points, [(100, 200, 2)],
                         "COORDINATE 元素只有一个坐标，all_coordinates 不生效")


class OcrMatchTest(unittest.TestCase):
    """OCR_AREA 元素：full_match 与 all_coordinates 及其组合"""

    OCR_RESULTS = [
        ("已领取", [0, 0, 100, 100], 0.9),
        ("已领取（1）", [200, 0, 300, 100], 0.9),
        ("未领取", [0, 200, 100, 300], 0.9),
    ]

    def test_substring_match_default(self):
        op, rec = _make_operationer(ocr_results=self.OCR_RESULTS)
        with unittest.mock.patch("time.sleep"):
            ok = op._click_element_once(_ocr_element(), 1, "已领取", 0.5, 0.5,
                                        True)
        self.assertTrue(ok)
        self.assertEqual(rec.points, [(50, 50, 1), (250, 50, 1)],
                         "默认子串匹配应命中[已领取]与[已领取（1）]")

    def test_full_match_only_exact_hit(self):
        op, rec = _make_operationer(ocr_results=self.OCR_RESULTS)
        with unittest.mock.patch("time.sleep"):
            ok = op._click_element_once(_ocr_element(), 1, "已领取", 0.5, 0.5,
                                        True, True)
        self.assertTrue(ok)
        self.assertEqual(rec.points, [(50, 50, 1)],
                         "全字匹配时[已领取（1）]不应命中")

    def test_full_match_with_all_coordinates_compatible(self):
        """全字匹配 + 点击全部命中（两项改动相互兼容）"""
        results = self.OCR_RESULTS + [("已领取", [0, 300, 100, 400], 0.9)]
        op, rec = _make_operationer(ocr_results=results)
        with unittest.mock.patch("time.sleep"):
            op._click_element_once(_ocr_element(), 1, "已领取", 0.5, 0.5, True,
                                   True)
        self.assertEqual(rec.points, [(50, 50, 1), (50, 350, 1)])

    def test_match_element_once_full_match_strips_whitespace(self):
        op, _ = _make_operationer(
            ocr_results=[(" 已领取 ", [0, 0, 10, 10], 0.9)])
        self.assertTrue(op._match_element_once(_ocr_element(), "已领取", True),
                        "全字匹配应忽略首尾空白")
        self.assertFalse(op._match_element_once(_ocr_element(), "领取", True),
                         "全字匹配时部分文本不应命中")
        self.assertTrue(op._match_element_once(_ocr_element(), "领取", False),
                        "默认子串匹配应命中")


class PublicApiForwardingTest(unittest.TestCase):
    """公开方法必须把新开关真正传下去（含 _search_loop 不透传 kwargs 的坑）"""

    def _patch_once(self, op):
        recorder = _CallRecorder()
        op._click_element_once = recorder
        return recorder

    def test_click_and_wait_forwards_flags(self):
        op, _ = _make_operationer()
        recorder = self._patch_once(op)
        with unittest.mock.patch("time.sleep"):
            ok = op.click_and_wait(_img_element(), "文本", True, True,
                                   max_attempts=1, wait_time=0,
                                   click_interval=0.25)
        self.assertTrue(ok)
        args, _kwargs = recorder.calls[0]
        self.assertEqual(args[0].name, "测试图")
        self.assertEqual(args[2], "文本")
        self.assertIs(args[5], True)
        self.assertIs(args[6], True)
        self.assertEqual(args[7], 0.25)

    def test_click_and_wait_defaults_regression(self):
        op, _ = _make_operationer()
        recorder = self._patch_once(op)
        with unittest.mock.patch("time.sleep"):
            op.click_and_wait(_img_element(), max_attempts=1, wait_time=0)
        args, _kwargs = recorder.calls[0]
        self.assertEqual((args[5], args[6], args[7]), (False, False, 0.5),
                         "默认值须与改动前一致：all_coordinates/full_match=False、间隔0.5")

    def test_search_and_click_forwards_flags(self):
        op, _ = _make_operationer()
        recorder = _CallRecorder()
        op.click_and_wait = recorder
        op.search_and_click(["元素A"], [], "文本", all_coordinates=True,
                            full_match=True, max_attempts=1, click_interval=0.25)
        _args, kwargs = recorder.calls[0]
        self.assertEqual(kwargs.get("match_text"), "文本")
        self.assertIs(kwargs.get("all_coordinates"), True)
        self.assertIs(kwargs.get("full_match"), True)
        self.assertEqual(kwargs.get("click_interval"), 0.25)

    def test_search_and_detect_forwards_full_match(self):
        op, _ = _make_operationer()
        recorder = _CallRecorder()
        op.detect_element = recorder
        op.search_and_detect(["元素A"], [], "文本", full_match=True,
                             max_attempts=1)
        _args, kwargs = recorder.calls[0]
        self.assertEqual(kwargs.get("match_text"), "文本")
        self.assertIs(kwargs.get("full_match"), True)

    def test_detect_element_forwards_full_match(self):
        op, _ = _make_operationer()
        recorder = _CallRecorder()
        op._match_element_once = recorder
        with unittest.mock.patch("time.sleep"):
            op.detect_element(_ocr_element(), "文本", True, max_attempts=1)
        args, _kwargs = recorder.calls[0]
        self.assertEqual(args[1], "文本")
        self.assertIs(args[2], True)


class RandomClickTest(unittest.TestCase):
    """random 参数：单目标随机取一个命中；多目标打乱顺序后依次点击"""

    COORDS = [(0, 0, 100, 100), (200, 0, 300, 100), (0, 200, 100, 300)]
    OCR_RESULTS = [
        ("已领取", [0, 0, 100, 100], 0.9),
        ("已领取", [200, 0, 300, 100], 0.9),
    ]

    @staticmethod
    def _fake_random():
        """choice 取最后一个、shuffle 反转，保证断言确定性"""
        fake = unittest.mock.MagicMock()
        fake.choice.side_effect = lambda seq: seq[-1]
        fake.shuffle.side_effect = lambda seq: seq.reverse()
        return fake

    def _patch_random(self, fake):
        return unittest.mock.patch("backend.core.legacy.Operationer._random",
                                   fake)

    def test_random_single_target_picks_random_match(self):
        op, rec = _make_operationer(match_coordinates=self.COORDS)
        fake = self._fake_random()
        with self._patch_random(fake):
            with unittest.mock.patch("time.sleep"):
                ok = op._click_element_once(_img_element(), 1, "",
                                            ratio_x=0.5, ratio_y=0.5,
                                            all_coordinates=False, random=True)
        self.assertTrue(ok)
        self.assertEqual(len(fake.choice.call_args[0][0]), 3,
                         "random=True 时应把全部命中交给随机选择")
        self.assertEqual(rec.points, [(50, 250, 1)],
                         "单目标随机：取 choice 选中的那个坐标")

    def test_random_all_coordinates_shuffles_order(self):
        op, rec = _make_operationer(match_coordinates=self.COORDS)
        fake = self._fake_random()
        with self._patch_random(fake):
            with unittest.mock.patch("time.sleep"):
                ok = op._click_element_once(_img_element(), 1, "",
                                            ratio_x=0.5, ratio_y=0.5,
                                            all_coordinates=True, random=True)
        self.assertTrue(ok)
        self.assertEqual(len(rec.points), 3, "多目标随机仍应点击全部命中")
        self.assertEqual(rec.points, [(50, 250, 1), (250, 50, 1), (50, 50, 1)],
                         "多目标随机：按打乱后的顺序点击")
        fake.choice.assert_not_called()

    def test_random_false_keeps_first_and_order(self):
        op, rec = _make_operationer(match_coordinates=self.COORDS)
        with unittest.mock.patch("time.sleep"):
            op._click_element_once(_img_element(), 1, "",
                                   ratio_x=0.5, ratio_y=0.5,
                                   all_coordinates=False, random=False)
        self.assertEqual(rec.points, [(50, 50, 1)],
                         "random=False 时仍取第一个命中（回归）")
        op2, rec2 = _make_operationer(match_coordinates=self.COORDS)
        with unittest.mock.patch("time.sleep"):
            op2._click_element_once(_img_element(), 1, "",
                                    ratio_x=0.5, ratio_y=0.5,
                                    all_coordinates=True, random=False)
        self.assertEqual(rec2.points, [(50, 50, 1), (250, 50, 1), (50, 250, 1)],
                         "random=False 时保持识别顺序（回归）")

    def test_random_with_ocr_results(self):
        op, rec = _make_operationer(ocr_results=self.OCR_RESULTS)
        fake = self._fake_random()
        with self._patch_random(fake):
            with unittest.mock.patch("time.sleep"):
                ok = op._click_element_once(_ocr_element(), 1, "已领取",
                                            ratio_x=0.5, ratio_y=0.5,
                                            all_coordinates=False, random=True)
        self.assertTrue(ok)
        self.assertEqual(len(fake.choice.call_args[0][0]), 2)
        self.assertEqual(rec.points, [(250, 50, 1)])

    def test_random_with_no_match_returns_false(self):
        op, rec = _make_operationer(match_coordinates=[])
        fake = self._fake_random()
        with self._patch_random(fake):
            ok = op._click_element_once(_img_element(), 1, "",
                                        ratio_x=0.5, ratio_y=0.5,
                                        all_coordinates=False, random=True)
        self.assertFalse(ok)
        self.assertEqual(rec.points, [])
        fake.choice.assert_not_called()

    def test_coordinate_element_unaffected_by_random(self):
        op, rec = _make_operationer(match_coordinates=self.COORDS)
        fake = self._fake_random()
        with self._patch_random(fake):
            ok = op._click_element_once(_coordinate_element(), 1, "",
                                        ratio_x=0.5, ratio_y=0.5,
                                        all_coordinates=True, random=True)
        self.assertTrue(ok)
        self.assertEqual(rec.points, [(100, 200, 1)])
        fake.choice.assert_not_called()
        fake.shuffle.assert_not_called()

    # ---- 公开方法透传（含 _search_loop 不透传 kwargs 的坑） ----

    def test_click_and_wait_forwards_random(self):
        op, _ = _make_operationer()
        recorder = _CallRecorder()
        op._click_element_once = recorder
        with unittest.mock.patch("time.sleep"):
            op.click_and_wait(_img_element(), max_attempts=1, wait_time=0,
                              random=True)
        args, _kwargs = recorder.calls[0]
        self.assertIs(args[5], False)
        self.assertIs(args[6], False)
        self.assertIs(args[8], True, "random 应作为最后一个参数传入")

    def test_click_and_wait_random_defaults_to_false(self):
        op, _ = _make_operationer()
        recorder = _CallRecorder()
        op._click_element_once = recorder
        with unittest.mock.patch("time.sleep"):
            op.click_and_wait(_img_element(), max_attempts=1, wait_time=0)
        args, _kwargs = recorder.calls[0]
        self.assertIs(args[8], False, "random 默认 False（行为与改动前一致）")

    def test_search_and_click_forwards_random(self):
        op, _ = _make_operationer()
        recorder = _CallRecorder()
        op.click_and_wait = recorder
        op.search_and_click(["元素A"], [], "文本", random=True, max_attempts=1)
        _args, kwargs = recorder.calls[0]
        self.assertIs(kwargs.get("random"), True)

    def test_real_random_module_produces_permutation(self):
        """不 mock 时使用真实 random：多目标应得到全部命中的某个排列"""
        op, rec = _make_operationer(match_coordinates=self.COORDS)
        with unittest.mock.patch("time.sleep"):
            op._click_element_once(_img_element(), 1, "",
                                   ratio_x=0.5, ratio_y=0.5,
                                   all_coordinates=True, random=True)
        self.assertEqual(sorted(rec.points),
                         sorted([(50, 50, 1), (250, 50, 1), (50, 250, 1)]),
                         "真实 random：应点击全部命中（顺序被打乱）")
        op2, rec2 = _make_operationer(match_coordinates=self.COORDS)
        with unittest.mock.patch("time.sleep"):
            op2._click_element_once(_img_element(), 1, "",
                                    ratio_x=0.5, ratio_y=0.5,
                                    all_coordinates=False, random=True)
        self.assertEqual(len(rec2.points), 1)
        self.assertIn(rec2.points[0],
                      [(50, 50, 1), (250, 50, 1), (50, 250, 1)],
                      "真实 random：单目标应是某个命中位置")


if __name__ == "__main__":
    unittest.main(verbosity=2)

