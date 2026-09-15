# -*- coding: utf-8 -*-
"""设备端残留触点（粘滞多点触摸）检测与清理。

背景（v0.17.46）
----------------
evdev 的 MT slot 状态属于**内核/模拟器侧**状态：minitouch 进程被终止时不会自动
抬起触点。若进程恰好死在 ``multi_tap`` 批次「已按下、未抬起」的窗口内（批次里
有 ``w 80`` 的停留期），这些 slot 会**永久停留按下态**；此后任何一次触摸都会被
Android 的 ``MotionEvent`` 当成同一手势，把残留的 pointer 一起上报给游戏——
表现就是「点一下屏幕同时触发所有之前预设好的连点坐标」，且只能重启模拟器。

更糟的是 ``minitouch`` 的 ``u`` 命令只对「该进程自己记录过按下的 slot」生效，
所以事后换一个连接/实例再发 ``u`` 是**空操作**（已实测）。

本模块不依赖 minitouch，直接用 ``getevent`` 找出多点触摸设备、用 ``sendevent``
写裸 evdev 的 MT 抬起序列（``ABS_MT_SLOT`` + ``ABS_MT_TRACKING_ID=-1`` +
``SYN_REPORT``），作为「连点停止 / 控制实例释放 / 调度器启停」时的兜底清理与
自检手段。实测可在秒级清除残留，无需重启模拟器。

注意：清理会抬起设备上**所有** MT slot，因此若用户正用手指触摸模拟器窗口，
该次触摸也会被抬起（需要重新按下）。仅在允许的时间点调用（停止连点后、释放
控制实例后、调度器启动前）。
"""
from __future__ import annotations

import logging
import re

# evdev 事件编码（linux/input-event-codes.h）
EV_SYN = 0
EV_ABS = 3
SYN_REPORT = 0
ABS_MT_SLOT = 47
ABS_MT_TRACKING_ID = 57

# 设备未声明 ABS_MT_SLOT 上限时的兜底 slot 数（Android 常见 10 指；雷电实测 16）
DEFAULT_MAX_SLOT = 15

_ADD_DEVICE_LINE = re.compile(r"add device \d+:\s*", re.I)
_MT_SLOT_MAX = re.compile(r"ABS_MT_SLOT\s*:.*?max\s+(\d+)", re.I)
_MT_TRACKING = re.compile(r"ABS_MT_TRACKING_ID", re.I)
_POINTER_IDS = re.compile(r"pointerIds=0x([0-9a-fA-F]+)")
_RAW_POINTER_COUNT = re.compile(r"Last Raw Touch:\s*pointerCount=(\d+)")
_RAW_POINT = re.compile(r"\[(\d+)\]:\s*id=(\d+),\s*x=(-?\d+),\s*y=(-?\d+)")


def _adb_shell(serial: str, command: str) -> str:
    """执行设备端 shell 命令并返回 stdout（失败抛异常）。

    经 adbutils（与项目其余 adb 调用一致，自动解析 adb 可执行文件路径）。
    """
    from adbutils import adb

    return adb.device(serial).shell(command)


def parse_touch_devices(getevent_output: str) -> list[tuple[str, int]]:
    """从 ``getevent -pl`` 输出解析多点触摸设备。

    :return: ``[(设备路径, ABS_MT_SLOT 最大值), ...]``；只包含声明了
        ``ABS_MT_TRACKING_ID``（即多点触摸）的设备。
    """
    devices: list[tuple[str, int]] = []
    for block in _ADD_DEVICE_LINE.split(getevent_output or "")[1:]:
        head = block.strip().splitlines()[0].strip() if block.strip() else ""
        path = head.split()[0] if head else ""
        if not path.startswith("/dev/input/"):
            continue
        if not _MT_TRACKING.search(block):
            continue
        m = _MT_SLOT_MAX.search(block)
        devices.append((path, int(m.group(1)) if m else DEFAULT_MAX_SLOT))
    return devices


def build_clean_commands(device_path: str, max_slot: int) -> str:
    """生成清除残留触点的裸 evdev 序列（整串一次下发，避免多次进程往返）。"""
    cmds = []
    for idx in range(max(int(max_slot), 0) + 1):
        cmds.append(f"sendevent {device_path} {EV_ABS} {ABS_MT_SLOT} {idx}")
        cmds.append(f"sendevent {device_path} {EV_ABS} {ABS_MT_TRACKING_ID} -1")
        cmds.append(f"sendevent {device_path} {EV_SYN} {SYN_REPORT} 0")
    return "; ".join(cmds)


