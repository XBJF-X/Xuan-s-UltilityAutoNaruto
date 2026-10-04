# -*- coding: utf-8 -*-
"""阶段 5 回归：前端 API 层目录化（`api/endpoints/*` + `api/client.ts` barrel）

背景：`api/client.ts` 原本 120 行、把 7 个端点对象（configApi / tasksApi / schedulerApi /
settingsApi / deviceApi / utilsApi / healthApi）与 HTTP 客户端再导出混在一起；`api/resource.ts`
是与页面同级的散装模块。现在端点对象按职责拆到 `api/endpoints/`，`client.ts` 退化为 barrel。

本脚本钉住：
1. `api/client.ts` 只做再导出（不得再内联定义端点对象）；
2. 每个 endpoints 模块导出预期的对象名；
3. barrel 必须再导出**全部**原有名字（否则既有 import 会静默失效）；
4. `api/resource.ts` 已并入 `api/endpoints/resource.ts`，且没有残留引用旧路径。
"""
import re
import sys
import unittest
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT))

API_DIR = _PROJECT_ROOT / "frontend" / "src" / "api"
CLIENT = API_DIR / "client.ts"

# 端点对象 → 定义它的模块
ENDPOINT_OWNERS = {
    "configApi": "endpoints/configs.ts",
    "tasksApi": "endpoints/configs.ts",
    "schedulerApi": "endpoints/scheduler.ts",
    "settingsApi": "endpoints/system.ts",
    "deviceApi": "endpoints/system.ts",
    "utilsApi": "endpoints/system.ts",
    "healthApi": "endpoints/system.ts",
}

# client.ts 必须继续再导出的名字（既有调用点依赖）
BARREL_EXPORTS = [
    "client", "ApiError", "errorMessage", "isApiError", "normalizeError", "request",
    "requestRaw", "abortAllInFlight", "inFlightCount",
    "configApi", "tasksApi", "schedulerApi", "settingsApi", "deviceApi", "utilsApi",
    "healthApi",
]


class EndpointsSplitTest(unittest.TestCase):

    def test_client_is_barrel_only(self):
        src = CLIENT.read_text(encoding="utf-8")
        for name in ENDPOINT_OWNERS:
            with self.subTest(endpoint=name):
                self.assertNotIn(f"export const {name} = {{", src,
                                 f"{name} 应定义在 endpoints/ 而不是 client.ts")

    def test_endpoint_modules_define_expected_objects(self):
        for name, relative in ENDPOINT_OWNERS.items():
            path = API_DIR / relative
            with self.subTest(endpoint=name, module=relative):
                self.assertTrue(path.exists(), f"缺少 {relative}")
                src = path.read_text(encoding="utf-8")
                self.assertIn(f"export const {name} = {{", src)

    def test_barrel_reexports_everything(self):
        src = CLIENT.read_text(encoding="utf-8")
        for name in BARREL_EXPORTS:
            with self.subTest(export=name):
                # 允许出现在 export { ... } 列表里（可跨行）
                self.assertRegex(
                    src, rf"export\s*\{{[^}}]*\b{name}\b", f"client.ts 未再导出 {name}")

    def test_barrel_points_to_endpoint_modules(self):
        src = CLIENT.read_text(encoding="utf-8")
        for relative in ("endpoints/configs", "endpoints/scheduler", "endpoints/system"):
            with self.subTest(module=relative):
                self.assertIn(f"from './{relative}'", src)

    def test_resource_module_moved_without_dangling_imports(self):
        self.assertFalse((API_DIR / "resource.ts").exists(),
                         "api/resource.ts 应已并入 api/endpoints/resource.ts")
        moved = API_DIR / "endpoints" / "resource.ts"
        self.assertTrue(moved.exists())
        src = moved.read_text(encoding="utf-8")
        self.assertIn("export const resourceApi", src)
        # 移动后相对导入必须指向上一级
        self.assertIn("from '../client'", src)
        self.assertNotIn("from './client'", src)

        src_root = _PROJECT_ROOT / "frontend" / "src"
        dangling = []
        for path in src_root.rglob("*.vue"):
            text = path.read_text(encoding="utf-8")
            if re.search(r"from\s+['\"](@/|\.\./|\./)*api/resource['\"]", text):
                dangling.append(str(path.relative_to(_PROJECT_ROOT)))
        for path in src_root.rglob("*.ts"):
            text = path.read_text(encoding="utf-8")
            if re.search(r"from\s+['\"](@/|\.\./|\./)*api/resource['\"]", text):
                dangling.append(str(path.relative_to(_PROJECT_ROOT)))
        self.assertEqual(dangling, [], f"仍引用旧路径 api/resource: {dangling}")

    def test_typecheck_config_covers_endpoints(self):
        """端点拆到子目录后，typecheck 白名单必须仍覆盖（否则 CI 会漏检）"""
        tsconfig = (_PROJECT_ROOT / "frontend" / "tsconfig.typecheck.json").read_text(
            encoding="utf-8")
        self.assertIn("src/api", tsconfig)


if __name__ == "__main__":
    unittest.main(verbosity=2)
