from typing import Optional

from PySide6.QtCore import QByteArray
from PySide6.QtGui import QPixmap, QImage

from tool.ResourceManager.model import Element


def element_to_qpixmap(element: Element, data_field: str = "bgra") -> Optional[QPixmap]:
    """
    将Element对象中的图像数据转换为QPixmap，支持bgra、gray（灰度图）、mask（二值图）

    Args:
        element: Element实例
        data_field: 要使用的图像数据字段（bgra/gray/mask）

    Returns: QPixmap对象或None（转换失败时）
    """
    # 校验输入
    if not element:
        return None

    # 校验数据字段合法性
    if data_field not in ["bgra", "gray", "mask"]:
        print(f"不支持的数据字段: {data_field}")
        return None

    # 获取指定字段的二进制数据
    image_data = getattr(element, data_field, None)
    if not image_data:
        print(f"元素的{data_field}字段数据为空")
        return None

    # 校验图像元数据（宽高必须存在）
    if not all([element.width, element.height]):
        print("元素缺少宽度或高度信息")
        return None

    try:
        q_byte_array = QByteArray(image_data)
        q_image = None

        if data_field == "bgra":
            # BGRA彩色图处理（4通道）

            # 用ARGB32格式加载后交换RGB通道
            q_image = QImage(
                q_byte_array.data(),
                element.width,
                element.height,
                element.width * 4,  # 每行字节数 = 宽度 × 4通道
                QImage.Format.Format_ARGB32
            )
            # q_image = q_image.rgbSwapped()  # BGRA -> RGBA转换

        elif data_field == "gray":
            # 灰度图处理（1通道，0-255取值）

            q_image = QImage(
                q_byte_array.data(),
                element.width,
                element.height,
                element.width * 1,  # 每行字节数 = 宽度 × 1通道
                QImage.Format.Format_Grayscale8
            )

        elif data_field == "mask":
            # 二值图处理（1通道，0或255取值）

            # 二值图本质是特殊的灰度图，用灰度图格式加载后可保持黑白效果
            q_image = QImage(
                q_byte_array.data(),
                element.width,
                element.height,
                element.width * 1,  # 每行字节数 = 宽度 × 1通道
                QImage.Format.Format_Grayscale8
            )

        if q_image and not q_image.isNull():
            return QPixmap.fromImage(q_image)
        else:
            print(f"无法创建{data_field}类型的QImage")
            return None

    except Exception as e:
        print(f"图像转换失败 ({data_field}): {str(e)}")
        return None
