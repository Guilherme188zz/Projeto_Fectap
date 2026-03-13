# -*- coding: utf-8 -*-

# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

# Form implementation modified from saepat_ui.py
# trial without centralwidget -- in work
#
# Created: Sun Nov 23 19:48:50 by: ed

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QApplication, QCheckBox, QFont, QFrame, QLabel,
                         QPushButton, QRadioButton, QWidget)
from gtable import Gtable

def tl(txt=''):
    return QApplication.translate("Vaccremind", txt, None, 1)

class Ui_Vaccremind(object):
    def setupUi(self, Vaccremind):
        Vaccremind.resize(870, 626)
        Vaccremind.setMinimumSize(870, 626)
        self.menubar = Vaccremind.menuBar()
        self.lLb = QLabel(Vaccremind)
        self.lLb.setGeometry(Vaccremind.width()-90, 1, 80, 19)
        self.lLb.setAlignment(Qt.AlignRight|Qt.AlignBottom)
        self.statusbar = Vaccremind.statusBar()
        self.statusbar.setSizeGripEnabled(False)
        self.no_dbconn = QLabel(self.statusbar)
        font = QFont()
        font.setBold(1)
        self.no_dbconn.setFont(font)
        self.statusbar.addPermanentWidget(self.no_dbconn)
        self.no_dbconn.hide()
        # no vaxx frame
        self.noVFr = QFrame(Vaccremind)
        self.noVFr.setGeometry(10, 10, 850, 521)
        self.noVFr.setMinimumSize(850, 491)
        self.noVFr.setAutoFillBackground(True)
        self.noVFr.setFrameShape(QFrame.StyledPanel)
        self.noVFr.setFrameShadow(QFrame.Raised)
        self.noVLb = QLabel(self.noVFr)
        self.noVLb.setGeometry(20, 20, 400, 26)
        ##self.noVLb.setAlignment(Qt.AlignLeft)
        self.noVLb.setTextFormat(Qt.PlainText)
        self.noVFr.hide()
        # match[es] frame: list
        self.matchFr = QFrame(Vaccremind)
        self.matchFr.setGeometry(10, 10, 850, 521)
        self.matchFr.setMinimumSize(850, 491)
        self.matchFr.setAutoFillBackground(True)
        self.matchFr.setFrameShape(QFrame.StyledPanel)
        self.matchFr.setFrameShadow(QFrame.Raised)
        self.matchnLb = QLabel(self.matchFr)
        self.matchnLb.setGeometry(10, 7, 231, 19)
        self.matchnLb.setTextFormat(Qt.PlainText)
        self.sortbyLb = QLabel(self.matchFr)
        self.sortbyLb.setGeometry(251, 8, 53, 19)
        self.sbynameRb = QRadioButton(self.matchFr)
        self.sbynameRb.setGeometry(325, 6, 90, 25)
        self.sbydateRb = QRadioButton(self.matchFr)
        self.sbydateRb.setGeometry(425, 6, 90, 25)
        self.sbycliRb = QRadioButton(self.matchFr)
        self.sbycliRb.setGeometry(525, 6, 90, 25)
        self.plist = Gtable(self.matchFr, scrollh=0, resizecols=True)
        self.plist.setGeometry(0, 34, 850, 455)
        self.plist.setMinimumSize(850, 455)
        ## self.matchFr.hide()
        # buttons
        self.mainPb = QPushButton(Vaccremind)
        self.mainPb.setGeometry(177, 540, 107, 24)
        self.closePb = QPushButton(Vaccremind)
        self.closePb.setGeometry(290, 540, 107, 24)
        
        self.retranslateUi(Vaccremind)

    def retranslateUi(self, Vaccremind):
        self.noVLb.setText(tl("No pending vaccinations."))
        self.sortbyLb.setText(tl("order by"))
        self.sbynameRb.setText(tl("&Name"))
        self.sbydateRb.setText(tl("Vacc &due"))
        self.sbycliRb.setText(tl("&Client"))
        self.mainPb.setText(tl("Print Letters"))
        self.closePb.setText(tl("Close"))
        self.no_dbconn.setText(tl('No db connection...'))

if __name__ == '__main__':
    from PyQt4.QtGui import QMainWindow, QShortcut
    a = QApplication([])
    b = Ui_Vaccremind()
    w = QMainWindow()
    b.setupUi(w)
    QShortcut('Ctrl+W', w, quit)
    w.show()
    exit(a.exec_())
