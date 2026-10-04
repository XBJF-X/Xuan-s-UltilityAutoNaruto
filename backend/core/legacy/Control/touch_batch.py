"""MiniTouch 批量指令构造（连点器「集中批量提交」）。

背景
----
连点器旧实现每一轮「按下 → 等待 → 抬起」都各自 ``publish`` 一次，而
``minidevice.MiniTouch.send`` 每次都要走一遍 ``sendall`` + ``recv``：

* 每个触点周期都要一次 Python 侧往返（``recv(0)`` 且带 GIL 释放），
  周期数一多就成为连点速度的上限；
* 周期间隔靠 ``time.sleep`` 在 Python 侧凑，抖动量直接体现为连点节奏不稳。

minitouch 的协议本身允许**一条命令流里连续写多个周期**：``c`` 只表示
"提交当前这批改动"，协议不要求每个周期结束后必须回一句，命令由设备端
顺序执行。于是把 N 个周期拼成一条命令流、只 ``publish`` 一次，就能在保持
"多点同时按下/抬起"语义不变的前提下，把 N 次往返压缩成 1 次。

本模块只负责**构造命令字符串**（纯函数，不碰设备），便于单测：
``test_scene/verify_clicker_batching.py``。
"""
from typing import List, Sequence, Tuple

# 单次 publish 拼装的周期上限：限制命令流长度，避免瞬时灌入过多指令导致
# 设备端积压、连点停止响应变慢（30 个周期 ≈ 1.4s 工作量，停止延迟可接受）。
MAX_CYCLES_PER_PUBLISH = 30

# 单个周期的「按下保持」默认时长（毫秒）。游戏对触摸的判定需要一次完整的
# down→up，太短的按住时间在部分机型上会被判为无效点击。
DEFAULT_TAP_HOLD_MS = 80


def build_tap_points_cycle(points: Sequence[Sequence[int]], pressure: int,
                           hold_ms: int) -> str:
    """构造「单周期按下全部触点 → 保持 hold_ms → 抬起全部触点」的命令片段。

    :param points: 已转换/已裁剪的坐标列表 ``[[x, y], ...]``
    :param pressure: 按压力度
    :param hold_ms: 按下保持时长（毫秒）
    :return: 不含结尾 ``c`` 的命令片段（每行一条指令）
    """
    lines: List[str] = []
    for idx, (x, y) in enumerate(points):
        lines.append(f"d {idx} {x} {y} {pressure}")
    # 所有触点先一起提交，保证"同时按下"
    lines.append("c")
    if hold_ms > 0:
        lines.append(f"w {hold_ms}")
    for idx in range(len(points)):
        lines.append(f"u {idx}")
    # 所有触点一起提交，保证"同时抬起"
    lines.append("c")
    return "\n".join(lines)


def build_tap_batch(points: Sequence[Sequence[int]], pressure: int = 100,
                    hold_ms: int = DEFAULT_TAP_HOLD_MS,
                    cycles: int = 1,
                    interval_ms: int = 0) -> Tuple[str, int]:
    """构造包含 ``cycles`` 个周期的批量命令流（一次 publish 提交）。

    第 i 个周期与第 i+1 个周期之间插入 ``w interval_ms``，保持原有连点节奏；
    最后一个周期后**不**追加等待，避免停止时多等一个间隔。

    注意 ``hold_ms + interval_ms`` 构成一个周期的设备端耗时，返回值 ``delay_ms``
    给出该总值，供调用方扣除设备端已消耗的时间（见 ``Clicker`` 的主循环）。

    :param points: 坐标列表 ``[[x, y], ...]``（需已做过坐标转换与触点数量裁剪）
    :param pressure: 按压力度
    :param hold_ms: 每周期按下保持时长（毫秒）
    :param cycles: 周期数（会被夹到 ``[1, MAX_CYCLES_PER_PUBLISH]``）
    :param interval_ms: 周期之间的额外间隔（毫秒）
    :return: ``(命令流, 设备端总耗时毫秒)``
    """
    if not points:
        raise ValueError("坐标列表为空，无法构造连点命令")

    cycles = max(1, min(int(cycles), MAX_CYCLES_PER_PUBLISH))
    hold_ms = max(0, int(hold_ms))
    interval_ms = max(0, int(interval_ms))

    cycle = build_tap_points_cycle(points, pressure, hold_ms)
    if cycles == 1:
        return cycle + "\n", hold_ms

    chunks: List[str] = []
    for i in range(cycles):
        chunks.append(cycle)
        if i != cycles - 1 and interval_ms > 0:
            chunks.append(f"w {interval_ms}")
    return "\n".join(chunks) + "\n", hold_ms + interval_ms
