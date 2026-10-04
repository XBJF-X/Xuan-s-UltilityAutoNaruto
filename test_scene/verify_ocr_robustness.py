# -*- coding: utf-8 -*-
"""验证：OCR 结果封装健壮性 + area_ocr 增强候选阶梯（2026-09-15）

覆盖：
  [1] `OcrText` 字段容错（None text/box、NaN score、点位序列 box、比例越界/NaN）
  [2] `OcrResultList` 方法矩阵（空表 / 多数字 / strict 开关 / 容错输入 / 别名 / 安全取值）
  [3] `Operationer.ocr_recognize` 恒返回 `OcrResultList`（空结果也是空表，bool=False）
  [4] `area_ocr` 增强阶梯（真实 ONNX + 实拍截图，样本缺失时 SKIP）：
      - 修复后 ROI（553/761/110×78）首级即读出数字 "9"
      - 修复前 ROI（577/768/82×111）下增强级兜底读出 "9"，并与 "过期" 正确去重
      - `enable_ocr_enhance=False` → 回退旧行为（只剩 "过期"）：证明可一键回退、零回归
  [5] "原本识别正常"的 OCR 元素回归：首级已含数字时，增强开/关结果必须完全一致

运行：.venv\\Scripts\\python.exe -X utf8 test_scene\\verify_ocr_robustness.py
（全部通过打印 "ALL PASS (n 项)"；任一断言失败抛 AssertionError）
"""
import copy
import logging
import os
import sys
import types
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

logging.basicConfig(level=logging.CRITICAL)  # 容错路径会记 WARNING，这里静默以免刷屏

from backend.core.legacy.Enums import ElementType                      # noqa: E402
from backend.core.legacy.Operationer import Operationer                # noqa: E402
from backend.core.legacy.OcrText import (                              # noqa: E402
    OcrResultList,
    OcrText,
    OcrTextList,
)

_PASS = [0]
_SKIP = [0]

# 实拍样本（用户提供的"秘境探险-匹配 / 剩余挑战券数量=9"截图）；缺失则跳过相关用例
_SAMPLE_SCREENSHOT = Path(r"C:\Users\ATRI_Robots\Desktop"
                          r"\0A613E73C75A8F0807D66525CE6DAF8F.png")
_TZQ_SCENE = "秘境探险-匹配"
_TZQ_ELEMENT = "剩余挑战券数量"
# 修复前的 ROI（数据层修复时的旧值），用于验证"增强级兜底"这条链路
_LEGACY_ROI = {"roi_x": 577, "roi_y": 768, "roi_width": 82, "roi_height": 111}


def check(cond: bool, msg: str):
    assert cond, f"FAIL: {msg}"
    _PASS[0] += 1
    print(f"  PASS: {msg}")


def skip(msg: str):
    _SKIP[0] += 1
    print(f"  SKIP: {msg}")


def _texts(results):
    return sorted(text for text, _box, _score in results)


# ============================== [1] OcrText 容错 ==============================
print("[1] OcrText 字段容错")
_empty = OcrText(None, None, None)
check(_empty.text == "" and _empty.box == [0, 0, 0, 0] and _empty.score == 0.0,
      "text/box/score 为 None 时归一为 ''/[0,0,0,0]/0.0（不抛异常）")
check(not _empty and _empty.extract_numbers() == []
      and _empty.first_number() is None,
      "空文本：bool=False、无数字、first_number()=None")

_nan = OcrText("abc", [10, 20, 30, 40], float("nan"))
check(_nan.score == 0.0 and _nan.box == [10, 20, 30, 40],
      "score=NaN 归一为 0.0")

_points = OcrText("x", [[5, 6], [25, 36], [25, 6], [5, 36]], 0.5)
check(_points.box == [5, 6, 25, 36], "点位序列 box 归一为外接矩形")

check(OcrText("x", [1, 2], 0.5).box == [0, 0, 0, 0],
      "box 长度不足 → 兜底 [0,0,0,0]（不抛异常）")
check(OcrText("x", [30, 40, 10, 20], 0.5).box == [10, 20, 30, 40],
      "box 逆序自动升序归一")
check(OcrText("x", "bad-box", 0.5).box == [0, 0, 0, 0],
      "box 为不可解析字符串 → 兜底 [0,0,0,0]")

_inner = OcrText("x", [10, 20, 30, 40])
check(_inner.get_inner_point(0.5, 0.5) == (20, 30), "get_inner_point 中心点正确")
check(_inner.get_inner_point(5, -3) == (30, 20), "get_inner_point 比例越界限幅 [0,1]")
check(_inner.get_inner_point(float("nan"), 0.5) == (20, 30),
      "get_inner_point 比例 NaN 回落 0.5")

