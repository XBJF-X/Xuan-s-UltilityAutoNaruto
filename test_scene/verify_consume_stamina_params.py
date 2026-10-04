# -*- coding: utf-8 -*-
"""验证「任务执行后是否消耗体力」开关 + 「检查更新」弹窗展示当前版本。

任务参数（schema 唯一来源 src/DefaultConfig.json，缺省值必须与旧行为等价）：
  - [一乐外卖] `领取后消耗体力`（BOOL，默认 true）：领到外卖时是否激活「消耗体力」
  - [购买体力] `购买后消耗体力`（BOOL，默认 true）：购买流程结束后是否激活「消耗体力」

版本展示：
  - 后端新增 `GET /api/utils/version`（只读根目录 _version.py，不访问更新源）
  - `check-update` 顶层（含失败分支）也带 `local_version`，前端 UpdateDialog 顶部展示

覆盖断言：
  A. DefaultConfig schema（类型/默认值/描述/参数名）
  B. 一乐外卖流程：缺省→激活（旧行为）/ True→激活 / False→不激活 / 未领到→不激活
  C. 购买体力流程：缺省→激活 / True→激活 / False→不激活 / 仍在购买中→不激活
  D. /utils/version 与 check-update 顶层 local_version（伪响应，不访问真实网络）
  E. 前端 UpdateDialog.vue / client.ts 的版本展示接线
"""
import asyncio
import json
import logging
import re
import sys
import unittest
from pathlib import Path
from unittest import mock

logging.basicConfig(level=logging.CRITICAL)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from backend.api import utils as utils_api                      # noqa: E402
from backend.core.legacy.Exceptions import TaskCompleted        # noqa: E402
from backend.core.legacy.Task.GouMaiTiLi import (               # noqa: E402
    PARAM_CONSUME_STAMINA as GOUMAI_PARAM,
    GouMaiTiLi,
)
from backend.core.legacy.Task.YiLeWaiMai import (               # noqa: E402
    PARAM_CONSUME_STAMINA as YILE_PARAM,
    YiLeWaiMai,
)

DEFAULT_CONFIG = _PROJECT_ROOT / "src" / "DefaultConfig.json"
YI_LE_TASK = "一乐外卖"
GOUMAI_TASK = "购买体力"


def _read_version_file() -> str:
    """直接解析根目录 _version.py（独立于被测实现，避免自证）。"""
    text = (_PROJECT_ROOT / "_version.py").read_text(encoding="utf-8")
    m = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
    return m.group(1).strip() if m else ""


class _FakeConfig:
    """最小 Config 替身：只实现 get_task_exe_param（缺省回落到调用方默认值）。"""

    def __init__(self, params=None):
        self.params = params or {}

    def get_task_exe_param(self, task_name, param_name, default=None):
        return self.params.get((task_name, param_name), default)


class _FakeOperationer:
    """按脚本返回 click_and_wait 结果，并记录点击顺序。"""

    def __init__(self, click_results=None, ocr_map=None):
        self._click_results = list(click_results or [])
        self.ocr_map = ocr_map or {}
        self.clicks = []

    def click_and_wait(self, element, **kwargs):
        self.clicks.append(element)
        if self._click_results:
            return self._click_results.pop(0)
        return True

    def ocr_recognize(self, element, **kwargs):
        return self.ocr_map.get(element)


class _FakeRemainTimes:
    """「剩余购买次数」OCR 结果替身。

    与 `OcrResultList` 的实际用法对齐：GouMaiTiLi 取数字走 `get_first_number()`，
    失败分支会打印 `texts()`（2026-09-15 健壮性改造后新增的 API）。
    """

    def __init__(self, numbers):
        self.numbers = list(numbers)

    def get_first_number(self):
        return self.numbers[0] if self.numbers else None

    def texts(self):
        return [str(n) for n in self.numbers]

    def is_greater_than(self, value):
        return bool(self.numbers) and self.numbers[0] > value

    def extract_all_numbers(self):
        return list(self.numbers)


