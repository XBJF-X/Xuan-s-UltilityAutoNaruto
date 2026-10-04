# -*- coding: utf-8 -*-
"""阶段 3 去重与分层回归（2026-10-04）

覆盖：
1. **同义模块收敛为再导出**（两条 import 路径指向同一对象，杜绝"改一处漏一处"）：
   - `core/enums.py` ← `legacy/Enums.py`
   - `core/config_model.py` ← `legacy/Config.py`（同名前曾有**两个 Config 类**）
   - `core/scene_graph.py` ← `legacy/Scene/SceneGraph.py`（两份实现行为不同：
     新层释放 `element.bgra`，旧层保留 4 通道数组）
   - 异常类保留 `legacy/Exceptions.py` 为唯一实现（40 处引用 + STOP_REASON_* 常量），
     已删除零引用的 `core/exceptions.py`（其中 `Stop` 还被重复定义了两次）
2. **死代码保持删除**（防回退）：`core/recognizer_engine.py`、`legacy/Setting.py`、
   `PriorityQueue` 的 4 个无调用点方法、`_cancel_scan_loop`、`/api/utils/serial-list`、
   `/api/configs/{id}/task-priorities` 三层死链、`_RELEASES_URL`、`_BINARY_FIELDS`。
3. **`_github_pat_configured` 已接线**（不再是被定义却从不调用的死函数）：
   `/api/utils/dependency-check` 返回布尔状态，且**不泄漏 token 本身**。
"""
import logging
import os
import sys
import unittest
from pathlib import Path

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT))


class ModuleConsolidationTest(unittest.TestCase):

    def test_config_is_single_class(self):
        from backend.core.config_model import Config as Canonical
        from backend.core.legacy.Config import Config as Legacy
        self.assertIs(Legacy, Canonical,
                      "legacy/Config.py 必须再导出 core/config_model.Config")

    def test_enums_are_single_definition(self):
        from backend.core.enums import ElementType as CanonicalE, MatchType as CanonicalM
        from backend.core.legacy.Enums import ElementType as LegacyE, MatchType as LegacyM
        from backend.core.legacy.Enums import KEY_INDEX as LegacyK
        from backend.core.enums import KEY_INDEX as CanonicalK
        self.assertIs(LegacyE, CanonicalE)
        self.assertIs(LegacyM, CanonicalM)
        self.assertIs(LegacyK, CanonicalK)
        # 取值必须一致（曾双份定义）
        self.assertEqual([e.value for e in CanonicalE], [0, 1, 2])
        self.assertEqual(len(list(CanonicalK)), 10)

    def test_scene_graph_is_single_implementation(self):
        from backend.core.scene_graph import SceneGraph as Canonical
        from backend.core.legacy.Scene.SceneGraph import SceneGraph as Legacy
        self.assertIs(Legacy, Canonical)
        # 唯一实现应保留内存优化（bgra 解码后释放）
        src = (_PROJECT_ROOT / "backend" / "core" / "scene_graph.py").read_text(
            encoding="utf-8")
        self.assertIn("element.bgra = None", src,
                      "core/scene_graph 的内存优化（bgra 释放）不能被回退")

    def test_exceptions_single_source(self):
        from backend.core.legacy.Exceptions import (
            STOP_REASON_STUCK, STUCK_STOP_REASONS, Stop, TaskCompleted,
        )
        self.assertEqual(STOP_REASON_STUCK, "stuck")
        self.assertIn(STOP_REASON_STUCK, STUCK_STOP_REASONS)
        self.assertTrue(issubclass(TaskCompleted, Exception))
        self.assertTrue(issubclass(Stop, Exception))
        # 零引用的 core/exceptions.py 必须保持删除（它内部 Stop 定义了两次）
        self.assertFalse((_PROJECT_ROOT / "backend" / "core" / "exceptions.py").exists())

    def test_legacy_setting_and_engine_removed(self):
        self.assertFalse(
            (_PROJECT_ROOT / "backend" / "core" / "legacy" / "Setting.py").exists(),
            "零引用的 legacy/Setting.py 必须保持删除（缺 optionxform，会小写化键名）")
        self.assertFalse(
            (_PROJECT_ROOT / "backend" / "core" / "recognizer_engine.py").exists(),
            "4 行转发壳 recognizer_engine.py 必须保持删除")

    def test_shim_modules_keep_importable(self):
        """旧 import 路径仍可用（15+16+6 处调用点无需改动）"""
        import importlib
        for module in ("backend.core.legacy.Enums", "backend.core.legacy.Config",
                       "backend.core.legacy.Exceptions",
                       "backend.core.legacy.Scene.SceneGraph"):
            with self.subTest(module=module):
                importlib.import_module(module)


