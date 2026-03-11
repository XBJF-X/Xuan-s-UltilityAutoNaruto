from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Exceptions import StepFailedError, EndEarly
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class ShengCunTiaoZhan(BaseTask):
    source_scene = "生存挑战"
    task_max_duration = timedelta(minutes=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_need_reset = False  # 标志是否需要检查重置
        self.bool_start = False  # 标志是否已开始扫荡

    @TransitionOn()
    def _(self):
        if not self.bool_start:
            if self.check_need_reset:
                if self.operationer.click_and_wait(
                        "重置",
                        wait_time=0,
                        auto_raise=False
                ):
                    if self.operationer.detect_element(
                            "生存挑战今天已经不能再重置了",
                            max_time=1
                    ):
                        self.logger.warning("已经不能再重置了，结束执行")
                        self.update_next_execute_time()
                        return True
                    else:
                        self.check_need_reset = False

            self.logger.info("开始扫荡")
            # 点击开始扫荡图标
            self.operationer.click_and_wait(
                "开始扫荡",
                wait_time=0
            )
            flag = self.operationer.search_and_detect(
                [
                    self.operationer.get_element("没有可以出战的忍者"),
                    self.operationer.get_element("已通过所有关卡")
                ],
                [],
                search_max_time=1.5,
                once_max_time=0.3
            )
            if flag:
                if flag == 1:
                    self.logger.warning("没有可出战的忍者，将进行重置")
                elif flag == 2:
                    self.logger.warning("已通过所有关卡，将进行重置")
                self.check_need_reset = True
            else:
                self.logger.debug("将开始扫荡")

        else:
            self.operationer.click_and_wait("出战", wait_time=0)
            # 等待生存挑战-已通过所有关卡出现
            if self.operationer.search_and_detect(
                    [
                        self.operationer.get_element("已通过所有关卡"),
                        self.operationer.get_element("没有可以出战的忍者"),
                    ],
                    [],
                    search_max_time=3,
                    once_max_time=0.4
            ):
                self.logger.info("系统自动扫荡结束")
                self.bool_start = False
                self.check_need_reset = True

        return False

    @TransitionOn("生存挑战-出战名单")
    def _(self):
        self.operationer.click_and_wait("准备就绪")
        return False

    @TransitionOn("出战名单-确认")
    def _(self):
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("生存挑战-扫荡确认")
    def _(self):
        self.operationer.click_and_wait("确定", wait_time=2)
        self.bool_start = True
        return False

    @TransitionOn("生存挑战-传送")
    def _(self):
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("生存挑战-重置")
    def _(self):
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("生存挑战-购买扫荡券")
    def _(self):
        self.operationer.click_and_wait("X")
        self.logger.warning("扫荡券不足，将停止扫荡，等待第二天执行，请自行解决扫荡券不足任务")
        self.update_next_execute_time()
        return True

    def reset_task_exe_proc(self) -> bool:
        self.check_need_reset = False
        self.bool_start = False
        return True
