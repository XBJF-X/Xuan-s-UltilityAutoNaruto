# -*- coding: utf-8 -*-
"""阶段 3.4 回归：api/utils 包拆分 + 分层规则（架构不变量用测试钉死）

覆盖：
1. **分层规则**（用 ast 精确读 import，不受注释/文档字符串干扰）：
   - `core/**` 不得 import `backend.api.*` / `backend.services.*`（本轮消除 6 处倒置）
   - `services/**` 不得 import `backend.api.*`
   - `api/**` 不得 import `backend.main`（消除 api → main → api 隐式循环）
2. **包拆分等价性**：`backend/api/utils.py` 单文件不存在；包内 6 个模块 + `__init__` 门面；
   13 个 `/api/utils/*` 端点仍在；旧模块属性（含 `requests` / `os` / `get_real_path`）全部可访问。
3. **下沉后的唯一实现**：
   - `SettingsService` 实现位于 core，services 只是再导出（同一类对象 → 既有
     `backend.services.settings_service.SettingsService._get_setting` patch 仍有效）
   - 版本工具唯一实现在 `core/version_info`，`api.utils._*` 是别名，`runtime_info` 委托它
   - `runtime.log_sinks` 注册表：main.py 注册、core/services 只读注册表
   - `runtime.module_registry`：main.py 写、api 读
"""
import ast
import logging
import sys
import unittest
from pathlib import Path

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT))


def _imported_modules(path: Path) -> set:
    """返回文件里所有 import 的模块名（绝对形式，ast 精确）"""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                modules.add(node.module)
    return modules


def _py_files(root: Path):
    return [p for p in root.rglob("*.py") if "__pycache__" not in p.parts]


class LayeringRulesTest(unittest.TestCase):
    """架构不变量：内层不得依赖外层"""

    def test_core_does_not_import_api_or_services(self):
        offenders = []
        for path in _py_files(_PROJECT_ROOT / "backend" / "core"):
            for mod in _imported_modules(path):
                if mod.startswith(("backend.api", "backend.services")):
                    offenders.append(f"{path.relative_to(_PROJECT_ROOT)} -> {mod}")
        self.assertEqual(offenders, [], "core 层不得依赖 api/services 层")

    def test_services_does_not_import_api(self):
        offenders = []
        for path in _py_files(_PROJECT_ROOT / "backend" / "services"):
            for mod in _imported_modules(path):
                if mod.startswith("backend.api"):
                    offenders.append(f"{path.relative_to(_PROJECT_ROOT)} -> {mod}")
        self.assertEqual(offenders, [], "services 层不得依赖 api 层")

    def test_api_does_not_import_main(self):
        offenders = []
        for path in _py_files(_PROJECT_ROOT / "backend" / "api"):
            for mod in _imported_modules(path):
                if mod == "backend.main":
                    offenders.append(str(path.relative_to(_PROJECT_ROOT)))
        self.assertEqual(offenders, [], "api 层不得 import backend.main（隐式循环）")

    def test_legacy_screen_does_not_import_api(self):
        """core/legacy 同样属于 core 层"""
        offenders = []
        for path in _py_files(_PROJECT_ROOT / "backend" / "core" / "legacy"):
            for mod in _imported_modules(path):
                if mod.startswith(("backend.api", "backend.services")):
                    offenders.append(f"{path.relative_to(_PROJECT_ROOT)} -> {mod}")
        self.assertEqual(offenders, [])


