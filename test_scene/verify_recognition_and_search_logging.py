# -*- coding: utf-8 -*-
"""验证「识别过程日志默认关闭」+「元素查找/OCR 汇总成一条 DEBUG 日志」（2026-09-13）。

背景（用户反馈）：
1. 场景识别把每一步都打成 DEBUG（弹窗逐项检查 21 行 + 候选/子场景逐项 + 模板匹配统计…），
   每次识别几十行，日志文件（Xuan.log 100MB 轮转）迅速膨胀，任务执行过程反而看不清；
2. 与之相反，Operationer 里真正需要的"查找图片元素 / OCR 区域"过程被省略了——
   匹配值算完就丢，OCR 文本逐条 DEBUG 且不汇总。

修复：
- `Recognizer` 增加识别过程日志总开关 `ENABLE_RECOGNITION_DEBUG_LOG`（默认 False，
  可用 `Recognizer(..., enable_debug_log=True)` 临时打开）；数据采集（`ctx.debug`/`collect`）
  与日志输出解耦；
- 新增 `Recognizer.collect_element_match()`：单次匹配 + 指标（未命中也有"最大响应值"，
  且不输出过程日志）；
- `Operationer` 用 `_SearchMetrics` 把整轮查找汇总成**一条** INFO
  （尝试次数 / 最高匹配值 / 匹配值列表 / 阈值 / 结果；OCR 则给出识别到的文本列表），
  `_ocr_results` 的逐条明细压成一条 DEBUG。

覆盖：
A. 日志开关
  1. 默认关闭 + 构造参数可开 + `_MatchContext.collect` 默认 False；
  2. 关闭时 `scene()` 一条过程日志都不输出，且识别结果与打开时一致；
  3. 打开时过程日志恢复（含"检查弹窗场景"逐项输出）；
B. 采集接口
  4. `collect_element_match` 命中/未命中都返回 method/max_val/threshold/hit；
  5. 采集过程不输出任何过程日志；
C. Operationer 汇总
  6. 图片元素：整轮查找只输出一条 DEBUG（且不产生 INFO），含尝试次数/最高匹配值/匹配值列表/阈值/结果；
  7. 未命中同样输出（便于判断阈值/ROI/画面问题）；
  8. OCR 区域：总述含识别到的文本列表（文本+置信度），明细压成 1 条 DEBUG；
  9. 纯坐标元素（无匹配过程）不产生总述；匹配值过多时折叠计数。
"""
import glob
import logging
import os
import sys
import threading
import unittest

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.core.legacy.Enums import ElementType  # noqa: E402
from backend.core.legacy.Operationer import (  # noqa: E402
    Operationer,
    _SearchMetrics,
    _format_match_values,
)
from backend.core.legacy.Recognizer import (  # noqa: E402
    ENABLE_RECOGNITION_DEBUG_LOG,
    Recognizer,
)
from backend.core.legacy.Scene.SceneGraph import SceneGraph  # noqa: E402
from backend.tools.resource_db import ResourceDBManager  # noqa: E402
from backend.utils import cv_imread  # noqa: E402

# 识别过程日志的特征片段（关闭后一条都不应出现）
PROCESS_LOG_MARKERS = (
    "检查弹窗场景", "开始匹配场景", "检查子场景", "匹配结果统计",
    "候选集裁剪", "不做裁剪，走全量仲裁", "全量兜底扫描",
)

_graph_cache = {}


def _graph():
    """进程内共享场景图（构建 ≈1.5s，避免每个用例重复解码元素图）"""
    if "graph" not in _graph_cache:
        _graph_cache["graph"] = SceneGraph(ResourceDBManager())
    return _graph_cache["graph"]


