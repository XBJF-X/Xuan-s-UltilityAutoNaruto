import logging
from collections import deque
from logging import Logger
from typing import List, Callable, Dict

from PySide6.QtCore import QThread

from utils.Base.Config import Config
from utils.Base.Enums import KEY_INDEX
from utils.Base.Operationer import Operationer


class TransitionManager:
    """管理场景跳转关系，完全依赖Operationer的current_scene和next_scene"""

    def __init__(self, config: Config, parent_logger: Logger | str = ""):
        if isinstance(parent_logger, str):
            self.logger = logging.getLogger(self.__class__.__name__)
        else:
            self.logger = parent_logger.getChild(self.__class__.__name__)
        self.config = config
        self.transition_map: Dict[tuple[str, str], Callable] = {}  # 键: (source_id, target_id)，值: 跳转函数
        self._register_transitions()

    def register(self, source_id: str, target_id: str):
        """装饰器：注册从source_id到target_id的跳转函数，强制绑定参数避免覆盖"""

        def decorator(func: Callable):
            def wrapper(operationer: Operationer, *args, **kwargs):
                return func(operationer, *args, **kwargs)

            self.transition_map[(source_id, target_id)] = wrapper
            return wrapper  # 返回当前键对应的独立wrapper

        return decorator

    def transition(self, operationer: Operationer, *args, **kwargs):
        """
        执行跳转的主入口：从operationer.current_scene跳转到operationer.next_scene
        无需传入source_id和target_id，完全由operationer的状态决定
        """

        # 从Operationer中获取当前场景和目标场景
        source_id = operationer.current_scene.name
        target_id = operationer.next_scene
        self.logger.debug(f"{source_id}->{target_id}")

        # 校验场景合法性
        if not target_id:
            raise ValueError("Operationer.next_scene未设置，无法确定目标场景")
        if source_id not in operationer.scene_graph.scenes or target_id not in operationer.scene_graph.scenes:
            raise ValueError(f"场景 {source_id} 或 {target_id} 不存在")
        if source_id == target_id:
            self.logger.debug(f"已在终点")
            return

        # 优先执行直接跳转函数
        if not (source_id, target_id) in self.transition_map:
            # 无直接跳转时，BFS寻找路径并依次跳转
            path = self.bfs_shortest_path(source_id, target_id)
            if not path:
                raise ValueError(f"无从 {source_id} 到 {target_id} 的跳转路径")
            kwargs["source_id"] = path[0]
            kwargs["target_id"] = path[1]
        else:
            kwargs["source_id"] = source_id
            kwargs["target_id"] = target_id

        if self._execute_transition(operationer, *args, **kwargs):
            operationer.current_scene = operationer.get_scene(target_id)
            self.logger.debug(f"直接跳转成功")
            return
        else:
            raise RuntimeError(f"从 {source_id} 到 {target_id} 跳转失败")

    def _execute_transition(self, operationer: Operationer, *args, **kwargs) -> int:
        """执行单个跳转步骤：从operationer.current_scene到operationer.next_scene"""
        source_id = kwargs.get("source_id")
        target_id = kwargs.get("target_id")
        key = (source_id, target_id)

        if key not in self.transition_map:
            raise ValueError(f"无 {source_id} 到 {target_id} 的跳转逻辑")

        # 调用注册的跳转函数，仅传入operationer（包含所有必要状态）
        self.transition_map[key](operationer=operationer, *args, **kwargs)
        return True

    def bfs_shortest_path(self, start_id: str, end_id: str) -> List[str]:
        """BFS寻找最短路径（基于已注册的跳转关系，不依赖scenes）"""
        # 1. 从transition_map中构建邻接表：{source_id: [target_ids...]}
        adjacency = {}
        for (source, target) in self.transition_map.keys():
            if source not in adjacency:
                adjacency[source] = []
            adjacency[source].append(target)  # 记录从source可直接跳转到的target

        # 2. BFS寻找最短路径
        queue = deque([(start_id, [start_id])])  # (当前场景, 路径列表)
        visited = {start_id}  # 避免重复访问

        while queue:
            current_id, path = queue.popleft()

            # 若当前场景已达目标，返回路径
            if current_id == end_id:
                return path

            # 遍历当前场景可直接跳转的所有目标场景
            for neighbor_id in adjacency.get(current_id, []):  # 若current_id无跳转关系，返回空列表
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))

        return []

    def _register_transitions(self):
        """
        注册跳转逻辑，完全依赖operationer的current_scene和next_scene
        不要忘记函数执行最后返回执行结果
        """

        @self.register("奖励", "主场景")
        @self.register("邮件", "主场景")
        @self.register("招募", "主场景")
        @self.register("好友", "主场景")
        @self.register("招财", "主场景")
        @self.register("冒险-冒险副本", "主场景")
        @self.register("冒险-精英副本", "主场景")
        @self.register("个人信息", "主场景")
        @self.register("活动", "主场景")
        @self.register("忍法帖", "主场景")
        @self.register("商城", "主场景")
        @self.register("商城-商店", "主场景")
        @self.register("丰饶之间", "主场景")
        @self.register("决斗场-首页", "主场景")
        @self.register("忍者挑战", "主场景")
        @self.register("任务集会所", "主场景")
        @self.register("试炼之地", "主场景")
        @self.register("排行榜", "主场景")
        @self.register("生存挑战", "主场景")
        @self.register("修行之路", "主场景")
        @self.register("小队突袭", "主场景")
        @self.register("装备", "主场景")
        @self.register("主场景-组织", "主场景")
        @self.register("组织", "主场景")
        @self.register("情报站-首页", "主场景")
        @self.register("情报站-村口", "主场景")
        @self.register("情报站-卷轴", "主场景")
        @self.register("情报站-忍者站", "主场景")
        @self.register("福利站", "主场景")
        @self.register("购买体力", "主场景")
        @self.register("每月签到", "主场景")
        @self.register("一乐外卖", "主场景")
        @self.register("忍者站", "主场景")
        @self.register("积分赛", "主场景")
        @self.register("普通招募", "主场景")
        @self.register("高级招募", "主场景")
        @self.register("主场景-装备", "主场景")
        @self.register("忍者大赛", "主场景")
        @self.register("火影格斗大赛-秋季赛", "主场景")
        @self.register("火影格斗大赛-无差别", "主场景")
        @self.register("聊天频道", "主场景")
        @self.register("情报站-动态详情", "主场景")
        @self.register("情报站-文章详情", "主场景")
        @self.register("冬日烟花季", "主场景")
        @self.register("个人信息-分享", "个人信息")
        @self.register("精英副本-便捷扫荡", "冒险-精英副本")
        @self.register("忍术对战", "决斗场-首页")
        @self.register("赛季任务", "决斗场-首页")
        @self.register("更多玩法", "决斗场-首页")
        @self.register("忍术对战-决斗任务", "忍术对战")
        @self.register("秘境探险-首页", "忍者挑战")
        @self.register("忍法帖-分享", "忍法帖-排行榜")
        @self.register("忍法帖-排行榜", "忍法帖")
        @self.register("组织助战-助战忍者", "小队突袭-组织助战")
        @self.register("X之要塞", "要塞战略图")
        @self.register("要塞战略图", "组织")
        @self.register("天地战场", "组织")
        @self.register("追击晓组织", "组织")
        @self.register("叛忍来袭", "组织")
        @self.register("出战名单-确认", "生存挑战-出战名单")
        @self.register("秘境探险-匹配", "离开队伍-确认")
        @self.register("小队突袭-组织助战", "离开队伍-确认")
        @self.register("二级密码", "购买体力")
        @self.register("二级密码", "小队突袭-组织助战")
        @self.register("二级密码", "招财")
        @self.register("昨日奖励", "组织祈福")
        @self.register("恭喜你获得", "组织祈福")
        @self.register("恭喜你获得", "天地战场-战场奖励")
        @self.register("恭喜你获得", "修行之路")
        @self.register("修行之路-扫荡", "修行之路")
        @self.register("修行之路-扫荡完成", "修行之路")
        @self.register("修行之路-正在扫荡", "修行之路")
        @self.register("修行之路-重置", "修行之路")
        @self.register("恭喜你获得", "任务集会所")
        @self.register("任务集会所-接取", "任务集会所")
        @self.register("生存挑战-出战名单", "生存挑战")
        @self.register("生存挑战-传送", "生存挑战")
        @self.register("生存挑战-扫荡确认", "生存挑战")
        @self.register("便捷扫荡-继续扫荡", "精英副本-便捷扫荡")
        @self.register("扫荡-继续扫荡", "材料详情-扫荡")
        @self.register("扫荡-已足够", "材料详情-扫荡")
        @self.register("体力不足", "材料详情-扫荡")
        @self.register("体力不足", "精英副本-便捷扫荡")
        @self.register("体力不足", "扫荡-继续扫荡")
        @self.register("材料详情-扫荡", "装备-材料详情")
        @self.register("装备-材料详情", "装备")
        @self.register("周活跃大礼", "奖励")
        @self.register("丰饶之间-一键完成", "丰饶之间")
        @self.register("决斗场-结算", "忍术对战")
        @self.register("决斗场-结算", "天之战场")
        @self.register("决斗场-结算", "地之战场")
        @self.register("决斗场-结算", "要塞内部")
        @self.register("决斗场-结算", "火影格斗大赛-无差别")
        @self.register("决斗任务-追回", "忍术对战-决斗任务")
        @self.register("积分赛-选择对手", "积分赛")
        @self.register("积分赛-段位奖励", "积分赛")
        @self.register("积分赛-排名奖励", "积分赛")
        @self.register("更多玩法-任务", "更多玩法")
        @self.register("更多玩法-任务", "绝迹战场")
        @self.register("更多玩法-任务", "大蛇丸试炼")
        @self.register("秘境探险-匹配-继续挑战确认", "秘境探险-匹配")
        @self.register("要塞内部", "要塞战略图")
        @self.register("要塞内部", "要塞内部-退出确认")
        @self.register("天地战场-战场奖励", "天之战场")
        @self.register("天地战场-战场奖励", "地之战场")
        @self.register("天地战场-配置阵容", "天地战场")
        @self.register("天地战场-确定进入", "天地战场")
        @self.register("天之战场", "天地战场")
        @self.register("地之战场", "天地战场")
        @self.register("领取好友体力成功", "好友")
        @self.register("更多玩法-匹配中", "绝迹战场")
        @self.register("更多玩法-匹配中", "大蛇丸试炼")
        @self.register("绝迹战场", "决斗场-首页")
        @self.register("大蛇丸试炼", "决斗场-首页")
        @self.register("天之战场", "天地战场-确认退出")
        @self.register("地之战场", "天地战场-确认退出")
        @self.register("无差别-继续出战", "火影格斗大赛-无差别")
        @self.register("无差别-成就奖励", "火影格斗大赛-无差别")
        @self.register("丰饶之间-暂停", "丰饶之间-内部")
        @self.register("追击晓组织-奖励", "追击晓组织")
        @self.register("叛忍来袭-更换忍者", "叛忍来袭")
        @self.register("生存挑战-重置", "生存挑战")
        @self.register("生存挑战-购买扫荡券", "生存挑战")
        @self.register("冬日烟花季-点燃免费爆竹", "冬日烟花季-主页")
        def _(operationer: Operationer, *args, **kwargs):
            """通用返回函数，点击[X]"""
            operationer.click_and_wait("X")

        @self.register("冬日烟花季-主页", "主场景")
        @self.register("生存挑战", "试炼之地")
        @self.register("修行之路", "试炼之地")
        @self.register("秘境奖励", "秘境探险-匹配")
        @self.register("绝迹战场", "更多玩法")
        @self.register("大蛇丸试炼", "更多玩法")
        @self.register("火影格斗大赛-秋季赛", "忍者大赛")
        @self.register("火影格斗大赛-无差别", "火影格斗大赛-秋季赛")
        def _(operationer: Operationer, *args, **kwargs):
            """通用返回函数，点击[返回]"""
            operationer.click_and_wait("返回")

        @self.register("主场景", "奖励")
        @self.register("主场景", "邮件")
        @self.register("主场景", "招募")
        @self.register("主场景", "招财")
        @self.register("主场景", "冒险-冒险副本")
        @self.register("主场景", "个人信息")
        @self.register("主场景", "忍法帖")
        @self.register("主场景", "活动")
        @self.register("主场景", "好友")
        @self.register("主场景", "购买体力")
        @self.register("主场景", "商城")
        @self.register("主场景-装备", "装备")
        @self.register("决斗场-首页", "忍术对战")
        @self.register("决斗场-首页", "赛季任务")
        @self.register("决斗场-首页", "更多玩法")
        @self.register("试炼之地", "生存挑战")
        @self.register("试炼之地", "修行之路")
        @self.register("招募", "普通招募")
        @self.register("招募", "高级招募")
        @self.register("普通招募", "高级招募")
        @self.register("主场景", "情报站-首页")
        @self.register("高级招募", "普通招募")
        @self.register("主场景", "高级招募")
        @self.register("主场景", "主场景-装备")
        def _(operationer: Operationer, *args, **kwargs):
            """通用跳转函数，点击[传入的目标ID]"""
            operationer.click_and_wait(kwargs.get("target_id"))

        @self.register("主场景", "丰饶之间")
        @self.register("主场景", "忍者挑战")
        @self.register("主场景", "排行榜")
        @self.register("主场景", "任务集会所")
        @self.register("主场景", "试炼之地")
        @self.register("主场景", "小队突袭")
        @self.register("主场景", "战区赛事")
        @self.register("主场景", "决斗场-首页")
        @self.register("主场景", "主场景-组织")
        @self.register("主场景", "积分赛")
        @self.register("主场景", "忍者大赛")
        def _(operationer: Operationer, *args, **kwargs):
            """主场景跳转分场景函数，滑动屏幕找到[传入的目标ID]并点击"""
            operationer.swipe_and_wait(
                (462, 340),
                (1445, 340),
                duration=0.1,
                wait_time=0,
                times=2
            )
            for _ in range(3):
                if operationer.click_and_wait(
                    kwargs.get("target_id"),
                    auto_raise=False,
                    wait_time=2
                ):
                    break
                operationer.swipe_and_wait(
                    (1345, 340),
                    (650, 340),
                    duration=0.7,
                    wait_time=0.5
                )

        @self.register("好友排名至X位", "主场景")
        @self.register("离开队伍-确认", "小队突袭")
        @self.register("离开队伍-确认", "秘境探险-首页")
        @self.register("组织祈福-今日次数已达上限", "组织祈福")
        @self.register("任务奖励-一键领取", "任务集会所")
        @self.register("任务奖励-一键领取", "追击晓组织-奖励")
        @self.register("便捷扫荡-扫荡结束", "精英副本-便捷扫荡")
        @self.register("福利站-100活跃奖励-确认", "福利站-活跃奖励-获得奖励")
        @self.register("招募结果", "高级招募")
        @self.register("招募结果", "普通招募")
        @self.register("副本内-暂停-退出战斗确认", "秘境探险-匹配")
        @self.register("副本内-暂停-退出战斗确认", "小队突袭")
        @self.register("更多玩法-结算", "绝迹战场")
        @self.register("更多玩法-结算", "大蛇丸试炼")
        @self.register("更多玩法-选择忍者", "大蛇丸试炼-副本内")
        @self.register("更多玩法-选择忍者", "绝迹战场-副本内")
        @self.register("你的对手离开了游戏", "大蛇丸试炼")
        @self.register("你的对手离开了游戏", "绝迹战场")
        @self.register("你的对手离开了游戏", "忍术对战")
        @self.register("你的对手离开了游戏", "要塞内部")
        @self.register("你的对手离开了游戏", "天之战场")
        @self.register("你的对手离开了游戏", "地之战场")
        @self.register("你的对手离开了游戏", "火影格斗大赛-无差别")
        @self.register("对手已经掉线了", "火影格斗大赛-无差别")
        @self.register("招募忍者已拥有", "招募结果")
        @self.register("要塞内部-退出确认", "要塞战略图")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("确定")

        @self.register("天地战场-确认退出", "天地战场")
        @self.register("天地战场-战场战斗已经结束", "天之战场")
        @self.register("天地战场-战场战斗已经结束", "地之战场")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("确认")

        @self.register("活动", "一乐外卖")
        @self.register("活动", "每月签到")
        @self.register("活动", "冬日烟花季")
        @self.register("一乐外卖", "每月签到")
        @self.register("一乐外卖", "冬日烟花季")
        @self.register("每月签到", "一乐外卖")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.search_and_click(
                [
                    kwargs.get("target_id")
                ],
                [
                    {
                        "swipe": {
                            "start_coordinate": [107, 846],
                            "end_coordinate": [107, 213],
                            "duration": 1
                        }
                    }
                ],
                max_attempts=2
            )

        @self.register("主场景-组织", "组织祈福")
        @self.register("主场景-组织", "叛忍来袭")
        @self.register("主场景-组织", "天地战场")
        @self.register("主场景-组织", "追击晓组织")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("玩法")
            operationer.search_and_click(
                [
                    f"{kwargs.get("target_id")}-前往"
                ],
                [
                    {
                        "swipe": {
                            "start_coordinate": [1000, 464],
                            "end_coordinate": [350, 464],
                            "duration": 0.5
                        }
                    }
                ],
                max_attempts=3
            )

        @self.register("福利站-40活跃奖励-抽取中", "福利站-活跃奖励-获得奖励")
        @self.register("决斗场-战斗中", "决斗场-单局结算")
        @self.register("决斗场-单局结算", "决斗场-结算")
        @self.register("大蛇丸试炼-副本内", "更多玩法-结算")
        @self.register("绝迹战场-副本内", "更多玩法-结算")
        @self.register("更多玩法-匹配成功", "绝迹战场")
        @self.register("更多玩法-匹配成功", "大蛇丸试炼")
        @self.register("无差别-禁用秘卷选择", "无差别-等待对方选择")
        @self.register("无差别-禁用忍者选择", "无差别-等待对方选择")
        @self.register("无差别-秘卷选择", "无差别-等待对方选择")
        @self.register("无差别-忍者选择", "无差别-等待对方选择")
        @self.register("无差别-等待对方选择", "无差别-禁用秘卷选择")
        @self.register("无差别-等待对方选择", "无差别-禁用忍者选择")
        @self.register("无差别-等待对方选择", "无差别-秘卷选择")
        @self.register("无差别-等待对方选择", "无差别-忍者选择")
        @self.register("无差别-等待对方选择", "火影格斗大赛-无差别")
        @self.register("丰饶之间-内部", "副本结算-点击任意位置关闭界面")
        def _(operationer: Operationer, *args, **kwargs):
            QThread.msleep(1000)

        @self.register("火影格斗大赛-秋季赛", "火影格斗大赛-无差别")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("无差别")

        @self.register("忍者大赛", "火影格斗大赛-秋季赛")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("火影格斗大赛")

        @self.register("个人信息", "个人信息-分享")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("分享")

        @self.register("忍术对战", "忍术对战-决斗任务")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("决斗任务")

        @self.register("冒险-冒险副本", "冒险-精英副本")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("精英副本")

        @self.register("冒险-精英副本", "冒险-冒险副本")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("冒险副本")

        @self.register("冒险-精英副本", "精英副本-便捷扫荡")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("便捷扫荡")

        @self.register("忍者挑战", "秘境探险-首页")
        def _(operationer: Operationer, *args, **kwargs):
            joystick = self.config.get_config("键位")[KEY_INDEX.JoyStick]
            operationer.long_press(
                x=joystick[0] - 40,
                y=joystick[1] + 40,
                duration=0.3
            )
            QThread.msleep(2000)
            operationer.click_and_wait("秘境探险")

        @self.register("秘境探险-首页", "秘境探险-匹配")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("创建房间")

        @self.register("忍法帖", "忍法帖-排行榜")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("排行榜")

        @self.register("忍法帖-排行榜", "忍法帖-分享")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("分享")

        @self.register("小队突袭", "小队突袭-组织助战")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("组织助战")

        @self.register("小队突袭-组织助战", "组织助战-助战忍者")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("我的助战")

        @self.register("主场景-组织", "组织")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("进入组织")

        @self.register("主场景-组织", "要塞战略图")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("玩法")
            operationer.search_and_click(
                [
                    "要塞争夺战-前往"
                ],
                [
                    {
                        "swipe": {
                            "start_coordinate": [1339, 464],
                            "end_coordinate": [260, 464],
                            "duration": 0.5
                        }
                    }
                ],
                max_attempts=3
            )

        @self.register("要塞战略图", "X之要塞")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("火之要塞")

        @self.register("X之要塞", "要塞内部")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("攻击")

        @self.register("组织祈福", "组织")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("X")
            if operationer.detect_element("蛤蟆存钱罐", auto_raise=False):
                operationer.click_and_wait("X")

        @self.register("情报站-首页", "情报站-卷轴")
        @self.register("情报站-村口", "情报站-卷轴")
        @self.register("忍者站", "情报站-卷轴")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("卷轴", wait_time=3)

        @self.register("情报站-首页", "忍者站")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("忍者站", wait_time=10)

        @self.register("情报站-首页", "福利站")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("福利站", wait_time=5)

        @self.register("情报站-首页", "情报站-村口")
        @self.register("情报站-卷轴", "情报站-村口")
        @self.register("忍者站", "情报站-村口")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("村口")

        @self.register("情报站-村口", "情报站-首页")
        @self.register("情报站-卷轴", "情报站-首页")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("首页", wait_time=3)

        @self.register("忍者站", "情报站-首页")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("推荐", wait_time=3)

        @self.register("福利站", "情报站-首页")
        @self.register("情报站-文章详情", "情报站-村口")
        @self.register("情报站-动态详情", "情报站-首页")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("后退", wait_time=3)

        @self.register("商城", "商城-商店")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("商店")

        @self.register("登录界面", "主场景")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("开始游戏")


        @self.register("决斗场-匹配中", "忍术对战")
        @self.register("决斗场-匹配中", "要塞内部")
        @self.register("决斗场-匹配中", "火影格斗大赛-无差别")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("取消匹配", auto_raise=False)

        @self.register("副本结算-点击任意位置关闭界面", "丰饶之间")
        @self.register("副本结算-点击任意位置关闭界面", "小队突袭")
        @self.register("副本结算-点击任意位置关闭界面", "叛忍来袭-内部")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("点击任意位置关闭界面")

        @self.register("福利站-每日签到", "福利站")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("立即签到")

        @self.register("福利站-签到成功", "福利站")
        @self.register("福利站-活跃奖励-获得奖励", "福利站")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("我知道了")

        @self.register("忍道称号", "个人信息")
        @self.register("忍道称号", "决斗场-首页")
        @self.register("格斗称号", "个人信息")
        @self.register("格斗称号", "决斗场-首页")
        def _(operationer: Operationer, *args, **kwargs):
            if not operationer.click_and_wait("下一步"):
                operationer.click_and_wait("确定")

        @self.register("新赛季初始段位", "决斗场-首页")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("升段奖励")

        @self.register("上赛季获得段位", "决斗场-首页")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("继续")

        @self.register("副本内", "副本内-暂停")
        @self.register("丰饶之间-内部", "丰饶之间-暂停")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("暂停")

        @self.register("副本内-暂停", "副本内-暂停-退出战斗确认")
        @self.register("丰饶之间-暂停", "丰饶之间")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("退出战斗")

        @self.register("冬日烟花季", "冬日烟花季-主页")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("立即前往")
