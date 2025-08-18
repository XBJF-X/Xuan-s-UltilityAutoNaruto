class TaskError(Exception):
    """任务执行异常的基类"""
    pass


class StepFailedError(TaskError):
    """步骤执行失败异常（如检测失败、点击无响应等）"""
    pass


class TimeOut(TaskError):
    """步骤执行失败异常（如检测失败、点击无响应等）"""
    pass


class EndEarly(TaskError):
    """步骤已经不需要再执行下去了，所以提前结束"""
    pass


class Stop(TaskError):
    """步骤已经不需要再执行下去了，所以提前结束"""
    pass
