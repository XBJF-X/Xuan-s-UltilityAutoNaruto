from datetime import timedelta
import re

from backend.core.legacy.Exceptions import TaskCompleted, StepFailedError, TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn


class JinBiZhaoCai(BaseTask):
    source_scene = "招财"
    task_max_duration = timedelta(minutes=3)

    def run(self):
        self.target_times=self.config.get_task_exe_param("金币招财", "招财次数")
        self.process_times=0
        self.buy_times=0
        return super().run()

    @TransitionOn()
    def _(self):
        # 分别识别两个区域
        round_ocr = self.operationer.ocr_recognize("招财轮次")
        coin_ocr = self.operationer.ocr_recognize("累积投币")

        if not round_ocr or not coin_ocr:
            raise StepFailedError("识别已招财次数失败：OCR 结果为空")

        # 提取数字对的正则
        pattern = re.compile(r'(\d+)\s*/\s*(\d+)')

        def extract_single_pair(ocr_list):
            """从 OCR 结果中提取唯一的数字对，返回 (int, int)，失败返回 None"""
            pairs = []
            for item in ocr_list:
                matches = pattern.findall(item.text)
                for m in matches:
                    pairs.append((int(m[0]), int(m[1])))
            if len(pairs) != 1:
                return None
            return pairs[0]

        round_pair = extract_single_pair(round_ocr)
        coin_pair = extract_single_pair(coin_ocr)

        if round_pair is None or coin_pair is None:
            self.logger.error(f"轮次数字对: {round_pair}, 投币数字对: {coin_pair}")
            raise StepFailedError("识别已招财次数失败，未找到唯一数字对")

        current_round, total_round = round_pair
        current_coin, total_coin = coin_pair

        self.process_times = total_coin * (current_round - 1) + current_coin
        self.logger.info(f"识别到当前已金币招财 {self.process_times} 次")

        if self.process_times >= self.target_times:
            raise TaskCompleted("已招满金币招财")

        if self.process_times < self.target_times:
            self.operationer.click_and_wait("金币招财")
            self.logger.info(f"已招财 {self.process_times + 1} 次")
            return False
    

    # @TransitionOn("二级密码")
    # def _(self):
    #     self.logger.debug("出现二级密码窗口")
    #     passward = self.config.get_config("二级密码")
    #     if len(passward) != 6:
    #         raise StepFailedError("请检查二级密码是否留空或漏位！")
    #     # 输入操作
    #     self.operationer.click_and_input(
    #         self.operationer.get_element("输入框"),
    #         passward
    #     )
    #     # 点击二级密码-确定
    #     if not self.operationer.click_and_wait(self.operationer.get_element("确定")):
    #         raise StepFailedError("二级密码验证失败")

    #     self.process_times -= 1
    #     self.logger.info(f"招财次数回退，已招财 {self.process_times} 次")
    #     return False

    # def reset_task_exe_prog(self) -> bool:
    #     self.config.set_task_exe_prog("金币招财", "已招财次数", 0)
    #     return True
