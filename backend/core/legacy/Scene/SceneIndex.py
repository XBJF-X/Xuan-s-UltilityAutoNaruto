# -*- coding: utf-8 -*-
"""场景候选索引：按场景转移图裁剪每帧的待匹配场景集。

## 为什么需要
`Recognizer.scene()` 原先每帧全量遍历 193 个场景（实测最坏帧 0.64s / 193 次模板匹配，
平均帧 0.18s），其中绝大多数场景与当前帧**不可能**相关（游戏场景跳转是沿有向图走的）。
本索引把"逐帧全量扫描"降级为"只扫描当前场景的入/出边邻居 + 弹窗"。

## 数据来源
- 静态边：`ResourceDBManager.get_all_scene_edges()`（当前库 193 场景 / 314 条边）。
- 运行时学习边：Tier-1 候选集未命中时，调用方（Recognizer）把 `hint -> 实得场景`
  记入 `learned`，使"图上缺边的真实跳转"只需付出一次全量兜底代价，之后不再重复，
  从而在**不动数据库**的前提下逐步收敛到"零兜底"。
- 同屏共存表（`SceneMeta.COINCIDENT_SCENES`）：父场景命中后需要下沉检查的子场景。
- 弹窗（`SceneMeta.POPUP_SCENES`）：由 `Recognizer._detect_popup_first` 单独处理，
  因此**不进入**本索引的候选集。

## 降级策略（显式，不静默）
索引构建依赖数据库连接。若无法读取边（无 ResourceDBManager 或查询失败）：
`available=False` → `candidates()` 返回 `None` → 调用方回退全量扫描（行为与优化前完全一致），
并记录一条 WARNING 说明原因。
"""
import logging
import threading
from typing import Dict, List, Optional, Sequence, Set, Tuple

from backend.core.legacy.Scene.SceneMeta import COINCIDENT_SCENES, POPUP_SCENES

# 缓存到 SceneGraph 实例上的属性名（共享 SceneGraph 单例 => 索引也被所有配置共享）
_INDEX_ATTR = "_scene_index"


