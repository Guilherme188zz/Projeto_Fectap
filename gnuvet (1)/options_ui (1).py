# -*- coding: utf-8 -*-

# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

# Initially created: Fri Apr 23 00:02:26 2010 by: PyQt4 UI code generator 4.4.2

from PyQt4.QtGui import (QApplication, QCheckBox, QDialogButtonBox)

def tl(txt=''):
    return QApplication.translate("Options", txt, None, 1)

class Ui_Options(object):
    def setupUi(self, Options):
        Options.resize(245,175)
        Options.setMinimumSize(245,175)
        self.buttonBox = QDialogButtonBox(Options)
        self.buttonBox.setGeometry(10,120,221,32)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.autoConsCb = QCheckBox(Options)
        self.autoConsCb.setGeometry(60,20,107,23)
        self.autoHistCb = QCheckBox(Options)
        self.autoHistCb.setGeometry(60,50,104,23)
        self.lSympCb = QCheckBox(Options)
        self.lSympCb.setGeometry(60,80,122,23)
        self.retranslateUi(Options)

    def retranslateUi(self, Options):
        Options.setWindowTitle(tl("GnuVet: Set Options"))
        self.autoConsCb.setToolTip(tl("To automatically book consultation"))
        self.autoConsCb.setText(tl("Auto-Consult"))
        self.autoHistCb.setToolTip(tl("To automatically open History Window."))
        self.autoHistCb.setText(tl("Auto-History"))
        self.lSympCb.setToolTip(tl("To use the Lead Symptom feature."))
        self.lSympCb.setText(tl("Lead Symptom"))

if __name__ == '__main__':
    from PyQt4.QtGui import QMainWindow, QShortcut
    a = QApplication([])
    b = Ui_Options()
    w = QMainWindow()
    b.setupUi(w)
    QShortcut('Ctrl+W', w, quit)
    w.show()
    exit(a.exec_())
