import json
import logging
import math
from typing import Any, Dict, List, Set

from PySide6.QtCore import Qt, QPointF, Signal, QObject, QLineF
from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QPainterPath, QAction, QFont
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsPathItem, QMenu, \
    QGraphicsTextItem, QDialog, \
    QVBoxLayout, QListWidget, QLabel, QDialogButtonBox, QGraphicsRectItem, QApplication

from StaticFunctions import get_real_path, setup_logging


class TaskNodeSignals(QObject):
    """信号容器类，用于处理非QObject派生类中的信号"""
    double_clicked = Signal(str)  # 节点双击信号
    clicked = Signal(str)  # 节点单击信号
    request_priority_change = Signal(str, int)  # 请求修改优先级信号（任务ID, 新优先级）


class TaskNode(QGraphicsRectItem):
    """自定义任务节点类，矩形节点"""

    def __init__(self, parent_tasks, task_id, pos=None, parent=None):
        # 先创建文本项以计算所需大小
        self.parent_tasks = parent_tasks
        self.text = QGraphicsTextItem(task_id)
        self.text.setDefaultTextColor(Qt.GlobalColor.white)
        font = QFont()
        font.setFamily('SimHei')
        font.setPointSize(70)
        font.setWeight(QFont.Weight.Medium)
        self.text.setFont(font)

        # 获取文本边界矩形
        text_rect = self.text.boundingRect()

        # 添加内边距（左右各10像素，上下各5像素）
        padding = QPointF(10, 3)
        width = text_rect.width() + padding.x()
        height = text_rect.height() + padding.y()

        # 创建矩形节点（基于文本大小）
        super().__init__(0, 0, width, height, parent)
        self.task_id = task_id
        self.is_highlighted = False  # 高亮状态
        self.normal_color = QColor(70, 130, 180)  # 正常颜色
        self.highlight_color = QColor(57, 197, 187)  # 高亮颜色（金色）

        # 创建信号容器对象
        self.signals = TaskNodeSignals()

        # 设置矩形样式
        self.setBrush(QBrush(self.normal_color))
        self.setPen(QPen(Qt.GlobalColor.black, 0))
        self.setZValue(1)

        # 允许节点被选择和移动
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)

        # 将文本添加到节点并居中
        self.text.setParentItem(self)
        text_x = (width - text_rect.width()) / 2
        text_y = (height - text_rect.height()) / 2
        self.text.setPos(text_x, text_y)

        # 禁用文本换行
        self.text.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.text.setTextWidth(-1)  # 禁用自动换行

        # 存储连接的边
        self.edges = []

        # 设置位置
        if pos:
            self.setPos(pos)
        else:
            # 设置节点中心位置
            self.setPos(-width / 2, -height / 2)

    def set_highlight(self, highlighted):
        """设置高亮状态"""
        self.is_highlighted = highlighted
        if highlighted:
            self.setBrush(QBrush(self.highlight_color))
        else:
            self.setBrush(QBrush(self.normal_color))
        self.update()

    def add_edge(self, edge):
        """添加连接的边"""
        if edge not in self.edges:
            self.edges.append(edge)

    def remove_edge(self, edge):
        """移除连接的边"""
        if edge in self.edges:
            self.edges.remove(edge)

    def mousePressEvent(self, event):
        """处理单击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.signals.clicked.emit(self.task_id)  # 通过信号容器发射单击信号
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """处理双击事件"""
        self.signals.double_clicked.emit(self.task_id)  # 通过信号容器发射信号
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        """处理右键菜单事件"""
        menu = QMenu()

        # 显示当前优先级（禁用状态，仅用于显示）
        current_priority = self.parent_tasks[self.task_id]["优先级"]
        current_priority_action = QAction(f"当前优先级: {current_priority}", menu)
        current_priority_action.setEnabled(False)
        menu.addAction(current_priority_action)

        # 添加分隔线
        menu.addSeparator()

        # 添加"复制任务名称"菜单项
        copy_action = QAction("复制任务名称", menu)
        copy_action.triggered.connect(lambda: QApplication.clipboard().setText(self.task_id))
        menu.addAction(copy_action)

        # 添加分隔线
        menu.addSeparator()

        # 计算最大优先级
        max_priority = max(task["优先级"] for task_id, task in self.parent_tasks.items()
                               if task_id != "开始")  # 排除虚拟根节点

        # 添加"修改优先级"子菜单
        priority_menu = menu.addMenu("修改优先级")
        for priority in range(-10, max_priority + 4):  # 范围从-10到最大优先级+3
            action = QAction(f"优先级 {priority}", priority_menu)
            action.triggered.connect(
                lambda checked, p=priority: self.signals.request_priority_change.emit(self.task_id, p)
            )
            priority_menu.addAction(action)

        menu.exec(event.screenPos())

    def itemChange(self, change, value):
        """当节点位置改变时，更新所有连接的边"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.edges:
                edge.update_position()
        return super().itemChange(change, value)


