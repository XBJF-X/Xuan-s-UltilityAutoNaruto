import time
import threading
import traceback
from enum import Enum
from typing import List, Tuple

# 必须在导入 adbutils / minidevice 之前固定 adb：用户本机的 adb 会与本项目
# 依赖库自带的 adb 争用同一个 adb server，导致 MiniTouch 初始化时 socket
# 读不到内容（现象：概率性初始化失败）。见 backend/runtime/adb_env.py。
from backend.runtime.adb_env import ensure_bundled_adb

ensure_bundled_adb()

from adbutils import adb
from minidevice import MiniTouch as MiniTouchCore
from minidevice.utils.command_builder_utils import CommandBuilder

from backend.core.legacy.Config import Config
from backend.core.legacy.Control import Control, InvalidResolution
from backend.core.legacy.Control import touch_residue
from backend.core.legacy.Control.adb_bootstrap import ensure_adb_device

# 设备端 minitouch 可执行文件路径（minidevice 的推送目标）
_MINITOUCH_REMOTE_PATH = "/data/local/tmp/minitouch"
# 返回 DIR / FILE / MISSING：用于识别「被其他程序误创建成目录」的情况
_MINITOUCH_PATH_STATE_CMD = (
    f"if [ -d {_MINITOUCH_REMOTE_PATH} ]; then echo DIR; "
    f"elif [ -f {_MINITOUCH_REMOTE_PATH} ]; then echo FILE; "
    "else echo MISSING; fi"
)


# 初始化重试：程序退出时会 adb kill-server，下次首次连接时 adb server 冷启动、
# 本机模拟器端口尚未被扫描到，`device 'emulator-xxxx' not found` 属瞬态错误；
# 等待设备就绪 + 有限重试即可自愈（U2 由 uiautomator2 内部等待设备，无此问题）。
_INIT_ATTEMPTS = 3
# 每次尝试前的 adb 就绪等待时长（秒），逐次缩短避免长时间阻塞调度器启动
_INIT_WAIT_TIMEOUTS = (15.0, 6.0, 6.0)
_INIT_RETRY_INTERVAL = 1.5

# 释放前「抬起全部触点 → 关闭 socket/杀进程」之间的等待时长（秒）。
# 抬起命令由设备端 minitouch 逐条执行，紧接着杀进程会让尚未处理的命令随进程一起
# 消失，evdev 的 MT slot 就会永久停在按下态（随后任何一次点击都会同时触发这些
# 坐标，只能重启模拟器）——v0.17.46 修复。
_RELEASE_LIFT_SETTLE = 0.15


class ArchType(Enum):
    ARM = "arm"
    ARM64 = "arm64"
    X86 = "x86"
    X86_64 = "x86_64"
    UNKNOWN = "unknown"


class MiniTouchInitError(RuntimeError):
    """带**失败步骤**的 MiniTouch 初始化异常（便于定位具体出错位置）。"""

    def __init__(self, step: str, serial: str, cause):
        self.step = step
        self.serial = serial or "未指定"
        self.cause = cause
        super().__init__(
            f"MiniTouch 初始化失败[{step}]（设备 {self.serial}）："
            f"{type(cause).__name__}: {cause}"
        )



