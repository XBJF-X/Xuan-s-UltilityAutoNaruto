# -*- coding: utf-8 -*-
"""阶段 3 单点化回归：模拟器环境知识（MuMu / 雷电）只有一个定义点

背景：改前同一份知识散在 6 处，候选清单还出现**顺序不同**的副本：
``api/validate.py``、``api/device.py``、``api/scheduler.py``、
``services/scheduler_service.py``、``core/legacy/Screen/MuMu.py``、``Screen/LD.py``。

覆盖：
1. 解析器行为（`MuMuManager info -v` 中英文运行标记 + 分辨率；`ldconsole list2` 列解析；
   16:9 判定容差）；
2. 文件检查（候选任一命中即满足；缺文件清单；路径为空）；
3. **单点化防回退**：全仓（除 `core/emulator_env.py`）不得再出现候选路径字面量；
4. `validate.py` 与 `emulator_env` 共用同一常量对象；
5. 调用点接线（device.py / api scheduler.py / scheduler_service.py / MuMu.py 均 import 共用模块）；
6. 用户可见文案未被这次重构改变（抽样断言）。
"""
import logging
import os
import sys
import tempfile
import unittest
from pathlib import Path

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT))

from backend.core import emulator_env as env  # noqa: E402


class ParserTest(unittest.TestCase):

    def test_mumu_info_english_and_chinese(self):
        info = env.parse_mumu_info("player_state=Running\nScreenWidth=1600\nScreenHeight=900")
        self.assertTrue(info.running)
        self.assertEqual(info.resolution, (1600, 900))
        self.assertTrue(info.is_16_9)

        self.assertTrue(env.parse_mumu_info("状态=运行").running)
        self.assertFalse(env.parse_mumu_info("state=Stopped").running)
        self.assertIsNone(env.parse_mumu_info("").resolution)

    def test_ld_list2_parsing(self):
        output = ("0,雷电模拟器1,1,1,1,0,0,1600,900\n"
                  "1,雷电模拟器2,1,1,0,0,0,1920,1080\n"
                  "不是实例行\n"
                  "2,缺列,1,1,0\n")
        instances = env.parse_ld_list2(output)
        self.assertEqual(sorted(instances), [0, 1])
        self.assertTrue(instances[0].running)
        self.assertFalse(instances[1].running)
        self.assertEqual(instances[1].resolution, (1920, 1080))
        self.assertTrue(instances[1].is_16_9)

    def test_is_16_9_tolerance(self):
        self.assertTrue(env.is_16_9(1600, 900))
        self.assertTrue(env.is_16_9(900, 1600), "竖向也应判定为 16:9")
        self.assertFalse(env.is_16_9(1600, 1000))
        self.assertFalse(env.is_16_9(1920, 1200), "16:10 不算 16:9")


