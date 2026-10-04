# -*- coding: utf-8 -*-
"""验证「运行时待补边清单」+ 资源管理器落库接口（识别缺边的收敛闭环）。

背景：场景识别按转移图裁剪候选集，候选集未命中时会全量兜底并记住"实际发生的跳转"
（学习边）。过去这些缺失的边只活在内存里，日志只有一句"建议在资源管理器中补上该边"，
于是同一处缺边反复付出兜底代价（2026-09-16 现场：组织 -> 主场景-组织 这条直连边缺失，
导致回源走「组织 -> 主场景 -> 忍界指引 -> 主场景-组织」3 跳）。

本脚本覆盖（全部离线，不依赖设备 / 真实数据库）：
1. 学习边 → 待补清单（去重、同边只记一次、非法/同名不记）；
2. 清单维护：按子集移除 / 全量清空；
3. 索引重建时收敛：已被人工落库的边、场景改名/删除后失效的边自动从清单剔除；
4. `peek_scene_index` 不触发构建（未构建返回 None），`get_scene_index` 后为同一实例；
5. API：`GET /scene-edges/pending`（未构建 → available=False）、`POST .../apply`
   （全部应用 / 子集应用 / 参数非法 400 / 索引未构建 409 / 失败明细与剩余条数）。

运行：.venv\\Scripts\\python.exe -X utf8 test_scene\\verify_pending_scene_edges.py
"""
import logging
import os
import sys
import unittest
from types import SimpleNamespace
from unittest import mock

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from fastapi import HTTPException  # noqa: E402

from backend.api import resource as resource_api  # noqa: E402
from backend.core.legacy.Scene.SceneIndex import (  # noqa: E402
    SceneIndex,
    get_scene_index,
    peek_scene_index,
)

LOG = "verify.pending_edges"
TRANSIT = "组织"
SOURCE = "主场景-组织"
MID = "主场景"


class _Edge:
    def __init__(self, source, target):
        self.source_scene = SimpleNamespace(name=source)
        self.target_scene = SimpleNamespace(name=target)


class _DB:
    """最小资源库替身：只提供 get_all_scene_edges。"""

    def __init__(self, edges=()):
        self.edges = [_Edge(s, t) for s, t in edges]

    def get_all_scene_edges(self):
        return list(self.edges)


class _Graph:
    def __init__(self, scenes, edges=()):
        self.scenes = {name: object() for name in scenes}
        self._resource_db = _DB(edges)


def _index(scenes=(TRANSIT, SOURCE, MID), edges=((MID, SOURCE),)):
    return SceneIndex(_Graph(scenes, edges), logging.getLogger(LOG))


class PendingEdgesTest(unittest.TestCase):
    """学习边 → 待补清单：记录、去重、维护与重建收敛。"""

    def test_learned_edge_is_pending_once(self):
        index = _index()
        self.assertEqual(index.pending_edges(), [])
        self.assertTrue(index.note_observed(TRANSIT, SOURCE))
        self.assertEqual(index.pending_edges(), [(TRANSIT, SOURCE)])
        # 同一跳转再次学到不重复登记（neighbors 已包含 → note_observed 返回 False）
        self.assertFalse(index.note_observed(TRANSIT, SOURCE))
        self.assertEqual(index.pending_edges(), [(TRANSIT, SOURCE)])

    def test_existing_db_edge_is_not_pending(self):
        index = _index()
        self.assertFalse(index.note_observed(MID, SOURCE),
                         "库里已有的边不应被当成待补边")
        self.assertEqual(index.pending_edges(), [])

    def test_invalid_or_same_scene_ignored(self):
        index = _index()
        for hint, scene in ((None, SOURCE), (TRANSIT, None),
                            (TRANSIT, TRANSIT), ("不存在的场景", SOURCE)):
            self.assertFalse(index.note_observed(hint, scene))
        self.assertEqual(index.pending_edges(), [])

    def test_clear_subset_and_all(self):
        index = _index(scenes=(TRANSIT, SOURCE, MID, "忍界指引"))
        index.note_observed(TRANSIT, SOURCE)
        index.note_observed(TRANSIT, MID)
        self.assertEqual(len(index.pending_edges()), 2)
        self.assertEqual(index.clear_pending_edges([(TRANSIT, SOURCE)]), 1)
        self.assertEqual(index.pending_edges(), [(TRANSIT, MID)])
        self.assertEqual(index.clear_pending_edges(), 1)
        self.assertEqual(index.pending_edges(), [])

    def test_rebuild_drops_applied_and_stale_edges(self):
        graph = _Graph((TRANSIT, SOURCE, MID), ((MID, SOURCE),))
        index = SceneIndex(graph, logging.getLogger(LOG))
        index.note_observed(TRANSIT, SOURCE)     # 待补：组织 -> 主场景-组织
        index.note_observed(TRANSIT, MID)        # 待补：组织 -> 主场景
        self.assertEqual(len(index.pending_edges()), 2)

        # 人工把第一条边落库（模拟 /apply 成功后重建索引）
        graph._resource_db.edges.append(_Edge(TRANSIT, SOURCE))
        index.invalidate()
        self.assertEqual(index.pending_edges(), [(TRANSIT, MID)],
                         "已落库的边必须从待补清单消失（否则一直提示）")

        # 场景被删除 → 指向它的待补边同样失效
        graph.scenes.pop(MID)
        index.invalidate()
        self.assertEqual(index.pending_edges(), [])

    def test_peek_does_not_build(self):
        graph = _Graph((TRANSIT, SOURCE))
        self.assertIsNone(peek_scene_index(graph),
                          "未构建时 peek 必须返回 None（不触发全量构建）")
        index = get_scene_index(graph)
        self.assertIs(peek_scene_index(graph), index)


