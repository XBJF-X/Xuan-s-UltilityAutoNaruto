# -*- coding: utf-8 -*-
"""验证 [每日分享]分享后自动关闭QQ&微信的后台（通过ADB操作）。

覆盖：
1. Device.app_stop 无参/带参（向后兼容）+ current_app_package 三种返回类型兼容；
2. 停包链路确为 ADB 的 `am force-stop`（MiniTouch 委托 adbutils 设备 → `shell am force-stop`）；
3. Operationer.close_share_app_background：参数开关、包名白名单、未识别目标三重判定；
4. 每日分享 / 忍法帖点赞分享 的分享流程：
   - 跳出游戏后识别到 QQ → 关闭 com.tencent.mobileqq；
   - 识别到微信 → 关闭 com.tencent.mm；
   - 未识别到 → 传空包名（由 close_share_app_background 告警跳过）；
   - 采样必须在 app_start 之前（否则会把游戏包名当成分享目标）。
"""
import logging
import os
import sys
import types
import unittest
import unittest.mock

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

try:  # minidevice 未发布到 PyPI（见 backend/requirements.txt 注释），CI 干净环境可能缺失
    from backend.core.legacy.Control.MiniTouch import MiniTouch
except ImportError as _mt_import_error:  # 仅缺依赖时降级：委托用例跳过，其余用例照常
    MiniTouch = None
    _MT_IMPORT_ERROR = _mt_import_error
else:
    _MT_IMPORT_ERROR = None
from backend.core.legacy.Device import Device
from backend.core.legacy.Exceptions import TaskCompleted
from backend.core.legacy.Operationer import Operationer
from backend.core.legacy.Task.MeiRiFenXiang import MeiRiFenXiang
from backend.core.legacy.Task.RenFaTieDianZanFenXiang import (
    RenFaTieDianZanFenXiang,
)

QQ = "com.tencent.mobileqq"
WX = "com.tencent.mm"
GAME = "com.tencent.KiHan"
OTHER_APP = "com.android.launcher"


class _Recorder:

    def __init__(self):
        self.calls = []

    def __call__(self, *args, **kwargs):
        self.calls.append(args[0] if len(args) == 1 else args)
        return True


class DeviceStopTest(unittest.TestCase):
    """① Device 层：停包能力与前台包名读取"""

    def _make_device(self, current_app_result):
        dev = object.__new__(Device)
        dev.package_name = GAME
        dev.logger = logging.getLogger("verify.device")
        dev.control_manager = types.SimpleNamespace(
            app_stop=_Recorder(), current_app=lambda: current_app_result)
        return dev

    def test_app_stop_default_stops_game(self):
        dev = self._make_device(None)
        dev.app_stop()
        self.assertEqual(dev.control_manager.app_stop.calls, [GAME],
                         "无参 app_stop 应仍停游戏本体（向后兼容）")

    def test_app_stop_with_package_stops_that_package(self):
        dev = self._make_device(None)
        dev.app_stop(QQ)
        self.assertEqual(dev.control_manager.app_stop.calls, [QQ])

    def test_current_app_package_dict(self):
        dev = self._make_device({"package": QQ, "activity": ".a"})
        self.assertEqual(dev.current_app_package, QQ)

    def test_current_app_package_tuple(self):
        dev = self._make_device((WX, ".b"))
        self.assertEqual(dev.current_app_package, WX)

    def test_current_app_package_object(self):
        front = types.SimpleNamespace(package=QQ, activity=".c")
        dev = self._make_device(front)
        self.assertEqual(dev.current_app_package, QQ)

    def test_current_app_package_empty(self):
        self.assertEqual(self._make_device(None).current_app_package, "")
        self.assertEqual(
            self._make_device({"package": None}).current_app_package, "")


class AdbForceStopTest(unittest.TestCase):
    """② 停包链路：MiniTouch 委托 adbutils 设备，最终执行为 adb shell am force-stop"""

    @unittest.skipIf(MiniTouch is None,
                     f"缺少 minidevice（{_MT_IMPORT_ERROR}）：无法导入 MiniTouch")
    def test_minitouch_delegates_to_adb_device(self):
        mt = object.__new__(MiniTouch)
        rec = _Recorder()
        mt.adb = types.SimpleNamespace(app_stop=rec)  # adbutils AdbDevice
        mt.app_stop(QQ)
        self.assertEqual(rec.calls, [QQ])

    def test_adbutils_app_stop_uses_am_force_stop(self):
        from adbutils._device import AdbDevice
        shell_cls = next(c for c in AdbDevice.__mro__
                         if "app_stop" in c.__dict__)
        rec = _Recorder()
        # shell_cls 为抽象基类（shell/sync 为抽象方法），构造具体子类以拦截底层命令
        harness_cls = type("_ShellHarness", (shell_cls, ), {
            "shell": lambda self, cmd: rec(cmd),
            "sync": lambda self: None,
        })
        harness_cls().app_stop(QQ)
        self.assertEqual(rec.calls, [["am", "force-stop", QQ]])


