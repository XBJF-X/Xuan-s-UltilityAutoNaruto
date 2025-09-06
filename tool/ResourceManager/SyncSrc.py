import os
import shutil
import logging
from pathlib import Path

from StaticFunctions import get_real_path


def sync_directories(raw_src_path, target_src_path):
    """
    同步两个目录，排除名为'Example.png'的文件，并删除目标目录中多余的文件

    参数:
        raw_src_path: 源目录路径 (raw_src/Template/Scene)
        target_src_path: 目标目录路径 (src/Template/Scene)
    """
    # 设置日志记录
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('directory_sync')

    # 确保路径存在
    raw_src = Path(raw_src_path)
    target_src = Path(target_src_path)

    if not raw_src.exists() or not raw_src.is_dir():
        logger.error(f"源目录不存在或不是目录: {raw_src}")
        return

    # 如果目标目录不存在则创建
    target_src.mkdir(parents=True, exist_ok=True)

    # 步骤1: 收集源目录中所有需要同步的文件（排除Example.png）
    source_files = []
    for root, dirs, files in os.walk(raw_src):
        relative_root = Path(root).relative_to(raw_src)
        for file in files:
            if file == "Example.png":
                continue  # 跳过Example.png文件
            source_file = relative_root / file
            source_files.append(source_file)

    logger.info(f"找到 {len(source_files)} 个需要同步的文件 (排除Example.png)")

    # 步骤2: 创建目标目录中需要的文件夹结构
    for source_file in source_files:
        target_dir = target_src / source_file.parent
        target_dir.mkdir(parents=True, exist_ok=True)

    # 步骤3: 同步文件
    copied_count = 0
    for source_file in source_files:
        source_path = raw_src / source_file
        target_path = target_src / source_file

        # 检查是否需要复制（文件不存在或内容不同）
        if not target_path.exists() or source_path.stat().st_mtime > target_path.stat().st_mtime:
            shutil.copy2(source_path, target_path)
            copied_count += 1
            logger.debug(f"复制: {source_file}")

    logger.info(f"复制了 {copied_count} 个文件")

    # 步骤4: 删除目标目录中多余的文件
    deleted_count = 0
    # 首先删除所有Example.png文件（无论是否在源目录存在）
    for root, dirs, files in os.walk(target_src):
        for file in files:
            if file == "Example.png":
                file_path = Path(root) / file
                file_path.unlink()
                deleted_count += 1
                logger.debug(f"删除Example.png: {file_path.relative_to(target_src)}")

    # 然后删除其他不在源目录中的文件
    for root, dirs, files in os.walk(target_src):
        relative_root = Path(root).relative_to(target_src)
        for file in files:
            if file == "Example.png":
                continue  # 已处理过

            relative_file = relative_root / file
            if relative_file not in source_files:
                file_path = target_src / relative_file
                file_path.unlink()
                deleted_count += 1
                logger.debug(f"删除多余文件: {relative_file}")

    logger.info(f"删除了 {deleted_count} 个文件")

    # 步骤5: 删除目标目录中多余的空文件夹
    empty_dir_deleted = 0
    for root, dirs, files in os.walk(target_src, topdown=False):
        current_dir = Path(root)
        # 如果目录为空且不是根目录
        if not os.listdir(root) and current_dir != target_src:
            try:
                current_dir.rmdir()
                empty_dir_deleted += 1
                logger.debug(f"删除空目录: {current_dir.relative_to(target_src)}")
            except OSError:
                pass  # 目录可能不为空或权限问题

    logger.info(f"删除了 {empty_dir_deleted} 个空目录")
    logger.info("同步完成!")


if __name__ == "__main__":
    # 执行同步
    sync_directories(
        Path(get_real_path("raw_src/Template/Scene")),
        Path(get_real_path("src/Template/Scene"))
    )
