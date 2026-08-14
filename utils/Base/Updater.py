import json
import os
import threading
import zipfile
from io import BytesIO
from pathlib import Path

import requests
from PySide6.QtCore import QObject, Signal

from StaticFunctions import get_real_path


class Updater(QObject):
    update_message = Signal(str, str)  # 第一个参数是标题，第二个参数是消息内容
    restart_required = Signal()  # 新增：通知主窗口需要重启

    repo_owner = "XBJF-X"
    repo_name = "Xuan-s-UltilityAutoNaruto"
    branch_name = "master"
    # 本地当前版本号（16.0），用于与 GitHub 最新 Release 版本号比较
    local_version = "0.16.0"
    # 升级通知标记文件名：存在时表示已通知用户手动升级，不再执行自动热更新
    upgrade_notice_flag = "upgrade_notice_shown.flag"

    def __init__(self, parent_logger):
        super().__init__()  # 调用父类初始化
        self.logger = parent_logger.getChild(self.__class__.__name__)
        self.master_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/branches/{self.branch_name}"
        self.zip_url = f"https://github.com/{self.repo_owner}/{self.repo_name}/archive/refs/heads/{self.branch_name}.zip"
        self.release_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        self.version_file_path = Path(get_real_path("version.json"))
        self.update_thread = None

    def check_update(self):
        # ==================== Release 检测：停止自动更新逻辑 ====================
        # 若已通知过升级（存在标记文件），跳过所有更新检查，避免重复通知或误拉取
        upgrade_notice_flag_path = Path(get_real_path(self.upgrade_notice_flag))
        if upgrade_notice_flag_path.exists():
            self.logger.info(f"检测到 {self.upgrade_notice_flag} 标记文件，本版本已停止自动热更新，跳过本次更新检查")
            return False, {}
        # 请求 GitHub 最新 Release 信息，若存在比本地更高的 Release，则通知手动升级并停止自动更新
        if self.check_upgrade_notice():
            return False, {}
        # =======================================================================

        current_version = None
        # 尝试读取本地版本文件，若不存在则视为需要更新
        try:
            with open(str(self.version_file_path), 'r', encoding='utf-8') as f:
                current_version = json.load(f)
            self.logger.info(f"当前版本 SHA：{current_version['commit']['sha']}")
        except FileNotFoundError:
            self.logger.info("version.json 不存在，视为需要更新")
        except Exception as e:
            self.update_message.emit("检查更新出错", f"读取本地版本文件出错：{e}")
            self.logger.error(f"读取本地版本文件出错：{e}")
            return False, {}

        # 获取远程版本信息
        try:
            response = requests.get(self.master_url, verify=False)
            self.logger.debug(f"Response Status Code：{response.status_code}")
            if response.status_code == 200:
                new_version = json.loads(response.content.decode("utf-8"))
                new_commit = new_version["commit"]
                # 若本地版本不存在或 SHA 不同，则提示更新
                if current_version is None or current_version["commit"]["sha"] != new_version["commit"][
                    "sha"]:
                    self.logger.info("检测到新版本！")
                    self.logger.info(f"最新提交 SHA：{new_commit['sha']}")
                    self.logger.info(f"最新提交 Committer：{new_commit['commit']['committer']['name']}")
                    self.logger.info(f"最新提交 Date：{new_commit['commit']['committer']['date']}")
                    self.logger.info(f"最新提交 Message：{new_commit['commit']['message']}")
                    return True, new_version
                self.update_message.emit("", "当前已是最新版本")
                self.logger.info("当前已是最新版本")
            else:
                self.update_message.emit("检查更新失败", f"HTTP状态码：{response.status_code}")
                self.logger.error(f"检查更新失败，HTTP状态码：{response.status_code}")
            return False, {}
        except Exception as e:
            self.update_message.emit("检查更新出错", f"{e}")
            self.logger.error(f"检查更新出错：{e}")
            return False, {}

    @staticmethod
    def _parse_version(version_str):
        """
        解析版本号字符串为整数元组，便于比较。

        兼容 'v0.17.0'、'0.17.0'、'17.0' 等格式，忽略非数字字符。
        例如 'v0.17.0' -> (0, 17, 0)
        """
        parts = []
        for part in str(version_str).split('.'):
            digits = ''.join(ch for ch in part if ch.isdigit())
            if digits:
                parts.append(int(digits))
        return tuple(parts)

    @staticmethod
    def _version_gt(latest, local):
        """
        比较两个版本元组，latest 是否严格大于 local。

        段数不足时按 0 补齐，例如 (17, 0) > (0, 16, 0) 为 True。
        """
        max_len = max(len(latest), len(local))
        latest_padded = latest + (0,) * (max_len - len(latest))
        local_padded = local + (0,) * (max_len - len(local))
        return latest_padded > local_padded

    def check_upgrade_notice(self):
        """
        检查 GitHub 最新 Release 版本号。

        若最新 Release 版本号大于本地版本（16.0），则弹窗通知用户前往 GitHub Release
        手动下载安装包升级，写入升级通知标记文件，并停止自动热更新（返回 True）。
        否则返回 False，继续执行原有热更新逻辑。

        当获取 Release 信息失败时，为保证原有更新流程可用，降级为继续热更新（返回 False）。
        """
        try:
            response = requests.get(self.release_url, verify=False)
            self.logger.debug(f"Release Response Status Code：{response.status_code}")
            if response.status_code != 200:
                self.logger.warning(
                    f"获取 GitHub 最新 Release 信息失败，HTTP状态码：{response.status_code}，继续执行原有热更新逻辑")
                return False
            release_info = json.loads(response.content.decode("utf-8"))
            tag_name = release_info.get("tag_name", "")
            latest_version = self._parse_version(tag_name)
            local_version = self._parse_version(self.local_version)
            self.logger.info(f"GitHub 最新 Release：{tag_name}，本地版本：{self.local_version}")
            if self._version_gt(latest_version, local_version):
                # 展示用版本号，如 v0.17.0 -> 0.17.0
                display_version = ".".join(str(x) for x in latest_version)
                self.update_message.emit(
                    "检测到新版本",
                    f"检测到新版本 {display_version}，请前往 GitHub Release 下载安装包手动升级。\n"
                    f"本版本已停止自动热更新。")
                self.logger.info(
                    f"检测到新版本 {display_version}，本版本已停止自动热更新，请前往 GitHub Release 下载安装包手动升级")
                # 写入本地标记文件，记录已通知；之后不再执行任何自动拉取代码的操作
                try:
                    with open(str(Path(get_real_path(self.upgrade_notice_flag))), "w", encoding="utf-8") as f:
                        f.write(tag_name)
                    self.logger.info(f"已写入升级通知标记文件：{self.upgrade_notice_flag}")
                except Exception as e:
                    self.logger.error(f"写入升级通知标记文件失败：{e}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"检查 GitHub 最新 Release 信息出错：{e}，继续执行原有热更新逻辑")
            return False

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

                # 更新完成，发出信号，注意这里传递两个参数：标题和消息
                commit_message = new_version["commit"]['commit']['message']
                self.update_message.emit("更新完成", f"新版本更新完毕，请重启程序\n更新内容：{commit_message}")

                self.restart_required.emit()

            with open("version.json", "w", encoding="utf-8") as f:
                json.dump(new_version, f, indent=4, ensure_ascii=False)
            self.logger.info("更新完成，下次启动Xuan生效")

        except Exception as e:
            self.logger.error(f"更新出错：{e}")
            # 如果更新出错，也可以发射一个信号来显示错误信息
            self.update_message.emit("更新出错", f"更新过程中出现错误：{e}")
        finally:
            self.update_thread = None

    def update(self, new_version):
        if self.update_thread:
            self.update_message.emit("重复更新", f"已经存在一个更新线程了")
            self.logger.warning("已经存在一个更新线程了")
            return
        self.update_thread = threading.Thread(
            target=self.update_implement, args=(new_version,), daemon=True)
        self.update_thread.start()
        self.update_message.emit("", "更新线程已启动")
        self.logger.info("更新线程已启动")
