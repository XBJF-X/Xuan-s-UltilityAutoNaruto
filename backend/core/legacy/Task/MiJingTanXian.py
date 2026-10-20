import time
from datetime import timedelta

from backend.core.legacy.Enums import KEY_INDEX
from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn


class MiJingTanXian(BaseTask):
    source_scene = "秘境探险-首页"
    task_max_duration = timedelta(hours=4)

    def run(self):
        self.fighting = False
        self.first_fight=False
        self.bool_sd=False
        self.fight_time=self.config.get_task_exe_param(self.task_name, "秘境刷取次数", 0)
        self.operationer.clicker.update_coordinates([
            self.config.get_config("键位")[KEY_INDEX.BasicAttack],
            self.config.get_config("键位")[KEY_INDEX.FirstSkill],
            self.config.get_config("键位")[KEY_INDEX.SecondSkill],
            self.config.get_config("键位")[KEY_INDEX.Substitution],
            self.config.get_config("键位")[KEY_INDEX.UltimateSkill]
        ])
        super().run()
    def _check_tzq_num(self)->bool:
        if self.fight_time and self.config.get_task_exe_prog(self.task_name, "秘境已刷取次数", 0)>=self.fight_time:
            return True
        return False
    @TransitionOn()
    def _(self):
        self.fighting = False
        self.operationer.clicker.stop()
        self.bool_click = False
        if self._check_tzq_num():
            self.config.set_task_exe_prog(self.task_name, "秘境已刷取次数", 0)
            raise TaskCompleted(f"已达到设定刷取次数 {self.fight_time} 次，任务执行结束")
        if self.bool_sd:
            sd_times= self.operationer.ocr_recognize("扫荡次数")
            if sd_times and ("0/5" not in sd_times[0].text):
                self.logger.info(f"{sd_times[0].text}，执行扫荡")
                self.operationer.click_and_wait("扫荡",wait_time=0)
                if self.operationer.detect_element("挑战券不足"):
                    raise TaskCompleted("挑战券已扫荡完，任务执行完成")
                return False
            else:
                self.logger.info("扫荡次数耗尽")
                self.bool_sd=False
        return "秘境探险-匹配"
    

    @TransitionOn("秘境探险-匹配")
    def _(self):
        self.fighting = False
        self.operationer.clicker.stop()
        self.bool_click = False

        if self._check_tzq_num():
            self.config.set_task_exe_prog(self.task_name, "秘境已刷取次数", 0)
            raise TaskCompleted(f"已达到设定刷取次数 {self.fight_time} 次，任务执行结束")
        ##############测试代码##############
        # self.operationer.click_and_wait("出战")
        # self.bool_click = True
        # self.logger.info("测试代码，无视挑战券数量，继续执行")
        # return False
        ###################################
        if self.operationer.detect_element("剩余挑战券-0",max_time=0.5, wait_time=0):
            raise TaskCompleted("任务执行完成")
        else:
            self.logger.info("挑战券未耗尽，继续执行")
        self.operationer.click_and_wait("出战")
        self.bool_click = True
        return False


    @TransitionOn("秘境奖励")
    def _(self):
        self.fighting = False
        self.bool_click = True
        self.operationer.clicker.stop()

        fighted_time=self.config.get_task_exe_prog(self.task_name, "秘境已刷取次数", 0)
        self.logger.info(f"当前已刷取 {fighted_time+1} 次秘境")
        self.config.set_task_exe_prog(self.task_name, "秘境已刷取次数", fighted_time+1)

        self.logger.info("等待系统自动翻牌结束...")
        self.operationer.wait_until_stable(stable_duration=2)

        while self.config.get_task_exe_prog(self.task_name, "忍具已翻牌次数", 0) < \
                self.config.get_task_exe_param(self.task_name, "忍具翻牌次数", 0):
            if self.operationer.detect_element("忍具金币翻牌"):
                self.logger.warning("忍具翻牌券已用尽，自动停止忍具翻牌...")
                break
            if not self.operationer.click_and_wait("忍具翻牌"):
                self.logger.warning("没有忍具牌可翻，自动停止忍具翻牌...")
                break
            temp_time = self.config.get_task_exe_prog(self.task_name,
                                                      "忍具已翻牌次数", 0)
            self.config.set_task_exe_prog(self.task_name, "忍具已翻牌次数",
                                          temp_time + 1)
            time.sleep(1)
        self.logger.info("忍具翻牌已结束")

        while self.config.get_task_exe_prog(self.task_name, "饰品已翻牌次数", 0) < \
                self.config.get_task_exe_param(self.task_name, "饰品翻牌次数", 0):
            if self.operationer.detect_element("饰品金币翻牌"):
                self.logger.warning("饰品翻牌券已用尽，自动停止饰品翻牌...")
                break
            if not self.operationer.click_and_wait("饰品翻牌"):
                self.logger.warning("没有饰品牌可翻，自动停止饰品翻牌...")
                break
            self.operationer.click_and_wait("饰品翻牌")
            temp_time = self.config.get_task_exe_prog(self.task_name,
                                                      "饰品已翻牌次数", 0)
            self.config.set_task_exe_prog(self.task_name, "饰品已翻牌次数",
                                          temp_time + 1)
            time.sleep(1)
        self.logger.info("饰品翻牌已结束")

        self.operationer.click_and_wait("返回")
        self.bool_click = False
        if not self.first_fight and not self.bool_sd:
            self.first_fight =True
            self.bool_sd=True
        if self.bool_sd:
            return "秘境探险-首页"
        else:
            return "秘境探险-匹配"

    @TransitionOn("恭喜你获得")
    def _(self):
        self.fighting = False
        self.bool_click = True
        self.operationer.clicker.stop()
        self.operationer.click_and_wait("X")
        return False

    @TransitionOn("秘境探险-匹配-继续挑战确认")
    def _(self):
        self.operationer.clicker.stop()
        self.bool_click = False
        self.operationer.click_and_wait("今日不再提示")
        self.operationer.click_and_wait("确定")
        return False
    
    @TransitionOn("秘境探险-匹配-只获得忍具确认")
    def _(self):
        self.operationer.clicker.stop()
        self.bool_click = False
        self.operationer.click_and_wait("本周不再提示")
        self.operationer.click_and_wait("确定")
        return False

    @TransitionOn("副本内")
    def _(self):
        self.bool_click = True
        if not self.fighting:
            flag = self.operationer.search_and_detect([
                self.operationer.get_element("落岩秘境"),
                self.operationer.get_element("阴阳秘境"),
                self.operationer.get_element("雷霆秘境"),
                self.operationer.get_element("烈炎秘境"),
                self.operationer.get_element("水牢秘境"),
                self.operationer.get_element("毒风秘境"),
                self.operationer.get_element("罡体秘境"),
            ], 
            [],
            once_max_attempts=1,
            max_attempts=1,
            wait_time=0)
            if flag in [4, 5, 7]:
                self.logger.info("检测到可连点过的秘境，开始战斗")
                self.fighting = True
                self.operationer.clicker.start()
                return False
            else:
                self.logger.info("不是可连点过的秘境，退出战斗")
                # 点暂停，退出，确认
                self.operationer.clicker.stop()
                self.operationer.click_and_wait("暂停")
                return False

        self.operationer.clicker.start()
        return False

    @TransitionOn("副本内-暂停")
    def _(self):
        self.operationer.clicker.stop()
        self.bool_click = True
        self.fighting = False
        self.operationer.click_and_wait("退出战斗")
        return False

    @TransitionOn("副本内-暂停-退出战斗确认")
    def _(self):
        self.operationer.clicker.stop()
        self.bool_click = True
        self.fighting = False
        self.operationer.click_and_wait("确定")
        return False
    
    @TransitionOn("离开队伍-确认")
    def _(self):
        self.operationer.clicker.stop()
        self.bool_click = False
        self.fighting = False
        self.operationer.click_and_wait("确定")
        return False

    def reset_task_exe_prog(self) -> bool:
        self.fighting = False
        self.config.set_task_exe_prog(self.task_name, "忍具已翻牌次数", 0)
        self.config.set_task_exe_prog(self.task_name, "饰品已翻牌次数", 0)
        self.config.set_task_exe_prog(self.task_name, "秘境已刷取次数", 0)
        return True
