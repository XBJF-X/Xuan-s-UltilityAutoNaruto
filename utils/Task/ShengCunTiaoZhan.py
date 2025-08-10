from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.Task.BaseTask import BaseTask


class ShengCunTiaoZhan(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        self.logger.info("进入[奖励]界面")
        # 点击奖励图标
        self.click_and_wait({"type": "ELEMENT", "name": "主场景-奖励"})
        # 确认奖励界面出现
        self.detect_and_wait({"type": "SCENE", "name": "奖励"})
        self.logger.info("跳转至[生存挑战]")
        # 点击完成1关生存挑战-立刻前往
        if not self.search_and_click(
                [
                    {"type": "ELEMENT", "name": "完成1关生存挑战-立刻前往"}
                ],
                [
                    {
                        "swipe": {
                            "start_coordinate": [1504, 340],
                            "end_coordinate": [344, 340],
                            "duration": 1
                        }
                    }
                ],
                max_attempts=3
        ):
            self._update_next_execute_time()
            raise self.EndEarly("无法跳转到[生存挑战]，可能已经完成")
        # 确认生存挑战界面出现
        self.detect_and_wait({"type": "SCENE", "name": "生存挑战"})
        self.logger.info("关闭系统自动打的弹窗")
        # 随便点一下把自动打的弹窗点掉
        self.click_and_wait({"type": "COORDINATE", "coordinate": [800, 750]})
        self.click_and_wait({"type": "COORDINATE", "coordinate": [800, 750]})
        self.logger.info("开始扫荡")
        # 点击开始扫荡图标
        self.click_and_wait(
            {'type': "ELEMENT", 'name': "生存挑战-开始扫荡"},
            wait_time=0
        )
        flag = self.search_and_detect(
            [
                {'type': "ELEMENT", 'name': "生存挑战-没有可以出战的忍者"},
                {'type': "ELEMENT", 'name': "生存挑战-已通过所有关卡"}
            ],
            [],
            search_max_time=2,
            once_max_time=0.5
        )
        if flag:
            if flag == 1:
                self.logger.warning("没有可出战的忍者，将进行重置")
            elif flag == 2:
                self.logger.warning("已通过所有关卡，将进行重置")
            if self.click_and_wait(
                    {'type': "ELEMENT", 'name': "生存挑战-重置"},
                    auto_raise=False
            ):
                self.click_and_wait({'type': "ELEMENT", 'name': "生存挑战-重置-确认"})
                # 随便点一下把自动打的弹窗点掉
                self.click_and_wait({"type": "COORDINATE", "coordinate": [800, 750]})
                self.click_and_wait({"type": "COORDINATE", "coordinate": [800, 750]})
                self.logger.info("重置后再次开始扫荡")
                # 点击开始扫荡图标
                self.click_and_wait({'type': "ELEMENT", 'name': "生存挑战-开始扫荡"})

        # 点击准备就绪
        self.click_and_wait({'type': "ELEMENT", 'name': "生存挑战-准备就绪"})
        self.logger.info("准备就绪")
        # 点击确定
        self.click_and_wait(
            {'type': "ELEMENT", 'name': "生存挑战-准备就绪-确定"},
            wait_time=3
        )
        # 点击确定
        self.click_and_wait(
            {'type': "ELEMENT", 'name': "生存挑战-准备就绪-确定-确定"},
            wait_time=3
        )
        self.logger.info("系统开始自动扫荡")

        # 等待生存挑战-已通过所有关卡出现
        if not self.search_and_detect(
                [
                    {'type': "ELEMENT", 'name': "生存挑战-已通过所有关卡"}
                    # {'type': "ELEMENT",'name': "生存挑战-可出战的忍者不足"},
                ],
                [],
                search_max_time=100
        ):
            raise self.StepFailedError("检测[生存挑战-已通过所有关卡]超时")
        self.logger.info("系统自动扫荡结束")
        self._update_next_execute_time()

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
