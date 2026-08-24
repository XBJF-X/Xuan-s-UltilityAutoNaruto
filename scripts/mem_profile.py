# -*- coding: utf-8 -*-
"""内存实测脚本：分阶段测量 Xuan 后端进程 RSS，定位内存大户（OCR 模型 / SceneGraph 元素图 / 多配置）。

用法：在项目根目录执行
    set PYTHONPATH=<项目根>
    .venv\\Scripts\\python.exe scripts\\mem_profile.py

阶段：
  0 进程基线
  1 import backend.main
  2 ConfigService 初始化（加载全部配置）
  3 共享 SceneGraph 加载（解码全部元素图）
  4 多配置 SchedulerService 构造（不启动）
  5 首个 OnnxOcr 模型加载（det+rec，~172MB 文件）
  6 第二份 OnnxOcr 模型加载（模拟第二个配置）→ 验证多配置是否翻倍
  7 单次 OCR 推理
"""
import io
import os
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

try:
    import psutil
except ImportError:
    print("缺少 psutil，请先安装：.venv\\Scripts\\pip install psutil")
    sys.exit(1)

_proc = psutil.Process(os.getpid())
_stage_rss = {}


def rss_mb() -> float:
    return _proc.memory_info().rss / 1024 / 1024


def gc_collect():
    import gc
    gc.collect()


def stage(name: str) -> None:
    gc_collect()
    _stage_rss[name] = rss_mb()
    prev = _stage_rss["0-进程基线"] if "0-进程基线" in _stage_rss else 0
    print(f"[{name}] RSS={_stage_rss[name]:8.1f} MB  (相对基线 +{_stage_rss[name] - prev:8.1f} MB)")


print(f"进程 PID={os.getpid()}")
stage("0-进程基线")

# ---- 1. import backend.main ----
import backend.main  # noqa: E402
stage("1-import backend.main")

# ---- 2. ConfigService 初始化 + 加载全部配置 ----
from backend.services.config_service import shared_config_service as _cs  # noqa: E402
cfg_list = _cs.list_configs()
print(f"    现有配置数: {len(cfg_list)}  ids={[c['id'] for c in cfg_list]}")
stage("2-ConfigService 初始化")

# ---- 3. 共享 SceneGraph 加载（解码全部元素图） ----
from backend.services.scheduler_service import get_shared_scene_graph  # noqa: E402
t0 = time.perf_counter()
sg = get_shared_scene_graph()
gc_collect()
stage("3-共享 SceneGraph 加载")
print(f"    SceneGraph 场景数={len(sg.scenes)}  加载耗时={time.perf_counter() - t0:.1f}s")

# ---- 4. 多配置 SchedulerService 构造（不启动，模拟多开） ----
from backend.services.scheduler_service import SchedulerService  # noqa: E402
scheds = []
for c in cfg_list[:4]:
    cfg = _cs.get_config(c["id"])
    if cfg is not None:
        scheds.append(SchedulerService(cfg))
stage("4-多配置 SchedulerService 构造")
print(f"    构造 {len(scheds)} 个 SchedulerService")

# ---- 5. 共享 OnnxOcr 首次加载（A：全局共享单例） ----
from backend.core.legacy.OnnxOcr import get_shared_onnx_ocr  # noqa: E402
t0 = time.perf_counter()
ocr1 = get_shared_onnx_ocr()
stage("5-共享 OnnxOcr 首次加载")
print(f"    加载耗时={time.perf_counter() - t0:.1f}s")

# ---- 6. 再次获取共享 OnnxOcr（模拟第二个配置，验证共享复用） ----
ocr2 = get_shared_onnx_ocr()
stage("6-再次获取共享 OnnxOcr")
print(f"    再次获取增量 = {_stage_rss['6-再次获取共享 OnnxOcr'] - _stage_rss['5-共享 OnnxOcr 首次加载']:.1f} MB  (共享后应为 ~0)")
assert ocr1 is ocr2, "共享单例应返回同一实例"

# ---- 7. 单次 OCR 推理（验证共享可行性/内存） ----
import numpy as np  # noqa: E402
dummy = np.full((320, 320, 3), 255, dtype=np.uint8)
ocr1.ocr(dummy, None)
stage("7-单次 OCR 推理后")

print("\n===== 各阶段增量汇总 =====")
base = _stage_rss["0-进程基线"]
for name in list(_stage_rss)[1:]:
    print(f"  {name}: +{_stage_rss[name] - base:8.1f} MB")
