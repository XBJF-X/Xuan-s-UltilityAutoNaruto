from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask


class DianFengDuiJue(BaseTask):
    def _execute(self):

        # 执行逻辑部分

        self.update_next_execute_time()

