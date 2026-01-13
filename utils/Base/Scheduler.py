import heapq
import logging
import os
import threading
import time
from datetime import datetime
from logging import Logger
from typing import Dict, TypeVar, Generic, List, Optional
from zoneinfo import ZoneInfo

from PySide6 import QtWidgets
from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition, Qt, QObject, Slot, QTimer
from PySide6.QtWidgets import QWidget, QLabel, QBoxLayout, QVBoxLayout, QFrame

from StaticFunctions import get_real_path, cv_save
from utils.Base.Config import Config
from utils.Base.Device import Device
from utils.Base.Operationer import Operationer
from utils.Base.Scene.SceneGraph import SceneGraph
from utils.Base.Scene.TransitionManager import TransitionManager
from utils.Base.Task import TASK_TYPE_MAP
from utils.Base.Task.BaseTask import BaseTask
from utils.ui.Service_ui import Ui_Service


class TaskWidget(QFrame):
    def __init__(self, task: BaseTask, parent=None):
        super().__init__(parent)
        self.task = task
        self.setFrameStyle(QFrame.Shape.Box)  # 明确边框样式（不影响自定义样式表）
        self.setFixedHeight(50)
        self.setContentsMargins(0, 5, 0, 5)

        # -------------------------- 1. 初始化控件（新增 objectName 用于样式选择）--------------------------
        # 创建垂直布局
        self.item_layout = QVBoxLayout(self)
        self.item_layout.setContentsMargins(5, 0, 5, 0)
        self.item_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # 任务名称标签（设置 objectName，方便样式表定位）
        self.name_label = QLabel(task.task_name)
        self.name_label.setObjectName("name_label")  # 关键：给标签命名，用于样式选择
        self.item_layout.addWidget(self.name_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # 时间标签（同样设置 objectName）
        self.time_label = QLabel()
        self.time_label.setObjectName("time_label")  # 关键：给标签命名
        self.item_layout.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # 初始化时直接调用 update_display（包含样式设置）
        self.update_display()

    def update_display(self):
        """更新显示内容 + 动态修改边框颜色"""
        # -------------------------- 2. 核心：根据任务状态确定边框颜色 --------------------------
        # 优先级规则：temp_priority=True（临时提权）> current_status（普通状态）
        if self.task.temp_priority:
            border_color = "#FF0000"  # 临时提权：红色边框
        else:
            # 普通状态：按 current_status 映射颜色（0=原有色，1=黄色，2=灰色）
            status_color_map = {
                0: "#779977",  # 状态0：原有默认色（深绿灰）
                1: "#FFFF00",  # 状态1：黄色
                2: "#999999"  # 状态2：灰色
            }
            # 若 current_status 不在 0/1/2 范围内，默认用原有色
            border_color = status_color_map.get(self.task.current_status, "#779977")

        # -------------------------- 3. 构建完整样式表（包含所有控件样式） --------------------------
        # 注意：样式表需覆盖所有需要的样式（边框、背景、标签字体等），避免原有样式丢失
        self.setStyleSheet(f"""
            /* 自身（QFrame）的样式：动态边框色 + 原有基础样式 */
            TaskWidget {{
                border: 3px solid {border_color};  /* 动态边框色 */
                border-radius: 5px;               /* 保留原有圆角 */
                background-color: #f0f0f0;        /* 保留原有背景色 */
            }}

            /* 任务名称标签样式（与原逻辑一致） */
            #name_label {{
                border: none;
                background-color: transparent;
                font-size: 13pt; 
                color: black;
            }}

            /* 时间标签样式（与原逻辑一致） */
            #time_label {{
                border: none;
                background-color: transparent;
                font-family: 'Microsoft YaHei'; 
                font-size: 10pt;
                font-weight: bold; 
                color: #666666;
            }}
        """)

        # -------------------------- 4. 保留原有显示逻辑 --------------------------
        # 更新任务名称
        priority_str = f"[{self.task.base_priority}]"
        self.name_label.setText(f"{priority_str.ljust(5)}{self.task.task_name}")

        # 更新下次执行时间（原有逻辑不变）
        current_date = datetime.now(ZoneInfo("Asia/Shanghai")).date()
        task_date = self.task.next_execute_time.date()
        delta = (task_date - current_date).days

        if delta == 0:
            date_str = "今天"
        elif delta == 1:
            date_str = "明天"
        else:
            date_str = self.task.next_execute_time.strftime("%Y-%m-%d")

        time_str = self.task.next_execute_time.strftime("%H:%M:%S")
        self.time_label.setText(f"下次执行 ：{date_str} {time_str}")

        # 控制控件可见性（原有逻辑不变）
        self.setVisible(self.task.is_activated)


B = TypeVar('B', bound=BaseTask)
T = TypeVar('T', bound=TaskWidget)


class PriorityQueue(Generic[B]):
    def __init__(self):
        self.heap: List[B] = []  # 存储 Task 的列表
        self.task_dic: Dict[str:B] = {}

    def enqueue(self, item: B):
        heapq.heappush(self.heap, item)  # 插入元素，自动维护堆序
        self.task_dic[item.task_name] = item

    def dequeue(self):
        if not self.is_empty():
            item = heapq.heappop(self.heap)
            del self.task_dic[item.task_name]
            return item  # 返回优先级最小的元素
        return None

    def is_empty(self):
        return len(self.heap) == 0

    def peek(self):
        return self.heap.copy()

    def get_task(self, task_name: str) -> Optional[B]:
        """获取任务而不删除它"""
        return self.task_dic.get(task_name)

    def reheapify(self):
        """重新构建整个堆"""
        tasks = self.heap.copy()
        self.heap = []
        for task in tasks:
            heapq.heappush(self.heap, task)

    def refresh_task(self, task_name: str) -> bool:
        """刷新指定任务的位置"""
        if task_name not in self.task_dic:
            return False
        task = self.task_dic[task_name]
        self.heap.remove(task)
        heapq.heapify(self.heap)
        heapq.heappush(self.heap, task)
        return True

    def update_task_status(self, task_name: str, new_status: int) -> bool:
        """更新任务状态"""
        if task_name not in self.task_dic:
            return False
        task = self.task_dic[task_name]
        task.current_status = new_status
        # 更新堆结构
        self.heap.remove(task)
        heapq.heapify(self.heap)
        heapq.heappush(self.heap, task)
        return True

    def get_tasks_by_status(self, status: int) -> List[B]:
        """获取指定状态的所有任务"""
        return [task for task in self.heap if task.current_status == status]


class TaskWidgetList(Generic[B, T]):
    def __init__(
        self,
        task_queue: PriorityQueue[B],
        tasks_layout: QBoxLayout,
        parent_logger: Logger = ""
    ):
        if isinstance(parent_logger, str):
            self.logger = logging.getLogger("任务控件列表")
        else:
            self.logger = parent_logger.getChild("任务控件列表")
        self.task_queue = task_queue

        # 初始化数据结构
        self.widgets: Dict[str, T] = {}  # 用字典存储控件，提高查找效率
        self.tasks_layout = tasks_layout

    def add_widget(self, task: B) -> T:
        """添加控件并保持有序"""
        # 如果控件已存在则先移除
        if task.task_name in self.widgets:
            self.remove_widget(task.task_name)
        # 创建新控件
        widget = TaskWidget(task, parent=self.tasks_layout.parentWidget())
        # 设置控件属性以便后续查找
        widget.setProperty("task_name", task.task_name)
        # 计算插入位置
        insert_index = self._find_insert_index(self.tasks_layout, task)
        # 插入到布局
        self.tasks_layout.insertWidget(insert_index, widget)
        # 存储控件引用
        self.widgets[task.task_name] = widget

        return widget

    def remove_widget(self, task_name: str) -> bool:
        """移除指定任务的控件"""
        if task_name not in self.widgets:
            return False

        # 获取控件和对应的布局
        widget = self.widgets[task_name]
        index = self._find_widget_index(widget)
        if index != -1:
            self.tasks_layout.takeAt(index)

        # 清理
        widget.deleteLater()
        del self.widgets[task_name]
        return True

    def find_widget(self, task_name: str) -> Optional[T]:
        """查找指定任务的控件"""
        return self.widgets.get(task_name)

    def refresh_task_widget(self, task_name: str) -> bool:
        """刷新单个任务控件"""
        try:
            self.task_queue.refresh_task(task_name)
            task = self.task_queue.get_task(task_name)
            if not task:
                self.logger.debug(f"任务 {task_name} 不在队列中")
                return False

            widget = self.find_widget(task_name)
            if not widget:
                widget = self.add_widget(task)
                if not widget:
                    return False

            # 更新显示
            widget.update_display()

            # 重新调整位置（状态可能已变更）
            current_index = self._find_widget_index(widget)
            if current_index != -1:
                self.tasks_layout.takeAt(current_index)

            new_index = self._find_insert_index(self.tasks_layout, task)
            self.tasks_layout.insertWidget(new_index, widget)
            return True

        except Exception as e:
            self.logger.error(f"刷新 {task_name} 控件失败: {e}", exc_info=True)
            return False

    def refresh_all_task_widgets(self) -> None:
        """刷新所有任务UI（在单一布局中按状态和优先级排序）"""
        # 1. 获取所有任务并按规则排序
        all_tasks = list(self.task_queue.heap)  # 假设heap包含所有任务
        # 按状态和优先级排序（复用_compare_tasks逻辑）
        all_tasks.sort(key=lambda x: (x.current_status, x))

        # 2. 记录所有有效任务名
        valid_task_names = set(task.task_name for task in all_tasks)

        # 3. 暂存当前布局中的所有控件
        current_widgets = []
        while self.tasks_layout.count() > 0:
            item = self.tasks_layout.takeAt(0)
            if item.widget():
                current_widgets.append(item.widget())

        # 4. 按排序后的任务重新组织布局
        for task in all_tasks:
            task_name = task.task_name
            widget = self.find_widget(task_name)

            if widget:
                # 复用现有控件并更新
                widget.update_display()
                # 从暂存列表中移除（避免后续被误处理）
                if widget in current_widgets:
                    current_widgets.remove(widget)
            else:
                # 创建新控件
                widget = TaskWidget(task, parent=self.tasks_layout.parentWidget())
                widget.setProperty("task_name", task_name)
                self.widgets[task_name] = widget

            # 插入到正确位置
            insert_idx = self._find_insert_index(self.tasks_layout, task)
            self.tasks_layout.insertWidget(insert_idx, widget)

        # 5. 处理暂存列表中剩余的无效控件（不在有效任务列表中）
        for widget in current_widgets:
            task_name = widget.property("task_name")
            if task_name and str(task_name) not in valid_task_names:
                # 清理已移除任务的控件
                if str(task_name) in self.widgets:
                    del self.widgets[str(task_name)]
                widget.deleteLater()
            else:
                # 对于仍有效的控件，重新插入到正确位置
                if task_name:
                    task = self.task_queue.get_task(str(task_name))
                    if task:
                        insert_idx = self._find_insert_index(self.tasks_layout, task)
                        self.tasks_layout.insertWidget(insert_idx, widget)

    def clear_all_widgets(self):
        """清除所有布局中的控件"""
        while self.tasks_layout.count() > 0:
            item = self.tasks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 清空控件字典
        for widget in self.widgets.values():
            widget.deleteLater()
        self.widgets.clear()

    def _find_insert_index(self, layout: QBoxLayout, task: B) -> int:
        """使用二分查找确定插入位置"""
        # 从布局中获取所有任务并提取排序键
        tasks = []
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget():
                task_name = item.widget().property("task_name")
                if task_name:
                    t = self.task_queue.get_task(str(task_name))
                    if t:
                        tasks.append(t)

        # 二分查找
        lo, hi = 0, len(tasks)
        while lo < hi:
            mid = (lo + hi) // 2
            mid_task = tasks[mid]

            # 比较任务
            if self._compare_tasks(task, mid_task) < 0:
                hi = mid
            else:
                lo = mid + 1
        return lo

    def _find_widget_index(self, widget: T) -> int:
        """查找控件在布局中的索引"""
        for i in range(self.tasks_layout.count()):
            item = self.tasks_layout.itemAt(i)
            if item.widget() == widget:
                return i
        return -1

    @staticmethod
    def _compare_tasks(task1: B, task2: B) -> int:
        """比较两个任务的优先级（先按状态，再按任务本身规则）"""
        if task1.current_status != task2.current_status:
            # 状态值越小优先级越高（根据实际业务调整）
            return -1 if task1.current_status < task2.current_status else 1
        # 先比较有无临时提权
        if task1.temp_priority != task2.temp_priority:
            return -1 if task1.temp_priority > task2.temp_priority else 1

        # 比较执行时间
        if task1.next_execute_time != task2.next_execute_time:
            return -1 if task1.next_execute_time < task2.next_execute_time else 1

        # 比较任务ID
        if task1.base_priority != task2.base_priority:
            return -1 if task1.base_priority < task2.base_priority else 1
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
    activate_another_task_signal = Signal(str)
    screen_save_signal = Signal(str)

    def __init__(self,
                 ui: Ui_Service,
                 config: Config,
                 scene_graph: SceneGraph,
                 ref_map: Dict,
                 parent_logger
                 ):
        super().__init__()
        self.logger = parent_logger.getChild(self.__class__.__name__)
        self.running = False
        self.UI = ui
        self.config = config
        self.task_common_control_ref_map = ref_map
        self.scene_graph = scene_graph
        self.transition_manager = TransitionManager(self.config, self.logger)

        # 初始化UI相关属性
        self.tasks_layout = None
        self.init_scroll_area_layouts()  # 初始化滚动区域布局
        self.task_queue = PriorityQueue[BaseTask]()
        self.task_widget_list = TaskWidgetList[BaseTask, TaskWidget](
            self.task_queue,
            self.tasks_layout,
            self.logger
        )
        self.activate_another_task_signal.connect(self.activate_another_task_implement)
        self.screen_save_signal.connect(self._handle_screen_save)

        self.device: Device | None = None

        self.timer_thread = TimerThread()
        self.timer_thread.timeout.connect(self.scan)
        # 启动调度器开始扫描
        self.timer_thread.start()  # 启动线程，线程会进入等待状态
        self.logger.info("初始化完成...")

    def start(self):
        self.logger.info("正在启动调度器...")
        self.UI.start_schedule_button.setEnabled(False)
        self.running = True
        self.device = Device(self.config, parent_logger=self.logger)
        if not self.device.device_ready:
            self.logger.warning("调度器初始化Device出错，请检查[助手设置]中串口和截图模式")
            self.UI.start_schedule_button.setEnabled(True)
            self.UI.start_schedule_button.setText("启动")
            return
        for task_name, task_info in self.config.tasks.items():
            self.logger.debug(f"[{task_name}]任务准备进入调度器")
            task_class = TASK_TYPE_MAP.get(task_name, None)
            if not task_class:
                self.logger.warning(f"[{task_name}] 任务创建出错")
                continue
            operationer_instance = Operationer(
                task_name,
                self.config,
                self.device,
                self.scene_graph,
                self.screen_save_signal,
                parent_logger=self.logger
            )
            task_instance = task_class(
                task_name,
                self.config,
                self.transition_manager,
                operationer_instance,
                self.activate_another_task_signal,
                self._execute_done_callback,
                parent_logger=self.logger
            )
            self.task_queue.enqueue(task_instance)
            self.task_widget_list.add_widget(task_instance)
        self.task_widget_list.refresh_all_task_widgets()
        self.timer_thread.trigger(self.config.get_config("扫描间隔"), 1000)
        self.UI.start_schedule_button.setEnabled(True)
        self.UI.start_schedule_button.setText("暂停")
        self.logger.info("调度器已完成启动")

    def stop(self):
        """停止调度器及其所有任务"""
        self.logger.info("正在停止调度器...")
        self.UI.start_schedule_button.setEnabled(False)
        self.running = False

        # 停止所有正在运行的任务
        for task in self.task_queue.get_tasks_by_status(0):
            task.stop()

        # 清空所有队列
        self.task_queue = PriorityQueue[BaseTask]()
        # 清除所有任务控件
        self.task_widget_list.clear_all_widgets()
        if self.device:
            # 释放设备资源
            if self.device.controller:
                self.device.controller.release()
                self.device.controller = None
            if self.device.screener:
                self.device.screener.release()
                self.device.screener = None
                self.device = None

        self.UI.start_schedule_button.setEnabled(True)
        self.UI.start_schedule_button.setText("启动")
        self.logger.info("调度器已完全停止")

    def toggle_task_activation(self, state, task_name: str):
        """切换任务的启用/禁用状态"""
        checkbox_widget = self.task_common_control_ref_map[task_name]["CheckBox"]
        checkbox_widget.setEnabled(False)
        self.config.set_task_base_config(task_name, "是否启用", state)
        temp_task = self.task_queue.get_task(task_name)
        if temp_task:
            if not state and temp_task.current_status == 0:
                temp_task.stop()
            self.task_widget_list.refresh_task_widget(task_name)
            self.logger.info(f"任务 {task_name} {'已启用' if state else '已禁用'}")
        checkbox_widget.setEnabled(True)

    def task_next_execute_time_editfinished(self, task_name):
        """如果清空则立即执行任务"""
        lineedit_widget = self.task_common_control_ref_map[task_name]["LineEdit"]
        if lineedit_widget.text() != "":
            return
        task = self.task_queue.get_task(task_name)
        if not task:
            self.logger.error(f"任务 {task_name} 不在队列中")
            return
        lineedit_widget.setEnabled(False)
        task.update_next_execute_time(2)
        self.task_widget_list.refresh_task_widget(task_name)
        lineedit_widget.setText(task.next_execute_time.strftime("%Y-%m-%d %H:%M:%S"))
        lineedit_widget.setEnabled(True)
        self.logger.info(f"任务 {task_name} 等待立即执行")

    def activate_another_task_implement(self, task_name):
        """任务调用其他任务立刻执行"""
        lineedit_widget = self.task_common_control_ref_map[task_name]["LineEdit"]
        lineedit_widget.setEnabled(False)
        self.config.set_task_base_config(task_name, "临时提权", True)
        task = self.task_queue.get_task(task_name)
        if not task:
            self.logger.error(f"任务 {task_name} 不在队列中")
            return
        lineedit_widget.setEnabled(False)
        task.update_next_execute_time(2)
        self.task_widget_list.refresh_task_widget(task_name)
        lineedit_widget.setText(task.next_execute_time.strftime("%Y-%m-%d %H:%M:%S"))
        lineedit_widget.setEnabled(True)
        self.logger.info(f"任务 {task_name} 等待立即执行")

    def init_scroll_area_layouts(self):
        """初始化任务滚动区域的布局"""
        self.tasks_layout = QtWidgets.QVBoxLayout(self.UI.scroll_tasks_area_content)
        self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tasks_layout.setSpacing(5)

    def _handle_screen_save(self, task_name):
        if self.UI.bool_save_img.isChecked():
            threading.Thread(target=self.save_screen, args=(task_name,)).start()

    def scan(self):
        """改进的扫描方法，避免快速重入"""
        if not self.running:
            return

        # 添加扫描锁防止重入
        if hasattr(self, '_scanning') and self._scanning:
            return

        self._scanning = True
        try:
            start = time.perf_counter()
            self.screen_save_signal.emit("扫描")

            moved_tasks = []

            # 扫描等待队列
            waiting_tasks = self.task_queue.get_tasks_by_status(2)
            for task in waiting_tasks:
                if not task.is_activated or task.current_status != 2:
                    continue

                if task.next_execute_time <= datetime.now(ZoneInfo("Asia/Shanghai")):
                    success = self.task_queue.update_task_status(task.task_name, 1)
                    if success:
                        self.task_widget_list.refresh_task_widget(task.task_name)
                        moved_tasks.append(task)
                        self.logger.info(f"[{task.task_name}]-[{task.base_priority}] 进入就绪队列")
            if moved_tasks:
                if self.running:
                    self.timer_thread.trigger(500)
            ready_tasks = self.task_queue.get_tasks_by_status(1)
            if ready_tasks:
                next_task = min(ready_tasks)
                # 检查运行队列
                running_tasks = self.task_queue.get_tasks_by_status(0)
                if not running_tasks:
                    success = self.task_queue.update_task_status(next_task.task_name, 0)
                    if success:
                        self.task_widget_list.refresh_task_widget(next_task.task_name)
                        next_task.run()
                else:
                    running_task = running_tasks[0]
                    if running_task > next_task:
                        # 说明执行中任务的优先级低于就绪任务，先提权，再停止正在执行的任务，再触发一次扫描，这样就能把提权后的任务放在执行队列了
                        self.config.set_task_base_config(next_task.task_name, "临时提权", True)
                        running_task.stop()

            if self.running:
                wait_time = max(100, self.config.get_config("扫描间隔") - 1000 * (
                        time.perf_counter() - start))
                self.timer_thread.trigger(int(wait_time))

        finally:
            self._scanning = False

    def _execute_done_callback(self, task: BaseTask):
        lineedit = self.task_common_control_ref_map[task.task_name]["LineEdit"]
        lineedit.setText(task.next_execute_time.strftime("%Y-%m-%d %H:%M:%S"))
        self.task_queue.update_task_status(task.task_name, 2)
        if task.temp_priority:
            self.config.set_task_base_config(task.task_name, "临时提权", False)
        task.temp_dead_line = None
        self.task_widget_list.refresh_task_widget(task.task_name)
        self.logger.info(f"[{task.task_name}]-[{task.base_priority}] 移出执行队列，进入等待队列")
        task.create_time = datetime.now(ZoneInfo("Asia/Shanghai"))

    def save_screen(self, name):
        """保存截图到文件"""
        try:
            if self.device is None:
                self.logger.warning("设备未初始化，无法截图")
                return
            screen = self.device.screen_cap()
            if screen is None or screen.size == 0:
                self.logger.warning("图像数据为空，无法保存")
                return

            image_dir = get_real_path("image")
            os.makedirs(image_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')
            save_dir = os.path.join(image_dir, name)
            save_path = os.path.join(image_dir, name, f"{timestamp}.png")
            if not os.path.exists(save_dir):
                os.makedirs(save_dir, exist_ok=True)
            cv_save(save_path, screen)
            self.logger.info("截图保存到%s", save_path)

        except Exception as e:
            self.logger.error(f"保存图像时发生错误: {e}")
