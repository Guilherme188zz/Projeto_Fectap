# -*- coding: utf-8 -*-

# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

# Initially created: Sun Feb  8 13:57:36 2015 by: PyQt4 UI code generator 4.11.2

# TODO:
# Wie Umlaute, z.B. UEberweisung, in deutsch?  Scheint kein Problem zu sein.
#
# Maybe: ck paymodes from db?  Increase height accordingly?

from PyQt4.QtCore import Qt # Alignment, alas
from PyQt4.QtGui import (QApplication, QCheckBox, QDialogButtonBox, 
                         QDoubleSpinBox, QLabel, QRadioButton, )

def tl(txt=''):
    return QApplication.translate("Payment", txt, None, 1)

class Ui_Payment(object):
    def setupUi(self, Payment):
        Payment.resize(431, 300)
        self.curbalLb = QLabel(Payment)
        self.curbalLb.setGeometry(20, 10, 111, 16)
        self.curbal = QLabel(Payment)
        self.curbal.setGeometry(140, 10, 101, 20)
        self.curbal.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.totbalLb = QLabel(Payment)
        self.totbalLb.setGeometry(20, 30, 111, 16)
        self.totbal = QLabel(Payment)
        self.totbal.setGeometry(140, 30, 101, 20)
        self.totbal.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.paymentLb = QLabel(Payment)
        self.paymentLb.setGeometry(20, 73, 57, 15)
        self.paymentSb = QDoubleSpinBox(Payment)
        self.paymentSb.setGeometry(112, 70, 151, 22)
        self.paymentSb.setMaximum(9999.99)
        self.paymentSb.setAlignment(
            Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.changeLb = QLabel(Payment)
        self.changeLb.setGeometry(20, 100, 52, 15)
        self.change = QLabel(Payment)
        self.change.setGeometry(120, 100, 121, 20)
        self.change.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.printinvCb = QCheckBox(Payment)
        self.printinvCb.setGeometry(20, 133, 100, 19)
        self.printrecCb = QCheckBox(Payment)
        self.printrecCb.setGeometry(20, 163, 100, 19)
        self.modeLb = QLabel(Payment)
        self.modeLb.setGeometry(280, 10, 101, 16)
        self.cashRb = QRadioButton(Payment)
        self.cashRb.setGeometry(280, 40, 120, 20)
        self.cashRb.setChecked(True)
        self.dcardRb = QRadioButton(Payment)
        self.dcardRb.setGeometry(280, 70, 120, 20)
        self.ccardRb = QRadioButton(Payment)
        self.ccardRb.setGeometry(280, 100, 120, 20)
        self.cheqRb = QRadioButton(Payment)
        self.cheqRb.setGeometry(280, 130, 120, 20)
        self.transRb = QRadioButton(Payment)
        self.transRb.setGeometry(280, 160, 120, 20)
        self.directRb = QRadioButton(Payment)
        self.directRb.setGeometry(280, 190, 120, 20)
        self.buttonBox = QDialogButtonBox(Payment)
        self.buttonBox.setGeometry(40, 240, 341, 32)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.paymentLb.setBuddy(self.paymentSb)

        self.retranslateUi(Payment)

    def retranslateUi(self, Payment):
        Payment.setWindowTitle(tl("GnuVet: Payment"))
        self.curbalLb.setText(tl("Current Balance:"))
        self.curbal.setText(tl("0.00"))
        self.totbalLb.setText(tl("Total Balance:"))
        self.totbal.setText(tl("0.00"))
        self.paymentLb.setText(tl("&Payment:"))
        self.changeLb.setText(tl("Change:"))
        self.change.setText(tl("0.00"))
        self.printinvCb.setText(tl("Pri&nt invoice"))
        self.printrecCb.setText(tl("Print r&eceipt"))
        self.modeLb.setText(tl("Payment Mode:"))
        self.cashRb.setText(tl("&Cash"))
        self.dcardRb.setText(tl("&Debit Card"))
        self.ccardRb.setText(tl("C&redit Card"))
        self.cheqRb.setText(tl("C&heque"))
        self.transRb.setText(tl("&Transfer"))
        self.directRb.setText(tl("D&irect Debit"))

if __name__ == "__main__":
    from PyQt4.QtGui import QMainWindow, QShortcut
    a = QApplication([])
    a.setStyle('plastique')
    b = Ui_Payment()
    w = QMainWindow()
    b.setupUi(w)
    QShortcut('Ctrl+W', w, quit)
    w.show()
    exit(a.exec_())