class UtilsPackageTest(unittest.TestCase):
    """api/utils.py → 包的等价性"""

    def test_monolith_removed_and_package_present(self):
        self.assertFalse((_PROJECT_ROOT / "backend" / "api" / "utils.py").exists(),
                         "拆分后不得再存在 backend/api/utils.py 单文件")
        pkg = _PROJECT_ROOT / "backend" / "api" / "utils"
        self.assertTrue(pkg.is_dir())
        for name in ("__init__.py", "common.py", "deps.py", "logs.py", "update.py",
                     "feedback.py", "system.py"):
            with self.subTest(module=name):
                self.assertTrue((pkg / name).exists(), f"缺少 {name}")

    def test_all_old_attributes_still_accessible(self):
        import backend.api.utils as utils_pkg
        # 既有调用点 / 测试用到的名字（含模块属性，测试会 patch 它们）
        for name in ("router", "logger", "requests", "os", "get_real_path",
                     "_get_config_username", "_read_tail", "parse_log_lines",
                     "check_dependency", "check_ocr_accel", "dependency_check",
                     "check_update", "get_local_version", "browse_folder",
                     "_extract_browse_pidl", "open_log_dir", "_latest_log_date_dir",
                     "_UPDATE_STATUS", "_FEEDBACK_STATUS", "_STATUS_LOCK",
                     "_UPDATE_VERIFY_TLS", "_get_latest_sha", "_verify_update_integrity",
                     "_do_feedback_package", "_latest_log_date_dir",
                     "_read_local_version", "_read_min_release_tag", "_version_gt",
                     "shared_config_service"):
            with self.subTest(name=name):
                self.assertTrue(hasattr(utils_pkg, name), f"backend.api.utils.{name} 丢失")

    def test_endpoints_preserved(self):
        import backend.main as main_module
        spec = main_module.app.openapi()
        utils_paths = sorted(p for p in spec["paths"] if p.startswith("/api/utils"))
        # 13（原有）+ 3（离线回滚：update-packages / rollback / rollback-status，
        # 由 backend/api/recovery.py 独立注册，见 v0.17.82）
        self.assertEqual(len(utils_paths), 16, f"utils 端点数变化: {utils_paths}")
        self.assertIn("/api/utils/log-history", utils_paths)
        self.assertIn("/api/utils/check-update", utils_paths)
        self.assertIn("/api/utils/feedback/package", utils_paths)
        self.assertIn("/api/utils/open-log-dir", utils_paths)
        # 回滚入口必须存在，且不能挂在 utils 包内（否则更新链路坏掉时一起失效）
        self.assertIn("/api/utils/update-packages", utils_paths)
        self.assertIn("/api/utils/rollback", utils_paths)
        self.assertIn("/api/utils/rollback-status", utils_paths)

    def test_submodule_loggers_share_package_name(self):
        """既有测试用 assertLogs("backend.api.utils")，子模块 logger 名必须一致"""
        import backend.api.utils.feedback as feedback_mod
        import backend.api.utils.system as system_mod
        self.assertEqual(feedback_mod.logger.name, "backend.api.utils")
        self.assertEqual(system_mod.logger.name, "backend.api.utils")


