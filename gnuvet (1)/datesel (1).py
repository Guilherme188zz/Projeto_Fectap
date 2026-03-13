"""Test date selection dialog."""
# discard this for datefix?

# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

from datetime import date
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QMainWindow
from keycheck import Keycheck
from datesel_ui import Ui_Datesel

class Datesel(QMainWindow):
    # signals
    datesig = pyqtSignal(date)

    def __init__(self, parent=None, today=None):
        super(Datesel, self).__init__(parent)
        self.today = today
        self.w = Ui_Datesel()
        self.w.setupUi(self)
        self.keycheck = Keycheck(self)
        self.installEventFilter(self.keycheck)
        self.keycheck.enter.connect(self.w.okPb.click)
        self.keycheck.esc.connect(self.w.ccPb.click)
        self.w.okPb.clicked.connect(self.accept)
        self.w.ccPb.clicked.connect(self.close)
        self.w.dE.setDate(today)
        self.w.dE.setFocus()

    def accept(self):
        self.datesig.emit(self.w.dE.date().toPyDate())
        self.close()

    def update_disp(self, today):
        self.w.dE.setDate(today)
        # connect?
        
if __name__ == '__main__':
    from PyQt4.QtGui import QApplication, QShortcut
    from datetime import date
    today = date.today()
    a = QApplication([])
    a.setStyle('plastique')
    b = Datesel(today=today)
    QShortcut('Ctrl+W', b, quit)
    b.show()
    exit(a.exec_())
