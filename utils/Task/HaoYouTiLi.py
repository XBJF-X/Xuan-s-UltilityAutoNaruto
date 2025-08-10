from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from utils.Task.BaseTask import BaseTask


class HaoYouTiLi(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        self.logger.info("进入[好友]界面")
        # 点击好友按钮
        self.click_and_wait({"type": "ELEMENT", "name": "主场景-好友"})
        # 确认好友界面出现
        self.detect_and_wait({"type": "SCENE", "name": "好友"})
        self.logger.info("开始领取游戏好友体力")
        # 点击游戏好友一键赠送
        self.click_and_wait({"type": "ELEMENT", "name": "好友-一键赠送"})
        # 点击游戏好友一键领取
        self.click_and_wait({"type": "ELEMENT", "name": "好友-一键领取"})
        # 点击游戏好友-领取成功-确认
        if self.click_and_wait(
                {"type": "ELEMENT", "name": "好友-领取成功-确认"},
                auto_raise=False
        ):
            self.logger.info("游戏好友体力领取成功")
        else:
            self.logger.warning("未能领取游戏好友体力")
        self.logger.info("开始领取QQ好友体力")
        # 切换到QQ好友界面
        self.click_and_wait({"type": "COORDINATE", "coordinate": [301, 433]})
        # 点击QQ好友一键赠送
        self.click_and_wait({"type": "ELEMENT", "name": "好友-一键赠送"})
        # 点击QQ好友一键领取
        self.click_and_wait({"type": "ELEMENT", "name": "好友-一键领取"})
        # 点击QQ好友-领取成功-确认
        if self.click_and_wait(
                {"type": "ELEMENT", "name": "好友-领取成功-确认"},
                auto_raise=False
        ):
            self.logger.info("QQ好友体力领取成功")
        else:
            self.logger.warning("未能领取QQ好友体力")
        self._activate_another_task("装备合成")
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
