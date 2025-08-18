import os
import shutil
import tempfile
import json
import logging
from pathlib import Path
from datetime import datetime
from packaging import version
from git import Repo, GitCommandError, Git

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('GitUpdater')


class Updater:
    def __init__(self, repo_url, install_dir, branch="master", config_files=None):
        """
        初始化 Git 更新器

        :param repo_url: Git 仓库 URL
        :param install_dir: 应用安装目录
        :param branch: 要跟踪的分支 (默认为 master)
        :param config_files: 需要保留的配置文件列表
        """
        self.repo_url = repo_url
        self.install_dir = Path(install_dir)
        self.branch = branch
        self.config_files = config_files or []
        self.current_version = self._get_current_version()
        self.latest_version = None

        # 确保安装目录存在
        self.install_dir.mkdir(parents=True, exist_ok=True)

        # 初始化 Git 对象
        self.git = Git(str(self.install_dir))

        # 检查是否已经是 Git 仓库
        self.is_git_repo = (self.install_dir / '.git').exists()

    def _get_current_version(self):
        """获取当前版本"""
        version_file = self.install_dir / 'version.json'
        if version_file.exists():
            try:
                with open(version_file, 'r') as f:
                    data = json.load(f)
                    return data.get('version', 'v0.0.0')
            except json.JSONDecodeError:
                logger.error("无法解析版本文件")

        # 如果没有版本文件，尝试获取 Git 标签
        if (self.install_dir / '.git').exists():
            try:
                repo = Repo(str(self.install_dir))
                tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
                if tags:
                    return tags[-1].name
            except Exception:
                pass

        return 'v0.0.0'

    def _update_version_info(self, new_version):
        """更新版本信息文件"""
        version_file = self.install_dir / 'version.json'
        version_data = {
            "version": new_version,
            "last_updated": datetime.now().isoformat(),
            "repo_url": self.repo_url,
            "branch": self.branch
        }

        with open(version_file, 'w') as f:
            json.dump(version_data, f, indent=2)

        logger.info(f"版本信息已更新至 {new_version}")

    def _backup_config(self, backup_dir):
        """备份配置文件"""
        if not self.config_files:
            return

        logger.info("备份配置文件中...")
        config_backup = Path(backup_dir) / 'config_backup'
        config_backup.mkdir(exist_ok=True)

        for config_file in self.config_files:
            source_path = self.install_dir / config_file
            if source_path.exists():
                dest_path = config_backup / config_file
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                if source_path.is_dir():
                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(source_path, dest_path)

                logger.debug(f"已备份: {config_file}")

    def _restore_config(self, backup_dir):
        """恢复配置文件"""
        if not self.config_files:
            return

        logger.info("恢复配置文件中...")
        config_backup = Path(backup_dir) / 'config_backup'

        for config_file in self.config_files:
            source_path = config_backup / config_file
            if source_path.exists():
                dest_path = self.install_dir / config_file
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                if source_path.is_dir():
                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(source_path, dest_path)

                logger.debug(f"已恢复: {config_file}")

    def _get_latest_version(self):
        """获取最新版本"""
        try:
            # 创建一个临时仓库来获取最新版本
            with tempfile.TemporaryDirectory() as temp_dir:
                repo = Repo.clone_from(
                    self.repo_url,
                    temp_dir,
                    branch=self.branch,
                    depth=1
                )

                # 获取最新标签
                tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
                if tags:
                    return tags[-1].name

                # 如果没有标签，使用最新提交的哈希
                return repo.head.commit.hexsha[:7]
        except GitCommandError as e:
            logger.error(f"获取最新版本失败: {e}")
            return None

    def needs_update(self):
        """检查是否需要更新"""
        self.latest_version = self._get_latest_version()
        if not self.latest_version:
            return False

        try:
            current_ver = version.parse(self.current_version.lstrip('v'))
            latest_ver = version.parse(self.latest_version.lstrip('v'))
            return latest_ver > current_ver
        except version.InvalidVersion:
            # 如果版本号不符合语义化版本规范，使用字符串比较
            return self.latest_version != self.current_version

    def incremental_update(self):
        """执行增量更新"""
        if not self.latest_version:
            logger.info("无法获取最新版本信息")
            return False

        if not self.needs_update():
            logger.info("当前已是最新版本")
            return True

        logger.info(f"发现新版本: {self.latest_version}")

        # 创建备份目录
        backup_dir = tempfile.mkdtemp()
        try:
            # 备份配置文件
            self._backup_config(backup_dir)

            # 如果是 Git 仓库，尝试拉取更新
            if self.is_git_repo:
                logger.info("尝试通过 Git 拉取更新...")
                try:
                    repo = Repo(str(self.install_dir))

                    # 检查是否有未提交的更改
                    if repo.is_dirty():
                        logger.warning("工作区有未提交的更改，暂存更改")
                        repo.git.stash('save', '--keep-index', 'Auto-update changes')

                    # 获取最新更改
                    origin = repo.remote(name='origin')
                    origin.fetch()

                    # 重置到最新版本
                    repo.git.reset('--hard', f'origin/{self.branch}')

                    # 更新版本信息
                    self._update_version_info(self.latest_version)

                    # 恢复配置文件
                    self._restore_config(backup_dir)

                    logger.info("Git 拉取更新成功完成!")
                    return True
                except GitCommandError as e:
                    logger.error(f"Git 拉取失败: {e}")

            # 如果不是 Git 仓库或拉取失败，使用完整更新
            logger.info("无法使用 Git 拉取，尝试完整更新...")
            return self.full_update()
        except Exception as e:
            logger.error(f"增量更新失败: {e}")
            return False
        finally:
            # 清理备份目录
            shutil.rmtree(backup_dir, ignore_errors=True)

    def full_update(self):
        """执行完整更新"""
        logger.info("开始完整更新...")

        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        try:
            # 备份配置文件
            backup_dir = tempfile.mkdtemp()
            self._backup_config(backup_dir)

            # 克隆最新仓库
            logger.info(f"正在克隆仓库: {self.repo_url}")
            repo = Repo.clone_from(
                self.repo_url,
                temp_dir,
                branch=self.branch
            )

            # 删除旧文件（保留配置文件）
            logger.info("清理旧文件...")
            for item in self.install_dir.iterdir():
                if item.name in ['.git', 'version.json']:
                    continue

                if item.name in self.config_files:
                    continue

                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink(missing_ok=True)

            # 复制新文件
            logger.info("复制新文件...")
            for item in Path(temp_dir).iterdir():
                if item.name == '.git':
                    continue

                dest = self.install_dir / item.name

                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)

            # 更新版本信息
            self._update_version_info(self.latest_version)

            # 恢复配置文件
            self._restore_config(backup_dir)

            logger.info("完整更新成功完成!")
            return True
        except GitCommandError as e:
            logger.error(f"克隆仓库失败: {e}")
            return False
        except Exception as e:
            logger.error(f"完整更新失败: {e}")
            return False
        finally:
            # 清理临时目录
            shutil.rmtree(temp_dir, ignore_errors=True)
            shutil.rmtree(backup_dir, ignore_errors=True)

    def run_update(self):
        """执行更新流程"""
        logger.info(f"当前版本: {self.current_version}")

        if self.incremental_update():
            return True
        elif self.full_update():
            return True

        logger.error("更新失败")
        return False


# 使用示例
if __name__ == "__main__":
    # 配置参数
    REPO_URL = "https://github.com/XBJF-X/Xuan-s-UltilityAutoNaruto.git"
    INSTALL_DIR = r"F:\PyProject\DailyQuestsHelper\git"

    # 需要保留的配置文件
    CONFIG_FILES = [
        "config/settings.ini",
        "user_data",
        "credentials.json"
    ]

    # 创建更新器
    updater = Updater(
        repo_url=REPO_URL,
        install_dir=INSTALL_DIR,
        branch="master",
        config_files=CONFIG_FILES
    )

    # 执行更新
    if updater.run_update():
        logger.info("更新成功！请重启应用。")
    else:
        logger.error("更新失败，请手动检查。")