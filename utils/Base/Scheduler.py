import heapq
import os
import threading
import time
from datetime import datetime
from typing import Dict, TypeVar, Generic, List, Optional
from zoneinfo import ZoneInfo

from PySide6 import QtWidgets
from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition, Qt, QObject, Slot
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
        self.setFrameStyle(QFrame.Shape.Box)  # 明确设置边框样式
        self.setFixedHeight(50)
        self.setContentsMargins(0, 5, 0, 5)
        self.setStyleSheet(
            """
                QWidget {
                    border: 2px solid #888;
                    border-radius: 5px;
                    background-color: #f0f0f0;
                }
            """)

        # 创建水平布局并设置为居中对齐
        self.item_layout = QVBoxLayout(self)
        self.item_layout.setContentsMargins(5, 0, 5, 0)
        self.item_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # 任务名称标签（第一个标签）
        self.name_label = QLabel(task.task_name)
        self.name_label.setStyleSheet(
            """
                border: none;
                background-color: transparent;
                font-size: 13pt; 
                color: black;
            """)
        self.item_layout.addWidget(self.name_label, alignment=Qt.AlignmentFlag.AlignLeft)

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
        self.time_label = QLabel(f"下次执行 ：{date_str} {time_str}")
        self.time_label.setStyleSheet(
            """
                border: none;
                background-color: transparent;
                font-family: 'Microsoft YaHei'; 
                font-size: 10pt;  /* 小字体 */
                font-weight: bold; 
                color: #666666;   /* 灰色 */
            """)
        self.item_layout.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignLeft)
        self.setVisible(task.is_activated)

    def update_display(self, task: BaseTask):
        """更新显示内容"""
        self.name_label.setText(task.task_name)

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
        self.time_label.setText(f"下次执行 ：{date_str} {time_str}")
        self.setVisible(task.is_activated)


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

    def execute_at_once(self, task_name: str):
        """立刻运行任务"""
        if task_name not in self.task_dic:
            return False, None
        task = self.task_dic[task_name]
        # 更新任务属性
        flag, net = task.update_next_execute_time(2)
        if not flag:  # 新增：更新失败直接返回
            return False, net
        # 从堆中移除并重新插入
        try:
            self.heap.remove(task)
            heapq.heapify(self.heap)  # 重新堆化
            heapq.heappush(self.heap, task)  # 重新插入
            return True, net
        except ValueError:
            return False, None

    def get_tasks_by_status(self, status: int) -> List[B]:
        """获取指定状态的所有任务"""
        return [task for task in self.heap if task.current_status == status]

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