def _make_task(cls, params=None, click_results=None, ocr_map=None):
    task = object.__new__(cls)
    task.logger = logging.getLogger("verify.consume")
    task.task_name = GOUMAI_TASK if cls is GouMaiTiLi else YI_LE_TASK
    task.config = _FakeConfig(params)
    task.operationer = _FakeOperationer(click_results, ocr_map)
    task.target_buy_times = 2
    activated = []
    task._activate_another_task = lambda name, **kw: activated.append(name)
    return task, activated


class SchemaTest(unittest.TestCase):
    """A. src/DefaultConfig.json 的参数 schema（前端面板的唯一数据源）"""

    def _param(self, task_name, param_name):
        schema = json.loads(DEFAULT_CONFIG.read_text(encoding="utf-8"))
        return schema["任务"][task_name]["执行参数"][param_name]

    def test_params_are_bool_default_true(self):
        for task_name, param_name in ((YI_LE_TASK, YILE_PARAM),
                                     (GOUMAI_TASK, GOUMAI_PARAM)):
            with self.subTest(task=task_name):
                param = self._param(task_name, param_name)
                self.assertEqual(param["类型"], "BOOL")
                self.assertIs(param["当前值"], True, "缺省必须等价于旧行为（会消耗体力）")
                self.assertTrue(param["描述"], "描述要写明默认值与关闭后的影响")
                self.assertNotIn("/", param_name, "参数名不能含斜杠（URL 拼接）")

    def test_param_names(self):
        self.assertEqual(YILE_PARAM, "领取后消耗体力")
        self.assertEqual(GOUMAI_PARAM, "购买后消耗体力")


class YiLeWaiMaiFlowTest(unittest.TestCase):
    """B. 一乐外卖：领取后是否激活消耗体力"""

    SCENE = YI_LE_TASK
    # 两次领到外卖后 while 退出（第三次返回 False）
    CLICKS = [True, True, False]

    def _run(self, params):
        task, activated = _make_task(YiLeWaiMai, params, self.CLICKS)
        with self.assertRaises(TaskCompleted):
            YiLeWaiMai.transition_func[self.SCENE](task)
        return task, activated

    def test_param_missing_activates_legacy_behaviour(self):
        task, activated = self._run({})
        self.assertEqual(activated, ["消耗体力"], "缺省（老配置）必须保持旧行为")
        self.assertIn("X", task.operationer.clicks, "收尾仍需关闭外卖窗口")

    def test_param_true_activates(self):
        _task, activated = self._run({(YI_LE_TASK, YILE_PARAM): True})
        self.assertEqual(activated, ["消耗体力"])

    def test_param_false_skips(self):
        _task, activated = self._run({(YI_LE_TASK, YILE_PARAM): False})
        self.assertEqual(activated, [], "关闭开关后不得激活消耗体力")

    def test_no_takeout_never_activates(self):
        task, activated = _make_task(YiLeWaiMai, {(YI_LE_TASK, YILE_PARAM): True},
                                     [False])
        with self.assertRaises(TaskCompleted):
            YiLeWaiMai.transition_func[self.SCENE](task)
        self.assertEqual(activated, [], "没领到外卖时不应消耗体力")


