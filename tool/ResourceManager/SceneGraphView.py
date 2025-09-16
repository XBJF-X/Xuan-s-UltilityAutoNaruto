import logging
import math
from pathlib import Path

from PySide6.QtCore import Qt, QPointF, Signal, QObject, QLineF
from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QPainterPath, QAction, QFont
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsPathItem, QMenu, \
    QGraphicsTextItem, QDialog, \
    QVBoxLayout, QListWidget, QLabel, QDialogButtonBox, QGraphicsRectItem, QApplication

from StaticFunctions import get_real_path
from tool.ResourceManager.ResourceDBManager import ResourceDBManager
from tool.ResourceManager.SceneEditor import SceneEditor
from utils.Base.Recognizer import Recognizer
from utils.Base.Scene.SceneGraph import SceneGraph
from utils.Base.Scene.TransitionManager import TransitionManager


class SceneNodeSignals(QObject):
    """信号容器类，用于处理非QObject派生类中的信号"""
    double_clicked = Signal(str)  # 节点双击信号，传递场景ID
    clicked = Signal(str)  # 节点单击信号，传递场景ID
    request_connect = Signal(str)  # 请求连接信号，传递源场景ID
    request_disconnect = Signal(str, str)  # 请求断开连接信号，传递源场景ID和目标场景ID
    request_del = Signal(str)


