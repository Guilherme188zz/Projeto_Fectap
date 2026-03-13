# -*- coding: utf-8 -*-

# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

# Form implementation generated from scratch Fr May 31 15:04:29

from PyQt4.QtGui import (
    QApplication,QCheckBox,QComboBox,QDateEdit,QLabel,QPushButton)
from tle import QTextLEdit

def tl(txt=''):
    return QApplication.translate("Datefix", txt, None, 1)

class Ui_Datefix(object):
    def setupUi(self, Datefix):
        Datefix.resize(500, 264)
        Datefix.setMinimumSize(500, 264)
        Datefix.setMaximumSize(500, 265)
        self.dateLb = QLabel(Datefix)
        self.dateLb.setGeometry(10, 10, 41, 22)
        self.dateDe = QDateEdit(Datefix)
        self.dateDe.setGeometry(56, 9, 110, 24)
        self.dateDe.setCalendarPopup(True)
        self.timeLb = QLabel(Datefix)
        self.timeLb.setGeometry(181, 10, 40, 22)
        self.timeDd = QComboBox(Datefix)
        self.timeDd.setGeometry(226, 9, 72, 24)
        self.staffLb = QLabel(Datefix)
        self.staffLb.setGeometry(318, 10, 50, 22)
        self.staffDd = QComboBox(Datefix)
        self.staffDd.setGeometry(366, 9, 118, 24)
        self.patPb = QPushButton(Datefix)
        self.patPb.setGeometry(72, 49, 174, 30)
        self.cliPb = QPushButton(Datefix)
        self.cliPb.setGeometry(257, 49, 174, 30)
        self.txtLb = QLabel(Datefix)
        self.txtLb.setGeometry(32, 103, 50, 22)
        self.tLe = QTextLEdit(Datefix, 100)
        self.tLe.setGeometry(72, 94, 360, 45)
        self.tLe.setTabChangesFocus(True)
        self.shortCb = QCheckBox(Datefix)
        self.shortCb.setGeometry(74, 155, 100, 22)
        self.durLb = QLabel(Datefix)
        self.durLb.setGeometry(74, 184, 70, 22)
        self.durDd = QComboBox(Datefix)
        self.durDd.setGeometry(144, 183, 72, 24)
        self.markLb = QLabel(Datefix)
        self.markLb.setGeometry(251, 166, 60, 22)
        self.markDd = QComboBox(Datefix)
        self.markDd.setGeometry(321, 165, 110, 24)
        self.okPb = QPushButton(Datefix)
        self.okPb.setGeometry(119, 224, 80, 24)
        self.resetPb = QPushButton(Datefix)
        self.resetPb.setGeometry(209, 224, 80, 24)
        self.ccPb = QPushButton(Datefix)
        self.ccPb.setGeometry(299, 224, 80, 24)
        self.dateLb.setBuddy(self.dateDe)
        self.timeLb.setBuddy(self.timeDd)
        self.staffLb.setBuddy(self.staffDd)
        self.txtLb.setBuddy(self.tLe)
        self.durLb.setBuddy(self.durDd)
        self.markLb.setBuddy(self.markDd)
        self.retranslateUi(Datefix)

    def retranslateUi(self, Datefix):
        Datefix.setWindowTitle(tl("GnuVet: Set Appointment"))
        self.shortCb.setText(tl("&no duration"))
        self.dateLb.setText(tl("&Date:"))
        self.timeLb.setText(tl("&Time:"))
        self.staffLb.setText(tl("&Staff:")) # tr_de: 'Für'
        self.patPb.setText(tl("&Pat: unknown"))
        self.cliPb.setText(tl("&Cli: unknown"))
        self.txtLb.setText(tl("Te&xt:"))
        self.shortCb.setToolTip(tl("Set this for short time activities"))
        self.durLb.setText(tl("D&uration:"))
        self.markLb.setText(tl("&Mark as:"))
        self.okPb.setText(tl("OK"))
        self.resetPb.setText(tl("&Reset"))
        self.ccPb.setText(tl("Cancel"))

if __name__ == '__main__':
    from PyQt4.QtGui import QMainWindow, QShortcut
    a = QApplication([])
    a.setStyle('plastique')
    b = Ui_Datefix()
    w = QMainWindow()
    b.setupUi(w)
    for h in xrange(24):
        b.timeDd.addItem('{:02}:00'.format(h))
        b.timeDd.addItem('{:02}:30'.format(h))
    b.staffDd.addItem('None')
    b.staffDd.addItem('Vet')
    b.staffDd.addItem('Nurse')
    QShortcut('Ctrl+W', w, quit)
    w.show()
    exit(a.exec_())
