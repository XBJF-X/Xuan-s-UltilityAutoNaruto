# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Service.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QLayout, QLineEdit, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QSpinBox, QStackedWidget,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

class Ui_Service(object):
    def setupUi(self, Service):
        if not Service.objectName():
            Service.setObjectName(u"Service")
        Service.resize(1157, 744)
        Service.setStyleSheet(u"font-family:\"Consolas\",\"\u9ed1\u4f53\";\n"
"font-size:15pt;")
        self.horizontalLayout_56 = QHBoxLayout(Service)
        self.horizontalLayout_56.setObjectName(u"horizontalLayout_56")
        self.widget_31 = QWidget(Service)
        self.widget_31.setObjectName(u"widget_31")
        self.horizontalLayout = QHBoxLayout(self.widget_31)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.widget_10 = QWidget(self.widget_31)
        self.widget_10.setObjectName(u"widget_10")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_10.sizePolicy().hasHeightForWidth())
        self.widget_10.setSizePolicy(sizePolicy)
        self.widget_10.setMinimumSize(QSize(230, 0))
        self.widget_10.setMaximumSize(QSize(230, 16777215))
        palette = QPalette()
        brush = QBrush(QColor(255, 255, 255, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush)
        self.widget_10.setPalette(palette)
        font = QFont()
        font.setFamilies([u"Consolas"])
        font.setPointSize(15)
        font.setBold(False)
        font.setItalic(False)
        self.widget_10.setFont(font)
        self.widget_10.setStyleSheet(u"background-color: white;")
        self.verticalLayout_5 = QVBoxLayout(self.widget_10)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.widget_9 = QWidget(self.widget_10)
        self.widget_9.setObjectName(u"widget_9")
        self.widget_9.setStyleSheet(u"")
        self.verticalLayout_8 = QVBoxLayout(self.widget_9)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(-1, 0, -1, -1)
        self.overview_panel_button = QPushButton(self.widget_9)
        self.overview_panel_button.setObjectName(u"overview_panel_button")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.overview_panel_button.sizePolicy().hasHeightForWidth())
        self.overview_panel_button.setSizePolicy(sizePolicy1)
        self.overview_panel_button.setMinimumSize(QSize(0, 40))
        self.overview_panel_button.setFont(font)
        self.overview_panel_button.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.overview_panel_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.overview_panel_button.setStyleSheet(u"QPushButton{\n"
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
        self.overview_panel_button.setAutoExclusive(False)
        self.overview_panel_button.setAutoDefault(False)
        self.overview_panel_button.setFlat(True)

        self.verticalLayout_8.addWidget(self.overview_panel_button)


        self.verticalLayout_5.addWidget(self.widget_9)

        self.widget_11 = QWidget(self.widget_10)
        self.widget_11.setObjectName(u"widget_11")
        self.verticalLayout_9 = QVBoxLayout(self.widget_11)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, -1, 0)
        self.treeWidget = QTreeWidget(self.widget_11)
        self.treeWidget.setObjectName(u"treeWidget")
        self.treeWidget.setMaximumSize(QSize(16777215, 16777215))
        font1 = QFont()
        font1.setFamilies([u"Consolas"])
        font1.setBold(False)
        font1.setItalic(False)
        self.treeWidget.setFont(font1)
        self.treeWidget.setStyleSheet(u"QTreeWidget {\n"
"	background-color:#f5f5f5;\n"
"	margin-left:10px;\n"
"	background: #F9F9F9;\n"
"	border-radius: 10px;\n"
"	outline: none;\n"
"	font-size: 20px;\n"
"}\n"
"QTreeWidget::item {\n"
"	height: 28px;\n"
"	font-weight: 400;\n"
"	color: #0f322f;\n"
"	padding-left:10px;\n"
"	padding-top:0px;\n"
"	padding-bottom:0px;\n"
"	margin-top:5px;\n"
"	margin-bottom:5px;\n"
"	outline: 0px;\n"
"	font-size: 10px;\n"
"}\n"
"QTreeWidget::item:hover {\n"
"	border: 0px;\n"
"	outline: 0px;\n"
"	border-left: 3px solid #39C5BB;\n"
"    color: #39C5BB;\n"
"}\n"
"QTreeWidget::item:selected{\n"
"    border: 0px;\n"
"	outline: 0px;\n"
"	border-left: 3px solid #39C5BB;\n"
"    color: #39C5BB;\n"
"}\n"
"QTreeWidget::item:selected:active{\n"
"    border: 0px;\n"
"	outline: 0px;\n"
"	border-left: 3px solid #39C5BB;\n"
"    color: #39C5BB;\n"
"}\n"
" \n"
"QTreeWidget::item:selected:!active {\n"
"    border: 0px;\n"
"	outline: 0px;\n"
"	border-left: 3px solid #39C5BB;\n"
"    color: #39C5BB;\n"
"}\n"
"QTreeWidget::branch {\n"
"	hei"
                        "ght: 28px;\n"
"	width: 28px;\n"
"	color:#0f322f;\n"
"}\n"
"QTreeWidget::branch::hover {\n"
"	height: 28px;\n"
"	width: 28px;\n"
"	color:#39C5BB;\n"
"}\n"
"QTreeWidget::indicator {\n"
"	height: 20px;\n"
"	width: 20px;\n"
"}\n"
"QTreeWidget QScrollBar:vertical {\n"
"    background-color: #ffffff;\n"
"    width: 7px;\n"
"    margin: 0px;\n"
"    border-radius: 4px;\n"
"}\n"
"QTreeWidget QScrollBar::handle:vertical {\n"
"    background-color: #8b8b8b;\n"
"    border-radius: 3px;\n"
"    margin: 3 0px 6 0px;\n"
"    min-height: 30px;\n"
"}\n"
"QTreeWidget QScrollBar::handle:vertical:hover,\n"
"QTreeWidget QScrollBar::handle:vertical:pressed {\n"
"    background-color: #3c3f41;\n"
"    border-radius: 3px;\n"
"    margin: 0 0px 0 0px;\n"
"}\n"
"QTreeWidget QScrollBar::sub-line:vertical,\n"
"QTreeWidget QScrollBar::add-line:vertical {\n"
"    border: none;\n"
"    height: 0px;\n"
"}\n"
"")
        self.treeWidget.setFrameShape(QFrame.Shape.NoFrame)
        self.treeWidget.setAutoScrollMargin(16)
        self.treeWidget.setIndentation(19)
        self.treeWidget.setRootIsDecorated(True)
        self.treeWidget.setUniformRowHeights(False)
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.setAnimated(True)
        self.treeWidget.setHeaderHidden(True)
        self.treeWidget.header().setVisible(False)

        self.verticalLayout_9.addWidget(self.treeWidget)


        self.verticalLayout_5.addWidget(self.widget_11)


        self.horizontalLayout.addWidget(self.widget_10)

        self.widget = QWidget(self.widget_31)
        self.widget.setObjectName(u"widget")
        palette1 = QPalette()
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush)
        brush1 = QBrush(QColor(229, 229, 229, 255))
        brush1.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush1)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush1)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush1)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush1)
        self.widget.setPalette(palette1)
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(self.widget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setStyleSheet(u"QStackedWidget QWidget {\n"
"                background-color: rgb(255, 255, 255);  /* \u80cc\u666f\u989c\u8272 */\n"
"            }")
        self.Overview_Panel_widget = QWidget()
        self.Overview_Panel_widget.setObjectName(u"Overview_Panel_widget")
        self.Overview_Panel_widget.setEnabled(True)
        self.Overview_Panel_widget.setStyleSheet(u"")
        self.horizontalLayout_2 = QHBoxLayout(self.Overview_Panel_widget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 10, 0, 0)
        self.widget_2 = QWidget(self.Overview_Panel_widget)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setMinimumSize(QSize(240, 0))
        self.widget_2.setMaximumSize(QSize(280, 16777215))
        self.widget_2.setStyleSheet(u"")
        self.verticalLayout_3 = QVBoxLayout(self.widget_2)
        self.verticalLayout_3.setSpacing(9)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(7, 0, 7, 0)
        self.widget_4 = QWidget(self.widget_2)
        self.widget_4.setObjectName(u"widget_4")
        palette2 = QPalette()
        brush2 = QBrush(QColor(15, 50, 47, 255))
        brush2.setStyle(Qt.BrushStyle.SolidPattern)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush2)
        brush3 = QBrush(QColor(222, 222, 222, 255))
        brush3.setStyle(Qt.BrushStyle.SolidPattern)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush3)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush2)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush2)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush3)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush3)
        brush4 = QBrush(QColor(15, 50, 47, 128))
        brush4.setStyle(Qt.BrushStyle.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush4)