def _test_images(limit: int = 1) -> list:
    files = sorted(glob.glob(os.path.join(_PROJECT_ROOT, "test_scene", "*.png")))
    if limit <= 0 or limit >= len(files):
        return files
    step = max(1, len(files) // limit)
    return files[::step][:limit]


class _CaptureHandler(logging.Handler):
    """收集某个 logger 上的记录（用于断言"有没有输出过程日志"）。"""

    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.records = []

    def emit(self, record):
        self.records.append(record)

    @property
    def messages(self):
        return [r.getMessage() for r in self.records]

    def process_logs(self):
        return [m for m in self.messages if any(k in m for k in PROCESS_LOG_MARKERS)]


def _capture(logger, func, level=logging.DEBUG):
    """在 logger 上挂临时 handler 执行 func（期间不外泄到控制台），返回 (handler, 返回值)"""
    previous_level, previous_propagate = logger.level, logger.propagate
    logger.setLevel(level)
    logger.propagate = False      # 避免测试输出被 root handler 打到控制台
    handler = _CaptureHandler()
    logger.addHandler(handler)
    try:
        result = func()
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous_level)
        logger.propagate = previous_propagate
    return handler, result


def _scene_name(result) -> str:
    return getattr(result, "name", None) or str(result)


class RecognitionLogSwitchTest(unittest.TestCase):
    """A/B：识别过程日志默认关闭，开发时一键打开"""

    @classmethod
    def setUpClass(cls):
        cls.image = None
        paths = _test_images(1)
        if paths:
            cls.image = cv_imread(paths[0])
        cls.image_path = paths[0] if paths else ""

    def _skip_if_no_image(self):
        if self.image is None:
            self.skipTest("test_scene 下无可用底图")

    # ---- 1. 开关默认值 ----

    def test_switch_off_by_default(self):
        self.assertFalse(ENABLE_RECOGNITION_DEBUG_LOG, "识别过程日志应默认关闭")
        graph = _graph()
        self.assertFalse(Recognizer(graph).enable_debug_log)
        self.assertTrue(Recognizer(graph, enable_debug_log=True).enable_debug_log)

    def test_collect_mode_is_independent_from_debug(self):
        recognizer = Recognizer(_graph())
        self.assertFalse(recognizer._make_ctx(False).collect)
        self.assertFalse(recognizer._make_ctx(False).debug)
        self.assertTrue(recognizer._make_ctx(False, True).collect,
                        "采集模式应可独立于过程日志开启")

    # ---- 2/3. 关闭 vs 打开的实际输出 ----

    def test_scene_quiet_by_default_and_noisy_when_enabled(self):
        self._skip_if_no_image()
        graph = _graph()
        quiet = Recognizer(graph)
        noisy = Recognizer(graph, enable_debug_log=True)

        quiet_handler, quiet_result = _capture(
            quiet.logger, lambda: quiet.scene(self.image, False))
        noisy_handler, noisy_result = _capture(
            noisy.logger, lambda: noisy.scene(self.image, False))

        self.assertEqual(_scene_name(quiet_result), _scene_name(noisy_result),
                         "日志开关不应影响识别结果")
        self.assertEqual(quiet_handler.process_logs(), [],
                         f"默认关闭时不应输出过程日志: {quiet_handler.process_logs()[:3]}")
        self.assertEqual([r for r in quiet_handler.records
                          if r.levelno == logging.DEBUG], [],
                         "默认关闭时识别路径不应有任何 DEBUG 输出")

        noisy_logs = noisy_handler.process_logs()
        self.assertTrue(any("检查弹窗场景" in m for m in noisy_logs),
                        "打开开关后应恢复弹窗逐项检查日志")
        self.assertGreaterEqual(len(noisy_logs), 10,
                                "打开开关后应有大量过程日志（本次识别帧）")


