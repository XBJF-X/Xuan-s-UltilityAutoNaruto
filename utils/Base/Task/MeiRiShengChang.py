import time
from datetime import timedelta

from utils.Base.Enums import KEY_INDEX
from utils.Base.Task.BaseTask import BaseTask, TransitionOn


class MeiRiShengChang(BaseTask):
    source_scene = "忍术对战"
    task_max_duration = timedelta(hours=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checked = False
        self.operationer.clicker.update_coordinates([
            self.config.get_config("键位")[KEY_INDEX.BasicAttack],
            self.config.get_config("键位")[KEY_INDEX.FirstSkill],
            self.config.get_config("键位")[KEY_INDEX.SecondSkill],
            self.config.get_config("键位")[KEY_INDEX.UltimateSkill],
            self.config.get_config("键位")[KEY_INDEX.SecretScroll],
            self.config.get_config("键位")[KEY_INDEX.Summon],
            self.config.get_config("键位")[KEY_INDEX.Substitution]
        ])

    @TransitionOn()
    def _(self):
        self.operationer.clicker.stop()
        if not self.checked:
            self.operationer.clicker.stop()
            self.operationer.click_and_wait("决斗任务")
            return False
        self.operationer.click_and_wait("开战")
        self.operationer.click_and_wait("开战")
        return False

    @TransitionOn("决斗场-匹配中")
    def _(self):
        self.operationer.clicker.stop()
        time.sleep(1)
        return False

    @TransitionOn("忍术对战-决斗任务")
    def _(self):
        self.operationer.clicker.stop()
        self.logger.info("领取所有待领取的决斗任务宝箱")

        while self.operationer.search_and_click(
                [
                    "宝箱-领取"
                ],
                [],
                max_attempts=1,
        ):
            continue

        flag = self.operationer.search_and_detect(
            [
                self.operationer.get_element("宝箱-追回"),
                self.operationer.get_element("宝箱-未达成"),
            ],
            [
                {
                    'swipe':
                    {
                        "start_coordinate": [1095, 500],
                        "end_coordinate": [1095, 250],
                        "duration": 0.8
                    }
                }
            ],
            max_attempts=2,
            bool_debug=True
        )
        match flag:
            case 0:
                # self.checked = True
                # self.operationer.click_and_wait("X")
                # return False
                self.checked = False
                self.operationer.click_and_wait("X")
                self.logger.info("结束执行")
                self.update_next_execute_time()
                return True
            case 1:
                # 触发追回
                self.operationer.click_and_wait("宝箱-追回")
                self.logger.info("存在可追回每日胜场宝箱，将追回后继续战斗...")
                self.checked = True
                return False
            case 2:
                # 如果存在未达成，则标记已经检查过并返回匹配页进行下一场战斗
                self.logger.info("仍有未达成的宝箱，将继续战斗...")
                self.checked = True
                self.operationer.click_and_wait("X")
                return False

    @TransitionOn("决斗任务-追回")
    def _(self):
        self.operationer.click_and_wait("追回", wait_time=0)
        if self.operationer.detect_element("道具不足"):
            self.checked = False
            self.operationer.click_and_wait("X")
            self.logger.info("结束执行")
            self.update_next_execute_time()
            return True
        return False

    @TransitionOn("决斗场-结算")
    def _(self):
        self.checked = False
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("决斗场-战斗中")
    def _(self):
        self.checked = False
        self.operationer.clicker.start()
        time.sleep(1)
        return False

    @TransitionOn("决斗场-单局结算")
    def _(self):
        self.checked = False
        self.operationer.clicker.stop()
        time.sleep(5)
        return False

    @TransitionOn("你的对手离开了游戏")
    def _(self):
        self.checked = False
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("未知场景")
    def _(self):
        self.operationer.clicker.stop()
        time.sleep(1)
        return False

    @TransitionOn("未注册场景")
    def _(self):
        self.operationer.clicker.stop()
        time.sleep(1)
        return False