class InversionFixesTest(unittest.TestCase):
    """下沉后的唯一实现与注册表"""

    def test_settings_service_is_core_class(self):
        from backend.core.settings_store import SettingsService as CoreSettings
        from backend.services.settings_service import SettingsService as ServiceSettings
        self.assertIs(ServiceSettings, CoreSettings,
                      "services 必须再导出同一类对象（patch 旧路径仍生效）")

    def test_version_helpers_single_source(self):
        from backend.api.utils import common
        from backend.core import version_info
        self.assertIs(common._read_local_version, version_info.read_client_version)
        self.assertIs(common._read_min_release_tag, version_info.read_min_release_tag)
        self.assertIs(common._version_gt, version_info.version_gt)
        self.assertIs(common._parse_version, version_info.parse_version)
        self.assertIs(common._is_major_minor_update, version_info.is_major_minor_update)
        # 版本比较行为（迁移前逐字一致：4 元组解析 + 预发布段规则）
        self.assertEqual(version_info.parse_version("v0.17.17"), (0, 17, 17, ""))
        self.assertEqual(version_info.parse_version("0.17.17-beta.1"), (0, 17, 17, "beta.1"))
        self.assertIsNone(version_info.parse_version("not-a-version"))
        self.assertTrue(version_info.version_gt("0.17.18", "0.17.17"))
        self.assertTrue(version_info.version_gt("0.17.17", "0.17.17-beta.1"))
        self.assertFalse(version_info.version_gt("0.17.17-beta.1", "0.17.17"))
        self.assertTrue(version_info.is_major_minor_update("0.18.0", "0.17.9"))
        self.assertFalse(version_info.is_major_minor_update("0.17.18", "0.17.17"))

    def test_runtime_info_delegates_version_read(self):
        src = (_PROJECT_ROOT / "backend" / "runtime_info.py").read_text(encoding="utf-8")
        self.assertIn("read_client_version", src,
                      "runtime_info.get_client_version 必须委托 core.version_info")
        from backend.runtime_info import get_client_version
        self.assertTrue(get_client_version())

    def test_log_sinks_registry(self):
        from backend.runtime import log_sinks
        sink = logging.StreamHandler()
        log_sinks.clear()
        try:
            self.assertEqual(log_sinks.get_handlers(), ())
            log_sinks.register_handler(sink)
            log_sinks.register_handler(sink)  # 幂等
            self.assertEqual(log_sinks.get_handlers(), (sink,))
            log_sinks.unregister_handler(sink)
            self.assertEqual(log_sinks.get_handlers(), ())
            log_sinks.register_handler(None)  # 容忍 None
            self.assertEqual(log_sinks.get_handlers(), ())
        finally:
            log_sinks.clear()

    def test_main_registers_log_sink_and_failed_modules(self):
        src = (_PROJECT_ROOT / "backend" / "main.py").read_text(encoding="utf-8")
        self.assertIn("register_handler", src, "main.py 必须把 WS handler 注册到 log_sinks")
        self.assertIn("module_registry.record_failed_module", src,
                      "main.py 必须把导入失败模块写入 registry")

    def test_module_registry_read_by_api(self):
        from backend.runtime import module_registry
        module_registry.clear()
        try:
            self.assertEqual(module_registry.failed_modules(), [])
            module_registry.record_failed_module("demo: boom")
            self.assertEqual(module_registry.failed_modules(), ["demo: boom"])
            # 返回副本，外部修改不影响内部
            module_registry.failed_modules().append("x")
            self.assertEqual(module_registry.failed_modules(), ["demo: boom"])
        finally:
            module_registry.clear()
        import backend.main as main_module
        self.assertEqual(main_module._FAILED_API_MODULES, [])

    def test_config_model_uses_log_sinks_not_api_ws(self):
        src = (_PROJECT_ROOT / "backend" / "core" / "config_model.py").read_text(encoding="utf-8")
        self.assertIn("log_sinks", src)
        self.assertNotIn("from backend.api.ws import", src)


