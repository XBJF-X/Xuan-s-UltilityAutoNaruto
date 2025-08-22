from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Base.Exceptions import StepFailedError, EndEarly
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class DengLuJiangLi(BaseTask):
    task_max_duration = timedelta(minutes=5)

    @TransitionOn("Default")
    def _(self):
        self.operationer.restart()
        if not self.operationer.search_and_detect(
                [self.scene_graph.scenes.get("登录")],
                [],
                search_max_time=120
        ):
            raise StepFailedError("加载到游戏登录界面失败")
        if not self.operationer.search_and_click(
                [self.scene_graph.scenes.get("登录").elements.get("开始游戏")],
                [],
                search_max_time=300
        ):
            raise StepFailedError("未出现[开始游戏]按钮，请检查是否掉授权或网络情况差")

        if not self.operationer.search_and_detect(
            [self.scene_graph.scenes.get("登录奖励")],
            [
                {'click': self.scene_graph.scenes.get("主场景").elements.get("公告-X")},
                {'click': self.scene_graph.scenes.get("主场景").elements.get("广告-X")}
            ],
            search_max_time=60,
            wait_time=3
        ):
            self._update_next_execute_time()
            raise EndEarly("未弹出登录奖励窗口，可能已领取")
        self.operationer.click_and_wait(self.scene_graph.scenes.get("登录奖励").elements.get("领取"))
        self.operationer.search_and_detect(
            [self.scene_graph.scenes.get("主场景")],
            [
                {'click': self.scene_graph.scenes.get("主场景").elements.get("公告-X")},
                {'click': self.scene_graph.scenes.get("主场景").elements.get("广告-X")}
            ],
            search_max_time=10,
            wait_time=3
        )
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
