"""Payment dialog -- to be called from client only."""

# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

from decimal import Decimal
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import (QMainWindow, QAction)
from payment_ui import Ui_Payment
from util import ch_conn

class Payment(QMainWindow):
    payment = pyqtSignal(tuple)
    
    def __init__(self, parent=None, totbalv=0, curbalv=0):
        super(Payment, self).__init__(parent)
        self.w = Ui_Payment()
        self.w.setupUi(self)
        self.conns = {} # qt disconnect bug
        self.sigs  = {}
        closeA = QAction(self)
        closeA.setShortcut('Ctrl+W')
        self.addAction(closeA)
        closeA.triggered.connect(self.close)
        ch_conn(self, 'valchanged', self.w.paymentSb.valueChanged, self.change)
        self.paymodes = (
            'cashRb', 'dcardRb', 'ccardRb', 'cheqRb', 'transRb', 'directRb')
        for rb in self.paymodes:
            getattr(self.w, rb).toggled.connect(self.radiocheck)
        self.w.buttonBox.rejected.connect(self.close)
        self.w.buttonBox.accepted.connect(self.done)
        self.devel()

    def change(self, val):
        dif = Decimal(str(val)) - self.curbalv
        if dif < 0:
            self.w.change.setText('0.00')
        else:
            self.w.change.setText(str(dif))

    def devel(self):
        self.totbalv = Decimal('80.63')
        self.curbalv = Decimal('80.63')
        self.w.totbal.setText(str(self.totbalv))
        self.w.curbal.setText(str(self.curbalv))

    def done(self):
        if self.w.printinvCb.isChecked():
            prinv = True
        if self.w.printrecCb.isChecked():
            prrec = True
        for rb in self.paymodes:
            if getattr(self.w, rb).isChecked():
                mode = rb[:-2]
                break
        self.payment.emit((Decimal(str(self.w.paymentSb.value())), mode,
                          prinv, prrec)) # this signal is connected in parent
        self.close()

    def radiocheck(self):
        if self.w.cashRb.isChecked():
            self.w.changeLb.setEnabled(True)
            self.w.change.setEnabled(True)
            ch_conn(
                self, 'valchanged', self.w.paymentSb.valueChanged, self.change)
            self.w.prrecCb.setEnabled(True)
        elif self.w.cashRb.isChecked() or self.w.dcard.isChecked():
            self.w.prrecCb.setEnabled(True)
        else:
            self.w.changeLb.setEnabled(False)
            self.w.change.setEnabled(False)
            self.w.prrecCb.setChecked(False)
            self.w.prrecCb.setEnabled(False)
            ch_conn(self, 'valchanged')
            
if __name__ == '__main__':
    from PyQt4.QtGui import QApplication, QShortcut
    a = QApplication([])
    w = Payment(None)
    w.show()
    exit(a.exec_())
