from typing import List


class OcrText:
    """OCR 识别结果文本封装。

    Attributes:
        text (str): 识别文本
        box (List[int]): 归一化边界框，格式 [x, y, w, h]
        score (float): 置信度
    """

    def __init__(self, text: str, box: List[int], score: float = 0.0):
        self.text = text
        self.box = list(box)  # [x, y, w, h]
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
        x, y, w, h = self.box
        rx = max(0.0, min(1.0, ratio_x))
        ry = max(0.0, min(1.0, ratio_y))
        return int(x + w * rx), int(y + h * ry)

    def extract_numbers(self) -> List[int]:
        """提取文本中所有连续数字。"""
        import re
        return [int(n) for n in re.findall(r'\d+', self.text)]

    def __repr__(self) -> str:
        return (f"OcrText(text={self.text!r}, box={self.box}, "
                f"score={self.score:.3f})")