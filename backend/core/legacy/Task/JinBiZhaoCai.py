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
        pattern = re.compile(r'(\d+)\s*/\s*(\d+)')

        def extract_pairs(ocr_list):
            """从 OCR 结果中提取所有数字对"""
            pairs = []
            if not ocr_list:
                return pairs
            for item in ocr_list:
                for m in pattern.findall(item.text):
                    pairs.append((int(m[0]), int(m[1])))
            return pairs

        def try_single(region_name):
            """单区域识别，要求唯一数字对，否则返回 None"""
            pairs = extract_pairs(self.operationer.ocr_recognize(region_name))
            return pairs[0] if len(pairs) == 1 else None

        round_pair = None
        coin_pair = None

        # ---------- 第一层：识别合并区域 ----------
        combined_pairs = extract_pairs(self.operationer.ocr_recognize("已招财次数"))
        if len(combined_pairs) == 2:
            # 合并区域通常按 y 坐标从上到下返回，即 轮次在前、投币在后
            round_pair, coin_pair = combined_pairs[0], combined_pairs[1]
            self.logger.debug(f"合并区域一次命中: round={round_pair}, coin={coin_pair}")
        elif len(combined_pairs) == 1:
            # 只拿到一个，归属不明，走子区域兜底
            self.logger.debug(f"合并区域仅识别到 1 个数字对: {combined_pairs[0]}")

        # ---------- 第二层：单区域兜底 ----------
        if round_pair is None:
            round_pair = try_single("招财轮次")
        if coin_pair is None:
            coin_pair = try_single("累积投币")

        if round_pair is None or coin_pair is None:
            self.logger.error(f"轮次数字对: {round_pair}, 投币数字对: {coin_pair}")
            raise StepFailedError("识别已招财次数失败，未找到完整数字对")

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