class TaskEdge(QGraphicsPathItem):
    """自定义任务边类，连接两个节点"""

    def __init__(self, source_node, target_node, parent=None):
        super().__init__(parent)
        self.source_node = source_node
        self.target_node = target_node

        # 颜色定义
        self.normal_color = QColor(105, 105, 105)  # 正常颜色-灰色
        self.warning_color = QColor(255, 140, 0)  # 警告颜色-橙色
        self.error_color = QColor(220, 20, 60)  # 错误颜色-红色

        self.setPen(QPen(self.normal_color, 10))

        # 添加边到节点的连接列表
        source_node.add_edge(self)
        target_node.add_edge(self)
        self.setZValue(0)

        # 初始更新位置
        self.update_position()

    def update_position(self):
        """更新边的位置（当节点移动时调用）"""

        def calculate_diag(rect, angle_rad):
            # 将角度归一化到[0, π)范围内
            angle_rad = angle_rad % math.pi
            # 处理接近水平的角度 (0° 或 180°)
            if angle_rad <= math.pi / 12 or angle_rad >= math.pi * 11 / 12:
                return rect.width() / 2

            # 处理接近垂直的角度 (90°)
            if math.pi / 2 - math.pi / 12 <= angle_rad <= math.pi / 2 + math.pi / 12:
                return rect.height() / 2
            # 计算矩形宽高比角度
            rect_angle = math.atan(rect.height() / rect.width())

            if angle_rad > math.pi / 2:
                angle_rad = math.pi - angle_rad

            if angle_rad <= rect_angle:
                return rect.width() / (2 * math.cos(angle_rad))
            else:
                return rect.height() / (2 * math.sin(angle_rad))

        path = QPainterPath()

        # 1. 计算源节点和目标节点的中心点
        source_center = self.source_node.rect().center() + self.source_node.pos()
        target_center = self.target_node.rect().center() + self.target_node.pos()

        # 创建QLineF对象（从源节点中心指向目标节点中心）
        line = QLineF(source_center, target_center)
        # 计算直线的角度（注意：Qt的角度是顺时针的，0度指向东）
        angle_deg = line.angle()

        # 转换为弧度并调整为数学坐标系（逆时针，0度指向东）
        angle_rad = math.radians(angle_deg)

        # 2. 计算节点对角线长度的一半（作为箭头偏移量）
        source_rect = self.source_node.rect()
        source_diag = calculate_diag(source_rect, angle_rad)

        target_rect = self.target_node.rect()
        target_diag = calculate_diag(target_rect, angle_rad)

        # 获取长度
        length = line.length()
        if length == 0:
            return

        # 3. 计算起点和终点（考虑节点对角线长度）
        # 起点：源节点中心向目标节点方向移动对角线一半的距离
        offset = 0.03
        start_point = line.pointAt(source_diag / length + offset)

        # 终点：目标节点中心向源节点方向移动对角线一半的距离
        end_point = line.pointAt(1 - target_diag / length - offset)

        # 绘制主连接线
        path.moveTo(start_point)
        path.lineTo(end_point)

        # 创建箭头 - 使用正确的角度计算
        arrow_size = 50

        # 4. 在终点处绘制箭头
        # 箭头位置：终点位置
        arrow_base = end_point

        # 计算箭头分支点
        arrow_p1 = arrow_base + QPointF(
            math.cos(angle_rad - math.pi + math.pi / 8) * arrow_size,
            -math.sin(angle_rad - math.pi + math.pi / 8) * arrow_size
        )
        arrow_p2 = arrow_base + QPointF(
            math.cos(angle_rad - math.pi - math.pi / 8) * arrow_size,
            -math.sin(angle_rad - math.pi - math.pi / 8) * arrow_size
        )

        # 绘制箭头
        path.moveTo(arrow_base)
        path.lineTo(arrow_p1)
        path.moveTo(arrow_base)
        path.lineTo(arrow_p2)

        self.setPath(path)


