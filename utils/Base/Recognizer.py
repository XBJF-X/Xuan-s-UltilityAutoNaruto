import logging
import os
import time
from typing import Tuple, List, Union, Set

import cv2
import numpy as np

from StaticFunctions import cv_imread
from StaticFunctions import setup_logging
from tool.ResourceManager.ResourceDBManager import ResourceDBManager
from tool.ResourceManager.model import Element, Scene
from utils.Base.Enums import MatchType
from utils.Base.Scene.SceneGraph import SceneGraph


class Recognizer:
    def __init__(self, scene_graph: SceneGraph, parent_logger: str | logging.Logger = ""):
        if isinstance(parent_logger, str):
            self.logger = logging.getLogger("识别器")
        else:
            self.logger = parent_logger.getChild("识别器")
        self.scene_graph = scene_graph
        self.popup_scenes = {
            "版本更新2",
            "版本更新1",
            "响应超时",
            "重连提示",
            "网络不畅通",
            "购买体力",
            "铜币不足",
            "是否隐藏气泡",
            "升级",
            "二级密码",
            "登录奖励",
            "网络异常重连失败",
            "网络连接失败",
            "安装包更新异常",
            "对方数据异常",
            "登录授权过期",
            "任务奖励-一键领取",
            "公告",
        }
        self.coincident_scenes = {
            "活动": [
                "每月签到",
                "一乐外卖"
            ],
            "主场景": [
                "主场景-装备"
            ],
            "装备": [
                "装备-材料详情",
                "材料详情-扫荡",
                "扫荡-继续扫荡",
                "扫荡-已足够"
            ],
            "修罗副本-关卡详情": [
                "材料详情-扫荡",
                "扫荡-继续扫荡"
            ],
            "生存挑战": [
                "生存挑战-扫荡确认",
                "生存挑战-传送",
                "生存挑战-重置",
                "生存挑战-购买扫荡券",
                "生存挑战-出战名单",
                "出战名单-确认"
            ],
            "福利站": [
                "福利站-签到成功",
                "福利站-活跃奖励-获得奖励",
                "福利站-每日签到",
                "福利站-40活跃奖励-抽取中",
                "福利站-100活跃奖励-确认"
            ],
            "副本内": [
                "副本内-暂停",
                "副本内-暂停-退出战斗确认",
                "副本结算-点击任意位置关闭界面"
            ],
            "冒险-精英副本": [
                "精英副本-便捷扫荡",
                "便捷扫荡-扫荡结束",
                "便捷扫荡-继续扫荡",
            ],
            "冒险-冒险副本": [
                "决斗场-战斗中",
            ],
            "精英副本-便捷扫荡": [
                "体力不足",
                "便捷扫荡-继续扫荡",
                "便捷扫荡-扫荡结束"
            ],
            "修行之路": [
                "修行之路-重置",
                "修行之路-扫荡",
                "修行之路-扫荡完成",
                "修行之路-正在扫荡"
            ],
            "忍术对战-决斗任务": [
                "决斗任务-追回"
            ],
            "忍术对战": [
                "决斗场-匹配中",
                "忍术对战-调整阵容",
            ],
            "任务集会所": [
                "任务集会所-接取"
            ],
            "决斗场-首页": [
                "上赛季获得段位",
                "新赛季初始段位",
            ],
            "决斗场-战斗中": [
                "决斗场-结算",
                "决斗场-单局结算",
                "你的对手离开了游戏"
            ],
            "组织": [
                "叛忍来袭-结束",
                "叛忍来袭-是否开启",
                "叛忍来袭-是否开启-双倍",
                "叛忍来袭-更换忍者",
                "叛忍来袭-未开始",
                "叛忍来袭-进行中",
                "叛忍来袭-选择难度",
                "叛忍来袭-即将开始",
                "叛忍来袭-已获得2次奖励",
                "叛忍来袭-今日叛忍已结束",
                "组织购买"
            ],
            "地之战场": [
                "天地战场-战场奖励",
                "天地战场-确认退出",
                "天地战场-战场战斗已经结束"
            ],
            "天之战场": [
                "天地战场-战场奖励",
                "天地战场-确认退出",
                "天地战场-战场战斗已经结束"
            ],
            "天地战场": [
                "天地战场-确定进入"
            ],
            "秘境探险-匹配": [
                "离开队伍-确认",
                "秘境探险-匹配-继续挑战确认"
            ],
            "好友": [
                "领取好友体力成功"
            ],
            "要塞内部": [
                "决斗场-匹配中",
                "要塞内部-退出确认"
            ],
            "要塞内部-退出确认": [
                "要塞内部"
            ],
            "组织祈福": [
                "组织祈福-今日次数已达上限",
                "昨日奖励"
            ],
            "小队突袭-组织助战": [
                "离开队伍-确认"
            ],
            "装备-材料详情": [
                "扫荡-已足够",
                "扫荡-继续扫荡"
            ],
            "积分赛": [
                "积分赛-排名奖励",
                "积分赛-段位奖励"
            ],
            "扫荡-继续扫荡": [
                "体力不足"],
            "材料详情-扫荡": [
                "体力不足",
                "扫荡-已足够"
            ],
            "商城": [
                "商城-商店"],
            "大蛇丸试炼-副本内": [
                "更多玩法-结算"
            ],
            "绝迹战场-副本内": [
                "更多玩法-结算"
            ],
            "丰饶之间-内部": [
                "丰饶之间-暂停"
            ],
            "火影格斗大赛-无差别": [
                "无差别-继续出战",
                "无差别-成就奖励"
            ],
            "大蛇丸试炼": [
                "更多玩法-匹配成功",
                "更多玩法-匹配中"
            ],
            "绝迹战场": [
                "更多玩法-匹配成功",
                "更多玩法-匹配中"
            ],
            "奖励": [
                "周活跃大礼"
            ],
            "招募": [
                "普通招募", "高级招募"
            ],
            "冬日烟花季-主页": [
                "冬日烟花季-点燃免费爆竹"
            ],
            "重返木叶": [
                "重返木叶-忍界指引"
            ],
            "叛忍来袭-内部": [
                "叛忍来袭-结束",
                "叛忍来袭-确认挑战",
            ],
        }
        # 用于记录本次识别中已排除的弹窗
        self._excluded_popups_in_current_recognition: Set[str] = set()
        # 用于调试时记录每个模板的匹配详情（在 bool_debug=True 时填充）
        self._debug_match_records = {}
        # 最近一次成功匹配的场景详情（在 bool_debug=True 时填充）
        self._last_successful_scene_details = None

    def scene(self, scene_img, bool_debug=False) -> Union[str, Scene]:
        """
        对场景进行分类的函数

        修改：优先识别弹窗场景，防止干扰其他场景识别

        Args:
            scene_img(np.ndarray): 需要识别的图像
            bool_debug(bool): 是否回报日志
        """
        # 重置本次识别的排除弹窗记录
        self._excluded_popups_in_current_recognition.clear()

        # 如果不是调试模式，保持原有行为（节省开销）
        if not bool_debug:
            popup_scene = self._detect_popup_first(scene_img, bool_debug)
            if popup_scene:
                return popup_scene
            return self._detect_normal_scene(scene_img, bool_debug)

        # Debug 模式：使用内部列表缓存日志（避免新增 handler），匹配成功时只输出与成功相关的日志，
        # 匹配失败时再输出本次匹配的全部日志。实现思路：临时猴补当前 logger 的方法，把日志先写入 `buffered_logs`，
        # 函数返回前再根据匹配结果回放或筛选这些缓存。

        # 清理本次识别的调试记录，并重置当前作用域
        try:
            self._debug_match_records.clear()
            self._last_successful_scene_details = None
        except Exception:
            self._debug_match_records = {}
            self._last_successful_scene_details = None
        self._current_debug_scope = None

        # 内存缓存：列表 of (levelno, message, scope)
        buffered_logs: List[tuple] = []

        # 备份原始 logger 方法
        orig_debug = self.logger.debug
        orig_info = self.logger.info
        orig_warning = self.logger.warning
        orig_error = self.logger.error
        orig_critical = self.logger.critical
        orig_exception = self.logger.exception
        orig_log = self.logger.log

        def _format_message(msg, *args, **kwargs):
            try:
                if args:
                    return msg % args
                return str(msg)
            except Exception:
                try:
                    return str(msg) + " " + " ".join(map(str, args))
                except Exception:
                    return str(msg)

        def _make_wrapper(levelno):
            def _w(msg, *args, **kwargs):
                try:
                    text = _format_message(msg, *args, **kwargs)
                except Exception:
                    text = str(msg)
                # 处理 exc_info 简单情况
                if kwargs.get('exc_info'):
                    try:
                        import traceback, sys
                        ei = kwargs.get('exc_info')
                        if ei is True:
                            text += '\n' + ''.join(traceback.format_exception(*sys.exc_info()))
                        elif isinstance(ei, tuple):
                            text += '\n' + ''.join(traceback.format_exception(*ei))
                    except Exception:
                        pass
                scope = getattr(self, '_current_debug_scope', None)
                buffered_logs.append((levelno, text, scope))
            return _w

        def _exception_wrapper(msg, *args, **kwargs):
            try:
                text = _format_message(msg, *args, **kwargs)
            except Exception:
                text = str(msg)
            try:
                import traceback, sys
                text += '\n' + ''.join(traceback.format_exception(*sys.exc_info()))
            except Exception:
                pass
            scope = getattr(self, '_current_debug_scope', None)
            buffered_logs.append((logging.ERROR, text, scope))

        def _log_wrapper(level, msg, *args, **kwargs):
            try:
                text = _format_message(msg, *args, **kwargs)
            except Exception:
                text = str(msg)
            scope = getattr(self, '_current_debug_scope', None)
            buffered_logs.append((level, text, scope))

        # 替换 logger 方法
        self.logger.debug = _make_wrapper(logging.DEBUG)
        self.logger.info = _make_wrapper(logging.INFO)
        self.logger.warning = _make_wrapper(logging.WARNING)
        self.logger.error = _make_wrapper(logging.ERROR)
        self.logger.critical = _make_wrapper(logging.CRITICAL)
        self.logger.exception = _exception_wrapper
        self.logger.log = _log_wrapper

        try:
            # 执行识别流程（所有内部日志会被缓冲）
            popup_scene = self._detect_popup_first(scene_img, True)
            if popup_scene:
                result = popup_scene
            else:
                result = self._detect_normal_scene(scene_img, True)
        finally:
            # 恢复原始 logger 方法
            try:
                self.logger.debug = orig_debug
                self.logger.info = orig_info
                self.logger.warning = orig_warning
                self.logger.error = orig_error
                self.logger.critical = orig_critical
                self.logger.exception = orig_exception
                self.logger.log = orig_log
            except Exception:
                pass

        # 判定匹配是否成功（把特殊未知场景视为失败）
        success = True
        if result is None or (isinstance(result, str) and result in ("未知场景", "未知含X场景")):
            success = False

        # 构建需要关联的名字集合，用于筛选相关日志
        matched_names = set()
        if isinstance(result, Scene):
            matched_names.add(result.name)
        elif isinstance(result, str):
            matched_names.add(result)

        # 根据匹配结果选择性输出日志
        if success:
            # 优先输出结构化的匹配细节（来自 _last_successful_scene_details），然后回放相关的原始缓冲日志
            details = None
            try:
                details = self._last_successful_scene_details
            except Exception:
                details = None

            if details:
                scene_name = details.get("scene")
                # self.logger.debug(f"匹配成功: {scene_name}")
                # for el in details.get("elements", []):
                #     el_name = el.get("element_name")
                #     match_count = el.get("match_count")
                #     self.logger.debug(f"  元素: {el_name} 匹配次数: {match_count}")
                #     dbg = el.get("debug")
                #     if dbg:
                #         method = dbg.get("method")
                #         if method == "TEMPLATE":
                #             self.logger.debug(f"    [{el_name}] 方法=TEMPLATE, max_val={dbg.get('max_val')}, threshold={dbg.get('threshold')}, matches_before_nms={dbg.get('sorted_matches_len', 0)}")
                #             kept = dbg.get("kept_confidences")
                #             if kept:
                #                 self.logger.debug(f"    [{el_name}] 去重后置信度: {kept}")
                #             boxes = el.get("boxes") or dbg.get("kept_boxes")
                #             if boxes:
                #                 self.logger.debug(f"    [{el_name}] 匹配框: {boxes}")
                #         elif method == "SIFT":
                #             self.logger.debug(f"    [{el_name}] 方法=SIFT, good_matches={dbg.get('good_matches')}, feature_template={dbg.get('num_template_features')}")
                #             if dbg.get("location"):
                #                 self.logger.debug(f"    [{el_name}] 位置: {dbg.get('location')}")

                # 仅回放属于成功场景作用域（scene:SceneName）的缓冲日志
                filtered_records = []
                for level, msg, scope in buffered_logs:
                    if scope and f"scene:{scene_name}" in scope:
                        filtered_records.append((level, msg))

                for level, msg in filtered_records:
                    try:
                        self.logger.log(level, msg)
                    except Exception:
                        pass
            else:
                # 无结构化细节时，按作用域筛选日志
                records_to_emit = []
                for level, msg, scope in buffered_logs:
                    if scope and any(f"scene:{name}" in scope for name in matched_names):
                        records_to_emit.append((level, msg))

                if not records_to_emit:
                    for name in matched_names:
                        self.logger.debug(f"匹配成功: {name}")
                else:
                    for level, msg in records_to_emit:
                        try:
                            self.logger.log(level, msg)
                        except Exception:
                            pass
        else:
            # 匹配失败：回放本次缓冲的所有日志，便于定位问题
            for level, msg, scope in buffered_logs:
                try:
                    self.logger.log(level, msg)
                except Exception:
                    pass

        return result

    def _detect_popup_first(self, scene_img, bool_debug=False) -> Union[Scene, None]:
        """
        优先识别弹窗场景

        Args:
            scene_img: 场景图像
            bool_debug: 是否调试模式

        Returns:
            如果识别到弹窗则返回Scene对象，否则返回None
        """
        for scene_id in self.popup_scenes:
            scene = self.scene_graph.scenes.get(scene_id)
            if not scene or not scene.elements:
                self.logger.warning(f"{scene_id}不存在或其下无元素")
                continue

            # 在调试模式下，设置当前匹配作用域为该场景，便于缓冲日志按场景分组
            prev_scope = getattr(self, '_current_debug_scope', None)
            if bool_debug:
                self._current_debug_scope = f"scene:{scene.name}"
                self.logger.debug(f"检查弹窗场景: {scene.name}")

            flag = self.scene_match(scene_img, scene, bool_debug)
            # 恢复之前的作用域
            if bool_debug:
                self._current_debug_scope = prev_scope
            if flag:
                # 将识别到的弹窗加入排除列表
                self._excluded_popups_in_current_recognition.add(scene_id)

                # 检查弹窗场景是否有子场景（如确认对话框等）
                final_scene = self._check_sub_scenes(scene_img, scene_id, bool_debug, is_popup=True)
                return final_scene

        return None

    def _detect_normal_scene(self, scene_img, bool_debug=False) -> Union[str, Scene]:
        """
        识别正常场景（非弹窗）

        Args:
            scene_img: 场景图像
            bool_debug: 是否调试模式

        Returns:
            识别到的场景
        """
        # 存储已检查过的场景，避免循环
        checked_scenes = set()
        current_scene = None

        # 先找到初始匹配的场景（排除弹窗场景）
        for scene_id, scene in self.scene_graph.scenes.items():
            # 跳过弹窗场景（已检查过）
            if scene_id in self.popup_scenes:
                continue

            if not scene.elements:
                continue

            # 在调试模式下，设置当前匹配作用域为该场景，便于缓冲日志按场景分组
            prev_scope = getattr(self, '_current_debug_scope', None)
            if bool_debug:
                self._current_debug_scope = f"scene:{scene.name}"
                self.logger.debug(f"开始匹配场景: {scene.name}")

            flag = self.scene_match(scene_img, scene, bool_debug)
            if bool_debug:
                self._current_debug_scope = prev_scope
            if flag:
                current_scene = scene_id
                break

        # 如果没有找到初始场景，检查特殊X标记
        if not current_scene:
            return self._check_unknown_with_x(scene_img, bool_debug)

        # 递归检查子场景，使用集合避免循环
        final_scene = self._check_sub_scenes(scene_img, current_scene, bool_debug, is_popup=False)

        # 如果是主场景，检查是否有X标记
        if final_scene == "主场景" or (isinstance(final_scene, Scene) and final_scene.name == "主场景"):
            unknown_with_x = self._check_unknown_with_x(scene_img, bool_debug)
            if unknown_with_x == "未知含X场景":
                return unknown_with_x

        return final_scene

    def _check_sub_scenes(self, scene_img, current_scene_id, bool_debug, is_popup=False) -> Union[str, Scene]:
        """
        递归检查子场景

        Args:
            scene_img: 场景图像
            current_scene_id: 当前场景ID
            bool_debug: 是否调试模式
            is_popup: 当前是否为弹窗场景

        Returns:
            最终场景
        """
        checked_scenes = set()
        current_scene = current_scene_id

        while current_scene in self.coincident_scenes and current_scene not in checked_scenes:
            checked_scenes.add(current_scene)
            found_sub_scene = None

            # 检查当前场景的所有子场景
            for sub_scene_name in self.coincident_scenes[current_scene]:
                # 跳过已检查过的场景
                if sub_scene_name in checked_scenes:
                    continue

                # 如果是弹窗场景且已排除，跳过
                if sub_scene_name in self._excluded_popups_in_current_recognition:
                    continue

                sub_scene = self.scene_graph.scenes.get(sub_scene_name)
                if not sub_scene:
                    continue

                # 在调试模式下，将当前作用域设置为正在检查的子场景
                prev_scope = getattr(self, '_current_debug_scope', None)
                if bool_debug:
                    self._current_debug_scope = f"scene:{sub_scene_name}"
                    self.logger.debug(f"检查子场景: {sub_scene_name}")

                flag = self.scene_match(scene_img, sub_scene, bool_debug)
                if bool_debug:
                    self._current_debug_scope = prev_scope

                if flag:
                    # 如果是弹窗场景，标记为已排除
                    if sub_scene_name in self.popup_scenes and not is_popup:
                        self._excluded_popups_in_current_recognition.add(sub_scene_name)

                    found_sub_scene = sub_scene_name
                    break  # 找到第一个匹配的子场景就继续深入检查

            # 如果找到子场景则继续深入，否则结束
            if found_sub_scene:
                current_scene = found_sub_scene
            else:
                break

        return self.scene_graph.scenes.get(current_scene, current_scene)

    def _check_unknown_with_x(self, scene_img, bool_debug=False) -> str:
        """
        检查未知含X场景

        Args:
            scene_img: 场景图像
            bool_debug: 是否调试模式

        Returns:
            场景名称
        """
        for x in [
            self.scene_graph.get_element("主场景", "X-普通"),
            self.scene_graph.get_element("主场景", "X-广告-1"),
            self.scene_graph.get_element("主场景", "X-广告-2")
        ]:
            if x:
                matches = self.element_match(scene_img, x, bool_debug)
                if matches:
                    return "未知含X场景"
        return "未知场景"

    def scene_match(self, scene_img, template, bool_debug=True):
        """
        只对传入场景进行匹配，为了与scene区分
        Args:
            scene_img:
            template(Scene):
            bool_debug:

        Returns:

        """
        result = []
        matched_elements_info = []
        for element in template.elements:
            if not element.symbol:
                continue
            # 在调试模式下，设置元素级作用域，保证模板/特征匹配时的日志可追溯到该元素
            prev_scope = getattr(self, '_current_debug_scope', None)
            if bool_debug:
                self._current_debug_scope = f"scene:{template.name}|element:{element.name}"
            try:
                matches = self.element_match(scene_img, element, bool_debug)
            finally:
                if bool_debug:
                    self._current_debug_scope = prev_scope
            if matches:
                match_count = len(matches)
                result.append(match_count)
                # 获取 element 的调试记录（如果有）
                element_debug = None
                try:
                    element_debug = self._debug_match_records.get(element.name, None)
                except Exception:
                    element_debug = None
                matched_elements_info.append({
                    "element_name": element.name,
                    "match_count": match_count,
                    "boxes": matches,
                    "debug": element_debug,
                })
            else:
                return False
        if result and max(result) > 0:
            if bool_debug:
                self.logger.info(f"匹配成功: {template.name}")
                try:
                    self._last_successful_scene_details = {
                        "scene": template.name,
                        "elements": matched_elements_info,
                    }
                except Exception:
                    self._last_successful_scene_details = None
            return True

    def element_match(self, scene_img, template, bool_debug=True):
        """
        在场景图中匹配模板元素，忽略模板的透明像素（Alpha=0区域），支持多目标和去重

        Args:
            scene_img(np.ndarray): 场景图像（BGR格式的numpy数组，如截图）
            template(Element): 模板图像
            bool_debug(bool): 是否回报日志

        Returns:
            List[Tuple[int, int, int, int]]
            目标位置列表，每个元素为(x1, y1, x2, y2)，表示匹配区域的左上角和右下角坐标
        """
        if template.match_type == MatchType.SIFT:
            return self.sift_match(template, scene_img)
        else:
            return self.template_match(template, scene_img, bool_debug)

    def sift_match(self, template: Element, scene_img, ratio=0.75):
        min_match_ratio = template.threshold
        # 1. 读取图像
        template_gray = template.gray
        scene_gray = cv2.cvtColor(scene_img, cv2.COLOR_BGR2GRAY).astype(np.uint8)

        x, y, w_roi, h_roi = template.roi_x, template.roi_y, template.roi_width, template.roi_height
        scene_gray_roi = scene_gray[y:y + h_roi, x:x + w_roi]

        h, w = template_gray.shape[:2]  # 模板尺寸

        # 2. 初始化SIFT检测器
        sift = cv2.SIFT_create()

        # 3. 检测特征点并计算描述符（计时）
        start_time = time.perf_counter()
        kp1, des1 = sift.detectAndCompute(template_gray, None)  # 模板特征
        kp2, des2 = sift.detectAndCompute(scene_gray_roi, None)  # 场景特征（在ROI区域内）
        feature_time = time.perf_counter() - start_time

        # 计算最小匹配点数（基于模板特征数量的比例）
        num_template_features = len(kp1)
        # 确保至少有4个匹配点（单应性矩阵计算的最小要求）
        min_good_matches = max(4, int(num_template_features * min_match_ratio))
        self.logger.debug(f"[{template.name}] 模板特征数: {num_template_features}, 所需最小匹配: {min_good_matches}")

        # 记录一些基础调试信息
        try:
            self._debug_match_records[template.name] = {
                "method": "SIFT",
                "num_template_features": int(num_template_features),
                "min_good_matches": int(min_good_matches),
            }
        except Exception:
            pass

        # 如果没有足够的特征点或描述符，直接返回空结果
        if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
            self.logger.debug(f"[{template.name}] 特征点不足: 模板={len(kp1) if kp1 else 0}, 场景={len(kp2) if kp2 else 0}")
            try:
                rec = self._debug_match_records.get(template.name, {})
                rec.update({
                    "kp_template": len(kp1) if kp1 else 0,
                    "kp_scene": len(kp2) if kp2 else 0,
                })
                self._debug_match_records[template.name] = rec
            except Exception:
                pass
            return []

        # 4. 匹配特征点（使用FLANN快速匹配器）
        start_time = time.perf_counter()
        # FLANN参数设置
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=70)  # 检查次数越多，匹配越准但越慢

        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)  # k=2返回每个特征的两个最佳匹配
        match_time = time.perf_counter() - start_time

        # 5. 应用Lowe's比例测试过滤误匹配
        good_matches = []
        for m, n in matches:
            if m.distance < ratio * n.distance:  # 最佳匹配距离远小于次佳匹配
                good_matches.append(m)
        self.logger.debug(f"[{template.name}] 有效匹配点数：{len(good_matches)}")
        try:
            rec = self._debug_match_records.get(template.name, {})
            rec.update({
                "kp_template": len(kp1),
                "kp_scene": len(kp2),
                "good_matches": len(good_matches),
            })
            self._debug_match_records[template.name] = rec
        except Exception:
            pass

        if len(good_matches) >= min_good_matches:
            # 提取匹配点坐标
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            # 计算单应性矩阵（通过RANSAC过滤异常值）
            H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            if H is None:
                self.logger.debug(f"[{template.name}] 无法计算单应性矩阵")
                try:
                    rec = self._debug_match_records.get(template.name, {})
                    rec.update({"H": None})
                    self._debug_match_records[template.name] = rec
                except Exception:
                    pass
                return []

            # 模板四个角点映射到场景图
            pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, H)  # 场景图中匹配区域的四个角点

            # 将ROI区域内的坐标转换为原图坐标
            for i in range(len(dst)):
                dst[i][0][0] += x  # x坐标加上ROI的x偏移
                dst[i][0][1] += y  # y坐标加上ROI的y偏移

            corners_2d = [point[0] for point in dst]  # 格式：[(x1,y1), (x2,y2), (x3,y3), (x4,y4)]

            # 计算最小和最大坐标（确定边界框）
            x_coords = [p[0] for p in corners_2d]
            y_coords = [p[1] for p in corners_2d]
            # 框的边界坐标
            location = (int(min(x_coords)), int(min(y_coords)), int(max(x_coords)), int(max(y_coords)))
            try:
                rec = self._debug_match_records.get(template.name, {})
                rec.update({"location": location})
                self._debug_match_records[template.name] = rec
            except Exception:
                pass
            return [location]
        else:
            return []

    def template_match(self, template: Element, scene_img, bool_debug: bool = True):
        start = time.perf_counter()
        template_img = template.gray
        mask = template.mask
        threshold = template.threshold

        # 1. 转换场景图像为灰度图（先获取原始尺寸）
        scene_gray = cv2.cvtColor(scene_img, cv2.COLOR_BGR2GRAY).astype(np.uint8)
        scene_h, scene_w = scene_gray.shape  # 原始场景图像的高度、宽度

        # 2. 修复ROI裁剪：确保不超出原始图像范围
        x = template.roi_x
        y = template.roi_y
        w = template.roi_width
        h = template.roi_height

        # 计算合法的ROI边界（避免越界）
        x_end = min(x + w, scene_w)  # 右边界不超过场景宽度
        y_end = min(y + h, scene_h)  # 下边界不超过场景高度
        x_start = max(x, 0)  # 左边界不小于0
        y_start = max(y, 0)  # 上边界不小于0

        # 裁剪合法的ROI区域
        scene_gray_roi = scene_gray[y_start:y_end, x_start:x_end]

        time_1 = time.perf_counter()
        # print(f"[ELEMENT_MATCH]预处理耗时 {(time_1 - start) * 1000:.2f} ms")

        # 6. 执行模板匹配（此时尺寸已合法）
        try:
            result = cv2.matchTemplate(
                image=scene_gray_roi,
                templ=template_img,
                method=cv2.TM_CCOEFF_NORMED,
                mask=mask
            )
            result = np.nan_to_num(result, nan=-1.0, posinf=-1.0, neginf=-1.0)
        except cv2.error as e:
            self.logger.error(f"[{template.name}] 模板匹配执行错误：{e}")
            return []
        time_2 = time.perf_counter()
        # # 检查result的统计信息
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if bool_debug:
            self.logger.debug(f"[{template.name}] 匹配结果统计：最大值={max_val:.2f}")
        # 记录模板匹配的调试信息（基本统计），供外部回放和结构化输出
        try:
            self._debug_match_records[template.name] = {
                "method": "TEMPLATE",
                "max_val": float(max_val),
                "min_val": float(min_val),
                "max_loc": max_loc,
                "roi": (x_start, y_start, x_end, y_end),
                "threshold": float(threshold),
            }
        except Exception:
            pass

        # 5. 筛选超过阈值的匹配位置，并绑定置信度
        locations = np.where(result >= threshold)  # 所有符合条件的位置
        if len(locations[0]) == 0:
            return []  # 无匹配结果

        # 提取每个匹配位置的置信度值
        confidences = [result[y, x] for y, x in zip(locations[0], locations[1])]
        h, w = template_img.shape[:2]  # type: ignore # 模板的高和宽
        # 构建(置信度, x1, y1, x2, y2)的列表，并按置信度降序排序
        matches_with_conf = [
            (conf, int(x + dx), int(y + dy), int(x + dx + w), int(y + dy + h))
            for dx, dy, conf in zip(locations[1], locations[0], confidences)
        ]
        matches_with_conf.sort(reverse=True, key=lambda x: x[0])

        # 提取排序后的框和对应的置信度
        sorted_matches = [(x1, y1, x2, y2) for (conf, x1, y1, x2, y2) in matches_with_conf]
        sorted_confidences = [conf for (conf, x1, y1, x2, y2) in matches_with_conf]  # 新增：提取置信度
        # print(f"[{template_name}]匹配位置（未去重）：{sorted_matches}")
        # print(f"[ELEMENT_MATCH]耗时 {(time.perf_counter() - start) * 1000:.2f} ms")
        # 调用NMS时传入置信度
        keep_boxes = self._non_max_suppression(sorted_matches,
                                               iou_threshold=0.3,
                                               confidences=sorted_confidences)
        # 记录去重后的置信度信息以便回放
        try:
            conf_map = {box: conf for box, conf in zip(sorted_matches, sorted_confidences)}
            kept_confidences = [conf_map.get(box, None) for box in keep_boxes]
            rec = self._debug_match_records.get(template.name, {})
            rec.update({
                "kept_boxes": keep_boxes,
                "kept_confidences": kept_confidences,
                "sorted_matches_len": len(sorted_matches),
            })
            self._debug_match_records[template.name] = rec
        except Exception:
            pass
        return keep_boxes

    @staticmethod
    def _non_max_suppression(boxes: List[Tuple[int, int, int, int]],
                             iou_threshold: float = 0.3,
                             confidences: List[float] = None) -> List[Tuple[int, int, int, int]]:
        """
        去除重叠度高的重复检测框（按置信度优先保留）
        :param boxes: 检测框列表
        :param iou_threshold: IOU阈值
        :param confidences: 每个框对应的置信度（与boxes顺序一致）
        """
        if not boxes:
            return []

        boxes_np = np.array(boxes, dtype=np.float32)
        x1, y1, x2, y2 = boxes_np[:, 0], boxes_np[:, 1], boxes_np[:, 2], boxes_np[:, 3]
        area = (x2 - x1 + 1) * (y2 - y1 + 1)

        # 关键修改：按置信度降序排序（若提供置信度），否则按原顺序
        if confidences is not None:
            indices = np.argsort(np.array(confidences))[::-1]  # 置信度降序索引
        else:
            indices = np.argsort(y2)  # 兼容旧逻辑（无置信度时）

        keep = []
        while indices.size > 0:
            idx = indices[0]  # 取当前置信度最高的框（原逻辑是取最后一个）
            keep.append(boxes[idx])
            indices = indices[1:]  # 移除当前框，处理剩余框

            # 计算与剩余框的IOU
            xx1, yy1 = np.maximum(x1[idx], x1[indices]), np.maximum(y1[idx], y1[indices])
            xx2, yy2 = np.minimum(x2[idx], x2[indices]), np.minimum(y2[idx], y2[indices])
            w, h = np.maximum(0, xx2 - xx1 + 1), np.maximum(0, yy2 - yy1 + 1)
            overlap = (w * h) / (area[idx] + area[indices] - w * h)

            # 保留IOU小于阈值的框
            indices = indices[overlap <= iou_threshold]

        # print(f"匹配位置（去重）：{keep}")
        return keep

    def _rgb_average(self, img, mask=None):
        """
        计算图像在掩码有效区域内的RGB平均颜色

        参数:
            img:
            mask: 外部掩码（可选），若无则使用图像自带的alpha通道

        返回:
            (r, g, b) 平均颜色元组，出错返回None
        """
        try:
            # 分离通道：OpenCV默认BGR(A)格式
            channels = cv2.split(img)
            b, g, r = channels[0:3]  # 提取BGR通道

            # 确定掩码
            if mask is not None:
                # 使用外部传入的掩码
                final_mask = mask
            elif img.shape[2] == 4:
                # 使用图像的alpha通道作为掩码
                _, final_mask = cv2.threshold(channels[3], 1, 255, cv2.THRESH_BINARY)
            else:
                # 无掩码时使用全白掩码
                final_mask = np.ones_like(b) * 255

            # 确保掩码是二值单通道
            if final_mask.ndim > 2:
                final_mask = cv2.cvtColor(final_mask, cv2.COLOR_BGR2GRAY)

            # 计算掩码区域内的平均颜色
            masked_pixels = final_mask > 0
            r_avg = int(np.mean(r[masked_pixels]))
            g_avg = int(np.mean(g[masked_pixels]))
            b_avg = int(np.mean(b[masked_pixels]))

            return r_avg, g_avg, b_avg

        except Exception as e:
            self.logger.error(f"计算平均颜色时出错: {str(e)}")
            return None


