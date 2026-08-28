import re
import time
from datetime import timedelta
from typing import List

from backend.core.legacy.OcrText import OcrText
from backend.core.legacy.Exceptions import StepFailedError, TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn




class GouMaiTiLi(BaseTask):
    source_scene = "主场景"
    task_max_duration = timedelta(minutes=3)

    def run(self):
        self.max_buy_times=0
        self.target_buy_times=0
        return super().run()


    @TransitionOn()
    def _(self):
        if not self.max_buy_times:
            self.operationer.click_and_wait("体力信息")
            tlgmcs = self.operationer.ocr_recognize("已购体力次数")
            if tlgmcs:
                pattern = re.compile(r'(\d+)\s*/\s*(\d+)')
                bought_times = None
                max_times = None

                # 遍历所有识别文本，查找第一个匹配的数字对
                for item in tlgmcs:
                    match = pattern.search(item.text)
                    if match:
                        bought_times = int(match.group(1))
                        max_times = int(match.group(2))
                        break

                if bought_times is None or max_times is None:
                    self.logger.error("未能从识别结果中提取到已购体力次数")
                    raise StepFailedError("识别已购体力次数失败，退出执行")

                self.logger.info(f"已购体力次数：{bought_times}/{max_times}")
                self.max_buy_times=max_times
                self.logger.info(f"每日最多可购买体力次数为 {self.max_buy_times} 次")
                buy_times=self.config.get_task_exe_param("购买体力", "购买体力次数")
                self.target_buy_times=max(0,self.max_buy_times-buy_times)
            else:
                raise StepFailedError("识别特权说明内容失败，将退出执行")
        # self.operationer.next_scene="充值" if not self.max_buy_times else "购买体力"
        if self.max_buy_times:
            self.operationer.next_scene="购买体力"
        return False
    
    # @TransitionOn("充值")
    # def _(self):
    #     self.operationer.click_and_wait("V特权")
    #     tqsm=self.operationer.ocr_recognize("特权说明区域")
    #     if tqsm:
    #         pattern = re.compile(r'体力每日可购买\s*(\d+)\s*次')
    #         matched=False
    #         for ocr in tqsm:
    #             match = pattern.search(ocr.text)
    #             if match:
    #                 self.max_buy_times=int(match.group(1))
    #                 matched=True
    #                 break
    #         if not matched:
    #             self.max_buy_times=5
    #         self.logger.info(f"每日最多可购买体力次数为 {self.max_buy_times} 次")
    #         buy_times=self.config.get_task_exe_param("购买体力", "购买体力次数")
    #         self.target_buy_times=max(0,self.max_buy_times-buy_times)
    #         self.operationer.next_scene="购买体力"
    #     else:
    #         raise StepFailedError("识别特权说明内容失败，将退出执行")
    #     return False

    @TransitionOn("购买体力")
    def _(self):
        sygmcs=self.operationer.ocr_recognize("剩余购买次数")
        if sygmcs :
            if sygmcs.is_greater_than(self.target_buy_times):
            # if sygmcs[0].extract_numbers()[0]>self.target_buy_times:
                self.operationer.click_and_wait("购买", wait_time=1.5)
                self.logger.info(f"将再次购买 {sygmcs.extract_all_numbers()[0]-self.target_buy_times} 次")
                return False
            else:
                self.logger.info("体力购买次数已足够")
        else:
            raise StepFailedError("识别已招财次数失败，自动退出执行")
        self.operationer.click_and_wait("X")
        self._activate_another_task("消耗体力")
        raise TaskCompleted("任务执行完成")
    
    # @TransitionOn("二级密码")
    # def _(self):
    #     self.logger.debug("出现二级密码窗口")
    #     passward = self.config.get_config("二级密码")
    #     if len(passward) != 6:
    #         raise StepFailedError("请检查二级密码！")
    #     # 输入操作
    #     self.operationer.click_and_input(
    #         self.operationer.get_element("输入框"),
    #         passward
    #     )
    #     # 点击二级密码-确定
    #     if not self.operationer.click_and_wait(self.operationer.get_element("确定")):
    #         raise StepFailedError("二级密码验证失败")
    #     self.target_buy_times+=1
    #     time.sleep(2)
    #     return False

    # def reset_task_exe_prog(self) -> bool:
    #     return True