class CollectElementMatchTest(unittest.TestCase):
    """B. `Recognizer.collect_element_match` 的指标采集"""

    @classmethod
    def setUpClass(cls):
        cls.images = {}
        for path in _test_images(1):
            img = cv_imread(path)
            if img is not None:
                cls.images[os.path.splitext(os.path.basename(path))[0]] = img

    def setUp(self):
        if not self.images:
            self.skipTest("test_scene 下无可用底图")

    @staticmethod
    def _first_symbol_element(scene):
        for element in scene.elements:
            if element.symbol:
                return element
        return None

    def test_hit_metrics_and_no_process_log(self):
        """命中：返回坐标 + 指标（method/max_val/threshold/hit），且不输出过程日志"""
        name, img = next(iter(self.images.items()))
        graph = _graph()
        scene = graph.get_scene(name)
        if scene is None:
            self.skipTest(f"场景库中无 {name}")
        element = self._first_symbol_element(scene)
        if element is None:
            self.skipTest(f"{name} 无标志元素")

        recognizer = Recognizer(graph)
        handler, (matches, metrics) = _capture(
            recognizer.logger,
            lambda: recognizer.collect_element_match(img, element))
        self.assertTrue(matches, "本场景自己的标志元素应命中")
        self.assertTrue(metrics.get("hit"))
        self.assertGreaterEqual(metrics.get("match_count", 0), 1)
        self.assertEqual(metrics.get("method"), "TEMPLATE")
        self.assertIn("threshold", metrics)
        self.assertGreaterEqual(metrics["max_val"], float(element.threshold))
        self.assertEqual(handler.process_logs(), [],
                         "采集模式不应输出过程日志")
        self.assertIsNone(recognizer._ctx.gray, "采集结束应释放整帧灰度缓存")

    def test_miss_metrics_carry_max_response(self):
        """未命中：仍给出最大响应值（判断"离阈值差多少"），且无过程日志"""
        name, img = next(iter(self.images.items()))
        graph = _graph()
        recognizer = Recognizer(graph)
        element = None
        for idx, (cand_name, cand) in enumerate(graph.scenes.items()):
            if idx > 60:      # 抽样查找即可，避免全库逐元素匹配拖慢用例
                break
            if cand_name == name or not cand.elements:
                continue
            for candidate in cand.elements:
                if candidate.symbol and not recognizer.element_match(img, candidate, False):
                    element = candidate
                    break
            if element is not None:
                break
        if element is None:
            self.skipTest("抽样范围内没找到【未命中】的标志元素")

        handler, (matches, metrics) = _capture(
            recognizer.logger,
            lambda: recognizer.collect_element_match(img, element))
        self.assertFalse(matches)
        self.assertFalse(metrics.get("hit"))
        self.assertIn("max_val", metrics)
        self.assertLess(metrics["max_val"], float(element.threshold))
        self.assertEqual(handler.process_logs(), [])


class _FakeDevice:
    """最小设备替身：只提供截图与点击"""

    def __init__(self, click_result=True):
        self._frame = object()
        self.click_result = click_result
        self.clicks = []

    def screen_cap(self):
        return self._frame

    def click(self, x, y, times=1):
        self.clicks.append((x, y, times))
        return self.click_result


class _FakeElement:
    """最小元素替身（只用到 name/type/ratio/坐标）"""

    def __init__(self, name, element_type=ElementType.IMG):
        self.name = name
        self.type = element_type
        self.ratio_x = 0.5
        self.ratio_y = 0.5
        self.coordinate_x = 100
        self.coordinate_y = 200


class _FakeRecognizer:
    """替身：按脚本依次返回匹配结果与指标；OCR 返回预设 (文本, 框, 分数)"""

    def __init__(self, script=None, ocr_results=None):
        self.script = list(script or [])      # [(matches, metrics), ...]，末项复用
        self.ocr_results = list(ocr_results or [])
        self.match_calls = 0

    def collect_element_match(self, scene_img, element, bool_debug=False):
        self.match_calls += 1
        if not self.script:
            return [], {"method": "TEMPLATE", "max_val": 0.0, "threshold": 0.8}
        index = min(self.match_calls - 1, len(self.script) - 1)
        matches, metrics = self.script[index]
        return list(matches), dict(metrics)

    def area_ocr(self, scene_img, element, bool_debug=False):
        return list(self.ocr_results)