class DeadCodeRemovedTest(unittest.TestCase):

    def test_priority_queue_dead_methods_removed(self):
        from backend.services.scheduler_service import PriorityQueue
        for name in ("dequeue", "peek", "reheapify", "refresh_task"):
            self.assertFalse(hasattr(PriorityQueue, name),
                             f"PriorityQueue.{name} 无调用点，应保持删除")
        for name in ("enqueue", "is_empty", "get_task", "update_task_status",
                     "get_tasks_by_status"):
            self.assertTrue(hasattr(PriorityQueue, name), f"{name} 是活跃方法")

    def test_cancel_scan_loop_removed(self):
        from backend.services.scheduler_service import SchedulerService
        self.assertFalse(hasattr(SchedulerService, "_cancel_scan_loop"))

    def test_task_priorities_chain_removed(self):
        from backend.services.config_service import ConfigService
        self.assertFalse(hasattr(ConfigService, "set_task_priorities"))
        self.assertFalse(hasattr(ConfigService, "get_task_priorities"))
        self.assertFalse(hasattr(ConfigService, "get_task_order"),
                         "get_task_order 无调用点（写侧 set_task_order 仍在用）")
        self.assertTrue(hasattr(ConfigService, "set_task_order"))

    def test_routes_removed(self):
        import backend.main as main_module
        paths = {getattr(r, "path", "") for mod in main_module._API_MODULES.values()
                 if mod is not None
                 for r in (getattr(getattr(mod, "router", None), "routes", []) or [])}
        self.assertNotIn("/serial-list", paths,
                         "utils 的 serial-list 与 device 版重复且前端未用，应保持删除")
        self.assertFalse(any("task-priorities" in p for p in paths))

    def test_module_level_dead_constants_removed(self):
        from backend.api import utils as utils_api
        self.assertFalse(hasattr(utils_api, "_RELEASES_URL"))
        from backend.api import resource as resource_api
        self.assertFalse(hasattr(resource_api, "_BINARY_FIELDS"))

    def test_frontend_dead_method_removed(self):
        src = (_PROJECT_ROOT / "frontend" / "src" / "api" / "client.ts").read_text(
            encoding="utf-8")
        # 只断言"方法定义与 URL"不存在（注释里会保留删除原因说明）
        self.assertNotIn("updateTaskPriorities:", src)
        self.assertNotIn("task-priorities", src)
        self.assertIn("updateTaskOrder:", src, "执行顺序接口仍在使用（PresetEditor）")


class PatStatusWiringTest(unittest.TestCase):

    def test_dependency_check_reports_pat_status_without_token(self):
        from backend.api import utils as utils_api
        result = utils_api.dependency_check()
        self.assertIn("github_pat_configured", result)
        self.assertIsInstance(result["github_pat_configured"], bool)
        blob = str(result)
        self.assertNotIn("ghp_", blob, "接口响应绝不能包含 token 本身")
        src = (_PROJECT_ROOT / "backend" / "api" / "utils.py").read_text(encoding="utf-8")
        self.assertIn("result[\"github_pat_configured\"] = _github_pat_configured()", src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
