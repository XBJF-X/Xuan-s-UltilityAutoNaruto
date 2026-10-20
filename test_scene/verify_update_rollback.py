# -*- coding: utf-8 -*-
"""更新包保留 + 离线回滚 回归（纯离线：不联网、不需要设备/模型）。

覆盖：
1. ``update_packages``：保存/命名/元数据、更新前快照、5 个配额裁剪、当前版本保护
2. ``rollback_service``：**更新链路被改坏时回滚仍成功**（故障注入）、离线执行、
   版本标识（version.json / _build_info.py）、各类拒绝场景
3. 解耦与防漂移：回滚链路模块级不 import update_service；排除清单三方一致
4. ``runtime_info`` 信任 rollback 标记（否则横幅/版本比对会错）
5. ``scripts/rollback.py`` 兜底脚本：常量与 service 一致、不 import backend
"""
import ast
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from backend import runtime_info  # noqa: E402
from backend.services import rollback_service as rb  # noqa: E402
from backend.services import update_packages as pk  # noqa: E402
from backend.services import update_service as us  # noqa: E402

UPDATE_SERVICE = _PROJECT_ROOT / "backend" / "services" / "update_service.py"
ROLLBACK_SERVICE = _PROJECT_ROOT / "backend" / "services" / "rollback_service.py"
ROLLBACK_SCRIPT = _PROJECT_ROOT / "scripts" / "rollback.py"


def sha(n: int) -> str:
    """生成确定性的 40 位十六进制提交 SHA（前缀随编号变化，避免截断后撞车）。"""
    return f"{n:02x}" * 20


