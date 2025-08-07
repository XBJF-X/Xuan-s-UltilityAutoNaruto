from datetime import timedelta

from utils.Task.BaseTask import BaseTask

armor_coodinates = [
    (226, 300),
    (436, 300),
    (646, 300),
    (226, 500),
    (436, 500),
    (646, 500),
]


class ZhuangBeiHeCheng(BaseTask):

    def _execute(self):
        # 确定在主场景
        if not self.home():
            raise self.StepFailedError("无法回到[主场景]")
        # 点击并确认进入装备界面
        self.click_and_wait({'type': "ELEMENT", 'name': "主场景-装备"})
        self.click_and_wait({'type': "ELEMENT", 'name': "主场景-装备-装备"})
        self.detect_and_wait({'type': 'SCENE', 'name': "装备"})

        # 点击配置设置中选中的装备
        self.click_and_wait(
            {
                'type': "COORDINATE",
                'coordinate': armor_coodinates[self.data.get("合成目标装备", 0)]
            }
        )
        # 可装备的一键添加
        if self.detect_and_wait(
                {'type': "ELEMENT", 'name': "装备-可装备"},
                auto_raise=False
        ):
            self.click_and_wait({'type': "ELEMENT", 'name': "装备-一键添加"})
            self.logger.warning("存在[可装备]装备，已一键装备")

        # # 先看看当前装备能不能进阶，毕竟进阶说明没有能扫荡的了
        # if self.click_and_wait({'type': "ELEMENT", 'name': "装备-进阶"}):
        #     self.logger.info("当前装备可进阶，已点击进阶")

        while self.click_and_wait(
                {'type': "ELEMENT", 'name': "装备-可扫荡"},
                wait_time=0,
                auto_raise=False
        ):
            # 可装备的一键添加
            if self.detect_and_wait({'type': "ELEMENT", 'name': "装备-可装备"}):
                self.click_and_wait({'type': "ELEMENT", 'name': "装备-一键添加"})
                self.logger.warning("存在[可装备]装备，已一键装备")

            # # 先看看当前装备能不能进阶，毕竟进阶说明没有能扫荡的了
            # if self.click_and_wait({'type': "ELEMENT", 'name': "装备-进阶"}):
            #     self.logger.info("当前装备可进阶，已点击进阶")

            # 如果当前装备存在可以扫荡的，先点击扫荡
            self.click_and_wait({'type': "ELEMENT", 'name': "装备-扫荡"})

            # 勾选扫荡40次
            if not self.detect_and_wait(
                    {'type': "ELEMENT", 'name': "装备-扫荡40次-选中"},
                    auto_raise=False
            ):
                self.click_and_wait({'type': "ELEMENT", 'name': "装备-扫荡40次-选中"})
                self.logger.warning("未勾选扫荡40次，已经勾选")

            # 点击开始扫荡
            self.click_and_wait(
                    {'type': "ELEMENT", 'name': "装备-开始扫荡"},
                    wait_time=0
            )
            # 检测是否体力不足
            if self.detect_and_wait(
                    {'type': "ELEMENT", 'name': "装备-体力不足"},
                    max_time=1,
                    auto_raise=False
            ):
                # 检测到体力不足
                self.logger.debug("体力耗尽，提前结束")
                # 点掉弹窗
                self.click_and_wait({'type': "COORDINATE", 'coordinate': (1400, 456)})
                # 点掉弹窗
                self.click_and_wait({'type': "COORDINATE", 'coordinate': (1400, 456)})
                # 检查能不能点击合成按钮
                self.click_and_wait({'type': "ELEMENT", 'name': "装备-合成"})
                # 返回装备界面
                self.click_and_wait({'type': "COORDINATE", 'coordinate': (1400, 456)})
                break
            else:
                self.click_and_wait(
                    {'type': "COORDINATE", 'coordinate': (1400, 456)},
                    wait_time=8
                )
                # 检测当前材料是否已足够
                if self.detect_and_wait(
                        {'type': "ELEMENT", 'name': "装备-已足够"},
                        auto_raise=False
                ):
                    # 点掉扫荡弹窗
                    self.click_and_wait({'type': "COORDINATE", 'coordinate': (1400, 456)})
                    # 检查能不能点击合成按钮
                    self.click_and_wait({'type': "ELEMENT", 'name': "装备-合成"})
                    # 点一下返回装备界面
                    self.click_and_wait({'type': "COORDINATE", 'coordinate': (1400, 456)})
                    continue
                else:
                    # 未检测到已足够，则尝试点击继续扫荡
                    self.click_and_wait(
                        {'type': "ELEMENT", 'name': "装备-继续扫荡"},
                        wait_time=0
                    )
                    # 检测是否体力不足
                    if self.detect_and_wait(
                            {'type': "ELEMENT", 'name': "装备-体力不足"},
                            max_time=1,
                            auto_raise=False
                    ):
                        # 检测到体力不足
                        self.logger.debug("体力耗尽，提前结束")
                        # 点掉弹窗
                        self.click_and_wait({'type': "COORDINATE", 'coordinate': (1400, 456)})
                        # 点掉弹窗
                        self.click_and_wait({'type': "COORDINATE", 'coordinate': (1400, 456)})
                        # 检查能不能点击合成按钮
                        self.click_and_wait({'type': "ELEMENT", 'name': "装备-合成"})
                        # 返回装备界面
                        self.click_and_wait({'type': "COORDINATE", 'coordinate': (1400, 456)})
                        break
                    else:
                        self.click_and_wait(
                            {'type': "COORDINATE", 'coordinate': (1400, 456)},
                            wait_time=8
                        )
                        # 检测当前材料是否已足够
                        if self.detect_and_wait(
                                {'type': "ELEMENT", 'name': "装备-已足够"},
                                auto_raise=False
                        ):
                            # 点掉扫荡弹窗
                            self.click_and_wait({'type': "COORDINATE", 'coordinate': (1400, 456)})
                            # 检查能不能点击合成按钮
                            self.click_and_wait({'type': "ELEMENT", 'name': "装备-合成"})
                            # 点一下返回装备界面
                            self.click_and_wait({'type': "COORDINATE", 'coordinate': (1400, 456)})
                        continue

        self._update_next_execute_time(delta=timedelta(hours=5))
