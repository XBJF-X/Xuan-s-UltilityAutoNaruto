# -*- coding: utf-8 -*-
"""临时探针：定位「连点中触摸屏幕 → 关闭任务」后模拟器触点残留（粘滞多点触摸）的根因。

背景：用户反馈连点过程中用手触摸屏幕，再关闭任务，之后只要点击屏幕就会同时触发
所有预设连点坐标（键位），且只能重启模拟器恢复。怀疑是 minitouch 服务进程在
「触点处于按下状态」时被终止，设备端 evdev 的 MT slot 状态没有被抬起，永久残留。

用法（在项目根目录，使用 .venv 的 python）：
    python -X utf8 test_scene/_probe_stale_touch.py dump      # 打印输入设备与输入状态
    python -X utf8 test_scene/_probe_stale_touch.py shot 名称  # 仅截图
    python -X utf8 test_scene/_probe_stale_touch.py repro     # 复现残留 + 截图佐证
    python -X utf8 test_scene/_probe_stale_touch.py recover   # 尝试用 sendevent 清除残留
"""

import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SERIAL = "emulator-5560"
SHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_probe_shots")

# 复现用坐标：贴近预设键位（右下角技能区），不点击任何危险 UI
PROBE_POINTS = [(1200, 700), (1300, 750), (1100, 760), (1350, 650)]


def adb(*args, binary=False):
    """执行 adb 命令（默认 utf-8 文本，binary=True 时返回 bytes）"""
    cmd = ["adb", "-s", SERIAL] + list(args)
    proc = subprocess.run(cmd, capture_output=True)
    if binary:
        return proc.stdout
    return proc.stdout.decode("utf-8", errors="replace")


def shell(cmd):
    return adb("shell", cmd)


def shot(name):
    os.makedirs(SHOT_DIR, exist_ok=True)
    path = os.path.join(SHOT_DIR, name + ".png")
    data = adb("exec-out", "screencap", "-p", binary=True)
    with open(path, "wb") as f:
        f.write(data)
    print(f"[shot] {path} ({len(data)} bytes)")
    return path


def input_state():
    """读取输入分发器的触摸状态（判定触点是否残留的权威依据）"""
    txt = shell("dumpsys input")
    lines = txt.splitlines()
    out = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("TouchStates") or stripped.startswith("Last Raw Touch"):
            out.append(line.rstrip())
            for follow in lines[idx + 1:idx + 3]:
                if follow.strip().startswith(("Windows:", "[0]:")):
                    out.append("    " + follow.strip()[:160])
                elif follow.strip().startswith("["):
                    out.append("    " + follow.strip()[:160])
                else:
                    break
    motion = [ln.strip() for ln in lines if ln.strip().startswith("MotionEvent(")]
    out.append(f"事件环形缓冲={len(motion)}")
    if motion:
        out.append("最新事件: " + motion[-1][:200])
    return "\n".join(out) if out else "(未取到触摸状态)"


def dump_state():
    """打印与多点触摸相关的设备信息与输入状态（供人工判读）"""
    print("=== 1. 触摸设备与 MT 能力 ===")
    txt = shell("getevent -pl")
    keep = []
    for line in txt.splitlines():
        low = line.lower()
        if ("add device" in low or "name:" in low or "abs_mt_slot" in low
                or "abs_mt_position_x" in low or "abs_mt_tracking" in low
                or "abs_mt_pressure" in low):
            keep.append(line.rstrip())
    print("\n".join(keep) if keep else txt[:4000])

    print("\n=== 2. 设备上 minitouch 进程 ===")
    print(shell("pidof minitouch").strip() or "(无 minitouch 进程)")

    print("\n=== 3. dumpsys input 关键片段 ===")
    txt = shell("dumpsys input")
    keep = []
    capture = False
    for line in txt.splitlines():
        low = line.lower()
        if "touch" in low or "pointer" in low or "input reader state" in low:
            keep.append(line.rstrip())
        elif capture and line.startswith("  "):
            keep.append(line.rstrip())
        capture = "input reader state" in low
    print("\n".join(keep[:200]) if keep else "(无匹配)")

    print("\n=== 4. pointer_location 开关 ===")
    print(shell("settings get system pointer_location").strip())


