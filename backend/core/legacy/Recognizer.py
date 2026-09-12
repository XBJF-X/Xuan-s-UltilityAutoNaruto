# -*- coding: utf-8 -*-
"""场景/元素识别器。

识别链：截图 → 弹窗优先 → 候选场景快扫 →（未命中时）全量兜底 → 同屏子场景下沉
→ 返回 `Scene` 对象，或 `"未知场景"` / `"未知含X场景"` 字符串。

## 性能（2026-09-12 实测：1600×900 截图 / 193 场景 / 314 条转移边）
- 优化前：每帧全量遍历 193 个场景，最坏帧 0.64s / 193 次 `scene_match`，
  常规帧均值 ≈0.18s，单次 `scene_match` ≈3.4ms（其中 `matchTemplate` 占 ~60%）。
- 优化后：只扫描「当前场景的入/出边邻居 + 弹窗」（见 `SceneIndex`），候选集 ≈4~25 个场景；
  Tier-1 未命中则全量兜底（**保证不漏判**）并把新跳转记为学习边，使兜底逐步归零。
- 单帧固定开销：整幅截图的灰度转换**按帧缓存**（原先每个元素各转一次，全量扫描 ≈135 次/帧
  ≈61ms），模板匹配尾部改为「`isfinite` + 阈值」一次筛候选（省掉 `nan_to_num` 整块拷贝
  与单独的 `minMaxLoc` 全图扫描）；未命中时的最大响应只在调试模式采集。
- 一键回退：`Recognizer(..., enable_pruning=False)` 恢复旧的全量扫描行为。
"""
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set, Tuple, Union

import cv2
import numpy as np

from backend.utils import cv_imread
from backend.utils import get_real_path
from backend.utils import setup_logging
from backend.tools.resource_db import ResourceDBManager
from backend.tools.resource_model import Element, Scene
from backend.core.legacy.Enums import ElementType, MatchType
from backend.core.legacy.OnnxOcr import get_shared_onnx_ocr
from backend.core.legacy.RecognizerDebug import (
    DebugScope,
    capture_logs,
    replay_buffered_logs,
    scoped,
)
from backend.core.legacy.Scene.SceneGraph import SceneGraph
from backend.core.legacy.Scene.SceneIndex import get_scene_index
from backend.core.legacy.Scene.SceneMeta import (
    COINCIDENT_SCENES,
    POPUP_SCENES,
    UNKNOWN_SCENE,
    UNKNOWN_SCENES,
    UNKNOWN_WITH_X_SCENE,
)

# OCR 小区域预放大参数（2026-08-25 实测校准）：
# 极小文本区域（如"剩余挑战券数量"数字角标）直接送模型时，det 预处理会先 padding 到
# 32x32 再线性放大到短边 736，文字信息损失严重导致检测/识别失败（表现为"识别不到且极快返回"）。
# 实测 3 张不同数字截图对比：原始 ROI 识别不稳定（数字 9/6 丢失），预放大到短边 256
# （约 3 倍）三张全部稳定识别出数字；放大到 512/736 反而因插值失真导致数字丢失。
_OCR_UPSCALE_MIN_SHORT_SIDE = 128   # ROI 短边低于该像素视为"小区域"，触发预放大
_OCR_UPSCALE_TARGET_SIDE = 256      # 放大目标：短边放大到 256（实测识别最稳定）
_OCR_UPSCALE_MAX_RATIO = 16.0       # 放大倍数上限，防止极小区域放大过猛（内存/耗时保护）

# 是否启用「按场景转移图裁剪待匹配场景集」（置 False 或构造参数 enable_pruning=False
# 即回到"每帧全量扫描"的旧行为）。
ENABLE_SCENE_PRUNING = True

# 弹窗场景的成员判断用 frozenset（self.popup_scenes 保持有序 tuple 供顺序匹配）
_POPUP_SCENE_SET = frozenset(POPUP_SCENES)


@dataclass
class _MatchContext:
    """一次 `scene()` 调用的上下文。

    替代原先散落在实例属性上的隐式状态（`_current_debug_scope` /
    `_debug_match_records` / `_last_successful_scene_details` /
    `_excluded_popups_in_current_recognition`），避免跨帧/跨线程互相串味。
    """

    debug: bool = False
    scope: Optional[DebugScope] = None
    records: Dict[str, dict] = field(default_factory=dict)
    success_details: Optional[dict] = None
    excluded_popups: Set[str] = field(default_factory=set)
    # 本帧灰度图缓存：同一帧内所有元素匹配共用一次 BGR→GRAY 转换（见 _scene_gray）
    gray: Optional[np.ndarray] = None


def _scene_name(result) -> Optional[str]:
    """把识别结果（Scene / str / None）归一为场景名。"""
    if result is None:
        return None
    return getattr(result, "name", None) or str(result)


def _is_unknown(result) -> bool:
    """是否为"未识别到已知场景"（None 或两个未知标记字符串）。"""
    if result is None:
        return True
    return isinstance(result, str) and result in UNKNOWN_SCENES


