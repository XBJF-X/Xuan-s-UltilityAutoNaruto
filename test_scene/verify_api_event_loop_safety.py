# -*- coding: utf-8 -*-
"""验证「API 层不再阻塞事件循环」与「GET 无副作用」（2026-09-17，阶段 1）

覆盖：
1. 阻塞型端点必须声明为**同步** `def`（由 FastAPI 投递到 anyio 线程池），
   `async def` 会把秒级/数十秒的阻塞工作跑在事件循环线程上，冻结 WS 日志推送与
   其他全部 API（用户感受为"点启动后界面卡死"）；
2. `peek_scheduler` 只读、不创建调度器实例（旧实现 GET /status、GET /tasks 会
   实例化 SchedulerService，Dashboard 5s 轮询让每个被看过的配置常驻对象）；
3. 事件循环显式注入（`bind_main_loop`）与"取不到 loop 时返回 None 而不抛异常"
   —— 阻塞端点移出事件循环后，`asyncio.get_event_loop()` 在工作线程会抛
   RuntimeError 并丢掉状态推送；
4. 程序退出清理入口存在（`shutdown_all_schedulers`）；
5. `SchedulerService.stop()` 会等待任务执行线程（`_join_task_threads`）。
"""
import inspect
import logging
import os
import sys
import unittest
from pathlib import Path

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.api import scheduler as sched_api  # noqa: E402

# 端点 → 是否必须同步（True=必须 def，False=允许 async）
_BLOCKING_ENDPOINTS = {
    "start_scheduler": True,        # 建设备/环境预检 subprocess/SceneGraph 解码
    "stop_scheduler": True,         # 连点线程等待 + 任务线程 join + adb 自检
    "precheck_scheduler": True,     # ensure_adb_device + adb devices
    "execute_task": True,           # 可能触发 scan（启任务线程 + 写配置）
    "toggle_task_activation": True,  # 写配置文件
    "get_scheduler_status": False,  # 只读快照
    "get_tasks": False,             # 只读快照
}


class EndpointLoopSafetyTest(unittest.TestCase):

    def test_blocking_endpoints_are_sync(self):
        for name, must_be_sync in _BLOCKING_ENDPOINTS.items():
            with self.subTest(endpoint=name):
                fn = getattr(sched_api, name)
                is_async = inspect.iscoroutinefunction(fn)
                if must_be_sync:
                    self.assertFalse(
                        is_async,
                        f"{name} 含阻塞工作，必须用 def（FastAPI 线程池）；"
                        f"async def 会冻结事件循环")
                else:
                    self.assertTrue(
                        is_async,
                        f"{name} 只读内存快照，保持 async def（不占线程池）")

    def test_device_blocking_endpoints_are_sync(self):
        """设备层端点（截图/adb/环境检测）同样不得跑在事件循环线程上"""
        from backend.api import device as device_api

        for name in ("get_screenshot", "save_screenshot", "check_environment",
                     "get_serial_list", "restart_adb", "clean_stale_contacts"):
            with self.subTest(endpoint=name):
                fn = getattr(device_api, name)
                self.assertFalse(
                    inspect.iscoroutinefunction(fn),
                    f"device.{name} 含 adb/截图阻塞调用，必须用 def")

    def test_update_check_is_sync(self):
        """check-update/dependency-check 走阻塞网络与 import，必须用 def"""
        from backend.api import utils as utils_api

        for name in ("check_update", "dependency_check", "get_log_history"):
            with self.subTest(endpoint=name):
                fn = getattr(utils_api, name)
                self.assertFalse(
                    inspect.iscoroutinefunction(fn),
                    f"utils.{name} 含阻塞网络/文件 IO，必须用 def")


