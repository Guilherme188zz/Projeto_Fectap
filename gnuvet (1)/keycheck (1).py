"""The Keycheck to enable a Default Key for QMainWindow."""
# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

from PyQt4.QtCore import QObject, pyqtSignal, QEvent, Qt

class Keycheck(QObject):
    enter = pyqtSignal()
    esc   = pyqtSignal()

    def __init__(self, parent=None):
        super(Keycheck, self).__init__(parent)

    def eventFilter(self, ob, ev):
        if ev.type() == QEvent.KeyPress:
            if ev.key() == Qt.Key_Enter or ev.key() == Qt.Key_Return:
                self.enter.emit()
                return True
            if ev.key() == Qt.Key_Escape:
                self.esc.emit()
                return True
            return False
        return False
    
class Backspace(QObject):
    bs = pyqtSignal(object)

    def __init__(self, parent=None):
        super(Backspace, self).__init__(parent)
        self.parent = parent

    def eventFilter(self, ob, ev):
        if ev.type() == QEvent.KeyPress:
            if ev.key() == Qt.Key_Backspace:
                self.bs.emit(self.parent)
                return True
            return False
        return False
