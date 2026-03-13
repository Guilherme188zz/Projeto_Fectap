"""The help module."""
# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

from os import uname, path
from PyQt4.QtCore import QUrl, pyqtSignal
from PyQt4.QtGui import QMainWindow, QMenu
from help_ui import Ui_Help
import gv_qrc
from util import newaction

class Help(QMainWindow):
    def __init__(self, parent=None, hdoc='toc.html'):
        super(Help, self).__init__(parent)
        self.w = Ui_Help()
        self.w.setupUi(self)
        self.w.textBrowser.setSearchPaths(self.help_dir())
        #    ACTIONS
        self.backA = newaction(self, 'Bac&k', 'Go to previous page', 'Alt+Left')
        self.forwardA = newaction(self,'&Forward','Go to next page','Alt+Right')
        closeA = newaction(self, '&Close', 'Close Help Window', 'Ctrl+W')
        contentsA = newaction(self, 'Co&ntents', 'Go to Table of Contents')
        indexA = newaction(self, 'Help &Index', 'Go to Help Index', 'Ctrl+I')
        quitA = newaction(self, '&Quit GnuVet', 'Quit GnuVet', 'Ctrl+Q')
        helpA = newaction(self, '&Help', 'How to use the Help System', 'F1')
        #    MENUES
        goM = QMenu(self.w.menubar)
        goM.setTitle(self.tr('&Go'))
        helpM = QMenu(self.w.menubar)
        helpM.setTitle(self.tr('&Help'))
        self.w.menubar.addAction(goM.menuAction())
        self.w.menubar.addAction(helpM.menuAction())
        goM.addAction(self.backA)
        goM.addAction(self.forwardA)
        goM.addSeparator()
        goM.addAction(contentsA)
        goM.addAction(indexA)
        goM.addSeparator()
        goM.addAction(closeA)
        goM.addAction(quitA)
        helpM.addAction(helpA)
        self.backA.setEnabled(0)
        self.forwardA.setEnabled(0)
        self.w.backTb.setEnabled(0)
        self.w.forwardTb.setEnabled(0)
        #    CONNECTIONS
        quitA.triggered.connect(self.gv_quitconfirm)
        helpA.triggered.connect(self.help_help)
        indexA.triggered.connect(self.help_index)
        closeA.triggered.connect(self.close)
        self.w.textBrowser.backwardAvailable.connect(self.toggle_back)
        self.w.textBrowser.forwardAvailable.connect(self.toggle_forw)
        self.w.backTb.clicked.connect(self.w.textBrowser.backward)
        self.backA.triggered.connect(self.w.textBrowser.backward)
        self.w.forwardTb.clicked.connect(self.w.textBrowser.forward)
        self.forwardA.triggered.connect(self.w.textBrowser.forward)
        contentsA.triggered.connect(self.contents_help)
        self.show()
        self.show_help(hdoc)

    def contents_help(self):
        self.help_file('toc.html')

    def gv_quitconfirm(self):
        if self.parent():
            self.parent().gv_quitconfirm()
        else:
            exit()
            
    def help_dir(self):
        """Return list of paths to help docs for setSearchPaths()."""
        if not 'os_name' in locals():
            from os import name as os_name
        if os_name == 'posix':
            return ['/usr/share/gnuvet/help/']
        elif os_name == 'nt':
            return ['/Program Files/gnuvet/help/']
        else:
            print('Xorry, OSs other than "posix" and "nt" not yet implemented.')
            return []

    def help_file(self, hfile):
        self.w.textBrowser.setSource(QUrl(hfile))

    def help_help(self):
        self.help_file('help.html')

    def help_index(self):
        self.help_file('index.html')

    def resizeEvent(self, ev):
        self.w.textBrowser.resize(ev.size().width(), ev.size().height()-89)

    def show_help(self, hdoc='toc.html'):
        self.help_file(hdoc)

    def toggle_back(self, avail=False):
        if avail:
            self.w.backTb.setEnabled(1)
            self.backA.setEnabled(1)
        else:
            self.w.backTb.setEnabled(0)
            self.backA.setEnabled(0)

    def toggle_forw(self, avail=False):
        if avail:
            self.w.forwardTb.setEnabled(1)
            self.forwardA.setEnabled(1)
        else:
            self.w.forwardTb.setEnabled(0)
            self.forwardA.setEnabled(0)

if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    a = QApplication([])
    c = Help(None)
    exit(a.exec_())
