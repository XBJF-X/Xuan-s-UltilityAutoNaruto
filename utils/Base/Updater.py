import json
import logging
import os
import threading
import time
import zipfile
from io import BytesIO
from pathlib import Path

import requests

from StaticFunctions import get_real_path


class Updater:
    repo_owner = "XBJF-X"
    repo_name = "Xuan-s-UltilityAutoNaruto"
    branch_name = "master"

    def __init__(self, parent_logger):
        self.logger = parent_logger.getChild(self.__class__.__name__)
        self.master_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/branches/{self.branch_name}"
        self.zip_url = f"https://github.com/{self.repo_owner}/{self.repo_name}/archive/refs/heads/{self.branch_name}.zip"
        self.version_file_path = Path(get_real_path("version.json"))
        self.update_thread = None

    def check_update(self):
        try:
            with open(str(self.version_file_path), 'r', encoding='utf-8') as f:
                current_version = json.load(f)
            self.logger.info(f"当前版本 SHA：{current_version['commit']['sha']}")

            response = requests.get(self.master_url, verify=False)
            self.logger.debug(f"Response Status Code：{response.status_code}")
            if response.status_code == 200:
                new_version = json.loads(response.content.decode("utf-8"))
                new_commit = new_version["commit"]
                self.logger.info(f"最新提交 SHA：{new_commit['sha']}")
                self.logger.info(f"最新提交 Committer：{new_commit['commit']["committer"]["name"]}")
                self.logger.info(f"最新提交 Date：{new_commit['commit']["committer"]["date"]}")
                self.logger.info(f"最新提交 Message：{new_commit['commit']['message']}")
                return current_version["commit"]["sha"] != new_version["commit"]["sha"], new_version
            else:
                return False, {}
        except Exception as e:
            self.logger.error(f"检查更新出错：{e}")
            return False, {}

    def update_implement(self, new_version):
        try:
            # 下载zip文件
            self.logger.info(f"正在下载: {self.zip_url}")
            self.logger.info(f"下载时间可能较长，请耐心等候...")
            zip_response = requests.get(self.zip_url, verify=False)
            zip_response.raise_for_status()

            # 解压逻辑：提取一级文件夹下的所有文件
            with zipfile.ZipFile(BytesIO(zip_response.content)) as zf:
                file_list = zf.namelist()
                if not file_list:
                    self.logger.warning("压缩包内无文件")
                    return

                # 获取一级文件夹名称（假设所有文件都在同一个顶层文件夹下）
                root_dir = file_list[0].split('/')[0] + '/'  # 加斜杠避免匹配同名文件
                root_dir_len = len(root_dir)

                # 过滤出一级文件夹下的所有文件（排除文件夹本身）
                files_to_extract = [
                    f for f in file_list
                    if f.startswith(root_dir) and f != root_dir  # 排除顶层文件夹目录项
                ]

                # 解压时去除顶层文件夹路径
                for file in files_to_extract:
                    # 构造目标路径（去掉顶层文件夹部分）
                    target_path = os.path.join(".", file[root_dir_len:])
                    # 创建目标目录（如果是文件夹）
                    if file.endswith('/'):
                        os.makedirs(target_path, exist_ok=True)
                    else:
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        # 提取文件内容
                        with zf.open(file) as source, open(target_path, 'wb') as dest:
                            dest.write(source.read())
                self.logger.info(f"解压完成，已提取一级文件夹下的所有文件到当前目录")

            with open("version.json", "w", encoding="utf-8") as f:
                json.dump(new_version, f, indent=4, ensure_ascii=False)
            self.logger.info("更新完成，下次启动Xuan生效")

        except Exception as e:
            self.logger.error(f"更新出错：{e}")

    def update(self, new_version):
        if self.update_thread:
            self.logger.warning("已经存在一个更新线程了")
            return
        self.update_thread = threading.Thread(
            target=self.update_implement, args=(new_version,), daemon=True)
        self.update_thread.start()
        self.logger.info("更新线程已启动")