def _make_operationer(recognizer, device=None):
    """构造只带识别/点击依赖的 Operationer（跳过 __init__ 的设备与点击器初始化）"""
    op = object.__new__(Operationer)
    op.logger = logging.getLogger("verify.op")
    op.task_name = "验证任务"
    op.recognizer = recognizer
    op.device = device or _FakeDevice()
    op.screen_save_func = lambda *args: None
    op.stop_event = threading.Event()
    op.current_scene = None
    op.__dict__.pop("_last_click_key", None)
    return op


class SearchSummaryLogTest(unittest.TestCase):
    """C. 元素查找/OCR 的"一条总述"日志"""

    def setUp(self):
        self.logger = logging.getLogger("verify.op")
        self.logger.setLevel(logging.DEBUG)

    @staticmethod
    def _summary_records(handler, element_name):
        return [r for r in handler.records
                if r.getMessage().startswith(f"[识别] 查找[{element_name}]")]

    @staticmethod
    def _summaries(handler, element_name):
        return [r.getMessage()
                for r in SearchSummaryLogTest._summary_records(handler, element_name)]

    def test_image_element_summary_collects_match_values(self):
        """图片元素：整轮查找只输出一条 DEBUG（不产生 INFO），含各字段"""
        recognizer = _FakeRecognizer(script=[
            ([], {"method": "TEMPLATE", "max_val": 0.62, "threshold": 0.8}),
            ([], {"method": "TEMPLATE", "max_val": 0.71, "threshold": 0.8}),
            ([(10, 10, 40, 40)],
             {"method": "TEMPLATE", "max_val": 0.86, "threshold": 0.8}),
        ])
        op = _make_operationer(recognizer)
        handler, result = _capture(
            self.logger,
            lambda: op.detect_element(_FakeElement("排行榜点赞-标志"),
                                      max_attempts=5, wait_time=0))
        self.assertTrue(result)
        records = self._summary_records(handler, "排行榜点赞-标志")
        self.assertEqual(len(records), 1, f"整轮查找只应一条总述: {records}")
        self.assertEqual(records[0].levelno, logging.DEBUG,
                         "查找总述应为 DEBUG 级别，不占用 INFO")
        self.assertEqual([r.getMessage() for r in handler.records
                          if r.levelno == logging.INFO], [],
                         "查找不应产生 INFO 日志")
        line = records[0].getMessage()
        self.assertIn("类型=图片", line)
        self.assertIn("尝试=3次", line)
        self.assertIn("最高匹配值=0.86", line)
        self.assertIn("匹配值=[0.62, 0.71, 0.86]", line)
        self.assertIn("阈值=0.80", line)
        self.assertIn("结果=命中", line)

    def test_miss_summary_still_reports_values(self):
        """未命中：同样输出一条 DEBUG 总述，且给出"离阈值差多少"（最高匹配值 < 阈值）"""
        recognizer = _FakeRecognizer(script=[
            ([], {"method": "TEMPLATE", "max_val": 0.42, "threshold": 0.8}),
        ])
        op = _make_operationer(recognizer)
        handler, result = _capture(
            self.logger,
            lambda: op.detect_element(_FakeElement("自动战斗中"),
                                      max_attempts=3, wait_time=0))
        self.assertFalse(result)
        records = self._summary_records(handler, "自动战斗中")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].levelno, logging.DEBUG)
        line = records[0].getMessage()
        self.assertIn("尝试=3次", line)
        self.assertIn("最高匹配值=0.42", line)
        self.assertIn("阈值=0.80", line)
        self.assertIn("结果=未命中", line)

    def test_click_path_emits_single_summary(self):
        """点击路径（click_and_wait）同样只汇总一条 DEBUG；点击日志仍为 INFO"""
        device = _FakeDevice(click_result=True)
        recognizer = _FakeRecognizer(script=[
            ([(10, 10, 40, 40)],
             {"method": "TEMPLATE", "max_val": 0.90, "threshold": 0.8}),
        ])
        op = _make_operationer(recognizer, device)
        handler, result = _capture(
            self.logger,
            lambda: op.click_and_wait(_FakeElement("确定"), wait_time=0,
                                      max_attempts=2))
        self.assertTrue(result)
        self.assertEqual(len(device.clicks), 1)
        records = self._summary_records(handler, "确定")
        self.assertEqual(len(records), 1, f"点击路径总述应只有一条: {records}")
        self.assertEqual(records[0].levelno, logging.DEBUG, "总述应为 DEBUG 级别")
        line = records[0].getMessage()
        self.assertIn("最高匹配值=0.90", line)
        self.assertIn("结果=命中", line)
        self.assertIn("[Click] [确定]",
                      [r.getMessage() for r in handler.records
                       if r.levelno == logging.INFO],
                      "点击日志（[Click]）仍应是 INFO")

    def test_ocr_summary_lists_recognized_texts(self):
        """OCR 区域：总述（DEBUG）列出识别到的文本，明细另压成 1 条 DEBUG"""
        ocr_results = [
            ("12", [100, 200, 140, 230], 0.98),
            ("挑战券", [150, 200, 260, 230], 0.96),
        ]
        op = _make_operationer(_FakeRecognizer(ocr_results=ocr_results))
        handler, result = _capture(
            self.logger,
            lambda: op.detect_element(
                _FakeElement("剩余挑战券", ElementType.OCR_AREA),
                match_text="挑战券", max_attempts=2, wait_time=0))
        self.assertTrue(result)
        records = self._summary_records(handler, "剩余挑战券")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].levelno, logging.DEBUG, "总述应为 DEBUG 级别")
        line = records[0].getMessage()
        self.assertIn("类型=OCR", line)
        self.assertIn("识别文本=['12'(0.98), '挑战券'(0.96)]", line)
        self.assertIn("匹配文本='挑战券'", line)
        self.assertIn("结果=命中", line)

        # 明细（排除总述本身）：1+N 条 → 1 条
        details = [r.getMessage() for r in handler.records
                   if r.levelno == logging.DEBUG
                   and not r.getMessage().startswith("[识别] 查找[")]
        self.assertEqual(len(details), 1,
                         f"OCR 明细应压成 1 条 DEBUG（原先 1+N 条）: {details}")
        self.assertIn("OCR 识别到 2 条", details[0])
        self.assertIn("挑战券", details[0])

    def test_coordinate_element_has_no_summary(self):
        """纯坐标元素没有匹配过程 → 不产生总述"""
        device = _FakeDevice(click_result=True)
        op = _make_operationer(_FakeRecognizer(), device)
        handler, result = _capture(
            self.logger,
            lambda: op.click_and_wait(
                _FakeElement("坐标点", ElementType.COORDINATE),
                wait_time=0, max_attempts=2))
        self.assertTrue(result)
        self.assertEqual([m for m in handler.messages
                          if m.startswith("[识别]")], [])

    def test_match_values_folded_when_too_many(self):
        """匹配值超过展示上限时折叠为计数（避免长重试把日志行拉长）"""
        text = _format_match_values([0.01 * i for i in range(12)])
        self.assertTrue(text.startswith("[0.00, 0.01"), text)
        self.assertIn("…共12次", text)
        self.assertNotIn("0.08", text, "第 9 个及之后的值应被折叠")

    def test_describe_without_match_values(self):
        """没有匹配值时的文案不出现异常数字"""
        metrics = _SearchMetrics(_FakeElement("坐标点", ElementType.COORDINATE))
        metrics.match_text = "坐标点"
        text = metrics.describe(hit=False)
        self.assertIn("最高匹配值=-", text)
        self.assertIn("匹配值=无", text)
        self.assertIn("结果=未命中", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