def make_zip(path: Path, top: str, files: dict[str, str]) -> Path:
    """造一个与远端归档同构的 zip（单一顶层目录 + 若干文本文件）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel, text in files.items():
            zf.writestr(f"{top}/{rel}", text)
    return path


def write_package(root: Path, commit: str, *, saved_at: str, kind="download",
                  files=None, top=None) -> Path:
    """直接在 ``root/update_packages`` 下写一个包 + sidecar（用于排序/裁剪测试）。"""
    pkg_root = root / pk.PACKAGE_DIR_NAME
    pkg_root.mkdir(parents=True, exist_ok=True)
    top = top or f"repo-{commit}"
    zip_path = make_zip(pkg_root / f"{commit}.zip", top,
                        files or {"backend/app.py": f"# {commit}\n"})
    (pkg_root / f"{commit}.json").write_text(json.dumps({
        "sha": commit, "short_sha": commit[:7], "kind": kind,
        "source": "test", "message": f"pkg {commit[:7]}",
        "top_dir": top, "saved_at": saved_at, "size": zip_path.stat().st_size,
    }, ensure_ascii=False), encoding="utf-8")
    return zip_path


def write_version_json(root: Path, commit: str, updated_by="hot-update",
                       extra: dict | None = None) -> None:
    payload = {"commit": {"sha": commit}, "updated_by": updated_by,
               "updated_at": "2026-10-20T00:00:00"}
    payload.update(extra or {})
    (root / "version.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


class PackageStorageTest(unittest.TestCase):
    """update_packages：保存 / 快照 / 列举 / 裁剪。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="xuan_pkg_")
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_save_package_records_meta_and_keeps_top_dir(self):
        src = make_zip(self.root / "download.zip", "repo-v17",
                       {"backend/a.py": "print(1)\n"})
        dest = pk.save_package(src, sha(1).upper(), kind="download", source="gitee",
                               message="测试包", project_root=self.root)
        self.assertEqual(dest.name, f"{sha(1)}.zip")
        meta = json.loads(dest.with_suffix(".json").read_text(encoding="utf-8"))
        self.assertEqual(meta["sha"], sha(1))
        self.assertEqual(meta["kind"], "download")
        self.assertEqual(meta["source"], "gitee")
        # 不重写归档（避免上百 MB IO），但顶层目录名要记录在案
        self.assertEqual(meta["top_dir"], "repo-v17")
        self.assertTrue(src.exists())  # 原文件不动（临时目录由更新流程清理）

    def test_save_package_rejects_bad_input(self):
        src = make_zip(self.root / "ok.zip", "repo-abc1234", {"a.txt": "x"})
        with self.assertRaises(ValueError):
            pk.save_package(src, "not-a-sha", project_root=self.root)
        bad = self.root / "bad.zip"
        bad.write_text("not a zip", encoding="utf-8")
        with self.assertRaises(ValueError):
            pk.save_package(bad, sha(2), project_root=self.root)
        multi = self.root / "multi.zip"
        with zipfile.ZipFile(multi, "w") as zf:
            zf.writestr("a/x.txt", "1")
            zf.writestr("b/y.txt", "2")
        with self.assertRaises(ValueError):
            pk.save_package(multi, sha(3), project_root=self.root)

    def test_snapshot_only_includes_existing_overwritten_files(self):
        (self.root / "backend").mkdir()
        (self.root / "backend" / "a.py").write_text("old\n", encoding="utf-8")
        (self.root / "frontend" / "dist").mkdir(parents=True)
        (self.root / "frontend" / "dist" / "index.html").write_text("old\n", encoding="utf-8")

        dest = pk.snapshot_overwritten_files(
            self.root, sha(4),
            ["backend/a.py", "frontend/dist/index.html", "backend/missing.py"])
        self.assertIsNotNone(dest)
        with zipfile.ZipFile(dest) as zf:
            names = sorted(zf.namelist())
        self.assertEqual(names, [f"repo-{sha(4)}/backend/a.py",
                                 f"repo-{sha(4)}/frontend/dist/index.html"])
        again = pk.snapshot_overwritten_files(self.root, sha(4), ["backend/a.py"])
        self.assertEqual(again, dest)  # 幂等

    def test_snapshot_skips_when_nothing_to_save(self):
        self.assertIsNone(pk.snapshot_overwritten_files(self.root, sha(5), ["nope.py"]))
        self.assertFalse((self.root / pk.PACKAGE_DIR_NAME / f"{sha(5)}.zip").exists())

    def test_list_packages_marks_current_and_sorts(self):
        write_package(self.root, sha(6), saved_at="2026-10-01T00:00:00")
        write_package(self.root, sha(7), saved_at="2026-10-02T00:00:00")
        (self.root / pk.PACKAGE_DIR_NAME / "notes.txt").write_text("ignore", encoding="utf-8")
        write_version_json(self.root, sha(6))
        items = pk.list_packages(self.root)
        self.assertEqual([item["sha"] for item in items], [sha(7), sha(6)])
        self.assertTrue(items[1]["is_current"])
        self.assertFalse(items[0]["is_current"])

    def test_prune_keeps_newest_and_protects_current(self):
        for index in range(6):
            write_package(self.root, sha(index + 10),
                          saved_at=f"2026-10-{index + 1:02d}T00:00:00")
        write_version_json(self.root, sha(10))  # 最旧的是当前版本 → 不得删
        removed = pk.prune_packages(self.root, keep=5)
        remaining = {item["sha"] for item in pk.list_packages(self.root)}
        self.assertEqual(len(remaining), 5)
        self.assertNotIn(sha(10), removed)
        self.assertEqual(removed, [sha(11)])
        self.assertFalse((self.root / pk.PACKAGE_DIR_NAME / f"{sha(11)}.json").exists())

    def test_prune_protects_explicit_sha(self):
        for index in range(6):
            write_package(self.root, sha(index + 20),
                          saved_at=f"2026-09-{index + 1:02d}T00:00:00")
        protected = sha(20)  # 最旧
        removed = pk.prune_packages(self.root, keep=2, protect_sha=protected)
        self.assertNotIn(protected, removed)
        self.assertEqual(len(pk.list_packages(self.root)), 2)


