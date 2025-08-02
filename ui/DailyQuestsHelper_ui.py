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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QGridLayout,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QMainWindow, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QStackedWidget, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget)

class Ui_DailyQuestsHelper(object):
    def setupUi(self, DailyQuestsHelper):
        if not DailyQuestsHelper.objectName():
            DailyQuestsHelper.setObjectName(u"DailyQuestsHelper")
        DailyQuestsHelper.resize(1328, 592)
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
        self.horizontalLayout.setObjectName(u"horizontalLayout")
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
        self.widget_2.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
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
        self.scroll_area_ready_content.setGeometry(QRect(0, 0, 230, 137))
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
        self.scroll_area_wait_content.setGeometry(QRect(0, 0, 230, 136))
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
        self.widget_12.setStyleSheet(u"#widget_12 {\n"
"    background-color: rgb(222, 222, 222);\n"
"	border-radius: 10px;\n"
"	font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"}\n"
"QLabel{color:#0f322f;}\n"
"QCheckBox{color:#0f322f;}")
        self.horizontalLayout_4 = QHBoxLayout(self.widget_12)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_5 = QLabel(self.widget_12)
        self.label_5.setObjectName(u"label_5")
        font3 = QFont()
        font3.setFamilies([u"\u4ed3\u8033\u4eca\u697702-6763"])
        font3.setBold(False)
        font3.setItalic(False)
        self.label_5.setFont(font3)
        self.label_5.setStyleSheet(u"font-size:25px;\n"
"")
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
        self.horizontalLayout_63 = QHBoxLayout(self.DengLuJiangLi_widget)
        self.horizontalLayout_63.setObjectName(u"horizontalLayout_63")
        self.widget_21 = QWidget(self.DengLuJiangLi_widget)
        self.widget_21.setObjectName(u"widget_21")
        self.widget_21.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_12 = QHBoxLayout(self.widget_21)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_12.addItem(self.horizontalSpacer_9)

        self.scrollArea_8 = QScrollArea(self.widget_21)
        self.scrollArea_8.setObjectName(u"scrollArea_8")
        self.scrollArea_8.setMinimumSize(QSize(600, 0))
        self.scrollArea_8.setWidgetResizable(True)
        self.scrollAreaWidgetContents_5 = QWidget()
        self.scrollAreaWidgetContents_5.setObjectName(u"scrollAreaWidgetContents_5")
        self.scrollAreaWidgetContents_5.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_25 = QVBoxLayout(self.scrollAreaWidgetContents_5)
        self.verticalLayout_25.setSpacing(10)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.verticalLayout_25.setContentsMargins(10, -1, 10, -1)
        self.widget_22 = QWidget(self.scrollAreaWidgetContents_5)
        self.widget_22.setObjectName(u"widget_22")
        self.widget_22.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_26 = QVBoxLayout(self.widget_22)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")
        self.label_18 = QLabel(self.widget_22)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_26.addWidget(self.label_18)

        self.line_8 = QFrame(self.widget_22)
        self.line_8.setObjectName(u"line_8")
        sizePolicy1.setHeightForWidth(self.line_8.sizePolicy().hasHeightForWidth())
        self.line_8.setSizePolicy(sizePolicy1)
        self.line_8.setStyleSheet(u"")
        self.line_8.setLineWidth(0)
        self.line_8.setMidLineWidth(2)
        self.line_8.setFrameShape(QFrame.Shape.HLine)
        self.line_8.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_26.addWidget(self.line_8)

        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_27 = QVBoxLayout()
        self.verticalLayout_27.setObjectName(u"verticalLayout_27")
        self.label_19 = QLabel(self.widget_22)
        self.label_19.setObjectName(u"label_19")

        self.verticalLayout_27.addWidget(self.label_19)

        self.label_20 = QLabel(self.widget_22)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_27.addWidget(self.label_20)


        self.gridLayout_5.addLayout(self.verticalLayout_27, 0, 0, 1, 1)

        self.checkBox_5 = QCheckBox(self.widget_22)
        self.checkBox_5.setObjectName(u"checkBox_5")
        self.checkBox_5.setStyleSheet(u"")

        self.gridLayout_5.addWidget(self.checkBox_5, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_14 = QVBoxLayout()
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.label_106 = QLabel(self.widget_22)
        self.label_106.setObjectName(u"label_106")

        self.verticalLayout_14.addWidget(self.label_106)

        self.label_107 = QLabel(self.widget_22)
        self.label_107.setObjectName(u"label_107")
        self.label_107.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_14.addWidget(self.label_107)


        self.gridLayout_5.addLayout(self.verticalLayout_14, 1, 0, 1, 1)

        self.lineEdit_3 = QLineEdit(self.widget_22)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        self.lineEdit_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_5.addWidget(self.lineEdit_3, 1, 1, 1, 1)

        self.gridLayout_5.setColumnStretch(0, 5)
        self.gridLayout_5.setColumnStretch(1, 2)

        self.verticalLayout_26.addLayout(self.gridLayout_5)


        self.verticalLayout_25.addWidget(self.widget_22, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_8.setWidget(self.scrollAreaWidgetContents_5)

        self.horizontalLayout_12.addWidget(self.scrollArea_8)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_12.addItem(self.horizontalSpacer_10)

        self.horizontalLayout_12.setStretch(0, 1)
        self.horizontalLayout_12.setStretch(1, 5)
        self.horizontalLayout_12.setStretch(2, 1)

        self.horizontalLayout_63.addWidget(self.widget_21)

        self.stackedWidget.addWidget(self.DengLuJiangLi_widget)
        self.PaiHangBangDianZan_widget = QWidget()
        self.PaiHangBangDianZan_widget.setObjectName(u"PaiHangBangDianZan_widget")
        self.horizontalLayout_64 = QHBoxLayout(self.PaiHangBangDianZan_widget)
        self.horizontalLayout_64.setObjectName(u"horizontalLayout_64")
        self.widget_23 = QWidget(self.PaiHangBangDianZan_widget)
        self.widget_23.setObjectName(u"widget_23")
        self.widget_23.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_13 = QHBoxLayout(self.widget_23)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_11)

        self.scrollArea_9 = QScrollArea(self.widget_23)
        self.scrollArea_9.setObjectName(u"scrollArea_9")
        self.scrollArea_9.setMinimumSize(QSize(600, 0))
        self.scrollArea_9.setWidgetResizable(True)
        self.scrollAreaWidgetContents_6 = QWidget()
        self.scrollAreaWidgetContents_6.setObjectName(u"scrollAreaWidgetContents_6")
        self.scrollAreaWidgetContents_6.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_28 = QVBoxLayout(self.scrollAreaWidgetContents_6)
        self.verticalLayout_28.setSpacing(10)
        self.verticalLayout_28.setObjectName(u"verticalLayout_28")
        self.verticalLayout_28.setContentsMargins(10, -1, 10, -1)
        self.widget_24 = QWidget(self.scrollAreaWidgetContents_6)
        self.widget_24.setObjectName(u"widget_24")
        self.widget_24.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_29 = QVBoxLayout(self.widget_24)
        self.verticalLayout_29.setObjectName(u"verticalLayout_29")
        self.label_21 = QLabel(self.widget_24)
        self.label_21.setObjectName(u"label_21")
        self.label_21.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_29.addWidget(self.label_21)

        self.line_9 = QFrame(self.widget_24)
        self.line_9.setObjectName(u"line_9")
        sizePolicy1.setHeightForWidth(self.line_9.sizePolicy().hasHeightForWidth())
        self.line_9.setSizePolicy(sizePolicy1)
        self.line_9.setStyleSheet(u"")
        self.line_9.setLineWidth(0)
        self.line_9.setMidLineWidth(2)
        self.line_9.setFrameShape(QFrame.Shape.HLine)
        self.line_9.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_29.addWidget(self.line_9)

        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_30 = QVBoxLayout()
        self.verticalLayout_30.setObjectName(u"verticalLayout_30")
        self.label_22 = QLabel(self.widget_24)
        self.label_22.setObjectName(u"label_22")

        self.verticalLayout_30.addWidget(self.label_22)

        self.label_23 = QLabel(self.widget_24)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_30.addWidget(self.label_23)


        self.gridLayout_6.addLayout(self.verticalLayout_30, 0, 0, 1, 1)

        self.checkBox_6 = QCheckBox(self.widget_24)
        self.checkBox_6.setObjectName(u"checkBox_6")
        self.checkBox_6.setStyleSheet(u"")

        self.gridLayout_6.addWidget(self.checkBox_6, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_15 = QVBoxLayout()
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.label_108 = QLabel(self.widget_24)
        self.label_108.setObjectName(u"label_108")

        self.verticalLayout_15.addWidget(self.label_108)

        self.label_109 = QLabel(self.widget_24)
        self.label_109.setObjectName(u"label_109")
        self.label_109.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_15.addWidget(self.label_109)


        self.gridLayout_6.addLayout(self.verticalLayout_15, 1, 0, 1, 1)

        self.lineEdit_4 = QLineEdit(self.widget_24)
        self.lineEdit_4.setObjectName(u"lineEdit_4")
        self.lineEdit_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_6.addWidget(self.lineEdit_4, 1, 1, 1, 1)

        self.gridLayout_6.setColumnStretch(0, 5)
        self.gridLayout_6.setColumnStretch(1, 2)

        self.verticalLayout_29.addLayout(self.gridLayout_6)


        self.verticalLayout_28.addWidget(self.widget_24, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_9.setWidget(self.scrollAreaWidgetContents_6)

        self.horizontalLayout_13.addWidget(self.scrollArea_9)

        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_12)

        self.horizontalLayout_13.setStretch(0, 1)
        self.horizontalLayout_13.setStretch(1, 5)
        self.horizontalLayout_13.setStretch(2, 1)

        self.horizontalLayout_64.addWidget(self.widget_23)

        self.stackedWidget.addWidget(self.PaiHangBangDianZan_widget)
        self.MeiYueQianDao_widget = QWidget()
        self.MeiYueQianDao_widget.setObjectName(u"MeiYueQianDao_widget")
        self.horizontalLayout_65 = QHBoxLayout(self.MeiYueQianDao_widget)
        self.horizontalLayout_65.setObjectName(u"horizontalLayout_65")
        self.widget_25 = QWidget(self.MeiYueQianDao_widget)
        self.widget_25.setObjectName(u"widget_25")
        self.widget_25.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_14 = QHBoxLayout(self.widget_25)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_14.addItem(self.horizontalSpacer_13)

        self.scrollArea_10 = QScrollArea(self.widget_25)
        self.scrollArea_10.setObjectName(u"scrollArea_10")
        self.scrollArea_10.setMinimumSize(QSize(600, 0))
        self.scrollArea_10.setWidgetResizable(True)
        self.scrollAreaWidgetContents_7 = QWidget()
        self.scrollAreaWidgetContents_7.setObjectName(u"scrollAreaWidgetContents_7")
        self.scrollAreaWidgetContents_7.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_31 = QVBoxLayout(self.scrollAreaWidgetContents_7)
        self.verticalLayout_31.setSpacing(10)
        self.verticalLayout_31.setObjectName(u"verticalLayout_31")
        self.verticalLayout_31.setContentsMargins(10, -1, 10, -1)
        self.widget_26 = QWidget(self.scrollAreaWidgetContents_7)
        self.widget_26.setObjectName(u"widget_26")
        self.widget_26.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_32 = QVBoxLayout(self.widget_26)
        self.verticalLayout_32.setObjectName(u"verticalLayout_32")
        self.label_24 = QLabel(self.widget_26)
        self.label_24.setObjectName(u"label_24")
        self.label_24.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_32.addWidget(self.label_24)

        self.line_10 = QFrame(self.widget_26)
        self.line_10.setObjectName(u"line_10")
        sizePolicy1.setHeightForWidth(self.line_10.sizePolicy().hasHeightForWidth())
        self.line_10.setSizePolicy(sizePolicy1)
        self.line_10.setStyleSheet(u"")
        self.line_10.setLineWidth(0)
        self.line_10.setMidLineWidth(2)
        self.line_10.setFrameShape(QFrame.Shape.HLine)
        self.line_10.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_32.addWidget(self.line_10)

        self.gridLayout_7 = QGridLayout()
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gridLayout_7.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_33 = QVBoxLayout()
        self.verticalLayout_33.setObjectName(u"verticalLayout_33")
        self.label_25 = QLabel(self.widget_26)
        self.label_25.setObjectName(u"label_25")

        self.verticalLayout_33.addWidget(self.label_25)

        self.label_26 = QLabel(self.widget_26)
        self.label_26.setObjectName(u"label_26")
        self.label_26.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_33.addWidget(self.label_26)


        self.gridLayout_7.addLayout(self.verticalLayout_33, 0, 0, 1, 1)

        self.checkBox_7 = QCheckBox(self.widget_26)
        self.checkBox_7.setObjectName(u"checkBox_7")
        self.checkBox_7.setStyleSheet(u"")

        self.gridLayout_7.addWidget(self.checkBox_7, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_16 = QVBoxLayout()
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.label_110 = QLabel(self.widget_26)
        self.label_110.setObjectName(u"label_110")

        self.verticalLayout_16.addWidget(self.label_110)

        self.label_111 = QLabel(self.widget_26)
        self.label_111.setObjectName(u"label_111")
        self.label_111.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_16.addWidget(self.label_111)


        self.gridLayout_7.addLayout(self.verticalLayout_16, 1, 0, 1, 1)

        self.lineEdit_5 = QLineEdit(self.widget_26)
        self.lineEdit_5.setObjectName(u"lineEdit_5")
        self.lineEdit_5.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_7.addWidget(self.lineEdit_5, 1, 1, 1, 1)

        self.gridLayout_7.setColumnStretch(0, 5)
        self.gridLayout_7.setColumnStretch(1, 2)

        self.verticalLayout_32.addLayout(self.gridLayout_7)


        self.verticalLayout_31.addWidget(self.widget_26, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_10.setWidget(self.scrollAreaWidgetContents_7)

        self.horizontalLayout_14.addWidget(self.scrollArea_10)

        self.horizontalSpacer_14 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_14.addItem(self.horizontalSpacer_14)

        self.horizontalLayout_14.setStretch(0, 1)
        self.horizontalLayout_14.setStretch(1, 5)
        self.horizontalLayout_14.setStretch(2, 1)

        self.horizontalLayout_65.addWidget(self.widget_25)

        self.stackedWidget.addWidget(self.MeiYueQianDao_widget)
        self.GouMaiTiLi_widget = QWidget()
        self.GouMaiTiLi_widget.setObjectName(u"GouMaiTiLi_widget")
        self.horizontalLayout_66 = QHBoxLayout(self.GouMaiTiLi_widget)
        self.horizontalLayout_66.setObjectName(u"horizontalLayout_66")
        self.widget_27 = QWidget(self.GouMaiTiLi_widget)
        self.widget_27.setObjectName(u"widget_27")
        self.widget_27.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_15 = QHBoxLayout(self.widget_27)
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.horizontalSpacer_15 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_15.addItem(self.horizontalSpacer_15)

        self.scrollArea_11 = QScrollArea(self.widget_27)
        self.scrollArea_11.setObjectName(u"scrollArea_11")
        self.scrollArea_11.setMinimumSize(QSize(600, 0))
        self.scrollArea_11.setWidgetResizable(True)
        self.scrollAreaWidgetContents_8 = QWidget()
        self.scrollAreaWidgetContents_8.setObjectName(u"scrollAreaWidgetContents_8")
        self.scrollAreaWidgetContents_8.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_34 = QVBoxLayout(self.scrollAreaWidgetContents_8)
        self.verticalLayout_34.setSpacing(10)
        self.verticalLayout_34.setObjectName(u"verticalLayout_34")
        self.verticalLayout_34.setContentsMargins(10, -1, 10, -1)
        self.widget_28 = QWidget(self.scrollAreaWidgetContents_8)
        self.widget_28.setObjectName(u"widget_28")
        self.widget_28.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_35 = QVBoxLayout(self.widget_28)
        self.verticalLayout_35.setObjectName(u"verticalLayout_35")
        self.label_27 = QLabel(self.widget_28)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_35.addWidget(self.label_27)

        self.line_11 = QFrame(self.widget_28)
        self.line_11.setObjectName(u"line_11")
        sizePolicy1.setHeightForWidth(self.line_11.sizePolicy().hasHeightForWidth())
        self.line_11.setSizePolicy(sizePolicy1)
        self.line_11.setStyleSheet(u"")
        self.line_11.setLineWidth(0)
        self.line_11.setMidLineWidth(2)
        self.line_11.setFrameShape(QFrame.Shape.HLine)
        self.line_11.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_35.addWidget(self.line_11)

        self.gridLayout_8 = QGridLayout()
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.gridLayout_8.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_36 = QVBoxLayout()
        self.verticalLayout_36.setObjectName(u"verticalLayout_36")
        self.label_28 = QLabel(self.widget_28)
        self.label_28.setObjectName(u"label_28")

        self.verticalLayout_36.addWidget(self.label_28)

        self.label_29 = QLabel(self.widget_28)
        self.label_29.setObjectName(u"label_29")
        self.label_29.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_36.addWidget(self.label_29)


        self.gridLayout_8.addLayout(self.verticalLayout_36, 0, 0, 1, 1)

        self.checkBox_8 = QCheckBox(self.widget_28)
        self.checkBox_8.setObjectName(u"checkBox_8")
        self.checkBox_8.setStyleSheet(u"")

        self.gridLayout_8.addWidget(self.checkBox_8, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_17 = QVBoxLayout()
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.label_112 = QLabel(self.widget_28)
        self.label_112.setObjectName(u"label_112")

        self.verticalLayout_17.addWidget(self.label_112)

        self.label_113 = QLabel(self.widget_28)
        self.label_113.setObjectName(u"label_113")
        self.label_113.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_17.addWidget(self.label_113)


        self.gridLayout_8.addLayout(self.verticalLayout_17, 1, 0, 1, 1)

        self.lineEdit_6 = QLineEdit(self.widget_28)
        self.lineEdit_6.setObjectName(u"lineEdit_6")
        self.lineEdit_6.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_8.addWidget(self.lineEdit_6, 1, 1, 1, 1)

        self.gridLayout_8.setColumnStretch(0, 5)
        self.gridLayout_8.setColumnStretch(1, 2)

        self.verticalLayout_35.addLayout(self.gridLayout_8)


        self.verticalLayout_34.addWidget(self.widget_28, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_11.setWidget(self.scrollAreaWidgetContents_8)

        self.horizontalLayout_15.addWidget(self.scrollArea_11)

        self.horizontalSpacer_16 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_15.addItem(self.horizontalSpacer_16)

        self.horizontalLayout_15.setStretch(0, 1)
        self.horizontalLayout_15.setStretch(1, 5)
        self.horizontalLayout_15.setStretch(2, 1)

        self.horizontalLayout_66.addWidget(self.widget_27)

        self.stackedWidget.addWidget(self.GouMaiTiLi_widget)
        self.JinBiZhaoCai_widget = QWidget()
        self.JinBiZhaoCai_widget.setObjectName(u"JinBiZhaoCai_widget")
        self.horizontalLayout_67 = QHBoxLayout(self.JinBiZhaoCai_widget)
        self.horizontalLayout_67.setObjectName(u"horizontalLayout_67")
        self.widget_29 = QWidget(self.JinBiZhaoCai_widget)
        self.widget_29.setObjectName(u"widget_29")
        self.widget_29.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_16 = QHBoxLayout(self.widget_29)
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.horizontalSpacer_17 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_17)

        self.scrollArea_12 = QScrollArea(self.widget_29)
        self.scrollArea_12.setObjectName(u"scrollArea_12")
        self.scrollArea_12.setMinimumSize(QSize(600, 0))
        self.scrollArea_12.setWidgetResizable(True)
        self.scrollAreaWidgetContents_9 = QWidget()
        self.scrollAreaWidgetContents_9.setObjectName(u"scrollAreaWidgetContents_9")
        self.scrollAreaWidgetContents_9.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_37 = QVBoxLayout(self.scrollAreaWidgetContents_9)
        self.verticalLayout_37.setSpacing(10)
        self.verticalLayout_37.setObjectName(u"verticalLayout_37")
        self.verticalLayout_37.setContentsMargins(10, -1, 10, -1)
        self.widget_30 = QWidget(self.scrollAreaWidgetContents_9)
        self.widget_30.setObjectName(u"widget_30")
        self.widget_30.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_38 = QVBoxLayout(self.widget_30)
        self.verticalLayout_38.setObjectName(u"verticalLayout_38")
        self.label_30 = QLabel(self.widget_30)
        self.label_30.setObjectName(u"label_30")
        self.label_30.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_38.addWidget(self.label_30)

        self.line_12 = QFrame(self.widget_30)
        self.line_12.setObjectName(u"line_12")
        sizePolicy1.setHeightForWidth(self.line_12.sizePolicy().hasHeightForWidth())
        self.line_12.setSizePolicy(sizePolicy1)
        self.line_12.setStyleSheet(u"")
        self.line_12.setLineWidth(0)
        self.line_12.setMidLineWidth(2)
        self.line_12.setFrameShape(QFrame.Shape.HLine)
        self.line_12.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_38.addWidget(self.line_12)

        self.gridLayout_9 = QGridLayout()
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.gridLayout_9.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_39 = QVBoxLayout()
        self.verticalLayout_39.setObjectName(u"verticalLayout_39")
        self.label_31 = QLabel(self.widget_30)
        self.label_31.setObjectName(u"label_31")

        self.verticalLayout_39.addWidget(self.label_31)

        self.label_32 = QLabel(self.widget_30)
        self.label_32.setObjectName(u"label_32")
        self.label_32.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_39.addWidget(self.label_32)


        self.gridLayout_9.addLayout(self.verticalLayout_39, 0, 0, 1, 1)

        self.checkBox_9 = QCheckBox(self.widget_30)
        self.checkBox_9.setObjectName(u"checkBox_9")
        self.checkBox_9.setStyleSheet(u"")

        self.gridLayout_9.addWidget(self.checkBox_9, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_18 = QVBoxLayout()
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.label_114 = QLabel(self.widget_30)
        self.label_114.setObjectName(u"label_114")

        self.verticalLayout_18.addWidget(self.label_114)

        self.label_115 = QLabel(self.widget_30)
        self.label_115.setObjectName(u"label_115")
        self.label_115.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_18.addWidget(self.label_115)


        self.gridLayout_9.addLayout(self.verticalLayout_18, 1, 0, 1, 1)

        self.lineEdit_7 = QLineEdit(self.widget_30)
        self.lineEdit_7.setObjectName(u"lineEdit_7")
        self.lineEdit_7.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_9.addWidget(self.lineEdit_7, 1, 1, 1, 1)

        self.gridLayout_9.setColumnStretch(0, 5)
        self.gridLayout_9.setColumnStretch(1, 2)

        self.verticalLayout_38.addLayout(self.gridLayout_9)


        self.verticalLayout_37.addWidget(self.widget_30, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_12.setWidget(self.scrollAreaWidgetContents_9)

        self.horizontalLayout_16.addWidget(self.scrollArea_12)

        self.horizontalSpacer_18 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_18)

        self.horizontalLayout_16.setStretch(0, 1)
        self.horizontalLayout_16.setStretch(1, 5)
        self.horizontalLayout_16.setStretch(2, 1)

        self.horizontalLayout_67.addWidget(self.widget_29)

        self.stackedWidget.addWidget(self.JinBiZhaoCai_widget)
        self.XiaoDuiTuXi_widget = QWidget()
        self.XiaoDuiTuXi_widget.setObjectName(u"XiaoDuiTuXi_widget")
        self.horizontalLayout_68 = QHBoxLayout(self.XiaoDuiTuXi_widget)
        self.horizontalLayout_68.setObjectName(u"horizontalLayout_68")
        self.widget_31 = QWidget(self.XiaoDuiTuXi_widget)
        self.widget_31.setObjectName(u"widget_31")
        self.widget_31.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_17 = QHBoxLayout(self.widget_31)
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.horizontalSpacer_19 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_17.addItem(self.horizontalSpacer_19)

        self.scrollArea_13 = QScrollArea(self.widget_31)
        self.scrollArea_13.setObjectName(u"scrollArea_13")
        self.scrollArea_13.setMinimumSize(QSize(600, 0))
        self.scrollArea_13.setWidgetResizable(True)
        self.scrollAreaWidgetContents_10 = QWidget()
        self.scrollAreaWidgetContents_10.setObjectName(u"scrollAreaWidgetContents_10")
        self.scrollAreaWidgetContents_10.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_40 = QVBoxLayout(self.scrollAreaWidgetContents_10)
        self.verticalLayout_40.setSpacing(10)
        self.verticalLayout_40.setObjectName(u"verticalLayout_40")
        self.verticalLayout_40.setContentsMargins(10, -1, 10, -1)
        self.widget_32 = QWidget(self.scrollAreaWidgetContents_10)
        self.widget_32.setObjectName(u"widget_32")
        self.widget_32.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_41 = QVBoxLayout(self.widget_32)
        self.verticalLayout_41.setObjectName(u"verticalLayout_41")
        self.label_33 = QLabel(self.widget_32)
        self.label_33.setObjectName(u"label_33")
        self.label_33.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_41.addWidget(self.label_33)

        self.line_13 = QFrame(self.widget_32)
        self.line_13.setObjectName(u"line_13")
        sizePolicy1.setHeightForWidth(self.line_13.sizePolicy().hasHeightForWidth())
        self.line_13.setSizePolicy(sizePolicy1)
        self.line_13.setStyleSheet(u"")
        self.line_13.setLineWidth(0)
        self.line_13.setMidLineWidth(2)
        self.line_13.setFrameShape(QFrame.Shape.HLine)
        self.line_13.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_41.addWidget(self.line_13)

        self.gridLayout_10 = QGridLayout()
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.gridLayout_10.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_42 = QVBoxLayout()
        self.verticalLayout_42.setObjectName(u"verticalLayout_42")
        self.label_34 = QLabel(self.widget_32)
        self.label_34.setObjectName(u"label_34")

        self.verticalLayout_42.addWidget(self.label_34)

        self.label_35 = QLabel(self.widget_32)
        self.label_35.setObjectName(u"label_35")
        self.label_35.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_42.addWidget(self.label_35)


        self.gridLayout_10.addLayout(self.verticalLayout_42, 0, 0, 1, 1)

        self.checkBox_10 = QCheckBox(self.widget_32)
        self.checkBox_10.setObjectName(u"checkBox_10")
        self.checkBox_10.setStyleSheet(u"")

        self.gridLayout_10.addWidget(self.checkBox_10, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_43 = QVBoxLayout()
        self.verticalLayout_43.setObjectName(u"verticalLayout_43")
        self.label_116 = QLabel(self.widget_32)
        self.label_116.setObjectName(u"label_116")

        self.verticalLayout_43.addWidget(self.label_116)

        self.label_117 = QLabel(self.widget_32)
        self.label_117.setObjectName(u"label_117")
        self.label_117.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_43.addWidget(self.label_117)


        self.gridLayout_10.addLayout(self.verticalLayout_43, 1, 0, 1, 1)

        self.lineEdit_8 = QLineEdit(self.widget_32)
        self.lineEdit_8.setObjectName(u"lineEdit_8")
        self.lineEdit_8.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_10.addWidget(self.lineEdit_8, 1, 1, 1, 1)

        self.gridLayout_10.setColumnStretch(0, 5)
        self.gridLayout_10.setColumnStretch(1, 2)

        self.verticalLayout_41.addLayout(self.gridLayout_10)


        self.verticalLayout_40.addWidget(self.widget_32, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_13.setWidget(self.scrollAreaWidgetContents_10)

        self.horizontalLayout_17.addWidget(self.scrollArea_13)

        self.horizontalSpacer_20 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_17.addItem(self.horizontalSpacer_20)

        self.horizontalLayout_17.setStretch(0, 1)
        self.horizontalLayout_17.setStretch(1, 5)
        self.horizontalLayout_17.setStretch(2, 1)

        self.horizontalLayout_68.addWidget(self.widget_31)

        self.stackedWidget.addWidget(self.XiaoDuiTuXi_widget)
        self.ZuZhiQiFu_widget = QWidget()
        self.ZuZhiQiFu_widget.setObjectName(u"ZuZhiQiFu_widget")
        self.horizontalLayout_6 = QHBoxLayout(self.ZuZhiQiFu_widget)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.widget_33 = QWidget(self.ZuZhiQiFu_widget)
        self.widget_33.setObjectName(u"widget_33")
        self.widget_33.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_18 = QHBoxLayout(self.widget_33)
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.horizontalSpacer_21 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer_21)

        self.scrollArea_14 = QScrollArea(self.widget_33)
        self.scrollArea_14.setObjectName(u"scrollArea_14")
        self.scrollArea_14.setMinimumSize(QSize(600, 0))
        self.scrollArea_14.setWidgetResizable(True)
        self.scrollAreaWidgetContents_11 = QWidget()
        self.scrollAreaWidgetContents_11.setObjectName(u"scrollAreaWidgetContents_11")
        self.scrollAreaWidgetContents_11.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_44 = QVBoxLayout(self.scrollAreaWidgetContents_11)
        self.verticalLayout_44.setSpacing(10)
        self.verticalLayout_44.setObjectName(u"verticalLayout_44")
        self.verticalLayout_44.setContentsMargins(10, -1, 10, -1)
        self.widget_34 = QWidget(self.scrollAreaWidgetContents_11)
        self.widget_34.setObjectName(u"widget_34")
        self.widget_34.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_45 = QVBoxLayout(self.widget_34)
        self.verticalLayout_45.setObjectName(u"verticalLayout_45")
        self.label_36 = QLabel(self.widget_34)
        self.label_36.setObjectName(u"label_36")
        self.label_36.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_45.addWidget(self.label_36)

        self.line_14 = QFrame(self.widget_34)
        self.line_14.setObjectName(u"line_14")
        sizePolicy1.setHeightForWidth(self.line_14.sizePolicy().hasHeightForWidth())
        self.line_14.setSizePolicy(sizePolicy1)
        self.line_14.setStyleSheet(u"")
        self.line_14.setLineWidth(0)
        self.line_14.setMidLineWidth(2)
        self.line_14.setFrameShape(QFrame.Shape.HLine)
        self.line_14.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_45.addWidget(self.line_14)

        self.gridLayout_11 = QGridLayout()
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.gridLayout_11.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_46 = QVBoxLayout()
        self.verticalLayout_46.setObjectName(u"verticalLayout_46")
        self.label_37 = QLabel(self.widget_34)
        self.label_37.setObjectName(u"label_37")

        self.verticalLayout_46.addWidget(self.label_37)

        self.label_38 = QLabel(self.widget_34)
        self.label_38.setObjectName(u"label_38")
        self.label_38.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_46.addWidget(self.label_38)


        self.gridLayout_11.addLayout(self.verticalLayout_46, 0, 0, 1, 1)

        self.checkBox_11 = QCheckBox(self.widget_34)
        self.checkBox_11.setObjectName(u"checkBox_11")
        self.checkBox_11.setStyleSheet(u"")

        self.gridLayout_11.addWidget(self.checkBox_11, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_47 = QVBoxLayout()
        self.verticalLayout_47.setObjectName(u"verticalLayout_47")
        self.label_118 = QLabel(self.widget_34)
        self.label_118.setObjectName(u"label_118")

        self.verticalLayout_47.addWidget(self.label_118)

        self.label_119 = QLabel(self.widget_34)
        self.label_119.setObjectName(u"label_119")
        self.label_119.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_47.addWidget(self.label_119)


        self.gridLayout_11.addLayout(self.verticalLayout_47, 1, 0, 1, 1)

        self.lineEdit_9 = QLineEdit(self.widget_34)
        self.lineEdit_9.setObjectName(u"lineEdit_9")
        self.lineEdit_9.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_11.addWidget(self.lineEdit_9, 1, 1, 1, 1)

        self.gridLayout_11.setColumnStretch(0, 5)
        self.gridLayout_11.setColumnStretch(1, 2)

        self.verticalLayout_45.addLayout(self.gridLayout_11)


        self.verticalLayout_44.addWidget(self.widget_34, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_14.setWidget(self.scrollAreaWidgetContents_11)

        self.horizontalLayout_18.addWidget(self.scrollArea_14)

        self.horizontalSpacer_22 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer_22)

        self.horizontalLayout_18.setStretch(0, 1)
        self.horizontalLayout_18.setStretch(1, 5)
        self.horizontalLayout_18.setStretch(2, 1)

        self.horizontalLayout_6.addWidget(self.widget_33)

        self.stackedWidget.addWidget(self.ZuZhiQiFu_widget)
        self.HaoYouTiLi_widget = QWidget()
        self.HaoYouTiLi_widget.setObjectName(u"HaoYouTiLi_widget")
        self.horizontalLayout_7 = QHBoxLayout(self.HaoYouTiLi_widget)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.widget_35 = QWidget(self.HaoYouTiLi_widget)
        self.widget_35.setObjectName(u"widget_35")
        self.widget_35.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_19 = QHBoxLayout(self.widget_35)
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.horizontalSpacer_23 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_19.addItem(self.horizontalSpacer_23)

        self.scrollArea_15 = QScrollArea(self.widget_35)
        self.scrollArea_15.setObjectName(u"scrollArea_15")
        self.scrollArea_15.setMinimumSize(QSize(600, 0))
        self.scrollArea_15.setWidgetResizable(True)
        self.scrollAreaWidgetContents_12 = QWidget()
        self.scrollAreaWidgetContents_12.setObjectName(u"scrollAreaWidgetContents_12")
        self.scrollAreaWidgetContents_12.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_48 = QVBoxLayout(self.scrollAreaWidgetContents_12)
        self.verticalLayout_48.setSpacing(10)
        self.verticalLayout_48.setObjectName(u"verticalLayout_48")
        self.verticalLayout_48.setContentsMargins(10, -1, 10, -1)
        self.widget_36 = QWidget(self.scrollAreaWidgetContents_12)
        self.widget_36.setObjectName(u"widget_36")
        self.widget_36.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_49 = QVBoxLayout(self.widget_36)
        self.verticalLayout_49.setObjectName(u"verticalLayout_49")
        self.label_39 = QLabel(self.widget_36)
        self.label_39.setObjectName(u"label_39")
        self.label_39.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_49.addWidget(self.label_39)

        self.line_15 = QFrame(self.widget_36)
        self.line_15.setObjectName(u"line_15")
        sizePolicy1.setHeightForWidth(self.line_15.sizePolicy().hasHeightForWidth())
        self.line_15.setSizePolicy(sizePolicy1)
        self.line_15.setStyleSheet(u"")
        self.line_15.setLineWidth(0)
        self.line_15.setMidLineWidth(2)
        self.line_15.setFrameShape(QFrame.Shape.HLine)
        self.line_15.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_49.addWidget(self.line_15)

        self.gridLayout_12 = QGridLayout()
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.gridLayout_12.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_50 = QVBoxLayout()
        self.verticalLayout_50.setObjectName(u"verticalLayout_50")
        self.label_40 = QLabel(self.widget_36)
        self.label_40.setObjectName(u"label_40")

        self.verticalLayout_50.addWidget(self.label_40)

        self.label_41 = QLabel(self.widget_36)
        self.label_41.setObjectName(u"label_41")
        self.label_41.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_50.addWidget(self.label_41)


        self.gridLayout_12.addLayout(self.verticalLayout_50, 0, 0, 1, 1)

        self.checkBox_12 = QCheckBox(self.widget_36)
        self.checkBox_12.setObjectName(u"checkBox_12")
        self.checkBox_12.setStyleSheet(u"")

        self.gridLayout_12.addWidget(self.checkBox_12, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_51 = QVBoxLayout()
        self.verticalLayout_51.setObjectName(u"verticalLayout_51")
        self.label_120 = QLabel(self.widget_36)
        self.label_120.setObjectName(u"label_120")

        self.verticalLayout_51.addWidget(self.label_120)

        self.label_121 = QLabel(self.widget_36)
        self.label_121.setObjectName(u"label_121")
        self.label_121.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_51.addWidget(self.label_121)


        self.gridLayout_12.addLayout(self.verticalLayout_51, 1, 0, 1, 1)

        self.lineEdit_10 = QLineEdit(self.widget_36)
        self.lineEdit_10.setObjectName(u"lineEdit_10")
        self.lineEdit_10.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_12.addWidget(self.lineEdit_10, 1, 1, 1, 1)

        self.gridLayout_12.setColumnStretch(0, 5)
        self.gridLayout_12.setColumnStretch(1, 2)

        self.verticalLayout_49.addLayout(self.gridLayout_12)


        self.verticalLayout_48.addWidget(self.widget_36, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_15.setWidget(self.scrollAreaWidgetContents_12)

        self.horizontalLayout_19.addWidget(self.scrollArea_15)

        self.horizontalSpacer_24 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_19.addItem(self.horizontalSpacer_24)

        self.horizontalLayout_19.setStretch(0, 1)
        self.horizontalLayout_19.setStretch(1, 5)
        self.horizontalLayout_19.setStretch(2, 1)

        self.horizontalLayout_7.addWidget(self.widget_35)

        self.stackedWidget.addWidget(self.HaoYouTiLi_widget)
        self.PuTongRenZheZhaoMu_widget = QWidget()
        self.PuTongRenZheZhaoMu_widget.setObjectName(u"PuTongRenZheZhaoMu_widget")
        self.horizontalLayout_8 = QHBoxLayout(self.PuTongRenZheZhaoMu_widget)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.widget_37 = QWidget(self.PuTongRenZheZhaoMu_widget)
        self.widget_37.setObjectName(u"widget_37")
        self.widget_37.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_20 = QHBoxLayout(self.widget_37)
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.horizontalSpacer_25 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_20.addItem(self.horizontalSpacer_25)

        self.scrollArea_16 = QScrollArea(self.widget_37)
        self.scrollArea_16.setObjectName(u"scrollArea_16")
        self.scrollArea_16.setMinimumSize(QSize(600, 0))
        self.scrollArea_16.setWidgetResizable(True)
        self.scrollAreaWidgetContents_13 = QWidget()
        self.scrollAreaWidgetContents_13.setObjectName(u"scrollAreaWidgetContents_13")
        self.scrollAreaWidgetContents_13.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_52 = QVBoxLayout(self.scrollAreaWidgetContents_13)
        self.verticalLayout_52.setSpacing(10)
        self.verticalLayout_52.setObjectName(u"verticalLayout_52")
        self.verticalLayout_52.setContentsMargins(10, -1, 10, -1)
        self.widget_38 = QWidget(self.scrollAreaWidgetContents_13)
        self.widget_38.setObjectName(u"widget_38")
        self.widget_38.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_53 = QVBoxLayout(self.widget_38)
        self.verticalLayout_53.setObjectName(u"verticalLayout_53")
        self.label_42 = QLabel(self.widget_38)
        self.label_42.setObjectName(u"label_42")
        self.label_42.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_53.addWidget(self.label_42)

        self.line_16 = QFrame(self.widget_38)
        self.line_16.setObjectName(u"line_16")
        sizePolicy1.setHeightForWidth(self.line_16.sizePolicy().hasHeightForWidth())
        self.line_16.setSizePolicy(sizePolicy1)
        self.line_16.setStyleSheet(u"")
        self.line_16.setLineWidth(0)
        self.line_16.setMidLineWidth(2)
        self.line_16.setFrameShape(QFrame.Shape.HLine)
        self.line_16.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_53.addWidget(self.line_16)

        self.gridLayout_13 = QGridLayout()
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.gridLayout_13.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_54 = QVBoxLayout()
        self.verticalLayout_54.setObjectName(u"verticalLayout_54")
        self.label_43 = QLabel(self.widget_38)
        self.label_43.setObjectName(u"label_43")

        self.verticalLayout_54.addWidget(self.label_43)

        self.label_44 = QLabel(self.widget_38)
        self.label_44.setObjectName(u"label_44")
        self.label_44.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_54.addWidget(self.label_44)


        self.gridLayout_13.addLayout(self.verticalLayout_54, 0, 0, 1, 1)

        self.checkBox_13 = QCheckBox(self.widget_38)
        self.checkBox_13.setObjectName(u"checkBox_13")
        self.checkBox_13.setStyleSheet(u"")

        self.gridLayout_13.addWidget(self.checkBox_13, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_55 = QVBoxLayout()
        self.verticalLayout_55.setObjectName(u"verticalLayout_55")
        self.label_122 = QLabel(self.widget_38)
        self.label_122.setObjectName(u"label_122")

        self.verticalLayout_55.addWidget(self.label_122)

        self.label_123 = QLabel(self.widget_38)
        self.label_123.setObjectName(u"label_123")
        self.label_123.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_55.addWidget(self.label_123)


        self.gridLayout_13.addLayout(self.verticalLayout_55, 1, 0, 1, 1)

        self.lineEdit_11 = QLineEdit(self.widget_38)
        self.lineEdit_11.setObjectName(u"lineEdit_11")
        self.lineEdit_11.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_13.addWidget(self.lineEdit_11, 1, 1, 1, 1)

        self.gridLayout_13.setColumnStretch(0, 5)
        self.gridLayout_13.setColumnStretch(1, 2)

        self.verticalLayout_53.addLayout(self.gridLayout_13)


        self.verticalLayout_52.addWidget(self.widget_38, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_16.setWidget(self.scrollAreaWidgetContents_13)

        self.horizontalLayout_20.addWidget(self.scrollArea_16)

        self.horizontalSpacer_26 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_20.addItem(self.horizontalSpacer_26)

        self.horizontalLayout_20.setStretch(0, 1)
        self.horizontalLayout_20.setStretch(1, 5)
        self.horizontalLayout_20.setStretch(2, 1)

        self.horizontalLayout_8.addWidget(self.widget_37)

        self.stackedWidget.addWidget(self.PuTongRenZheZhaoMu_widget)
        self.MeiRiFenXiang_widget = QWidget()
        self.MeiRiFenXiang_widget.setObjectName(u"MeiRiFenXiang_widget")
        self.horizontalLayout_42 = QHBoxLayout(self.MeiRiFenXiang_widget)
        self.horizontalLayout_42.setObjectName(u"horizontalLayout_42")
        self.widget_51 = QWidget(self.MeiRiFenXiang_widget)
        self.widget_51.setObjectName(u"widget_51")
        self.widget_51.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_27 = QHBoxLayout(self.widget_51)
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.horizontalSpacer_39 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_27.addItem(self.horizontalSpacer_39)

        self.scrollArea_23 = QScrollArea(self.widget_51)
        self.scrollArea_23.setObjectName(u"scrollArea_23")
        self.scrollArea_23.setMinimumSize(QSize(600, 0))
        self.scrollArea_23.setWidgetResizable(True)
        self.scrollAreaWidgetContents_20 = QWidget()
        self.scrollAreaWidgetContents_20.setObjectName(u"scrollAreaWidgetContents_20")
        self.scrollAreaWidgetContents_20.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_80 = QVBoxLayout(self.scrollAreaWidgetContents_20)
        self.verticalLayout_80.setSpacing(10)
        self.verticalLayout_80.setObjectName(u"verticalLayout_80")
        self.verticalLayout_80.setContentsMargins(10, -1, 10, -1)
        self.widget_52 = QWidget(self.scrollAreaWidgetContents_20)
        self.widget_52.setObjectName(u"widget_52")
        self.widget_52.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_81 = QVBoxLayout(self.widget_52)
        self.verticalLayout_81.setObjectName(u"verticalLayout_81")
        self.label_63 = QLabel(self.widget_52)
        self.label_63.setObjectName(u"label_63")
        self.label_63.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_81.addWidget(self.label_63)

        self.line_23 = QFrame(self.widget_52)
        self.line_23.setObjectName(u"line_23")
        sizePolicy1.setHeightForWidth(self.line_23.sizePolicy().hasHeightForWidth())
        self.line_23.setSizePolicy(sizePolicy1)
        self.line_23.setStyleSheet(u"")
        self.line_23.setLineWidth(0)
        self.line_23.setMidLineWidth(2)
        self.line_23.setFrameShape(QFrame.Shape.HLine)
        self.line_23.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_81.addWidget(self.line_23)

        self.gridLayout_20 = QGridLayout()
        self.gridLayout_20.setObjectName(u"gridLayout_20")
        self.gridLayout_20.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_82 = QVBoxLayout()
        self.verticalLayout_82.setObjectName(u"verticalLayout_82")
        self.label_64 = QLabel(self.widget_52)
        self.label_64.setObjectName(u"label_64")

        self.verticalLayout_82.addWidget(self.label_64)

        self.label_65 = QLabel(self.widget_52)
        self.label_65.setObjectName(u"label_65")
        self.label_65.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_82.addWidget(self.label_65)


        self.gridLayout_20.addLayout(self.verticalLayout_82, 0, 0, 1, 1)

        self.checkBox_20 = QCheckBox(self.widget_52)
        self.checkBox_20.setObjectName(u"checkBox_20")
        self.checkBox_20.setStyleSheet(u"")

        self.gridLayout_20.addWidget(self.checkBox_20, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_83 = QVBoxLayout()
        self.verticalLayout_83.setObjectName(u"verticalLayout_83")
        self.label_136 = QLabel(self.widget_52)
        self.label_136.setObjectName(u"label_136")

        self.verticalLayout_83.addWidget(self.label_136)

        self.label_137 = QLabel(self.widget_52)
        self.label_137.setObjectName(u"label_137")
        self.label_137.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_83.addWidget(self.label_137)


        self.gridLayout_20.addLayout(self.verticalLayout_83, 1, 0, 1, 1)

        self.lineEdit_18 = QLineEdit(self.widget_52)
        self.lineEdit_18.setObjectName(u"lineEdit_18")
        self.lineEdit_18.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_20.addWidget(self.lineEdit_18, 1, 1, 1, 1)

        self.gridLayout_20.setColumnStretch(0, 5)
        self.gridLayout_20.setColumnStretch(1, 2)

        self.verticalLayout_81.addLayout(self.gridLayout_20)


        self.verticalLayout_80.addWidget(self.widget_52, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_23.setWidget(self.scrollAreaWidgetContents_20)

        self.horizontalLayout_27.addWidget(self.scrollArea_23)

        self.horizontalSpacer_40 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_27.addItem(self.horizontalSpacer_40)

        self.horizontalLayout_27.setStretch(0, 1)
        self.horizontalLayout_27.setStretch(1, 5)
        self.horizontalLayout_27.setStretch(2, 1)

        self.horizontalLayout_42.addWidget(self.widget_51)

        self.stackedWidget.addWidget(self.MeiRiFenXiang_widget)
        self.FengRaoZhiJian_widget = QWidget()
        self.FengRaoZhiJian_widget.setObjectName(u"FengRaoZhiJian_widget")
        self.horizontalLayout_43 = QHBoxLayout(self.FengRaoZhiJian_widget)
        self.horizontalLayout_43.setObjectName(u"horizontalLayout_43")
        self.widget_39 = QWidget(self.FengRaoZhiJian_widget)
        self.widget_39.setObjectName(u"widget_39")
        self.widget_39.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_21 = QHBoxLayout(self.widget_39)
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.horizontalSpacer_27 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_21.addItem(self.horizontalSpacer_27)

        self.scrollArea_17 = QScrollArea(self.widget_39)
        self.scrollArea_17.setObjectName(u"scrollArea_17")
        self.scrollArea_17.setMinimumSize(QSize(600, 0))
        self.scrollArea_17.setWidgetResizable(True)
        self.scrollAreaWidgetContents_14 = QWidget()
        self.scrollAreaWidgetContents_14.setObjectName(u"scrollAreaWidgetContents_14")
        self.scrollAreaWidgetContents_14.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_56 = QVBoxLayout(self.scrollAreaWidgetContents_14)
        self.verticalLayout_56.setSpacing(10)
        self.verticalLayout_56.setObjectName(u"verticalLayout_56")
        self.verticalLayout_56.setContentsMargins(10, -1, 10, -1)
        self.widget_40 = QWidget(self.scrollAreaWidgetContents_14)
        self.widget_40.setObjectName(u"widget_40")
        self.widget_40.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_57 = QVBoxLayout(self.widget_40)
        self.verticalLayout_57.setObjectName(u"verticalLayout_57")
        self.label_45 = QLabel(self.widget_40)
        self.label_45.setObjectName(u"label_45")
        self.label_45.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_57.addWidget(self.label_45)

        self.line_17 = QFrame(self.widget_40)
        self.line_17.setObjectName(u"line_17")
        sizePolicy1.setHeightForWidth(self.line_17.sizePolicy().hasHeightForWidth())
        self.line_17.setSizePolicy(sizePolicy1)
        self.line_17.setStyleSheet(u"")
        self.line_17.setLineWidth(0)
        self.line_17.setMidLineWidth(2)
        self.line_17.setFrameShape(QFrame.Shape.HLine)
        self.line_17.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_57.addWidget(self.line_17)

        self.gridLayout_14 = QGridLayout()
        self.gridLayout_14.setObjectName(u"gridLayout_14")
        self.gridLayout_14.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_58 = QVBoxLayout()
        self.verticalLayout_58.setObjectName(u"verticalLayout_58")
        self.label_46 = QLabel(self.widget_40)
        self.label_46.setObjectName(u"label_46")

        self.verticalLayout_58.addWidget(self.label_46)

        self.label_47 = QLabel(self.widget_40)
        self.label_47.setObjectName(u"label_47")
        self.label_47.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_58.addWidget(self.label_47)


        self.gridLayout_14.addLayout(self.verticalLayout_58, 0, 0, 1, 1)

        self.checkBox_14 = QCheckBox(self.widget_40)
        self.checkBox_14.setObjectName(u"checkBox_14")
        self.checkBox_14.setStyleSheet(u"")

        self.gridLayout_14.addWidget(self.checkBox_14, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_59 = QVBoxLayout()
        self.verticalLayout_59.setObjectName(u"verticalLayout_59")
        self.label_124 = QLabel(self.widget_40)
        self.label_124.setObjectName(u"label_124")

        self.verticalLayout_59.addWidget(self.label_124)

        self.label_125 = QLabel(self.widget_40)
        self.label_125.setObjectName(u"label_125")
        self.label_125.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_59.addWidget(self.label_125)


        self.gridLayout_14.addLayout(self.verticalLayout_59, 1, 0, 1, 1)

        self.lineEdit_12 = QLineEdit(self.widget_40)
        self.lineEdit_12.setObjectName(u"lineEdit_12")
        self.lineEdit_12.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_14.addWidget(self.lineEdit_12, 1, 1, 1, 1)

        self.gridLayout_14.setColumnStretch(0, 5)
        self.gridLayout_14.setColumnStretch(1, 2)

        self.verticalLayout_57.addLayout(self.gridLayout_14)


        self.verticalLayout_56.addWidget(self.widget_40, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_17.setWidget(self.scrollAreaWidgetContents_14)

        self.horizontalLayout_21.addWidget(self.scrollArea_17)

        self.horizontalSpacer_28 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_21.addItem(self.horizontalSpacer_28)

        self.horizontalLayout_21.setStretch(0, 1)
        self.horizontalLayout_21.setStretch(1, 5)
        self.horizontalLayout_21.setStretch(2, 1)

        self.horizontalLayout_43.addWidget(self.widget_39)

        self.stackedWidget.addWidget(self.FengRaoZhiJian_widget)
        self.RenWuJiHuiSuo_widget = QWidget()
        self.RenWuJiHuiSuo_widget.setObjectName(u"RenWuJiHuiSuo_widget")
        self.horizontalLayout_44 = QHBoxLayout(self.RenWuJiHuiSuo_widget)
        self.horizontalLayout_44.setObjectName(u"horizontalLayout_44")
        self.widget_67 = QWidget(self.RenWuJiHuiSuo_widget)
        self.widget_67.setObjectName(u"widget_67")
        self.widget_67.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_35 = QHBoxLayout(self.widget_67)
        self.horizontalLayout_35.setObjectName(u"horizontalLayout_35")
        self.horizontalSpacer_55 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_35.addItem(self.horizontalSpacer_55)

        self.scrollArea_31 = QScrollArea(self.widget_67)
        self.scrollArea_31.setObjectName(u"scrollArea_31")
        self.scrollArea_31.setMinimumSize(QSize(600, 0))
        self.scrollArea_31.setWidgetResizable(True)
        self.scrollAreaWidgetContents_28 = QWidget()
        self.scrollAreaWidgetContents_28.setObjectName(u"scrollAreaWidgetContents_28")
        self.scrollAreaWidgetContents_28.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_112 = QVBoxLayout(self.scrollAreaWidgetContents_28)
        self.verticalLayout_112.setSpacing(10)
        self.verticalLayout_112.setObjectName(u"verticalLayout_112")
        self.verticalLayout_112.setContentsMargins(10, -1, 10, -1)
        self.widget_68 = QWidget(self.scrollAreaWidgetContents_28)
        self.widget_68.setObjectName(u"widget_68")
        self.widget_68.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_113 = QVBoxLayout(self.widget_68)
        self.verticalLayout_113.setObjectName(u"verticalLayout_113")
        self.label_87 = QLabel(self.widget_68)
        self.label_87.setObjectName(u"label_87")
        self.label_87.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_113.addWidget(self.label_87)

        self.line_31 = QFrame(self.widget_68)
        self.line_31.setObjectName(u"line_31")
        sizePolicy1.setHeightForWidth(self.line_31.sizePolicy().hasHeightForWidth())
        self.line_31.setSizePolicy(sizePolicy1)
        self.line_31.setStyleSheet(u"")
        self.line_31.setLineWidth(0)
        self.line_31.setMidLineWidth(2)
        self.line_31.setFrameShape(QFrame.Shape.HLine)
        self.line_31.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_113.addWidget(self.line_31)

        self.gridLayout_28 = QGridLayout()
        self.gridLayout_28.setObjectName(u"gridLayout_28")
        self.gridLayout_28.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_114 = QVBoxLayout()
        self.verticalLayout_114.setObjectName(u"verticalLayout_114")
        self.label_88 = QLabel(self.widget_68)
        self.label_88.setObjectName(u"label_88")

        self.verticalLayout_114.addWidget(self.label_88)

        self.label_89 = QLabel(self.widget_68)
        self.label_89.setObjectName(u"label_89")
        self.label_89.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_114.addWidget(self.label_89)


        self.gridLayout_28.addLayout(self.verticalLayout_114, 0, 0, 1, 1)

        self.checkBox_28 = QCheckBox(self.widget_68)
        self.checkBox_28.setObjectName(u"checkBox_28")
        self.checkBox_28.setStyleSheet(u"")

        self.gridLayout_28.addWidget(self.checkBox_28, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_115 = QVBoxLayout()
        self.verticalLayout_115.setObjectName(u"verticalLayout_115")
        self.label_152 = QLabel(self.widget_68)
        self.label_152.setObjectName(u"label_152")

        self.verticalLayout_115.addWidget(self.label_152)

        self.label_153 = QLabel(self.widget_68)
        self.label_153.setObjectName(u"label_153")
        self.label_153.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_115.addWidget(self.label_153)


        self.gridLayout_28.addLayout(self.verticalLayout_115, 1, 0, 1, 1)

        self.lineEdit_26 = QLineEdit(self.widget_68)
        self.lineEdit_26.setObjectName(u"lineEdit_26")
        self.lineEdit_26.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_28.addWidget(self.lineEdit_26, 1, 1, 1, 1)

        self.gridLayout_28.setColumnStretch(0, 5)
        self.gridLayout_28.setColumnStretch(1, 2)

        self.verticalLayout_113.addLayout(self.gridLayout_28)


        self.verticalLayout_112.addWidget(self.widget_68, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_31.setWidget(self.scrollAreaWidgetContents_28)

        self.horizontalLayout_35.addWidget(self.scrollArea_31)

        self.horizontalSpacer_56 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_35.addItem(self.horizontalSpacer_56)

        self.horizontalLayout_35.setStretch(0, 1)
        self.horizontalLayout_35.setStretch(1, 5)
        self.horizontalLayout_35.setStretch(2, 1)

        self.horizontalLayout_44.addWidget(self.widget_67)

        self.stackedWidget.addWidget(self.RenWuJiHuiSuo_widget)
        self.YiLeWaiMai_widget = QWidget()
        self.YiLeWaiMai_widget.setObjectName(u"YiLeWaiMai_widget")
        self.horizontalLayout_45 = QHBoxLayout(self.YiLeWaiMai_widget)
        self.horizontalLayout_45.setObjectName(u"horizontalLayout_45")
        self.widget_79 = QWidget(self.YiLeWaiMai_widget)
        self.widget_79.setObjectName(u"widget_79")
        self.widget_79.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_41 = QHBoxLayout(self.widget_79)
        self.horizontalLayout_41.setObjectName(u"horizontalLayout_41")
        self.horizontalSpacer_67 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_41.addItem(self.horizontalSpacer_67)

        self.scrollArea_37 = QScrollArea(self.widget_79)
        self.scrollArea_37.setObjectName(u"scrollArea_37")
        self.scrollArea_37.setMinimumSize(QSize(600, 0))
        self.scrollArea_37.setWidgetResizable(True)
        self.scrollAreaWidgetContents_34 = QWidget()
        self.scrollAreaWidgetContents_34.setObjectName(u"scrollAreaWidgetContents_34")
        self.scrollAreaWidgetContents_34.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_136 = QVBoxLayout(self.scrollAreaWidgetContents_34)
        self.verticalLayout_136.setSpacing(10)
        self.verticalLayout_136.setObjectName(u"verticalLayout_136")
        self.verticalLayout_136.setContentsMargins(10, -1, 10, -1)
        self.widget_80 = QWidget(self.scrollAreaWidgetContents_34)
        self.widget_80.setObjectName(u"widget_80")
        self.widget_80.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_137 = QVBoxLayout(self.widget_80)
        self.verticalLayout_137.setObjectName(u"verticalLayout_137")
        self.label_167 = QLabel(self.widget_80)
        self.label_167.setObjectName(u"label_167")
        self.label_167.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_137.addWidget(self.label_167)

        self.line_37 = QFrame(self.widget_80)
        self.line_37.setObjectName(u"line_37")
        sizePolicy1.setHeightForWidth(self.line_37.sizePolicy().hasHeightForWidth())
        self.line_37.setSizePolicy(sizePolicy1)
        self.line_37.setStyleSheet(u"")
        self.line_37.setLineWidth(0)
        self.line_37.setMidLineWidth(2)
        self.line_37.setFrameShape(QFrame.Shape.HLine)
        self.line_37.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_137.addWidget(self.line_37)

        self.gridLayout_34 = QGridLayout()
        self.gridLayout_34.setObjectName(u"gridLayout_34")
        self.gridLayout_34.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_138 = QVBoxLayout()
        self.verticalLayout_138.setObjectName(u"verticalLayout_138")
        self.label_168 = QLabel(self.widget_80)
        self.label_168.setObjectName(u"label_168")

        self.verticalLayout_138.addWidget(self.label_168)

        self.label_169 = QLabel(self.widget_80)
        self.label_169.setObjectName(u"label_169")
        self.label_169.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_138.addWidget(self.label_169)


        self.gridLayout_34.addLayout(self.verticalLayout_138, 0, 0, 1, 1)

        self.checkBox_34 = QCheckBox(self.widget_80)
        self.checkBox_34.setObjectName(u"checkBox_34")
        self.checkBox_34.setStyleSheet(u"")

        self.gridLayout_34.addWidget(self.checkBox_34, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_139 = QVBoxLayout()
        self.verticalLayout_139.setObjectName(u"verticalLayout_139")
        self.label_170 = QLabel(self.widget_80)
        self.label_170.setObjectName(u"label_170")

        self.verticalLayout_139.addWidget(self.label_170)

        self.label_171 = QLabel(self.widget_80)
        self.label_171.setObjectName(u"label_171")
        self.label_171.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_139.addWidget(self.label_171)


        self.gridLayout_34.addLayout(self.verticalLayout_139, 1, 0, 1, 1)

        self.lineEdit_32 = QLineEdit(self.widget_80)
        self.lineEdit_32.setObjectName(u"lineEdit_32")
        self.lineEdit_32.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_34.addWidget(self.lineEdit_32, 1, 1, 1, 1)

        self.gridLayout_34.setColumnStretch(0, 5)
        self.gridLayout_34.setColumnStretch(1, 2)

        self.verticalLayout_137.addLayout(self.gridLayout_34)


        self.verticalLayout_136.addWidget(self.widget_80, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_37.setWidget(self.scrollAreaWidgetContents_34)

        self.horizontalLayout_41.addWidget(self.scrollArea_37)

        self.horizontalSpacer_68 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_41.addItem(self.horizontalSpacer_68)

        self.horizontalLayout_41.setStretch(0, 1)
        self.horizontalLayout_41.setStretch(1, 5)
        self.horizontalLayout_41.setStretch(2, 1)

        self.horizontalLayout_45.addWidget(self.widget_79)

        self.stackedWidget.addWidget(self.YiLeWaiMai_widget)
        self.MeiRiShengChang_widget = QWidget()
        self.MeiRiShengChang_widget.setObjectName(u"MeiRiShengChang_widget")
        self.horizontalLayout_46 = QHBoxLayout(self.MeiRiShengChang_widget)
        self.horizontalLayout_46.setObjectName(u"horizontalLayout_46")
        self.widget_53 = QWidget(self.MeiRiShengChang_widget)
        self.widget_53.setObjectName(u"widget_53")
        self.widget_53.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_28 = QHBoxLayout(self.widget_53)
        self.horizontalLayout_28.setObjectName(u"horizontalLayout_28")
        self.horizontalSpacer_41 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_28.addItem(self.horizontalSpacer_41)

        self.scrollArea_24 = QScrollArea(self.widget_53)
        self.scrollArea_24.setObjectName(u"scrollArea_24")
        self.scrollArea_24.setMinimumSize(QSize(600, 0))
        self.scrollArea_24.setWidgetResizable(True)
        self.scrollAreaWidgetContents_21 = QWidget()
        self.scrollAreaWidgetContents_21.setObjectName(u"scrollAreaWidgetContents_21")
        self.scrollAreaWidgetContents_21.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_84 = QVBoxLayout(self.scrollAreaWidgetContents_21)
        self.verticalLayout_84.setSpacing(10)
        self.verticalLayout_84.setObjectName(u"verticalLayout_84")
        self.verticalLayout_84.setContentsMargins(10, -1, 10, -1)
        self.widget_54 = QWidget(self.scrollAreaWidgetContents_21)
        self.widget_54.setObjectName(u"widget_54")
        self.widget_54.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_85 = QVBoxLayout(self.widget_54)
        self.verticalLayout_85.setObjectName(u"verticalLayout_85")
        self.label_66 = QLabel(self.widget_54)
        self.label_66.setObjectName(u"label_66")
        self.label_66.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_85.addWidget(self.label_66)

        self.line_24 = QFrame(self.widget_54)
        self.line_24.setObjectName(u"line_24")
        sizePolicy1.setHeightForWidth(self.line_24.sizePolicy().hasHeightForWidth())
        self.line_24.setSizePolicy(sizePolicy1)
        self.line_24.setStyleSheet(u"")
        self.line_24.setLineWidth(0)
        self.line_24.setMidLineWidth(2)
        self.line_24.setFrameShape(QFrame.Shape.HLine)
        self.line_24.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_85.addWidget(self.line_24)

        self.gridLayout_21 = QGridLayout()
        self.gridLayout_21.setObjectName(u"gridLayout_21")
        self.gridLayout_21.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_86 = QVBoxLayout()
        self.verticalLayout_86.setObjectName(u"verticalLayout_86")
        self.label_67 = QLabel(self.widget_54)
        self.label_67.setObjectName(u"label_67")

        self.verticalLayout_86.addWidget(self.label_67)

        self.label_68 = QLabel(self.widget_54)
        self.label_68.setObjectName(u"label_68")
        self.label_68.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_86.addWidget(self.label_68)


        self.gridLayout_21.addLayout(self.verticalLayout_86, 0, 0, 1, 1)

        self.checkBox_21 = QCheckBox(self.widget_54)
        self.checkBox_21.setObjectName(u"checkBox_21")
        self.checkBox_21.setStyleSheet(u"")

        self.gridLayout_21.addWidget(self.checkBox_21, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_87 = QVBoxLayout()
        self.verticalLayout_87.setObjectName(u"verticalLayout_87")
        self.label_138 = QLabel(self.widget_54)
        self.label_138.setObjectName(u"label_138")

        self.verticalLayout_87.addWidget(self.label_138)

        self.label_139 = QLabel(self.widget_54)
        self.label_139.setObjectName(u"label_139")
        self.label_139.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_87.addWidget(self.label_139)


        self.gridLayout_21.addLayout(self.verticalLayout_87, 1, 0, 1, 1)

        self.lineEdit_19 = QLineEdit(self.widget_54)
        self.lineEdit_19.setObjectName(u"lineEdit_19")
        self.lineEdit_19.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_21.addWidget(self.lineEdit_19, 1, 1, 1, 1)

        self.gridLayout_21.setColumnStretch(0, 5)
        self.gridLayout_21.setColumnStretch(1, 2)

        self.verticalLayout_85.addLayout(self.gridLayout_21)


        self.verticalLayout_84.addWidget(self.widget_54, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_24.setWidget(self.scrollAreaWidgetContents_21)

        self.horizontalLayout_28.addWidget(self.scrollArea_24)

        self.horizontalSpacer_42 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_28.addItem(self.horizontalSpacer_42)

        self.horizontalLayout_28.setStretch(0, 1)
        self.horizontalLayout_28.setStretch(1, 5)
        self.horizontalLayout_28.setStretch(2, 1)

        self.horizontalLayout_46.addWidget(self.widget_53)

        self.stackedWidget.addWidget(self.MeiRiShengChang_widget)
        self.ShengCunTiaoZhan_widget = QWidget()
        self.ShengCunTiaoZhan_widget.setObjectName(u"ShengCunTiaoZhan_widget")
        self.horizontalLayout_47 = QHBoxLayout(self.ShengCunTiaoZhan_widget)
        self.horizontalLayout_47.setObjectName(u"horizontalLayout_47")
        self.widget_71 = QWidget(self.ShengCunTiaoZhan_widget)
        self.widget_71.setObjectName(u"widget_71")
        self.widget_71.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_37 = QHBoxLayout(self.widget_71)
        self.horizontalLayout_37.setObjectName(u"horizontalLayout_37")
        self.horizontalSpacer_59 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_37.addItem(self.horizontalSpacer_59)

        self.scrollArea_33 = QScrollArea(self.widget_71)
        self.scrollArea_33.setObjectName(u"scrollArea_33")
        self.scrollArea_33.setMinimumSize(QSize(600, 0))
        self.scrollArea_33.setWidgetResizable(True)
        self.scrollAreaWidgetContents_30 = QWidget()
        self.scrollAreaWidgetContents_30.setObjectName(u"scrollAreaWidgetContents_30")
        self.scrollAreaWidgetContents_30.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_120 = QVBoxLayout(self.scrollAreaWidgetContents_30)
        self.verticalLayout_120.setSpacing(10)
        self.verticalLayout_120.setObjectName(u"verticalLayout_120")
        self.verticalLayout_120.setContentsMargins(10, -1, 10, -1)
        self.widget_72 = QWidget(self.scrollAreaWidgetContents_30)
        self.widget_72.setObjectName(u"widget_72")
        self.widget_72.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_121 = QVBoxLayout(self.widget_72)
        self.verticalLayout_121.setObjectName(u"verticalLayout_121")
        self.label_93 = QLabel(self.widget_72)
        self.label_93.setObjectName(u"label_93")
        self.label_93.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_121.addWidget(self.label_93)

        self.line_33 = QFrame(self.widget_72)
        self.line_33.setObjectName(u"line_33")
        sizePolicy1.setHeightForWidth(self.line_33.sizePolicy().hasHeightForWidth())
        self.line_33.setSizePolicy(sizePolicy1)
        self.line_33.setStyleSheet(u"")
        self.line_33.setLineWidth(0)
        self.line_33.setMidLineWidth(2)
        self.line_33.setFrameShape(QFrame.Shape.HLine)
        self.line_33.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_121.addWidget(self.line_33)

        self.gridLayout_30 = QGridLayout()
        self.gridLayout_30.setObjectName(u"gridLayout_30")
        self.gridLayout_30.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_122 = QVBoxLayout()
        self.verticalLayout_122.setObjectName(u"verticalLayout_122")
        self.label_94 = QLabel(self.widget_72)
        self.label_94.setObjectName(u"label_94")

        self.verticalLayout_122.addWidget(self.label_94)

        self.label_95 = QLabel(self.widget_72)
        self.label_95.setObjectName(u"label_95")
        self.label_95.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_122.addWidget(self.label_95)


        self.gridLayout_30.addLayout(self.verticalLayout_122, 0, 0, 1, 1)

        self.checkBox_30 = QCheckBox(self.widget_72)
        self.checkBox_30.setObjectName(u"checkBox_30")
        self.checkBox_30.setStyleSheet(u"")

        self.gridLayout_30.addWidget(self.checkBox_30, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_123 = QVBoxLayout()
        self.verticalLayout_123.setObjectName(u"verticalLayout_123")
        self.label_156 = QLabel(self.widget_72)
        self.label_156.setObjectName(u"label_156")

        self.verticalLayout_123.addWidget(self.label_156)

        self.label_157 = QLabel(self.widget_72)
        self.label_157.setObjectName(u"label_157")
        self.label_157.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_123.addWidget(self.label_157)


        self.gridLayout_30.addLayout(self.verticalLayout_123, 1, 0, 1, 1)

        self.lineEdit_28 = QLineEdit(self.widget_72)
        self.lineEdit_28.setObjectName(u"lineEdit_28")
        self.lineEdit_28.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_30.addWidget(self.lineEdit_28, 1, 1, 1, 1)

        self.gridLayout_30.setColumnStretch(0, 5)
        self.gridLayout_30.setColumnStretch(1, 2)

        self.verticalLayout_121.addLayout(self.gridLayout_30)


        self.verticalLayout_120.addWidget(self.widget_72, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_33.setWidget(self.scrollAreaWidgetContents_30)

        self.horizontalLayout_37.addWidget(self.scrollArea_33)

        self.horizontalSpacer_60 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_37.addItem(self.horizontalSpacer_60)

        self.horizontalLayout_37.setStretch(0, 1)
        self.horizontalLayout_37.setStretch(1, 5)
        self.horizontalLayout_37.setStretch(2, 1)

        self.horizontalLayout_47.addWidget(self.widget_71)

        self.stackedWidget.addWidget(self.ShengCunTiaoZhan_widget)
        self.MiJingTanXian_widget = QWidget()
        self.MiJingTanXian_widget.setObjectName(u"MiJingTanXian_widget")
        self.horizontalLayout_48 = QHBoxLayout(self.MiJingTanXian_widget)
        self.horizontalLayout_48.setObjectName(u"horizontalLayout_48")
        self.widget_57 = QWidget(self.MiJingTanXian_widget)
        self.widget_57.setObjectName(u"widget_57")
        self.widget_57.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_30 = QHBoxLayout(self.widget_57)
        self.horizontalLayout_30.setObjectName(u"horizontalLayout_30")
        self.horizontalSpacer_45 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_30.addItem(self.horizontalSpacer_45)

        self.scrollArea_26 = QScrollArea(self.widget_57)
        self.scrollArea_26.setObjectName(u"scrollArea_26")
        self.scrollArea_26.setMinimumSize(QSize(600, 0))
        self.scrollArea_26.setWidgetResizable(True)
        self.scrollAreaWidgetContents_23 = QWidget()
        self.scrollAreaWidgetContents_23.setObjectName(u"scrollAreaWidgetContents_23")
        self.scrollAreaWidgetContents_23.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_92 = QVBoxLayout(self.scrollAreaWidgetContents_23)
        self.verticalLayout_92.setSpacing(10)
        self.verticalLayout_92.setObjectName(u"verticalLayout_92")
        self.verticalLayout_92.setContentsMargins(10, -1, 10, -1)
        self.widget_58 = QWidget(self.scrollAreaWidgetContents_23)
        self.widget_58.setObjectName(u"widget_58")
        self.widget_58.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_93 = QVBoxLayout(self.widget_58)
        self.verticalLayout_93.setObjectName(u"verticalLayout_93")
        self.label_72 = QLabel(self.widget_58)
        self.label_72.setObjectName(u"label_72")
        self.label_72.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_93.addWidget(self.label_72)

        self.line_26 = QFrame(self.widget_58)
        self.line_26.setObjectName(u"line_26")
        sizePolicy1.setHeightForWidth(self.line_26.sizePolicy().hasHeightForWidth())
        self.line_26.setSizePolicy(sizePolicy1)
        self.line_26.setStyleSheet(u"")
        self.line_26.setLineWidth(0)
        self.line_26.setMidLineWidth(2)
        self.line_26.setFrameShape(QFrame.Shape.HLine)
        self.line_26.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_93.addWidget(self.line_26)

        self.gridLayout_23 = QGridLayout()
        self.gridLayout_23.setObjectName(u"gridLayout_23")
        self.gridLayout_23.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_94 = QVBoxLayout()
        self.verticalLayout_94.setObjectName(u"verticalLayout_94")
        self.label_73 = QLabel(self.widget_58)
        self.label_73.setObjectName(u"label_73")

        self.verticalLayout_94.addWidget(self.label_73)

        self.label_74 = QLabel(self.widget_58)
        self.label_74.setObjectName(u"label_74")
        self.label_74.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_94.addWidget(self.label_74)


        self.gridLayout_23.addLayout(self.verticalLayout_94, 0, 0, 1, 1)

        self.checkBox_23 = QCheckBox(self.widget_58)
        self.checkBox_23.setObjectName(u"checkBox_23")
        self.checkBox_23.setStyleSheet(u"")

        self.gridLayout_23.addWidget(self.checkBox_23, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_95 = QVBoxLayout()
        self.verticalLayout_95.setObjectName(u"verticalLayout_95")
        self.label_142 = QLabel(self.widget_58)
        self.label_142.setObjectName(u"label_142")

        self.verticalLayout_95.addWidget(self.label_142)

        self.label_143 = QLabel(self.widget_58)
        self.label_143.setObjectName(u"label_143")
        self.label_143.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_95.addWidget(self.label_143)


        self.gridLayout_23.addLayout(self.verticalLayout_95, 1, 0, 1, 1)

        self.lineEdit_21 = QLineEdit(self.widget_58)
        self.lineEdit_21.setObjectName(u"lineEdit_21")
        self.lineEdit_21.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_23.addWidget(self.lineEdit_21, 1, 1, 1, 1)

        self.gridLayout_23.setColumnStretch(0, 5)
        self.gridLayout_23.setColumnStretch(1, 2)

        self.verticalLayout_93.addLayout(self.gridLayout_23)


        self.verticalLayout_92.addWidget(self.widget_58, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_26.setWidget(self.scrollAreaWidgetContents_23)

        self.horizontalLayout_30.addWidget(self.scrollArea_26)

        self.horizontalSpacer_46 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_30.addItem(self.horizontalSpacer_46)

        self.horizontalLayout_30.setStretch(0, 1)
        self.horizontalLayout_30.setStretch(1, 5)
        self.horizontalLayout_30.setStretch(2, 1)

        self.horizontalLayout_48.addWidget(self.widget_57)

        self.stackedWidget.addWidget(self.MiJingTanXian_widget)
        self.QingBaoZhan_widget = QWidget()
        self.QingBaoZhan_widget.setObjectName(u"QingBaoZhan_widget")
        self.horizontalLayout_49 = QHBoxLayout(self.QingBaoZhan_widget)
        self.horizontalLayout_49.setObjectName(u"horizontalLayout_49")
        self.widget_61 = QWidget(self.QingBaoZhan_widget)
        self.widget_61.setObjectName(u"widget_61")
        self.widget_61.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_32 = QHBoxLayout(self.widget_61)
        self.horizontalLayout_32.setObjectName(u"horizontalLayout_32")
        self.horizontalSpacer_49 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_32.addItem(self.horizontalSpacer_49)

        self.scrollArea_28 = QScrollArea(self.widget_61)
        self.scrollArea_28.setObjectName(u"scrollArea_28")
        self.scrollArea_28.setMinimumSize(QSize(600, 0))
        self.scrollArea_28.setWidgetResizable(True)
        self.scrollAreaWidgetContents_25 = QWidget()
        self.scrollAreaWidgetContents_25.setObjectName(u"scrollAreaWidgetContents_25")
        self.scrollAreaWidgetContents_25.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_100 = QVBoxLayout(self.scrollAreaWidgetContents_25)
        self.verticalLayout_100.setSpacing(10)
        self.verticalLayout_100.setObjectName(u"verticalLayout_100")
        self.verticalLayout_100.setContentsMargins(10, -1, 10, -1)
        self.widget_62 = QWidget(self.scrollAreaWidgetContents_25)
        self.widget_62.setObjectName(u"widget_62")
        self.widget_62.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_101 = QVBoxLayout(self.widget_62)
        self.verticalLayout_101.setObjectName(u"verticalLayout_101")
        self.label_78 = QLabel(self.widget_62)
        self.label_78.setObjectName(u"label_78")
        self.label_78.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_101.addWidget(self.label_78)

        self.line_28 = QFrame(self.widget_62)
        self.line_28.setObjectName(u"line_28")
        sizePolicy1.setHeightForWidth(self.line_28.sizePolicy().hasHeightForWidth())
        self.line_28.setSizePolicy(sizePolicy1)
        self.line_28.setStyleSheet(u"")
        self.line_28.setLineWidth(0)
        self.line_28.setMidLineWidth(2)
        self.line_28.setFrameShape(QFrame.Shape.HLine)
        self.line_28.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_101.addWidget(self.line_28)

        self.gridLayout_25 = QGridLayout()
        self.gridLayout_25.setObjectName(u"gridLayout_25")
        self.gridLayout_25.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_102 = QVBoxLayout()
        self.verticalLayout_102.setObjectName(u"verticalLayout_102")
        self.label_79 = QLabel(self.widget_62)
        self.label_79.setObjectName(u"label_79")

        self.verticalLayout_102.addWidget(self.label_79)

        self.label_80 = QLabel(self.widget_62)
        self.label_80.setObjectName(u"label_80")
        self.label_80.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_102.addWidget(self.label_80)


        self.gridLayout_25.addLayout(self.verticalLayout_102, 0, 0, 1, 1)

        self.checkBox_25 = QCheckBox(self.widget_62)
        self.checkBox_25.setObjectName(u"checkBox_25")
        self.checkBox_25.setStyleSheet(u"")

        self.gridLayout_25.addWidget(self.checkBox_25, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_103 = QVBoxLayout()
        self.verticalLayout_103.setObjectName(u"verticalLayout_103")
        self.label_146 = QLabel(self.widget_62)
        self.label_146.setObjectName(u"label_146")

        self.verticalLayout_103.addWidget(self.label_146)

        self.label_147 = QLabel(self.widget_62)
        self.label_147.setObjectName(u"label_147")
        self.label_147.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_103.addWidget(self.label_147)


        self.gridLayout_25.addLayout(self.verticalLayout_103, 1, 0, 1, 1)

        self.lineEdit_23 = QLineEdit(self.widget_62)
        self.lineEdit_23.setObjectName(u"lineEdit_23")
        self.lineEdit_23.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_25.addWidget(self.lineEdit_23, 1, 1, 1, 1)

        self.gridLayout_25.setColumnStretch(0, 5)
        self.gridLayout_25.setColumnStretch(1, 2)

        self.verticalLayout_101.addLayout(self.gridLayout_25)


        self.verticalLayout_100.addWidget(self.widget_62, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_28.setWidget(self.scrollAreaWidgetContents_25)

        self.horizontalLayout_32.addWidget(self.scrollArea_28)

        self.horizontalSpacer_50 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_32.addItem(self.horizontalSpacer_50)

        self.horizontalLayout_32.setStretch(0, 1)
        self.horizontalLayout_32.setStretch(1, 5)
        self.horizontalLayout_32.setStretch(2, 1)

        self.horizontalLayout_49.addWidget(self.widget_61)

        self.stackedWidget.addWidget(self.QingBaoZhan_widget)
        self.MaoXianFuBen_widget = QWidget()
        self.MaoXianFuBen_widget.setObjectName(u"MaoXianFuBen_widget")
        self.horizontalLayout_50 = QHBoxLayout(self.MaoXianFuBen_widget)
        self.horizontalLayout_50.setObjectName(u"horizontalLayout_50")
        self.widget_49 = QWidget(self.MaoXianFuBen_widget)
        self.widget_49.setObjectName(u"widget_49")
        self.widget_49.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_26 = QHBoxLayout(self.widget_49)
        self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
        self.horizontalSpacer_37 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_26.addItem(self.horizontalSpacer_37)

        self.scrollArea_22 = QScrollArea(self.widget_49)
        self.scrollArea_22.setObjectName(u"scrollArea_22")
        self.scrollArea_22.setMinimumSize(QSize(600, 0))
        self.scrollArea_22.setWidgetResizable(True)
        self.scrollAreaWidgetContents_19 = QWidget()
        self.scrollAreaWidgetContents_19.setObjectName(u"scrollAreaWidgetContents_19")
        self.scrollAreaWidgetContents_19.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_76 = QVBoxLayout(self.scrollAreaWidgetContents_19)
        self.verticalLayout_76.setSpacing(10)
        self.verticalLayout_76.setObjectName(u"verticalLayout_76")
        self.verticalLayout_76.setContentsMargins(10, -1, 10, -1)
        self.widget_50 = QWidget(self.scrollAreaWidgetContents_19)
        self.widget_50.setObjectName(u"widget_50")
        self.widget_50.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_77 = QVBoxLayout(self.widget_50)
        self.verticalLayout_77.setObjectName(u"verticalLayout_77")
        self.label_60 = QLabel(self.widget_50)
        self.label_60.setObjectName(u"label_60")
        self.label_60.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_77.addWidget(self.label_60)

        self.line_22 = QFrame(self.widget_50)
        self.line_22.setObjectName(u"line_22")
        sizePolicy1.setHeightForWidth(self.line_22.sizePolicy().hasHeightForWidth())
        self.line_22.setSizePolicy(sizePolicy1)
        self.line_22.setStyleSheet(u"")
        self.line_22.setLineWidth(0)
        self.line_22.setMidLineWidth(2)
        self.line_22.setFrameShape(QFrame.Shape.HLine)
        self.line_22.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_77.addWidget(self.line_22)

        self.gridLayout_19 = QGridLayout()
        self.gridLayout_19.setObjectName(u"gridLayout_19")
        self.gridLayout_19.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_78 = QVBoxLayout()
        self.verticalLayout_78.setObjectName(u"verticalLayout_78")
        self.label_61 = QLabel(self.widget_50)
        self.label_61.setObjectName(u"label_61")

        self.verticalLayout_78.addWidget(self.label_61)

        self.label_62 = QLabel(self.widget_50)
        self.label_62.setObjectName(u"label_62")
        self.label_62.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_78.addWidget(self.label_62)


        self.gridLayout_19.addLayout(self.verticalLayout_78, 0, 0, 1, 1)

        self.checkBox_19 = QCheckBox(self.widget_50)
        self.checkBox_19.setObjectName(u"checkBox_19")
        self.checkBox_19.setStyleSheet(u"")

        self.gridLayout_19.addWidget(self.checkBox_19, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_79 = QVBoxLayout()
        self.verticalLayout_79.setObjectName(u"verticalLayout_79")
        self.label_134 = QLabel(self.widget_50)
        self.label_134.setObjectName(u"label_134")

        self.verticalLayout_79.addWidget(self.label_134)

        self.label_135 = QLabel(self.widget_50)
        self.label_135.setObjectName(u"label_135")
        self.label_135.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_79.addWidget(self.label_135)


        self.gridLayout_19.addLayout(self.verticalLayout_79, 1, 0, 1, 1)

        self.lineEdit_17 = QLineEdit(self.widget_50)
        self.lineEdit_17.setObjectName(u"lineEdit_17")
        self.lineEdit_17.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_19.addWidget(self.lineEdit_17, 1, 1, 1, 1)

        self.gridLayout_19.setColumnStretch(0, 5)
        self.gridLayout_19.setColumnStretch(1, 2)

        self.verticalLayout_77.addLayout(self.gridLayout_19)


        self.verticalLayout_76.addWidget(self.widget_50, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_22.setWidget(self.scrollAreaWidgetContents_19)

        self.horizontalLayout_26.addWidget(self.scrollArea_22)

        self.horizontalSpacer_38 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_26.addItem(self.horizontalSpacer_38)

        self.horizontalLayout_26.setStretch(0, 1)
        self.horizontalLayout_26.setStretch(1, 5)
        self.horizontalLayout_26.setStretch(2, 1)

        self.horizontalLayout_50.addWidget(self.widget_49)

        self.stackedWidget.addWidget(self.MaoXianFuBen_widget)
        self.HuoYueDuJiangLi_widget = QWidget()
        self.HuoYueDuJiangLi_widget.setObjectName(u"HuoYueDuJiangLi_widget")
        self.horizontalLayout_51 = QHBoxLayout(self.HuoYueDuJiangLi_widget)
        self.horizontalLayout_51.setObjectName(u"horizontalLayout_51")
        self.widget_45 = QWidget(self.HuoYueDuJiangLi_widget)
        self.widget_45.setObjectName(u"widget_45")
        self.widget_45.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_24 = QHBoxLayout(self.widget_45)
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.horizontalSpacer_33 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_24.addItem(self.horizontalSpacer_33)

        self.scrollArea_20 = QScrollArea(self.widget_45)
        self.scrollArea_20.setObjectName(u"scrollArea_20")
        self.scrollArea_20.setMinimumSize(QSize(600, 0))
        self.scrollArea_20.setWidgetResizable(True)
        self.scrollAreaWidgetContents_17 = QWidget()
        self.scrollAreaWidgetContents_17.setObjectName(u"scrollAreaWidgetContents_17")
        self.scrollAreaWidgetContents_17.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_68 = QVBoxLayout(self.scrollAreaWidgetContents_17)
        self.verticalLayout_68.setSpacing(10)
        self.verticalLayout_68.setObjectName(u"verticalLayout_68")
        self.verticalLayout_68.setContentsMargins(10, -1, 10, -1)
        self.widget_46 = QWidget(self.scrollAreaWidgetContents_17)
        self.widget_46.setObjectName(u"widget_46")
        self.widget_46.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_69 = QVBoxLayout(self.widget_46)
        self.verticalLayout_69.setObjectName(u"verticalLayout_69")
        self.label_54 = QLabel(self.widget_46)
        self.label_54.setObjectName(u"label_54")
        self.label_54.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_69.addWidget(self.label_54)

        self.line_20 = QFrame(self.widget_46)
        self.line_20.setObjectName(u"line_20")
        sizePolicy1.setHeightForWidth(self.line_20.sizePolicy().hasHeightForWidth())
        self.line_20.setSizePolicy(sizePolicy1)
        self.line_20.setStyleSheet(u"")
        self.line_20.setLineWidth(0)
        self.line_20.setMidLineWidth(2)
        self.line_20.setFrameShape(QFrame.Shape.HLine)
        self.line_20.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_69.addWidget(self.line_20)

        self.gridLayout_17 = QGridLayout()
        self.gridLayout_17.setObjectName(u"gridLayout_17")
        self.gridLayout_17.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_70 = QVBoxLayout()
        self.verticalLayout_70.setObjectName(u"verticalLayout_70")
        self.label_55 = QLabel(self.widget_46)
        self.label_55.setObjectName(u"label_55")

        self.verticalLayout_70.addWidget(self.label_55)

        self.label_56 = QLabel(self.widget_46)
        self.label_56.setObjectName(u"label_56")
        self.label_56.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_70.addWidget(self.label_56)


        self.gridLayout_17.addLayout(self.verticalLayout_70, 0, 0, 1, 1)

        self.checkBox_17 = QCheckBox(self.widget_46)
        self.checkBox_17.setObjectName(u"checkBox_17")
        self.checkBox_17.setStyleSheet(u"")

        self.gridLayout_17.addWidget(self.checkBox_17, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_71 = QVBoxLayout()
        self.verticalLayout_71.setObjectName(u"verticalLayout_71")
        self.label_130 = QLabel(self.widget_46)
        self.label_130.setObjectName(u"label_130")

        self.verticalLayout_71.addWidget(self.label_130)

        self.label_131 = QLabel(self.widget_46)
        self.label_131.setObjectName(u"label_131")
        self.label_131.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_71.addWidget(self.label_131)


        self.gridLayout_17.addLayout(self.verticalLayout_71, 1, 0, 1, 1)

        self.lineEdit_15 = QLineEdit(self.widget_46)
        self.lineEdit_15.setObjectName(u"lineEdit_15")
        self.lineEdit_15.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_17.addWidget(self.lineEdit_15, 1, 1, 1, 1)

        self.gridLayout_17.setColumnStretch(0, 5)
        self.gridLayout_17.setColumnStretch(1, 2)

        self.verticalLayout_69.addLayout(self.gridLayout_17)


        self.verticalLayout_68.addWidget(self.widget_46, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_20.setWidget(self.scrollAreaWidgetContents_17)

        self.horizontalLayout_24.addWidget(self.scrollArea_20)

        self.horizontalSpacer_34 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_24.addItem(self.horizontalSpacer_34)

        self.horizontalLayout_24.setStretch(0, 1)
        self.horizontalLayout_24.setStretch(1, 5)
        self.horizontalLayout_24.setStretch(2, 1)

        self.horizontalLayout_51.addWidget(self.widget_45)

        self.stackedWidget.addWidget(self.HuoYueDuJiangLi_widget)
        self.QingKongYouJian_widget = QWidget()
        self.QingKongYouJian_widget.setObjectName(u"QingKongYouJian_widget")
        self.horizontalLayout_52 = QHBoxLayout(self.QingKongYouJian_widget)
        self.horizontalLayout_52.setObjectName(u"horizontalLayout_52")
        self.widget_63 = QWidget(self.QingKongYouJian_widget)
        self.widget_63.setObjectName(u"widget_63")
        self.widget_63.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_33 = QHBoxLayout(self.widget_63)
        self.horizontalLayout_33.setObjectName(u"horizontalLayout_33")
        self.horizontalSpacer_51 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_33.addItem(self.horizontalSpacer_51)

        self.scrollArea_29 = QScrollArea(self.widget_63)
        self.scrollArea_29.setObjectName(u"scrollArea_29")
        self.scrollArea_29.setMinimumSize(QSize(600, 0))
        self.scrollArea_29.setWidgetResizable(True)
        self.scrollAreaWidgetContents_26 = QWidget()
        self.scrollAreaWidgetContents_26.setObjectName(u"scrollAreaWidgetContents_26")
        self.scrollAreaWidgetContents_26.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_104 = QVBoxLayout(self.scrollAreaWidgetContents_26)
        self.verticalLayout_104.setSpacing(10)
        self.verticalLayout_104.setObjectName(u"verticalLayout_104")
        self.verticalLayout_104.setContentsMargins(10, -1, 10, -1)
        self.widget_64 = QWidget(self.scrollAreaWidgetContents_26)
        self.widget_64.setObjectName(u"widget_64")
        self.widget_64.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_105 = QVBoxLayout(self.widget_64)
        self.verticalLayout_105.setObjectName(u"verticalLayout_105")
        self.label_81 = QLabel(self.widget_64)
        self.label_81.setObjectName(u"label_81")
        self.label_81.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_105.addWidget(self.label_81)

        self.line_29 = QFrame(self.widget_64)
        self.line_29.setObjectName(u"line_29")
        sizePolicy1.setHeightForWidth(self.line_29.sizePolicy().hasHeightForWidth())
        self.line_29.setSizePolicy(sizePolicy1)
        self.line_29.setStyleSheet(u"")
        self.line_29.setLineWidth(0)
        self.line_29.setMidLineWidth(2)
        self.line_29.setFrameShape(QFrame.Shape.HLine)
        self.line_29.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_105.addWidget(self.line_29)

        self.gridLayout_26 = QGridLayout()
        self.gridLayout_26.setObjectName(u"gridLayout_26")
        self.gridLayout_26.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_106 = QVBoxLayout()
        self.verticalLayout_106.setObjectName(u"verticalLayout_106")
        self.label_82 = QLabel(self.widget_64)
        self.label_82.setObjectName(u"label_82")

        self.verticalLayout_106.addWidget(self.label_82)

        self.label_83 = QLabel(self.widget_64)
        self.label_83.setObjectName(u"label_83")
        self.label_83.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_106.addWidget(self.label_83)


        self.gridLayout_26.addLayout(self.verticalLayout_106, 0, 0, 1, 1)

        self.checkBox_26 = QCheckBox(self.widget_64)
        self.checkBox_26.setObjectName(u"checkBox_26")
        self.checkBox_26.setStyleSheet(u"")

        self.gridLayout_26.addWidget(self.checkBox_26, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_107 = QVBoxLayout()
        self.verticalLayout_107.setObjectName(u"verticalLayout_107")
        self.label_148 = QLabel(self.widget_64)
        self.label_148.setObjectName(u"label_148")

        self.verticalLayout_107.addWidget(self.label_148)

        self.label_149 = QLabel(self.widget_64)
        self.label_149.setObjectName(u"label_149")
        self.label_149.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_107.addWidget(self.label_149)


        self.gridLayout_26.addLayout(self.verticalLayout_107, 1, 0, 1, 1)

        self.lineEdit_24 = QLineEdit(self.widget_64)
        self.lineEdit_24.setObjectName(u"lineEdit_24")
        self.lineEdit_24.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_26.addWidget(self.lineEdit_24, 1, 1, 1, 1)

        self.gridLayout_26.setColumnStretch(0, 5)
        self.gridLayout_26.setColumnStretch(1, 2)

        self.verticalLayout_105.addLayout(self.gridLayout_26)


        self.verticalLayout_104.addWidget(self.widget_64, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_29.setWidget(self.scrollAreaWidgetContents_26)

        self.horizontalLayout_33.addWidget(self.scrollArea_29)

        self.horizontalSpacer_52 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_33.addItem(self.horizontalSpacer_52)

        self.horizontalLayout_33.setStretch(0, 1)
        self.horizontalLayout_33.setStretch(1, 5)
        self.horizontalLayout_33.setStretch(2, 1)

        self.horizontalLayout_52.addWidget(self.widget_63)

        self.stackedWidget.addWidget(self.QingKongYouJian_widget)
        self.XiuXingZhiLu_widget = QWidget()
        self.XiuXingZhiLu_widget.setObjectName(u"XiuXingZhiLu_widget")
        self.horizontalLayout_53 = QHBoxLayout(self.XiuXingZhiLu_widget)
        self.horizontalLayout_53.setObjectName(u"horizontalLayout_53")
        self.widget_75 = QWidget(self.XiuXingZhiLu_widget)
        self.widget_75.setObjectName(u"widget_75")
        self.widget_75.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_39 = QHBoxLayout(self.widget_75)
        self.horizontalLayout_39.setObjectName(u"horizontalLayout_39")
        self.horizontalSpacer_63 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_39.addItem(self.horizontalSpacer_63)

        self.scrollArea_35 = QScrollArea(self.widget_75)
        self.scrollArea_35.setObjectName(u"scrollArea_35")
        self.scrollArea_35.setMinimumSize(QSize(600, 0))
        self.scrollArea_35.setWidgetResizable(True)
        self.scrollAreaWidgetContents_32 = QWidget()
        self.scrollAreaWidgetContents_32.setObjectName(u"scrollAreaWidgetContents_32")
        self.scrollAreaWidgetContents_32.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_128 = QVBoxLayout(self.scrollAreaWidgetContents_32)
        self.verticalLayout_128.setSpacing(10)
        self.verticalLayout_128.setObjectName(u"verticalLayout_128")
        self.verticalLayout_128.setContentsMargins(10, -1, 10, -1)
        self.widget_76 = QWidget(self.scrollAreaWidgetContents_32)
        self.widget_76.setObjectName(u"widget_76")
        self.widget_76.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_129 = QVBoxLayout(self.widget_76)
        self.verticalLayout_129.setObjectName(u"verticalLayout_129")
        self.label_99 = QLabel(self.widget_76)
        self.label_99.setObjectName(u"label_99")
        self.label_99.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_129.addWidget(self.label_99)

        self.line_35 = QFrame(self.widget_76)
        self.line_35.setObjectName(u"line_35")
        sizePolicy1.setHeightForWidth(self.line_35.sizePolicy().hasHeightForWidth())
        self.line_35.setSizePolicy(sizePolicy1)
        self.line_35.setStyleSheet(u"")
        self.line_35.setLineWidth(0)
        self.line_35.setMidLineWidth(2)
        self.line_35.setFrameShape(QFrame.Shape.HLine)
        self.line_35.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_129.addWidget(self.line_35)

        self.gridLayout_32 = QGridLayout()
        self.gridLayout_32.setObjectName(u"gridLayout_32")
        self.gridLayout_32.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_130 = QVBoxLayout()
        self.verticalLayout_130.setObjectName(u"verticalLayout_130")
        self.label_100 = QLabel(self.widget_76)
        self.label_100.setObjectName(u"label_100")

        self.verticalLayout_130.addWidget(self.label_100)

        self.label_101 = QLabel(self.widget_76)
        self.label_101.setObjectName(u"label_101")
        self.label_101.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_130.addWidget(self.label_101)


        self.gridLayout_32.addLayout(self.verticalLayout_130, 0, 0, 1, 1)

        self.checkBox_32 = QCheckBox(self.widget_76)
        self.checkBox_32.setObjectName(u"checkBox_32")
        self.checkBox_32.setStyleSheet(u"")

        self.gridLayout_32.addWidget(self.checkBox_32, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_131 = QVBoxLayout()
        self.verticalLayout_131.setObjectName(u"verticalLayout_131")
        self.label_160 = QLabel(self.widget_76)
        self.label_160.setObjectName(u"label_160")

        self.verticalLayout_131.addWidget(self.label_160)

        self.label_161 = QLabel(self.widget_76)
        self.label_161.setObjectName(u"label_161")
        self.label_161.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_131.addWidget(self.label_161)


        self.gridLayout_32.addLayout(self.verticalLayout_131, 1, 0, 1, 1)

        self.lineEdit_30 = QLineEdit(self.widget_76)
        self.lineEdit_30.setObjectName(u"lineEdit_30")
        self.lineEdit_30.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_32.addWidget(self.lineEdit_30, 1, 1, 1, 1)

        self.gridLayout_32.setColumnStretch(0, 5)
        self.gridLayout_32.setColumnStretch(1, 2)

        self.verticalLayout_129.addLayout(self.gridLayout_32)


        self.verticalLayout_128.addWidget(self.widget_76, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_35.setWidget(self.scrollAreaWidgetContents_32)

        self.horizontalLayout_39.addWidget(self.scrollArea_35)

        self.horizontalSpacer_64 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_39.addItem(self.horizontalSpacer_64)

        self.horizontalLayout_39.setStretch(0, 1)
        self.horizontalLayout_39.setStretch(1, 5)
        self.horizontalLayout_39.setStretch(2, 1)

        self.horizontalLayout_53.addWidget(self.widget_75)

        self.stackedWidget.addWidget(self.XiuXingZhiLu_widget)
        self.RenFaTieDianZanFenXiang_widget = QWidget()
        self.RenFaTieDianZanFenXiang_widget.setObjectName(u"RenFaTieDianZanFenXiang_widget")
        self.horizontalLayout_54 = QHBoxLayout(self.RenFaTieDianZanFenXiang_widget)
        self.horizontalLayout_54.setObjectName(u"horizontalLayout_54")
        self.widget_65 = QWidget(self.RenFaTieDianZanFenXiang_widget)
        self.widget_65.setObjectName(u"widget_65")
        self.widget_65.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_34 = QHBoxLayout(self.widget_65)
        self.horizontalLayout_34.setObjectName(u"horizontalLayout_34")
        self.horizontalSpacer_53 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_34.addItem(self.horizontalSpacer_53)

        self.scrollArea_30 = QScrollArea(self.widget_65)
        self.scrollArea_30.setObjectName(u"scrollArea_30")
        self.scrollArea_30.setMinimumSize(QSize(600, 0))
        self.scrollArea_30.setWidgetResizable(True)
        self.scrollAreaWidgetContents_27 = QWidget()
        self.scrollAreaWidgetContents_27.setObjectName(u"scrollAreaWidgetContents_27")
        self.scrollAreaWidgetContents_27.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_108 = QVBoxLayout(self.scrollAreaWidgetContents_27)
        self.verticalLayout_108.setSpacing(10)
        self.verticalLayout_108.setObjectName(u"verticalLayout_108")
        self.verticalLayout_108.setContentsMargins(10, -1, 10, -1)
        self.widget_66 = QWidget(self.scrollAreaWidgetContents_27)
        self.widget_66.setObjectName(u"widget_66")
        self.widget_66.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_109 = QVBoxLayout(self.widget_66)
        self.verticalLayout_109.setObjectName(u"verticalLayout_109")
        self.label_84 = QLabel(self.widget_66)
        self.label_84.setObjectName(u"label_84")
        self.label_84.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_109.addWidget(self.label_84)

        self.line_30 = QFrame(self.widget_66)
        self.line_30.setObjectName(u"line_30")
        sizePolicy1.setHeightForWidth(self.line_30.sizePolicy().hasHeightForWidth())
        self.line_30.setSizePolicy(sizePolicy1)
        self.line_30.setStyleSheet(u"")
        self.line_30.setLineWidth(0)
        self.line_30.setMidLineWidth(2)
        self.line_30.setFrameShape(QFrame.Shape.HLine)
        self.line_30.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_109.addWidget(self.line_30)

        self.gridLayout_27 = QGridLayout()
        self.gridLayout_27.setObjectName(u"gridLayout_27")
        self.gridLayout_27.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_110 = QVBoxLayout()
        self.verticalLayout_110.setObjectName(u"verticalLayout_110")
        self.label_85 = QLabel(self.widget_66)
        self.label_85.setObjectName(u"label_85")

        self.verticalLayout_110.addWidget(self.label_85)

        self.label_86 = QLabel(self.widget_66)
        self.label_86.setObjectName(u"label_86")
        self.label_86.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_110.addWidget(self.label_86)


        self.gridLayout_27.addLayout(self.verticalLayout_110, 0, 0, 1, 1)

        self.checkBox_27 = QCheckBox(self.widget_66)
        self.checkBox_27.setObjectName(u"checkBox_27")
        self.checkBox_27.setStyleSheet(u"")

        self.gridLayout_27.addWidget(self.checkBox_27, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_111 = QVBoxLayout()
        self.verticalLayout_111.setObjectName(u"verticalLayout_111")
        self.label_150 = QLabel(self.widget_66)
        self.label_150.setObjectName(u"label_150")

        self.verticalLayout_111.addWidget(self.label_150)

        self.label_151 = QLabel(self.widget_66)
        self.label_151.setObjectName(u"label_151")
        self.label_151.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_111.addWidget(self.label_151)


        self.gridLayout_27.addLayout(self.verticalLayout_111, 1, 0, 1, 1)

        self.lineEdit_25 = QLineEdit(self.widget_66)
        self.lineEdit_25.setObjectName(u"lineEdit_25")
        self.lineEdit_25.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_27.addWidget(self.lineEdit_25, 1, 1, 1, 1)

        self.gridLayout_27.setColumnStretch(0, 5)
        self.gridLayout_27.setColumnStretch(1, 2)

        self.verticalLayout_109.addLayout(self.gridLayout_27)


        self.verticalLayout_108.addWidget(self.widget_66, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_30.setWidget(self.scrollAreaWidgetContents_27)

        self.horizontalLayout_34.addWidget(self.scrollArea_30)

        self.horizontalSpacer_54 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_34.addItem(self.horizontalSpacer_54)

        self.horizontalLayout_34.setStretch(0, 1)
        self.horizontalLayout_34.setStretch(1, 5)
        self.horizontalLayout_34.setStretch(2, 1)

        self.horizontalLayout_54.addWidget(self.widget_65)

        self.stackedWidget.addWidget(self.RenFaTieDianZanFenXiang_widget)
        self.TuanBen_widget = QWidget()
        self.TuanBen_widget.setObjectName(u"TuanBen_widget")
        self.horizontalLayout_55 = QHBoxLayout(self.TuanBen_widget)
        self.horizontalLayout_55.setObjectName(u"horizontalLayout_55")
        self.widget_73 = QWidget(self.TuanBen_widget)
        self.widget_73.setObjectName(u"widget_73")
        self.widget_73.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_38 = QHBoxLayout(self.widget_73)
        self.horizontalLayout_38.setObjectName(u"horizontalLayout_38")
        self.horizontalSpacer_61 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_38.addItem(self.horizontalSpacer_61)

        self.scrollArea_34 = QScrollArea(self.widget_73)
        self.scrollArea_34.setObjectName(u"scrollArea_34")
        self.scrollArea_34.setMinimumSize(QSize(600, 0))
        self.scrollArea_34.setWidgetResizable(True)
        self.scrollAreaWidgetContents_31 = QWidget()
        self.scrollAreaWidgetContents_31.setObjectName(u"scrollAreaWidgetContents_31")
        self.scrollAreaWidgetContents_31.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_124 = QVBoxLayout(self.scrollAreaWidgetContents_31)
        self.verticalLayout_124.setSpacing(10)
        self.verticalLayout_124.setObjectName(u"verticalLayout_124")
        self.verticalLayout_124.setContentsMargins(10, -1, 10, -1)
        self.widget_74 = QWidget(self.scrollAreaWidgetContents_31)
        self.widget_74.setObjectName(u"widget_74")
        self.widget_74.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_125 = QVBoxLayout(self.widget_74)
        self.verticalLayout_125.setObjectName(u"verticalLayout_125")
        self.label_96 = QLabel(self.widget_74)
        self.label_96.setObjectName(u"label_96")
        self.label_96.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_125.addWidget(self.label_96)

        self.line_34 = QFrame(self.widget_74)
        self.line_34.setObjectName(u"line_34")
        sizePolicy1.setHeightForWidth(self.line_34.sizePolicy().hasHeightForWidth())
        self.line_34.setSizePolicy(sizePolicy1)
        self.line_34.setStyleSheet(u"")
        self.line_34.setLineWidth(0)
        self.line_34.setMidLineWidth(2)
        self.line_34.setFrameShape(QFrame.Shape.HLine)
        self.line_34.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_125.addWidget(self.line_34)

        self.gridLayout_31 = QGridLayout()
        self.gridLayout_31.setObjectName(u"gridLayout_31")
        self.gridLayout_31.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_126 = QVBoxLayout()
        self.verticalLayout_126.setObjectName(u"verticalLayout_126")
        self.label_97 = QLabel(self.widget_74)
        self.label_97.setObjectName(u"label_97")

        self.verticalLayout_126.addWidget(self.label_97)

        self.label_98 = QLabel(self.widget_74)
        self.label_98.setObjectName(u"label_98")
        self.label_98.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_126.addWidget(self.label_98)


        self.gridLayout_31.addLayout(self.verticalLayout_126, 0, 0, 1, 1)

        self.checkBox_31 = QCheckBox(self.widget_74)
        self.checkBox_31.setObjectName(u"checkBox_31")
        self.checkBox_31.setStyleSheet(u"")

        self.gridLayout_31.addWidget(self.checkBox_31, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_127 = QVBoxLayout()
        self.verticalLayout_127.setObjectName(u"verticalLayout_127")
        self.label_158 = QLabel(self.widget_74)
        self.label_158.setObjectName(u"label_158")

        self.verticalLayout_127.addWidget(self.label_158)

        self.label_159 = QLabel(self.widget_74)
        self.label_159.setObjectName(u"label_159")
        self.label_159.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_127.addWidget(self.label_159)


        self.gridLayout_31.addLayout(self.verticalLayout_127, 1, 0, 1, 1)

        self.lineEdit_29 = QLineEdit(self.widget_74)
        self.lineEdit_29.setObjectName(u"lineEdit_29")
        self.lineEdit_29.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_31.addWidget(self.lineEdit_29, 1, 1, 1, 1)

        self.gridLayout_31.setColumnStretch(0, 5)
        self.gridLayout_31.setColumnStretch(1, 2)

        self.verticalLayout_125.addLayout(self.gridLayout_31)


        self.verticalLayout_124.addWidget(self.widget_74, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_34.setWidget(self.scrollAreaWidgetContents_31)

        self.horizontalLayout_38.addWidget(self.scrollArea_34)

        self.horizontalSpacer_62 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_38.addItem(self.horizontalSpacer_62)

        self.horizontalLayout_38.setStretch(0, 1)
        self.horizontalLayout_38.setStretch(1, 5)
        self.horizontalLayout_38.setStretch(2, 1)

        self.horizontalLayout_55.addWidget(self.widget_73)

        self.stackedWidget.addWidget(self.TuanBen_widget)
        self.YaoSaiZhengDuoZhan_widget = QWidget()
        self.YaoSaiZhengDuoZhan_widget.setObjectName(u"YaoSaiZhengDuoZhan_widget")
        self.horizontalLayout_56 = QHBoxLayout(self.YaoSaiZhengDuoZhan_widget)
        self.horizontalLayout_56.setObjectName(u"horizontalLayout_56")
        self.widget_77 = QWidget(self.YaoSaiZhengDuoZhan_widget)
        self.widget_77.setObjectName(u"widget_77")
        self.widget_77.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_40 = QHBoxLayout(self.widget_77)
        self.horizontalLayout_40.setObjectName(u"horizontalLayout_40")
        self.horizontalSpacer_65 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_40.addItem(self.horizontalSpacer_65)

        self.scrollArea_36 = QScrollArea(self.widget_77)
        self.scrollArea_36.setObjectName(u"scrollArea_36")
        self.scrollArea_36.setMinimumSize(QSize(600, 0))
        self.scrollArea_36.setWidgetResizable(True)
        self.scrollAreaWidgetContents_33 = QWidget()
        self.scrollAreaWidgetContents_33.setObjectName(u"scrollAreaWidgetContents_33")
        self.scrollAreaWidgetContents_33.setGeometry(QRect(0, 0, 730, 536))
        self.verticalLayout_132 = QVBoxLayout(self.scrollAreaWidgetContents_33)
        self.verticalLayout_132.setSpacing(10)
        self.verticalLayout_132.setObjectName(u"verticalLayout_132")
        self.verticalLayout_132.setContentsMargins(10, -1, 10, -1)
        self.widget_78 = QWidget(self.scrollAreaWidgetContents_33)
        self.widget_78.setObjectName(u"widget_78")
        self.widget_78.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_133 = QVBoxLayout(self.widget_78)
        self.verticalLayout_133.setObjectName(u"verticalLayout_133")
        self.label_162 = QLabel(self.widget_78)
        self.label_162.setObjectName(u"label_162")
        self.label_162.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_133.addWidget(self.label_162)

        self.line_36 = QFrame(self.widget_78)
        self.line_36.setObjectName(u"line_36")
        sizePolicy1.setHeightForWidth(self.line_36.sizePolicy().hasHeightForWidth())
        self.line_36.setSizePolicy(sizePolicy1)
        self.line_36.setStyleSheet(u"")
        self.line_36.setLineWidth(0)
        self.line_36.setMidLineWidth(2)
        self.line_36.setFrameShape(QFrame.Shape.HLine)
        self.line_36.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_133.addWidget(self.line_36)

        self.gridLayout_33 = QGridLayout()
        self.gridLayout_33.setObjectName(u"gridLayout_33")
        self.gridLayout_33.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_134 = QVBoxLayout()
        self.verticalLayout_134.setObjectName(u"verticalLayout_134")
        self.label_163 = QLabel(self.widget_78)
        self.label_163.setObjectName(u"label_163")

        self.verticalLayout_134.addWidget(self.label_163)

        self.label_164 = QLabel(self.widget_78)
        self.label_164.setObjectName(u"label_164")
        self.label_164.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_134.addWidget(self.label_164)


        self.gridLayout_33.addLayout(self.verticalLayout_134, 0, 0, 1, 1)

        self.checkBox_33 = QCheckBox(self.widget_78)
        self.checkBox_33.setObjectName(u"checkBox_33")
        self.checkBox_33.setStyleSheet(u"")

        self.gridLayout_33.addWidget(self.checkBox_33, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_135 = QVBoxLayout()
        self.verticalLayout_135.setObjectName(u"verticalLayout_135")
        self.label_165 = QLabel(self.widget_78)
        self.label_165.setObjectName(u"label_165")

        self.verticalLayout_135.addWidget(self.label_165)

        self.label_166 = QLabel(self.widget_78)
        self.label_166.setObjectName(u"label_166")
        self.label_166.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_135.addWidget(self.label_166)


        self.gridLayout_33.addLayout(self.verticalLayout_135, 1, 0, 1, 1)

        self.lineEdit_31 = QLineEdit(self.widget_78)
        self.lineEdit_31.setObjectName(u"lineEdit_31")
        self.lineEdit_31.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_33.addWidget(self.lineEdit_31, 1, 1, 1, 1)

        self.gridLayout_33.setColumnStretch(0, 5)
        self.gridLayout_33.setColumnStretch(1, 2)

        self.verticalLayout_133.addLayout(self.gridLayout_33)


        self.verticalLayout_132.addWidget(self.widget_78, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_36.setWidget(self.scrollAreaWidgetContents_33)

        self.horizontalLayout_40.addWidget(self.scrollArea_36)

        self.horizontalSpacer_66 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_40.addItem(self.horizontalSpacer_66)

        self.horizontalLayout_40.setStretch(0, 1)
        self.horizontalLayout_40.setStretch(1, 5)
        self.horizontalLayout_40.setStretch(2, 1)

        self.horizontalLayout_56.addWidget(self.widget_77)

        self.stackedWidget.addWidget(self.YaoSaiZhengDuoZhan_widget)
        self.PanRenLaiXi_widget = QWidget()
        self.PanRenLaiXi_widget.setObjectName(u"PanRenLaiXi_widget")
        self.horizontalLayout_57 = QHBoxLayout(self.PanRenLaiXi_widget)
        self.horizontalLayout_57.setObjectName(u"horizontalLayout_57")
        self.widget_59 = QWidget(self.PanRenLaiXi_widget)
        self.widget_59.setObjectName(u"widget_59")
        self.widget_59.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_31 = QHBoxLayout(self.widget_59)
        self.horizontalLayout_31.setObjectName(u"horizontalLayout_31")
        self.horizontalSpacer_47 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_31.addItem(self.horizontalSpacer_47)

        self.scrollArea_27 = QScrollArea(self.widget_59)
        self.scrollArea_27.setObjectName(u"scrollArea_27")
        self.scrollArea_27.setMinimumSize(QSize(600, 0))
        self.scrollArea_27.setWidgetResizable(True)
        self.scrollAreaWidgetContents_24 = QWidget()
        self.scrollAreaWidgetContents_24.setObjectName(u"scrollAreaWidgetContents_24")
        self.scrollAreaWidgetContents_24.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_96 = QVBoxLayout(self.scrollAreaWidgetContents_24)
        self.verticalLayout_96.setSpacing(10)
        self.verticalLayout_96.setObjectName(u"verticalLayout_96")
        self.verticalLayout_96.setContentsMargins(10, -1, 10, -1)
        self.widget_60 = QWidget(self.scrollAreaWidgetContents_24)
        self.widget_60.setObjectName(u"widget_60")
        self.widget_60.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_97 = QVBoxLayout(self.widget_60)
        self.verticalLayout_97.setObjectName(u"verticalLayout_97")
        self.label_75 = QLabel(self.widget_60)
        self.label_75.setObjectName(u"label_75")
        self.label_75.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_97.addWidget(self.label_75)

        self.line_27 = QFrame(self.widget_60)
        self.line_27.setObjectName(u"line_27")
        sizePolicy1.setHeightForWidth(self.line_27.sizePolicy().hasHeightForWidth())
        self.line_27.setSizePolicy(sizePolicy1)
        self.line_27.setStyleSheet(u"")
        self.line_27.setLineWidth(0)
        self.line_27.setMidLineWidth(2)
        self.line_27.setFrameShape(QFrame.Shape.HLine)
        self.line_27.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_97.addWidget(self.line_27)

        self.gridLayout_24 = QGridLayout()
        self.gridLayout_24.setObjectName(u"gridLayout_24")
        self.gridLayout_24.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_98 = QVBoxLayout()
        self.verticalLayout_98.setObjectName(u"verticalLayout_98")
        self.label_76 = QLabel(self.widget_60)
        self.label_76.setObjectName(u"label_76")

        self.verticalLayout_98.addWidget(self.label_76)

        self.label_77 = QLabel(self.widget_60)
        self.label_77.setObjectName(u"label_77")
        self.label_77.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_98.addWidget(self.label_77)


        self.gridLayout_24.addLayout(self.verticalLayout_98, 0, 0, 1, 1)

        self.checkBox_24 = QCheckBox(self.widget_60)
        self.checkBox_24.setObjectName(u"checkBox_24")
        self.checkBox_24.setStyleSheet(u"")

        self.gridLayout_24.addWidget(self.checkBox_24, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_99 = QVBoxLayout()
        self.verticalLayout_99.setObjectName(u"verticalLayout_99")
        self.label_144 = QLabel(self.widget_60)
        self.label_144.setObjectName(u"label_144")

        self.verticalLayout_99.addWidget(self.label_144)

        self.label_145 = QLabel(self.widget_60)
        self.label_145.setObjectName(u"label_145")
        self.label_145.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_99.addWidget(self.label_145)


        self.gridLayout_24.addLayout(self.verticalLayout_99, 1, 0, 1, 1)

        self.lineEdit_22 = QLineEdit(self.widget_60)
        self.lineEdit_22.setObjectName(u"lineEdit_22")
        self.lineEdit_22.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_24.addWidget(self.lineEdit_22, 1, 1, 1, 1)

        self.gridLayout_24.setColumnStretch(0, 5)
        self.gridLayout_24.setColumnStretch(1, 2)

        self.verticalLayout_97.addLayout(self.gridLayout_24)


        self.verticalLayout_96.addWidget(self.widget_60, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_27.setWidget(self.scrollAreaWidgetContents_24)

        self.horizontalLayout_31.addWidget(self.scrollArea_27)

        self.horizontalSpacer_48 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_31.addItem(self.horizontalSpacer_48)

        self.horizontalLayout_31.setStretch(0, 1)
        self.horizontalLayout_31.setStretch(1, 5)
        self.horizontalLayout_31.setStretch(2, 1)

        self.horizontalLayout_57.addWidget(self.widget_59)

        self.stackedWidget.addWidget(self.PanRenLaiXi_widget)
        self.KuaFuZhengBaSai_widget = QWidget()
        self.KuaFuZhengBaSai_widget.setObjectName(u"KuaFuZhengBaSai_widget")
        self.horizontalLayout_58 = QHBoxLayout(self.KuaFuZhengBaSai_widget)
        self.horizontalLayout_58.setObjectName(u"horizontalLayout_58")
        self.widget_47 = QWidget(self.KuaFuZhengBaSai_widget)
        self.widget_47.setObjectName(u"widget_47")
        self.widget_47.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_25 = QHBoxLayout(self.widget_47)
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.horizontalSpacer_35 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_25.addItem(self.horizontalSpacer_35)

        self.scrollArea_21 = QScrollArea(self.widget_47)
        self.scrollArea_21.setObjectName(u"scrollArea_21")
        self.scrollArea_21.setMinimumSize(QSize(600, 0))
        self.scrollArea_21.setWidgetResizable(True)
        self.scrollAreaWidgetContents_18 = QWidget()
        self.scrollAreaWidgetContents_18.setObjectName(u"scrollAreaWidgetContents_18")
        self.scrollAreaWidgetContents_18.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_72 = QVBoxLayout(self.scrollAreaWidgetContents_18)
        self.verticalLayout_72.setSpacing(10)
        self.verticalLayout_72.setObjectName(u"verticalLayout_72")
        self.verticalLayout_72.setContentsMargins(10, -1, 10, -1)
        self.widget_48 = QWidget(self.scrollAreaWidgetContents_18)
        self.widget_48.setObjectName(u"widget_48")
        self.widget_48.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_73 = QVBoxLayout(self.widget_48)
        self.verticalLayout_73.setObjectName(u"verticalLayout_73")
        self.label_57 = QLabel(self.widget_48)
        self.label_57.setObjectName(u"label_57")
        self.label_57.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_73.addWidget(self.label_57)

        self.line_21 = QFrame(self.widget_48)
        self.line_21.setObjectName(u"line_21")
        sizePolicy1.setHeightForWidth(self.line_21.sizePolicy().hasHeightForWidth())
        self.line_21.setSizePolicy(sizePolicy1)
        self.line_21.setStyleSheet(u"")
        self.line_21.setLineWidth(0)
        self.line_21.setMidLineWidth(2)
        self.line_21.setFrameShape(QFrame.Shape.HLine)
        self.line_21.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_73.addWidget(self.line_21)

        self.gridLayout_18 = QGridLayout()
        self.gridLayout_18.setObjectName(u"gridLayout_18")
        self.gridLayout_18.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_74 = QVBoxLayout()
        self.verticalLayout_74.setObjectName(u"verticalLayout_74")
        self.label_58 = QLabel(self.widget_48)
        self.label_58.setObjectName(u"label_58")

        self.verticalLayout_74.addWidget(self.label_58)

        self.label_59 = QLabel(self.widget_48)
        self.label_59.setObjectName(u"label_59")
        self.label_59.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_74.addWidget(self.label_59)


        self.gridLayout_18.addLayout(self.verticalLayout_74, 0, 0, 1, 1)

        self.checkBox_18 = QCheckBox(self.widget_48)
        self.checkBox_18.setObjectName(u"checkBox_18")
        self.checkBox_18.setStyleSheet(u"")

        self.gridLayout_18.addWidget(self.checkBox_18, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_75 = QVBoxLayout()
        self.verticalLayout_75.setObjectName(u"verticalLayout_75")
        self.label_132 = QLabel(self.widget_48)
        self.label_132.setObjectName(u"label_132")

        self.verticalLayout_75.addWidget(self.label_132)

        self.label_133 = QLabel(self.widget_48)
        self.label_133.setObjectName(u"label_133")
        self.label_133.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_75.addWidget(self.label_133)


        self.gridLayout_18.addLayout(self.verticalLayout_75, 1, 0, 1, 1)

        self.lineEdit_16 = QLineEdit(self.widget_48)
        self.lineEdit_16.setObjectName(u"lineEdit_16")
        self.lineEdit_16.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_18.addWidget(self.lineEdit_16, 1, 1, 1, 1)

        self.gridLayout_18.setColumnStretch(0, 5)
        self.gridLayout_18.setColumnStretch(1, 2)

        self.verticalLayout_73.addLayout(self.gridLayout_18)


        self.verticalLayout_72.addWidget(self.widget_48, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_21.setWidget(self.scrollAreaWidgetContents_18)

        self.horizontalLayout_25.addWidget(self.scrollArea_21)

        self.horizontalSpacer_36 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_25.addItem(self.horizontalSpacer_36)

        self.horizontalLayout_25.setStretch(0, 1)
        self.horizontalLayout_25.setStretch(1, 5)
        self.horizontalLayout_25.setStretch(2, 1)

        self.horizontalLayout_58.addWidget(self.widget_47)

        self.stackedWidget.addWidget(self.KuaFuZhengBaSai_widget)
        self.GaoJiRenZheZhaoMu_widget = QWidget()
        self.GaoJiRenZheZhaoMu_widget.setObjectName(u"GaoJiRenZheZhaoMu_widget")
        self.horizontalLayout_59 = QHBoxLayout(self.GaoJiRenZheZhaoMu_widget)
        self.horizontalLayout_59.setObjectName(u"horizontalLayout_59")
        self.widget_41 = QWidget(self.GaoJiRenZheZhaoMu_widget)
        self.widget_41.setObjectName(u"widget_41")
        self.widget_41.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_22 = QHBoxLayout(self.widget_41)
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.horizontalSpacer_29 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_22.addItem(self.horizontalSpacer_29)

        self.scrollArea_18 = QScrollArea(self.widget_41)
        self.scrollArea_18.setObjectName(u"scrollArea_18")
        self.scrollArea_18.setMinimumSize(QSize(600, 0))
        self.scrollArea_18.setWidgetResizable(True)
        self.scrollAreaWidgetContents_15 = QWidget()
        self.scrollAreaWidgetContents_15.setObjectName(u"scrollAreaWidgetContents_15")
        self.scrollAreaWidgetContents_15.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_60 = QVBoxLayout(self.scrollAreaWidgetContents_15)
        self.verticalLayout_60.setSpacing(10)
        self.verticalLayout_60.setObjectName(u"verticalLayout_60")
        self.verticalLayout_60.setContentsMargins(10, -1, 10, -1)
        self.widget_42 = QWidget(self.scrollAreaWidgetContents_15)
        self.widget_42.setObjectName(u"widget_42")
        self.widget_42.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_61 = QVBoxLayout(self.widget_42)
        self.verticalLayout_61.setObjectName(u"verticalLayout_61")
        self.label_48 = QLabel(self.widget_42)
        self.label_48.setObjectName(u"label_48")
        self.label_48.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_61.addWidget(self.label_48)

        self.line_18 = QFrame(self.widget_42)
        self.line_18.setObjectName(u"line_18")
        sizePolicy1.setHeightForWidth(self.line_18.sizePolicy().hasHeightForWidth())
        self.line_18.setSizePolicy(sizePolicy1)
        self.line_18.setStyleSheet(u"")
        self.line_18.setLineWidth(0)
        self.line_18.setMidLineWidth(2)
        self.line_18.setFrameShape(QFrame.Shape.HLine)
        self.line_18.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_61.addWidget(self.line_18)

        self.gridLayout_15 = QGridLayout()
        self.gridLayout_15.setObjectName(u"gridLayout_15")
        self.gridLayout_15.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_62 = QVBoxLayout()
        self.verticalLayout_62.setObjectName(u"verticalLayout_62")
        self.label_49 = QLabel(self.widget_42)
        self.label_49.setObjectName(u"label_49")

        self.verticalLayout_62.addWidget(self.label_49)

        self.label_50 = QLabel(self.widget_42)
        self.label_50.setObjectName(u"label_50")
        self.label_50.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_62.addWidget(self.label_50)


        self.gridLayout_15.addLayout(self.verticalLayout_62, 0, 0, 1, 1)

        self.checkBox_15 = QCheckBox(self.widget_42)
        self.checkBox_15.setObjectName(u"checkBox_15")
        self.checkBox_15.setStyleSheet(u"")

        self.gridLayout_15.addWidget(self.checkBox_15, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_63 = QVBoxLayout()
        self.verticalLayout_63.setObjectName(u"verticalLayout_63")
        self.label_126 = QLabel(self.widget_42)
        self.label_126.setObjectName(u"label_126")

        self.verticalLayout_63.addWidget(self.label_126)

        self.label_127 = QLabel(self.widget_42)
        self.label_127.setObjectName(u"label_127")
        self.label_127.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_63.addWidget(self.label_127)


        self.gridLayout_15.addLayout(self.verticalLayout_63, 1, 0, 1, 1)

        self.lineEdit_13 = QLineEdit(self.widget_42)
        self.lineEdit_13.setObjectName(u"lineEdit_13")
        self.lineEdit_13.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_15.addWidget(self.lineEdit_13, 1, 1, 1, 1)

        self.gridLayout_15.setColumnStretch(0, 5)
        self.gridLayout_15.setColumnStretch(1, 2)

        self.verticalLayout_61.addLayout(self.gridLayout_15)


        self.verticalLayout_60.addWidget(self.widget_42, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_18.setWidget(self.scrollAreaWidgetContents_15)

        self.horizontalLayout_22.addWidget(self.scrollArea_18)

        self.horizontalSpacer_30 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_22.addItem(self.horizontalSpacer_30)

        self.horizontalLayout_22.setStretch(0, 1)
        self.horizontalLayout_22.setStretch(1, 5)
        self.horizontalLayout_22.setStretch(2, 1)

        self.horizontalLayout_59.addWidget(self.widget_41)

        self.stackedWidget.addWidget(self.GaoJiRenZheZhaoMu_widget)
        self.MeiZhouShengChang_widget = QWidget()
        self.MeiZhouShengChang_widget.setObjectName(u"MeiZhouShengChang_widget")
        self.horizontalLayout_60 = QHBoxLayout(self.MeiZhouShengChang_widget)
        self.horizontalLayout_60.setObjectName(u"horizontalLayout_60")
        self.widget_55 = QWidget(self.MeiZhouShengChang_widget)
        self.widget_55.setObjectName(u"widget_55")
        self.widget_55.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_29 = QHBoxLayout(self.widget_55)
        self.horizontalLayout_29.setObjectName(u"horizontalLayout_29")
        self.horizontalSpacer_43 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_29.addItem(self.horizontalSpacer_43)

        self.scrollArea_25 = QScrollArea(self.widget_55)
        self.scrollArea_25.setObjectName(u"scrollArea_25")
        self.scrollArea_25.setMinimumSize(QSize(600, 0))
        self.scrollArea_25.setWidgetResizable(True)
        self.scrollAreaWidgetContents_22 = QWidget()
        self.scrollAreaWidgetContents_22.setObjectName(u"scrollAreaWidgetContents_22")
        self.scrollAreaWidgetContents_22.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_88 = QVBoxLayout(self.scrollAreaWidgetContents_22)
        self.verticalLayout_88.setSpacing(10)
        self.verticalLayout_88.setObjectName(u"verticalLayout_88")
        self.verticalLayout_88.setContentsMargins(10, -1, 10, -1)
        self.widget_56 = QWidget(self.scrollAreaWidgetContents_22)
        self.widget_56.setObjectName(u"widget_56")
        self.widget_56.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_89 = QVBoxLayout(self.widget_56)
        self.verticalLayout_89.setObjectName(u"verticalLayout_89")
        self.label_69 = QLabel(self.widget_56)
        self.label_69.setObjectName(u"label_69")
        self.label_69.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_89.addWidget(self.label_69)

        self.line_25 = QFrame(self.widget_56)
        self.line_25.setObjectName(u"line_25")
        sizePolicy1.setHeightForWidth(self.line_25.sizePolicy().hasHeightForWidth())
        self.line_25.setSizePolicy(sizePolicy1)
        self.line_25.setStyleSheet(u"")
        self.line_25.setLineWidth(0)
        self.line_25.setMidLineWidth(2)
        self.line_25.setFrameShape(QFrame.Shape.HLine)
        self.line_25.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_89.addWidget(self.line_25)

        self.gridLayout_22 = QGridLayout()
        self.gridLayout_22.setObjectName(u"gridLayout_22")
        self.gridLayout_22.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_90 = QVBoxLayout()
        self.verticalLayout_90.setObjectName(u"verticalLayout_90")
        self.label_70 = QLabel(self.widget_56)
        self.label_70.setObjectName(u"label_70")

        self.verticalLayout_90.addWidget(self.label_70)

        self.label_71 = QLabel(self.widget_56)
        self.label_71.setObjectName(u"label_71")
        self.label_71.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_90.addWidget(self.label_71)


        self.gridLayout_22.addLayout(self.verticalLayout_90, 0, 0, 1, 1)

        self.checkBox_22 = QCheckBox(self.widget_56)
        self.checkBox_22.setObjectName(u"checkBox_22")
        self.checkBox_22.setStyleSheet(u"")

        self.gridLayout_22.addWidget(self.checkBox_22, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_91 = QVBoxLayout()
        self.verticalLayout_91.setObjectName(u"verticalLayout_91")
        self.label_140 = QLabel(self.widget_56)
        self.label_140.setObjectName(u"label_140")

        self.verticalLayout_91.addWidget(self.label_140)

        self.label_141 = QLabel(self.widget_56)
        self.label_141.setObjectName(u"label_141")
        self.label_141.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_91.addWidget(self.label_141)


        self.gridLayout_22.addLayout(self.verticalLayout_91, 1, 0, 1, 1)

        self.lineEdit_20 = QLineEdit(self.widget_56)
        self.lineEdit_20.setObjectName(u"lineEdit_20")
        self.lineEdit_20.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_22.addWidget(self.lineEdit_20, 1, 1, 1, 1)

        self.gridLayout_22.setColumnStretch(0, 5)
        self.gridLayout_22.setColumnStretch(1, 2)

        self.verticalLayout_89.addLayout(self.gridLayout_22)


        self.verticalLayout_88.addWidget(self.widget_56, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_25.setWidget(self.scrollAreaWidgetContents_22)

        self.horizontalLayout_29.addWidget(self.scrollArea_25)

        self.horizontalSpacer_44 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_29.addItem(self.horizontalSpacer_44)

        self.horizontalLayout_29.setStretch(0, 1)
        self.horizontalLayout_29.setStretch(1, 5)
        self.horizontalLayout_29.setStretch(2, 1)

        self.horizontalLayout_60.addWidget(self.widget_55)

        self.stackedWidget.addWidget(self.MeiZhouShengChang_widget)
        self.SaiJiShengChang_widget = QWidget()
        self.SaiJiShengChang_widget.setObjectName(u"SaiJiShengChang_widget")
        self.horizontalLayout_61 = QHBoxLayout(self.SaiJiShengChang_widget)
        self.horizontalLayout_61.setObjectName(u"horizontalLayout_61")
        self.widget_69 = QWidget(self.SaiJiShengChang_widget)
        self.widget_69.setObjectName(u"widget_69")
        self.widget_69.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_36 = QHBoxLayout(self.widget_69)
        self.horizontalLayout_36.setObjectName(u"horizontalLayout_36")
        self.horizontalSpacer_57 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_36.addItem(self.horizontalSpacer_57)

        self.scrollArea_32 = QScrollArea(self.widget_69)
        self.scrollArea_32.setObjectName(u"scrollArea_32")
        self.scrollArea_32.setMinimumSize(QSize(600, 0))
        self.scrollArea_32.setWidgetResizable(True)
        self.scrollAreaWidgetContents_29 = QWidget()
        self.scrollAreaWidgetContents_29.setObjectName(u"scrollAreaWidgetContents_29")
        self.scrollAreaWidgetContents_29.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_116 = QVBoxLayout(self.scrollAreaWidgetContents_29)
        self.verticalLayout_116.setSpacing(10)
        self.verticalLayout_116.setObjectName(u"verticalLayout_116")
        self.verticalLayout_116.setContentsMargins(10, -1, 10, -1)
        self.widget_70 = QWidget(self.scrollAreaWidgetContents_29)
        self.widget_70.setObjectName(u"widget_70")
        self.widget_70.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_117 = QVBoxLayout(self.widget_70)
        self.verticalLayout_117.setObjectName(u"verticalLayout_117")
        self.label_90 = QLabel(self.widget_70)
        self.label_90.setObjectName(u"label_90")
        self.label_90.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_117.addWidget(self.label_90)

        self.line_32 = QFrame(self.widget_70)
        self.line_32.setObjectName(u"line_32")
        sizePolicy1.setHeightForWidth(self.line_32.sizePolicy().hasHeightForWidth())
        self.line_32.setSizePolicy(sizePolicy1)
        self.line_32.setStyleSheet(u"")
        self.line_32.setLineWidth(0)
        self.line_32.setMidLineWidth(2)
        self.line_32.setFrameShape(QFrame.Shape.HLine)
        self.line_32.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_117.addWidget(self.line_32)

        self.gridLayout_29 = QGridLayout()
        self.gridLayout_29.setObjectName(u"gridLayout_29")
        self.gridLayout_29.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_118 = QVBoxLayout()
        self.verticalLayout_118.setObjectName(u"verticalLayout_118")
        self.label_91 = QLabel(self.widget_70)
        self.label_91.setObjectName(u"label_91")

        self.verticalLayout_118.addWidget(self.label_91)

        self.label_92 = QLabel(self.widget_70)
        self.label_92.setObjectName(u"label_92")
        self.label_92.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_118.addWidget(self.label_92)


        self.gridLayout_29.addLayout(self.verticalLayout_118, 0, 0, 1, 1)

        self.checkBox_29 = QCheckBox(self.widget_70)
        self.checkBox_29.setObjectName(u"checkBox_29")
        self.checkBox_29.setStyleSheet(u"")

        self.gridLayout_29.addWidget(self.checkBox_29, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_119 = QVBoxLayout()
        self.verticalLayout_119.setObjectName(u"verticalLayout_119")
        self.label_154 = QLabel(self.widget_70)
        self.label_154.setObjectName(u"label_154")

        self.verticalLayout_119.addWidget(self.label_154)

        self.label_155 = QLabel(self.widget_70)
        self.label_155.setObjectName(u"label_155")
        self.label_155.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_119.addWidget(self.label_155)


        self.gridLayout_29.addLayout(self.verticalLayout_119, 1, 0, 1, 1)

        self.lineEdit_27 = QLineEdit(self.widget_70)
        self.lineEdit_27.setObjectName(u"lineEdit_27")
        self.lineEdit_27.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_29.addWidget(self.lineEdit_27, 1, 1, 1, 1)

        self.gridLayout_29.setColumnStretch(0, 5)
        self.gridLayout_29.setColumnStretch(1, 2)

        self.verticalLayout_117.addLayout(self.gridLayout_29)


        self.verticalLayout_116.addWidget(self.widget_70, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_32.setWidget(self.scrollAreaWidgetContents_29)

        self.horizontalLayout_36.addWidget(self.scrollArea_32)

        self.horizontalSpacer_58 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_36.addItem(self.horizontalSpacer_58)

        self.horizontalLayout_36.setStretch(0, 1)
        self.horizontalLayout_36.setStretch(1, 5)
        self.horizontalLayout_36.setStretch(2, 1)

        self.horizontalLayout_61.addWidget(self.widget_69)

        self.stackedWidget.addWidget(self.SaiJiShengChang_widget)
        self.GengDuoWanFa_widget = QWidget()
        self.GengDuoWanFa_widget.setObjectName(u"GengDuoWanFa_widget")
        self.horizontalLayout_62 = QHBoxLayout(self.GengDuoWanFa_widget)
        self.horizontalLayout_62.setObjectName(u"horizontalLayout_62")
        self.widget_43 = QWidget(self.GengDuoWanFa_widget)
        self.widget_43.setObjectName(u"widget_43")
        self.widget_43.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_23 = QHBoxLayout(self.widget_43)
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.horizontalSpacer_31 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_23.addItem(self.horizontalSpacer_31)

        self.scrollArea_19 = QScrollArea(self.widget_43)
        self.scrollArea_19.setObjectName(u"scrollArea_19")
        self.scrollArea_19.setMinimumSize(QSize(600, 0))
        self.scrollArea_19.setWidgetResizable(True)
        self.scrollAreaWidgetContents_16 = QWidget()
        self.scrollAreaWidgetContents_16.setObjectName(u"scrollAreaWidgetContents_16")
        self.scrollAreaWidgetContents_16.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_64 = QVBoxLayout(self.scrollAreaWidgetContents_16)
        self.verticalLayout_64.setSpacing(10)
        self.verticalLayout_64.setObjectName(u"verticalLayout_64")
        self.verticalLayout_64.setContentsMargins(10, -1, 10, -1)
        self.widget_44 = QWidget(self.scrollAreaWidgetContents_16)
        self.widget_44.setObjectName(u"widget_44")
        self.widget_44.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_65 = QVBoxLayout(self.widget_44)
        self.verticalLayout_65.setObjectName(u"verticalLayout_65")
        self.label_51 = QLabel(self.widget_44)
        self.label_51.setObjectName(u"label_51")
        self.label_51.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_65.addWidget(self.label_51)

        self.line_19 = QFrame(self.widget_44)
        self.line_19.setObjectName(u"line_19")
        sizePolicy1.setHeightForWidth(self.line_19.sizePolicy().hasHeightForWidth())
        self.line_19.setSizePolicy(sizePolicy1)
        self.line_19.setStyleSheet(u"")
        self.line_19.setLineWidth(0)
        self.line_19.setMidLineWidth(2)
        self.line_19.setFrameShape(QFrame.Shape.HLine)
        self.line_19.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_65.addWidget(self.line_19)

        self.gridLayout_16 = QGridLayout()
        self.gridLayout_16.setObjectName(u"gridLayout_16")
        self.gridLayout_16.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_66 = QVBoxLayout()
        self.verticalLayout_66.setObjectName(u"verticalLayout_66")
        self.label_52 = QLabel(self.widget_44)
        self.label_52.setObjectName(u"label_52")

        self.verticalLayout_66.addWidget(self.label_52)

        self.label_53 = QLabel(self.widget_44)
        self.label_53.setObjectName(u"label_53")
        self.label_53.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_66.addWidget(self.label_53)


        self.gridLayout_16.addLayout(self.verticalLayout_66, 0, 0, 1, 1)

        self.checkBox_16 = QCheckBox(self.widget_44)
        self.checkBox_16.setObjectName(u"checkBox_16")
        self.checkBox_16.setStyleSheet(u"")

        self.gridLayout_16.addWidget(self.checkBox_16, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_67 = QVBoxLayout()
        self.verticalLayout_67.setObjectName(u"verticalLayout_67")
        self.label_128 = QLabel(self.widget_44)
        self.label_128.setObjectName(u"label_128")

        self.verticalLayout_67.addWidget(self.label_128)

        self.label_129 = QLabel(self.widget_44)
        self.label_129.setObjectName(u"label_129")
        self.label_129.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_67.addWidget(self.label_129)


        self.gridLayout_16.addLayout(self.verticalLayout_67, 1, 0, 1, 1)

        self.lineEdit_14 = QLineEdit(self.widget_44)
        self.lineEdit_14.setObjectName(u"lineEdit_14")
        self.lineEdit_14.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_16.addWidget(self.lineEdit_14, 1, 1, 1, 1)

        self.gridLayout_16.setColumnStretch(0, 5)
        self.gridLayout_16.setColumnStretch(1, 2)

        self.verticalLayout_65.addLayout(self.gridLayout_16)


        self.verticalLayout_64.addWidget(self.widget_44, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_19.setWidget(self.scrollAreaWidgetContents_16)

        self.horizontalLayout_23.addWidget(self.scrollArea_19)

        self.horizontalSpacer_32 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_23.addItem(self.horizontalSpacer_32)

        self.horizontalLayout_23.setStretch(0, 1)
        self.horizontalLayout_23.setStretch(1, 5)
        self.horizontalLayout_23.setStretch(2, 1)

        self.horizontalLayout_62.addWidget(self.widget_43)

        self.stackedWidget.addWidget(self.GengDuoWanFa_widget)
        self.ChongQiYouXi_widget = QWidget()
        self.ChongQiYouXi_widget.setObjectName(u"ChongQiYouXi_widget")
        self.horizontalLayout_10 = QHBoxLayout(self.ChongQiYouXi_widget)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.widget_17 = QWidget(self.ChongQiYouXi_widget)
        self.widget_17.setObjectName(u"widget_17")
        self.widget_17.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_9 = QHBoxLayout(self.widget_17)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_5)

        self.scrollArea_6 = QScrollArea(self.widget_17)
        self.scrollArea_6.setObjectName(u"scrollArea_6")
        self.scrollArea_6.setMinimumSize(QSize(600, 0))
        self.scrollArea_6.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_19 = QVBoxLayout(self.scrollAreaWidgetContents_3)
        self.verticalLayout_19.setSpacing(10)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.verticalLayout_19.setContentsMargins(10, -1, 10, -1)
        self.widget_18 = QWidget(self.scrollAreaWidgetContents_3)
        self.widget_18.setObjectName(u"widget_18")
        self.widget_18.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_20 = QVBoxLayout(self.widget_18)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.label_12 = QLabel(self.widget_18)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_20.addWidget(self.label_12)

        self.line_6 = QFrame(self.widget_18)
        self.line_6.setObjectName(u"line_6")
        sizePolicy1.setHeightForWidth(self.line_6.sizePolicy().hasHeightForWidth())
        self.line_6.setSizePolicy(sizePolicy1)
        self.line_6.setStyleSheet(u"")
        self.line_6.setLineWidth(0)
        self.line_6.setMidLineWidth(2)
        self.line_6.setFrameShape(QFrame.Shape.HLine)
        self.line_6.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_20.addWidget(self.line_6)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_21 = QVBoxLayout()
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.label_13 = QLabel(self.widget_18)
        self.label_13.setObjectName(u"label_13")

        self.verticalLayout_21.addWidget(self.label_13)

        self.label_14 = QLabel(self.widget_18)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_21.addWidget(self.label_14)


        self.gridLayout_3.addLayout(self.verticalLayout_21, 0, 0, 1, 1)

        self.checkBox_3 = QCheckBox(self.widget_18)
        self.checkBox_3.setObjectName(u"checkBox_3")
        self.checkBox_3.setStyleSheet(u"")

        self.gridLayout_3.addWidget(self.checkBox_3, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.label_102 = QLabel(self.widget_18)
        self.label_102.setObjectName(u"label_102")

        self.verticalLayout_12.addWidget(self.label_102)

        self.label_103 = QLabel(self.widget_18)
        self.label_103.setObjectName(u"label_103")
        self.label_103.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_12.addWidget(self.label_103)


        self.gridLayout_3.addLayout(self.verticalLayout_12, 1, 0, 1, 1)

        self.lineEdit = QLineEdit(self.widget_18)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_3.addWidget(self.lineEdit, 1, 1, 1, 1)

        self.gridLayout_3.setColumnStretch(0, 5)
        self.gridLayout_3.setColumnStretch(1, 2)

        self.verticalLayout_20.addLayout(self.gridLayout_3)


        self.verticalLayout_19.addWidget(self.widget_18, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_6.setWidget(self.scrollAreaWidgetContents_3)

        self.horizontalLayout_9.addWidget(self.scrollArea_6)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_6)

        self.horizontalLayout_9.setStretch(0, 1)
        self.horizontalLayout_9.setStretch(1, 5)
        self.horizontalLayout_9.setStretch(2, 1)

        self.horizontalLayout_10.addWidget(self.widget_17)

        self.stackedWidget.addWidget(self.ChongQiYouXi_widget)
        self.DQH_Settings_widget = QWidget()
        self.DQH_Settings_widget.setObjectName(u"DQH_Settings_widget")
        self.horizontalLayout_5 = QHBoxLayout(self.DQH_Settings_widget)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.widget_19 = QWidget(self.DQH_Settings_widget)
        self.widget_19.setObjectName(u"widget_19")
        self.widget_19.setStyleSheet(u"font: 15pt \"\u4ed3\u8033\u4eca\u697702-6763\";\n"
"color:#0f322f;")
        self.horizontalLayout_11 = QHBoxLayout(self.widget_19)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_11.addItem(self.horizontalSpacer_7)

        self.scrollArea_7 = QScrollArea(self.widget_19)
        self.scrollArea_7.setObjectName(u"scrollArea_7")
        self.scrollArea_7.setMinimumSize(QSize(600, 0))
        self.scrollArea_7.setWidgetResizable(True)
        self.scrollAreaWidgetContents_4 = QWidget()
        self.scrollAreaWidgetContents_4.setObjectName(u"scrollAreaWidgetContents_4")
        self.scrollAreaWidgetContents_4.setGeometry(QRect(0, 0, 598, 536))
        self.verticalLayout_22 = QVBoxLayout(self.scrollAreaWidgetContents_4)
        self.verticalLayout_22.setSpacing(10)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.verticalLayout_22.setContentsMargins(10, -1, 10, -1)
        self.widget_20 = QWidget(self.scrollAreaWidgetContents_4)
        self.widget_20.setObjectName(u"widget_20")
        self.widget_20.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"Line{\n"
"border:2px solid #969696;\n"
"border-radius:1px;\n"
"            }\n"
"\n"
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
"/* 1. \u672a\u9009\u4e2d\uff08\u9ed8\u8ba4\uff09\u72b6\u6001\u7684\u4e0b"
                        "\u8fb9\u6846 */\n"
"            QLineEdit {\n"
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
"        "
                        "    \n"
"            /* 3. \u9f20\u6807\u7565\u8fc7\uff08\u60ac\u505c\uff09\u72b6\u6001\u7684\u4e0b\u8fb9\u6846 */\n"
"            QLineEdit:hover {\n"
"                border-bottom: 4px solid #0f322f;  /* \u6df1\u7070\u8272\u4e0b\u8fb9\u6846\uff08\u4e2d\u95f4\u72b6\u6001\uff09 */\n"
"            }")
        self.verticalLayout_23 = QVBoxLayout(self.widget_20)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.label_15 = QLabel(self.widget_20)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setStyleSheet(u"font-size:20pt;\n"
"border:none;")

        self.verticalLayout_23.addWidget(self.label_15)

        self.line_7 = QFrame(self.widget_20)
        self.line_7.setObjectName(u"line_7")
        sizePolicy1.setHeightForWidth(self.line_7.sizePolicy().hasHeightForWidth())
        self.line_7.setSizePolicy(sizePolicy1)
        self.line_7.setStyleSheet(u"")
        self.line_7.setLineWidth(0)
        self.line_7.setMidLineWidth(2)
        self.line_7.setFrameShape(QFrame.Shape.HLine)
        self.line_7.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_23.addWidget(self.line_7)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout_24 = QVBoxLayout()
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.label_16 = QLabel(self.widget_20)
        self.label_16.setObjectName(u"label_16")

        self.verticalLayout_24.addWidget(self.label_16)

        self.label_17 = QLabel(self.widget_20)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_24.addWidget(self.label_17)


        self.gridLayout_4.addLayout(self.verticalLayout_24, 0, 0, 1, 1)

        self.checkBox_4 = QCheckBox(self.widget_20)
        self.checkBox_4.setObjectName(u"checkBox_4")
        self.checkBox_4.setStyleSheet(u"")

        self.gridLayout_4.addWidget(self.checkBox_4, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_13 = QVBoxLayout()
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.label_104 = QLabel(self.widget_20)
        self.label_104.setObjectName(u"label_104")

        self.verticalLayout_13.addWidget(self.label_104)

        self.label_105 = QLabel(self.widget_20)
        self.label_105.setObjectName(u"label_105")
        self.label_105.setStyleSheet(u"font-size:10pt;\n"
"color:#39C5BB;")

        self.verticalLayout_13.addWidget(self.label_105)


        self.gridLayout_4.addLayout(self.verticalLayout_13, 1, 0, 1, 1)

        self.lineEdit_2 = QLineEdit(self.widget_20)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_4.addWidget(self.lineEdit_2, 1, 1, 1, 1)

        self.gridLayout_4.setColumnStretch(0, 5)
        self.gridLayout_4.setColumnStretch(1, 2)

        self.verticalLayout_23.addLayout(self.gridLayout_4)


        self.verticalLayout_22.addWidget(self.widget_20, 0, Qt.AlignmentFlag.AlignTop)

        self.scrollArea_7.setWidget(self.scrollAreaWidgetContents_4)

        self.horizontalLayout_11.addWidget(self.scrollArea_7)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_11.addItem(self.horizontalSpacer_8)

        self.horizontalLayout_11.setStretch(0, 1)
        self.horizontalLayout_11.setStretch(1, 5)
        self.horizontalLayout_11.setStretch(2, 1)

        self.horizontalLayout_5.addWidget(self.widget_19)

        self.stackedWidget.addWidget(self.DQH_Settings_widget)

        self.verticalLayout_2.addWidget(self.stackedWidget)


        self.horizontalLayout.addWidget(self.widget)

        DailyQuestsHelper.setCentralWidget(self.centralwidget)

        self.retranslateUi(DailyQuestsHelper)

        self.overview_panel_button.setDefault(False)
        self.stackedWidget.setCurrentIndex(0)


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
        self.label_18.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_19.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_20.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_5.setText("")
        self.label_106.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_107.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_21.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_22.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_23.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_6.setText("")
        self.label_108.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_109.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_24.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_25.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_26.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_7.setText("")
        self.label_110.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_111.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_27.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_28.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_29.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_8.setText("")
        self.label_112.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_113.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_30.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_31.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_32.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_9.setText("")
        self.label_114.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_115.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_33.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_34.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_35.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_10.setText("")
        self.label_116.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_117.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_36.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_37.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_38.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_11.setText("")
        self.label_118.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_119.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_39.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_40.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_41.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_12.setText("")
        self.label_120.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_121.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_42.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_43.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_44.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_13.setText("")
        self.label_122.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_123.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_63.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_64.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_65.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_20.setText("")
        self.label_136.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_137.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_45.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_46.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_47.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_14.setText("")
        self.label_124.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_125.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_87.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_88.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_89.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_28.setText("")
        self.label_152.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_153.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_167.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_168.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_169.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_34.setText("")
        self.label_170.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_171.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_66.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_67.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_68.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_21.setText("")
        self.label_138.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_139.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_93.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_94.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_95.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_30.setText("")
        self.label_156.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_157.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_72.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_73.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_74.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_23.setText("")
        self.label_142.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_143.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_78.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_79.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_80.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_25.setText("")
        self.label_146.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_147.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_60.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_61.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_62.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_19.setText("")
        self.label_134.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_135.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_54.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_55.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_56.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_17.setText("")
        self.label_130.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_131.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_81.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_82.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_83.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_26.setText("")
        self.label_148.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_149.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_99.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_100.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_101.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_32.setText("")
        self.label_160.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_161.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_84.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_85.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_86.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_27.setText("")
        self.label_150.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_151.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_96.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_97.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_98.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_31.setText("")
        self.label_158.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_159.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_162.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_163.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_164.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_33.setText("")
        self.label_165.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_166.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_75.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_76.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_77.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_24.setText("")
        self.label_144.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_145.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_57.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_58.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_59.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_18.setText("")
        self.label_132.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_133.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_48.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_49.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_50.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_15.setText("")
        self.label_126.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_127.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_69.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_70.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_71.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_22.setText("")
        self.label_140.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_141.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_90.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_91.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_92.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_29.setText("")
        self.label_154.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_155.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_51.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_52.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_53.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_16.setText("")
        self.label_128.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_129.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_12.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_13.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_14.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_3.setText("")
        self.label_102.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_103.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
        self.label_15.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4efb\u52a1\u8bbe\u7f6e", None))
        self.label_16.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u542f\u7528\u4efb\u52a1", None))
        self.label_17.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u5c06\u8fd9\u4e2a\u4efb\u52a1\u52a0\u5165\u8c03\u5ea6\u5668", None))
        self.checkBox_4.setText("")
        self.label_104.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u4e0b\u6b21\u6267\u884c\u65f6\u95f4", None))
        self.label_105.setText(QCoreApplication.translate("DailyQuestsHelper", u"\u81ea\u52a8\u8ba1\u7b97\u5f97\u51fa\uff0c\u65e0\u987b\u4fee\u6539\uff0c\u6e05\u7a7a\u5219\u7acb\u523b\u8fd0\u884c", None))
    # retranslateUi

