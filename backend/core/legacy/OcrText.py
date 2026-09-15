# -*- coding: utf-8 -*-
"""OCR 识别结果封装：`OcrText`（单条）与 `OcrResultList`（结果列表，别名 `OcrTextList`）。

## 健壮性约定（2026-09-15 改造）
识别层（`Recognizer.area_ocr` / `Operationer._ocr_results`）送进来的字段可能残缺：
模型少字段、box 点数不足、score 为 None/NaN、甚至整条不是 `OcrText`。这些情况
**不应**打断任务执行，统一在封装层做类型归一 + WARNING 留痕（不使用 `pass` 静默吞掉）。

数字类方法**默认不抛异常**（`strict=False`）：数字个数不符合预期时记 WARNING 并返回
安全值（`None` / `False`），避免"OCR 读出两个数字"就把整个任务炸掉；需要严格语义的
调用方显式传 `strict=True`（仍抛 `ValueError`，保持旧行为可用）。
"""
import logging
import math
import re
from typing import Iterable, Iterator, List, Optional, Sequence

logger = logging.getLogger("OcrText")

# 连续数字串（保持与历史行为一致："5/50" -> [5, 50]）
_NUMBER_RE = re.compile(r"\d+")

# box 归一失败时的兜底值（全 0 表示"无有效位置信息"）
_EMPTY_BOX = [0, 0, 0, 0]


def _normalize_text(text) -> str:
    """任意输入归一为 str（None -> ""）。"""
    if text is None:
        return ""
    if isinstance(text, str):
        return text
    return str(text)


def _normalize_score(score) -> float:
    """任意输入归一为有限 float（None/NaN/inf/非数值 -> 0.0）。"""
    try:
        value = float(score)
    except (TypeError, ValueError):
        logger.warning("OCR 置信度非数值（%r），按 0.0 处理", score)
        return 0.0
    if math.isnan(value) or math.isinf(value):
        logger.warning("OCR 置信度非法（%r），按 0.0 处理", value)
        return 0.0
    return value


def _normalize_box(box) -> List[int]:
    """把任意 box 表示归一为 `[x1, y1, x2, y2]`（升序）。

    支持：扁平序列 `[x1, y1, x2, y2]`、检测框点位序列 `[[x, y], ...]`（取外接矩形）。
    无法解析时返回 `[0, 0, 0, 0]` 并记 WARNING（不抛异常）。
    """
    if box is None:
        logger.warning("OCR 文本框为空（None），按 %s 处理", _EMPTY_BOX)
        return list(_EMPTY_BOX)
    try:
        values = list(box)
    except TypeError:
        logger.warning("OCR 文本框不可迭代（%r），按 %s 处理", box, _EMPTY_BOX)
        return list(_EMPTY_BOX)

    # 点位序列：[[x1, y1], [x2, y2], ...] -> 外接矩形
    if values and all(isinstance(point, (list, tuple)) for point in values):
        xs, ys = [], []
        for point in values:
            if len(point) < 2:
                continue
            xs.append(float(point[0]))
            ys.append(float(point[1]))
        if xs and ys:
            return [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))]
        logger.warning("OCR 文本框点位不足（%r），按 %s 处理", box, _EMPTY_BOX)
        return list(_EMPTY_BOX)

    if len(values) < 4:
        logger.warning("OCR 文本框长度不足（%r），按 %s 处理", box, _EMPTY_BOX)
        return list(_EMPTY_BOX)

    try:
        x1, y1, x2, y2 = (int(float(values[i])) for i in range(4))
    except (TypeError, ValueError):
        logger.warning("OCR 文本框含非数值（%r），按 %s 处理", box, _EMPTY_BOX)
        return list(_EMPTY_BOX)

    return [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]


def _normalize_ratio(ratio, default: float = 0.5) -> float:
    """比例归一：非数值/NaN -> default，其余限幅到 [0, 1]。"""
    try:
        value = float(ratio)
    except (TypeError, ValueError):
        return default
    if math.isnan(value):
        return default
    return max(0.0, min(1.0, value))


class OcrText:
    """OCR 识别结果文本封装。

    Attributes:
        text (str): 识别文本（None/非 str 自动归一）
        box (List[int]): 边界框，格式 [x1, y1, x2, y2]
        score (float): 置信度（None/NaN 自动归一为 0.0）
    """

    def __init__(self, text: str, box: Sequence, score: float = 0.0):
        self.text = _normalize_text(text)
        self.box = _normalize_box(box)  # [x1, y1, x2, y2]
        self.score = _normalize_score(score)

    def get_inner_point(self, ratio_x: float = 0.5,
                        ratio_y: float = 0.5) -> tuple:
        """返回框内比例位置像素坐标。

        Args:
            ratio_x: 水平比例，范围 [0, 1]（越界限幅，非法值回落 0.5）
            ratio_y: 垂直比例，范围 [0, 1]（同上）

        Returns:
            (x, y) 绝对像素坐标；box 无有效信息时返回其中心（即原值），不抛异常
        """
        x1, y1, x2, y2 = self.box
        rx = _normalize_ratio(ratio_x)
        ry = _normalize_ratio(ratio_y)
        return int(x1 + (x2 - x1) * rx), int(y1 + (y2 - y1) * ry)

    def extract_numbers(self) -> List[int]:
        """提取文本中所有连续数字（异常时返回空列表，不打断任务）。"""
        try:
            return [int(n) for n in _NUMBER_RE.findall(self.text)]
        except Exception as e:  # 理论上不可达；留痕而非静默
            logger.warning("提取数字失败（text=%r）：%s", self.text, e)
            return []

    def first_number(self) -> Optional[int]:
        """首个连续数字；没有则返回 None。"""
        numbers = self.extract_numbers()
        return numbers[0] if numbers else None

    def has_number(self, target_number: int) -> bool:
        """文本中是否包含指定数字。"""
        return target_number in self.extract_numbers()

    def __bool__(self) -> bool:
        return bool(self.text.strip())

    def __repr__(self) -> str:
        return (f"OcrText(text={self.text!r}, box={self.box}, "
                f"score={self.score:.3f})")


