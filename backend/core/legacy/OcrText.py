from typing import List, Iterator


class OcrText:
    """OCR 识别结果文本封装。

    Attributes:
        text (str): 识别文本
        box (List[int]): 边界框，格式 [x1, y1, x2, y2]
        score (float): 置信度
    """

    def __init__(self, text: str, box: List[int], score: float = 0.0):
        self.text = text
        self.box = list(box)  # [x1, y1, x2, y2]
        self.score = score

    def get_inner_point(self, ratio_x: float = 0.5,
                        ratio_y: float = 0.5) -> tuple:
        """返回框内比例位置像素坐标。

        Args:
            ratio_x: 水平比例，范围 [0, 1]
            ratio_y: 垂直比例，范围 [0, 1]

        Returns:
            (x, y) 绝对像素坐标
        """
        x1, y1, x2, y2 = self.box
        rx = max(0.0, min(1.0, ratio_x))
        ry = max(0.0, min(1.0, ratio_y))
        return int(x1 + (x2 - x1) * rx), int(y1 + (y2 - y1) * ry)

    def extract_numbers(self) -> List[int]:
        """提取文本中所有连续数字。"""
        import re
        return [int(n) for n in re.findall(r'\d+', self.text)]

    def __repr__(self) -> str:
        return (f"OcrText(text={self.text!r}, box={self.box}, "
                f"score={self.score:.3f})")


from typing import List, Iterator, Optional

class OcrResultList:
    """OCR 识别结果列表的包装类，提供便捷的数字提取与判断方法。"""

    def __init__(self, ocr_texts: List[OcrText]):
        self._items = ocr_texts

    def extract_all_numbers(self) -> List[int]:
        """提取所有识别文本中出现的连续数字（保持出现顺序）。"""
        numbers = []
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

    def is_greater_than(self, target: int, strict: bool = True) -> bool:
        """判断识别结果中的唯一数字是否大于给定数字。

        Args:
            target: 要比较的目标数字。
            strict: 若为 True，当数字个数不为 1 时抛出 ValueError；否则返回 False。

        Returns:
            若唯一数字存在且大于 target，返回 True；否则返回 False。
        """
        num = self.get_single_number()
        if num is None:
            if strict:
                raise ValueError("识别结果中数字个数不为 1，无法进行大小比较")
            return False
        return num > target

    def is_less_than(self, target: int, strict: bool = True) -> bool:
        """判断识别结果中的唯一数字是否小于给定数字。"""
        num = self.get_single_number()
        if num is None:
            if strict:
                raise ValueError("识别结果中数字个数不为 1，无法进行大小比较")
            return False
        return num < target

    def is_equal_to(self, target: int, strict: bool = True) -> bool:
        """判断识别结果中的唯一数字是否等于给定数字（与 has_number 类似但严格要求唯一）。"""
        num = self.get_single_number()
        if num is None:
            if strict:
                raise ValueError("识别结果中数字个数不为 1，无法进行大小比较")
            return False
        return num == target

    # 以下方法使对象可以像列表一样使用
    def __iter__(self) -> Iterator[OcrText]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def __repr__(self) -> str:
        return f"OcrResultList({self._items!r})"