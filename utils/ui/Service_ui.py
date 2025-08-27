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
        Service.resize(1163, 621)
        Service.setStyleSheet(u"/*\n"
"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"font: 15pt \"Microsoft YaHei UI\";\n"
"*/\n"
"font-family:\"Consolas\",\"\u9ed1\u4f53\";\n"
"font-size:15pt;\n"
"\n"
"")
        self.horizontalLayout_56 = QHBoxLayout(Service)
        self.horizontalLayout_56.setSpacing(0)
        self.horizontalLayout_56.setObjectName(u"horizontalLayout_56")
        self.horizontalLayout_56.setContentsMargins(0, 0, 0, 0)
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
        self.verticalLayout_9.setContentsMargins(0, 0, -1, -1)
        self.treeWidget = QTreeWidget(self.widget_11)
        __qtreewidgetitem = QTreeWidgetItem(self.treeWidget)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        __qtreewidgetitem1 = QTreeWidgetItem(self.treeWidget)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(__qtreewidgetitem1)
        __qtreewidgetitem2 = QTreeWidgetItem(self.treeWidget)
        QTreeWidgetItem(__qtreewidgetitem2)
        QTreeWidgetItem(__qtreewidgetitem2)
        QTreeWidgetItem(__qtreewidgetitem2)
        QTreeWidgetItem(__qtreewidgetitem2)
        __qtreewidgetitem3 = QTreeWidgetItem(self.treeWidget)
        QTreeWidgetItem(__qtreewidgetitem3)
        QTreeWidgetItem(__qtreewidgetitem3)
        QTreeWidgetItem(self.treeWidget)
        QTreeWidgetItem(self.treeWidget)
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
        self.Overview_Panel_widget = QWidget()
        self.Overview_Panel_widget.setObjectName(u"Overview_Panel_widget")
        self.Overview_Panel_widget.setEnabled(True)
        self.horizontalLayout_2 = QHBoxLayout(self.Overview_Panel_widget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
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
"}")
        self.horizontalLayout_3 = QHBoxLayout(self.widget_4)
        self.horizontalLayout_3.setSpacing(4)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 10, 0)
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
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush2)
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush2)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush4)
#endif
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush5)
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush2)
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush2)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush4)
#endif
        brush6 = QBrush(QColor(120, 120, 120, 255))
        brush6.setStyle(Qt.BrushStyle.SolidPattern)
        palette3.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush6)
        palette3.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush2)
        palette3.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush2)
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
        palette4.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush2)
        palette4.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush2)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette4.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush4)
#endif
        palette4.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush5)
        palette4.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush2)
        palette4.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush2)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette4.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush4)
#endif
        palette4.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush6)
        palette4.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush2)
        palette4.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush2)
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
        self.scroll_area_ready_content.setGeometry(QRect(0, 0, 232, 87))
        self.scrollArea_2.setWidget(self.scroll_area_ready_content)

        self.verticalLayout_6.addWidget(self.scrollArea_2)


        self.verticalLayout_3.addWidget(self.widget_6)

        self.widget_7 = QWidget(self.widget_2)
        self.widget_7.setObjectName(u"widget_7")
        self.widget_7.setStyleSheet(u"#widget_7 {  /* \u4ec5\u5339\u914d objectName \u4e3a myWidget \u7684\u63a7\u4ef6 */\n"
"    background-color: rgb(222, 222, 222);\n"
"border-radius: 10px;\n"
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
        palette5.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush2)
        palette5.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush2)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette5.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush4)
#endif
        palette5.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush5)
        palette5.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush2)
        palette5.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush2)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette5.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush4)
