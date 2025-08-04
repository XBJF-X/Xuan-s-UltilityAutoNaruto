import heapq
import logging
import os
import threading
import time
from datetime import datetime
from typing import Dict, TypeVar, Generic, List, Optional
from zoneinfo import ZoneInfo

from PySide6 import QtWidgets
from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition, Qt, QObject, Slot
from PySide6.QtWidgets import QWidget, QLabel, QBoxLayout, QVBoxLayout

from StaticFunctions import get_real_path, cv_save
from ui.DailyQuestsHelper_ui import Ui_DailyQuestsHelper
from utils.Base.Recognizer import Recognizer
from utils.Config import Config
from utils.Device import Device
from utils.Task import TASK_TYPE_MAP
from utils.Task.BaseTask import BaseTask, CycleType

T = TypeVar('T', bound=BaseTask)
W = TypeVar('W', bound=QWidget)


class PriorityQueue(Generic[T]):
    def __init__(self):
        self.heap: List[T] = []  # 存储 Task 的列表
        self.task_dic: Dict[str:T] = {}

    def enqueue(self, item: T):
        heapq.heappush(self.heap, item)  # 插入元素，自动维护堆序
        self.task_dic[item.task_name] = item

    def dequeue(self):
        if not self.is_empty():
            item = heapq.heappop(self.heap)
            del self.task_dic[item.task_name]
            return item  # 返回优先级最小的元素

    def is_empty(self):
        return len(self.heap) == 0

    def peek(self):
        return self.heap.copy()

    def remove(self, task_name: str):
        """从队列中移除指定任务"""
        try:
            self.heap.remove(self.task_dic[task_name])
            heapq.heapify(self.heap)  # 重新堆化
            return True
        except ValueError:
            return False

    def update(self, task_name: str, **kwargs) -> bool:
        """在队列中更新某个任务的状态"""
        if task_name not in self.task_dic:
            return False
        task = self.task_dic[task_name]
        # 更新任务属性
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
            else:
                # 可以记录警告或忽略
                pass
        # 从堆中移除并重新插入
        try:
            self.heap.remove(task)
            heapq.heapify(self.heap)  # 重新堆化
            heapq.heappush(self.heap, task)  # 重新插入
            return True
        except ValueError:
            return False