class _FakeIndex:
    """API 层测试用的索引替身（只暴露接口需要的方法）。"""

    def __init__(self, pending):
        self._pending = list(pending)
        self.cleared = []

    def pending_edges(self):
        return list(self._pending)

    def clear_pending_edges(self, pairs=None):
        if pairs is None:
            removed = len(self._pending)
            self._pending = []
        else:
            wanted = {(str(s), str(t)) for s, t in pairs}
            kept = [p for p in self._pending if p not in wanted]
            removed = len(self._pending) - len(kept)
            self._pending = kept
        self.cleared.append(pairs)
        return removed


class _FakeResourceDB:
    def __init__(self, ok_edges=()):
        self.ok_edges = {(s, t) for s, t in ok_edges}
        self.calls = []

    def add_scene_edge(self, source, target):
        self.calls.append((source, target))
        return (source, target) in self.ok_edges


class PendingEdgesApiTest(unittest.TestCase):
    """`/scene-edges/pending` 与 `/apply` 的契约与副作用。"""

    def test_list_when_index_unavailable(self):
        with mock.patch.object(resource_api, "_peek_scene_index", return_value=None):
            payload = resource_api.list_pending_scene_edges()
        self.assertFalse(payload["available"])
        self.assertEqual(payload["count"], 0)
        self.assertEqual(payload["edges"], [])
        self.assertTrue(payload["reason"])

    def test_list_returns_pending_pairs(self):
        index = _FakeIndex([(TRANSIT, SOURCE)])
        with mock.patch.object(resource_api, "_peek_scene_index", return_value=index):
            payload = resource_api.list_pending_scene_edges()
        self.assertTrue(payload["available"])
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["edges"],
                         [{"source": TRANSIT, "target": SOURCE}])

    def test_apply_all_clears_applied_and_invalidates(self):
        index = _FakeIndex([(TRANSIT, SOURCE), (TRANSIT, MID)])
        db = _FakeResourceDB(ok_edges=[(TRANSIT, SOURCE)])
        with mock.patch.object(resource_api, "_peek_scene_index", return_value=index), \
                mock.patch.object(resource_api, "_db", db), \
                mock.patch.object(resource_api, "_invalidate_graph_edges") as invalidate:
            payload = resource_api.apply_pending_scene_edges(None)
        self.assertFalse(payload["ok"], "有失败项时 ok 应为 False")
        self.assertEqual(payload["applied"], 1)
        self.assertEqual(payload["failed"], [{"source": TRANSIT, "target": MID}])
        self.assertEqual(payload["remaining"], 1)
        self.assertEqual(index.pending_edges(), [(TRANSIT, MID)],
                         "只有成功落库的边才从待补清单移除")
        self.assertEqual(invalidate.call_count, 1, "边变化后必须失效候选集索引")

    def test_apply_subset_only(self):
        index = _FakeIndex([(TRANSIT, SOURCE), (TRANSIT, MID)])
        db = _FakeResourceDB(ok_edges=[(TRANSIT, MID)])
        with mock.patch.object(resource_api, "_peek_scene_index", return_value=index), \
                mock.patch.object(resource_api, "_db", db), \
                mock.patch.object(resource_api, "_invalidate_graph_edges"):
            payload = resource_api.apply_pending_scene_edges(
                {"edges": [{"source": TRANSIT, "target": MID}]})
        self.assertTrue(payload["ok"])
        self.assertEqual(db.calls, [(TRANSIT, MID)], "子集应用不得触碰未指定的边")
        self.assertEqual(index.pending_edges(), [(TRANSIT, SOURCE)])

    def test_apply_invalid_payload(self):
        index = _FakeIndex([(TRANSIT, SOURCE)])
        with mock.patch.object(resource_api, "_peek_scene_index", return_value=index):
            with self.assertRaises(HTTPException) as ctx:
                resource_api.apply_pending_scene_edges({"edges": "not-a-list"})
            self.assertEqual(ctx.exception.status_code, 400)
            with self.assertRaises(HTTPException) as ctx:
                resource_api.apply_pending_scene_edges({"edges": [{"source": TRANSIT}]})
            self.assertEqual(ctx.exception.status_code, 400)

    def test_apply_without_index_is_conflict(self):
        with mock.patch.object(resource_api, "_peek_scene_index", return_value=None):
            with self.assertRaises(HTTPException) as ctx:
                resource_api.apply_pending_scene_edges(None)
        self.assertEqual(ctx.exception.status_code, 409)

    def test_apply_empty_pending_is_noop(self):
        index = _FakeIndex([])
        db = _FakeResourceDB()
        with mock.patch.object(resource_api, "_peek_scene_index", return_value=index), \
                mock.patch.object(resource_api, "_db", db), \
                mock.patch.object(resource_api, "_invalidate_graph_edges") as invalidate:
            payload = resource_api.apply_pending_scene_edges(None)
        self.assertEqual(payload, {"ok": True, "applied": 0, "failed": [],
                                   "remaining": 0})
        self.assertEqual(db.calls, [])
        self.assertEqual(invalidate.call_count, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