class GouMaiTiLiFlowTest(unittest.TestCase):
    """C. 购买体力：购买流程结束后是否激活消耗体力"""

    SCENE = "购买体力"

    def _run(self, params, remain=0):
        ocr_map = {"剩余购买次数": _FakeRemainTimes([remain])}
        task, activated = _make_task(GouMaiTiLi, params, ocr_map=ocr_map)
        with self.assertRaises(TaskCompleted):
            GouMaiTiLi.transition_func[self.SCENE](task)
        return task, activated

    def test_param_missing_activates_legacy_behaviour(self):
        task, activated = self._run({})
        self.assertEqual(activated, ["消耗体力"], "缺省（老配置）必须保持旧行为")
        self.assertEqual(task.operationer.clicks, ["X"], "先关闭购买窗口再激活")

    def test_param_true_activates(self):
        _task, activated = self._run({(GOUMAI_TASK, GOUMAI_PARAM): True})
        self.assertEqual(activated, ["消耗体力"])

    def test_param_false_skips(self):
        task, activated = self._run({(GOUMAI_TASK, GOUMAI_PARAM): False})
        self.assertEqual(activated, [], "关闭开关后不得激活消耗体力")
        self.assertEqual(task.operationer.clicks, ["X"])

    def test_still_buying_never_activates(self):
        """剩余次数仍大于目标值 → 继续购买并 return，不得到收尾激活分支"""
        ocr_map = {"剩余购买次数": _FakeRemainTimes([5])}
        task, activated = _make_task(GouMaiTiLi, {(GOUMAI_TASK, GOUMAI_PARAM): True},
                                     ocr_map=ocr_map)
        self.assertFalse(GouMaiTiLi.transition_func[self.SCENE](task))
        self.assertEqual(activated, [], "购买过程中不得激活消耗体力")
        self.assertEqual(task.operationer.clicks, ["购买"])


class _FakeResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self.content = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8")


def _fake_requests_get(url, **kwargs):
    """伪更新源：分支/提交列表返回 200，Releases 均返回 404（不访问真实网络）。"""
    sha = "b" * 40
    if "/branches/" in url:
        return _FakeResponse(200, {"commit": {"sha": sha,
                                              "commit": {"message": "feat: fake"}}})
    if url.endswith("/commits"):
        return _FakeResponse(200, [{
            "sha": sha,
            "commit": {"message": "feat: fake",
                       "committer": {"date": "2026-09-12T00:00:00Z"},
                       "author": {"name": "tester"}},
        }])
    return _FakeResponse(404)


class LocalVersionApiTest(unittest.TestCase):
    """D. /utils/version 与 check-update 顶层的 local_version"""

    def test_version_endpoint_reads_version_file(self):
        # get_local_version 仍是 async（只读一个小文件，开销可忽略）；
        # check_update / dependency-check / log-history 已改为同步端点（走线程池）
        res = asyncio.run(utils_api.get_local_version())
        self.assertTrue(res["ok"])
        self.assertEqual(res["version"], _read_version_file())

    def test_check_update_returns_local_version(self):
        with mock.patch("backend.api.utils.requests.get",
                        side_effect=_fake_requests_get):
            res = utils_api.check_update()
        self.assertTrue(res["ok"], res)
        self.assertEqual(res["local_version"], _read_version_file())
        self.assertEqual(res["update_type"], "hot", "伪更新源应识别为热更新")

    def test_check_update_offline_still_returns_local_version(self):
        """更新源不可达（网络异常）时也必须带 local_version，供弹窗展示"""
        with mock.patch("backend.api.utils.requests.get",
                        side_effect=Exception("network down")):
            res = utils_api.check_update()
        self.assertFalse(res["ok"])
        self.assertEqual(res["local_version"], _read_version_file())


class FrontendWiringTest(unittest.TestCase):
    """E. 前端接线：UpdateDialog 展示当前版本、client.ts 暴露 /utils/version"""

    def test_update_dialog_shows_local_version(self):
        vue = (_PROJECT_ROOT / "frontend/src/components/UpdateDialog.vue"
               ).read_text(encoding="utf-8")
        self.assertIn("当前客户端版本", vue)
        self.assertIn("localVersion", vue)
        self.assertIn("utilsApi.localVersion()", vue, "弹窗打开即读取本地版本")
        self.assertIn("data?.local_version", vue, "check-update 响应也用于补版本")

    def test_client_exposes_version_api(self):
        ts = (_PROJECT_ROOT / "frontend/src/api/client.ts").read_text(encoding="utf-8")
        self.assertIn("localVersion: () => client.get('/utils/version')", ts)


if __name__ == "__main__":
    unittest.main(verbosity=2)
