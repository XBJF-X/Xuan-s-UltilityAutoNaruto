# -*- coding: utf-8 -*-
"""场景识别「按转移图裁剪候选集」验证 + 全量识别一致性回归（v0.17.39）。

背景：`Recognizer.scene()` 原先每帧全量遍历 193 个场景。实测（2026-09-12，1600×900）：
最坏帧 0.64s / 193 次 `scene_match`，14 张真实底图均值 ≈0.18s，单次匹配 ≈3.4ms。
优化：只匹配「当前场景的入/出边邻居 + 弹窗」，未命中则**全量兜底**（保证不漏判）
并把真实跳转记为运行时学习边（下次不再付全量代价）。

覆盖：
1. `SceneIndex`：可用性/统计、候选集内容（hint 自身 + 入/出边邻居 + 同屏子场景，
   不含弹窗）、未知 hint 返回 None（调用方走全量）
2. 全量 vs 裁剪**逐图识别结果一致**（默认抽样 6 张；`--full` 跑全部底图）
3. hint ≠ 真实场景（邻居 / 远端 / 不存在）时结果仍一致（依赖全量兜底）
4. 学习边：远端 hint 兜底命中后写入学习边，第二次同 hint 由 Tier-1 命中
5. 性能：同场景帧的 `scene_match` 次数显著低于全量帧
6. 接线：BaseTask 传 hint、资源管理器改场景/边后失效索引、元数据与旧内联数据一致

运行（必须用项目虚拟环境）：
    .venv\\Scripts\\python.exe -X utf8 test_scene\\verify_recognizer_pruning.py
    .venv\\Scripts\\python.exe -X utf8 test_scene\\verify_recognizer_pruning.py --full
    .venv\\Scripts\\python.exe -X utf8 test_scene\\verify_recognizer_pruning.py --limit 3
"""
import glob
import logging
import os
import sys
import time
import unittest

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.core.legacy.Recognizer import Recognizer
from backend.core.legacy.Scene.SceneGraph import SceneGraph
from backend.core.legacy.Scene.SceneIndex import get_scene_index, scene_candidates
from backend.core.legacy.Scene.SceneMeta import (
    COINCIDENT_SCENES,
    POPUP_SCENES,
    UNKNOWN_SCENES,
)
from backend.tools.resource_db import ResourceDBManager
from backend.utils import cv_imread

DEFAULT_SAMPLE = 6
# 实时链模拟：每个场景连续跑 N 帧（1 帧切换 + N 帧停留），贴近任务循环里
# "切场景后要盯同一画面若干帧"的真实比例
STEADY_FRAMES_PER_SCENE = 4

_graph_cache = {}


def _graph() -> SceneGraph:
    """进程内共享的 SceneGraph（构建一次 ~1.5s，避免每个用例重复解码元素图）"""
    if "graph" not in _graph_cache:
        _graph_cache["graph"] = SceneGraph(ResourceDBManager())
    return _graph_cache["graph"]


