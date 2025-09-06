import logging
import logging
import os
from typing import Dict

from PySide6.QtCore import Qt, Signal, Slot, QPointF, QRectF, QPoint
from PySide6.QtGui import QPixmap, QAction, QStandardItem, QStandardItemModel, QDragEnterEvent, \
    QDropEvent, QMouseEvent, QPen, QColor, QBrush
from PySide6.QtWidgets import (QDialog, QFileDialog, QMessageBox, QGraphicsScene,
                               QLabel, QMenu, QGraphicsView,
                               QGraphicsPixmapItem, QVBoxLayout, QWidget, QScrollArea,
                               QGraphicsRectItem, QFrame)

from StaticFunctions import cv_imread, split_gray_alpha, split_gray_alpha_bytes, \
    element_to_qpixmap
from tool.ResourceManager.NewElement import NewElement, RatioDialog
from tool.ResourceManager.ResourceDBManager import ResourceDBManager
from tool.ResourceManager.model import Element
from ui.SceneEditor_ui import Ui_SceneEditor
from utils.Base.Enums import ElementType, MatchType
from utils.Base.Recognizer import Recognizer


class ImageGraphicsView(QGraphicsView):
    roiSelected = Signal(QRectF)  # 框选区域信号
    coordinateSelected = Signal(QPointF)  # 坐标选择信号
    coordinateHovered = Signal(QPointF)  # 新增：鼠标悬停坐标信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger("场景编辑器-预览框")
        # 创建场景
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        # 设置提示文本
        self.scene.addText("拖拽图片到此处预览")
        # 启用拖拽功能
        self.setAcceptDrops(True)
        # 启用鼠标追踪
        self.setMouseTracking(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # 用于手动实现拖拽的变量
        self._is_panning = False
        self._pan_start_vscroll = None
        self._pan_start_hscroll = None
        self._pan_start_pos = QPointF()

        # 背景图片项
        self.background_item = None

        # 添加高亮区域相关变量
        self.highlight_item = None  # 高亮区域图形项
        self.highlight_rect = None  # 当前高亮区域

        # 新增状态变量
        self.selection_mode = None  # 'roi', 'coordinate'
        self.selection_rect = None  # 用于绘制选择框的图形项
        self.selection_start = None  # 选择开始点

        # 创建坐标显示标签
        self.coord_label = QLabel(self)
        self.coord_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 150);
                color: white;
                padding: 2px 5px;
                border-radius: 3px;
                font: 10pt "Consolas";
            }
        """)
        self.coord_label.setText("(x, y)")
        self.coord_label.adjustSize()
        self.coord_label.hide()  # 初始隐藏

    def highlight_area(self, rect: QRectF):
        """
        在背景图片上高亮显示指定区域

        :param rect: 要高亮的区域 (x, y, width, height)
        """
        # 清除现有高亮区域
        self.clear_highlight()

        # 创建半透明红色矩形
        self.highlight_item = QGraphicsRectItem(rect)

        # 设置样式：红色边框 + 半透明红色填充
        pen = QPen(Qt.GlobalColor.red, 2)
        brush = QBrush(QColor(255, 0, 0, 50))  # 半透明红色

        self.highlight_item.setPen(pen)
        self.highlight_item.setBrush(brush)

        # 添加到场景
        self.scene.addItem(self.highlight_item)

        # 保存当前高亮区域
        self.highlight_rect = rect

        # 确保高亮区域可见
        self.ensureVisible(self.highlight_item)

    def clear_highlight(self):
        """清除高亮区域"""
        if self.highlight_item:
            self.scene.removeItem(self.highlight_item)
            self.highlight_item = None
            self.highlight_rect = None

    def setSelectionMode(self, mode):
        """设置选择模式"""
        self.selection_mode = mode

        # 清除之前的选区图形
        if self.selection_rect:
            self.scene.removeItem(self.selection_rect)
            self.selection_rect = None

        if mode == 'roi':
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif mode == 'coordinate':
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event: QMouseEvent):
        if self.selection_mode and event.button() == Qt.MouseButton.LeftButton:
            # 使用 mapToScene 将视图坐标转换为场景坐标
            scene_pos = self.mapToScene(event.position().toPoint())

            # 开始选择操作
            self.selection_start = scene_pos

            if self.selection_mode == 'roi':
                # 创建选择矩形
                self.selection_rect = QGraphicsRectItem()
                self.selection_rect.setPen(QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.DashLine))
                self.scene.addItem(self.selection_rect)
                self.selection_rect.setRect(QRectF(self.selection_start, self.selection_start))
            elif self.selection_mode == 'coordinate':
                # 立即完成坐标选择
                self._handleCoordinateSelection(self.selection_start)

            event.accept()
        else:
            # 只在非选择模式下启用拖拽
            if event.button() == Qt.MouseButton.LeftButton and not self.selection_mode:
                self._is_panning = True
                self._pan_start_pos = event.position()
                # 记录拖拽开始时的滚动条位置
                self._pan_start_hscroll = self.horizontalScrollBar().value()
                self._pan_start_vscroll = self.verticalScrollBar().value()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                event.accept()
            else:
                super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        # 处理选择模式下的移动
        if self.selection_mode == 'roi' and self.selection_rect and self.selection_start:
            # 使用 mapToScene 将视图坐标转换为场景坐标
            current_scene_pos = self.mapToScene(event.position().toPoint())

            # 更新选择矩形
            rect = QRectF(self.selection_start, current_scene_pos).normalized()
            self.selection_rect.setRect(rect)
            event.accept()
        elif self._is_panning and not self.selection_mode:
            current_pos = event.pos()
            # 计算位移（注意滚动方向与鼠标移动方向相反）
            delta_x = self._pan_start_pos.x() - current_pos.x()
            delta_y = self._pan_start_pos.y() - current_pos.y()

            # 直接更新滚动条位置
            self.horizontalScrollBar().setValue(self._pan_start_hscroll + int(delta_x))
            self.verticalScrollBar().setValue(self._pan_start_vscroll + int(delta_y))

            event.accept()
        else:
            super().mouseMoveEvent(event)

        # 新增：显示鼠标位置坐标（无论是否在选择模式下都执行）
        if self.background_item:
            # 将鼠标位置转换为场景坐标
            scene_pos = self.mapToScene(event.position().toPoint())

            # 获取背景图片的边界矩形
            bg_rect = self.background_item.sceneBoundingRect()

            # 检查鼠标是否在背景图片内
            if bg_rect.contains(scene_pos):
                # 计算相对于背景图片左上角的坐标
                x = scene_pos.x() - bg_rect.x()
                y = scene_pos.y() - bg_rect.y()

                # 更新坐标标签文本
                self.coord_label.setText(f"({int(x)}, {int(y)})")
                self.coord_label.adjustSize()

                # 将标签放置在鼠标右下方（避免遮挡）
                label_pos = event.position().toPoint() + QPoint(10, 10)

                # 确保标签不会超出视图边界
                viewport_rect = self.viewport().rect()
                max_x = viewport_rect.right() - self.coord_label.width()
                max_y = viewport_rect.bottom() - self.coord_label.height()

                # 限制位置在视图范围内
                label_pos.setX(min(max(label_pos.x(), viewport_rect.left()), max_x))
                label_pos.setY(min(max(label_pos.y(), viewport_rect.top()), max_y))

                self.coord_label.move(label_pos)
                self.coord_label.show()

                # 发射悬停坐标信号（如果需要）
                self.coordinateHovered.emit(QPointF(x, y))
            else:
                self.coord_label.hide()
        else:
            self.coord_label.hide()

    def leaveEvent(self, event):
        """鼠标离开视图时隐藏坐标标签"""
        self.coord_label.hide()
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.selection_mode == 'roi' and self.selection_rect and self.selection_start:
            # 使用 mapToScene 将视图坐标转换为场景坐标
            current_scene_pos = self.mapToScene(event.position().toPoint())

            # 完成ROI选择
            rect = QRectF(self.selection_start, current_scene_pos).normalized()

            # 确保矩形在背景图片范围内
            if self.background_item:
                bg_rect = self.background_item.sceneBoundingRect()
                rect = rect.intersected(bg_rect)

            # 发射信号并清理
            self.roiSelected.emit(rect)
            self._cleanupSelection()
            event.accept()
        elif event.button() == Qt.MouseButton.LeftButton and self._is_panning:
            self._is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)  # 恢复默认光标
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def _handleCoordinateSelection(self, point):
        """处理坐标选择"""
        # 确保点在背景图片范围内
        if self.background_item:
            bg_rect = self.background_item.sceneBoundingRect()
            if bg_rect.contains(point):
                self.coordinateSelected.emit(point)

        self._cleanupSelection()

    def _cleanupSelection(self):
        """清理选择状态"""
        if self.selection_rect:
            self.scene.removeItem(self.selection_rect)
            self.selection_rect = None

        self.selection_start = None
        self.selection_mode = None
        self.setCursor(Qt.CursorShape.ArrowCursor)

    # 修改后的dropEvent：处理背景图片拖入
    def dropEvent(self, event: QDropEvent):
        """放下事件：处理图片文件"""
        if event.mimeData().hasUrls():
            self.clear_highlight()
            # 清空现有场景内容
            self.scene.clear()

            # 重置背景项
            self.background_item = None

            # 处理每个拖入的文件
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if self.is_image_file(file_path):
                        # 显示背景图片
                        pixmap = QPixmap(file_path)
                        if not pixmap.isNull():
                            # 创建背景项
                            self.background_item = QGraphicsPixmapItem(pixmap)
                            self.background_item.setZValue(0)  # 背景在底层
                            self.scene.addItem(self.background_item)

                            # 设置场景大小
                            self.scene.setSceneRect(pixmap.rect())

                            # 居中显示图片
                            self.fitInView(self.background_item, Qt.AspectRatioMode.KeepAspectRatio)

                            event.acceptProposedAction()
                            return

            # 如果没有成功加载背景图片，恢复提示文本
            self.scene.addText("拖拽图片到此处预览")
        event.ignore()

    def resizeEvent(self, event):
        """窗口大小改变时，重新居中图片"""
        super().resizeEvent(event)
        if self.background_item:
            self.fitInView(self.background_item, Qt.AspectRatioMode.KeepAspectRatio)

    def wheelEvent(self, event):
        """缩放视图"""
        zoom_factor = 1.2
        if event.angleDelta().y() < 0:
            zoom_factor = 1.0 / zoom_factor

        # 保存当前视图中心
        old_pos = self.mapToScene(self.viewport().rect().center())

        # 执行缩放
        self.scale(zoom_factor, zoom_factor)

        # 缩放后重新居中
        if self.background_item:
            self.centerOn(old_pos)
            self.fitInView(self.background_item, Qt.AspectRatioMode.KeepAspectRatio)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件：判断是否为图片文件"""
        if event.mimeData().hasUrls():
            # 检查第一个URL是否为图片文件
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    # 检查文件扩展名
                    if self.is_image_file(file_path):
                        event.acceptProposedAction()
                        return
        event.ignore()

    def dragMoveEvent(self, event):
        """拖拽移动事件：接受拖拽"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def is_image_file(self, file_path):
        """判断文件是否为图片格式"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
        ext = os.path.splitext(file_path)[1].lower()
        return ext in image_extensions


