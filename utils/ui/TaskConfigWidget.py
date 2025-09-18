from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea,
    QWidget as QScrollAreaWidgetContents, QLabel, QCheckBox, QLineEdit,
    QSpinBox, QComboBox, QSpacerItem, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, QObject
from typing import Dict, Any, Optional

card_style = """
QWidget {
    background-color: #dfdfdf;  /* 卡片背景色 */
    border-radius: 10px;
}

/* 勾选框样式 */
QCheckBox::indicator {
    width: 20px;
    height: 20px;
    outline: none;
    border: none;
}

QCheckBox::indicator:unchecked {
    border: 2px solid #0f322f;
    border-radius: 3px;
}

QCheckBox::indicator:checked {
    background-color: #39C5BB;
    border: 2px solid #0f322f;
    border-radius: 3px;
}

QCheckBox::indicator:disabled {
    background-color: #f0f0f0;
    border-color: #cccccc;
}

/* 输入框样式 */
QLineEdit {
    border: none;
    border-bottom: 3px solid #969696;
    padding: 5px 0;
    border-radius: 0px;
    background: transparent;
}

QLineEdit:focus {
    border-bottom: 4px solid #39C5BB;
    outline: none;
}

QLineEdit:hover {
    border-bottom: 4px solid #39C5BB;
}

/* 下拉框样式 */
QComboBox {
    border: 2px solid #0f322f;
    border-radius: 3px;
    padding: 5px 0px 5px 10px;
    background-color: #e7e7e7;
    min-height: 20px;
    min-width: 100px;
}

QComboBox::drop-down {
    border: none;
}

QComboBox::down-arrow,
QComboBox::down-arrow:on {
    image: none;
}

QComboBox QAbstractItemView {
    border: 2px solid #b5b5b5;
    border-radius: 3px;
    background-color: #e7e7e7;
    padding: 5px;
    selection-background-color: #39C5BB;
    selection-color: #000000;
}

QComboBox:hover,
QComboBox:focus {
    border-color: #39C5BB;
    outline: none;
}

/* 数字输入框样式 */
QSpinBox {
    border: 2px solid #0f322f;
    border-radius: 3px;
    padding: 5px 10px 5px 10px;
    background-color: #e7e7e7;
    min-height: 20px;
}

QSpinBox::up-button,
QSpinBox::down-button {
    border: none;
    width: 0;
    height: 0;
}

QSpinBox:hover,
QSpinBox:focus {
    border-color: #39C5BB;
    outline: none;
}

QSpinBox::edit-focus {
    background-color: transparent;
    border: none;
    outline: none;
}

/* 按钮样式 */
QPushButton {
    min-height: 26px;
    border: 2px solid #0f322f;
    background-color: #e7e7e7;
    border-radius: 3px;
    outline: none;
    color: #0f322f;
    padding-top: 2px;
    padding-bottom: 2px;
}

QPushButton::hover {
    border: 2px solid #39C5BB;
    color: #39C5BB;
}
"""
title_style = """
font-size:18pt;
border:none;
margin:7px;
"""
sub_title_style = """
font-size:13pt;
color:rgba(255, 0, 0, 100);
margin-left:9px;
"""
divider_style = """
QFrame{
border:2px solid #969696;
border-radius:1px;
}
"""