#endif
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush2)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush3)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush2)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush2)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush3)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush3)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush4)
#endif
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush2)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush3)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush2)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush2)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush3)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush3)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, brush4)
#endif
        self.widget_4.setPalette(palette2)
        self.widget_4.setStyleSheet(u"#widget_4 {  /* \u4ec5\u5339\u914d objectName \u4e3a myWidget \u7684\u63a7\u4ef6 */\n"
"    background-color: rgb(222, 222, 222);\n"
"border-radius: 10px;\n"
"}\n"
"QWidget QLabel {\n"
"    background-color: rgb(222, 222, 222);\n"
"border-radius: 10px;\n"
"}")
        self.horizontalLayout_3 = QHBoxLayout(self.widget_4)
        self.horizontalLayout_3.setSpacing(4)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 9, 10, 9)
        self.label = QLabel(self.widget_4)
        self.label.setObjectName(u"label")
        self.label.setStyleSheet(u"font-size:23px;\n"
"margin-top:0px;\n"
"margin-bottom:0px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setIndent(0)

        self.horizontalLayout_3.addWidget(self.label)

        self.start_schedule_button = QPushButton(self.widget_4)
        self.start_schedule_button.setObjectName(u"start_schedule_button")
        self.start_schedule_button.setEnabled(True)
        self.start_schedule_button.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.start_schedule_button.setStyleSheet(u"QPushButton{\n"
"border: 2px solid #b5b5b5;  /* 2px\u5bbd\u7684\u6df1\u7070\u8272\u5b9e\u7ebf\u8fb9\u6846 */\n"
"background-color: rgb(255, 255, 255);\n"
"border-radius:10px;\n"
"outline:none;\n"
"color:#0f322f;\n"
"padding-top:5px;\n"
"padding-bottom:5px;\n"
"}\n"
"QPushButton::hover {\n"
"border: 2px solid #39C5BB;  /* 2px\u5bbd\u7684\u6df1\u7070\u8272\u5b9e\u7ebf\u8fb9\u6846 */\n"
"background-color: rgb(255, 255, 255);\n"
"border-radius:10px;\n"
"outline:none;\n"
"padding-top:5px;\n"
"color:#39C5BB;\n"
"padding-bottom:5px;\n"
"}\n"
"QPushButton:disabled {\n"
"        background-color: #dedede;  /* \u80cc\u666f\u8272 */\n"
"        color: #b5b5b5;             /* \u6587\u5b57\u989c\u8272 */\n"
"        border: 2px solid #b5b5b5;  /* 2px\u5bbd\u7684\u6df1\u7070\u8272\u5b9e\u7ebf\u8fb9\u6846 */\n"
"    }")

        self.horizontalLayout_3.addWidget(self.start_schedule_button)


        self.verticalLayout_3.addWidget(self.widget_4)

        self.widget_5 = QWidget(self.widget_2)
        self.widget_5.setObjectName(u"widget_5")
        self.widget_5.setStyleSheet(u"#widget_5 {  /* \u4ec5\u5339\u914d objectName \u4e3a myWidget \u7684\u63a7\u4ef6 */\n"
"    background-color: rgb(222, 222, 222);\n"
"border-radius: 10px;\n"
"}\n"
"QWidget QLabel {\n"
"    background-color: rgb(222, 222, 222);\n"
"}")
        self.verticalLayout = QVBoxLayout(self.widget_5)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(9, 9, 9, 9)
        self.label_2 = QLabel(self.widget_5)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setStyleSheet(u"\n"
"margin-top:3px;\n"
"margin-bottom:0px;\n"
"")

        self.verticalLayout.addWidget(self.label_2)

        self.line = QFrame(self.widget_5)
        self.line.setObjectName(u"line")
        palette3 = QPalette()
        brush5 = QBrush(QColor(179, 179, 179, 255))
        brush5.setStyle(Qt.BrushStyle.SolidPattern)
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush5)
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush)
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush2)
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush2)
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush)
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush4)
#endif
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush5)
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush)
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush2)
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush2)
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush)
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush4)
#endif
        brush6 = QBrush(QColor(120, 120, 120, 255))
        brush6.setStyle(Qt.BrushStyle.SolidPattern)
        palette3.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush6)
        palette3.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush)
        palette3.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush2)
        palette3.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush2)
        palette3.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush)
        palette3.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette3.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, brush4)
#endif
        self.line.setPalette(palette3)
        self.line.setLineWidth(2)
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.scrollArea = QScrollArea(self.widget_5)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setStyleSheet(u"QScrollArea {\n"
"    /* \u4e3b\u8fb9\u6846\uff1a\u7070\u8272\u5b9e\u7ebf\uff0c2px\u5bbd\uff0c\u5706\u89d25px */\n"
"    border: 2px solid rgb(209, 209, 209);\n"
"    border-radius: 5px;\n"
"    /* \u5185\u8fb9\u8ddd\uff0c\u907f\u514d\u5185\u5bb9\u7d27\u8d34\u8fb9\u6846 */\n"
"    padding-right: 3px;\n"
"    /* \u80cc\u666f\u8272 */\n"
"    background-color: #e7e7e7;\n"
"}\n"
"\n"
"/* \u6eda\u52a8\u533a\u57df\u7684\u5185\u5bb9\u533a\u57df\uff08QScrollArea\u7684\u89c6\u53e3\uff09 */\n"
"QScrollArea > QWidget > QWidget {\n"
"    /* \u5185\u5bb9\u533a\u57df\u80cc\u666f\u8272 */\n"
"    background-color: #e2e2e2;\n"
"}\n"
"        /* \u5782\u76f4\u6eda\u52a8\u6761\u6574\u4f53 */\n"
"        QScrollBar:vertical {\n"
"            background-color: #e2e2e2;\n"
"            width: 6px;\n"
"            margin: 0px;\n"
"            border-radius: 4px;\n"
"        }\n"
"        QScrollBar::handle:vertical {\n"
"            background-color: #8b8b8b;\n"
"            border-radius: 3px;\n"
"            margin: 3 0px 6 0px;"
                        "\n"
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
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scroll_area_running_content = QWidget()
        self.scroll_area_running_content.setObjectName(u"scroll_area_running_content")
        self.scroll_area_running_content.setGeometry(QRect(0, 0, 232, 63))
        self.scrollArea.setWidget(self.scroll_area_running_content)

        self.verticalLayout.addWidget(self.scrollArea)


        self.verticalLayout_3.addWidget(self.widget_5)

        self.widget_6 = QWidget(self.widget_2)
        self.widget_6.setObjectName(u"widget_6")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.widget_6.sizePolicy().hasHeightForWidth())
        self.widget_6.setSizePolicy(sizePolicy2)
        self.widget_6.setStyleSheet(u"#widget_6 {  /* \u4ec5\u5339\u914d objectName \u4e3a myWidget \u7684\u63a7\u4ef6 */\n"
"    background-color: rgb(222, 222, 222);\n"
"border-radius: 10px;\n"
"}\n"
"QWidget QLabel {\n"
"    background-color: rgb(222, 222, 222);\n"
"}")
        self.verticalLayout_6 = QVBoxLayout(self.widget_6)
        self.verticalLayout_6.setSpacing(4)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(9, 9, 9, 9)
        self.label_3 = QLabel(self.widget_6)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setStyleSheet(u"margin-top:3px;\n"
"margin-bottom:0px;")

        self.verticalLayout_6.addWidget(self.label_3)

        self.line_2 = QFrame(self.widget_6)
        self.line_2.setObjectName(u"line_2")
        palette4 = QPalette()
        palette4.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush5)
        palette4.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush)
        palette4.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush2)
        palette4.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush2)
        palette4.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush)
        palette4.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette4.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush4)
#endif
        palette4.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush5)
        palette4.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush)
        palette4.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush2)
        palette4.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush2)
        palette4.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush)
        palette4.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette4.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush4)
#endif
        palette4.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush6)
        palette4.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush)
        palette4.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush2)
        palette4.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush2)
        palette4.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush)
        palette4.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette4.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, brush4)
