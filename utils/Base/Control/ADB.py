import re
import subprocess
from typing import Tuple

from utils.Base.Config import Config
from utils.Base.Control import Control


class ADB(Control):
    """
    ADB 控制实现类
    基于原生 ADB 命令实现所有设备控制操作，兼容安卓设备
    """

    def __init__(self, config: Config, parent_logger=None, device_serial: str = ""):
        super().__init__(config, parent_logger)
        # 从配置中获取设备序列号（多设备必备）
        self.device_serial = device_serial if device_serial else self.config.get_config("串口")
        # 初始化 ADB 基础命令前缀（指定设备）
        self.adb_prefix = self._build_adb_prefix()
        self.screen_size = self.get_screen_size()
        # 标记实例就绪
        self._ready = True
        self.logger.info(f"ADB 控制器初始化成功，设备序列号: {self.device_serial}")

    def _build_adb_prefix(self) -> str:
        """构建 ADB 命令前缀（指定目标设备）"""
        if self.device_serial:
            return f"adb -s {self.device_serial}"
        return "adb"

    def _run_cmd(self, cmd: str, timeout: float = 10) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=timeout
            )
            output = result.stdout.strip() + result.stderr.strip()
            if result.returncode == 0:
                self.logger.debug(f"命令执行成功: {cmd}")
                return True, output
            else:
                self.logger.error(f"命令执行失败: {cmd}, 错误: {output}")
                return False, output
        except subprocess.TimeoutExpired:
            self.logger.error(f"命令执行超时({timeout}s): {cmd}")
            return False, "命令执行超时"
        except Exception as e:
            self.logger.error(f"命令执行异常: {cmd}, {e}")
            return False, str(e)

    # ==================== 实现抽象基类的所有方法 ====================
    def release(self):
        """释放资源：重置状态"""
        self._ready = False
        self.logger.info("ADB 控制器已释放资源")

    @property
    def ready(self):
        """就绪状态属性"""
        return self._ready

    def get_screen_size(self) -> Tuple[int, int]:
        """
        获取设备屏幕尺寸
        :return: (宽度, 高度)
        """
        cmd = f"{self.adb_prefix} shell wm size"
        success, output = self._run_cmd(cmd)
        if not success:
            return 0, 0
        # 正则解析屏幕分辨率
        match = re.search(r"(\d+)x(\d+)", output)
        if match:
            width, height = int(match.group(1)), int(match.group(2))
            self.logger.info(f"获取屏幕尺寸成功: {width}x{height}")
            return width, height
        self.logger.error(f"解析屏幕尺寸失败: {output}")
        return 0, 0

    def click(self, x: int, y: int):
        """点击坐标 (x, y)"""
        cmd = f"{self.adb_prefix} shell input tap {x} {y}"
        self._run_cmd(cmd)
        self.logger.debug(f"执行点击: ({x}, {y})")

    def swipe(self, start_coordinate: Tuple[int, int], end_coordinate: Tuple[
        int, int], duration: float = 0.5):
        """
        滑动操作
        :param start_coordinate: 起始坐标 (x1, y1)
        :param end_coordinate: 结束坐标 (x2, y2)
        :param duration: 滑动时长（秒），自动转为毫秒
        """
        x1, y1 = start_coordinate
        x2, y2 = end_coordinate
        # ADB 滑动时长单位为毫秒
        duration_ms = int(duration * 1000)
        cmd = f"{self.adb_prefix} shell input swipe {x1} {y1} {x2} {y2} {duration_ms}"
        self._run_cmd(cmd)
        self.logger.debug(f"执行滑动: ({x1},{y1}) -> ({x2},{y2}), 时长: {duration}s")

    def app_stop(self, package_name: str):
        """强制停止应用"""
        cmd = f"{self.adb_prefix} shell am force-stop {package_name}"
        self._run_cmd(cmd)
        self.logger.info(f"已停止应用: {package_name}")

    def app_start(self, package_name: str):
        """启动应用（通过包名启动默认Activity）"""
        cmd = f"{self.adb_prefix} shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1"
        self._run_cmd(cmd)
        self.logger.info(f"已启动应用: {package_name}")

    def current_app(self) -> Tuple[str, str]:
        """
        获取当前前台应用
        :return: (包名, Activity)
        """
        cmd = f"{self.adb_prefix} shell dumpsys window | findstr mCurrentFocus"
        success, output = self._run_cmd(cmd)
        if not success:
            return "", ""
        # 正则解析包名和Activity
        match = re.search(r"(\S+)/(\S+)}", output)
        if match:
            pkg, activity = match.group(1), match.group(2)
            self.logger.info(f"当前应用: {pkg}/{activity}")
            return pkg, activity
        self.logger.error(f"解析当前应用失败: {output}")
        return "", ""

    def input(self, input_text: str):
        """输入文本（自动转义特殊字符）"""
        # 转义 ADB 不支持的特殊字符
        input_text = input_text.replace(" ", "%s").replace("&", "\\&").replace('"', '\\"')
        cmd = f'{self.adb_prefix} shell input text "{input_text}"'
        self._run_cmd(cmd)
        self.logger.debug(f"执行输入: {input_text}")

    def press_key(self, key: int | str):
        """
        按键操作
        :param key: 键值（数字/字符串，如 3=HOME, 4=BACK）
        """
        cmd = f"{self.adb_prefix} shell input keyevent {key}"
        self._run_cmd(cmd)
        self.logger.debug(f"执行按键: {key}")

    def touch_down(self, x: int, y: int):
        """按下坐标（ADB 通过 sendevent 实现原生按下）"""
        # 发送触摸按下事件
        cmd = f"{self.adb_prefix} shell sendevent /dev/input/event1 3 57 1 && " \
              f"{self.adb_prefix} shell sendevent /dev/input/event1 3 53 {x} && " \
              f"{self.adb_prefix} shell sendevent /dev/input/event1 3 54 {y} && " \
              f"{self.adb_prefix} shell sendevent /dev/input/event1 0 0 0"
        self._run_cmd(cmd)
        self.logger.debug(f"执行按下: ({x}, {y})")

    def touch_up(self, x: int, y: int):
        """抬起坐标（ADB 通过 sendevent 实现原生抬起）"""
        # 发送触摸抬起事件
        cmd = f"{self.adb_prefix} shell sendevent /dev/input/event1 3 57 -1 && " \
              f"{self.adb_prefix} shell sendevent /dev/input/event1 0 0 0"
        self._run_cmd(cmd)
        self.logger.debug(f"执行抬起: ({x}, {y})")

    def long_press(self, x: int, y: int, duration: float):
        """
        长按操作
        :param x: 坐标X
        :param y: 坐标Y
        :param duration: 长按时长（秒）
        """
        # 长按 = 滑动同一个坐标，指定时长
        self.swipe((x, y), (x, y), duration)
        self.logger.debug(f"执行长按: ({x}, {y}), 时长: {duration}s")


if __name__ == "__main__":
    instance = ADB(None, None, "emulator-5554")
    for _ in range(8):
        instance.swipe((202, 150), (202, 763), duration=0.1)
    for _ in range(8):
        instance.swipe((202, 763), (202, 150), duration=0.8)
