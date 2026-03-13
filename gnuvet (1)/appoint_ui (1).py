# -*- coding: utf-8 -*-

# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

# Form implementation generated from scratch Sat May 18 21:28:50 2013

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QApplication,QComboBox,QFont,QFrame,QLabel,QPixmap,
                         QPushButton,QRadioButton)
from gtable import Gtable
import gv_qrc

def tl(txt=''):
    return QApplication.translate("Appointer", txt, None, 1)

class Ui_Appointer(object):
    def setupUi(self, Appointer):
        Appointer.resize(958, 645)
        Appointer.setMinimumSize(958, 645)
        Appointer.setMaximumSize(958, 646)
        # self.centralwidget = QWidget(Appointer)
        self.menubar = Appointer.menuBar()
        self.statusbar = Appointer.statusBar()
        self.statusbar.setSizeGripEnabled(False)
        self.no_dbconn = QLabel(self.statusbar)
        font = QFont()
        font.setBold(True)
        self.no_dbconn.setFont(font)
        self.statusbar.addPermanentWidget(self.no_dbconn, 0)
        self.no_dbconn.hide()
        self.lLb = QLabel(Appointer)
        self.lLb.setGeometry(Appointer.width()-90, 1, 85, 19)
        self.lLb.setAlignment(Qt.AlignRight|Qt.AlignBottom) # tryin 2 elim Qt
        ## self.lLb.setAlignment(0x0002|0x0040) # dont work
        ## self.lLb.setAlignment(0x0042) # dont work
        ## self.lLb.setStyleSheet( # dont work either
        ##     """QLabel { text-align: right; vertical-align: bottom; }""")
        self.monthRb = QRadioButton(Appointer)
        self.monthRb.setGeometry(10, 35, 50, 22)
        self.weekRb = QRadioButton(Appointer)
        self.weekRb.setGeometry(60, 35, 50, 22)
        self.dayRb = QRadioButton(Appointer)
        self.dayRb.setGeometry(110, 35, 50, 22)
        self.yearbackPb = QPushButton(Appointer)
        self.yearbackPb.setGeometry(170, 33, 70, 24)
        self.monthbackPb = QPushButton(Appointer)
        self.monthbackPb.setGeometry(245, 33, 70, 24)
        self.weekbackPb = QPushButton(Appointer)
        self.weekbackPb.setGeometry(320, 33, 70, 24)
        self.daybackPb = QPushButton(Appointer)
        self.daybackPb.setGeometry(395, 33, 70, 24)
        self.dayforePb = QPushButton(Appointer)
        self.dayforePb.setGeometry(470, 33, 70, 24)
        self.weekforePb = QPushButton(Appointer)
        self.weekforePb.setGeometry(545, 33, 70, 24)
        self.monthforePb = QPushButton(Appointer)
        self.monthforePb.setGeometry(620, 33, 70, 24)
        self.yearforePb = QPushButton(Appointer)
        self.yearforePb.setGeometry(695, 33, 70, 24)
        self.staffLb = QLabel(Appointer)
        self.staffLb.setGeometry(780, 34, 40, 22)
        self.staffDd = QComboBox(Appointer)
        self.staffDd.setGeometry(823, 33, 118, 24)
        self.calendar = Gtable(Appointer, scrollh=0)
        self.calendar.jump = True
        self.calendar.setGeometry(12, 69, 930, 514)
        self.calendar.rowmode = 0 # single cell
        self.confirm = QFrame(Appointer)
        self.confirm.setAutoFillBackground(True)
        self.confirm.setFrameShape(6) # QFrame.StyledPanel)
        self.confirm.setFrameShadow(20) # QFrame.Raised)
        self.confirm.setGeometry(300, 200, 350, 200)
        self.confirm.warnPix = QLabel(self.confirm)
        self.confirm.warnPix.setGeometry(15, 60, 40, 39)
        self.confirm.warnPix.setPixmap(QPixmap(":/images/warning.png"))
        self.confirm.msgLb = QLabel(self.confirm)
        self.confirm.msgLb.setWordWrap(True)
        self.confirm.msgLb.setText('Oops, there\'s summin wrong!')
        self.confirmokPb = QPushButton(self.confirm)
        self.confirmokPb.setGeometry(15, 160, 98, 24)
        self.confirmeditPb = QPushButton(self.confirm)
        self.confirmeditPb.setGeometry(125, 160, 98, 24)
        self.confirmccPb = QPushButton(self.confirm)
        self.confirmccPb.setGeometry(235, 160, 98, 24)
        self.confirmeditPb.setDefault(True)
        self.confirmeditPb.setAutoDefault(True)
        self.confirm.hide()
        self.closePb = QPushButton(Appointer)
        self.closePb.setGeometry(439, 595, 80, 24)
        self.staffLb.setBuddy(self.staffDd)
        self.retranslateUi(Appointer)

    def retranslateUi(self, Appointer):
        Appointer.setWindowTitle(tl("GnuVet: Appointments"))
        self.monthRb.setText(tl("&M"))
        self.monthRb.setToolTip(tl("Display month"))
        self.weekRb.setText(tl("&W"))
        self.weekRb.setToolTip(tl("Display week"))
        self.dayRb.setText(tl("&D"))
        self.dayRb.setToolTip(tl("Display day"))
        self.yearbackPb.setText(tl("&< year"))
        self.yearbackPb.setToolTip(tl("Select this day one year earlier"))
        self.monthbackPb.setText(tl("< m&onth"))
        self.monthbackPb.setToolTip(tl("Select this day one month earlier"))
        self.weekbackPb.setText(tl("< w&eek"))
        self.weekbackPb.setToolTip(tl("Select this day one week earlier"))
        self.daybackPb.setText(tl("< d&ay"))
        self.daybackPb.setToolTip(tl("Select one day earlier"))
        self.dayforePb.setText(tl("da&y >"))
        self.dayforePb.setToolTip(tl("Select one day later"))
        self.weekforePb.setText(tl("wee&k >"))
        self.weekforePb.setToolTip(tl("Select this day one week later"))
        self.monthforePb.setText(tl("month& >"))
        self.monthforePb.setToolTip(tl("Select this day one month later"))
        self.yearforePb.setText(tl("year &>"))
        self.yearforePb.setToolTip(tl("Select this day one year later"))
        self.staffLb.setText(tl("&Staff:"))
        self.confirmokPb.setText(tl("Save &anyway"))
        self.confirmeditPb.setText(tl("&Edit entry"))
        self.confirmccPb.setText(tl("&Cancel"))
        self.closePb.setText(tl("Close"))

if __name__ == '__main__':
    from PyQt4.QtGui import QMainWindow, QShortcut
    a = QApplication([])
    a.setStyle('plastique')
    b = Ui_Appointer()
    w = QMainWindow()
    b.setupUi(w)
    b.lLb.setText('appoint_ui')
    QShortcut('Ctrl+W', w, quit)
    b.closePb.clicked.connect(quit)
    w.show()
    exit(a.exec_())
    
