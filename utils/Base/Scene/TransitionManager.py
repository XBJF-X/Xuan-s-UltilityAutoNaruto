import logging
from collections import deque
from typing import Dict, List

from PySide6.QtCore import QThread

from utils.Base.Config import Config
from utils.Base.Enums import KEY_INDEX
from utils.Base.Operationer import Operationer
from utils.Base.Scene.Scene import Scene


class TransitionManager:
    """管理场景跳转关系，完全依赖Operationer的current_scene和next_scene"""

    def __init__(self, config: Config, scenes: Dict[str, Scene], parent_logger):
        self.logger = parent_logger.getChild(self.__class__.__name__)
        self.config = config
        self.scenes = scenes  # 仅用于BFS路径搜索
        self.transition_map = {}  # 键: (source_id, target_id)，值: 跳转函数
        self._register_transitions()

    def register(self, source_id: str, target_id: str):
        """装饰器：注册从source_id到target_id的跳转函数"""

        def decorator(func):
            self.transition_map[(source_id, target_id)] = func
            return func

        return decorator

    def transition(self, operationer: Operationer, *args, **kwargs):
        """
        执行跳转的主入口：从operationer.current_scene跳转到operationer.next_scene
        无需传入source_id和target_id，完全由operationer的状态决定
        """
        # 从Operationer中获取当前场景和目标场景
        source_id = operationer.current_scene.id
        target_id = operationer.next_scene
        self.logger.debug(f"{source_id}->{target_id}")
        # 校验场景合法性
        if not target_id:
            raise ValueError("Operationer.next_scene未设置，无法确定目标场景")
        if source_id not in self.scenes or target_id not in self.scenes:
            raise ValueError(f"场景 {source_id} 或 {target_id} 不存在")
        if source_id == target_id:
            self.logger.debug(f"已在终点")
            return

        # 优先执行直接跳转函数
        if (source_id, target_id) in self.transition_map:
            if self._execute_transition(operationer, *args, **kwargs):
                operationer.current_scene = self.scenes.get(target_id)
                self.logger.debug(f"直接跳转成功")
                return
            else:
                raise RuntimeError(f"从 {source_id} 到 {target_id} 跳转失败")

        # 无直接跳转时，BFS寻找路径并依次跳转
        path = self._bfs_shortest_path(source_id, target_id)
        if not path:
            raise ValueError(f"无从 {source_id} 到 {target_id} 的跳转路径")

        # 沿路径执行跳转（每步都会更新operationer的current_scene和next_scene）
        for i in range(len(path) - 1):
            # 更新当前步骤的目标场景
            operationer.next_scene = path[i + 1]
            # 执行跳转
            if not self._execute_transition(operationer, *args, **kwargs):
                raise RuntimeError(f"从 {path[i]} 到 {path[i + 1]} 跳转失败")
            else:
                self.logger.debug(f"从 {path[i]} 到 {path[i + 1]} 跳转成功")
                operationer.current_scene = self.scenes.get(path[i + 1])

    def _execute_transition(self, operationer: Operationer, *args, **kwargs) -> int:
        """执行单个跳转步骤：从operationer.current_scene到operationer.next_scene"""
        source_id = operationer.current_scene.id
        target_id = operationer.next_scene
        key = (source_id, target_id)

        if key not in self.transition_map:
            raise ValueError(f"无 {source_id} 到 {target_id} 的跳转逻辑")

        # 调用注册的跳转函数，仅传入operationer（包含所有必要状态）
        self.transition_map[key](operationer=operationer, *args, **kwargs)
        return operationer.search_and_detect(
            [operationer.scene_graph.scenes.get(target_id)],
            [],
            search_max_time=10,
            wait_time=0
        )

    def _bfs_shortest_path(self, start_id: str, end_id: str) -> List[str]:
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
        @self.register("冒险", "主场景")
        @self.register("冒险-精英副本", "主场景")
        @self.register("个人信息", "主场景")
        @self.register("活动", "主场景")
        @self.register("忍法帖", "主场景")
        @self.register("商城", "主场景")
        @self.register("丰饶之间", "主场景")
        @self.register("决斗场-首页", "主场景")
        @self.register("忍者挑战", "主场景")
        @self.register("任务集会所", "主场景")
        @self.register("试炼之地", "主场景")
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
        @self.register("个人信息-分享", "个人信息")
        @self.register("精英副本-便捷扫荡", "冒险-精英副本")
        @self.register("忍术对战-单人模式", "决斗场-首页")
        @self.register("决斗场-赛季", "决斗场-首页")
        @self.register("忍术对战-单人模式-决斗任务", "忍术对战-单人模式")
        @self.register("秘境探险-首页", "忍者挑战")
        @self.register("忍法帖-分享", "忍法帖-排行榜")
        @self.register("忍法帖-排行榜", "忍法帖")
        @self.register("组织助战-助战忍者", "小队突袭-组织助战")
        @self.register("X之要塞", "要塞战略图")
        @self.register("要塞战略图", "组织")
        @self.register("天地战场", "组织")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("X")

        @self.register("生存挑战", "试炼之地")
        @self.register("修行之路", "试炼之地")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("返回")

        @self.register("主场景", "奖励")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("奖励")

        @self.register("主场景", "邮件")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("邮件")

        @self.register("主场景", "招募")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("招募")

        @self.register("主场景", "好友")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("好友")

        @self.register("主场景", "招财")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("招财")

        @self.register("主场景", "冒险")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("冒险")

        @self.register("主场景", "个人信息")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("个人信息")
            while operationer.click_and_wait(
                    operationer.scene_graph.scenes.get("个人信息").elements.get("称号-下一步"),
                    max_time=7,
                    auto_raise=False
            ):
                continue
            while operationer.click_and_wait(
                    operationer.scene_graph.scenes.get("个人信息").elements.get("称号-确定"),
                    max_time=7,
                    auto_raise=False
            ):
                continue

        @self.register("主场景", "忍法帖")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("忍法帖")

        @self.register("主场景", "活动")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("活动")

        @self.register("主场景", "装备")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("装备")
            operationer.click_and_wait("装备-装备")

        @self.register("主场景", "情报站-首页")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("情报社")

        @self.register("主场景", "商城")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("商城")

        @self.register("主场景", "丰饶之间")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.swipe_and_wait(
                (462, 340),
                (1345, 340),
                duration=0.2,
                wait_time=0.1,
                times=2
            )
            for _ in range(3):
                if operationer.click_and_wait("丰饶之间",  auto_raise=False):
                    break
                operationer.swipe_and_wait(
                    (1345, 340),
                    (800, 340),
                    duration=0.7,
                    wait_time=0.1
                )

        @self.register("主场景", "决斗场-首页")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.swipe_and_wait(
                (462, 340),
                (1345, 340),
                duration=0.2,
                wait_time=0.1,
                times=2
            )
            for _ in range(3):
                if operationer.click_and_wait("决斗场",  auto_raise=False):
                    break
                operationer.swipe_and_wait(
                    (1345, 340),
                    (800, 340),
                    duration=0.7,
                    wait_time=0.1
                )

            while operationer.click_and_wait(
                    self.scenes.get("决斗场-首页").elements.get("称号-下一步"),
                    max_time=0.5,  auto_raise=False
            ):
                continue
            while operationer.click_and_wait(
                    self.scenes.get("决斗场-首页").elements.get("称号-确定"),
                    max_time=0.5,  auto_raise=False
            ):
                continue
            operationer.click_and_wait(
                self.scenes.get("决斗场-首页").elements.get("上赛季获得段位-继续"),
                max_time=0.5,  auto_raise=False)
            operationer.click_and_wait(
                self.scenes.get("决斗场-首页").elements.get("新赛季初始段位-升段奖励"),
                max_time=0.5,  auto_raise=False)

        @self.register("主场景", "忍者挑战")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.swipe_and_wait(
                (462, 340),
                (1345, 340),
                duration=0.2,
                wait_time=0.1,
                times=2
            )
            for _ in range(3):
                if operationer.click_and_wait("忍者挑战", auto_raise=False):
                    break
                operationer.swipe_and_wait(
                    (1345, 340),
                    (800, 340),
                    duration=0.7,
                    wait_time=0.1
                )

        @self.register("主场景", "排行榜")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.swipe_and_wait(
                (462, 340),
                (1345, 340),
                duration=0.2,
                wait_time=0.1,
                times=2
            )
            for _ in range(3):
                if operationer.click_and_wait("排行榜", auto_raise=False):
                    break
                operationer.swipe_and_wait(
                    (1345, 340),
                    (800, 340),
                    duration=0.7,
                    wait_time=0.1
                )

        @self.register("主场景", "任务集会所")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.swipe_and_wait(
                (462, 340),
                (1345, 340),
                duration=0.2,
                wait_time=0.1,
                times=2
            )
            for _ in range(3):
                if operationer.click_and_wait("任务集会所",  auto_raise=False):
                    break
                operationer.swipe_and_wait(
                    (1345, 340),
                    (800, 340),
                    duration=0.7,
                    wait_time=0.1
                )

        @self.register("主场景", "试炼之地")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.swipe_and_wait(
                (462, 340),
                (1345, 340),
                duration=0.2,
                wait_time=0.1,
                times=2
            )
            for _ in range(3):
                if operationer.click_and_wait("试炼之地",  auto_raise=False):
                    break
                operationer.swipe_and_wait(
                    (1345, 340),
                    (800, 340),
                    duration=0.7,
                    wait_time=0.1
                )

        @self.register("主场景", "小队突袭")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.swipe_and_wait(
                (462, 340),
                (1345, 340),
                duration=0.2,
                wait_time=0.1,
                times=2
            )
            for _ in range(3):
                if operationer.click_and_wait("小队突袭",  auto_raise=False):
                    break
                operationer.swipe_and_wait(
                    (1345, 340),
                    (800, 340),
                    duration=0.7,
                    wait_time=0.1
                )

        @self.register("主场景", "主场景-组织")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.swipe_and_wait(
                (462, 340),
                (1345, 340),
                duration=0.2,
                wait_time=0.1,
                times=2
            )
            for _ in range(3):
                if operationer.click_and_wait("组织",  auto_raise=False):
                    break
                operationer.swipe_and_wait(
                    (1345, 340),
                    (800, 340),
                    duration=0.7,
                    wait_time=0.1
                )

        @self.register("个人信息", "个人信息-分享")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("分享")

        @self.register("决斗场-首页", "忍术对战-单人模式")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("决斗场-忍术对战")

        @self.register("决斗场-首页", "决斗场-赛季")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("决斗季大奖")

        @self.register("忍术对战-单人模式", "忍术对战-单人模式-决斗任务")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("决斗任务")

        @self.register("冒险", "冒险-精英副本")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("精英副本")

        @self.register("冒险-精英副本", "精英副本-便捷扫荡")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("便捷扫荡")

        @self.register("忍者挑战", "秘境探险-首页")
        def _(operationer: Operationer, *args, **kwargs):
            joystick = self.config.get_config("键位")[KEY_INDEX.JoyStick]
            operationer.long_press(
                x=joystick[0] - 30,
                y=joystick[1],
                duration=0.3
            )
            QThread.msleep(2000)
            operationer.click_and_wait("秘境探险")

        @self.register("秘境探险-首页", "秘境探险-匹配")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("创建房间")

        @self.register("秘境探险-匹配", "秘境探险-首页")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("X")
            operationer.click_and_wait("离开队伍-确定")

        @self.register("忍法帖", "忍法帖-排行榜")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("排行榜")

        @self.register("忍法帖-排行榜", "忍法帖-分享")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("分享")

        @self.register("试炼之地", "生存挑战")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("生存挑战")
            operationer.click_and_wait("空白点")
            operationer.click_and_wait("空白点")
            operationer.click_and_wait("空白点")

        @self.register("试炼之地", "修行之路")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("修行之路")

        @self.register("小队突袭", "小队突袭-组织助战")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("组织助战")

        @self.register("小队突袭-组织助战", "小队突袭")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("X")
            operationer.click_and_wait("离开队伍-确定")

        @self.register("小队突袭-组织助战", "组织助战-助战忍者")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("我的助战")

        @self.register("主场景-组织", "组织祈福")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("玩法")
            operationer.search_and_click(
                [
                    "组织祈福-前往"
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
            operationer.click_and_wait("X之要塞-攻击")

        @self.register("主场景-组织", "天地战场")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("玩法")
            operationer.search_and_click(
                [
                    "天地战场-前往"
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

        @self.register("组织祈福", "组织")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("X")
            if operationer.detect_element("蛤蟆存钱罐", auto_raise=False):
                operationer.click_and_wait("X")

        @self.register("情报站-首页", "情报站-卷轴")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("卷轴")

        @self.register("情报站-首页", "情报站-忍者站")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("忍者站")

        @self.register("情报站-忍者站", "情报站-首页")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("首页")

        @self.register("情报站-首页", "福利站")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("福利站")
            operationer.search_and_detect(
                [
                    operationer.scene_graph.scenes.get("福利站")
                ],
                [
                    {'click': operationer.scene_graph.scenes.get("福利站").elements.get("X")}
                ],
                search_max_time=15,
            )

        @self.register("情报站-卷轴", "情报站-村口")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("村口")

        @self.register("情报站-村口", "情报站-首页")
        def _(operationer: Operationer, *args, **kwargs):
            operationer.click_and_wait("首页")
