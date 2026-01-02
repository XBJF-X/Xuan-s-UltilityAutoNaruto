from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask


# Todo：完善组织争霸
class ZuZhiZhengBa(BaseTask):
    def _execute(self):
        # 确定在主场景

        self.update_next_execute_time()
