# -*- coding: utf-8 -*-
"""验证本次两处修复：
1. 任务激活改为"登记待激活 → 任务结束回调统一激活"（scheduler_service）
2. MuMu/LD 安装路径只从 setting.ini [助手设置] 读取（config_model / legacy.Config）
"""
import json
import logging
import os
import shutil
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

# 跨任务激活的调用形态断言需要来源常量（v0.17.43 起 execute_task_now 区分来源）
from backend.services.scheduler_service import SOURCE_ACTIVATION  # noqa: E402


def _patch_settings(ini_path):
    """把全局 SettingsService 数据源指向临时 setting.ini，返回还原函数"""
    import backend.services.settings_service as ss_mod
    from backend.core.setting_model import Setting

    setting = Setting(parent_logger=logging.getLogger("verify"), setting_path=ini_path)
    orig = ss_mod.SettingsService._get_setting
    ss_mod.SettingsService._get_setting = lambda self: setting
    return orig


def _restore_settings(orig):
    import backend.services.settings_service as ss_mod
    ss_mod.SettingsService._get_setting = orig


def _write_cfg(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class PathKeyConfigTest(unittest.TestCase):
    """问题2：安装路径只读 setting.ini，不读 config JSON"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="xuan_verify_")
        self.ini_path = Path(self.tmp) / "setting.ini"
        self.ini_path.write_text(
            "[助手设置]\r\nMuMu安装路径 = D:\\mumu_new\r\n雷电安装路径 = D:\\ld_new\r\n",
            encoding="utf-8",
        )
        self._orig = _patch_settings(self.ini_path)
        cfg_path = Path(self.tmp) / "Config_Test.json"
        _write_cfg(cfg_path, {
            "配置文件版本": "V3",
            "用户名": "verify_user",
            "MuMu安装路径": "E:/stale/mumu",
            "雷电安装路径": "E:/stale/ld",
            "任务": {},
        })
        from backend.core.config_model import Config
        self.cfg = Config(parent_logger=logging.getLogger("verify"),
                          config_path=cfg_path)

    def tearDown(self):
        _restore_settings(self._orig)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_get_config_uses_setting_ini_only(self):
        # JSON 残留 E:/stale/mumu，必须读 setting.ini 的 D:\mumu_new
        self.assertEqual(self.cfg.get_config("MuMu安装路径"), "D:\\mumu_new")
        self.assertEqual(self.cfg.get_config("雷电安装路径"), "D:\\ld_new")
        self.assertNotEqual(self.cfg.get_config("MuMu安装路径"), "E:/stale/mumu")

    def test_path_keys_removed_from_setting_dics(self):
        self.assertNotIn("MuMu安装路径", self.cfg.setting_dics)
        self.assertNotIn("雷电安装路径", self.cfg.setting_dics)
        on_disk = json.loads(self.cfg.config_path.read_text(encoding="utf-8"))
        self.assertNotIn("MuMu安装路径", on_disk)
        self.assertNotIn("雷电安装路径", on_disk)

    def test_set_config_writes_setting_ini_only(self):
        self.cfg.set_config("MuMu安装路径", "D:/newest/mumu")
        self.assertNotIn("MuMu安装路径", self.cfg.setting_dics)
        self.assertEqual(self.cfg.get_config("MuMu安装路径"), "D:/newest/mumu")
        self.assertIn("D:/newest/mumu", self.ini_path.read_text(encoding="utf-8"))



class LegacyConfigPathTest(unittest.TestCase):
    """问题2：BaseTask 引用的 legacy.Config 同样只读 setting.ini"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="xuan_verify_legacy_")
        self.ini_path = Path(self.tmp) / "setting.ini"
        self.ini_path.write_text(
            "[助手设置]\r\nMuMu安装路径 = D:\\mumu_legacy\r\n", encoding="utf-8")
        self._orig = _patch_settings(self.ini_path)
        cfg_path = Path(self.tmp) / "Config_Test.json"
        _write_cfg(cfg_path, {
            "配置文件版本": "V3",
            "用户名": "verify_user",
            "MuMu安装路径": "X:/legacy/stale",
            "任务": {},
        })
        from backend.core.legacy.Config import Config
        self.cfg = Config(parent_logger=logging.getLogger("verify"),
                          config_path=cfg_path)

    def tearDown(self):
        _restore_settings(self._orig)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_legacy_get_config_setting_ini_only(self):
        self.assertEqual(self.cfg.get_config("MuMu安装路径"), "D:\\mumu_legacy")
        self.assertNotEqual(self.cfg.get_config("MuMu安装路径"), "X:/legacy/stale")

    def test_legacy_set_config_writes_setting_ini_only(self):
        self.cfg.set_config("雷电安装路径", "D:/ld_legacy")
        self.assertNotIn("雷电安装路径", self.cfg.setting_dics)
        self.assertEqual(self.cfg.get_config("雷电安装路径"), "D:/ld_legacy")


class SchedulerActivationTest(unittest.TestCase):
    """问题1：待激活列表登记 + 任务结束回调统一激活"""

    class _FakeTask:
        """仅用于入队，供 get_task 命中（execute_task_now 在测试中打桩）"""
        def __init__(self, name):
            self.task_name = name
            self.current_status = 2

        def __lt__(self, other):
            return self.task_name < other.task_name

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="xuan_verify_sched_")
        self.ini_path = Path(self.tmp) / "setting.ini"
        self.ini_path.write_text("[助手设置]\r\n", encoding="utf-8")
        self._orig = _patch_settings(self.ini_path)
        cfg_path = Path(self.tmp) / "Config_Test.json"
        _write_cfg(cfg_path, {
            "配置文件版本": "V3",
            "用户名": "verify_user",
            "配置类型": "持久",
            "任务": {
                "一乐外卖": {"是否启用": True, "下次执行时间": 0, "是否临时": False,
                           "基础优先级": 0, "连点优先级": 0, "类型": 0,
                           "执行参数": {}, "执行进度": {}},
                "消耗体力": {"是否启用": False, "下次执行时间": 0, "是否临时": False,
                           "基础优先级": 0, "连点优先级": 0, "类型": 3,
                           "执行参数": {}, "执行进度": {}},
            },
        })
        from backend.core.config_model import Config
        self.cfg = Config(parent_logger=logging.getLogger("verify"),
                          config_path=cfg_path)
        from backend.services.scheduler_service import SchedulerService
        self.sched = SchedulerService(config=self.cfg)
        self.sched.running = True
        # 入队任务（调度器真实 start 时才实例化任务，这里用最小假对象）
        for name in ("消耗体力", "叛忍来袭", "天地战场"):
            self.sched.task_queue.enqueue(self._FakeTask(name))

    def tearDown(self):
        _restore_settings(self._orig)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_activate_request_records_pending_and_dedupes(self):
        self.sched.execute_task_now = unittest.mock.Mock()
        self.sched._on_task_activate_request("消耗体力")
        self.sched._on_task_activate_request("消耗体力")
        self.assertEqual(self.sched._pending_activate_tasks, ["消耗体力"])
        # 登记阶段不立即执行
        self.sched.execute_task_now.assert_not_called()

    def test_process_pending_persistent_mode(self):
        self.sched.execute_task_now = unittest.mock.Mock()
        self.sched.scan = unittest.mock.Mock()
        self.sched.run_once = False
        self.sched._on_task_activate_request("消耗体力")
        self.sched._process_pending_activations()
        self.sched.execute_task_now.assert_called_once_with(
            "消耗体力", enable_if_needed=True, source=SOURCE_ACTIVATION)
        self.sched.scan.assert_called_once()
        self.assertEqual(self.sched._pending_activate_tasks, [])

    def test_process_pending_once_mode_inserts_front(self):
        self.sched.execute_task_now = unittest.mock.Mock()
        self.sched.scan = unittest.mock.Mock()
        self.sched.run_once = True
        self.sched.pending_once_tasks = ["天地战场"]
        self.sched._on_task_activate_request("叛忍来袭")
        self.sched._process_pending_activations()
        self.sched.execute_task_now.assert_called_once_with(
            "叛忍来袭", enable_if_needed=True, source=SOURCE_ACTIVATION)
        # 被激活任务插入预设队列最前，确保下一轮扫描执行
        self.assertEqual(self.sched.pending_once_tasks, ["叛忍来袭", "天地战场"])
        self.assertEqual(self.sched._pending_activate_tasks, [])

    def test_pending_cleared_on_stop(self):
        self.sched._pending_activate_tasks = ["消耗体力"]
        self.sched.stop()
        self.assertEqual(self.sched._pending_activate_tasks, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
