# -*- coding: utf-8 -*-
"""临时探针：用项目自身的 Clicker + ControlManager 复现「连点中 → 停止（关闭任务）→ 触点残留」。

复现的核心是 SchedulerService.stop() 的调用方式：
    task.stop()                        # 非阻塞，仅置 stop_event，不等连点线程
    control_manager.release()          # 立刻释放控制实例（内部 up-all 后 kill 设备端 minitouch 进程）
连点线程此刻可能正在执行 multi_tap（设备端批次里有 80ms 的 w 80 停留期），
进程被杀 → 抬起丢失 → evdev 的 MT slot 永久处于按下状态。

用法：python -X utf8 test_scene/_probe_clicker_race.py [轮数]
"""

import logging
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SERIAL = "emulator-5560"
POINTS = [(1200, 700), (1300, 750), (1100, 760), (1350, 650)]

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
LOG = logging.getLogger("probe")


def shell(cmd):
    return subprocess.run(["adb", "-s", SERIAL, "shell", cmd],
                          capture_output=True).stdout.decode("utf-8", errors="replace")


def touch_state():
    """返回 (是否被占用/残留的触点描述, 原始帧描述)"""
    txt = shell("dumpsys input")
    lines = txt.splitlines()
    gesture = "无"
    raw = "无"
    for idx, line in enumerate(lines):
        s = line.strip()
        if s.startswith("TouchStates:"):
            gesture = s
        elif s.startswith("TouchStatesByDisplay"):
            detail = [ln.strip() for ln in lines[idx + 1:idx + 6]]
            gesture = " | ".join([s] + detail)
        elif s.startswith("Last Raw Touch: pointerCount="):
            raw = s.split("TouchStates")[0].strip()
    return gesture, raw


def clean_stale_contacts(dev="/dev/input/event2"):
    """裸 evdev MT 抬起序列（不依赖 minitouch），用于每轮之间复位。

    整条命令一次 adb shell 下发，避免 48 次进程往返。
    """
    cmds = []
    for idx in range(16):
        cmds.append(f"sendevent {dev} 3 47 {idx}")
        cmds.append(f"sendevent {dev} 3 57 -1")
        cmds.append(f"sendevent {dev} 0 0 0")
    shell("; ".join(cmds))


class _StubConfig:
    def __init__(self, serial):
        self.serial = serial

    def get_config(self, key, empty=None):
        if key == "控制模式":
            return 0  # ControlMode.MiniTouch
        if key == "串口":
            return self.serial
        return empty

    def set_config(self, key, value):
        pass


class _StubDevice:
    def __init__(self, control_manager):
        self.control_manager = control_manager

    def regularize_coordinate(self, x, y):
        return x, y


class _StubOperationer:
    def __init__(self, config, device):
        self.config = config
        self.device = device


def main():
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    from backend.core.legacy.Control.ControlManager import ControlManager
    from backend.core.legacy.Clicker import Clicker

    cfg = _StubConfig(SERIAL)
    cm = ControlManager(cfg, LOG)
    if not cm.ready:
        print("[race] ControlManager 未就绪，退出")
        return
    clicker = Clicker(_StubOperationer(cfg, _StubDevice(cm)), LOG)
    clicker.update_coordinates(POINTS)

    print(f"每轮 = 启动连点 → 0.8s 后按 SchedulerService.stop() 的方式停止（先 release 再等连点线程）")
    print(f"坐标={POINTS}\n")
    stuck_rounds = 0
    for round_no in range(1, rounds + 1):
        clean_stale_contacts()
        time.sleep(0.2)
        if not cm.ready:
            cm.replace_current_control(cm.create_control_instance())
        clicker.last_minitouch_create_time = time.perf_counter()
        clicker.start()
        time.sleep(0.8)

        # ↓↓↓ 与 SchedulerService.stop() 一致：不等待连点线程就释放控制实例
        cm.release()
        clicker.stop()
        time.sleep(0.6)

        gesture, raw = touch_state()
        stuck = "ByDisplay" in gesture or "pointerIds=0x" in gesture
        stuck_rounds += 1 if stuck else 0
        print(f"--- 第 {round_no} 轮 ---")
        print(f"  连点后状态: {gesture}")
        print(f"  原始帧: {raw}")
        print(f"  判定: {'★残留（模拟器触摸状态被卡住）' if stuck else '干净'}")
        clean_stale_contacts()  # 复位，避免污染下一轮
        time.sleep(0.3)

    print(f"\n结果: {stuck_rounds}/{rounds} 轮出现触点残留（进程在按下期间被杀）")
    gesture, raw = touch_state()
    print(f"收尾状态: {gesture} / {raw}")


if __name__ == "__main__":
    main()
