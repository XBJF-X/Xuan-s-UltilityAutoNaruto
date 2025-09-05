import ctypes
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from PySide6.QtCore import Qt, QByteArray
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QImage

from tool.ResourceManager.model import Element


def resource_path(relative_path):
    """
    获取程序解压到的临时目录的文件的位置
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    # 强制转换为长路径（仅限Windows）
    if sys.platform.startswith('win'):
        from ctypes import windll, create_unicode_buffer
        try:
            buf = create_unicode_buffer(512)
            windll.kernel32.GetLongPathNameW(base_path, buf, 512)
            base_path = buf.value
        except Exception:
            pass
    # print(base_path)
    full_path = os.path.normpath(os.path.join(base_path, relative_path))
    return full_path


def get_real_path(relative_path=""):
    """
    获取基于可执行文件位置的绝对路径

    参数:
        relative_path: 相对于可执行文件的相对路径，默认为返回可执行文件所在目录）

    返回:
        基于可执行文件位置的绝对路径
    """
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件
        if sys.platform == 'win32':
            # Windows平台获取可执行文件路径
            buf = ctypes.create_unicode_buffer(1024)
            ctypes.windll.kernel32.GetModuleFileNameW(None, buf, 1024)
            exe_dir = os.path.dirname(os.path.abspath(buf.value))
        else:
            # 其他平台获取可执行文件路径
            exe_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    else:
        # 如果是普通Python脚本运行
        exe_dir = os.path.dirname(os.path.abspath(__file__))

    # 组合路径并规范化
    return os.path.normpath(os.path.join(exe_dir, relative_path))


def cv_save(image_path, image_array, params=None):
    """
    image_array:图像数组；image_path:图像的保存全路径
    """
    if params is None:
        params = [
            cv2.IMWRITE_PNG_COMPRESSION,
            0  # 压缩等级0-9
        ]
    cv2.imencode('.png', image_array, params)[1].tofile(image_path)


def cv_imread(file_path):
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    return cv_img


def extract_diamond_region(image):
    """
    截取图像中的正菱形区域，其他区域置为0

    :param image: 输入的BGR图像或灰度图像
    :return: 只保留正菱形区域的图像（与输入图像通道数相同）
    """
    # 获取图像尺寸
    height, width = image.shape[:2]
    # 检查图像是否为单通道（灰度图像）
    is_gray = len(image.shape) == 2

    # 创建与图像相同大小的单通道黑色掩膜
    mask = np.zeros((height, width), dtype=np.uint8)

    # 计算菱形的四个顶点坐标
    # 菱形中心点
    center_x, center_y = width // 2, height // 2

    # 计算菱形的半径（取宽高中较小值的一半）
    radius = min(width, height) // 2

    # 菱形的四个顶点（上、右、下、左）
    top = (center_x, center_y - radius)
    right = (center_x + radius, center_y)
    bottom = (center_x, center_y + radius)
    left = (center_x - radius, center_y)

    # 创建菱形轮廓
    diamond_pts = np.array([top, right, bottom, left], dtype=np.int32)

    # 在掩膜上绘制填充的菱形
    cv2.fillPoly(mask, [diamond_pts], color=255)

    if is_gray:
        # 对于灰度图像，直接使用单通道掩膜进行按位与操作
        result = cv2.bitwise_and(image, mask)
    else:
        # 对于BGR图像，将掩膜转换为三通道，以便与BGR图像进行按位与操作
        mask_bgr = cv2.merge([mask, mask, mask])
        result = cv2.bitwise_and(image, mask_bgr)

    # 保存处理后的图像（可根据需要注释掉）
    # cv2.imwrite(f"F:/PyProject/ImageMatch/temp/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')}.png", result)
    return result


def create_rounded_pixmap(pixmap: QPixmap, radius: int) -> QPixmap:
    """带圆角的 QPixmap"""
    if pixmap.isNull():  # 不处理空数据或者错误数据
        return pixmap

    # 获取图片原始尺寸
    original_width = pixmap.width()
    original_height = pixmap.height()

    # 创建与目标尺寸一致的 QPixmap
    dest_image = QPixmap(radius, radius)
    dest_image.fill(Qt.transparent)

    painter = QPainter(dest_image)
    painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
    painter.setRenderHint(QPainter.SmoothPixmapTransform)  # 平滑处理

    # 裁剪成圆形
    path = QPainterPath()
    path.addEllipse(0, 0, radius, radius)
    painter.setClipPath(path)

    # 计算缩放比例，保证图片显示区域完整
    scale_width = radius / original_width
    scale_height = radius / original_height
    scale = min(scale_width, scale_height)

    # 计算缩放后的尺寸
    scaled_width = int(original_width * scale)
    scaled_height = int(original_height * scale)

    # 绘制图片，居中显示在圆形区域内
    painter.drawPixmap(
        (radius - scaled_width) // 2,
        (radius - scaled_height) // 2,
        scaled_width,
        scaled_height,
        pixmap
    )

    painter.end()
    return dest_image


def split_gray_alpha(input_path, output_bgra_path=None, output_gray_path=None, output_mask_path=None):
    """
    将PNG分离为灰度图和掩码图（分别保存为单通道PNG）
    """
    try:
        # 读取原图（保留所有通道）
        img = cv_imread(input_path)
        if img is None:
            raise FileNotFoundError(f"无法读取图片: {input_path}")

        # 提取灰度通道
        if img.shape[-1] in (3, 4):  # 彩色图（带或不带Alpha）
            gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY)
        else:  # 已为灰度图
            gray = img if len(img.shape) == 2 else img[:, :, 0]

        # 提取或创建Alpha通道（掩码）
        if img.shape[-1] == 4:
            alpha = img[:, :, 3]
        else:
            alpha = np.ones_like(gray, dtype=np.uint8) * 255  # 全不透明
        # 保存为单通道PNG（启用最高压缩）
        if output_bgra_path:
            cv_save(output_bgra_path, img, [cv2.IMWRITE_PNG_COMPRESSION, 9])  # 压缩等级0-9（9最高）
        if output_gray_path:
            cv_save(output_gray_path, gray, [cv2.IMWRITE_PNG_COMPRESSION, 9])  # 压缩等级0-9（9最高）
        if output_mask_path:
            cv_save(output_mask_path, alpha, [cv2.IMWRITE_PNG_COMPRESSION, 9])
        print(f"分离成功: {os.path.basename(input_path)} -> 灰度图 + 掩码图")
        return (
            np.ascontiguousarray(img),
            np.ascontiguousarray(gray),
            np.ascontiguousarray(alpha)
        )
    except Exception as e:
        print(f"处理失败 {os.path.basename(input_path)}: {str(e)}")


def split_gray_alpha_bytes(bgra_bytes):
    """
    将BGRA格式的二进制数据分离为灰度图和掩码图（单通道）

    Args:
        bgra_bytes: BGRA格式的图像二进制数据（bytes类型）

    Returns:
        原图矩阵（BGRA）、灰度图矩阵、掩码图矩阵（Alpha通道）
    """
    try:
        if not bgra_bytes:
            raise ValueError("输入的二进制数据为空")

        # 1. 将二进制数据解码为OpenCV图像矩阵
        # 先转换为numpy数组
        nparr = np.frombuffer(bgra_bytes, np.uint8)
        # 解码为BGRA格式的图像（IMREAD_UNCHANGED保留所有通道）
        img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise Exception("二进制数据解码失败，不是有效的图像格式")

        # 2. 验证图像通道数（确保是3通道BGR或4通道BGRA）
        if img.shape[-1] not in (3, 4):
            raise ValueError(f"不支持的通道数: {img.shape[-1]}，预期3或4")

        # 3. 提取灰度通道（基于BGR通道转换）
        gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY)

        # 4. 提取或创建Alpha通道（掩码）
        if img.shape[-1] == 4:
            alpha = img[:, :, 3]  # 直接提取第4通道作为掩码
        else:
            # 若没有Alpha通道，创建全白掩码（全不透明）
            alpha = np.ones_like(gray, dtype=np.uint8) * 255

        print("灰度图和掩码图分离成功")
        return (
            np.ascontiguousarray(img),
            np.ascontiguousarray(gray),
            np.ascontiguousarray(alpha)
        )

    except Exception as e:
        print(f"处理失败: {str(e)}")
        return None, None, None


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
