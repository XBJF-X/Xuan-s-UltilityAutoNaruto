from datetime import timedelta

from backend.core.legacy.Enums import KEY_INDEX
from backend.core.legacy.Task import MeiRiShengChang
from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Task.BaseTask import TransitionOn
from backend.core.legacy.Task.schedule import Custom, Monthly

PARAM_DAYS_FROM_END = "倒数第几天"
DEFAULT_DAYS_FROM_END = 2
# 窗口长度：覆盖赛季结算（原行为为倒数第 2 天起 2 天）
SEASON_WINDOW_SPAN = timedelta(days=2)


def _monthly_windows(base, ctx):
    """赛季胜场窗口：按任务参数“每月倒数第几天”生成窗口（缺省/非法回退倒数第 2 天）。

    具体日期由 :class:`Monthly` 解析，负索引超出当月天数时会收敛到当月 1 号，
    不会跨到上个月（例如 2 月设为“倒数第 30 天” → 2 月 1 日）。
    """
    days_from_end = DEFAULT_DAYS_FROM_END
    if ctx is not None:
        raw = ctx.param("赛季胜场", PARAM_DAYS_FROM_END, DEFAULT_DAYS_FROM_END)
        try:
            days_from_end = int(raw)
        except (TypeError, ValueError):
            days_from_end = DEFAULT_DAYS_FROM_END
        if days_from_end < 1:
            # Monthly 不接受 0（正数第几天 / 负数为倒数第几天），非法值回退默认
            days_from_end = DEFAULT_DAYS_FROM_END
    return Monthly(day=-days_from_end, span=SEASON_WINDOW_SPAN).windows(base)


class SaiJiShengChang(MeiRiShengChang):
    source_scene = "赛季任务"
    task_max_duration = None
    # 每月任务：窗口 [本月倒数第 N 天 5:01, +2 天)，覆盖赛季结算窗口
    schedule = Custom(_monthly_windows,
                      cycle=lambda base: base.replace(day=28) + timedelta(days=4),
                      describe_text="每月倒数第 N 天 5:01 起 2 天（默认倒数第 2 天）")


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checked = False
        self.finished = False
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
        self.bool_click = False
        self.operationer.clicker.stop()
        if not self.checked:
            while self.operationer.click_and_wait("领取"):
                continue
            self.operationer.swipe_and_wait(
                start_coordinate=[1262, 191],
                end_coordinate=[1262, 696],
                duration=0.5
            )
            if not self.operationer.search_and_detect(
                ["决斗场内获得N次胜利-已领"],
                [
                {
                    'swipe':
                    {
                        "start_coordinate": [1262, 696],
                        "end_coordinate": [1262, 191],
                        "duration": 0.8
                    }
                }
            ],
            max_attempts=2,
            bool_debug=True
            ):
                self.checked = True
                self.operationer.click_and_wait("X")
                return False
            # if not self.operationer.detect_element(
            #         "决斗场内获得N次胜利-已领",
            #         wait_time=2,
            #         max_time=1
            # ):
            #     self.checked = True
            #     self.operationer.click_and_wait("X")
            #     return False
            else:
                self.checked = True
                self.finished = True
                self.operationer.clicker.stop()
                self.logger.warning("已打完所有赛季胜场")
                self.operationer.click_and_wait("X")
                raise TaskCompleted("任务执行完成")
        if not self.finished:
            self.operationer.click_and_wait("X")
            return False

    @TransitionOn("决斗场-首页")
    def _(self):
        self.bool_click = False
        self.operationer.clicker.stop()
        if self.checked:
            self.operationer.click_and_wait("忍术对战")
        else:
            self.operationer.click_and_wait("赛季任务")
        return False

    @TransitionOn("忍术对战")
    def _(self):
        self.bool_click = False
        self.operationer.clicker.stop()

        if not self.checked:
            self.operationer.click_and_wait("X")
            return False

        if not self.finished:
            self.operationer.click_and_wait("开战")
            self.operationer.click_and_wait("开战")
            self.bool_click = True
            return False
        raise TaskCompleted("任务执行完成")

