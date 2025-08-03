import heapq
import json
import logging
import os
import threading
import time
from datetime import datetime
from typing import Dict, TypeVar, Generic, List
from zoneinfo import ZoneInfo

import cv2
import numpy as np

from PySide6 import QtWidgets
from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition, Qt, QObject, Slot
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QLayout, QBoxLayout

from StaticFunctions import get_real_path, cv_save
from ui.DailyQuestsHelper_ui import Ui_DailyQuestsHelper
from utils.core.Base.Recognizer import Recognizer
from utils.core.Config import Config
from utils.core.Device import Device
from utils.core.Task import TASK_TYPE_MAP
from utils.core.Task.BaseTask import BaseTask, CycleType

T = TypeVar('T', bound=BaseTask)
W = TypeVar('W', bound=QWidget)


class PriorityQueue(Generic[T]):
    def __init__(self):
        self.heap: List[T] = []  # 存储 Task 的列表

    def enqueue(self, item: BaseTask):
        heapq.heappush(self.heap, item)  # 插入元素，自动维护堆序

    def dequeue(self):
        if not self.is_empty():
            return heapq.heappop(self.heap)  # 返回优先级最小的元素

    def is_empty(self):
        return len(self.heap) == 0

    def peek(self):
        return self.heap.copy()


class TaskWidgetList(Generic[W]):
    def __init__(self, layout: QBoxLayout):
        self.widgets: List[W] = []  # 存储QWidget的列表
        self.tasks: Dict[str, BaseTask] = {}  # 任务名到任务对象的映射
        self.layout = layout  # 关联的布局

    def add_widget(self, widget: W, task: BaseTask):
        """添加控件并保持有序"""

        # 存储任务引用
        self.tasks[task.task_name] = task
        # 计算插入位置
        insert_index = self._find_insert_index(task)

        # 插入到列表
        self.widgets.insert(insert_index, widget)

        # 插入到布局
        self.layout.insertWidget(insert_index, widget)

        # 设置控件属性以便后续查找
        widget.setProperty("task_name", task.task_name)

    def remove_widget(self, task_name: str):
        """移除指定任务的控件"""

        # 从任务映射中移除
        if task_name in self.tasks:
            del self.tasks[task_name]

        # 从控件列表中移除
        for i, widget in enumerate(self.widgets):
            widget_task_name = widget.property("task_name")
            if widget_task_name == task_name:
                # 从列表中移除
                self.widgets.pop(i)

                # 从布局中移除
                self.layout.takeAt(i)
                widget.deleteLater()
                return True
        return False

    def _find_insert_index(self, task: BaseTask) -> int:
        """使用二分查找确定插入位置"""
        lo, hi = 0, len(self.widgets)
        while lo < hi:
            mid = (lo + hi) // 2
            mid_widget = self.widgets[mid]
            mid_task_name = mid_widget.property("task_name")
            mid_task = self.tasks[mid_task_name]

            # 直接比较任务对象
            if self._compare_tasks(task, mid_task) < 0:
                hi = mid
            else:
                lo = mid + 1
        return lo

    @staticmethod
    def _compare_tasks(task1: BaseTask, task2: BaseTask) -> int:
        """比较两个任务的优先级"""
        # 比较执行时间
        if task1.next_execute_time != task2.next_execute_time:
            return -1 if task1.next_execute_time < task2.next_execute_time else 1

        # 比较任务ID
        if task1.task_id != task2.task_id:
            return -1 if task1.task_id < task2.task_id else 1

        # 比较创建时间
        if task1.create_time != task2.create_time:
            return -1 if task1.create_time < task2.create_time else 1

        return 0


class TimerThread(QThread):
    """被动触发的定时器线程，用于延时后发送信号"""
    timeout = Signal(object)  # 携带数据的超时信号

    def __init__(self):
        super().__init__()
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.delay_ms = 0
        self.data = None
        self._is_triggered = False
        self._is_running = True

    @Slot(int, object)
    def trigger(self, delay_ms, data=None):
        """触发定时器，设置延时时间和数据"""
        self.mutex.lock()
        self.delay_ms = delay_ms
        self.data = data
        self._is_triggered = True
        self.condition.wakeOne()  # 唤醒等待的线程
        self.mutex.unlock()

    def run(self):
        """线程执行函数"""
        while self._is_running:
            self.mutex.lock()
            # 等待触发信号
            while not self._is_triggered and self._is_running:
                self.condition.wait(self.mutex)

            if not self._is_running:  # 检查是否需要退出
                self.mutex.unlock()
                break

            delay_ms = self.delay_ms
            data = self.data
            self._is_triggered = False  # 重置触发状态
            self.mutex.unlock()

            # 执行延时
            if delay_ms > 0:
                QThread.msleep(delay_ms)
                # 延时结束后发送信号
                self.timeout.emit(data)

    def stop(self):
        """停止线程（在应用退出时调用）"""
        self.mutex.lock()
        self._is_running = False
        self.condition.wakeOne()
        self.mutex.unlock()
        self.wait()