#endif
        self.line_2.setPalette(palette4)
        self.line_2.setLineWidth(2)
        self.line_2.setFrameShape(QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_6.addWidget(self.line_2)

        self.scrollArea_2 = QScrollArea(self.widget_6)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setStyleSheet(u"QScrollArea {\n"
"    /* \u4e3b\u8fb9\u6846\uff1a\u7070\u8272\u5b9e\u7ebf\uff0c2px\u5bbd\uff0c\u5706\u89d25px */\n"
"    border: 2px solid rgb(209, 209, 209);\n"
"    border-radius: 5px;\n"
"    /* \u5185\u8fb9\u8ddd\uff0c\u907f\u514d\u5185\u5bb9\u7d27\u8d34\u8fb9\u6846 */\n"
"    padding-right: 3px;\n"
"    /* \u80cc\u666f\u8272 */\n"
"    background-color: #e7e7e7;\n"
"}\n"
"\n"
"/* \u6eda\u52a8\u533a\u57df\u7684\u5185\u5bb9\u533a\u57df\uff08QScrollArea\u7684\u89c6\u53e3\uff09 */\n"
"QScrollArea > QWidget > QWidget {\n"
"    /* \u5185\u5bb9\u533a\u57df\u80cc\u666f\u8272 */\n"
"    background-color: #e2e2e2;\n"
"}\n"
"        /* \u5782\u76f4\u6eda\u52a8\u6761\u6574\u4f53 */\n"
"        QScrollBar:vertical {\n"
"            background-color: #e2e2e2;\n"
"            width: 6px;\n"
"            margin: 0px;\n"
"            border-radius: 4px;\n"
"        }\n"
"        QScrollBar::handle:vertical {\n"
"            background-color: #8b8b8b;\n"
"            border-radius: 3px;\n"
"            margin: 3 0px 6 0px;"
                        "\n"
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
        self.scrollArea_2.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea_2.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea_2.setWidgetResizable(True)
        self.scroll_area_ready_content = QWidget()
        self.scroll_area_ready_content.setObjectName(u"scroll_area_ready_content")
        self.scroll_area_ready_content.setGeometry(QRect(0, 0, 232, 124))
        self.scrollArea_2.setWidget(self.scroll_area_ready_content)

        self.verticalLayout_6.addWidget(self.scrollArea_2)


        self.verticalLayout_3.addWidget(self.widget_6)

        self.widget_7 = QWidget(self.widget_2)
        self.widget_7.setObjectName(u"widget_7")
        self.widget_7.setStyleSheet(u"#widget_7 {  /* \u4ec5\u5339\u914d objectName \u4e3a myWidget \u7684\u63a7\u4ef6 */\n"
"    background-color: rgb(222, 222, 222);\n"
"border-radius: 10px;\n"
"}\n"
"QWidget QLabel {\n"
"    background-color: rgb(222, 222, 222);\n"
"}")
        self.verticalLayout_7 = QVBoxLayout(self.widget_7)
        self.verticalLayout_7.setSpacing(4)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(9, 9, 9, 9)
        self.label_4 = QLabel(self.widget_7)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setStyleSheet(u"\n"
"margin-top:3px;\n"
"margin-bottom:0px;")

        self.verticalLayout_7.addWidget(self.label_4)

        self.line_3 = QFrame(self.widget_7)
        self.line_3.setObjectName(u"line_3")
        palette5 = QPalette()
        palette5.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush5)
        palette5.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush)
        palette5.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush2)
        palette5.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush2)
        palette5.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush)
        palette5.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette5.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush4)
#endif
        palette5.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush5)
        palette5.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush)
        palette5.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush2)
        palette5.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush2)
        palette5.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush)
        palette5.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette5.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush4)
#endif
        palette5.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush6)
        palette5.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush)
        palette5.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush2)
        palette5.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush2)
        palette5.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush)
        palette5.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette5.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, brush4)
