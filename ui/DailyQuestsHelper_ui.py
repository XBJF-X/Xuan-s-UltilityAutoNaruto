# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DailyQuestsHelper.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QHBoxLayout,
    QHeaderView, QLabel, QMainWindow, QPushButton,
    QScrollArea, QSizePolicy, QStackedWidget, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidget)

class Ui_DailyQuestsHelper(object):
    def setupUi(self, DailyQuestsHelper):
        if not DailyQuestsHelper.objectName():
            DailyQuestsHelper.setObjectName(u"DailyQuestsHelper")
        DailyQuestsHelper.resize(1320, 598)
        font = QFont()
        font.setFamilies([u"\u4ed3\u8033\u4eca\u697702-6763"])
        DailyQuestsHelper.setFont(font)
        DailyQuestsHelper.setStyleSheet(u"")
        self.centralwidget = QWidget(DailyQuestsHelper)
        self.centralwidget.setObjectName(u"centralwidget")
        font1 = QFont()
        font1.setFamilies([u"\u4ed3\u8033\u4eca\u697702-6763"])
        font1.setPointSize(15)
        self.centralwidget.setFont(font1)
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.widget_10 = QWidget(self.centralwidget)
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
        self.widget_10.setFont(font1)
        self.widget_10.setStyleSheet(u"background-color: white;")
        self.verticalLayout_5 = QVBoxLayout(self.widget_10)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.widget_9 = QWidget(self.widget_10)
        self.widget_9.setObjectName(u"widget_9")
        self.widget_9.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";")
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
        font2 = QFont()
        font2.setFamilies([u"\u4ed3\u8033\u4eca\u697702-6763"])
        font2.setPointSize(15)
        font2.setBold(False)
        font2.setItalic(False)
        self.overview_panel_button.setFont(font2)
        self.overview_panel_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.overview_panel_button.setStyleSheet(u"border: 2px solid #b5b5b5;  /* 2px\u5bbd\u7684\u6df1\u7070\u8272\u5b9e\u7ebf\u8fb9\u6846 */\n"
"background-color: rgb(255, 255, 255);\n"
"border-radius:10px;")
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
        __qtreewidgetitem1 = QTreeWidgetItem(self.treeWidget)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(__qtreewidgetitem1)
        __qtreewidgetitem2 = QTreeWidgetItem(self.treeWidget)
        QTreeWidgetItem(__qtreewidgetitem2)
        __qtreewidgetitem3 = QTreeWidgetItem(self.treeWidget)
        QTreeWidgetItem(__qtreewidgetitem3)
        __qtreewidgetitem4 = QTreeWidgetItem(self.treeWidget)
        QTreeWidgetItem(__qtreewidgetitem4)
        QTreeWidgetItem(__qtreewidgetitem4)
        QTreeWidgetItem(__qtreewidgetitem4)
        QTreeWidgetItem(__qtreewidgetitem4)
        QTreeWidgetItem(self.treeWidget)
        QTreeWidgetItem(self.treeWidget)
        self.treeWidget.setObjectName(u"treeWidget")
        self.treeWidget.setMaximumSize(QSize(16777215, 16777215))
        self.treeWidget.setFont(font)
        self.treeWidget.setStyleSheet(u"QTreeWidget {\n"
"	background-color:#f5f5f5;\n"
"	margin-left:10px;\n"
"	background: #F9F9F9;\n"
"	border-right: 1px solid #D3D6DD;\n"
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
"QTreeWidget::branc"
                        "h {\n"
"	height: 28px;\n"
"	width: 28px;\n"
"}\n"
" \n"
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
"}")
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

        self.widget = QWidget(self.centralwidget)
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
        self.horizontalLayout_2 = QHBoxLayout(self.Overview_Panel_widget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.widget_2 = QWidget(self.Overview_Panel_widget)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setMinimumSize(QSize(270, 0))
        self.widget_2.setMaximumSize(QSize(270, 16777215))
        self.widget_2.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";")
        self.verticalLayout_3 = QVBoxLayout(self.widget_2)
        self.verticalLayout_3.setSpacing(9)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(7, 0, 7, 0)
        self.widget_4 = QWidget(self.widget_2)
        self.widget_4.setObjectName(u"widget_4")
        palette2 = QPalette()
        brush2 = QBrush(QColor(222, 222, 222, 255))
        brush2.setStyle(Qt.BrushStyle.SolidPattern)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush2)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush2)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush2)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush2)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush2)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush2)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush2)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush2)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush2)
        self.widget_4.setPalette(palette2)
        self.widget_4.setStyleSheet(u"#widget_4 {  /* \u4ec5\u5339\u914d objectName \u4e3a myWidget \u7684\u63a7\u4ef6 */\n"
"    background-color: rgb(222, 222, 222);\n"
"border-radius: 10px;\n"
"}")
        self.horizontalLayout_3 = QHBoxLayout(self.widget_4)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
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
        self.start_schedule_button.setStyleSheet(u"QPushBotton:{\n"
"border-radius: 10px;\n"
"border: none;\n"
"border-bottom:0px;\n"
"}")

        self.horizontalLayout_3.addWidget(self.start_schedule_button)


        self.verticalLayout_3.addWidget(self.widget_4)

        self.widget_5 = QWidget(self.widget_2)
        self.widget_5.setObjectName(u"widget_5")
        self.widget_5.setStyleSheet(u"#widget_5 {  /* \u4ec5\u5339\u914d objectName \u4e3a myWidget \u7684\u63a7\u4ef6 */\n"
"    background-color: rgb(222, 222, 222);\n"
"border-radius: 10px;\n"
"}")
        self.verticalLayout = QVBoxLayout(self.widget_5)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 0, 5, 5)
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
        brush3 = QBrush(QColor(179, 179, 179, 255))
        brush3.setStyle(Qt.BrushStyle.SolidPattern)
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush3)
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush3)
        brush4 = QBrush(QColor(120, 120, 120, 255))
        brush4.setStyle(Qt.BrushStyle.SolidPattern)
        palette3.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush4)
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
        self.scroll_area_running_content.setGeometry(QRect(0, 0, 230, 63))
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
        self.verticalLayout_6.setSpacing(3)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(5, 0, 5, 5)
        self.label_3 = QLabel(self.widget_6)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setStyleSheet(u"margin-top:3px;\n"
"margin-bottom:0px;")

        self.verticalLayout_6.addWidget(self.label_3)

        self.line_2 = QFrame(self.widget_6)
        self.line_2.setObjectName(u"line_2")
        palette4 = QPalette()
        palette4.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush3)
        palette4.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush3)
        palette4.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush4)
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
        self.scroll_area_ready_content.setGeometry(QRect(0, 0, 230, 147))
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
        self.verticalLayout_7.setSpacing(3)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(5, 0, 5, 5)
        self.label_4 = QLabel(self.widget_7)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setStyleSheet(u"\n"
"margin-top:3px;\n"
"margin-bottom:0px;")

        self.verticalLayout_7.addWidget(self.label_4)

        self.line_3 = QFrame(self.widget_7)
        self.line_3.setObjectName(u"line_3")
        palette5 = QPalette()
        palette5.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush3)
        palette5.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush3)
        palette5.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush4)
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
        self.scroll_area_wait_content.setGeometry(QRect(0, 0, 230, 147))
        self.scrollArea_3.setWidget(self.scroll_area_wait_content)

        self.verticalLayout_7.addWidget(self.scrollArea_3)


        self.verticalLayout_3.addWidget(self.widget_7)

        self.verticalLayout_3.setStretch(0, 1)
        self.verticalLayout_3.setStretch(2, 4)
        self.verticalLayout_3.setStretch(3, 4)

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
        self.verticalLayout_10.setContentsMargins(7, 0, 0, 0)
        self.widget_12 = QWidget(self.widget_8)
        self.widget_12.setObjectName(u"widget_12")
        self.widget_12.setStyleSheet(u"#widget_12 {  /* \u4ec5\u5339\u914d objectName \u4e3a myWidget \u7684\u63a7\u4ef6 */\n"
"    background-color: rgb(222, 222, 222);\n"
"border-radius: 10px;\n"
"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"}")
        self.horizontalLayout_4 = QHBoxLayout(self.widget_12)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_5 = QLabel(self.widget_12)
        self.label_5.setObjectName(u"label_5")
        font3 = QFont()
        font3.setFamilies([u"\u4ed3\u8033\u4eca\u697702-6763"])
        font3.setBold(False)
        font3.setItalic(False)
        self.label_5.setFont(font3)
        self.label_5.setStyleSheet(u"font-size:25px;")
        self.label_5.setIndent(10)

        self.horizontalLayout_4.addWidget(self.label_5)

        self.bool_save_img = QCheckBox(self.widget_12)
        self.bool_save_img.setObjectName(u"bool_save_img")
        self.bool_save_img.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";")

        self.horizontalLayout_4.addWidget(self.bool_save_img, 0, Qt.AlignmentFlag.AlignRight)


        self.verticalLayout_10.addWidget(self.widget_12)


        self.verticalLayout_4.addWidget(self.widget_8)

        self.logs_container = QWidget(self.widget_3)
        self.logs_container.setObjectName(u"logs_container")
        self.logs_container.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.logs_container.setStyleSheet(u"")

        self.verticalLayout_4.addWidget(self.logs_container)

        self.verticalLayout_4.setStretch(0, 1)
        self.verticalLayout_4.setStretch(1, 11)

        self.horizontalLayout_2.addWidget(self.widget_3)

        self.horizontalLayout_2.setStretch(1, 1)
        self.stackedWidget.addWidget(self.Overview_Panel_widget)
        self.DengLuJiangLi_widget = QWidget()
        self.DengLuJiangLi_widget.setObjectName(u"DengLuJiangLi_widget")
        self.stackedWidget.addWidget(self.DengLuJiangLi_widget)
        self.PaiHangBangDianZan_widget = QWidget()
        self.PaiHangBangDianZan_widget.setObjectName(u"PaiHangBangDianZan_widget")
        self.stackedWidget.addWidget(self.PaiHangBangDianZan_widget)
        self.MeiYueQianDao_widget = QWidget()
        self.MeiYueQianDao_widget.setObjectName(u"MeiYueQianDao_widget")
        self.stackedWidget.addWidget(self.MeiYueQianDao_widget)
        self.GouMaiTiLi_widget = QWidget()
        self.GouMaiTiLi_widget.setObjectName(u"GouMaiTiLi_widget")
        self.stackedWidget.addWidget(self.GouMaiTiLi_widget)
        self.JinBiZhaoCai_widget = QWidget()
        self.JinBiZhaoCai_widget.setObjectName(u"JinBiZhaoCai_widget")
        self.stackedWidget.addWidget(self.JinBiZhaoCai_widget)
        self.XiaoDuiTuXi_widget = QWidget()
        self.XiaoDuiTuXi_widget.setObjectName(u"XiaoDuiTuXi_widget")
        self.stackedWidget.addWidget(self.XiaoDuiTuXi_widget)
        self.ZuZhiQiFu_widget = QWidget()
        self.ZuZhiQiFu_widget.setObjectName(u"ZuZhiQiFu_widget")
        self.stackedWidget.addWidget(self.ZuZhiQiFu_widget)
        self.HaoYouTiLi_widget = QWidget()
        self.HaoYouTiLi_widget.setObjectName(u"HaoYouTiLi_widget")
        self.stackedWidget.addWidget(self.HaoYouTiLi_widget)
        self.PuTongRenZheZhaoMu_widget = QWidget()
        self.PuTongRenZheZhaoMu_widget.setObjectName(u"PuTongRenZheZhaoMu_widget")
        self.stackedWidget.addWidget(self.PuTongRenZheZhaoMu_widget)
        self.MeiRiFenXiang_widget = QWidget()
        self.MeiRiFenXiang_widget.setObjectName(u"MeiRiFenXiang_widget")
        self.stackedWidget.addWidget(self.MeiRiFenXiang_widget)
        self.FengRaoZhiJian_widget = QWidget()
        self.FengRaoZhiJian_widget.setObjectName(u"FengRaoZhiJian_widget")
        self.stackedWidget.addWidget(self.FengRaoZhiJian_widget)
        self.RenWuJiHuiSuo_widget = QWidget()
        self.RenWuJiHuiSuo_widget.setObjectName(u"RenWuJiHuiSuo_widget")
        self.stackedWidget.addWidget(self.RenWuJiHuiSuo_widget)
        self.YiLeWaiMai_widget = QWidget()
        self.YiLeWaiMai_widget.setObjectName(u"YiLeWaiMai_widget")
        self.stackedWidget.addWidget(self.YiLeWaiMai_widget)
        self.MeiRiShengChang_widget = QWidget()
        self.MeiRiShengChang_widget.setObjectName(u"MeiRiShengChang_widget")
        self.stackedWidget.addWidget(self.MeiRiShengChang_widget)
        self.ShengCunTiaoZhan_widget = QWidget()
        self.ShengCunTiaoZhan_widget.setObjectName(u"ShengCunTiaoZhan_widget")
        self.stackedWidget.addWidget(self.ShengCunTiaoZhan_widget)
        self.MiJingTanXian_widget = QWidget()
        self.MiJingTanXian_widget.setObjectName(u"MiJingTanXian_widget")
        self.stackedWidget.addWidget(self.MiJingTanXian_widget)
        self.QingBaoZhan_widget = QWidget()
        self.QingBaoZhan_widget.setObjectName(u"QingBaoZhan_widget")
        self.stackedWidget.addWidget(self.QingBaoZhan_widget)
        self.MaoXianFuBen_widget = QWidget()
        self.MaoXianFuBen_widget.setObjectName(u"MaoXianFuBen_widget")
        self.stackedWidget.addWidget(self.MaoXianFuBen_widget)
        self.HuoYueDuJiangLi_widget = QWidget()
        self.HuoYueDuJiangLi_widget.setObjectName(u"HuoYueDuJiangLi_widget")
        self.stackedWidget.addWidget(self.HuoYueDuJiangLi_widget)
        self.QingKongYouJian_widget = QWidget()
        self.QingKongYouJian_widget.setObjectName(u"QingKongYouJian_widget")
        self.stackedWidget.addWidget(self.QingKongYouJian_widget)
        self.XiuXingZhiLu_widget = QWidget()
        self.XiuXingZhiLu_widget.setObjectName(u"XiuXingZhiLu_widget")
        self.stackedWidget.addWidget(self.XiuXingZhiLu_widget)
        self.RenFaTieDianZanFenXiang_widget = QWidget()
        self.RenFaTieDianZanFenXiang_widget.setObjectName(u"RenFaTieDianZanFenXiang_widget")
        self.stackedWidget.addWidget(self.RenFaTieDianZanFenXiang_widget)
        self.TuanBen_widget = QWidget()
        self.TuanBen_widget.setObjectName(u"TuanBen_widget")
        self.stackedWidget.addWidget(self.TuanBen_widget)
        self.YaoSaiZhengDuoZhan_widget = QWidget()
        self.YaoSaiZhengDuoZhan_widget.setObjectName(u"YaoSaiZhengDuoZhan_widget")
        self.stackedWidget.addWidget(self.YaoSaiZhengDuoZhan_widget)
        self.PanRenLaiXi_widget = QWidget()
        self.PanRenLaiXi_widget.setObjectName(u"PanRenLaiXi_widget")
        self.stackedWidget.addWidget(self.PanRenLaiXi_widget)
        self.KuaFuZhengBaSai_widget = QWidget()
        self.KuaFuZhengBaSai_widget.setObjectName(u"KuaFuZhengBaSai_widget")
        self.stackedWidget.addWidget(self.KuaFuZhengBaSai_widget)
        self.GaoJiRenZheZhaoMu_widget = QWidget()
        self.GaoJiRenZheZhaoMu_widget.setObjectName(u"GaoJiRenZheZhaoMu_widget")
        self.stackedWidget.addWidget(self.GaoJiRenZheZhaoMu_widget)
        self.MeiZhouShengChang_widget = QWidget()
        self.MeiZhouShengChang_widget.setObjectName(u"MeiZhouShengChang_widget")
        self.stackedWidget.addWidget(self.MeiZhouShengChang_widget)
        self.SaiJiShengChang_widget = QWidget()
        self.SaiJiShengChang_widget.setObjectName(u"SaiJiShengChang_widget")
        self.stackedWidget.addWidget(self.SaiJiShengChang_widget)
        self.GengDuoWanFa_widget = QWidget()
        self.GengDuoWanFa_widget.setObjectName(u"GengDuoWanFa_widget")
        self.stackedWidget.addWidget(self.GengDuoWanFa_widget)
        self.ChongQiYouXi_widget = QWidget()
        self.ChongQiYouXi_widget.setObjectName(u"ChongQiYouXi_widget")
        self.stackedWidget.addWidget(self.ChongQiYouXi_widget)
        self.DQH_Settings_widget = QWidget()
        self.DQH_Settings_widget.setObjectName(u"DQH_Settings_widget")
        self.stackedWidget.addWidget(self.DQH_Settings_widget)

        self.verticalLayout_2.addWidget(self.stackedWidget)


        self.horizontalLayout.addWidget(self.widget)

        DailyQuestsHelper.setCentralWidget(self.centralwidget)

        self.retranslateUi(DailyQuestsHelper)

        self.overview_panel_button.setDefault(False)


        QMetaObject.connectSlotsByName(DailyQuestsHelper)
    # setupUi

    def retranslateUi(self, DailyQuestsHelper):
        DailyQuestsHelper.setWindowTitle(QCoreApplication.translate("DailyQuestsHelper", u"\u65e5\u5e38\u52a9\u624b", None))
        self.overview_panel_button.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u603b\u89c8\u9762\u677f", None))
        ___qtreewidgetitem = self.treeWidget.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u914d\u7f6e", None));

        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        ___qtreewidgetitem1 = self.treeWidget.topLevelItem(0)
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u6bcf\u65e5\u4efb\u52a1", None));
        ___qtreewidgetitem2 = ___qtreewidgetitem1.child(0)
        ___qtreewidgetitem2.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u767b\u5f55\u5956\u52b1", None));
        ___qtreewidgetitem3 = ___qtreewidgetitem1.child(1)
        ___qtreewidgetitem3.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u6392\u884c\u699c\u70b9\u8d5e", None));
        ___qtreewidgetitem4 = ___qtreewidgetitem1.child(2)
        ___qtreewidgetitem4.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u6bcf\u6708\u7b7e\u5230", None));
        ___qtreewidgetitem5 = ___qtreewidgetitem1.child(3)
        ___qtreewidgetitem5.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u8d2d\u4e70\u4f53\u529b", None));
        ___qtreewidgetitem6 = ___qtreewidgetitem1.child(4)
        ___qtreewidgetitem6.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u91d1\u5e01\u62db\u8d22", None));
        ___qtreewidgetitem7 = ___qtreewidgetitem1.child(5)
        ___qtreewidgetitem7.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u5c0f\u961f\u7a81\u88ad", None));
        ___qtreewidgetitem8 = ___qtreewidgetitem1.child(6)
        ___qtreewidgetitem8.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u7ec4\u7ec7\u7948\u798f", None));
        ___qtreewidgetitem9 = ___qtreewidgetitem1.child(7)
        ___qtreewidgetitem9.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u597d\u53cb\u4f53\u529b", None));
        ___qtreewidgetitem10 = ___qtreewidgetitem1.child(8)
        ___qtreewidgetitem10.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u666e\u901a\u5fcd\u8005\u62db\u52df", None));
        ___qtreewidgetitem11 = ___qtreewidgetitem1.child(9)
        ___qtreewidgetitem11.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u6bcf\u65e5\u5206\u4eab", None));
        ___qtreewidgetitem12 = ___qtreewidgetitem1.child(10)
        ___qtreewidgetitem12.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u4e30\u9976\u4e4b\u95f4", None));
        ___qtreewidgetitem13 = ___qtreewidgetitem1.child(11)
        ___qtreewidgetitem13.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u96c6\u4f1a\u6240", None));
        ___qtreewidgetitem14 = ___qtreewidgetitem1.child(12)
        ___qtreewidgetitem14.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u4e00\u4e50\u5916\u5356", None));
        ___qtreewidgetitem15 = ___qtreewidgetitem1.child(13)
        ___qtreewidgetitem15.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u6bcf\u65e5\u80dc\u573a", None));
        ___qtreewidgetitem16 = ___qtreewidgetitem1.child(14)
        ___qtreewidgetitem16.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u751f\u5b58\u6311\u6218", None));
        ___qtreewidgetitem17 = ___qtreewidgetitem1.child(15)
        ___qtreewidgetitem17.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u79d8\u5883\u63a2\u9669", None));
        ___qtreewidgetitem18 = ___qtreewidgetitem1.child(16)
        ___qtreewidgetitem18.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u60c5\u62a5\u7ad9", None));
        ___qtreewidgetitem19 = ___qtreewidgetitem1.child(17)
        ___qtreewidgetitem19.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u5192\u9669\u526f\u672c", None));
        ___qtreewidgetitem20 = ___qtreewidgetitem1.child(18)
        ___qtreewidgetitem20.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u6d3b\u8dc3\u5ea6\u5956\u52b1", None));
        ___qtreewidgetitem21 = ___qtreewidgetitem1.child(19)
        ___qtreewidgetitem21.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u6e05\u7a7a\u90ae\u4ef6", None));
        ___qtreewidgetitem22 = self.treeWidget.topLevelItem(1)
        ___qtreewidgetitem22.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u6bcf\u5468\u4efb\u52a1", None));
        ___qtreewidgetitem23 = ___qtreewidgetitem22.child(0)
        ___qtreewidgetitem23.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u4fee\u884c\u4e4b\u8def", None));
        ___qtreewidgetitem24 = ___qtreewidgetitem22.child(1)
        ___qtreewidgetitem24.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u5fcd\u6cd5\u5e16\u70b9\u8d5e\u5206\u4eab", None));
        ___qtreewidgetitem25 = ___qtreewidgetitem22.child(2)
        ___qtreewidgetitem25.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u56e2\u672c", None));
        ___qtreewidgetitem26 = ___qtreewidgetitem22.child(3)
        ___qtreewidgetitem26.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u8981\u585e\u4e89\u593a\u6218", None));
        ___qtreewidgetitem27 = ___qtreewidgetitem22.child(4)
        ___qtreewidgetitem27.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u53db\u5fcd\u6765\u88ad", None));
        ___qtreewidgetitem28 = self.treeWidget.topLevelItem(2)
        ___qtreewidgetitem28.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u6bcf\u6708\u4efb\u52a1", None));
        ___qtreewidgetitem29 = ___qtreewidgetitem28.child(0)
        ___qtreewidgetitem29.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u8de8\u670d\u4e89\u9738\u8d5b", None));
        ___qtreewidgetitem30 = self.treeWidget.topLevelItem(3)
        ___qtreewidgetitem30.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u5468\u671f\u4efb\u52a1", None));
        ___qtreewidgetitem31 = ___qtreewidgetitem30.child(0)
        ___qtreewidgetitem31.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u9ad8\u7ea7\u5fcd\u8005\u62db\u52df", None));
        ___qtreewidgetitem32 = self.treeWidget.topLevelItem(4)
        ___qtreewidgetitem32.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u4e34\u65f6\u4efb\u52a1", None));
        ___qtreewidgetitem33 = ___qtreewidgetitem32.child(0)
        ___qtreewidgetitem33.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u6bcf\u5468\u80dc\u573a", None));
        ___qtreewidgetitem34 = ___qtreewidgetitem32.child(1)
        ___qtreewidgetitem34.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u8d5b\u5b63\u80dc\u573a", None));
        ___qtreewidgetitem35 = ___qtreewidgetitem32.child(2)
        ___qtreewidgetitem35.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u66f4\u591a\u73a9\u6cd5", None));
        ___qtreewidgetitem36 = ___qtreewidgetitem32.child(3)
        ___qtreewidgetitem36.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u91cd\u542f\u6e38\u620f", None));
        ___qtreewidgetitem37 = self.treeWidget.topLevelItem(5)
        ___qtreewidgetitem37.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u6d3b\u52a8\u4efb\u52a1", None));
        ___qtreewidgetitem38 = self.treeWidget.topLevelItem(6)
        ___qtreewidgetitem38.setText(0, QCoreApplication.translate("DailyQuestsHelper", u"\u52a9\u624b\u8bbe\u7f6e", None));
        self.treeWidget.setSortingEnabled(__sortingEnabled)

        self.label.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u8c03\u5ea6\u5668", None))
        self.start_schedule_button.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u52a8", None))
        self.label_2.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u8fd0\u884c\u961f\u5217", None))
        self.label_3.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c31\u7eea\u961f\u5217", None))
        self.label_4.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u7b49\u5f85\u961f\u5217", None))
        self.label_5.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u65e5\u5fd7", None))
        self.bool_save_img.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4fdd\u5b58\u56fe\u50cf\uff08Debug\u7528\uff09", None))
    # retranslateUi

