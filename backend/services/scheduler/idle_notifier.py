"""空闲/预设完成通知（桌面通知，仅 Windows）

阶段 4.3：从 `SchedulerService`(1540 行) 抽出的第三块职责。原先"是否开启通知""怎么发"
"何时判定告一段落"三件事与调度循环混在一起；抽走后服务侧只剩调用点。

`notify_account_idle` 需要读取调度器状态（`run_once` / `_pending_activate_tasks` /
`task_queue` / `_completed_count` / `_preset_total`）与去抖标记 `_idle_notified`，
全部经 `service` 回指实时读取；`_idle_notified` 由本类持有，服务侧以同名 property 暴露
（含 setter，测试会直接写）。
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from backend.services.scheduler.constants import IDLE_NOTIFY_THRESHOLD


class IdleNotifier:
    """桌面通知：开关读取、发送、空闲/预设完成判定"""

    def __init__(self, service: Any):
        self.service = service
        # 去抖标记：同一段空闲只通知一次（有任务进入执行/就绪队列即重新武装）
        self.idle_notified = False

    @property
    def logger(self) -> logging.Logger:
        return self.service.logger

    @property
    def config(self):
        return getattr(self.service, "config", None)

    def notifications_enabled(self) -> bool:
        """[助手设置] 任务通知 开关（默认开启）。"""
        try:
            from backend.services.settings_service import SettingsService
            return SettingsService().getboolean("助手设置", "任务通知", default=True)
        except Exception as e:
            # setting.ini 属外部依赖：读取失败按"开启"处理并留痕，不影响调度
            self.logger.warning(f"读取[助手设置]任务通知失败，按开启处理: {e}")
            return True

    def send(self, title: str, message: str) -> None:
        """底层发送（开关/平台检查 + notify_async）。

        服务侧 `_notify_user` 转发到这里；而上层的 `notify_preset_finished` /
        `notify_account_idle` 反过来调用 `service._notify_user`，以保持
        "实例属性替换 `sched._notify_user` 即可捕获通知"这一既有测试/扩展点。
        """
        if not self.notifications_enabled():
            self.logger.debug("任务通知开关已关闭，跳过本次通知")
            return
        from backend.services.notify_service import is_supported, notify_async
        if not is_supported():
            self.logger.debug("当前平台不支持桌面通知（仅 Windows），跳过本次通知")
            return
        self.logger.info(f"发送桌面通知：{title} | {message}")
        notify_async(title, message, logger=self.logger)

    def notify_preset_finished(self) -> None:
        """临时预设模式：预设任务全部执行完毕后通知用户。"""
        username = self.config.get_config("用户名", "未知用户")
        self.service._notify_user(
            "玄的日常助手 · 预设执行完毕",
            f"{username}：预设任务已全部执行完毕"
            f"（共 {self.service._preset_total} 个任务），调度器已自动停止")

    def notify_account_idle(self, now: datetime) -> None:
        """账号配置模式：执行告一段落时通知用户。

        判定（与需求一致）：执行队列与就绪队列均为空，且最早的等待队列项
        （仅统计已启用的任务）排期也在 ``IDLE_NOTIFY_THRESHOLD``（1 小时）之后；
        队列里已无待执行任务时同样视为告一段落。

        去抖：同一段空闲只通知一次（``idle_notified``）；一旦有任务进入执行/就绪
        队列即重新武装，便于下一次告一段落再次提醒。另外，本次启动后尚未执行过
        任何任务（刚启动）时不通知，避免刚打开就弹窗。

        时机：本方法在扫描末尾（任务入队/抢占判定之后）与任务完成回调中
        （``_process_pending_activations`` 之后）都会被调用。若回调里还有登记的
        待激活任务（``_pending_activate_tasks``）尚未落地，此刻队列虽空但马上会有
        任务替补进就绪/执行队列，因此直接按"尚未告一段落"处理，不发通知。
        """
        service = self.service
        if service.run_once:
            return
        if service._pending_activate_tasks:
            # 待激活任务尚未处理：不能判定为空闲（否则通知刚发出任务就补位）
            self.idle_notified = False
            return
        if (service.task_queue.get_tasks_by_status(0)
                or service.task_queue.get_tasks_by_status(1)):
            # 有任务在执行/待执行 → 重新武装通知
            self.idle_notified = False
            return
        if service._completed_count == 0:
            return
        if self.idle_notified:
            return

        upcoming = []
        for task in service.task_queue.get_tasks_by_status(2):
            if not getattr(task, "is_activated", False):
                continue
            next_execute = getattr(task, "next_execute_time", None)
            if isinstance(next_execute, datetime):
                upcoming.append(task)

        username = self.config.get_config("用户名", "未知用户")
        if not upcoming:
            self.idle_notified = True
            self.service._notify_user(
                "玄的日常助手 · 任务告一段落",
                f"{username}：所有任务已执行完毕，当前没有待执行的任务"
                "（1 小时内无排期），助手已进入空闲状态")
            return

        earliest = min(upcoming, key=lambda t: t.next_execute_time)
        if earliest.next_execute_time <= now + IDLE_NOTIFY_THRESHOLD:
            # 1 小时内有任务要跑，不算告一段落
            self.idle_notified = False
            return
        self.idle_notified = True
        hours = (earliest.next_execute_time - now).total_seconds() / 3600
        self.service._notify_user(
            "玄的日常助手 · 任务告一段落",
            f"{username}：当前所有任务已执行完毕，下一个任务"
            f"「{earliest.task_name}」将于 "
            f"{earliest.next_execute_time.strftime('%m-%d %H:%M')} 执行"
            f"（约 {hours:.1f} 小时后）")
