from datetime import timedelta, datetime, time, date
from zoneinfo import ZoneInfo

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

        # 所有可合成的逐个点击
        while self.click_and_wait(
                {'type': "ELEMENT", 'name': "装备-可合成"},
                auto_raise=False
        ):
            # 检查能不能点击合成按钮
            if self.click_and_wait(
                    {'type': "ELEMENT", 'name': "装备-合成"},
                    auto_raise=False
            ):
                self.logger.debug("可合成，点击合成")
            # 返回装备界面
            self.click_and_wait({'type': "COORDINATE", 'coordinate': (1400, 456)})

        # 可装备的一键添加
        if self.detect_and_wait(
                {'type': "ELEMENT", 'name': "装备-可装备"},
                auto_raise=False
        ):
            self.click_and_wait({'type': "ELEMENT", 'name': "装备-一键添加"})
            self.logger.warning("存在[可装备]装备，已一键装备")

        # 先看看当前装备能不能进阶，毕竟进阶说明没有能扫荡的了
        if self.click_and_wait(
                {'type': "ELEMENT", 'name': "装备-进阶"},
                auto_raise=False
        ):
            self.logger.info("当前装备可进阶，已点击进阶")

        flag = self.search_and_detect(
            [
                {'type': "ELEMENT", 'name': "装备-可扫荡"},
                {'type': "ELEMENT", 'name': "装备-可装备"},
            ],
            [],
            wait_time=0,
            once_max_time=1,
            bool_debug=True
        )
        while flag:
            if flag == 2:
                self.click_and_wait({'type': "ELEMENT", 'name': "装备-一键添加"})
                self.logger.warning("存在[可装备]装备，已一键装备")

            # 先看看当前装备能不能进阶，毕竟进阶说明没有能扫荡的了
            if self.click_and_wait(
                    {'type': "ELEMENT", 'name': "装备-进阶"},
                    auto_raise=False
            ):
                self.logger.info("当前装备可进阶，已点击进阶")

            # 如果当前装备存在可以扫荡的，先点击扫荡
            self.click_and_wait({'type': "ELEMENT", 'name': "装备-可扫荡"})
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
                wait_time=1
            )
            # 检测是否体力不足
            if self.detect_and_wait(
                    {'type': "ELEMENT", 'name': "装备-体力不足"},
                    max_time=1,
                    wait_time=1,
                    auto_raise=False
            ):
                # 检测到体力不足
                self.logger.debug("体力耗尽，提前结束")
                # 点掉弹窗
                self.click_and_wait({'type': "COORDINATE", 'coordinate': (1400, 456)})
                # 点掉弹窗
                self.click_and_wait({'type': "COORDINATE", 'coordinate': (1400, 456)})
                # 检查能不能点击合成按钮
                if self.click_and_wait(
                        {'type': "ELEMENT", 'name': "装备-合成"},
                        auto_raise=False
                ):
                    self.logger.debug("可合成，点击合成")
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
                    if self.click_and_wait(
                            {'type': "ELEMENT", 'name': "装备-合成"},
                            auto_raise=False
                    ):
                        self.logger.debug("可合成，点击合成")
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
                        if self.click_and_wait(
                                {'type': "ELEMENT", 'name': "装备-合成"},
                                auto_raise=False
                        ):
                            self.logger.debug("可合成，点击合成")
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
                            if self.click_and_wait(
                                    {'type': "ELEMENT", 'name': "装备-合成"},
                                    auto_raise=False
                            ):
                                self.logger.debug("可合成，点击合成")
                            # 点一下返回装备界面
                            self.click_and_wait({'type': "COORDINATE", 'coordinate': (1400, 456)})
            flag = self.search_and_detect(
                [
                    {'type': "ELEMENT", 'name': "装备-可扫荡"},
                    {'type': "ELEMENT", 'name': "装备-可装备"},
                ],
                [],
                wait_time=0,
                once_max_time=1,
                bool_debug=True
            )

        flag, min_time_delta = get_min_time_delta()
        if flag:
            self._update_next_execute_time(delta=min_time_delta)
        else:
            self._update_next_execute_time()


def get_min_time_delta():
    """
    计算时间差并按照规则返回结果：
    - 小于今天5点：返回False和0
    - 今天5点到16点之间：返回到16点的时间差与3小时的最小值
    - 过了今天16点：返回False和0
    """
    # 获取当前时间
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    today = date.today()

    # 创建今天5点和16点的datetime对象
    today_5am = datetime.combine(today, time(5, 0), tzinfo=ZoneInfo("Asia/Shanghai"))
    today_16pm = datetime.combine(today, time(16, 0), tzinfo=ZoneInfo("Asia/Shanghai"))

    # 情况1：当前时间小于今天5点
    if now < today_5am:
        return False, timedelta(0)

    # 情况2：当前时间在今天5点到16点之间
    elif today_5am <= now < today_16pm:
        to_16pm = today_16pm - now
        five_hours = timedelta(hours=3)
        return True, min(to_16pm, five_hours)

    # 情况3：当前时间过了今天16点
    else:  # now >= today_16pm
        return False, timedelta(0)
