# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AddConfig.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_AddConfig(object):
    def setupUi(self, AddConfig):
        if not AddConfig.objectName():
            AddConfig.setObjectName(u"AddConfig")
        AddConfig.resize(268, 125)
        AddConfig.setStyleSheet(u"font-family:\"Consolas\",\"\u9ed1\u4f53\";\n"
"font-size:11pt;")
        self.horizontalLayout = QHBoxLayout(AddConfig)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.scene_info_form = QWidget(AddConfig)
        self.scene_info_form.setObjectName(u"scene_info_form")
        self.scene_info_form.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"border-radius:10px;\n"
"            }\n"
"\n"
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"QLineEdit {\n"
"                /* \u6e05\u9664\u9ed8\u8ba4\u8fb9\u6846\uff0c\u53ea\u4fdd\u7559\u4e0b\u8fb9\u6846 */\n"
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
"                border-bottom: 4px solid #39C5BB;  /* \u84dd"
                        "\u8272\u4e0b\u8fb9\u6846\uff08\u7a81\u51fa\u663e\u793a\uff09 */\n"
"                outline: none;  /* \u53bb\u9664\u7cfb\u7edf\u9ed8\u8ba4\u7684\u805a\u7126\u5916\u8fb9\u6846 */\n"
"            }\n"
"            \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
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
"    border: no"
                        "ne;  /* \u53bb\u9664\u9ed8\u8ba4\u6309\u94ae\u8fb9\u6846 */\n"
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
"QSpinBox"
                        " {\n"
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
"    border: 2p"
                        "x solid #0f322f;\n"
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
"max-width:100p"
                        "x;\n"
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
        self.verticalLayout = QVBoxLayout(self.scene_info_form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.user_name_Label = QLabel(self.scene_info_form)
        self.user_name_Label.setObjectName(u"user_name_Label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.user_name_Label)

        self.user_name_LineEdit = QLineEdit(self.scene_info_form)
        self.user_name_LineEdit.setObjectName(u"user_name_LineEdit")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.user_name_LineEdit)


        self.verticalLayout.addLayout(self.formLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 10, 5, 10)
        self.confirm = QPushButton(self.scene_info_form)
        self.confirm.setObjectName(u"confirm")

        self.horizontalLayout_2.addWidget(self.confirm)

        self.cancel = QPushButton(self.scene_info_form)
        self.cancel.setObjectName(u"cancel")

        self.horizontalLayout_2.addWidget(self.cancel)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.verticalLayout.setStretch(0, 1)

        self.horizontalLayout.addWidget(self.scene_info_form)


        self.retranslateUi(AddConfig)
        self.confirm.clicked.connect(AddConfig.accept)
        self.cancel.clicked.connect(AddConfig.reject)

        QMetaObject.connectSlotsByName(AddConfig)
    # setupUi

    def retranslateUi(self, AddConfig):
        AddConfig.setWindowTitle(QCoreApplication.translate("AddConfig", u"\u589e\u52a0\u914d\u7f6e", None))
        self.user_name_Label.setText(QCoreApplication.translate("AddConfig", u"\u7528\u6237\u540d\uff1a", None))
        self.confirm.setText(QCoreApplication.translate("AddConfig", u"\u786e\u8ba4", None))
        self.cancel.setText(QCoreApplication.translate("AddConfig", u"\u53d6\u6d88", None))
    # retranslateUi

