"""调度器内部常量（阶段 4 逐步从 scheduler_service 抽出）

放在独立模块是为了避免"协作者 ← 服务"的循环导入：协作者需要常量，
而服务需要 import 协作者。
"""
from datetime import timedelta

# ===== 账号配置模式“告一段落”判定 =====
# 执行队列与就绪队列均为空，且最早的等待任务排期也在该阈值之后时，
# 视为本段时间的执行告一段落，向用户发送一次桌面通知
IDLE_NOTIFY_THRESHOLD = timedelta(hours=1)

__all__ = ["IDLE_NOTIFY_THRESHOLD"]
