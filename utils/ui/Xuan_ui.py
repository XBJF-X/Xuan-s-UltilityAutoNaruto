# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Xuan.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
    QStackedWidget, QVBoxLayout, QWidget)

class Ui_Xuan(object):
    def setupUi(self, Xuan):
        if not Xuan.objectName():
            Xuan.setObjectName(u"Xuan")
        Xuan.resize(1197, 679)
        Xuan.setMinimumSize(QSize(180, 0))
        font = QFont()
        font.setFamilies([u"Consolas"])
        font.setPointSize(15)
        font.setBold(False)
        font.setItalic(False)
        Xuan.setFont(font)
        Xuan.setStyleSheet(u"/*\n"
"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"font: 15pt \"Microsoft YaHei UI\";\n"
"*/\n"
"font-family:\"Consolas\",\"\u9ed1\u4f53\";\n"
"font-size:15pt;\n"
"\n"
"")
        self.centralwidget = QWidget(Xuan)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setFont(font)
        self.centralwidget.setStyleSheet(u"")
        self.verticalLayout_15 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.widget_25 = QWidget(self.centralwidget)
        self.widget_25.setObjectName(u"widget_25")
        self.widget_25.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }")
        self.horizontalLayout_56 = QHBoxLayout(self.widget_25)
        self.horizontalLayout_56.setObjectName(u"horizontalLayout_56")
        self.horizontalLayout_56.setContentsMargins(0, 0, 0, 0)
        self.widget_90 = QWidget(self.widget_25)
        self.widget_90.setObjectName(u"widget_90")
        self.widget_90.setStyleSheet(u"/*\n"
"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"font: 15pt \"Microsoft YaHei UI\";\n"
"*/\n"
"font-family: \"Microsoft YaHei UI\", \"\u9ed1\u4f53\";\n"
"font-size: 20pt;\n"
"font-weight: bold;\n"
"color: #0f322f;\n"
"")
        self.horizontalLayout_68 = QHBoxLayout(self.widget_90)
        self.horizontalLayout_68.setObjectName(u"horizontalLayout_68")
        self.label_6 = QLabel(self.widget_90)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_68.addWidget(self.label_6)

        self.frame_53 = QFrame(self.widget_90)
        self.frame_53.setObjectName(u"frame_53")
        self.frame_53.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"padding:5px;\n"
