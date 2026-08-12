import logging
from typing import Dict, List, Tuple, Union

from backend.utils import get_real_path
from backend.core.legacy.OnnxOcr.onnx_paddleocr import ONNXPaddleOcr



class OnnxOcr:
    """基于ONNX的OCR识别器，使用PaddleOCR模型进行文本检测和识别"""

    # OCR 模型已从 utils/ 迁移至 bin/ppocrv5（随 Release 包分发，避免热更新重复下载）
    det_model=get_real_path("bin/ppocrv5/det.onnx")
    rec_model=get_real_path("bin/ppocrv5/rec.onnx")
    rec_dict=get_real_path("bin/ppocrv5/ppocrv5_dict.txt")

    def __init__(self,parent_logger=None,use_gpu=False):
        self.logger = parent_logger.getChild(self.__class__.__name__) if parent_logger else logging.getLogger(self.__class__.__name__)
        self.engine = ONNXPaddleOcr(
        use_gpu=use_gpu,
        use_angle_cls=False,
        det_model_dir=str(self.det_model),
        rec_model_dir=str(self.rec_model),
        rec_char_dict_path=str(self.rec_dict),
    )
        
    def ocr(self, 
            image,
            box,
            image_size=(1600, 900),
            only_num=False,
            raw_json=False,
        ) -> Union[List[Dict], str]:
        """对输入图像进行OCR识别，并按需要还原坐标/过滤文本/格式化返回结果。"""
        raw_result = self.engine.ocr(image)

        # ONNXPaddleOcr 的返回结构通常为: [[ [box, [text, score]], ... ]]
        lines = raw_result[0] if isinstance(raw_result, list) and raw_result else []
        offset_x, offset_y = self._parse_crop_offset(box, image_size)

        results: List[Dict] = []
        for line in lines:
            if not isinstance(line, list) or len(line) < 2:
                continue

            det_box, rec = line[0], line[1]
            if not isinstance(rec, (list, tuple)) or len(rec) < 2:
                continue

            text = str(rec[0])
            score = float(rec[1])
            if only_num:
                text = self._extract_digits(text)
                if not text:
                    continue

            restored_box = self._restore_to_original(det_box, offset_x, offset_y)
            results.append({"text": text, "score": score, "box": restored_box})

        if raw_json:
            return results

        return "".join(item["text"] for item in results)

    def _parse_crop_offset(self, crop_box, image_size: Tuple[int, int]) -> Tuple[int, int]:
        """将裁剪区域 box 解析为原图上的左上角偏移量 (x, y)。"""
        width, height = image_size

        if not crop_box:
            return 0, 0

        # 支持 [x1, y1, x2, y2]
        if isinstance(crop_box, (list, tuple)) and len(crop_box) == 4 and not isinstance(crop_box[0], (list, tuple)):
            x1, y1 = float(crop_box[0]), float(crop_box[1])
            return self._to_abs_xy(x1, y1, width, height)

        # 支持 [[x1, y1], [x2, y2]]
        if isinstance(crop_box, (list, tuple)) and len(crop_box) >= 1 and isinstance(crop_box[0], (list, tuple)):
            x1, y1 = float(crop_box[0][0]), float(crop_box[0][1])
            return self._to_abs_xy(x1, y1, width, height)

        return 0, 0

    def _to_abs_xy(self, x: float, y: float, width: int, height: int) -> Tuple[int, int]:
        """将可能的归一化坐标转换为绝对像素坐标。"""
        if 0 <= x <= 1 and 0 <= y <= 1:
            return int(round(x * width)), int(round(y * height))
        return int(round(x)), int(round(y))

    def _restore_to_original(self, det_box, offset_x: int, offset_y: int):
        """把裁剪图坐标系中的检测框点位还原到原图坐标系。"""
        restored = []
        for point in det_box:
            x, y = point[0], point[1]
            restored.append([int(round(x + offset_x)), int(round(y + offset_y))])
        return restored

    def _extract_digits(self, text: str) -> str:
        """仅保留数字字符。"""
        return "".join(ch for ch in text if ch.isdigit())
