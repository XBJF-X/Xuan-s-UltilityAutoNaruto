from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class Example(BaseTask):
    @TransitionOn()
    def _execute(self):
        # 此时已经进入了[我指定的那个场景]

        # 从配置文件中读所有的小关卡的完成情况
        config = self.config.get_config("XXX")

        if not config["关卡1"]:
            # 搜索点进关卡，执行你的派遣之类的，没看懂，但是流程应该挺固定

            # 设置配置项为True

            # 执行结束直接在这里返回[我指定的那个场景]
            if self._stop_event.is_set():
                return True
            return False

        elif config["关卡2"]:
            # 同上
            return False
        # .....

        # 执行结束，更新下次执行时间

        self.update_next_execute_time()
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
                pass

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