class CloseShareAppTest(unittest.TestCase):
    """③ Operationer.close_share_app_background 判定分支"""

    def _make_operationer(self, param_value=True, use_default=False):
        op = object.__new__(Operationer)
        op.task_name = "每日分享"
        op.logger = logging.getLogger("verify.op")
        if use_default:
            # 模拟任务参数缺失：get_task_exe_param 返回调用方给的 empty 默认值
            op.config = types.SimpleNamespace(
                get_task_exe_param=lambda task, key, empty=None: empty)
        else:
            op.config = types.SimpleNamespace(
                get_task_exe_param=lambda task, key, empty=None: param_value)
        rec = _Recorder()
        op.app_stop = rec
        return op, rec

    def test_param_missing_defaults_to_enabled(self):
        op, rec = self._make_operationer(use_default=True)
        self.assertTrue(op.close_share_app_background(QQ))
        self.assertEqual(rec.calls, [QQ], "参数缺失时应视为开启并执行关闭")

    def test_param_disabled_skips(self):
        op, rec = self._make_operationer(param_value=False)
        self.assertFalse(op.close_share_app_background(QQ))
        self.assertEqual(rec.calls, [], "开关关闭时不得调用 app_stop")

    def test_unknown_package_skips(self):
        op, rec = self._make_operationer()
        for pkg in ("", None, OTHER_APP, GAME):
            self.assertFalse(op.close_share_app_background(pkg))
        self.assertEqual(rec.calls, [], "未识别到 QQ/微信时不得盲发 force-stop")

    def test_qq_and_wechat_whitelisted(self):
        op, rec = self._make_operationer()
        self.assertTrue(op.close_share_app_background(QQ))
        self.assertTrue(op.close_share_app_background(WX))
        self.assertEqual(rec.calls, [QQ, WX])


class _FakeOperationer:
    """分享流程用的假执行器：按脚本返回前台状态与前台包名"""

    SHARE_APP_PACKAGES = Operationer.SHARE_APP_PACKAGES

    def __init__(self, front_flags, packages):
        self._front_flags = list(front_flags)
        self._packages = list(packages)
        self.events = []
        self.closed = []
        self.clicked = []

    @property
    def is_naruto_frontend(self):
        if self._front_flags:
            return self._front_flags.pop(0)
        return True

    @property
    def current_app_package(self):
        pkg = self._packages.pop(0) if self._packages else ""
        self.events.append(f"sample:{pkg}")
        return pkg

    def app_start(self):
        self.events.append("app_start")

    def press_key(self, key):
        self.events.append(f"press_key:{key}")

    def click_and_wait(self, *args, **kwargs):
        self.clicked.append((args, kwargs))
        return True

    def close_share_app_background(self, share_app):
        self.events.append(f"close:{share_app}")
        self.closed.append(share_app)
        return True


class ShareFlowTest(unittest.TestCase):
    """④ 分享流程：识别跳转应用并在回到游戏后关闭"""

    # front_flags 前两个 False：先跳过"跳出游戏"等待循环，再让返回游戏的
    # 循环进入一轮后立刻判定为已回前台；packages 为等待期间采样到的前台包名。
    FRONT_FLAGS = [False, False]

    def _run_flow(self, task_cls, scene, packages, front_flags=None):
        task = object.__new__(task_cls)
        task.logger = logging.getLogger("verify.task")
        task.operationer = _FakeOperationer(
            self.FRONT_FLAGS if front_flags is None else front_flags, packages)
        with unittest.mock.patch("time.sleep"):
            with self.assertRaises(TaskCompleted):
                task_cls.transition_func[scene](task)
        return task.operationer

    def _assert_sampled_before_app_start(self, op):
        sample_idx = next(i for i, e in enumerate(op.events)
                          if e.startswith("sample:"))
        self.assertLess(sample_idx, op.events.index("app_start"),
                        "必须在 app_start 之前采样前台包名")

    def test_meirifenxiang_closes_qq(self):
        op = self._run_flow(MeiRiFenXiang, "个人信息-分享", [QQ])
        self.assertEqual(op.closed, [QQ])
        self._assert_sampled_before_app_start(op)

    def test_meirifenxiang_closes_wechat(self):
        op = self._run_flow(MeiRiFenXiang, "个人信息-分享", [WX])
        self.assertEqual(op.closed, [WX])
        self._assert_sampled_before_app_start(op)

    def test_meirifenxiang_unknown_app_passes_empty(self):
        op = self._run_flow(MeiRiFenXiang, "个人信息-分享", [OTHER_APP])
        self.assertEqual(op.closed, [""], "未识别到目标应用时应传空包名交由上层跳过")
        self.assertNotIn("close:%s" % OTHER_APP, op.events)

    def test_renfatiedianzanfenxiang_closes_qq(self):
        op = self._run_flow(RenFaTieDianZanFenXiang, "忍法帖-分享", [QQ])
        self.assertEqual(op.closed, [QQ])
        self._assert_sampled_before_app_start(op)

    def test_renfatiedianzanfenxiang_closes_wechat(self):
        op = self._run_flow(RenFaTieDianZanFenXiang, "忍法帖-分享", [WX])
        self.assertEqual(op.closed, [WX])

    def test_share_app_recorded_on_later_round(self):
        """首轮采样到其它应用、次轮才采样到 QQ 时，仍以 QQ 为准"""
        op = self._run_flow(MeiRiFenXiang, "个人信息-分享", [OTHER_APP, QQ],
                            front_flags=[False, False, False, False])
        self.assertEqual(op.closed, [QQ])
        self.assertIn("press_key:BACK", op.events, "次轮前应尝试过 BACK 返回游戏")


if __name__ == "__main__":
    unittest.main(verbosity=2)

