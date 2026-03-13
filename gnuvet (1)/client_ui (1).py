# -*- coding: utf-8 -*-

# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

# Initially created: Fri Feb 18 13:30:31 2011 by: PyQt4 UI code generator 4.7.3

# TODO:
# why's menubar smaller than in other windows?
# eliminate self.centralwidget?

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QApplication, QComboBox, QFont, QWidget, QLabel,
                         QPixmap, QPushButton)
from gtable import Gtable

def tl(txt=''):
    return QApplication.translate("Client", txt, None, 1)

class Ui_Client(object):
    def setupUi(self, Client):
        Client.resize(957, 660)
        Client.setMinimumSize(957, 661)
        self.centralwidget = QWidget(Client)
        self.menubar = Client.menuBar()
        self.statusbar = Client.statusBar()
        self.statusbar.setSizeGripEnabled(False)
        self.no_dbconn = QLabel(self.statusbar)
        font = QFont()
        font.setBold(True)
        self.no_dbconn.setFont(font)
        self.statusbar.addPermanentWidget(self.no_dbconn, 0)
        self.no_dbconn.hide()
        self.lLb = QLabel(Client)
        self.lLb.setGeometry(Client.width()-90, 1, 85, 19)
        self.lLb.setAlignment(Qt.AlignRight|Qt.AlignBottom)
        self.nameLb = QLabel(self.centralwidget)
        self.nameLb.setGeometry(10, 10, 281, 19)
        self.nameLb.setMinimumSize(0, 19)
        self.nameLb.setMaximumSize(291, 19)
        self.addr1Lb = QLabel(self.centralwidget)
	self.addr1Lb.setGeometry(10, 30, 241, 19)
        self.addr1Lb.setTextInteractionFlags(
            Qt.TextSelectableByMouse|Qt.TextSelectableByKeyboard)
        self.addr2Lb = QLabel(self.centralwidget)
	self.addr2Lb.setGeometry(10, 50, 241, 19)
        self.addr2Lb.setTextInteractionFlags(
            Qt.TextSelectableByMouse|Qt.TextSelectableByKeyboard)
        self.addr3Lb = QLabel(self.centralwidget)
	self.addr3Lb.setGeometry(10, 70, 241, 19)
        self.addr3Lb.setTextInteractionFlags(
            Qt.TextSelectableByMouse|Qt.TextSelectableByKeyboard)
        self.telLb = QLabel(self.centralwidget)
	self.telLb.setGeometry(10, 90, 40, 19)
        self.telDd = QComboBox(self.centralwidget)
        self.telDd.setGeometry(60, 88, 270, 22)
        self.bdPix = QLabel(self.centralwidget)
        self.bdPix.setGeometry(300, 10, 17, 20)
        self.bdPix.setPixmap(QPixmap(":/images/redflag.png"))
        self.emailLb = QLabel(self.centralwidget)
	self.emailLb.setGeometry(370, 10, 250, 18)
        self.emailLb.setMaximumSize(290, 18)
        self.lastLb = QLabel(self.centralwidget)
	self.lastLb.setGeometry(370, 50, 90, 18)
        self.ldateLb = QLabel(self.centralwidget)
	self.ldateLb.setGeometry(465, 50, 80, 18)
        self.regLb = QLabel(self.centralwidget)
	self.regLb.setGeometry(370, 70, 90, 18)
        self.regdateLb = QLabel(self.centralwidget)
	self.regdateLb.setGeometry(465, 70, 80, 18)
        self.annoLb = QLabel(self.centralwidget)
	self.annoLb.setGeometry(680, 10, 81, 19)
        self.annoLb.setTextInteractionFlags(
            Qt.TextSelectableByMouse|Qt.TextSelectableByKeyboard)
        self.annotxtLb = QLabel(self.centralwidget)
	self.annotxtLb.setGeometry(680, 30, 251, 131)
        self.annotxtLb.setWordWrap(1)
        self.annotxtLb.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self.nameLb.setFont(font)
        self.patientsLb = QLabel(self.centralwidget)
	self.patientsLb.setGeometry(10, 156, 66, 18)
        self.patientsLb.setFont(font)
        self.patientsLb.setTextFormat(Qt.PlainText)
        self.newPb = QPushButton(self.centralwidget)
        self.newPb.setGeometry(330, 130, 140, 24)
        self.ripPb = QPushButton(self.centralwidget)
        self.ripPb.setGeometry(490, 130, 140, 24)
        self.plist = Gtable(self.centralwidget, resizecols=True, scrollh=0)
        self.plist.setGeometry(10, 180, 921, 371)
        self.plist.setMinimumSize(621, 371)
        self.balLb = QLabel(self.centralwidget)
	self.balLb.setGeometry(10, 570, 107, 18)
        self.balanceLb = QLabel(self.centralwidget)
	self.balanceLb.setGeometry(130, 570, 72, 18)
        self.balanceLb.setAlignment(
            Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.mainPb = QPushButton(self.centralwidget)
        self.mainPb.setGeometry(340, 570, 140, 24)
        self.cancelPb = QPushButton(self.centralwidget)
        self.cancelPb.setGeometry(500, 570, 140, 24)
        Client.setCentralWidget(self.centralwidget)
        self.retranslateUi(Client)

    def retranslateUi(self, Client):
        Client.setWindowTitle(tl("GnuVet: Client"))
        # devel:
        if __name__ == '__main__':
            self.nameLb.setText(tl("Mr Client N"))
            self.addr1Lb.setText(tl("House Street"))
            self.addr2Lb.setText(tl("Village, City"))
            self.addr3Lb.setText(tl("B76 0BA"))
            self.telLb.setText(tl("Tel:"))
            self.balanceLb.setText(tl("0.00"))
            self.ldateLb.setText(tl("30.04.2009"))
            self.regdateLb.setText(tl("18.12.2008"))
            self.telDd.addItem(tl('+43 664 675 60 22'))
        # end devel
        self.annoLb.setText(tl("Annotations:"))
        self.bdPix.setToolTip(tl("Bad Debtor"))
        self.emailLb.setText(tl("client.surname@provider.net"))
        self.lastLb.setText(tl("Last Seen:"))
        self.regLb.setText(tl("Registered:"))
        self.patientsLb.setText(tl("Patients:"))
        self.newPb.setText(tl("New Patient"))
        self.ripPb.setText(tl("&Mark as deceased"))
        self.balLb.setText(tl("Current Balance:"))
        self.mainPb.setText(tl("Select &Patient"))
        self.cancelPb.setText(tl("Cancel"))
        self.cancelPb.setShortcut(tl("Esc"))
        self.no_dbconn.setText(tl("No db connection..."))

if __name__ == '__main__':
    from PyQt4.QtGui import QMainWindow, QShortcut
    import gv_qrc
    a = QApplication([])
    a.setStyle('plastique')
    b = Ui_Client()
    w = QMainWindow()
    b.setupUi(w)
    b.lLb.setText('client_ui')
    QShortcut('Ctrl+W', w, quit)
    b.no_dbconn.show()
    w.show()
    exit(a.exec_())
