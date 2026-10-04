# -*- coding: utf-8 -*-
"""场景标志元素重叠体检（只读诊断，用于定位"一图多匹配"要收紧哪个元素）。

## 背景
`Recognizer` 报出的场景由"哪个匹配场景先被检查到"决定：
全量扫描按**数据库顺序**，裁剪扫描按**候选集顺序**。若同一张截图能被多个场景的**标志元素**
同时匹配（库中标志元素重叠），两种规则就可能给出不同场景——两者其实都能匹配截图，
属于**数据层面歧义**（不是识别逻辑错误）。

## 这个脚本给你什么
逐张底图列出：全量仲裁结果 + 额外也能匹配的场景 + **具体是哪个标志元素**匹配的
（元素名 / 相似度 max_val / 阈值 / 元素 ID / 场景 ID）+ 修复入口（资源管理器页面路径）。

顺带做一次"标志元素搜索空间"体检：ROI 远大于模板（(ROI-模板+1)² 位置数过大）的元素
会让单次匹配暴涨（曾出现 230×60 模板配 1600×900 全屏 ROI → 单次 133ms）。

## 查看 / 修复入口
- 前端「资源管理器」页 `/resourcemanager`：场景树 → 元素表格（`标志` 列 = 标志元素）。
- 前端「场景编辑器」页 `/resource-scene/<场景ID>`：元素列表右上角红色「标志」角标，
  选中即可改 ROI / 阈值 / 图片；也可取消 `标志` 勾选（该元素便不再参与场景判定）。
- 后端 API：`POST /api/resource/elements/{元素ID}/match`（底图上单独验证该元素）、
  `POST /api/resource/scenes/{场景ID}/match`（底图整体识别）。

## 运行
    .venv\\Scripts\\python.exe -X utf8 test_scene\\_check_scene_flag_overlap.py            # 抽样 12 张
    .venv\\Scripts\\python.exe -X utf8 test_scene\\_check_scene_flag_overlap.py --limit 30
    .venv\\Scripts\\python.exe -X utf8 test_scene\\_check_scene_flag_overlap.py --all      # 全量（~2 分钟）
    .venv\\Scripts\\python.exe -X utf8 test_scene\\_check_scene_flag_overlap.py --scene X之要塞
"""
import glob
import logging
import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)
try:                                     # 控制台输出统一 UTF-8（Windows 默认 GBK 会崩）
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from backend.core.legacy.Recognizer import Recognizer
from backend.core.legacy.Scene.SceneGraph import SceneGraph
from backend.core.legacy.Scene.SceneMeta import COINCIDENT_SCENES, POPUP_SCENES
from backend.tools.resource_db import ResourceDBManager
from backend.utils import cv_imread

DEFAULT_LIMIT = 12
# 搜索位置数 = (ROI宽-模板宽+1) × (ROI高-模板高+1)：超过该值说明 ROI 相对模板过大，值得收紧
SEARCH_POSITION_ALERT = 300_000


def _parse_args():
    """解析 --limit N / --all / --scene 名字"""
    argv = sys.argv[1:]
    limit = DEFAULT_LIMIT
    scene_filter = None
    if "--all" in argv:
        limit = 0
    if "--limit" in argv:
        idx = argv.index("--limit")
        if idx + 1 < len(argv):
            limit = int(argv[idx + 1])
    if "--scene" in argv:
        idx = argv.index("--scene")
        if idx + 1 < len(argv):
            scene_filter = argv[idx + 1]
    return limit, scene_filter