class PeekSchedulerTest(unittest.TestCase):

    def setUp(self):
        self._saved = dict(sched_api._schedulers)
        sched_api._schedulers.clear()

    def tearDown(self):
        sched_api._schedulers.clear()
        sched_api._schedulers.update(self._saved)

    def test_peek_returns_none_and_does_not_create(self):
        sentinel = object()
        self.assertIsNone(sched_api.peek_scheduler("Config_404"))
        self.assertEqual(sched_api._schedulers, {},
                         "peek_scheduler 不得写入注册表（不得实例化调度器）")

        sched_api._schedulers["Config_1"] = sentinel
        self.assertIs(sched_api.peek_scheduler("Config_1"), sentinel)

    def test_registry_has_lock(self):
        import threading
        self.assertIsInstance(sched_api._schedulers_lock, type(threading.RLock()),
                              "注册表必须有锁（check-then-create 并发会建两个调度器）")

    def test_read_endpoints_do_not_create_scheduler(self):
        """GET /status、GET /tasks 必须走 peek_scheduler（源码级防回退）"""
        import inspect
        for fn in (sched_api.get_scheduler_status, sched_api.get_tasks):
            src = inspect.getsource(fn)
            self.assertIn("peek_scheduler(", src,
                          f"{fn.__name__} 必须用 peek_scheduler 读状态")
            self.assertNotIn("_get_scheduler(", src,
                             f"{fn.__name__} 不得再创建调度器实例")


class MainLoopInjectionTest(unittest.TestCase):

    def setUp(self):
        self._orig = sched_api._main_loop
        sched_api._main_loop = None

    def tearDown(self):
        sched_api._main_loop = self._orig

    def test_returns_none_outside_event_loop(self):
        """工作线程/普通调用里取不到 loop 时必须返回 None（旧实现抛 RuntimeError）"""
        self.assertIsNone(sched_api._get_main_loop_or_none())

    def test_bound_loop_is_used(self):
        import asyncio
        loop = asyncio.new_event_loop()
        try:
            sched_api.bind_main_loop(loop)
            self.assertIs(sched_api._get_main_loop_or_none(), loop)
        finally:
            loop.close()
        # 关闭后不再返回（回退到 None 或重新探测）
        self.assertIsNone(sched_api._get_main_loop_or_none())

    def test_shutdown_entry_exists(self):
        self.assertTrue(callable(getattr(sched_api, "shutdown_all_schedulers", None)))
        self.assertEqual(sched_api.shutdown_all_schedulers(), [],
                         "无调度器时应快速返回空列表")


class StopJoinsTaskThreadsTest(unittest.TestCase):

    def test_join_helper_exists(self):
        from backend.services.scheduler_service import SchedulerService
        self.assertTrue(callable(getattr(SchedulerService, "_join_task_threads", None)),
                        "stop() 必须等待任务执行线程收尾")

    def test_join_helper_returns_unfinished_names(self):
        import threading
        import time as _time
        from backend.services.scheduler_service import SchedulerService

        sched = object.__new__(SchedulerService)
        sched.logger = logging.getLogger("verify_join")

        class _Task:
            task_name = "慢任务"

            def __init__(self):
                self._execution_thread = threading.Thread(
                    target=lambda: _time.sleep(1.0), daemon=True)
                self._execution_thread.start()

        task = _Task()
        try:
            pending = sched._join_task_threads([task], timeout=0.05)
            self.assertEqual(pending, ["慢任务"], "超时未退出应被上报")
        finally:
            task._execution_thread.join(timeout=2.0)

    def test_join_helper_ignores_current_thread(self):
        """从任务线程自身调用 stop() 时不得自 join（会死等）"""
        import threading
        from backend.services.scheduler_service import SchedulerService

        sched = object.__new__(SchedulerService)
        sched.logger = logging.getLogger("verify_join2")
        holder = {}

        class _Task:
            task_name = "自身"

            def __init__(self):
                holder["task"] = self
                self._execution_thread = threading.current_thread()

        task = _Task()
        self.assertEqual(sched._join_task_threads([task], timeout=0.05), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
