# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SceneEditor.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QDialog, QDoubleSpinBox, QFormLayout, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QStackedWidget, QTreeView, QVBoxLayout,
    QWidget)

class Ui_SceneEditor(object):
    def setupUi(self, SceneEditor):
        if not SceneEditor.objectName():
            SceneEditor.setObjectName(u"SceneEditor")
        SceneEditor.resize(1448, 855)
        SceneEditor.setStyleSheet(u"font-family:\"Consolas\",\"\u9ed1\u4f53\";\n"
"font-size:11pt;")
        self.horizontalLayout = QHBoxLayout(SceneEditor)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.image_container = QWidget(SceneEditor)
        self.image_container.setObjectName(u"image_container")
        self.image_container.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"border-radius:10px;\n"
"            }")
        self.verticalLayout_4 = QVBoxLayout(self.image_container)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")

        self.horizontalLayout.addWidget(self.image_container)

        self.widget_2 = QWidget(SceneEditor)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setMinimumSize(QSize(300, 0))
        self.widget_2.setStyleSheet(u"QWidget {\n"
"                background-color: #eeeeee;  /* \u80cc\u666f\u989c\u8272 */\n"
"border-radius:10px;\n"
"            }\n"
"")
        self.verticalLayout = QVBoxLayout(self.widget_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 0)
        self.widget_3 = QWidget(self.widget_2)
        self.widget_3.setObjectName(u"widget_3")
        self.widget_3.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"border-radius:10px;\n"
