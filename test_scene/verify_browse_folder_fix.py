# -*- coding: utf-8 -*-
"""验证「选择文件夹」对话框修复（反馈界面/助手设置 → /browse-folder）。

背景（用户反馈 2026-09-15 18:55:59）：
    点击反馈界面「选择保存位置」后日志出现
    `打开文件夹选择对话框失败: None is not a valid ITEMIDLIST in this context`。
    根因：pywin32 的 `SHBrowseForFolder` 返回 `(pidl, displayName, iImage)` 三元组，
    **用户取消/直接关闭对话框时 pidl 为 None，而容器本身仍是真值元组**；旧实现只判断
    `if folder_selected:`，于是把 None 当 PIDL 传给 `SHGetPathFromIDListW`，
    pywin32 的 `PyWinObject_AsPIDL(bNoneOK=False)` 抛
    `TypeError: None is not a valid ITEMIDLIST in this context`。
    旧实现还有两个附带问题：`title` 从未传给 API（标题不生效）；对话框 owner 为 None
    可能弹在应用窗口后面，用户以为"没反应"而按 Esc（正好走上面的崩溃路径）。

本脚本覆盖（全部离线，monkeypatch shell/win32gui，不弹真实对话框）：
  1. `_extract_browse_pidl` 各种返回形态（None / 单值 / 序列 / 空序列 / (None,)*3）；
  2. 成功路径：ok/path/cancelled 正确，且 hwnd/pidlRoot/title/flags 真正透传；
  3. 用户取消（(None,None,None) / None）→ cancelled=True、不再抛异常、不记 ERROR；
  4. 兜底：ANSI 回退返回的 mbcs bytes 路径解码、非文件系统项目（空路径）、取路径抛异常；
  5. 对话框创建真失败 → ok=False、cancelled=False、message 有内容且记 ERROR；
  6. `GetForegroundWindow` 不可用时回退 0（桌面为 owner）且仍可成功；
  7. 源码级防回退（不得再出现 `folder_selected[0]`）。

运行：.venv\\Scripts\\python.exe -X utf8 test_scene\\verify_browse_folder_fix.py
"""
import logging
import os
import sys
import unittest
import unittest.mock
from pathlib import Path

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

import win32com.shell.shell as shell_mod  # noqa: E402
import win32com.shell.shellcon as shellcon  # noqa: E402
import win32gui  # noqa: E402

from backend.api import utils as api_utils  # noqa: E402

LOG = "backend.api.utils"