def parse_touch_state(dumpsys_input_output: str) -> dict:
    """从 ``dumpsys input`` 输出解析触摸状态。

    :return: ``{available, active, pointer_ids, raw_pointer_count, points}``

        - ``active``：``InputDispatcher`` 当前是否存在未结束的手势
          （``TouchStatesByDisplay`` 出现 = 有 pointer 仍处于按下态）；
        - ``pointer_ids``：被占用的 pointer id 掩码原样（调试用）；
        - ``raw_pointer_count`` / ``points``：MT 设备最后一帧的触点数与坐标。
    """
    state = {
        "available": False,
        "active": False,
        "pointer_ids": [],
        "raw_pointer_count": 0,
        "points": [],
    }
    lines = (dumpsys_input_output or "").splitlines()
    if not lines:
        return state
    state["available"] = True

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("TouchStates:"):
            state["active"] = "no displays touched" not in stripped
        elif stripped.startswith("TouchStatesByDisplay"):
            state["active"] = True
        else:
            for match in _POINTER_IDS.finditer(stripped):
                if int(match.group(1), 16):
                    state["pointer_ids"].append(match.group(1))

    for idx, line in enumerate(lines):
        match = _RAW_POINTER_COUNT.search(line.strip())
        if not match:
            continue
        state["raw_pointer_count"] = max(state["raw_pointer_count"], int(match.group(1)))
        for follow in lines[idx + 1: idx + 1 + state["raw_pointer_count"]]:
            point = _RAW_POINT.search(follow.strip())
            if point:
                state["points"].append((int(point.group(3)), int(point.group(4))))
    return state


def detect_touch_state(serial: str, logger=None) -> dict:
    """读取设备当前触摸状态（用于残留自检；读不到时 ``available=False``）。"""
    log = logger or logging.getLogger(__name__)
    if not serial:
        return {"available": False, "active": False, "pointer_ids": [],
                "raw_pointer_count": 0, "points": []}
    try:
        return parse_touch_state(_adb_shell(serial, "dumpsys input"))
    except Exception as e:
        log.debug(f"读取触摸状态失败（忽略，继续后续流程）: {e}")
        return {"available": False, "active": False, "pointer_ids": [],
                "raw_pointer_count": 0, "points": []}


def clean_stale_contacts(serial: str, logger=None, reason: str = "") -> bool:
    """抬起设备端所有 MT slot，清除残留触点（幂等）。

    :param serial: 设备串口
    :param logger: 可选 logger
    :param reason: 调用原因（写入日志，便于反馈定位）
    :return: True=至少成功清理了一个多点触摸设备
    """
    log = logger or logging.getLogger(__name__)
    if not serial:
        log.warning(f"残留触点清理跳过（串口为空）{f'：{reason}' if reason else ''}")
        return False

    try:
        output = _adb_shell(serial, "getevent -pl")
    except Exception as e:
        log.warning(f"残留触点清理失败：读取输入设备列表出错（{e}）")
        return False

    devices = parse_touch_devices(output)
    if not devices:
        log.warning("残留触点清理失败：未在 getevent 输出中找到多点触摸设备")
        return False

    cleaned: list[str] = []
    for path, max_slot in devices:
        try:
            _adb_shell(serial, build_clean_commands(path, max_slot))
            cleaned.append(path)
        except Exception as e:
            log.warning(f"残留触点清理失败：{path} 写入抬起事件出错（{e}）")

    if not cleaned:
        return False
    log.info(
        f"已清理设备端残留触点（{reason or '无原因标记'}）: {', '.join(cleaned)}"
    )
    return True


def ensure_no_stale_contacts(serial: str, logger=None, reason: str = "") -> bool:
    """自检 + 自愈：先读触摸状态，存在未结束手势（疑似残留）才清理并记日志。

    :return: True=检测到并已清理；False=无残留（或读取失败，未做清理）
    """
    log = logger or logging.getLogger(__name__)
    state = detect_touch_state(serial, logger=log)
    if not state.get("available"):
        return False
    if not state.get("active"):
        log.debug(f"残留触点自检通过（{reason or '无原因标记'}）：无未结束手势")
        return False

    count = state.get("raw_pointer_count") or 0
    points = ", ".join(f"({x},{y})" for x, y in state.get("points", [])[:10])
    log.warning(
        f"检测到设备端存在未结束的触摸手势（{reason or '无原因标记'}）："
        f"触点数={count}{f'，坐标=[{points}]' if points else ''}"
        f"{'，pointerIds=' + '/'.join(state['pointer_ids']) if state.get('pointer_ids') else ''}"
    )
    cleaned = clean_stale_contacts(serial, logger=log, reason=f"{reason}｜自检发现残留")
    if not cleaned:
        log.warning(
            "残留触点清理未成功，若模拟器出现「一次点击触发多个坐标」的异常，"
            "请重启模拟器后再反馈"
        )
    return cleaned