if __name__ == "__main__":
    logger = setup_logging()
    rg = Recognizer(SceneGraph(ResourceDBManager()))

    # 图片目录路径
    image_dir = r"F:\PyProject\Xuan\test_scene"

    # 获取目录下所有图片文件
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    image_files = [
        f for f in os.listdir(image_dir)
        if os.path.isfile(os.path.join(image_dir, f)) and
           os.path.splitext(f)[1].lower() in image_extensions
    ]

    for img_file in image_files:
        # 提取场景名（不含扩展名）
        scene_name = os.path.splitext(img_file)[0]

        # if scene_name not in ["网络不畅通"]:
        #     continue
        img_path = os.path.join(image_dir, img_file)

        try:
            # 读取图片
            img = cv_imread(img_path)
            if img is None:
                print(f"无法读取图片: {img_file}")
                continue

            # 执行识别并计时
            start_time = time.perf_counter()
            result = rg.scene(img, False)  # 假设该方法返回识别出的场景名
            if isinstance(result, Scene):
                result = result.name
            elapsed_time = time.perf_counter() - start_time

            # 比对结果
            if result != scene_name:
                print(f"⚠️ 不一致 - 图片: {img_file} | 预期: {scene_name} | 实际: {result} | 耗时: {elapsed_time:.2f}秒")
            else:
                print(f"✅ 一致 - 图片: {img_file} | 场景: {scene_name} | 耗时: {elapsed_time:.2f}秒")

        except Exception as e:
            print(f"处理图片 {img_file} 时出错: {str(e)}")
