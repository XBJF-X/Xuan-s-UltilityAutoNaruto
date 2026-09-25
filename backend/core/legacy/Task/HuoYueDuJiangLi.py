from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn


class HuoYueDuJiangLi(BaseTask):
    source_scene = "奖励"
    task_max_duration = timedelta(minutes=3)

        
    def run(self):
        self.finished = False
        return super().run()
    @TransitionOn()
    def _(self):
        if self.finished:
            if self.reset_task_exe_prog():
                raise TaskCompleted("活跃度奖励领取完成")
            else:
                self.schedule_next_with_delay(timedelta(hours=3))
                raise TaskCompleted("活跃度不足，延迟重试")
            
        hyd=self.operationer.ocr_recognize("活跃度")
        hyd_num=hyd.get_first_number() or 100

        TIERS=[10,40,80,100]

        filter_tiers=[x for x in TIERS if x <= hyd_num]
        
        for tier in filter_tiers:
            self.operationer.click_and_wait(f"每日活跃度-{tier}-待领取",wait_time=1,max_time=1.5,click_times=2,click_interval=1)
            if self.operationer.detect_element(f"每日活跃度-{tier}-已领取",wait_time=0, max_time=1):
                self.config.set_task_exe_prog(self.task_name, f"{tier}活跃度已领取", True)

        if not self.config.get_task_exe_prog(self.task_name, f"周活跃礼已领取", False):
            self.operationer.click_and_wait("周活跃礼")
            return False
        
        self.finished = True
        return False

    @TransitionOn("周活跃大礼")
    def _(self):
        if self.operationer.click_and_wait("领取"):
            self.config.set_task_exe_prog(self.task_name, f"周活跃礼已领取", True)
            self.logger.info("周活跃奖励领取成功")
        self.operationer.click_and_wait("X")
        self.finished = True
        return False

        


    def reset_task_exe_prog(self) -> bool:
        self.finished = False
        if (self.config.get_task_exe_prog(self.task_name, f"周活跃礼已领取", False) and
                datetime.now(ZoneInfo("Asia/Shanghai")).weekday() == 6):
            # 每周日重置周活跃领取状态
            self.config.set_task_exe_prog(self.task_name, f"周活跃礼已领取", False)
        flag = all([
            self.config.get_task_exe_prog(self.task_name, f"10活跃度已领取", False),
            self.config.get_task_exe_prog(self.task_name, f"40活跃度已领取", False),
            self.config.get_task_exe_prog(self.task_name, f"80活跃度已领取", False),
            self.config.get_task_exe_prog(self.task_name, f"100活跃度已领取", False)
        ])
        self.config.set_task_exe_prog(self.task_name, f"10活跃度已领取", False)
        self.config.set_task_exe_prog(self.task_name, f"40活跃度已领取", False)
        self.config.set_task_exe_prog(self.task_name, f"80活跃度已领取", False)
        self.config.set_task_exe_prog(self.task_name, f"100活跃度已领取", False)
        if flag:
            self.logger.debug("所有活跃度奖励已领取")
            return True
        else:
            self.logger.debug("存在未领取活跃度奖励")
            return False
