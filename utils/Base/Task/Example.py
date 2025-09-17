from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class Example(BaseTask):
    @TransitionOn()
    def _(self):
        self.update_next_execute_time()
        return True