#endif
        palette5.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush6)
        palette5.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush2)
        palette5.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush2)
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
        self.scroll_area_wait_content.setGeometry(QRect(0, 0, 232, 187))
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
        self.label_5 = QLabel(self.widget_12)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font1)
        self.label_5.setStyleSheet(u"font-size:25px;\n"
"")
        self.label_5.setIndent(10)

        self.horizontalLayout_4.addWidget(self.label_5, 0, Qt.AlignmentFlag.AlignLeft)

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
        self.DengLuJiangLi_widget = QWidget()
        self.DengLuJiangLi_widget.setObjectName(u"DengLuJiangLi_widget")
        self.horizontalLayout_25 = QHBoxLayout(self.DengLuJiangLi_widget)
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.widget_44 = QWidget(self.DengLuJiangLi_widget)
        self.widget_44.setObjectName(u"widget_44")
        self.widget_44.setStyleSheet(u"")
        self.horizontalLayout_24 = QHBoxLayout(self.widget_44)
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.horizontalSpacer_23 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_24.addItem(self.horizontalSpacer_23)

        self.scrollArea_15 = QScrollArea(self.widget_44)
        self.scrollArea_15.setObjectName(u"scrollArea_15")
        self.scrollArea_15.setMinimumSize(QSize(600, 0))
        self.scrollArea_15.setWidgetResizable(True)
        self.scrollArea_15.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_12 = QWidget()
        self.scrollAreaWidgetContents_12.setObjectName(u"scrollAreaWidgetContents_12")
        self.scrollAreaWidgetContents_12.setGeometry(QRect(0, 0, 566, 234))
        self.verticalLayout_73 = QVBoxLayout(self.scrollAreaWidgetContents_12)
        self.verticalLayout_73.setSpacing(20)
        self.verticalLayout_73.setObjectName(u"verticalLayout_73")
        self.widget_45 = QWidget(self.scrollAreaWidgetContents_12)
        self.widget_45.setObjectName(u"widget_45")
        self.widget_45.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_74 = QVBoxLayout(self.widget_45)
        self.verticalLayout_74.setObjectName(u"verticalLayout_74")
        self.verticalLayout_74.setContentsMargins(-1, 7, -1, -1)
        self.label_73 = QLabel(self.widget_45)
        self.label_73.setObjectName(u"label_73")
        self.label_73.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_74.addWidget(self.label_73)

        self.frame_19 = QFrame(self.widget_45)
        self.frame_19.setObjectName(u"frame_19")
        self.frame_19.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_19.setFrameShape(QFrame.Shape.HLine)
        self.frame_19.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_74.addWidget(self.frame_19)

        self.gridLayout_24 = QGridLayout()
        self.gridLayout_24.setObjectName(u"gridLayout_24")
        self.gridLayout_24.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_75 = QVBoxLayout()
        self.verticalLayout_75.setObjectName(u"verticalLayout_75")
        self.label_74 = QLabel(self.widget_45)
        self.label_74.setObjectName(u"label_74")

        self.verticalLayout_75.addWidget(self.label_74)

        self.label_75 = QLabel(self.widget_45)
        self.label_75.setObjectName(u"label_75")
        self.label_75.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_75.addWidget(self.label_75)


        self.gridLayout_24.addLayout(self.verticalLayout_75, 0, 0, 1, 1)

        self.DengLuJiangLi_Enable = QCheckBox(self.widget_45)
        self.DengLuJiangLi_Enable.setObjectName(u"DengLuJiangLi_Enable")
        self.DengLuJiangLi_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.DengLuJiangLi_Enable.setStyleSheet(u"")

        self.gridLayout_24.addWidget(self.DengLuJiangLi_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_76 = QVBoxLayout()
        self.verticalLayout_76.setObjectName(u"verticalLayout_76")
        self.label_132 = QLabel(self.widget_45)
        self.label_132.setObjectName(u"label_132")

        self.verticalLayout_76.addWidget(self.label_132)

        self.label_133 = QLabel(self.widget_45)
        self.label_133.setObjectName(u"label_133")
        self.label_133.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_76.addWidget(self.label_133)


        self.gridLayout_24.addLayout(self.verticalLayout_76, 1, 0, 1, 1)

        self.DengLuJiangLi_next_execute_time = QLineEdit(self.widget_45)
        self.DengLuJiangLi_next_execute_time.setObjectName(u"DengLuJiangLi_next_execute_time")
        self.DengLuJiangLi_next_execute_time.setMinimumSize(QSize(200, 0))
        self.DengLuJiangLi_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.DengLuJiangLi_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_24.addWidget(self.DengLuJiangLi_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_24.setColumnStretch(0, 5)
        self.gridLayout_24.setColumnStretch(1, 2)

        self.verticalLayout_74.addLayout(self.gridLayout_24)


        self.verticalLayout_73.addWidget(self.widget_45)

        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_73.addItem(self.verticalSpacer_7)

        self.scrollArea_15.setWidget(self.scrollAreaWidgetContents_12)

        self.horizontalLayout_24.addWidget(self.scrollArea_15)

        self.horizontalSpacer_24 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_24.addItem(self.horizontalSpacer_24)

        self.horizontalLayout_24.setStretch(0, 1)
        self.horizontalLayout_24.setStretch(1, 5)
        self.horizontalLayout_24.setStretch(2, 1)

        self.horizontalLayout_25.addWidget(self.widget_44)

        self.stackedWidget.addWidget(self.DengLuJiangLi_widget)
        self.PaiHangBangDianZan_widget = QWidget()
        self.PaiHangBangDianZan_widget.setObjectName(u"PaiHangBangDianZan_widget")
        self.horizontalLayout_32 = QHBoxLayout(self.PaiHangBangDianZan_widget)
        self.horizontalLayout_32.setObjectName(u"horizontalLayout_32")
        self.widget_52 = QWidget(self.PaiHangBangDianZan_widget)
        self.widget_52.setObjectName(u"widget_52")
        self.widget_52.setStyleSheet(u";")
        self.horizontalLayout_31 = QHBoxLayout(self.widget_52)
        self.horizontalLayout_31.setObjectName(u"horizontalLayout_31")
        self.horizontalSpacer_31 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_31.addItem(self.horizontalSpacer_31)

        self.scrollArea_19 = QScrollArea(self.widget_52)
        self.scrollArea_19.setObjectName(u"scrollArea_19")
        self.scrollArea_19.setMinimumSize(QSize(600, 0))
        self.scrollArea_19.setWidgetResizable(True)
        self.scrollArea_19.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_16 = QWidget()
        self.scrollAreaWidgetContents_16.setObjectName(u"scrollAreaWidgetContents_16")
        self.scrollAreaWidgetContents_16.setGeometry(QRect(0, 0, 566, 234))
        self.verticalLayout_89 = QVBoxLayout(self.scrollAreaWidgetContents_16)
        self.verticalLayout_89.setSpacing(20)
        self.verticalLayout_89.setObjectName(u"verticalLayout_89")
        self.widget_53 = QWidget(self.scrollAreaWidgetContents_16)
        self.widget_53.setObjectName(u"widget_53")
        self.widget_53.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_90 = QVBoxLayout(self.widget_53)
        self.verticalLayout_90.setObjectName(u"verticalLayout_90")
        self.verticalLayout_90.setContentsMargins(-1, 7, -1, -1)
        self.label_85 = QLabel(self.widget_53)
        self.label_85.setObjectName(u"label_85")
        self.label_85.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_90.addWidget(self.label_85)

        self.frame_23 = QFrame(self.widget_53)
        self.frame_23.setObjectName(u"frame_23")
        self.frame_23.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_23.setFrameShape(QFrame.Shape.HLine)
        self.frame_23.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_90.addWidget(self.frame_23)

        self.gridLayout_28 = QGridLayout()
        self.gridLayout_28.setObjectName(u"gridLayout_28")
        self.gridLayout_28.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_91 = QVBoxLayout()
        self.verticalLayout_91.setObjectName(u"verticalLayout_91")
        self.label_86 = QLabel(self.widget_53)
        self.label_86.setObjectName(u"label_86")

        self.verticalLayout_91.addWidget(self.label_86)

        self.label_87 = QLabel(self.widget_53)
        self.label_87.setObjectName(u"label_87")
        self.label_87.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_91.addWidget(self.label_87)


        self.gridLayout_28.addLayout(self.verticalLayout_91, 0, 0, 1, 1)

        self.PaiHangBangDianZan_Enable = QCheckBox(self.widget_53)
        self.PaiHangBangDianZan_Enable.setObjectName(u"PaiHangBangDianZan_Enable")
        self.PaiHangBangDianZan_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.PaiHangBangDianZan_Enable.setStyleSheet(u"")

        self.gridLayout_28.addWidget(self.PaiHangBangDianZan_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_92 = QVBoxLayout()
        self.verticalLayout_92.setObjectName(u"verticalLayout_92")
        self.label_140 = QLabel(self.widget_53)
        self.label_140.setObjectName(u"label_140")

        self.verticalLayout_92.addWidget(self.label_140)

        self.label_141 = QLabel(self.widget_53)
        self.label_141.setObjectName(u"label_141")
        self.label_141.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_92.addWidget(self.label_141)


        self.gridLayout_28.addLayout(self.verticalLayout_92, 1, 0, 1, 1)

        self.PaiHangBangDianZan_next_execute_time = QLineEdit(self.widget_53)
        self.PaiHangBangDianZan_next_execute_time.setObjectName(u"PaiHangBangDianZan_next_execute_time")
        self.PaiHangBangDianZan_next_execute_time.setMinimumSize(QSize(200, 0))
        self.PaiHangBangDianZan_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.PaiHangBangDianZan_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_28.addWidget(self.PaiHangBangDianZan_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_28.setColumnStretch(0, 5)
        self.gridLayout_28.setColumnStretch(1, 2)

        self.verticalLayout_90.addLayout(self.gridLayout_28)


        self.verticalLayout_89.addWidget(self.widget_53)

        self.verticalSpacer_11 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_89.addItem(self.verticalSpacer_11)

        self.scrollArea_19.setWidget(self.scrollAreaWidgetContents_16)

        self.horizontalLayout_31.addWidget(self.scrollArea_19)

        self.horizontalSpacer_32 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_31.addItem(self.horizontalSpacer_32)

        self.horizontalLayout_31.setStretch(0, 1)
        self.horizontalLayout_31.setStretch(1, 5)
        self.horizontalLayout_31.setStretch(2, 1)

        self.horizontalLayout_32.addWidget(self.widget_52)

        self.stackedWidget.addWidget(self.PaiHangBangDianZan_widget)
        self.MeiYueQianDao_widget = QWidget()
        self.MeiYueQianDao_widget.setObjectName(u"MeiYueQianDao_widget")
        self.horizontalLayout_34 = QHBoxLayout(self.MeiYueQianDao_widget)
        self.horizontalLayout_34.setObjectName(u"horizontalLayout_34")
        self.widget_54 = QWidget(self.MeiYueQianDao_widget)
        self.widget_54.setObjectName(u"widget_54")
        self.widget_54.setStyleSheet(u"")
        self.horizontalLayout_33 = QHBoxLayout(self.widget_54)
        self.horizontalLayout_33.setObjectName(u"horizontalLayout_33")
        self.horizontalSpacer_33 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_33.addItem(self.horizontalSpacer_33)

        self.scrollArea_20 = QScrollArea(self.widget_54)
        self.scrollArea_20.setObjectName(u"scrollArea_20")
        self.scrollArea_20.setMinimumSize(QSize(600, 0))
        self.scrollArea_20.setWidgetResizable(True)
        self.scrollArea_20.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_17 = QWidget()
        self.scrollAreaWidgetContents_17.setObjectName(u"scrollAreaWidgetContents_17")
        self.scrollAreaWidgetContents_17.setGeometry(QRect(0, 0, 566, 234))
        self.verticalLayout_93 = QVBoxLayout(self.scrollAreaWidgetContents_17)
        self.verticalLayout_93.setSpacing(20)
        self.verticalLayout_93.setObjectName(u"verticalLayout_93")
        self.widget_55 = QWidget(self.scrollAreaWidgetContents_17)
        self.widget_55.setObjectName(u"widget_55")
        self.widget_55.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_94 = QVBoxLayout(self.widget_55)
        self.verticalLayout_94.setObjectName(u"verticalLayout_94")
        self.verticalLayout_94.setContentsMargins(-1, 7, -1, -1)
        self.label_88 = QLabel(self.widget_55)
        self.label_88.setObjectName(u"label_88")
        self.label_88.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_94.addWidget(self.label_88)

        self.frame_24 = QFrame(self.widget_55)
        self.frame_24.setObjectName(u"frame_24")
        self.frame_24.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_24.setFrameShape(QFrame.Shape.HLine)
        self.frame_24.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_94.addWidget(self.frame_24)

        self.gridLayout_29 = QGridLayout()
        self.gridLayout_29.setObjectName(u"gridLayout_29")
        self.gridLayout_29.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_95 = QVBoxLayout()
        self.verticalLayout_95.setObjectName(u"verticalLayout_95")
        self.label_89 = QLabel(self.widget_55)
        self.label_89.setObjectName(u"label_89")

        self.verticalLayout_95.addWidget(self.label_89)

        self.label_90 = QLabel(self.widget_55)
        self.label_90.setObjectName(u"label_90")
        self.label_90.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_95.addWidget(self.label_90)


        self.gridLayout_29.addLayout(self.verticalLayout_95, 0, 0, 1, 1)

        self.MeiYueQianDao_Enable = QCheckBox(self.widget_55)
        self.MeiYueQianDao_Enable.setObjectName(u"MeiYueQianDao_Enable")
        self.MeiYueQianDao_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.MeiYueQianDao_Enable.setStyleSheet(u"")

        self.gridLayout_29.addWidget(self.MeiYueQianDao_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_96 = QVBoxLayout()
        self.verticalLayout_96.setObjectName(u"verticalLayout_96")
        self.label_142 = QLabel(self.widget_55)
        self.label_142.setObjectName(u"label_142")

        self.verticalLayout_96.addWidget(self.label_142)

        self.label_143 = QLabel(self.widget_55)
        self.label_143.setObjectName(u"label_143")
        self.label_143.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_96.addWidget(self.label_143)


        self.gridLayout_29.addLayout(self.verticalLayout_96, 1, 0, 1, 1)

        self.MeiYueQianDao_next_execute_time = QLineEdit(self.widget_55)
        self.MeiYueQianDao_next_execute_time.setObjectName(u"MeiYueQianDao_next_execute_time")
        self.MeiYueQianDao_next_execute_time.setMinimumSize(QSize(200, 0))
        self.MeiYueQianDao_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.MeiYueQianDao_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_29.addWidget(self.MeiYueQianDao_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_29.setColumnStretch(0, 5)
        self.gridLayout_29.setColumnStretch(1, 2)

        self.verticalLayout_94.addLayout(self.gridLayout_29)


        self.verticalLayout_93.addWidget(self.widget_55)

        self.verticalSpacer_12 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_93.addItem(self.verticalSpacer_12)

        self.scrollArea_20.setWidget(self.scrollAreaWidgetContents_17)

        self.horizontalLayout_33.addWidget(self.scrollArea_20)

        self.horizontalSpacer_34 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_33.addItem(self.horizontalSpacer_34)

        self.horizontalLayout_33.setStretch(0, 1)
        self.horizontalLayout_33.setStretch(1, 5)
        self.horizontalLayout_33.setStretch(2, 1)

        self.horizontalLayout_34.addWidget(self.widget_54)

        self.stackedWidget.addWidget(self.MeiYueQianDao_widget)
        self.GouMaiTiLi_widget = QWidget()
        self.GouMaiTiLi_widget.setObjectName(u"GouMaiTiLi_widget")
        self.horizontalLayout_14 = QHBoxLayout(self.GouMaiTiLi_widget)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.widget_24 = QWidget(self.GouMaiTiLi_widget)
        self.widget_24.setObjectName(u"widget_24")
        self.widget_24.setStyleSheet(u"")
        self.horizontalLayout_13 = QHBoxLayout(self.widget_24)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_11)

        self.scrollArea_9 = QScrollArea(self.widget_24)
        self.scrollArea_9.setObjectName(u"scrollArea_9")
        self.scrollArea_9.setMinimumSize(QSize(600, 0))
        self.scrollArea_9.setWidgetResizable(True)
        self.scrollArea_9.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_6 = QWidget()
        self.scrollAreaWidgetContents_6.setObjectName(u"scrollAreaWidgetContents_6")
        self.scrollAreaWidgetContents_6.setGeometry(QRect(0, 0, 566, 416))
        self.verticalLayout_46 = QVBoxLayout(self.scrollAreaWidgetContents_6)
        self.verticalLayout_46.setSpacing(20)
        self.verticalLayout_46.setObjectName(u"verticalLayout_46")
        self.widget_30 = QWidget(self.scrollAreaWidgetContents_6)
        self.widget_30.setObjectName(u"widget_30")
        self.widget_30.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_41 = QVBoxLayout(self.widget_30)
        self.verticalLayout_41.setObjectName(u"verticalLayout_41")
        self.verticalLayout_41.setContentsMargins(-1, 7, -1, -1)
        self.label_55 = QLabel(self.widget_30)
        self.label_55.setObjectName(u"label_55")
        self.label_55.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_41.addWidget(self.label_55)

        self.frame_12 = QFrame(self.widget_30)
        self.frame_12.setObjectName(u"frame_12")
        self.frame_12.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_12.setFrameShape(QFrame.Shape.HLine)
        self.frame_12.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_41.addWidget(self.frame_12)

        self.gridLayout_18 = QGridLayout()
        self.gridLayout_18.setObjectName(u"gridLayout_18")
        self.gridLayout_18.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_54 = QVBoxLayout()
        self.verticalLayout_54.setObjectName(u"verticalLayout_54")
        self.label_56 = QLabel(self.widget_30)
        self.label_56.setObjectName(u"label_56")

        self.verticalLayout_54.addWidget(self.label_56)

        self.label_57 = QLabel(self.widget_30)
        self.label_57.setObjectName(u"label_57")
        self.label_57.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_54.addWidget(self.label_57)


        self.gridLayout_18.addLayout(self.verticalLayout_54, 0, 0, 1, 1)

        self.GouMaiTiLi_Enable = QCheckBox(self.widget_30)
        self.GouMaiTiLi_Enable.setObjectName(u"GouMaiTiLi_Enable")
        self.GouMaiTiLi_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.GouMaiTiLi_Enable.setStyleSheet(u"")

        self.gridLayout_18.addWidget(self.GouMaiTiLi_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_55 = QVBoxLayout()
        self.verticalLayout_55.setObjectName(u"verticalLayout_55")
        self.label_120 = QLabel(self.widget_30)
        self.label_120.setObjectName(u"label_120")

        self.verticalLayout_55.addWidget(self.label_120)

        self.label_121 = QLabel(self.widget_30)
        self.label_121.setObjectName(u"label_121")
        self.label_121.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_55.addWidget(self.label_121)


        self.gridLayout_18.addLayout(self.verticalLayout_55, 1, 0, 1, 1)

        self.GouMaiTiLi_next_execute_time = QLineEdit(self.widget_30)
        self.GouMaiTiLi_next_execute_time.setObjectName(u"GouMaiTiLi_next_execute_time")
        self.GouMaiTiLi_next_execute_time.setMinimumSize(QSize(200, 0))
        self.GouMaiTiLi_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.GouMaiTiLi_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_18.addWidget(self.GouMaiTiLi_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_18.setColumnStretch(0, 5)
        self.gridLayout_18.setColumnStretch(1, 2)

        self.verticalLayout_41.addLayout(self.gridLayout_18)


        self.verticalLayout_46.addWidget(self.widget_30)

        self.widget_26 = QWidget(self.scrollAreaWidgetContents_6)
        self.widget_26.setObjectName(u"widget_26")
        self.widget_26.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_45 = QVBoxLayout(self.widget_26)
        self.verticalLayout_45.setSpacing(6)
        self.verticalLayout_45.setObjectName(u"verticalLayout_45")
        self.verticalLayout_45.setContentsMargins(-1, 7, -1, -1)
        self.label_41 = QLabel(self.widget_26)
        self.label_41.setObjectName(u"label_41")
        self.label_41.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_45.addWidget(self.label_41)

        self.frame_10 = QFrame(self.widget_26)
        self.frame_10.setObjectName(u"frame_10")
        self.frame_10.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_10.setFrameShape(QFrame.Shape.HLine)
        self.frame_10.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_45.addWidget(self.frame_10)

        self.gridLayout_13 = QGridLayout()
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.gridLayout_13.setVerticalSpacing(0)
        self.gridLayout_13.setContentsMargins(10, 10, 0, 0)
        self.widget_32 = QWidget(self.widget_26)
        self.widget_32.setObjectName(u"widget_32")
        self.verticalLayout_44 = QVBoxLayout(self.widget_32)
        self.verticalLayout_44.setSpacing(6)
        self.verticalLayout_44.setObjectName(u"verticalLayout_44")
        self.verticalLayout_44.setContentsMargins(0, 0, 0, 0)
        self.label_42 = QLabel(self.widget_32)
        self.label_42.setObjectName(u"label_42")

        self.verticalLayout_44.addWidget(self.label_42)

        self.label_43 = QLabel(self.widget_32)
        self.label_43.setObjectName(u"label_43")
        self.label_43.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")
        self.label_43.setTextFormat(Qt.TextFormat.AutoText)
        self.label_43.setWordWrap(True)

        self.verticalLayout_44.addWidget(self.label_43)


        self.gridLayout_13.addWidget(self.widget_32, 0, 0, 1, 1)

        self.GouMaiTiLi_times = QSpinBox(self.widget_26)
        self.GouMaiTiLi_times.setObjectName(u"GouMaiTiLi_times")
        self.GouMaiTiLi_times.setMaximumSize(QSize(80, 35))
        self.GouMaiTiLi_times.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.GouMaiTiLi_times.setWrapping(False)
        self.GouMaiTiLi_times.setFrame(True)
        self.GouMaiTiLi_times.setMaximum(30)
        self.GouMaiTiLi_times.setValue(0)

        self.gridLayout_13.addWidget(self.GouMaiTiLi_times, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter)

        self.gridLayout_13.setColumnStretch(0, 5)
        self.gridLayout_13.setColumnStretch(1, 2)

        self.verticalLayout_45.addLayout(self.gridLayout_13)


        self.verticalLayout_46.addWidget(self.widget_26)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_46.addItem(self.verticalSpacer)

        self.scrollArea_9.setWidget(self.scrollAreaWidgetContents_6)

        self.horizontalLayout_13.addWidget(self.scrollArea_9)

        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_12)

        self.horizontalLayout_13.setStretch(0, 1)
        self.horizontalLayout_13.setStretch(1, 5)
        self.horizontalLayout_13.setStretch(2, 1)

        self.horizontalLayout_14.addWidget(self.widget_24)

        self.stackedWidget.addWidget(self.GouMaiTiLi_widget)
        self.JinBiZhaoCai_widget = QWidget()
        self.JinBiZhaoCai_widget.setObjectName(u"JinBiZhaoCai_widget")
        self.horizontalLayout_9 = QHBoxLayout(self.JinBiZhaoCai_widget)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.widget_27 = QWidget(self.JinBiZhaoCai_widget)
        self.widget_27.setObjectName(u"widget_27")
        self.widget_27.setStyleSheet(u"")
        self.horizontalLayout_15 = QHBoxLayout(self.widget_27)
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_15.addItem(self.horizontalSpacer_13)

        self.scrollArea_10 = QScrollArea(self.widget_27)
        self.scrollArea_10.setObjectName(u"scrollArea_10")
        self.scrollArea_10.setMinimumSize(QSize(600, 0))
        self.scrollArea_10.setWidgetResizable(True)
        self.scrollArea_10.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_7 = QWidget()
        self.scrollAreaWidgetContents_7.setObjectName(u"scrollAreaWidgetContents_7")
        self.scrollAreaWidgetContents_7.setGeometry(QRect(0, 0, 566, 452))
        self.verticalLayout_47 = QVBoxLayout(self.scrollAreaWidgetContents_7)
        self.verticalLayout_47.setSpacing(20)
        self.verticalLayout_47.setObjectName(u"verticalLayout_47")
        self.widget_33 = QWidget(self.scrollAreaWidgetContents_7)
        self.widget_33.setObjectName(u"widget_33")
        self.widget_33.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_48 = QVBoxLayout(self.widget_33)
        self.verticalLayout_48.setObjectName(u"verticalLayout_48")
        self.verticalLayout_48.setContentsMargins(-1, 7, -1, -1)
        self.label_58 = QLabel(self.widget_33)
        self.label_58.setObjectName(u"label_58")
        self.label_58.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_48.addWidget(self.label_58)

        self.frame_13 = QFrame(self.widget_33)
        self.frame_13.setObjectName(u"frame_13")
        self.frame_13.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_13.setFrameShape(QFrame.Shape.HLine)
        self.frame_13.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_48.addWidget(self.frame_13)

        self.gridLayout_19 = QGridLayout()
        self.gridLayout_19.setObjectName(u"gridLayout_19")
        self.gridLayout_19.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_56 = QVBoxLayout()
        self.verticalLayout_56.setObjectName(u"verticalLayout_56")
        self.label_59 = QLabel(self.widget_33)
        self.label_59.setObjectName(u"label_59")

        self.verticalLayout_56.addWidget(self.label_59)

        self.label_60 = QLabel(self.widget_33)
        self.label_60.setObjectName(u"label_60")
        self.label_60.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_56.addWidget(self.label_60)


        self.gridLayout_19.addLayout(self.verticalLayout_56, 0, 0, 1, 1)

        self.JinBiZhaoCai_Enable = QCheckBox(self.widget_33)
        self.JinBiZhaoCai_Enable.setObjectName(u"JinBiZhaoCai_Enable")
        self.JinBiZhaoCai_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.JinBiZhaoCai_Enable.setStyleSheet(u"")

        self.gridLayout_19.addWidget(self.JinBiZhaoCai_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_57 = QVBoxLayout()
        self.verticalLayout_57.setObjectName(u"verticalLayout_57")
        self.label_122 = QLabel(self.widget_33)
        self.label_122.setObjectName(u"label_122")

        self.verticalLayout_57.addWidget(self.label_122)

        self.label_123 = QLabel(self.widget_33)
        self.label_123.setObjectName(u"label_123")
        self.label_123.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_57.addWidget(self.label_123)


        self.gridLayout_19.addLayout(self.verticalLayout_57, 1, 0, 1, 1)

        self.JinBiZhaoCai_next_execute_time = QLineEdit(self.widget_33)
        self.JinBiZhaoCai_next_execute_time.setObjectName(u"JinBiZhaoCai_next_execute_time")
        self.JinBiZhaoCai_next_execute_time.setMinimumSize(QSize(200, 0))
        self.JinBiZhaoCai_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.JinBiZhaoCai_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_19.addWidget(self.JinBiZhaoCai_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_19.setColumnStretch(0, 5)
        self.gridLayout_19.setColumnStretch(1, 2)

        self.verticalLayout_48.addLayout(self.gridLayout_19)


        self.verticalLayout_47.addWidget(self.widget_33)

        self.widget_28 = QWidget(self.scrollAreaWidgetContents_7)
        self.widget_28.setObjectName(u"widget_28")
        self.widget_28.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_49 = QVBoxLayout(self.widget_28)
        self.verticalLayout_49.setSpacing(6)
        self.verticalLayout_49.setObjectName(u"verticalLayout_49")
        self.verticalLayout_49.setContentsMargins(-1, 7, -1, -1)
        self.label_44 = QLabel(self.widget_28)
        self.label_44.setObjectName(u"label_44")
        self.label_44.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_49.addWidget(self.label_44)

        self.frame_11 = QFrame(self.widget_28)
        self.frame_11.setObjectName(u"frame_11")
        self.frame_11.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_11.setFrameShape(QFrame.Shape.HLine)
        self.frame_11.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_49.addWidget(self.frame_11)

        self.gridLayout_14 = QGridLayout()
        self.gridLayout_14.setObjectName(u"gridLayout_14")
        self.gridLayout_14.setVerticalSpacing(0)
        self.gridLayout_14.setContentsMargins(10, 10, 0, 15)
        self.widget_34 = QWidget(self.widget_28)
        self.widget_34.setObjectName(u"widget_34")
        self.widget_34.setMinimumSize(QSize(0, 70))
        self.verticalLayout_50 = QVBoxLayout(self.widget_34)
        self.verticalLayout_50.setSpacing(6)
        self.verticalLayout_50.setObjectName(u"verticalLayout_50")
        self.verticalLayout_50.setContentsMargins(0, 0, 0, 0)
        self.label_45 = QLabel(self.widget_34)
        self.label_45.setObjectName(u"label_45")

        self.verticalLayout_50.addWidget(self.label_45)

        self.label_46 = QLabel(self.widget_34)
        self.label_46.setObjectName(u"label_46")
        sizePolicy2.setHeightForWidth(self.label_46.sizePolicy().hasHeightForWidth())
        self.label_46.setSizePolicy(sizePolicy2)
        self.label_46.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")
        self.label_46.setTextFormat(Qt.TextFormat.AutoText)
        self.label_46.setWordWrap(True)
        self.label_46.setMargin(0)

        self.verticalLayout_50.addWidget(self.label_46)


        self.gridLayout_14.addWidget(self.widget_34, 0, 0, 1, 1)

        self.JinBiZhaoCai_times = QSpinBox(self.widget_28)
        self.JinBiZhaoCai_times.setObjectName(u"JinBiZhaoCai_times")
        self.JinBiZhaoCai_times.setMaximumSize(QSize(80, 35))
        self.JinBiZhaoCai_times.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.JinBiZhaoCai_times.setWrapping(False)
        self.JinBiZhaoCai_times.setFrame(True)
        self.JinBiZhaoCai_times.setMaximum(120)
        self.JinBiZhaoCai_times.setValue(0)

        self.gridLayout_14.addWidget(self.JinBiZhaoCai_times, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter)

        self.gridLayout_14.setColumnStretch(0, 5)
        self.gridLayout_14.setColumnStretch(1, 2)

        self.verticalLayout_49.addLayout(self.gridLayout_14)


        self.verticalLayout_47.addWidget(self.widget_28)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_47.addItem(self.verticalSpacer_2)

        self.scrollArea_10.setWidget(self.scrollAreaWidgetContents_7)

        self.horizontalLayout_15.addWidget(self.scrollArea_10)

        self.horizontalSpacer_14 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_15.addItem(self.horizontalSpacer_14)

        self.horizontalLayout_15.setStretch(0, 1)
        self.horizontalLayout_15.setStretch(1, 5)
        self.horizontalLayout_15.setStretch(2, 1)

        self.horizontalLayout_9.addWidget(self.widget_27)

        self.stackedWidget.addWidget(self.JinBiZhaoCai_widget)
        self.XiaoDuiTuXi_widget = QWidget()
        self.XiaoDuiTuXi_widget.setObjectName(u"XiaoDuiTuXi_widget")
        self.horizontalLayout_17 = QHBoxLayout(self.XiaoDuiTuXi_widget)
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.widget_29 = QWidget(self.XiaoDuiTuXi_widget)
        self.widget_29.setObjectName(u"widget_29")
        self.widget_29.setStyleSheet(u"")
        self.horizontalLayout_16 = QHBoxLayout(self.widget_29)
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.horizontalSpacer_15 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_15)

        self.scrollArea_11 = QScrollArea(self.widget_29)
        self.scrollArea_11.setObjectName(u"scrollArea_11")
        self.scrollArea_11.setMinimumSize(QSize(600, 0))
        self.scrollArea_11.setWidgetResizable(True)
        self.scrollArea_11.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_8 = QWidget()
        self.scrollAreaWidgetContents_8.setObjectName(u"scrollAreaWidgetContents_8")
        self.scrollAreaWidgetContents_8.setGeometry(QRect(0, 0, 566, 455))
        self.verticalLayout_51 = QVBoxLayout(self.scrollAreaWidgetContents_8)
        self.verticalLayout_51.setSpacing(20)
        self.verticalLayout_51.setObjectName(u"verticalLayout_51")
        self.widget_35 = QWidget(self.scrollAreaWidgetContents_8)
        self.widget_35.setObjectName(u"widget_35")
        self.widget_35.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_52 = QVBoxLayout(self.widget_35)
        self.verticalLayout_52.setObjectName(u"verticalLayout_52")
        self.verticalLayout_52.setContentsMargins(-1, 7, -1, -1)
        self.label_61 = QLabel(self.widget_35)
        self.label_61.setObjectName(u"label_61")
        self.label_61.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_52.addWidget(self.label_61)

        self.frame_14 = QFrame(self.widget_35)
        self.frame_14.setObjectName(u"frame_14")
        self.frame_14.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_14.setFrameShape(QFrame.Shape.HLine)
        self.frame_14.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_52.addWidget(self.frame_14)

        self.gridLayout_20 = QGridLayout()
        self.gridLayout_20.setObjectName(u"gridLayout_20")
        self.gridLayout_20.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_58 = QVBoxLayout()
        self.verticalLayout_58.setObjectName(u"verticalLayout_58")
        self.label_62 = QLabel(self.widget_35)
        self.label_62.setObjectName(u"label_62")

        self.verticalLayout_58.addWidget(self.label_62)

        self.label_63 = QLabel(self.widget_35)
        self.label_63.setObjectName(u"label_63")
        self.label_63.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_58.addWidget(self.label_63)


        self.gridLayout_20.addLayout(self.verticalLayout_58, 0, 0, 1, 1)

        self.XiaoDuiTuXi_Enable = QCheckBox(self.widget_35)
        self.XiaoDuiTuXi_Enable.setObjectName(u"XiaoDuiTuXi_Enable")
        self.XiaoDuiTuXi_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.XiaoDuiTuXi_Enable.setStyleSheet(u"")

        self.gridLayout_20.addWidget(self.XiaoDuiTuXi_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_59 = QVBoxLayout()
        self.verticalLayout_59.setObjectName(u"verticalLayout_59")
        self.label_124 = QLabel(self.widget_35)
        self.label_124.setObjectName(u"label_124")

        self.verticalLayout_59.addWidget(self.label_124)

        self.label_125 = QLabel(self.widget_35)
        self.label_125.setObjectName(u"label_125")
        self.label_125.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_59.addWidget(self.label_125)


        self.gridLayout_20.addLayout(self.verticalLayout_59, 1, 0, 1, 1)

        self.XiaoDuiTuXi_next_execute_time = QLineEdit(self.widget_35)
        self.XiaoDuiTuXi_next_execute_time.setObjectName(u"XiaoDuiTuXi_next_execute_time")
        self.XiaoDuiTuXi_next_execute_time.setMinimumSize(QSize(200, 0))
        self.XiaoDuiTuXi_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.XiaoDuiTuXi_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_20.addWidget(self.XiaoDuiTuXi_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_20.setColumnStretch(0, 5)
        self.gridLayout_20.setColumnStretch(1, 2)

        self.verticalLayout_52.addLayout(self.gridLayout_20)


        self.verticalLayout_51.addWidget(self.widget_35)

        self.widget_36 = QWidget(self.scrollAreaWidgetContents_8)
        self.widget_36.setObjectName(u"widget_36")
        self.widget_36.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_53 = QVBoxLayout(self.widget_36)
        self.verticalLayout_53.setSpacing(6)
        self.verticalLayout_53.setObjectName(u"verticalLayout_53")
        self.verticalLayout_53.setContentsMargins(-1, 7, -1, -1)
        self.label_47 = QLabel(self.widget_36)
        self.label_47.setObjectName(u"label_47")
        self.label_47.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_53.addWidget(self.label_47)

        self.frame_15 = QFrame(self.widget_36)
        self.frame_15.setObjectName(u"frame_15")
        self.frame_15.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_15.setFrameShape(QFrame.Shape.HLine)
        self.frame_15.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_53.addWidget(self.frame_15)

        self.gridLayout_15 = QGridLayout()
        self.gridLayout_15.setObjectName(u"gridLayout_15")
        self.gridLayout_15.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        self.gridLayout_15.setVerticalSpacing(6)
        self.gridLayout_15.setContentsMargins(10, 10, 0, 15)
        self.widget_37 = QWidget(self.widget_36)
        self.widget_37.setObjectName(u"widget_37")
        self.widget_37.setMinimumSize(QSize(0, 30))
        self.verticalLayout_60 = QVBoxLayout(self.widget_37)
        self.verticalLayout_60.setSpacing(6)
        self.verticalLayout_60.setObjectName(u"verticalLayout_60")
        self.verticalLayout_60.setContentsMargins(0, 0, 0, 0)
        self.label_48 = QLabel(self.widget_37)
        self.label_48.setObjectName(u"label_48")
        self.label_48.setMaximumSize(QSize(16777215, 30))

        self.verticalLayout_60.addWidget(self.label_48)


        self.gridLayout_15.addWidget(self.widget_37, 1, 0, 1, 1)

        self.XiaoDuiTuXi_4rewards_times = QSpinBox(self.widget_36)
        self.XiaoDuiTuXi_4rewards_times.setObjectName(u"XiaoDuiTuXi_4rewards_times")
        self.XiaoDuiTuXi_4rewards_times.setMaximumSize(QSize(80, 35))
        self.XiaoDuiTuXi_4rewards_times.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.XiaoDuiTuXi_4rewards_times.setWrapping(False)
        self.XiaoDuiTuXi_4rewards_times.setFrame(True)
        self.XiaoDuiTuXi_4rewards_times.setMaximum(2)
        self.XiaoDuiTuXi_4rewards_times.setValue(0)

        self.gridLayout_15.addWidget(self.XiaoDuiTuXi_4rewards_times, 1, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter)

        self.widget_16 = QWidget(self.widget_36)
        self.widget_16.setObjectName(u"widget_16")
        self.verticalLayout_12 = QVBoxLayout(self.widget_16)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.label_13 = QLabel(self.widget_16)
        self.label_13.setObjectName(u"label_13")

        self.verticalLayout_12.addWidget(self.label_13)

        self.label_12 = QLabel(self.widget_16)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_12.addWidget(self.label_12)


        self.gridLayout_15.addWidget(self.widget_16, 0, 0, 1, 1)

        self.XiaoDuiTuXi_4rewards_Enable = QCheckBox(self.widget_36)
        self.XiaoDuiTuXi_4rewards_Enable.setObjectName(u"XiaoDuiTuXi_4rewards_Enable")
        self.XiaoDuiTuXi_4rewards_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.gridLayout_15.addWidget(self.XiaoDuiTuXi_4rewards_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter)

        self.gridLayout_15.setColumnStretch(0, 5)
        self.gridLayout_15.setColumnStretch(1, 2)

        self.verticalLayout_53.addLayout(self.gridLayout_15)


        self.verticalLayout_51.addWidget(self.widget_36)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_51.addItem(self.verticalSpacer_3)

        self.scrollArea_11.setWidget(self.scrollAreaWidgetContents_8)

        self.horizontalLayout_16.addWidget(self.scrollArea_11)

        self.horizontalSpacer_16 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_16)

        self.horizontalLayout_16.setStretch(0, 1)
        self.horizontalLayout_16.setStretch(1, 5)
        self.horizontalLayout_16.setStretch(2, 1)

        self.horizontalLayout_17.addWidget(self.widget_29)

        self.stackedWidget.addWidget(self.XiaoDuiTuXi_widget)
        self.ZuZhiQiFu_widget = QWidget()
        self.ZuZhiQiFu_widget.setObjectName(u"ZuZhiQiFu_widget")
        self.horizontalLayout_6 = QHBoxLayout(self.ZuZhiQiFu_widget)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.widget_80 = QWidget(self.ZuZhiQiFu_widget)
        self.widget_80.setObjectName(u"widget_80")
        self.widget_80.setStyleSheet(u"")
        self.horizontalLayout_62 = QHBoxLayout(self.widget_80)
        self.horizontalLayout_62.setObjectName(u"horizontalLayout_62")
        self.horizontalSpacer_59 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_62.addItem(self.horizontalSpacer_59)

        self.scrollArea_33 = QScrollArea(self.widget_80)
        self.scrollArea_33.setObjectName(u"scrollArea_33")
        self.scrollArea_33.setMinimumSize(QSize(600, 0))
        self.scrollArea_33.setWidgetResizable(True)
        self.scrollArea_33.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_30 = QWidget()
        self.scrollAreaWidgetContents_30.setObjectName(u"scrollAreaWidgetContents_30")
        self.scrollAreaWidgetContents_30.setGeometry(QRect(0, 0, 566, 234))
        self.verticalLayout_145 = QVBoxLayout(self.scrollAreaWidgetContents_30)
        self.verticalLayout_145.setSpacing(20)
        self.verticalLayout_145.setObjectName(u"verticalLayout_145")
        self.widget_81 = QWidget(self.scrollAreaWidgetContents_30)
        self.widget_81.setObjectName(u"widget_81")
        self.widget_81.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_146 = QVBoxLayout(self.widget_81)
        self.verticalLayout_146.setObjectName(u"verticalLayout_146")
        self.verticalLayout_146.setContentsMargins(-1, 7, -1, -1)
        self.label_187 = QLabel(self.widget_81)
        self.label_187.setObjectName(u"label_187")
        self.label_187.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_146.addWidget(self.label_187)

        self.frame_37 = QFrame(self.widget_81)
        self.frame_37.setObjectName(u"frame_37")
        self.frame_37.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_37.setFrameShape(QFrame.Shape.HLine)
        self.frame_37.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_146.addWidget(self.frame_37)

        self.gridLayout_42 = QGridLayout()
        self.gridLayout_42.setObjectName(u"gridLayout_42")
        self.gridLayout_42.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_147 = QVBoxLayout()
        self.verticalLayout_147.setObjectName(u"verticalLayout_147")
        self.label_188 = QLabel(self.widget_81)
        self.label_188.setObjectName(u"label_188")

        self.verticalLayout_147.addWidget(self.label_188)

        self.label_189 = QLabel(self.widget_81)
        self.label_189.setObjectName(u"label_189")
        self.label_189.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_147.addWidget(self.label_189)


        self.gridLayout_42.addLayout(self.verticalLayout_147, 0, 0, 1, 1)

        self.ZuZhiQiFu_Enable = QCheckBox(self.widget_81)
        self.ZuZhiQiFu_Enable.setObjectName(u"ZuZhiQiFu_Enable")
        self.ZuZhiQiFu_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.ZuZhiQiFu_Enable.setStyleSheet(u"")

        self.gridLayout_42.addWidget(self.ZuZhiQiFu_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_148 = QVBoxLayout()
        self.verticalLayout_148.setObjectName(u"verticalLayout_148")
        self.label_190 = QLabel(self.widget_81)
        self.label_190.setObjectName(u"label_190")

        self.verticalLayout_148.addWidget(self.label_190)

        self.label_191 = QLabel(self.widget_81)
        self.label_191.setObjectName(u"label_191")
        self.label_191.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_148.addWidget(self.label_191)


        self.gridLayout_42.addLayout(self.verticalLayout_148, 1, 0, 1, 1)

        self.ZuZhiQiFu_next_execute_time = QLineEdit(self.widget_81)
        self.ZuZhiQiFu_next_execute_time.setObjectName(u"ZuZhiQiFu_next_execute_time")
        self.ZuZhiQiFu_next_execute_time.setMinimumSize(QSize(200, 0))
        self.ZuZhiQiFu_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.ZuZhiQiFu_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_42.addWidget(self.ZuZhiQiFu_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_42.setColumnStretch(0, 5)
        self.gridLayout_42.setColumnStretch(1, 2)

        self.verticalLayout_146.addLayout(self.gridLayout_42)


        self.verticalLayout_145.addWidget(self.widget_81)

        self.verticalSpacer_25 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_145.addItem(self.verticalSpacer_25)

        self.scrollArea_33.setWidget(self.scrollAreaWidgetContents_30)

        self.horizontalLayout_62.addWidget(self.scrollArea_33)

        self.horizontalSpacer_60 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_62.addItem(self.horizontalSpacer_60)

        self.horizontalLayout_62.setStretch(0, 1)
        self.horizontalLayout_62.setStretch(1, 5)
        self.horizontalLayout_62.setStretch(2, 1)

        self.horizontalLayout_6.addWidget(self.widget_80)

        self.stackedWidget.addWidget(self.ZuZhiQiFu_widget)
        self.HaoYouTiLi_widget = QWidget()
        self.HaoYouTiLi_widget.setObjectName(u"HaoYouTiLi_widget")
        self.horizontalLayout_7 = QHBoxLayout(self.HaoYouTiLi_widget)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.widget_50 = QWidget(self.HaoYouTiLi_widget)
        self.widget_50.setObjectName(u"widget_50")
        self.widget_50.setStyleSheet(u"")
        self.horizontalLayout_30 = QHBoxLayout(self.widget_50)
        self.horizontalLayout_30.setObjectName(u"horizontalLayout_30")
        self.horizontalSpacer_29 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_30.addItem(self.horizontalSpacer_29)

        self.scrollArea_18 = QScrollArea(self.widget_50)
        self.scrollArea_18.setObjectName(u"scrollArea_18")
        self.scrollArea_18.setMinimumSize(QSize(600, 0))
        self.scrollArea_18.setWidgetResizable(True)
        self.scrollArea_18.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_15 = QWidget()
        self.scrollAreaWidgetContents_15.setObjectName(u"scrollAreaWidgetContents_15")
        self.scrollAreaWidgetContents_15.setGeometry(QRect(0, 0, 566, 234))
        self.verticalLayout_85 = QVBoxLayout(self.scrollAreaWidgetContents_15)
        self.verticalLayout_85.setSpacing(20)
        self.verticalLayout_85.setObjectName(u"verticalLayout_85")
        self.widget_51 = QWidget(self.scrollAreaWidgetContents_15)
        self.widget_51.setObjectName(u"widget_51")
        self.widget_51.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_86 = QVBoxLayout(self.widget_51)
        self.verticalLayout_86.setObjectName(u"verticalLayout_86")
        self.verticalLayout_86.setContentsMargins(-1, 7, -1, -1)
        self.label_82 = QLabel(self.widget_51)
        self.label_82.setObjectName(u"label_82")
        self.label_82.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_86.addWidget(self.label_82)

        self.frame_22 = QFrame(self.widget_51)
        self.frame_22.setObjectName(u"frame_22")
        self.frame_22.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_22.setFrameShape(QFrame.Shape.HLine)
        self.frame_22.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_86.addWidget(self.frame_22)

        self.gridLayout_27 = QGridLayout()
        self.gridLayout_27.setObjectName(u"gridLayout_27")
        self.gridLayout_27.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_87 = QVBoxLayout()
        self.verticalLayout_87.setObjectName(u"verticalLayout_87")
        self.label_83 = QLabel(self.widget_51)
        self.label_83.setObjectName(u"label_83")

        self.verticalLayout_87.addWidget(self.label_83)

        self.label_84 = QLabel(self.widget_51)
        self.label_84.setObjectName(u"label_84")
        self.label_84.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_87.addWidget(self.label_84)


        self.gridLayout_27.addLayout(self.verticalLayout_87, 0, 0, 1, 1)

        self.HaoYouTiLi_Enable = QCheckBox(self.widget_51)
        self.HaoYouTiLi_Enable.setObjectName(u"HaoYouTiLi_Enable")
        self.HaoYouTiLi_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.HaoYouTiLi_Enable.setStyleSheet(u"")

        self.gridLayout_27.addWidget(self.HaoYouTiLi_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_88 = QVBoxLayout()
        self.verticalLayout_88.setObjectName(u"verticalLayout_88")
        self.label_138 = QLabel(self.widget_51)
        self.label_138.setObjectName(u"label_138")

        self.verticalLayout_88.addWidget(self.label_138)

        self.label_139 = QLabel(self.widget_51)
        self.label_139.setObjectName(u"label_139")
        self.label_139.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_88.addWidget(self.label_139)


        self.gridLayout_27.addLayout(self.verticalLayout_88, 1, 0, 1, 1)

        self.HaoYouTiLi_next_execute_time = QLineEdit(self.widget_51)
        self.HaoYouTiLi_next_execute_time.setObjectName(u"HaoYouTiLi_next_execute_time")
        self.HaoYouTiLi_next_execute_time.setMinimumSize(QSize(200, 0))
        self.HaoYouTiLi_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.HaoYouTiLi_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_27.addWidget(self.HaoYouTiLi_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_27.setColumnStretch(0, 5)
        self.gridLayout_27.setColumnStretch(1, 2)

        self.verticalLayout_86.addLayout(self.gridLayout_27)


        self.verticalLayout_85.addWidget(self.widget_51)

        self.verticalSpacer_10 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_85.addItem(self.verticalSpacer_10)

        self.scrollArea_18.setWidget(self.scrollAreaWidgetContents_15)

        self.horizontalLayout_30.addWidget(self.scrollArea_18)

        self.horizontalSpacer_30 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_30.addItem(self.horizontalSpacer_30)

        self.horizontalLayout_30.setStretch(0, 1)
        self.horizontalLayout_30.setStretch(1, 5)
        self.horizontalLayout_30.setStretch(2, 1)

        self.horizontalLayout_7.addWidget(self.widget_50)

        self.stackedWidget.addWidget(self.HaoYouTiLi_widget)
        self.PuTongRenZheZhaoMu_widget = QWidget()
        self.PuTongRenZheZhaoMu_widget.setObjectName(u"PuTongRenZheZhaoMu_widget")
        self.horizontalLayout_8 = QHBoxLayout(self.PuTongRenZheZhaoMu_widget)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.widget_66 = QWidget(self.PuTongRenZheZhaoMu_widget)
        self.widget_66.setObjectName(u"widget_66")
        self.widget_66.setStyleSheet(u"")
        self.horizontalLayout_48 = QHBoxLayout(self.widget_66)
        self.horizontalLayout_48.setObjectName(u"horizontalLayout_48")
        self.horizontalSpacer_45 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_48.addItem(self.horizontalSpacer_45)

        self.scrollArea_26 = QScrollArea(self.widget_66)
        self.scrollArea_26.setObjectName(u"scrollArea_26")
        self.scrollArea_26.setMinimumSize(QSize(600, 0))
        self.scrollArea_26.setWidgetResizable(True)
        self.scrollArea_26.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_23 = QWidget()
        self.scrollAreaWidgetContents_23.setObjectName(u"scrollAreaWidgetContents_23")
        self.scrollAreaWidgetContents_23.setGeometry(QRect(0, 0, 566, 234))
        self.verticalLayout_117 = QVBoxLayout(self.scrollAreaWidgetContents_23)
        self.verticalLayout_117.setSpacing(20)
        self.verticalLayout_117.setObjectName(u"verticalLayout_117")
        self.widget_67 = QWidget(self.scrollAreaWidgetContents_23)
        self.widget_67.setObjectName(u"widget_67")
        self.widget_67.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_118 = QVBoxLayout(self.widget_67)
        self.verticalLayout_118.setObjectName(u"verticalLayout_118")
        self.verticalLayout_118.setContentsMargins(-1, 7, -1, -1)
        self.label_118 = QLabel(self.widget_67)
        self.label_118.setObjectName(u"label_118")
        self.label_118.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_118.addWidget(self.label_118)

        self.frame_30 = QFrame(self.widget_67)
        self.frame_30.setObjectName(u"frame_30")
        self.frame_30.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_30.setFrameShape(QFrame.Shape.HLine)
        self.frame_30.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_118.addWidget(self.frame_30)

        self.gridLayout_35 = QGridLayout()
        self.gridLayout_35.setObjectName(u"gridLayout_35")
        self.gridLayout_35.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_119 = QVBoxLayout()
        self.verticalLayout_119.setObjectName(u"verticalLayout_119")
        self.label_119 = QLabel(self.widget_67)
        self.label_119.setObjectName(u"label_119")

        self.verticalLayout_119.addWidget(self.label_119)

        self.label_154 = QLabel(self.widget_67)
        self.label_154.setObjectName(u"label_154")
        self.label_154.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_119.addWidget(self.label_154)


        self.gridLayout_35.addLayout(self.verticalLayout_119, 0, 0, 1, 1)

        self.PuTongRenZheZhaoMu_Enable = QCheckBox(self.widget_67)
        self.PuTongRenZheZhaoMu_Enable.setObjectName(u"PuTongRenZheZhaoMu_Enable")
        self.PuTongRenZheZhaoMu_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.PuTongRenZheZhaoMu_Enable.setStyleSheet(u"")

        self.gridLayout_35.addWidget(self.PuTongRenZheZhaoMu_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_120 = QVBoxLayout()
        self.verticalLayout_120.setObjectName(u"verticalLayout_120")
        self.label_155 = QLabel(self.widget_67)
        self.label_155.setObjectName(u"label_155")

        self.verticalLayout_120.addWidget(self.label_155)

        self.label_156 = QLabel(self.widget_67)
        self.label_156.setObjectName(u"label_156")
        self.label_156.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_120.addWidget(self.label_156)


        self.gridLayout_35.addLayout(self.verticalLayout_120, 1, 0, 1, 1)

        self.PuTongRenZheZhaoMu_next_execute_time = QLineEdit(self.widget_67)
        self.PuTongRenZheZhaoMu_next_execute_time.setObjectName(u"PuTongRenZheZhaoMu_next_execute_time")
        self.PuTongRenZheZhaoMu_next_execute_time.setMinimumSize(QSize(200, 0))
        self.PuTongRenZheZhaoMu_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.PuTongRenZheZhaoMu_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_35.addWidget(self.PuTongRenZheZhaoMu_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_35.setColumnStretch(0, 5)
        self.gridLayout_35.setColumnStretch(1, 2)

        self.verticalLayout_118.addLayout(self.gridLayout_35)


        self.verticalLayout_117.addWidget(self.widget_67)

        self.verticalSpacer_18 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_117.addItem(self.verticalSpacer_18)

        self.scrollArea_26.setWidget(self.scrollAreaWidgetContents_23)

        self.horizontalLayout_48.addWidget(self.scrollArea_26)

        self.horizontalSpacer_46 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_48.addItem(self.horizontalSpacer_46)

        self.horizontalLayout_48.setStretch(0, 1)
        self.horizontalLayout_48.setStretch(1, 5)
        self.horizontalLayout_48.setStretch(2, 1)

        self.horizontalLayout_8.addWidget(self.widget_66)

        self.stackedWidget.addWidget(self.PuTongRenZheZhaoMu_widget)
        self.MeiRiFenXiang_widget = QWidget()
        self.MeiRiFenXiang_widget.setObjectName(u"MeiRiFenXiang_widget")
        self.horizontalLayout_38 = QHBoxLayout(self.MeiRiFenXiang_widget)
        self.horizontalLayout_38.setObjectName(u"horizontalLayout_38")
        self.widget_58 = QWidget(self.MeiRiFenXiang_widget)
        self.widget_58.setObjectName(u"widget_58")
        self.widget_58.setStyleSheet(u"")
        self.horizontalLayout_37 = QHBoxLayout(self.widget_58)
        self.horizontalLayout_37.setObjectName(u"horizontalLayout_37")
        self.horizontalSpacer_37 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_37.addItem(self.horizontalSpacer_37)

        self.scrollArea_22 = QScrollArea(self.widget_58)
        self.scrollArea_22.setObjectName(u"scrollArea_22")
        self.scrollArea_22.setMinimumSize(QSize(600, 0))
        self.scrollArea_22.setWidgetResizable(True)
        self.scrollArea_22.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_19 = QWidget()
        self.scrollAreaWidgetContents_19.setObjectName(u"scrollAreaWidgetContents_19")
        self.scrollAreaWidgetContents_19.setGeometry(QRect(0, 0, 566, 298))
        self.verticalLayout_101 = QVBoxLayout(self.scrollAreaWidgetContents_19)
        self.verticalLayout_101.setSpacing(20)
        self.verticalLayout_101.setObjectName(u"verticalLayout_101")
        self.widget_59 = QWidget(self.scrollAreaWidgetContents_19)
        self.widget_59.setObjectName(u"widget_59")
        self.widget_59.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_102 = QVBoxLayout(self.widget_59)
        self.verticalLayout_102.setObjectName(u"verticalLayout_102")
        self.verticalLayout_102.setContentsMargins(-1, 7, -1, -1)
        self.label_94 = QLabel(self.widget_59)
        self.label_94.setObjectName(u"label_94")
        self.label_94.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_102.addWidget(self.label_94)

        self.label_38 = QLabel(self.widget_59)
        self.label_38.setObjectName(u"label_38")
        self.label_38.setStyleSheet(u"font-size:13pt;\n"
"color:rgba(255, 0, 0, 100);\n"
"margin-left:18px;")

        self.verticalLayout_102.addWidget(self.label_38)

        self.frame_26 = QFrame(self.widget_59)
        self.frame_26.setObjectName(u"frame_26")
        self.frame_26.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_26.setFrameShape(QFrame.Shape.HLine)
        self.frame_26.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_102.addWidget(self.frame_26)

        self.gridLayout_31 = QGridLayout()
        self.gridLayout_31.setObjectName(u"gridLayout_31")
        self.gridLayout_31.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_103 = QVBoxLayout()
        self.verticalLayout_103.setObjectName(u"verticalLayout_103")
        self.label_95 = QLabel(self.widget_59)
        self.label_95.setObjectName(u"label_95")

        self.verticalLayout_103.addWidget(self.label_95)

        self.label_96 = QLabel(self.widget_59)
        self.label_96.setObjectName(u"label_96")
        self.label_96.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_103.addWidget(self.label_96)


        self.gridLayout_31.addLayout(self.verticalLayout_103, 0, 0, 1, 1)

        self.MeiRiFenXiang_Enable = QCheckBox(self.widget_59)
        self.MeiRiFenXiang_Enable.setObjectName(u"MeiRiFenXiang_Enable")
        self.MeiRiFenXiang_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.MeiRiFenXiang_Enable.setStyleSheet(u"")

        self.gridLayout_31.addWidget(self.MeiRiFenXiang_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_104 = QVBoxLayout()
        self.verticalLayout_104.setObjectName(u"verticalLayout_104")
        self.label_146 = QLabel(self.widget_59)
        self.label_146.setObjectName(u"label_146")

        self.verticalLayout_104.addWidget(self.label_146)

        self.label_147 = QLabel(self.widget_59)
        self.label_147.setObjectName(u"label_147")
        self.label_147.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_104.addWidget(self.label_147)


        self.gridLayout_31.addLayout(self.verticalLayout_104, 1, 0, 1, 1)

        self.MeiRiFenXiang_next_execute_time = QLineEdit(self.widget_59)
        self.MeiRiFenXiang_next_execute_time.setObjectName(u"MeiRiFenXiang_next_execute_time")
        self.MeiRiFenXiang_next_execute_time.setMinimumSize(QSize(200, 0))
        self.MeiRiFenXiang_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.MeiRiFenXiang_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_31.addWidget(self.MeiRiFenXiang_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_31.setColumnStretch(0, 5)
        self.gridLayout_31.setColumnStretch(1, 2)

        self.verticalLayout_102.addLayout(self.gridLayout_31)


        self.verticalLayout_101.addWidget(self.widget_59)

        self.verticalSpacer_14 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_101.addItem(self.verticalSpacer_14)

        self.scrollArea_22.setWidget(self.scrollAreaWidgetContents_19)

        self.horizontalLayout_37.addWidget(self.scrollArea_22)

        self.horizontalSpacer_38 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_37.addItem(self.horizontalSpacer_38)

        self.horizontalLayout_37.setStretch(0, 1)
        self.horizontalLayout_37.setStretch(1, 5)
        self.horizontalLayout_37.setStretch(2, 1)

        self.horizontalLayout_38.addWidget(self.widget_58)

        self.stackedWidget.addWidget(self.MeiRiFenXiang_widget)
        self.FengRaoZhiJian_widget = QWidget()
        self.FengRaoZhiJian_widget.setObjectName(u"FengRaoZhiJian_widget")
        self.horizontalLayout_27 = QHBoxLayout(self.FengRaoZhiJian_widget)
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.widget_46 = QWidget(self.FengRaoZhiJian_widget)
        self.widget_46.setObjectName(u"widget_46")
        self.widget_46.setStyleSheet(u"")
        self.horizontalLayout_26 = QHBoxLayout(self.widget_46)
        self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
        self.horizontalSpacer_25 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_26.addItem(self.horizontalSpacer_25)

        self.scrollArea_16 = QScrollArea(self.widget_46)
        self.scrollArea_16.setObjectName(u"scrollArea_16")
        self.scrollArea_16.setMinimumSize(QSize(600, 0))
        self.scrollArea_16.setWidgetResizable(True)
        self.scrollArea_16.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_13 = QWidget()
        self.scrollAreaWidgetContents_13.setObjectName(u"scrollAreaWidgetContents_13")
        self.scrollAreaWidgetContents_13.setGeometry(QRect(0, 0, 566, 260))
        self.verticalLayout_77 = QVBoxLayout(self.scrollAreaWidgetContents_13)
        self.verticalLayout_77.setSpacing(20)
        self.verticalLayout_77.setObjectName(u"verticalLayout_77")
        self.widget_47 = QWidget(self.scrollAreaWidgetContents_13)
        self.widget_47.setObjectName(u"widget_47")
        self.widget_47.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_78 = QVBoxLayout(self.widget_47)
        self.verticalLayout_78.setObjectName(u"verticalLayout_78")
        self.verticalLayout_78.setContentsMargins(-1, 7, -1, -1)
        self.label_76 = QLabel(self.widget_47)
        self.label_76.setObjectName(u"label_76")
        self.label_76.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_78.addWidget(self.label_76)

        self.label_226 = QLabel(self.widget_47)
        self.label_226.setObjectName(u"label_226")
        self.label_226.setStyleSheet(u"font-size:13pt;\n"
"color:rgba(255, 0, 0, 100);\n"
"margin-left:18px;")

        self.verticalLayout_78.addWidget(self.label_226)

        self.frame_20 = QFrame(self.widget_47)
        self.frame_20.setObjectName(u"frame_20")
        self.frame_20.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_20.setFrameShape(QFrame.Shape.HLine)
        self.frame_20.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_78.addWidget(self.frame_20)

        self.gridLayout_25 = QGridLayout()
        self.gridLayout_25.setObjectName(u"gridLayout_25")
        self.gridLayout_25.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_79 = QVBoxLayout()
        self.verticalLayout_79.setObjectName(u"verticalLayout_79")
        self.label_77 = QLabel(self.widget_47)
        self.label_77.setObjectName(u"label_77")

        self.verticalLayout_79.addWidget(self.label_77)

        self.label_78 = QLabel(self.widget_47)
        self.label_78.setObjectName(u"label_78")
        self.label_78.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_79.addWidget(self.label_78)


        self.gridLayout_25.addLayout(self.verticalLayout_79, 0, 0, 1, 1)

        self.FengRaoZhiJian_Enable = QCheckBox(self.widget_47)
        self.FengRaoZhiJian_Enable.setObjectName(u"FengRaoZhiJian_Enable")
        self.FengRaoZhiJian_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.FengRaoZhiJian_Enable.setStyleSheet(u"")

        self.gridLayout_25.addWidget(self.FengRaoZhiJian_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_80 = QVBoxLayout()
        self.verticalLayout_80.setObjectName(u"verticalLayout_80")
        self.label_134 = QLabel(self.widget_47)
        self.label_134.setObjectName(u"label_134")

        self.verticalLayout_80.addWidget(self.label_134)

        self.label_135 = QLabel(self.widget_47)
        self.label_135.setObjectName(u"label_135")
        self.label_135.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_80.addWidget(self.label_135)


        self.gridLayout_25.addLayout(self.verticalLayout_80, 1, 0, 1, 1)

        self.FengRaoZhiJian_next_execute_time = QLineEdit(self.widget_47)
        self.FengRaoZhiJian_next_execute_time.setObjectName(u"FengRaoZhiJian_next_execute_time")
        self.FengRaoZhiJian_next_execute_time.setMinimumSize(QSize(200, 0))
        self.FengRaoZhiJian_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.FengRaoZhiJian_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_25.addWidget(self.FengRaoZhiJian_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_25.setColumnStretch(0, 5)
        self.gridLayout_25.setColumnStretch(1, 2)

        self.verticalLayout_78.addLayout(self.gridLayout_25)


        self.verticalLayout_77.addWidget(self.widget_47)

        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_77.addItem(self.verticalSpacer_8)

        self.scrollArea_16.setWidget(self.scrollAreaWidgetContents_13)

        self.horizontalLayout_26.addWidget(self.scrollArea_16)

        self.horizontalSpacer_26 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_26.addItem(self.horizontalSpacer_26)

        self.horizontalLayout_26.setStretch(0, 1)
        self.horizontalLayout_26.setStretch(1, 5)
        self.horizontalLayout_26.setStretch(2, 1)

        self.horizontalLayout_27.addWidget(self.widget_46)

        self.stackedWidget.addWidget(self.FengRaoZhiJian_widget)
        self.RenWuJiHuiSuo_widget = QWidget()
        self.RenWuJiHuiSuo_widget.setObjectName(u"RenWuJiHuiSuo_widget")
        self.horizontalLayout_44 = QHBoxLayout(self.RenWuJiHuiSuo_widget)
        self.horizontalLayout_44.setObjectName(u"horizontalLayout_44")
        self.widget_74 = QWidget(self.RenWuJiHuiSuo_widget)
        self.widget_74.setObjectName(u"widget_74")
        self.widget_74.setStyleSheet(u"")
        self.horizontalLayout_59 = QHBoxLayout(self.widget_74)
        self.horizontalLayout_59.setObjectName(u"horizontalLayout_59")
        self.horizontalSpacer_53 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_59.addItem(self.horizontalSpacer_53)

        self.scrollArea_30 = QScrollArea(self.widget_74)
        self.scrollArea_30.setObjectName(u"scrollArea_30")
        self.scrollArea_30.setMinimumSize(QSize(600, 0))
        self.scrollArea_30.setWidgetResizable(True)
        self.scrollArea_30.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_27 = QWidget()
        self.scrollAreaWidgetContents_27.setObjectName(u"scrollAreaWidgetContents_27")
        self.scrollAreaWidgetContents_27.setGeometry(QRect(0, 0, 566, 260))
        self.verticalLayout_133 = QVBoxLayout(self.scrollAreaWidgetContents_27)
        self.verticalLayout_133.setSpacing(20)
        self.verticalLayout_133.setObjectName(u"verticalLayout_133")
        self.widget_75 = QWidget(self.scrollAreaWidgetContents_27)
        self.widget_75.setObjectName(u"widget_75")
        self.widget_75.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_134 = QVBoxLayout(self.widget_75)
        self.verticalLayout_134.setObjectName(u"verticalLayout_134")
        self.verticalLayout_134.setContentsMargins(-1, 7, -1, -1)
        self.label_172 = QLabel(self.widget_75)
        self.label_172.setObjectName(u"label_172")
        self.label_172.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_134.addWidget(self.label_172)

        self.label_49 = QLabel(self.widget_75)
        self.label_49.setObjectName(u"label_49")
        self.label_49.setStyleSheet(u"font-size:13pt;\n"
"color:rgba(255, 0, 0, 100);\n"
"margin-left:18px;")

        self.verticalLayout_134.addWidget(self.label_49)

        self.frame_34 = QFrame(self.widget_75)
        self.frame_34.setObjectName(u"frame_34")
        self.frame_34.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_34.setFrameShape(QFrame.Shape.HLine)
        self.frame_34.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_134.addWidget(self.frame_34)

        self.gridLayout_39 = QGridLayout()
        self.gridLayout_39.setObjectName(u"gridLayout_39")
        self.gridLayout_39.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_135 = QVBoxLayout()
        self.verticalLayout_135.setObjectName(u"verticalLayout_135")
        self.label_173 = QLabel(self.widget_75)
        self.label_173.setObjectName(u"label_173")

        self.verticalLayout_135.addWidget(self.label_173)

        self.label_174 = QLabel(self.widget_75)
        self.label_174.setObjectName(u"label_174")
        self.label_174.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_135.addWidget(self.label_174)


        self.gridLayout_39.addLayout(self.verticalLayout_135, 0, 0, 1, 1)

        self.RenWuJiHuiSuo_Enable = QCheckBox(self.widget_75)
        self.RenWuJiHuiSuo_Enable.setObjectName(u"RenWuJiHuiSuo_Enable")
        self.RenWuJiHuiSuo_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.RenWuJiHuiSuo_Enable.setStyleSheet(u"")

        self.gridLayout_39.addWidget(self.RenWuJiHuiSuo_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_136 = QVBoxLayout()
        self.verticalLayout_136.setObjectName(u"verticalLayout_136")
        self.label_175 = QLabel(self.widget_75)
        self.label_175.setObjectName(u"label_175")

        self.verticalLayout_136.addWidget(self.label_175)

        self.label_176 = QLabel(self.widget_75)
        self.label_176.setObjectName(u"label_176")
        self.label_176.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_136.addWidget(self.label_176)


        self.gridLayout_39.addLayout(self.verticalLayout_136, 1, 0, 1, 1)

        self.RenWuJiHuiSuo_next_execute_time = QLineEdit(self.widget_75)
        self.RenWuJiHuiSuo_next_execute_time.setObjectName(u"RenWuJiHuiSuo_next_execute_time")
        self.RenWuJiHuiSuo_next_execute_time.setMinimumSize(QSize(200, 0))
        self.RenWuJiHuiSuo_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.RenWuJiHuiSuo_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_39.addWidget(self.RenWuJiHuiSuo_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_39.setColumnStretch(0, 5)
        self.gridLayout_39.setColumnStretch(1, 2)

        self.verticalLayout_134.addLayout(self.gridLayout_39)


        self.verticalLayout_133.addWidget(self.widget_75)

        self.verticalSpacer_22 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_133.addItem(self.verticalSpacer_22)

        self.scrollArea_30.setWidget(self.scrollAreaWidgetContents_27)

        self.horizontalLayout_59.addWidget(self.scrollArea_30)

        self.horizontalSpacer_54 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_59.addItem(self.horizontalSpacer_54)

        self.horizontalLayout_59.setStretch(0, 1)
        self.horizontalLayout_59.setStretch(1, 5)
        self.horizontalLayout_59.setStretch(2, 1)

        self.horizontalLayout_44.addWidget(self.widget_74)

        self.stackedWidget.addWidget(self.RenWuJiHuiSuo_widget)
        self.YiLeWaiMai_widget = QWidget()
        self.YiLeWaiMai_widget.setObjectName(u"YiLeWaiMai_widget")
        self.horizontalLayout_45 = QHBoxLayout(self.YiLeWaiMai_widget)
        self.horizontalLayout_45.setObjectName(u"horizontalLayout_45")
        self.widget_78 = QWidget(self.YiLeWaiMai_widget)
        self.widget_78.setObjectName(u"widget_78")
        self.widget_78.setStyleSheet(u"")
        self.horizontalLayout_61 = QHBoxLayout(self.widget_78)
        self.horizontalLayout_61.setObjectName(u"horizontalLayout_61")
        self.horizontalSpacer_57 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_61.addItem(self.horizontalSpacer_57)

        self.scrollArea_32 = QScrollArea(self.widget_78)
        self.scrollArea_32.setObjectName(u"scrollArea_32")
        self.scrollArea_32.setMinimumSize(QSize(600, 0))
        self.scrollArea_32.setWidgetResizable(True)
        self.scrollArea_32.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_29 = QWidget()
        self.scrollAreaWidgetContents_29.setObjectName(u"scrollAreaWidgetContents_29")
        self.scrollAreaWidgetContents_29.setGeometry(QRect(0, 0, 566, 234))
        self.verticalLayout_141 = QVBoxLayout(self.scrollAreaWidgetContents_29)
        self.verticalLayout_141.setSpacing(20)
        self.verticalLayout_141.setObjectName(u"verticalLayout_141")
        self.widget_79 = QWidget(self.scrollAreaWidgetContents_29)
        self.widget_79.setObjectName(u"widget_79")
        self.widget_79.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_142 = QVBoxLayout(self.widget_79)
        self.verticalLayout_142.setObjectName(u"verticalLayout_142")
        self.verticalLayout_142.setContentsMargins(-1, 7, -1, -1)
        self.label_182 = QLabel(self.widget_79)
        self.label_182.setObjectName(u"label_182")
        self.label_182.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_142.addWidget(self.label_182)

        self.frame_36 = QFrame(self.widget_79)
        self.frame_36.setObjectName(u"frame_36")
        self.frame_36.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_36.setFrameShape(QFrame.Shape.HLine)
        self.frame_36.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_142.addWidget(self.frame_36)

        self.gridLayout_41 = QGridLayout()
        self.gridLayout_41.setObjectName(u"gridLayout_41")
        self.gridLayout_41.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_143 = QVBoxLayout()
        self.verticalLayout_143.setObjectName(u"verticalLayout_143")
        self.label_183 = QLabel(self.widget_79)
        self.label_183.setObjectName(u"label_183")

        self.verticalLayout_143.addWidget(self.label_183)

        self.label_184 = QLabel(self.widget_79)
        self.label_184.setObjectName(u"label_184")
        self.label_184.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_143.addWidget(self.label_184)


        self.gridLayout_41.addLayout(self.verticalLayout_143, 0, 0, 1, 1)

        self.YiLeWaiMai_Enable = QCheckBox(self.widget_79)
        self.YiLeWaiMai_Enable.setObjectName(u"YiLeWaiMai_Enable")
        self.YiLeWaiMai_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.YiLeWaiMai_Enable.setStyleSheet(u"")

        self.gridLayout_41.addWidget(self.YiLeWaiMai_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_144 = QVBoxLayout()
        self.verticalLayout_144.setObjectName(u"verticalLayout_144")
        self.label_185 = QLabel(self.widget_79)
        self.label_185.setObjectName(u"label_185")

        self.verticalLayout_144.addWidget(self.label_185)

        self.label_186 = QLabel(self.widget_79)
        self.label_186.setObjectName(u"label_186")
        self.label_186.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_144.addWidget(self.label_186)


        self.gridLayout_41.addLayout(self.verticalLayout_144, 1, 0, 1, 1)

        self.YiLeWaiMai_next_execute_time = QLineEdit(self.widget_79)
        self.YiLeWaiMai_next_execute_time.setObjectName(u"YiLeWaiMai_next_execute_time")
        self.YiLeWaiMai_next_execute_time.setMinimumSize(QSize(200, 0))
        self.YiLeWaiMai_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.YiLeWaiMai_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_41.addWidget(self.YiLeWaiMai_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_41.setColumnStretch(0, 5)
        self.gridLayout_41.setColumnStretch(1, 2)

        self.verticalLayout_142.addLayout(self.gridLayout_41)


        self.verticalLayout_141.addWidget(self.widget_79)

        self.verticalSpacer_24 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_141.addItem(self.verticalSpacer_24)

        self.scrollArea_32.setWidget(self.scrollAreaWidgetContents_29)

        self.horizontalLayout_61.addWidget(self.scrollArea_32)

        self.horizontalSpacer_58 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_61.addItem(self.horizontalSpacer_58)

        self.horizontalLayout_61.setStretch(0, 1)
        self.horizontalLayout_61.setStretch(1, 5)
        self.horizontalLayout_61.setStretch(2, 1)

        self.horizontalLayout_45.addWidget(self.widget_78)

        self.stackedWidget.addWidget(self.YiLeWaiMai_widget)
        self.MeiRiShengChang_widget = QWidget()
        self.MeiRiShengChang_widget.setObjectName(u"MeiRiShengChang_widget")
        self.horizontalLayout_36 = QHBoxLayout(self.MeiRiShengChang_widget)
        self.horizontalLayout_36.setObjectName(u"horizontalLayout_36")
        self.widget_56 = QWidget(self.MeiRiShengChang_widget)
        self.widget_56.setObjectName(u"widget_56")
        self.widget_56.setStyleSheet(u"")
        self.horizontalLayout_35 = QHBoxLayout(self.widget_56)
        self.horizontalLayout_35.setObjectName(u"horizontalLayout_35")
        self.horizontalSpacer_35 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_35.addItem(self.horizontalSpacer_35)

        self.scrollArea_21 = QScrollArea(self.widget_56)
        self.scrollArea_21.setObjectName(u"scrollArea_21")
        self.scrollArea_21.setMinimumSize(QSize(600, 0))
        self.scrollArea_21.setWidgetResizable(True)
        self.scrollArea_21.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_18 = QWidget()
        self.scrollAreaWidgetContents_18.setObjectName(u"scrollAreaWidgetContents_18")
        self.scrollAreaWidgetContents_18.setGeometry(QRect(0, 0, 590, 260))
        self.verticalLayout_97 = QVBoxLayout(self.scrollAreaWidgetContents_18)
        self.verticalLayout_97.setSpacing(20)
        self.verticalLayout_97.setObjectName(u"verticalLayout_97")
        self.widget_57 = QWidget(self.scrollAreaWidgetContents_18)
        self.widget_57.setObjectName(u"widget_57")
        self.widget_57.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_98 = QVBoxLayout(self.widget_57)
        self.verticalLayout_98.setObjectName(u"verticalLayout_98")
        self.verticalLayout_98.setContentsMargins(-1, 7, -1, -1)
        self.label_91 = QLabel(self.widget_57)
        self.label_91.setObjectName(u"label_91")
        self.label_91.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_98.addWidget(self.label_91)

        self.label_14 = QLabel(self.widget_57)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setStyleSheet(u"font-size:13pt;\n"
"color:rgba(255, 0, 0, 100);\n"
"margin-left:18px;")

        self.verticalLayout_98.addWidget(self.label_14)

        self.frame_25 = QFrame(self.widget_57)
        self.frame_25.setObjectName(u"frame_25")
        self.frame_25.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_25.setFrameShape(QFrame.Shape.HLine)
        self.frame_25.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_98.addWidget(self.frame_25)

        self.gridLayout_30 = QGridLayout()
        self.gridLayout_30.setObjectName(u"gridLayout_30")
        self.gridLayout_30.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_99 = QVBoxLayout()
        self.verticalLayout_99.setObjectName(u"verticalLayout_99")
        self.label_92 = QLabel(self.widget_57)
        self.label_92.setObjectName(u"label_92")

        self.verticalLayout_99.addWidget(self.label_92)

        self.label_93 = QLabel(self.widget_57)
        self.label_93.setObjectName(u"label_93")
        self.label_93.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_99.addWidget(self.label_93)


        self.gridLayout_30.addLayout(self.verticalLayout_99, 0, 0, 1, 1)

        self.MeiRiShengChang_Enable = QCheckBox(self.widget_57)
        self.MeiRiShengChang_Enable.setObjectName(u"MeiRiShengChang_Enable")
        self.MeiRiShengChang_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.MeiRiShengChang_Enable.setStyleSheet(u"")

        self.gridLayout_30.addWidget(self.MeiRiShengChang_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_100 = QVBoxLayout()
        self.verticalLayout_100.setObjectName(u"verticalLayout_100")
        self.label_144 = QLabel(self.widget_57)
        self.label_144.setObjectName(u"label_144")

        self.verticalLayout_100.addWidget(self.label_144)

        self.label_145 = QLabel(self.widget_57)
        self.label_145.setObjectName(u"label_145")
        self.label_145.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_100.addWidget(self.label_145)


        self.gridLayout_30.addLayout(self.verticalLayout_100, 1, 0, 1, 1)

        self.MeiRiShengChang_next_execute_time = QLineEdit(self.widget_57)
        self.MeiRiShengChang_next_execute_time.setObjectName(u"MeiRiShengChang_next_execute_time")
        self.MeiRiShengChang_next_execute_time.setMinimumSize(QSize(200, 0))
        self.MeiRiShengChang_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.MeiRiShengChang_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_30.addWidget(self.MeiRiShengChang_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_30.setColumnStretch(0, 5)
        self.gridLayout_30.setColumnStretch(1, 2)

        self.verticalLayout_98.addLayout(self.gridLayout_30)


        self.verticalLayout_97.addWidget(self.widget_57)

        self.verticalSpacer_13 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_97.addItem(self.verticalSpacer_13)

        self.scrollArea_21.setWidget(self.scrollAreaWidgetContents_18)

        self.horizontalLayout_35.addWidget(self.scrollArea_21)

        self.horizontalSpacer_36 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_35.addItem(self.horizontalSpacer_36)

        self.horizontalLayout_35.setStretch(0, 1)
        self.horizontalLayout_35.setStretch(1, 5)
        self.horizontalLayout_35.setStretch(2, 1)

        self.horizontalLayout_36.addWidget(self.widget_56)

        self.stackedWidget.addWidget(self.MeiRiShengChang_widget)
        self.ShengCunTiaoZhan_widget = QWidget()
        self.ShengCunTiaoZhan_widget.setObjectName(u"ShengCunTiaoZhan_widget")
        self.horizontalLayout_47 = QHBoxLayout(self.ShengCunTiaoZhan_widget)
        self.horizontalLayout_47.setObjectName(u"horizontalLayout_47")
        self.widget_82 = QWidget(self.ShengCunTiaoZhan_widget)
        self.widget_82.setObjectName(u"widget_82")
        self.widget_82.setStyleSheet(u"")
        self.horizontalLayout_63 = QHBoxLayout(self.widget_82)
        self.horizontalLayout_63.setObjectName(u"horizontalLayout_63")
        self.horizontalSpacer_61 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_63.addItem(self.horizontalSpacer_61)

        self.scrollArea_34 = QScrollArea(self.widget_82)
        self.scrollArea_34.setObjectName(u"scrollArea_34")
        self.scrollArea_34.setMinimumSize(QSize(600, 0))
        self.scrollArea_34.setWidgetResizable(True)
        self.scrollArea_34.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_31 = QWidget()
        self.scrollAreaWidgetContents_31.setObjectName(u"scrollAreaWidgetContents_31")
        self.scrollAreaWidgetContents_31.setGeometry(QRect(0, 0, 566, 260))
        self.verticalLayout_149 = QVBoxLayout(self.scrollAreaWidgetContents_31)
        self.verticalLayout_149.setSpacing(20)
        self.verticalLayout_149.setObjectName(u"verticalLayout_149")
        self.widget_83 = QWidget(self.scrollAreaWidgetContents_31)
        self.widget_83.setObjectName(u"widget_83")
        self.widget_83.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_150 = QVBoxLayout(self.widget_83)
        self.verticalLayout_150.setObjectName(u"verticalLayout_150")
        self.verticalLayout_150.setContentsMargins(-1, 7, -1, -1)
        self.label_192 = QLabel(self.widget_83)
        self.label_192.setObjectName(u"label_192")
        self.label_192.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_150.addWidget(self.label_192)

        self.label_50 = QLabel(self.widget_83)
        self.label_50.setObjectName(u"label_50")
        self.label_50.setStyleSheet(u"font-size:13pt;\n"
"color:rgba(255, 0, 0, 100);\n"
"margin-left:18px;")

        self.verticalLayout_150.addWidget(self.label_50)

        self.frame_38 = QFrame(self.widget_83)
        self.frame_38.setObjectName(u"frame_38")
        self.frame_38.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_38.setFrameShape(QFrame.Shape.HLine)
        self.frame_38.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_150.addWidget(self.frame_38)

        self.gridLayout_43 = QGridLayout()
        self.gridLayout_43.setObjectName(u"gridLayout_43")
        self.gridLayout_43.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_151 = QVBoxLayout()
        self.verticalLayout_151.setObjectName(u"verticalLayout_151")
        self.label_193 = QLabel(self.widget_83)
        self.label_193.setObjectName(u"label_193")

        self.verticalLayout_151.addWidget(self.label_193)

        self.label_194 = QLabel(self.widget_83)
        self.label_194.setObjectName(u"label_194")
        self.label_194.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_151.addWidget(self.label_194)


        self.gridLayout_43.addLayout(self.verticalLayout_151, 0, 0, 1, 1)

        self.ShengCunTiaoZhan_Enable = QCheckBox(self.widget_83)
        self.ShengCunTiaoZhan_Enable.setObjectName(u"ShengCunTiaoZhan_Enable")
        self.ShengCunTiaoZhan_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.ShengCunTiaoZhan_Enable.setStyleSheet(u"")

        self.gridLayout_43.addWidget(self.ShengCunTiaoZhan_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_152 = QVBoxLayout()
        self.verticalLayout_152.setObjectName(u"verticalLayout_152")
        self.label_195 = QLabel(self.widget_83)
        self.label_195.setObjectName(u"label_195")

        self.verticalLayout_152.addWidget(self.label_195)

        self.label_196 = QLabel(self.widget_83)
        self.label_196.setObjectName(u"label_196")
        self.label_196.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_152.addWidget(self.label_196)


        self.gridLayout_43.addLayout(self.verticalLayout_152, 1, 0, 1, 1)

        self.ShengCunTiaoZhan_next_execute_time = QLineEdit(self.widget_83)
        self.ShengCunTiaoZhan_next_execute_time.setObjectName(u"ShengCunTiaoZhan_next_execute_time")
        self.ShengCunTiaoZhan_next_execute_time.setMinimumSize(QSize(200, 0))
        self.ShengCunTiaoZhan_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.ShengCunTiaoZhan_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_43.addWidget(self.ShengCunTiaoZhan_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_43.setColumnStretch(0, 5)
        self.gridLayout_43.setColumnStretch(1, 2)

        self.verticalLayout_150.addLayout(self.gridLayout_43)


        self.verticalLayout_149.addWidget(self.widget_83)

        self.verticalSpacer_26 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_149.addItem(self.verticalSpacer_26)

        self.scrollArea_34.setWidget(self.scrollAreaWidgetContents_31)

        self.horizontalLayout_63.addWidget(self.scrollArea_34)

        self.horizontalSpacer_62 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_63.addItem(self.horizontalSpacer_62)

        self.horizontalLayout_63.setStretch(0, 1)
        self.horizontalLayout_63.setStretch(1, 5)
        self.horizontalLayout_63.setStretch(2, 1)

        self.horizontalLayout_47.addWidget(self.widget_82)

        self.stackedWidget.addWidget(self.ShengCunTiaoZhan_widget)
        self.MiJingTanXian_widget = QWidget()
        self.MiJingTanXian_widget.setObjectName(u"MiJingTanXian_widget")
        self.horizontalLayout_65 = QHBoxLayout(self.MiJingTanXian_widget)
        self.horizontalLayout_65.setObjectName(u"horizontalLayout_65")
        self.widget_84 = QWidget(self.MiJingTanXian_widget)
        self.widget_84.setObjectName(u"widget_84")
        self.widget_84.setStyleSheet(u"")
        self.horizontalLayout_64 = QHBoxLayout(self.widget_84)
        self.horizontalLayout_64.setObjectName(u"horizontalLayout_64")
        self.horizontalSpacer_63 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_64.addItem(self.horizontalSpacer_63)

        self.scrollArea_35 = QScrollArea(self.widget_84)
        self.scrollArea_35.setObjectName(u"scrollArea_35")
        self.scrollArea_35.setMinimumSize(QSize(600, 0))
        self.scrollArea_35.setWidgetResizable(True)
        self.scrollArea_35.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_32 = QWidget()
        self.scrollAreaWidgetContents_32.setObjectName(u"scrollAreaWidgetContents_32")
        self.scrollAreaWidgetContents_32.setGeometry(QRect(0, 0, 566, 234))
        self.verticalLayout_153 = QVBoxLayout(self.scrollAreaWidgetContents_32)
        self.verticalLayout_153.setSpacing(20)
        self.verticalLayout_153.setObjectName(u"verticalLayout_153")
        self.widget_85 = QWidget(self.scrollAreaWidgetContents_32)
        self.widget_85.setObjectName(u"widget_85")
        self.widget_85.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_154 = QVBoxLayout(self.widget_85)
        self.verticalLayout_154.setObjectName(u"verticalLayout_154")
        self.verticalLayout_154.setContentsMargins(-1, 7, -1, -1)
        self.label_197 = QLabel(self.widget_85)
        self.label_197.setObjectName(u"label_197")
        self.label_197.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_154.addWidget(self.label_197)

        self.frame_39 = QFrame(self.widget_85)
        self.frame_39.setObjectName(u"frame_39")
        self.frame_39.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_39.setFrameShape(QFrame.Shape.HLine)
        self.frame_39.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_154.addWidget(self.frame_39)

        self.gridLayout_44 = QGridLayout()
        self.gridLayout_44.setObjectName(u"gridLayout_44")
        self.gridLayout_44.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_155 = QVBoxLayout()
        self.verticalLayout_155.setObjectName(u"verticalLayout_155")
        self.label_198 = QLabel(self.widget_85)
        self.label_198.setObjectName(u"label_198")

        self.verticalLayout_155.addWidget(self.label_198)

        self.label_199 = QLabel(self.widget_85)
        self.label_199.setObjectName(u"label_199")
        self.label_199.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_155.addWidget(self.label_199)


        self.gridLayout_44.addLayout(self.verticalLayout_155, 0, 0, 1, 1)

        self.MiJingTanXian_Enable = QCheckBox(self.widget_85)
        self.MiJingTanXian_Enable.setObjectName(u"MiJingTanXian_Enable")
        self.MiJingTanXian_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.MiJingTanXian_Enable.setStyleSheet(u"")

        self.gridLayout_44.addWidget(self.MiJingTanXian_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_156 = QVBoxLayout()
        self.verticalLayout_156.setObjectName(u"verticalLayout_156")
        self.label_200 = QLabel(self.widget_85)
        self.label_200.setObjectName(u"label_200")

        self.verticalLayout_156.addWidget(self.label_200)

        self.label_201 = QLabel(self.widget_85)
        self.label_201.setObjectName(u"label_201")
        self.label_201.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_156.addWidget(self.label_201)


        self.gridLayout_44.addLayout(self.verticalLayout_156, 1, 0, 1, 1)

        self.MiJingTanXian_next_execute_time = QLineEdit(self.widget_85)
        self.MiJingTanXian_next_execute_time.setObjectName(u"MiJingTanXian_next_execute_time")
        self.MiJingTanXian_next_execute_time.setMinimumSize(QSize(200, 0))
        self.MiJingTanXian_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.MiJingTanXian_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_44.addWidget(self.MiJingTanXian_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_44.setColumnStretch(0, 5)
        self.gridLayout_44.setColumnStretch(1, 2)

        self.verticalLayout_154.addLayout(self.gridLayout_44)


        self.verticalLayout_153.addWidget(self.widget_85)

        self.verticalSpacer_27 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_153.addItem(self.verticalSpacer_27)

        self.scrollArea_35.setWidget(self.scrollAreaWidgetContents_32)

        self.horizontalLayout_64.addWidget(self.scrollArea_35)

        self.horizontalSpacer_64 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_64.addItem(self.horizontalSpacer_64)

        self.horizontalLayout_64.setStretch(0, 1)
        self.horizontalLayout_64.setStretch(1, 5)
        self.horizontalLayout_64.setStretch(2, 1)

        self.horizontalLayout_65.addWidget(self.widget_84)

        self.stackedWidget.addWidget(self.MiJingTanXian_widget)
        self.ShangChengJiangLi_widget = QWidget()
        self.ShangChengJiangLi_widget.setObjectName(u"ShangChengJiangLi_widget")
        self.horizontalLayout_80 = QHBoxLayout(self.ShangChengJiangLi_widget)
        self.horizontalLayout_80.setObjectName(u"horizontalLayout_80")
        self.widget_107 = QWidget(self.ShangChengJiangLi_widget)
        self.widget_107.setObjectName(u"widget_107")
        self.widget_107.setStyleSheet(u"")
        self.horizontalLayout_79 = QHBoxLayout(self.widget_107)
        self.horizontalLayout_79.setObjectName(u"horizontalLayout_79")
        self.horizontalSpacer_83 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_79.addItem(self.horizontalSpacer_83)

        self.scrollArea_45 = QScrollArea(self.widget_107)
        self.scrollArea_45.setObjectName(u"scrollArea_45")
        self.scrollArea_45.setMinimumSize(QSize(600, 0))
        self.scrollArea_45.setWidgetResizable(True)
        self.scrollArea_45.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_42 = QWidget()
        self.scrollAreaWidgetContents_42.setObjectName(u"scrollAreaWidgetContents_42")
        self.scrollAreaWidgetContents_42.setGeometry(QRect(0, 0, 566, 234))
        self.verticalLayout_199 = QVBoxLayout(self.scrollAreaWidgetContents_42)
        self.verticalLayout_199.setSpacing(20)
        self.verticalLayout_199.setObjectName(u"verticalLayout_199")
        self.widget_108 = QWidget(self.scrollAreaWidgetContents_42)
        self.widget_108.setObjectName(u"widget_108")
        self.widget_108.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_200 = QVBoxLayout(self.widget_108)
        self.verticalLayout_200.setObjectName(u"verticalLayout_200")
        self.verticalLayout_200.setContentsMargins(-1, 7, -1, -1)
        self.label_259 = QLabel(self.widget_108)
        self.label_259.setObjectName(u"label_259")
        self.label_259.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_200.addWidget(self.label_259)

        self.frame_51 = QFrame(self.widget_108)
        self.frame_51.setObjectName(u"frame_51")
        self.frame_51.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_51.setFrameShape(QFrame.Shape.HLine)
        self.frame_51.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_200.addWidget(self.frame_51)

        self.gridLayout_55 = QGridLayout()
        self.gridLayout_55.setObjectName(u"gridLayout_55")
        self.gridLayout_55.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_201 = QVBoxLayout()
        self.verticalLayout_201.setObjectName(u"verticalLayout_201")
        self.label_261 = QLabel(self.widget_108)
        self.label_261.setObjectName(u"label_261")

        self.verticalLayout_201.addWidget(self.label_261)

        self.label_262 = QLabel(self.widget_108)
        self.label_262.setObjectName(u"label_262")
        self.label_262.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_201.addWidget(self.label_262)


        self.gridLayout_55.addLayout(self.verticalLayout_201, 0, 0, 1, 1)

        self.ShangChengJiangLi_Enable = QCheckBox(self.widget_108)
        self.ShangChengJiangLi_Enable.setObjectName(u"ShangChengJiangLi_Enable")
        self.ShangChengJiangLi_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.ShangChengJiangLi_Enable.setStyleSheet(u"")

        self.gridLayout_55.addWidget(self.ShangChengJiangLi_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_202 = QVBoxLayout()
        self.verticalLayout_202.setObjectName(u"verticalLayout_202")
        self.label_263 = QLabel(self.widget_108)
        self.label_263.setObjectName(u"label_263")

        self.verticalLayout_202.addWidget(self.label_263)

        self.label_264 = QLabel(self.widget_108)
        self.label_264.setObjectName(u"label_264")
        self.label_264.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_202.addWidget(self.label_264)


        self.gridLayout_55.addLayout(self.verticalLayout_202, 1, 0, 1, 1)

        self.ShangChengJiangLi_next_execute_time = QLineEdit(self.widget_108)
        self.ShangChengJiangLi_next_execute_time.setObjectName(u"ShangChengJiangLi_next_execute_time")
        self.ShangChengJiangLi_next_execute_time.setMinimumSize(QSize(200, 0))
        self.ShangChengJiangLi_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.ShangChengJiangLi_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_55.addWidget(self.ShangChengJiangLi_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_55.setColumnStretch(0, 5)
        self.gridLayout_55.setColumnStretch(1, 2)

        self.verticalLayout_200.addLayout(self.gridLayout_55)


        self.verticalLayout_199.addWidget(self.widget_108)

        self.verticalSpacer_38 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_199.addItem(self.verticalSpacer_38)

        self.scrollArea_45.setWidget(self.scrollAreaWidgetContents_42)

        self.horizontalLayout_79.addWidget(self.scrollArea_45)

        self.horizontalSpacer_84 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_79.addItem(self.horizontalSpacer_84)

        self.horizontalLayout_79.setStretch(0, 1)
        self.horizontalLayout_79.setStretch(1, 5)
        self.horizontalLayout_79.setStretch(2, 1)

        self.horizontalLayout_80.addWidget(self.widget_107)

        self.stackedWidget.addWidget(self.ShangChengJiangLi_widget)
        self.QingBaoZhan_widget = QWidget()
        self.QingBaoZhan_widget.setObjectName(u"QingBaoZhan_widget")
        self.horizontalLayout_50 = QHBoxLayout(self.QingBaoZhan_widget)
        self.horizontalLayout_50.setObjectName(u"horizontalLayout_50")
        self.widget_68 = QWidget(self.QingBaoZhan_widget)
        self.widget_68.setObjectName(u"widget_68")
        self.widget_68.setStyleSheet(u"")
        self.horizontalLayout_49 = QHBoxLayout(self.widget_68)
        self.horizontalLayout_49.setObjectName(u"horizontalLayout_49")
        self.horizontalSpacer_47 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_49.addItem(self.horizontalSpacer_47)

        self.scrollArea_27 = QScrollArea(self.widget_68)
        self.scrollArea_27.setObjectName(u"scrollArea_27")
        self.scrollArea_27.setMinimumSize(QSize(600, 0))
        self.scrollArea_27.setWidgetResizable(True)
        self.scrollArea_27.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_24 = QWidget()
        self.scrollAreaWidgetContents_24.setObjectName(u"scrollAreaWidgetContents_24")
        self.scrollAreaWidgetContents_24.setGeometry(QRect(0, 0, 566, 260))
        self.verticalLayout_121 = QVBoxLayout(self.scrollAreaWidgetContents_24)
        self.verticalLayout_121.setSpacing(20)
        self.verticalLayout_121.setObjectName(u"verticalLayout_121")
        self.widget_69 = QWidget(self.scrollAreaWidgetContents_24)
        self.widget_69.setObjectName(u"widget_69")
        self.widget_69.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_122 = QVBoxLayout(self.widget_69)
        self.verticalLayout_122.setObjectName(u"verticalLayout_122")
        self.verticalLayout_122.setContentsMargins(-1, 7, -1, -1)
        self.label_157 = QLabel(self.widget_69)
        self.label_157.setObjectName(u"label_157")
        self.label_157.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_122.addWidget(self.label_157)

        self.label_40 = QLabel(self.widget_69)
        self.label_40.setObjectName(u"label_40")
        self.label_40.setStyleSheet(u"font-size:13pt;\n"
"color:rgba(255, 0, 0, 100);\n"
"margin-left:18px;")

        self.verticalLayout_122.addWidget(self.label_40)

        self.frame_31 = QFrame(self.widget_69)
        self.frame_31.setObjectName(u"frame_31")
        self.frame_31.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_31.setFrameShape(QFrame.Shape.HLine)
        self.frame_31.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_122.addWidget(self.frame_31)

        self.gridLayout_36 = QGridLayout()
        self.gridLayout_36.setObjectName(u"gridLayout_36")
        self.gridLayout_36.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_123 = QVBoxLayout()
        self.verticalLayout_123.setObjectName(u"verticalLayout_123")
        self.label_158 = QLabel(self.widget_69)
        self.label_158.setObjectName(u"label_158")

        self.verticalLayout_123.addWidget(self.label_158)

        self.label_159 = QLabel(self.widget_69)
        self.label_159.setObjectName(u"label_159")
        self.label_159.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_123.addWidget(self.label_159)


        self.gridLayout_36.addLayout(self.verticalLayout_123, 0, 0, 1, 1)

        self.QingBaoZhan_Enable = QCheckBox(self.widget_69)
        self.QingBaoZhan_Enable.setObjectName(u"QingBaoZhan_Enable")
        self.QingBaoZhan_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.QingBaoZhan_Enable.setStyleSheet(u"")

        self.gridLayout_36.addWidget(self.QingBaoZhan_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_124 = QVBoxLayout()
        self.verticalLayout_124.setObjectName(u"verticalLayout_124")
        self.label_160 = QLabel(self.widget_69)
        self.label_160.setObjectName(u"label_160")

        self.verticalLayout_124.addWidget(self.label_160)

        self.label_161 = QLabel(self.widget_69)
        self.label_161.setObjectName(u"label_161")
        self.label_161.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_124.addWidget(self.label_161)


        self.gridLayout_36.addLayout(self.verticalLayout_124, 1, 0, 1, 1)

        self.QingBaoZhan_next_execute_time = QLineEdit(self.widget_69)
        self.QingBaoZhan_next_execute_time.setObjectName(u"QingBaoZhan_next_execute_time")
        self.QingBaoZhan_next_execute_time.setMinimumSize(QSize(200, 0))
        self.QingBaoZhan_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.QingBaoZhan_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_36.addWidget(self.QingBaoZhan_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_36.setColumnStretch(0, 5)
        self.gridLayout_36.setColumnStretch(1, 2)

        self.verticalLayout_122.addLayout(self.gridLayout_36)


        self.verticalLayout_121.addWidget(self.widget_69)

        self.verticalSpacer_19 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_121.addItem(self.verticalSpacer_19)

        self.scrollArea_27.setWidget(self.scrollAreaWidgetContents_24)

        self.horizontalLayout_49.addWidget(self.scrollArea_27)

        self.horizontalSpacer_48 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_49.addItem(self.horizontalSpacer_48)

        self.horizontalLayout_49.setStretch(0, 1)
        self.horizontalLayout_49.setStretch(1, 5)
        self.horizontalLayout_49.setStretch(2, 1)

        self.horizontalLayout_50.addWidget(self.widget_68)

        self.stackedWidget.addWidget(self.QingBaoZhan_widget)
        self.MaoXianFuBen_widget = QWidget()
        self.MaoXianFuBen_widget.setObjectName(u"MaoXianFuBen_widget")
        self.horizontalLayout_40 = QHBoxLayout(self.MaoXianFuBen_widget)
        self.horizontalLayout_40.setObjectName(u"horizontalLayout_40")
        self.widget_60 = QWidget(self.MaoXianFuBen_widget)
        self.widget_60.setObjectName(u"widget_60")
        self.widget_60.setStyleSheet(u"")
        self.horizontalLayout_39 = QHBoxLayout(self.widget_60)
        self.horizontalLayout_39.setObjectName(u"horizontalLayout_39")
        self.horizontalSpacer_39 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_39.addItem(self.horizontalSpacer_39)

        self.scrollArea_23 = QScrollArea(self.widget_60)
        self.scrollArea_23.setObjectName(u"scrollArea_23")
        self.scrollArea_23.setMinimumSize(QSize(600, 0))
        self.scrollArea_23.setWidgetResizable(True)
        self.scrollArea_23.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_20 = QWidget()
        self.scrollAreaWidgetContents_20.setObjectName(u"scrollAreaWidgetContents_20")
        self.scrollAreaWidgetContents_20.setGeometry(QRect(0, 0, 566, 280))
        self.verticalLayout_105 = QVBoxLayout(self.scrollAreaWidgetContents_20)
        self.verticalLayout_105.setSpacing(20)
        self.verticalLayout_105.setObjectName(u"verticalLayout_105")
        self.widget_61 = QWidget(self.scrollAreaWidgetContents_20)
        self.widget_61.setObjectName(u"widget_61")
        self.widget_61.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_106 = QVBoxLayout(self.widget_61)
        self.verticalLayout_106.setObjectName(u"verticalLayout_106")
        self.verticalLayout_106.setContentsMargins(-1, 7, -1, -1)
        self.label_97 = QLabel(self.widget_61)
        self.label_97.setObjectName(u"label_97")
        self.label_97.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_106.addWidget(self.label_97)

        self.label_53 = QLabel(self.widget_61)
        self.label_53.setObjectName(u"label_53")
        self.label_53.setStyleSheet(u"font-size:13pt;\n"
"color:rgba(255, 0, 0, 100);\n"
"margin-left:18px;")

        self.verticalLayout_106.addWidget(self.label_53)

        self.frame_27 = QFrame(self.widget_61)
        self.frame_27.setObjectName(u"frame_27")
        self.frame_27.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_27.setFrameShape(QFrame.Shape.HLine)
        self.frame_27.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_106.addWidget(self.frame_27)

        self.gridLayout_32 = QGridLayout()
        self.gridLayout_32.setObjectName(u"gridLayout_32")
        self.gridLayout_32.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_107 = QVBoxLayout()
        self.verticalLayout_107.setObjectName(u"verticalLayout_107")
        self.label_98 = QLabel(self.widget_61)
        self.label_98.setObjectName(u"label_98")

        self.verticalLayout_107.addWidget(self.label_98)

        self.label_99 = QLabel(self.widget_61)
        self.label_99.setObjectName(u"label_99")
        self.label_99.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_107.addWidget(self.label_99)


        self.gridLayout_32.addLayout(self.verticalLayout_107, 0, 0, 1, 1)

        self.MaoXianFuBen_Enable = QCheckBox(self.widget_61)
        self.MaoXianFuBen_Enable.setObjectName(u"MaoXianFuBen_Enable")
        self.MaoXianFuBen_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.MaoXianFuBen_Enable.setStyleSheet(u"")

        self.gridLayout_32.addWidget(self.MaoXianFuBen_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_108 = QVBoxLayout()
        self.verticalLayout_108.setObjectName(u"verticalLayout_108")
        self.label_148 = QLabel(self.widget_61)
        self.label_148.setObjectName(u"label_148")

        self.verticalLayout_108.addWidget(self.label_148)

        self.label_149 = QLabel(self.widget_61)
        self.label_149.setObjectName(u"label_149")
        self.label_149.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_108.addWidget(self.label_149)


        self.gridLayout_32.addLayout(self.verticalLayout_108, 1, 0, 1, 1)

        self.MaoXianFuBen_next_execute_time = QLineEdit(self.widget_61)
        self.MaoXianFuBen_next_execute_time.setObjectName(u"MaoXianFuBen_next_execute_time")
        self.MaoXianFuBen_next_execute_time.setMinimumSize(QSize(200, 0))
        self.MaoXianFuBen_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.MaoXianFuBen_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_32.addWidget(self.MaoXianFuBen_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_32.setColumnStretch(0, 5)
        self.gridLayout_32.setColumnStretch(1, 2)

        self.verticalLayout_106.addLayout(self.gridLayout_32)


        self.verticalLayout_105.addWidget(self.widget_61)

        self.verticalSpacer_15 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_105.addItem(self.verticalSpacer_15)

        self.scrollArea_23.setWidget(self.scrollAreaWidgetContents_20)

        self.horizontalLayout_39.addWidget(self.scrollArea_23)

        self.horizontalSpacer_40 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_39.addItem(self.horizontalSpacer_40)

        self.horizontalLayout_39.setStretch(0, 1)
        self.horizontalLayout_39.setStretch(1, 5)
        self.horizontalLayout_39.setStretch(2, 1)

        self.horizontalLayout_40.addWidget(self.widget_60)

        self.stackedWidget.addWidget(self.MaoXianFuBen_widget)
        self.HuoYueDuJiangLi_widget = QWidget()
        self.HuoYueDuJiangLi_widget.setObjectName(u"HuoYueDuJiangLi_widget")
        self.horizontalLayout_42 = QHBoxLayout(self.HuoYueDuJiangLi_widget)
        self.horizontalLayout_42.setObjectName(u"horizontalLayout_42")
        self.widget_62 = QWidget(self.HuoYueDuJiangLi_widget)
        self.widget_62.setObjectName(u"widget_62")
        self.widget_62.setStyleSheet(u"")
        self.horizontalLayout_41 = QHBoxLayout(self.widget_62)
        self.horizontalLayout_41.setObjectName(u"horizontalLayout_41")
        self.horizontalSpacer_41 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_41.addItem(self.horizontalSpacer_41)

        self.scrollArea_24 = QScrollArea(self.widget_62)
        self.scrollArea_24.setObjectName(u"scrollArea_24")
        self.scrollArea_24.setMinimumSize(QSize(600, 0))
        self.scrollArea_24.setWidgetResizable(True)
        self.scrollArea_24.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_21 = QWidget()
        self.scrollAreaWidgetContents_21.setObjectName(u"scrollAreaWidgetContents_21")
        self.scrollAreaWidgetContents_21.setGeometry(QRect(0, 0, 566, 234))
        self.verticalLayout_109 = QVBoxLayout(self.scrollAreaWidgetContents_21)
        self.verticalLayout_109.setSpacing(20)
        self.verticalLayout_109.setObjectName(u"verticalLayout_109")
        self.widget_63 = QWidget(self.scrollAreaWidgetContents_21)
        self.widget_63.setObjectName(u"widget_63")
        self.widget_63.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_110 = QVBoxLayout(self.widget_63)
        self.verticalLayout_110.setObjectName(u"verticalLayout_110")
        self.verticalLayout_110.setContentsMargins(-1, 7, -1, -1)
        self.label_100 = QLabel(self.widget_63)
        self.label_100.setObjectName(u"label_100")
        self.label_100.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_110.addWidget(self.label_100)

        self.frame_28 = QFrame(self.widget_63)
        self.frame_28.setObjectName(u"frame_28")
        self.frame_28.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_28.setFrameShape(QFrame.Shape.HLine)
        self.frame_28.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_110.addWidget(self.frame_28)

        self.gridLayout_33 = QGridLayout()
        self.gridLayout_33.setObjectName(u"gridLayout_33")
        self.gridLayout_33.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_111 = QVBoxLayout()
        self.verticalLayout_111.setObjectName(u"verticalLayout_111")
        self.label_101 = QLabel(self.widget_63)
        self.label_101.setObjectName(u"label_101")

        self.verticalLayout_111.addWidget(self.label_101)

        self.label_102 = QLabel(self.widget_63)
        self.label_102.setObjectName(u"label_102")
        self.label_102.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_111.addWidget(self.label_102)


        self.gridLayout_33.addLayout(self.verticalLayout_111, 0, 0, 1, 1)

        self.HuoYueDuJiangLi_Enable = QCheckBox(self.widget_63)
        self.HuoYueDuJiangLi_Enable.setObjectName(u"HuoYueDuJiangLi_Enable")
        self.HuoYueDuJiangLi_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.HuoYueDuJiangLi_Enable.setStyleSheet(u"")

        self.gridLayout_33.addWidget(self.HuoYueDuJiangLi_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_112 = QVBoxLayout()
        self.verticalLayout_112.setObjectName(u"verticalLayout_112")
        self.label_150 = QLabel(self.widget_63)
        self.label_150.setObjectName(u"label_150")

        self.verticalLayout_112.addWidget(self.label_150)

        self.label_151 = QLabel(self.widget_63)
        self.label_151.setObjectName(u"label_151")
        self.label_151.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_112.addWidget(self.label_151)


        self.gridLayout_33.addLayout(self.verticalLayout_112, 1, 0, 1, 1)

        self.HuoYueDuJiangLi_next_execute_time = QLineEdit(self.widget_63)
        self.HuoYueDuJiangLi_next_execute_time.setObjectName(u"HuoYueDuJiangLi_next_execute_time")
        self.HuoYueDuJiangLi_next_execute_time.setMinimumSize(QSize(200, 0))
        self.HuoYueDuJiangLi_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.HuoYueDuJiangLi_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_33.addWidget(self.HuoYueDuJiangLi_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_33.setColumnStretch(0, 5)
        self.gridLayout_33.setColumnStretch(1, 2)

        self.verticalLayout_110.addLayout(self.gridLayout_33)


        self.verticalLayout_109.addWidget(self.widget_63)

        self.verticalSpacer_16 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_109.addItem(self.verticalSpacer_16)

        self.scrollArea_24.setWidget(self.scrollAreaWidgetContents_21)

        self.horizontalLayout_41.addWidget(self.scrollArea_24)

        self.horizontalSpacer_42 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_41.addItem(self.horizontalSpacer_42)

        self.horizontalLayout_41.setStretch(0, 1)
        self.horizontalLayout_41.setStretch(1, 5)
        self.horizontalLayout_41.setStretch(2, 1)

        self.horizontalLayout_42.addWidget(self.widget_62)

        self.stackedWidget.addWidget(self.HuoYueDuJiangLi_widget)
        self.QingKongYouJian_widget = QWidget()
        self.QingKongYouJian_widget.setObjectName(u"QingKongYouJian_widget")
        self.horizontalLayout_52 = QHBoxLayout(self.QingKongYouJian_widget)
        self.horizontalLayout_52.setObjectName(u"horizontalLayout_52")
        self.widget_70 = QWidget(self.QingKongYouJian_widget)
        self.widget_70.setObjectName(u"widget_70")
        self.widget_70.setStyleSheet(u"")
        self.horizontalLayout_51 = QHBoxLayout(self.widget_70)
        self.horizontalLayout_51.setObjectName(u"horizontalLayout_51")
        self.horizontalSpacer_49 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_51.addItem(self.horizontalSpacer_49)

        self.scrollArea_28 = QScrollArea(self.widget_70)
        self.scrollArea_28.setObjectName(u"scrollArea_28")
        self.scrollArea_28.setMinimumSize(QSize(600, 0))
        self.scrollArea_28.setWidgetResizable(True)
        self.scrollArea_28.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_25 = QWidget()
        self.scrollAreaWidgetContents_25.setObjectName(u"scrollAreaWidgetContents_25")
        self.scrollAreaWidgetContents_25.setGeometry(QRect(0, 0, 566, 234))
        self.verticalLayout_125 = QVBoxLayout(self.scrollAreaWidgetContents_25)
        self.verticalLayout_125.setSpacing(20)
        self.verticalLayout_125.setObjectName(u"verticalLayout_125")
        self.widget_71 = QWidget(self.scrollAreaWidgetContents_25)
        self.widget_71.setObjectName(u"widget_71")
        self.widget_71.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_126 = QVBoxLayout(self.widget_71)
        self.verticalLayout_126.setObjectName(u"verticalLayout_126")
        self.verticalLayout_126.setContentsMargins(-1, 7, -1, -1)
        self.label_162 = QLabel(self.widget_71)
        self.label_162.setObjectName(u"label_162")
        self.label_162.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_126.addWidget(self.label_162)

        self.frame_32 = QFrame(self.widget_71)
        self.frame_32.setObjectName(u"frame_32")
        self.frame_32.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_32.setFrameShape(QFrame.Shape.HLine)
        self.frame_32.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_126.addWidget(self.frame_32)

        self.gridLayout_37 = QGridLayout()
        self.gridLayout_37.setObjectName(u"gridLayout_37")
        self.gridLayout_37.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_127 = QVBoxLayout()
        self.verticalLayout_127.setObjectName(u"verticalLayout_127")
        self.label_163 = QLabel(self.widget_71)
        self.label_163.setObjectName(u"label_163")

        self.verticalLayout_127.addWidget(self.label_163)

        self.label_164 = QLabel(self.widget_71)
        self.label_164.setObjectName(u"label_164")
        self.label_164.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_127.addWidget(self.label_164)


        self.gridLayout_37.addLayout(self.verticalLayout_127, 0, 0, 1, 1)

        self.QingKongYouJian_Enable = QCheckBox(self.widget_71)
        self.QingKongYouJian_Enable.setObjectName(u"QingKongYouJian_Enable")
        self.QingKongYouJian_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.QingKongYouJian_Enable.setStyleSheet(u"")

        self.gridLayout_37.addWidget(self.QingKongYouJian_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_128 = QVBoxLayout()
        self.verticalLayout_128.setObjectName(u"verticalLayout_128")
        self.label_165 = QLabel(self.widget_71)
        self.label_165.setObjectName(u"label_165")

        self.verticalLayout_128.addWidget(self.label_165)

        self.label_166 = QLabel(self.widget_71)
        self.label_166.setObjectName(u"label_166")
        self.label_166.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_128.addWidget(self.label_166)


        self.gridLayout_37.addLayout(self.verticalLayout_128, 1, 0, 1, 1)

        self.QingKongYouJian_next_execute_time = QLineEdit(self.widget_71)
        self.QingKongYouJian_next_execute_time.setObjectName(u"QingKongYouJian_next_execute_time")
        self.QingKongYouJian_next_execute_time.setMinimumSize(QSize(200, 0))
        self.QingKongYouJian_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.QingKongYouJian_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_37.addWidget(self.QingKongYouJian_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_37.setColumnStretch(0, 5)
        self.gridLayout_37.setColumnStretch(1, 2)

        self.verticalLayout_126.addLayout(self.gridLayout_37)


        self.verticalLayout_125.addWidget(self.widget_71)

        self.verticalSpacer_20 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_125.addItem(self.verticalSpacer_20)

        self.scrollArea_28.setWidget(self.scrollAreaWidgetContents_25)

        self.horizontalLayout_51.addWidget(self.scrollArea_28)

        self.horizontalSpacer_50 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_51.addItem(self.horizontalSpacer_50)

        self.horizontalLayout_51.setStretch(0, 1)
        self.horizontalLayout_51.setStretch(1, 5)
        self.horizontalLayout_51.setStretch(2, 1)

        self.horizontalLayout_52.addWidget(self.widget_70)

        self.stackedWidget.addWidget(self.QingKongYouJian_widget)
        self.XiuXingZhiLu_widget = QWidget()
        self.XiuXingZhiLu_widget.setObjectName(u"XiuXingZhiLu_widget")
        self.horizontalLayout_53 = QHBoxLayout(self.XiuXingZhiLu_widget)
        self.horizontalLayout_53.setObjectName(u"horizontalLayout_53")
        self.widget_76 = QWidget(self.XiuXingZhiLu_widget)
        self.widget_76.setObjectName(u"widget_76")
        self.widget_76.setStyleSheet(u"")
        self.horizontalLayout_60 = QHBoxLayout(self.widget_76)
        self.horizontalLayout_60.setObjectName(u"horizontalLayout_60")
        self.horizontalSpacer_55 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_60.addItem(self.horizontalSpacer_55)

        self.scrollArea_31 = QScrollArea(self.widget_76)
        self.scrollArea_31.setObjectName(u"scrollArea_31")
        self.scrollArea_31.setMinimumSize(QSize(600, 0))
        self.scrollArea_31.setWidgetResizable(True)
        self.scrollArea_31.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_28 = QWidget()
        self.scrollAreaWidgetContents_28.setObjectName(u"scrollAreaWidgetContents_28")
        self.scrollAreaWidgetContents_28.setGeometry(QRect(0, 0, 566, 234))
        self.verticalLayout_137 = QVBoxLayout(self.scrollAreaWidgetContents_28)
        self.verticalLayout_137.setSpacing(20)
        self.verticalLayout_137.setObjectName(u"verticalLayout_137")
        self.widget_77 = QWidget(self.scrollAreaWidgetContents_28)
        self.widget_77.setObjectName(u"widget_77")
        self.widget_77.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_138 = QVBoxLayout(self.widget_77)
        self.verticalLayout_138.setObjectName(u"verticalLayout_138")
        self.verticalLayout_138.setContentsMargins(-1, 7, -1, -1)
        self.label_177 = QLabel(self.widget_77)
        self.label_177.setObjectName(u"label_177")
        self.label_177.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_138.addWidget(self.label_177)

        self.frame_35 = QFrame(self.widget_77)
        self.frame_35.setObjectName(u"frame_35")
        self.frame_35.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_35.setFrameShape(QFrame.Shape.HLine)
        self.frame_35.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_138.addWidget(self.frame_35)

        self.gridLayout_40 = QGridLayout()
        self.gridLayout_40.setObjectName(u"gridLayout_40")
        self.gridLayout_40.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_139 = QVBoxLayout()
        self.verticalLayout_139.setObjectName(u"verticalLayout_139")
        self.label_178 = QLabel(self.widget_77)
        self.label_178.setObjectName(u"label_178")

        self.verticalLayout_139.addWidget(self.label_178)

        self.label_179 = QLabel(self.widget_77)
        self.label_179.setObjectName(u"label_179")
        self.label_179.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_139.addWidget(self.label_179)


        self.gridLayout_40.addLayout(self.verticalLayout_139, 0, 0, 1, 1)

        self.XiuXingZhiLu_Enable = QCheckBox(self.widget_77)
        self.XiuXingZhiLu_Enable.setObjectName(u"XiuXingZhiLu_Enable")
        self.XiuXingZhiLu_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.XiuXingZhiLu_Enable.setStyleSheet(u"")

        self.gridLayout_40.addWidget(self.XiuXingZhiLu_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_140 = QVBoxLayout()
        self.verticalLayout_140.setObjectName(u"verticalLayout_140")
        self.label_180 = QLabel(self.widget_77)
        self.label_180.setObjectName(u"label_180")

        self.verticalLayout_140.addWidget(self.label_180)

        self.label_181 = QLabel(self.widget_77)
        self.label_181.setObjectName(u"label_181")
        self.label_181.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_140.addWidget(self.label_181)


        self.gridLayout_40.addLayout(self.verticalLayout_140, 1, 0, 1, 1)

        self.XiuXingZhiLu_next_execute_time = QLineEdit(self.widget_77)
        self.XiuXingZhiLu_next_execute_time.setObjectName(u"XiuXingZhiLu_next_execute_time")
        self.XiuXingZhiLu_next_execute_time.setMinimumSize(QSize(200, 0))
        self.XiuXingZhiLu_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.XiuXingZhiLu_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_40.addWidget(self.XiuXingZhiLu_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_40.setColumnStretch(0, 5)
        self.gridLayout_40.setColumnStretch(1, 2)

        self.verticalLayout_138.addLayout(self.gridLayout_40)


        self.verticalLayout_137.addWidget(self.widget_77)

        self.verticalSpacer_23 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_137.addItem(self.verticalSpacer_23)

        self.scrollArea_31.setWidget(self.scrollAreaWidgetContents_28)

        self.horizontalLayout_60.addWidget(self.scrollArea_31)

        self.horizontalSpacer_56 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_60.addItem(self.horizontalSpacer_56)

        self.horizontalLayout_60.setStretch(0, 1)
        self.horizontalLayout_60.setStretch(1, 5)
        self.horizontalLayout_60.setStretch(2, 1)

        self.horizontalLayout_53.addWidget(self.widget_76)

        self.stackedWidget.addWidget(self.XiuXingZhiLu_widget)
        self.MeiZhouShengChang_widget = QWidget()
        self.MeiZhouShengChang_widget.setObjectName(u"MeiZhouShengChang_widget")
        self.horizontalLayout_19 = QHBoxLayout(self.MeiZhouShengChang_widget)
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.widget_38 = QWidget(self.MeiZhouShengChang_widget)
        self.widget_38.setObjectName(u"widget_38")
        self.widget_38.setStyleSheet(u"")
        self.horizontalLayout_18 = QHBoxLayout(self.widget_38)
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.horizontalSpacer_17 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer_17)

        self.scrollArea_12 = QScrollArea(self.widget_38)
        self.scrollArea_12.setObjectName(u"scrollArea_12")
        self.scrollArea_12.setMinimumSize(QSize(600, 0))
        self.scrollArea_12.setWidgetResizable(True)
        self.scrollArea_12.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_9 = QWidget()
        self.scrollAreaWidgetContents_9.setObjectName(u"scrollAreaWidgetContents_9")
        self.scrollAreaWidgetContents_9.setGeometry(QRect(0, 0, 566, 252))
        self.verticalLayout_61 = QVBoxLayout(self.scrollAreaWidgetContents_9)
        self.verticalLayout_61.setSpacing(20)
        self.verticalLayout_61.setObjectName(u"verticalLayout_61")
        self.widget_39 = QWidget(self.scrollAreaWidgetContents_9)
        self.widget_39.setObjectName(u"widget_39")
        self.widget_39.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_62 = QVBoxLayout(self.widget_39)
        self.verticalLayout_62.setObjectName(u"verticalLayout_62")
        self.verticalLayout_62.setContentsMargins(-1, 7, -1, -1)
        self.label_64 = QLabel(self.widget_39)
        self.label_64.setObjectName(u"label_64")
        self.label_64.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_62.addWidget(self.label_64)

        self.frame_16 = QFrame(self.widget_39)
        self.frame_16.setObjectName(u"frame_16")
        self.frame_16.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_16.setFrameShape(QFrame.Shape.HLine)
        self.frame_16.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_62.addWidget(self.frame_16)

        self.gridLayout_21 = QGridLayout()
        self.gridLayout_21.setObjectName(u"gridLayout_21")
        self.gridLayout_21.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_63 = QVBoxLayout()
        self.verticalLayout_63.setObjectName(u"verticalLayout_63")
        self.label_65 = QLabel(self.widget_39)
        self.label_65.setObjectName(u"label_65")

        self.verticalLayout_63.addWidget(self.label_65)

        self.label_66 = QLabel(self.widget_39)
        self.label_66.setObjectName(u"label_66")
        self.label_66.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_63.addWidget(self.label_66)


        self.gridLayout_21.addLayout(self.verticalLayout_63, 0, 0, 1, 1)

        self.MeiZhouShengChang_Enable = QCheckBox(self.widget_39)
        self.MeiZhouShengChang_Enable.setObjectName(u"MeiZhouShengChang_Enable")
        self.MeiZhouShengChang_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.MeiZhouShengChang_Enable.setStyleSheet(u"")

        self.gridLayout_21.addWidget(self.MeiZhouShengChang_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_64 = QVBoxLayout()
        self.verticalLayout_64.setObjectName(u"verticalLayout_64")
        self.label_126 = QLabel(self.widget_39)
        self.label_126.setObjectName(u"label_126")

        self.verticalLayout_64.addWidget(self.label_126)

        self.label_127 = QLabel(self.widget_39)
        self.label_127.setObjectName(u"label_127")
        self.label_127.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_64.addWidget(self.label_127)


        self.gridLayout_21.addLayout(self.verticalLayout_64, 1, 0, 1, 1)

        self.MeiZhouShengChang_next_execute_time = QLineEdit(self.widget_39)
        self.MeiZhouShengChang_next_execute_time.setObjectName(u"MeiZhouShengChang_next_execute_time")
        self.MeiZhouShengChang_next_execute_time.setMinimumSize(QSize(200, 0))
        self.MeiZhouShengChang_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.MeiZhouShengChang_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_21.addWidget(self.MeiZhouShengChang_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_21.setColumnStretch(0, 5)
        self.gridLayout_21.setColumnStretch(1, 2)

        self.verticalLayout_62.addLayout(self.gridLayout_21)


        self.verticalLayout_61.addWidget(self.widget_39)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_61.addItem(self.verticalSpacer_4)

        self.scrollArea_12.setWidget(self.scrollAreaWidgetContents_9)

        self.horizontalLayout_18.addWidget(self.scrollArea_12)

        self.horizontalSpacer_18 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer_18)

        self.horizontalLayout_18.setStretch(0, 1)
        self.horizontalLayout_18.setStretch(1, 5)
        self.horizontalLayout_18.setStretch(2, 1)

        self.horizontalLayout_19.addWidget(self.widget_38)

        self.stackedWidget.addWidget(self.MeiZhouShengChang_widget)
        self.RenFaTieDianZanFenXiang_widget = QWidget()
        self.RenFaTieDianZanFenXiang_widget.setObjectName(u"RenFaTieDianZanFenXiang_widget")
        self.horizontalLayout_58 = QHBoxLayout(self.RenFaTieDianZanFenXiang_widget)
        self.horizontalLayout_58.setObjectName(u"horizontalLayout_58")
        self.widget_72 = QWidget(self.RenFaTieDianZanFenXiang_widget)
        self.widget_72.setObjectName(u"widget_72")
        self.widget_72.setStyleSheet(u"")
        self.horizontalLayout_54 = QHBoxLayout(self.widget_72)
        self.horizontalLayout_54.setObjectName(u"horizontalLayout_54")
        self.horizontalSpacer_51 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_54.addItem(self.horizontalSpacer_51)

        self.scrollArea_29 = QScrollArea(self.widget_72)
        self.scrollArea_29.setObjectName(u"scrollArea_29")
        self.scrollArea_29.setMinimumSize(QSize(600, 0))
        self.scrollArea_29.setWidgetResizable(True)
        self.scrollArea_29.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_26 = QWidget()
        self.scrollAreaWidgetContents_26.setObjectName(u"scrollAreaWidgetContents_26")
        self.scrollAreaWidgetContents_26.setGeometry(QRect(0, 0, 566, 260))
        self.verticalLayout_129 = QVBoxLayout(self.scrollAreaWidgetContents_26)
        self.verticalLayout_129.setSpacing(20)
        self.verticalLayout_129.setObjectName(u"verticalLayout_129")
        self.widget_73 = QWidget(self.scrollAreaWidgetContents_26)
        self.widget_73.setObjectName(u"widget_73")
        self.widget_73.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_130 = QVBoxLayout(self.widget_73)
        self.verticalLayout_130.setObjectName(u"verticalLayout_130")
        self.verticalLayout_130.setContentsMargins(-1, 7, -1, -1)
        self.label_167 = QLabel(self.widget_73)
        self.label_167.setObjectName(u"label_167")
        self.label_167.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_130.addWidget(self.label_167)

        self.label_51 = QLabel(self.widget_73)
        self.label_51.setObjectName(u"label_51")
        self.label_51.setStyleSheet(u"font-size:13pt;\n"
"color:rgba(255, 0, 0, 100);\n"
"margin-left:18px;")

        self.verticalLayout_130.addWidget(self.label_51)

        self.frame_33 = QFrame(self.widget_73)
        self.frame_33.setObjectName(u"frame_33")
        self.frame_33.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_33.setFrameShape(QFrame.Shape.HLine)
        self.frame_33.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_130.addWidget(self.frame_33)

        self.gridLayout_38 = QGridLayout()
        self.gridLayout_38.setObjectName(u"gridLayout_38")
        self.gridLayout_38.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_131 = QVBoxLayout()
        self.verticalLayout_131.setObjectName(u"verticalLayout_131")
        self.label_168 = QLabel(self.widget_73)
        self.label_168.setObjectName(u"label_168")

        self.verticalLayout_131.addWidget(self.label_168)

        self.label_169 = QLabel(self.widget_73)
        self.label_169.setObjectName(u"label_169")
        self.label_169.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_131.addWidget(self.label_169)


        self.gridLayout_38.addLayout(self.verticalLayout_131, 0, 0, 1, 1)

        self.RenFaTieDianZanFenXiang_Enable = QCheckBox(self.widget_73)
        self.RenFaTieDianZanFenXiang_Enable.setObjectName(u"RenFaTieDianZanFenXiang_Enable")
        self.RenFaTieDianZanFenXiang_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.RenFaTieDianZanFenXiang_Enable.setStyleSheet(u"")

        self.gridLayout_38.addWidget(self.RenFaTieDianZanFenXiang_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_132 = QVBoxLayout()
        self.verticalLayout_132.setObjectName(u"verticalLayout_132")
        self.label_170 = QLabel(self.widget_73)
        self.label_170.setObjectName(u"label_170")

        self.verticalLayout_132.addWidget(self.label_170)

        self.label_171 = QLabel(self.widget_73)
        self.label_171.setObjectName(u"label_171")
        self.label_171.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_132.addWidget(self.label_171)


        self.gridLayout_38.addLayout(self.verticalLayout_132, 1, 0, 1, 1)

        self.RenFaTieDianZanFenXiang_next_execute_time = QLineEdit(self.widget_73)
        self.RenFaTieDianZanFenXiang_next_execute_time.setObjectName(u"RenFaTieDianZanFenXiang_next_execute_time")
        self.RenFaTieDianZanFenXiang_next_execute_time.setMinimumSize(QSize(200, 0))
        self.RenFaTieDianZanFenXiang_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.RenFaTieDianZanFenXiang_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_38.addWidget(self.RenFaTieDianZanFenXiang_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_38.setColumnStretch(0, 5)
        self.gridLayout_38.setColumnStretch(1, 2)

        self.verticalLayout_130.addLayout(self.gridLayout_38)


        self.verticalLayout_129.addWidget(self.widget_73)

        self.verticalSpacer_21 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_129.addItem(self.verticalSpacer_21)

        self.scrollArea_29.setWidget(self.scrollAreaWidgetContents_26)

        self.horizontalLayout_54.addWidget(self.scrollArea_29)

        self.horizontalSpacer_52 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_54.addItem(self.horizontalSpacer_52)

        self.horizontalLayout_54.setStretch(0, 1)
        self.horizontalLayout_54.setStretch(1, 5)
        self.horizontalLayout_54.setStretch(2, 1)

        self.horizontalLayout_58.addWidget(self.widget_72)

        self.stackedWidget.addWidget(self.RenFaTieDianZanFenXiang_widget)
        self.GengDuoWanFa_widget = QWidget()
        self.GengDuoWanFa_widget.setObjectName(u"GengDuoWanFa_widget")
        self.horizontalLayout_23 = QHBoxLayout(self.GengDuoWanFa_widget)
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.widget_42 = QWidget(self.GengDuoWanFa_widget)
        self.widget_42.setObjectName(u"widget_42")
        self.widget_42.setStyleSheet(u"")
        self.horizontalLayout_22 = QHBoxLayout(self.widget_42)
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.horizontalSpacer_21 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_22.addItem(self.horizontalSpacer_21)

        self.scrollArea_14 = QScrollArea(self.widget_42)
        self.scrollArea_14.setObjectName(u"scrollArea_14")
        self.scrollArea_14.setMinimumSize(QSize(600, 0))
        self.scrollArea_14.setWidgetResizable(True)
        self.scrollArea_14.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_11 = QWidget()
        self.scrollAreaWidgetContents_11.setObjectName(u"scrollAreaWidgetContents_11")
        self.scrollAreaWidgetContents_11.setGeometry(QRect(0, 0, 566, 252))
        self.verticalLayout_69 = QVBoxLayout(self.scrollAreaWidgetContents_11)
        self.verticalLayout_69.setSpacing(20)
        self.verticalLayout_69.setObjectName(u"verticalLayout_69")
        self.widget_43 = QWidget(self.scrollAreaWidgetContents_11)
        self.widget_43.setObjectName(u"widget_43")
        self.widget_43.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_70 = QVBoxLayout(self.widget_43)
        self.verticalLayout_70.setObjectName(u"verticalLayout_70")
        self.verticalLayout_70.setContentsMargins(-1, 7, -1, -1)
        self.label_70 = QLabel(self.widget_43)
        self.label_70.setObjectName(u"label_70")
        self.label_70.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_70.addWidget(self.label_70)

        self.frame_18 = QFrame(self.widget_43)
        self.frame_18.setObjectName(u"frame_18")
        self.frame_18.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_18.setFrameShape(QFrame.Shape.HLine)
        self.frame_18.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_70.addWidget(self.frame_18)

        self.gridLayout_23 = QGridLayout()
        self.gridLayout_23.setObjectName(u"gridLayout_23")
        self.gridLayout_23.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_71 = QVBoxLayout()
        self.verticalLayout_71.setObjectName(u"verticalLayout_71")
        self.label_71 = QLabel(self.widget_43)
        self.label_71.setObjectName(u"label_71")

        self.verticalLayout_71.addWidget(self.label_71)

        self.label_72 = QLabel(self.widget_43)
        self.label_72.setObjectName(u"label_72")
        self.label_72.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_71.addWidget(self.label_72)


        self.gridLayout_23.addLayout(self.verticalLayout_71, 0, 0, 1, 1)

        self.GengDuoWanFa_Enable = QCheckBox(self.widget_43)
        self.GengDuoWanFa_Enable.setObjectName(u"GengDuoWanFa_Enable")
        self.GengDuoWanFa_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.GengDuoWanFa_Enable.setStyleSheet(u"")

        self.gridLayout_23.addWidget(self.GengDuoWanFa_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_72 = QVBoxLayout()
        self.verticalLayout_72.setObjectName(u"verticalLayout_72")
        self.label_130 = QLabel(self.widget_43)
        self.label_130.setObjectName(u"label_130")

        self.verticalLayout_72.addWidget(self.label_130)

        self.label_131 = QLabel(self.widget_43)
        self.label_131.setObjectName(u"label_131")
        self.label_131.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_72.addWidget(self.label_131)


        self.gridLayout_23.addLayout(self.verticalLayout_72, 1, 0, 1, 1)

        self.GengDuoWanFa_next_execute_time = QLineEdit(self.widget_43)
        self.GengDuoWanFa_next_execute_time.setObjectName(u"GengDuoWanFa_next_execute_time")
        self.GengDuoWanFa_next_execute_time.setMinimumSize(QSize(200, 0))
        self.GengDuoWanFa_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.GengDuoWanFa_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_23.addWidget(self.GengDuoWanFa_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_23.setColumnStretch(0, 5)
        self.gridLayout_23.setColumnStretch(1, 2)

        self.verticalLayout_70.addLayout(self.gridLayout_23)


        self.verticalLayout_69.addWidget(self.widget_43)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_69.addItem(self.verticalSpacer_6)

        self.scrollArea_14.setWidget(self.scrollAreaWidgetContents_11)

        self.horizontalLayout_22.addWidget(self.scrollArea_14)

        self.horizontalSpacer_22 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_22.addItem(self.horizontalSpacer_22)

        self.horizontalLayout_22.setStretch(0, 1)
        self.horizontalLayout_22.setStretch(1, 5)
        self.horizontalLayout_22.setStretch(2, 1)

        self.horizontalLayout_23.addWidget(self.widget_42)

        self.stackedWidget.addWidget(self.GengDuoWanFa_widget)
        self.TuanBen_widget = QWidget()
        self.TuanBen_widget.setObjectName(u"TuanBen_widget")
        self.horizontalLayout_67 = QHBoxLayout(self.TuanBen_widget)
        self.horizontalLayout_67.setObjectName(u"horizontalLayout_67")
        self.widget_88 = QWidget(self.TuanBen_widget)
        self.widget_88.setObjectName(u"widget_88")
        self.widget_88.setStyleSheet(u"")
        self.horizontalLayout_55 = QHBoxLayout(self.widget_88)
        self.horizontalLayout_55.setObjectName(u"horizontalLayout_55")
        self.horizontalSpacer_67 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_55.addItem(self.horizontalSpacer_67)

        self.scrollArea_37 = QScrollArea(self.widget_88)
        self.scrollArea_37.setObjectName(u"scrollArea_37")
        self.scrollArea_37.setMinimumSize(QSize(600, 0))
        self.scrollArea_37.setWidgetResizable(True)
        self.scrollArea_37.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_34 = QWidget()
        self.scrollAreaWidgetContents_34.setObjectName(u"scrollAreaWidgetContents_34")
        self.scrollAreaWidgetContents_34.setGeometry(QRect(0, 0, 566, 260))
        self.verticalLayout_161 = QVBoxLayout(self.scrollAreaWidgetContents_34)
        self.verticalLayout_161.setSpacing(20)
        self.verticalLayout_161.setObjectName(u"verticalLayout_161")
        self.widget_89 = QWidget(self.scrollAreaWidgetContents_34)
        self.widget_89.setObjectName(u"widget_89")
        self.widget_89.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_162 = QVBoxLayout(self.widget_89)
        self.verticalLayout_162.setObjectName(u"verticalLayout_162")
        self.verticalLayout_162.setContentsMargins(-1, 7, -1, -1)
        self.label_208 = QLabel(self.widget_89)
        self.label_208.setObjectName(u"label_208")
        self.label_208.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_162.addWidget(self.label_208)

        self.label_209 = QLabel(self.widget_89)
        self.label_209.setObjectName(u"label_209")
        self.label_209.setStyleSheet(u"font-size:13pt;\n"
"color:rgba(255, 0, 0, 100);\n"
"margin-left:18px;")

        self.verticalLayout_162.addWidget(self.label_209)

        self.frame_41 = QFrame(self.widget_89)
        self.frame_41.setObjectName(u"frame_41")
        self.frame_41.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_41.setFrameShape(QFrame.Shape.HLine)
        self.frame_41.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_162.addWidget(self.frame_41)

        self.gridLayout_46 = QGridLayout()
        self.gridLayout_46.setObjectName(u"gridLayout_46")
        self.gridLayout_46.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_163 = QVBoxLayout()
        self.verticalLayout_163.setObjectName(u"verticalLayout_163")
        self.label_210 = QLabel(self.widget_89)
        self.label_210.setObjectName(u"label_210")

        self.verticalLayout_163.addWidget(self.label_210)

        self.label_211 = QLabel(self.widget_89)
        self.label_211.setObjectName(u"label_211")
        self.label_211.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_163.addWidget(self.label_211)


        self.gridLayout_46.addLayout(self.verticalLayout_163, 0, 0, 1, 1)

        self.TuanBen_Enable = QCheckBox(self.widget_89)
        self.TuanBen_Enable.setObjectName(u"TuanBen_Enable")
        self.TuanBen_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.TuanBen_Enable.setStyleSheet(u"")

        self.gridLayout_46.addWidget(self.TuanBen_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_164 = QVBoxLayout()
        self.verticalLayout_164.setObjectName(u"verticalLayout_164")
        self.label_212 = QLabel(self.widget_89)
        self.label_212.setObjectName(u"label_212")

        self.verticalLayout_164.addWidget(self.label_212)

        self.label_213 = QLabel(self.widget_89)
        self.label_213.setObjectName(u"label_213")
        self.label_213.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_164.addWidget(self.label_213)


        self.gridLayout_46.addLayout(self.verticalLayout_164, 1, 0, 1, 1)

        self.TuanBen_next_execute_time = QLineEdit(self.widget_89)
        self.TuanBen_next_execute_time.setObjectName(u"TuanBen_next_execute_time")
        self.TuanBen_next_execute_time.setMinimumSize(QSize(200, 0))
        self.TuanBen_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.TuanBen_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_46.addWidget(self.TuanBen_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_46.setColumnStretch(0, 5)
        self.gridLayout_46.setColumnStretch(1, 2)

        self.verticalLayout_162.addLayout(self.gridLayout_46)


        self.verticalLayout_161.addWidget(self.widget_89)

        self.verticalSpacer_29 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_161.addItem(self.verticalSpacer_29)

        self.scrollArea_37.setWidget(self.scrollAreaWidgetContents_34)

        self.horizontalLayout_55.addWidget(self.scrollArea_37)

        self.horizontalSpacer_68 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_55.addItem(self.horizontalSpacer_68)

        self.horizontalLayout_55.setStretch(0, 1)
        self.horizontalLayout_55.setStretch(1, 5)
        self.horizontalLayout_55.setStretch(2, 1)

        self.horizontalLayout_67.addWidget(self.widget_88)

        self.stackedWidget.addWidget(self.TuanBen_widget)
        self.BenFuYaoSaiZhan_widget = QWidget()
        self.BenFuYaoSaiZhan_widget.setObjectName(u"BenFuYaoSaiZhan_widget")
        self.horizontalLayout_76 = QHBoxLayout(self.BenFuYaoSaiZhan_widget)
        self.horizontalLayout_76.setObjectName(u"horizontalLayout_76")
        self.widget_101 = QWidget(self.BenFuYaoSaiZhan_widget)
        self.widget_101.setObjectName(u"widget_101")
        self.widget_101.setStyleSheet(u"")
        self.horizontalLayout_72 = QHBoxLayout(self.widget_101)
        self.horizontalLayout_72.setObjectName(u"horizontalLayout_72")
        self.horizontalSpacer_77 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_72.addItem(self.horizontalSpacer_77)

        self.scrollArea_42 = QScrollArea(self.widget_101)
        self.scrollArea_42.setObjectName(u"scrollArea_42")
        self.scrollArea_42.setMinimumSize(QSize(600, 0))
        self.scrollArea_42.setWidgetResizable(True)
        self.scrollArea_42.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_39 = QWidget()
        self.scrollAreaWidgetContents_39.setObjectName(u"scrollAreaWidgetContents_39")
        self.scrollAreaWidgetContents_39.setGeometry(QRect(0, 0, 566, 260))
        self.verticalLayout_187 = QVBoxLayout(self.scrollAreaWidgetContents_39)
        self.verticalLayout_187.setSpacing(20)
        self.verticalLayout_187.setObjectName(u"verticalLayout_187")
        self.widget_102 = QWidget(self.scrollAreaWidgetContents_39)
        self.widget_102.setObjectName(u"widget_102")
        self.widget_102.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_188 = QVBoxLayout(self.widget_102)
        self.verticalLayout_188.setObjectName(u"verticalLayout_188")
        self.verticalLayout_188.setContentsMargins(-1, 7, -1, -1)
        self.label_241 = QLabel(self.widget_102)
        self.label_241.setObjectName(u"label_241")
        self.label_241.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_188.addWidget(self.label_241)

        self.label_242 = QLabel(self.widget_102)
        self.label_242.setObjectName(u"label_242")
        self.label_242.setStyleSheet(u"font-size:13pt;\n"
"color:rgba(255, 0, 0, 100);\n"
"margin-left:18px;")

        self.verticalLayout_188.addWidget(self.label_242)

        self.frame_48 = QFrame(self.widget_102)
        self.frame_48.setObjectName(u"frame_48")
        self.frame_48.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_48.setFrameShape(QFrame.Shape.HLine)
        self.frame_48.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_188.addWidget(self.frame_48)

        self.gridLayout_52 = QGridLayout()
        self.gridLayout_52.setObjectName(u"gridLayout_52")
        self.gridLayout_52.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_189 = QVBoxLayout()
        self.verticalLayout_189.setObjectName(u"verticalLayout_189")
        self.label_243 = QLabel(self.widget_102)
        self.label_243.setObjectName(u"label_243")

        self.verticalLayout_189.addWidget(self.label_243)

        self.label_244 = QLabel(self.widget_102)
        self.label_244.setObjectName(u"label_244")
        self.label_244.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_189.addWidget(self.label_244)


        self.gridLayout_52.addLayout(self.verticalLayout_189, 0, 0, 1, 1)

        self.BenFuYaoSaiZhan_Enable = QCheckBox(self.widget_102)
        self.BenFuYaoSaiZhan_Enable.setObjectName(u"BenFuYaoSaiZhan_Enable")
        self.BenFuYaoSaiZhan_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.BenFuYaoSaiZhan_Enable.setStyleSheet(u"")

        self.gridLayout_52.addWidget(self.BenFuYaoSaiZhan_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_190 = QVBoxLayout()
        self.verticalLayout_190.setObjectName(u"verticalLayout_190")
        self.label_245 = QLabel(self.widget_102)
        self.label_245.setObjectName(u"label_245")

        self.verticalLayout_190.addWidget(self.label_245)

        self.label_246 = QLabel(self.widget_102)
        self.label_246.setObjectName(u"label_246")
        self.label_246.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_190.addWidget(self.label_246)


        self.gridLayout_52.addLayout(self.verticalLayout_190, 1, 0, 1, 1)

        self.BenFuYaoSaiZhan_next_execute_time = QLineEdit(self.widget_102)
        self.BenFuYaoSaiZhan_next_execute_time.setObjectName(u"BenFuYaoSaiZhan_next_execute_time")
        self.BenFuYaoSaiZhan_next_execute_time.setMinimumSize(QSize(200, 0))
        self.BenFuYaoSaiZhan_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.BenFuYaoSaiZhan_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_52.addWidget(self.BenFuYaoSaiZhan_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_52.setColumnStretch(0, 5)
        self.gridLayout_52.setColumnStretch(1, 2)

        self.verticalLayout_188.addLayout(self.gridLayout_52)


        self.verticalLayout_187.addWidget(self.widget_102)

        self.verticalSpacer_35 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_187.addItem(self.verticalSpacer_35)

        self.scrollArea_42.setWidget(self.scrollAreaWidgetContents_39)

        self.horizontalLayout_72.addWidget(self.scrollArea_42)

        self.horizontalSpacer_78 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_72.addItem(self.horizontalSpacer_78)

        self.horizontalLayout_72.setStretch(0, 1)
        self.horizontalLayout_72.setStretch(1, 5)
        self.horizontalLayout_72.setStretch(2, 1)

        self.horizontalLayout_76.addWidget(self.widget_101)

        self.stackedWidget.addWidget(self.BenFuYaoSaiZhan_widget)
        self.PanRenLaiXi_widget = QWidget()
        self.PanRenLaiXi_widget.setObjectName(u"PanRenLaiXi_widget")
        self.horizontalLayout_66 = QHBoxLayout(self.PanRenLaiXi_widget)
        self.horizontalLayout_66.setObjectName(u"horizontalLayout_66")
        self.widget_86 = QWidget(self.PanRenLaiXi_widget)
        self.widget_86.setObjectName(u"widget_86")
        self.widget_86.setStyleSheet(u"")
        self.horizontalLayout_57 = QHBoxLayout(self.widget_86)
        self.horizontalLayout_57.setObjectName(u"horizontalLayout_57")
        self.horizontalSpacer_65 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_57.addItem(self.horizontalSpacer_65)

        self.scrollArea_36 = QScrollArea(self.widget_86)
        self.scrollArea_36.setObjectName(u"scrollArea_36")
        self.scrollArea_36.setMinimumSize(QSize(600, 0))
        self.scrollArea_36.setWidgetResizable(True)
        self.scrollArea_36.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_33 = QWidget()
        self.scrollAreaWidgetContents_33.setObjectName(u"scrollAreaWidgetContents_33")
        self.scrollAreaWidgetContents_33.setGeometry(QRect(0, 0, 566, 260))
        self.verticalLayout_157 = QVBoxLayout(self.scrollAreaWidgetContents_33)
        self.verticalLayout_157.setSpacing(20)
        self.verticalLayout_157.setObjectName(u"verticalLayout_157")
        self.widget_87 = QWidget(self.scrollAreaWidgetContents_33)
        self.widget_87.setObjectName(u"widget_87")
        self.widget_87.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_158 = QVBoxLayout(self.widget_87)
        self.verticalLayout_158.setObjectName(u"verticalLayout_158")
        self.verticalLayout_158.setContentsMargins(-1, 7, -1, -1)
        self.label_202 = QLabel(self.widget_87)
        self.label_202.setObjectName(u"label_202")
        self.label_202.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_158.addWidget(self.label_202)

        self.label_203 = QLabel(self.widget_87)
        self.label_203.setObjectName(u"label_203")
        self.label_203.setStyleSheet(u"font-size:13pt;\n"
"color:rgba(255, 0, 0, 100);\n"
"margin-left:18px;")

        self.verticalLayout_158.addWidget(self.label_203)

        self.frame_40 = QFrame(self.widget_87)
        self.frame_40.setObjectName(u"frame_40")
        self.frame_40.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_40.setFrameShape(QFrame.Shape.HLine)
        self.frame_40.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_158.addWidget(self.frame_40)

        self.gridLayout_45 = QGridLayout()
        self.gridLayout_45.setObjectName(u"gridLayout_45")
        self.gridLayout_45.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_159 = QVBoxLayout()
        self.verticalLayout_159.setObjectName(u"verticalLayout_159")
        self.label_204 = QLabel(self.widget_87)
        self.label_204.setObjectName(u"label_204")

        self.verticalLayout_159.addWidget(self.label_204)

        self.label_205 = QLabel(self.widget_87)
        self.label_205.setObjectName(u"label_205")
        self.label_205.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_159.addWidget(self.label_205)


        self.gridLayout_45.addLayout(self.verticalLayout_159, 0, 0, 1, 1)

        self.PanRenLaiXi_Enable = QCheckBox(self.widget_87)
        self.PanRenLaiXi_Enable.setObjectName(u"PanRenLaiXi_Enable")
        self.PanRenLaiXi_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.PanRenLaiXi_Enable.setStyleSheet(u"")

        self.gridLayout_45.addWidget(self.PanRenLaiXi_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_160 = QVBoxLayout()
        self.verticalLayout_160.setObjectName(u"verticalLayout_160")
        self.label_206 = QLabel(self.widget_87)
        self.label_206.setObjectName(u"label_206")

        self.verticalLayout_160.addWidget(self.label_206)

        self.label_207 = QLabel(self.widget_87)
        self.label_207.setObjectName(u"label_207")
        self.label_207.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_160.addWidget(self.label_207)


        self.gridLayout_45.addLayout(self.verticalLayout_160, 1, 0, 1, 1)

        self.PanRenLaiXi_next_execute_time = QLineEdit(self.widget_87)
        self.PanRenLaiXi_next_execute_time.setObjectName(u"PanRenLaiXi_next_execute_time")
        self.PanRenLaiXi_next_execute_time.setMinimumSize(QSize(200, 0))
        self.PanRenLaiXi_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.PanRenLaiXi_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_45.addWidget(self.PanRenLaiXi_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_45.setColumnStretch(0, 5)
        self.gridLayout_45.setColumnStretch(1, 2)

        self.verticalLayout_158.addLayout(self.gridLayout_45)


        self.verticalLayout_157.addWidget(self.widget_87)

        self.verticalSpacer_28 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_157.addItem(self.verticalSpacer_28)

        self.scrollArea_36.setWidget(self.scrollAreaWidgetContents_33)

        self.horizontalLayout_57.addWidget(self.scrollArea_36)

        self.horizontalSpacer_66 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_57.addItem(self.horizontalSpacer_66)

        self.horizontalLayout_57.setStretch(0, 1)
        self.horizontalLayout_57.setStretch(1, 5)
        self.horizontalLayout_57.setStretch(2, 1)

        self.horizontalLayout_66.addWidget(self.widget_86)

        self.stackedWidget.addWidget(self.PanRenLaiXi_widget)
        self.TianDiZhanChang_widget = QWidget()
        self.TianDiZhanChang_widget.setObjectName(u"TianDiZhanChang_widget")
        self.horizontalLayout_77 = QHBoxLayout(self.TianDiZhanChang_widget)
        self.horizontalLayout_77.setObjectName(u"horizontalLayout_77")
        self.widget_103 = QWidget(self.TianDiZhanChang_widget)
        self.widget_103.setObjectName(u"widget_103")
        self.widget_103.setStyleSheet(u"")
        self.horizontalLayout_73 = QHBoxLayout(self.widget_103)
        self.horizontalLayout_73.setObjectName(u"horizontalLayout_73")
        self.horizontalSpacer_79 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_73.addItem(self.horizontalSpacer_79)

        self.scrollArea_43 = QScrollArea(self.widget_103)
        self.scrollArea_43.setObjectName(u"scrollArea_43")
        self.scrollArea_43.setMinimumSize(QSize(600, 0))
        self.scrollArea_43.setWidgetResizable(True)
        self.scrollArea_43.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_40 = QWidget()
        self.scrollAreaWidgetContents_40.setObjectName(u"scrollAreaWidgetContents_40")
        self.scrollAreaWidgetContents_40.setGeometry(QRect(0, 0, 566, 260))
        self.verticalLayout_191 = QVBoxLayout(self.scrollAreaWidgetContents_40)
        self.verticalLayout_191.setSpacing(20)
        self.verticalLayout_191.setObjectName(u"verticalLayout_191")
        self.widget_104 = QWidget(self.scrollAreaWidgetContents_40)
        self.widget_104.setObjectName(u"widget_104")
        self.widget_104.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_192 = QVBoxLayout(self.widget_104)
        self.verticalLayout_192.setObjectName(u"verticalLayout_192")
        self.verticalLayout_192.setContentsMargins(-1, 7, -1, -1)
        self.label_247 = QLabel(self.widget_104)
        self.label_247.setObjectName(u"label_247")
        self.label_247.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_192.addWidget(self.label_247)

        self.label_248 = QLabel(self.widget_104)
        self.label_248.setObjectName(u"label_248")
        self.label_248.setStyleSheet(u"font-size:13pt;\n"
"color:rgba(255, 0, 0, 100);\n"
"margin-left:18px;")

        self.verticalLayout_192.addWidget(self.label_248)

        self.frame_49 = QFrame(self.widget_104)
        self.frame_49.setObjectName(u"frame_49")
        self.frame_49.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_49.setFrameShape(QFrame.Shape.HLine)
        self.frame_49.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_192.addWidget(self.frame_49)

        self.gridLayout_53 = QGridLayout()
        self.gridLayout_53.setObjectName(u"gridLayout_53")
        self.gridLayout_53.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_193 = QVBoxLayout()
        self.verticalLayout_193.setObjectName(u"verticalLayout_193")
        self.label_249 = QLabel(self.widget_104)
        self.label_249.setObjectName(u"label_249")

        self.verticalLayout_193.addWidget(self.label_249)

        self.label_250 = QLabel(self.widget_104)
        self.label_250.setObjectName(u"label_250")
        self.label_250.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_193.addWidget(self.label_250)


        self.gridLayout_53.addLayout(self.verticalLayout_193, 0, 0, 1, 1)

        self.TianDiZhanChang_Enable = QCheckBox(self.widget_104)
        self.TianDiZhanChang_Enable.setObjectName(u"TianDiZhanChang_Enable")
        self.TianDiZhanChang_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.TianDiZhanChang_Enable.setStyleSheet(u"")

        self.gridLayout_53.addWidget(self.TianDiZhanChang_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_194 = QVBoxLayout()
        self.verticalLayout_194.setObjectName(u"verticalLayout_194")
        self.label_251 = QLabel(self.widget_104)
        self.label_251.setObjectName(u"label_251")

        self.verticalLayout_194.addWidget(self.label_251)

        self.label_252 = QLabel(self.widget_104)
        self.label_252.setObjectName(u"label_252")
        self.label_252.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_194.addWidget(self.label_252)


        self.gridLayout_53.addLayout(self.verticalLayout_194, 1, 0, 1, 1)

        self.TianDiZhanChang_next_execute_time = QLineEdit(self.widget_104)
        self.TianDiZhanChang_next_execute_time.setObjectName(u"TianDiZhanChang_next_execute_time")
        self.TianDiZhanChang_next_execute_time.setMinimumSize(QSize(200, 0))
        self.TianDiZhanChang_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.TianDiZhanChang_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_53.addWidget(self.TianDiZhanChang_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_53.setColumnStretch(0, 5)
        self.gridLayout_53.setColumnStretch(1, 2)

        self.verticalLayout_192.addLayout(self.gridLayout_53)


        self.verticalLayout_191.addWidget(self.widget_104)

        self.verticalSpacer_36 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_191.addItem(self.verticalSpacer_36)

        self.scrollArea_43.setWidget(self.scrollAreaWidgetContents_40)

        self.horizontalLayout_73.addWidget(self.scrollArea_43)

        self.horizontalSpacer_80 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_73.addItem(self.horizontalSpacer_80)

        self.horizontalLayout_73.setStretch(0, 1)
        self.horizontalLayout_73.setStretch(1, 5)
        self.horizontalLayout_73.setStretch(2, 1)

        self.horizontalLayout_77.addWidget(self.widget_103)

        self.stackedWidget.addWidget(self.TianDiZhanChang_widget)
        self.ZhuiJiXiaoZuZhi_widget = QWidget()
        self.ZhuiJiXiaoZuZhi_widget.setObjectName(u"ZhuiJiXiaoZuZhi_widget")
        self.horizontalLayout_78 = QHBoxLayout(self.ZhuiJiXiaoZuZhi_widget)
        self.horizontalLayout_78.setObjectName(u"horizontalLayout_78")
        self.widget_105 = QWidget(self.ZhuiJiXiaoZuZhi_widget)
        self.widget_105.setObjectName(u"widget_105")
        self.widget_105.setStyleSheet(u"")
        self.horizontalLayout_74 = QHBoxLayout(self.widget_105)
        self.horizontalLayout_74.setObjectName(u"horizontalLayout_74")
        self.horizontalSpacer_81 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_74.addItem(self.horizontalSpacer_81)

        self.scrollArea_44 = QScrollArea(self.widget_105)
        self.scrollArea_44.setObjectName(u"scrollArea_44")
        self.scrollArea_44.setMinimumSize(QSize(600, 0))
        self.scrollArea_44.setWidgetResizable(True)
        self.scrollArea_44.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_41 = QWidget()
        self.scrollAreaWidgetContents_41.setObjectName(u"scrollAreaWidgetContents_41")
        self.scrollAreaWidgetContents_41.setGeometry(QRect(0, 0, 566, 260))
        self.verticalLayout_195 = QVBoxLayout(self.scrollAreaWidgetContents_41)
        self.verticalLayout_195.setSpacing(20)
        self.verticalLayout_195.setObjectName(u"verticalLayout_195")
        self.widget_106 = QWidget(self.scrollAreaWidgetContents_41)
        self.widget_106.setObjectName(u"widget_106")
        self.widget_106.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_196 = QVBoxLayout(self.widget_106)
        self.verticalLayout_196.setObjectName(u"verticalLayout_196")
        self.verticalLayout_196.setContentsMargins(-1, 7, -1, -1)
        self.label_253 = QLabel(self.widget_106)
        self.label_253.setObjectName(u"label_253")
        self.label_253.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_196.addWidget(self.label_253)

        self.label_254 = QLabel(self.widget_106)
        self.label_254.setObjectName(u"label_254")
        self.label_254.setStyleSheet(u"font-size:13pt;\n"
"color:rgba(255, 0, 0, 100);\n"
"margin-left:18px;")

        self.verticalLayout_196.addWidget(self.label_254)

        self.frame_50 = QFrame(self.widget_106)
        self.frame_50.setObjectName(u"frame_50")
        self.frame_50.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_50.setFrameShape(QFrame.Shape.HLine)
        self.frame_50.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_196.addWidget(self.frame_50)

        self.gridLayout_54 = QGridLayout()
        self.gridLayout_54.setObjectName(u"gridLayout_54")
        self.gridLayout_54.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_197 = QVBoxLayout()
        self.verticalLayout_197.setObjectName(u"verticalLayout_197")
        self.label_255 = QLabel(self.widget_106)
        self.label_255.setObjectName(u"label_255")

        self.verticalLayout_197.addWidget(self.label_255)

        self.label_256 = QLabel(self.widget_106)
        self.label_256.setObjectName(u"label_256")
        self.label_256.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_197.addWidget(self.label_256)


        self.gridLayout_54.addLayout(self.verticalLayout_197, 0, 0, 1, 1)

        self.ZhuiJiXiaoZuZhi_Enable = QCheckBox(self.widget_106)
        self.ZhuiJiXiaoZuZhi_Enable.setObjectName(u"ZhuiJiXiaoZuZhi_Enable")
        self.ZhuiJiXiaoZuZhi_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.ZhuiJiXiaoZuZhi_Enable.setStyleSheet(u"")

        self.gridLayout_54.addWidget(self.ZhuiJiXiaoZuZhi_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_198 = QVBoxLayout()
        self.verticalLayout_198.setObjectName(u"verticalLayout_198")
        self.label_257 = QLabel(self.widget_106)
        self.label_257.setObjectName(u"label_257")

        self.verticalLayout_198.addWidget(self.label_257)

        self.label_258 = QLabel(self.widget_106)
        self.label_258.setObjectName(u"label_258")
        self.label_258.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_198.addWidget(self.label_258)


        self.gridLayout_54.addLayout(self.verticalLayout_198, 1, 0, 1, 1)

        self.ZhuiJiXiaoZuZhi_next_execute_time = QLineEdit(self.widget_106)
        self.ZhuiJiXiaoZuZhi_next_execute_time.setObjectName(u"ZhuiJiXiaoZuZhi_next_execute_time")
        self.ZhuiJiXiaoZuZhi_next_execute_time.setMinimumSize(QSize(200, 0))
        self.ZhuiJiXiaoZuZhi_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.ZhuiJiXiaoZuZhi_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_54.addWidget(self.ZhuiJiXiaoZuZhi_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_54.setColumnStretch(0, 5)
        self.gridLayout_54.setColumnStretch(1, 2)

        self.verticalLayout_196.addLayout(self.gridLayout_54)


        self.verticalLayout_195.addWidget(self.widget_106)

        self.verticalSpacer_37 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_195.addItem(self.verticalSpacer_37)

        self.scrollArea_44.setWidget(self.scrollAreaWidgetContents_41)

        self.horizontalLayout_74.addWidget(self.scrollArea_44)

        self.horizontalSpacer_82 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_74.addItem(self.horizontalSpacer_82)

        self.horizontalLayout_74.setStretch(0, 1)
        self.horizontalLayout_74.setStretch(1, 5)
        self.horizontalLayout_74.setStretch(2, 1)

        self.horizontalLayout_78.addWidget(self.widget_105)

        self.stackedWidget.addWidget(self.ZhuiJiXiaoZuZhi_widget)
        self.KuaFuYaoSaiZhan_widget = QWidget()
        self.KuaFuYaoSaiZhan_widget.setObjectName(u"KuaFuYaoSaiZhan_widget")
        self.horizontalLayout_75 = QHBoxLayout(self.KuaFuYaoSaiZhan_widget)
        self.horizontalLayout_75.setObjectName(u"horizontalLayout_75")
        self.widget_99 = QWidget(self.KuaFuYaoSaiZhan_widget)
        self.widget_99.setObjectName(u"widget_99")
        self.widget_99.setStyleSheet(u"")
        self.horizontalLayout_71 = QHBoxLayout(self.widget_99)
        self.horizontalLayout_71.setObjectName(u"horizontalLayout_71")
        self.horizontalSpacer_75 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_71.addItem(self.horizontalSpacer_75)

        self.scrollArea_41 = QScrollArea(self.widget_99)
        self.scrollArea_41.setObjectName(u"scrollArea_41")
        self.scrollArea_41.setMinimumSize(QSize(600, 0))
        self.scrollArea_41.setWidgetResizable(True)
        self.scrollArea_41.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_38 = QWidget()
        self.scrollAreaWidgetContents_38.setObjectName(u"scrollAreaWidgetContents_38")
        self.scrollAreaWidgetContents_38.setGeometry(QRect(0, 0, 566, 260))
        self.verticalLayout_183 = QVBoxLayout(self.scrollAreaWidgetContents_38)
        self.verticalLayout_183.setSpacing(20)
        self.verticalLayout_183.setObjectName(u"verticalLayout_183")
        self.widget_100 = QWidget(self.scrollAreaWidgetContents_38)
        self.widget_100.setObjectName(u"widget_100")
        self.widget_100.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_184 = QVBoxLayout(self.widget_100)
        self.verticalLayout_184.setObjectName(u"verticalLayout_184")
        self.verticalLayout_184.setContentsMargins(-1, 7, -1, -1)
        self.label_236 = QLabel(self.widget_100)
        self.label_236.setObjectName(u"label_236")
        self.label_236.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_184.addWidget(self.label_236)

        self.label_113 = QLabel(self.widget_100)
        self.label_113.setObjectName(u"label_113")
        self.label_113.setStyleSheet(u"font-size:13pt;\n"
"color:rgba(255, 0, 0, 100);\n"
"margin-left:18px;")

        self.verticalLayout_184.addWidget(self.label_113)

        self.frame_47 = QFrame(self.widget_100)
        self.frame_47.setObjectName(u"frame_47")
        self.frame_47.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_47.setFrameShape(QFrame.Shape.HLine)
        self.frame_47.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_184.addWidget(self.frame_47)

        self.gridLayout_51 = QGridLayout()
        self.gridLayout_51.setObjectName(u"gridLayout_51")
        self.gridLayout_51.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_185 = QVBoxLayout()
        self.verticalLayout_185.setObjectName(u"verticalLayout_185")
        self.label_237 = QLabel(self.widget_100)
        self.label_237.setObjectName(u"label_237")

        self.verticalLayout_185.addWidget(self.label_237)

        self.label_238 = QLabel(self.widget_100)
        self.label_238.setObjectName(u"label_238")
        self.label_238.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_185.addWidget(self.label_238)


        self.gridLayout_51.addLayout(self.verticalLayout_185, 0, 0, 1, 1)

        self.KuaFuYaoSaiZhan_Enable = QCheckBox(self.widget_100)
        self.KuaFuYaoSaiZhan_Enable.setObjectName(u"KuaFuYaoSaiZhan_Enable")
        self.KuaFuYaoSaiZhan_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.KuaFuYaoSaiZhan_Enable.setStyleSheet(u"")

        self.gridLayout_51.addWidget(self.KuaFuYaoSaiZhan_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_186 = QVBoxLayout()
        self.verticalLayout_186.setObjectName(u"verticalLayout_186")
        self.label_239 = QLabel(self.widget_100)
        self.label_239.setObjectName(u"label_239")

        self.verticalLayout_186.addWidget(self.label_239)

        self.label_240 = QLabel(self.widget_100)
        self.label_240.setObjectName(u"label_240")
        self.label_240.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_186.addWidget(self.label_240)


        self.gridLayout_51.addLayout(self.verticalLayout_186, 1, 0, 1, 1)

        self.KuaFuYaoSaiZhan_next_execute_time = QLineEdit(self.widget_100)
        self.KuaFuYaoSaiZhan_next_execute_time.setObjectName(u"KuaFuYaoSaiZhan_next_execute_time")
        self.KuaFuYaoSaiZhan_next_execute_time.setMinimumSize(QSize(200, 0))
        self.KuaFuYaoSaiZhan_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.KuaFuYaoSaiZhan_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_51.addWidget(self.KuaFuYaoSaiZhan_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_51.setColumnStretch(0, 5)
        self.gridLayout_51.setColumnStretch(1, 2)

        self.verticalLayout_184.addLayout(self.gridLayout_51)


        self.verticalLayout_183.addWidget(self.widget_100)

        self.verticalSpacer_34 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_183.addItem(self.verticalSpacer_34)

        self.scrollArea_41.setWidget(self.scrollAreaWidgetContents_38)

        self.horizontalLayout_71.addWidget(self.scrollArea_41)

        self.horizontalSpacer_76 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_71.addItem(self.horizontalSpacer_76)

        self.horizontalLayout_71.setStretch(0, 1)
        self.horizontalLayout_71.setStretch(1, 5)
        self.horizontalLayout_71.setStretch(2, 1)

        self.horizontalLayout_75.addWidget(self.widget_99)

        self.stackedWidget.addWidget(self.KuaFuYaoSaiZhan_widget)
        self.DianFengDuiJue_widget = QWidget()
        self.DianFengDuiJue_widget.setObjectName(u"DianFengDuiJue_widget")
        self.horizontalLayout_11 = QHBoxLayout(self.DianFengDuiJue_widget)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.widget_97 = QWidget(self.DianFengDuiJue_widget)
        self.widget_97.setObjectName(u"widget_97")
        self.widget_97.setStyleSheet(u"")
        self.horizontalLayout_70 = QHBoxLayout(self.widget_97)
        self.horizontalLayout_70.setObjectName(u"horizontalLayout_70")
        self.horizontalSpacer_73 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_70.addItem(self.horizontalSpacer_73)

        self.scrollArea_40 = QScrollArea(self.widget_97)
        self.scrollArea_40.setObjectName(u"scrollArea_40")
        self.scrollArea_40.setMinimumSize(QSize(600, 0))
        self.scrollArea_40.setWidgetResizable(True)
        self.scrollArea_40.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_37 = QWidget()
        self.scrollAreaWidgetContents_37.setObjectName(u"scrollAreaWidgetContents_37")
        self.scrollAreaWidgetContents_37.setGeometry(QRect(0, 0, 566, 260))
        self.verticalLayout_179 = QVBoxLayout(self.scrollAreaWidgetContents_37)
        self.verticalLayout_179.setSpacing(20)
        self.verticalLayout_179.setObjectName(u"verticalLayout_179")
        self.widget_98 = QWidget(self.scrollAreaWidgetContents_37)
        self.widget_98.setObjectName(u"widget_98")
        self.widget_98.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_180 = QVBoxLayout(self.widget_98)
        self.verticalLayout_180.setObjectName(u"verticalLayout_180")
        self.verticalLayout_180.setContentsMargins(-1, 7, -1, -1)
        self.label_223 = QLabel(self.widget_98)
        self.label_223.setObjectName(u"label_223")
        self.label_223.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_180.addWidget(self.label_223)

        self.label_112 = QLabel(self.widget_98)
        self.label_112.setObjectName(u"label_112")
        self.label_112.setStyleSheet(u"font-size:13pt;\n"
"color:rgba(255, 0, 0, 100);\n"
"margin-left:18px;")

        self.verticalLayout_180.addWidget(self.label_112)

        self.frame_46 = QFrame(self.widget_98)
        self.frame_46.setObjectName(u"frame_46")
        self.frame_46.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_46.setFrameShape(QFrame.Shape.HLine)
        self.frame_46.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_180.addWidget(self.frame_46)

        self.gridLayout_50 = QGridLayout()
        self.gridLayout_50.setObjectName(u"gridLayout_50")
        self.gridLayout_50.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_181 = QVBoxLayout()
        self.verticalLayout_181.setObjectName(u"verticalLayout_181")
        self.label_224 = QLabel(self.widget_98)
        self.label_224.setObjectName(u"label_224")

        self.verticalLayout_181.addWidget(self.label_224)

        self.label_225 = QLabel(self.widget_98)
        self.label_225.setObjectName(u"label_225")
        self.label_225.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_181.addWidget(self.label_225)


        self.gridLayout_50.addLayout(self.verticalLayout_181, 0, 0, 1, 1)

        self.DianFengDuiJue_Enable = QCheckBox(self.widget_98)
        self.DianFengDuiJue_Enable.setObjectName(u"DianFengDuiJue_Enable")
        self.DianFengDuiJue_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.DianFengDuiJue_Enable.setStyleSheet(u"")

        self.gridLayout_50.addWidget(self.DianFengDuiJue_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_182 = QVBoxLayout()
        self.verticalLayout_182.setObjectName(u"verticalLayout_182")
        self.label_232 = QLabel(self.widget_98)
        self.label_232.setObjectName(u"label_232")

        self.verticalLayout_182.addWidget(self.label_232)

        self.label_235 = QLabel(self.widget_98)
        self.label_235.setObjectName(u"label_235")
        self.label_235.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_182.addWidget(self.label_235)


        self.gridLayout_50.addLayout(self.verticalLayout_182, 1, 0, 1, 1)

        self.DianFengDuiJue_next_execute_time = QLineEdit(self.widget_98)
        self.DianFengDuiJue_next_execute_time.setObjectName(u"DianFengDuiJue_next_execute_time")
        self.DianFengDuiJue_next_execute_time.setMinimumSize(QSize(200, 0))
        self.DianFengDuiJue_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.DianFengDuiJue_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_50.addWidget(self.DianFengDuiJue_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_50.setColumnStretch(0, 5)
        self.gridLayout_50.setColumnStretch(1, 2)

        self.verticalLayout_180.addLayout(self.gridLayout_50)


        self.verticalLayout_179.addWidget(self.widget_98)

        self.verticalSpacer_33 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_179.addItem(self.verticalSpacer_33)

        self.scrollArea_40.setWidget(self.scrollAreaWidgetContents_37)

        self.horizontalLayout_70.addWidget(self.scrollArea_40)

        self.horizontalSpacer_74 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_70.addItem(self.horizontalSpacer_74)

        self.horizontalLayout_70.setStretch(0, 1)
        self.horizontalLayout_70.setStretch(1, 5)
        self.horizontalLayout_70.setStretch(2, 1)

        self.horizontalLayout_11.addWidget(self.widget_97)

        self.stackedWidget.addWidget(self.DianFengDuiJue_widget)
        self.ZuZhiZhengBa_widget = QWidget()
        self.ZuZhiZhengBa_widget.setObjectName(u"ZuZhiZhengBa_widget")
        self.horizontalLayout_46 = QHBoxLayout(self.ZuZhiZhengBa_widget)
        self.horizontalLayout_46.setObjectName(u"horizontalLayout_46")
        self.widget_64 = QWidget(self.ZuZhiZhengBa_widget)
        self.widget_64.setObjectName(u"widget_64")
        self.widget_64.setStyleSheet(u"")
        self.horizontalLayout_43 = QHBoxLayout(self.widget_64)
        self.horizontalLayout_43.setObjectName(u"horizontalLayout_43")
        self.horizontalSpacer_43 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_43.addItem(self.horizontalSpacer_43)

        self.scrollArea_25 = QScrollArea(self.widget_64)
        self.scrollArea_25.setObjectName(u"scrollArea_25")
        self.scrollArea_25.setMinimumSize(QSize(600, 0))
        self.scrollArea_25.setWidgetResizable(True)
        self.scrollArea_25.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_22 = QWidget()
        self.scrollAreaWidgetContents_22.setObjectName(u"scrollAreaWidgetContents_22")
        self.scrollAreaWidgetContents_22.setGeometry(QRect(0, 0, 566, 260))
        self.verticalLayout_113 = QVBoxLayout(self.scrollAreaWidgetContents_22)
        self.verticalLayout_113.setSpacing(20)
        self.verticalLayout_113.setObjectName(u"verticalLayout_113")
        self.widget_65 = QWidget(self.scrollAreaWidgetContents_22)
        self.widget_65.setObjectName(u"widget_65")
        self.widget_65.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_114 = QVBoxLayout(self.widget_65)
        self.verticalLayout_114.setObjectName(u"verticalLayout_114")
        self.verticalLayout_114.setContentsMargins(-1, 7, -1, -1)
        self.label_103 = QLabel(self.widget_65)
        self.label_103.setObjectName(u"label_103")
        self.label_103.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_114.addWidget(self.label_103)

        self.label_39 = QLabel(self.widget_65)
        self.label_39.setObjectName(u"label_39")
        self.label_39.setStyleSheet(u"font-size:13pt;\n"
"color:rgba(255, 0, 0, 100);\n"
"margin-left:18px;")

        self.verticalLayout_114.addWidget(self.label_39)

        self.frame_29 = QFrame(self.widget_65)
        self.frame_29.setObjectName(u"frame_29")
        self.frame_29.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_29.setFrameShape(QFrame.Shape.HLine)
        self.frame_29.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_114.addWidget(self.frame_29)

        self.gridLayout_34 = QGridLayout()
        self.gridLayout_34.setObjectName(u"gridLayout_34")
        self.gridLayout_34.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_116 = QVBoxLayout()
        self.verticalLayout_116.setObjectName(u"verticalLayout_116")
        self.label_152 = QLabel(self.widget_65)
        self.label_152.setObjectName(u"label_152")

        self.verticalLayout_116.addWidget(self.label_152)

        self.label_153 = QLabel(self.widget_65)
        self.label_153.setObjectName(u"label_153")
        self.label_153.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_116.addWidget(self.label_153)


        self.gridLayout_34.addLayout(self.verticalLayout_116, 1, 0, 1, 1)

        self.verticalLayout_115 = QVBoxLayout()
        self.verticalLayout_115.setObjectName(u"verticalLayout_115")
        self.label_116 = QLabel(self.widget_65)
        self.label_116.setObjectName(u"label_116")

        self.verticalLayout_115.addWidget(self.label_116)

        self.label_117 = QLabel(self.widget_65)
        self.label_117.setObjectName(u"label_117")
        self.label_117.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_115.addWidget(self.label_117)


        self.gridLayout_34.addLayout(self.verticalLayout_115, 0, 0, 1, 1)

        self.ZuZhiZhengBa_Enable = QCheckBox(self.widget_65)
        self.ZuZhiZhengBa_Enable.setObjectName(u"ZuZhiZhengBa_Enable")
        self.ZuZhiZhengBa_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.ZuZhiZhengBa_Enable.setStyleSheet(u"")

        self.gridLayout_34.addWidget(self.ZuZhiZhengBa_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.ZuZhiZhengBa_next_execute_time = QLineEdit(self.widget_65)
        self.ZuZhiZhengBa_next_execute_time.setObjectName(u"ZuZhiZhengBa_next_execute_time")
        self.ZuZhiZhengBa_next_execute_time.setMinimumSize(QSize(200, 0))
        self.ZuZhiZhengBa_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.ZuZhiZhengBa_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_34.addWidget(self.ZuZhiZhengBa_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_34.setColumnStretch(0, 5)
        self.gridLayout_34.setColumnStretch(1, 2)

        self.verticalLayout_114.addLayout(self.gridLayout_34)


        self.verticalLayout_113.addWidget(self.widget_65)

        self.verticalSpacer_17 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_113.addItem(self.verticalSpacer_17)

        self.scrollArea_25.setWidget(self.scrollAreaWidgetContents_22)

        self.horizontalLayout_43.addWidget(self.scrollArea_25)

        self.horizontalSpacer_44 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_43.addItem(self.horizontalSpacer_44)

        self.horizontalLayout_43.setStretch(0, 1)
        self.horizontalLayout_43.setStretch(1, 5)
        self.horizontalLayout_43.setStretch(2, 1)

        self.horizontalLayout_46.addWidget(self.widget_64)

        self.stackedWidget.addWidget(self.ZuZhiZhengBa_widget)
        self.SaiJiShengChang_widget = QWidget()
        self.SaiJiShengChang_widget.setObjectName(u"SaiJiShengChang_widget")
        self.horizontalLayout_21 = QHBoxLayout(self.SaiJiShengChang_widget)
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.widget_40 = QWidget(self.SaiJiShengChang_widget)
        self.widget_40.setObjectName(u"widget_40")
        self.widget_40.setStyleSheet(u"")
        self.horizontalLayout_20 = QHBoxLayout(self.widget_40)
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.horizontalSpacer_19 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_20.addItem(self.horizontalSpacer_19)

        self.scrollArea_13 = QScrollArea(self.widget_40)
        self.scrollArea_13.setObjectName(u"scrollArea_13")
        self.scrollArea_13.setMinimumSize(QSize(600, 0))
        self.scrollArea_13.setWidgetResizable(True)
        self.scrollArea_13.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_10 = QWidget()
        self.scrollAreaWidgetContents_10.setObjectName(u"scrollAreaWidgetContents_10")
        self.scrollAreaWidgetContents_10.setGeometry(QRect(0, 0, 566, 252))
        self.verticalLayout_65 = QVBoxLayout(self.scrollAreaWidgetContents_10)
        self.verticalLayout_65.setSpacing(20)
        self.verticalLayout_65.setObjectName(u"verticalLayout_65")
        self.widget_41 = QWidget(self.scrollAreaWidgetContents_10)
        self.widget_41.setObjectName(u"widget_41")
        self.widget_41.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_66 = QVBoxLayout(self.widget_41)
        self.verticalLayout_66.setObjectName(u"verticalLayout_66")
        self.verticalLayout_66.setContentsMargins(-1, 7, -1, -1)
        self.label_67 = QLabel(self.widget_41)
        self.label_67.setObjectName(u"label_67")
        self.label_67.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_66.addWidget(self.label_67)

        self.frame_17 = QFrame(self.widget_41)
        self.frame_17.setObjectName(u"frame_17")
        self.frame_17.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_17.setFrameShape(QFrame.Shape.HLine)
        self.frame_17.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_66.addWidget(self.frame_17)

        self.gridLayout_22 = QGridLayout()
        self.gridLayout_22.setObjectName(u"gridLayout_22")
        self.gridLayout_22.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_67 = QVBoxLayout()
        self.verticalLayout_67.setObjectName(u"verticalLayout_67")
        self.label_68 = QLabel(self.widget_41)
        self.label_68.setObjectName(u"label_68")

        self.verticalLayout_67.addWidget(self.label_68)

        self.label_69 = QLabel(self.widget_41)
        self.label_69.setObjectName(u"label_69")
        self.label_69.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_67.addWidget(self.label_69)


        self.gridLayout_22.addLayout(self.verticalLayout_67, 0, 0, 1, 1)

        self.SaiJiShengChang_Enable = QCheckBox(self.widget_41)
        self.SaiJiShengChang_Enable.setObjectName(u"SaiJiShengChang_Enable")
        self.SaiJiShengChang_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.SaiJiShengChang_Enable.setStyleSheet(u"")

        self.gridLayout_22.addWidget(self.SaiJiShengChang_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_68 = QVBoxLayout()
        self.verticalLayout_68.setObjectName(u"verticalLayout_68")
        self.label_128 = QLabel(self.widget_41)
        self.label_128.setObjectName(u"label_128")

        self.verticalLayout_68.addWidget(self.label_128)

        self.label_129 = QLabel(self.widget_41)
        self.label_129.setObjectName(u"label_129")
        self.label_129.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_68.addWidget(self.label_129)


        self.gridLayout_22.addLayout(self.verticalLayout_68, 1, 0, 1, 1)

        self.SaiJiShengChang_next_execute_time = QLineEdit(self.widget_41)
        self.SaiJiShengChang_next_execute_time.setObjectName(u"SaiJiShengChang_next_execute_time")
        self.SaiJiShengChang_next_execute_time.setMinimumSize(QSize(200, 0))
        self.SaiJiShengChang_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.SaiJiShengChang_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_22.addWidget(self.SaiJiShengChang_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_22.setColumnStretch(0, 5)
        self.gridLayout_22.setColumnStretch(1, 2)

        self.verticalLayout_66.addLayout(self.gridLayout_22)


        self.verticalLayout_65.addWidget(self.widget_41)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_65.addItem(self.verticalSpacer_5)

        self.scrollArea_13.setWidget(self.scrollAreaWidgetContents_10)

        self.horizontalLayout_20.addWidget(self.scrollArea_13)

        self.horizontalSpacer_20 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_20.addItem(self.horizontalSpacer_20)

        self.horizontalLayout_20.setStretch(0, 1)
        self.horizontalLayout_20.setStretch(1, 5)
        self.horizontalLayout_20.setStretch(2, 1)

        self.horizontalLayout_21.addWidget(self.widget_40)

        self.stackedWidget.addWidget(self.SaiJiShengChang_widget)
        self.ZhuangBeiHeCheng = QWidget()
        self.ZhuangBeiHeCheng.setObjectName(u"ZhuangBeiHeCheng")
        self.horizontalLayout_10 = QHBoxLayout(self.ZhuangBeiHeCheng)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.widget_92 = QWidget(self.ZhuangBeiHeCheng)
        self.widget_92.setObjectName(u"widget_92")
        self.widget_92.setStyleSheet(u"")
        self.horizontalLayout_69 = QHBoxLayout(self.widget_92)
        self.horizontalLayout_69.setObjectName(u"horizontalLayout_69")
        self.horizontalSpacer_71 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_69.addItem(self.horizontalSpacer_71)

        self.scrollArea_39 = QScrollArea(self.widget_92)
        self.scrollArea_39.setObjectName(u"scrollArea_39")
        self.scrollArea_39.setMinimumSize(QSize(600, 0))
        self.scrollArea_39.setWidgetResizable(True)
        self.scrollArea_39.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_36 = QWidget()
        self.scrollAreaWidgetContents_36.setObjectName(u"scrollAreaWidgetContents_36")
        self.scrollAreaWidgetContents_36.setGeometry(QRect(0, 0, 566, 412))
        self.verticalLayout_169 = QVBoxLayout(self.scrollAreaWidgetContents_36)
        self.verticalLayout_169.setSpacing(20)
        self.verticalLayout_169.setObjectName(u"verticalLayout_169")
        self.widget_93 = QWidget(self.scrollAreaWidgetContents_36)
        self.widget_93.setObjectName(u"widget_93")
        self.widget_93.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_170 = QVBoxLayout(self.widget_93)
        self.verticalLayout_170.setObjectName(u"verticalLayout_170")
        self.verticalLayout_170.setContentsMargins(-1, 7, -1, -1)
        self.label_104 = QLabel(self.widget_93)
        self.label_104.setObjectName(u"label_104")
        self.label_104.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_170.addWidget(self.label_104)

        self.frame_43 = QFrame(self.widget_93)
        self.frame_43.setObjectName(u"frame_43")
        self.frame_43.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_43.setFrameShape(QFrame.Shape.HLine)
        self.frame_43.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_170.addWidget(self.frame_43)

        self.gridLayout_48 = QGridLayout()
        self.gridLayout_48.setObjectName(u"gridLayout_48")
        self.gridLayout_48.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_171 = QVBoxLayout()
        self.verticalLayout_171.setObjectName(u"verticalLayout_171")
        self.label_105 = QLabel(self.widget_93)
        self.label_105.setObjectName(u"label_105")

        self.verticalLayout_171.addWidget(self.label_105)

        self.label_108 = QLabel(self.widget_93)
        self.label_108.setObjectName(u"label_108")
        self.label_108.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_171.addWidget(self.label_108)


        self.gridLayout_48.addLayout(self.verticalLayout_171, 0, 0, 1, 1)

        self.ZhuangBeiHeCheng_Enable = QCheckBox(self.widget_93)
        self.ZhuangBeiHeCheng_Enable.setObjectName(u"ZhuangBeiHeCheng_Enable")
        self.ZhuangBeiHeCheng_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.ZhuangBeiHeCheng_Enable.setStyleSheet(u"")

        self.gridLayout_48.addWidget(self.ZhuangBeiHeCheng_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_172 = QVBoxLayout()
        self.verticalLayout_172.setObjectName(u"verticalLayout_172")
        self.label_221 = QLabel(self.widget_93)
        self.label_221.setObjectName(u"label_221")

        self.verticalLayout_172.addWidget(self.label_221)

        self.label_222 = QLabel(self.widget_93)
        self.label_222.setObjectName(u"label_222")
        self.label_222.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_172.addWidget(self.label_222)


        self.gridLayout_48.addLayout(self.verticalLayout_172, 1, 0, 1, 1)

        self.ZhuangBeiHeCheng_next_execute_time = QLineEdit(self.widget_93)
        self.ZhuangBeiHeCheng_next_execute_time.setObjectName(u"ZhuangBeiHeCheng_next_execute_time")
        self.ZhuangBeiHeCheng_next_execute_time.setMinimumSize(QSize(200, 0))
        self.ZhuangBeiHeCheng_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.ZhuangBeiHeCheng_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_48.addWidget(self.ZhuangBeiHeCheng_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_48.setColumnStretch(0, 5)
        self.gridLayout_48.setColumnStretch(1, 2)

        self.verticalLayout_170.addLayout(self.gridLayout_48)


        self.verticalLayout_169.addWidget(self.widget_93)

        self.widget_96 = QWidget(self.scrollAreaWidgetContents_36)
        self.widget_96.setObjectName(u"widget_96")
        self.widget_96.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_177 = QVBoxLayout(self.widget_96)
        self.verticalLayout_177.setObjectName(u"verticalLayout_177")
        self.verticalLayout_177.setContentsMargins(-1, 7, -1, -1)
        self.label_109 = QLabel(self.widget_96)
        self.label_109.setObjectName(u"label_109")
        self.label_109.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_177.addWidget(self.label_109)

        self.frame_45 = QFrame(self.widget_96)
        self.frame_45.setObjectName(u"frame_45")
        self.frame_45.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_45.setFrameShape(QFrame.Shape.HLine)
        self.frame_45.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_177.addWidget(self.frame_45)

        self.gridLayout_49 = QGridLayout()
        self.gridLayout_49.setObjectName(u"gridLayout_49")
        self.gridLayout_49.setContentsMargins(10, 10, 0, 10)
        self.ZhuangBeiHeCheng_target_armor = QComboBox(self.widget_96)
        self.ZhuangBeiHeCheng_target_armor.addItem("")
        self.ZhuangBeiHeCheng_target_armor.addItem("")
        self.ZhuangBeiHeCheng_target_armor.addItem("")
        self.ZhuangBeiHeCheng_target_armor.addItem("")
        self.ZhuangBeiHeCheng_target_armor.addItem("")
        self.ZhuangBeiHeCheng_target_armor.addItem("")
        self.ZhuangBeiHeCheng_target_armor.setObjectName(u"ZhuangBeiHeCheng_target_armor")
        self.ZhuangBeiHeCheng_target_armor.setMinimumSize(QSize(100, 34))
        self.ZhuangBeiHeCheng_target_armor.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.gridLayout_49.addWidget(self.ZhuangBeiHeCheng_target_armor, 0, 1, 1, 1)

        self.verticalLayout_178 = QVBoxLayout()
        self.verticalLayout_178.setObjectName(u"verticalLayout_178")
        self.label_110 = QLabel(self.widget_96)
        self.label_110.setObjectName(u"label_110")

        self.verticalLayout_178.addWidget(self.label_110)

        self.label_111 = QLabel(self.widget_96)
        self.label_111.setObjectName(u"label_111")
        self.label_111.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_178.addWidget(self.label_111)


        self.gridLayout_49.addLayout(self.verticalLayout_178, 0, 0, 1, 1)

        self.gridLayout_49.setColumnStretch(0, 5)

        self.verticalLayout_177.addLayout(self.gridLayout_49)


        self.verticalLayout_169.addWidget(self.widget_96)

        self.verticalSpacer_31 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_169.addItem(self.verticalSpacer_31)

        self.scrollArea_39.setWidget(self.scrollAreaWidgetContents_36)

        self.horizontalLayout_69.addWidget(self.scrollArea_39)

        self.horizontalSpacer_72 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_69.addItem(self.horizontalSpacer_72)

        self.horizontalLayout_69.setStretch(0, 1)
        self.horizontalLayout_69.setStretch(1, 5)
        self.horizontalLayout_69.setStretch(2, 1)

        self.horizontalLayout_10.addWidget(self.widget_92)

        self.stackedWidget.addWidget(self.ZhuangBeiHeCheng)
        self.GaoJiRenZheZhaoMu_widget = QWidget()
        self.GaoJiRenZheZhaoMu_widget.setObjectName(u"GaoJiRenZheZhaoMu_widget")
        self.horizontalLayout_29 = QHBoxLayout(self.GaoJiRenZheZhaoMu_widget)
        self.horizontalLayout_29.setObjectName(u"horizontalLayout_29")
        self.widget_48 = QWidget(self.GaoJiRenZheZhaoMu_widget)
        self.widget_48.setObjectName(u"widget_48")
        self.widget_48.setStyleSheet(u"")
        self.horizontalLayout_28 = QHBoxLayout(self.widget_48)
        self.horizontalLayout_28.setObjectName(u"horizontalLayout_28")
        self.horizontalSpacer_27 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_28.addItem(self.horizontalSpacer_27)

        self.scrollArea_17 = QScrollArea(self.widget_48)
        self.scrollArea_17.setObjectName(u"scrollArea_17")
        self.scrollArea_17.setMinimumSize(QSize(600, 0))
        self.scrollArea_17.setWidgetResizable(True)
        self.scrollArea_17.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_14 = QWidget()
        self.scrollAreaWidgetContents_14.setObjectName(u"scrollAreaWidgetContents_14")
        self.scrollAreaWidgetContents_14.setGeometry(QRect(0, 0, 566, 234))
        self.verticalLayout_81 = QVBoxLayout(self.scrollAreaWidgetContents_14)
        self.verticalLayout_81.setSpacing(20)
        self.verticalLayout_81.setObjectName(u"verticalLayout_81")
        self.widget_49 = QWidget(self.scrollAreaWidgetContents_14)
        self.widget_49.setObjectName(u"widget_49")
        self.widget_49.setStyleSheet(u"QWidget {\n"
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
        self.verticalLayout_82 = QVBoxLayout(self.widget_49)
        self.verticalLayout_82.setObjectName(u"verticalLayout_82")
        self.verticalLayout_82.setContentsMargins(-1, 7, -1, -1)
        self.label_79 = QLabel(self.widget_49)
        self.label_79.setObjectName(u"label_79")
        self.label_79.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_82.addWidget(self.label_79)

        self.frame_21 = QFrame(self.widget_49)
        self.frame_21.setObjectName(u"frame_21")
        self.frame_21.setStyleSheet(u"QWidget QFrame{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }")
        self.frame_21.setFrameShape(QFrame.Shape.HLine)
        self.frame_21.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_82.addWidget(self.frame_21)

        self.gridLayout_26 = QGridLayout()
        self.gridLayout_26.setObjectName(u"gridLayout_26")
        self.gridLayout_26.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout_83 = QVBoxLayout()
        self.verticalLayout_83.setObjectName(u"verticalLayout_83")
        self.label_80 = QLabel(self.widget_49)
        self.label_80.setObjectName(u"label_80")

        self.verticalLayout_83.addWidget(self.label_80)

        self.label_81 = QLabel(self.widget_49)
        self.label_81.setObjectName(u"label_81")
        self.label_81.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_83.addWidget(self.label_81)


        self.gridLayout_26.addLayout(self.verticalLayout_83, 0, 0, 1, 1)

        self.GaoJiRenZheZhaoMu_Enable = QCheckBox(self.widget_49)
        self.GaoJiRenZheZhaoMu_Enable.setObjectName(u"GaoJiRenZheZhaoMu_Enable")
        self.GaoJiRenZheZhaoMu_Enable.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.GaoJiRenZheZhaoMu_Enable.setStyleSheet(u"")

        self.gridLayout_26.addWidget(self.GaoJiRenZheZhaoMu_Enable, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_84 = QVBoxLayout()
        self.verticalLayout_84.setObjectName(u"verticalLayout_84")
        self.label_136 = QLabel(self.widget_49)
        self.label_136.setObjectName(u"label_136")

        self.verticalLayout_84.addWidget(self.label_136)

        self.label_137 = QLabel(self.widget_49)
        self.label_137.setObjectName(u"label_137")
        self.label_137.setStyleSheet(u"font-size:11pt;\n"
"color:#959595;\n"
"margin-left:18px;")

        self.verticalLayout_84.addWidget(self.label_137)


        self.gridLayout_26.addLayout(self.verticalLayout_84, 1, 0, 1, 1)

        self.GaoJiRenZheZhaoMu_next_execute_time = QLineEdit(self.widget_49)
        self.GaoJiRenZheZhaoMu_next_execute_time.setObjectName(u"GaoJiRenZheZhaoMu_next_execute_time")
        self.GaoJiRenZheZhaoMu_next_execute_time.setMinimumSize(QSize(200, 0))
        self.GaoJiRenZheZhaoMu_next_execute_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.GaoJiRenZheZhaoMu_next_execute_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_26.addWidget(self.GaoJiRenZheZhaoMu_next_execute_time, 1, 1, 1, 1)

        self.gridLayout_26.setColumnStretch(0, 5)
        self.gridLayout_26.setColumnStretch(1, 2)

        self.verticalLayout_82.addLayout(self.gridLayout_26)


        self.verticalLayout_81.addWidget(self.widget_49)

        self.verticalSpacer_9 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_81.addItem(self.verticalSpacer_9)

        self.scrollArea_17.setWidget(self.scrollAreaWidgetContents_14)

        self.horizontalLayout_28.addWidget(self.scrollArea_17)

        self.horizontalSpacer_28 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_28.addItem(self.horizontalSpacer_28)

        self.horizontalLayout_28.setStretch(0, 1)
        self.horizontalLayout_28.setStretch(1, 5)
        self.horizontalLayout_28.setStretch(2, 1)

        self.horizontalLayout_29.addWidget(self.widget_48)

        self.stackedWidget.addWidget(self.GaoJiRenZheZhaoMu_widget)
        self.DQH_Settings_widget = QWidget()
        self.DQH_Settings_widget.setObjectName(u"DQH_Settings_widget")
        self.DQH_Settings_widget.setMinimumSize(QSize(180, 0))
        self.horizontalLayout_5 = QHBoxLayout(self.DQH_Settings_widget)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.widget_19 = QWidget(self.DQH_Settings_widget)
        self.widget_19.setObjectName(u"widget_19")
        self.widget_19.setStyleSheet(u"")
        self.horizontalLayout_12 = QHBoxLayout(self.widget_19)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_12.addItem(self.horizontalSpacer_9)

        self.scrollArea_8 = QScrollArea(self.widget_19)
        self.scrollArea_8.setObjectName(u"scrollArea_8")
        self.scrollArea_8.setMinimumSize(QSize(600, 0))
        self.scrollArea_8.setWidgetResizable(True)
        self.scrollArea_8.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.scrollAreaWidgetContents_5 = QWidget()
        self.scrollAreaWidgetContents_5.setObjectName(u"scrollAreaWidgetContents_5")
        self.scrollAreaWidgetContents_5.setGeometry(QRect(0, -87, 619, 1162))
        self.verticalLayout_25 = QVBoxLayout(self.scrollAreaWidgetContents_5)
        self.verticalLayout_25.setSpacing(20)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.verticalLayout_25.setContentsMargins(10, -1, 10, -1)
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

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_12.addItem(self.horizontalSpacer_10)

        self.horizontalLayout_12.setStretch(0, 1)
        self.horizontalLayout_12.setStretch(1, 5)
        self.horizontalLayout_12.setStretch(2, 1)

        self.horizontalLayout_5.addWidget(self.widget_19)

        self.stackedWidget.addWidget(self.DQH_Settings_widget)

        self.verticalLayout_2.addWidget(self.stackedWidget)


        self.horizontalLayout.addWidget(self.widget)


        self.horizontalLayout_56.addWidget(self.widget_31)


        self.retranslateUi(Service)
        self.screen_mode.currentIndexChanged.connect(self.screen_mode_settings_stackedWidget.setCurrentIndex)

        self.overview_panel_button.setDefault(False)
        self.stackedWidget.setCurrentIndex(37)
        self.screen_mode_settings_stackedWidget.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(Service)
    # setupUi

    def retranslateUi(self, Service):
        Service.setWindowTitle(QCoreApplication.translate("Service", u"Form", None))
        self.overview_panel_button.setText(QCoreApplication.translate("Service", u"\u603b\u89c8\u9762\u677f", None))
        ___qtreewidgetitem = self.treeWidget.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("Service", u"\u914d\u7f6e", None));

        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        ___qtreewidgetitem1 = self.treeWidget.topLevelItem(0)
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("Service", u"\u6bcf\u65e5\u4efb\u52a1", None));
        ___qtreewidgetitem2 = ___qtreewidgetitem1.child(0)
        ___qtreewidgetitem2.setText(0, QCoreApplication.translate("Service", u"\u767b\u5f55\u5956\u52b1", None));
        ___qtreewidgetitem3 = ___qtreewidgetitem1.child(1)
        ___qtreewidgetitem3.setText(0, QCoreApplication.translate("Service", u"\u6392\u884c\u699c\u70b9\u8d5e", None));
        ___qtreewidgetitem4 = ___qtreewidgetitem1.child(2)
        ___qtreewidgetitem4.setText(0, QCoreApplication.translate("Service", u"\u6bcf\u6708\u7b7e\u5230", None));
        ___qtreewidgetitem5 = ___qtreewidgetitem1.child(3)
        ___qtreewidgetitem5.setText(0, QCoreApplication.translate("Service", u"\u8d2d\u4e70\u4f53\u529b", None));
        ___qtreewidgetitem6 = ___qtreewidgetitem1.child(4)
        ___qtreewidgetitem6.setText(0, QCoreApplication.translate("Service", u"\u91d1\u5e01\u62db\u8d22", None));
        ___qtreewidgetitem7 = ___qtreewidgetitem1.child(5)
        ___qtreewidgetitem7.setText(0, QCoreApplication.translate("Service", u"\u5c0f\u961f\u7a81\u88ad", None));
        ___qtreewidgetitem8 = ___qtreewidgetitem1.child(6)
        ___qtreewidgetitem8.setText(0, QCoreApplication.translate("Service", u"\u7ec4\u7ec7\u7948\u798f", None));
        ___qtreewidgetitem9 = ___qtreewidgetitem1.child(7)
        ___qtreewidgetitem9.setText(0, QCoreApplication.translate("Service", u"\u597d\u53cb\u4f53\u529b", None));
        ___qtreewidgetitem10 = ___qtreewidgetitem1.child(8)
        ___qtreewidgetitem10.setText(0, QCoreApplication.translate("Service", u"\u666e\u901a\u5fcd\u8005\u62db\u52df", None));
        ___qtreewidgetitem11 = ___qtreewidgetitem1.child(9)
        ___qtreewidgetitem11.setText(0, QCoreApplication.translate("Service", u"\u6bcf\u65e5\u5206\u4eab", None));
        ___qtreewidgetitem12 = ___qtreewidgetitem1.child(10)
        ___qtreewidgetitem12.setText(0, QCoreApplication.translate("Service", u"\u4e30\u9976\u4e4b\u95f4", None));
        ___qtreewidgetitem13 = ___qtreewidgetitem1.child(11)
        ___qtreewidgetitem13.setText(0, QCoreApplication.translate("Service", u"\u4efb\u52a1\u96c6\u4f1a\u6240", None));
        ___qtreewidgetitem14 = ___qtreewidgetitem1.child(12)
        ___qtreewidgetitem14.setText(0, QCoreApplication.translate("Service", u"\u4e00\u4e50\u5916\u5356", None));
        ___qtreewidgetitem15 = ___qtreewidgetitem1.child(13)
        ___qtreewidgetitem15.setText(0, QCoreApplication.translate("Service", u"\u6bcf\u65e5\u80dc\u573a", None));
        ___qtreewidgetitem16 = ___qtreewidgetitem1.child(14)
        ___qtreewidgetitem16.setText(0, QCoreApplication.translate("Service", u"\u751f\u5b58\u6311\u6218", None));
        ___qtreewidgetitem17 = ___qtreewidgetitem1.child(15)
        ___qtreewidgetitem17.setText(0, QCoreApplication.translate("Service", u"\u79d8\u5883\u63a2\u9669", None));
        ___qtreewidgetitem18 = ___qtreewidgetitem1.child(16)
        ___qtreewidgetitem18.setText(0, QCoreApplication.translate("Service", u"\u5546\u57ce\u5956\u52b1", None));
        ___qtreewidgetitem19 = ___qtreewidgetitem1.child(17)
        ___qtreewidgetitem19.setText(0, QCoreApplication.translate("Service", u"\u60c5\u62a5\u7ad9", None));
        ___qtreewidgetitem20 = ___qtreewidgetitem1.child(18)
        ___qtreewidgetitem20.setText(0, QCoreApplication.translate("Service", u"\u5192\u9669\u526f\u672c", None));
        ___qtreewidgetitem21 = ___qtreewidgetitem1.child(19)
        ___qtreewidgetitem21.setText(0, QCoreApplication.translate("Service", u"\u6d3b\u8dc3\u5ea6\u5956\u52b1", None));
        ___qtreewidgetitem22 = ___qtreewidgetitem1.child(20)
        ___qtreewidgetitem22.setText(0, QCoreApplication.translate("Service", u"\u6e05\u7a7a\u90ae\u4ef6", None));
        ___qtreewidgetitem23 = self.treeWidget.topLevelItem(1)
        ___qtreewidgetitem23.setText(0, QCoreApplication.translate("Service", u"\u6bcf\u5468\u4efb\u52a1", None));
        ___qtreewidgetitem24 = ___qtreewidgetitem23.child(0)
        ___qtreewidgetitem24.setText(0, QCoreApplication.translate("Service", u"\u4fee\u884c\u4e4b\u8def", None));
        ___qtreewidgetitem25 = ___qtreewidgetitem23.child(1)
        ___qtreewidgetitem25.setText(0, QCoreApplication.translate("Service", u"\u6bcf\u5468\u80dc\u573a", None));
        ___qtreewidgetitem26 = ___qtreewidgetitem23.child(2)
        ___qtreewidgetitem26.setText(0, QCoreApplication.translate("Service", u"\u5fcd\u6cd5\u5e16\u70b9\u8d5e\u5206\u4eab", None));
        ___qtreewidgetitem27 = ___qtreewidgetitem23.child(3)
        ___qtreewidgetitem27.setText(0, QCoreApplication.translate("Service", u"\u66f4\u591a\u73a9\u6cd5", None));
        ___qtreewidgetitem28 = ___qtreewidgetitem23.child(4)
        ___qtreewidgetitem28.setText(0, QCoreApplication.translate("Service", u"\u56e2\u672c", None));
        ___qtreewidgetitem29 = ___qtreewidgetitem23.child(5)
        ___qtreewidgetitem29.setText(0, QCoreApplication.translate("Service", u"\u672c\u670d\u8981\u585e\u6218", None));
        ___qtreewidgetitem30 = ___qtreewidgetitem23.child(6)
        ___qtreewidgetitem30.setText(0, QCoreApplication.translate("Service", u"\u53db\u5fcd\u6765\u88ad", None));
        ___qtreewidgetitem31 = ___qtreewidgetitem23.child(7)
        ___qtreewidgetitem31.setText(0, QCoreApplication.translate("Service", u"\u5929\u5730\u6218\u573a", None));
        ___qtreewidgetitem32 = ___qtreewidgetitem23.child(8)
        ___qtreewidgetitem32.setText(0, QCoreApplication.translate("Service", u"\u8ffd\u51fb\u6653\u7ec4\u7ec7", None));
        ___qtreewidgetitem33 = self.treeWidget.topLevelItem(2)
        ___qtreewidgetitem33.setText(0, QCoreApplication.translate("Service", u"\u6bcf\u6708\u4efb\u52a1", None));
        ___qtreewidgetitem34 = ___qtreewidgetitem33.child(0)
        ___qtreewidgetitem34.setText(0, QCoreApplication.translate("Service", u"\u8de8\u670d\u8981\u585e\u6218", None));
        ___qtreewidgetitem35 = ___qtreewidgetitem33.child(1)
        ___qtreewidgetitem35.setText(0, QCoreApplication.translate("Service", u"\u5dc5\u5cf0\u5bf9\u51b3", None));
        ___qtreewidgetitem36 = ___qtreewidgetitem33.child(2)
        ___qtreewidgetitem36.setText(0, QCoreApplication.translate("Service", u"\u7ec4\u7ec7\u4e89\u9738", None));
        ___qtreewidgetitem37 = ___qtreewidgetitem33.child(3)
        ___qtreewidgetitem37.setText(0, QCoreApplication.translate("Service", u"\u8d5b\u5b63\u80dc\u573a", None));
        ___qtreewidgetitem38 = self.treeWidget.topLevelItem(3)
        ___qtreewidgetitem38.setText(0, QCoreApplication.translate("Service", u"\u5468\u671f\u4efb\u52a1", None));
        ___qtreewidgetitem39 = ___qtreewidgetitem38.child(0)
        ___qtreewidgetitem39.setText(0, QCoreApplication.translate("Service", u"\u88c5\u5907\u5408\u6210", None));
        ___qtreewidgetitem40 = ___qtreewidgetitem38.child(1)
        ___qtreewidgetitem40.setText(0, QCoreApplication.translate("Service", u"\u9ad8\u7ea7\u5fcd\u8005\u62db\u52df", None));
        ___qtreewidgetitem41 = self.treeWidget.topLevelItem(4)
        ___qtreewidgetitem41.setText(0, QCoreApplication.translate("Service", u"\u6d3b\u52a8\u4efb\u52a1", None));
        ___qtreewidgetitem42 = self.treeWidget.topLevelItem(5)
        ___qtreewidgetitem42.setText(0, QCoreApplication.translate("Service", u"\u52a9\u624b\u8bbe\u7f6e", None));
        self.treeWidget.setSortingEnabled(__sortingEnabled)

        self.label.setText(QCoreApplication.translate("Service", u"\u8c03\u5ea6\u5668", None))
        self.start_schedule_button.setText(QCoreApplication.translate("Service", u"\u542f\u52a8", None))
        self.label_2.setText(QCoreApplication.translate("Service", u"\u8fd0\u884c\u961f\u5217", None))
        self.label_3.setText(QCoreApplication.translate("Service", u"\u5c31\u7eea\u961f\u5217", None))
        self.label_4.setText(QCoreApplication.translate("Service", u"\u7b49\u5f85\u961f\u5217", None))
        self.label_5.setText(QCoreApplication.translate("Service", u"\u65e5\u5fd7", None))
        self.bool_debug.setText(QCoreApplication.translate("Service", u"\u8c03\u8bd5\u6a21\u5f0f", None))
        self.bool_save_img.setText(QCoreApplication.translate("Service", u"\u4fdd\u5b58\u56fe\u50cf", None))
        self.label_73.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_74.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_75.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.DengLuJiangLi_Enable.setText("")
        self.label_132.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_133.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_85.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_86.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_87.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.PaiHangBangDianZan_Enable.setText("")
        self.label_140.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_141.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_88.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_89.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_90.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.MeiYueQianDao_Enable.setText("")
        self.label_142.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_143.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_55.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_56.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_57.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.GouMaiTiLi_Enable.setText("")
        self.label_120.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_121.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_41.setText(QCoreApplication.translate("Service", u"\u8d2d\u4e70\u4f53\u529b", None))
#if QT_CONFIG(tooltip)
        self.label_42.setToolTip(QCoreApplication.translate("Service", u"  - DxCam\n"
"    \u901f\u5ea6\u5feb\uff0c\u4f46\u662f\u6a21\u62df\u5668\u7a97\u53e3\u5fc5\u987b\u5728\u5c4f\u5e55\u8fb9\u754c\u5185\uff0c\u4e0d\u80fd\u6700\u5c0f\u5316\u6216\u88ab\u906e\u6321\n"
"  - MuMu\n"
"    \u4f7f\u7528MuMu\u6a21\u62df\u5668\u7684\u63a5\u53e3\u622a\u56fe\uff0c\u6a21\u62df\u5668\u53ef\u4ee5\u6700\u5c0f\u5316/\u88ab\u906e\u6321\n"
"  - LD\n"
"    \u4f7f\u7528\u96f7\u7535\u6a21\u62df\u5668\u7684\u63a5\u53e3\u622a\u56fe\uff0c\u6a21\u62df\u5668\u53ef\u4ee5\u6700\u5c0f\u5316/\u88ab\u906e\u6321", None))
#endif // QT_CONFIG(tooltip)
        self.label_42.setText(QCoreApplication.translate("Service", u"\u8d2d\u4e70\u4f53\u529b\u6b21\u6570", None))
        self.label_43.setText(QCoreApplication.translate("Service", u"\u9700\u8981\u8bbe\u7f6e\u52a9\u624b\u8bbe\u7f6e-\u4e8c\u7ea7\u5bc6\u7801", None))
        self.GouMaiTiLi_times.setSuffix("")
        self.label_58.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_59.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_60.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.JinBiZhaoCai_Enable.setText("")
        self.label_122.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_123.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_44.setText(QCoreApplication.translate("Service", u"\u91d1\u5e01\u62db\u8d22", None))
#if QT_CONFIG(tooltip)
        self.label_45.setToolTip(QCoreApplication.translate("Service", u"  - DxCam\n"
"    \u901f\u5ea6\u5feb\uff0c\u4f46\u662f\u6a21\u62df\u5668\u7a97\u53e3\u5fc5\u987b\u5728\u5c4f\u5e55\u8fb9\u754c\u5185\uff0c\u4e0d\u80fd\u6700\u5c0f\u5316\u6216\u88ab\u906e\u6321\n"
"  - MuMu\n"
"    \u4f7f\u7528MuMu\u6a21\u62df\u5668\u7684\u63a5\u53e3\u622a\u56fe\uff0c\u6a21\u62df\u5668\u53ef\u4ee5\u6700\u5c0f\u5316/\u88ab\u906e\u6321\n"
"  - LD\n"
"    \u4f7f\u7528\u96f7\u7535\u6a21\u62df\u5668\u7684\u63a5\u53e3\u622a\u56fe\uff0c\u6a21\u62df\u5668\u53ef\u4ee5\u6700\u5c0f\u5316/\u88ab\u906e\u6321", None))
#endif // QT_CONFIG(tooltip)
        self.label_45.setText(QCoreApplication.translate("Service", u"\u62db\u8d22\u6b21\u6570", None))
        self.label_46.setText(QCoreApplication.translate("Service", u"\u8be5\u8bbe\u7f6e\u5305\u542b\u514d\u8d39\u6b21\u6570\u5728\u5185\u7684\u6b21\u6570!!!\n"
"\u9700\u8981\u8bbe\u7f6e\u52a9\u624b\u8bbe\u7f6e-\u4e8c\u7ea7\u5bc6\u7801", None))
        self.JinBiZhaoCai_times.setSuffix("")
        self.label_61.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_62.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_63.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.XiaoDuiTuXi_Enable.setText("")
        self.label_124.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_125.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_47.setText(QCoreApplication.translate("Service", u"\u5c0f\u961f\u7a81\u88ad", None))
#if QT_CONFIG(tooltip)
        self.label_48.setToolTip(QCoreApplication.translate("Service", u"  - DxCam\n"
"    \u901f\u5ea6\u5feb\uff0c\u4f46\u662f\u6a21\u62df\u5668\u7a97\u53e3\u5fc5\u987b\u5728\u5c4f\u5e55\u8fb9\u754c\u5185\uff0c\u4e0d\u80fd\u6700\u5c0f\u5316\u6216\u88ab\u906e\u6321\n"
"  - MuMu\n"
"    \u4f7f\u7528MuMu\u6a21\u62df\u5668\u7684\u63a5\u53e3\u622a\u56fe\uff0c\u6a21\u62df\u5668\u53ef\u4ee5\u6700\u5c0f\u5316/\u88ab\u906e\u6321\n"
"  - LD\n"
"    \u4f7f\u7528\u96f7\u7535\u6a21\u62df\u5668\u7684\u63a5\u53e3\u622a\u56fe\uff0c\u6a21\u62df\u5668\u53ef\u4ee5\u6700\u5c0f\u5316/\u88ab\u906e\u6321", None))
#endif // QT_CONFIG(tooltip)
        self.label_48.setText(QCoreApplication.translate("Service", u"\u56db\u500d\u5956\u52b1\u6b21\u6570", None))
        self.XiaoDuiTuXi_4rewards_times.setSuffix("")
        self.label_13.setText(QCoreApplication.translate("Service", u"\u56db\u500d\u5956\u52b1\u52fe\u9009", None))
        self.label_12.setText(QCoreApplication.translate("Service", u"\u9009\u62e9\u540e\u4f1a\u81ea\u52a8\u52fe\u9009\u6536\u53d6\u56db\u500d\u5956\u52b1\n"
"\u9700\u8981\u52a9\u624b\u8bbe\u7f6e\u4e2d\u8bbe\u7f6e\u4e8c\u7ea7\u5bc6\u7801", None))
        self.XiaoDuiTuXi_4rewards_Enable.setText("")
        self.label_187.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_188.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_189.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.ZuZhiQiFu_Enable.setText("")
        self.label_190.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_191.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_82.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_83.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_84.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.HaoYouTiLi_Enable.setText("")
        self.label_138.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_139.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_118.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_119.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_154.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.PuTongRenZheZhaoMu_Enable.setText("")
        self.label_155.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_156.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_94.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_38.setText(QCoreApplication.translate("Service", u"\u8be5\u4efb\u52a1\u53ef\u80fd\u4f1a\u56e0\u4e3a\u6a21\u62df\u5668\u706b\u5f71\u5206\u4eab\u5361\u6b7b\u95ee\u9898\u5931\u8d25\n"
"\u5982\u679c\u4f60\u7684\u6a21\u62df\u5668\u51fa\u8fc7\u8fd9\u79cd\u95ee\u9898\u8bf7\u8c28\u614e\u5f00\u542f", None))
        self.label_95.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_96.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668\n"
"\u9700\u8981\u6a21\u62df\u5668\u5b89\u88c5QQ\uff08\u767b\u4e0d\u767b\u5f55\u90fd\u53ef\u4ee5\uff09", None))
        self.MeiRiFenXiang_Enable.setText("")
        self.label_146.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_147.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_76.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_226.setText(QCoreApplication.translate("Service", u"\u9700\u8981\u5728\u52a9\u624b\u8bbe\u7f6e\u4e2d\u914d\u7f6e\u952e\u4f4d", None))
        self.label_77.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_78.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.FengRaoZhiJian_Enable.setText("")
        self.label_134.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_135.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_172.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_49.setText(QCoreApplication.translate("Service", u"\u7531\u4e8e\u63a5\u53d6\u7b97\u6cd5\u672a\u5b9e\u73b0\uff0c\u8d85\u5f71\u7279\u6743\u7528\u6237\u6536\u76ca\u4e0d\u80fd\u6700\u5927\u5316", None))
        self.label_173.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_174.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.RenWuJiHuiSuo_Enable.setText("")
        self.label_175.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_176.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_182.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_183.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_184.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.YiLeWaiMai_Enable.setText("")
        self.label_185.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_186.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_91.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_14.setText(QCoreApplication.translate("Service", u"\u6ce8\u610f\uff1a\u8be5\u4efb\u52a1\u4f1a\u76f4\u63a5\u4f7f\u7528\u5f53\u524d\u5339\u914d\u9635\u5bb9\uff0c\u8bf7\u63d0\u524d\u8bbe\u7f6e\u597d\u9635\u5bb9\u9632\u6b62\u6389\u80dc\u7387", None))
        self.label_92.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_93.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.MeiRiShengChang_Enable.setText("")
        self.label_144.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_145.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_192.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_50.setText(QCoreApplication.translate("Service", u"\u8bf7\u4fdd\u8bc1\u6218\u529b\u80fd\u626b\u8361\u8fc7\u751f\u5b58\u6311\u6218\uff0c\u5426\u5219\u6536\u76ca\u6ca1\u6709\u624b\u6253\u9ad8", None))
        self.label_193.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_194.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.ShengCunTiaoZhan_Enable.setText("")
        self.label_195.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_196.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_197.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_198.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_199.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.MiJingTanXian_Enable.setText("")
        self.label_200.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_201.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_259.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_261.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_262.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.ShangChengJiangLi_Enable.setText("")
        self.label_263.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_264.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_157.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_40.setText(QCoreApplication.translate("Service", u"\u8be5\u4efb\u52a1\u53ef\u80fd\u56e0\u4e3a\u7f51\u7edc\u8fde\u63a5\u5dee\u5bfc\u81f4\u5931\u8d25\uff0c\u8bf7\u52a1\u5fc5\u786e\u4fdd\u7f51\u7edc\u8fde\u63a5\u6b63\u5e38", None))
        self.label_158.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_159.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.QingBaoZhan_Enable.setText("")
        self.label_160.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_161.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_97.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_53.setText(QCoreApplication.translate("Service", u"\u8bf7\u4fdd\u8bc1\u81ea\u5df1\u5728\u6a21\u62df\u5668\u4e0a\u624b\u52a8\u626b\u8361\u8fc7\u4e00\u6b21\u7cbe\u82f1\u526f\u672c\n"
"\u5426\u5219\u4efb\u52a1\u4f1a\u52fe\u9009\u5168\u9009\u4ee5\u8fbe\u5230\u901a\u8fc7\u4efb\u52a1\u7684\u76ee\u7684", None))
        self.label_98.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_99.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.MaoXianFuBen_Enable.setText("")
        self.label_148.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_149.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_100.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_101.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_102.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.HuoYueDuJiangLi_Enable.setText("")
        self.label_150.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_151.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_162.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_163.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_164.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.QingKongYouJian_Enable.setText("")
        self.label_165.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_166.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_177.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_178.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_179.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.XiuXingZhiLu_Enable.setText("")
        self.label_180.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_181.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_64.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_65.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_66.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668\n"
"\u4e34\u65f6\u4efb\u52a1\u4f1a\u5728\u7ed3\u675f\u540e\u81ea\u52a8\u7981\u7528\u4efb\u52a1", None))
        self.MeiZhouShengChang_Enable.setText("")
        self.label_126.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_127.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_167.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_51.setText(QCoreApplication.translate("Service", u"\u6a21\u62df\u5668\u9700\u8981\u5b89\u88c5QQ", None))
        self.label_168.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_169.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.RenFaTieDianZanFenXiang_Enable.setText("")
        self.label_170.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_171.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_70.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_71.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_72.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668\n"
"\u4e34\u65f6\u4efb\u52a1\u4f1a\u5728\u7ed3\u675f\u540e\u81ea\u52a8\u7981\u7528\u4efb\u52a1", None))
        self.GengDuoWanFa_Enable.setText("")
        self.label_130.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_131.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_208.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_209.setText(QCoreApplication.translate("Service", u"\u5f85\u5f00\u53d1", None))
        self.label_210.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_211.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.TuanBen_Enable.setText("")
        self.label_212.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_213.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_241.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_242.setText(QCoreApplication.translate("Service", u"\u5f85\u5f00\u53d1", None))
        self.label_243.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_244.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.BenFuYaoSaiZhan_Enable.setText("")
        self.label_245.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_246.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_202.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_203.setText(QCoreApplication.translate("Service", u"\u5f85\u5f00\u53d1", None))
        self.label_204.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_205.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.PanRenLaiXi_Enable.setText("")
        self.label_206.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_207.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_247.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_248.setText(QCoreApplication.translate("Service", u"\u5f85\u5f00\u53d1", None))
        self.label_249.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_250.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.TianDiZhanChang_Enable.setText("")
        self.label_251.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_252.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_253.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_254.setText(QCoreApplication.translate("Service", u"\u5f85\u5f00\u53d1", None))
        self.label_255.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_256.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.ZhuiJiXiaoZuZhi_Enable.setText("")
        self.label_257.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_258.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_236.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_113.setText(QCoreApplication.translate("Service", u"\u5f85\u5f00\u53d1", None))
        self.label_237.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_238.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.KuaFuYaoSaiZhan_Enable.setText("")
        self.label_239.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_240.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_223.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_112.setText(QCoreApplication.translate("Service", u"\u5f85\u5f00\u53d1", None))
        self.label_224.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_225.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.DianFengDuiJue_Enable.setText("")
        self.label_232.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_235.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_103.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_39.setText(QCoreApplication.translate("Service", u"\u5f85\u5f00\u53d1", None))
        self.label_152.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_153.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_116.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_117.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.ZuZhiZhengBa_Enable.setText("")
        self.label_67.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_68.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_69.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668\n"
"\u4e34\u65f6\u4efb\u52a1\u4f1a\u5728\u7ed3\u675f\u540e\u81ea\u52a8\u7981\u7528\u4efb\u52a1", None))
        self.SaiJiShengChang_Enable.setText("")
        self.label_128.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_129.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_104.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_105.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_108.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668\n"
"\u4e34\u65f6\u4efb\u52a1\u4f1a\u5728\u7ed3\u675f\u540e\u81ea\u52a8\u7981\u7528\u4efb\u52a1", None))
        self.ZhuangBeiHeCheng_Enable.setText("")
        self.label_221.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_222.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_109.setText(QCoreApplication.translate("Service", u"\u88c5\u5907\u5408\u6210", None))
        self.ZhuangBeiHeCheng_target_armor.setItemText(0, QCoreApplication.translate("Service", u"\u6b66\u5668", None))
        self.ZhuangBeiHeCheng_target_armor.setItemText(1, QCoreApplication.translate("Service", u"\u5934\u76d4", None))
        self.ZhuangBeiHeCheng_target_armor.setItemText(2, QCoreApplication.translate("Service", u"\u80f8\u7532", None))
        self.ZhuangBeiHeCheng_target_armor.setItemText(3, QCoreApplication.translate("Service", u"\u5fcd\u4e4b\u4e66", None))
        self.ZhuangBeiHeCheng_target_armor.setItemText(4, QCoreApplication.translate("Service", u"\u9879\u94fe", None))
        self.ZhuangBeiHeCheng_target_armor.setItemText(5, QCoreApplication.translate("Service", u"\u6212\u6307", None))

        self.label_110.setText(QCoreApplication.translate("Service", u"\u5408\u6210\u76ee\u6807\u88c5\u5907", None))
        self.label_111.setText(QCoreApplication.translate("Service", u"\u5c06\u4f53\u529b\u6d88\u8017\u5728\u8be5\u90e8\u4f4d\u88c5\u5907\u7684\u6750\u6599\u626b\u8361\u548c\u8fdb\u9636\u4e0a", None))
        self.label_79.setText(QCoreApplication.translate("Service", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_80.setText(QCoreApplication.translate("Service", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_81.setText(QCoreApplication.translate("Service", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.GaoJiRenZheZhaoMu_Enable.setText("")
        self.label_136.setText(QCoreApplication.translate("Service", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_137.setText(QCoreApplication.translate("Service", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
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

