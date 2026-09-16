class TaskError(Exception):
    """任务执行异常的基类"""
    pass


class StepFailedError(TaskError):
    """步骤执行失败异常（如检测失败、点击无响应等）"""
    pass


class TimeOutDeadLineError(TaskError):
    """步骤执行超时"""
    pass

class TimeOutMaxDurationError(TaskError):
    """步骤执行超时"""
    pass


class TaskCompleted(TaskError):
    """任务正常完成"""
    pass


class TooEarlyToRun(TaskError):
    """执行时间早于任务可执行窗口"""
    pass


class Stop(TaskError):
    """任务被要求停止"""
    pass


# --------------------------------------------------------------------------- #
#                            停止原因（Stop 分支据此区分收尾动作）                 #
# --------------------------------------------------------------------------- #
# 由 BaseTask.stop(reason=...) / TaskExecutor.stop_task(task, reason=...) 传递：
# 卡死类停止（STUCK / FROZEN）意味着"任务未能自行恢复"，下次执行时间不能留在
# 过去（否则会被调度器按扫描间隔立刻重跑），必须由 on_stuck 重新排期（冷却重试）。
STOP_REASON_UNKNOWN = ""
STOP_REASON_STUCK = "stuck"      # 超时监视器判定「场景停滞」且任务自救失败
STOP_REASON_FROZEN = "frozen"    # 超时监视器判定「游戏/模拟器卡死」
# 卡死类停止原因的集合（供 BaseTask 判定是否走 on_stuck 冷却重试）
STUCK_STOP_REASONS = (STOP_REASON_STUCK, STOP_REASON_FROZEN)