#endif
        self.line_3.setPalette(palette5)
        self.line_3.setLineWidth(2)
        self.line_3.setFrameShape(QFrame.Shape.VLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_7.addWidget(self.line_3)

        self.scrollArea_3 = QScrollArea(self.widget_7)
        self.scrollArea_3.setObjectName(u"scrollArea_3")
        self.scrollArea_3.setStyleSheet(u"QScrollArea {\n"
"    /* \u4e3b\u8fb9\u6846\uff1a\u7070\u8272\u5b9e\u7ebf\uff0c2px\u5bbd\uff0c\u5706\u89d25px */\n"
"    border: 2px solid rgb(209, 209, 209);\n"
"    border-radius: 5px;\n"
"    /* \u5185\u8fb9\u8ddd\uff0c\u907f\u514d\u5185\u5bb9\u7d27\u8d34\u8fb9\u6846 */\n"
"    padding-right: 3px;\n"
"    /* \u80cc\u666f\u8272 */\n"
"    background-color: #e7e7e7;\n"
"}\n"
"\n"
"/* \u6eda\u52a8\u533a\u57df\u7684\u5185\u5bb9\u533a\u57df\uff08QScrollArea\u7684\u89c6\u53e3\uff09 */\n"
"QScrollArea > QWidget > QWidget {\n"
"    /* \u5185\u5bb9\u533a\u57df\u80cc\u666f\u8272 */\n"
"    background-color: #e2e2e2;\n"
"}\n"
"        /* \u5782\u76f4\u6eda\u52a8\u6761\u6574\u4f53 */\n"
"        QScrollBar:vertical {\n"
"            background-color: #e2e2e2;\n"
"            width: 6px;\n"
"            margin: 0px;\n"
"            border-radius: 4px;\n"
"        }\n"
"        QScrollBar::handle:vertical {\n"
"            background-color: #8b8b8b;\n"
"            border-radius: 3px;\n"
"            margin: 3 0px 6 0px;"
                        "\n"
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
        self.scrollArea_3.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea_3.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea_3.setWidgetResizable(True)
        self.scroll_area_wait_content = QWidget()
        self.scroll_area_wait_content.setObjectName(u"scroll_area_wait_content")
        self.scroll_area_wait_content.setGeometry(QRect(0, 0, 232, 250))
        self.scrollArea_3.setWidget(self.scroll_area_wait_content)

        self.verticalLayout_7.addWidget(self.scrollArea_3)


        self.verticalLayout_3.addWidget(self.widget_7)

        self.verticalLayout_3.setStretch(0, 1)
        self.verticalLayout_3.setStretch(1, 1)
        self.verticalLayout_3.setStretch(2, 3)
        self.verticalLayout_3.setStretch(3, 5)

        self.horizontalLayout_2.addWidget(self.widget_2)

        self.widget_3 = QWidget(self.Overview_Panel_widget)
        self.widget_3.setObjectName(u"widget_3")
        self.verticalLayout_4 = QVBoxLayout(self.widget_3)
        self.verticalLayout_4.setSpacing(5)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.widget_8 = QWidget(self.widget_3)
        self.widget_8.setObjectName(u"widget_8")
        self.widget_8.setStyleSheet(u"")
        self.verticalLayout_10 = QVBoxLayout(self.widget_8)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(9, 0, 9, 0)
        self.widget_12 = QWidget(self.widget_8)
        self.widget_12.setObjectName(u"widget_12")
        self.widget_12.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"QLabel{color:#0f322f;}\n"
"/* \u8c03\u6574\u52fe\u9009\u6846\u7684\u5927\u5c0f */\n"
"QCheckBox::indicator {\n"
"color:#0f322f;\n"
"	width: 14px;      /* \u52fe\u9009\u6846\u5bbd\u5ea6 */\n"
"	height: 14px;     /* \u52fe\u9009\u6846\u9ad8\u5ea6 */\n"
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
"            QLine"
                        "Edit {\n"
"                /* \u6e05\u9664\u9ed8\u8ba4\u8fb9\u6846\uff0c\u53ea\u4fdd\u7559\u4e0b\u8fb9\u6846 */\n"
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
"            /* 3. \u9f20\u6807"
                        "\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.horizontalLayout_4 = QHBoxLayout(self.widget_12)
        self.horizontalLayout_4.setSpacing(15)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.log_text_label = QLabel(self.widget_12)
        self.log_text_label.setObjectName(u"log_text_label")
        self.log_text_label.setFont(font1)
        self.log_text_label.setStyleSheet(u"font-size:25px;\n"
"")
        self.log_text_label.setIndent(10)

        self.horizontalLayout_4.addWidget(self.log_text_label, 0, Qt.AlignmentFlag.AlignLeft)

        self.bool_debug = QCheckBox(self.widget_12)
        self.bool_debug.setObjectName(u"bool_debug")
        self.bool_debug.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.horizontalLayout_4.addWidget(self.bool_debug, 0, Qt.AlignmentFlag.AlignRight)

        self.bool_save_img = QCheckBox(self.widget_12)
        self.bool_save_img.setObjectName(u"bool_save_img")
        self.bool_save_img.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.bool_save_img.setStyleSheet(u"")

        self.horizontalLayout_4.addWidget(self.bool_save_img, 0, Qt.AlignmentFlag.AlignRight)

        self.horizontalLayout_4.setStretch(0, 1)

        self.verticalLayout_10.addWidget(self.widget_12)


        self.verticalLayout_4.addWidget(self.widget_8)

        self.logs_container = QWidget(self.widget_3)
        self.logs_container.setObjectName(u"logs_container")
        self.logs_container.setEnabled(True)
        self.logs_container.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.logs_container.setStyleSheet(u"")

        self.verticalLayout_4.addWidget(self.logs_container)

        self.verticalLayout_4.setStretch(0, 1)
        self.verticalLayout_4.setStretch(1, 11)

        self.horizontalLayout_2.addWidget(self.widget_3)

        self.horizontalLayout_2.setStretch(0, 1)
        self.stackedWidget.addWidget(self.Overview_Panel_widget)
        self.DQH_Settings_widget = QWidget()
        self.DQH_Settings_widget.setObjectName(u"DQH_Settings_widget")
        self.DQH_Settings_widget.setMinimumSize(QSize(180, 0))
        self.horizontalLayout_5 = QHBoxLayout(self.DQH_Settings_widget)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 10, 0, 0)
        self.widget_19 = QWidget(self.DQH_Settings_widget)
        self.widget_19.setObjectName(u"widget_19")
        self.widget_19.setStyleSheet(u"")
        self.horizontalLayout_12 = QHBoxLayout(self.widget_19)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(-1, 0, -1, 0)
        self.scrollArea_8 = QScrollArea(self.widget_19)
        self.scrollArea_8.setObjectName(u"scrollArea_8")
        self.scrollArea_8.setMinimumSize(QSize(600, 0))
        self.scrollArea_8.setWidgetResizable(True)
        self.scrollArea_8.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_5 = QWidget()
        self.scrollAreaWidgetContents_5.setObjectName(u"scrollAreaWidgetContents_5")
        self.scrollAreaWidgetContents_5.setGeometry(QRect(0, 0, 493, 1144))
        self.verticalLayout_25 = QVBoxLayout(self.scrollAreaWidgetContents_5)
        self.verticalLayout_25.setSpacing(20)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.verticalLayout_25.setContentsMargins(0, 0, 0, 0)
        self.widget_21 = QWidget(self.scrollAreaWidgetContents_5)
        self.widget_21.setObjectName(u"widget_21")
        self.widget_21.setStyleSheet(u"QWidget {\n"
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
"QLineEdit {\n"
"                /* \u6e05\u9664\u9ed8\u8ba4\u8fb9"
                        "\u6846\uff0c\u53ea\u4fdd\u7559\u4e0b\u8fb9\u6846 */\n"
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
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846"
                        " */\n"
"QLineEdit:hover {\n"
"                border-bottom: 4px solid #39C5BB;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }\n"
"/* QComboBox \u6837\u5f0f */\n"
"QComboBox {\n"
"    border: 2px solid #0f322f;  /* \u8fb9\u6846\u989c\u8272\u4e0eCheckBox\u4fdd\u6301\u4e00\u81f4 */\n"
"    border-radius: 3px;\n"
"    padding: 5px 0px 5px 10px;  /* \u53f3\u4fa7\u9884\u7559\u7a7a\u95f4\u7ed9\u81ea\u5b9a\u4e49\u7bad\u5934 */\n"
"    background-color: #e7e7e7;\n"
"    min-height: 20px;\n"
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
"    image: none;  /* \u4e0b\u62c9"
                        "\u72b6\u6001\u4e5f\u4e0d\u663e\u793a\u9ed8\u8ba4\u7bad\u5934 */\n"
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
"    min-height: 20px;\n"
"}\n"
"\n"
"/* \u9690\u85cfQSpinBox\u9ed8\u8ba4\u4e0a\u4e0b\u6309\u94ae */\n"
"QSpinBox::up-button, QSpinBox::down-button"
                        " {\n"
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
"\n"
"QPushButton{\n"
"min-height: 26px;\n"
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
        self.verticalLayout_26 = QVBoxLayout(self.widget_21)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")
        self.verticalLayout_26.setContentsMargins(-1, 7, -1, -1)
        self.label_18 = QLabel(self.widget_21)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_26.addWidget(self.label_18)

        self.frame_3 = QFrame(self.widget_21)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_3.setFrameShape(QFrame.Shape.HLine)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_26.addWidget(self.frame_3)

        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(10, 10, 10, 10)
        self.widget_20 = QWidget(self.widget_21)
        self.widget_20.setObjectName(u"widget_20")
        self.verticalLayout_13 = QVBoxLayout(self.widget_20)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.serial_list_button = QPushButton(self.widget_20)
        self.serial_list_button.setObjectName(u"serial_list_button")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.serial_list_button.sizePolicy().hasHeightForWidth())
        self.serial_list_button.setSizePolicy(sizePolicy3)
        self.serial_list_button.setMinimumSize(QSize(100, 34))

        self.verticalLayout_13.addWidget(self.serial_list_button, 0, Qt.AlignmentFlag.AlignHCenter)

        self.serial = QLineEdit(self.widget_20)
        self.serial.setObjectName(u"serial")
        self.serial.setMinimumSize(QSize(170, 0))
        self.serial.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.serial.setMaxLength(30)
        self.serial.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_13.addWidget(self.serial)


        self.gridLayout_5.addWidget(self.widget_20, 2, 1, 1, 1)

        self.verticalLayout_27 = QVBoxLayout()
        self.verticalLayout_27.setObjectName(u"verticalLayout_27")
        self.label_19 = QLabel(self.widget_21)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setStyleSheet(u"QLabel QToolTip {\n"
"                background-color: #f0f0f0;  /* \u80cc\u666f\u8272 */\n"
"                color: #333333;             /* \u6587\u5b57\u989c\u8272 */\n"
"                border: 1px solid #cccccc;  /* \u8fb9\u6846 */\n"
"                padding: 6px 10px;          /* \u5185\u8fb9\u8ddd */\n"
"                font-family: \"\u9ed1\u4f53\", sans-serif;  /* \u5b57\u4f53 */\n"
"                font-size: 15px;            /* \u5b57\u53f7 */\n"
"            }\n"
"")

        self.verticalLayout_27.addWidget(self.label_19)

        self.label_20 = QLabel(self.widget_21)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")
        self.label_20.setTextFormat(Qt.TextFormat.AutoText)

        self.verticalLayout_27.addWidget(self.label_20)


        self.gridLayout_5.addLayout(self.verticalLayout_27, 1, 0, 1, 1)

        self.control_mode = QComboBox(self.widget_21)
        self.control_mode.addItem("")
        self.control_mode.addItem("")
        self.control_mode.setObjectName(u"control_mode")
        self.control_mode.setMaximumSize(QSize(120, 16777215))

        self.gridLayout_5.addWidget(self.control_mode, 1, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter)

        self.verticalLayout_14 = QVBoxLayout()
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.label_106 = QLabel(self.widget_21)
        self.label_106.setObjectName(u"label_106")

        self.verticalLayout_14.addWidget(self.label_106)

        self.label_107 = QLabel(self.widget_21)
        self.label_107.setObjectName(u"label_107")
        self.label_107.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_14.addWidget(self.label_107)


        self.gridLayout_5.addLayout(self.verticalLayout_14, 2, 0, 1, 1)

        self.gridLayout_5.setColumnStretch(0, 5)

        self.verticalLayout_26.addLayout(self.gridLayout_5)


        self.verticalLayout_25.addWidget(self.widget_21, 0, Qt.AlignmentFlag.AlignTop)

        self.widget_23 = QWidget(self.scrollAreaWidgetContents_5)
        self.widget_23.setObjectName(u"widget_23")
        sizePolicy2.setHeightForWidth(self.widget_23.sizePolicy().hasHeightForWidth())
        self.widget_23.setSizePolicy(sizePolicy2)
        self.widget_23.setStyleSheet(u"QWidget {\n"
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
"QLineEdit {\n"
"                /* \u6e05\u9664\u9ed8\u8ba4\u8fb9"
                        "\u6846\uff0c\u53ea\u4fdd\u7559\u4e0b\u8fb9\u6846 */\n"
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
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001"
                        "\u7684\u4e0b\u8fb9\u6846 */\n"
"QLineEdit:hover {\n"
"                border-bottom: 4px solid #39C5BB;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }\n"
"/* QComboBox \u6837\u5f0f */\n"
"QComboBox {\n"
"    border: 2px solid #0f322f;  /* \u8fb9\u6846\u989c\u8272\u4e0eCheckBox\u4fdd\u6301\u4e00\u81f4 */\n"
"    border-radius: 3px;\n"
"    padding: 5px 0px 5px 10px;  /* \u53f3\u4fa7\u9884\u7559\u7a7a\u95f4\u7ed9\u81ea\u5b9a\u4e49\u7bad\u5934 */\n"
"    background-color: #e7e7e7;\n"
"    min-height: 20px;\n"
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
"    ima"
                        "ge: none;  /* \u4e0b\u62c9\u72b6\u6001\u4e5f\u4e0d\u663e\u793a\u9ed8\u8ba4\u7bad\u5934 */\n"
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
"    min-height: 20px;\n"
"}\n"
"\n"
"/* \u9690\u85cfQSpinBox\u9ed8\u8ba4\u4e0a\u4e0b\u6309\u94ae */\n"
"QSpinBox::up-but"
                        "ton, QSpinBox::down-button {\n"
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
"\n"
"QPushButton{\n"
"min-height: 26px;\n"
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
        self.verticalLayout_36 = QVBoxLayout(self.widget_23)
        self.verticalLayout_36.setSpacing(6)
        self.verticalLayout_36.setObjectName(u"verticalLayout_36")
        self.verticalLayout_36.setContentsMargins(-1, 9, -1, -1)
        self.label_33 = QLabel(self.widget_23)
        self.label_33.setObjectName(u"label_33")
        self.label_33.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_36.addWidget(self.label_33)

        self.frame_8 = QFrame(self.widget_23)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_8.setFrameShape(QFrame.Shape.HLine)
        self.frame_8.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_36.addWidget(self.frame_8)

        self.gridLayout_10 = QGridLayout()
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.gridLayout_10.setVerticalSpacing(0)
        self.gridLayout_10.setContentsMargins(10, 10, 0, 0)
        self.screen_mode = QComboBox(self.widget_23)
        self.screen_mode.addItem("")
        self.screen_mode.addItem("")
        self.screen_mode.addItem("")
        self.screen_mode.addItem("")
        self.screen_mode.addItem("")
        self.screen_mode.setObjectName(u"screen_mode")
        self.screen_mode.setMinimumSize(QSize(180, 34))

        self.gridLayout_10.addWidget(self.screen_mode, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter)

        self.widget_13 = QWidget(self.widget_23)
        self.widget_13.setObjectName(u"widget_13")
        self.verticalLayout_37 = QVBoxLayout(self.widget_13)
        self.verticalLayout_37.setSpacing(6)
        self.verticalLayout_37.setObjectName(u"verticalLayout_37")
        self.verticalLayout_37.setContentsMargins(0, 0, 0, 0)
        self.label_34 = QLabel(self.widget_13)
        self.label_34.setObjectName(u"label_34")
        self.label_34.setStyleSheet(u"QLabel QToolTip {\n"
"                background-color: #f0f0f0;  /* \u80cc\u666f\u8272 */\n"
"                color: #333333;             /* \u6587\u5b57\u989c\u8272 */\n"
"                border: 1px solid #cccccc;  /* \u8fb9\u6846 */\n"
"                padding: 6px 10px;          /* \u5185\u8fb9\u8ddd */\n"
"                font-family: \"\u9ed1\u4f53\", sans-serif;  /* \u5b57\u4f53 */\n"
"                font-size: 15px;            /* \u5b57\u53f7 */\n"
"            }\n"
"")

        self.verticalLayout_37.addWidget(self.label_34)

        self.label_35 = QLabel(self.widget_13)
        self.label_35.setObjectName(u"label_35")
        self.label_35.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")
        self.label_35.setTextFormat(Qt.TextFormat.AutoText)
        self.label_35.setWordWrap(True)

        self.verticalLayout_37.addWidget(self.label_35)


        self.gridLayout_10.addWidget(self.widget_13, 0, 0, 1, 1)

        self.gridLayout_10.setColumnStretch(0, 5)

        self.verticalLayout_36.addLayout(self.gridLayout_10)

        self.screen_mode_settings_stackedWidget = QStackedWidget(self.widget_23)
        self.screen_mode_settings_stackedWidget.setObjectName(u"screen_mode_settings_stackedWidget")
        self.DroidCastRaw = QWidget()
        self.DroidCastRaw.setObjectName(u"DroidCastRaw")
        self.verticalLayout_11 = QVBoxLayout(self.DroidCastRaw)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 9, 0, 9)
        self.screen_mode_settings_stackedWidget.addWidget(self.DroidCastRaw)
        self.WindowCapture = QWidget()
        self.WindowCapture.setObjectName(u"WindowCapture")
        self.screen_mode_settings_stackedWidget.addWidget(self.WindowCapture)
        self.U2 = QWidget()
        self.U2.setObjectName(u"U2")
        self.screen_mode_settings_stackedWidget.addWidget(self.U2)
        self.MuMu = QWidget()
        self.MuMu.setObjectName(u"MuMu")
        self.verticalLayout_39 = QVBoxLayout(self.MuMu)
        self.verticalLayout_39.setObjectName(u"verticalLayout_39")
        self.verticalLayout_39.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_11 = QGridLayout()
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.gridLayout_11.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        self.gridLayout_11.setHorizontalSpacing(20)
        self.gridLayout_11.setVerticalSpacing(5)
        self.gridLayout_11.setContentsMargins(10, 0, -1, -1)
        self.label_10 = QLabel(self.MuMu)
        self.label_10.setObjectName(u"label_10")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy4)
        self.label_10.setMaximumSize(QSize(16777215, 20))

        self.gridLayout_11.addWidget(self.label_10, 0, 0, 1, 1)

        self.MuMu_install_path = QLineEdit(self.MuMu)
        self.MuMu_install_path.setObjectName(u"MuMu_install_path")
        self.MuMu_install_path.setMaximumSize(QSize(16777215, 40))
        self.MuMu_install_path.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.MuMu_install_path.setReadOnly(True)

        self.gridLayout_11.addWidget(self.MuMu_install_path, 1, 0, 1, 1)

        self.MuMu_install_path_browse = QPushButton(self.MuMu)
        self.MuMu_install_path_browse.setObjectName(u"MuMu_install_path_browse")
        self.MuMu_install_path_browse.setMaximumSize(QSize(16777215, 35))
        self.MuMu_install_path_browse.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.gridLayout_11.addWidget(self.MuMu_install_path_browse, 1, 1, 1, 1)

        self.widget_14 = QWidget(self.MuMu)
        self.widget_14.setObjectName(u"widget_14")
        self.verticalLayout_35 = QVBoxLayout(self.widget_14)
        self.verticalLayout_35.setObjectName(u"verticalLayout_35")
        self.verticalLayout_35.setContentsMargins(0, 0, 0, 0)
        self.label_11 = QLabel(self.widget_14)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setMaximumSize(QSize(16777215, 20))

        self.verticalLayout_35.addWidget(self.label_11)

        self.label_31 = QLabel(self.widget_14)
        self.label_31.setObjectName(u"label_31")
        self.label_31.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_35.addWidget(self.label_31)


        self.gridLayout_11.addWidget(self.widget_14, 3, 0, 1, 1)

        self.MuMu_instance_index = QSpinBox(self.MuMu)
        self.MuMu_instance_index.setObjectName(u"MuMu_instance_index")
        self.MuMu_instance_index.setMinimumSize(QSize(0, 34))
        self.MuMu_instance_index.setMaximumSize(QSize(70, 35))

        self.gridLayout_11.addWidget(self.MuMu_instance_index, 3, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter)

        self.gridLayout_11.setColumnStretch(0, 5)

        self.verticalLayout_39.addLayout(self.gridLayout_11)

        self.screen_mode_settings_stackedWidget.addWidget(self.MuMu)
        self.LD = QWidget()
        self.LD.setObjectName(u"LD")
        self.verticalLayout_38 = QVBoxLayout(self.LD)
        self.verticalLayout_38.setSpacing(0)
        self.verticalLayout_38.setObjectName(u"verticalLayout_38")
        self.verticalLayout_38.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(20)
        self.gridLayout_2.setVerticalSpacing(5)
        self.gridLayout_2.setContentsMargins(10, 0, -1, -1)
        self.label_8 = QLabel(self.LD)
        self.label_8.setObjectName(u"label_8")
        sizePolicy4.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy4)
        self.label_8.setMaximumSize(QSize(16777215, 20))

        self.gridLayout_2.addWidget(self.label_8, 0, 0, 1, 1)

        self.LD_install_path = QLineEdit(self.LD)
        self.LD_install_path.setObjectName(u"LD_install_path")
        self.LD_install_path.setMaximumSize(QSize(16777215, 40))
        self.LD_install_path.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.LD_install_path.setReadOnly(True)

        self.gridLayout_2.addWidget(self.LD_install_path, 1, 0, 1, 1)

        self.LD_install_path_browse = QPushButton(self.LD)
        self.LD_install_path_browse.setObjectName(u"LD_install_path_browse")
        self.LD_install_path_browse.setMaximumSize(QSize(16777215, 35))
        self.LD_install_path_browse.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.LD_install_path_browse.setStyleSheet(u"")

        self.gridLayout_2.addWidget(self.LD_install_path_browse, 1, 1, 1, 1)

        self.widget_15 = QWidget(self.LD)
        self.widget_15.setObjectName(u"widget_15")
        self.verticalLayout_40 = QVBoxLayout(self.widget_15)
        self.verticalLayout_40.setSpacing(6)
        self.verticalLayout_40.setObjectName(u"verticalLayout_40")
        self.verticalLayout_40.setContentsMargins(0, 0, 0, 0)
        self.label_9 = QLabel(self.widget_15)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setMaximumSize(QSize(16777215, 20))

        self.verticalLayout_40.addWidget(self.label_9)

        self.label_32 = QLabel(self.widget_15)
        self.label_32.setObjectName(u"label_32")
        self.label_32.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_40.addWidget(self.label_32)


        self.gridLayout_2.addWidget(self.widget_15, 3, 0, 1, 1)

        self.LD_instance_index = QSpinBox(self.LD)
        self.LD_instance_index.setObjectName(u"LD_instance_index")
        self.LD_instance_index.setMaximumSize(QSize(70, 35))

        self.gridLayout_2.addWidget(self.LD_instance_index, 3, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter)

        self.gridLayout_2.setColumnStretch(0, 5)

        self.verticalLayout_38.addLayout(self.gridLayout_2)

        self.screen_mode_settings_stackedWidget.addWidget(self.LD)

        self.verticalLayout_36.addWidget(self.screen_mode_settings_stackedWidget)


        self.verticalLayout_25.addWidget(self.widget_23)

        self.widget_95 = QWidget(self.scrollAreaWidgetContents_5)
        self.widget_95.setObjectName(u"widget_95")
        self.widget_95.setStyleSheet(u"QWidget {\n"
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
"QLineEdit {\n"
"                /* \u6e05\u9664\u9ed8\u8ba4\u8fb9"
                        "\u6846\uff0c\u53ea\u4fdd\u7559\u4e0b\u8fb9\u6846 */\n"
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
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846"
                        " */\n"
"QLineEdit:hover {\n"
"                border-bottom: 4px solid #39C5BB;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }\n"
"/* QComboBox \u6837\u5f0f */\n"
"QComboBox {\n"
"    border: 2px solid #0f322f;  /* \u8fb9\u6846\u989c\u8272\u4e0eCheckBox\u4fdd\u6301\u4e00\u81f4 */\n"
"    border-radius: 3px;\n"
"    padding: 5px 0px 5px 10px;  /* \u53f3\u4fa7\u9884\u7559\u7a7a\u95f4\u7ed9\u81ea\u5b9a\u4e49\u7bad\u5934 */\n"
"    background-color: #e7e7e7;\n"
"    min-height: 20px;\n"
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
"    image: none;  /* \u4e0b\u62c9"
                        "\u72b6\u6001\u4e5f\u4e0d\u663e\u793a\u9ed8\u8ba4\u7bad\u5934 */\n"
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
"    min-height: 20px;\n"
"}\n"
"\n"
"/* \u9690\u85cfQSpinBox\u9ed8\u8ba4\u4e0a\u4e0b\u6309\u94ae */\n"
"QSpinBox::up-button, QSpinBox::down-button"
                        " {\n"
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
"\n"
"QPushButton{\n"
"min-height: 26px;\n"
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
        self.verticalLayout_175 = QVBoxLayout(self.widget_95)
        self.verticalLayout_175.setSpacing(6)
        self.verticalLayout_175.setObjectName(u"verticalLayout_175")
        self.verticalLayout_175.setContentsMargins(-1, 9, -1, -1)
        self.label_231 = QLabel(self.widget_95)
        self.label_231.setObjectName(u"label_231")
        self.label_231.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_175.addWidget(self.label_231)

        self.frame_44 = QFrame(self.widget_95)
        self.frame_44.setObjectName(u"frame_44")
        self.frame_44.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_44.setFrameShape(QFrame.Shape.HLine)
        self.frame_44.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_175.addWidget(self.frame_44)

        self.gridLayout_16 = QGridLayout()
        self.gridLayout_16.setObjectName(u"gridLayout_16")
        self.gridLayout_16.setVerticalSpacing(0)
        self.gridLayout_16.setContentsMargins(10, 10, 0, 0)
        self.widget_18 = QWidget(self.widget_95)
        self.widget_18.setObjectName(u"widget_18")
        self.widget_18.setMinimumSize(QSize(0, 0))
        self.verticalLayout_176 = QVBoxLayout(self.widget_18)
        self.verticalLayout_176.setSpacing(6)
        self.verticalLayout_176.setObjectName(u"verticalLayout_176")
        self.verticalLayout_176.setContentsMargins(0, 0, 0, 0)
        self.label_233 = QLabel(self.widget_18)
        self.label_233.setObjectName(u"label_233")

        self.verticalLayout_176.addWidget(self.label_233)

        self.label_234 = QLabel(self.widget_18)
        self.label_234.setObjectName(u"label_234")
        self.label_234.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")
        self.label_234.setTextFormat(Qt.TextFormat.AutoText)
        self.label_234.setWordWrap(True)

        self.verticalLayout_176.addWidget(self.label_234)


        self.gridLayout_16.addWidget(self.widget_18, 0, 0, 1, 1)

        self.scan_inerval = QSpinBox(self.widget_95)
        self.scan_inerval.setObjectName(u"scan_inerval")
        self.scan_inerval.setMaximumSize(QSize(110, 35))
        self.scan_inerval.setWrapping(False)
        self.scan_inerval.setFrame(True)
        self.scan_inerval.setMinimum(50)
        self.scan_inerval.setMaximum(9999)
        self.scan_inerval.setValue(1000)

        self.gridLayout_16.addWidget(self.scan_inerval, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter)

        self.gridLayout_16.setColumnStretch(0, 5)

        self.verticalLayout_175.addLayout(self.gridLayout_16)


        self.verticalLayout_25.addWidget(self.widget_95)

        self.widget_94 = QWidget(self.scrollAreaWidgetContents_5)
        self.widget_94.setObjectName(u"widget_94")
        self.widget_94.setStyleSheet(u"QWidget {\n"
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
"QLineEdit {\n"
"                /* \u6e05\u9664\u9ed8\u8ba4\u8fb9"
                        "\u6846\uff0c\u53ea\u4fdd\u7559\u4e0b\u8fb9\u6846 */\n"
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
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846"
                        " */\n"
"QLineEdit:hover {\n"
"                border-bottom: 4px solid #39C5BB;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }\n"
"/* QComboBox \u6837\u5f0f */\n"
"QComboBox {\n"
"    border: 2px solid #0f322f;  /* \u8fb9\u6846\u989c\u8272\u4e0eCheckBox\u4fdd\u6301\u4e00\u81f4 */\n"
"    border-radius: 3px;\n"
"    padding: 5px 0px 5px 10px;  /* \u53f3\u4fa7\u9884\u7559\u7a7a\u95f4\u7ed9\u81ea\u5b9a\u4e49\u7bad\u5934 */\n"
"    background-color: #e7e7e7;\n"
"    min-height: 20px;\n"
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
"    image: none;  /* \u4e0b\u62c9"
                        "\u72b6\u6001\u4e5f\u4e0d\u663e\u793a\u9ed8\u8ba4\u7bad\u5934 */\n"
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
"    min-height: 20px;\n"
"}\n"
"\n"
"/* \u9690\u85cfQSpinBox\u9ed8\u8ba4\u4e0a\u4e0b\u6309\u94ae */\n"
"QSpinBox::up-button, QSpinBox::down-button"
                        " {\n"
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
"\n"
"QPushButton{\n"
"min-height: 26px;\n"
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
        self.verticalLayout_173 = QVBoxLayout(self.widget_94)
        self.verticalLayout_173.setSpacing(6)
        self.verticalLayout_173.setObjectName(u"verticalLayout_173")
        self.verticalLayout_173.setContentsMargins(-1, 9, -1, -1)
        self.label_227 = QLabel(self.widget_94)
        self.label_227.setObjectName(u"label_227")
        self.label_227.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_173.addWidget(self.label_227)

        self.label_230 = QLabel(self.widget_94)
        self.label_230.setObjectName(u"label_230")
        self.label_230.setStyleSheet(u"font-size:13pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_173.addWidget(self.label_230)

        self.frame_9 = QFrame(self.widget_94)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_9.setFrameShape(QFrame.Shape.HLine)
        self.frame_9.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_173.addWidget(self.frame_9)

        self.gridLayout_12 = QGridLayout()
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.gridLayout_12.setVerticalSpacing(0)
        self.gridLayout_12.setContentsMargins(10, 10, 0, 0)
        self.widget_17 = QWidget(self.widget_94)
        self.widget_17.setObjectName(u"widget_17")
        self.verticalLayout_174 = QVBoxLayout(self.widget_17)
        self.verticalLayout_174.setSpacing(6)
        self.verticalLayout_174.setObjectName(u"verticalLayout_174")
        self.verticalLayout_174.setContentsMargins(0, 0, 0, 0)
        self.label_228 = QLabel(self.widget_17)
        self.label_228.setObjectName(u"label_228")

        self.verticalLayout_174.addWidget(self.label_228)

        self.label_229 = QLabel(self.widget_17)
        self.label_229.setObjectName(u"label_229")
        self.label_229.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")
        self.label_229.setTextFormat(Qt.TextFormat.AutoText)
        self.label_229.setWordWrap(True)

        self.verticalLayout_174.addWidget(self.label_229)


        self.gridLayout_12.addWidget(self.widget_17, 0, 0, 1, 1)

        self.key_map_configuration_button = QPushButton(self.widget_94)
        self.key_map_configuration_button.setObjectName(u"key_map_configuration_button")
        self.key_map_configuration_button.setMinimumSize(QSize(70, 34))
        self.key_map_configuration_button.setMaximumSize(QSize(16777215, 35))
        self.key_map_configuration_button.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.key_map_configuration_button.setStyleSheet(u"")

        self.gridLayout_12.addWidget(self.key_map_configuration_button, 0, 1, 1, 1)

        self.gridLayout_12.setColumnStretch(0, 5)

        self.verticalLayout_173.addLayout(self.gridLayout_12)


        self.verticalLayout_25.addWidget(self.widget_94)

        self.widget_22 = QWidget(self.scrollAreaWidgetContents_5)
        self.widget_22.setObjectName(u"widget_22")
        self.widget_22.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_34 = QVBoxLayout(self.widget_22)
        self.verticalLayout_34.setObjectName(u"verticalLayout_34")
        self.verticalLayout_34.setContentsMargins(-1, 7, -1, -1)
        self.label_30 = QLabel(self.widget_22)
        self.label_30.setObjectName(u"label_30")
        self.label_30.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_34.addWidget(self.label_30)

        self.frame_7 = QFrame(self.widget_22)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_7.setFrameShape(QFrame.Shape.HLine)
        self.frame_7.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_34.addWidget(self.frame_7)

        self.gridLayout_9 = QGridLayout()
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.gridLayout_9.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_18 = QVBoxLayout()
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.label_114 = QLabel(self.widget_22)
        self.label_114.setObjectName(u"label_114")

        self.verticalLayout_18.addWidget(self.label_114)

        self.label_115 = QLabel(self.widget_22)
        self.label_115.setObjectName(u"label_115")
        self.label_115.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_18.addWidget(self.label_115)


        self.gridLayout_9.addLayout(self.verticalLayout_18, 0, 0, 1, 1)

        self.secondary_password = QLineEdit(self.widget_22)
        self.secondary_password.setObjectName(u"secondary_password")
        self.secondary_password.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.secondary_password.setMaxLength(6)
        self.secondary_password.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        self.secondary_password.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.secondary_password.setDragEnabled(False)

        self.gridLayout_9.addWidget(self.secondary_password, 0, 1, 1, 1)

        self.gridLayout_9.setColumnStretch(0, 5)

        self.verticalLayout_34.addLayout(self.gridLayout_9)


        self.verticalLayout_25.addWidget(self.widget_22, 0, Qt.AlignmentFlag.AlignTop)

        self.verticalSpacer_32 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_25.addItem(self.verticalSpacer_32)

        self.scrollArea_8.setWidget(self.scrollAreaWidgetContents_5)

        self.horizontalLayout_12.addWidget(self.scrollArea_8)

        self.horizontalLayout_12.setStretch(0, 5)

        self.horizontalLayout_5.addWidget(self.widget_19)

        self.stackedWidget.addWidget(self.DQH_Settings_widget)

        self.verticalLayout_2.addWidget(self.stackedWidget)


        self.horizontalLayout.addWidget(self.widget)


        self.horizontalLayout_56.addWidget(self.widget_31)


        self.retranslateUi(Service)

        self.overview_panel_button.setDefault(False)
        self.stackedWidget.setCurrentIndex(0)
        self.screen_mode_settings_stackedWidget.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(Service)
    # setupUi

    def retranslateUi(self, Service):
        Service.setWindowTitle(QCoreApplication.translate("Service", u"Form", None))
        self.overview_panel_button.setText(QCoreApplication.translate("Service", u"\u603b\u89c8\u9762\u677f", None))
        ___qtreewidgetitem = self.treeWidget.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("Service", u"\u914d\u7f6e", None));
        self.label.setText(QCoreApplication.translate("Service", u"\u8c03\u5ea6\u5668", None))
        self.start_schedule_button.setText(QCoreApplication.translate("Service", u"\u542f\u52a8", None))
        self.label_2.setText(QCoreApplication.translate("Service", u"\u8fd0\u884c\u961f\u5217", None))
        self.label_3.setText(QCoreApplication.translate("Service", u"\u5c31\u7eea\u961f\u5217", None))
        self.label_4.setText(QCoreApplication.translate("Service", u"\u7b49\u5f85\u961f\u5217", None))
        self.log_text_label.setText(QCoreApplication.translate("Service", u"\u65e5\u5fd7", None))
        self.bool_debug.setText(QCoreApplication.translate("Service", u"\u8c03\u8bd5\u6a21\u5f0f", None))
        self.bool_save_img.setText(QCoreApplication.translate("Service", u"\u4fdd\u5b58\u56fe\u50cf", None))
        self.label_18.setText(QCoreApplication.translate("Service", u"\u63a7\u5236\u6a21\u5f0f", None))
        self.serial_list_button.setText(QCoreApplication.translate("Service", u"\u4e32\u53e3\u5217\u8868", None))
        self.serial.setText("")
        self.serial.setPlaceholderText(QCoreApplication.translate("Service", u"127.0.0.1:5555", None))
#if QT_CONFIG(tooltip)
        self.label_19.setToolTip(QCoreApplication.translate("Service", u"ADB\uff1a\u901a\u7528\u65b9\u6848\uff0c\u6027\u80fd\u4e0d\u9ad8\n"
"U2\uff1auiautomator2", None))
#endif // QT_CONFIG(tooltip)
        self.label_19.setText(QCoreApplication.translate("Service", u"\u63a7\u5236\u6a21\u5f0f\u9009\u62e9", None))
        self.label_20.setText(QCoreApplication.translate("Service", u"\u51b3\u5b9a\u4f7f\u7528\u54ea\u79cd\u65b9\u6848\u63a7\u5236\u6a21\u62df\u5668\n"
"\u9f20\u6807\u60ac\u505c\u67e5\u770b\u8be6\u7ec6\u4ecb\u7ecd", None))
        self.control_mode.setItemText(0, QCoreApplication.translate("Service", u"ADB", None))
        self.control_mode.setItemText(1, QCoreApplication.translate("Service", u"U2", None))

#if QT_CONFIG(tooltip)
        self.label_106.setToolTip(QCoreApplication.translate("Service", u"\u8bf7\u5148\u6253\u5f00\u81ea\u5df1\u7684\u6a21\u62df\u5668\n"
"\u70b9\u51fb\u53f3\u4fa7\u4e32\u53e3\u5217\u8868\n"
"\u81ea\u884c\u5206\u8fa8\u54ea\u4e2a\u4e32\u53e3\u662f\u81ea\u5df1\u6b63\u5728\u4f7f\u7528\u7684\u6a21\u62df\u5668\u7684\u4e32\u53e3\n"
"\u8be5\u4e32\u53e3\u4f1a\u88abDroidCastRaw\u548cU2\u5171\u540c\u4f7f\u7528", None))
#endif // QT_CONFIG(tooltip)
        self.label_106.setText(QCoreApplication.translate("Service", u"\u4e32\u53e3", None))
        self.label_107.setText(QCoreApplication.translate("Service", u"\u6a21\u62df\u5668\u7684ADB\u7aef\u53e3\u5730\u5740\n"
"\u9f20\u6807\u60ac\u505c\u67e5\u770b\u8be6\u7ec6\u4ecb\u7ecd", None))
        self.label_33.setText(QCoreApplication.translate("Service", u"\u622a\u56fe\u6a21\u5f0f", None))
        self.screen_mode.setItemText(0, QCoreApplication.translate("Service", u"DroidCastRaw", None))
        self.screen_mode.setItemText(1, QCoreApplication.translate("Service", u"WindowCapture", None))
        self.screen_mode.setItemText(2, QCoreApplication.translate("Service", u"U2", None))
        self.screen_mode.setItemText(3, QCoreApplication.translate("Service", u"MuMu", None))
        self.screen_mode.setItemText(4, QCoreApplication.translate("Service", u"LD", None))

#if QT_CONFIG(tooltip)
        self.label_34.setToolTip(QCoreApplication.translate("Service", u"DroidCastRaw\uff1a70-100ms \uff0c\u6a21\u62df\u5668\u53ef\u6700\u5c0f\u5316\uff0c\u53ef\u906e\u6321\n"
"WindowCapture\uff1a10-20ms\uff0c\u6355\u83b7\u7a97\u53e3\u4f4d\u56fe\uff0c\u6a21\u62df\u5668\u4e0d\u53ef\u6700\u5c0f\u5316\uff0c\u53ef\u906e\u6321\n"
"U2\uff1a70-100ms\uff0c\u4f7f\u7528uiautomator2\u5185\u7f6e\u51fd\u6570\uff0c\u6a21\u62df\u5668\u53ef\u6700\u5c0f\u5316\uff0c\u53ef\u906e\u6321\n"
"MuMu\uff1a5-10ms\uff0c\u4f7f\u7528MuMu\u6a21\u62df\u5668\u7684\u63a5\u53e3\uff0c\u6a21\u62df\u5668\u53ef\u6700\u5c0f\u5316\uff0c\u53ef\u906e\u6321\n"
"LD\uff1a5-10ms\uff0c\u4f7f\u7528\u96f7\u7535\u6a21\u62df\u5668\u7684\u63a5\u53e3\uff0c\u6a21\u62df\u5668\u53ef\u6700\u5c0f\u5316\uff0c\u53ef\u906e\u6321", None))
#endif // QT_CONFIG(tooltip)
        self.label_34.setText(QCoreApplication.translate("Service", u"\u622a\u56fe\u6a21\u5f0f\u9009\u62e9", None))
        self.label_35.setText(QCoreApplication.translate("Service", u"\u6839\u636e\u81ea\u5df1\u7684\u60c5\u51b5\u51b3\u5b9a\u4f7f\u7528\n"
"\u9f20\u6807\u60ac\u505c\u67e5\u770b\u8be6\u7ec6\u4ecb\u7ecd", None))
        self.label_10.setText(QCoreApplication.translate("Service", u"MuMu\u6a21\u62df\u5668\u5b89\u88c5\u8def\u5f84", None))
        self.MuMu_install_path.setText("")
        self.MuMu_install_path.setPlaceholderText(QCoreApplication.translate("Service", u".../MuMuPlayer-12.0(\u8be5\u6587\u4ef6\u5939\u4e0b\u987b\u6709shell\u6587\u4ef6\u5939\uff09", None))
        self.MuMu_install_path_browse.setText(QCoreApplication.translate("Service", u"\u6d4f\u89c8", None))
        self.label_11.setText(QCoreApplication.translate("Service", u"MuMu\u5b9e\u4f8b\u7d22\u5f15", None))
        self.label_31.setText(QCoreApplication.translate("Service", u"\u5728MuMu\u591a\u5f00\u5668\u4e2d\u67e5\u770b\u81ea\u5df1\u6b63\u5728\u4f7f\u7528\u7684\u6a21\u62df\u5668\u5b9e\u4f8b\u7d22\u5f15\n"
"\u5982\u679c\u662f\u7b2c\u4e00\u4e2a\u6a21\u62df\u5668\u5c31\u662f0\uff0c\u4f9d\u6b21\u7c7b\u63a8", None))
        self.label_8.setText(QCoreApplication.translate("Service", u"\u96f7\u7535\u6a21\u62df\u5668\u5b89\u88c5\u8def\u5f84", None))
        self.LD_install_path.setText("")
        self.LD_install_path.setPlaceholderText(QCoreApplication.translate("Service", u".../leidian/LDPlayer9(\u8be5\u6587\u4ef6\u5939\u4e0b\u987b\u6709ld.exe\u6587\u4ef6\u5939\uff09", None))
        self.LD_install_path_browse.setText(QCoreApplication.translate("Service", u"\u6d4f\u89c8", None))
        self.label_9.setText(QCoreApplication.translate("Service", u"\u96f7\u7535\u5b9e\u4f8b\u7d22\u5f15", None))
        self.label_32.setText(QCoreApplication.translate("Service", u"\u5728\u96f7\u7535\u591a\u5f00\u5668\u4e2d\u67e5\u770b\u81ea\u5df1\u6b63\u5728\u4f7f\u7528\u7684\u6a21\u62df\u5668\u5b9e\u4f8b\u7d22\u5f15\n"
"\u5982\u679c\u662f\u7b2c\u4e00\u4e2a\u6a21\u62df\u5668\u5c31\u662f0\uff0c\u4f9d\u6b21\u7c7b\u63a8", None))
        self.label_231.setText(QCoreApplication.translate("Service", u"\u8c03\u5ea6\u8bbe\u7f6e", None))
#if QT_CONFIG(tooltip)
        self.label_233.setToolTip(QCoreApplication.translate("Service", u"  - DxCam\n"
"    \u901f\u5ea6\u5feb\uff0c\u4f46\u662f\u6a21\u62df\u5668\u7a97\u53e3\u5fc5\u987b\u5728\u5c4f\u5e55\u8fb9\u754c\u5185\uff0c\u4e0d\u80fd\u6700\u5c0f\u5316\u6216\u88ab\u906e\u6321\n"
"  - MuMu\n"
"    \u4f7f\u7528MuMu\u6a21\u62df\u5668\u7684\u63a5\u53e3\u622a\u56fe\uff0c\u6a21\u62df\u5668\u53ef\u4ee5\u6700\u5c0f\u5316/\u88ab\u906e\u6321\n"
"  - LD\n"
"    \u4f7f\u7528\u96f7\u7535\u6a21\u62df\u5668\u7684\u63a5\u53e3\u622a\u56fe\uff0c\u6a21\u62df\u5668\u53ef\u4ee5\u6700\u5c0f\u5316/\u88ab\u906e\u6321", None))
#endif // QT_CONFIG(tooltip)
        self.label_233.setText(QCoreApplication.translate("Service", u"\u626b\u63cf\u95f4\u9694", None))
        self.label_234.setText(QCoreApplication.translate("Service", u"\u95f4\u9694\u8d8a\u5c0f\u8c03\u5ea6\u5668\u626b\u63cf\u4efb\u52a1\u8d8a\u9891\u7e41\n"
"\u4e00\u822c1000ms\u8db3\u77e3", None))
        self.scan_inerval.setSuffix(QCoreApplication.translate("Service", u" ms", None))
        self.label_227.setText(QCoreApplication.translate("Service", u"\u8fde\u70b9\u952e\u4f4d", None))
        self.label_230.setText(QCoreApplication.translate("Service", u"\u8bf8\u5982\u4e30\u9976\u4e4b\u95f4\uff0c\u6bcf\u65e5\u80dc\u573a\u7b49\u4efb\u52a1\u7684\u5fc5\u8981\u8bbe\u7f6e", None))
#if QT_CONFIG(tooltip)
        self.label_228.setToolTip(QCoreApplication.translate("Service", u"  - DxCam\n"
"    \u901f\u5ea6\u5feb\uff0c\u4f46\u662f\u6a21\u62df\u5668\u7a97\u53e3\u5fc5\u987b\u5728\u5c4f\u5e55\u8fb9\u754c\u5185\uff0c\u4e0d\u80fd\u6700\u5c0f\u5316\u6216\u88ab\u906e\u6321\n"
"  - MuMu\n"
"    \u4f7f\u7528MuMu\u6a21\u62df\u5668\u7684\u63a5\u53e3\u622a\u56fe\uff0c\u6a21\u62df\u5668\u53ef\u4ee5\u6700\u5c0f\u5316/\u88ab\u906e\u6321\n"
"  - LD\n"
"    \u4f7f\u7528\u96f7\u7535\u6a21\u62df\u5668\u7684\u63a5\u53e3\u622a\u56fe\uff0c\u6a21\u62df\u5668\u53ef\u4ee5\u6700\u5c0f\u5316/\u88ab\u906e\u6321", None))
#endif // QT_CONFIG(tooltip)
        self.label_228.setText(QCoreApplication.translate("Service", u"\u952e\u4f4d\u914d\u7f6e", None))
        self.label_229.setText(QCoreApplication.translate("Service", u"\u5173\u95ed\u8c03\u5ea6\u5668\u4e4b\u540e\uff0c\u8fdb\u5165\u7ec3\u4e60\u573a\uff0c\u70b9\u51fb\u53f3\u4fa7\u914d\u7f6e\u6309\u94ae\n"
"\u5c06\u5f39\u51fa\u7a97\u53e3\u4e2d\u7684\u952e\u4f4d\u63a7\u4ef6\u62d6\u52a8\u5230\u56fe\u4e2d\u4f60\u7684\u5bf9\u5e94\u952e\u4f4d\u4e0a", None))
        self.key_map_configuration_button.setText(QCoreApplication.translate("Service", u"\u914d\u7f6e", None))
        self.label_30.setText(QCoreApplication.translate("Service", u"\u4e8c\u7ea7\u5bc6\u7801", None))
        self.label_114.setText(QCoreApplication.translate("Service", u"\u4e8c\u7ea7\u5bc6\u7801", None))
        self.label_115.setText(QCoreApplication.translate("Service", u"\u7528\u6765\u81ea\u52a8\u6267\u884c\u4e00\u4e9b\u9700\u8981\u4e8c\u7ea7\u5bc6\u7801\u7684\u4efb\u52a1\n"
"\u53ea\u5728\u672c\u5730\u5b58\u50a8", None))
        self.secondary_password.setInputMask("")
        self.secondary_password.setPlaceholderText(QCoreApplication.translate("Service", u"\u5fc5\u987b\u4e3a\u516d\u4f4d", None))
    # retranslateUi

