from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Task.BaseTask import BaseTask


class JinBiZhaoCai(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        if self.config.get_config("已金币招财次数") >= self.data.get("招财次数", 0):
            self._update_next_execute_time()
            self.config.set_config("已金币招财次数", 0)
            raise self.EndEarly("已招满金币招财")
        self.logger.info("进入金币招财界面")
        # 点击金币招财图标
        self.click_and_wait({"type": "COORDINATE", "coordinate": [950, 50]})
        # 确认招财界面出现
        self.detect_and_wait({"type": "SCENE", "name": "招财"})
        # 确认免费招财按钮出现
        if self.detect_and_wait(
                {"type": "ELEMENT", "name": "招财-免费一次"},
                auto_raise=False
        ):
            # 点击两次招财-免费一次
            self.click_and_wait({"type": "ELEMENT", "name": "招财-免费一次"})
            self.logger.info(f"已招财 1 次")
            self.click_and_wait({"type": "ELEMENT", "name": "招财-免费一次"})
            self.logger.info(f"已招财 2 次")
        else:
            self.logger.debug("不存在免费招财次数")
        self.config.set_config("已金币招财次数", 2)
        times = self.config.get_config("已金币招财次数")
        while times < self.data.get("招财次数", 2):
            self.click_and_wait({'type': "ELEMENT", "name": "招财-付费"})
            if not self.pass_secondary_password():
                times += 1
                self.config.set_config("已金币招财次数", times)
                self.logger.info(f"已招财 {times} 次")
        self._update_next_execute_time()
        self.config.set_config("已金币招财次数", 0)

    def _update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        match flag:

            case 0:  # 创建任务时使用，需要读取config中的时间，按照空/已存在分别处理
                next_exec_ts = self.data.get('下次执行时间')
                if next_exec_ts == 0:
                    # 若初始值为0，设置为当前UTC时间（或其他合理时间）
                    self.next_execute_time = datetime.now(ZoneInfo("Asia/Shanghai"))
                else:
                    # 从时间戳转换为datetime对象（指定UTC时区避免歧义）
                    self.next_execute_time = datetime.fromtimestamp(next_exec_ts, tz=ZoneInfo("Asia/Shanghai"))

            case 1:  # 正常执行完毕，更新为下次执行的时间
                next_day = current_time + timedelta(days=1)
                # 新建时间时指定时区（与current_time一致）
                self.next_execute_time = datetime(
                    next_day.year, next_day.month, next_day.day, 5, 0,
                    tzinfo=china_tz  # 关键：添加时区信息
                )

            case 2:  # 立刻执行，通常把时间重置到能保证第二天之前即可，不同的任务分别处理
                self.next_execute_time = datetime.now(ZoneInfo("Asia/Shanghai"))

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
