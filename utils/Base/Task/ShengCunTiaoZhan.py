from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Exceptions import StepFailedError, EndEarly
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class ShengCunTiaoZhan(BaseTask):
    source_scene = "生存挑战"
    task_max_duration = timedelta(minutes=3)

    @TransitionOn()
    def _(self):
        self.logger.info("开始扫荡")
        # 点击开始扫荡图标
        self.operationer.click_and_wait(
            "开始扫荡",
            wait_time=0
        )
        flag = self.operationer.search_and_detect(
            [
                self.operationer.current_scene.elements.get("没有可以出战的忍者"),
                self.operationer.current_scene.elements.get("已通过所有关卡")
            ],
            [],
            search_max_time=2,
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
                    self._update_next_execute_time()
                    raise EndEarly("已经不能再重置了，结束执行")
                self.operationer.click_and_wait("重置-确认")
                # 随便点一下把自动打的弹窗点掉
                self.operationer.click_and_wait("空白点")
                self.operationer.click_and_wait("空白点")
                self.logger.info("重置后再次开始扫荡")
                # 点击开始扫荡图标
                self.operationer.click_and_wait("开始扫荡")
        # 点击准备就绪
        self.operationer.click_and_wait("准备就绪")
        self.logger.info("准备就绪")
        # 点击确定
        self.operationer.click_and_wait(
            "准备就绪-确定",
            wait_time=3
        )
        # 点击确定
        self.operationer.click_and_wait(
            "准备就绪-确定-确定",
            wait_time=3
        )
        self.logger.info("系统开始自动扫荡")

        # 等待生存挑战-已通过所有关卡出现
        if not self.operationer.search_and_detect(
                [
                    self.operationer.current_scene.elements.get("已通过所有关卡"),
                    # "可出战的忍者不足",
                ],
                [],
                search_max_time=100
        ):
            raise StepFailedError("检测[生存挑战-已通过所有关卡]超时")
        self.logger.info("系统自动扫荡结束")
        self.operationer.click_and_wait("X")
        self._update_next_execute_time()
        return True

    def _update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        match flag:

            case 0:  # 创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                next_exec_ts = self.data.get('下次执行时间')
                if next_exec_ts == 0:
                    # 若初始值为0，设置为当前UTC时间（或其他合理时间）
                    self.next_execute_time = datetime.now(china_tz)
                else:
                    # 从时间戳转换为datetime对象（指定UTC时区避免歧义）
                    self.next_execute_time = datetime.fromtimestamp(next_exec_ts, tz=china_tz)

            case 1:  # 正常执行完毕，更新为下次执行的时间
                next_day = current_time + timedelta(days=1)
                # 新建时间时指定时区（与current_time一致）
                self.next_execute_time = datetime(
                    next_day.year, next_day.month, next_day.day, 5, 0,
                    tzinfo=china_tz  # 关键：添加时区信息
                )

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                self.next_execute_time = datetime.now(china_tz)

            case 3:  # 把执行时间推迟delta时间，要求 delta!=None
                if delta is None:
                    self.logger.warning(f"update_next_execute_time传入的delta为空")
                    return
                self.next_execute_time = current_time + delta

            case _:
                self.logger.warning(f"请检查update_next_execute_time传入的参数：flag={flag},delta={delta}")
                return

        self.logger.info(f"下次执行时间为：{self.next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
        self.config.set_task_config(self.task_name, "下次执行时间", int(self.next_execute_time.timestamp()))
