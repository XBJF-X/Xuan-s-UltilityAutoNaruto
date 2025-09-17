from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Exceptions import StepFailedError, EndEarly
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class ShengCunTiaoZhan(BaseTask):
    source_scene = "生存挑战"
    task_max_duration = timedelta(minutes=3)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flag_1 = False

    @TransitionOn()
    def _(self):
        if not self.flag_1:
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
                search_max_time=1,
                once_max_time=0.3
            )
            if flag:
                if flag == 1:
                    self.logger.warning("没有可出战的忍者，将进行重置")
                elif flag == 2:
                    self.logger.warning("已通过所有关卡，将进行重置")
                if self.operationer.click_and_wait(
                        "重置",
                        wait_time=0,
                        auto_raise=False
                ):
                    if self.operationer.detect_element(
                            "生存挑战今天已经不能再重置了",
                            max_time=0.5
                    ):
                        self.update_next_execute_time()
                        raise EndEarly("已经不能再重置了，结束执行")
                    else:
                        return False
            else:
                self.flag_1 = True
                return False

        # 等待生存挑战-已通过所有关卡出现
        if not self.operationer.search_and_detect(
                [
                    self.operationer.get_element("已通过所有关卡"),
                    # "可出战的忍者不足",
                ],
                [],
                search_max_time=60
        ):
            raise StepFailedError("检测[生存挑战-已通过所有关卡]超时")
        self.logger.info("系统自动扫荡结束")
        self.operationer.click_and_wait("X")
        self.update_next_execute_time()
        return True

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
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("生存挑战-传送")
    def _(self):
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("生存挑战-重置")
    def _(self):
        self.operationer.click_and_wait("确定")
        return False
