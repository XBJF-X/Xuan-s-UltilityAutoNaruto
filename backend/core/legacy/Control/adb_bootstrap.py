# -*- coding: utf-8 -*-
"""ADB 设备就绪等待（修复 adb server 冷启动导致的 MiniTouch 初始化失败）。

背景
----
程序退出时会执行 ``adb kill-server`` 清理残留 adb 进程（issue #4），因此下次
运行时首次访问 adb 会触发 adb server 冷启动。adb server 启动后需要异步扫描
本机模拟器端口，刚启动瞬间 ``adb devices`` 可能枚举不到 ``emulator-xxxx``；
此时 MiniTouch（minidevice）立刻发命令就会抛
``device 'emulator-5560' not found``——即"第一次启动调度器失败、等几秒后
手动重启调度器又能成功"的竞态。

本模块提供 :func:`ensure_adb_device`：在创建控制实例之前，等待目标串口出现在
adb 设备列表中（state=device）：

- ``ip:port`` 串口：额外主动 ``adb connect`` 兜底（server 未扫描到该端口时）；
- 本机模拟器串口（``emulator-xxxx`` / ``127.0.0.1:xxxx``）：等待一定时间仍未
  出现则重启一次 adb server，强制重新扫描本机模拟器端口（只做一次，避免反复
  重启影响其他正在运行的配置）。

超时返回 False，由调用方给出明确报错，不抛出异常。
"""
from __future__ import annotations

import logging
import re
import time

# ip:port 串口（如 127.0.0.1:5555 / 192.168.1.2:7555）
_IP_PORT_RE = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}:\d+$")
# 本机模拟器串口：emulator-5560（adb server 扫描本机端口自动发现）
# 或已手动 adb connect 的 127.0.0.1:5561
_LOCAL_EMULATOR_RE = re.compile(r"^emulator-\d+$|^127\.0\.0\.1:\d+$")

DEFAULT_TIMEOUT = 15.0
DEFAULT_POLL_INTERVAL = 0.5
# 单次 adb connect 的超时（秒），避免一个 connect 卡死整个等待流程
CONNECT_TIMEOUT = 3.0
# 本机模拟器串口等待超过该秒数仍未出现 → 重启一次 adb server 强制重扫端口
RESCAN_AFTER = 3.0


def normalize_serial(serial) -> str:
    """规范化串口字符串（去空白、全角冒号转半角）。"""
    return str(serial or "").strip().replace("：", ":")


def adb_device_states() -> dict:
    """返回 ``{serial: state}``（含 offline/unauthorized）。

    首次调用会触发 adb server 启动（adbutils 内部执行 ``adb start-server``）。
    adb 不可用/查询失败时抛出异常，由调用方决定是否重试。
    """
    from adbutils import adb

    return {info.serial: info.state for info in adb.list()}


def _try_connect(adb, serial: str, log) -> None:
    """对 ip:port 串口主动 adb connect（幂等；失败只记 debug，不中断等待）。"""
    try:
        adb.connect(serial, timeout=CONNECT_TIMEOUT)
    except Exception as e:
        log.debug(f"adb connect {serial} 未成功: {e}")


def _try_rescan_adb_server(adb, serial: str, log) -> None:
    """重启 adb server 以强制重新扫描本机模拟器端口（失败只记日志）。"""
    log.info(f"adb 设备列表中暂未发现 {serial}，重启 adb server 重新扫描本机模拟器端口...")
    try:
        adb.server_kill()
    except Exception as e:
        log.debug(f"adb kill-server 失败（忽略，继续等待）: {e}")


def ensure_adb_device(serial, logger=None, timeout: float = DEFAULT_TIMEOUT,
                      poll_interval: float = DEFAULT_POLL_INTERVAL,
                      allow_rescan: bool = True) -> bool:
    """等待 ``serial`` 在 adb 设备列表中处于 ``device`` 状态。

    :param serial: 目标串口（``emulator-5560`` / ``127.0.0.1:5555``）
    :param logger: 可选 logger，缺省用模块 logger
    :param timeout: 最长等待秒数（超时返回 False）
    :param poll_interval: 轮询间隔秒数
    :param allow_rescan: 本机模拟器串口长时间未出现时，是否允许重启 adb server
        强制重扫端口。**预检等只读场景传 False**，避免影响其他正在运行的配置。
    :return: True=设备已就绪；False=超时未就绪（调用方应给出明确报错）
    """
    serial = normalize_serial(serial)
    log = logger or logging.getLogger(__name__)
    if not serial:
        log.warning("ADB 就绪等待跳过：串口为空")
        return False

    from adbutils import adb

    start = time.monotonic()
    deadline = start + max(float(timeout), 0.0)
    interval = max(float(poll_interval), 0.1)
    attempt = 0
    rescan_done = False
    states: dict = {}

    while True:
        attempt += 1
        try:
            states = adb_device_states()
        except FileNotFoundError as e:
            # adb 可执行文件不存在：重试也不可能成功，直接失败（由调用方提示）
            log.error(f"未找到 adb 可执行文件，无法等待设备就绪: {e}")
            return False
        except Exception as e:
            # adb server 冷启动/查询失败：记录后继续等待，由超时统一兜底
            log.debug(f"ADB 设备列表查询失败（第 {attempt} 次）: {e}")
            states = {}

        if states.get(serial) == "device":
            if attempt > 1:
                log.info(f"ADB 设备已就绪: {serial}（等待 {time.monotonic() - start:.1f}s）")
            return True

        elapsed = time.monotonic() - start

        # ip:port 串口：主动 connect 兜底（模拟器重启/端口转发丢失时同样有效）
        if _IP_PORT_RE.match(serial):
            _try_connect(adb, serial, log)

        # 本机模拟器串口：等待一段时间仍未出现 → 重启一次 server 强制重扫端口
        if (allow_rescan and not rescan_done and elapsed >= RESCAN_AFTER
                and _LOCAL_EMULATOR_RE.match(serial)):
            rescan_done = True
            _try_rescan_adb_server(adb, serial, log)
            continue  # 下一轮 adb.list() 会自动重新启动 adb server

        if time.monotonic() >= deadline:
            break
        time.sleep(interval)

    elapsed = time.monotonic() - start
    detail = "、".join(f"{s}({st})" for s, st in states.items()) or "无"
    log.error(
        f"ADB 设备 {serial} 在 {elapsed:.1f}s 内未就绪（当前 adb 设备：{detail}）。"
        "请确认模拟器已启动，且「助手设置-串口」与模拟器 adb 端口一致。"
    )
    return False
