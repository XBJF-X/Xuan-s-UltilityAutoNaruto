from datetime import timedelta

from utils.Base.Task.BaseTask import BaseTask

# Todo：自动叛忍任务
class PanRenLaiXi(BaseTask):
    source_scene = "叛忍来袭"
    task_max_duration = timedelta(minutes=30)
