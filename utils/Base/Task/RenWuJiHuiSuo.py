from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Base.Exceptions import EndEarly, StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class RenWuJiHuiSuo(BaseTask):
    source_scene = "任务集会所"
    task_max_duration = timedelta(minutes=3)

    @TransitionOn()
    def _(self):
        self.logger.info("开始领取任务奖励")
        # 点掉所有的可领取
        while self.operationer.click_and_wait(
                "可领取",
                auto_raise=False
        ):
            # 如果少于3个，则点击领取会直接弹出恭喜你获得弹窗
            if self.operationer.detect_element(
                    "恭喜你获得",
                    wait_time=0,
                    auto_raise=False
            ):
                # 随便点一下，关掉弹窗
                self.operationer.click_and_wait("X")
                # 这个时候不需要检测有没有一键领取所有奖励的弹窗了，可以直接下一次领取了
                continue
            # 假如可领取的多于等于3个，会出现让你确认是否一键领取的弹窗，我们直接看看能不能点击确认
            # 能点击确认的话就说明出现了弹窗，那就按照多于三个的逻辑来
            if self.operationer.click_and_wait(
                    "一键领取所有奖励-确定",
                    auto_raise=False
            ):
                # 出现恭喜你获得弹窗
                if self.operationer.detect_element(
                        "恭喜你获得",
                        wait_time=0,
                        auto_raise=False
                ):
                    # 随便点一下，关掉弹窗
                    self.operationer.click_and_wait("X")
                    # 可以直接结束奖励领取的循环了
                    self.logger.info("一键领取所有奖励")
                    break

        self.logger.info("开始接取任务")
        # 先看看是不是已经领完了所有任务了
        if self.operationer.detect_element(
                "今天所有任务已经领完",
                auto_raise=False
        ):
            self.update_next_execute_time()
            raise EndEarly("今日任务已经领完，提前退出执行")

        task_sum = 0

        while not self.operationer.search_and_detect(
                [
                    self.operationer.current_scene.elements.get("任务栏满了"),
                    self.operationer.current_scene.elements.get("今天所有任务已经领完"),
                ],
                [],
                once_max_time=1,
                search_max_time=2,
                bool_debug=True
        ):
            # 点掉所有的接取按钮，直到出现任务栏已满的提示
            while self.operationer.click_and_wait(
                    "接取",
                    auto_raise=False
            ):
                if not self.operationer.search_and_click(
                        [
                            "接取-推荐小队",
                            "接取-默认忍者"
                        ],
                        [],
                        max_attempts=2

                ):
                    raise StepFailedError("安排任务忍者失败")
                # 出战
                self.operationer.click_and_wait(
                    "接取-出战",
                    wait_time=0
                )
                # 检查任务栏是否已满
                match self.operationer.search_and_detect(
                        [
                            self.operationer.current_scene.elements.get("任务栏满了"),
                            self.operationer.current_scene.elements.get("今天所有任务已经领完"),
                        ],
                        [],
                        once_max_time=1,
                        search_max_time=2
                ):
                    case 0:
                        task_sum += 1
                        self.logger.info(f"已接取 {task_sum} 个任务")
                    case 1:
                        self.operationer.click_and_wait("X")
                        self.update_next_execute_time(3, timedelta(hours=1))
                        raise EndEarly("任务栏已满，等待下次检查")
                    case 2:
                        self.operationer.click_and_wait("X")
                        self.update_next_execute_time()
                        raise EndEarly("任务栏已满/今日任务已经领完")
            if self.operationer.click_and_wait(
                    "超影免费",
                    auto_raise=False
            ):
                self.logger.info("刷新任务列表")
            else:
                # 能接取的都接了，无法刷新，可以退出执行了
                self.operationer.click_and_wait("X")
                self.update_next_execute_time(3, timedelta(hours=1))
                raise EndEarly("无法刷新，提前退出执行")
        self.operationer.click_and_wait("X")
        self.update_next_execute_time(3, timedelta(hours=1))
        return True

    def update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
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
                    return False, None
                self.next_execute_time = current_time + delta

            case _:
                self.logger.warning(f"请检查update_next_execute_time传入的参数：flag={flag},delta={delta}")
                return False, None

        self.logger.info(f"下次执行时间为：{self.next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
        self.config.set_task_config(self.task_name, "下次执行时间", int(self.next_execute_time.timestamp()))
        return True, self.next_execute_time