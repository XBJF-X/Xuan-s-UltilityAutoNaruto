"""后端独立的路径工具 - 不依赖 StaticFunctions（避免引入 PySide6/cv2）"""
import os
import sys
from pathlib import Path


def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).resolve().parent.parent


def get_real_path(relative_path: str = "") -> str:
    """获取基于项目根目录的绝对路径"""
    root = get_project_root()
    return os.path.normpath(os.path.join(str(root), relative_path))