def _images(limit: int, scene_filter: str | None):
    """底图列表（可选按场景名过滤；limit<=0 表示全量）"""
    files = sorted(glob.glob(os.path.join(_PROJECT_ROOT, "test_scene", "*.png")))
    if scene_filter:
        files = [f for f in files if os.path.splitext(os.path.basename(f))[0] == scene_filter]
    if 0 < limit < len(files):
        step = max(1, len(files) // limit)
        files = files[::step][:limit]
    return files


def _matching_scenes(recognizer: Recognizer, img):
    """数据库顺序返回所有"标志元素匹配该截图"的场景"""
    matched = []
    for scene in recognizer.scene_graph.scenes.values():
        if not scene.elements:
            continue
        if recognizer.scene_match(img, scene, False):
            matched.append(scene)
    return matched


def _matched_flag_elements(recognizer: Recognizer, img, scene):
    """该场景里命中的标志元素明细：[(元素, 命中数, 相似度 max_val, 阈值)]"""
    hits = []
    for element in scene.elements:
        if not element.symbol:
            continue
        matches = recognizer.element_match(img, element, False)
        if not matches:
            continue
        record = recognizer._debug_match_records.get(element.name) or {}
        hits.append((element, len(matches), record.get("max_val"), element.threshold))
    return hits


def _relation(a: str, b: str, popup_set) -> str:
    """判断两个场景重叠的性质（决定要不要去收紧元素）"""
    if a in popup_set and b in popup_set:
        return "弹窗重叠（仲裁靠弹窗顺序，建议收敛）"
    if (a in popup_set) != (b in popup_set):
        return "弹窗↔场景（弹窗优先检查，通常无害）"
    for parent, children in COINCIDENT_SCENES.items():
        if (a == parent and b in children) or (b == parent and a in children):
            return "父子/同屏（正常，靠同屏表下沉）"
    return "★ 独立场景重叠（建议收紧该元素）"


def _report_overlap(images, graph, popup_scenes):
    """逐图报告重叠；返回 (重叠底图数, {(场景名, 元素名): (性质, [他人底图名...])})"""
    recognizer = Recognizer(graph)
    popup_set = set(popup_scenes)
    overlap_images = 0
    aggregated = {}

    for path in images:
        name = os.path.splitext(os.path.basename(path))[0]
        img = cv_imread(path)
        if img is None:
            print(f"[跳过] 无法读取 {path}")
            continue

        # 一次全量扫描收集所有匹配场景（与 scene() 的判定一致：弹窗优先 → DB 顺序）
        matched = _matching_scenes(recognizer, img)
        if len(matched) <= 1:
            continue
        overlap_images += 1

        matched_names = {scene.name for scene in matched}
        popup_seed = next((p for p in popup_scenes if p in matched_names), None)
        if popup_seed:
            seed, kind = popup_seed, "弹窗优先"
        else:
            seed, kind = matched[0].name, "DB 顺序"
        # 复用识别器的同屏子场景下沉，得到与 scene() 相同的最终结果（不再重复全量扫描）
        final = recognizer._check_sub_scenes(img, seed, False, is_popup=bool(popup_seed))
        final_name = getattr(final, "name", final)

        print(f"\n底图: {name}.png")
        print(f"  全量仲裁结果: {final_name}（{kind}：{seed}）")
        for scene in matched:
            if scene.name == seed:
                continue
            relation = _relation(seed, scene.name, popup_set)
            for element, count, max_val, threshold in _matched_flag_elements(recognizer, img, scene):
                score = f"{max_val:.3f}" if isinstance(max_val, float) else "n/a"
                print(f"  额外匹配: 场景《{scene.name}》元素《{element.name}》"
                      f" 相似度={score} 阈值={threshold} 命中框={count}  [{relation}]")
                print(f"      元素ID={element.id}  场景ID={scene.id}")
                print(f"      修复入口: /resource-scene/{scene.id}"
                      f"（改该元素 ROI/阈值/图片，或取消勾选『标志』）")
                key = (scene.name, element.name)
                if key in aggregated:
                    aggregated[key][1].append(name)
                else:
                    aggregated[key] = (relation, [name])
    return overlap_images, aggregated


def _report_search_space(graph):
    """标志元素搜索空间体检：ROI 远大于模板 → 单次匹配耗时暴涨（曾出现 133ms/次）"""
    alerts = []
    for scene in graph.scenes.values():
        for element in scene.elements:
            if not element.symbol:
                continue
            gray = getattr(element, "gray", None)
            if gray is None or gray.size == 0:
                continue
            tmpl_h, tmpl_w = gray.shape[:2]
            positions = (max(element.roi_width - tmpl_w + 1, 0)
                         * max(element.roi_height - tmpl_h + 1, 0))
            if positions > SEARCH_POSITION_ALERT:
                alerts.append((positions, scene, element, tmpl_w, tmpl_h))
    alerts.sort(reverse=True, key=lambda item: item[0])

    print(f"\n=== 标志元素搜索空间体检（位置数 > {SEARCH_POSITION_ALERT:,} 建议收紧 ROI）===")
    if not alerts:
        print("  未发现：所有标志元素的 ROI 与模板尺寸相称")
    for positions, scene, element, tmpl_w, tmpl_h in alerts:
        print(f"  {positions:>12,} 位置 | 场景《{scene.name}》元素《{element.name}》"
              f" 模板 {tmpl_w}×{tmpl_h} ROI {element.roi_width}×{element.roi_height}"
              f" @({element.roi_x},{element.roi_y})")
        print(f"      修复入口: /resource-scene/{scene.id}")
    return alerts


def main():
    logging.basicConfig(level=logging.CRITICAL)
    limit, scene_filter = _parse_args()
    graph = SceneGraph(ResourceDBManager())
    images = _images(limit, scene_filter)
    if not images:
        print("未找到底图（test_scene/*.png），可用 --scene <场景名> 指定单张")
        return 1

    print(f"=== 标志元素重叠体检：{len(images)} 张底图（场景库共 {len(graph.scenes)} 个场景）===")
    overlap, aggregated = _report_overlap(images, graph, POPUP_SCENES)

    print(f"\n=== 汇总：{overlap}/{len(images)} 张底图存在『一图多匹配』 ===")
    if not aggregated:
        print("  无重叠：每张底图只有唯一场景的（非弹窗）标志元素匹配")

    # ★ 独立场景重叠排在最前（只有这类才需要去收紧元素）
    def _sort_key(item):
        (scene_name, _element_name), (relation, owners) = item
        return (0 if relation.startswith("★") else 1, -len(set(owners)), scene_name)

    for (scene_name, element_name), (relation, owners) in sorted(aggregated.items(), key=_sort_key):
        unique = sorted(set(owners))
        shown = "、".join(unique[:6]) + (" …" if len(unique) > 6 else "")
        print(f"  《{scene_name}》/《{element_name}》 额外匹配 {len(unique)} 张他人底图"
              f" [{relation}]: {shown}")

    _report_search_space(graph)

    print("\n说明：额外匹配≠错误。父子/弹层场景共用标志元素属正常（识别链会按同屏共存表下沉）；"
          "\n只有互相独立的场景之间重叠，才会让『候选集顺序』与『DB 顺序』给出不同场景，才需要收紧。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
