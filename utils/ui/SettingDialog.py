from typing import Dict, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
                               QFormLayout, QLineEdit, QSpinBox, QCheckBox,
                               QPushButton, QWidget)

from utils.Base.Setting import Setting

form_style = """
QWidget {
    background-color: #dfdfdf;  /* 背景颜色 */
    /*border-radius:10px;*/
}
/* 调整勾选框的大小 */
QCheckBox::indicator {
width: 20px;      /* 勾选框宽度 */
height: 20px;     /* 勾选框高度 */
outline:none;
border:none;
}

/* 可选：设置勾选框不同状态的样式 */
QCheckBox::indicator:unchecked {
border: 2px solid #0f322f;
border-radius: 3px;
}
QCheckBox::indicator:checked {
background-color:#39C5BB;
border: 2px solid #0f322f;
border-radius: 3px;

}

/* 禁用状态 */
QCheckBox::indicator:disabled {
background-color: #f0f0f0;
border-color: #cccccc;
}
/* 1. 未选中（默认）状态的下边框 */
QLineEdit {
/* 清除默认边框，只保留下边框 */
font-size:11pt;
border: none;
border-bottom: 3px solid #969696;  /* 灰色下边框 */
padding: 5px 0;  /* 上下下内边距，避免文字紧贴紧贴边框 */
border-radius:0px;
background: transparent;  /* 背景透明，只显示下边框 */
}
            
            /* 2. 选中（获得焦点点）状态的下边框 */
QLineEdit:focus {
                border-bottom: 4px solid #39C5BB;  /* 蓝色下边框（突出显示） */
                outline: none;  /* 去除系统默认的聚焦外边框 */
            }
            
            /* 3. 鼠标略过（悬停）状态的下边框 */
QLineEdit:hover {
                border-bottom: 4px solid #39C5BB;  /* 深灰色下边框（中间状态） */
            }
/* QComboBox 样式 */
QComboBox {
    border: 2px solid #0f322f;  /* 边框颜色与CheckBox保持一致 */
    border-radius: 3px;
    padding: 5px 0px 5px 10px;  /* 右侧预留空间给自定义箭头 */
    background-color: #e7e7e7;
    min-height: 20px;
}

/* 隐藏QComboBox默认下拉按钮 */
QComboBox::drop-down {
    border: none;  /* 去除默认按钮边框 */

}

/* 自定义下拉箭头（使用三角形字符模拟） */
QComboBox::down-arrow {
    image: none;  /* 去除默认箭头 */
}

QComboBox::down-arrow:on {
    image: none;  /* 下拉状态也不显示默认箭头 */
}

/* 下拉列表样式 */
QComboBox QAbstractItemView {
    border: 2px solid #b5b5b5;
    border-radius: 3px;
    background-color: #e7e7e7;
    padding: 5px;
    selection-background-color: #39C5BB;  /* 选中项背景色 */
    selection-color: #000000;
}

/* 悬停和选中状态 */
QComboBox:hover {
    border-color: #39C5BB;
}

QComboBox:focus {
    border-color: #39C5BB;
    outline: none;
}

/* QSpinBox 样式 */
QSpinBox {
    border: 2px solid #0f322f;
    border-radius: 3px;
    padding: 5px 10px 5px 10px;  /* 右侧预留空间给自定义按钮 */
    background-color: #e7e7e7;
    min-height: 20px;
}

/* 隐藏QSpinBox默认上下按钮 */
QSpinBox::up-button, QSpinBox::down-button {
    border: none;
    width: 0;  /* 隐藏默认按钮 */
    height: 0;
}



/* 悬停和选中状态 */
QSpinBox:hover {
    border-color: #39C5BB;
}

QSpinBox:focus {
    border-color: #39C5BB;
    outline: none;
}

/* 解决QSpinBox编辑区域与整体样式冲突 */
QSpinBox::edit-focus {
    background-color: transparent;
    border: none;
    outline: none;
}

QPushButton{
min-height: 26px;
border: 1px solid #0f322f;  /* 2px宽的深灰色实线边框 */
background-color: #e7e7e7;
border-radius:3px;
outline:none;
color:#0f322f;
padding-top:2px;
padding-bottom:2px;
}
QPushButton::hover {
border: 1px solid #39C5BB;  /* 2px宽的深灰色实线边框 */
color:#39C5BB;
}

"""


