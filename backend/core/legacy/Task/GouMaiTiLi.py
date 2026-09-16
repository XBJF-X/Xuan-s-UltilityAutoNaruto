import re
import time
from datetime import timedelta
from typing import List

from backend.core.legacy.OcrText import OcrText
from backend.core.legacy.Exceptions import StepFailedError, TaskCompleted
from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn

PARAM_CONSUME_STAMINA = "购买后消耗体力"


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
            
        if self.max_buy_times:
            return "购买体力"
        return False
    

    @TransitionOn("购买体力")
    def _(self):
        sygmcs=self.operationer.ocr_recognize("剩余购买次数")
        remain = sygmcs.get_first_number() if sygmcs else None
        if remain is not None:
            if remain > self.target_buy_times:
                self.operationer.click_and_wait("购买", wait_time=1.5)
                self.logger.info(f"将再次购买 {remain - self.target_buy_times} 次")
                return False
            self.logger.info("体力购买次数已足够")
        else:
            # OCR 未读出数字不再直接抛异常中断任务：记 WARNING 后按"已足够"收尾
            self.logger.warning(
                "未识别到[剩余购买次数]数字（识别文本=%s），按已足够处理",
                sygmcs.texts() if sygmcs else [])
        self.operationer.click_and_wait("X")
        # 参数缺省视为开启：保持"购买流程结束后激活消耗体力"的既有语义
        if self.config.get_task_exe_param(
                self.task_name, PARAM_CONSUME_STAMINA, True):
            self._activate_another_task("消耗体力")
        else:
            self.logger.info("已按参数设置跳过[消耗体力]任务")
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
