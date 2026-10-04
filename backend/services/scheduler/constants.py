"""调度器内部常量（阶段 4 逐步从 scheduler_service 抽出）

放在独立模块是为了避免"协作者 ← 服务"的循环导入：协作者需要常量，
而服务需要 import 协作者。
"""
from datetime import timedelta

# ===== 账号配置模式“告一段落”判定 =====
# 执行队列与就绪队列均为空，且最早的等待任务排期也在该阈值之后时，
# 视为本段时间的执行告一段落，向用户发送一次桌面通知
IDLE_NOTIFY_THRESHOLD = timedelta(hours=1)

# ===== 立即执行的触发来源 =====
# 用户点「执行」（手动）：默认做**窗口预检**，窗口外拒绝并返回原因（可显式强制忽略）
SOURCE_MANUAL = "manual"
# 任务结束后激活另一任务（`BaseTask._activate_another_task`）：窗口守卫见 skip_expired_activation
SOURCE_ACTIVATION = "activation"

__all__ = ["IDLE_NOTIFY_THRESHOLD", "SOURCE_MANUAL", "SOURCE_ACTIVATION"]
