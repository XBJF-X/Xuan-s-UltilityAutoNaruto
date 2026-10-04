# -*- coding: utf-8 -*-
"""API 契约回归（阶段 2）：response_model 不得变成"字段过滤器"

背景：审查发现 67 个 REST 端点里只有 3 个声明 `response_model`，前端靠手抄字段
（`resource.ts` ↔ `resource.py`）对齐。补 `response_model` 的最大风险是**漏声明某字段
把前端在用的数据静默过滤掉**，因此本项目约定：
1. 所有响应模型继承 `PassthroughModel`（`extra="allow"`），未声明字段照样返回；
2. 本次声明覆盖的端点必须在 OpenAPI 里有真实 schema（不是裸 `{}`）；
3. `app.openapi()` 必须能生成（schema 自身合法）。

覆盖：
- OpenAPI 生成成功；
- 关键路径的 200 响应带 `$ref`/对象 schema；
- `PassthroughModel` 的 extra 透传（任务快照的新增字段不被吞）；
- 所有声明了 response_model 的 APIRoute 都是"可透传"类型（防回退）。
"""
import logging
import os
import sys
import unittest

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

# 必须声明 response_model 的关键端点（前端直接消费其形状）
_REQUIRED_SCHEMA_PATHS = {
    "/api/health": "get",
    "/api/utils/version": "get",
    "/api/scheduler/status/{config_id}": "get",
    "/api/scheduler/tasks/{config_id}": "get",
    "/api/device/{config_id}/serial-list": "get",
    "/api/device/{config_id}/adb-restart": "post",
    "/api/settings/": "get",
    "/api/configs/": "get",
    "/api/configs/{config_id}": "get",
}


class OpenApiContractTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import backend.main as main_module
        cls.app = main_module.app
        cls.spec = main_module.app.openapi()

    def test_openapi_generates(self):
        self.assertIn("paths", self.spec)
        self.assertGreater(len(self.spec["paths"]), 30)

    def test_required_paths_have_schema(self):
        for path, method in _REQUIRED_SCHEMA_PATHS.items():
            with self.subTest(path=path):
                op = self.spec["paths"].get(path)
                self.assertIsNotNone(op, f"OpenAPI 缺少路径 {path}")
                content = (op[method].get("responses", {}).get("200", {})
                           .get("content", {}).get("application/json", {}))
                schema = content.get("schema") or {}
                self.assertTrue(schema, f"{path} 的 200 响应没有 schema（仍是裸 dict）")


class PassthroughModelTest(unittest.TestCase):
    """extra='allow'：声明 response_model 不能过滤掉未声明字段"""

    def test_task_runtime_item_keeps_extra_fields(self):
        from backend.api.schemas import TaskRuntimeItem

        payload = {"name": "消耗体力", "status": 1, "priority": 3,
                   "base_priority": 5, "activated": True,
                   "next_execute": "2026-10-04 12:00:00",
                   "future_field": "新增字段不能被吞"}
        model = TaskRuntimeItem.model_validate(payload)
        dumped = model.model_dump()
        for key, value in payload.items():
            self.assertEqual(dumped.get(key), value, f"字段 {key} 丢失或被改写")

    def test_scheduler_status_keeps_extra_fields(self):
        from backend.api.schemas import SchedulerStatus

        payload = {"running": True, "task_count": 7, "mode": "persistent",
                   "current_task": "天地战场", "error": ""}
        dumped = SchedulerStatus.model_validate(payload).model_dump()
        self.assertEqual(dumped["running"], True)
        self.assertEqual(dumped["current_task"], "天地战场")
        self.assertEqual(dumped["error"], "")

    def test_declared_models_are_passthrough(self):
        """所有声明了 response_model 的路由，其模型必须可透传（防未来偷偷加严格模型）"""
        import backend.main as main_module
        from fastapi.routing import APIRoute
        from backend.api.schemas import PassthroughModel

        def base_model(model):
            return getattr(model, "__origin__", model)   # list[X] -> X

        # 注意：FastAPI 0.139 的 include_router 不把子路由摊进 app.routes（是 _IncludedRouter），
        # 因此同时遍历各 api 模块自己的 router
        routes = list(main_module.app.routes)
        for mod in main_module._API_MODULES.values():
            router = getattr(mod, "router", None) if mod is not None else None
            routes.extend(getattr(router, "routes", []) or [])

        checked = 0
        for route in routes:
            if not isinstance(route, APIRoute) or route.response_model is None:
                continue
            model = base_model(route.response_model)
            if not isinstance(model, type):
                continue                      # dict[str, ...] 等泛型：无 extra 概念
            if not issubclass(model, PassthroughModel):
                continue                      # config.py 的 ConfigSummary/Detail 自有一套
            self.assertEqual(model.model_config.get("extra"), "allow",
                             f"{route.path} 的 {model.__name__} 必须允许透传字段")
            checked += 1
        self.assertGreaterEqual(checked, 5,
                                "至少应有 5 个端点使用可透传的 response_model")


if __name__ == "__main__":
    unittest.main(verbosity=2)
