# -*- coding: utf-8 -*-
"""识别器调试日志：按作用域缓冲 + 回放。

`Recognizer.scene(bool_debug=True)` 需要在"匹配成功"时只输出与命中场景相关的日志、
"匹配失败"时输出全部日志。原实现直接内联在 `scene()` 里（120+ 行，动态替换 logger 的
7 个方法），本模块把它抽成两段：

- `capture_logs(logger, scope)`：上下文管理器，作用域内的日志进入内存缓冲；
- `replay_buffered_logs(...)`：按识别结果筛选并回放缓冲日志。

作用域（scope）由 `DebugScope` 承载（`scene:场景名` / `scene:场景名|element:元素名`），
由识别流程在进出场景/元素匹配时设置，日志按 scope 归档以便精确筛选。
"""
import logging
import threading
from contextlib import contextmanager
from typing import Iterable, Iterator, List, Optional, Tuple

from backend.core.legacy.Scene.SceneMeta import UNKNOWN_SCENES

# 缓冲日志条目：(levelno, message, scope)
BufferedLog = Tuple[int, str, Optional[str]]

# 识别可能来自多个线程（每个配置一个调度线程 / API 线程），缓冲依赖对 logger 方法的
# 临时替换，必须串行化以免互相吞日志。debug 模式仅调试期使用，代价可接受。
_CAPTURE_LOCK = threading.RLock()


class DebugScope:
    """当前调试作用域（可变对象，供识别流程嵌套设置/还原）。"""

    __slots__ = ("value",)

    def __init__(self, value: Optional[str] = None):
        self.value = value


def _format_message(msg, args) -> str:
    """把 logging 的 %-style 参数格式化进消息文本（失败时退化为 str 拼接）。"""
    if not args:
        return str(msg)
    try:
        return msg % args
    except Exception:
        try:
            return str(msg) + " " + " ".join(map(str, args))
        except Exception:
            return str(msg)


@contextmanager
def capture_logs(logger: logging.Logger, scope: DebugScope) -> Iterator[List[BufferedLog]]:
    """临时把 logger 的输出改写入内存列表，退出作用域时恢复。

    Args:
        logger: 目标 logger（内部把 debug/info/warning/error/critical/exception/log
            全部替换为缓冲写入）。
        scope: 作用域承载对象，写入时读取其当前值作为日志的 scope 标签。

    Yields:
        List[BufferedLog]：缓冲列表（每条为 levelno/message/scope）。
    """
    buffered: List[BufferedLog] = []
    originals = {
        name: getattr(logger, name)
        for name in ("debug", "info", "warning", "error", "critical", "exception", "log")
    }

    def _make_wrapper(levelno: int):
        def _wrapper(msg, *args, **kwargs):
            text = _format_message(msg, args)
            if kwargs.get("exc_info"):
                text += "\n" + _format_exception(kwargs.get("exc_info"))
            buffered.append((levelno, text, scope.value))
        return _wrapper

    def _exception_wrapper(msg, *args, **kwargs):
        text = _format_message(msg, args) + "\n" + _format_exception(kwargs.get("exc_info"))
        buffered.append((logging.ERROR, text, scope.value))

    def _log_wrapper(levelno, msg, *args, **kwargs):
        buffered.append((levelno, _format_message(msg, args), scope.value))

    with _CAPTURE_LOCK:
        for levelno, name in (
            (logging.DEBUG, "debug"), (logging.INFO, "info"),
            (logging.WARNING, "warning"), (logging.ERROR, "error"),
            (logging.CRITICAL, "critical"),
        ):
            setattr(logger, name, _make_wrapper(levelno))
        logger.exception = _exception_wrapper
        logger.log = _log_wrapper
        try:
            yield buffered
        finally:
            for name, original in originals.items():
                setattr(logger, name, original)


def _format_exception(exc_info) -> str:
    """格式化异常信息（exc_info 为 True/tuple 时取当前或给定异常）。"""
    import sys
    import traceback

    try:
        if exc_info is True or exc_info is None:
            exc_info = sys.exc_info()
        if isinstance(exc_info, tuple):
            return "".join(traceback.format_exception(*exc_info))
    except Exception:
        return ""
    return ""


def replay_buffered_logs(
    logger: logging.Logger,
    buffered: Iterable[BufferedLog],
    result,
    details: Optional[dict] = None,
) -> None:
    """按识别结果筛选并回放缓冲日志。

    规则（与内联实现一致）：
    - 匹配成功且有结构化 details：只回放命中场景作用域（`scene:场景名`）的日志；
    - 匹配成功但无 details：回放命中名字作用域的日志；一条都没有时仅打一条
      `匹配成功: 场景名`（失败场景不匹配是常态，无日志即代表顺利短路）；
    - 匹配失败（None / 未知场景 / 未知含X场景）：回放全部缓冲日志，便于定位。
    """
    items = list(buffered)
    if isinstance(result, str) and result in UNKNOWN_SCENES:
        success = False
    else:
        success = result is not None

    matched_names = set()
    if result is not None:
        matched_names.add(getattr(result, "name", None) or str(result))

    if not success:
        for levelno, message, _scope in items:
            logger.log(levelno, message)
        return

    if details:
        scene_name = details.get("scene")
        wanted = (f"scene:{scene_name}",) if scene_name else ()
    else:
        wanted = tuple(f"scene:{name}" for name in matched_names)

    emitted = 0
    for levelno, message, scope in items:
        if scope and any(tag in scope for tag in wanted):
            logger.log(levelno, message)
            emitted += 1
    if not emitted:
        for name in matched_names:
            logger.debug(f"匹配成功: {name}")


@contextmanager
def scoped(ctx, value: Optional[str]) -> Iterator[None]:
    """在给定上下文里临时设置调试作用域（ctx 无 scope 时为空操作）。"""
    scope = getattr(ctx, "scope", None)
    if scope is None:
        yield
        return
    previous = scope.value
    scope.value = value
    try:
        yield
    finally:
        scope.value = previous


__all__ = ["DebugScope", "BufferedLog", "capture_logs", "replay_buffered_logs", "scoped"]
