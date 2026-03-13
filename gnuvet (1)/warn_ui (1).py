"""Warning window -- replacing QMessageBox."""

# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

# Created from scratch: Tue May  8 15:54:35 2012 by: ed

from PyQt4.QtGui import (QApplication, QFont, QLabel, QPixmap, QPushButton,)
from PyQt4.QtCore import Qt # alignment

class Ui_Warning(object):
    def setupUi(self, Warning):
        Warning.setMinimumSize(500, 300)
        Warning.setMaximumSize(500, 300)
        self.wPix = QLabel(Warning)
        self.wPix.setGeometry(20, 95, 40, 39)
        self.wPix.setPixmap(QPixmap(":/images/warning.png"))
        self.wHd = QLabel(Warning)
        self.wHd.setGeometry(80, 20, 340, 30)
        self.wHd.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        self.wHd.setFont(font)
        self.wLb = QLabel(Warning)
        self.wLb.setGeometry(80, 60, 340, 180)
        self.wLb.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
        self.wLb.setWordWrap(True)
        self.okPb = QPushButton(Warning)
        self.okPb.setGeometry(210, 250, 80, 30)
        self.okPb.setDefault(True)
        self.okPb.setAutoDefault(True)
        self.retranslateUi(Warning)

    def retranslateUi(self, Warning):
        Warning.setWindowTitle(QApplication.translate(
            "Warning", "GnuVet: Warning", None, 1))
        self.okPb.setText(QApplication.translate(
            "Warning", "Ok", None, 1))

if __name__ == '__main__':
    from PyQt4.QtGui import QMainWindow, QShortcut
    import gv_qrc
    a = QApplication([])
    Warning = QMainWindow()
    b = Ui_Warning()
    b.setupUi(Warning)
    b.wHd.setText('Error Header')
    b.wLb.setText('Warning text:\nThis is an example Warning Text.')
    QShortcut('Ctrl+Q', Warning, quit)
    Warning.show()
    exit(a.exec_())
