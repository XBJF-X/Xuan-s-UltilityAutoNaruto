# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'NewElement.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QDoubleSpinBox, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QStackedWidget,
    QVBoxLayout, QWidget)

class Ui_NewElement(object):
    def setupUi(self, NewElement):
        if not NewElement.objectName():
            NewElement.setObjectName(u"NewElement")
        NewElement.resize(318, 360)
        NewElement.setStyleSheet(u"font-family:\"Consolas\",\"\u9ed1\u4f53\";\n"
"font-size:11pt;")
        self.verticalLayout_2 = QVBoxLayout(NewElement)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.element_info_form = QWidget(NewElement)
        self.element_info_form.setObjectName(u"element_info_form")
        self.element_info_form.setStyleSheet(u"QWidget {\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"QLineEdit {\n"
"                /* \u6e05\u9664\u9ed8\u8ba4\u8fb9\u6846\uff0c\u53ea\u4fdd\u7559\u4e0b\u8fb9\u6846 */\n"
"				font-size:11pt;\n"
"                border: none;\n"
"                border-bottom:"
                        " 3px solid #969696;  /* \u7070\u8272\u4e0b\u8fb9\u6846 */\n"
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
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"QLineEdit:hover {\n"
"                border-bottom: 4px solid #39C5BB;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846"
                        "\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
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
"QComboBox::down-arrow:on {\n"
"    image: none;  /* \u4e0b\u62c9\u72b6\u6001\u4e5f\u4e0d\u663e\u793a\u9ed8\u8ba4\u7bad\u5934 */\n"
"}\n"
""
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
"/* \u9690\u85cfQSpinBox\u9ed8\u8ba4\u4e0a\u4e0b\u6309\u94ae */\n"
"QSpinBox::up-button, QSpinBox::down-button {\n"
"    border: none;\n"
" "
                        "   width: 0;  /* \u9690\u85cf\u9ed8\u8ba4\u6309\u94ae */\n"
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
"/* \u9690\u85cfQSpinBox\u9ed8\u8ba4\u4e0a\u4e0b\u6309\u94ae */\n"
"QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {\n"
"    border: none;\n"
"    width:"
                        " 0;  /* \u9690\u85cf\u9ed8\u8ba4\u6309\u94ae */\n"
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
"border: 2px solid #39C5BB;  /* 2px\u5bbd\u7684\u6df1\u7070\u8272\u5b9e\u7ebf\u8fb9\u6846 */\n"
"outline:none;\n"
"color:#39C5BB;\n"
"}\n"
"")
        self.verticalLayout = QVBoxLayout(self.element_info_form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.element_id_Label = QLabel(self.element_info_form)
        self.element_id_Label.setObjectName(u"element_id_Label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.element_id_Label)

        self.element_id_LineEdit = QLineEdit(self.element_info_form)
        self.element_id_LineEdit.setObjectName(u"element_id_LineEdit")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.element_id_LineEdit)

        self.element_type_Label = QLabel(self.element_info_form)
        self.element_type_Label.setObjectName(u"element_type_Label")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.element_type_Label)

        self.element_type_ComboBox = QComboBox(self.element_info_form)
        self.element_type_ComboBox.addItem("")
        self.element_type_ComboBox.addItem("")
        self.element_type_ComboBox.setObjectName(u"element_type_ComboBox")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.element_type_ComboBox)

        self.element_image_Widget = QWidget(self.element_info_form)
        self.element_image_Widget.setObjectName(u"element_image_Widget")
        self.verticalLayout_3 = QVBoxLayout(self.element_image_Widget)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.element_image_Widget)


        self.verticalLayout.addLayout(self.formLayout)

        self.stackedWidget = QStackedWidget(self.element_info_form)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.IMG_element_form = QWidget()
        self.IMG_element_form.setObjectName(u"IMG_element_form")
        self.verticalLayout_5 = QVBoxLayout(self.IMG_element_form)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setLabelAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formLayout_2.setFormAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)
        self.element_threshold_Label_2 = QLabel(self.IMG_element_form)
        self.element_threshold_Label_2.setObjectName(u"element_threshold_Label_2")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.element_threshold_Label_2)

        self.element_threshold_DoubleSpinBox_2 = QDoubleSpinBox(self.IMG_element_form)
        self.element_threshold_DoubleSpinBox_2.setObjectName(u"element_threshold_DoubleSpinBox_2")
        self.element_threshold_DoubleSpinBox_2.setMaximum(1.000000000000000)
        self.element_threshold_DoubleSpinBox_2.setSingleStep(0.010000000000000)
        self.element_threshold_DoubleSpinBox_2.setValue(0.800000000000000)

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.element_threshold_DoubleSpinBox_2)

        self.element_match_type_Label_2 = QLabel(self.IMG_element_form)
        self.element_match_type_Label_2.setObjectName(u"element_match_type_Label_2")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.element_match_type_Label_2)

        self.element_match_type_ComboBox_2 = QComboBox(self.IMG_element_form)
        self.element_match_type_ComboBox_2.addItem("")
        self.element_match_type_ComboBox_2.addItem("")
        self.element_match_type_ComboBox_2.setObjectName(u"element_match_type_ComboBox_2")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.element_match_type_ComboBox_2)

        self.element_image_Label_2 = QLabel(self.IMG_element_form)
        self.element_image_Label_2.setObjectName(u"element_image_Label_2")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.LabelRole, self.element_image_Label_2)

        self.set_img_btn = QPushButton(self.IMG_element_form)
        self.set_img_btn.setObjectName(u"set_img_btn")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.FieldRole, self.set_img_btn)

        self.element_ratio_Label = QLabel(self.IMG_element_form)
        self.element_ratio_Label.setObjectName(u"element_ratio_Label")

        self.formLayout_2.setWidget(4, QFormLayout.ItemRole.LabelRole, self.element_ratio_Label)

        self.element_ratio_Widget = QWidget(self.IMG_element_form)
        self.element_ratio_Widget.setObjectName(u"element_ratio_Widget")
        self.verticalLayout_4 = QVBoxLayout(self.element_ratio_Widget)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.element_ratio = QLabel(self.element_ratio_Widget)
        self.element_ratio.setObjectName(u"element_ratio")

        self.verticalLayout_4.addWidget(self.element_ratio)


        self.formLayout_2.setWidget(4, QFormLayout.ItemRole.FieldRole, self.element_ratio_Widget)

        self.ratioLabel = QLabel(self.IMG_element_form)
        self.ratioLabel.setObjectName(u"ratioLabel")

        self.formLayout_2.setWidget(5, QFormLayout.ItemRole.LabelRole, self.ratioLabel)

        self.ratioWidget = QWidget(self.IMG_element_form)
        self.ratioWidget.setObjectName(u"ratioWidget")
        self.verticalLayout_6 = QVBoxLayout(self.ratioWidget)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.set_ratio_btn = QPushButton(self.ratioWidget)
        self.set_ratio_btn.setObjectName(u"set_ratio_btn")

        self.verticalLayout_6.addWidget(self.set_ratio_btn)


        self.formLayout_2.setWidget(5, QFormLayout.ItemRole.FieldRole, self.ratioWidget)

        self.Label = QLabel(self.IMG_element_form)
        self.Label.setObjectName(u"Label")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.Label)

        self.is_symbol = QCheckBox(self.IMG_element_form)
        self.is_symbol.setObjectName(u"is_symbol")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.is_symbol)


        self.verticalLayout_5.addLayout(self.formLayout_2)

        self.stackedWidget.addWidget(self.IMG_element_form)
        self.COORDINATE_element_form = QWidget()
        self.COORDINATE_element_form.setObjectName(u"COORDINATE_element_form")
        self.verticalLayout_11 = QVBoxLayout(self.COORDINATE_element_form)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.formLayout_6 = QFormLayout()
        self.formLayout_6.setObjectName(u"formLayout_6")
        self.formLayout_6.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self.formLayout_6.setLabelAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formLayout_6.setFormAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formLayout_6.setHorizontalSpacing(6)

        self.verticalLayout_11.addLayout(self.formLayout_6)

        self.stackedWidget.addWidget(self.COORDINATE_element_form)

        self.verticalLayout.addWidget(self.stackedWidget)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 10, 5, 10)
        self.confirm = QPushButton(self.element_info_form)
        self.confirm.setObjectName(u"confirm")

        self.horizontalLayout_2.addWidget(self.confirm)

        self.cancel = QPushButton(self.element_info_form)
        self.cancel.setObjectName(u"cancel")

        self.horizontalLayout_2.addWidget(self.cancel)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.verticalLayout.setStretch(1, 1)

        self.verticalLayout_2.addWidget(self.element_info_form)


        self.retranslateUi(NewElement)
        self.element_type_ComboBox.currentIndexChanged.connect(self.stackedWidget.setCurrentIndex)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(NewElement)
    # setupUi

    def retranslateUi(self, NewElement):
        NewElement.setWindowTitle(QCoreApplication.translate("NewElement", u"\u65b0\u5efa\u5143\u7d20", None))
        self.element_id_Label.setText(QCoreApplication.translate("NewElement", u"\u5143\u7d20ID\uff1a", None))
        self.element_type_Label.setText(QCoreApplication.translate("NewElement", u"\u5143\u7d20\u7c7b\u578b\uff1a", None))
        self.element_type_ComboBox.setItemText(0, QCoreApplication.translate("NewElement", u"IMG", None))
        self.element_type_ComboBox.setItemText(1, QCoreApplication.translate("NewElement", u"COORDINATE", None))

        self.element_threshold_Label_2.setText(QCoreApplication.translate("NewElement", u"\u6a21\u7248\u5339\u914d\u9608\u503c\uff1a", None))
        self.element_match_type_Label_2.setText(QCoreApplication.translate("NewElement", u"\u5143\u7d20\u5339\u914d\u7c7b\u578b\uff1a", None))
        self.element_match_type_ComboBox_2.setItemText(0, QCoreApplication.translate("NewElement", u"TEMPLATE", None))
        self.element_match_type_ComboBox_2.setItemText(1, QCoreApplication.translate("NewElement", u"SIFT", None))

        self.element_image_Label_2.setText(QCoreApplication.translate("NewElement", u"\u5143\u7d20\u56fe\u7247\uff1a", None))
        self.set_img_btn.setText(QCoreApplication.translate("NewElement", u"\u9009\u62e9\u56fe\u7247", None))
        self.element_ratio_Label.setText(QCoreApplication.translate("NewElement", u"Ratio\uff1a", None))
        self.element_ratio.setText(QCoreApplication.translate("NewElement", u"(0.5,0.5)", None))
        self.ratioLabel.setText(QCoreApplication.translate("NewElement", u"\u8bbe\u7f6eRatio\uff1a", None))
        self.set_ratio_btn.setText(QCoreApplication.translate("NewElement", u"\u8bbe\u7f6eRatio", None))
        self.Label.setText(QCoreApplication.translate("NewElement", u"\u662f\u5426\u4e3a\u6807\u5fd7", None))
        self.confirm.setText(QCoreApplication.translate("NewElement", u"\u786e\u8ba4", None))
        self.cancel.setText(QCoreApplication.translate("NewElement", u"\u53d6\u6d88", None))
    # retranslateUi