class MiniTouch(Control):
    """
    基于minidevice.MiniTouch封装的控制器
    """

    def __init__(self, config: Config, parent_logger=None, serial: str = ""):
        super().__init__(config, parent_logger)
        self._released = False
        self._mt_core = None
        self._core_lock = threading.RLock()
        self._shutdown_requested = threading.Event()
        try:
            self.serial = serial or config.get_config("串口")
            self.serial = self.serial.replace("：", ":")
            if not self.serial:
                raise RuntimeError("设备序列号不能为空")

            self._init_device()

        except Exception as e:
            self.logger.error(f"MiniTouch 初始化失败: {e}", exc_info=e)
            self.release()
            self._released = True
            raise

    def _init_device(self):
        """初始化 minitouch 核心与设备信息（adb 未就绪时等待并重试）。

        adb server 冷启动（程序退出时执行过 adb kill-server）或模拟器刚上线时，
        `device 'xxx' not found`、端口转发失败等都属于瞬态错误；这里先等待目标
        串口在 adb 设备列表中就绪，再对整体初始化做有限重试。
        """
        last_error: Exception | None = None
        for attempt in range(1, _INIT_ATTEMPTS + 1):
            wait_timeout = _INIT_WAIT_TIMEOUTS[
                min(attempt - 1, len(_INIT_WAIT_TIMEOUTS) - 1)]
            ensure_adb_device(self.serial, self.logger, timeout=wait_timeout)
            step = "检查/清理设备端 minitouch 路径"
            try:
                # 关键前置检查：/data/local/tmp/minitouch 被其他程序误创建成
                # 目录时，minidevice 会把二进制推进该目录、再执行目录 → 报
                # "Is a directory"，且错误被 socket 解析成无意义的解包异常。
                self._prepare_minitouch_path()

                step = "启动 minidevice minitouch 核心（推送/转发/socket 握手）"
                self._build_core()

                step = "读取 adb 设备信息"
                self.adb = adb.device(self.serial)
                self.get_device_info()

                step = "校验屏幕分辨率比例"
                if not self.check_resolution():
                    raise InvalidResolution("模拟器分辨率比例不符合16:9的要求，请在模拟器设置内切换！")
                self.logger.info(
                    f"MiniTouch 初始化成功 | 分辨率:{self.screen_size[0]}x{self.screen_size[1]},最大连接数:{self.max_contacts},最大压力:{self.max_pressure}"
                )
                return
            except InvalidResolution:
                # 分辨率不符属配置问题，重试无意义，直接由上层报错
                raise
            except MiniTouchInitError as e:
                last_error = e
                self._diagnose_minitouch_failure(e.step)
                # 半初始化的核心可能已启动设备端 minitouch 服务/占用 socket，重试前清理
                self._discard_core()
                if attempt < _INIT_ATTEMPTS:
                    self.logger.warning(
                        f"MiniTouch 初始化第 {attempt} 次失败（{e}），"
                        f"{_INIT_RETRY_INTERVAL}s 后重试..."
                    )
                    time.sleep(_INIT_RETRY_INTERVAL)
            except Exception as e:
                last_error = MiniTouchInitError(step, self.serial, e)
                self._diagnose_minitouch_failure(step)
                # 半初始化的核心可能已启动设备端 minitouch 服务/占用 socket，重试前清理
                self._discard_core()
                if attempt < _INIT_ATTEMPTS:
                    self.logger.warning(
                        f"MiniTouch 初始化第 {attempt} 次失败（{last_error}）"
                        f"{chr(10)}{traceback.format_exc()}"
                        f"{_INIT_RETRY_INTERVAL}s 后重试..."
                    )
                    time.sleep(_INIT_RETRY_INTERVAL)
        if last_error is not None:
            raise last_error
        raise RuntimeError("MiniTouch 初始化失败：重试流程未产生异常，请检查 adb 与模拟器状态")

    @staticmethod
    def _shell_text(device, command: str) -> str:
        """执行设备端 shell 命令并统一转成文本（兼容返回 bytes 的实现）。"""
        output = device.shell(command)
        if isinstance(output, bytes):
            return output.decode("utf-8", errors="replace")
        return str(output or "")

    def _read_minitouch_path_state(self) -> str:
        """返回设备端 minitouch 路径状态：DIR / FILE / MISSING。"""
        device = adb.device(self.serial)
        if getattr(device, "shell", None) is None:
            # 仅测试替身会出现（真实 adbutils.AdbDevice 一定有 shell）；
            # 显式跳过而不是伪造结果，避免误删真实设备上的文件。
            self.logger.debug(
                "当前 adb 设备对象不支持 shell（测试替身），跳过 minitouch 路径预检")
            return "SKIPPED"
        try:
            output = self._shell_text(device, _MINITOUCH_PATH_STATE_CMD)
        except Exception as e:
            raise MiniTouchInitError(
                f"检查 {_MINITOUCH_REMOTE_PATH} 是否为目录", self.serial, e) from e
        return output.strip().splitlines()[-1].strip().upper() if output.strip() else ""

    def _prepare_minitouch_path(self) -> str:
        """初始化前检查设备端 minitouch 路径；若被误创建成目录则删除。

        minidevice 的 ``MiniTouch.__init__`` 会直接把二进制 push 到
        ``/data/local/tmp/minitouch`` 并执行它。目标若是目录，push 变成
        "放进目录"，执行时得到 ``Is a directory``；该错误又发生在 socket
        握手之前，最终只表现为读不到协议头（``ValueError: not enough values
        to unpack``），非常难定位。这里在创建核心前显式检查并清理。
        """
        state = self._read_minitouch_path_state()
        if state == "SKIPPED":
            return state
        if state == "DIR":
            self.logger.warning(
                f"检测到设备端 {_MINITOUCH_REMOTE_PATH} 是目录"
                "（可能被其他程序误创建），先删除再初始化 MiniTouch...")
            device = adb.device(self.serial)
            try:
                output = self._shell_text(
                    device, f"rm -rf {_MINITOUCH_REMOTE_PATH} && echo REMOVED"
                ).strip()
            except Exception as e:
                raise MiniTouchInitError(
                    f"删除被误创建为目录的 {_MINITOUCH_REMOTE_PATH}", self.serial, e) from e
            if "REMOVED" not in output:
                raise MiniTouchInitError(
                    f"删除被误创建为目录的 {_MINITOUCH_REMOTE_PATH}", self.serial,
                    f"删除命令未成功（设备返回：{output[:200] or '空'}）")
            if self._read_minitouch_path_state() == "DIR":
                raise MiniTouchInitError(
                    f"删除被误创建为目录的 {_MINITOUCH_REMOTE_PATH}", self.serial,
                    "删除后仍为目录（可能无写权限或被其他进程占用）")
            self.logger.info(
                f"已删除被误创建为目录的 {_MINITOUCH_REMOTE_PATH}，继续初始化 MiniTouch")
            state = "MISSING"
        elif state == "FILE":
            self.logger.debug(
                f"设备端 {_MINITOUCH_REMOTE_PATH} 已存在（文件），将由 minidevice 覆盖推送")
        elif state == "MISSING":
            self.logger.debug(f"设备端 {_MINITOUCH_REMOTE_PATH} 不存在，等待 minidevice 推送")
        else:
            raise MiniTouchInitError(
                f"检查 {_MINITOUCH_REMOTE_PATH} 是否为目录", self.serial,
                f"无法识别的路径状态：{state[:200] or '空'}")
        return state

    def _diagnose_minitouch_failure(self, step: str) -> None:
        """初始化失败时补充设备端关键状态（不抛异常，只记日志）。

        socket 握手失败时原生异常缺少上下文；这里把「路径类型 / 进程 / ABI」
        打出来，便于区分「目录占位」「进程残留」「二进制不兼容」等原因。
        """
        try:
            device = adb.device(self.serial)
            if getattr(device, "shell", None) is None:
                return
            for command in (
                f"ls -ld {_MINITOUCH_REMOTE_PATH}",
                "pidof minitouch",
                "getprop ro.product.cpu.abi",
                "getprop ro.build.version.sdk",
            ):
                try:
                    output = self._shell_text(device, command).strip()
                except Exception as e:
                    output = f"<执行失败: {e}>"
                self.logger.warning(
                    f"MiniTouch 诊断[{step}] $ {command} -> {output[:300] or '空'}")
        except Exception as e:
            self.logger.warning(f"MiniTouch 诊断信息采集失败: {e}")

    def _discard_core(self):
        """丢弃未完成初始化的 minitouch 核心（重试前释放进程与 socket）。

        注意：``_released`` / ``_shutdown_requested`` 不动——本方法只服务于
        初始化重试，最终失败仍由 ``__init__`` 的 ``release()`` 统一善后。
        """
        core = self._mt_core
        self._mt_core = None
        if core is not None:
            try:
                core.stop()
            except Exception as e:
                self.logger.debug(f"清理未就绪的 MiniTouch 核心失败: {e}")

    def _build_core(self):
        """构造 minidevice 核心，并把失败上下文补进异常文本。

        minidevice 内部依次做：push 二进制 → chmod → kill 旧进程 → 启动
        ``/data/local/tmp/minitouch`` → 端口转发 → 读 socket 协议头。
        这一段抛出的原生异常（尤其是 socket 解包错误）不含任何上下文，这里补上
        串口与设备端路径，便于定位。
        """
        try:
            self._mt_core = MiniTouchCore(self.serial)
        except Exception as e:
            raise RuntimeError(
                f"minidevice.MiniTouch 构造失败（串口={self.serial}，"
                f"设备端路径={_MINITOUCH_REMOTE_PATH}，adb={adb.__class__.__module__}）："
                f"{type(e).__name__}: {e}"
            ) from e
        self._max_contacts = int(self._mt_core.max_contacts)
        self.max_pressure = int(self._mt_core.max_pressure)
        self._released = False

    def _send_up_all_contacts(self, core: MiniTouchCore):
        for idx in range(self.max_contacts):
            core.send(f"u {idx}\n")
        core.send("c\n")

    def _is_disconnect_error(self, exc: Exception) -> bool:
        return getattr(exc, "winerror", None) == 10053 or "10053" in str(exc)

    def _lift_contacts_on(self, core) -> bool:
        """在指定核心上抬起全部触点。

        必须由**按下触点的那个连接**发出才有效：minitouch 只对自己记录过按下的
        slot 执行 ``u``，换实例/换连接再抬是空操作（实测）。无核心时视为成功。
        """
        if core is None:
            return True
        try:
            self._send_up_all_contacts(core)
            return True
        except Exception as e:
            if self._is_disconnect_error(e):
                self.logger.warning(
                    f"抬起触点失败（连接已断开），设备端可能残留按下中的触点: {e}")
            else:
                self.logger.warning(f"抬起触点失败，设备端可能残留按下中的触点: {e}")
            return False

    def _cleanup_stale_contacts(self, reason: str) -> bool:
        """裸 evdev 兜底清理残留触点（不依赖 minitouch 内部状态）。"""
        return touch_residue.clean_stale_contacts(
            self.serial, logger=self.logger, reason=reason)

    def _stop_core(self, core, context: str = "") -> None:
        """关闭 socket 并终止设备端 minitouch 进程（失败只记日志，不阻断流程）。"""
        if core is None:
            return
        try:
            core.stop()
        except Exception as e:
            self.logger.warning(f"停止 MiniTouch 服务失败{f'（{context}）' if context else ''}: {e}")

    def _reconnect(self):
        with self._core_lock:
            if self._released or self._shutdown_requested.is_set():
                return False
            try:
                self.logger.info("MiniTouch 连接异常，尝试重建控制实例...")
                old_core = self._mt_core
                # 顺序铁律（v0.17.49 修正）：抬起 → 等设备端执行完 → **停旧核心** →
                # 再建新核心。minidevice 的设备端只有一个 minitouch 进程，而
                # `MiniTouchCore.__init__`（新建）与 `MiniTouchCore.stop`（旧实现里
                # 在新核心之后调用）都会 `pidof minitouch` 把它 kill 掉——先建后停
                # 会把**刚启动的新进程**一起杀掉，新 socket 随即变成死连接：
                # 下一次点击 `sendall` 缓冲成功、再下一次抛 WinError 10053，于是
                # 「点一次重连一次」（现场日志每 6~7 秒一轮重连 + 残留清理）。
                old_lifted = self._lift_contacts_on(old_core)
                if old_lifted and old_core is not None:
                    # 让设备端把抬起命令处理完，否则随后 kill 进程会吞掉未处理的命令
                    time.sleep(_RELEASE_LIFT_SETTLE)
                self._stop_core(old_core, context="重连")
                self._build_core()
                if self._shutdown_requested.is_set():
                    self._release_new_core_after_shutdown()
                    return False
                if not old_lifted:
                    # 旧连接已断（命令发不出去）→ 设备端可能残留按下中的触点。
                    # 裸 evdev 清理要跑 getevent/dumpsys（秒级），放在重连热路径上
                    # 会把连点拖成「点一次卡几秒」，因此只挂起标记，由任务边界
                    # （连点启动前 / 控制实例释放 / 调度器启停自检）统一清理；
                    # 重复挂起时不再反复告警。
                    if touch_residue.mark_pending_cleanup(
                            self.serial, logger=self.logger,
                            reason="重连时旧连接抬起失败"):
                        self.logger.warning(
                            "重建前旧连接已断开，触点抬起失败：设备端可能残留按下中的触点，"
                            "将在连点启动/结束、调度器启停等任务边界清理（不在连点中途阻塞）")
                self.logger.info("MiniTouch 重建成功")
                return True
            except Exception as e:
                self._released = True
                self.logger.error(f"MiniTouch 重建失败: {e}")
                return False

    def _release_new_core_after_shutdown(self) -> None:
        """重建过程中收到退出请求：停掉刚建好的核心并置为已释放。"""
        core = self._mt_core
        self._mt_core = None
        self._stop_core(core, context="重建期间收到退出请求")
        self._released = True

    # ==================== 实现Control抽象基类必须方法 ====================
    @property
    def ready(self) -> bool:
        """Control约束：就绪状态"""
        return not self._released and self._mt_core is not None

    @property
    def core(self):
        """当前 minidevice 核心（未就绪时 None）。

        供连点器的「集中批量提交」直接投递整段命令流使用：批量提交需要绕过
        ``multi_tap``（它一次只发一个周期），但仍必须复用**同一个**核心实例与
        **同一把** ``_core_lock``，否则会与在途的 ``multi_tap`` / ``release``
        争用同一个 socket。
        """
        return self._mt_core

    @property
    def max_contacts(self) -> int:
        """设备端支持的最大同时触点数（未就绪时回退 1）。"""
        return int(getattr(self, "_max_contacts", 1) or 1)

    def tap_command_batch(self, raw_points, command: str):
        """把一段已构造好的 minitouch 命令流批量投递给设备（集中批量提交）。

        与 ``multi_tap`` 共用 ``_core_lock`` 与同一个核心，因此不会与在途的
        ``multi_tap`` / ``release`` 争用 socket。

        :param raw_points: 本次批量涉及的**原始**坐标列表，仅用于连接异常时打日志
        :param command: ``touch_batch.build_tap_batch`` 产出的完整命令流
        :return: True=已投递；False=未就绪/连接已断开（调用方按需重建）
        """
        if not self.ready:
            return False
        with self._core_lock:
            core = self._mt_core
            if core is None:
                return False
            try:
                core.send(command)
                return True
            except Exception as e:
                if self._is_disconnect_error(e):
                    self.logger.warning(f"批量连点投递失败（连接断开），尝试重建: {e}")
                    self._reconnect()
                    return False
                raise

    def convert_point(self, x, y):
        """对外暴露的坐标转换（含旋转补偿），供连点器批量提交使用。"""
        return self.__convert(x, y)

    @property
    def rotated(self):
        return self.orientation

    @property
    def screen_size(self):
        width, height = self.window_size[0], self.window_size[1]
        if width < height:
            return height, width
        return width, height

    def get_device_info(self):
        """获取设备信息"""
        self.abi = self.adb.getprop("ro.product.cpu.abi")  # 获取设备架构
        self.sdk = self.adb.getprop("ro.build.version.sdk")  # 获取设备sdk
        self.orientation = self.adb.rotation()  # 屏幕方向获取
        self.window_size = self.adb.window_size()
        self.width = self.window_size.width
        self.height = self.window_size.height
        self.logger.debug(
            f"屏幕方向:{self.orientation},屏幕宽度:{self.width},屏幕高度:{self.height}")

    def check_resolution(self):  # type: ignore[override]
        return int(self.screen_size[0] * 9) == int(self.screen_size[1] * 16)

    def release(self):
        """释放控制实例：抬起全部触点 → 关闭 socket → 终止设备端 minitouch。

        整段在 ``_core_lock`` 内完成，避免与在途 ``multi_tap`` 争用同一 socket；
        抬起与 kill 之间留 ``_RELEASE_LIFT_SETTLE`` 让设备端把抬起命令执行完，
        否则 slot 会永久停在按下态。
        """
        with self._core_lock:
            if self._released:
                return
            self._shutdown_requested.set()
            self._released = True
            core = self._mt_core
            self._mt_core = None
            lifted = self._lift_contacts_on(core)
            if core is not None:
                if lifted:
                    time.sleep(_RELEASE_LIFT_SETTLE)
                self._stop_core(core, context="释放")
        if not lifted:
            # 抬起没成功：触点可能仍按在设备上（此后点击会同时触发多个坐标）
            self._cleanup_stale_contacts("释放控制实例时抬起失败")
        else:
            # 任务结束边界：补执行重连时挂起（当时为不阻塞连点而未清理）的残留清理；
            # 无挂起时零开销，不访问设备（v0.17.49）
            touch_residue.flush_pending_cleanup(
                self.serial, logger=self.logger,
                reason="释放控制实例时补清理挂起的残留触点")
        self.logger.info("MiniTouch 已完全释放")

    def up_all_contacts(self) -> bool:
        """抬起全部触点；失败时用裸 evdev 兜底清理。

        注意：只有「按下触点的那个连接」发出的 ``u`` 才有效，所以这里必须在
        当前核心上发送（而不是新建实例后发送）。

        :return: True=触点已抬起（或兜底清理成功）
        """
        with self._core_lock:
            lifted = self._lift_contacts_on(self._mt_core)
        if not lifted:
            lifted = self._cleanup_stale_contacts("抬起全部触点失败")
        return lifted

    # ==================== 核心触摸方法（直接转发minidevice实现） ====================
    def click(self, x: int, y: int, duration: int = 100):
        """
        单点点击（满足Control约束 + 兼容原有接口）
        :param x: X坐标
        :param y: Y坐标
        :param duration: 点击时长(ms)，minidevice默认100
        """
        if not self.ready:
            return
        with self._core_lock:
            core = self._mt_core
            if core is None:
                return
            try:
                core.click(x, y, duration)
            except Exception as e:
                if self._is_disconnect_error(e):
                    self._reconnect()
                    return
                raise

    def swipe(self,
              start_coordinate: Tuple[int, int],
              end_coordinate: Tuple[int, int],
              duration: float = 1.0):
        """
        单指滑动
        :param start_coordinate: 起点 (x1,y1)
        :param end_coordinate: 终点 (x2,y2)
        :param duration: 滑动总时长（秒！！！） 传1=1秒，传2=2秒
        """
        if not self.ready:
            return
        with self._core_lock:
            core = self._mt_core
            if core is None:
                return
            points = []
            total_ms = 0
            try:
                x1, y1 = start_coordinate
                x2, y2 = end_coordinate

                total_ms = int(duration * 1000)
                TOTAL_STEPS = int(total_ms / 16)

                # 生成均匀滑动路径
                points = []
                for i in range(TOTAL_STEPS + 1):
                    ratio = i / TOTAL_STEPS
                    x = int(x1 + (x2 - x1) * ratio)
                    y = int(y1 + (y2 - y1) * ratio)
                    points.append((x, y))

                core.swipe(points, total_ms)
                # self.logger.debug(f"滑动: {start_coordinate} -> {end_coordinate} | 总时长:{duration}s")
                time.sleep(duration * 1.1)
            except Exception as e:
                if self._is_disconnect_error(e):
                    self._reconnect()
                    return
                raise

    # ==================== 复用ADB实现Control其他抽象方法 ====================
    def app_stop(self, package_name: str):
        self.adb.app_stop(package_name)

    def app_start(self, package_name: str):
        self.adb.app_start(package_name)

    def current_app(self):  # type: ignore[override]
        front_app = self.adb.app_current()
        return {"package": front_app.package, "activity": front_app.activity}

    def input(self, input_text: str):
        self.adb.send_keys(input_text)

    def press_key(self, key: int | str):
        self.adb.keyevent(key)

    def touch_down(self, x: int, y: int):
        """Control约束：按下（基于minitouch指令封装）"""
        if not self.ready:
            return
        x, y = self.__convert(x, y)
        with self._core_lock:
            core = self._mt_core
            if core is None:
                return
            try:
                core.send(f"d 0 {x} {y} {self.max_pressure}\nc")
            except Exception as e:
                if self._is_disconnect_error(e):
                    self._reconnect()
                    return
                raise

    def touch_up(self, x: int, y: int):
        """Control约束：抬起"""
        if not self.ready:
            return
        x, y = self.__convert(x, y)
        with self._core_lock:
            core = self._mt_core
            if core is None:
                return
            try:
                core.send("u 0\nc")
            except Exception as e:
                if self._is_disconnect_error(e):
                    self._reconnect()
                    return
                raise

    def long_press(self, x: int, y: int, duration: float):
        """Control约束：长按"""
        if not self.ready:
            return

        start_time = time.perf_counter()

        hold_ms = max(0, int(duration * 1000))
        x, y = self.__convert(x, y)
        with self._core_lock:
            core = self._mt_core
            if core is None:
                return
            builder = CommandBuilder()
            builder.down(0, int(x), int(y), self.max_pressure)
            builder.commit()
            if hold_ms > 0:
                builder.wait(hold_ms)
            builder.up(0)
            builder.commit()
            try:
                builder.publish(core)
            except Exception as e:
                if self._is_disconnect_error(e):
                    self._reconnect()
                    return
                raise
        time.sleep(duration * 1.2 - (time.perf_counter() - start_time))

    def multi_tap(self,
                  points: List[List[int]],
                  pressure: int = 100,
                  duration: float = 0.1):
        """
        多点同时点击（使用 CommandBuilder）
        :param points: 坐标列表 [[x1,y1], [x2,y2], ...]
        :param pressure: 按压力度（默认100）
        :param duration: 按下持续时间（秒）
        """
        if not self.ready:
            return

        with self._core_lock:
            core = self._mt_core
            if core is None:
                return
            # 限制触点数量并进行坐标边界保护
            points = points[:self.max_contacts]
            points = [
                list(map(int, self.__convert(point[0], point[1])))
                for point in points
            ]

            builder = CommandBuilder()
            # 1. 同时按下所有点
            for idx, (x, y) in enumerate(points):
                builder.down(idx, x, y, pressure)
            builder.commit()  # 提交，使所有按下同时生效

            # 2. 等待指定时长
            builder.wait(int(duration * 1000))

            # 3. 同时抬起所有点
            for idx in range(len(points)):
                builder.up(idx)
            builder.commit()  # 提交，使所有抬起同时生效

            # 4. 发送命令到设备（self._mt_core 有 send 方法）
            try:
                builder.publish(core)
            except Exception as e:
                if self._is_disconnect_error(e):
                    self._reconnect()
                    return
                raise

    def __convert(self, x, y):
        if self.rotated == 0:
            pass
        elif self.rotated == 1:
            x, y = self.screen_size[1] - y, x
        elif self.rotated == 2:
            x, y = self.screen_size[0] - x, self.screen_size[1] - y
        elif self.rotated == 3:
            x, y = y, self.screen_size[0] - x
        return x, y

    def __del__(self):
        if hasattr(self, '_released') and not self._released:
            self.release()


if __name__ == "__main__":
    mt = MiniTouch(None, None, "emulator-5558")
    mt.long_press(300, 100, 1)