_numbers = OcrText("5/50", [0, 0, 1, 1], 0.9)
check(_numbers.extract_numbers() == [5, 50] and _numbers.first_number() == 5,
      "extract_numbers 保持 '5/50' -> [5, 50] 语义，first_number()=5")
check(_numbers.has_number(50) and not _numbers.has_number(7),
      "OcrText.has_number 单条判定正确")


# ========================== [2] OcrResultList 方法矩阵 ==========================
print("[2] OcrResultList 方法矩阵")
_empty_list = OcrResultList()
check(isinstance(_empty_list, OcrResultList) and len(_empty_list) == 0
      and not _empty_list and _empty_list.is_empty(),
      "空构造：len=0 / bool=False / is_empty()=True")
check(_empty_list.texts() == [] and _empty_list.extract_all_numbers() == []
      and _empty_list.get_first_number() is None
      and _empty_list.get_number(3) is None
      and _empty_list.get_single_number() is None,
      "空表：文本/数字提取与取值全部安全返回（不抛异常）")
check(_empty_list.first() is None and _empty_list.best() is None
      and _empty_list.safe_get(0) is None,
      "空表：first()/best()/safe_get() 返回 None（不抛 IndexError）")
check(OcrTextList is OcrResultList, "OcrTextList 是 OcrResultList 的别名")

check(OcrResultList([("5/50", [1, 2, 3, 4], 0.9)]).texts() == ["5/50"],
      "容错：元组项 (text, box, score) 自动包装为 OcrText")
check(OcrResultList(123).is_empty(), "容错：不可迭代输入按空表处理")
check(OcrResultList([None, 42, "x"]).is_empty(),
      "容错：非法结果项被跳过（不抛异常）")

_two = OcrResultList([OcrText("12", [0, 0, 10, 10], 0.9),
                      OcrText("7", [20, 0, 30, 10], 0.8)])
check(_two.extract_all_numbers() == [12, 7] and _two.get_first_number() == 12
      and _two.get_number(1) == 7 and _two.get_number(9) is None,
      "多数字：extract_all_numbers / get_first_number / get_number 正确")
check(_two.get_single_number() is None,
      "多数字：get_single_number() 仍返回 None（语义不变）")
check(_two.is_greater_than(10) is False and _two.is_less_than(10) is False
      and _two.is_equal_to(10) is False,
      "多数字 + strict=False（默认）：比较返回 False，不抛 ValueError")
_raised = False
try:
    _two.is_greater_than(10, strict=True)
except ValueError:
    _raised = True
check(_raised, "多数字 + strict=True：仍抛 ValueError（兼容旧严格语义）")

_single = OcrResultList([OcrText("12", [0, 0, 10, 10], 0.9)])
check(_single.is_greater_than(10) and _single.is_less_than(20)
      and _single.is_equal_to(12) and _single.get_single_number() == 12,
      "唯一数字：比较方法与 get_single_number() 正确")
check(_single.first().text == "12" and _single.best().score == 0.9
      and _single[0].text == "12" and list(_single)[0].text == "12",
      "first()/best()/索引/迭代 均可用")


# ==================== [3] ocr_recognize 恒返回 OcrResultList ====================
print("[3] Operationer.ocr_recognize 恒返回 OcrResultList")
_op = object.__new__(Operationer)
_op.task_name = "verify"
_op.logger = logging.getLogger("verify.ocr")
_op.current_scene = None
_op.device = types.SimpleNamespace(screen_cap=lambda: None)
_op.recognizer = types.SimpleNamespace(area_ocr=lambda img, el, dbg=False: [])
_element = types.SimpleNamespace(type=ElementType.OCR_AREA, name="占位区域")
_empty_result = _op.ocr_recognize(_element)
check(isinstance(_empty_result, OcrResultList) and not _empty_result
      and _empty_result.get_first_number() is None,
      "无识别结果时返回空 OcrResultList（不再是裸 []，消除 AttributeError 隐患）")

_op.recognizer.area_ocr = lambda img, el, dbg=False: [
    ("9", [1, 2, 3, 4], 0.9), ("过期", [5, 6, 7, 8], 0.95)]
_hit_result = _op.ocr_recognize(_element)
check(isinstance(_hit_result, OcrResultList)
      and _hit_result.get_first_number() == 9
      and _hit_result.texts()[0] == "过期",
      "有结果时按置信度降序返回 OcrResultList，可直接取数字")


# ============ [4]/[5] area_ocr 增强阶梯 + 原本正常元素零回归（真实模型） ============
print("[4]/[5] area_ocr 增强阶梯与零回归（真实 ONNX 模型）")
_MODEL_OK = all((_REPO_ROOT / "bin" / "ppocrv5" / name).exists()
                for name in ("det.onnx", "rec.onnx", "ppocrv5_dict.txt"))
