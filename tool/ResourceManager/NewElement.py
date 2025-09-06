import logging
from pathlib import Path

from PySide6.QtCore import QPointF, Qt, QSize
from PySide6.QtGui import QPixmap, QMouseEvent
from PySide6.QtWidgets import QTreeView, QDialog, QVBoxLayout, QLabel, QMessageBox, QDialogButtonBox, \
    QFileDialog

from StaticFunctions import split_gray_alpha, element_to_qpixmap
from tool.ResourceManager.ResourceDBManager import ResourceDBManager
from tool.ResourceManager.model import Scene, Element
from ui.NewElement_ui import Ui_NewElement


class RatioDialog(QDialog):
    def __init__(self, image: Path | Element, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置比例")
        self.setMinimumSize(400, 400)
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
        """处理图片点击事件"""
        # 获取点击位置相对于QLabel的位置
        label_pos = event.position()

        # 获取图片在QLabel中的实际位置和大小
        pixmap = self.image_label.pixmap()
        if pixmap is None:
            return

        # 计算缩放比例
        label_size = self.image_label.size()
        pixmap_size = pixmap.size()

        scale_x = pixmap_size.width() / label_size.width()
        scale_y = pixmap_size.height() / label_size.height()

        # 计算点击位置在原始图片中的位置
        if scale_x > scale_y:
            # 宽度方向填满
            scaled_height = pixmap_size.height() / scale_x
            y_offset = (label_size.height() - scaled_height) / 2
            pix_x = label_pos.x() * scale_x
            pix_y = (label_pos.y() - y_offset) * scale_x
        else:
            # 高度方向填满
            scaled_width = pixmap_size.width() / scale_y
            x_offset = (label_size.width() - scaled_width) / 2
            pix_x = (label_pos.x() - x_offset) * scale_y
            pix_y = label_pos.y() * scale_y

        # 确保在图片范围内
        pix_x = max(0.0, min(pix_x, pixmap_size.width()))
        pix_y = max(0.0, min(pix_y, pixmap_size.height()))

        # 计算比例 (相对于图片尺寸)
        self.ratio_point = QPointF(
            round(pix_x / pixmap_size.width(), 2),
            round(pix_y / pixmap_size.height(), 2)
        )

        # 更新信息
        self.info_label.setText(
            f"已选择: ({self.ratio_point.x():.4f}, {self.ratio_point.y():.4f})\n"
            "点击确定保存比例"
        )

    def get_ratio(self) -> QPointF:
        """获取选择的比例"""
        return self.ratio_point


class NewElement(QDialog):
    def __init__(self, scene: Scene, resource_manager: ResourceDBManager, tree: QTreeView):
        super().__init__()
        self.UI = Ui_NewElement()
        self.UI.setupUi(self)
        self.logger = logging.getLogger("新建元素")
        self.scene = scene
        self.resource_manager = resource_manager
        self.tree = tree

        self.element_img_path: Path | None = None
        self.element_ratio_x = 0.5
        self.element_ratio_y = 0.5

        self.bind_signals()

    def bind_signals(self):
        self.UI.set_img_btn.clicked.connect(self._handle_set_img_btn_clicked)
        self.UI.set_ratio_btn.clicked.connect(self._handle_set_ratio_btn_clicked)

        self.UI.confirm.clicked.connect(self._handle_confirm)
        self.UI.cancel.clicked.connect(self._handle_cancel)

    def _handle_set_img_btn_clicked(self):
        """选择元素图片并添加"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, f"选择【{self.UI.element_id_LineEdit.text()}】图片", "", "PNG图片 (*.png)"
        )
        if file_path:
            try:
                self.logger.debug(file_path)
                self.element_img_path = Path(file_path)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加【{self.UI.element_id_LineEdit.text()}】图片失败: {str(e)}")

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
            if self.element_img_path:
                bgra, gray, mask = split_gray_alpha(self.element_img_path)
                self.resource_manager.add_element_to_scene(
                    scene_name=self.scene.name,
                    element_name=self.UI.element_id_LineEdit.text(),
                    type=self.UI.element_type_ComboBox.currentIndex(),
                    threshold=self.UI.element_threshold_DoubleSpinBox_2.value(),
                    match_type=self.UI.element_match_type_ComboBox_2.currentIndex(),
                    ratio_x=self.element_ratio_x,
                    ratio_y=self.element_ratio_y,
                    bgra=bgra,
                    gray=gray,
                    mask=mask,
                    width=gray.shape[1],
                    height=gray.shape[0],
                    channels=bgra.shape[-1]
                )
            else:
                self.resource_manager.add_element_to_scene(
                    scene_name=self.scene.name,
                    element_name=self.UI.element_id_LineEdit.text(),
                    type=self.UI.element_type_ComboBox.currentIndex(),
                    threshold=self.UI.element_threshold_DoubleSpinBox_2.value(),
                    match_type=self.UI.element_match_type_ComboBox_2.currentIndex(),
                    ratio_x=self.element_ratio_x,
                    ratio_y=self.element_ratio_y
                )

            self.accept()  # 关闭对话框，返回QDialog.Accepted
        else:
            self.logger.warning("场景ID不能为空")

    def _handle_cancel(self):
        # 取消操作：直接关闭对话框
        self.reject()  # 关闭对话框，返回QDialog.Rejected
