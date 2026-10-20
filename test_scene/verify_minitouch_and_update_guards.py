# -*- coding: utf-8 -*-
"""验证本轮 5 项修复中可离线测试的部分。

1. MiniTouch：设备端 ``/data/local/tmp/minitouch`` 被误创建成目录时，初始化前
   自动删除；删除失败/状态异常时抛带「失败步骤」的 MiniTouchInitError。
2. 更新：任意 commit 拉取参数校验与透传；文件覆盖校验不通过时不得写 version.json；
   下载循环拿到非 zip 响应时必须降级到下一个源（不能因漏 import 抛 NameError
   后被 except 吞掉 —— 那会让双源全部失败、热更新整体不可用）。
3. 横幅：commit 优先取实时来源（git / version.json），构建快照仅兜底。
4. adb：统一解析到依赖库自带的 adbutils/binaries/adb.exe。

全部不访问网络、不触碰真实 adb/模拟器。
"""
import hashlib
import logging
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

try:  # minidevice 未发布到 PyPI（见 backend/requirements.txt 注释），CI 干净环境可能缺失
    from backend.core.legacy.Control import MiniTouch as mt_module
except ImportError as _mt_import_error:  # 仅缺依赖时降级：MiniTouch 用例跳过，其余用例照常
    mt_module = None
    _MT_IMPORT_ERROR = _mt_import_error
else:
    _MT_IMPORT_ERROR = None
from backend import runtime_info
from backend.services import update_service as us
from backend.runtime import adb_env


class _FakeDevice:
    """按顺序返回 shell 状态的假设备。"""

    rm_output = "REMOVED\n"

    def __init__(self, states):
        self.states = list(states)
        self.commands = []

    def shell(self, command):
        self.commands.append(command)
        if "if [ -d" in command:
            if len(self.states) > 1:
                return self.states.pop(0)
            return self.states[0]
        if "rm -rf" in command:
            return self.rm_output
        return ""


def _make_minitouch(device):
    mt = object.__new__(mt_module.MiniTouch)
    mt.serial = "emulator-5560"
    mt.logger = logging.getLogger("test.minitouch.path")
    mt_module.adb = SimpleNamespace(device=lambda serial: device)
    return mt


@unittest.skipIf(mt_module is None,
                 f"缺少 minidevice（{_MT_IMPORT_ERROR}）：MiniTouch 路径用例无法导入被测模块")
class MiniTouchPathTest(unittest.TestCase):
    def test_directory_is_removed_before_init(self):
        dev = _FakeDevice(["DIR\n", "MISSING\n"])
        mt = _make_minitouch(dev)
        state = mt._prepare_minitouch_path()
        self.assertEqual(state, "MISSING")
        self.assertTrue(any("rm -rf /data/local/tmp/minitouch" in c for c in dev.commands),
                        "目录必须被删除")

    def test_file_or_missing_is_untouched(self):
        dev = _FakeDevice(["FILE\n"])
        mt = _make_minitouch(dev)
        self.assertEqual(mt._prepare_minitouch_path(), "FILE")
        self.assertFalse(any("rm -rf" in c for c in dev.commands))
        dev2 = _FakeDevice(["MISSING\n"])
        mt2 = _make_minitouch(dev2)
        self.assertEqual(mt2._prepare_minitouch_path(), "MISSING")

    def test_remove_failure_reports_step(self):
        dev = _FakeDevice(["DIR\n", "DIR\n"])
        dev.rm_output = ""
        mt = _make_minitouch(dev)
        with self.assertRaises(mt_module.MiniTouchInitError) as ctx:
            mt._prepare_minitouch_path()
        self.assertIn("删除", str(ctx.exception))
        self.assertEqual(ctx.exception.step, "删除被误创建为目录的 /data/local/tmp/minitouch")

    def test_unknown_state_raises(self):
        dev = _FakeDevice(["BROKEN\n"])
        mt = _make_minitouch(dev)
        with self.assertRaises(mt_module.MiniTouchInitError) as ctx:
            mt._prepare_minitouch_path()
        self.assertIn("无法识别的路径状态", str(ctx.exception))


class RuntimeCommitTest(unittest.TestCase):
    def test_git_head_wins_over_build_snapshot(self):
        build = {"commit": "9f747da4", "build_time": "", "branch": "v17"}
        with mock.patch.object(runtime_info, "_git_head_commit", return_value="39aa2315"), \
                mock.patch.object(runtime_info, "read_version_json_commit", return_value="abc1234"), \
                mock.patch.object(runtime_info, "get_build_info", return_value=build):
            self.assertEqual(runtime_info.get_runtime_commit(), "39aa2315")

    def test_version_json_wins_over_build_snapshot(self):
        build = {"commit": "9f747da4", "build_time": "", "branch": "v17"}
        with mock.patch.object(runtime_info, "_git_head_commit", return_value=""), \
                mock.patch.object(runtime_info, "read_version_json_commit", return_value="abc1234"), \
                mock.patch.object(runtime_info, "get_build_info", return_value=build):
            self.assertEqual(runtime_info.get_runtime_commit(), "abc1234")

    def test_build_snapshot_is_last_resort(self):
        build = {"commit": "9f747da4", "build_time": "", "branch": "v17"}
        with mock.patch.object(runtime_info, "_git_head_commit", return_value=""), \
                mock.patch.object(runtime_info, "read_version_json_commit", return_value=""), \
                mock.patch.object(runtime_info, "get_build_info", return_value=build):
            self.assertEqual(runtime_info.get_runtime_commit(), "9f747da4")