class TaskGraphView(QGraphicsView):
    """任务图可视化视图（增强版）"""

    # 定义信号
    node_double_clicked = Signal(str)  # 节点双击信号
    node_clicked = Signal(str)  # 节点单击信号
    connect_requested = Signal(str)  # 连接请求信号（源节点ID）
    disconnect_requested = Signal(str, str)  # 断开连接请求信号（源节点ID, 目标节点ID）
    # 新增优先级修改信号
    priority_change_requested = Signal(str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger("任务可视化视图")
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.tasks: Dict[
        str:Any] = json.load(open(get_real_path("src/TaskConfig.json"), 'r', encoding='utf-8'))
        self.nodes = {}  # 任务ID到节点对象的映射
        self.edges = {}  # (源ID, 目标ID)到边对象的映射
        self.highlighted_node = None  # 当前高亮的节点

        # 存储任务树结构
        self.task_tree = {}  # 任务ID到子任务ID列表的映射
        self.parent_map = {}  # 任务ID到父任务ID的映射

        # 设置视图属性
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setInteractive(True)

        # 修改信号连接
        self.node_clicked.connect(self.handle_node_clicked)
        self.node_double_clicked.connect(self.handle_node_double_clicked)
        self.priority_change_requested.connect(self.handle_priority_change)

        self.init()

    def init(self):
        """初始化任务树和视图"""
        self.clear()
        self.highlighted_node = None

        # 添加虚拟根节点到任务配置
        virtual_root_id = "开始"
        self.tasks[virtual_root_id] = {
            "优先级": -10,
            "临时提权": False,
            "描述": "虚拟根节点"
        }

        # 构建任务树
        self.build_task_tree()

        # 创建所有节点
        # 先创建虚拟根节点
        virtual_root = self.add_node(virtual_root_id)
        virtual_root.setBrush(QBrush(QColor(50, 50, 50)))  # 深灰色
        virtual_root.text.setDefaultTextColor(Qt.GlobalColor.white)

        # 创建其他节点
        for task_id in self.tasks:
            if task_id != virtual_root_id:
                self.add_node(task_id)

        # 创建所有边（基于任务树）
        for parent_id, children in self.task_tree.items():
            for child_id in children:
                self.add_edge(parent_id, child_id)

        # 初始化后自动布局
        self.auto_layout()

    def build_task_tree(self):
        """根据优先级构建任务树"""
        # 按优先级分组
        priority_groups = {}
        for task_id, task in self.tasks.items():
            priority = task["优先级"]
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(task_id)

        # 按优先级排序
        sorted_priorities = sorted(priority_groups.keys())

        # 初始化任务树和父映射
        self.task_tree = {task_id: [] for task_id in self.tasks}
        self.parent_map = {task_id: None for task_id in self.tasks}

        # 虚拟根节点的优先级是最低的
        virtual_root_id = "开始"

        # 找到第二低的优先级（除了虚拟根节点）
        min_priority = float('inf')
        for task_id, task in self.tasks.items():
            if task_id != virtual_root_id:
                min_priority = min(min_priority, task["优先级"])

        # 将最低优先级的任务作为虚拟根节点的子节点
        for task_id, task in self.tasks.items():
            if task_id != virtual_root_id and task["优先级"] == min_priority:
                self.task_tree[virtual_root_id].append(task_id)
                self.parent_map[task_id] = virtual_root_id

        # 构建其余树结构
        for i in range(1, len(sorted_priorities)):
            current_priority = sorted_priorities[i]
            prev_priority = sorted_priorities[i - 1]

            # 跳过虚拟根节点的优先级
            if current_priority == -10:
                continue

            # 当前优先级的所有任务都是前一个优先级所有任务的子节点
            for parent_id in priority_groups[prev_priority]:
                if parent_id != virtual_root_id:  # 跳过虚拟根节点
                    for child_id in priority_groups[current_priority]:
                        if child_id != virtual_root_id:  # 跳过虚拟根节点
                            self.task_tree[parent_id].append(child_id)
                            self.parent_map[child_id] = parent_id

    def add_node(self, task_id, pos=None):
        """添加任务节点"""
        if task_id in self.nodes:
            return self.nodes[task_id]

        node = TaskNode(self.tasks, task_id, pos)
        self.scene.addItem(node)
        self.nodes[task_id] = node

        # 连接节点的信号
        node.signals.double_clicked.connect(self.node_double_clicked)
        node.signals.clicked.connect(self.node_clicked)
        node.signals.request_priority_change.connect(self.priority_change_requested)

        # 如果未指定位置，使用改进的自动布局算法避免重叠
        if pos is None:
            count = len(self.nodes)
            min_distance = 150  # 节点间最小距离

            # 计算初始位置（环形布局）
            angle = (count * 360 / max(1, len(self.nodes))) % 360
            radius = max(200, min(800, count * 80))  # 动态调整半径

            # 计算初始位置
            x = radius * math.cos(math.radians(angle))
            y = radius * math.sin(math.radians(angle))
            pos = QPointF(x, y)

            # 检查是否与现有节点重叠
            for other_id, other_node in self.nodes.items():
                if other_id == task_id:
                    continue

                other_pos = other_node.pos()
                distance = math.sqrt((pos.x() - other_pos.x()) ** 2 + (pos.y() - other_pos.y()) ** 2)

                # 如果距离太近，调整位置
                if distance < min_distance:
                    # 计算移动方向
                    dx = pos.x() - other_pos.x()
                    dy = pos.y() - other_pos.y()

                    if dx == 0 and dy == 0:
                        dx = 1  # 避免除以零

                    # 计算方向向量并归一化
                    length = math.sqrt(dx ** 2 + dy ** 2)
                    dx /= length
                    dy /= length

                    # 移动到最小距离处
                    move_distance = min_distance - distance + 10
                    pos.setX(other_pos.x() + (dx * (distance + move_distance)))
                    pos.setY(other_pos.y() + (dy * (distance + move_distance)))

            # 设置最终位置
            node.setPos(pos)

        return node

    def handle_priority_change(self, task_id, new_priority):
        """处理优先级修改请求"""
        if task_id in self.tasks:
            self.tasks[task_id]["优先级"] = new_priority
            self.save_config()
            # 重新初始化视图以更新布局
            self.init()


    def add_edge(self, source_id, target_id):
        """添加任务跳转关系"""
        if source_id not in self.nodes or target_id not in self.nodes:
            return None

        key = (source_id, target_id)
        if key in self.edges:
            return self.edges[key]

        source_node = self.nodes[source_id]
        target_node = self.nodes[target_id]

        # 创建自定义边
        edge = TaskEdge(source_node, target_node)
        self.scene.addItem(edge)
        self.edges[key] = edge

        return edge

    def remove_edge(self, source_id, target_id):
        """移除跳转关系"""
        key = (source_id, target_id)
        if key in self.edges:
            edge = self.edges.pop(key)
            self.scene.removeItem(edge)

            # 从节点的边列表中移除
            edge.source_node.remove_edge(edge)
            edge.target_node.remove_edge(edge)

    def clear(self):
        """清空视图"""
        self.scene.clear()
        self.nodes = {}
        self.edges = {}

    def wheelEvent(self, event):
        """缩放视图"""
        zoom_factor = 1.2
        if event.angleDelta().y() < 0:
            zoom_factor = 1.0 / zoom_factor
        self.scale(zoom_factor, zoom_factor)

    def handle_node_double_clicked(self, task_id):
        """处理节点双击事件"""
        # 可以在这里添加编辑任务详情的功能
        pass

    def handle_connect_request(self, source_id):
        """处理连接请求"""
        # 创建节点选择对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("选择目标节点")
        dialog.setMinimumSize(300, 400)

        layout = QVBoxLayout(dialog)

        # 添加节点列表
        node_list = QListWidget()
        node_list.setFont(QFont('SimHei', 11))

        # 列出所有不是源节点且不是源节点祖先的任务（避免循环）
        valid_targets = []
        for task_id in self.tasks.keys():
            if task_id != source_id and not self.is_ancestor(task_id, source_id):
                valid_targets.append(task_id)

        for task_id in valid_targets:
            node_list.addItem(task_id)

        layout.addWidget(QLabel("选择要连接到的节点:"))
        layout.addWidget(node_list)

        # 添加按钮
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        layout.addWidget(btn_box)

        if dialog.exec() == QDialog.DialogCode.Accepted and node_list.currentItem():
            target_id = node_list.currentItem().text()
            self.connect_tasks(source_id, target_id)

    def is_ancestor(self, task_id, potential_ancestor_id):
        """检查一个任务是否是另一个任务的祖先"""
        current_id = task_id
        while current_id in self.parent_map and self.parent_map[current_id] is not None:
            if self.parent_map[current_id] == potential_ancestor_id:
                return True
            current_id = self.parent_map[current_id]
        return False

    def connect_tasks(self, source_id, target_id):
        """连接两个任务并更新优先级"""
        # 获取源任务和目标任务的优先级
        source_priority = self.tasks[source_id]["优先级"]

        # 目标任务的新优先级应该是源任务优先级 + 1
        new_priority = source_priority + 1

        # 更新目标任务及其所有子任务的优先级
        self.update_priority_recursive(target_id, new_priority)

        # 保存到配置文件
        self.save_config()

        # 更新任务树结构
        # 1. 从原来的父节点中移除目标任务
        old_parent = self.parent_map[target_id]
        if old_parent:
            self.task_tree[old_parent].remove(target_id)

        # 2. 将目标任务添加到源节点的子节点列表中
        self.task_tree[source_id].append(target_id)
        self.parent_map[target_id] = source_id

        # 重新初始化视图
        self.init()

    def update_priority_recursive(self, task_id, new_priority):
        """递归更新任务及其所有子任务的优先级"""
        # 更新当前任务的优先级
        self.tasks[task_id]["优先级"] = new_priority

        # 递归更新所有子任务的优先级
        for child_id in self.task_tree[task_id]:
            self.update_priority_recursive(child_id, new_priority + 1)

    def save_config(self):
        """保存配置到文件"""
        try:
            with open(get_real_path("src/TaskConfig.json"), 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, indent=4, ensure_ascii=False)
            self.logger.info("配置文件已更新")
        except Exception as e:
            self.logger.error(f"保存配置文件时出错: {e}")

    def handle_disconnect_request(self, source_id, target_id):
        """处理断开连接请求"""
        # 从任务树中移除连接
        if source_id in self.task_tree and target_id in self.task_tree[source_id]:
            self.task_tree[source_id].remove(target_id)
            self.parent_map[target_id] = None

            # 重新计算目标任务的优先级（设置为最低优先级）
            min_priority = min(task["优先级"] for task in self.tasks.values())
            self.update_priority_recursive(target_id, min_priority)

            # 保存到配置文件
            self.save_config()

            # 重新初始化视图
            self.init()


    def showEvent(self, event):
        """显示时适应视图"""
        super().showEvent(event)
        if self.scene.items():
            self.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def auto_layout(self):
        """基于任务树的层级布局"""
        if not self.nodes:
            return

        # 1. 计算每个层级的节点
        layers = {}  # 存储每个层级的节点
        node_layers = {}  # 存储每个节点所在的层级

        def assign_layer(task_id, layer=0):
            """递归分配节点层级"""
            if task_id not in node_layers:
                node_layers[task_id] = layer
                if layer not in layers:
                    layers[layer] = []
                layers[layer].append(task_id)
                # 递归处理子节点
                for child_id in self.task_tree.get(task_id, []):
                    assign_layer(child_id, layer + 1)

        # 找到根节点（没有父节点的节点）
        root_nodes = [task_id for task_id in self.tasks.keys()
            if self.parent_map.get(task_id) is None]

        # 从每个根节点开始分配层级
        for root in root_nodes:
            assign_layer(root)

        # 2. 设置布局参数
        vertical_spacing = 500  # 层级之间的垂直间距
        horizontal_spacing = 800  # 同层级节点之间的水平间距
        start_y = -len(layers) * vertical_spacing / 2  # 最上层的Y坐标

        # 3. 布局每一层的节点
        for layer, task_ids in sorted(layers.items()):
            # 计算当前层的起始X坐标（居中对齐）
            layer_width = (len(task_ids) - 1) * horizontal_spacing
            start_x = -layer_width / 2

            # 布局当前层的所有节点
            for i, task_id in enumerate(task_ids):
                if task_id in self.nodes:
                    node = self.nodes[task_id]
                    x = start_x + i * horizontal_spacing
                    y = start_y + layer * vertical_spacing
                    node.setPos(x, y)

        # 4. 适应视图
        self.fitInView(self.scene.itemsBoundingRect(),
                       Qt.AspectRatioMode.KeepAspectRatio)

    def handle_node_clicked(self, task_id):
        """处理节点单击事件"""
        # 如果点击的是当前已高亮的节点，则取消高亮
        if self.highlighted_node and self.highlighted_node.base_priority == task_id:
            self.clear_highlights()
            return

        # 清除之前的高亮
        self.clear_highlights()

        # 获取当前点击的节点
        node = self.nodes.get(task_id)
        if not node:
            return

        # 高亮当前节点
        node.set_highlight(True)
        self.highlighted_node = node

        # 高亮直接连接的节点和边
        for edge in node.edges:
            if edge.source_node == node:
                # 高亮被指向的节点
                edge.target_node.set_highlight(True)

    def clear_highlights(self):
        """清除所有高亮效果"""
        if self.highlighted_node:
            self.highlighted_node.set_highlight(False)
            self.highlighted_node = None

        # 清除所有节点的高亮
        for node in self.nodes.values():
            node.set_highlight(False)

    def mousePressEvent(self, event):
        """处理视图鼠标点击事件"""
        # 只处理节点点击，不处理空白区域点击
        super().mousePressEvent(event)


if __name__ == "__main__":
    import sys

    setup_logging()

    app = QApplication(sys.argv)
    view = TaskGraphView()
    view.show()
    sys.exit(app.exec())