class TaskWidgetList(Generic[W]):
    def __init__(self, layout: QBoxLayout):
        self.widgets: List[W] = []  # 存储QWidget的列表
        self.tasks: Dict[str, T] = {}  # 任务名到任务对象的映射
        self.layout = layout  # 关联的布局

    def add_widget(self, widget: W, task: T):
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

        # 根据任务状态设置初始可见性
        widget.setVisible(task.is_activated)

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

    def find_widget(self, task_name: str) -> Optional[W]:
        """查找指定任务的控件"""
        for widget in self.widgets:
            if widget.property("task_name") == task_name:
                return widget
        return None

    def update_task_widget(self, task_name: str, **kwargs) -> bool:
        """更新任务控件的显示信息（如下次次执行时间）"""
        if task_name not in self.tasks:
            return False
        task = self.tasks[task_name]
        widget = self.find_widget(task_name)
        if not widget:
            return False
        # 更新属性
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        widget, _, _ = create_task_widget(task)

        # 重新排序控件（因为执行时间变更可能影响优先级）
        if task in self.tasks.values():
            # 先移除再重新添加以触发排序
            self.remove_widget(task.task_name)
            self.add_widget(widget, task)

    def _find_insert_index(self, task: T) -> int:
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
    def _compare_tasks(task1: T, task2: T) -> int:
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

    def __init__(self, ui: Ui_DailyQuestsHelper, recognizer: Recognizer, config: Config, ref_map: Dict):
        super().__init__()
        self.logger = logging.getLogger("调度器")
        self.running = False
        self.UI = ui
        self.config = config
        self.task_common_control_ref_map = ref_map
        self.recognizer = recognizer
        self.running_queue = PriorityQueue[BaseTask]()  # 执行队列
        self.ready_queue = PriorityQueue[BaseTask]()  # 就绪队列
        self.waiting_queue = PriorityQueue[BaseTask]()  # 等待队列
        self.all_tasks = {}  # 存储所有任务，包括未启用的

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
        # 启动调度器开始扫描
        self.timer_thread.start()  # 启动线程，线程会进入等待状态

        # tracemalloc.start()
        # self.snapshot1 = tracemalloc.take_snapshot()
        self.logger.info("初始化完成...")

    def start(self):
        self.logger.info("正在启动调度器...")
        self.UI.start_schedule_button.setEnabled(False)
        self.running = True
        self.device = Device(self.config, self.recognizer)

        for task_info in self.config.tasks.values():
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
            self.all_tasks[task_name] = task_instance  # 添加到所有任务集合

            self.waiting_queue.enqueue(task_instance)
            self.create_task_ui(task_instance, 2)

        self.timer_thread.trigger(self.config.get_config("扫描间隔"), 1000)
        self.UI.start_schedule_button.setEnabled(True)
        self.UI.start_schedule_button.setText("暂停")
        self.logger.info("调度器已完成启动")

    def stop(self):
        """
            停止调度器及其所有任务
        """
        self.logger.info("正在停止调度器...")
        self.UI.start_schedule_button.setEnabled(False)
        self.running = False

        # 停止所有正在运行的任务
        running_tasks = self.running_queue.peek()[:]  # 复制当前运行队列
        for task in running_tasks:
            task.stop()

        # 清空所有队列
        self.running_queue = PriorityQueue[BaseTask]()
        self.ready_queue = PriorityQueue[BaseTask]()
        self.waiting_queue = PriorityQueue[BaseTask]()
        self.all_tasks.clear()

        # 清空UI显示
        self.clear_ui()

        # 释放设备资源
        self.device = None
        self.UI.start_schedule_button.setEnabled(True)
        self.UI.start_schedule_button.setText("启动")
        self.logger.info("调度器已完全停止")

    def toggle_task_activation(self, state, task_name: str):
        """切换任务的启用/禁用状态"""
        checkbox_widget = self.task_common_control_ref_map[task_name]["CheckBox"]
        self.config.set_task_config(task_name, "是否启用", checkbox_widget.isChecked())
        if not self.running:
            return
        checkbox_widget.setEnabled(False)
        is_activated = checkbox_widget.isChecked()
        self.logger.info(f"任务 {task_name} 切换为 {'已启用' if is_activated else '已禁用'}")

        if not self.waiting_queue.update(task_name, is_activated=is_activated):
            if not self.ready_queue.update(task_name, is_activated=is_activated):
                if not self.running_queue.update(task_name, is_activated=is_activated):
                    self.logger.error(f"切换 {task_name} 为 {checkbox_widget.isChecked()}失败")
                    return
                else:
                    self.running_widget_list.update_task_widget(task_name, is_activated=is_activated)
            else:
                self.ready_widget_list.update_task_widget(task_name, is_activated=is_activated)
        else:
            self.waiting_widget_list.update_task_widget(task_name, is_activated=is_activated)
        checkbox_widget.setEnabled(True)
        self.logger.info(f"任务 {task_name} {'已启用' if is_activated else '已禁用'}")

        # 触发一次扫描
        self.timer_thread.trigger(0)

    def task_next_execute_time_editfinished(self, task_name):
        """如果清空则立即执行任务"""
        lineedit_widget = self.task_common_control_ref_map[task_name]["LineEdit"]
        if lineedit_widget.text() == "":
            self.config.set_task_config(task_name, "下次执行时间", int(datetime.now(ZoneInfo("Asia/Shanghai")).timestamp()))
            lineedit_widget.setText(datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S"))
        if not self.running:
            return
        lineedit_widget.setEnabled(False)
        net = datetime.now(ZoneInfo("Asia/Shanghai"))
        if not self.waiting_queue.update(task_name, next_execute_time=net):
            if not self.ready_queue.update(task_name, next_execute_time=net):
                if not self.running_queue.update(task_name, next_execute_time=net):
                    self.logger.error(f"任务 {task_name} 放入等待队列等待立即执行失败")
                    return
                else:
                    self.running_widget_list.update_task_widget(task_name, next_execute_time=net)
            else:
                self.ready_widget_list.update_task_widget(task_name, next_execute_time=net)
        else:
            self.waiting_widget_list.update_task_widget(task_name, next_execute_time=net)
        lineedit_widget.setEnabled(True)
        self.logger.info(f"任务 {task_name} 已放入等待队列等待立即执行")

        # 触发一次扫描
        self.timer_thread.trigger(0)

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
        widget, _, _ = create_task_widget(task)
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

        # 扫描等待队列，检查任务是否可以执行
        waiting_tasks = self.waiting_queue.peek()[:]  # 复制一份当前等待队列
        for task in waiting_tasks:
            if not task.is_activated:  # 不处理未启用的任务
                continue
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
            # 检查任务是否仍处于启用状态
            if not task_to_execute.is_activated:
                # 如果已被禁用，将其移至等待队列
                task_to_execute.current_status = 2
                self.waiting_queue.enqueue(task_to_execute)
                self.add_task_ui_signal.emit(task_to_execute, 2)
                if self.running:
                    # 继续下一次扫描
                    wait_time = max(0.0, self.config.get_config("扫描间隔") - 1000 * (
                            time.perf_counter() - start))
                    self.timer_thread.trigger(int(wait_time))  # 每秒扫描一次
                return
            task_to_execute.current_status = 0  # 更新状态为执行中
            # 增加运行队列中的任务
            self.running_queue.enqueue(task_to_execute)
            self.add_task_ui_signal.emit(task_to_execute, 0)
            task_to_execute.run()

        if self.running:
            # 继续下一次扫描
            wait_time = max(0.0, self.config.get_config("扫描间隔") - 1000 * (
                    time.perf_counter() - start))
            self.timer_thread.trigger(int(wait_time))  # 每秒扫描一次

    def _execute_done_callback(self, task: BaseTask):
        lineedit = self.task_common_control_ref_map[task.task_name]["LineEdit"]
        lineedit.setText(task.next_execute_time.strftime("%Y-%m-%d %H:%M:%S"))
        self.running_queue.dequeue()
        self.remove_task_ui_signal.emit(task, 0)
        # 只有启用的非临时任务才会回到等待队列
        if task.is_activated and task.cycle_type != CycleType.TEMP and self.running:
            task.current_status = 2
            task.create_time = datetime.now(ZoneInfo("Asia/Shanghai"))
            # 添加到等待队列
            self.waiting_queue.enqueue(task)
            self.add_task_ui_signal.emit(task, 2)

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


def create_task_widget(task: BaseTask) -> tuple[QWidget, QLabel, QLabel]:
    """创建任务控件，包含两个独立标签（任务名称和执行时间）"""
    item_widget = QWidget()
    item_widget.setFixedHeight(50)
    item_widget.setContentsMargins(0, 5, 0, 5)
    item_widget.setStyleSheet("""
            QWidget {
                border: 1px solid #888;
                border-radius: 5px;
                background-color: #f0f0f0;
            }
        """)

    # 创建水平布局并设置为居中对齐
    item_layout = QVBoxLayout(item_widget)
    item_layout.setContentsMargins(5, 0, 5, 0)
    item_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # 任务名称标签（第一个标签）
    name_label = QLabel(task.task_name)
    name_label.setStyleSheet("""
            border: none;
            background-color: transparent;

            font-size: 14pt; 

            color: black;
        """)
    item_layout.addWidget(name_label, alignment=Qt.AlignmentFlag.AlignLeft)

    # 执行时间标签（第二个标签，灰色小字体）
    current_date = datetime.now(ZoneInfo("Asia/Shanghai")).date()
    task_date = task.next_execute_time.date()
    delta = (task_date - current_date).days

    if delta == 0:
        date_str = "今天"
    elif delta == 1:
        date_str = "明天"
    else:
        date_str = task.next_execute_time.strftime("%Y-%m-%d")

    time_str = task.next_execute_time.strftime("%H:%M:%S")
    time_label = QLabel(f"下次执行 ：{date_str} {time_str}")
    time_label.setStyleSheet("""
            border: none;
            background-color: transparent;
            font-family: 'Microsoft YaHei'; 
            font-size: 10pt;  /* 小字体 */
            font-weight: bold; 
            color: #666666;   /* 灰色 */
        """)
    item_layout.addWidget(time_label, alignment=Qt.AlignmentFlag.AlignLeft)

    return item_widget, name_label, time_label
