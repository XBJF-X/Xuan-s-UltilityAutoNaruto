# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SceneManager.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QMainWindow, QMenu,
    QMenuBar, QSizePolicy, QWidget)

class Ui_SceneManager(object):
    def setupUi(self, SceneManager):
        if not SceneManager.objectName():
            SceneManager.setObjectName(u"SceneManager")
        SceneManager.resize(963, 600)
        SceneManager.setStyleSheet(u"font-family:\"Consolas\",\"\u9ed1\u4f53\";\n"
"font-size:11pt;\n"
"\n"
"")
        self.refresh = QAction(SceneManager)
        self.refresh.setObjectName(u"refresh")
        self.save = QAction(SceneManager)
        self.save.setObjectName(u"save")
        self.new_node = QAction(SceneManager)
        self.new_node.setObjectName(u"new_node")
        self.auto_layout = QAction(SceneManager)
        self.auto_layout.setObjectName(u"auto_layout")
        self.centralwidget = QWidget(SceneManager)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setMinimumSize(QSize(963, 567))
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        SceneManager.setCentralWidget(self.centralwidget)
        self.menuBar = QMenuBar(SceneManager)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 963, 33))
        self.menu = QMenu(self.menuBar)
        self.menu.setObjectName(u"menu")
        SceneManager.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menu.menuAction())
        self.menu.addAction(self.refresh)
        self.menu.addAction(self.save)
        self.menu.addAction(self.new_node)
        self.menu.addAction(self.auto_layout)

        self.retranslateUi(SceneManager)

        QMetaObject.connectSlotsByName(SceneManager)
    # setupUi

    def retranslateUi(self, SceneManager):
        SceneManager.setWindowTitle(QCoreApplication.translate("SceneManager", u"\u573a\u666f\u7ba1\u7406", None))
        self.refresh.setText(QCoreApplication.translate("SceneManager", u"\u5237\u65b0\u89c6\u56fe", None))
        self.save.setText(QCoreApplication.translate("SceneManager", u"\u4fdd\u5b58\u9879\u76ee", None))
        self.new_node.setText(QCoreApplication.translate("SceneManager", u"\u65b0\u5efa\u8282\u70b9", None))
        self.auto_layout.setText(QCoreApplication.translate("SceneManager", u"\u81ea\u52a8\u5e03\u5c40", None))
        self.menu.setTitle(QCoreApplication.translate("SceneManager", u"\u83dc\u5355", None))
    # retranslateUi