class SettingDialog(QDialog):
    """配置修改对话框，自动根据Setting中的配置项生成UI"""

    def __init__(self, parent: QWidget, logger, setting: Setting):
        super().__init__(parent)
        self.logger = logger.getChild(self.__class__.__name__)
        self.setting = setting  # 保存Setting实例引用
        self.widget_mapping: Dict[Tuple[str, str], QWidget] = {}  # 存储(section, key)与控件的映射

        self.setWindowTitle("设置")
        self.resize(600, 500)
        self._init_ui()

    def _init_ui(self):
        """初始化UI布局和控件"""
        self.setStyleSheet(form_style)
        main_layout = QVBoxLayout(self)

        # 生成配置项UI
        self._create_config_widgets(main_layout)

        # 添加按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        # 确认按钮
        ok_btn = QPushButton("确认")
        ok_btn.clicked.connect(self.accept)

        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)

        # 重置按钮
        reset_btn = QPushButton("重置为默认值")
        reset_btn.clicked.connect(self._reset_to_default)

        btn_layout.addWidget(reset_btn)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def _create_config_widgets(self, parent_layout: QVBoxLayout):
        """根据配置项创建UI控件"""
        # 获取所有配置节
        sections = self.setting.config.sections()

        for section in sections:
            # 为每个配置节创建分组框
            group_box = QGroupBox(section)
            form_layout = QFormLayout()
            form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
            form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            # 获取当前节的所有配置项
            options = self.setting.config.items(section)

            for key, value in options:
                # 根据值类型创建对应的控件
                widget = self._create_widget_based_on_type(section, key, value)
                if widget:
                    form_layout.addRow(f"{key}:", widget)
                    self.widget_mapping[(section, key)] = widget

            group_box.setLayout(form_layout)
            parent_layout.addWidget(group_box)

        parent_layout.addStretch()

    def _create_widget_based_on_type(self, section: str, key: str, value: str) -> QWidget:
        """根据值的类型创建对应的输入控件"""
        # 尝试判断值类型
        if value.lower() in ("true", "false"):
            # 布尔类型 - 使用复选框
            widget = QCheckBox()
            widget.setChecked(value.lower() == "true")
            widget.toggled.connect(
                lambda checked, s=section, k=key: self._on_bool_changed(s, k, checked)
            )
            return widget

        try:
            # 整数类型 - 使用SpinBox
            int_val = int(value)
            widget = QSpinBox()
            widget.setRange(-2147483647, 2147483647)
            widget.setValue(int_val)
            widget.valueChanged.connect(
                lambda val, s=section, k=key: self._on_int_changed(s, k, val)
            )
            return widget
        except ValueError:
            pass

        # 默认视为字符串类型 - 使用LineEdit
        widget = QLineEdit(value)
        widget.textChanged.connect(
            lambda text, s=section, k=key: self._on_str_changed(s, k, text)
        )
        return widget

    def _on_str_changed(self, section: str, key: str, value: str):
        """字符串类型配置项变化处理"""
        self.setting.set(section, key, value)
        self.logger.debug(f"更新配置 [{section}] {key} = {value}")

    def _on_int_changed(self, section: str, key: str, value: int):
        """整数类型配置项变化处理"""
        self.setting.set(section, key, value)
        self.logger.debug(f"更新配置 [{section}] {key} = {value}")

    def _on_bool_changed(self, section: str, key: str, value: bool):
        """布尔类型配置项变化处理"""
        self.setting.set(section, key, str(value).lower())
        self.logger.debug(f"更新配置 [{section}] {key} = {value}")

    def _reset_to_default(self):
        """重置所有配置为默认值"""
        # 重新加载并合并配置（会覆盖用户配置）
        self.setting.load_and_merge_config()
        self.setting.save_to_file()

        # 更新UI显示
        self._update_widgets_from_config()
        self.logger.info("已重置所有配置为默认值")

    def _update_widgets_from_config(self):
        """从配置更新控件显示"""
        for (section, key), widget in self.widget_mapping.items():
            value = self.setting.get(section, key)
            if isinstance(widget, QLineEdit):
                widget.setText(value)
            elif isinstance(widget, QSpinBox):
                try:
                    widget.setValue(int(value))
                except ValueError:
                    self.logger.warning(f"无法将 [{section}] {key} 的值 {value} 转换为整数")
            elif isinstance(widget, QCheckBox):
                widget.setChecked(value.lower() == "true")

    def accept(self) -> None:
        """确认按钮处理"""
        self.logger.info("配置修改已确认")
        super().accept()

    def reject(self) -> None:
        """取消按钮处理 - 恢复修改前的配置"""
        self.logger.info("配置修改已取消")
        self._update_widgets_from_config()  # 恢复UI显示
        super().reject()
