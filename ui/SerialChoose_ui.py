# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SerialChoose.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_SerialChoose(object):
    def setupUi(self, SerialChoose):
        if not SerialChoose.objectName():
            SerialChoose.setObjectName(u"SerialChoose")
        SerialChoose.resize(394, 268)
        SerialChoose.setMinimumSize(QSize(394, 268))
        SerialChoose.setMaximumSize(QSize(522, 573))
        SerialChoose.setStyleSheet(u"font-family:\"Consolas\",\"\u9ed1\u4f53\";\n"
"font-size:15pt;\n"
"\n"
"")
        self.horizontalLayout = QHBoxLayout(SerialChoose)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.serial_listWidget = QListWidget(SerialChoose)
        self.serial_listWidget.setObjectName(u"serial_listWidget")
        self.serial_listWidget.setMinimumSize(QSize(250, 250))
        self.serial_listWidget.setMaximumSize(QSize(16777215, 16777215))
        self.serial_listWidget.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"QLabel{color:#0f322f;}")

        self.horizontalLayout.addWidget(self.serial_listWidget)

        self.widget_2 = QWidget(SerialChoose)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setMinimumSize(QSize(120, 0))
        self.widget_2.setMaximumSize(QSize(120, 16777215))
        self.widget_2.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"QLabel{color:#0f322f;}")
        self.verticalLayout = QVBoxLayout(self.widget_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.ok = QPushButton(self.widget_2)
        self.ok.setObjectName(u"ok")
        self.ok.setStyleSheet(u"QPushButton{\n"
"border: 2px solid #b5b5b5;  /* 2px\u5bbd\u7684\u6df1\u7070\u8272\u5b9e\u7ebf\u8fb9\u6846 */\n"
"background-color: rgb(255, 255, 255);\n"
"border-radius:10px;\n"
"outline:none;\n"
"color:#0f322f;\n"
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

        self.verticalLayout.addWidget(self.ok, 0, Qt.AlignmentFlag.AlignBottom)


        self.horizontalLayout.addWidget(self.widget_2)


        self.retranslateUi(SerialChoose)

        QMetaObject.connectSlotsByName(SerialChoose)
    # setupUi

    def retranslateUi(self, SerialChoose):
        SerialChoose.setWindowTitle(QCoreApplication.translate("SerialChoose", u"\u4e32\u53e3\u5217\u8868", None))
        self.ok.setText(QCoreApplication.translate("SerialChoose", u"\u786e\u5b9a", None))
    # retranslateUi

