# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'updateQT.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!

import sys
import update

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QWidget, QToolTip, QDesktopWidget, QMessageBox, QPushButton, QApplication)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QCoreApplication

class updateUI(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # 这种静态的方法设置一个用于显示工具提示的字体。我们使用10px滑体字体。
        QToolTip.setFont(QFont('SansSerif', 10))

        # 创建一个提示，我们称之为settooltip()方法。我们可以使用丰富的文本格式
        self.setToolTip('This is a <b>QWidget</b> widget')

        update_btn = QPushButton('检查更新', self)
        update_btn.setToolTip('连接服务器进行 <b>更新</b> 无法回退请注意！')
        update_btn.setGeometry(QtCore.QRect(150, 170, 75, 23))
        update_btn.setObjectName("检查更新")
        update_btn.clicked.connect(update.update)

        quit_btn = QPushButton('退出更新', self)
        quit_btn.setToolTip('退出更新程序')
        quit_btn.setGeometry(QtCore.QRect(150, 210, 75, 23))
        quit_btn.setObjectName("退出更新")
        quit_btn.clicked.connect(QCoreApplication.instance().quit)

        self.setGeometry(400, 400, 400, 300)
        self.setWindowTitle('人在江湖在线更新')
        self.center()
        self.show()

    def closeEvent(self, event):

        reply = QMessageBox.question(self, '退出更新',
                                     "确定要退出更新么?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def center(self):

        # 获得窗口
        qr = self.frameGeometry()
        # 获得屏幕中心点
        cp = QDesktopWidget().availableGeometry().center()
        # 显示到屏幕中心
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = updateUI()
    sys.exit(app.exec_())