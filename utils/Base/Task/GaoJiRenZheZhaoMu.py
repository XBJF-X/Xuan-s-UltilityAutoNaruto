import datetime
from datetime import timedelta

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class GaoJiRenZheZhaoMu(BaseTask):
    source_scene = "高级招募"
    task_max_duration = timedelta(minutes=3)

    @TransitionOn()
    def _(self):
        self.logger.info("进行免费高级招募")
        # 点击高级招募-免费
        if self.operationer.click_and_wait("免费"):
            self.logger.info("免费高级招募成功")
            return False
        else:
            self.logger.warning("免费高级招募失败")
            self.update_next_execute_time(3, timedelta(minutes=10))
        self.operationer.click_and_wait("X")
        return True

    @TransitionOn("招募结果")
    def _(self):
        while not self.operationer.search_and_click(
                [
                    "确定"
                ],
                [
                    {
                        "click": {
                            "type": "COORDINATE",
                            "coordinate": [800, 730]
                        }
                    }
                ],
                max_attempts=2,
                once_max_time=5
        ):
            continue
        self.update_next_execute_time(3, timedelta(days=2))
        return True

    @TransitionOn("招募忍者已拥有")
    def _(self):
        self.operationer.click_and_wait("确定")
        return False

    def _handle_initialization(self, current_time: datetime.datetime) -> datetime.datetime:
        """处理任务初始化时的时间设置（case0）"""
        china_tz = current_time.tzinfo
        # 读取配置中的时间
        next_exec_ts = self.config.get_task_base_config(self.task_name, "下次执行时间")

        # 高级忍者招募的本周期执行时间默认为当前时间
        next_execute_time = current_time

        if not next_exec_ts:
            # 配置中未设置下次执行时间，返回默认时间
            return next_execute_time

        try:
            next_exec_dt = datetime.datetime.fromtimestamp(next_exec_ts, tz=china_tz)
        except Exception as e:
            self.logger.warning(f"解析下次执行时间戳失败: {next_exec_ts}, 错误: {e}")
            return next_execute_time

        # 判断下次执行时间是否过期
        if next_exec_dt < current_time:
            return next_execute_time

        # 配置中的下次执行时间未过期，直接返回
        return next_exec_dt