@unittest.skipUnless(os.name == "nt", "文件夹对话框仅支持 Windows")
class BrowseFolderFixTest(unittest.TestCase):
    """替换 shell/win32gui 相关函数，验证取消与成功两条链路的返回值契约。"""

    def setUp(self):
        self.calls = {}
        self.browse_return = None
        self.browse_error = None
        self.path_return = ""
        self.path_error = None
        self.fg_value = 4242
        self.fg_error = None
        for patcher in (
            unittest.mock.patch.object(shell_mod, "SHBrowseForFolder", self._fake_browse),
            unittest.mock.patch.object(shell_mod, "SHGetPathFromIDListW", self._fake_get_path),
            unittest.mock.patch.object(win32gui, "GetForegroundWindow", self._fake_fg),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    # ---------------- 替身 ----------------
    def _fake_browse(self, *args):
        self.calls["browse_args"] = args
        if self.browse_error is not None:
            raise self.browse_error
        return self.browse_return

    def _fake_get_path(self, pidl):
        self.calls["pidl"] = pidl
        if self.path_error is not None:
            raise self.path_error
        return self.path_return

    def _fake_fg(self):
        if self.fg_error is not None:
            raise self.fg_error
        return self.fg_value

    def _browse(self, title="选择压缩包保存位置"):
        return api_utils.browse_folder({"title": title})

    # ---------------- 1. PIDL 解包 ----------------
    def test_extract_pidl_shapes(self):
        self.assertIsNone(api_utils._extract_browse_pidl(None), "取消时可能直接返回 None")
        self.assertIsNone(api_utils._extract_browse_pidl(()), "空序列视为取消")
        self.assertIsNone(api_utils._extract_browse_pidl((None, None, None)),
                          "取消时 pywin32 返回 (None,None,None)：必须识别为取消")
        self.assertEqual(api_utils._extract_browse_pidl((11, "name", 0)), 11)
        self.assertEqual(api_utils._extract_browse_pidl([11, "name", 0]), 11)
        self.assertEqual(api_utils._extract_browse_pidl(11), 11, "兼容直接返回 PIDL 的形态")

    # ---------------- 2. 成功路径 ----------------
    def test_success_returns_path_and_passes_arguments(self):
        self.browse_return = (1234, "Xuan", 0)
        self.path_return = "E:\\反馈包"
        result = self._browse()
        self.assertEqual(result, {"ok": True, "cancelled": False, "path": "E:\\反馈包"})
        args = self.calls["browse_args"]
        self.assertEqual(len(args), 4, "必须显式传 hwnd/pidlRoot/title/flags")
        self.assertEqual(args[0], 4242, "owner 应为前台窗口（对话框置前，避免看不见）")
        self.assertIsNone(args[1], "pidlRoot 为 None（从桌面开始）")
        self.assertEqual(args[2], "选择压缩包保存位置", "标题必须真正传给 API（旧实现丢了）")
        self.assertEqual(args[3], shellcon.BIF_RETURNONLYFSDIRS, "仅允许选择文件系统目录")
        self.assertEqual(self.calls["pidl"], 1234, "取路径必须用解包后的 PIDL")

    def test_mbcs_bytes_path_decoded(self):
        """ANSI 回退版本（SHGetPathFromIDList）返回 mbcs bytes，必须按系统代码页解码

        路径样本必须能在**当前系统 ANSI 代码页**下编码：CI（en-US，cp1252）无法
        编码中文，硬编码中文会导致 `encode("mbcs")` 先抛 UnicodeEncodeError（与
        被测实现无关）。因此按优先级挑一个可编码的非 ASCII 样本——中文系统仍走
        中文路径（覆盖真实场景），英文系统退化为含变音字母的路径，语义一致。
        """
        self.browse_return = (7, "name", 0)
        expected = None
        for candidate in ("E:\\中文目录\\反馈", "E:\\café\\report"):
            try:
                self.path_return = candidate.encode("mbcs")
            except UnicodeEncodeError:
                continue
            expected = candidate
            break
        if expected is None:
            self.skipTest("当前系统 ANSI 代码页无法编码任何非 ASCII 路径样本")
        result = self._browse()
        self.assertTrue(result["ok"])
        self.assertEqual(result["path"], expected)

    # ---------------- 3. 取消 ----------------
    def test_cancel_tuple_of_none_is_not_an_error(self):
        """用户取消：不得再抛 ITEMIDLIST 错误，也不得记 ERROR（本次反馈的核心）"""
        self.browse_return = (None, None, None)
        with self.assertLogs(LOG, level=logging.DEBUG) as cm:
            result = self._browse()
        self.assertFalse(result["ok"])
        self.assertTrue(result["cancelled"])
        self.assertIsNone(result["path"])
        self.assertNotIn("pidl", self.calls, "取消时不应再去调用 SHGetPathFromIDListW")
        self.assertEqual([r for r in cm.records if r.levelno >= logging.ERROR], [],
                         "取消不是错误，不得记 ERROR")

    def test_cancel_none_result(self):
        self.browse_return = None
        with self.assertLogs(LOG, level=logging.DEBUG):
            result = self._browse()
        self.assertFalse(result["ok"])
        self.assertTrue(result["cancelled"])
        self.assertIsNone(result["path"])

    # ---------------- 4. 兜底 ----------------
    def test_non_filesystem_item_treated_as_cancel(self):
        """选中"此电脑/网络"等非文件系统项目：取不到路径，按取消处理（不报错）"""
        self.browse_return = (8, "此电脑", 0)
        self.path_return = ""
        with self.assertLogs(LOG, level=logging.INFO):
            result = self._browse()
        self.assertFalse(result["ok"])
        self.assertTrue(result["cancelled"])

    def test_path_lookup_error_treated_as_cancel(self):
        """pywin32 对非文件系统项目会抛 shell.error（此处用同类异常替身）"""
        self.browse_return = (9, "网络", 0)
        self.path_error = OSError("非文件系统项目没有路径")
        with self.assertLogs(LOG, level=logging.INFO):
            result = self._browse()
        self.assertTrue(result["cancelled"])
        self.assertIsNone(result["path"])

    # ---------------- 5. 真失败 ----------------
    def test_dialog_failure_returns_message_and_logs_error(self):
        self.browse_error = RuntimeError("COM 未初始化")
        with self.assertLogs(LOG, level=logging.ERROR) as cm:
            result = self._browse()
        self.assertFalse(result["ok"])
        self.assertFalse(result["cancelled"], "真失败必须与取消区分开")
        self.assertIn("COM 未初始化", result["message"])
        self.assertTrue(any(r.levelno >= logging.ERROR for r in cm.records),
                        "真失败必须留 ERROR 日志")

    # ---------------- 6. 前台窗口兜底 ----------------
    def test_foreground_window_failure_falls_back_to_desktop(self):
        self.fg_error = RuntimeError("取不到前台窗口")
        self.browse_return = (5, "n", 0)
        self.path_return = "D:\\pkg"
        result = self._browse()
        self.assertTrue(result["ok"])
        self.assertEqual(self.calls["browse_args"][0], 0, "取不到前台窗口时回退桌面 owner")

    # ---------------- 7. 源码级防回退 ----------------
    def test_source_no_longer_indexes_result_directly(self):
        # 阶段 3.4：backend/api/utils.py 已拆分包，读整包源码（browse-folder 在 system.py）
        utils_pkg = Path(_PROJECT_ROOT) / "backend" / "api" / "utils"
        source = "\n".join(p.read_text(encoding="utf-8")
                           for p in sorted(utils_pkg.glob("*.py")))
        self.assertNotIn("folder_selected[0]", source,
                         "不得再用 folder_selected[0] 取 PIDL（取消时是 None）")
        self.assertIn("_extract_browse_pidl", source)
        self.assertIn("cancelled", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)