_setup_ok = False
if not _MODEL_OK:
    skip("ONNX 模型缺失（bin/ppocrv5/），跳过真实识别用例")
else:
    try:
        import cv2
        from backend.core.legacy.Recognizer import Recognizer
        from backend.core.legacy.Scene.SceneGraph import SceneGraph
        from backend.tools.resource_db import ResourceDBManager
        _graph = SceneGraph(ResourceDBManager())
        _setup_ok = True
    except Exception as exc:                       # noqa: BLE001 - 验证脚本打印原因即可
        skip(f"识别链路初始化失败：{exc}")


def _signature(results):
    """识别结果签名（文本 + 框），用于比较两级链路是否给出相同结果。"""
    return sorted((text, tuple(box)) for text, box, _score in results)


if _setup_ok and not _SAMPLE_SCREENSHOT.exists():
    skip(f"实拍样本不存在（{_SAMPLE_SCREENSHOT}），跳过阶梯用例")

if _setup_ok and _SAMPLE_SCREENSHOT.exists():
    print("[4] 实拍样本：修复后 ROI 首级命中 / 旧 ROI 增强兜底 / 开关可回退")
    _image = cv2.imread(str(_SAMPLE_SCREENSHOT))
    check(_image is not None, "读取实拍样本截图")
    _tzq = _graph.get_element(_TZQ_SCENE, _TZQ_ELEMENT)
    if _tzq is None:
        skip(f"资源库未找到 [{_TZQ_SCENE}/{_TZQ_ELEMENT}]，跳过阶梯用例")
    else:
        print(f"  (当前 ROI: {_tzq.roi_x},{_tzq.roi_y},"
              f"{_tzq.roi_width}×{_tzq.roi_height})")
        _primary = Recognizer(_graph).area_ocr(_image, _tzq)
        check("9" in [t for t, _b, _s in _primary],
              f"修复后 ROI 首级即读出数字 9（结果={_texts(_primary)}）")
        check(all(_tzq.roi_x <= box[0] and box[2] <= _tzq.roi_x + _tzq.roi_width
                  and _tzq.roi_y <= box[1]
                  and box[3] <= _tzq.roi_y + _tzq.roi_height
                  for _t, box, _s in _primary),
              "首级识别框全部落在 ROI 内（预放大坐标还原正确）")

        _legacy = copy.copy(_tzq)
        for _key, _value in _LEGACY_ROI.items():
            setattr(_legacy, _key, _value)
        _with_ladder = Recognizer(_graph).area_ocr(_image, _legacy)
        _without = Recognizer(_graph, enable_ocr_enhance=False).area_ocr(
            _image, _legacy)
        check("9" in [t for t, _b, _s in _with_ladder],
              f"旧 ROI 下增强级兜底读出 9（结果={_texts(_with_ladder)}）")
        check("过期" in [t for t, _b, _s in _with_ladder]
              and "天过期" not in [t for t, _b, _s in _with_ladder],
              "增强级噪声（天过期）被同位置去重丢弃，高分文本保留")
        check("9" not in [t for t, _b, _s in _without]
              and _texts(_without) == ["过期"],
              f"enable_ocr_enhance=False 回退旧行为（结果={_texts(_without)}）")

if _setup_ok:
    print("[5] 原本识别正常的 OCR 元素：增强开/关结果一致")
    # 底图是中文文件名：必须用项目封装的 cv_imread（cv2.imread 在 Windows 打不开中文路径）
    from backend.utils import cv_imread
    _candidates = []
    for _scene in _graph.scenes.values():
        _base = _REPO_ROOT / "test_scene" / f"{_scene.name}.png"
        if not _base.exists():
            continue
        for _ele in _scene.elements:
            if _ele.type == ElementType.OCR_AREA:
                _candidates.append((_scene.name, _ele, _base))
    print(f"  (候选 {len(_candidates)} 个，最多评估 10 张底图)")
    _runs = 0
    _asserted = 0
    for _scene_name, _ele, _base in _candidates:
        if _runs >= 10:
            break
        _base_img = cv_imread(str(_base))
        if _base_img is None:
            skip(f"底图读取失败：{_base.name}")
            continue
        _off = Recognizer(_graph, enable_ocr_enhance=False).area_ocr(
            _base_img, _ele)
        _runs += 1
        if not any(ch.isdigit() for t, _b, _s in _off for ch in t):
            continue        # 首级无数字：按设计会启用增强级，不做一致性断言
        _on = Recognizer(_graph).area_ocr(_base_img, _ele)
        _asserted += 1
        check(_signature(_on) == _signature(_off),
              f"[{_scene_name}/{_ele.name}] 首级含数字 → 增强开/关结果一致"
              f"（{_texts(_off)}）")
    if _asserted == 0:
        skip("评估样本中没有'首级即含数字'的底图，未产生一致性断言")


