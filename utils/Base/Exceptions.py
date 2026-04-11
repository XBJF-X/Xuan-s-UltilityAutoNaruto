class TaskError(Exception):
    """任务执行异常的基类"""
    pass


class StepFailedError(TaskError):
    """步骤执行失败异常（如检测失败、点击无响应等）"""
    pass


class TimeOut(TaskError):
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
