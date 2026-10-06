# -*- coding: utf-8 -*-
"""每日截图配额（每个配置当天的 screenshot 目录最多保留 X 张自动截图）。

需求（2026-09-17，用户确认方案 A + C）：
- R1/R2：每个配置**当天**日志文件夹 ``log/<用户名>/<日期>/screenshot`` 内最多保留 X 张
  自动截图，超出则删除**最早**的截图（保留最新的 X 张）；
- 计数范围：**只统计自动截图**（``screenshot/<任务名>/*.png``）。顶栏「截图」按钮保存的
  用户手动截图位于 ``screenshot/用户截图/``，**不统计、不删除**；
- X 来自全局设置 ``[助手设置] 每日截图上限``（默认 100，最小值 100）。

硬盘读写量保护（R6，不牺牲截图功能本身）：
- **M1 内存索引**：首次（或跨天）只扫一次目录建立 ``{路径: (mtime_ns, name)}`` 索引，
  之后每次保存只做内存增删，避免"每保存一张就 listdir 整个目录"；
- **M2 批量删除**：只在写入成功后清理一次，且把所有超出项一次性删除，完成后只打**一条**
  汇总日志（不逐文件刷日志）；
- **容错**：任何删除/stat 失败只记 warning 并继续，绝不向调用方抛异常（截图主流程优先）。

线程安全：同一 ``(用户名, 日期)`` 目录只应有一个索引实例，实例内用 ``threading.Lock``
串行化（同一配置的多个任务线程可能并发保存）。
"""
from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# ===== 常量 =====
#: 全局设置段/键（`src/DefaultSetting.ini`）
SETTING_SECTION = "助手设置"
SETTING_KEY = "每日截图上限"
#: 默认值与最小值（用户要求：默认 100，最小 100）
DEFAULT_DAILY_LIMIT = 100
MIN_DAILY_LIMIT = 100
#: 用户手动截图子目录（不参与配额统计与删除）
USER_SCREENSHOT_DIR = "用户截图"
#: 自动截图子目录结构：screenshot/<任务名>/*.png
AUTO_SCREENSHOT_GLOB = "*/*.png"


def get_daily_limit(settings=None) -> int:
    """读取全局设置里的每日截图上限（默认 100，最小 100）。

    读取失败/非法值 → 回退默认值并 ``warning`` 留痕（不抛异常：截图主流程不能被设置问题打断）。
    """
    value = None
    try:
        if settings is None:
            from backend.core.settings_store import SettingsService
            settings = SettingsService()
        value = settings.get(SETTING_SECTION, SETTING_KEY)
    except Exception as e:  # pragma: no cover - 极端环境（setting.ini 不可读）
        logging.getLogger("ScreenshotQuota").warning(
            "读取[%s] %s 失败，按默认值 %d 处理: %s",
            SETTING_SECTION, SETTING_KEY, DEFAULT_DAILY_LIMIT, e)
    return normalize_daily_limit(value)


def normalize_daily_limit(raw) -> int:
    """把设置值夹到合法区间：非数字/空 → 默认 100；小于 100 → 100。"""
    try:
        if raw is None or str(raw).strip() == "":
            return DEFAULT_DAILY_LIMIT
        limit = int(float(str(raw).strip()))
    except (TypeError, ValueError):
        return DEFAULT_DAILY_LIMIT
    if limit < MIN_DAILY_LIMIT:
        return MIN_DAILY_LIMIT
    return limit


@dataclass
class QuotaResult:
    """一次配额检查的结果（供日志与单测断言）"""

    #: 实际删除的文件数
    deleted: int
    #: 清理后索引中的自动截图总数
    total: int
    #: 文件不存在（不在配额管辖范围，如日志目录外）时为 True
    skipped: bool = False