class TaskWidgetList(Generic[B, T]):
    def __init__(
        self,
        task_queue: PriorityQueue[B],
        running_layout: QBoxLayout,
        ready_layout: QBoxLayout,
        waiting_layout: QBoxLayout
    ):
        self.task_queue = task_queue

        # 初始化数据结构
        self.widgets: Dict[str, T] = {}  # 用字典存储控件，提高查找效率

        # 状态到布局的映射
        self.status_to_layout = {
            0: running_layout,
            1: ready_layout,
            2: waiting_layout
        }

    def add_widget(self, task: B) -> T:
        """添加控件并保持有序"""
        # 如果控件已存在则先移除
        if task.task_name in self.widgets:
            self.remove_widget(task.task_name)
        layout = self._get_layout_for_task(task)
        if not layout:
            raise ValueError(f"No layout found for task status: {task.current_status}")
        # 创建新控件
        widget = TaskWidget(task, parent=layout.parentWidget())
        # 设置控件属性以便后续查找
        widget.setProperty("task_name", task.task_name)
        # 计算插入位置
        insert_index = self._find_insert_index(layout, task)
        # 插入到布局
        layout.insertWidget(insert_index, widget)
        # 存储控件引用
        self.widgets[task.task_name] = widget

        return widget

    def remove_widget(self, task_name: str) -> bool:
        """移除指定任务的控件"""
        if task_name not in self.widgets:
            return False

        # 获取控件和对应的布局
        widget = self.widgets[task_name]
        task = self.task_queue.get_task(task_name)

        # 从布局中移除
        if task:
            layout = self._get_layout_for_task(task)
            if layout:
                index = self._find_widget_index(layout, widget)
                if index != -1:
                    layout.takeAt(index)

        # 清理
        widget.deleteLater()
        del self.widgets[task_name]
        return True

    def find_widget(self, task_name: str) -> Optional[T]:
        """查找指定任务的控件"""
        return self.widgets.get(task_name)

    def refresh_task_widget(self, task_name: str) -> bool:
        """刷新指定任务的UI显示（仅移动布局/更新显示，不删除控件）"""
        task = self.task_queue.get_task(task_name)
        if not task:
            return False  # 任务不存在，无需刷新

        widget = self.find_widget(task_name)
        if not widget:
            # 若控件不存在，可选择创建（也可返回False，根据业务决定）
            widget = self.add_widget(task)  # 复用add_widget的创建逻辑，避免重复代码
            if not widget:
                return False

        # 1. 统一更新显示（含可见性：update_display已绑定task.is_activated）
        widget.update_display(task)

        # 2. 状态变化时移动控件到正确布局（不删除，仅调整布局归属）
        target_layout = self._get_layout_for_task(task)  # 任务应在的目标布局
        current_layout = self._get_widget_layout(widget)  # 控件当前所在布局

        if target_layout != current_layout:
            # 从原布局移除（takeAt仅移除布局项，不删除控件实例）
            if current_layout:
                idx = self._find_widget_index(current_layout, widget)
                if idx != -1:
                    current_layout.takeAt(idx)  # 仅移除布局关联，控件实例保留

            # 插入目标布局的正确排序位置
            insert_idx = self._find_insert_index(target_layout, task)
            target_layout.insertWidget(insert_idx, widget)

        return True

    def refresh_all_task_widgets(self) -> None:
        """刷新所有任务UI（复用控件+仅调整布局+统一可见性，不主动删除控件）"""
        # 1. 先按任务状态分组（从优先级队列获取最新任务列表）
        tasks_by_status = {}
        for task in self.task_queue.heap:
            status = task.current_status
            if status not in tasks_by_status:
                tasks_by_status[status] = []
            tasks_by_status[status].append(task)

        # 2. 记录所有"仍在队列中的任务名"（用于后续清理无效控件）
        valid_task_names = set(task.task_name for task in self.task_queue.heap)

        # 3. 逐个处理每个布局（仅移动/更新控件，不删除）
        for status, target_layout in self.status_to_layout.items():
            # 3.1 取出当前布局的所有控件（暂存，后续按排序重新插入）
            current_widgets_in_layout = []
            while target_layout.count() > 0:
                item = target_layout.takeAt(0)  # 移除布局项，保留控件实例
                if item.widget():
                    current_widgets_in_layout.append(item.widget())

            # 3.2 获取当前状态下的所有任务（已按优先级排序）
            tasks_in_status = tasks_by_status.get(status, [])
            # 确保任务排序规则不变（与原逻辑一致）
            tasks_in_status.sort(key=lambda x: (x.next_execute_time, x.task_id, x.create_time))

            # 3.3 按排序后的任务，重新组织布局控件（复用现有控件）
            for task in tasks_in_status:
                task_name = task.task_name
                widget = self.find_widget(task_name)  # 从全局控件字典找已有控件

                if widget:
                    # 情况1：控件已存在——更新显示+加入目标布局
                    widget.update_display(task)
                    # 从"当前布局暂存列表"中移除（避免后续被误处理）
                    if widget in current_widgets_in_layout:
                        current_widgets_in_layout.remove(widget)
                else:
                    # 情况2：控件不存在——创建新控件（仅在首次出现时创建）
                    widget = TaskWidget(task)
                    widget.setProperty("task_name", task_name)
                    self.widgets[task_name] = widget  # 加入全局控件字典管理

                # 插入目标布局的正确位置（维持排序）
                insert_idx = self._find_insert_index(target_layout, task)
                target_layout.insertWidget(insert_idx, widget)

            # 3.4 处理当前布局中"不属于该状态"的控件（移到正确布局，不删除）
            for orphan_widget in current_widgets_in_layout:
                orphan_task_name = orphan_widget.property("task_name")
                if not orphan_task_name:
                    continue
                # 找到控件对应的任务，移动到正确布局
                orphan_task = self.task_queue.get_task(str(orphan_task_name))
                if orphan_task:
                    # 递归调用单任务刷新，自动处理布局移动
                    self.refresh_task_widget(str(orphan_task_name))

        # 4. 最后清理"任务已从队列移除，但控件仍存在"的无效控件（避免内存泄漏）
        # （这一步不是"主动删除有效控件"，而是清理无效控件，可选保留但建议加）
        invalid_widget_names = []
        for task_name, widget in self.widgets.items():
            if task_name not in valid_task_names:
                invalid_widget_names.append(task_name)
        for task_name in invalid_widget_names:
            widget = self.widgets.pop(task_name)
            # 从所有布局中移除（防止残留）
            for layout in self.status_to_layout.values():
                idx = self._find_widget_index(layout, widget)
                if idx != -1:
                    layout.takeAt(idx)
            widget.deleteLater()  # 仅清理无效控件

    def clear_all_widgets(self):
        """清除所有布局中的控件"""
        # 清除所有布局中的控件
        for layout in self.status_to_layout.values():
            while layout.count() > 0:
                item = layout.takeAt(0)
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

    def _get_layout_for_task(self, task: B) -> Optional[QBoxLayout]:
        """获取任务状态对应的布局"""
        return self.status_to_layout.get(task.current_status)

    def _get_widget_layout(self, widget: T) -> Optional[QBoxLayout]:
        """获取控件当前所在的布局"""
        for layout in self.status_to_layout.values():
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item.widget() == widget:
                    return layout
        return None

    @staticmethod
    def _find_widget_index(layout: QBoxLayout, widget: T) -> int:
        """查找控件在布局中的索引"""
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget() == widget:
                return i
        return -1

    @staticmethod
    def _compare_tasks(task1: B, task2: B) -> int:
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
        self.init_scroll_area_layouts()  # 初始化滚动区域布局
        self.task_queue = PriorityQueue[BaseTask]()
        self.task_widget_list = TaskWidgetList[BaseTask, TaskWidget](
            self.task_queue,
            self.running_layout,
            self.ready_layout,
            self.waiting_layout
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
            if not state:
                temp_task.stop()
            self.task_widget_list.refresh_task_widget(task_name)
            self.logger.info(f"任务 {task_name} {'已启用' if state else '已禁用'}")
        checkbox_widget.setEnabled(True)

    def task_next_execute_time_editfinished(self, task_name):
        """如果清空则立即执行任务"""
        lineedit_widget = self.task_common_control_ref_map[task_name]["LineEdit"]
        if lineedit_widget.text() != "":
            return

        if not self.running:
            return
        lineedit_widget.setEnabled(False)
        flag, net = self.task_queue.execute_at_once(task_name)
        self.task_widget_list.refresh_task_widget(task_name)
        lineedit_widget.setText(net.strftime("%Y-%m-%d %H:%M:%S"))
        lineedit_widget.setEnabled(True)
        if not flag:
            self.logger.error(f"任务 {task_name} 放入等待队列等待立即执行失败")
            return
        self.logger.info(f"任务 {task_name} 已放入等待队列等待立即执行")

    def activate_another_task_implement(self, task_name):
        """任务调用其他任务立刻执行"""
        if not self.running:
            return

        flag, net = self.task_queue.execute_at_once(task_name)
        self.task_widget_list.refresh_task_widget(task_name)
        if not flag:
            self.logger.error(f"任务 {task_name} 放入等待队列等待立即执行失败")
            return
        self.logger.info(f"任务 {task_name} 已放入等待队列等待立即执行")

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

    def _handle_screen_save(self, task_name):
        threading.Thread(target=self.save_screen, args=(task_name,)).start()

    def scan(self):
        """
        1.扫描等待队列中的任务，如果可以执行则放入就绪队列
        2.扫描就绪队列，如果执行队列为空且就绪队列不为空，则从就绪队列中取出优先级最高的Task交给Executor执行
        """
        # self.logger.debug("开始检查")
        start = time.perf_counter()
        if self.UI.bool_save_img.isChecked():
            self.screen_save_signal.emit("扫描")

        moved_tasks = []  # 记录从等待队列移动到就绪队列的任务

        # 扫描等待队列，检查任务是否可以执行
        waiting_tasks = self.task_queue.get_tasks_by_status(2)
        # self.logger.debug(len(waiting_tasks))
        for task in waiting_tasks:
            # self.logger.debug(f"检查{task}")
            if not task.is_activated:  # 不处理未启用的任务
                continue
            if task.current_status != 2:  # 只处理等待状态的任务
                continue

            if task.next_execute_time <= datetime.now(ZoneInfo("Asia/Shanghai")):
                self.task_queue.update_task_status(task.task_name, 1)  # 更新为就绪状态
                self.task_widget_list.refresh_task_widget(task.task_name)
                moved_tasks.append(task)
                self.logger.info(f"[{task.task_name}]-[{task.task_id}] 进入就绪队列")

        # 如果有任务被移动，重新触发扫描以检查就绪队列
        if moved_tasks:
            if self.running:
                self.logger.debug("有任务被移动，重新触发扫描以检查就绪队列")
                self.timer_thread.trigger(100)  # 立即触发下一次扫描
                return

        # 检查是否有运行中的任务
        running_tasks = self.task_queue.get_tasks_by_status(0)
        if not running_tasks:  # 没有运行中的任务
            # 获取就绪状态的任务
            ready_tasks = self.task_queue.get_tasks_by_status(1)
            if ready_tasks:  # 有就绪任务
                # 获取优先级最高的就绪任务
                next_task = min(ready_tasks)  # 使用堆的特性
                self.task_queue.update_task_status(next_task.task_name, 0)
                self.task_widget_list.refresh_task_widget(next_task.task_name)
                next_task.run()

        if self.running:
            # 继续下一次扫描
            wait_time = max(100, self.config.get_config("扫描间隔") - 1000 * (
                    time.perf_counter() - start))
            self.timer_thread.trigger(int(wait_time))  # 每秒扫描一次

    def _execute_done_callback(self, task: BaseTask):
        lineedit = self.task_common_control_ref_map[task.task_name]["LineEdit"]
        lineedit.setText(task.next_execute_time.strftime("%Y-%m-%d %H:%M:%S"))
        self.task_queue.update_task_status(task.task_name, 2)
        self.task_widget_list.refresh_task_widget(task.task_name)
        self.logger.info(f"[{task.task_name}]-[{task.task_id}] 移出执行队列，进入等待队列")
        if task.is_activated and self.running:
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