class ServiceLayerSinkingTest(unittest.TestCase):
    """阶段 3.4（后半）：api 层只做参数映射，业务逻辑下沉 services

    首个落地：`services/log_service.py`（日志尾部读取/行解析/按配置汇总），
    `api/utils/logs.py` 退化为 3 行适配；`api/utils/common.py` 以同名再导出保持
    既有 import 路径（`from backend.api.utils import parse_log_lines` 等）与测试 patch 目标。
    """

    def test_log_service_exists_and_exports(self):
        path = _PROJECT_ROOT / "backend" / "services" / "log_service.py"
        self.assertTrue(path.exists())
        from backend.services import log_service
        for name in ("get_config_username", "read_tail", "parse_log_lines",
                     "read_log_history"):
            with self.subTest(name=name):
                self.assertTrue(hasattr(log_service, name), f"log_service 缺少 {name}")

    def test_route_is_thin_adapter(self):
        src = (_PROJECT_ROOT / "backend" / "api" / "utils" / "logs.py").read_text(
            encoding="utf-8")
        self.assertIn("from backend.services.log_service import read_log_history", src)
        # 解析/汇总逻辑不得再留在路由里（只查代码，文档字符串里的说明不算）
        code = "\n".join(line.split("#", 1)[0] for line in src.splitlines())
        code = code.split('"""')
        code = "".join(code[i] for i in range(0, len(code), 2))
        for moved in ("def parse_log_lines", "def _read_tail", 'glob("Main.log',
                      "parse_log_lines("):
            with self.subTest(moved=moved):
                self.assertNotIn(moved, code, f"{moved} 应已下沉到 log_service")
        # 路由应只剩参数映射（imports + logger + router + 装饰器 + 函数签名 + return）
        self.assertLessEqual(len(code.splitlines()), 25,
                             f"路由仍偏厚：{len(code.splitlines())} 行代码")

    def test_api_reexports_service_functions(self):
        from backend.api.utils import common
        from backend.services import log_service
        self.assertIs(common.parse_log_lines, log_service.parse_log_lines)
        self.assertIs(common._read_tail, log_service.read_tail)
        self.assertIs(common._get_config_username, log_service.get_config_username)

    def test_service_does_not_import_api(self):
        """下沉后的服务不得反向依赖 api（与 LayeringRulesTest 同源，此处针对新模块）"""
        from collections import defaultdict
        offenders = defaultdict(list)
        for path in _py_files(_PROJECT_ROOT / "backend" / "services"):
            for mod in _imported_modules(path):
                if mod.startswith("backend.api"):
                    offenders[str(path.relative_to(_PROJECT_ROOT))].append(mod)
        self.assertEqual(dict(offenders), {})

    # ---- 反馈打包（阶段 3.4 后半，第二批） ----
    def test_feedback_service_exists_and_exports(self):
        path = _PROJECT_ROOT / "backend" / "services" / "feedback_service.py"
        self.assertTrue(path.exists())
        from backend.services import feedback_service
        for name in ("FEEDBACK_STATUS", "set_status", "snapshot", "collect_options",
                     "start_package", "run_package"):
            with self.subTest(name=name):
                self.assertTrue(hasattr(feedback_service, name), f"feedback_service 缺少 {name}")

    def test_feedback_route_is_thin_adapter(self):
        src = (_PROJECT_ROOT / "backend" / "api" / "utils" / "feedback.py").read_text(
            encoding="utf-8")
        self.assertIn("from backend.services.feedback_service import", src)
        code = "\n".join(line.split("#", 1)[0] for line in src.splitlines())
        code_parts = code.split('"""')
        code = "".join(code_parts[i] for i in range(0, len(code_parts), 2))
        for moved in ("zipfile", "threading.Thread", "ZIP_DEFLATED", "def _do_feedback_package"):
            with self.subTest(moved=moved):
                self.assertNotIn(moved, code, f"{moved} 应已下沉到 feedback_service")
        # import + logger + router + 3 个装饰器与函数签名 + return（无业务逻辑）
        self.assertLessEqual(len(code.splitlines()), 50,
                             f"路由仍偏厚：{len(code.splitlines())} 行代码")

    def test_feedback_state_is_shared_object(self):
        import backend.api.utils as utils_pkg
        from backend.services import feedback_service
        self.assertIs(utils_pkg._FEEDBACK_STATUS, feedback_service.FEEDBACK_STATUS,
                      "api 层必须再导出同一个状态字典（测试会就地 clear/update）")
        self.assertIs(utils_pkg._do_feedback_package, feedback_service.run_package)
        self.assertIs(utils_pkg._set_feedback_status, feedback_service.set_status)

    # ---- 更新链路（阶段 3.4 后半，第三批：平台/PAT/状态先行） ----
    def test_update_service_platform_knowledge(self):
        path = _PROJECT_ROOT / "backend" / "services" / "update_service.py"
        self.assertTrue(path.exists())
        from backend.services import update_service
        for name in ("PLATFORMS", "UPDATE_STATUS", "UPDATE_VERIFY_TLS", "get_update_source",
                     "get_github_pat", "platform_headers", "github_pat_configured",
                     "select_platforms", "api_url", "get_releases_url", "set_update_status"):
            with self.subTest(name=name):
                self.assertTrue(hasattr(update_service, name), f"update_service 缺少 {name}")

    def test_update_state_is_shared_object(self):
        import backend.api.utils as utils_pkg
        from backend.services import update_service
        self.assertIs(utils_pkg._UPDATE_STATUS, update_service.UPDATE_STATUS)
        self.assertIs(utils_pkg._STATUS_LOCK, update_service.STATUS_LOCK)
        self.assertIs(utils_pkg._get_releases_url, update_service.get_releases_url)
        self.assertIs(utils_pkg._github_pat_configured, update_service.github_pat_configured)

    def test_update_service_full_api(self):
        """阶段 3.4（后半）第四批：检查更新 + 应用更新链路已全部下沉"""
        from backend.services import update_service
        for name in ("check_update", "check_full_update", "read_local_sha",
                     "write_restart_request", "backup_for_hot_update",
                     "verify_update_integrity", "get_latest_sha",
                     "start_apply_update", "start_apply_release_update",
                     "do_apply_update", "do_apply_release_update",
                     "UPDATE_EXCLUDE_DIRS", "UPDATE_EXCLUDE_FILES"):
            with self.subTest(name=name):
                self.assertTrue(hasattr(update_service, name),
                                f"update_service 缺少 {name}")

    def test_update_route_is_thin_adapter(self):
        src = (_PROJECT_ROOT / "backend" / "api" / "utils" / "update.py").read_text(
            encoding="utf-8")
        code = "\n".join(line.split("#", 1)[0] for line in src.splitlines())
        parts = code.split('"""')
        code = "".join(parts[i] for i in range(0, len(parts), 2))
        for moved in ("def _do_apply_update", "def _do_apply_release_update",
                      "def _verify_update_integrity", "requests.get(",
                      "zipfile", "shutil.copy2", "def check_update():\n    \"\"\"检查更新：对比本地"):
            with self.subTest(moved=moved):
                self.assertNotIn(moved, code, f"{moved} 应已下沉到 update_service")
        # import 列表（含再导出）+ logger + router + 6 个路由（依赖检查那段是编排）
        self.assertLessEqual(len(code.splitlines()), 110,
                             f"路由仍偏厚：{len(code.splitlines())} 行代码")

    def test_update_reexports_match_service(self):
        import backend.api.utils as utils_pkg
        from backend.services import update_service
        for api_name, service_name in (
            ("_check_full_update", "check_full_update"),
            ("_read_local_sha", "read_local_sha"),
            ("_write_restart_request", "write_restart_request"),
            ("_backup_for_hot_update", "backup_for_hot_update"),
            ("_verify_update_integrity", "verify_update_integrity"),
            ("_get_latest_sha", "get_latest_sha"),
            ("_do_apply_update", "do_apply_update"),
            ("_do_apply_release_update", "do_apply_release_update"),
            ("_set_update_status", "set_update_status"),
            ("_SHA_SUFFIX_RE", "_SHA_SUFFIX_RE"),
        ):
            with self.subTest(api=api_name):
                self.assertIs(getattr(utils_pkg, api_name),
                              getattr(update_service, service_name),
                              f"{api_name} 必须与服务的 {service_name} 是同一对象")


class DependencyCheckRegistryTest(unittest.TestCase):
    """接口行为：#/dependency-check 从登记表读失败模块"""

    def test_dependency_check_reports_registry_entries(self):
        from backend.api import utils as utils_api
        from backend.runtime import module_registry
        module_registry.clear()
        try:
            result = utils_api.dependency_check()
            self.assertNotIn("demo: boom", result["missing_modules"])
            module_registry.record_failed_module("demo: boom")
            result = utils_api.dependency_check()
            self.assertIn("demo: boom", result["missing_modules"])
            self.assertFalse(result["ok"], "有导入失败模块时 ok 必须为 False")
        finally:
            module_registry.clear()


if __name__ == "__main__":
    unittest.main(verbosity=2)
