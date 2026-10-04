# -*- coding: utf-8 -*-
"""单元素匹配诊断：解释"为什么这个标志元素会误匹配别人的底图"，并给出调整建议（只读）。

## 原理（先讲清机制，再看数字）
`element_match` 走的是 `cv2.matchTemplate(..., TM_CCOEFF_NORMED, mask=mask)`，其分数为

    R = Σ[(T-μT)·(I-μI)·M²] / sqrt( Σ[(T-μT)·M]² · Σ[(I-μI)·M]² )

- **先去均值再归一化**：只衡量"去掉亮度/对比度后的形状相关性"，跟绝对亮度、整体强弱无关。
  于是**低对比（σ 小）的模板**只要大致走向相似（比如一条亮带、一片渐变），就能拿到高分。
- **只统计掩码内像素**（`M` = alpha>0 的区域）：有效样本数 = 不透明像素数。样本越少，
  统计噪声越大，无关画面被"偶然刷高"的概率越大。
- **搜索位置数 = (ROI-模板+1)²**：每个位置都是一次"试验"，位置越多，出现偶然高分的概率越大
  （多重比较）。若 ROI 恰好等于模板大小（只有 1 个位置），就不是搜索空间问题，而是模板本身不独特。
- 阈值是"命中线"：0.8 表示相关系数 0.8。压线命中（0.806 vs 0.8）几乎必然来自上述某种
  "模板不独特/样本太少/位置太多"，而不是真的长得像。

## 输出
元素与模板画像（尺寸、掩码不透明占比、模板 σ/均值）→ 在指定底图上的命中位置与分数 →
该元素对**其它底图的误匹配天花板**（分布 + 建议阈值）→ 针对性调整建议（提高阈值/收紧 ROI/换图/换标志元素）。

## 运行
    # A) 单元素归因：为什么它会误匹配 + 该怎么改
    .venv\\Scripts\\python.exe -X utf8 test_scene\\_explain_flag_element_match.py \\
        --element 3568545a-6ddb-4185-abd0-066ccfe7a9cf --image X之要塞 --sample 60
    .venv\\Scripts\\python.exe -X utf8 test_scene\\_explain_flag_element_match.py \\
        --scene 冒险-修罗副本 --element-name 标志 --image X之要塞

    # B) 候选标志元素区分度排名：只给场景名即可（回答"该给这个场景加哪个标志"）
    .venv\\Scripts\\python.exe -X utf8 test_scene\\_explain_flag_element_match.py \\
        --scene 冒险-修罗副本 --sample 30 --top 10

    # C) 历史库 A/B 对比（先导出旧库到目录）
    git show <旧commit>:src/database.db > log\\hist_old\\database.db
    .venv\\Scripts\\python.exe -X utf8 test_scene\\_explain_flag_element_match.py \\
        --db-dir log\\hist_old --element <元素ID> --image <底图名>
"""
import glob
import logging
import os
import statistics
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import cv2
import numpy as np
from pathlib import Path

from backend.core.legacy.Recognizer import Recognizer
from backend.core.legacy.Scene.SceneGraph import SceneGraph
from backend.tools.resource_db import ResourceDBManager
from backend.utils import cv_imread

DEFAULT_SAMPLE = 60
FLAT_SIGMA_ALERT = 25.0          # 模板去均值后标准差低于此值 → 视为"低对比/不独特"
OPAQUE_RATIO_ALERT = 0.5         # 不透明像素占比低于此值 → 有效样本偏少
SEARCH_POSITION_ALERT = 30_000   # 搜索位置数超过此值 → ROI 相对模板过大
THRESHOLD_MARGIN = 0.03          # 建议阈值 = 他人底图最高分 + 该安全余量


def _parse_args():
    argv = sys.argv[1:]
    opts = {"element": None, "scene": None, "element_name": None,
            "image": None, "sample": DEFAULT_SAMPLE, "db_dir": None, "top": 0}
    for key in ("element", "scene", "element-name", "image", "sample", "db-dir", "top"):
        flag = f"--{key}"
        if flag in argv:
            idx = argv.index(flag)
            if idx + 1 < len(argv):
                value = argv[idx + 1]
                opts[key.replace("-", "_")] = int(value) if key in ("sample", "top") else value
    return opts


def _find_element(graph, opts):
    """按元素 ID 或 场景名+元素名 定位标志元素"""
    for scene in graph.scenes.values():
        for element in scene.elements:
            if opts["element"] and element.id == opts["element"]:
                return scene, element
            if (opts["scene"] and opts["element_name"]
                    and scene.name == opts["scene"] and element.name == opts["element_name"]):
                return scene, element
    return None, None