class Recognizer:
    """场景识别器：全量兜底的候选集裁剪识别（详见模块 docstring）。"""

    def __init__(self, scene_graph: SceneGraph, parent_logger: str | logging.Logger = "",
                 *, enable_pruning: bool = ENABLE_SCENE_PRUNING):
        if isinstance(parent_logger, str):
            self.logger = logging.getLogger("识别器")
        else:
            self.logger = parent_logger.getChild("识别器")
        self.scene_graph = scene_graph
        # 元数据（纯数据外移到 SceneMeta：弹窗为有序 tuple，匹配顺序 = 定义顺序）
        self.popup_scenes = POPUP_SCENES
        self.coincident_scenes = COINCIDENT_SCENES
        self.enable_pruning = enable_pruning
        # OCR 识别器（惰性初始化，仅在首次使用 OCR 时加载模型）
        self._onnx_ocr = None
        # 本实例上一帧命中的场景名：调用方未传 hint 时的裁剪依据
        self._last_matched_scene: Optional[str] = None
        # 当前帧上下文 + 兼容旧实例属性名（调试脚本/旧代码可能直接读取）
        self._ctx = _MatchContext()
        self._excluded_popups_in_current_recognition: Set[str] = self._ctx.excluded_popups
        self._debug_match_records: Dict[str, dict] = self._ctx.records
        self._last_successful_scene_details: Optional[dict] = None

    # ============================================================= 对外入口

    def scene(self, scene_img, bool_debug: bool = False, hint: Optional[str] = None,
              allow_full_scan: bool = True) -> Union[str, Scene, None]:
        """识别截图所属场景。

        Args:
            scene_img: BGR 截图（numpy 数组）
            bool_debug: 调试模式：缓冲匹配日志并按匹配结果筛选回放（正常路径不付该开销）
            hint: 当前所处场景名。给出时（且与本实例上一帧识别一致，即"可信"）启用
                "按转移图裁剪"，只匹配 hint 自身、其入/出边邻居、同屏子场景与弹窗；
                不可信（hint 与本实例上一帧识别不一致，说明状态走样）或未给出时，
                退回全量扫描仲裁（与优化前行为一致）。
            allow_full_scan: Tier-1 候选集未命中时是否退化为全量扫描。默认 True
                （保证不漏判）；置 False 表示只信任候选集（更快，仅供对照测试）。

        Returns:
            Scene 对象（命中）；`"未知场景"` / `"未知含X场景"`（未命中）；
            None（既无命中场景，也没有 X 标记元素）
        """
        if not bool_debug:
            return self._recognize(scene_img, _MatchContext(), hint, allow_full_scan)

        # 调试模式：识别过程日志先缓冲，返回前按匹配结果筛选回放
        ctx = self._make_ctx(True)
        with capture_logs(self.logger, ctx.scope) as buffered:
            result = self._recognize(scene_img, ctx, hint, allow_full_scan)
        replay_buffered_logs(self.logger, buffered, result, self._last_successful_scene_details)
        return result

    def _make_ctx(self, debug: bool) -> _MatchContext:
        """构造一次识别调用的上下文（debug 时带日志作用域载体）。"""
        return _MatchContext(debug=debug, scope=DebugScope() if debug else None)

    def _ensure_ctx(self, ctx: Optional[_MatchContext], debug: bool) -> _MatchContext:
        """取调用方传入的帧上下文；未传（外部直接调 scene_match/element_match 等）时
        新建并挂到实例上——保证 `self._debug_match_records` 等兼容属性仍能读到本次记录。
        """
        if isinstance(ctx, _MatchContext):
            return ctx
        ctx = self._make_ctx(bool(debug))
        self._bind_context(ctx)
        return ctx

    def _bind_context(self, ctx: _MatchContext) -> None:
        """把本帧上下文挂到实例上（并同步旧的属性名，保持外部可读）。"""
        self._ctx = ctx
        self._excluded_popups_in_current_recognition = ctx.excluded_popups
        self._debug_match_records = ctx.records

    def _scene_gray(self, ctx: _MatchContext, scene_img) -> np.ndarray:
        """取当前帧的灰度图（按帧缓存：整幅截图只做一次 BGR→GRAY）。

        原先每个元素的 `template_match`/`sift_match` 都各自对整幅截图转一次灰度：
        全量扫描时每帧 ~135 次（实测 ≈0.45ms/次 ≈ 61ms/帧，约占单帧成本 17%）。
        缓存挂在帧上下文里，形状不一致时自动重算（防御 ctx 被跨图复用）。
        """
        gray = ctx.gray
        if gray is None or gray.shape != scene_img.shape[:2]:
            gray = cv2.cvtColor(scene_img, cv2.COLOR_BGR2GRAY).astype(np.uint8)
            ctx.gray = gray
        return gray

    # ============================================================= 识别主流程

    def _recognize(self, scene_img, ctx: _MatchContext, hint: Optional[str],
                   allow_full_scan: bool) -> Union[str, Scene, None]:
        """两级识别：候选集快扫（Tier-1）→ 全量兜底（Tier-2）。"""
        self._bind_context(ctx)
        hint = hint or self._last_matched_scene
        index = get_scene_index(self.scene_graph, self.logger)

        # 可信 hint：调用方给的 hint 与本实例上一帧的识别结果一致（说明跟踪的状态没走样）。
        # 不可信时不裁剪——一个陈旧/错误的 hint 所在场景**可能恰好也能匹配当前画面**
        # （库中存在重叠标志元素），从而抢在真实场景之前被采纳（误判）。此时退回全量扫描
        # 仲裁（与优化前行为一致）；只有稳定帧（hint 与自身状态一致）才享受裁剪收益。
        trusted = hint is not None and hint == self._last_matched_scene
        candidates = index.candidates(hint) if (self.enable_pruning and trusted) else None
        if candidates is not None:
            self.logger.debug(
                "候选集裁剪：hint=%s，候选 %d 个（%s）",
                hint, len(candidates), "、".join(candidates),
            )
        elif self.enable_pruning and hint and not trusted:
            index.full_scan_untrusted += 1
            self.logger.debug(
                "hint=%s 与上一帧识别（%s）不一致 → 不做裁剪，走全量仲裁",
                hint, self._last_matched_scene)

        result = self._detect_popup_first(scene_img, ctx)
        if result is None:
            result = self._detect_normal_scene(scene_img, ctx, candidates)

        if _is_unknown(result) and candidates is not None and allow_full_scan:
            # 候选集未命中（图上缺边 / 新场景 / 跳到了远端）→ 全量兜底，保证不漏判。
            # 注意：弹窗扫描无需重做——上面已对**同一帧**扫过全部弹窗且未命中，
            # 重复一遍只会白付 19 次模板匹配。
            index.full_scan_fallbacks += 1
            self.logger.debug(
                "候选集未命中（hint=%s，候选 %d 个）→ 全量兜底扫描", hint, len(candidates))
            result = self._detect_normal_scene(scene_img, ctx, None)
        elif candidates is not None and not _is_unknown(result):
            index.tier1_hits += 1

        if not _is_unknown(result):
            # 学习边：把"我们真实观察到的一次跳转"补进索引（图上没有这条边时才记），
            # 让同一处缺边只需付一次全量兜底代价。以自身上一帧识别为起点，
            # 避免把陈旧的调用方 hint 当成真实跳转学进去。
            index.note_observed(self._last_matched_scene, _scene_name(result))
            self._last_matched_scene = _scene_name(result)
        self._last_successful_scene_details = ctx.success_details
        ctx.gray = None      # 释放本帧灰度缓存（别让实例长期持有 ~4MB 的整帧灰度）
        return result

    def _detect_popup_first(self, scene_img, ctx=None) -> Optional[Scene]:
        """优先识别弹窗场景（弹窗遮挡下层场景，必须先判）。

        Args:
            scene_img: 场景图像
            ctx: `_MatchContext`；为兼容旧调用也可直接传 bool（= bool_debug）

        Returns:
            命中弹窗（或其同屏子场景）返回 Scene，否则 None
        """
        ctx = self._ensure_ctx(ctx, bool(ctx))
        for scene_id in self.popup_scenes:
            scene = self.scene_graph.scenes.get(scene_id)
            if not scene or not scene.elements:
                self.logger.warning(f"{scene_id}不存在或其下无元素")
                continue

            with scoped(ctx, f"scene:{scene.name}"):
                self.logger.debug(f"检查弹窗场景: {scene.name}")
                flag = self.scene_match(scene_img, scene, ctx=ctx)
            if flag:
                # 本次识别后续下沉时不再重复检查该弹窗
                ctx.excluded_popups.add(scene_id)
                return self._check_sub_scenes(scene_img, scene_id, ctx, is_popup=True)
        return None

    def _detect_normal_scene(self, scene_img, ctx=None,
                             candidates: Optional[Sequence[str]] = None):
        """在候选集（candidates=None 时为全量）内找首个匹配场景并下沉同屏子场景。

        Args:
            scene_img: 场景图像
            ctx: `_MatchContext`（兼容旧调用可直接传 bool = bool_debug）
            candidates: 候选场景名序列（Tier-1）；None = 全量扫描（顺序同旧实现）

        Returns:
            Scene / `"未知场景"` / `"未知含X场景"`
        """
        ctx = self._ensure_ctx(ctx, bool(ctx))
        scene_ids = candidates if candidates is not None else self.scene_graph.scenes
        current_scene = None
        for scene_id in scene_ids:
            if scene_id in _POPUP_SCENE_SET:      # 弹窗已在上一步检查过
                continue
            scene = self.scene_graph.scenes.get(scene_id)
            if not scene or not scene.elements:
                continue

            with scoped(ctx, f"scene:{scene.name}"):
                self.logger.debug(f"开始匹配场景: {scene.name}")
                flag = self.scene_match(scene_img, scene, ctx=ctx)
            if flag:
                current_scene = scene_id
                break

        if not current_scene:
            return self._check_unknown_with_x(scene_img, ctx)

        final_scene = self._check_sub_scenes(scene_img, current_scene, ctx, is_popup=False)
        # 主场景页可能残留广告/活动弹层的 X 标记 → 仍按"未知含X场景"上报
        if _scene_name(final_scene) == "主场景":
            if self._check_unknown_with_x(scene_img, ctx) == UNKNOWN_WITH_X_SCENE:
                return UNKNOWN_WITH_X_SCENE
        return final_scene

    def _check_sub_scenes(self, scene_img, current_scene_id, ctx=None,
                          is_popup: bool = False):
        """沿同屏共存表（COINCIDENT_SCENES）逐层下沉子场景。

        Args:
            scene_img: 场景图像
            current_scene_id: 当前已匹配的场景名
            ctx: `_MatchContext`（兼容旧调用可直接传 bool = bool_debug）
            is_popup: 当前起点是否为弹窗（弹窗场景不加入"已排除弹窗"）

        Returns:
            最终场景（Scene；若场景名不在库中则返回名字本身）
        """
        ctx = self._ensure_ctx(ctx, bool(ctx))
        checked_scenes = set()
        current_scene = current_scene_id

        while current_scene in self.coincident_scenes and current_scene not in checked_scenes:
            checked_scenes.add(current_scene)
            found_sub_scene = None

            for sub_scene_name in self.coincident_scenes[current_scene]:
                if sub_scene_name in checked_scenes:
                    continue
                # 本轮识别中已被排除的弹窗不再重复检查
                if sub_scene_name in ctx.excluded_popups:
                    continue
                sub_scene = self.scene_graph.scenes.get(sub_scene_name)
                if not sub_scene:
                    continue

                with scoped(ctx, f"scene:{sub_scene_name}"):
                    self.logger.debug(f"检查子场景: {sub_scene_name}")
                    flag = self.scene_match(scene_img, sub_scene, ctx=ctx)
                if flag:
                    if sub_scene_name in _POPUP_SCENE_SET and not is_popup:
                        ctx.excluded_popups.add(sub_scene_name)
                    found_sub_scene = sub_scene_name
                    break      # 命中第一个子场景即继续深入

            if found_sub_scene:
                current_scene = found_sub_scene
            else:
                break

        return self.scene_graph.scenes.get(current_scene, current_scene)

    def _check_unknown_with_x(self, scene_img, ctx=None) -> str:
        """用主场景的 X 标记元素区分"未知含X场景"与"未知场景"。"""
        ctx = self._ensure_ctx(ctx, bool(ctx))
        for x in (
            self.scene_graph.get_element("主场景", "X-普通"),
            self.scene_graph.get_element("主场景", "X-广告-1"),
            self.scene_graph.get_element("主场景", "X-广告-2"),
        ):
            if x and self.element_match(scene_img, x, ctx=ctx):
                return UNKNOWN_WITH_X_SCENE
        return UNKNOWN_SCENE

    # ============================================================= 元素/区域识别

    def area_ocr(self, scene_img, ocr_area: Element, bool_debug: bool = False) -> List:
        """对指定 OcrArea 区域执行 OCR 识别。

        Args:
            scene_img(np.ndarray): 场景图像（BGR，如截图）
            ocr_area(Element): OCR_AREA 类型元素
            bool_debug(bool): 是否回报日志

        Returns:
            List[Tuple[str, List[int], float]]：识别结果列表，每项为
            (识别文本, [x1, y1, x2, y2], 置信度)；坐标为原图坐标（已叠加 ROI 偏移）
        """
        if ocr_area.type != ElementType.OCR_AREA:
            self.logger.warning(f"[{ocr_area.name}] 不是 OcrArea 类型，跳过 OCR 识别")
            return []

        # 惰性获取全局共享 OCR 识别器（所有配置复用同一份 ONNX 模型，避免多开内存翻倍）
        if self._onnx_ocr is None:
            self._onnx_ocr = get_shared_onnx_ocr()

        # 裁剪识别区域
        x, y = ocr_area.roi_x, ocr_area.roi_y
        w, h = ocr_area.roi_width, ocr_area.roi_height
        scene_h, scene_w = scene_img.shape[:2]
        x_end = min(x + w, scene_w)
        y_end = min(y + h, scene_h)
        x_start = max(x, 0)
        y_start = max(y, 0)
        if x_end <= x_start or y_end <= y_start:
            self.logger.warning(f"[{ocr_area.name}] ROI 区域非法，跳过 OCR 识别")
            return []
        roi_img = scene_img[y_start:y_end, x_start:x_end]
        # png 底图/截图可能带 alpha 通道（4 通道 BGRA），而 OCR 检测预处理
        # NormalizeImage 仅支持 3 通道（mean/std 为 1x1x3），4 通道会触发
        # numpy 广播错误（(H,W,4) - (1,1,3)）导致 OCR 识别失败，统一转 3 通道 BGR。
        if roi_img.ndim == 3 and roi_img.shape[2] == 4:
            roi_img = cv2.cvtColor(roi_img, cv2.COLOR_BGRA2BGR)

        # 过小区域识别前放大：短边 < 128px 的 ROI 直接送模型时，det 内部 padding + 放大
        # 会导致文字模糊、检测不到文本（表现为"识别不到且极快返回"）。
        up_scale = 1.0
        roi_h, roi_w = roi_img.shape[:2]
        if min(roi_h, roi_w) < _OCR_UPSCALE_MIN_SHORT_SIDE:
            up_scale = min(
                _OCR_UPSCALE_TARGET_SIDE / float(min(roi_h, roi_w)),
                _OCR_UPSCALE_MAX_RATIO,
            )
            new_w = max(int(round(roi_w * up_scale)), 1)
            new_h = max(int(round(roi_h * up_scale)), 1)
            roi_img = cv2.resize(roi_img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

        try:
            # 注意：OnnxOcr.ocr 第二个参数是裁剪框 box，而非阈值。
            # 此处 roi_img 已是裁剪后的区域，传 None 表示无需坐标偏移复原；
            # raw_json=True 获取结构化列表 [{"text", "score", "box"}, ...]。
            results = self._onnx_ocr.ocr(
                roi_img, None, (scene_w, scene_h), raw_json=True) or []
        except Exception as e:
            self.logger.error(f"[{ocr_area.name}] OCR 识别失败：{e}")
            return []

        # 文本框坐标除以放大比例还原到 ROI 原坐标，再叠加 ROI 偏移得到原图坐标
        min_score = getattr(ocr_area, "ocr_min_score", 0.5)
        area_results = []
        for item in results:
            text = item.get("text", "")
            score = float(item.get("score", 0.0))
            if score < min_score:
                continue
            # 框格式遵循项目惯例：[[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
            box = item.get("box", [])
            xs = [float(p[0]) / up_scale for p in box]
            ys = [float(p[1]) / up_scale for p in box]
            area_results.append((text, [
                x_start + int(min(xs)), y_start + int(min(ys)),
                x_start + int(max(xs)), y_start + int(max(ys))
            ], score))

        if bool_debug:
            self.logger.debug(f"[{ocr_area.name}] OCR 识别到 {len(area_results)} 条文本")
        return area_results

    def _record_match_debug(self, ctx: _MatchContext, name: str, **fields) -> None:
        """合并记录元素匹配调试信息（替代原先 6 处重复的 try/except 写字典）。"""
        ctx.records.setdefault(name, {}).update(fields)

    def scene_match(self, scene_img, template: Scene, bool_debug: bool = True,
                    ctx: Optional[_MatchContext] = None) -> bool:
        """只对传入的场景做匹配（与 `scene()` 区分）。

        判定规则：场景的**全部**标志元素（`symbol=True`）都命中才算匹配成功，
        任一标志元素不命中立即短路返回 False。

        Args:
            scene_img(np.ndarray): 场景图像
            template(Scene): 待匹配场景
            bool_debug(bool): 是否回报日志
            ctx(_MatchContext): 内部传递的帧上下文（外部调用无需传）

        Returns:
            True = 命中；False = 未命中
        """
        ctx = self._ensure_ctx(ctx, bool_debug)
        result = []
        matched_elements_info = []
        for element in template.elements:
            if not element.symbol:
                continue
            with scoped(ctx, f"scene:{template.name}|element:{element.name}"):
                if element.type == ElementType.OCR_AREA:
                    # OCR 标志元素：识别 ROI 内文本，元素名作为子串出现即视为匹配
                    matches = self._ocr_element_match(scene_img, element, bool_debug)
                else:
                    matches = self.element_match(scene_img, element, bool_debug, ctx=ctx)
            if not matches:
                return False
            result.append(len(matches))
            matched_elements_info.append({
                "element_name": element.name,
                "match_count": len(matches),
                "boxes": matches,
                "debug": ctx.records.get(element.name),
            })

        if result and max(result) > 0:
            if ctx.debug:
                self.logger.info(f"匹配成功: {template.name}")
                ctx.success_details = {
                    "scene": template.name,
                    "elements": matched_elements_info,
                }
            return True
        # 场景没有任何标志元素（`result` 为空）→ 视为不匹配（与旧实现一致）
        return False

    def _ocr_element_match(self, scene_img, element: Element,
                           bool_debug: bool = False) -> List:
        """OCR 标志元素匹配：ROI 内任一识别文本包含元素名即命中。

        匹配机制与其他类型标志元素一致（全部标志元素都要命中场景才算命中）：
        - 命中返回对应文本框列表（`[x1, y1, x2, y2]`，原图坐标）；
        - 无命中返回 []（等价于模板匹配失败，场景整体不匹配）。

        Args:
            scene_img(np.ndarray): 场景图像
            element(Element): OCR_AREA 类型的标志元素
            bool_debug(bool): 是否回报日志

        Returns:
            List[List[int]]: 命中的文本框列表
        """
        results = self.area_ocr(scene_img, element, bool_debug)
        return [box for text, box, _score in results if element.name in text]

    def element_match(self, scene_img, template: Element, bool_debug: bool = True,
                      ctx: Optional[_MatchContext] = None) -> List:
        """按元素的匹配方式分派匹配（TEMPLATE / SIFT）。

        Args:
            scene_img(np.ndarray): 场景图像
            template(Element): 模板元素
            bool_debug(bool): 是否回报日志
            ctx(_MatchContext): 内部传递的帧上下文（外部调用无需传）

        Returns:
            List[Tuple[int, int, int, int]]：命中的框坐标列表（x1, y1, x2, y2）
        """
        ctx = self._ensure_ctx(ctx, bool_debug)
        if template.match_type == MatchType.SIFT:
            return self.sift_match(template, scene_img, ctx=ctx)
        return self.template_match(template, scene_img, bool_debug, ctx=ctx)

    def sift_match(self, template: Element, scene_img, ratio: float = 0.75,
                   ctx: Optional[_MatchContext] = None) -> List:
        """SIFT 特征匹配（ROI 限定）。

        Args:
            template(Element): 模板元素（`match_type == MatchType.SIFT`）
            scene_img(np.ndarray): 场景图像
            ratio(float): Lowe's ratio 测试阈值
            ctx(_MatchContext): 内部传递的帧上下文

        Returns:
            List[Tuple[int, int, int, int]]：命中的外接矩形（0 或 1 个）
        """
        ctx = self._ensure_ctx(ctx, False)
        min_match_ratio = template.threshold
        template_gray = template.gray
        scene_gray = self._scene_gray(ctx, scene_img)

        x, y, w_roi, h_roi = template.roi_x, template.roi_y, template.roi_width, template.roi_height
        scene_gray_roi = scene_gray[y:y + h_roi, x:x + w_roi]

        h, w = template_gray.shape[:2]  # 模板尺寸
        sift = cv2.SIFT_create()

        # 检测特征点并计算描述符
        start_time = time.perf_counter()
        kp1, des1 = sift.detectAndCompute(template_gray, None)      # 模板特征
        kp2, des2 = sift.detectAndCompute(scene_gray_roi, None)     # 场景特征（ROI 内）
        feature_time = time.perf_counter() - start_time

        # 最小匹配点数 = 模板特征数 × 比例（至少 4 个，单应性矩阵最低要求）
        num_template_features = len(kp1)
        min_good_matches = max(4, int(num_template_features * min_match_ratio))
        self.logger.debug(
            f"[{template.name}] 模板特征数: {num_template_features}, "
            f"所需最小匹配: {min_good_matches}（特征提取 {feature_time * 1000:.1f}ms）"
        )
        self._record_match_debug(
            ctx, template.name,
            method="SIFT",
            num_template_features=int(num_template_features),
            min_good_matches=int(min_good_matches),
        )

        # 特征点/描述符不足 → 直接判不匹配
        if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
            self.logger.debug(
                f"[{template.name}] 特征点不足: 模板={len(kp1) if kp1 else 0}, "
                f"场景={len(kp2) if kp2 else 0}"
            )
            self._record_match_debug(
                ctx, template.name,
                kp_template=len(kp1) if kp1 else 0,
                kp_scene=len(kp2) if kp2 else 0,
            )
            return []

        # FLANN 快速匹配 + Lowe's ratio 过滤误匹配
        start_time = time.perf_counter()
        flann = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=70))
        matches = flann.knnMatch(des1, des2, k=2)   # 每个特征的两个最佳匹配
        match_time = time.perf_counter() - start_time

        good_matches = [m for m, n in matches if m.distance < ratio * n.distance]
        self.logger.debug(
            f"[{template.name}] 有效匹配点数：{len(good_matches)}（匹配 {match_time * 1000:.1f}ms）")
        self._record_match_debug(
            ctx, template.name,
            kp_template=len(kp1),
            kp_scene=len(kp2),
            good_matches=len(good_matches),
        )

        if len(good_matches) < min_good_matches:
            return []

        # 提取匹配点坐标并求单应性矩阵（RANSAC 过滤异常值）
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        H, _mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        if H is None:
            self.logger.debug(f"[{template.name}] 无法计算单应性矩阵")
            self._record_match_debug(ctx, template.name, H=None)
            return []

        # 模板四角映射到场景图，再叠加 ROI 偏移还原成原图坐标
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, H)
        for point in dst:
            point[0][0] += x
            point[0][1] += y

        corners_2d = [point[0] for point in dst]      # [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
        x_coords = [p[0] for p in corners_2d]
        y_coords = [p[1] for p in corners_2d]
        location = (int(min(x_coords)), int(min(y_coords)),
                    int(max(x_coords)), int(max(y_coords)))
        self._record_match_debug(ctx, template.name, location=location)
        return [location]

    def template_match(self, template: Element, scene_img, bool_debug: bool = True,
                       ctx: Optional[_MatchContext] = None) -> List:
        """模板匹配（TM_CCOEFF_NORMED + 掩码，忽略模板透明像素），支持多目标 + NMS 去重。

        Args:
            template(Element): 模板元素
            scene_img(np.ndarray): 场景图像（BGR）
            bool_debug(bool): 是否回报日志
            ctx(_MatchContext): 内部传递的帧上下文（外部调用无需传）

        Returns:
            List[Tuple[int, int, int, int]]：去重后的命中框（x1, y1, x2, y2）
        """
        ctx = self._ensure_ctx(ctx, bool_debug)
        template_img = template.gray
        mask = template.mask
        threshold = template.threshold

        # 1. 取本帧灰度图（按帧缓存：同一帧内所有元素共用一次转换）
        scene_gray = self._scene_gray(ctx, scene_img)
        scene_h, scene_w = scene_gray.shape

        # 2. ROI 裁剪（越界收敛，保证框合法）
        x, y = template.roi_x, template.roi_y
        roi_w, roi_h = template.roi_width, template.roi_height
        x_end = min(x + roi_w, scene_w)
        y_end = min(y + roi_h, scene_h)
        x_start = max(x, 0)
        y_start = max(y, 0)
        scene_gray_roi = scene_gray[y_start:y_end, x_start:x_end]

        # 3. 执行模板匹配（此时尺寸已合法）
        try:
            result = cv2.matchTemplate(
                image=scene_gray_roi,
                templ=template_img,
                method=cv2.TM_CCOEFF_NORMED,
                mask=mask,
            )
        except cv2.error as e:
            self.logger.error(f"[{template.name}] 模板匹配执行错误：{e}")
            return []

        # 4. 一次筛出候选：掩码匹配在边缘/平坦区会产生 NaN/±Inf，用 isfinite 与阈值一并排除
        #    （省掉 nan_to_num 的整块拷贝，也不再单独跑一次 minMaxLoc 全图扫描）
        finite = np.isfinite(result)
        locations = np.where(finite & (result >= threshold))
        if locations[0].size == 0:
            # 未命中：仅调试模式再取一次最大响应，便于排查"离阈值差多少"
            #（生产路径不付这次全图扫描的代价，也不留调试记录）
            if ctx.debug:
                finite_values = result[finite]
                self._record_match_debug(
                    ctx, template.name,
                    method="TEMPLATE",
                    max_val=float(finite_values.max()) if finite_values.size else -1.0,
                    roi=(x_start, y_start, x_end, y_end),
                    threshold=float(threshold),
                )
            return []

        # 5. 按置信度降序排序（命中框 = ROI 内坐标 + ROI 偏移）
        confidences = result[locations[0], locations[1]]
        tmpl_h, tmpl_w = template_img.shape[:2]
        matches_with_conf = [
            (float(conf), int(x + dx), int(y + dy), int(x + dx + tmpl_w), int(y + dy + tmpl_h))
            for dx, dy, conf in zip(locations[1], locations[0], confidences)
        ]
        matches_with_conf.sort(reverse=True, key=lambda item: item[0])

        if bool_debug:
            self.logger.debug(f"[{template.name}] 匹配结果统计：最大值={matches_with_conf[0][0]:.2f}")
        self._record_match_debug(
            ctx, template.name,
            method="TEMPLATE",
            max_val=matches_with_conf[0][0],
            roi=(x_start, y_start, x_end, y_end),
            threshold=float(threshold),
        )

        sorted_matches = [(x1, y1, x2, y2) for (_conf, x1, y1, x2, y2) in matches_with_conf]
        sorted_confidences = [conf for (conf, *_rest) in matches_with_conf]

        # 6. NMS 去重（保留置信度更高的框）
        keep_boxes = self._non_max_suppression(
            sorted_matches, iou_threshold=0.3, confidences=sorted_confidences)
        conf_map = dict(zip(sorted_matches, sorted_confidences))
        self._record_match_debug(
            ctx, template.name,
            kept_boxes=keep_boxes,
            kept_confidences=[conf_map.get(box) for box in keep_boxes],
            sorted_matches_len=len(sorted_matches),
        )
        return keep_boxes

    # ============================================================= 工具方法

    @staticmethod
    def _non_max_suppression(boxes: List[Tuple[int, int, int, int]],
                             iou_threshold: float = 0.3,
                             confidences: Optional[List[float]] = None) -> List[Tuple[int, int, int, int]]:
        """去除重叠度高的重复检测框（按置信度优先保留）。

        Args:
            boxes: 检测框列表 [(x1, y1, x2, y2), ...]
            iou_threshold: IOU 阈值（> 该值的框视为重复）
            confidences: 与 boxes 一一对应的置信度；缺省时按 y2 排序

        Returns:
            去重后的框列表
        """
        if not boxes:
            return []

        boxes_np = np.array(boxes, dtype=np.float32)
        x1, y1, x2, y2 = boxes_np[:, 0], boxes_np[:, 1], boxes_np[:, 2], boxes_np[:, 3]
        area = (x2 - x1 + 1) * (y2 - y1 + 1)

        # 关键：按置信度降序排序（无置信度时兼容旧逻辑，按 y2 升序取反）
        if confidences is not None:
            indices = np.argsort(np.array(confidences))[::-1]
        else:
            indices = np.argsort(y2)

        keep = []
        while indices.size > 0:
            idx = indices[0]              # 当前置信度最高的框
            keep.append(boxes[idx])
            indices = indices[1:]         # 移除当前框，处理剩余框

            xx1, yy1 = np.maximum(x1[idx], x1[indices]), np.maximum(y1[idx], y1[indices])
            xx2, yy2 = np.minimum(x2[idx], x2[indices]), np.minimum(y2[idx], y2[indices])
            w, h = np.maximum(0, xx2 - xx1 + 1), np.maximum(0, yy2 - yy1 + 1)
            overlap = (w * h) / (area[idx] + area[indices] - w * h)
            indices = indices[overlap <= iou_threshold]   # 只保留 IOU 小于阈值的框
        return keep

    def _rgb_average(self, img, mask=None):
        """计算图像在掩码有效区域内的 RGB 平均颜色。

        Args:
            img: BGR(A) 图像
            mask: 外部掩码（可选）；缺省时用 alpha 通道，无 alpha 则整图

        Returns:
            (r, g, b) 平均颜色元组；出错返回 None
        """
        try:
            channels = cv2.split(img)
            b, g, r = channels[0:3]      # OpenCV 默认 BGR(A)

            if mask is not None:
                final_mask = mask
            elif img.shape[2] == 4:
                _, final_mask = cv2.threshold(channels[3], 1, 255, cv2.THRESH_BINARY)
            else:
                final_mask = np.ones_like(b) * 255

            if final_mask.ndim > 2:      # 掩码必须是二值单通道
                final_mask = cv2.cvtColor(final_mask, cv2.COLOR_BGR2GRAY)

            masked_pixels = final_mask > 0
            return (int(np.mean(r[masked_pixels])),
                    int(np.mean(g[masked_pixels])),
                    int(np.mean(b[masked_pixels])))
        except Exception as e:
            self.logger.error(f"计算平均颜色时出错: {str(e)}")
            return None


