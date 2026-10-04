# -*- coding: utf-8 -*-
"""阶段 3.5 回归：BaseTask 收敛（内置场景处理函数外移 + 清理钩子合并）

覆盖：
1. 21 个内置"公共弹窗/独立场景"处理函数仍全部注册（场景名集合与表逐一对应，
   且类属性上的是同一个函数对象）；
2. **MRO 合并语义不变**：实例侧按 `reversed(mro)` 合并 `transition_func`，
   子类同名场景覆盖默认实现、未覆盖的默认项仍可用（这是 41 个任务文件依赖的行为）；
3. BaseTask 类体内不再有 `_` 处理函数（`@TransitionOn` 装饰的方法），
   注册表集中在 `Task/default_transitions.py`；
4. 五个 `_cleanup_on_*` 钩子合并为 `_cleanup(reason)`，别名保留且行为一致
   （停止连点 + 复位进度，调用点 `handle_task_exceptions` 无需改动）。
"""
import inspect
import logging
import os
import sys
import unittest
from pathlib import Path

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT))

from backend.core.legacy.Task.BaseTask import BaseTask, TransitionOn  # noqa: E402
from backend.core.legacy.Task.default_transitions import (  # noqa: E402
    DEFAULT_TRANSITION_HANDLERS, install_default_handlers,
)
from backend.core.legacy.Task.schedule import AnyTime  # noqa: E402


class DefaultHandlersTest(unittest.TestCase):

    def test_all_default_handlers_registered(self):
        self.assertEqual(len(DEFAULT_TRANSITION_HANDLERS), 21)
        for scene, func in DEFAULT_TRANSITION_HANDLERS.items():
            with self.subTest(scene=scene):
                self.assertIs(BaseTask.transition_func.get(scene), func,
                              f"场景 {scene} 未被注册或注册成了别的函数")

    def test_expected_scene_set(self):
        expected = {
            "二级密码", "升级", "公告", "登录界面-开始游戏", "登录奖励",
            "好友排名至X位", "重连提示", "响应超时", "安装包更新异常", "对方数据异常",
            "网络不畅通", "登录授权过期", "版本更新1", "版本更新2", "是否隐藏气泡",
            "网络连接失败", "聊天频道", "网络异常重连失败", "未知含X场景",
            "未知场景", "未注册场景",
        }
        self.assertEqual(set(DEFAULT_TRANSITION_HANDLERS), expected)

    def test_mro_merge_semantics(self):
        """复刻 BaseTask.__init__ 的合并逻辑：默认项 + 子类覆盖同时可用"""
        class Sub(BaseTask):
            source_scene = "主场景"
            schedule = AnyTime()

            @TransitionOn("公告")
            def _(self):
                return "sub"

        merged: dict = {}
        for cls in reversed(Sub.mro()):
            if hasattr(cls, "transition_func"):
                merged.update(cls.transition_func)
        self.assertIn("Sub", merged["公告"].__qualname__,
                      "子类同名场景必须覆盖默认实现")
        self.assertIn("升级", merged, "未被覆盖的默认场景仍应可用")
        self.assertIs(merged["升级"], DEFAULT_TRANSITION_HANDLERS["升级"])

    def test_install_is_idempotent(self):
        before = dict(BaseTask.transition_func)
        try:
            install_default_handlers(BaseTask)
            self.assertEqual(len(BaseTask.transition_func), len(before))
        finally:
            BaseTask.transition_func = before


class BaseTaskSourceTest(unittest.TestCase):

    def setUp(self):
        self.src = (_PROJECT_ROOT / "backend" / "core" / "legacy" / "Task"
                    / "BaseTask.py").read_text(encoding="utf-8")

    def test_no_decorated_handlers_in_base_task(self):
        self.assertNotIn("\n    @TransitionOn(", self.src,
                         "BaseTask 类体内不应再有 @TransitionOn 处理函数（已外移）")
        self.assertIn("transition_func: dict = {}", self.src)
        self.assertIn("install_default_handlers(BaseTask, replace=True)", self.src)

    def test_cleanup_hooks_merged(self):
        self.assertIn("def _cleanup(self, reason", self.src)
        for alias, reason in (("_cleanup_on_stop", "stop"),
                              ("_cleanup_on_error", "error"),
                              ("_cleanup_on_timeout", "timeout"),
                              ("_cleanup_on_complete", "complete"),
                              ("_cleanup_on_too_early", "too_early")):
            with self.subTest(alias=alias):
                self.assertIn(f'self._cleanup("{reason}")', self.src,
                              f"{alias} 应转发到 _cleanup")
        # 五个别名的方法体应只有一行转发（不再各自复制实现）
        self.assertEqual(self.src.count("self.operationer.clicker.stop()"), 1,
                         "停止连点只应出现在 _cleanup 一处")

    def test_exception_matrix_still_calls_aliases(self):
        """handle_task_exceptions 的调用点未变（别名必须保留）"""
        for alias in ("_cleanup_on_complete", "_cleanup_on_too_early",
                      "_cleanup_on_error", "_cleanup_on_stop", "_cleanup_on_timeout"):
            self.assertIn(f"self.{alias}()", self.src)


class CleanupBehaviorTest(unittest.TestCase):

    class _FakeClicker:
        def __init__(self):
            self.stops = 0

        def stop(self):
            self.stops += 1

    class _Task:
        """最小替身：只提供 _cleanup 需要的能力 + 真实方法绑定"""

        def __init__(self):
            self.logger = logging.getLogger("verify_cleanup")
            self.operationer = type("Op", (), {"clicker": CleanupBehaviorTest._FakeClicker()})()
            self.reset_calls = 0

        def reset_task_exe_prog(self):
            self.reset_calls += 1
            return True

        _cleanup = BaseTask._cleanup
        _cleanup_on_stop = BaseTask._cleanup_on_stop
        _cleanup_on_error = BaseTask._cleanup_on_error
        _cleanup_on_timeout = BaseTask._cleanup_on_timeout
        _cleanup_on_complete = BaseTask._cleanup_on_complete
        _cleanup_on_too_early = BaseTask._cleanup_on_too_early

    def test_all_aliases_do_same_cleanup(self):
        for alias in ("_cleanup_on_stop", "_cleanup_on_error", "_cleanup_on_timeout",
                      "_cleanup_on_complete", "_cleanup_on_too_early"):
            with self.subTest(alias=alias):
                task = self._Task()
                getattr(task, alias)()
                self.assertEqual(task.operationer.clicker.stops, 1, "应停止连点")
                self.assertEqual(task.reset_calls, 1, "应复位执行进度")
        self.assertIs(inspect.ismethod(self._Task()._cleanup), True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
