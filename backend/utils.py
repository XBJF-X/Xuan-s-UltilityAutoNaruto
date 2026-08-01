"""后端工具函数 - 路径、图像IO、日志等（不依赖 PySide6）"""
import logging
import os
import sys
from pathlib import Path

import cv2
import numpy as np


def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).resolve().parent.parent


def get_real_path(relative_path: str = "") -> str:
    """获取基于项目根目录的绝对路径"""
    root = get_project_root()
    return os.path.normpath(os.path.join(str(root), relative_path))


def cv_imread(file_path):
    """使用 cv2 读取图像，支持中文路径"""
    return cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)


def cv_save(image_path, image_array, params=None):
    """保存图像，支持中文路径"""
    if params is None:
        params = [cv2.IMWRITE_PNG_COMPRESSION, 0]
    cv2.imencode('.png', image_array, params)[1].tofile(image_path)


def setup_logging():
    """简易日志配置（与原版兼容）"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )