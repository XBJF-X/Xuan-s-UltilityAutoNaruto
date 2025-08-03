# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'KeyMapConfiguration.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

class Ui_KeyMapConfiguration(object):
    def setupUi(self, KeyMapConfiguration):
        if not KeyMapConfiguration.objectName():
            KeyMapConfiguration.setObjectName(u"KeyMapConfiguration")
        KeyMapConfiguration.resize(771, 577)
        KeyMapConfiguration.setStyleSheet(u"font: 15pt \"\u9ed1\u4f53\";")
        self.horizontalLayout = QHBoxLayout(KeyMapConfiguration)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.image_container = QWidget(KeyMapConfiguration)
        self.image_container.setObjectName(u"image_container")
        self.verticalLayout_3 = QVBoxLayout(self.image_container)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.image_label = QLabel(self.image_container)
        self.image_label.setObjectName(u"image_label")

        self.verticalLayout_3.addWidget(self.image_label)


        self.horizontalLayout.addWidget(self.image_container)

        self.widget_2 = QWidget(KeyMapConfiguration)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setMaximumSize(QSize(150, 16777215))
        self.widget_2.setStyleSheet(u"QWidget {\n"
"                background-color: #dfdfdf;  /* \u80cc\u666f\u989c\u8272 */\n"
"				border-radius:10px;\n"
"            }\n"
"QLabel{color:#0f322f;}")
        self.verticalLayout_2 = QVBoxLayout(self.widget_2)
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(10, 10, 0, 0)
        self.A = QLabel(self.widget_2)
        self.A.setObjectName(u"A")
        self.A.setMaximumSize(QSize(200, 16777215))

        self.verticalLayout_2.addWidget(self.A)

        self.skill_1 = QLabel(self.widget_2)
        self.skill_1.setObjectName(u"skill_1")

        self.verticalLayout_2.addWidget(self.skill_1)

        self.skill_2 = QLabel(self.widget_2)
        self.skill_2.setObjectName(u"skill_2")

        self.verticalLayout_2.addWidget(self.skill_2)

        self.ougi = QLabel(self.widget_2)
        self.ougi.setObjectName(u"ougi")

        self.verticalLayout_2.addWidget(self.ougi)

        self.left_sub_skill = QLabel(self.widget_2)
        self.left_sub_skill.setObjectName(u"left_sub_skill")

        self.verticalLayout_2.addWidget(self.left_sub_skill)

        self.right_sub_skill = QLabel(self.widget_2)
        self.right_sub_skill.setObjectName(u"right_sub_skill")

        self.verticalLayout_2.addWidget(self.right_sub_skill)

        self.stand_in = QLabel(self.widget_2)
        self.stand_in.setObjectName(u"stand_in")

        self.verticalLayout_2.addWidget(self.stand_in)

        self.secret_ecroll = QLabel(self.widget_2)
        self.secret_ecroll.setObjectName(u"secret_ecroll")

        self.verticalLayout_2.addWidget(self.secret_ecroll)

        self.tongling = QLabel(self.widget_2)
        self.tongling.setObjectName(u"tongling")

        self.verticalLayout_2.addWidget(self.tongling)

        self.joystick = QLabel(self.widget_2)
        self.joystick.setObjectName(u"joystick")

        self.verticalLayout_2.addWidget(self.joystick)

        self.widget_3 = QWidget(self.widget_2)
        self.widget_3.setObjectName(u"widget_3")
        self.verticalLayout = QVBoxLayout(self.widget_3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.finish = QPushButton(self.widget_3)
        self.finish.setObjectName(u"finish")
        self.finish.setMinimumSize(QSize(100, 40))
        self.finish.setMaximumSize(QSize(90, 16777215))
        self.finish.setStyleSheet(u"QPushButton{\n"
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

        self.verticalLayout.addWidget(self.finish, 0, Qt.AlignmentFlag.AlignHCenter)


        self.verticalLayout_2.addWidget(self.widget_3)


        self.horizontalLayout.addWidget(self.widget_2, 0, Qt.AlignmentFlag.AlignTop)


        self.retranslateUi(KeyMapConfiguration)

        QMetaObject.connectSlotsByName(KeyMapConfiguration)
    # setupUi

    def retranslateUi(self, KeyMapConfiguration):
        KeyMapConfiguration.setWindowTitle(QCoreApplication.translate("KeyMapConfiguration", u"\u952e\u4f4d\u914d\u7f6e", None))
        self.image_label.setText("")
        self.A.setText(QCoreApplication.translate("KeyMapConfiguration", u"1\uff1a\u5e73A", None))
        self.skill_1.setText(QCoreApplication.translate("KeyMapConfiguration", u"2\uff1a\u4e00\u6280\u80fd", None))
        self.skill_2.setText(QCoreApplication.translate("KeyMapConfiguration", u"3\uff1a\u4e8c\u6280\u80fd", None))
        self.ougi.setText(QCoreApplication.translate("KeyMapConfiguration", u"4\uff1a\u5965\u4e49", None))
        self.left_sub_skill.setText(QCoreApplication.translate("KeyMapConfiguration", u"5\uff1a\u5de6\u5b50\u6280\u80fd", None))
        self.right_sub_skill.setText(QCoreApplication.translate("KeyMapConfiguration", u"6\uff1a\u53f3\u5b50\u6280\u80fd", None))
        self.stand_in.setText(QCoreApplication.translate("KeyMapConfiguration", u"7\uff1a\u66ff\u8eab", None))
        self.secret_ecroll.setText(QCoreApplication.translate("KeyMapConfiguration", u"8\uff1a\u79d8\u5377", None))
        self.tongling.setText(QCoreApplication.translate("KeyMapConfiguration", u"9\uff1a\u901a\u7075", None))
        self.joystick.setText(QCoreApplication.translate("KeyMapConfiguration", u"10\uff1a\u6447\u6746", None))
        self.finish.setText(QCoreApplication.translate("KeyMapConfiguration", u"\u7ed3\u675f", None))
    # retranslateUi

