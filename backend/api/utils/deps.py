"""依赖与 OCR 加速探测（`/dependency-check` 与启动引导弹窗的数据来源）。

阶段 3.4：由 backend/api/utils.py 拆分而来；
模块级 logger 名为 "backend.api.utils"（与拆分前一致，保证日志连续性与
既有测试的 assertLogs("backend.api.utils") 继续有效）。"""
import threading
import time

import logging

from backend.api.utils.common import (
    _DEPENDENCY_PROBE_MODULES,
    _get_releases_url,
    _read_local_version,
    _read_min_release_tag,
    _version_gt,
)
from typing import Optional

from fastapi import APIRouter

logger = logging.getLogger("backend.api.utils")

router = APIRouter()


# ============================================================
# OCR GPU(DirectML) 加速可用性检查
# ============================================================
# v0.17.17 起 OCR 默认走 onnxruntime 的 DirectML(DmlExecutionProvider) GPU 加速
# （实测单次推理 92.7ms → 39.8ms）。若本地依赖库仍是标准 onnxruntime（不含 DML
# provider），OnnxOcr 会**静默回退 CPU 推理**（只在 stderr 留一句提示，日志里看不到），
# 表现为调度器跑任务时 CPU 占用呈尖峰状偏高。故此处探测一次并由前端弹窗提示用户
# 前往 Release 覆盖安装 v0.17.17+（依赖库随安装包分发，热更新不携带）。
_OCR_ACCEL_MIN_TAG = "v0.17.17"
_OCR_ACCEL_HINT = (
    f"当前依赖库不支持Ocr GPU加速，请到项目主页下载{_OCR_ACCEL_MIN_TAG}以上的最新Release覆盖安装"
)
_OCR_ACCEL_CACHE: Optional[dict] = None
_OCR_ACCEL_LOCK = threading.Lock()


def _probe_onnxruntime_providers() -> dict:
    """探测 onnxruntime 的可用 providers / 版本 / 发行包名。

    独立成函数便于单测打桩（真实调用会 import onnxruntime，实测 ~0.3s）。

    Returns:
        dict: ``{providers: list[str], version: str, package: str, error: str}``，
              ``error`` 非空表示探测失败（如未安装 onnxruntime）。
    """
    import importlib.util

    info = {"providers": [], "version": "", "package": "", "error": ""}
    try:
        if importlib.util.find_spec("onnxruntime") is None:
            info["error"] = "onnxruntime 未安装"
            return info
    except Exception as e:
        info["error"] = f"onnxruntime 探测失败: {e}"
        return info

    try:
        import onnxruntime  # 重型导入：结果被 check_ocr_accel 缓存，仅执行一次
        info["providers"] = list(onnxruntime.get_available_providers() or [])
        info["version"] = str(getattr(onnxruntime, "__version__", "") or "")
    except Exception as e:
        info["error"] = f"onnxruntime 导入失败: {e}"
        return info

    # 发行包名：只有 onnxruntime-directml 才带 DmlExecutionProvider。
    # 装有 directml 包时 metadata 中 onnxruntime-directml 有版本、onnxruntime 无，
    # 因此按 directml → gpu → 标准 的顺序取第一个可查到的发行包名。
    try:
        import importlib.metadata as md
        for dist in ("onnxruntime-directml", "onnxruntime-gpu", "onnxruntime"):
            try:
                md.version(dist)
                info["package"] = dist
                break
            except Exception:
                continue
    except Exception:
        pass
    return info


def _ocr_accel_enabled() -> bool:
    """读取 [助手设置] OCR加速 开关（默认开启）。"""
    try:
        from backend.services.settings_service import SettingsService
        return SettingsService().getboolean("助手设置", "OCR加速", default=True)
    except Exception:
        return True


def _copy_accel_result(result: dict) -> dict:
    """返回探测结果副本（``providers`` 是可变列表，避免调用方修改污染缓存）。"""
    out = dict(result)
    out["providers"] = list(result.get("providers") or [])
    return out


