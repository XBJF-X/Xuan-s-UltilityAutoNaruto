# -*- coding: utf-8 -*-
"""验证：OCR GPU(DirectML) 推理失败后自动 CPU 兜底 + open-log-dir 目录解析/打开

运行：.venv\\Scripts\\python.exe test_scene\\verify_ocr_cpu_fallback.py
（全部通过打印 "ALL PASS (n 项)"；任一失败抛出 AssertionError）
"""
import sys
import logging
import tempfile
import threading
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_PASS = [0]


def check(cond: bool, msg: str):
    assert cond, f"FAIL: {msg}"
    _PASS[0] += 1
    print(f"  PASS: {msg}")


# ============ 1. OnnxOcr CPU 兜底逻辑（不加载真实模型，monkeypatch 引擎） ============
import backend.core.legacy.OnnxOcr as ocr_mod
from backend.core.legacy.OnnxOcr import OnnxOcr


class _FakeEngine:
    """模拟 OCR 引擎：fail=True 时推理抛异常，否则返回空结果"""

    def __init__(self, name: str, fail: bool = False):
        self.name = name
        self.fail = fail
        self.ocr_calls = 0

    def ocr(self, image):
        self.ocr_calls += 1
        if self.fail:
            raise RuntimeError(f"[{self.name}] DML inference failed (mock)")
        return []


def _make_instance(engine: _FakeEngine, cpu_fallback: bool = False) -> OnnxOcr:
    inst = object.__new__(OnnxOcr)
    inst.logger = logging.getLogger("verify-ocr-cpu-fallback")
    inst.logger.setLevel(logging.CRITICAL)  # 静默测试日志
    inst.engine = engine
    inst._lock = threading.Lock()
    inst._cpu_fallback = cpu_fallback
    return inst


print("[1] OCR GPU 失败 -> 自动 CPU 兜底")
_build_calls: list = []
_orig_factory = ocr_mod.ONNXPaddleOcr


def _fake_factory(**kwargs):
    _build_calls.append(dict(kwargs))
    return _FakeEngine("cpu", fail=False)


ocr_mod.ONNXPaddleOcr = _fake_factory
try:
    gpu = _FakeEngine("gpu", fail=True)
    inst = _make_instance(gpu)
    res = inst.ocr(None, None, raw_json=True)
    check(inst._cpu_fallback is True, "GPU 失败后自动切为 CPU 兜底模式")
    check(gpu.ocr_calls == 1, "GPU 引擎仅被尝试一次")
    check(inst.engine.name == "cpu" and inst.engine.ocr_calls == 1, "CPU 引擎重建并重试成功")
    check(res == [], "CPU 兜底结果正常返回")
    check(len(_build_calls) == 1 and _build_calls[0]["use_gpu"] is False,
          "重建引擎 use_gpu=False")

    # 后续调用直接走 CPU，不再触发重建
    inst.ocr(None, None)
    check(len(_build_calls) == 1, "切换后后续识别不再重复重建/尝试 GPU")
    check(inst.engine.ocr_calls == 2, "后续识别直接走 CPU 引擎")

    # CPU 引擎自身失败（真实错误）时应原样抛出
    inst.engine.fail = True
    try:
        inst.ocr(None, None)
        check(False, "CPU 引擎失败应抛出异常")
    except RuntimeError:
        check(True, "CPU 兜底引擎失败时异常原样抛出")

    # 初始即 CPU 模式（use_gpu=False 构建）失败时不尝试重建，直接抛出
    cpu = _FakeEngine("cpu", fail=True)
    inst2 = _make_instance(cpu, cpu_fallback=True)
    try:
        inst2.ocr(None, None)
        check(False, "初始 CPU 模式失败应抛出异常")
    except RuntimeError:
        check(True, "初始 CPU 模式失败直接抛出，不做无谓重建")
    check(len(_build_calls) == 1, "初始 CPU 模式失败不触发重建")
finally:
    ocr_mod.ONNXPaddleOcr = _orig_factory


# ============ 2. open-log-dir：目录层级解析 + os.startfile 打开 ============
print("[2] open-log-dir 目录解析与打开")
import backend.api.utils as utils_mod

_tmp = Path(tempfile.mkdtemp(prefix="xuan_verify_log_"))
_log_root = _tmp / "log"
(_log_root / "TestUser" / "2026-09-05").mkdir(parents=True)
(_log_root / "TestUser" / "2026-09-07").mkdir(parents=True)
(_log_root / "TestUser" / "2026-09-06").mkdir(parents=True)
# 09-05 无日志，09-06/09-07 有日志
(_log_root / "TestUser" / "2026-09-06" / "Xuan.log").write_text("x", encoding="utf-8")
(_log_root / "TestUser" / "2026-09-07" / "Xuan.log").write_text("x", encoding="utf-8")
# 非日期目录/无日志目录不应被选中
(_log_root / "TestUser" / "screenshot").mkdir(parents=True, exist_ok=True)

_opened: list = []
_orig_get_real_path = utils_mod.get_real_path
_orig_get_username = utils_mod._get_config_username
_orig_startfile = utils_mod.os.startfile
utils_mod.os.startfile = lambda p: _opened.append(Path(p))


def _reset(username_map=None):
    _opened.clear()
    utils_mod.get_real_path = lambda key: str(_log_root if key == "log" else _tmp)
    utils_mod._get_config_username = lambda cid: (username_map or {}).get(cid, "")


try:
    # 2.1 最近含日志的日期目录
    _reset({"Config_1": "TestUser"})
    r = utils_mod.open_log_dir("Config_1")
    check(r["ok"] is True and Path(r["path"]) == _log_root / "TestUser" / "2026-09-07",
          "打开最近含日志的日期目录 log/TestUser/2026-09-07")
    check(len(_opened) == 1 and _opened[0] == _log_root / "TestUser" / "2026-09-07",
          "os.startfile 打开的是 2026-09-07 目录")

    # 2.2 无日期目录 -> 退回用户目录（自动创建）
    _reset({"Config_2": "NewUser"})
    r = utils_mod.open_log_dir("Config_2")
    check(r["ok"] is True and Path(r["path"]) == _log_root / "NewUser",
          "无日期目录时退回 log/NewUser 并自动创建")
    check((_log_root / "NewUser").is_dir(), "log/NewUser 目录已创建")

    # 2.3 用户名取不到 -> 退回 log 根目录
    _reset(None)
    r = utils_mod.open_log_dir("Config_Nonexistent")
    check(r["ok"] is True and Path(r["path"]) == _log_root, "取不到用户名时退回 log 根目录")

    # 2.4 空 config / __global__ -> 打开 log 根目录
    for cid in ("", "__global__"):
        _reset({"Config_1": "TestUser"})
        r = utils_mod.open_log_dir(cid)
        check(r["ok"] is True and Path(r["path"]) == _log_root, f"config_id='{cid}' 打开 log 根目录")

    # 2.5 纯解析辅助：只认含日志文件的日期目录
    latest = utils_mod._latest_log_date_dir(_log_root / "TestUser")
    check(latest == _log_root / "TestUser" / "2026-09-07", "_latest_log_date_dir 返回含日志的最近日期目录")
    latest2 = utils_mod._latest_log_date_dir(_log_root / "NewUser")
    check(latest2 is None, "无日期目录时 _latest_log_date_dir 返回 None")
finally:
    utils_mod.get_real_path = _orig_get_real_path
    utils_mod._get_config_username = _orig_get_username
    utils_mod.os.startfile = _orig_startfile

print(f"\nALL PASS ({_PASS[0]} 项)")
