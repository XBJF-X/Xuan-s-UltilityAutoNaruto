import concurrent.futures
import enum
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Tuple
from zoneinfo import ZoneInfo

from PySide6.QtCore import QThread

from utils.Config import Config
from utils.Device import Device


class CycleType(enum.IntEnum):
    """任务的周期类型"""
    DAILY = 0
    WEEKLY = 1
    MONTHLY = 2
    PERIOD = 3
    TEMP = 4


class BaseTask:
    class TaskError(Exception):
        """任务执行异常的基类"""
        pass

    class StepFailedError(TaskError):
        """步骤执行失败异常（如检测失败、点击无响应等）"""
        pass

    class EndEarly(TaskError):
        """步骤已经不需要再执行下去了，所以提前结束"""
        pass

    class Stop(TaskError):
        """步骤已经不需要再执行下去了，所以提前结束"""
        pass

    def __init__(
        self,
        task_name: str,
        config: Config,
        device: Device,
        callback: Callable
    ):
        # 任务信息
        self.create_time = datetime.now(ZoneInfo("Asia/Shanghai"))
        self.current_status = 2
        # 0 - 正在执行
        # 1 - 就绪状态，等待执行
        # 2 - 等待状态，等待就绪
        self.config = config
        self.data: Dict = config.tasks.get(task_name)
        self._execution_thread = None
        self._stop_event = threading.Event()
        self.task_name = self.data.get('任务名称')
        self.logger = logging.getLogger(self.task_name)
        self.task_id = self.data.get('任务ID')
        self.resolution = self.data.get('任务基准分辨率')
        self.is_activated = self.data.get('是否启用')
        self.cycle_type = CycleType(self.data.get('周期类型'))
        next_exec_ts = self.data.get('下次执行时间')
        if next_exec_ts == 0:
            # 若初始值为0，设置为当前UTC时间（或其他合理时间）
            self.next_execute_time = datetime.now(ZoneInfo("Asia/Shanghai"))
        else:
            # 从时间戳转换为datetime对象（指定UTC时区避免歧义）
            self.next_execute_time = datetime.fromtimestamp(next_exec_ts, tz=ZoneInfo("Asia/Shanghai"))
        # 任务执行需要的组件
        self.device = device
        self.callback = callback

    def __lt__(self, other):
        # 先比较task_id，若相同则比较时间戳（确保唯一性）
        if self.task_id != other.task_id:
            return self.task_id < other.task_id
        return self.create_time < other.create_time

    def __repr__(self):
        info_text = (f"任务名称: {self.task_name},"
                     f"任务ID:{self.task_id},"
                     f"任务状态:{self.current_status},"
                     f"周期类型:{CycleType(self.cycle_type)},"
                     f"下次执行时间:{self.next_execute_time}"
                     )

        info = {
            "任务名称": self.task_name,
            "任务ID": self.task_id,
            "任务状态": self.current_status,
            "任务基准分辨率": self.resolution,
            "是否启用": self.is_activated,
            "周期类型": self.cycle_type,
            "下次执行时间": self.next_execute_time
        }
        return info_text

    def run(self):
        """
        启动新线程执行execute避免阻塞进程
        """
        # 重置停止标志
        self._stop_event.clear()  # 重置停止标志
        # 保存线程对象以便后续停止
        self._execution_thread = threading.Thread(target=self._execute, daemon=True)
        self._execution_thread.start()

    def stop(self):
        """
        停止当前正在执行的任务
        """
        self.logger.info(f"正在停止任务: {self.task_name}")
        # 设置停止标志
        self._stop_event.set()
        # 如果任务线程正在运行，等待其结束
        if hasattr(self, '_execution_thread') and self._execution_thread.is_alive():
            self._execution_thread.join(timeout=5.0)
            if self._execution_thread.is_alive():
                self.logger.warning(f"任务 {self.task_name} 线程未能在5秒内停止")

    def _should_stop(self):
        """检查是否收到停止请求"""
        return self._stop_event.is_set()

    def _execute(self):
        """
        任务的处理逻辑，默认需要自己重载为所用的逻辑
        """
        self.home()
        self.callback(self)

    def detect_and_wait(self, params, wait_time=1, max_time=2.0, max_attempts=None, bool_debug: bool = True):
        """
        检测并等待一段时间
        """
        start_time = time.perf_counter()
        if max_attempts:
            for i in range(max_attempts):
                if self.device.detect(params, bool_debug):
                    QThread.msleep(int(wait_time * 1000))
                    return True
            return False
        else:
            while time.perf_counter() - start_time < max_time:
                if self.device.detect(params, bool_debug):
                    QThread.msleep(int(wait_time * 1000))
                    return True
            return False

    def click_and_wait(self, params, wait_time=1.5, max_time=2.0, click_times=1, max_attempts=None):
        """
        点击并等待一段时间
        """
        start_time = time.perf_counter()
        if max_attempts:
            for i in range(max_attempts):
                if self.device.click(params, self.resolution, times=click_times):
                    QThread.msleep(int(wait_time * 1000))
                    return True
            return False
        else:
            while time.perf_counter() - start_time < max_time:
                if self.device.click(params, self.resolution, times=click_times):
                    QThread.msleep(int(wait_time * 1000))
                    return True
            return False

    def auto_cycle_actioner(self,
                            actions: list[Tuple],
                            stop_conditions: List = None,
                            max_time: float = None,
                            max_workers: int = 1,
                            bool_debug: bool = False
                            ):
        """
        自动连点器 - 按坐标列表循环点击，支持两种停止条件

        Args:
            actions: 操作格式为 [(action, (x1,y1)) , ...]
            stop_conditions: 停止条件字典列表，用于传入判定条件（默认None）
            max_time: 最大点击轮次（默认None）
            max_workers: 最大工作线程数，默认1
            bool_debug: 要不要输出日志（避免有的过程检测次数过多导致日志累积）

        Returns:
            实际执行的点击轮次
        """
        # 检查参数
        if not actions:
            self.logger.warning("操作列表为空，无法执行")
            return 0

        # 检查停止条件
        if stop_conditions is None and max_time is None:
            self.logger.warning("未设置停止条件，将执行无限循环点击")

        start = time.perf_counter()
        stop_event = threading.Event()  # 用于通知停止的事件

        # 判定线程函数
        def check_stop_condition():
            nonlocal stop_event
            while not stop_event.is_set():
                # 执行检查
                # print(time.perf_counter())
                if self._should_stop():
                    stop_event.set()
                    raise self.Stop
                if max_time is not None and time.perf_counter() - start >= max_time:
                    self.logger.debug(f"达到最大时长 {max_time}，操作停止")
                    stop_event.set()
                    return
                if stop_conditions is not None:
                    for stop_condition in stop_conditions:
                        if self._should_stop():
                            stop_event.set()
                            raise self.Stop
                        if self.detect_and_wait(stop_condition, 0, max_attempts=1, bool_debug=False):
                            self.logger.debug(f"判定条件成立，点击停止")
                            stop_event.set()
                            return
                QThread.msleep(20)

        # 点击工作函数
        def click_worker(coord):
            nonlocal stop_event
            x, y = coord
            while not stop_event.is_set():
                self.device.click_position((x, y), resolution=self.resolution)
            return x, y

        def press_worker(coord):
            nonlocal stop_event
            x, y = coord
            instance = self.device.controller.touch_down(x, y)
            while not stop_event.is_set():
                QThread.msleep(50)
                continue
            instance.touch_up(x, y)
            return x, y

        # 如果设置了停止条件，启动判定线程
        if stop_conditions is not None or max_time is not None:
            checker_thread = threading.Thread(target=check_stop_condition, daemon=True)
            checker_thread.start()

        # 创建线程池
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for action in actions:
                futures.append(executor.submit(click_worker, action[1]))
                # if action[0] == "CLICK":
                #     futures.append(executor.submit(click_worker, action[1]))
                # elif action[0] == "PRESS":
                #     futures.append(executor.submit(press_worker, action[1]))
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                except Exception as e:
                    self.logger.error(f"点击{result}过程中发生错误: {e}")

        # 等待判定线程结束（如果有）
        if stop_conditions is not None or max_time is not None:
            checker_thread.join(timeout=1.0)

    def click_and_search(self, params_list, search_actions, search_times, wait_time=1):
        """
            循环执行元素点击搜索，支持多轮次、多位置尝试，并在过程中执行辅助操作（如点击或滑动）

            Args:
                params_list (List[Dict]): 待点击的元素参数列表，每个元素是一个字典，格式与click_and_wait一致
                search_actions (List[Dict]): 搜索过程中执行的辅助动作列表，支持两种操作：
                    - {'click': 点击参数}：执行点击操作
                    - {'swipe': 滑动参数}：执行滑动操作
                search_times (int): 搜索尝试的轮次
                wait_time (int): 点击后等待的时间

            Returns:
                bool: 是否成功找到并点击了params_list中的任一元素
        """
        self.logger.debug(f"元素点击搜索内容：")
        for params in params_list:
            if params['type'] == "ELEMENT":
                self.logger.debug(f"[元素] {params['name']}")
            elif params['type'] == "COORDINATE":
                self.logger.debug(f"[坐标] {params['coordinate']}")
        for i in range(search_times):
            if self._should_stop():
                raise self.Stop
            self.logger.debug(f"第 {i + 1} 次搜索")
            for params in params_list:
                if self.click_and_wait(params, wait_time=wait_time):
                    return True
            for action in search_actions:
                if "click" in action:
                    self.click_and_wait(action['click'])
                elif "swipe" in action:
                    self.device.swipe(
                        action['swipe']['start_coordinate'],
                        action['swipe']['end_coordinate'],
                        action['swipe']['duration'],
                        self.resolution)
        return False

    def detect_and_search(self, params_list, search_actions, search_max_time=None, once_max_time=1, wait_time=1):
        """
            循环执行元素检测，支持多轮次、多位置尝试，并在过程中执行辅助操作（如点击或滑动）

            Args:
                params_list (List[Dict]): 待点击的元素参数列表，每个元素是一个字典，格式与click_and_wait()一致
                search_actions (List[Dict]): 搜索过程中执行的辅助动作列表，支持两种操作：
                    - {'click': 点击参数}：执行点击操作
                    - {'swipe': 滑动参数}：执行滑动操作
                search_max_time (float): 搜索尝试的轮次数组
                once_max_time (float):单次搜索的最大时长，定义与detect_and_wait()一致
                wait_time (int): 如果寻找到了，要等待几秒

            Returns:
                bool: 是否成功找到并点击了params_list中的任一元素
        """
        self.logger.debug(f"元素检测搜索内容：")
        for params in params_list:
            if params['type'] == "ELEMENT":
                self.logger.debug(f"[元素] {params['name']}")
            elif params['type'] == "SCENE":
                self.logger.debug(f"[场景] {params['name']}")
        start = time.perf_counter()
        while True:
            if self._should_stop():
                raise self.Stop
            if search_max_time:
                if time.perf_counter() - start > search_max_time:
                    self.logger.warning(f"搜索超时：{time.perf_counter() - start:.1f}s")
                    return 0
            for index, params in enumerate(params_list):
                if self._should_stop():
                    raise self.Stop
                if self.detect_and_wait(params, wait_time=wait_time, max_time=once_max_time):
                    return index + 1
            for action in search_actions:
                if self._should_stop():
                    raise self.Stop
                if "click" in action:
                    self.click_and_wait(action['click'], max_time=1)
                elif "swipe" in action:
                    self.device.swipe(
                        action['swipe']['start_coordinate'],
                        action['swipe']['end_coordinate'],
                        action['swipe']['duration'],
                        self.resolution)

    def click_and_input(self, input_edit_params, input_text):
        """
        第一个参数为需要点击的输入框的参数，第二个为要输入的文字
        """
        if self.click_and_wait(input_edit_params):
            self.device.input(input_text)
            self.click_and_wait(input_edit_params)
            return True
        return False

    def pass_secondary_password(self):
        """
        过二级密码的通用函数,返回True表示检测到了二级密码的弹窗,反之没有
        """
        # 可能有二级密码，用户输入密码
        if self.detect_and_wait({
            "type": "SCENE",
            "name": "二级密码"
        }):
            self.logger.debug("出现二级密码窗口")
            passward = self.config.get_config("二级密码")
            if len(passward) != 6:
                raise self.StepFailedError("请检查二级密码！")

            # 输入操作
            self.click_and_input({
                "type": "ELEMENT",
                "name": "二级密码-输入框"
            }, passward)
            # 点击二级密码-确定
            if not self.click_and_wait({
                "type": "ELEMENT",
                "name": "二级密码-确定"
            }):
                raise self.StepFailedError("二级密码验证失败")
            self.logger.debug("验证二级密码结束")
            return True
        self.logger.debug("未出现二级密码窗口")
        return False

    def esc(self, x_names=None):
        """
        回退一次，默认点击X，毕竟你游大部分情况下都能点X返回上一步，也可自定义返回点击的元素
        """
        if x_names is None:
            x_names = ["决斗场-X", "X", "招募-X", "情报站-X"]
        for x_name in x_names:
            if self.click_and_wait(
                    {
                        'type': "ELEMENT",
                        'name': x_name
                    },
                    max_time=0.4
            ):
                return True
        return False

    def home(self, home_name="主场景", x_names=None, max_attempts=None, max_time=30):
        """
        不断调用esc回退至主场景，也可以修改home_name和x_names达到回退到某个场景的目的
        """
        if x_names is None:
            x_names = ["决斗场-X", "X", "招募-X", "情报站-X"]
        self.logger.debug(f"回退至[{home_name}]")
        attempt = 0
        start = time.perf_counter()
        while not self.device.detect({
            'type': "SCENE",
            'name': home_name
        }):
            attempt += 1
            if attempt > 1:
                self.device.click_position([1526, 44], self.resolution)
            if not self.esc(x_names):
                self.logger.warning(f"回退失败{attempt}次，已过去 {time.perf_counter() - start:2f}s")
            if max_attempts is not None:
                if attempt >= max_attempts:
                    self.logger.error(f"已达最大回退次数：{max_attempts}")
                    return False
            else:
                if time.perf_counter() - start > max_time:
                    self.logger.error(f"已达最大回退时长：{max_time}")
                    return False
        return True

    def press(self, key, wait_time=0):
        """
        模拟设备按键，输入key即为按键名称
        """
        self.device.press(key)
        if wait_time:
            QThread.msleep(int(wait_time * 1000))

    def restart(self):
        """
        重启火影忍者
        """
        self.device.restart()

    def _update_next_execute_time(self,
                                  time_offset: timedelta = timedelta(hours=5),
                                  delta: timedelta = None
                                  ):
        """
        用于更新下次执行时间，不传入参数则更新为自己周期的第一天的五点
        传入timedelta对象可以自定义延迟，即当前时间后多久再次执行
        """
        # 明确指定中国时区（带时区的当前时间）
        china_tz = ZoneInfo("Asia/Shanghai")
        current_time = datetime.now(china_tz)

        if delta is not None:
            self.next_execute_time = current_time + delta
            self.logger.info(f"下次执行时间为：{self.next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
            self.config.set_task_config(self.task_name, "下次执行时间", int(self.next_execute_time.timestamp()))
            return
        if self.cycle_type == CycleType.DAILY:
            next_day = current_time + timedelta(days=1)
            # 新建时间时指定时区（与current_time一致）
            self.next_execute_time = datetime(
                next_day.year, next_day.month, next_day.day, 0, 0,
                tzinfo=china_tz  # 关键：添加时区信息
            ) + time_offset
            self.logger.info(f"下次执行时间为：{self.next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
            self.config.set_task_config(self.task_name, "下次执行时间", int(self.next_execute_time.timestamp()))

        elif self.cycle_type == CycleType.WEEKLY:
            days_ahead = 7 - current_time.weekday()
            if days_ahead == 0:
                days_ahead = 7
            next_monday = current_time + timedelta(days=days_ahead)
            self.next_execute_time = datetime(
                next_monday.year, next_monday.month, next_monday.day, 0, 0,
                tzinfo=china_tz
            ) + time_offset
            self.logger.info(f"下次执行时间为：{self.next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
            self.config.set_task_config(self.task_name, "下次执行时间", int(self.next_execute_time.timestamp()))

        elif self.cycle_type == CycleType.MONTHLY:
            year = current_time.year
            month = current_time.month + 1
            if month > 12:
                month = 1
                year += 1
            self.next_execute_time = datetime(
                year, month, 1, 0, 0,
                tzinfo=china_tz  # 关键：添加时区信息
            ) + time_offset
            self.logger.info(f"下次执行时间为：{self.next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
            self.config.set_task_config(self.task_name, "下次执行时间", int(self.next_execute_time.timestamp()))
        else:
            self.logger.warning(f"{CycleType(self.cycle_type)}任务")