def check_ocr_accel(refresh: bool = False) -> dict:
    """OCR GPU(DirectML) 加速可用性检查（结果缓存，避免重复重型导入）。

    Returns:
        dict: {
          ``supported``: DML provider 是否可用（依赖库能力）；
          ``enabled``: [助手设置] OCR加速 开关；
          ``needs_notice``: 是否需要前端弹窗提示（依赖库不支持 GPU 加速）；
          ``reason``: ok / no_dml_provider / not_installed / disabled_by_setting；
          ``providers`` / ``onnxruntime_version`` / ``package``: 探测详情（供反馈定位）；
          ``min_release_tag``: 满足 GPU 加速的最低 Release 版本；
          ``message``: 面向用户的提示（``needs_notice`` 时非空）。
        }
    """
    global _OCR_ACCEL_CACHE
    if _OCR_ACCEL_CACHE is not None and not refresh:
        return _copy_accel_result(_OCR_ACCEL_CACHE)

    with _OCR_ACCEL_LOCK:
        if _OCR_ACCEL_CACHE is not None and not refresh:
            return _copy_accel_result(_OCR_ACCEL_CACHE)

        probe = _probe_onnxruntime_providers()
        enabled = _ocr_accel_enabled()
        supported = "DmlExecutionProvider" in probe["providers"]

        if probe["error"]:
            reason, message = "not_installed", ""
        elif not supported:
            reason, message = "no_dml_provider", _OCR_ACCEL_HINT
        elif not enabled:
            reason, message = "disabled_by_setting", ""
        else:
            reason, message = "ok", ""

        result = {
            "supported": supported,
            "enabled": enabled,
            "needs_notice": reason == "no_dml_provider",
            "reason": reason,
            "providers": probe["providers"],
            "onnxruntime_version": probe["version"],
            "package": probe["package"],
            "min_release_tag": _OCR_ACCEL_MIN_TAG,
            "message": message,
        }
        _OCR_ACCEL_CACHE = result

        if reason == "no_dml_provider":
            logger.warning(
                "OCR GPU加速不可用：onnxruntime 发行包=%s providers=%s，OCR 将回退 CPU "
                "推理（CPU 占用升高呈尖峰）。%s",
                probe["package"] or "未知", probe["providers"], _OCR_ACCEL_HINT)
        elif reason == "ok":
            logger.info("OCR GPU加速可用：providers=%s package=%s version=%s",
                        probe["providers"], probe["package"] or "未知",
                        probe["version"] or "未知")
        else:
            logger.warning("OCR GPU加速检查异常：reason=%s enabled=%s error=%s",
                           reason, enabled, probe["error"] or "-")
        return _copy_accel_result(result)



def check_dependency(include_ocr: bool = False) -> dict:
    """依赖健康检查：本 commit 所需依赖库版本是否满足 + 关键 Python 依赖是否缺失。

    用于：①调度器启动前硬拦截（不满足禁止启动，防止因代码依赖新依赖库导致任务恶性 BUG）；
         ②前端启动时弹窗提示用户前往 Release 下载完整安装包。

    Args:
        include_ocr: 是否附带 OCR GPU(DirectML) 加速可用性检查（``ocr_accel`` 字段）。
            OCR 探测会 import onnxruntime（实测 ~0.3s，结果缓存），因此仅前端启动检查
            走 ``True``；调度器启动拦截等高频路径保持 ``False``，避免多余的重型导入。
    """
    import importlib.util

    local_version = _read_local_version()
    required_tag, required_version = _read_min_release_tag()
    deprecated = (
        bool(required_version)
        and bool(local_version)
        and _version_gt(required_version, local_version)
    )

    missing_modules = []
    for mod_name in _DEPENDENCY_PROBE_MODULES:
        try:
            spec = importlib.util.find_spec(mod_name)
            if spec is None:
                missing_modules.append(mod_name)
        except (ImportError, AttributeError):
            missing_modules.append(mod_name)
        except Exception:
            # 其余异常（模块自身初始化报错等）不归类为缺失，避免误报
            pass

    result = {
        "ok": not deprecated and not missing_modules,
        "deprecated": deprecated,
        "local_version": local_version,
        "required_tag": required_tag,
        "required_version": required_version,
        "missing_modules": missing_modules,
        "release_url": _get_releases_url(),
    }
    if include_ocr:
        # OCR GPU 加速可用性（不参与 ok 判定：不可用时 OCR 自动走 CPU 兜底，功能不受影响，
        # 只影响性能与 CPU 占用，故单独一项由前端弹窗提示）
        result["ocr_accel"] = check_ocr_accel()
    return result