class ScreenshotQuota:
    """某个 ``(用户名, 日期)`` 的 screenshot 目录配额管理器（内存索引 + 批量删最早）"""

    def __init__(self, root, logger: Optional[logging.Logger] = None, *,
                 user_subdir: str = USER_SCREENSHOT_DIR,
                 glob_pattern: str = AUTO_SCREENSHOT_GLOB):
        self.root = Path(root)
        self.logger = logger or logging.getLogger("ScreenshotQuota")
        self.user_subdir = user_subdir
        self.glob_pattern = glob_pattern
        self._lock = threading.Lock()
        # 索引构建锁：并发保存时只允许一个线程扫目录（其余直接复用索引），避免多线程
        # 同时 listdir 造成重复磁盘 IO（R6：尽量保护硬盘读写量）
        self._build_lock = threading.Lock()
        # 索引：绝对路径 -> (mtime_ns, 文件名)；仅含自动截图，按需排序（不每次重排）
        self._index: dict[Path, tuple[int, str]] = {}
        self._built = False
        # 累计统计（供排查/日志）
        self.total_deleted = 0
        self.prune_calls = 0
        self.scan_count = 0

    # ---------------- 索引 ----------------

    @property
    def user_dir(self) -> Path:
        """用户手动截图子目录（不参与配额）"""
        return self.root / self.user_subdir

    def _iter_candidates(self) -> list[Path]:
        """候选自动截图：``root/*/*.png``，且显式排除 ``用户截图/`` 子目录。"""
        if not self.root.is_dir():
            return []
        try:
            found = list(self.root.glob(self.glob_pattern))
        except OSError as e:
            self.logger.warning("扫描截图目录失败 %s: %s", self.root, e)
            return []
        out: list[Path] = []
        for path in found:
            try:
                if path.parent.name == self.user_subdir:
                    continue
                if path.is_file():
                    out.append(path)
            except OSError:
                # 扫描期间文件被外部删除/权限问题：跳过该文件（不影响其余条目）
                continue
        return out

    def build_index(self) -> int:
        """重建内存索引（每次进入新日期或首次保存时调用一次），返回索引条目数。

        并发保护：同一时刻只有一个线程真正扫目录，其余线程等它完成后直接复用结果
        （避免多任务线程同时 listdir，放大磁盘 IO）。
        """
        with self._build_lock:
            if self._built:
                return self.count()
            entries: dict[Path, tuple[int, str]] = {}
            for path in self._iter_candidates():
                try:
                    entries[path] = (path.stat().st_mtime_ns, path.name)
                except OSError as e:
                    self.logger.warning("读取截图时间失败（跳过）%s: %s", path.name, e)
            with self._lock:
                self._index = entries
                self._built = True
                self.scan_count += 1
                total = len(entries)
            self.logger.debug("截图配额索引已建立：%s 共 %d 张自动截图", self.root, total)
            return total

    def reset_index(self) -> None:
        """丢弃内存索引（下次 ``prune`` 时重新扫描目录）。

        用途：测试隔离；也可供"外部批量改动目录"后强制重新对账。
        """
        with self._lock:
            self._index = {}
            self._built = False

    def count(self) -> int:
        """当前索引中的自动截图张数（不访问磁盘）"""
        with self._lock:
            return len(self._index)

    # ---------------- 配额清理 ----------------

    def prune(self, path, limit) -> QuotaResult:
        """把 ``path`` 纳入索引，并按 ``limit`` 删除最早的自动截图。

        - ``path`` 不在本目录管辖范围内（例如已切到新日期/日志目录外）→ 不处理，返回
          ``skipped=True``（由调用方按 ``(用户名, 日期)`` 取正确实例后重试）；
        - 只有写入成功后才会走到这里，因此"删除最早的"语义为"保留最新 X 张"；
        - 删除失败逐项 warning 并继续，永不抛异常。
        """
        limit = normalize_daily_limit(limit)
        file_path = Path(path)
        try:
            resolved = file_path.resolve()
            root_resolved = self.root.resolve()
        except OSError:
            resolved, root_resolved = file_path, self.root

        if resolved.parent.name == self.user_subdir:
            # 用户手动截图不参与配额（调用方本不该传，这里双保险）
            return QuotaResult(deleted=0, total=self.count(), skipped=True)

        try:
            in_scope = resolved.is_relative_to(root_resolved)
        except ValueError:
            in_scope = False
        if not in_scope:
            return QuotaResult(deleted=0, total=self.count(), skipped=True)

        if not self._built:
            self.build_index()

        return self._prune_locked(resolved, limit)

    def _prune_locked(self, resolved: Path, limit: int) -> QuotaResult:
        """索引已就绪时的配额清理（调用方保证 ``build_index`` 已执行过一次）"""
        with self._lock:
            if resolved.exists():
                try:
                    self._index[resolved] = (resolved.stat().st_mtime_ns, resolved.name)
                except OSError as e:
                    self.logger.warning("读取新截图时间失败（仍计入配额）%s: %s", resolved.name, e)
                    self._index[resolved] = (-1, resolved.name)
            total = len(self._index)
            if total <= limit:
                return QuotaResult(deleted=0, total=total)

            # 删最早：按 (mtime_ns, 文件名) 升序，删除最早的 over 个。
            # 新图刚写入，是最新的一张，因此不会被选中（下面仍有保底判断）。
            over = total - limit
            ordered = sorted(self._index.items(), key=lambda kv: (kv[1][0], kv[1][1]))
            victims = ordered[:over]
            kept = dict(ordered[over:])

        deleted = 0
        failed: list[tuple[Path, tuple[int, str]]] = []
        for victim, meta in victims:
            if victim == resolved:
                # 保底：绝不删掉刚写入的这张（极端时钟回拨场景）
                kept[victim] = meta
                continue
            try:
                os.remove(victim)
                deleted += 1
            except FileNotFoundError:
                deleted += 1  # 外部已删除，视作已清理
            except OSError as e:
                self.logger.warning("删除最早截图失败（保留）%s: %s", victim.name, e)
                failed.append((victim, meta))

        with self._lock:
            for victim, meta in failed:
                kept[victim] = meta
            self._index = kept
            self.total_deleted += deleted
            self.prune_calls += 1
            remaining = len(kept)

        if deleted:
            self.logger.info(
                "已清理最早的 %d 张截图（每日上限 %d，当前保留 %d 张）：%s",
                deleted, limit, remaining, self.root)
        elif failed:
            self.logger.warning(
                "截图数量超过每日上限（%d/%d）但删除失败，保留 %d 张：%s",
                total, limit, remaining, self.root)
        return QuotaResult(deleted=deleted, total=remaining)

    def stats(self) -> dict:
        """配额运行统计（供排查与调试输出）"""
        with self._lock:
            return {
                "root": str(self.root),
                "indexed": len(self._index),
                "scans": self.scan_count,
                "prune_calls": self.prune_calls,
                "total_deleted": self.total_deleted,
            }
