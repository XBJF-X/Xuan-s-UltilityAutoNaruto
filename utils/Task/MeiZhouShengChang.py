from datetime import datetime, timedelta

from utils.KeyMapConfiguration import KEY_INDEX
from utils.Task import MeiRiShengChang
from utils.Task.BaseTask import BaseTask


class MeiZhouShengChang(MeiRiShengChang):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        self.logger.info("进入[决斗场-首页]")
        if not self.search_and_click(
                [
                    {"type": "ELEMENT", "name": "主场景-决斗场"}
                ],
                [
                    {
                        "swipe": {
                            "start_coordinate": [1345, 86],
                            "end_coordinate": [462, 86],
                            "duration": 1
                        }
                    }
                ],
                max_attempts=2

        ):
            if not self.search_and_click(
                    [
                        {"type": "ELEMENT", "name": "主场景-决斗场"}
                    ],
                    [
                        {
                            "swipe": {
                                "start_coordinate": [462, 86],
                                "end_coordinate": [1345, 86],
                                "duration": 1
                            }
                        }
                    ],
                    max_attempts=2

            ):
                raise self.StepFailedError("无法进入[决斗场]")
        self.detect_and_wait({'type': "SCENE", 'name': "决斗场-首页"})
        self.logger.info("进入[决斗场-忍术对战-单人模式]")
        self.click_and_wait({'type': "ELEMENT", 'name': "决斗场-忍术对战"})
        self.detect_and_wait({'type': "SCENE", 'name': "决斗场-忍术对战-单人模式"})
        self.logger.info("查看[决斗场-忍术对战-单人模式-决斗任务]")
        self.click_and_wait({'type': "ELEMENT", 'name': "决斗场-忍术对战-单人模式-决斗任务"})
        self.detect_and_wait({'type': "SCENE", 'name': "决斗场-忍术对战-单人模式-决斗任务"})
        self.logger.info("领取所有待领取的决斗任务宝箱")
        while self.click_and_wait(
                {'type': "ELEMENT", 'name': "决斗任务-宝箱-待领取"},
                auto_raise=False
        ):
            continue

        # 假如周胜场没满，则继续挂周胜
        while not self.detect_and_wait(
                {'type': "ELEMENT", 'name': "决斗任务-满胜场"},
                max_time=1,
                auto_raise=False
        ):
            self.logger.warning("周胜场未满，继续执行")
            # 点掉决斗任务窗口
            self.click_and_wait({'type': "COORDINATE", 'coordinate': [1523, 45]})
            self.fight()
            self.logger.info("查看[决斗场-忍术对战-单人模式-决斗任务]")
            self.click_and_wait({'type': "ELEMENT", 'name': "决斗场-忍术对战-单人模式-决斗任务"})
            self.detect_and_wait({'type': "SCENE", 'name': "决斗场-忍术对战-单人模式-决斗任务"})
            self.logger.info("领取所有待领取的决斗任务宝箱")
            while self.click_and_wait(
                    {'type': "ELEMENT", 'name': "决斗任务-宝箱-待领取"},
                    max_time=3,
                    auto_raise=False
            ):
                continue
        self.logger.warning("周胜场已满")
        # 点掉决斗任务弹窗
        self.click_and_wait({'type': "COORDINATE", 'coordinate': [1523, 45]})
        self._update_next_execute_time(delta=time_until_next_sunday_noon())


def time_until_next_sunday_noon():
    # 获取当前时间
    now = datetime.now()

    # 计算下一个周日的日期
    # weekday() 返回：0=周一, 1=周二, ..., 6=周日
    days_until_sunday = (6 - now.weekday()) % 7 or 7  # 如果今天是周日，则取7天
    next_sunday = now + timedelta(days=days_until_sunday)

    # 设置时间为下周日12:00:00
    next_sunday_noon = datetime(next_sunday.year, next_sunday.month, next_sunday.day, 12, 0, 0)

    # 计算时间差（确保结果非负）
    delta = next_sunday_noon - now
    return delta if delta.total_seconds() > 0 else timedelta(0)