class ImagePreviewDialog(QDialog):
    def __init__(self, element, parent=None):
        super().__init__(parent)
        self.setWindowTitle("图片预览")
        self.resize(800, 600)  # 设置初始大小
        self.setStyleSheet(
            """
            background-color: #f0f0f0;
        QScrollBar:vertical {
            background-color: rgb(197, 197, 197);
            width: 6px;
            margin: 1px;
            border-radius: 3px;
        }
        QScrollBar::handle:vertical {
            background-color: #8b8b8b;
            border-radius: 3px;
            margin: 3 0px 6 0px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover,
        QScrollBar::handle:vertical:pressed {
            background-color: #3c3f41;
            border-radius: 3px;
            margin: 0 0px 0 0px;
        }
        QScrollBar::sub-line:vertical {
            border: none;
            height: 0px;
        }
        QScrollBar::add-line:vertical {
            border: none;
            height: 0px;
        }
        QScrollBar:horizontal {
            background-color: rgb(197, 197, 197);
            width: 6px;
            margin: 1px;
            border-radius: 3px;
        }
        QScrollBar::handle:horizontal {
            background-color: #8b8b8b;
            border-radius: 3px;
            margin: 3 0px 6 0px;
            min-height: 30px;
        }
        QScrollBar::handle:horizontal:hover,
        QScrollBar::handle:horizontal:pressed {
            background-color: #3c3f41;
            border-radius: 3px;
            margin: 0 0px 0 0px;
        }
        QScrollBar::sub-line:horizontal {
            border: none;
            height: 0px;
        }
        QScrollBar::add-line:horizontal {
            border: none;
            height: 0px;
        }
            """
        )  # 设置对话框背景色

        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)  # 增加外边距
        main_layout.setSpacing(20)  # 增加控件间距

        # 添加滚动区域（避免图片过大超出窗口）
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)  # 移除边框
        main_layout.addWidget(scroll_area)

        # 滚动区域内的容器
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 图片居中显示
        container_layout.setContentsMargins(10, 10, 10, 10)  # 容器内边距
        container_layout.setSpacing(20)  # 增加图片间距
        scroll_area.setWidget(container)
        bgar = element_to_qpixmap(element, "bgra")
        gray = element_to_qpixmap(element, "gray")
        mask = element_to_qpixmap(element, "mask")

        # 依次添加三张图片
        self._add_image_to_layout(container_layout, bgar, "原图 (BGAR)")
        self._add_image_to_layout(container_layout, gray, "灰度图 (GRAY)")
        self._add_image_to_layout(container_layout, mask, "掩码图 (MASK)")

    @staticmethod
    def _add_image_to_layout(layout, image: QPixmap, title: str):
        """向布局添加图片和标题，处理图片不存在的情况"""
        # 创建包装容器 - 带背景色和圆角
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #d0d0d0;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)  # 内边距
        container_layout.setSpacing(5)  # 控件间距

        # 添加标题标签
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-family: "Consolas", "黑体";
                font-size: 14pt;
                font-weight: bold;
                color: #333333;
                padding: 3px;
                border:none;
            }
        """)
        container_layout.addWidget(title_label)

        if image is None:
            # 图片存在但无法加载（如格式错误）
            error_label = QLabel(f"图片为空")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("""
                            QLabel {
                                color: #ff5555;
                                padding: 20px;
                                font-size: 12pt;
                            }
                        """)
            container_layout.addWidget(error_label)
        elif image.isNull():
            # 图片存在但无法加载（如格式错误）
            error_label = QLabel(f"无法加载图片")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("""
                QLabel {
                    color: #ff5555;
                    padding: 20px;
                    font-size: 12pt;
                }
            """)
            container_layout.addWidget(error_label)
        else:
            # 限制图片最大宽度（避免过宽）
            max_width = 700
            if image.width() > max_width:
                image = image.scaledToWidth(max_width, Qt.TransformationMode.SmoothTransformation)

            image_label = QLabel()
            image_label.setPixmap(image)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image_label.setStyleSheet("""
            background-color: transparent;
            border:none;
            """)  # 透明背景
            container_layout.addWidget(image_label)

        layout.addWidget(container)


class SceneEditor(QDialog):
    item_clicked = Signal(dict)

    def __init__(self, scene_id, resource_manager: ResourceDBManager, recognizer: Recognizer):
        super().__init__()
        self.UI = Ui_SceneEditor()
        self.UI.setupUi(self)
        self.logger = logging.getLogger("场景&元素编辑器")
        self.scene_id = scene_id
        self.resource_manager = resource_manager
        self.recognizer = recognizer
        self.current_scene = self.resource_manager.get_scene_by_name(self.scene_id)
        self.current_item = None
        self.clicked_index = None

        self.element_ratio_list = [0.5, 0.5]
        self.element_roi_list = [0, 0, 1600, 900]
        self.element_coordinate_list = [0, 0]

        # 创建自定义的图片视图
        self.img_graphics_view = ImageGraphicsView()
        self.UI.image_container.layout().addWidget(self.img_graphics_view)

        # 连接点击信号
        self.UI.Element_tree.clicked.connect(self.on_item_clicked)
        # 连接自定义信号到槽函数
        self.item_clicked.connect(self._handle_tree_item_clicked)
        # 初始化树视图
        self._init_tree_view()
        # 绑定信号槽
        self._bind_signals()

    def _init_tree_view(self):
        """初始化树视图显示场景和元素结构，按首字母排序节点"""
        self.current_scene = self.resource_manager.get_scene_by_name(self.scene_id)
        # 创建标准项模型（0行，1列）
        model = QStandardItemModel(0, 1, self)

        # 添加根节点
        root = QStandardItem(self.current_scene.name)
        model.appendRow(root)

        # 收集所有元素ID并按首字母排序
        element_ids = sorted([element.name for element in self.current_scene.elements])  # 按首字母升序排序

        # 按排序后的顺序添加子节点
        for element_id in element_ids:
            element = self.resource_manager.get_scene_element(self.scene_id, element_id)
            child = QStandardItem(element_id)
            if element.type == ElementType.IMG and element.match_type == MatchType.SIFT:
                child.setData(QColor(255, 0, 0), Qt.ItemDataRole.ForegroundRole)
            root.appendRow(child)

        # 设置模型到TreeView
        self.UI.Element_tree.setModel(model)

        # 对根节点的子节点按第0列（元素ID列）进行升序排序
        # 第一个参数：排序的列索引（这里只有1列，所以是0）
        # 第二个参数：排序方式（Qt.AscendingOrder 升序，Qt.DescendingOrder 降序）
        root.sortChildren(0, Qt.SortOrder.AscendingOrder)

        # 展开所有节点
        self.UI.Element_tree.expandAll()

    def on_item_clicked(self, index):
        # 获取模型和项目
        model = self.UI.Element_tree.model()
        item = model.itemFromIndex(index)
        item_name = item.text()

        # 判断节点类型：检查父索引是否有效
        # 根节点的父索引是无效的（isValid() 返回 False）
        if not index.parent().isValid():
            node_type = "SCENE"  # 根节点
        else:
            node_type = "ELEMENT"  # 子节点（包括所有层级的子节点）
        # 发射信号，包含名称和类型
        self.item_clicked.emit({'type': node_type, 'id': item_name})

    @Slot(str)
    def _handle_tree_item_clicked(self, item_dict: Dict):
        self._handle_save()
        item_type = item_dict.get('type')
        item_id = item_dict.get('id')
        if self.current_item is not None and self.current_item.get('id') == item_id:
            self.logger.debug(f"已选中{item_id}")
            return
        else:
            self.current_item = item_dict
            self.element_ratio_list = [0.5, 0.5]
            self.element_roi_list = [0, 0, 1600, 900]
            self.element_coordinate_list = [0, 0]
            if item_type == "SCENE":
                self.logger.debug(f"场景[{item_id}]")
                # 加载当前值
                self.UI.scene_id_edit.setText(self.current_scene.name)
                self.UI.stackedWidget.setCurrentIndex(0)
                self.img_graphics_view.clear_highlight()

            elif item_type == "ELEMENT":
                self.logger.debug(f"元素[{item_id}]")
                element: Element = self.resource_manager.get_scene_element(self.scene_id, item_id)
                if element.type == ElementType.IMG:
                    # 加载当前值
                    self.UI.element_id_edit.setText(element.name)
                    self.UI.element_type.setCurrentIndex(element.type.value)
                    self.UI.element_threshold.setValue(element.threshold)
                    self.UI.element_ratio.setText(f"({element.ratio_x:.2f},{element.ratio_y:.2f})")
                    self.element_ratio_list = [element.ratio_x, element.ratio_y]
                    self.UI.element_match_type.setCurrentIndex(element.match_type.value)
                    self.UI.element_roi.setText(str([element.roi_x, element.roi_y, element.roi_width,
                                                        element.roi_height]))
                    self.img_graphics_view.highlight_area(
                        QRectF(
                            element.roi_x,
                            element.roi_y,
                            element.roi_width,
                            element.roi_height
                        ))
                    # if element.match_type == MatchType.TEMPLATE:
                    #     self.img_graphics_view.highlight_area(
                    #         QRectF(
                    #             element.roi[0],
                    #             element.roi[1],
                    #             element.roi[2],
                    #             element.roi[3]
                    #         ))
                    # else:
                    #     self.img_graphics_view.clear_highlight()
                    self.element_roi_list = [element.roi_x, element.roi_y, element.roi_width,
                        element.roi_height]
                    self.UI.stackedWidget.setCurrentIndex(1)
                    self.UI.stackedWidget_2.setCurrentIndex(0)

                elif element.type == ElementType.COORDINATE:
                    self.UI.element_id_edit.setText(element.name)
                    self.UI.element_type.setCurrentIndex(element.type.value)
                    self.UI.element_coordinate.setText(str([element.coordinate_x, element.coordinate_y]))
                    self.img_graphics_view.highlight_area(
                        QRectF(
                            element.coordinate_x - 20,
                            element.coordinate_y - 20,
                            40,
                            40
                        ))
                    self.element_coordinate_list = [element.coordinate_x, element.coordinate_y]
                    self.UI.stackedWidget.setCurrentIndex(1)
                    self.UI.stackedWidget_2.setCurrentIndex(1)

    def _bind_signals(self):
        """绑定信号和槽函数"""
        # 设置右键菜单
        self.UI.Element_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.UI.Element_tree.customContextMenuRequested.connect(self.show_context_menu)
        self.UI.button_save.clicked.connect(self._handle_save)
        self.UI.button_cancel.clicked.connect(self._handle_cancel)

        # 连接控件响应函数
        self.UI.scene_view_image_btn.clicked.connect(self._handle_view_image_btn_clicked)
        self.UI.scene_set_image_btn.clicked.connect(self._handle_set_img_btn_clicked)
        self.UI.element_view_image_btn.clicked.connect(self._handle_view_image_btn_clicked)
        self.UI.element_set_image_btn.clicked.connect(self._handle_set_img_btn_clicked)
        self.UI.set_roi_btn.clicked.connect(self._handle_set_roi_btn_clicked)
        self.UI.set_ratio_btn.clicked.connect(self._handle_set_ratio_btn_clicked)
        self.UI.set_coordinate_btn.clicked.connect(self._handle_set_coordinate_btn_clicked)
        self.UI.scene_split_image_btn.clicked.connect(self._handle_split_img_btn_clicked)
        self.UI.element_split_image_btn.clicked.connect(self._handle_split_img_btn_clicked)
        self.UI.scene_match_btn.clicked.connect(self._handle_match_btn_clicked)
        self.UI.element_match_btn.clicked.connect(self._handle_match_btn_clicked)

    def show_context_menu(self, position):
        # 获取右键点击位置对应的索引
        self.clicked_index = self.UI.Element_tree.indexAt(position)

        # 检查是否为根节点（根节点的父索引无效）
        is_root_node = self.clicked_index.isValid() and not self.clicked_index.parent().isValid()

        if is_root_node:
            # 是根节点，显示菜单
            context_menu = QMenu(self)

            # 添加"增加新元素"动作
            add_action = QAction("新建元素", self)
            add_action.triggered.connect(self._add_element)
            context_menu.addAction(add_action)

            # 在点击位置显示菜单
            context_menu.exec(self.UI.Element_tree.viewport().mapToGlobal(position))
        else:
            # 是根节点，显示菜单
            context_menu = QMenu(self)

            # 关键修改：获取当前元素ID并传递给删除函数
            model = self.UI.Element_tree.model()
            element_id = model.data(model.index(self.clicked_index.row(), 0, self.clicked_index.parent()))
            delete_action = QAction(f"删除[{element_id}]", self)
            # 使用lambda捕获element_id并传递给_del_element
            delete_action.triggered.connect(lambda: self._del_element(element_id))
            context_menu.addAction(delete_action)
            context_menu.exec(self.UI.Element_tree.viewport().mapToGlobal(position))

    def _add_element(self):
        self.logger.debug("新建元素窗口开启")
        ne = NewElement(self.current_scene, self.resource_manager, self.UI.Element_tree)
        # 显示模态对话框（用户必须完成操作才能返回）
        result = ne.exec()  # 阻塞当前流程，直到对话框关闭

        # 根据对话框返回结果进行后续处理
        if result == QDialog.DialogCode.Accepted:
            self._init_tree_view()
            self.logger.debug(f"确认创建新元素")
        else:
            self.logger.debug("取消创建新元素")

    def _del_element(self, element_id):
        if not element_id:
            return

        # 弹出确认对话框
        reply = QMessageBox.question(
            self,  # 父窗口
            "确认删除",  # 标题
            f"确定要删除元素【{element_id}】吗？\n删除后不可恢复",  # 提示信息
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,  # 按钮组合
            QMessageBox.StandardButton.No  # 默认选中按钮（推荐默认选No，防止误操作）
        )

        # 根据用户选择执行操作
        if reply == QMessageBox.StandardButton.Yes:
            self.logger.debug(f"用户确认删除元素【{element_id}】")
            try:
                self.resource_manager.delete_element_from_scene(self.scene_id, element_id)
                self._init_tree_view()
                QMessageBox.information(self, "成功", f"元素【{element_id}】已删除")
            except Exception as e:
                self.logger.error(f"删除元素失败: {str(e)}")
                QMessageBox.critical(self, "错误", f"删除失败：{str(e)}")
        else:
            self.logger.debug(f"用户取消删除元素【{element_id}】")

    def _handle_view_image_btn_clicked(self):
        if not self.current_item:
            QMessageBox.warning(self, "警告", "请先选择一个元素/场景")
            return
        item_type = self.current_item.get('type')
        item_id = self.current_item.get('id')
        try:
            if item_type == "SCENE":
                pass
            elif item_type == "ELEMENT":
                element: Element = self.resource_manager.get_scene_element(self.scene_id, item_id)
                # 显示图片预览对话框
                dialog = ImagePreviewDialog(element, self)
                dialog.exec()  # 模态显示对话框
            else:
                QMessageBox.warning(self, "警告", "未知类型，无法预览图片")
                return

        except Exception as e:
            QMessageBox.critical(self, "错误", f"预览图片失败: {str(e)}")

    def _handle_set_img_btn_clicked(self):
        """选择元素图片并添加"""
        if not self.current_item:
            QMessageBox.warning(self, "警告", "请先选择一个元素/场景")
            return
        item_type = self.current_item.get('type')
        item_id = self.current_item.get('id')
        if item_type == "SCENE":
            pass
        elif item_type == "ELEMENT":
            element: Element = self.resource_manager.get_scene_element(self.scene_id, item_id)
            file_path, _ = QFileDialog.getOpenFileName(
                self, f"选择【{item_id}】图片", "", "PNG图片 (*.png)"
            )
            if file_path:
                try:
                    self.logger.debug(file_path)
                    bgra, gray, mask = split_gray_alpha(file_path)
                    self.resource_manager.update_element_info(
                        scene_name=self.scene_id,
                        element_name=item_id,
                        bgra=bgra,
                        gray=gray,
                        mask=mask,
                        width=gray.shape[1],
                        height=gray.shape[0],
                        channels=bgra.shape[-1]
                    )
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"添加【{item_id}】图片失败: {str(e)}")

    def _handle_split_img_btn_clicked(self):
        if not self.current_item:
            QMessageBox.warning(self, "警告", "请先选择一个元素/场景")
            return
        item_type = self.current_item.get('type')
        item_id = self.current_item.get('id')
        if item_type == "SCENE":
            pass
        elif item_type == "ELEMENT":
            element: Element = self.resource_manager.get_scene_element(self.scene_id, item_id)
            if element.bgra:
                try:
                    bgra, gray, mask = split_gray_alpha_bytes(element.bgra)
                    self.resource_manager.update_element_info(
                        scene_name=self.scene_id,
                        element_name=element.name,
                        bgra=bgra,
                        gray=gray,
                        mask=mask,
                        width=gray.shape[1],
                        height=gray.shape[0],
                        channels=bgra.shape[-1]
                    )
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"添加【{item_id}】图片失败: {str(e)}")

    def _handle_match_btn_clicked(self):
        if not self.current_item:
            QMessageBox.warning(self, "警告", "请先选择一个元素/场景")
            return
        item_type = self.current_item.get('type')
        item_id = self.current_item.get('id')
        if item_type == "SCENE":
            if (self.current_scene.dir / "Example.png").exists():
                try:
                    scene_img = cv_imread(self.current_scene.dir / "Example.png")
                    flag, confidence = self.recognizer.scene_match(scene_img, self.recognizer.scene_graph.scenes.get(self.current_scene.name))
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"匹配失败: {str(e)}")
            else:
                QMessageBox.critical(self, "错误", f"目标不存在示例图片")
        elif item_type == "ELEMENT":
            element: Element = self.recognizer.scene_graph.scenes.get(self.current_scene.name).elements.get(item_id)
            if (self.current_scene.dir / "Example.png").exists():
                try:
                    scene_img = cv_imread(self.current_scene.dir / "Example.png")
                    coordinates = self.recognizer.element_match(scene_img, element)
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"匹配失败: {str(e)}")
            else:
                QMessageBox.critical(self, "错误", f"目标不存在示例图片")

    def _handle_set_roi_btn_clicked(self):
        """设置ROI：在背景图片上框选区域"""
        if not self.current_item or self.current_item['type'] != "ELEMENT":
            QMessageBox.warning(self, "警告", "请先选择一个元素")
            return

        if not self.img_graphics_view.background_item:
            QMessageBox.warning(self, "警告", "请先添加背景图片")
            return

        # 设置选择模式
        self.img_graphics_view.setSelectionMode('roi')

        # 连接信号
        self.img_graphics_view.roiSelected.connect(self._on_roi_selected)

    def _on_roi_selected(self, rect: QRectF):
        """处理ROI选择结果"""
        # 更新UI显示
        roi_str = f"({rect.x():.0f}, {rect.y():.0f}, {rect.width():.0f}, {rect.height():.0f})"
        self.img_graphics_view.highlight_area(
            QRectF(
                rect.x(),
                rect.y(),
                rect.width(),
                rect.height()
            ))
        self.element_roi_list = [int(rect.x()), int(rect.y()), int(rect.width()), int(rect.height())]
        self.UI.element_roi.setText(roi_str)

        # 断开信号连接
        self.img_graphics_view.roiSelected.disconnect(self._on_roi_selected)

    def _handle_set_ratio_btn_clicked(self):
        """设置Ratio：在元素图片上点击获取比例"""
        if not self.current_item or self.current_item['type'] != "ELEMENT":
            QMessageBox.warning(self, "警告", "请先选择一个元素")
            return

        element: Element = self.resource_manager.get_scene_element(self.scene_id, self.current_item['id'])

        if not element.bgra:
            QMessageBox.warning(self, "警告", "元素图片不存在")
            return

        # 创建对话框
        dialog = RatioDialog(element, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            ratio = dialog.get_ratio()
            # 更新UI显示
            ratio_str = f"({ratio.x():.2f}, {ratio.y():.2f})"
            self.element_ratio_list = [round(ratio.x(), 2), round(ratio.y(), 2)]
            self.UI.element_ratio.setText(ratio_str)

    def _handle_set_coordinate_btn_clicked(self):
        """设置坐标：在背景图片上点击获取坐标"""
        if not self.current_item or self.current_item['type'] != "ELEMENT":
            QMessageBox.warning(self, "警告", "请先选择一个元素")
            return

        if not self.img_graphics_view.background_item:
            QMessageBox.warning(self, "警告", "请先添加背景图片")
            return

        # 设置选择模式
        self.img_graphics_view.setSelectionMode('coordinate')

        # 连接信号
        self.img_graphics_view.coordinateSelected.connect(self._on_coordinate_selected)

    def _on_coordinate_selected(self, point: QPointF):
        """处理坐标选择结果"""
        # 更新UI显示
        coord_str = f"({point.x():.0f}, {point.y():.0f})"
        self.img_graphics_view.highlight_area(
            QRectF(
                point.x() - 20,
                point.y() - 20,
                40,
                40
            ))
        self.element_coordinate_list = [int(point.x()), int(point.y())]
        self.UI.element_coordinate.setText(coord_str)

        # 断开信号连接
        self.img_graphics_view.coordinateSelected.disconnect(self._on_coordinate_selected)

    def _handle_save(self):
        if not self.current_item:
            return
        if self.current_item.get('type') == "SCENE":
            if self.UI.scene_id_edit.text() != self.scene_id:
                self.resource_manager.rename_scene(self.scene_id, self.UI.scene_id_edit.text())
                self.scene_id = self.UI.scene_id_edit.text()

        elif self.current_item.get('type') == "ELEMENT":
            self.resource_manager.update_element_info(
                scene_name=self.scene_id,
                element_name=self.current_item.get('id'),
                type=self.UI.element_type.currentIndex(),
                threshold=self.UI.element_threshold.value(),
                match_type=self.UI.element_match_type.currentIndex(),
                ratio_x=self.element_ratio_list[0],
                ratio_y=self.element_ratio_list[1],
                roi_x=self.element_roi_list[0],
                roi_y=self.element_roi_list[1],
                roi_width=self.element_roi_list[2],
                roi_height=self.element_roi_list[3],
                coordinate_x=self.element_coordinate_list[0],
                coordinate_y=self.element_coordinate_list[1]
            )
            if self.UI.element_id_edit.text() != self.current_item.get('id'):
                self.resource_manager.rename_element(self.scene_id, self.current_item.get('id'), self.UI.element_id_edit.text())

        self.logger.debug(f"[{self.current_item.get('type')}-{self.current_item.get('id')}]保存成功")
        self._init_tree_view()
        self.img_graphics_view.clear_highlight()
        self.current_item = None

    def _handle_cancel(self):
        # 取消操作：直接关闭对话框
        self.reject()  # 关闭对话框，返回QDialog.Rejected

#
# if __name__ == "__main__":
#     def setup_logging():
#         # 创建基础日志格式
#         log_format = "%(asctime)s - %(levelname)s - %(message)s"
#
#         # 创建基础配置
#         logging.basicConfig(
#             level=logging.DEBUG,  # 设置默认日志级别
#             format=log_format,
#             handlers=[
#                 logging.StreamHandler(sys.stdout)  # 输出到控制台
#             ]
#         )
#
#         # 获取根日志记录器
#         logger = logging.getLogger()
#
#         # 设置更详细的日志格式（可选）
#         formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#
#         # 更新所有处理器的格式
#         for handler in logger.handlers:
#             handler.setFormatter(formatter)
#
#         # 设置特定模块的日志级别（可选）
#         # logging.getLogger("PySide6").setLevel(logging.WARNING)
#         # logging.getLogger("urllib3").setLevel(logging.WARNING)
#
#         return logger
#
#
#     # 设置日志系统
#     logger = setup_logging()
#     # 1. 首先设置DPI感知 - 使用兼容性更好的旧版API
#     if sys.platform == 'win32':
#         try:
#             # 使用兼容性更好的旧版API
#             ctypes.windll.user32.SetProcessDPIAware()
#         except Exception as e:
#             print(f"设置DPI感知失败: {e}")
#
#     # 2. 创建应用实例前设置高DPI策略
#     os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
#
#     # 3. 创建应用实例
#     app = QApplication(sys.argv)
#
#     # 4. 设置高DPI缩放策略（可选）
#     # 在PySide6 6.4+版本中，这步可能不需要
#     # app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
#     resource_manager = SceneResourceManager(Path(get_real_path("raw_src/Template/Scene")))
#     editor = SceneEditor("主场景", resource_manager)
#     editor.exec()