class UpdateGuardsTest(unittest.TestCase):
    def test_normalize_target_sha(self):
        self.assertEqual(us.normalize_target_sha(" 9F747DA4 "), "9f747da4")
        self.assertIsNone(us.normalize_target_sha("../../etc/passwd"))
        self.assertIsNone(us.normalize_target_sha(""))
        self.assertIsNone(us.normalize_target_sha("xyz"))

    def test_verify_replaced_files(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "backend").mkdir()
            target = root / "backend" / "a.py"
            target.write_text("print(1)\n", encoding="utf-8")
            sha = hashlib.sha256(target.read_bytes()).hexdigest()
            us.verify_replaced_files(root, {"backend/a.py": sha})
            with self.assertRaises(RuntimeError):
                us.verify_replaced_files(root, {"backend/a.py": "0" * 64})
            with self.assertRaises(RuntimeError):
                us.verify_replaced_files(root, {"backend/missing.py": sha})

    def test_start_apply_update_passes_target(self):
        captured = {}

        class _FakeThread:
            def __init__(self, target=None, args=(), daemon=None):
                captured["target"] = target
                captured["args"] = args

            def start(self):
                captured["started"] = True

        saved = us.threading.Thread
        saved_status = dict(us.UPDATE_STATUS)
        us.threading.Thread = _FakeThread
        try:
            us.UPDATE_STATUS.update({"running": False})
            result = us.start_apply_update("ABCDEF1")
            self.assertTrue(result["ok"])
            self.assertEqual(captured["args"], ("abcdef1",))
        finally:
            us.threading.Thread = saved
            us.UPDATE_STATUS.update(saved_status)

    def test_invalid_target_rejected(self):
        saved_status = dict(us.UPDATE_STATUS)
        try:
            us.UPDATE_STATUS.update({"running": False})
            result = us.start_apply_update("not-a-sha")
            self.assertFalse(result["ok"])
            self.assertIn("非法", result["message"])
        finally:
            us.UPDATE_STATUS.update(saved_status)

    def test_integrity_binds_to_requested_commit(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "repo-abc1234"
            src.mkdir()
            us.verify_update_integrity(src, {"key": "github", "label": "GitHub"},
                                       expected_sha="abc1234")
            with self.assertRaises(RuntimeError):
                us.verify_update_integrity(src, {"key": "github", "label": "GitHub"},
                                           expected_sha="def5678")


class _FakeResponse:
    """最小 requests 响应替身：`with requests.get(...) as r` 需要上下文管理协议。"""

    def __init__(self, body: bytes, content_type: str = "application/octet-stream"):
        self._body = body
        self.headers = {"Content-Type": content_type,
                        "Content-Length": str(len(body))}
        self.status_code = 200

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def raise_for_status(self):
        return None

    def iter_content(self, chunk_size=8192):
        yield self._body


class UpdateDownloadLoopTest(unittest.TestCase):
    """离线跑**真实**下载循环：非 zip 必须走「不是有效 zip」降级，而不是 NameError。

    回归背景（2026-10）：update_service 下沉时漏了 `import zipfile`，
    `zipfile.is_zipfile()` 在函数体里抛 NameError → 被 except 吞成
    「下载更新包失败」→ 两个源都失败 → 热更新整体不可用。而 compileall、
    模块导入冒烟、当时的全部回归脚本都是绿的（没有一处执行到这一行）。
    """

    def test_non_zip_response_falls_back_for_every_platform(self):
        saved_status = dict(us.UPDATE_STATUS)
        try:
            with tempfile.TemporaryDirectory() as td:
                fake = _FakeResponse(b"<html>robot check</html>")
                platforms = [us.PLATFORMS["github"], us.PLATFORMS["gitee"]]
                with mock.patch.object(us, "get_real_path", return_value=td), \
                        mock.patch.object(us, "select_platforms", return_value=platforms), \
                        mock.patch("requests.get", return_value=fake), \
                        self.assertLogs("UpdateService", level="WARNING") as logs:
                    us.do_apply_update()
                text = "\n".join(logs.output)
            # 两个源都识别出「不是有效 zip」并降级 = is_zipfile 真的执行了
            self.assertEqual(text.count("不是有效 zip"), 2, text)
            self.assertNotIn("is not defined", text)  # 兜底：绝不能是 NameError 文案
            self.assertEqual(us.UPDATE_STATUS.get("error"), "download_failed")
        finally:
            us.UPDATE_STATUS.update(saved_status)


class BundledAdbTest(unittest.TestCase):

    def test_bundled_adb_found(self):
        path = adb_env.find_bundled_adb()
        self.assertTrue(path, "未能定位 adbutils/binaries/adb.exe")
        self.assertEqual(Path(path).name.lower(), "adb.exe" if os.name == "nt" else "adb")

    def test_env_points_to_bundled(self):
        path = adb_env.ensure_bundled_adb()
        self.assertEqual(os.environ.get("ADBUTILS_ADB_PATH"), path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
