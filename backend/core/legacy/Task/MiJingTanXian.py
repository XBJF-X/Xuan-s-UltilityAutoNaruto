import time
from datetime import timedelta

from backend.core.legacy.Enums import KEY_INDEX
from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn


class MiJingTanXian(BaseTask):
    source_scene = "秘境探险-首页"
    task_max_duration = timedelta(hours=4)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fighting = False
        self.reset_task_exe_prog()

    def run(self):
        self.first_fight=False
        self.bool_sd=False
        self.operationer.clicker.update_coordinates([
            self.config.get_config("键位")[KEY_INDEX.BasicAttack],
            self.config.get_config("键位")[KEY_INDEX.FirstSkill],
            self.config.get_config("键位")[KEY_INDEX.SecondSkill],
            self.config.get_config("键位")[KEY_INDEX.Substitution],
            self.config.get_config("键位")[KEY_INDEX.UltimateSkill]
        ])
        super().run()

    @TransitionOn()
    def _(self):
        self.fighting = False
        self.operationer.clicker.stop()
        self.bool_click = False
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
    
    # 剩余挑战券 OCR 读取失败时的重试次数与间隔（切场景瞬间/单帧抖动常读不到）
    TZQ_OCR_ATTEMPTS = 3
    TZQ_OCR_RETRY_INTERVAL = 0.4

    @TransitionOn("秘境探险-匹配")
    def _(self):
        self.fighting = False
        self.operationer.clicker.stop()
        self.bool_click = False
        ##############测试代码##############
        # self.operationer.click_and_wait("出战")
        # self.bool_click = True
        # self.logger.info("测试代码，无视挑战券数量，继续执行")
        # return False
        ###################################
        tzq = self._read_remain_ticket_count()
        if tzq == 0:
            self.logger.info("挑战券已耗尽，任务执行结束")
            raise TaskCompleted("任务执行完成")
        if tzq is not None:
            self.logger.info(f"挑战券为 {tzq} ，继续执行")
        else:
            raise TaskCompleted("识别剩余挑战券数量失败（已重试 %d 次），按未知处理：不再尝试出战",self.TZQ_OCR_ATTEMPTS)
        self.operationer.click_and_wait("出战")
        self.bool_click = True
        return False

    def _read_remain_ticket_count(self):
        """读剩余挑战券数量：重试若干次，返回非负整数；始终读不到返回 None。

        - 取数字统一走 `OcrResultList.get_first_number()`：旧的
          `extract_all_numbers()[0]` 在"只识别到文本、没有数字"时会抛 IndexError；
        - 每次重试都会重新截图识别（`ocr_recognize` 内部重新截图）；
        - 全部失败时用同场景的图片元素 `剩余挑战券-0` 作辅助判据：命中即判定券已耗尽
          （实测 9 张券时该模板 max_val≈0.84 < 阈值 0.91，不会误判）。
        """
        texts = []
        for attempt in range(1, self.TZQ_OCR_ATTEMPTS + 1):
            result = self.operationer.ocr_recognize("剩余挑战券数量")
            texts = result.texts() if result else []
            number = result.get_first_number() if result else None
            if number is not None:
                return number
            if attempt < self.TZQ_OCR_ATTEMPTS:
                time.sleep(self.TZQ_OCR_RETRY_INTERVAL)
        self.logger.warning("剩余挑战券 OCR 识别文本=%s（未读出数字）", texts)
        zero_flag = self.operationer.get_element("剩余挑战券-0")
        if zero_flag is not None and self.operationer.detect_element(
                zero_flag, max_time=0.5, wait_time=0):
            self.logger.info("OCR 未读出数字，但命中[剩余挑战券-0]模板，判定券已耗尽")
            return 0
        return None

    def _no_ticket_tip_shown(self) -> bool:
        """点出战之后是否出现「挑战券不足」提示。

        该元素属于[秘境探险-首页]场景，而 `Operationer.get_element(name)` 默认只在
        `current_scene` 内解析，故这里显式指定场景获取元素对象（否则会抛"元素未定义"）。
        元素缺失（资源库未配置）时返回 False，不影响主流程。
        """
        try:
            element = self.operationer.get_element("挑战券不足", "秘境探险-首页")
        except Exception as e:
            self.logger.warning("获取[挑战券不足]元素失败：%s", e)
            return False
        if element is None:
            self.logger.warning("[挑战券不足]元素未配置，跳过该判据")
            return False
        return bool(self.operationer.detect_element(
            element, max_time=1.0, wait_time=0))


    @TransitionOn("秘境奖励")
    def _(self):
        self.fighting = False
        self.bool_click = True
        self.operationer.clicker.stop()
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
        self.reset_task_exe_prog()
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
            else:
                self.logger.info("不是可连点过的秘境，退出战斗")
                # 点暂停，退出，确认
                self.operationer.clicker.stop()
                self.operationer.click_and_wait("暂停")

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
        return True