def _test_images(limit: int) -> list:
    """test_scene 下的底图列表（按文件名排序，均匀抽样 limit 张）"""
    files = sorted(glob.glob(os.path.join(_PROJECT_ROOT, "test_scene", "*.png")))
    if limit <= 0 or limit >= len(files):
        return files
    step = max(1, len(files) // limit)
    return files[::step][:limit]


def _parse_args():
    """解析 --full / --limit N / XUAN_REGRESS_LIMIT，并从 sys.argv 移除自定义参数"""
    limit = DEFAULT_SAMPLE
    raw = list(sys.argv[1:])
    if "--full" in raw:
        limit = 0
    elif "--limit" in raw:
        idx = raw.index("--limit")
        if idx + 1 < len(raw):
            limit = int(raw[idx + 1])
    env = os.environ.get("XUAN_REGRESS_LIMIT")
    if env:
        limit = int(env)

    # unittest.main() 会解析 sys.argv，未知参数会直接报错 → 先摘掉自定义参数
    cleaned, skip_next = [sys.argv[0]], False
    for arg in raw:
        if skip_next:
            skip_next = False
            continue
        if arg == "--full":
            continue
        if arg == "--limit":
            skip_next = True
            continue
        cleaned.append(arg)
    sys.argv = cleaned
    return limit


_LIMIT = _parse_args()


def _name(result) -> str:
    """识别结果归一为场景名/未知标记"""
    return getattr(result, "name", None) or str(result)


def _scan_once(recognizer: Recognizer, img, hint=None, allow_full_scan=True):
    """执行一次识别并统计 scene_match 调用次数（含弹窗与子场景下沉）"""
    counter = {"n": 0}
    original = recognizer.scene_match

    def counting_scene_match(*args, **kwargs):
        counter["n"] += 1
        return original(*args, **kwargs)

    recognizer.scene_match = counting_scene_match
    try:
        start = time.perf_counter()
        result = recognizer.scene(img, bool_debug=False, hint=hint,
                                  allow_full_scan=allow_full_scan)
        elapsed = time.perf_counter() - start
    finally:
        recognizer.scene_match = original
    return result, counter["n"], elapsed


class SceneIndexTest(unittest.TestCase):
    """候选集索引本身（不识别图片）"""

    @classmethod
    def setUpClass(cls):
        cls.graph = _graph()
        cls.index = get_scene_index(cls.graph)

    def test_available_and_stats(self):
        stats = self.index.stats()
        self.assertTrue(stats["available"], f"索引不可用: {stats['unavailable_reason']}")
        self.assertGreaterEqual(stats["scene_count"], 190)
        self.assertGreaterEqual(stats["out_edge_count"], 300)
        self.assertEqual(stats["popup_count"], len(POPUP_SCENES))

    def test_candidates_hint_first_and_exclude_popups(self):
        cands = self.index.candidates("主场景")   # 入/出边最多的枢纽场景
        self.assertIsNotNone(cands)
        self.assertEqual(cands[0], "主场景", "hint 自身必须排在最前（同场景帧 1 次匹配即命中）")
        self.assertFalse(set(cands) & set(POPUP_SCENES), "候选集不含弹窗（弹窗单独优先匹配）")
        self.assertLess(len(cands), len(self.graph.scenes), "候选集必须小于全量场景数")
        for name in self.index.neighbors("主场景"):
            self.assertIn(name, cands)

    def test_candidates_none_when_no_hint_or_unknown(self):
        self.assertIsNone(self.index.candidates(None))
        self.assertIsNone(self.index.candidates(""))
        self.assertIsNone(self.index.candidates("不存在的场景"))
        self.assertIsNone(scene_candidates(self.graph, "不存在的场景"))

    def test_edge_neighbors_bidirectional(self):
        edges = self.graph._resource_db.get_all_scene_edges()
        self.assertTrue(edges, "数据库无场景边")
        edge = edges[0]
        source, target = edge.source_scene.name, edge.target_scene.name
        self.assertIn(target, self.index.candidates(source), "出边邻居必须在候选集内")
        self.assertIn(source, self.index.candidates(target), "入边邻居必须在候选集内")

    def test_meta_matches_recognizer_instance(self):
        recognizer = Recognizer(self.graph)
        self.assertEqual(tuple(recognizer.popup_scenes), tuple(POPUP_SCENES))
        self.assertEqual(recognizer.coincident_scenes, COINCIDENT_SCENES)
        # 迁移自内联数据的关键项（防止漏项/串项）
        self.assertIn("聊天", POPUP_SCENES)
        self.assertIn("主场景-装备", COINCIDENT_SCENES["主场景"])
        self.assertEqual(COINCIDENT_SCENES["商城"], ())
        self.assertGreaterEqual(len(COINCIDENT_SCENES), 30)
        self.assertEqual(tuple(UNKNOWN_SCENES), ("未知场景", "未知含X场景"))


class RecognitionConsistencyTest(unittest.TestCase):
    """全量 vs 裁剪：逐图结果必须一致（不漏判、不误判）"""

    @classmethod
    def setUpClass(cls):
        cls.limit = _LIMIT
        cls.graph = _graph()
        cls.index = get_scene_index(cls.graph)
        cls.images = {}          # 图名 -> ndarray
        for path in _test_images(cls.limit):
            img = cv_imread(path)
            if img is not None:
                cls.images[os.path.splitext(os.path.basename(path))[0]] = img

        cls.full_results, cls.steady_results, cls.live_results = {}, {}, {}
        cls.live_first_results = {}                      # 实时链首帧（切换帧）结果
        cls.scan_counts, cls.time_cost = {}, {}          # 稳态：全量 vs 裁剪 匹配次数/耗时
        cls.live_counts, cls.live_time = {}, {}          # 实时链：连续帧（hint=上一帧结果）

        for name, img in cls.images.items():
            # 基线：每张图用新建识别器（无 hint、无历史）→ 与优化前行为一致
            result, count, elapsed = _scan_once(Recognizer(cls.graph), img)
            cls.full_results[name] = _name(result)
            cls.scan_counts[name] = [count, 0]
            cls.time_cost[name] = [elapsed, 0.0]

            # 稳态：hint = 本底图场景名且与自身状态一致（可信）→ 走 Tier-1 候选集
            recognizer = Recognizer(cls.graph)
            recognizer._last_matched_scene = name
            result, count, elapsed = _scan_once(recognizer, img, hint=name)
            cls.steady_results[name] = _name(result)
            cls.scan_counts[name][1] = count
            cls.time_cost[name][1] = elapsed

        # 实时链：单个识别器连续处理；每个场景按真实循环模式跑 1+N 帧
        # （第 1 帧=刚跳到该场景，其后 N 帧=停留），hint 始终是上一帧识别结果
        live = Recognizer(cls.graph)
        hint = None
        for name, img in cls.images.items():
            frames = 0
            count_sum = 0
            time_sum = 0.0
            for _ in range(1 + STEADY_FRAMES_PER_SCENE):
                result, count, elapsed = _scan_once(live, img, hint=hint)
                if frames == 0:
                    cls.live_first_results[name] = _name(result)
                hint = _name(result)
                count_sum += count
                time_sum += elapsed
                frames += 1
            cls.live_results[name] = hint
            cls.live_counts[name] = count_sum
            cls.live_time[name] = time_sum

    def test_pruned_equals_full_scan(self):
        """逐图：裁剪（稳态 / 实时链首帧 / 实时链稳态）识别结果 == 全量扫描结果"""
        self.assertTrue(self.images, "test_scene 下没有可用底图")
        for name, full_name in self.full_results.items():
            with self.subTest(image=name, mode="steady"):
                self.assertEqual(self.steady_results.get(name), full_name)
            with self.subTest(image=name, mode="live_first_frame"):
                self.assertEqual(self.live_first_results.get(name), full_name)
            with self.subTest(image=name, mode="live"):
                self.assertEqual(self.live_results.get(name), full_name)

    def test_pruned_matches_file_name(self):
        """回归基线：全量结果应与底图文件名（= 场景名或未知标记）一致"""
        for name, full_name in self.full_results.items():
            with self.subTest(image=name):
                self.assertEqual(full_name, name,
                                 "全量扫描结果与文件名不一致（数据问题：底图/ROI/阈值需修）")

    def test_pruning_reduces_match_count(self):
        """性能：稳态裁剪的匹配次数显著低于全量，且至少一张图 < 1/3；实时链不劣于全量"""
        full_total = sum(v[0] for v in self.scan_counts.values())
        steady_total = sum(v[1] for v in self.scan_counts.values())
        live_total = sum(self.live_counts.values())
        full_time = sum(v[0] for v in self.time_cost.values())
        steady_time = sum(v[1] for v in self.time_cost.values())
        live_time = sum(self.live_time.values())
        print(f"\n[统计] {len(self.images)} 张底图（匹配次数 / 耗时）")
        for name in self.images:
            print(f"  - {name}: 全量 {self.scan_counts[name][0]:>3} / {self.time_cost[name][0]:.2f}s"
                  f" | 稳态裁剪 {self.scan_counts[name][1]:>3} / {self.time_cost[name][1]:.2f}s"
                  f" | 实时链 {self.live_counts[name]:>3} / {self.live_time[name]:.2f}s")
        print(f"  合计: 全量 {full_total} / {full_time:.2f}s | "
              f"稳态裁剪 {steady_total} / {steady_time:.2f}s | "
              f"实时链 {live_total} / {live_time:.2f}s")

        frames = 1 + STEADY_FRAMES_PER_SCENE
        improved = [n for n, (f, p) in self.scan_counts.items() if p * 3 < f]
        self.assertTrue(improved, "应至少有一张底图的裁剪匹配次数不到全量的 1/3")
        self.assertLess(steady_total, full_total * 0.6,
                        "稳态裁剪的总匹配次数应显著少于全量（<60%）")
        # 实时链每张图跑了 frames 帧，等价的"逐帧全量"成本是 full_total * frames
        self.assertLess(live_total, full_total * frames * 0.6,
                        "实时链（每场景 1 切换帧 + {} 停留帧）总成本应比逐帧全量省一半以上"
                        .format(STEADY_FRAMES_PER_SCENE))

    def test_hint_with_neighbor_scene_consistent(self):
        """hint 取"真实场景的邻居"时结果一致（覆盖 Tier-1 命中邻居）"""
        for name, full_name in list(self.full_results.items())[:3]:
            neighbors = self.index.neighbors(full_name)
            if not neighbors:
                continue
            result, _count, _elapsed = _scan_once(
                Recognizer(self.graph), self.images[name], hint=neighbors[0])
            self.assertEqual(_name(result), full_name,
                             f"{name}: hint={neighbors[0]} 时结果不一致")

    def test_unknown_hint_string_consistent(self):
        """hint 为未知标记字符串（非场景名）时退回全量，结果一致"""
        for name, full_name in list(self.full_results.items())[:2]:
            result, _count, _elapsed = _scan_once(
                Recognizer(self.graph), self.images[name], hint=UNKNOWN_SCENES[0])
            self.assertEqual(_name(result), full_name)


class FallbackAndLearningTest(unittest.TestCase):
    """Tier-1 未命中 → 全量兜底（不漏判）+ 学习边（下次不再兜底）"""

    @classmethod
    def setUpClass(cls):
        cls.limit = _LIMIT
        cls.graph = _graph()
        cls.index = get_scene_index(cls.graph)
        cls.images = {}
        for path in _test_images(cls.limit):
            img = cv_imread(path)
            if img is not None:
                cls.images[os.path.splitext(os.path.basename(path))[0]] = img

    def _matching_scenes(self, img) -> set:
        """一次全量扫描：求出所有"标志元素匹配该截图"的场景（构造用例 / 识别数据歧义用）"""
        recognizer = Recognizer(self.graph)
        return {
            name for name, scene in self.graph.scenes.items()
            if scene.elements and recognizer.scene_match(img, scene, False)
        }

    def _remote_hint(self, actual: str, img=None, max_candidates: int = 8):
        """找一个"候选集不含 actual、规模较小、且候选集里没有会匹配该截图的场景"的远端场景。

        限制候选集规模的原因：枢纽场景（如 `主场景`，入/出边合计 ≈48）作 hint 时，
        Tier-1 要扫完这些邻居，成本会接近一次全量扫描（这是"按转移图裁剪"的固有特性，
        收益取决于场景图的入/出度）——用它做"次数更少"的断言会掩盖学习边的效果。
        """
        matching = self._matching_scenes(img) if img is not None else None
        for name in self.graph.scenes:
            cands = self.index.candidates(name)
            if not cands or name == actual or actual in cands:
                continue
            if len(cands) > max_candidates:
                continue
            if matching is not None and matching & set(cands):
                continue
            return name
        return None

    def _full_scan(self, img) -> str:
        """全量扫描基线（新建识别器，无 hint / 无历史）"""
        result, _count, _elapsed = _scan_once(Recognizer(self.graph), img)
        return _name(result)

    def _full_scan_counted(self, img):
        """全量扫描基线：返回 (场景名, scene_match 次数)，供相对耗时/次数断言"""
        result, count, _elapsed = _scan_once(Recognizer(self.graph), img)
        return _name(result), count

    def test_untrusted_hint_uses_full_scan_arbitration(self):
        """陈旧/错误 hint 不得抢占结果。

        库中存在重叠的标志元素 → 旧 hint 所在场景也可能"恰好"匹配当前画面，若直接采纳
        就会误判（实测案例：X之要塞 底图被 冒险-修罗副本 抢先匹配）。因此 hint 与自身
        上一帧识别不一致时必须退回全量扫描（按 DB 顺序仲裁），与优化前结果一致。
        """
        name, img = next(iter(self.images.items()))
        full = self._full_scan(img)
        remote = self._remote_hint(full)
        self.assertIsNotNone(remote, "找不到与真实场景无候选关系的远端场景")
        # 新建识别器（_last_matched_scene=None）→ hint 不可信 → 全量仲裁
        result, _count, _elapsed = _scan_once(Recognizer(self.graph), img, hint=remote)
        self.assertEqual(_name(result), full, "不可信 hint 必须由全量扫描仲裁")

    def test_trusted_hint_uses_candidates(self):
        """可信 hint（与自身上一帧识别一致）→ 走 Tier-1 候选集，匹配次数应少于全量"""
        name, img = next(iter(self.images.items()))
        full, full_count = self._full_scan_counted(img)
        recognizer = Recognizer(self.graph)
        recognizer._last_matched_scene = full      # 模拟"上一帧就是该场景"
        hits_before = self.index.tier1_hits
        result, count, _elapsed = _scan_once(recognizer, img, hint=full)
        self.assertEqual(_name(result), full)
        self.assertGreater(self.index.tier1_hits, hits_before, "应命中 Tier-1")
        # 用相对比较而非硬编码上限（弹窗列表/场景库变化会让绝对数字漂移）
        self.assertLess(count, full_count,
                        f"Tier-1 命中帧（{count} 次）应少于全量扫描（{full_count} 次）")

    def test_trusted_remote_hint_falls_back_and_learns_edge(self):
        """可信 hint + 跳到远端场景：全量兜底识别正确，并记入学习边供下次 Tier-1 使用"""
        name, img = next(iter(self.images.items()))
        full, full_count = self._full_scan_counted(img)
        remote = self._remote_hint(full, img)
        self.assertIsNotNone(remote, "找不到「标志元素不重叠」的远端场景")

        recognizer = Recognizer(self.graph)
        recognizer._last_matched_scene = remote    # 模拟真实流程：上一帧确实在 remote
        before = self.index.stats()["learned_edge_count"]
        result, _count, _elapsed = _scan_once(recognizer, img, hint=remote)
        self.assertEqual(_name(result), full, "远端 hint 时必须靠全量兜底识别正确")
        self.assertIn(full, self.index.neighbors(remote), "兜底命中后应记入学习边")
        self.assertGreater(self.index.stats()["learned_edge_count"], before,
                           "学习边计数应增加")

        # 学习边生效：即使禁用全量兜底，也能靠候选集（含学习边）识别正确，且次数少于全量
        recognizer._last_matched_scene = remote    # 保持 hint 可信
        result2, count2, _elapsed2 = _scan_once(
            recognizer, img, hint=remote, allow_full_scan=False)
        self.assertEqual(_name(result2), full, "学习边应让下次直接命中 Tier-1")
        self.assertLess(count2, full_count,
                        f"学习边命中帧（{count2} 次）应少于全量扫描（{full_count} 次）")

    def test_overlapping_flag_scenes(self):
        """登记"标志元素重叠"的数据歧义（本次优化暴露、非优化引入）。

        库中部分场景的标志元素会同时匹配同一张截图（如 X之要塞 的截图也能被
        冒险-修罗副本 的标志元素匹配）。存在重叠时，"取候选集里第一个命中"与
        "取全量 DB 顺序里第一个命中"可能给出不同场景——两者都能匹配该截图。
        本用例断言的是可保证的强不变量：**裁剪返回的场景必须确实匹配该截图**
        （不会凭空返回不匹配的场景），并列出有重叠的底图，便于后续收紧标志元素（数据修复）。
        """
        ambiguous = 0
        for name, img in self.images.items():
            actual = self._full_scan(img)
            matching = self._matching_scenes(img)
            recognizer = Recognizer(self.graph)
            recognizer._last_matched_scene = actual
            result, _count, _elapsed = _scan_once(recognizer, img, hint=actual)
            self.assertIn(_name(result), matching, "裁剪结果必须确实匹配该截图")
            extra = matching - {actual}
            if extra:
                ambiguous += 1
                print(f"\n[歧义] {name}: 全量={actual}；另有 {len(extra)} 个场景的标志元素"
                      f"也匹配该截图（例：{sorted(extra)[:3]}）")
        print(f"[歧义] 抽样中「一图多匹配」的底图数: {ambiguous}/{len(self.images)}")

    def test_index_invalidate_rebuilds_edges(self):
        """invalidate() 后索引可用且边数不减少（重建读到的是库中最新边）"""
        self.index.invalidate()
        stats = self.index.stats()
        self.assertTrue(stats["available"], "失效后重建应仍然可用")
        self.assertGreaterEqual(stats["out_edge_count"], 300)
        self.assertIsNotNone(self.index.candidates("主场景"))


class FrameGrayReuseTest(unittest.TestCase):
    """单帧灰度复用 + 模板匹配尾部精简的行为与开销"""

    @classmethod
    def setUpClass(cls):
        cls.graph = _graph()
        cls.images = {}
        for path in _test_images(2):
            img = cv_imread(path)
            if img is not None:
                cls.images[os.path.splitext(os.path.basename(path))[0]] = img

    def test_full_frame_gray_converted_once_per_frame(self):
        """全量扫描一帧：整幅截图的 BGR→GRAY 只做 1 次（优化前 ≈193 次）"""
        import cv2
        original = cv2.cvtColor
        calls = []

        def counting_cvt_color(src, code, *args, **kwargs):
            calls.append(getattr(src, "shape", None))
            return original(src, code, *args, **kwargs)

        for name, img in self.images.items():
            calls.clear()
            cv2.cvtColor = counting_cvt_color
            try:
                Recognizer(self.graph).scene(img, bool_debug=False)
            finally:
                cv2.cvtColor = original
            full_frame = [shape for shape in calls if shape and tuple(shape[:2]) == img.shape[:2]]
            self.assertEqual(len(full_frame), 1,
                             f"{name}: 整幅灰度转换应只有 1 次，实际 {len(full_frame)} 次")

    def test_frame_gray_cache_released_after_recognition(self):
        """识别结束后不保留整帧灰度（避免每个识别器实例长期持有 ~4MB）"""
        recognizer = Recognizer(self.graph)
        for img in self.images.values():
            recognizer.scene(img, bool_debug=False)
            self.assertIsNone(recognizer._ctx.gray, "识别结束后应释放帧灰度缓存")

    def test_miss_records_max_response_only_in_debug(self):
        """未命中元素：调试模式记录最大响应（排查差多少），生产模式不留调试记录"""
        name, img = next(iter(self.images.items()))
        recognizer = Recognizer(self.graph)

        # 找一个"确实不匹配该底图"的标志元素（库中存在重叠标志，故要实测筛选）
        element = None
        for cand_name, cand in self.graph.scenes.items():
            if cand_name == name or not cand.elements:
                continue
            for candidate in cand.elements:
                if candidate.symbol and not recognizer.element_match(img, candidate, False):
                    element = candidate
                    break
            if element is not None:
                break
        self.assertIsNotNone(element, "找不到可用于测试的未命中标志元素")
        self.assertNotIn(element.name, recognizer._debug_match_records,
                         "生产路径不应为未命中元素写调试记录")

        # 调试路径：记录最大响应（应低于阈值，说明差多少）
        self.assertFalse(recognizer.element_match(img, element, True))
        record = recognizer._debug_match_records.get(element.name) or {}
        self.assertEqual(record.get("method"), "TEMPLATE")
        self.assertIn("max_val", record)
        self.assertLess(record["max_val"], float(element.threshold))
        self.assertNotIn("min_val", record, "min_val 未使用，已随精简移除")


class WiringTest(unittest.TestCase):
    """接线检查（源码级，零运行成本）"""

    def _read(self, rel: str) -> str:
        with open(os.path.join(_PROJECT_ROOT, rel), encoding="utf-8") as f:
            return f.read()

    def test_basetask_passes_hint(self):
        src = self._read(os.path.join("backend", "core", "legacy", "Task", "BaseTask.py"))
        self.assertIn("hint = getattr(self.operationer.current_scene", src)
        self.assertIn("recognizer.scene(screenshot, bool_debug=False, hint=hint)", src)

    def test_resource_api_invalidates_index(self):
        src = self._read(os.path.join("backend", "api", "resource.py"))
        self.assertGreaterEqual(src.count("_invalidate_graph_edges()"), 5,
                                "边/场景变更处都应失效候选集索引")
        self.assertIn("peek_shared_scene_graph", src,
                      "失效不应触发共享 SceneGraph 的全量构建")

    def test_scene_index_helpers_exported(self):
        import backend.core.legacy.Scene.SceneIndex as SceneIndex
        for name in ("SceneIndex", "get_scene_index", "invalidate_scene_index", "scene_candidates"):
            self.assertTrue(hasattr(SceneIndex, name), f"缺少导出: {name}")

    def test_public_signatures_backward_compatible(self):
        """公开方法签名保持兼容（旧的 bool_debug 位置参数仍可用）"""
        graph = _graph()
        recognizer = Recognizer(graph)
        paths = _test_images(1)
        img = cv_imread(paths[0]) if paths else None
        if img is None:
            self.skipTest("无可用底图")
        scene = graph.get_scene("主场景")
        # 旧调用形态：第 3 个位置参数传 bool
        recognizer.scene_match(img, scene, False)
        element = graph.get_element("主场景", "X-普通")
        if element is not None:
            recognizer.element_match(img, element, False)
        # 新调用形态
        recognizer.scene(img, bool_debug=False, hint="主场景", allow_full_scan=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)