class Scheduler(QObject):
    add_task_ui_signal = Signal(BaseTask, int)
    remove_task_ui_signal = Signal(BaseTask, int)

    def __init__(self, ui: Ui_DailyQuestsHelper, config: Config):
        super().__init__()
        self.logger = logging.getLogger("调度器")
        self.running = False
        self.UI = ui
        self.config = config
        self.scene_templates = self.preprocess_templates("src/SceneInfo.json")
        self.element_templates = self.preprocess_templates("src/ElementInfo.json")
        self.recognizer = Recognizer(self.scene_templates, self.element_templates)
        self.running_queue = PriorityQueue[BaseTask]()  # 执行队列
        self.ready_queue = PriorityQueue[BaseTask]()  # 就绪队列
        self.waiting_queue = PriorityQueue[BaseTask]()  # 等待队列

        # 初始化UI相关属性
        self.init_scroll_area_layouts()  # 初始化滚动区域布局
        self.running_widget_list = TaskWidgetList(self.running_layout)  # 执行队列
        self.ready_widget_list = TaskWidgetList(self.ready_layout)  # 就绪队列
        self.waiting_widget_list = TaskWidgetList(self.waiting_layout)  # 等待队列

        # 连接信号到槽
        self.add_task_ui_signal.connect(self.create_task_ui)
        self.remove_task_ui_signal.connect(self.remove_task_ui)

        self.device: Device = None

        self.timer_thread = TimerThread()
        self.timer_thread.timeout.connect(self.scan)

        # tracemalloc.start()
        # self.snapshot1 = tracemalloc.take_snapshot()
        self.logger.info("初始化完成...")

    def start(self):
        self.logger.info("正在启动调度器...")
        self.UI.start_schedule_button.setText("暂停")
        self.UI.start_schedule_button.setEnabled(False)
        self.running = True
        self.device = Device(self.config, self.recognizer)

        for task_info in self.config.tasks.values():
            if not task_info.get("是否启用", 0):
                continue
            if task_info.get("周期类型", 4) == CycleType.TEMP.value:
                continue

            task_name = task_info.get('任务名称')
            task_class = TASK_TYPE_MAP.get(task_name, None)
            if not task_class:
                self.logger.warning(f"[{task_name}] 任务创建出错")
                continue
            task_instance = task_class(
                task_name,
                self.config,
                self.device,
                self._execute_done_callback
            )
            self.waiting_queue.enqueue(task_instance)
            self.create_task_ui(task_instance, 2)
        # 启动调度器开始扫描
        self.timer_thread.start()  # 启动线程，线程会进入等待状态
        self.timer_thread.trigger(self.config.get_config("扫描间隔"),1000)
        self.UI.start_schedule_button.setEnabled(True)
        self.logger.info("调度器已完成启动")

    def stop(self):
        """
            停止调度器及其所有任务
        """
        self.logger.info("正在停止调度器...")
        self.UI.start_schedule_button.setText("启动")
        self.UI.start_schedule_button.setEnabled(False)
        self.running = False

        # 停止定时器线程
        if hasattr(self, 'timer_thread'):
            self.timer_thread.stop()

        # 停止所有正在运行的任务
        running_tasks = self.running_queue.peek()[:]  # 复制当前运行队列
        for task in running_tasks:
            task.stop()

        # 清空所有队列
        self.running_queue = PriorityQueue[BaseTask]()
        self.ready_queue = PriorityQueue[BaseTask]()
        self.waiting_queue = PriorityQueue[BaseTask]()

        # 清空UI显示
        self.clear_ui()

        # 释放设备资源
        self.device = None
        self.UI.start_schedule_button.setEnabled(True)
        self.logger.info("调度器已完全停止")

    def clear_ui(self):
        """清空所有UI队列显示"""
        # 清空运行队列UI
        for widget in self.running_widget_list.widgets[:]:
            task_name = widget.property("task_name")
            self.running_widget_list.remove_widget(task_name)

        # 清空就绪队列UI
        for widget in self.ready_widget_list.widgets[:]:
            task_name = widget.property("task_name")
            self.ready_widget_list.remove_widget(task_name)

        # 清空等待队列UI
        for widget in self.waiting_widget_list.widgets[:]:
            task_name = widget.property("task_name")
            self.waiting_widget_list.remove_widget(task_name)

    def preprocess_templates(self, info_path) -> Dict:
        """预处理模板图像"""
        # self.logger.debug("预处理模版图像：")
        templates_dic = {}
        with open(get_real_path(info_path), "r", encoding='utf-8') as f:
            templates = json.load(f)

        for key, template in templates.items():
            try:
                gray_path = get_real_path(os.path.join(template['path'], "Gray", f"{key}.png"))
                alpha_path = get_real_path(os.path.join(template['path'], "Alpha", f"{key}.png"))
                # self.logger.debug("模板路径：%s", template_path)
                with open(gray_path, 'rb') as f:
                    gray_array = np.frombuffer(f.read(), dtype=np.uint8)
                    gray = cv2.imdecode(gray_array, cv2.IMREAD_GRAYSCALE)
                    if gray is None:
                        raise FileNotFoundError(f"文件存在但无法读取: {gray_path}")
                    template['GRAY'] = gray.astype(np.uint8)
                with open(alpha_path, 'rb') as f:
                    alpha_array = np.frombuffer(f.read(), dtype=np.uint8)
                    alpha = cv2.imdecode(alpha_array, cv2.IMREAD_GRAYSCALE)
                    if alpha is None:
                        raise FileNotFoundError(f"文件存在但无法读取: {alpha_path}")
                    template['MASK'] = alpha.astype(np.uint8)

                templates_dic[key] = template
            except Exception as e:
                self.logger.error("模板预处理失败: %s", f"{template['path']}{key}.png")
        return templates_dic

    def init_scroll_area_layouts(self):
        """初始化三个滚动区域的布局"""
        # 运行队列区域布局
        self.running_layout = QtWidgets.QVBoxLayout(self.UI.scroll_area_running_content)
        self.running_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.running_layout.setSpacing(5)

        # 就绪队列区域布局
        self.ready_layout = QtWidgets.QVBoxLayout(self.UI.scroll_area_ready_content)
        self.ready_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.ready_layout.setSpacing(5)

        # 等待队列区域布局
        self.waiting_layout = QtWidgets.QVBoxLayout(self.UI.scroll_area_wait_content)
        self.waiting_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.waiting_layout.setSpacing(5)

    def create_task_ui(self, task: BaseTask, status):
        """为任务创建UI元素并添加到对应队列区域"""
        # 创建任务控件
        widget, time_label = self._create_task_widget(task)

        # 更新标签内容
        time_label.setText(f"{task.task_name}\n下次执行:{task.next_execute_time.strftime('%Y-%m-%d %H:%M:%S')}")
        # 根据任务状态添加到对应列表
        if status == 0:  # 运行中
            self.running_widget_list.add_widget(widget, task)
        elif status == 1:  # 就绪
            self.ready_widget_list.add_widget(widget, task)
        elif status == 2:  # 等待中
            self.waiting_widget_list.add_widget(widget, task)

    def remove_task_ui(self, task: BaseTask, status):
        """从UI中移除任务元素"""
        # 从对应列表中移除
        if status == 0:  # 运行中
            self.running_widget_list.remove_widget(task.task_name)
        elif status == 1:  # 就绪
            self.ready_widget_list.remove_widget(task.task_name)
        elif status == 2:  # 等待中
            self.waiting_widget_list.remove_widget(task.task_name)

    def scan(self):
        """
        1.扫描等待队列中的任务，如果可以执行则放入就绪队列
        2.扫描就绪队列，如果执行队列为空且就绪队列不为空，则从就绪队列中取出优先级最高的Task交给Executor执行
        """
        start = time.perf_counter()
        if self.UI.bool_save_img.isChecked():
            threading.Thread(target=self.save_screen).start()

        moved_tasks = []  # 记录从等待队列移动到就绪队列的任务

        # self.logger.debug("Scanning...")
        # for element in self.controller.device.xpath('//*').all():
        #     print(f"元素: {element.info}")
        #     # 打印关键属性
        #     print(f"  text: {element.info.get('text')}")
        #     print(f"  resourceId: {element.info.get('resourceId')}")
        #     print(f"  className: {element.info.get('className')}")
        #     print(f"  bounds: {element.info.get('bounds')}")
        #     print("-" * 30)
        # 扫描等待队列，检查任务是否可以执行
        waiting_tasks = self.waiting_queue.peek()[:]  # 复制一份当前等待队列
        for task in waiting_tasks:
            if task.current_status != 2:  # 只处理等待状态的任务
                continue

            # 根据周期类型判断是否需要执行
            should_execute = task.next_execute_time <= datetime.now(ZoneInfo("Asia/Shanghai"))
            # 如果满足执行条件，将任务从等待队列移至就绪队列
            if should_execute:
                self.waiting_queue.dequeue()  # 从等待队列移除
                self.remove_task_ui_signal.emit(task, 2)
                task.current_status = 1  # 更新状态为就绪
                self.ready_queue.enqueue(task)  # 添加到就绪队列
                self.add_task_ui_signal.emit(task, 1)
                moved_tasks.append(task)
                self.logger.info(f"[{task.task_name}]-[{task.task_id}] 就绪")

        # 如果有任务被移动，重新触发扫描以检查就绪队列
        if moved_tasks:
            if self.running:
                self.timer_thread.trigger(0)  # 立即触发下一次扫描

        # 扫描就绪队列，当执行队列为空时将就绪队列中的任务移至执行队列
        if self.running_queue.is_empty() and not self.ready_queue.is_empty():
            # 移除就绪队列中的任务
            task_to_execute = self.ready_queue.dequeue()
            self.remove_task_ui_signal.emit(task_to_execute, 1)
            task_to_execute.current_status = 0  # 更新状态为执行中
            # 增加运行队列中的任务
            self.running_queue.enqueue(task_to_execute)
            self.add_task_ui_signal.emit(task_to_execute, 0)
            task_to_execute.run()

        if self.running:
            # 继续下一次扫描
            # snapshot2 = tracemalloc.take_snapshot()
            # top_stats = snapshot2.compare_to(self.snapshot1, 'lineno')
            # print("[内存增长统计]")
            # for stat in top_stats[:10]:  # 打印前10个增长最多的项
            #     print(stat)
            wait_time = max(0.0, self.config.get_config("扫描间隔") - 1000*(time.perf_counter() - start))
            self.timer_thread.trigger(int(wait_time))  # 每秒扫描一次

    def _execute_done_callback(self, task: BaseTask):
        self.running_queue.dequeue()
        self.remove_task_ui_signal.emit(task, 0)
        if task.cycle_type != CycleType.TEMP and self.running:
            task.current_status = 2
            task.create_time = datetime.now(ZoneInfo("Asia/Shanghai"))
            # 添加到等待队列
            self.waiting_queue.enqueue(task)
            self.add_task_ui_signal.emit(task, 2)

    @staticmethod
    def _create_task_widget(task: BaseTask) -> tuple[QWidget, QLabel]:
        """创建任务控件"""
        item_widget = QWidget()
        # # 设置固定大小（如果传入size参数则使用该大小）
        item_widget.setFixedHeight(50)

        item_widget.setStyleSheet("""
                QWidget {
                    border: 1px solid #888;
                    border-radius: 5px;
                    background-color: #f0f0f0;
                }
            """)

        # 创建水平布局并设置为居中对齐
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(10, 0, 10, 0)
        item_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 倒计时时间标签
        time_label = QLabel(f"{task.task_name}\n下次执行:{task.next_execute_time.strftime("%Y-%m-%d %H:%M:%S")}")
        time_label.setStyleSheet("""
                border: none;
                background-color: transparent;
                font-family: 'Microsoft YaHei'; 
                font-size: 13px; 
                font-weight: bold; 
                color: black;
            """)
        item_layout.addWidget(time_label)

        return item_widget, time_label

    def save_screen(self):
        """保存截图到文件"""
        try:
            screen = self.device.screen_cap()
            if screen is None or screen.size == 0:
                self.logger.warning("图像数据为空，无法保存")
                return

            image_dir = get_real_path("image")
            os.makedirs(image_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')
            save_path = os.path.join(image_dir, f"{timestamp}.png")
            cv_save(save_path, screen)
            self.logger.info("截图保存到%s", save_path)

            # success = cv2.imwrite(save_path, self.screen, [cv2.IMWRITE_PNG_COMPRESSION, 0])
            # if success:
            #     self.logger.info(f"截图保存到{save_path}")
            # else:
            #     self.logger.error(f"保存图像失败: {save_path}")

        except Exception as e:
            self.logger.error(f"保存图像时发生错误: {e}")