class RollbackTest(unittest.TestCase):
    """离线回滚：真实文件替换 + 版本标识 + 拒绝场景 + 故障注入。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="xuan_rb_")
        self.root = Path(self._tmp.name)
        self.good = sha(0xA1)
        self.bad = sha(0xB2)
        (self.root / "backend").mkdir()
        (self.root / "backend" / "app.py").write_text("BAD\n", encoding="utf-8")
        write_version_json(self.root, self.bad)
        write_package(self.root, self.good, saved_at="2026-10-01T00:00:00",
                      files={"backend/app.py": "GOOD\n",
                             "backend/new_module.py": "NEW\n"})
        self.saved_status = dict(us.UPDATE_STATUS)
        self._patches = [
            mock.patch.object(rb, "_release_database", lambda *a, **k: None),
        ]
        for patcher in self._patches:
            patcher.start()

    def tearDown(self):
        for patcher in self._patches:
            patcher.stop()
        us.UPDATE_STATUS.clear()
        us.UPDATE_STATUS.update(self.saved_status)
        rb._STATUS.update({"running": False, "mode": "rollback", "target_sha": "",
                           "phase": "", "percent": 0, "message": "", "error": "",
                           "output": None})
        self._tmp.cleanup()

    def test_offline_rollback_restores_files_and_version(self):
        with mock.patch("requests.get", side_effect=AssertionError("回滚不得联网")):
            rb.do_rollback(self.good, self.root)
        self.assertEqual((self.root / "backend" / "app.py").read_text(encoding="utf-8"),
                         "GOOD\n")
        self.assertTrue((self.root / "backend" / "new_module.py").is_file())
        data = json.loads((self.root / "version.json").read_text(encoding="utf-8"))
        self.assertEqual(data["commit"]["sha"], self.good)
        self.assertEqual(data["updated_by"], "rollback")
        self.assertEqual(data["rolled_back_from"], self.bad)
        self.assertTrue((self.root / "log" / "restart_request.json").is_file())
        self.assertEqual(us.UPDATE_STATUS.get("mode"), "rollback")
        self.assertEqual(us.UPDATE_STATUS.get("phase"), "done")
        self.assertFalse(us.UPDATE_STATUS.get("running"))
        # 回滚目标此后就是"当前版本"，包必须保留
        items = pk.list_packages(self.root)
        self.assertTrue(any(item["sha"] == self.good and item["is_current"] for item in items))

    def test_build_info_refreshed_when_present(self):
        (self.root / "_build_info.py").write_text(
            '__build_time__ = "2026-01-01 00:00:00"\n'
            f'__commit__ = "{self.bad}"\n__branch__ = "v17"\n', encoding="utf-8")
        rb.do_rollback(self.good, self.root)
        text = (self.root / "_build_info.py").read_text(encoding="utf-8")
        self.assertIn(f'__commit__ = "{self.good}"', text)
        self.assertIn('__branch__ = "v17"', text)

    def test_fault_injection_update_layer_broken_rollback_still_works(self):
        """核心场景：坏 commit 把更新链路改坏（抛异常）时，回滚仍必须成功。"""
        with mock.patch.object(us, "do_apply_update",
                               side_effect=RuntimeError("更新链路坏了")), \
                mock.patch.object(us, "set_update_status",
                                  side_effect=RuntimeError("状态同步坏了")):
            rb.do_rollback(self.good, self.root)
        self.assertEqual((self.root / "backend" / "app.py").read_text(encoding="utf-8"),
                         "GOOD\n")
        self.assertEqual(rb.status_snapshot().get("phase"), "done")

    def test_start_rollback_rejections(self):
        self.assertFalse(rb.start_rollback("../../etc", self.root)["ok"])
        self.assertFalse(rb.start_rollback(sha(0xFE), self.root)["ok"])      # 没有包
        self.assertFalse(rb.start_rollback(self.bad, self.root)["ok"])       # 等于当前版本
        corrupted = pk.package_root(self.root) / f"{sha(0xC3)}.zip"
        corrupted.write_text("not a zip", encoding="utf-8")
        self.assertFalse(rb.start_rollback(sha(0xC3), self.root)["ok"])
        us.UPDATE_STATUS["running"] = True
        try:
            result = rb.start_rollback(self.good, self.root)
            self.assertFalse(result["ok"])
            self.assertIn("执行中", result["message"])
        finally:
            us.UPDATE_STATUS["running"] = False

    def test_identity_mismatch_aborts_without_touching_files(self):
        other = sha(0xD4)
        target = sha(0xD5)
        write_package(self.root, target, saved_at="2026-10-03T00:00:00",
                      top=f"repo-{other}", files={"backend/app.py": "OTHER\n"})
        rb.do_rollback(target, self.root)
        self.assertEqual(rb.status_snapshot().get("phase"), "error")
        self.assertEqual((self.root / "backend" / "app.py").read_text(encoding="utf-8"),
                         "BAD\n")


class DecouplingTest(unittest.TestCase):
    """回滚链路必须与更新链路解耦（否则坏 commit 会让两者一起失效）。"""

    def test_no_module_level_update_service_import(self):
        tree = ast.parse(ROLLBACK_SERVICE.read_text(encoding="utf-8"))
        for node in tree.body:  # 只看模块级（函数内的延迟导入允许：仅用于同步状态）
            if isinstance(node, ast.ImportFrom):
                self.assertNotIn("update_service", node.module or "",
                                 "回滚服务不得在模块级 import update_service")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotIn("update_service", alias.name)

    def test_rollback_service_never_uses_network(self):
        src = ROLLBACK_SERVICE.read_text(encoding="utf-8")
        self.assertNotIn("import requests", src)
        self.assertNotIn("requests.get", src)

    def test_exclusion_sets_match_update_service(self):
        self.assertEqual(rb.ROLLBACK_EXCLUDE_DIRS, us.UPDATE_EXCLUDE_DIRS)
        self.assertEqual(rb.ROLLBACK_EXCLUDE_FILES, us.UPDATE_EXCLUDE_FILES)

    def test_branch_constant_matches_update_service(self):
        self.assertEqual(rb.DEFAULT_BRANCH, us.BRANCH)

    def test_rollback_script_exclusions_match_services(self):
        tree = ast.parse(ROLLBACK_SCRIPT.read_text(encoding="utf-8"))
        found = {}
        for node in tree.body:
            if (isinstance(node, ast.Assign) and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id in ("EXCLUDE_DIRS", "EXCLUDE_FILES")):
                found[node.targets[0].id] = set(ast.literal_eval(node.value))
        self.assertEqual(found.get("EXCLUDE_DIRS"), us.UPDATE_EXCLUDE_DIRS)
        self.assertEqual(found.get("EXCLUDE_FILES"), us.UPDATE_EXCLUDE_FILES)
        self.assertEqual(found.get("EXCLUDE_DIRS"), rb.ROLLBACK_EXCLUDE_DIRS)

    def test_rollback_script_does_not_import_backend(self):
        tree = ast.parse(ROLLBACK_SCRIPT.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                self.assertFalse((node.module or "").startswith("backend"),
                                 "兜底脚本必须能在后端损坏时独立运行")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertFalse(alias.name.startswith("backend"))


class RuntimeInfoRollbackTest(unittest.TestCase):
    """版本标识：横幅/版本比对要能读到回滚后的提交。"""

    def test_trusts_rollback_marker(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_version_json(root, sha(0xE5), updated_by="rollback")
            with mock.patch.object(runtime_info, "get_real_path",
                                   side_effect=lambda rel="": str(root / rel) if rel else str(root)):
                self.assertEqual(runtime_info.read_version_json_commit(), sha(0xE5))

    def test_still_trusts_hot_update_marker(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_version_json(root, sha(0xE6), updated_by="hot-update")
            with mock.patch.object(runtime_info, "get_real_path",
                                   side_effect=lambda rel="": str(root / rel) if rel else str(root)):
                self.assertEqual(runtime_info.read_version_json_commit(), sha(0xE6))


class UpdateWiringTest(unittest.TestCase):
    """更新链路接线（防回退）：快照必须在替换前，包保存/裁剪必须在成功后。"""

    def test_do_apply_update_snapshots_before_replacing(self):
        src = UPDATE_SERVICE.read_text(encoding="utf-8")
        for token in ("snapshot_overwritten_files(", "save_package(", "prune_packages("):
            self.assertIn(token, src, f"update_service 缺少 {token} 接线")
        self.assertLess(src.index("snapshot_overwritten_files("),
                        src.index("shutil.copy2(src_file, dst)"),
                        "更新前快照必须在替换循环之前")

    def test_update_status_exposes_mode_fields(self):
        self.assertIn("mode", us.UPDATE_STATUS)
        self.assertIn("target_sha", us.UPDATE_STATUS)


if __name__ == "__main__":
    unittest.main(verbosity=2)

