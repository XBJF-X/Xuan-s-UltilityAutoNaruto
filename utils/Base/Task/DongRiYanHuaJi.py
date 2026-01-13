from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class DongRiYanHuaJi(BaseTask):
    source_scene = "冬日烟花季-主页"
    dead_line = time(22, 0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bool_light_fireworks = False
        self.operationer.clicker.update_coordinates([
            [self.operationer.get_element("领取", "冬日烟花季-主页").coordinate_x,
                self.operationer.get_element("领取", "冬日烟花季-主页").coordinate_y],
            [self.operationer.get_element("关闭红包", "冬日烟花季-主页").coordinate_x,
                self.operationer.get_element("关闭红包", "冬日烟花季-主页").coordinate_y]
        ])

    @TransitionOn()
    def _(self):
        if not self.bool_light_fireworks:
            self.operationer.clicker.stop()
            self.operationer.click_and_wait("点燃烟火")
            self.operationer.click_and_wait("免费烟火")
            self.bool_light_fireworks = True
            return False
        if datetime.now(tz=ZoneInfo("Asia/Shanghai")) < self.temp_dead_line:
            self.operationer.clicker.start()
            return False
        self.operationer.clicker.stop()
        self.update_next_execute_time()
        return True

    @TransitionOn("冬日烟花季-点燃免费爆竹")
    def _(self):
        self.operationer.click_and_wait("是")
        return False

    def update_next_execute_time(self, flag: int = 1, delta: timedelta = None):
        """
        用于更新本任务的下次执行时间

        Args:
            flag: 更新下次执行时间的模式
                0：创建任务时初始化时间
                1：正常执行完毕，更新为下次执行时间
                3：把执行时间推迟delta时间，要求 delta!=None
            delta: 延迟的时长（仅flag=3时有效）
        Returns:
            tuple: (是否成功, 下次执行时间datetime对象)
        """
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        try:
            match flag:
                case 0 | 2:
                    next_execute_time = self._handle_initialization(current_time)
                case 1:
                    next_execute_time = self._handle_execution_completed(current_time)
                case 3:
                    next_execute_time = self._handle_delay(current_time, delta)
                case _:
                    self.logger.warning(f"不支持的更新模式: {flag}")
                    return False, None

            if next_execute_time is None:
                return False, None

            self.logger.info(f"下次执行时间为：{next_execute_time.strftime('%Y-%m-%d %H:%M:%S')}")
            self.config.set_task_base_config(
                self.task_name,
                "下次执行时间",
                int(next_execute_time.timestamp())
            )
            return True, next_execute_time

        except Exception as e:
            self.logger.error(f"更新下次执行时间失败: {str(e)}")
            return False, None

    def _handle_initialization(self, current_time: datetime) -> datetime:
        """处理任务初始化时的时间设置（case0）"""
        china_tz = current_time.tzinfo

        next_execute_time = datetime(
            current_time.year,
            current_time.month,
            current_time.day,
            19, 0, 00,
            tzinfo=china_tz
        )
        return next_execute_time

    def _handle_execution_completed(self, current_time: datetime) -> datetime:
        """处理任务执行完成后的时间更新（case1）"""
        china_tz = current_time.tzinfo
        next_day = current_time + timedelta(days=1)
        return datetime(
            next_day.year,
            next_day.month,
            next_day.day,
            19, 0, 20,
            tzinfo=china_tz
        )