def enter_minitouch():
    """创建项目自身的 MiniTouch 控制实例（会拉起设备端 minitouch 服务）"""
    from backend.core.legacy.Control.MiniTouch import MiniTouch
    mt = MiniTouch(None, None, SERIAL)
    print(f"[mt] MiniTouch 就绪 max_contacts={mt.max_contacts} max_pressure={mt.max_pressure} "
          f"screen={mt.screen_size} abi={getattr(mt, 'abi', '?')}")
    return mt


def press_all(core, points):
    """发送按下（不发送抬起）——模拟 multi_tap 的中间状态"""
    for idx, (x, y) in enumerate(points):
        core.send(f"d {idx} {x} {y} 100\n")
    core.send("c\n")
    print(f"[mt] 已按下 {len(points)} 个触点（未抬起）: {points}")


def lift_all(core, count):
    """抬起全部触点（与 _send_up_all_contacts 同构）"""
    for idx in range(count):
        core.send(f"u {idx}\n")
    core.send("c\n")
    print("[mt] 已发送抬起全部触点")


def cmd_shot(name):
    shell("settings put system pointer_location 1")
    time.sleep(0.5)
    shot(name)


def cmd_repro():
    from minidevice import MiniTouch as MiniTouchCore

    original = shell("settings get system pointer_location").strip()
    print(f"[env] 原始 pointer_location={original}（结束时恢复）")
    shell("settings put system pointer_location 1")
    time.sleep(0.8)
    shot("00_baseline")

    mt = enter_minitouch()
    core = mt._mt_core
    try:
        print("\n--- 步骤1：发送 4 点按下（不抬起），模拟 multi_tap 中间态 ---")
        press_all(core, PROBE_POINTS)
        time.sleep(0.6)
        print(input_state())
        shot("01_points_down")

        # 关键一步：模拟当前代码「MiniTouch 刷新 / release」时设备端进程先被杀死
        # （minidevice.MiniTouchCore.__init__ 内部会执行 kill minitouch）
        print("\n--- 步骤2：新建 MiniTouchCore（先杀旧进程）---")
        new_core = MiniTouchCore(SERIAL)
        print(f"[probe] 新实例已建立 pid={new_core.pid}，旧实例 socket 已不通")
        time.sleep(0.6)
        print(input_state())
        shot("02_after_kill")

        # 旧连接尝试抬起（当前 release() 的真实行为：socket 已死 → 抛异常）
        print("\n--- 步骤3：旧连接抬起（等价 release() 里 _send_up_all_contacts）---")
        try:
            lift_all(core, len(PROBE_POINTS))
            print("[probe] 旧连接抬起命令：发送成功（无异常）")
        except Exception as e:
            print(f"[probe] 旧连接抬起失败（预期）: {type(e).__name__}: {e}")

        print("\n--- 步骤4：新连接抬起全部触点，观察是否可救回 ---")
        try:
            lift_all(new_core, len(PROBE_POINTS))
            print("[probe] 新连接抬起全部触点：已发送")
        except Exception as e:
            print(f"[probe] 新连接抬起失败: {type(e).__name__}: {e}")
        time.sleep(0.6)
        print(input_state())
        shot("03_after_new_up")
        print(f"[probe] 设备上 minitouch pid: {shell('pidof minitouch').strip() or '(无)'}")
    finally:
        try:
            mt.release()
        except Exception as e:
            print(f"[probe] release 异常: {e}")
        shell(f"settings put system pointer_location {original}")
        print(f"[env] 已恢复 pointer_location={original}")


def cmd_state():
    """打印当前触摸残留状态（TouchStates + Last Raw Touch）"""
    print(input_state())


def _raw_up_sendevent(dev, slots):
    """用 sendevent 直接写 evdev 的 MT 抬起序列（不依赖 minitouch 内部状态）"""
    for idx in slots:
        shell(f"sendevent {dev} 3 47 {idx}")   # EV_ABS ABS_MT_SLOT
        shell(f"sendevent {dev} 3 57 -1")      # EV_ABS ABS_MT_TRACKING_ID -1
        shell(f"sendevent {dev} 0 0 0")        # EV_SYN SYN_REPORT