if __name__ == "__main__":
    import sys

    logger = setup_logging()
    graph = SceneGraph(ResourceDBManager())

    # 图片目录路径（基于项目根目录，兼容中文路径）
    image_dir = get_real_path("test_scene")
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    image_files = [
        f for f in os.listdir(image_dir)
        if os.path.isfile(os.path.join(image_dir, f))
        and os.path.splitext(f)[1].lower() in image_extensions
    ]
    # 用法：
    #   python -m backend.core.legacy.Recognizer                       全量跑 test_scene
    #   python -m backend.core.legacy.Recognizer "场景A.png" "场景B.png"  只跑指定图片
    #   追加 --compare                                                  同时跑"裁剪模式"并对比一致性/耗时
    argv = sys.argv[1:]
    compare = "--compare" in argv
    names = [a for a in argv if not a.startswith("--")]
    if names:
        image_files = [a for a in names if a in image_files]

    # 全量模式：每张图新建识别器（无 hint、无历史）→ 与优化前的行为完全一致
    # 裁剪模式：复用同一识别器（内部保留上一帧命中场景作为 hint），模拟任务循环
    live_recognizer = Recognizer(graph)

    ok_count = mismatch_count = error_count = 0
    total_full = total_live = 0.0
    for img_file in sorted(image_files):
        scene_name = os.path.splitext(img_file)[0]
        img = cv_imread(os.path.join(image_dir, img_file))
        if img is None:
            error_count += 1
            print(f"[ERR] 无法读取图片: {img_file}", flush=True)
            continue

        try:
            start = time.perf_counter()
            full = Recognizer(graph).scene(img, False)
            full_time = time.perf_counter() - start
            full_name = full.name if isinstance(full, Scene) else full
            total_full += full_time

            live_name, live_time = full_name, 0.0
            if compare:
                start = time.perf_counter()
                live = live_recognizer.scene(img, False)
                live_time = time.perf_counter() - start
                live_name = live.name if isinstance(live, Scene) else live
                total_live += live_time
        except Exception as e:
            error_count += 1
            print(f"[ERR] 出错 - 图片: {img_file} | 错误: {str(e)}", flush=True)
            continue

        if live_name != scene_name:
            mismatch_count += 1
            print(
                f"[FAIL] 不一致 - 图片: {img_file} | 预期: {scene_name} | "
                f"实际: {live_name} | 全量: {full_name}({full_time:.2f}s) | "
                f"裁剪: {live_time:.2f}s", flush=True)
        elif compare and live_name != full_name:
            mismatch_count += 1
            print(
                f"[FAIL] 裁剪与全量结果不一致 - 图片: {img_file} | "
                f"全量: {full_name} | 裁剪: {live_name}", flush=True)
        else:
            ok_count += 1
            print(
                f"[OK] 一致 - 图片: {img_file} | 全量: {full_time:.2f}s"
                + (f" | 裁剪: {live_time:.2f}s" if compare else ""), flush=True)

    print("=" * 60)
    print(f"验证完成: 共 {len(image_files)} 张 | 一致 {ok_count} | "
          f"不一致 {mismatch_count} | 出错 {error_count}")
    print(f"全量耗时: {total_full:.2f}秒"
          + (f" | 裁剪耗时: {total_live:.2f}秒" if compare else ""))
    if compare:
        print(f"索引统计: {get_scene_index(graph).stats()}")

