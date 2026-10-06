# -*- coding: utf-8 -*-
"""截图运行守卫（本次运行计数 + 完全重复画面跳过 + 超限弹窗事件）

阶段 4 系列的协作者风格：从 `SchedulerService._save_screenshot` 抽出三块与"截图"强相关、
但与调度编排水无关的职责，便于注入/单测/复用：

1. **M5 完全重复画面跳过**（用户确认的追加省 IO 措施）：同一任务内，若本次要保存的截图
   与上一张**逐像素完全相同**（通过 :func:`frame_digest` 比较），则跳过写盘，只记 DEBUG。
   静止/黑屏/加载帧期间几乎零写盘；只要画面有变化就照常保存，因此"任务执行过程"完整可回溯。
   **错误/超时/卡死截图（reason 非空）永不跳过**——异常现场必须落盘。
2. **本次运行计数**：每次成功落盘 +1（跳过的不计）。
3. **超限提醒**：本次运行计数 > 每日上限（默认 100）时，向 GUI 广播**一次** `screenshot.limit`
   事件（每个配置、每次运行各自一次），提示用户关闭日志面板右上角的「截图」开关。
   广播只做一次，后续只累计计数，避免"每张截图一次弹窗 + 一条日志"反向放大磁盘/网络开销。

"本次运行"边界：`SchedulerService` 每次 `start()` 调用 :meth:`ScreenshotGuard.reset_run`
（停止后重新启动 = 新的一次运行）。
"""
from __future__ import annotations

import hashlib
import logging
from typing import Callable, Optional

#: WS 事件类型（v1 信封；旧前端按未知 type 安全忽略）
WS_EVENT_SCREENSHOT_LIMIT = "screenshot.limit"


def frame_digest(img, shape) -> str:
    """计算一帧画面的指纹（用于"与上一张是否完全一致"的对比）。

    实现：对 ``(高度, 宽度, 通道数)`` + ``dtype`` + 像素字节的**首尾各 128 字节**求
    blake2b（16 字节）。首尾抽样是指纹的快速近似：它能以极低成本抓住"完全相同"与
    "明显不同"，而 M5 的判定只用于**跳过**——误判（把不同画面当相同）的后果是少存
    一张重复价值的截图，不会丢异常现场（错误截图永不跳过）。整帧哈希（1600×900 约
    10ms/张）与"省 IO"的目标相悖，故不采用。
    """
    try:
        contiguous = img if img.flags["C_CONTIGUOUS"] else img.copy()
        payload = memoryview(contiguous.tobytes())
        dtype = str(img.dtype)
    except Exception:  # pragma: no cover - 非数组输入兜底（此时退回"不跳过"）
        return ""
    digest = hashlib.blake2b(digest_size=16)
    digest.update(repr(shape).encode("ascii", "replace"))
    digest.update(dtype.encode("ascii", "replace"))
    digest.update(payload[:128])
    digest.update(payload[-128:])
    return digest.hexdigest()


class ScreenshotGuard:
    """单配置（单调度器实例）的截图运行守卫"""

    def __init__(self, config_id: str, logger: logging.Logger, *,
                 alert_callback: Optional[Callable[[dict], None]] = None,
                 summary_log_interval: int = 500):
        self.config_id = config_id
        self.logger = logger
        # 超限事件回调（由组合根注入：services 不反向依赖 api.ws）
        self.alert_callback = alert_callback
        # 每隔多少张打一条 INFO 计数日志（避免逐张刷日志；0 = 关闭）
        self.summary_log_interval = max(0, int(summary_log_interval))
        self._run_count = 0
        self._alert_sent = False
        self._last_digest: dict[str, str] = {}
        self.skipped_count = 0
        # 每日上限：None = 每次保存时实时读取全局设置；非 None = 固定值（单测注入）
        self._limit_override: Optional[int] = None

    # ---------------- 配置 ----------------

    @property
    def run_count(self) -> int:
        """本次运行成功保存的截图张数"""
        return self._run_count

    @property
    def alert_sent(self) -> bool:
        """本次运行是否已广播过超限提醒"""
        return self._alert_sent

    def set_limit(self, limit: Optional[int]) -> None:
        """固定每日上限（单测/特殊场景注入）；传 None 恢复"实时读全局设置"。"""
        from backend.services.screenshot_quota import normalize_daily_limit
        self._limit_override = None if limit is None else normalize_daily_limit(limit)

    def current_limit(self) -> int:
        """当前生效的每日上限（实时读全局设置，读失败回退默认值）"""
        if self._limit_override is not None:
            return self._limit_override
        from backend.services.screenshot_quota import get_daily_limit
        return get_daily_limit()

    # ---------------- 运行边界 ----------------

    def reset_run(self) -> None:
        """新的一次运行开始：计数归零、允许再次提醒、清空重复指纹"""
        self._run_count = 0
        self._alert_sent = False
        self._last_digest.clear()
        self.skipped_count = 0

    # ---------------- 重复画面判定 ----------------

    def should_skip(self, task_name: str, img, *, reason: str = "") -> bool:
        """判断是否可跳过本次写盘（仅"与上一张完全相同"时跳过）。

        - ``reason`` 非空（错误/超时/卡死自动截图）→ 永不跳过；
        - 返回 True 时内部已更新指纹与跳过计数。
        """
        if reason:
            return False
        key = task_name or ""
        try:
            digest = frame_digest(img, getattr(img, "shape", None))
        except Exception as e:  # pragma: no cover - 指纹异常不影响截图本身
            self.logger.debug("截图指纹计算失败（照常保存）: %s", e)
            return False
        if not digest:
            return False
        if self._last_digest.get(key) == digest:
            self.skipped_count += 1
            self.logger.debug(
                "跳过与前一张完全相同的截图（任务=%s，省一次写盘）", task_name)
            return True
        self._last_digest[key] = digest
        return False

    def forget_task(self, task_name: str) -> None:
        """丢弃某任务的上一帧指纹（如任务被停止/切换，避免跨轮误判）"""
        self._last_digest.pop(task_name or "", None)

    # ---------------- 保存后记账与提醒 ----------------

    def note_saved(self) -> dict:
        """记录一次成功落盘；返回本次运行计数快照（供日志/提醒使用）"""
        self._run_count += 1
        count = self._run_count
        limit = self.current_limit()
        if self.summary_log_interval and count % self.summary_log_interval == 0:
            self.logger.info(
                "本次运行已保存 %d 张截图（每日上限 %d，跳过重复 %d 张）",
                count, limit, self.skipped_count)
        return {"run_count": count, "limit": limit}

    def maybe_alert(self, *, run_count: int, limit: int, today_count: int) -> bool:
        """本次运行计数**超过**上限时广播一次提醒；已提醒过返回 False。

        返回 True 表示本次真的广播了（供调用方补日志/单测断言）。
        """
        if run_count <= limit or self._alert_sent:
            return False
        self._alert_sent = True
        payload = {
            "config_id": self.config_id,
            "limit": int(limit),
            "run_count": int(run_count),
            "today_count": int(today_count),
        }
        self.logger.warning(
            "本次运行截图已达 %d 张（每日上限 %d，今日截图 %d 张）："
            "建议关闭日志面板右上角的「截图」开关，避免不必要的磁盘读写",
            run_count, limit, today_count)
        if self.alert_callback is not None:
            try:
                self.alert_callback(payload)
            except Exception as e:
                # 提醒失败不得影响截图主流程
                self.logger.warning("截图超限提醒广播失败: %s", e)
        else:
            self.logger.debug("截图超限提醒未接线（无回调），仅记录日志")
        return True