"font-size:15pt;\n"
"            }\n"
"")
        self.verticalLayout_2 = QVBoxLayout(self.widget_3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.Element_tree = QTreeView(self.widget_3)
        self.Element_tree.setObjectName(u"Element_tree")
        self.Element_tree.setStyleSheet(u"/* \u5782\u76f4\u6eda\u52a8\u6761\u6574\u4f53 */\n"
"        QScrollBar:vertical {\n"
"            background-color: rgb(197, 197, 197);\n"
"            width: 6px;\n"
"            margin: 1px;\n"
"            border-radius: 3px;\n"
"        }\n"
"        QScrollBar::handle:vertical {\n"
"            background-color: #8b8b8b;\n"
"            border-radius: 3px;\n"
"            margin: 3 0px 6 0px;\n"
"            min-height: 30px;\n"
"        }\n"
"        QScrollBar::handle:vertical:hover,\n"
"        QScrollBar::handle:vertical:pressed {\n"
"            background-color: #3c3f41;\n"
"            border-radius: 3px;\n"
"            margin: 0 0px 0 0px;\n"
"        }\n"
"        QScrollBar::sub-line:vertical {\n"
"            border: none;\n"
"            height: 0px;\n"
"        }\n"
"        QScrollBar::add-line:vertical {\n"
"            border: none;\n"
"            height: 0px;\n"
"        }")
        self.Element_tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.Element_tree.header().setVisible(False)

        self.verticalLayout_2.addWidget(self.Element_tree)


        self.verticalLayout.addWidget(self.widget_3)

        self.stackedWidget = QStackedWidget(self.widget_2)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"border-radius:10px;\n"
"            }\n"
"/* \u8c03\u6574\u52fe\u9009\u6846\u7684\u5927\u5c0f */\n"
"QCheckBox::indicator {\n"
"	width: 20px;      /* \u52fe\u9009\u6846\u5bbd\u5ea6 */\n"
"	height: 20px;     /* \u52fe\u9009\u6846\u9ad8\u5ea6 */\n"
"	outline:none;\n"
"border:none;\n"
"}\n"
"\n"
"/* \u53ef\u9009\uff1a\u8bbe\u7f6e\u52fe\u9009\u6846\u4e0d\u540c\u72b6\u6001\u7684\u6837\u5f0f */\n"
"QCheckBox::indicator:unchecked {\n"
"	border: 2px solid #0f322f;\n"
"	border-radius: 3px;\n"
"}\n"
"QCheckBox::indicator:checked {\n"
"	background-color:#39C5BB;\n"
"	border: 2px solid #0f322f;\n"
"	border-radius: 3px;\n"
"	\n"
"}\n"
"\n"
"/* \u7981\u7528\u72b6\u6001 */\n"
"QCheckBox::indicator:disabled {\n"
"	background-color: #f0f0f0;\n"
"	border-color: #cccccc;\n"
"}\n"
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"QLineEdit {\n"
"                /* \u6e05\u9664\u9ed8\u8ba4\u8fb9\u6846"
                        "\uff0c\u53ea\u4fdd\u7559\u4e0b\u8fb9\u6846 */\n"
"				font-size:11pt;\n"
"                border: none;\n"
"                border-bottom: 3px solid #969696;  /* \u7070\u8272\u4e0b\u8fb9\u6846 */\n"
"                padding: 5px 0;  /* \u4e0a\u4e0b\u4e0b\u5185\u8fb9\u8ddd\uff0c\u907f\u514d\u6587\u5b57\u7d27\u8d34\u7d27\u8d34\u8fb9\u6846 */\n"
"				border-radius:0px;\n"
"                background: transparent;  /* \u80cc\u666f\u900f\u660e\uff0c\u53ea\u663e\u793a\u4e0b\u8fb9\u6846 */\n"
"            }\n"
"            \n"
"            /* 2. \u9009\u4e2d\uff08\u83b7\u5f97\u7126\u70b9\u70b9\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"QLineEdit:focus {\n"
"                border-bottom: 4px solid #39C5BB;  /* \u84dd\u8272\u4e0b\u8fb9\u6846\uff08\u7a81\u51fa\u663e\u793a\uff09 */\n"
"                outline: none;  /* \u53bb\u9664\u7cfb\u7edf\u9ed8\u8ba4\u7684\u805a\u7126\u5916\u8fb9\u6846 */\n"
"            }\n"
"            \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684"
                        "\u4e0b\u8fb9\u6846 */\n"
"QLineEdit:hover {\n"
"                border-bottom: 4px solid #39C5BB;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }\n"
"/* QComboBox \u6837\u5f0f */\n"
"QComboBox {\n"
"    border: 2px solid #0f322f;  /* \u8fb9\u6846\u989c\u8272\u4e0eCheckBox\u4fdd\u6301\u4e00\u81f4 */\n"
"    border-radius: 3px;\n"
"    padding: 5px 0px 5px 10px;  /* \u53f3\u4fa7\u9884\u7559\u7a7a\u95f4\u7ed9\u81ea\u5b9a\u4e49\u7bad\u5934 */\n"
"    background-color: #e7e7e7;\n"
"	max-height: 17px;\n"
"    min-height: 15px;\n"
"	max-width:100px;\n"
"}\n"
"\n"
"/* \u9690\u85cfQComboBox\u9ed8\u8ba4\u4e0b\u62c9\u6309\u94ae */\n"
"QComboBox::drop-down {\n"
"    border: none;  /* \u53bb\u9664\u9ed8\u8ba4\u6309\u94ae\u8fb9\u6846 */\n"
"\n"
"}\n"
"\n"
"/* \u81ea\u5b9a\u4e49\u4e0b\u62c9\u7bad\u5934\uff08\u4f7f\u7528\u4e09\u89d2\u5f62\u5b57\u7b26\u6a21\u62df\uff09 */\n"
"QComboBox::down-arrow {\n"
"    image: none;  /* \u53bb\u9664\u9ed8\u8ba4\u7bad\u5934 */\n"
"}\n"
"\n"
""
                        "QComboBox::down-arrow:on {\n"
"    image: none;  /* \u4e0b\u62c9\u72b6\u6001\u4e5f\u4e0d\u663e\u793a\u9ed8\u8ba4\u7bad\u5934 */\n"
"}\n"
"\n"
"/* \u4e0b\u62c9\u5217\u8868\u6837\u5f0f */\n"
"QComboBox QAbstractItemView {\n"
"    border: 2px solid #b5b5b5;\n"
"    border-radius: 3px;\n"
"    background-color: #e7e7e7;\n"
"    padding: 5px;\n"
"    selection-background-color: #39C5BB;  /* \u9009\u4e2d\u9879\u80cc\u666f\u8272 */\n"
"    selection-color: #000000;\n"
"}\n"
"\n"
"/* \u60ac\u505c\u548c\u9009\u4e2d\u72b6\u6001 */\n"
"QComboBox:hover {\n"
"    border-color: #39C5BB;\n"
"}\n"
"\n"
"QComboBox:focus {\n"
"    border-color: #39C5BB;\n"
"    outline: none;\n"
"}\n"
"\n"
"/* QSpinBox \u6837\u5f0f */\n"
"QSpinBox {\n"
"    border: 2px solid #0f322f;\n"
"    border-radius: 3px;\n"
"    padding: 5px 10px 5px 10px;  /* \u53f3\u4fa7\u9884\u7559\u7a7a\u95f4\u7ed9\u81ea\u5b9a\u4e49\u6309\u94ae */\n"
"    background-color: #e7e7e7;\n"
"	max-height: 17px;\n"
"    min-height: 15px;\n"
"	max-width:40px;\n"
"}\n"
"\n"
"/"
                        "* \u9690\u85cfQSpinBox\u9ed8\u8ba4\u4e0a\u4e0b\u6309\u94ae */\n"
"QSpinBox::up-button, QSpinBox::down-button {\n"
"    border: none;\n"
"    width: 0;  /* \u9690\u85cf\u9ed8\u8ba4\u6309\u94ae */\n"
"    height: 0;\n"
"}\n"
"\n"
"\n"
"\n"
"/* \u60ac\u505c\u548c\u9009\u4e2d\u72b6\u6001 */\n"
"QSpinBox:hover {\n"
"    border-color: #39C5BB;\n"
"}\n"
"\n"
"QSpinBox:focus {\n"
"    border-color: #39C5BB;\n"
"    outline: none;\n"
"}\n"
"\n"
"/* \u89e3\u51b3QSpinBox\u7f16\u8f91\u533a\u57df\u4e0e\u6574\u4f53\u6837\u5f0f\u51b2\u7a81 */\n"
"QSpinBox::edit-focus {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    outline: none;\n"
"}\n"
"/* QSpinBox \u6837\u5f0f */\n"
"QDoubleSpinBox {\n"
"    border: 2px solid #0f322f;\n"
"    border-radius: 3px;\n"
"    padding: 5px 10px 5px 10px;  /* \u53f3\u4fa7\u9884\u7559\u7a7a\u95f4\u7ed9\u81ea\u5b9a\u4e49\u6309\u94ae */\n"
"    background-color: #e7e7e7;\n"
"	max-height: 17px;\n"
"    min-height: 15px;\n"
"	max-width:50px;\n"
"}\n"
"\n"
"/* \u9690\u85cfQSpinBo"
                        "x\u9ed8\u8ba4\u4e0a\u4e0b\u6309\u94ae */\n"
"QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {\n"
"    border: none;\n"
"    width: 0;  /* \u9690\u85cf\u9ed8\u8ba4\u6309\u94ae */\n"
"    height: 0;\n"
"}\n"
"\n"
"\n"
"\n"
"/* \u60ac\u505c\u548c\u9009\u4e2d\u72b6\u6001 */\n"
"QDoubleSpinBox:hover {\n"
"    border-color: #39C5BB;\n"
"}\n"
"\n"
"QDoubleSpinBox:focus {\n"
"    border-color: #39C5BB;\n"
"    outline: none;\n"
"}\n"
"\n"
"/* \u89e3\u51b3QSpinBox\u7f16\u8f91\u533a\u57df\u4e0e\u6574\u4f53\u6837\u5f0f\u51b2\u7a81 */\n"
"QDoubleSpinBox::edit-focus {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    outline: none;\n"
"}\n"
"\n"
"QPushButton{\n"
"min-height: 20px;\n"
"max-width:100px;\n"
"border: 2px solid #0f322f;  /* 2px\u5bbd\u7684\u6df1\u7070\u8272\u5b9e\u7ebf\u8fb9\u6846 */\n"
"background-color: #e7e7e7;\n"
"border-radius:3px;\n"
"outline:none;\n"
"color:#0f322f;\n"
"padding-top:2px;\n"
"padding-bottom:2px;\n"
"}\n"
"QPushButton::hover {\n"
"border: 2px solid #39C5BB;  /* 2p"
                        "x\u5bbd\u7684\u6df1\u7070\u8272\u5b9e\u7ebf\u8fb9\u6846 */\n"
"outline:none;\n"
"color:#39C5BB;\n"
"}\n"
"")
        self.SceneEditorPage = QWidget()
        self.SceneEditorPage.setObjectName(u"SceneEditorPage")
        self.verticalLayout_6 = QVBoxLayout(self.SceneEditorPage)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.scene_id_Label = QLabel(self.SceneEditorPage)
        self.scene_id_Label.setObjectName(u"scene_id_Label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.scene_id_Label)

        self.scene_id_edit = QLineEdit(self.SceneEditorPage)
        self.scene_id_edit.setObjectName(u"scene_id_edit")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.scene_id_edit)

        self.scene_thresholdLabel = QLabel(self.SceneEditorPage)
        self.scene_thresholdLabel.setObjectName(u"scene_thresholdLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.scene_thresholdLabel)

        self.scene_threshold = QDoubleSpinBox(self.SceneEditorPage)
        self.scene_threshold.setObjectName(u"scene_threshold")
        self.scene_threshold.setMaximum(1.000000000000000)
        self.scene_threshold.setSingleStep(0.010000000000000)
        self.scene_threshold.setValue(0.800000000000000)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.scene_threshold)

        self.Label = QLabel(self.SceneEditorPage)
        self.Label.setObjectName(u"Label")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.Label)

        self.scene_match_btn = QPushButton(self.SceneEditorPage)
        self.scene_match_btn.setObjectName(u"scene_match_btn")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.scene_match_btn)


        self.verticalLayout_6.addLayout(self.formLayout)

        self.stackedWidget.addWidget(self.SceneEditorPage)
        self.ElementEditorPage = QWidget()
        self.ElementEditorPage.setObjectName(u"ElementEditorPage")
        self.verticalLayout_12 = QVBoxLayout(self.ElementEditorPage)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.element_id_Label = QLabel(self.ElementEditorPage)
        self.element_id_Label.setObjectName(u"element_id_Label")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.element_id_Label)

        self.element_id_edit = QLineEdit(self.ElementEditorPage)
        self.element_id_edit.setObjectName(u"element_id_edit")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.element_id_edit)

        self.element_type_Label = QLabel(self.ElementEditorPage)
        self.element_type_Label.setObjectName(u"element_type_Label")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.element_type_Label)

        self.element_type = QComboBox(self.ElementEditorPage)
        self.element_type.addItem("")
        self.element_type.addItem("")
        self.element_type.setObjectName(u"element_type")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.element_type)

        self.element_image_Widget = QWidget(self.ElementEditorPage)
        self.element_image_Widget.setObjectName(u"element_image_Widget")
        self.verticalLayout_3 = QVBoxLayout(self.element_image_Widget)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.element_image_Widget)


        self.verticalLayout_12.addLayout(self.formLayout_2)

        self.stackedWidget_2 = QStackedWidget(self.ElementEditorPage)
        self.stackedWidget_2.setObjectName(u"stackedWidget_2")
        self.IMG_element_form = QWidget()
        self.IMG_element_form.setObjectName(u"IMG_element_form")
        self.verticalLayout_8 = QVBoxLayout(self.IMG_element_form)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.formLayout_3 = QFormLayout()
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.formLayout_3.setLabelAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formLayout_3.setFormAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)
        self.element_threshold_Label_2 = QLabel(self.IMG_element_form)
        self.element_threshold_Label_2.setObjectName(u"element_threshold_Label_2")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.element_threshold_Label_2)

        self.element_threshold = QDoubleSpinBox(self.IMG_element_form)
        self.element_threshold.setObjectName(u"element_threshold")
        self.element_threshold.setMaximum(1.000000000000000)
        self.element_threshold.setSingleStep(0.010000000000000)
        self.element_threshold.setValue(0.800000000000000)

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.FieldRole, self.element_threshold)

        self.element_match_type_Label_2 = QLabel(self.IMG_element_form)
        self.element_match_type_Label_2.setObjectName(u"element_match_type_Label_2")

        self.formLayout_3.setWidget(2, QFormLayout.ItemRole.LabelRole, self.element_match_type_Label_2)

        self.element_match_type = QComboBox(self.IMG_element_form)
        self.element_match_type.addItem("")
        self.element_match_type.addItem("")
        self.element_match_type.setObjectName(u"element_match_type")

        self.formLayout_3.setWidget(2, QFormLayout.ItemRole.FieldRole, self.element_match_type)

        self.element_image_Label_2 = QLabel(self.IMG_element_form)
        self.element_image_Label_2.setObjectName(u"element_image_Label_2")

        self.formLayout_3.setWidget(5, QFormLayout.ItemRole.LabelRole, self.element_image_Label_2)

        self.widget = QWidget(self.IMG_element_form)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout_4 = QHBoxLayout(self.widget)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.element_set_image_btn = QPushButton(self.widget)
        self.element_set_image_btn.setObjectName(u"element_set_image_btn")

        self.horizontalLayout_4.addWidget(self.element_set_image_btn)

        self.element_split_image_btn = QPushButton(self.widget)
        self.element_split_image_btn.setObjectName(u"element_split_image_btn")

        self.horizontalLayout_4.addWidget(self.element_split_image_btn)


        self.formLayout_3.setWidget(5, QFormLayout.ItemRole.FieldRole, self.widget)

        self.element_ratio_Label = QLabel(self.IMG_element_form)
        self.element_ratio_Label.setObjectName(u"element_ratio_Label")

        self.formLayout_3.setWidget(7, QFormLayout.ItemRole.LabelRole, self.element_ratio_Label)

        self.element_ratio_Widget = QWidget(self.IMG_element_form)
        self.element_ratio_Widget.setObjectName(u"element_ratio_Widget")
        self.verticalLayout_9 = QVBoxLayout(self.element_ratio_Widget)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.element_ratio = QLabel(self.element_ratio_Widget)
        self.element_ratio.setObjectName(u"element_ratio")

        self.verticalLayout_9.addWidget(self.element_ratio)


        self.formLayout_3.setWidget(7, QFormLayout.ItemRole.FieldRole, self.element_ratio_Widget)

        self.ratioLabel = QLabel(self.IMG_element_form)
        self.ratioLabel.setObjectName(u"ratioLabel")

        self.formLayout_3.setWidget(8, QFormLayout.ItemRole.LabelRole, self.ratioLabel)

        self.ratioWidget = QWidget(self.IMG_element_form)
        self.ratioWidget.setObjectName(u"ratioWidget")
        self.verticalLayout_10 = QVBoxLayout(self.ratioWidget)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.set_ratio_btn = QPushButton(self.ratioWidget)
        self.set_ratio_btn.setObjectName(u"set_ratio_btn")

        self.verticalLayout_10.addWidget(self.set_ratio_btn)


        self.formLayout_3.setWidget(8, QFormLayout.ItemRole.FieldRole, self.ratioWidget)

        self.element_ratio_Label_3 = QLabel(self.IMG_element_form)
        self.element_ratio_Label_3.setObjectName(u"element_ratio_Label_3")

        self.formLayout_3.setWidget(9, QFormLayout.ItemRole.LabelRole, self.element_ratio_Label_3)

        self.element_roi = QLabel(self.IMG_element_form)
        self.element_roi.setObjectName(u"element_roi")

        self.formLayout_3.setWidget(9, QFormLayout.ItemRole.FieldRole, self.element_roi)

        self.ratioLabel_3 = QLabel(self.IMG_element_form)
        self.ratioLabel_3.setObjectName(u"ratioLabel_3")

        self.formLayout_3.setWidget(10, QFormLayout.ItemRole.LabelRole, self.ratioLabel_3)

        self.set_roi_btn = QPushButton(self.IMG_element_form)
        self.set_roi_btn.setObjectName(u"set_roi_btn")

        self.formLayout_3.setWidget(10, QFormLayout.ItemRole.FieldRole, self.set_roi_btn)

        self.widget_4 = QWidget(self.IMG_element_form)
        self.widget_4.setObjectName(u"widget_4")
        self.horizontalLayout_6 = QHBoxLayout(self.widget_4)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.element_view_image_btn = QPushButton(self.widget_4)
        self.element_view_image_btn.setObjectName(u"element_view_image_btn")

        self.horizontalLayout_6.addWidget(self.element_view_image_btn)

        self.element_match_btn = QPushButton(self.widget_4)
        self.element_match_btn.setObjectName(u"element_match_btn")

        self.horizontalLayout_6.addWidget(self.element_match_btn)


        self.formLayout_3.setWidget(3, QFormLayout.ItemRole.FieldRole, self.widget_4)

        self.element_image_Label_4 = QLabel(self.IMG_element_form)
        self.element_image_Label_4.setObjectName(u"element_image_Label_4")

        self.formLayout_3.setWidget(3, QFormLayout.ItemRole.LabelRole, self.element_image_Label_4)

        self.is_symbol_Label = QLabel(self.IMG_element_form)
        self.is_symbol_Label.setObjectName(u"is_symbol_Label")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.is_symbol_Label)

        self.is_symbol = QCheckBox(self.IMG_element_form)
        self.is_symbol.setObjectName(u"is_symbol")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.FieldRole, self.is_symbol)


        self.verticalLayout_8.addLayout(self.formLayout_3)

        self.stackedWidget_2.addWidget(self.IMG_element_form)
        self.COORDINATE_element_form = QWidget()
        self.COORDINATE_element_form.setObjectName(u"COORDINATE_element_form")
        self.verticalLayout_11 = QVBoxLayout(self.COORDINATE_element_form)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.formLayout_6 = QFormLayout()
        self.formLayout_6.setObjectName(u"formLayout_6")
        self.formLayout_6.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self.formLayout_6.setLabelAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formLayout_6.setFormAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)
        self.formLayout_6.setHorizontalSpacing(6)
        self.Label_2 = QLabel(self.COORDINATE_element_form)
        self.Label_2.setObjectName(u"Label_2")

        self.formLayout_6.setWidget(0, QFormLayout.ItemRole.LabelRole, self.Label_2)

        self.Widget_2 = QWidget(self.COORDINATE_element_form)
        self.Widget_2.setObjectName(u"Widget_2")
        self.verticalLayout_15 = QVBoxLayout(self.Widget_2)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.element_coordinate = QLabel(self.Widget_2)
        self.element_coordinate.setObjectName(u"element_coordinate")

        self.verticalLayout_15.addWidget(self.element_coordinate)


        self.formLayout_6.setWidget(0, QFormLayout.ItemRole.FieldRole, self.Widget_2)

        self.Label_3 = QLabel(self.COORDINATE_element_form)
        self.Label_3.setObjectName(u"Label_3")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Label_3.sizePolicy().hasHeightForWidth())
        self.Label_3.setSizePolicy(sizePolicy)

        self.formLayout_6.setWidget(1, QFormLayout.ItemRole.LabelRole, self.Label_3)

        self.Widget_3 = QWidget(self.COORDINATE_element_form)
        self.Widget_3.setObjectName(u"Widget_3")
        self.verticalLayout_16 = QVBoxLayout(self.Widget_3)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.set_coordinate_btn = QPushButton(self.Widget_3)
        self.set_coordinate_btn.setObjectName(u"set_coordinate_btn")

        self.verticalLayout_16.addWidget(self.set_coordinate_btn)


        self.formLayout_6.setWidget(1, QFormLayout.ItemRole.FieldRole, self.Widget_3)


        self.verticalLayout_11.addLayout(self.formLayout_6)

        self.stackedWidget_2.addWidget(self.COORDINATE_element_form)

        self.verticalLayout_12.addWidget(self.stackedWidget_2)

        self.stackedWidget.addWidget(self.ElementEditorPage)

        self.verticalLayout.addWidget(self.stackedWidget)

        self.widget_5 = QWidget(self.widget_2)
        self.widget_5.setObjectName(u"widget_5")
        self.widget_5.setStyleSheet(u"QPushButton{\n"
"border: 2px solid #b5b5b5;  /* 2px\u5bbd\u7684\u6df1\u7070\u8272\u5b9e\u7ebf\u8fb9\u6846 */\n"
"background-color: rgb(255, 255, 255);\n"
"border-radius:10px;\n"
"outline:none;\n"
"color:#0f322f;\n"
"font-size:14pt;\n"
"padding-top:2px;\n"
"padding-bottom:2px;\n"
"}\n"
"QPushButton::hover {\n"
"border: 2px solid #39C5BB;  /* 2px\u5bbd\u7684\u6df1\u7070\u8272\u5b9e\u7ebf\u8fb9\u6846 */\n"
"background-color: rgb(255, 255, 255);\n"
"border-radius:10px;\n"
"outline:none;\n"
"padding-top:2px;\n"
"color:#39C5BB;\n"
"padding-bottom:2px;\n"
"}")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, 9, -1, -1)
        self.button_save = QPushButton(self.widget_5)
        self.button_save.setObjectName(u"button_save")
        self.button_save.setMinimumSize(QSize(0, 30))

        self.horizontalLayout_2.addWidget(self.button_save)

        self.button_cancel = QPushButton(self.widget_5)
        self.button_cancel.setObjectName(u"button_cancel")
        self.button_cancel.setMinimumSize(QSize(0, 30))

        self.horizontalLayout_2.addWidget(self.button_cancel)


        self.verticalLayout.addWidget(self.widget_5)

        self.verticalLayout.setStretch(0, 1)

        self.horizontalLayout.addWidget(self.widget_2)

        self.horizontalLayout.setStretch(0, 6)
        self.horizontalLayout.setStretch(1, 2)

        self.retranslateUi(SceneEditor)
        self.element_type.currentIndexChanged.connect(self.stackedWidget_2.setCurrentIndex)

        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget_2.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(SceneEditor)
    # setupUi

    def retranslateUi(self, SceneEditor):
        SceneEditor.setWindowTitle(QCoreApplication.translate("SceneEditor", u"\u573a\u666f&\u5143\u7d20\u7f16\u8f91\u5668", None))
        self.scene_id_Label.setText(QCoreApplication.translate("SceneEditor", u"\u573a\u666fID\uff1a", None))
        self.scene_thresholdLabel.setText(QCoreApplication.translate("SceneEditor", u"\u5339\u914d\u9608\u503c\uff1a", None))
        self.Label.setText(QCoreApplication.translate("SceneEditor", u"\u573a\u666f\u5339\u914d\uff1a", None))
        self.scene_match_btn.setText(QCoreApplication.translate("SceneEditor", u"\u6267\u884c\u5339\u914d", None))
        self.element_id_Label.setText(QCoreApplication.translate("SceneEditor", u"\u5143\u7d20ID\uff1a", None))
        self.element_type_Label.setText(QCoreApplication.translate("SceneEditor", u"\u5143\u7d20\u7c7b\u578b\uff1a", None))
        self.element_type.setItemText(0, QCoreApplication.translate("SceneEditor", u"IMG", None))
        self.element_type.setItemText(1, QCoreApplication.translate("SceneEditor", u"COORDINATE", None))

        self.element_threshold_Label_2.setText(QCoreApplication.translate("SceneEditor", u"\u6a21\u7248\u5339\u914d\u9608\u503c\uff1a", None))
        self.element_match_type_Label_2.setText(QCoreApplication.translate("SceneEditor", u"\u5339\u914d\u7c7b\u578b\uff1a", None))
        self.element_match_type.setItemText(0, QCoreApplication.translate("SceneEditor", u"TEMPLATE", None))
        self.element_match_type.setItemText(1, QCoreApplication.translate("SceneEditor", u"SIFT", None))

        self.element_image_Label_2.setText(QCoreApplication.translate("SceneEditor", u"\u9009\u62e9\u56fe\u7247\uff1a", None))
        self.element_set_image_btn.setText(QCoreApplication.translate("SceneEditor", u"\u9009\u62e9\u56fe\u7247", None))
        self.element_split_image_btn.setText(QCoreApplication.translate("SceneEditor", u"\u5206\u79bb\u56fe\u7247", None))
        self.element_ratio_Label.setText(QCoreApplication.translate("SceneEditor", u"Ratio\uff1a", None))
        self.element_ratio.setText(QCoreApplication.translate("SceneEditor", u"(0.5,0.5)", None))
        self.ratioLabel.setText(QCoreApplication.translate("SceneEditor", u"\u8bbe\u7f6eRatio\uff1a", None))
        self.set_ratio_btn.setText(QCoreApplication.translate("SceneEditor", u"\u8bbe\u7f6eRatio", None))
        self.element_ratio_Label_3.setText(QCoreApplication.translate("SceneEditor", u"Roi\uff1a", None))
        self.element_roi.setText(QCoreApplication.translate("SceneEditor", u"(0,0,1600,900)", None))
        self.ratioLabel_3.setText(QCoreApplication.translate("SceneEditor", u"\u8bbe\u7f6eRoi\uff1a", None))
        self.set_roi_btn.setText(QCoreApplication.translate("SceneEditor", u"\u8bbe\u7f6eRoi", None))
        self.element_view_image_btn.setText(QCoreApplication.translate("SceneEditor", u"\u67e5\u770b\u56fe\u7247", None))
        self.element_match_btn.setText(QCoreApplication.translate("SceneEditor", u"\u6267\u884c\u5339\u914d", None))
        self.element_image_Label_4.setText(QCoreApplication.translate("SceneEditor", u"\u5143\u7d20\u56fe\u7247\uff1a", None))
        self.is_symbol_Label.setText(QCoreApplication.translate("SceneEditor", u"\u662f\u5426\u4e3a\u6807\u5fd7", None))
        self.Label_2.setText(QCoreApplication.translate("SceneEditor", u"\u5750\u6807\uff1a", None))
        self.element_coordinate.setText(QCoreApplication.translate("SceneEditor", u"(0,0)", None))
        self.Label_3.setText(QCoreApplication.translate("SceneEditor", u"\u8bbe\u7f6e\u5750\u6807\uff1a", None))
        self.set_coordinate_btn.setText(QCoreApplication.translate("SceneEditor", u"\u8bbe\u7f6e\u5750\u6807", None))
        self.button_save.setText(QCoreApplication.translate("SceneEditor", u"\u4fdd\u5b58", None))
        self.button_cancel.setText(QCoreApplication.translate("SceneEditor", u"\u9000\u51fa", None))
    # retranslateUi