"            }")
        self.frame_53.setFrameShape(QFrame.Shape.VLine)
        self.frame_53.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout_68.addWidget(self.frame_53)


        self.horizontalLayout_56.addWidget(self.widget_90)

        self.widget_91 = QWidget(self.widget_25)
        self.widget_91.setObjectName(u"widget_91")
        self.horizontalLayout_81 = QHBoxLayout(self.widget_91)
        self.horizontalLayout_81.setSpacing(10)
        self.horizontalLayout_81.setObjectName(u"horizontalLayout_81")
        self.horizontalLayout_81.setContentsMargins(0, 0, 9, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_81.addItem(self.horizontalSpacer)

        self.go_to_github_btn = QPushButton(self.widget_91)
        self.go_to_github_btn.setObjectName(u"go_to_github_btn")
        self.go_to_github_btn.setMinimumSize(QSize(90, 35))
        self.go_to_github_btn.setStyleSheet(u"QPushButton{\n"
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

        self.horizontalLayout_81.addWidget(self.go_to_github_btn)

        self.update_btn = QPushButton(self.widget_91)
        self.update_btn.setObjectName(u"update_btn")
        self.update_btn.setMinimumSize(QSize(110, 35))
        self.update_btn.setStyleSheet(u"QPushButton{\n"
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

        self.horizontalLayout_81.addWidget(self.update_btn)

        self.min_btn = QPushButton(self.widget_91)
        self.min_btn.setObjectName(u"min_btn")
        self.min_btn.setMinimumSize(QSize(85, 35))
        self.min_btn.setStyleSheet(u"QPushButton{\n"
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

        self.horizontalLayout_81.addWidget(self.min_btn)

        self.exit_btn = QPushButton(self.widget_91)
        self.exit_btn.setObjectName(u"exit_btn")
        self.exit_btn.setMinimumSize(QSize(70, 35))
        self.exit_btn.setStyleSheet(u"QPushButton{\n"
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

        self.horizontalLayout_81.addWidget(self.exit_btn)


        self.horizontalLayout_56.addWidget(self.widget_91)


        self.verticalLayout_15.addWidget(self.widget_25)

        self.widget_109 = QWidget(self.centralwidget)
        self.widget_109.setObjectName(u"widget_109")
        self.horizontalLayout = QHBoxLayout(self.widget_109)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.widget_110 = QWidget(self.widget_109)
        self.widget_110.setObjectName(u"widget_110")
        self.widget_110.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
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
"            QLineEdit {\n"
"                /* \u6e05\u9664\u9ed8"
                        "\u8ba4\u8fb9\u6846\uff0c\u53ea\u4fdd\u7559\u4e0b\u8fb9\u6846 */\n"
"                border: none;\n"
"                border-bottom: 3px solid #969696;  /* \u7070\u8272\u4e0b\u8fb9\u6846 */\n"
"                padding: 5px 0;  /* \u4e0a\u4e0b\u4e0b\u5185\u8fb9\u8ddd\uff0c\u907f\u514d\u6587\u5b57\u7d27\u8d34\u7d27\u8d34\u8fb9\u6846 */\n"
"				border-radius:0px;\n"
"                background: transparent;  /* \u80cc\u666f\u900f\u660e\uff0c\u53ea\u663e\u793a\u4e0b\u8fb9\u6846 */\n"
"            }\n"
"            \n"
"            /* 2. \u9009\u4e2d\uff08\u83b7\u5f97\u7126\u70b9\u70b9\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:focus {\n"
"                border-bottom: 4px solid #39C5BB;  /* \u84dd\u8272\u4e0b\u8fb9\u6846\uff08\u7a81\u51fa\u663e\u793a\uff09 */\n"
"                outline: none;  /* \u53bb\u9664\u7cfb\u7edf\u9ed8\u8ba4\u7684\u805a\u7126\u5916\u8fb9\u6846 */\n"
"            }\n"
"            \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001"
                        "\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #39C5BB;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_16 = QVBoxLayout(self.widget_110)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalSpacer_30 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_16.addItem(self.verticalSpacer_30)

        self.add_config_btn = QPushButton(self.widget_110)
        self.add_config_btn.setObjectName(u"add_config_btn")
        self.add_config_btn.setMinimumSize(QSize(30, 0))
        self.add_config_btn.setMaximumSize(QSize(50, 16777215))
        self.add_config_btn.setStyleSheet(u"QPushButton{\n"
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

        self.verticalLayout_16.addWidget(self.add_config_btn)


        self.horizontalLayout.addWidget(self.widget_110)

        self.ServiceStackedWidget = QStackedWidget(self.widget_109)
        self.ServiceStackedWidget.setObjectName(u"ServiceStackedWidget")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.ServiceStackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.ServiceStackedWidget.addWidget(self.page_2)

        self.horizontalLayout.addWidget(self.ServiceStackedWidget)


        self.verticalLayout_15.addWidget(self.widget_109)

        Xuan.setCentralWidget(self.centralwidget)

        self.retranslateUi(Xuan)

        QMetaObject.connectSlotsByName(Xuan)
    # setupUi

    def retranslateUi(self, Xuan):
        Xuan.setWindowTitle(QCoreApplication.translate("Xuan", u"XUAN\uff08Xuan's UtilityAutoNaruto\uff09", None))
        self.label_6.setText(QCoreApplication.translate("Xuan", u"   Xuan\u2018s Utility Auto Naruto   ", None))
        self.go_to_github_btn.setText(QCoreApplication.translate("Xuan", u"Github", None))
        self.update_btn.setText(QCoreApplication.translate("Xuan", u"\u68c0\u67e5\u66f4\u65b0", None))
        self.min_btn.setText(QCoreApplication.translate("Xuan", u"\u6700\u5c0f\u5316", None))
        self.exit_btn.setText(QCoreApplication.translate("Xuan", u"\u9000\u51fa", None))
        self.add_config_btn.setText(QCoreApplication.translate("Xuan", u"+", None))
    # retranslateUi