class OcrResultList:
    """OCR 识别结果列表的包装类，提供便捷的数字提取与判断方法。

    可像列表一样迭代/取长度/索引；空结果同样返回本对象（`bool()` 为 False），
    调用方不必区分"空列表"与"结果列表"两种类型。
    """

    def __init__(self, ocr_texts: Optional[Iterable] = None):
        self._items: List[OcrText] = []
        if ocr_texts is None:
            return
        try:
            items = list(ocr_texts)
        except TypeError:
            logger.warning("OCR 结果不可迭代（%r），按空结果处理", ocr_texts)
            return
        for item in items:
            if isinstance(item, OcrText):
                self._items.append(item)
                continue
            # 容错：允许直接送 (text, box) / (text, box, score) 元组
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                score = item[2] if len(item) >= 3 else 0.0
                self._items.append(OcrText(item[0], item[1], score))
                continue
            logger.warning("跳过非 OCR 结果项（%r）", item)

    # ------------------------------------------------------------ 数字提取

    def extract_all_numbers(self) -> List[int]:
        """提取所有识别文本中出现的连续数字（保持出现顺序）。"""
        numbers: List[int] = []
        for ocr_text in self._items:
            numbers.extend(ocr_text.extract_numbers())
        return numbers

    def has_number(self, target_number: int) -> bool:
        """判断识别结果中是否包含指定的数字。"""
        return target_number in self.extract_all_numbers()

    def get_single_number(self) -> Optional[int]:
        """如果识别结果中恰好只有一个数字，则返回该数字；否则返回 None。"""
        numbers = self.extract_all_numbers()
        return numbers[0] if len(numbers) == 1 else None

    def get_number(self, index: int = 0) -> Optional[int]:
        """取第 index 个提取到的数字（越界返回 None，不抛 IndexError）。"""
        numbers = self.extract_all_numbers()
        if len(numbers) <= index or index < -len(numbers):
            return None
        return numbers[index]

    def get_first_number(self) -> Optional[int]:
        """首个提取到的数字（= `get_number(0)`）；没有则 None。"""
        return self.get_number(0)

    # ------------------------------------------------------------ 比较方法
    #
    # 默认 strict=False：数字个数不为 1 时记 WARNING 并返回 False（不炸任务）；
    # strict=True 保持旧语义（抛 ValueError），供确需严格判定的调用方使用。

    def _strict_or_false(self, strict: bool, action: str) -> bool:
        if strict:
            raise ValueError("识别结果中数字个数不为 1，无法进行大小比较")
        logger.warning("识别结果数字个数不为 1（%r），无法%s，按 False 处理",
                       self.texts(), action)
        return False

    def is_greater_than(self, target: int, strict: bool = False) -> bool:
        """判断识别结果中的唯一数字是否大于给定数字。"""
        num = self.get_single_number()
        if num is None:
            return self._strict_or_false(strict, "比较大小")
        return num > target

    def is_less_than(self, target: int, strict: bool = False) -> bool:
        """判断识别结果中的唯一数字是否小于给定数字。"""
        num = self.get_single_number()
        if num is None:
            return self._strict_or_false(strict, "比较大小")
        return num < target

    def is_equal_to(self, target: int, strict: bool = False) -> bool:
        """判断识别结果中的唯一数字是否等于给定数字（与 has_number 类似但严格要求唯一）。"""
        num = self.get_single_number()
        if num is None:
            return self._strict_or_false(strict, "比较大小")
        return num == target

    # ------------------------------------------------------------ 通用取值

    def first(self) -> Optional[OcrText]:
        """第一条识别结果（空表返回 None）。"""
        return self._items[0] if self._items else None

    def best(self) -> Optional[OcrText]:
        """置信度最高的结果（空表返回 None）。"""
        if not self._items:
            return None
        return max(self._items, key=lambda item: item.score)

    def texts(self) -> List[str]:
        """全部识别文本（便于日志与断言）。"""
        return [item.text for item in self._items]

    def is_empty(self) -> bool:
        """是否没有任何识别结果。"""
        return not self._items

    def safe_get(self, index: int) -> Optional[OcrText]:
        """按索引取值，越界返回 None（不抛 IndexError）。"""
        if -len(self._items) <= index < len(self._items):
            return self._items[index]
        return None

    # 以下方法使对象可以像列表一样使用
    def __iter__(self) -> Iterator[OcrText]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def __bool__(self) -> bool:
        return bool(self._items)

    def __repr__(self) -> str:
        return f"OcrResultList({self._items!r})"


# 兼容命名：本类即"OCR 文本列表"（文档/调用方常称其为 OcrTextList）
OcrTextList = OcrResultList
