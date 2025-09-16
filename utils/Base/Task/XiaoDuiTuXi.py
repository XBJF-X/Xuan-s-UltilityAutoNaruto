import logging
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from PySide6.QtCore import QThread

from utils.Base.Config import Config
from utils.Base.Exceptions import EndEarly, StepFailedError
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class XiaoDuiTuXi(BaseTask):
    source_scene = "小队突袭"
    task_max_duration = timedelta(minutes=10)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zhuzhan_reward_collected = False
        if self.data.get("四倍奖励勾选"):
            self.four_reward_times = self.config.get_task_config(self.task_name, "四倍奖励次数")
        else:
            self.four_reward_times = 0
        self.four_reward_collected_times = 0
        self.finished = False

    @TransitionOn("小队突袭")
    def _(self):
        self.operationer.click_and_wait("组织助战")
        return False

    @TransitionOn("小队突袭-组织助战")
    def _(self):
        if not self.zhuzhan_reward_collected:
            self.operationer.click_and_wait("我的助战")
            return False
        if not self.operationer.detect_element(
                "今日收益次数已达上限",
                auto_raise=False
        ):
            if not self._select_four_rewards():
                return True
            self.logger.info("出战")
            self.operationer.click_and_wait("出战")
            return False
        self.update_next_execute_time()
        self.logger.info("小队突袭次数已用尽")
        return True

    @TransitionOn("组织助战-助战忍者")
    def _(self):
        self.logger.info("领取助战奖励")
        # 点击领取
        if self.operationer.click_and_wait(
                "领取",
                auto_raise=False
        ):
            self.logger.info("助战奖励领取成功")
        self.zhuzhan_reward_collected = True
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("离开队伍-确认")
    def _(self):
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("副本结算-点击任意位置关闭界面")
    def _(self):
        self.operationer.click_and_wait("点击任意位置关闭界面")
        self.four_reward_collected_times += 1
        return False

    @TransitionOn("副本内")
    def _(self):
        QThread.msleep(1000)
        return False

    @TransitionOn("副本内-暂停")
    def _(self):
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("副本内-暂停-退出战斗确认")
    def _(self):
        self.operationer.click_and_wait("X")
        return False

    def _select_four_rewards(self):
        if self.four_reward_collected_times < self.four_reward_times:
            self.logger.info("勾选四倍奖励")
            if not self.operationer.detect_element(
                    "四倍奖励-选中",
                    auto_raise=False
            ):
                if not self.operationer.click_and_wait(
                        "四倍奖励-未选中",
                        auto_raise=False
                ):
                    self.logger.warning("小队突袭四倍奖励选中失败")
                    return False
        else:
            self.logger.info("取消勾选四倍奖励")
            if not self.operationer.detect_element(
                    "四倍奖励-未选中",
                    auto_raise=False
            ):
                if not self.operationer.click_and_wait(
                        "四倍奖励-选中",
                        auto_raise=False
                ):
                    self.logger.warning("小队突袭四倍奖励取消选中失败")
                    return False
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


def setup_logging():
    # 创建基础日志格式
    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    # 创建基础配置
    logging.basicConfig(
        level=logging.DEBUG,  # 设置默认日志级别
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)  # 输出到控制台
        ]
    )

    # 获取根日志记录器
    logger = logging.getLogger()

    # 设置更详细的日志格式（可选）
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # 更新所有处理器的格式
    for handler in logger.handlers:
        handler.setFormatter(formatter)

    # 设置特定模块的日志级别（可选）
    # logging.getLogger("PySide6").setLevel(logging.WARNING)
    # logging.getLogger("urllib3").setLevel(logging.WARNING)

    return logger


if __name__ == "__main__":
    # 设置日志系统
    logger = setup_logging()
    xdtx = XiaoDuiTuXi(
        "小队突袭",
        Config(),
        None,
        None,
        None,
        None,
        None,
        None,
    )
    print(xdtx.transition_func)