class SceneIndex:
    """场景转移图索引：邻居查询 + 候选集生成 + 运行时学习边。"""

    def __init__(
        self,
        graph,
        parent_logger: logging.Logger | str = "",
        popup_scenes: Sequence[str] = POPUP_SCENES,
        coincident_scenes: Dict[str, Sequence[str]] = COINCIDENT_SCENES,
    ):
        if isinstance(parent_logger, str) or not parent_logger:
            self.logger = logging.getLogger(self.__class__.__name__)
        else:
            self.logger = parent_logger.getChild(self.__class__.__name__)
        self._graph = graph
        self._popup_scenes: Set[str] = set(popup_scenes)
        self._coincident = coincident_scenes
        self._lock = threading.RLock()
        # 邻接表（懒构建；invalidate() 后重建）
        self._out_edges: Dict[str, List[str]] = {}
        self._in_edges: Dict[str, List[str]] = {}
        self._built = False
        # 运行时学习边：hint -> 实测到的场景（补充数据库里缺失的边）
        self._learned: Dict[str, List[str]] = {}
        # 统计（供验证脚本/日志观察裁剪效果）
        self.tier1_hits = 0
        self.full_scan_fallbacks = 0
        self.full_scan_untrusted = 0
        self.unavailable_reason = ""

    # ------------------------------------------------------------------ 构建

    @property
    def available(self) -> bool:
        """索引是否可用（不可用时调用方应回退全量扫描）。"""
        self._ensure_built()
        return self._built

    @property
    def scene_names(self) -> Set[str]:
        return set(getattr(self._graph, "scenes", {}) or {})

    def _resource_db(self):
        """取共享 SceneGraph 持有的 ResourceDBManager（读边用）。"""
        return getattr(self._graph, "_resource_db", None)

    def _ensure_built(self) -> None:
        if self._built:
            return
        with self._lock:
            if self._built:
                return
            db = self._resource_db()
            if db is None:
                self.unavailable_reason = "SceneGraph 未持有 ResourceDBManager，无法读取场景边"
                self.logger.warning(
                    "场景候选索引不可用（%s）→ 每帧回退全量扫描；如需启用按转移图裁剪，"
                    "请用 ResourceDBManager 构建 SceneGraph",
                    self.unavailable_reason,
                )
                return
            try:
                edges = db.get_all_scene_edges()
            except Exception as e:  # 读库失败：降级为全量扫描（保证不漏判）
                self.unavailable_reason = f"读取场景边失败: {e}"
                self.logger.warning(
                    "场景候选索引不可用（%s）→ 每帧回退全量扫描", self.unavailable_reason
                )
                return

            out_edges: Dict[str, List[str]] = {}
            in_edges: Dict[str, List[str]] = {}
            for edge in edges:
                source = getattr(getattr(edge, "source_scene", None), "name", None)
                target = getattr(getattr(edge, "target_scene", None), "name", None)
                if not source or not target:
                    continue
                out_edges.setdefault(source, []).append(target)
                in_edges.setdefault(target, []).append(source)
            self._out_edges = out_edges
            self._in_edges = in_edges
            self._built = True
            # 场景改名/删除后，历史学习边可能指向不存在的场景 → 按当前场景名过滤
            known = self.scene_names
            self._learned = {
                src: [dst for dst in dsts if dst in known]
                for src, dsts in self._learned.items()
                if src in known
            }
            self.logger.debug(
                "场景候选索引构建完成：%d 场景 / %d 条边（出度最大 %d）",
                len(known), len(edges),
                max((len(v) for v in out_edges.values()), default=0),
            )

    def invalidate(self) -> None:
        """资源管理器中增删场景/边后调用：下次使用时重建邻接表（保留学习边）。"""
        with self._lock:
            self._built = False
            self._out_edges = {}
            self._in_edges = {}
        self.logger.debug("场景候选索引已失效，将在下次识别时重建")

    # ------------------------------------------------------------------ 查询

    def neighbors(self, hint: str) -> Tuple[str, ...]:
        """hint 的入/出边邻居（出边优先），不含弹窗与 hint 自身。"""
        self._ensure_built()
        ordered: List[str] = []
        seen: Set[str] = set()
        for name in (
            *self._out_edges.get(hint, ()),
            *self._in_edges.get(hint, ()),
            *self._learned.get(hint, ()),
            *self._coincident.get(hint, ()),
        ):
            if name == hint or name in seen or name in self._popup_scenes:
                continue
            seen.add(name)
            ordered.append(name)
        return tuple(ordered)

    def candidates(self, hint: Optional[str]) -> Optional[Tuple[str, ...]]:
        """生成待匹配场景集（hint 自身在最前，命中即短路）。

        Returns:
            None 表示"无法裁剪"（索引不可用 / 无 hint / hint 不在场景库），
            调用方应执行全量扫描。
        """
        if not hint:
            return None
        self._ensure_built()
        if not self._built:
            return None
        scenes = getattr(self._graph, "scenes", {}) or {}
        if hint not in scenes or hint in self._popup_scenes:
            # hint 未知（新场景/改名/未知场景字符串）→ 不裁剪，走全量
            return None
        return (hint, *self.neighbors(hint))

    def note_observed(self, hint: Optional[str], scene_name: Optional[str]) -> bool:
        """记录"从 hint 实际跳到了 scene_name"（Tier-1 未命中后的兜底学习）。

        Returns:
            是否新增了一条学习边（用于日志/统计）。
        """
        if not hint or not scene_name or hint == scene_name:
            return False
        self._ensure_built()
        if not self._built:
            return False
        known = self.scene_names
        if hint not in known or scene_name not in known:
            return False
        if scene_name in self.neighbors(hint):
            return False
        with self._lock:
            self._learned.setdefault(hint, []).append(scene_name)
        self.logger.info(
            "场景候选索引学习到新跳转：%s -> %s（建议在资源管理器中补上该边，"
            "以免下次仍需全量兜底）", hint, scene_name,
        )
        return True

    def stats(self) -> Dict[str, object]:
        self._ensure_built()
        return {
            "available": self._built,
            "scene_count": len(self.scene_names),
            "out_edge_count": sum(len(v) for v in self._out_edges.values()),
            "learned_edge_count": sum(len(v) for v in self._learned.values()),
            "popup_count": len(self._popup_scenes),
            "tier1_hits": self.tier1_hits,
            "full_scan_fallbacks": self.full_scan_fallbacks,
            "full_scan_untrusted": self.full_scan_untrusted,
            "unavailable_reason": self.unavailable_reason,
        }


def get_scene_index(
    graph,
    parent_logger: logging.Logger | str = "",
    *,
    popup_scenes: Sequence[str] = POPUP_SCENES,
    coincident_scenes: Dict[str, Sequence[str]] = COINCIDENT_SCENES,
) -> SceneIndex:
    """获取（惰性构建）挂在 SceneGraph 上的共享索引。

    共享 SceneGraph 单例 => 索引同样被所有配置/所有 Recognizer 实例共享，
    学习边因此是进程级累积的。
    """
    index = getattr(graph, _INDEX_ATTR, None)
    if index is None:
        index = SceneIndex(
            graph,
            parent_logger,
            popup_scenes=popup_scenes,
            coincident_scenes=coincident_scenes,
        )
        setattr(graph, _INDEX_ATTR, index)
    return index


def invalidate_scene_index(graph) -> bool:
    """资源管理器改动场景/边后失效索引；返回是否命中已有索引。"""
    index = getattr(graph, _INDEX_ATTR, None)
    if index is None:
        return False
    index.invalidate()
    return True


def scene_candidates(
    graph, hint: Optional[str], parent_logger: logging.Logger | str = "",
) -> Optional[Tuple[str, ...]]:
    """便捷函数：直接取候选集（None = 应全量扫描）。"""
    return get_scene_index(graph, parent_logger).candidates(hint)


__all__ = [
    "SceneIndex",
    "get_scene_index",
    "invalidate_scene_index",
    "scene_candidates",
]

