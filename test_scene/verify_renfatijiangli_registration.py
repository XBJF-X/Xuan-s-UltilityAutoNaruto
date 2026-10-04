# -*- coding: utf-8 -*-
"""验证 [忍法帖奖励]（RenFaTieJiangLi）已正确注册，程序可识别加载。

覆盖：
1. Task/__init__.py：导入 + TASK_TYPE_MAP（中文名→类）+ TASK_NAME_CN2EN_MAP 一致性；
2. src/DefaultConfig.json：条目存在、类别=每周(类型 1)、优先级与[情报站]一致；
3. V3 配置合并：存量用户配置（不含该任务）加载后自动补齐条目。
"""
import json
import logging
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from backend.core.legacy.Task import TASK_NAME_CN2EN_MAP, TASK_TYPE_MAP
from backend.core.legacy.Task.BaseTask import BaseTask
from backend.core.legacy.Task.RenFaTieJiangLi import RenFaTieJiangLi

TASK_CN = "忍法帖奖励"
REF_TASK_CN = "情报站"
DEFAULT_CONFIG = Path(_PROJECT_ROOT) / "src" / "DefaultConfig.json"


def _load_default_tasks():
    return json.loads(DEFAULT_CONFIG.read_text(encoding="utf-8"))["任务"]


def _patch_settings(ini_path):
    import backend.services.settings_service as ss_mod
    from backend.core.setting_model import Setting

    setting = Setting(parent_logger=logging.getLogger("verify"),
                      setting_path=ini_path)
    orig = ss_mod.SettingsService._get_setting
    ss_mod.SettingsService._get_setting = lambda self: setting
    return orig


def _restore_settings(orig):
    import backend.services.settings_service as ss_mod
    ss_mod.SettingsService._get_setting = orig


class TaskMapTest(unittest.TestCase):

    def test_registered_in_type_map(self):
        self.assertIn(TASK_CN, TASK_TYPE_MAP)
        self.assertIs(TASK_TYPE_MAP[TASK_CN], RenFaTieJiangLi)
        self.assertTrue(issubclass(TASK_TYPE_MAP[TASK_CN], BaseTask))

    def test_registered_in_cn2en_map(self):
        self.assertEqual(TASK_NAME_CN2EN_MAP.get(TASK_CN), "RenFaTieJiangLi")

    def test_new_task_class_matches_module(self):
        cls = TASK_TYPE_MAP[TASK_CN]
        self.assertEqual(cls.__name__, "RenFaTieJiangLi")
        self.assertTrue(cls.__module__.endswith("RenFaTieJiangLi"))

    def test_maps_are_consistent(self):
        self.assertEqual(set(TASK_TYPE_MAP), set(TASK_NAME_CN2EN_MAP))
        for cn, cls in TASK_TYPE_MAP.items():
            self.assertEqual(cls.__name__, TASK_NAME_CN2EN_MAP[cn], cn)


class DefaultConfigTest(unittest.TestCase):

    def test_entry_exists_with_weekly_type(self):
        tasks = _load_default_tasks()
        self.assertIn(TASK_CN, tasks)
        self.assertEqual(tasks[TASK_CN]["类型"], 1, "类别应为每周任务（类型=1）")

    def test_priority_same_as_reference_task(self):
        tasks = _load_default_tasks()
        entry, ref = tasks[TASK_CN], tasks[REF_TASK_CN]
        self.assertEqual(entry["连点优先级"], ref["连点优先级"])
        self.assertEqual(entry["基础优先级"], ref["基础优先级"])

    def test_entry_defaults(self):
        entry = _load_default_tasks()[TASK_CN]
        self.assertFalse(entry["是否启用"])
        self.assertEqual(entry["下次执行时间"], 0)
        self.assertFalse(entry["是否临时"])
        self.assertEqual(entry["执行参数"], {})
        self.assertEqual(entry["执行进度"], {})
        self.assertTrue(entry["描述"])


class LegacyConfigMergeTest(unittest.TestCase):
    """存量配置（不含该任务）加载后应自动补齐条目"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="xuan_verify_reg_")
        ini_path = Path(self.tmp) / "setting.ini"
        ini_path.write_text("[助手设置]\r\n", encoding="utf-8")
        self._orig = _patch_settings(ini_path)

    def tearDown(self):
        _restore_settings(self._orig)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_merged_into_existing_config(self):
        cfg_path = Path(self.tmp) / "Config_Test.json"
        cfg_path.write_text(json.dumps({
            "配置文件版本": "V3",
            "用户名": "verify_user",
            "配置类型": "持久",
            "任务": {REF_TASK_CN: {"是否启用": True, "下次执行时间": 0,
                                 "执行参数": {}, "执行进度": {},
                                 "连点优先级": 0, "基础优先级": 9,
                                 "类型": 0, "是否临时": False}},
        }, ensure_ascii=False), encoding="utf-8")
        from backend.core.config_model import Config
        cfg = Config(parent_logger=logging.getLogger("verify"),
                     config_path=cfg_path)
        self.assertIn(TASK_CN, cfg.tasks, "存量配置应自动补齐新任务条目")
        entry = cfg.tasks[TASK_CN]
        self.assertEqual(entry["类型"], 1)
        self.assertEqual(entry["连点优先级"], 0)
        self.assertEqual(entry["基础优先级"], 9)
        self.assertFalse(entry["是否启用"])
        # 调度器 _lazy_init 的取类方式：按中文名从映射表取任务类
        self.assertIs(TASK_TYPE_MAP.get(TASK_CN), RenFaTieJiangLi)


if __name__ == "__main__":
    unittest.main(verbosity=2)