class FileCheckTest(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="xuan_env_"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_find_and_missing(self):
        (self.tmp / "shell").mkdir()
        (self.tmp / "shell" / "MuMuManager.exe").write_text("x")
        self.assertEqual(env.find_mumu_manager(self.tmp),
                         self.tmp / "shell" / "MuMuManager.exe")
        dll_ok, manager_ok = env.check_mumu_files(self.tmp)
        self.assertFalse(dll_ok)
        self.assertTrue(manager_ok)
        self.assertEqual(env.missing_files(self.tmp, env.LD_REQUIRED_FILES),
                         ["ldconsole.exe", "ldopengl64.dll"])
        self.assertEqual(env.missing_files("", env.LD_REQUIRED_FILES),
                         ["ldconsole.exe", "ldopengl64.dll"],
                         "未配置路径时全部算缺失")
        self.assertIsNone(env.find_mumu_manager(""))

    def test_ld_required_files_are_single_source(self):
        (self.tmp / "ldconsole.exe").write_text("x")
        (self.tmp / "ldopengl64.dll").write_text("x")
        self.assertEqual(env.check_ld_files(self.tmp), (True, True))


class SingleSourceTest(unittest.TestCase):
    """候选路径字面量只能出现在 core/emulator_env.py"""

    def _py_files(self):
        return [p for p in (_PROJECT_ROOT / "backend").rglob("*.py")
                if "__pycache__" not in p.parts]

    def test_candidate_literals_appear_once(self):
        """多段候选路径（含子目录）只能出现在 emulator_env.py

        裸文件名（`MuMuManager.exe` / `ldconsole.exe`）会合法地出现在**用户提示文案**里，
        因此这里只对"带目录的候选"做零容忍，并额外禁止旧的内联候选写法
        （`for rel in ("MuMuManager.exe", ...)`）。
        """
        literals = [c for c in list(env.MUMU_MANAGER_CANDIDATES) + list(env.MUMU_DLL_CANDIDATES)
                    if "/" in c]
        offenders = []
        for path in self._py_files():
            if path.name == "emulator_env.py":
                continue
            text = path.read_text(encoding="utf-8")
            for literal in literals:
                if f'"{literal}"' in text or f"'{literal}'" in text:
                    offenders.append(f"{path.relative_to(_PROJECT_ROOT)}: {literal}")
            # 旧的内联候选写法（阶段 3 已移除，防止回退）
            if 'for rel in ("MuMuManager.exe"' in text:
                offenders.append(f"{path.relative_to(_PROJECT_ROOT)}: 内联 MuMu 候选元组")
        self.assertEqual(offenders, [],
                         "候选路径字面量重复出现，必须改为从 core/emulator_env 导入")

    def test_16_9_formula_appears_once(self):
        formula = "max(rw, rh) * 9 - min(rw, rh) * 16"
        offenders = []
        for path in self._py_files():
            if path.name == "emulator_env.py":
                continue
            text = path.read_text(encoding="utf-8")
            if formula in text:
                offenders.append(str(path.relative_to(_PROJECT_ROOT)))
        self.assertEqual(offenders, [], "16:9 判定式重复实现，应调用 emulator_env.is_16_9")

    def test_callers_import_shared_module(self):
        expectations = {
            "backend/api/validate.py": "core.emulator_env",
            "backend/api/device.py": "core.emulator_env",
            "backend/api/scheduler.py": "core.emulator_env",
            "backend/services/scheduler_service.py": "core.emulator_env",
            "backend/core/legacy/Screen/MuMu.py": "core.emulator_env",
        }
        for rel, needle in expectations.items():
            with self.subTest(file=rel):
                text = (_PROJECT_ROOT / rel).read_text(encoding="utf-8")
                self.assertIn(needle, text, f"{rel} 应复用 core/emulator_env")

    def test_validate_reexports_same_constants(self):
        from backend.api import validate
        self.assertIs(validate.MUMU_DLL_CANDIDATES, env.MUMU_DLL_CANDIDATES)
        self.assertIs(validate.MUMU_MANAGER_CANDIDATES, env.MUMU_MANAGER_CANDIDATES)


class CallSiteBehaviorTest(unittest.TestCase):
    """调用点文案与判定行为未被重构改变（抽样）"""

    class _FakeCfg:
        def __init__(self, values):
            self._values = values

        def get_config(self, key, default=None):
            return self._values.get(key, default)

    def test_precheck_mumu_missing_files_message(self):
        from backend.api.scheduler import _precheck_screenshot_path
        cfg = self._FakeCfg({"截图模式": 3, "MuMu安装路径": str(Path(tempfile.gettempdir()))})
        errors = _precheck_screenshot_path(cfg)
        self.assertIn("MuMu 安装路径下未找到 external_renderer_ipc.dll（截图动态库）", errors)
        self.assertIn("MuMu 安装路径下未找到 MuMuManager.exe", errors)

    def test_precheck_ld_unconfigured_message(self):
        from backend.api.scheduler import _precheck_screenshot_path
        cfg = self._FakeCfg({"截图模式": 4, "雷电安装路径": ""})
        self.assertEqual(_precheck_screenshot_path(cfg),
                         ["未配置 雷电安装路径（截图模式为 LD 时需要，请在全局设置中配置）"])

    def test_precheck_ok_for_non_emulator_mode(self):
        from backend.api.scheduler import _precheck_screenshot_path
        self.assertEqual(_precheck_screenshot_path(self._FakeCfg({"截图模式": 2})), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
