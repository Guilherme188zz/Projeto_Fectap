# -*- coding: utf-8 -*-

# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

# Initially created: Mon Dec 22 21:53:13 2014 by: PyQt4 UI code generator 4.11.2

from PyQt4.QtGui import (QApplication, QCheckBox, QFont, QFrame, QLabel,
                         QLineEdit, QPixmap, QPushButton, QRadioButton,
                         QScrollArea)
import gv_qrc

def tl(txt=''):
    return QApplication.translate("Aebasecol", txt, None, 1)

class Ui_Aebasecol(object):
    devels = 0
    
    def setupUi(self, Aebasecol):
        Aebasecol.resize(400, 469)
        Aebasecol.setMinimumSize(400, 469)
        Aebasecol.setMaximumSize(400, 470)
        self.menubar = Aebasecol.menuBar()
        self.statusbar = Aebasecol.statusBar()
        self.statusbar.setSizeGripEnabled(False)
        self.no_dbconn = QLabel(self.statusbar)
        font = QFont()
        font.setBold(True)
        self.no_dbconn.setFont(font)
        self.statusbar.addPermanentWidget(self.no_dbconn, 0)
        self.no_dbconn.hide()
        self.aeFr = QFrame(Aebasecol)
        self.aeFr.setGeometry(10, 40, 380, 340)
        self.aeFr.setAutoFillBackground(True)
        self.aeFr.setFrameShape(6) # StyledPanel
        self.aeFr.setFrameShadow(20) # Raised
        self.bcnameLb = QLabel(self.aeFr)
        self.bcnameLb.setGeometry(31, 10, 115, 19)
        self.bcnameLe = QLineEdit(self.aeFr)
        self.bcnameLe.setGeometry(30, 30, 231, 27)
        self.bcnameLe.setMaxLength(25)
        self.combLb = QLabel(self.aeFr)
        self.combLb.setGeometry(31, 70, 240, 24)
        self.possRb = QRadioButton(self.aeFr)
        self.possRb.setGeometry(30, 95, 78, 23)
        self.possRb.setChecked(True)
        self.oblRb = QRadioButton(self.aeFr)
        self.oblRb.setGeometry(30, 115, 91, 23)
        self.noRb = QRadioButton(self.aeFr)
        self.noRb.setGeometry(30, 135, 58, 23)
        self.specLb = QLabel(self.aeFr)
        self.specLb.setGeometry(31, 170, 231, 37)
        ## self.specLb.setFrameShape(1)
        self.specLb.setWordWrap(True)
        self.spscrollA = QScrollArea(self.aeFr)
        self.spscrollA.setGeometry(30, 220, 231, 110)
        self.spscrollA.setHorizontalScrollBarPolicy(1)
        self.spscrollA.setVerticalScrollBarPolicy(0)
        ## self.spscrollA.setFrameShape(1)
        self.specFr = QFrame(self.spscrollA) # aeFr?
        self.specFr.setGeometry(0, 0, 230, 106)
        self.specFr.setFrameShape(6)
        self.specFr.setFrameShadow(30)
        self.spscrollA.setWidget(self.specFr)
        self.allCb = QCheckBox(
            QApplication.translate("Aebasecol", "Select All", None, 1),
            self.specFr)
        self.allCb.setGeometry(20, 10, 200, 21)
        self.line = QFrame(self.specFr)
        self.line.setGeometry(20, 36, 180, 2)
        self.line.setFrameShape(6)
        self.togglePb = QPushButton(self.aeFr)
        self.togglePb.setGeometry(280, 255, 80, 30)
        self.errFr = QFrame(Aebasecol)
        self.errFr.setGeometry(10, 40, 380, 340)
        self.errFr.setAutoFillBackground(True)
        self.errFr.setFrameShape(6)
        self.errFr.setFrameShadow(20)
        self.warnLb = QLabel(self.errFr)
        self.warnLb.setGeometry(10, 130, 40, 39)
        self.warnLb.setPixmap(QPixmap(":/images/warning.png"))
        self.errmsgLb = QLabel(self.errFr)
        self.errmsgLb.setGeometry(70, 69, 210, 175)
        self.errmsgLb.setWordWrap(True)
        self.confFr = QFrame(Aebasecol)
        self.confFr.setGeometry(10, 40, 380, 340)
        self.confFr.setAutoFillBackground(True)
        self.confFr.setFrameShape(6)
        self.confFr.setFrameShadow(20)
        self.qLb = QLabel(self.confFr)
        self.qLb.setGeometry(20, 148, 32, 32)
        self.qLb.setPixmap(QPixmap(":/images/question.png"))
        self.cscrollA = QScrollArea(self.confFr)
        self.cscrollA.setGeometry(79, 24, 261, 281)
        self.cscrollA.setHorizontalScrollBarPolicy(1)
        self.cscrollA.setVerticalScrollBarPolicy(0)
        self.confmsgLb = QLabel(self.cscrollA)
        self.confmsgLb.setGeometry(0, 0, 261, 277)
        self.cscrollA.setWidget(self.confmsgLb)
        self.okPb = QPushButton(Aebasecol)
        self.okPb.setGeometry(110, 408, 80, 30)
        self.closePb = QPushButton(Aebasecol)
        self.closePb.setGeometry(210, 408, 80, 30)
        self.closePb.setAutoDefault(True)
        self.bcnameLb.setBuddy(self.bcnameLe)

        self.retranslateUi(Aebasecol)

    def retranslateUi(self, Aebasecol):
        Aebasecol.setWindowTitle(tl("GnuVet: Add Basecolour"))
        self.no_dbconn.setText(tl("No db connection..."))
        self.bcnameLb.setText(tl("BaseC&olour Name:"))
        self.okPb.setText(tl("OK"))
        self.closePb.setText(tl("Cancel"))
        self.closePb.setShortcut(tl("Esc"))
        self.combLb.setText(tl("Combinations with other Basecolours:"))
        self.possRb.setText(tl("&possible"))
        self.possRb.setToolTip(tl(
            "This Basecolour can be combined with others"))
        self.possRb.setStatusTip(tl("Combination possible"))
        self.oblRb.setText(tl("n&ecessary"))
        self.oblRb.setToolTip(tl(
            "This Basecolour has to be combined with another"))
        self.oblRb.setStatusTip(tl("Combination required"))
        self.noRb.setText(tl("&none"))
        self.noRb.setToolTip(tl(
            "This Basecolour can not be combined with others"))
        self.noRb.setStatusTip(tl("No combination possible"))
        self.specLb.setText(tl(
                "Please select species for which new basecolour applies:"))
        self.togglePb.setText(tl("Toggle &All"))

    def develf(self):
        if self.devels == 0:
            self.aeFr.hide()
            self.confFr.hide()
            self.errFr.show()
            self.devels = 1
        elif self.devels == 1:
            self.confFr.hide()
            self.errFr.hide()
            self.aeFr.show()
            self.devels = 2
        elif self.devels == 2:
            self.aeFr.hide()
            self.errFr.hide()
            self.confFr.show()
            self.devels = 0

if __name__ == '__main__':
    from PyQt4.QtGui import QAction, QApplication, QMainWindow, QShortcut
    a = QApplication([])
    a.setStyle('plastique')
    b = Ui_Aebasecol()
    w = QMainWindow()
    b.setupUi(w)
    develA = QAction(w)
    develA.setShortcut('Ctrl+D')
    develA.triggered.connect(b.develf)
    w.addAction(develA)
    QShortcut('Ctrl+Q', w, quit)
    b.closePb.clicked.connect(quit)
    w.show()
    exit(a.exec_())
