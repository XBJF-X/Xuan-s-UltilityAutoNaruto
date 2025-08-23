import logging
import sys

import cv2
from PIL.ImageQt import QPixmap
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QCursor, QPainter, QColor, QPen, QImage
from PySide6.QtWidgets import QDialog, QApplication, QWidget

from utils.ui.KeyMapConfiguration_ui import Ui_KeyMapConfiguration
from utils.Base.Config import Config


class SkillButton(QWidget):
    """技能按钮控件，可拖动"""

    def __init__(self, skill_id: int, parent=None):
        super().__init__(parent)
        self.skill_id = skill_id  # 技能ID，用于标识不同技能
        self.setFixedSize(50, 50)  # 固定大小
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))  # 鼠标悬停时显示手型
        self.dragging = False
        self.offset = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            # 使用新的position()方法替代pos()，并转换为QPoint
            self.offset = event.position().toPoint()  # 记录鼠标相对于控件的位置
            self.raise_()  # 置于顶层
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            # 获取鼠标在屏幕中的全局位置
            global_pos = event.globalPosition().toPoint()
            # 将父控件的左上角转换为全局坐标
            parent_global_pos = self.parent().mapToGlobal(QPoint(0, 0))
            # 计算鼠标在父控件中的相对位置（减去偏移量）
            new_pos = global_pos - parent_global_pos - self.offset

            # 限制在父控件范围内
            new_pos.setX(max(0, min(new_pos.x(), self.parent().width() - self.width())))
            new_pos.setY(max(0, min(new_pos.y(), self.parent().height() - self.height())))
            self.move(new_pos)
        super().mouseMoveEvent(event)

    def paintEvent(self, event):
        # 绘制圆形按钮
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 抗锯齿

        # 绘制圆形背景
        painter.setBrush(QColor(50, 150, 255, 150))  # 半透明蓝色
        painter.setPen(QPen(QColor(255, 255, 255), 2))  # 白色边框
        painter.drawEllipse(2, 2, self.width() - 4, self.height() - 4)

        # 创建并设置字体 - 关键修改
        font = painter.font()
        # 根据按钮大小动态计算字体大小
        font_size = int(min(self.width(), self.height()) * 0.4)  # 占按钮大小的40%
        font.setPointSize(font_size)
        font.setBold(True)  # 加粗
        painter.setFont(font)

        # 绘制技能ID
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, str(self.skill_id + 1))


class KeyMapConfiguration(QDialog):
    def __init__(self, config: Config, screen, parent_logger, parent=None):
        super().__init__(parent)
        self.UI = Ui_KeyMapConfiguration()
        self.UI.setupUi(self)
        self.config = config
        self.logger = parent_logger.getChild(self.__class__.__name__)
        self.skill_buttons = []  # 存储所有技能按钮
        self.result_positions = [[] for _ in range(10)]
        self.setModal(True)

        # 将BGR转换为RGB
        rgb_image = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
        # 获取图像尺寸和通道数
        height, width, channel = rgb_image.shape
        self.screen_size = [width, height]
        bytes_per_line = channel * width
        # 创建QImage
        q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        self.UI.image_label.setPixmap(QPixmap.fromImage(q_image))
        # 设置标签大小
        self.UI.image_label.setFixedSize(width, height)
        # 设置容器大小与图片一致
        self.UI.image_container.setFixedSize(width, height)
        # 添加技能按钮
        for i in range(10):
            skill_btn = SkillButton(i, self.UI.image_container)
            x, y = self.config.get_config("键位")[i]
            real_x = x * self.screen_size[0] / 1600 - skill_btn.width() / 2
            real_y = y * self.screen_size[1] / 900 - skill_btn.height() / 2
            skill_btn.move(real_x, real_y)
            skill_btn.show()
            self.skill_buttons.append(skill_btn)
        self.UI.finish.clicked.connect(self._on_finish)
        # 调整窗口初始大小为屏幕的80%
        screen_geometry = QApplication.primaryScreen().geometry()
        self.resize(int(screen_geometry.width() * 0.7), int(screen_geometry.height() * 0.7))

    def _on_finish(self):
        """确认按钮点击事件，收集所有技能按钮位置"""
        for btn in self.skill_buttons:
            # 获取按钮在图片容器中的相对位置
            pos = btn.pos()
            x = int((pos.x() * 1600 / self.screen_size[0]) + btn.width() / 2)
            y = int((pos.y() * 900 / self.screen_size[1]) + btn.height() / 2)
            self.result_positions[btn.skill_id] = [x, y]

        self.config.set_config("键位", self.result_positions)
        # 关闭对话框
        self.accept()


if __name__ == "__main__":
    # 3. 创建应用实例
    app = QApplication(sys.argv)

    # 4. 设置高DPI缩放策略（可选）
    # 在PySide6 6.4+版本中，这步可能不需要
    # app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    img = cv2.imread("2025-08-02_20-06-59.742203.png", cv2.IMREAD_UNCHANGED)
    daily_quests_helper = KeyMapConfiguration(Config(), img, None)
    daily_quests_helper.show()
    sys.exit(app.exec())