class SceneNode(QGraphicsRectItem):
    """自定义场景节点类，矩形节点"""

    def __init__(self, scene_id, pos=None, parent=None):
        # 先创建文本项以计算所需大小
        self.text = QGraphicsTextItem(scene_id)
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
        self.scene_id = scene_id
        self.is_highlighted = False  # 高亮状态
        self.normal_color = QColor(70, 130, 180)  # 正常颜色
        self.highlight_color = QColor(57, 197, 187)  # 高亮颜色（金色）

        # 创建信号容器对象
        self.signals = SceneNodeSignals()

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
            self.signals.clicked.emit(self.scene_id)  # 通过信号容器发射单击信号
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """处理双击事件"""
        self.signals.double_clicked.emit(self.scene_id)  # 通过信号容器发射信号
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        """处理右键菜单事件"""
        menu = QMenu()

        # 添加"复制场景名称"菜单项
        copy_action = QAction("复制场景名称", menu)
        copy_action.triggered.connect(lambda: QApplication.clipboard().setText(self.scene_id))
        menu.addAction(copy_action)

        # 添加分隔线
        menu.addSeparator()
        # 添加"连接节点"菜单项
        connect_action = QAction("连接到节点", menu)
        connect_action.triggered.connect(lambda: self.signals.request_connect.emit(self.scene_id))
        menu.addAction(connect_action)

        # 添加"断开连接"子菜单
        if self.edges:
            disconnect_menu = menu.addMenu("断开连接")
            for edge in self.edges:
                # 只处理从当前节点出发的边
                if edge.source_node == self:
                    action = QAction(f"断开与 {edge.target_node.scene_id} 的连接", disconnect_menu)
                    action.triggered.connect(
                        lambda _, s=self.scene_id, t=edge.target_node.scene_id:
                        self.signals.request_disconnect.emit(s, t)
                    )
                    disconnect_menu.addAction(action)
        # 添加"连接节点"菜单项
        del_action = QAction("删除该节点", menu)
        del_action.triggered.connect(lambda: self.signals.request_del.emit(self.scene_id))
        menu.addAction(del_action)

        menu.exec(event.screenPos())

    def itemChange(self, change, value):
        """当节点位置改变时，更新所有连接的边"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.edges:
                edge.update_position()
        return super().itemChange(change, value)


class SceneEdge(QGraphicsPathItem):
    """自定义场景边类，连接两个节点"""

    def __init__(self, source_node, target_node, transition_manager, parent=None):
        super().__init__(parent)
        self.source_node = source_node
        self.target_node = target_node

        # 颜色定义
        self.normal_color = QColor(105, 105, 105)  # 正常颜色-灰色
        self.warning_color = QColor(255, 140, 0)   # 警告颜色-橙色
        self.error_color = QColor(220, 20, 60)     # 错误颜色-红色

        # 只检查当前边的方向是否实现
        source_to_target = (source_node.scene_id, target_node.scene_id) in transition_manager.transition_map

        # 根据实现状态设置颜色
        if source_to_target:
            # 已实现
            self.setPen(QPen(self.normal_color, 10))
        else:
            # 未实现
            self.setPen(QPen(self.error_color, 10))

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


class SceneGraphView(QGraphicsView):
    """场景图可视化视图（增强版）"""

    # 定义信号
    node_double_clicked = Signal(str)  # 节点双击信号
    node_clicked = Signal(str)  # 节点单击信号
    connect_requested = Signal(str)  # 连接请求信号（源节点ID）
    disconnect_requested = Signal(str, str)  # 断开连接请求信号（源节点ID, 目标节点ID）
    del_requested = Signal(str)

    def __init__(self, resource_manager: ResourceDBManager, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger("场景可视化视图")
        self.resource_manager = resource_manager
        self.transition_manager = TransitionManager(None)
        self.recognizer = Recognizer(SceneGraph(self.resource_manager))
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.nodes = {}  # 场景ID到节点对象的映射
        self.edges = {}  # (源ID, 目标ID)到边对象的映射
        self.highlighted_node = None  # 当前高亮的节点

        # 设置视图属性
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setInteractive(True)

        # 连接信号
        # 连接节点单击信号
        self.node_clicked.connect(self.handle_node_clicked)
        self.node_double_clicked.connect(self.handle_node_double_clicked)
        self.connect_requested.connect(self.handle_connect_request)
        self.disconnect_requested.connect(self.handle_disconnect_request)
        self.del_requested.connect(self.handle_del_request)

        self.init()

    def init(self):
        self.clear()
        self.highlighted_node = None  # 当前高亮的节点
        for scene in self.resource_manager.get_all_scenes():
            self.add_node(scene.name)
        for edge in self.resource_manager.get_all_scene_edges():
            self.logger.debug(f"连接[{edge.source_scene.name}]->[{edge.target_scene.name}]")
            self.add_edge(edge.source_scene.name, edge.target_scene.name)

        # 初始化后自动布局
        self.auto_layout()

    def add_node(self, scene_id, pos=None):
        """添加场景节点"""
        if scene_id in self.nodes:
            return self.nodes[scene_id]

        # 创建自定义节点
        node = SceneNode(scene_id, pos)
        self.scene.addItem(node)
        self.nodes[scene_id] = node

        if not any(element.symbol == 1 for element in
                           self.resource_manager.get_scene_by_name(scene_id).elements):
            node.text.setDefaultTextColor(Qt.GlobalColor.red)

        destination = Path(get_real_path("test_scene")) / f"{scene_id}.png"
        if not destination.exists():
            node.text.setDefaultTextColor(Qt.GlobalColor.yellow)

        # 连接节点的信号
        node.signals.double_clicked.connect(self.node_double_clicked)
        node.signals.clicked.connect(self.node_clicked)  # 连接单击信号
        node.signals.request_connect.connect(self.connect_requested)
        node.signals.request_disconnect.connect(self.disconnect_requested)
        node.signals.request_del.connect(self.del_requested)

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
                if other_id == scene_id:
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

    def remove_node(self, scene_id):
        """删除场景节点及其所有关联的边"""
        # 先收集所有需要删除的边
        edges_to_remove = []
        for edge_key in list(self.edges.keys()):  # 使用list()避免迭代时修改字典
            if edge_key[0] == scene_id or edge_key[1] == scene_id:
                edges_to_remove.append(edge_key)

        # 删除所有关联的边
        for edge_key in edges_to_remove:
            self.remove_edge(edge_key[0], edge_key[1])

        # 删除节点本身
        if scene_id in self.nodes:
            node = self.nodes[scene_id]
            self.scene.removeItem(node)
            del self.nodes[scene_id]

    def add_edge(self, source_id, target_id):
        """添加场景跳转关系"""
        if source_id not in self.nodes or target_id not in self.nodes:
            return None

        key = (source_id, target_id)
        if key in self.edges:
            return self.edges[key]

        source_node = self.nodes[source_id]
        target_node = self.nodes[target_id]

        # 创建自定义边，传入 transition_manager
        edge = SceneEdge(source_node, target_node, self.transition_manager)
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

    def handle_node_double_clicked(self, scene_id):
        # 创建 NewSceneNode 对话框实例，传入资源管理器
        se = SceneEditor(scene_id, self.resource_manager, self.recognizer)
        # 显示模态对话框（用户必须完成操作才能返回）
        result = se.exec()  # 阻塞当前流程，直到对话框关闭

        # 根据对话框返回结果进行后续处理
        if result == QDialog.DialogCode.Accepted:
            self.logger.debug(f"保存对[{scene_id}]场景&元素的编辑")
        else:
            self.logger.debug(f"[{scene_id}]场景&元素编辑器退出")

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
        target_ids = [edge.target_scene.name for edge in
            self.resource_manager.get_scene_by_name(source_id).out_edges]
        for node_id in self.nodes.keys():
            if node_id != source_id and node_id not in target_ids:
                node_list.addItem(node_id)

        layout.addWidget(QLabel("选择要连接到的节点:"))
        layout.addWidget(node_list)

        # 添加按钮
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        layout.addWidget(btn_box)

        if dialog.exec() == QDialog.DialogCode.Accepted and node_list.currentItem():
            target_id = node_list.currentItem().text()
            self.add_edge(source_id, target_id)
            self.logger.debug(f"连接[{source_id}]->[{target_id}]")
            self.resource_manager.add_scene_edge(source_id, target_id)
            # # 连接后自动布局
            # self.auto_layout()

    def handle_disconnect_request(self, source_id, target_id):
        """处理断开连接请求"""
        self.remove_edge(source_id, target_id)
        self.logger.debug(f"断开[{source_id}]->[{target_id}]")
        self.resource_manager.delete_scene_edge(source_id, target_id)
        # # 断开后自动布局
        # self.auto_layout()

    def handle_del_request(self, scene_id):
        self.logger.debug(f"删除场景[{scene_id}]")
        self.resource_manager.delete_scene(scene_id)
        self.remove_node(scene_id)

    def showEvent(self, event):
        """显示时适应视图"""
        super().showEvent(event)
        if self.scene.items():
            self.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def auto_layout(self, iterations=30000):
        """
        使用networkx优化布局，替代手动实现的力导向算法
        参数:
            iterations: 迭代次数，默认1000次
        """
        if len(self.nodes) == 0:
            return

        # 创建networkx图对象
        import networkx as nx
        G = nx.Graph()

        # 添加节点（使用节点对象ID作为标识）
        node_ids = {}
        for idx, node in enumerate(self.nodes.values()):
            node_ids[idx] = node
            G.add_node(idx)

        # 添加边
        for edge in self.edges.values():
            source_idx = [idx for idx, n in node_ids.items() if n == edge.source_node][0]
            target_idx = [idx for idx, n in node_ids.items() if n == edge.target_node][0]
            G.add_edge(source_idx, target_idx)

        # 使用networkx的spring_layout布局算法
        pos = nx.spring_layout(
            G,
            k=1000 / len(G.nodes) ** 0.5,  # 节点间距参数
            iterations=iterations,
            seed=42,  # 固定种子保证可重复布局
            scale=1000 * len(G.nodes) ** 0.5  # 布局缩放比例
        )

        # 应用布局到节点
        for idx, position in pos.items():
            node = node_ids[idx]
            node.setPos(position[0], position[1])  # 缩放坐标到合适范围

        # 布局完成后适应视图
        self.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def handle_node_clicked(self, scene_id):
        """处理节点单击事件"""
        # 如果点击的是当前已高亮的节点，则取消高亮
        if self.highlighted_node and self.highlighted_node.scene_id == scene_id:
            self.clear_highlights()
            return

        # 清除之前的高亮
        self.clear_highlights()

        # 获取当前点击的节点
        node = self.nodes.get(scene_id)
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