def cmd_fix():
    """尝试清除残留触点：先试 sendevent，再试 minitouch 的 down+up 配对"""
    dev = os.environ.get("PROBE_TOUCH_DEV", "/dev/input/event2")
    print(f"[fix] 设备端 uid: {shell('id').strip()}")
    print("--- 修复前 ---")
    print(input_state())

    print(f"\n--- 方案A：sendevent {dev} 逐 slot 写 TRACKING_ID=-1 ---")
    _raw_up_sendevent(dev, range(16))
    time.sleep(0.6)
    print(input_state())

    print("\n--- 方案B：minitouch 先 down 再 up 配对（让它记录该 slot 已按下）---")
    from minidevice import MiniTouch as MiniTouchCore
    core = MiniTouchCore(SERIAL)
    try:
        for idx in range(int(core.max_contacts)):
            core.send(f"d {idx} 800 400 1\n")
            core.send(f"u {idx}\n")
        core.send("c\n")
        time.sleep(0.6)
        print(input_state())
    finally:
        core.stop()


def cmd_order():
    """对比验证：抬起（同一连接）必须发生在进程被杀之前"""
    from minidevice import MiniTouch as MiniTouchCore

    print("=== 场景1：先在同一连接抬起 → 再被杀进程（预期：无残留）===")
    mt = enter_minitouch()
    core = mt._mt_core
    press_all(core, PROBE_POINTS)
    time.sleep(0.5)
    print("[order] 按下后状态：")
    print(input_state())
    lift_all(core, mt.max_contacts)
    time.sleep(0.5)
    print("[order] 同一连接抬起后状态：")
    print(input_state())
    new_core = MiniTouchCore(SERIAL)  # 杀死旧进程
    time.sleep(0.5)
    print("[order] 杀死旧进程后状态（预期无残留）：")
    print(input_state())
    try:
        new_core.stop()
    except Exception as e:
        print(f"[order] 清理新实例失败: {e}")
    mt.release()

    print("\n=== 场景2：进程被杀时触点仍按下（复现用户问题，随后立即清理）===")
    mt2 = enter_minitouch()
    core2 = mt2._mt_core
    press_all(core2, PROBE_POINTS[:2])
    time.sleep(0.5)
    killed = MiniTouchCore(SERIAL)  # 旧进程被杀，触点仍按下
    time.sleep(0.5)
    print("[order] 进程被杀后状态（预期残留）：")
    print(input_state())
    _raw_up_sendevent(os.environ.get("PROBE_TOUCH_DEV", "/dev/input/event2"), range(16))
    time.sleep(0.5)
    print("[order] sendevent 清理后状态（预期无残留）：")
    print(input_state())
    try:
        killed.stop()
    except Exception as e:
        print(f"[order] 清理实例失败: {e}")
    mt2.release()


def cmd_recover():
    """直接用 sendevent 写 MT 抬起序列清除残留（不依赖 minitouch）"""
    from minidevice import MiniTouch as MiniTouchCore
    core = MiniTouchCore(SERIAL)
    abs_mt_slot, abs_mt_tracking = 0x2f, 0x39
    try:
        max_contacts = int(core.max_contacts)
        dev = os.environ.get("PROBE_TOUCH_DEV", "/dev/input/event1")
        for idx in range(max_contacts):
            shell(f"sendevent {dev} {abs_mt_slot} {idx}")
            shell(f"sendevent {dev} {abs_mt_tracking} -1")
            shell(f"sendevent {dev} 0 0 0")
        print(f"[recover] 已向 {dev} 写入 {max_contacts} 个 slot 的 TRACKING_ID=-1")
    finally:
        core.stop()


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "dump"
    if action == "dump":
        dump_state()
    elif action == "state":
        cmd_state()
    elif action == "fix":
        cmd_fix()
    elif action == "order":
        cmd_order()
    elif action == "shot":
        cmd_shot(sys.argv[2] if len(sys.argv) > 2 else "manual")
    elif action == "repro":
        cmd_repro()
    elif action == "recover":
        cmd_recover()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
