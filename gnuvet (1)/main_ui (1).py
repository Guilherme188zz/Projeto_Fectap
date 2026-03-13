# -*- coding: utf-8 -*-

# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

# Initially created: Mon Apr 19 13:36:59 2010 by: PyQt4 UI code generator 4.4.2

from PyQt4.QtGui import (QApplication, QFont, QFrame, QLabel, QLineEdit,
                         QMenu, QPixmap, QPushButton, QShortcut, QWidget,)
from PyQt4.QtCore import Qt # for alignment

def tl(txt=''):
    return QApplication.translate("Mainform", txt, None, 1)
    
class Ui_Mainform(object):
    def setupUi(self, Mainform):
        Mainform.resize(390,280)
        Mainform.setMinimumSize(390,280)
        # one pixel, otherwise at least enlightenment hides titlebar
        Mainform.setMaximumSize(391,280)
        self.centralwidget = QWidget(Mainform)
        self.gnuLb = QLabel(self.centralwidget)
        self.gnuLb.setGeometry(90,30,214,155)
        self.gnuLb.setPixmap(QPixmap(":/images/gnu.png"))
        # quit Frame
        self.qFr = QFrame(self.centralwidget)
        self.qFr.setGeometry(10,0,361,231)
        self.qFr.setFrameStyle(0)
        self.closeLb = QLabel(self.qFr)
        self.closeLb.setGeometry(108,18,198,19)
        font = QFont()
        font.setBold(True)
        self.closeLb.setFont(font)
        self.qLb = QLabel(self.qFr)
        self.qLb.setGeometry(50,13,32,32)
        self.qLb.setPixmap(QPixmap(":/images/question.png"))
        self.noPb = QPushButton(self.qFr)
        self.noPb.setGeometry(190,190,84,30)
        self.noPb.setAutoDefault(False)
        self.noPb.setDefault(True)
        self.yesPb = QPushButton(self.qFr)
        self.yesPb.setGeometry(90,190,84,30)
        self.gnubgLb = QLabel(self.qFr)
        self.gnubgLb.setGeometry(83,30,214,155)
        self.gnubgLb.setPixmap(QPixmap(":/images/gnu-bg.png"))
        self.qFr.hide()
        # login Frame
        self.lFr = QWidget(self.centralwidget)
        self.lFr.setGeometry(10, 0, 390, 280)
        self.lgnuLb = QLabel(self.lFr)
        self.lgnuLb.setGeometry(83,30,214,155)
        self.lgnuLb.setPixmap(QPixmap(":/images/gnu-bg.png"))
        self.lognameLb = QLabel(self.lFr)
        self.lognameLe = QLineEdit(self.lFr)
        self.logpassLb = QLabel(self.lFr)
        self.logpassLe = QLineEdit(self.lFr)
        self.logokPb   = QPushButton(self.lFr)
        self.lognameLb.setGeometry(20, 73, 102, 19)
        self.lognameLe.setGeometry(160, 72, 151, 21)
        self.logpassLb.setGeometry(20, 114, 94, 19)
        self.logpassLe.setGeometry(160, 113, 151, 21)
        self.logokPb.setGeometry(145, 160, 84, 30)
        self.lognameLe.setMaxLength(25)
        self.logpassLe.setMaxLength(25)
        self.logpassLe.setEchoMode(1) # QLineEdit.NoEcho
        self.lognameLb.setBuddy(self.lognameLe)
        self.logpassLb.setBuddy(self.logpassLe)
        #devel:
        self.lFr.hide()
        # Mainform further
        Mainform.setCentralWidget(self.centralwidget)
        self.menubar = Mainform.menuBar()
        self.taskM = QMenu(self.menubar)
        self.maintM = QMenu(self.menubar)
        self.helpM = QMenu(self.menubar)
        self.statusbar = Mainform.statusBar()
        self.statusbar.setSizeGripEnabled(False)
        #    NODBCONN
        self.no_dbconn = QLabel(self.statusbar)
        self.no_dbconn.setGeometry(100, 240, 198, 19)
        self.no_dbconn.setFont(font)
        self.statusbar.addPermanentWidget(self.no_dbconn)
        self.menubar.addAction(self.taskM.menuAction())
        self.menubar.addAction(self.maintM.menuAction())
        self.menubar.addAction(self.helpM.menuAction())
        self.lLb = QLabel(Mainform)
        self.lLb.setGeometry(Mainform.width()-90, 1, 85, 19)
        self.lLb.setAlignment(Qt.AlignRight|Qt.AlignBottom)
        self.retranslateUi(Mainform)

    def retranslateUi(self, Mainform):
        Mainform.setWindowTitle(tl("GnuVet"))
        self.closeLb.setText(tl("You want to close GnuVet?"))
        self.noPb.setText(tl("&No"))
        self.noPb.setShortcut(tl("N"))
        self.yesPb.setText(tl("&Yes"))
        self.yesPb.setShortcut(tl("Y"))
        self.maintM.setTitle(tl("&Maintenance"))
        self.taskM.setTitle(tl("&Task"))
        self.helpM.setTitle(tl("&Help"))
        self.lognameLb.setText(tl("&Username:"))
        self.logpassLb.setText(tl("&Password:"))
        self.logokPb.setText(tl("&Login"))
        self.lLb.setText(tl("no login"))
        self.no_dbconn.setText(tl('No db connection...'))

if __name__ == '__main__':
    import gv_qrc
    a = QApplication([])
    from PyQt4.QtGui import QMainWindow
    Mainform = QMainWindow()
    b = Ui_Mainform()
    b.setupUi(Mainform)
    QShortcut('Ctrl+Q', Mainform, quit)
    Mainform.show()
    exit(a.exec_())