class TaskConfigWidget(QWidget):
    """
    任务配置UI抽象类（PySide6版本）：
    - 第一张卡片：基础设置（是否启用、下次执行时间）
    - 第二张卡片：所有执行参数（无论数量多少都在同一张卡片内）
    """

    def __init__(self, task_name, task_info: Dict[str, Any], parent: Optional[QObject] = None):
        super().__init__(parent)
        self.task_name = task_name
        self.task_info = task_info
        self.exec_params = self.task_info.get("执行参数", {})  # 提取执行参数
        self.task_widget_dic = {
            "执行参数": self.exec_params
        }
        # 初始化主布局（滚动区域）
        self._init_main_scroll_layout()
        # 生成基础设置卡片
        self._create_basic_setting_card()
        # 生成执行参数卡片（包含所有执行参数）
        self._create_exec_param_card()
        # 预留样式接口
        self._init_style_placeholder()

    def _init_main_scroll_layout(self) -> None:
        """初始化主布局：滚动区域包裹内容"""
        # 根布局
        self.root_layout = QHBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        # 中间容器Widget
        self.mid_widget = QWidget()
        self.mid_layout = QHBoxLayout(self.mid_widget)
        self.mid_layout.setContentsMargins(-1, 0, -1, 0)
        self.mid_layout.setStretch(0, 5)
        # 滚动区域
        self.scroll_area = QScrollArea(self.mid_widget)
        self.scroll_area.setMinimumSize(600, 0)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(
            Qt.AlignmentFlag.AlignLeading | Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        # 滚动区域内容容器
        self.scroll_content = QScrollAreaWidgetContents()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(20)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 设置顶部对齐
        # 组装滚动区域
        self.scroll_area.setWidget(self.scroll_content)
        self.mid_layout.addWidget(self.scroll_area)
        self.root_layout.addWidget(self.mid_widget)

    def _create_basic_setting_card(self) -> None:
        """创建基础设置卡片：包含是否启用和下次执行时间"""
        # 基础设置卡片容器
        self.basic_card = QWidget(self.scroll_content)
        self.basic_layout = QVBoxLayout(self.basic_card)
        self.basic_layout.setContentsMargins(-1, 7, -1, -1)

        # 卡片标题
        self.basic_title = QLabel(self.basic_card)
        self.basic_title.setText(f"{self.task_name} | 任务设置")
        self.basic_title.setStyleSheet(title_style)
        self.basic_layout.addWidget(self.basic_title)

        # 标题下方分割线
        self.basic_divider = QFrame(self.basic_card)
        self.basic_divider.setFrameShape(QFrame.Shape.HLine)
        self.basic_divider.setFrameShadow(QFrame.Shadow.Raised)
        self.basic_divider.setStyleSheet(divider_style)
        self.basic_layout.addWidget(self.basic_divider)

        if self.task_info.get("描述", ""):
            # 卡片标题
            self.basic_sub_title = QLabel(self.basic_card)
            self.basic_sub_title.setText(self.task_info.get("描述", ""))
            self.basic_sub_title.setStyleSheet(sub_title_style)
            self.basic_layout.addWidget(self.basic_sub_title)

        # 基础设置网格布局
        self.basic_grid = QGridLayout()
        self.basic_grid.setContentsMargins(10, 10, 0, 10)
        self.basic_grid.setColumnStretch(0, 5)
        self.basic_grid.setColumnStretch(1, 2)

        # 「是否启用」选项
        self.enable_label_widget = QWidget(self.basic_card)
        self.enable_label_layout = QVBoxLayout(self.enable_label_widget)
        self.enable_label_layout.setContentsMargins(0, 0, 0, 0)

        self.enable_main_label = QLabel(self.enable_label_widget)
        self.enable_main_label.setText("启用任务")

        self.enable_desc_label = QLabel(self.enable_label_widget)
        self.enable_desc_label.setText("将这个任务加入调度器")
        self.enable_desc_label.setStyleSheet("font-size:11pt;color:#959595;margin-left:18px;")

        self.enable_label_layout.addWidget(self.enable_main_label)
        self.enable_label_layout.addWidget(self.enable_desc_label)

        self.enable_checkbox = QCheckBox(self.basic_card)
        self.enable_checkbox.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.task_widget_dic["是否启用"] = self.enable_checkbox

        self.basic_grid.addWidget(self.enable_label_widget, 0, 0, 1, 1)
        self.basic_grid.addWidget(
            self.enable_checkbox, 0, 1, 1, 1,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )

        # 「下次执行时间」选项
        self.time_label_widget = QWidget(self.basic_card)
        self.time_label_layout = QVBoxLayout(self.time_label_widget)
        self.time_label_layout.setContentsMargins(0, 0, 0, 0)

        self.time_main_label = QLabel(self.time_label_widget)
        self.time_main_label.setText("下次执行时间")

        self.time_desc_label = QLabel(self.time_label_widget)
        self.time_desc_label.setText("自动计算得出，无须修改，如果想立刻运行任务请清空并回车")
        self.time_desc_label.setStyleSheet("font-size:11pt;color:#959595;margin-left:18px;")

        self.time_label_layout.addWidget(self.time_main_label)
        self.time_label_layout.addWidget(self.time_desc_label)

        self.time_lineedit = QLineEdit(self.basic_card)
        self.time_lineedit.setMinimumSize(200, 0)
        self.time_lineedit.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.time_lineedit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.task_widget_dic["下次执行时间"] = self.time_lineedit

        self.basic_grid.addWidget(self.time_label_widget, 1, 0, 1, 1)
        self.basic_grid.addWidget(self.time_lineedit, 1, 1, 1, 1)

        # 添加网格布局到卡片
        self.basic_layout.addLayout(self.basic_grid)
        # 将卡片添加到滚动区域
        self.scroll_layout.addWidget(self.basic_card)

    def _create_exec_param_card(self) -> None:
        """创建执行参数卡片：包含所有执行参数（无论数量多少）"""
        if not self.exec_params:  # 没有执行参数则不创建此卡片
            return

        # 执行参数卡片容器
        self.param_card = QWidget(self.scroll_content)
        self.param_layout = QVBoxLayout(self.param_card)
        self.param_layout.setContentsMargins(-1, 7, -1, -1)

        # 卡片标题
        self.param_title = QLabel(self.param_card)
        self.param_title.setText(self.task_name)
        self.param_title.setStyleSheet(title_style)
        self.param_layout.addWidget(self.param_title)

        # 标题下方分割线
        self.param_divider = QFrame(self.param_card)
        self.param_divider.setFrameShape(QFrame.Shape.HLine)
        self.param_divider.setFrameShadow(QFrame.Shadow.Raised)
        self.param_divider.setStyleSheet(divider_style)
        self.param_layout.addWidget(self.param_divider)

        # 执行参数网格布局（所有参数都放在这个布局中）
        self.param_grid = QGridLayout()
        self.param_grid.setVerticalSpacing(15)  # 参数之间的垂直间距
        self.param_grid.setContentsMargins(10, 10, 0, 10)
        self.param_grid.setColumnStretch(0, 5)
        self.param_grid.setColumnStretch(1, 2)

        # 遍历所有执行参数，动态生成行
        for row_idx, (param_name, param_detail) in enumerate(self.exec_params.items()):
            # 参数标签容器
            self.param_label_widget = QWidget(self.param_card)
            self.param_label_layout = QVBoxLayout(self.param_label_widget)
            self.param_label_layout.setContentsMargins(0, 0, 0, 0)

            # 主标签
            self.param_main_label = QLabel(self.param_label_widget)
            self.param_main_label.setText(param_name)

            # 描述标签
            self.param_desc_label = QLabel(self.param_label_widget)
            self.param_desc_label.setText(param_detail.get("描述", ""))
            self.param_desc_label.setStyleSheet("font-size:11pt;color:#959595;margin-left:18px;")
            self.param_desc_label.setWordWrap(True)

            self.param_label_layout.addWidget(self.param_main_label)
            self.param_label_layout.addWidget(self.param_desc_label)

            # 根据类型创建对应控件
            param_type = param_detail.get("类型", "").upper()
            if param_type == "INT":
                self.param_widget = QSpinBox(self.param_card)
                self.param_widget.setMaximumSize(80, 35)
                self.param_widget.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
                # 设置范围
                min_val = param_detail.get("最小值", 0)
                max_val = param_detail.get("最大值", 100)
                self.param_widget.setMinimum(min_val)
                self.param_widget.setMaximum(max_val)
                self.param_widget.setValue(min_val)

            elif param_type == "COMBOX":
                self.param_widget = QComboBox(self.param_card)
                self.param_widget.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
                # 添加选项
                enum_list = param_detail.get("枚举列表", [])
                self.param_widget.addItems(enum_list)
                if enum_list:
                    self.param_widget.setCurrentIndex(0)

            else:
                self.param_widget = QLabel(self.param_card)
                self.param_widget.setText(f"不支持的参数类型：{param_type}")
                self.param_widget.setStyleSheet("color:red;")
            self.task_widget_dic["执行参数"][param_name]["控件"] = self.param_widget
            # 添加到网格布局
            self.param_grid.addWidget(self.param_label_widget, row_idx, 0, 1, 1)
            self.param_grid.addWidget(
                self.param_widget, row_idx, 1, 1, 1,
                Qt.AlignmentFlag.AlignHCenter
            )

        # 添加网格布局到卡片
        self.param_layout.addLayout(self.param_grid)
        # 将卡片添加到滚动区域
        self.scroll_layout.addWidget(self.param_card)

    def _init_style_placeholder(self) -> None:
        """样式预留接口"""
        self.basic_card.setStyleSheet(card_style)
        if getattr(self, 'param_card', None):
            self.param_card.setStyleSheet(card_style)

    def get_widget(self) -> QWidget:
        """获取当前Widget，用于添加到stackedWidget"""
        return self


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # 示例任务配置
    sample_task_info = {
        "优先级": 0,
        "临时提权": False,
        "描述": "自动购买体力以保证日常任务完成",
        "执行参数": {
            "购买体力次数": {
                "描述": "设置每天购买体力的次数",
                "类型": "INT",
                "最小值": 0,
                "最大值": 100,
            },
            "购买体力方式": {
                "描述": "选择购买体力的方式",
                "类型": "COMBOX",
                "枚举列表": ["金币", "钻石", "忍币"]
            }
        },
        "下次执行时间": 0
    }

    widget = TaskConfigWidget("购买体力", sample_task_info)
    for key, value in widget.task_widget_dic["执行参数"].items():
        print(key, ":", value)
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