def _template_profile(element):
    """模板画像：掩码不透明占比、有效像素上的均值/标准差"""
    gray = element.gray
    mask = (element.mask > 0)
    values = gray[mask]
    sigma = float(values.std()) if values.size else 0.0
    return {
        "shape": (int(gray.shape[1]), int(gray.shape[0])),       # (w, h)
        "opaque_ratio": float(mask.mean()) if mask.size else 0.0,
        "valid_pixels": int(values.size),
        "mean": float(values.mean()) if values.size else 0.0,
        "sigma": sigma,
    }


def _search_positions(element):
    """搜索位置数 = (ROI宽-模板宽+1) × (ROI高-模板高+1)"""
    tmpl_h, tmpl_w = element.gray.shape[:2]
    return (max(element.roi_width - tmpl_w + 1, 0) * max(element.roi_height - tmpl_h + 1, 0))


def _match_score(element, img):
    """直接用 OpenCV 复算一次匹配：返回 (最高 NCC, 命中框)"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.uint8)
    x, y = element.roi_x, element.roi_y
    roi = gray[max(y, 0):max(y, 0) + element.roi_height,
               max(x, 0):max(x, 0) + element.roi_width]
    if roi.size == 0 or roi.shape[0] < element.gray.shape[0] or roi.shape[1] < element.gray.shape[1]:
        return None, None
    result = cv2.matchTemplate(roi, element.gray, cv2.TM_CCOEFF_NORMED, mask=element.mask)
    finite = np.isfinite(result)
    if not finite.any():
        return None, None
    _, max_val, _, max_loc = cv2.minMaxLoc(np.where(finite, result, -1.0))
    tmpl_h, tmpl_w = element.gray.shape[:2]
    box = (x + max_loc[0], y + max_loc[1], x + max_loc[0] + tmpl_w, y + max_loc[1] + tmpl_h)
    return float(max_val), box


def _base_images(exclude_names=()):
    """test_scene 下的底图 {场景名: 路径}（排除指定名字）"""
    images = {}
    for path in sorted(glob.glob(os.path.join(_PROJECT_ROOT, "test_scene", "*.png"))):
        name = os.path.splitext(os.path.basename(path))[0]
        if name not in exclude_names:
            images[name] = path
    return images


def _sample(images, limit):
    """均匀抽样 limit 张"""
    keys = sorted(images)
    if limit <= 0 or limit >= len(keys):
        return keys
    step = max(1, len(keys) // limit)
    return keys[::step][:limit]


def _foreign_ceiling(element, images, limit):
    """该元素对"他人底图"的误匹配分：[(底图名, 分数, 是否越过阈值), ...]（降序）"""
    rows = []
    for name in _sample(images, limit):
        img = cv_imread(images[name])
        if img is None:
            continue
        score, _box = _match_score(element, img)
        if score is not None:
            rows.append((name, score, score >= element.threshold))
    rows.sort(key=lambda row: -row[1])
    return rows


def _advice(element, profile, positions, own_score, ceiling, alternatives):
    """基于真实数字给出针对性建议"""
    lines = []
    top = ceiling[0] if ceiling else (None, 0.0, False)
    if ceiling:
        suggested = min(0.99, round(top[1] + THRESHOLD_MARGIN, 2))
        if own_score is not None and suggested >= own_score - 0.02:
            safe = max(0.0, round(own_score - 0.05, 2))
            lines.append(f"① 只提阈值不够：他人底图最高 {top[1]:.3f} 已逼近自己底图 {own_score:.3f}，"
                         f"阈值最多提到 {safe} → 建议同时改模板（见 ②/③）")
        else:
            lines.append(f"① 提高阈值：当前 {element.threshold} → 建议 ≥ {suggested}"
                         f"（他人底图最高 {top[1]:.3f}「{top[0]}」"
                         + (f"，自己底图 {own_score:.3f}" if own_score is not None else "") + "）")
    if profile["sigma"] < FLAT_SIGMA_ALERT:
        lines.append(f"② 模板对比度低（有效像素 σ={profile['sigma']:.1f} < {FLAT_SIGMA_ALERT:.0f}）："
                     f"去均值归一化后这类模板极易被无关画面刷高分 → 换一张细节更多、更独特的元素图")
    if profile["opaque_ratio"] < OPAQUE_RATIO_ALERT:
        lines.append(f"③ 不透明像素占比仅 {profile['opaque_ratio'] * 100:.0f}%"
                     f"（有效像素 {profile['valid_pixels']}）：参与比较的样本太少、分数不稳 → "
                     f"重新框选图片，让标志内容占满框、少留透明边")
    if positions > SEARCH_POSITION_ALERT:
        lines.append(f"④ ROI 相对模板过大（搜索位置 {positions:,} 个）：位置越多越容易偶发高分 → "
                     f"把 ROI 收紧到标志实际出现的小范围")
    elif positions <= 1:
        lines.append(f"④ ROI ≈ 模板大小（搜索位置 {positions}）：不存在搜索空间过大的问题，"
                     f"误匹配来自模板本身不够独特 → 走 ②/③ 或换标志元素")
    if alternatives:
        names = "、".join(f"{name}(阈值{thr})" for name, thr in alternatives[:5])
        lines.append(f"⑤ 换/加一个更有区分度的标志元素：该场景其它元素 → {names}")
    hit_rate = sum(1 for _n, _s, over in ceiling if over)
    if hit_rate:
        lines.append(f"※ 抽样 {len(ceiling)} 张他人底图中已有 {hit_rate} 张越过当前阈值")
    return lines


def _rank_candidates(scene, images, sample, top_n):
    """评估该场景所有 IMG 元素的"区分度"：自己底图分 vs 他人底图最高分。

    判定一个元素能否胜任标志：既要能命中自己底图（自己分高），又要不会命中别人
    （他人底图最高分低）——即需要存在安全阈值区间 [他人最高+0.05, 自己分-0.05]。
    """
    own_path = os.path.join(_PROJECT_ROOT, "test_scene", f"{scene.name}.png")
    own_img = cv_imread(own_path) if os.path.exists(own_path) else None
    rows = []
    for element in scene.elements:
        gray = getattr(element, "gray", None)
        if gray is None or gray.size == 0:
            continue                       # 只评估 IMG 元素
        profile = _template_profile(element)
        positions = _search_positions(element)
        own = None
        if own_img is not None:
            own, _box = _match_score(element, own_img)
        ceiling = _foreign_ceiling(element, images, sample)
        foreign_max = ceiling[0][1] if ceiling else 0.0
        rows.append({
            "element": element,
            "profile": profile,
            "positions": positions,
            "own": own,
            "foreign_max": foreign_max,
            "foreign_top": ceiling[0][0] if ceiling else None,
        })
    # 区分度优先：他人最高分越低越好；同等再看自己分是否稳（以免自己都命中不了）
    rows.sort(key=lambda r: (r["foreign_max"], -(r["own"] or 0.0)))
    return rows[:top_n] if top_n > 0 else rows


def _print_ranking(scene, rows, sample):
    """打印候选标志元素排名 + 可用性判定 + 推荐阈值"""
    print(f"\n=== 场景《{scene.name}》候选标志元素区分度排名"
          f"（对 {sample} 张他人底图抽样）===")
    print(f"  {'元素':<16}{'标志':<6}{'有效像素':<10}{'模板σ':<8}{'位置数':<10}"
          f"{'自己分':<8}{'他人最高':<10}{'余量':<9}判定")
    usable = []
    for row in rows:
        element = row["element"]
        own = row["own"]
        foreign_max = row["foreign_max"]
        margin = (own - foreign_max) if own is not None else None
        if own is None:
            verdict, rec = "✘ 自己底图无法命中（ROI/图片需修）", None
        elif foreign_max + 0.05 <= own - 0.05:
            # 推荐阈值：能沿用默认 0.8 就沿用，否则取安全区间下沿
            rec = 0.8 if foreign_max + 0.05 <= 0.8 <= own - 0.05 else round(foreign_max + 0.05, 2)
            verdict = "✔ 可用作标志"
            usable.append((element.name, rec, own, foreign_max))
        else:
            rec = None
            verdict = "✘ 区分度不足"
        print(f"  {element.name[:14]:<16}{'是' if element.symbol else '否':<6}"
              f"{row['profile']['valid_pixels']:<10}{row['profile']['sigma']:<8.1f}"
              f"{row['positions']:<10}{'—' if own is None else f'{own:.3f}':<8}"
              f"{foreign_max:<10.3f}{'—' if margin is None else f'{margin:+.3f}':<9}{verdict}"
              + (f"（阈值建议 {rec}）" if rec is not None else ""))

    print("\n--- 结论 ---")
    if usable:
        best = usable[0]
        print(f"  最优选：给《{scene.name}》加/改用《{best[0]}》作为标志元素"
              f"（阈值 {best[1]}；自己底图 {best[2]:.3f}，他人最高 {best[3]:.3f}）")
        print("  两个及以上标志元素是 AND 关系（全部命中才算场景命中）→ 可显著降低误命中")
        print(f"  操作：/resource-scene/{scene.id} → 新增/选中该元素 → 勾选「标志」→ 设阈值 → 保存")
    else:
        print("  该场景没有元素能满足『自己命中 & 不命中他人』→ 建议改用父子/同屏机制，"
              "或提高现有标志的阈值并接受一定的漏判风险")
    print("  复核：加完后跑 _check_scene_flag_overlap.py --scene <场景名> 与 "
          "verify_recognizer_pruning.py，确认误命中消失且不漏判")


def main():
    logging.basicConfig(level=logging.CRITICAL)
    opts = _parse_args()
    # 注：ResourceDBManager 是进程内单例，首次构造决定库路径 → 必须在任何其它取库之前指定
    db_dir = Path(opts["db_dir"]) if opts["db_dir"] else None
    graph = SceneGraph(ResourceDBManager(db_dir))
    scene, element = _find_element(graph, opts)
    if element is None:
        # 只给了场景名 → 输出"候选标志元素区分度排名"（回答：该给这个场景加哪个标志）
        target_scene = graph.scenes.get(opts["scene"]) if opts["scene"] else None
        if target_scene is not None:
            sample = int(opts["sample"] or DEFAULT_SAMPLE)
            images = _base_images(exclude_names=(target_scene.name,))
            rows = _rank_candidates(target_scene, images, sample, int(opts["top"] or 0))
            _print_ranking(target_scene, rows, sample)
            return 0
        print("未找到元素/场景：请用 --element <元素ID>，或 --scene <场景名> [--element-name <元素名>]")
        return 1

    profile = _template_profile(element)
    positions = _search_positions(element)
    print(f"=== 元素匹配诊断：《{scene.name}》/《{element.name}》 ===")
    print(f"  类型={getattr(element.type, 'name', element.type)}  "
          f"匹配方式={getattr(element.match_type, 'name', element.match_type)}  "
          f"阈值={element.threshold}  标志={element.symbol}")
    print(f"  模板尺寸 {profile['shape'][0]}×{profile['shape'][1]}  "
          f"不透明像素占比 {profile['opaque_ratio'] * 100:.1f}%（有效像素 {profile['valid_pixels']}）")
    print(f"  模板统计（仅有效像素）：均值 {profile['mean']:.1f}  标准差 σ {profile['sigma']:.1f}")
    print(f"  ROI = ({element.roi_x},{element.roi_y}) {element.roi_width}×{element.roi_height}"
          f" → 搜索位置 {positions:,} 个")
    print(f"  修复入口: /resource-scene/{scene.id}   元素ID={element.id}  场景ID={scene.id}")

    own_path = os.path.join(_PROJECT_ROOT, "test_scene", f"{scene.name}.png")
    own_score = None
    if os.path.exists(own_path):
        own_score, own_box = _match_score(element, cv_imread(own_path))
        print(f"\n--- 自己的底图（{scene.name}.png）---")
        if own_score is None:
            print("  该底图在此 ROI 下无法匹配（ROI 越界或尺寸不足）")
        else:
            print(f"  最高分 = {round(own_score, 3)}  命中框 {own_box}"
                  f"  与阈值 {element.threshold} 的余量 {round(own_score - element.threshold, 3)}")

    target = opts["image"]
    if target:
        target_path = os.path.join(_PROJECT_ROOT, "test_scene", f"{target}.png")
        if not os.path.exists(target_path):
            print(f"\n[跳过] 找不到底图 {target_path}")
        else:
            score, box = _match_score(element, cv_imread(target_path))
            verdict = "越过阈值 → 会误命中" if (score or 0) >= element.threshold else "未越过阈值"
            print(f"\n--- 在『{target}』底图上的匹配 ---")
            print(f"  最高分 = {round(score, 3) if score is not None else None}"
                  f"（阈值 {element.threshold}，{verdict}）  命中框 {box}")
            print("  机制：TM_CCOEFF_NORMED 先去均值再归一化，分数只反映『形状相关性』；"
                  "低对比模板 / 有效像素少 / 搜索位置多，都会把它抬到阈值以上")

    images = _base_images(exclude_names=(scene.name,))
    ceiling = _foreign_ceiling(element, images, int(opts["sample"] or DEFAULT_SAMPLE))
    if ceiling:
        scores = [score for _n, score, _over in ceiling]
        over = [row for row in ceiling if row[2]]
        print(f"\n--- 该元素对他人底图的『误匹配天花板』（抽样 {len(ceiling)} 张）---")
        print(f"  中位 {statistics.median(scores):.3f}  "
              f"90 分位 {sorted(scores)[int(len(scores) * 0.9)]:.3f}  最高 {scores[0]:.3f}「{ceiling[0][0]}」")
        print(f"  越过当前阈值的底图数：{len(over)}"
              + (f" → {[name for name, _s, _o in over[:8]]}" if over else ""))

    alternatives = [(e.name, e.threshold) for e in scene.elements if e.symbol and e is not element]
    print("\n--- 针对性调整建议 ---")
    for line in _advice(element, profile, positions, own_score, ceiling, alternatives):
        print(f"  {line}")
    if not ceiling:
        print("  （未取得他人底图样本，建议加大 --sample）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