# ======== [6] MiJingTanXian 剩余挑战券流程（重试 / 未知降级 / 挑战券不足收尾） ========
print("[6] MiJingTanXian 剩余挑战券读取与降级策略（假操作器）")
from backend.core.legacy.Exceptions import TaskCompleted           # noqa: E402
from backend.core.legacy.Task import MiJingTanXian as _mjtx_mod    # noqa: E402
from backend.core.legacy.Task.MiJingTanXian import MiJingTanXian   # noqa: E402

# 让重试间隔不真的 sleep（不改生产代码，只替换模块引用）
_mjtx_mod.time = types.SimpleNamespace(sleep=lambda _seconds: None)

_MATCH_SCENE = "秘境探险-匹配"


class _FakeOperationer:
    """按"每次 OCR 返回的数字序列"驱动 MiJingTanXian 的假操作器。"""

    def __init__(self, number_batches, zero_template=False,
                 no_ticket_tip=False, no_ticket_element=True):
        self._batches = [list(batch) for batch in number_batches]
        self.zero_template = zero_template       # [剩余挑战券-0] 图片元素是否命中
        self.no_ticket_tip = no_ticket_tip       # [挑战券不足] 是否命中
        self.no_ticket_element = no_ticket_element   # [挑战券不足] 元素是否存在
        self.ocr_calls = 0
        self.clicks = []
        self.clicker = types.SimpleNamespace(stop=lambda: None)

    def ocr_recognize(self, element, **kwargs):
        self.ocr_calls += 1
        numbers = self._batches.pop(0) if self._batches else []
        return OcrResultList([OcrText(str(n), [0, 0, 10, 10], 0.9)
                              for n in numbers])

    def get_element(self, name, scene=None):
        if name == "剩余挑战券-0":
            return types.SimpleNamespace(name=name) if self.zero_template else None
        if name == "挑战券不足":
            return (types.SimpleNamespace(name=name)
                    if self.no_ticket_element else None)
        return None

    def detect_element(self, element, **kwargs):
        if element.name == "剩余挑战券-0":
            return self.zero_template
        return self.no_ticket_tip

    def click_and_wait(self, element, **kwargs):
        self.clicks.append(element)
        return True


def _make_mjtx_task(operationer):
    task = object.__new__(MiJingTanXian)
    task.logger = logging.getLogger("verify.mjtx")
    task.operationer = operationer
    task.fighting = False
    task.bool_click = False
    return task


def _run_match_scene(task):
    return MiJingTanXian.transition_func[_MATCH_SCENE](task)


_task = _make_mjtx_task(_FakeOperationer([[9]]))
check(_run_match_scene(_task) is False
      and _task.operationer.clicks == ["出战"] and _task.bool_click is True,
      "读到 9：点[出战]后 return False（继续流程）")

_task = _make_mjtx_task(_FakeOperationer([[0]]))
_raised = False
try:
    _run_match_scene(_task)
except TaskCompleted:
    _raised = True
check(_raised and _task.operationer.clicks == [],
      "读到 0：抛 TaskCompleted（不再点出战）")

_task = _make_mjtx_task(_FakeOperationer([[], [], [3]]))
check(_run_match_scene(_task) is False
      and _task.operationer.ocr_calls == 3
      and _task.operationer.clicks == ["出战"],
      "前两次读不到数字 → 重试第 3 次读到 3 后继续（含 IndexError 修复）")

_task = _make_mjtx_task(_FakeOperationer([[], [], []], zero_template=True))
_raised = False
try:
    _run_match_scene(_task)
except TaskCompleted:
    _raised = True
check(_raised and _task.operationer.clicks == [],
      "3 次都读不到 + 命中[剩余挑战券-0]模板 → 判定券耗尽并结束")

_task = _make_mjtx_task(_FakeOperationer([[], [], []], no_ticket_tip=True))
_raised = False
try:
    _run_match_scene(_task)
except TaskCompleted:
    _raised = True
check(_raised and _task.operationer.clicks == ["出战"],
      "3 次都读不到 → 按未知继续点[出战]，检测到[挑战券不足]后结束")

_task = _make_mjtx_task(_FakeOperationer([[], [], []]))
check(_run_match_scene(_task) is False
      and _task.operationer.clicks == ["出战"],
      "3 次都读不到且无任何提示 → 仍点[出战]并 return False（不中断任务）")

_task = _make_mjtx_task(_FakeOperationer([[], [], []], no_ticket_element=False))
check(_run_match_scene(_task) is False
      and _task.operationer.clicks == ["出战"],
      "[挑战券不足]元素未配置时安全跳过该判据（不抛异常）")


print(f"\nALL PASS ({_PASS[0]} 项)" + (f" | SKIP {_SKIP[0]} 项" if _SKIP[0] else ""))



