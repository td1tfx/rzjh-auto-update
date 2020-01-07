# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'updateQT.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!

import sys
import update
import subprocess
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QWidget, QToolTip, QDesktopWidget, QMessageBox, QPushButton, QApplication, QPushButton, QMainWindow)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QCoreApplication

class updateUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # 这种静态的方法设置一个用于显示工具提示的字体。我们使用10px滑体字体。
        QToolTip.setFont(QFont('SansSerif', 10))

        # 创建一个提示，我们称之为settooltip()方法。我们可以使用丰富的文本格式
        self.setToolTip('This is a <b>QWidget</b> widget')

        self.update_btn = QPushButton('检查更新', self)
        self.update_btn.setToolTip('连接服务器进行 <b>更新</b> 无法回退请注意！')
        self.update_btn.setGeometry(QtCore.QRect(250, 400, 80, 26))
        self.update_btn.setObjectName("检查更新")
        self.update_btn.setEnabled(False)
        self.update_btn.clicked.connect(self.callupdate)


        self.quit_btn = QPushButton('开始游戏', self)
        self.quit_btn.setToolTip('开始游戏')
        self.quit_btn.setGeometry(QtCore.QRect(380, 400, 80, 26))
        self.quit_btn.setObjectName("开始游戏")
        #quit_btn.clicked.connect(QCoreApplication.instance().quit)
        self.quit_btn.clicked.connect(self.excuteExe)

        self.quit_btn = QPushButton('显示更新记录', self)
        self.quit_btn.setToolTip('显示更新记录')
        self.quit_btn.setGeometry(QtCore.QRect(510, 400, 80, 26))
        self.quit_btn.setObjectName("显示更新记录")
        #quit_btn.clicked.connect(QCoreApplication.instance().quit)
        self.quit_btn.clicked.connect(self.showtxt)

        self.textBrowser = QtWidgets.QTextBrowser(self)
        self.textBrowser.setGeometry(QtCore.QRect(150, 20, 450, 350))
        self.textBrowser.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("宋体")
        self.textBrowser.setFont(font)
        self.textBrowser.setObjectName("更新信息显示")

        self.setGeometry(400, 400, 800, 600)
        self.setWindowTitle('人在江湖在线更新')
        self.center()
        self.printf("欢迎使用人在江湖自动更新程序-made by 泥巴")
        self.printf("提醒: 更新前请关闭游戏，否则更新会失败！")
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

    def printf(self, mypstr):

        #自定义类print函数,借用c语言 printf
        #Mypstr：是待显示的字符串
        self.textBrowser.append(mypstr)   #在指定的区域显示提示信息
        self.cursor=self.textBrowser.textCursor()
        self.textBrowser.moveCursor(self.cursor.End)  #光标移到最后，这样就会自动显示出来
        QtWidgets.QApplication.processEvents()  #一定加上这个功能，不然有卡顿

    def callupdate(self):
        update_avalible = update.checkUpdate(self)
        if update_avalible > 0:
            self.update_btn.setEnabled(True)
            is_update = QMessageBox.information(self, "选择是否更新", "有可用更新，是否立即更新？", QMessageBox.Yes | QMessageBox.No)
            if is_update == QMessageBox.Yes:
                update.doUpdate(self)
                self.update_btn.setEnabled(False)
                is_showgxtxt = QMessageBox.information(self, "是否查看更新日志", "更新完成，是否查看更新日志？", QMessageBox.Yes | QMessageBox.No)
                if is_showgxtxt == QMessageBox.Yes:
                    self.showtxt()
                is_excute = QMessageBox.information(self, "选择是否启动游戏", "更新完成，大侠要直接开始游戏么？", QMessageBox.Yes | QMessageBox.No)
                if is_excute == QMessageBox.Yes:
                    self.excuteExe()
        elif update_avalible < 0 :
            self.update_btn.setEnabled(True)
        else:
            pass


    def excuteExe(self):
        main_exe = "In_stories.exe"
        if os.path.exists(main_exe):
            subprocess.Popen(main_exe)
            print("run ", main_exe)
        sys.exit()

    def showtxt(self):
        txt = "rzjh_gx.txt"
        if os.path.exists(txt):
            with open(txt, 'r') as f:
                gxtxt = f.read()
                QMessageBox.about(self,"更新记录",gxtxt)
        else:
            self.printf("找不到任何更新记录！")



class popupMessage(QWidget):

    def __init__(self):
        super().__init__()
        self.initbox()

    def initbox(self):
        self.setGeometry(100, 200, 200, 150)
        self.setWindowTitle('人在江湖在线更新')
        self.center()

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
    ui = updateUI()
    ui.callupdate()
    sys.exit(app.exec_())

