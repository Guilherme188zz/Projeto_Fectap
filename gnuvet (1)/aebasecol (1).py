"""Add or edit base-colours."""

# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

# TODO:
# replace spec_code char -> bit?
# save all basecolours as col.lower()?

from psycopg2 import OperationalError
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import (QCheckBox, QLabel, QMainWindow, QMenu)

from keycheck import Keycheck
from util import ch_conn, newaction, querydb
from aebasecol_ui import Ui_Aebasecol

class Aebasecol(QMainWindow):
    # signals
    addedbc = pyqtSignal(int, str, str)
    gaia    = None
    helpsig = pyqtSignal(str)
    savestate = pyqtSignal(list)

    def __init__(self, parent=None):
        super(Aebasecol, self).__init__(parent)
        self.w = Ui_Aebasecol()
        self.w.setupUi(self)
        self.conns = {} # pyqt bug: disconnect() w/o arg can segfault
        self.sigs  = {}
        #    ACTIONS
        closeA = newaction(self, 'Close &Window', 'Close this window', 'Ctrl+W')
        self.dbA = newaction(self, '&Reconnect to database',
                             'Try to reconnect to database', 'Ctrl+R')
        helpA = newaction(self, '&Help', 'Context sensitive help', 'F1')
        aboutA = newaction(self, 'About &GnuVet', 'GnuVet version info')
        quitA = newaction(
            self, '&Quit GnuVet', 'Close all windows and quit GnuVet', 'Ctrl+Q')
        self.addAction(closeA)
        #    MENUES
        taskM = QMenu('&Task', self.w.menubar)
        helpM = QMenu('&Help', self.w.menubar)
        self.w.menubar.addAction(taskM.menuAction())
        self.w.menubar.addAction(helpM.menuAction())
        taskM.addAction(self.dbA)
        taskM.addSeparator()
        taskM.setSeparatorsCollapsible(True)
        taskM.addAction(closeA)
        taskM.addAction(quitA)
        helpM.addAction(helpA)
        helpM.addSeparator()
        helpM.addAction(aboutA)
        #    CONNECTIONS
        closeA.triggered.connect(self.close)
        helpA.triggered.connect(self.help_self)
        quitA.triggered.connect(self.gv_quitconfirm)
        self.w.allCb.stateChanged.connect(self.sel_all)
        self.w.togglePb.clicked.connect(self.toggle)
        #    GAIA
        if parent: # devel if
            if parent.gaia == 'gaia':
                self.gaia = parent
            else:
                self.gaia = parent.gaia
            self.options = self.gaia.options
            self.db = self.gaia.db
            self.dbA.triggered.connect(self.gaia.db_reconnect)
            aboutA.triggered.connect(self.gaia.about)
            self.gaia.gvquit.connect(self.gv_quit)
            self.gaia.dbstate.connect(self.db_state)
            self.helpsig.connect(self.gaia.gv_help)
        ## else: # commented out for devel
        ##     from options import defaults as options
        ##     self.options = options
        ##     import dbmod
        ##     dbh = dbmod.Db_handler('enno')
        ##     self.db = dbh.db_connect()
        ##     if type(self.db) ist str:
        ##         self.db_state(self.db)
        ##         return
        ## if 'lang' in self.options and self.options['lang'] == 'en':
        ##     setlocale(LC_ALL, 'C')
        ## else:
        ##     resetlocale()
        ## try:
        ##     self.curs = self.db.cursor()
        ## except (OperationalError, AttributeError) as e: # No db
        ##     self.db_state(e)
        ##     return
        #    INIT
        self.dbA.setVisible(False)
        self.dbA.setEnabled(False)
        ## l = querydb(self,
        ##             'select spec_name,spec_id,spec_code from species '
        ##             'order by spec_name')
        # devel:
        l = (('Canine', 1, False), ('Feline', 2, False),
             ('Rabbit', 4, True), ('Rodent', 8, False)) # end devel
        if l is None:  return # db error
        ly = 41
        lincr = 26
        self.cblist = []
        self.id2spec = {}
        for s in l:
            cb = QCheckBox(s[0], self.w.specFr)
            cb.setGeometry(20, ly, 200, 21)
            self.cblist.append(cb)
            cb.stateChanged.connect(self.ckall)
            self.id2spec[s[1]] = s[2]
            ly += lincr
        self.w.specFr.resize(self.w.specFr.width(), ly + 10)
        self.keycheck = Keycheck(self)
        self.installEventFilter(self.keycheck)
        ch_conn(self, 'esc', self.keycheck.esc, self.w.closePb.click)
        self.w.closePb.clicked.connect(self.close)
        self.w.errFr.hide()
        self.w.confFr.hide()
        self.show()

    def ckall(self, state):
        if state == 0:
            self.w.allCb.setChecked(False)
    
    def closeEvent(self, ev):
        pass

    def confirm(self):
        """Ck data and ask for confirmation."""
        pass
    
    def db_state(self, msg=''):
        """Actions to be taken on db loss or gain."""
        self.dberr = msg and True or False
        self.w.no_dbconn.setVisible(self.dberr)
        self.dbstate.emit(not self.dberr)
        self.dbdep_enable(not self.dberr)

    def done(self):
        data = [str(bcnameLe.text().toLatin1()).lower()]
        ##data.append(or all cbs)
        ##data.append(ck combination radiobuttons)
        suc = querydb(self,
                      'insert into basecolours(bcol,bc_speccode,bc_combine)'
                      'values(%1, %2, %3)returning bcol_id', data)
        if suc is None:  return # db error
        # ...
        self.newbc.emit(tuple)
        self.close()
        
    def errormsg(self, msg='', level=None):
        pass
        
    def gv_quitconfirm(self):
        if self.gaia:
            self.gaia.gv_quitconfirm()
        else:
            self.close()

    def help_self(self):
        self.helpsig.emit('aebasecol.html')

    def restore(self):
        """Restore state from pre-crash."""
        pass

    def save_state(self):
        """Save unsaved data to file in case of db loss."""
        pass
    
    def sel_all(self, state):
        if state == 2:
            for c in self.cblist:
                c.setChecked(True)

    def toggle(self):
        for c in self.cblist:
            if c.isChecked():
                c.setChecked(False)
            else:
                c.setChecked(True)

if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    a = QApplication([])
    a.setStyle('plastique')
    b = Aebasecol()
    exit(a.exec_())
