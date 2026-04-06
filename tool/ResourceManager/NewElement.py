import logging
from pathlib import Path

from PySide6.QtCore import QPointF, Qt, QSize
from PySide6.QtGui import QPixmap, QMouseEvent
from PySide6.QtWidgets import QTreeView, QDialog, QVBoxLayout, QLabel, QMessageBox, QDialogButtonBox, \
    QFileDialog

from StaticFunctions import split_gray_alpha
from tool.ResourceManager.ResourceDBManager import ResourceDBManager
from tool.ResourceManager.model import Scene, Element, element_to_qpixmap
from tool.ResourceManager.ui.NewElement_ui import Ui_NewElement
from utils.Base.Enums import ElementType


class RatioDialog(QDialog):
    def __init__(self, image: Path | Element, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置比例")
        self.setMinimumSize(1000, 1200)
        self.ratio_point = QPointF()
        # 主布局
        layout = QVBoxLayout(self)

        # 图片标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray;")

        # 加载图片
        if isinstance(image, Path):
            pixmap = QPixmap(str(image))
            if pixmap.isNull():
                QMessageBox.critical(self, "错误", "无法加载图片")
                self.reject()
                return
        elif isinstance(image, Element):
            pixmap = element_to_qpixmap(image, "bgra")

        # 缩放图片以适应窗口
        max_size = QSize(600, 600)
        if pixmap.width() > max_size.width() or pixmap.height() > max_size.height():
            pixmap = pixmap.scaled(max_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self.image_label.setPixmap(pixmap)
        self.original_size = pixmap.size()

        # 提示标签
        self.info_label = QLabel("点击图片选择位置")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # 添加到布局
        layout.addWidget(self.image_label)
        layout.addWidget(self.info_label)
        layout.addWidget(button_box)

        # 连接点击事件
        self.image_label.mousePressEvent = self.on_image_clicked

    def on_image_clicked(self, event: QMouseEvent):
        """处理图片点击事件 - 支持图片外坐标"""
        label_pos = event.position()

        pixmap = self.image_label.pixmap()
        if pixmap is None:
            return

        # 获取显示图片的实际大小
        display_size = pixmap.size()
        label_size = self.image_label.size()

        # 计算图片显示区域的偏移量（居中对齐）
        x_offset = (label_size.width() - display_size.width()) / 2
        y_offset = (label_size.height() - display_size.height()) / 2

        # 计算点击位置相对于图片显示区域左上角的坐标（允许负值）
        img_x = label_pos.x() - x_offset
        img_y = label_pos.y() - y_offset

        # 计算归一化坐标（原点在图片左上角，允许超出 [0,1] 范围）
        # 直接使用 img_x / display_size.width()，允许负值和大于1的值
        self.ratio_point = QPointF(
            round(img_x / display_size.width(), 4),
            round(img_y / display_size.height(), 4)
        )

        # 判断点击位置状态
        in_horizontal = 0 <= self.ratio_point.x() <= 1
        in_vertical = 0 <= self.ratio_point.y() <= 1

        if in_horizontal and in_vertical:
            status = "✅ 图片内部"
        elif in_horizontal or in_vertical:
            status = "⚠️ 图片边缘外部"
        else:
            status = "❌ 图片角部外部"

        # 更新信息
        self.info_label.setText(
            f"已选择: ({self.ratio_point.x():.4f}, {self.ratio_point.y():.4f})\n"
            f"状态: {status}\n"
            f"点击位置在图片{'内' if in_horizontal and in_vertical else '外'}\n"
            "点击确定保存比例"
        )

    def get_ratio(self) -> QPointF:
        """获取选择的比例"""
        return self.ratio_point

class NewElement(QDialog):
    def __init__(self, scene: Scene, resource_manager: ResourceDBManager, tree: QTreeView, img_path: Path | None = None):
        super().__init__()
        self.UI = Ui_NewElement()
        self.UI.setupUi(self)
        self.logger = logging.getLogger("新建元素")
        self.scene = scene
        self.resource_manager = resource_manager
        self.tree = tree

        self.element_img_path: Path | None = img_path
        if self.element_img_path:
            self.UI.element_id_LineEdit.setText(self.element_img_path.stem)
        self.element_ratio_x = 0.5
        self.element_ratio_y = 0.5

        self.bind_signals()

    def bind_signals(self):
        self.UI.set_img_btn.clicked.connect(self._handle_set_img_btn_clicked)
        self.UI.set_ratio_btn.clicked.connect(self._handle_set_ratio_btn_clicked)

        self.UI.confirm.clicked.connect(self._handle_confirm)
        self.UI.cancel.clicked.connect(self._handle_cancel)
        self.UI.is_symbol.clicked.connect(self._handle_symbol)

    def _handle_set_img_btn_clicked(self):
        """选择元素图片并添加（支持覆盖拖拽的路径）"""
        # 打开文件选择框时，默认路径设为拖拽的图片路径（优化体验）
        initial_dir = str(self.element_img_path.parent) if self.element_img_path else ""
        file_path, _ = QFileDialog.getOpenFileName(
            self, f"选择【{self.UI.element_id_LineEdit.text()}】图片", initial_dir, "PNG图片 (*.png)"
        )
        if file_path:
            try:
                self.logger.debug(f"重新选择图片：{file_path}")
                self.element_img_path = Path(file_path)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加图片失败: {str(e)}")

    def _handle_set_ratio_btn_clicked(self):
        """设置Ratio：在元素图片上点击获取比例"""
        if not self.element_img_path:
            QMessageBox.warning(self, "警告", "未选择元素图片")
            return
        if not self.element_img_path.exists():
            QMessageBox.warning(self, "警告", "元素图片不存在")
            return

        # 创建对话框
        dialog = RatioDialog(self.element_img_path, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            ratio = dialog.get_ratio()
            # 更新UI显示
            ratio_str = f"({ratio.x():.2f}, {ratio.y():.2f})"
            self.element_ratio_x = round(ratio.x(), 2)
            self.element_ratio_y = round(ratio.y(), 2)
            self.UI.element_ratio.setText(ratio_str)

    def _handle_confirm(self):
        # 确认操作：添加场景后关闭对话框
        if self.UI.element_id_LineEdit.text():  # 简单校验：确保场景ID不为空
            if self.UI.element_type_ComboBox.currentIndex() == ElementType.IMG.value:
                if self.element_img_path:
                    bgra, gray, mask = split_gray_alpha(self.element_img_path)
                    self.resource_manager.add_element_to_scene(
                        scene_name=self.scene.name,
                        element_name=self.UI.element_id_LineEdit.text(),
                        symbol=self.UI.is_symbol.isChecked(),
                        type=self.UI.element_type_ComboBox.currentIndex(),
                        threshold=self.UI.element_threshold_DoubleSpinBox_2.value(),
                        match_type=self.UI.element_match_type_ComboBox_2.currentIndex(),
                        ratio_x=self.element_ratio_x,
                        ratio_y=self.element_ratio_y,
                        bgra=bgra,
                        gray=gray,
                        mask=mask
                    )
                else:
                    self.resource_manager.add_element_to_scene(
                        scene_name=self.scene.name,
                        element_name=self.UI.element_id_LineEdit.text(),
                        symbol=self.UI.is_symbol.isChecked(),
                        type=self.UI.element_type_ComboBox.currentIndex(),
                        threshold=self.UI.element_threshold_DoubleSpinBox_2.value(),
                        match_type=self.UI.element_match_type_ComboBox_2.currentIndex(),
                        ratio_x=self.element_ratio_x,
                        ratio_y=self.element_ratio_y
                    )
            else:
                self.resource_manager.add_element_to_scene(
                    scene_name=self.scene.name,
                    element_name=self.UI.element_id_LineEdit.text(),
                    symbol=False,
                    type=self.UI.element_type_ComboBox.currentIndex()
                )

            self.accept()  # 关闭对话框，返回QDialog.Accepted
        else:
            self.logger.warning("场景ID不能为空")

    def _handle_cancel(self):
        # 取消操作：直接关闭对话框
        self.reject()  # 关闭对话框，返回QDialog.Rejected

    def _handle_symbol(self, flag):
        if flag:
            self.UI.element_id_LineEdit.setText("标志")
            self.UI.element_type_ComboBox.setCurrentIndex(ElementType.IMG.value)
            self.UI.element_type_ComboBox.setEnabled(False)
        else:
            self.UI.element_type_ComboBox.setEnabled(True)
