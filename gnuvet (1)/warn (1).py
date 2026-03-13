#!/usr/bin/python
"""Warning window -- replacing QMessageBox."""

# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

from PyQt4.QtGui import QMainWindow, QAction
from PyQt4.QtCore import pyqtSignal
from warn_ui import Ui_Warning
import gv_qrc

class Warning(QMainWindow):
    """GnuVet Warning Window."""
    closed = pyqtSignal()
    
    def __init__(self, parent=None, header='', msg=''):
        super(Warning, self).__init__(parent)
        self.w = Ui_Warning()
        self.w.setupUi(self)
        self.setWindowModality(2)
        self.w.wHd.setText(header)
        self.w.wLb.setText(str(msg))
        quitA = QAction(self)
        quitA.setAutoRepeat(False)
        quitA.setShortcut(self.tr('Ctrl+Q'))
        quitA.triggered.connect(self.gv_quitconfirm)
        self.addAction(quitA)
        self.w.okPb.clicked.connect(self.close)
        self.show()

    def closeEvent(self, ev):
        self.closed.emit()

    def gv_quitconfirm(self):
        if self.parent():
            self.parent().gv_quitconfirm()
        else:
            exit()

    def showmsg(self, title='Warning', txt='No text provided'):
        self.w.wHd.setText(title)
        self.w.wLb.setText(txt)

if __name__ == '__main__':
    from PyQt4.QtGui import QApplication, QMainWindow
    a = QApplication([])
    b = Warning(None, 'Error', 'Long error msg\nwith explanations')
    exit(a.exec_())

    
