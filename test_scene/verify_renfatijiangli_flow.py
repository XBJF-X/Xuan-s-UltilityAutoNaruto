# -*- coding: utf-8 -*-
"""验证 [忍法帖奖励] 周活跃场景的两处 bug 修复：

1. "已领"命中数统计：原写法 len([item.text=="已领" for item in yl]) 恒等于 OCR 结果
   条数，只要返回 5 条文本（无论内容）就判定"全部领完"；
2. 活跃度档位领取：原写法 filtered_tiers=[x < hyd_num for x in TIERS] 生成布尔列表，
   随后把布尔值当档位号拼进元素名（"活跃度-True"/"活跃度-False"）。
"""
import logging
import os
import sys
import types
import unittest

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.core.legacy.OcrText import OcrText
from backend.core.legacy.Task.RenFaTieJiangLi import RenFaTieJiangLi

WEEKLY_ACTIVE_SCENE = "忍法帖-周活跃"


def _ocr_texts(*texts):
    return [OcrText(t, [0, 0, 10, 10], 0.9) for t in texts]


class _FakeOperationer:

    def __init__(self, ocr_map):
        self.ocr_map = ocr_map
        self.clicks = []

    def ocr_recognize(self, element, **kwargs):
        return self.ocr_map.get(element)

    def click_and_wait(self, element, **kwargs):
        self.clicks.append(element)
        return True


def _make_task(ocr_map):
    task = object.__new__(RenFaTieJiangLi)
    task.logger = logging.getLogger("verify.rftjl.flow")
    task.all_tasks = False
    task.all_activations = False
    task.operationer = _FakeOperationer(ocr_map)
    return task


def _run_weekly_active(task):
    return RenFaTieJiangLi.transition_func[WEEKLY_ACTIVE_SCENE](task)


class ClaimedCountTest(unittest.TestCase):
    """bug1：只有恰好 5 条"已领"才算全部领完"""

    def test_five_hits_marks_all_activations(self):
        task = _make_task({"已领": _ocr_texts("已领", "已领", "已领", "已领", "已领")})
        self.assertTrue(_run_weekly_active(task))
        self.assertTrue(task.all_activations)

    def test_five_results_but_not_all_hits(self):
        """回归：原实现此处会误判为全部领完"""
        task = _make_task({"已领": _ocr_texts("已领", "已领", "已领", "未领", "未领")})
        self.assertFalse(_run_weekly_active(task))
        self.assertFalse(task.all_activations)

    def test_two_hits_is_not_all_claimed(self):
        task = _make_task({"已领": _ocr_texts("已领", "已领")})
        self.assertFalse(_run_weekly_active(task))
        self.assertFalse(task.all_activations)

    def test_empty_ocr_result_is_not_all_claimed(self):
        task = _make_task({"已领": []})
        self.assertFalse(_run_weekly_active(task))
        self.assertFalse(task.all_activations)


class TierClickTest(unittest.TestCase):
    """bug2：按档位号点击"活跃度-{tier}"，不得出现布尔值元素名"""

    def _task_with_value(self, value):
        return _make_task({
            "已领": _ocr_texts("已领"),
            "本周活跃度值": types.SimpleNamespace(
                get_single_number=lambda: value),
        })

    def test_clicks_only_below_value(self):
        task = self._task_with_value(160)
        self.assertFalse(_run_weekly_active(task))
        self.assertEqual(task.operationer.clicks,
                         ["活跃度-50", "活跃度-100", "活跃度-150"])

    def test_clicks_all_tiers_when_value_high(self):
        task = self._task_with_value(999)
        _run_weekly_active(task)
        self.assertEqual(task.operationer.clicks,
                         ["活跃度-50", "活跃度-100", "活跃度-150",
                          "活跃度-200", "活跃度-300"])

    def test_no_clicks_when_value_too_low(self):
        task = self._task_with_value(40)
        _run_weekly_active(task)
        self.assertEqual(task.operationer.clicks, [])

    def test_no_clicks_when_value_unparsable(self):
        task = self._task_with_value(None)
        _run_weekly_active(task)
        self.assertEqual(task.operationer.clicks, [])

    def test_element_names_never_contain_bool(self):
        task = self._task_with_value(160)
        _run_weekly_active(task)
        for name in task.operationer.clicks:
            self.assertNotIn("True", name)
            self.assertNotIn("False", name)


if __name__ == "__main__":
    unittest.main(verbosity=2)