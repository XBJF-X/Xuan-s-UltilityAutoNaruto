import time
import datetime


from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn

class RenFaTieJiangLi(BaseTask):
    source_scene = "忍法帖-周任务"
    task_max_duration = datetime.timedelta(minutes=3)
    # 任务内进度标记：run() 每次执行前重置为 False，_handle_execution_completed 用它
    # 决定下次执行时间（类属性默认值保证未执行过 run() 的路径也能安全读取）
    all_tasks = False
    all_activations = False


    def run(self):
        self.all_tasks=False
        self.all_activations=False
        super().run()

    @TransitionOn()
    def _(self):
        if not self.operationer.click_and_wait("领取",random=True):
            self.all_tasks=True
            self.logger.info("所有周任务经验已领取完毕，跳转至周活跃度奖励")
            self.operationer.click_and_wait("周活跃")

        return False
    
    @TransitionOn("忍法帖-周活跃")
    def _(self):
        yl=self.operationer.ocr_recognize("已领")
        # 统计"已领"命中数：原写法 len([bool...]) 等于 OCR 结果条数，与命中无关
        if sum(item.text == "已领" for item in yl) == 5:
            self.all_activations=True
            return True
        TIERS = [50,100,150,200,300]
        hyd=self.operationer.ocr_recognize("本周活跃度值")
        if hyd:
            hyd_num=hyd.get_single_number()
            if hyd_num:
                # 仅领取当前活跃度值已超过的档位：原写法生成布尔列表后把布尔值当档位号用
                for tier in TIERS:
                    if tier >= hyd_num:
                        continue
                    self.operationer.click_and_wait(f"活跃度-{tier}",click_times=2)
                    self.logger.info(f"活跃度[{tier}]奖励已领取")
        return False


    def _get_execute_window(self,dt: datetime.datetime | None = None):
        if dt is None:
            dt=self.last_run_time
        today = dt.date()
        if dt.time() < datetime.time(5, 1):
            today -= datetime.timedelta(days=1)
        
        # 计算today所在的周一
        this_monday = today - datetime.timedelta(days=today.weekday())

        start_dt = datetime.datetime.combine(this_monday, datetime.time(5, 1), tzinfo=self.tz_info)
        dead_dt = datetime.datetime.combine(this_monday+datetime.timedelta(weeks=1), datetime.time(5, 1), tzinfo=self.tz_info)

        return [(start_dt, dead_dt)]
    
    def get_next_cycle_day(self, dt: datetime.datetime) -> datetime.datetime:
        return dt + datetime.timedelta(weeks=1)

    def _handle_execution_completed(
            self, current_time: datetime.datetime) -> datetime.datetime:
        """返回下一次执行时间。

        - 周任务经验与周活跃度奖励都已领完（all_tasks 与 all_activations 均为 True）：
          本周期已无事可做，排到下一周周一 5:01。直接复用 BaseTask 的周期计算
          （completed=True 取所属周期的下一周期起点）配合本类的周窗口得到；
        - 否则仍按日周期补领：今天未过 5:01 则今天 5:01，已过则明天 5:01。
          复用 BaseTask 的日窗口换算（5:01 为日界），不重复实现日界规则。
        """
        current_time = self._ensure_tz_aware(current_time)
        if self.all_tasks and self.all_activations:
            return self.get_cycle_execute_time(current_time, completed=True)
        # 本类的 _get_execute_window 已被重写为周维度，日周期须显式取 BaseTask 的日窗口：
        # completed 语义 = 先前进一个日周期，再取该周期起点（今天/明天 5:01）
        daily_window = BaseTask._get_execute_window(
            self, current_time + datetime.timedelta(days=1))
        return daily_window[0][0]