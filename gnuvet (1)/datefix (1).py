"""Appointment setting dialog."""

# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

# TODO:
# app collisions?  -> ck_app!
# added: db_reconnect -- without really implementing it:
#     user passwd host?

from datetime import datetime, timedelta # date, time
from psycopg2 import OperationalError
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QMainWindow, QIcon
from keycheck import Keycheck
from util import ch_conn, newaction, querydb
from datefix_ui import Ui_Datefix
import gv_qrc

class Datefix(QMainWindow):
    # signals
    about = pyqtSignal()
    data = pyqtSignal(tuple)
    dbstate = pyqtSignal(object)
    gvquit = pyqtSignal(bool)
    helpsig = pyqtSignal(str)
    savestate = pyqtSignal(dict)

    # vars
    changes = False
    dberr = False
    appstaffid = None
    
    def __init__(self, parent=None, appid=None, appdt=None, apptxt=None,
                 appcid=None, apppid=None, appstf=None, appdur=None):
        super(Datefix, self).__init__(parent)
        self.parent = parent
        self.w = Ui_Datefix()
        self.w.setupUi(self)
        self.conns = {} # pyqt bug: disconnect() w/o arg can segfault
        self.sigs  = {}
        develA = newaction(self, short='Ctrl+B')
        develA.triggered.connect(self.develf)
        self.addAction(develA)
        quitA = newaction(self, short='Ctrl+Q')
        quitA.triggered.connect(self.gv_quitconfirm)
        self.addAction(quitA)
        closeA = newaction(self, short='Ctrl+W')
        closeA.triggered.connect(self.close)
        self.addAction(closeA)
        helpA = newaction(self, 'F1')
        helpA.triggered.connect(self.help_self)
        self.addAction(helpA)
        if parent: # devel if
            parent.gvquit.connect(self.gv_quit)
            self.helpsig.connect(parent.gv_help)
            self.options = parent.options
            self.db = parent.db
            self.staffid = parent.staffid
        else:
            from options import defaults as options
            self.options = options
            self.staffid = 1
            import dbmod
            dbh = dbmod.Db_handler('enno')
            self.db = dbh.db_connect()
            if type(self.db) is str:
                self.db_state(self.db)
                return
        try:
            self.curs = self.db.cursor()
        except (OperationalError, AttributeError) as e:
            self.db_state(e)
            return
        self.populstaff()
        if self.dberr:
            return
        if 'cal_res' in self.options:
            self.cal_res = self.options['cal_res']
        else:
            self.cal_res = 0
        self.popultimes()
        self.populmarks()
        self.pid = apppid
        self.cid = appcid
        self.w.shortCb.stateChanged.connect(self.toggleshort)
        self.update_disp(appid, appdt, apptxt, appcid,
                         apppid, appstf, appdur)
        self.keycheck = Keycheck(self)
        self.installEventFilter(self.keycheck)
        self.keycheck.enter.connect(self.w.okPb.click)
        self.keycheck.esc.connect(self.w.ccPb.click)
        ## self.w.timeDd.activated.connect(self.ck_app)
        ## self.w.staffDd.activated.connect(self.ck_app)
        self.w.okPb.setDefault(True)
        self.w.okPb.setAutoDefault(True)
        self.w.patPb.clicked.connect(self.getpat)
        self.w.cliPb.clicked.connect(self.getcli)
        self.w.okPb.clicked.connect(self.done)
        self.w.resetPb.clicked.connect(self.reset)
        self.w.ccPb.clicked.connect(self.close)

    def adjdur(self):
        pass
    
    ## def ck_app(self): # dies auslagern in appoint
    ##     if not self.appstaffid or self.w.shortCb.isChecked():
    ##         return
    ##     startdt = datetime.strptime(
    ##         str(self.w.dateDe.date().toString('dd.MM.yyyy')) + ' ' +
    ##         str(self.w.timeDd.currentText()), '%d.%m.%Y %H:%M')
    ##     td = map(int, str(self.w.timeDd.currentText()).split(':'))
    ##     td = timedelta(0, td[0]*3600 + td[1]*60)
    ##     res = querydb(
    ##         self,
    ##         'select app_id,app_dt,app_text,app_cid,app_pid,app_dur from '
    ##         "appointments where app_dur!='0' and(app_dt,app_dur)overlaps(%s,%s)"
    ##         'and app_staffid=%s',
    ##         (startdt, td, self.appstaffid))
    ##     if res is None:  return # db error
    ##     for e in res:
    ##         self.w.dateDe.setDate(e[1])
    ##         self.w.timeDd.setCurrentIndex(self.w.timeDd.findText(
    ##             e[1].strftime('%H:%M')))
    ##         if e[3]:
    ##             self.setcli(e[3])
    ##         if e[4]:
    ##             self.setpat(e[4])
    ##         self.w.tLe.setPlainText(e[2])
    ##         self.w.durDd.setCurrentIndex(self.w.durDd.findText(
    ##             '{:02}:{:02}'.format(
    ##                 e[5].seconds/3600, (e[5].seconds%3600)/60)))
    ##         self.appid = e[0]
    ##         self.setWindowTitle('GnuVet: ' + self.tr('Edit Appointment'))
    ##         self.action = 'e' # edit

    def db_reconnect(self): # copied from gnuv.py, remodel to self.gaia!
        args = {}
        if self.user:
            args['user'] = self.user
        if self.passwd:
            args['passwd'] = self.passwd
        if self.dbhost:
            args['dbhost'] = self.dbhost
        self.dbh = dbmod.Db_handler(**args)
        self.db = self.dbh.db_connect()
        if not self.db or isinstance(self.db, str):
            return
        ##self.dbdep_enable() # not implemented here (?)
        self.curs = self.db.cursor()
        self.dbstate.emit(self.db)
        
    def db_state(self, msg=''):
        """Actions to be taken on db loss or gain."""
        self.dberr = msg and True or False
        ## self.w.no_dbconn(setVisible(self.dberr) # implement in appoint?
        self.dbstate.emit(not self.dberr)
        ## self.dbdep_enable(not self.dberr)
        if not self.parent: # devel
            if not hasattr(self, 'warnw'):
                from warn import Warning
            if not msg:
                msg = self.tr('Unspecified db error.')
            self.warnw = Warning(self, self.tr('GnuVet: Db Error'), msg)
            if not self.isVisible():
                self.warnw.closed.connect(self.show)
        
    def done(self):
        h, m = map(int, self.w.timeDd.currentText().split(':'))
        datum = self.w.dateDe.date().toPyDate()
        dur = map(int, str(self.w.durDd.currentText()).split(':'))
        dur = dur[0]*3600 + dur[1]*60
        self.data.emit(
            (datetime(datum.year, datum.month, datum.day, h, m),
             str(self.w.tLe.toPlainText()),
             self.cid,
             self.pid,
             self.appstaffid,
             timedelta(0, dur),
             self.action,
             self.w.markDd.currentIndex() and
             (self.w.markDd.currentIndex() == 1 and 'd' or
              self.w.markDd.currentIndex() == 2 and 'm') or 'o'))
        self.close()

    def getcli(self):
        if not hasattr(self, 'cliw'):
            from saecli import Saecli
            self.cliw = Saecli(self)
        else:
            self.cliw.raise_()
        self.cliw.show()
        self.cliw.cidsig.connect(self.setcli)

    def getpat(self):
        if not hasattr(self, 'patw'):
            from saepat import Saepat
            self.patw = Saepat(self)
        else:
            self.patw.raise_()
        self.patw.show()

    def gv_help(self, page=''):
        self.helpsig.emit(page)
        
    def gv_quit(self, quitnow=False): # cave: Action.checked = False
        self.shutdown = quitnow
        self.gvquit.emit(quitnow)
        if quitnow:
            self.close()
        
    def gv_quitconfirm(self):
        if self.parent:
            self.parent.gv_quitconfirm()
        else:
            self.close()

    def help_self(self):
        self.helpsig.emit('datefix.html')

    def populdur(self):
        self.w.durDd.clear()
        self.durs = []
        for t in xrange(8):
            if t:
                self.durs.append('{:02}:00'.format(t))
            if self.cal_res == 2:
                self.durs.append('{:02}:15'.format(t))
                self.durs.append('{:02}:30'.format(t))
                self.durs.append('{:02}:45'.format(t))
            elif self.cal_res == 1:
                self.durs.append('{:02}:30'.format(t))
        if self.appdur and (self.appdur not in self.durs):
           for e in self.durs:
               if e < self.appdur:  continue
               self.durs.insert(self.durs.index(e), self.appdur)
               break
        for e in self.durs:
            self.w.durDd.addItem(e)
        self.w.durDd.setEnabled(True)

    def populmarks(self):
        """open done missed -- should be enough."""
        ## addItem ( const QIcon & icon, const QString & text, const QVariant & userData = QVariant() )
        self.w.markDd.addItem(QIcon(":/images/markopen.png"), self.tr('open'))
        self.w.markDd.addItem(QIcon(":/images/markdone.png"), self.tr('done'))
        self.w.markDd.addItem(QIcon(":/images/markmissed.png"),
                              self.tr('missed'))
                
    def populstaff(self):
        stf = querydb(
            self,
            'select stf_id,stf_short from staff order by stf_short')
        if stf is None:  return # db error
        self.w.staffDd.addItem('None', 0)
        if not stf:
            self.w.staffLb.hide()
            self.w.staffDd.hide()
            return
        for e in stf:
            self.w.staffDd.addItem(e[1], e[0])
        self.w.staffDd.currentIndexChanged.connect(self.setappstaff)
        if self.staffid:
            self.w.staffDd.setCurrentIndex(
                self.w.staffDd.findData(self.staffid, 32))

    def popultimes(self):
        for t in xrange(24):
            self.w.timeDd.addItem('{:02}:00'.format(t))
            if self.cal_res == 2:
                self.w.timeDd.addItem('{:02}:15'.format(t))
                self.w.timeDd.addItem('{:02}:30'.format(t))
                self.w.timeDd.addItem('{:02}:45'.format(t))
            elif self.cal_res == 1:
                self.w.timeDd.addItem('{:02}:30'.format(t))

    def reset(self):
        self.w.staffDd.setCurrentIndex(0)
        self.appstaffid = None
        self.w.patPb.setText(self.tr('&Pat: unknown'))
        self.pid = None
        self.w.cliPb.setText(self.tr('&Cli: unknown'))
        self.w.tLe.setPlainText('')
        self.w.durDd.setCurrentIndex(0)
        self.setWindowTitle('GnuVet: ' + self.tr('Set Appointment'))
    
    def setappstaff(self, stfid):
        self.appstaffid = self.w.staffDd.itemData(stfid, 32).toInt()[0]
        if not stfid:
            self.appstaffid = None

    def setcli(self, cid): # hierwei confirm owner change?
        self.cid = cid
        self.csname = querydb(
            self,
            'select c_sname from clients where c_id=%s', (cid,))
        if self.csname is None:  return # db error
        self.csname = self.csname[0][0]
        self.w.cliPb.setText(self.tr('&Cli: ') + self.csname)

    def setpat(self, pid):
        self.pid = pid
        self.pname = querydb(
            self,
            'select p_name,p_cid from patients where p_id=%s', (pid,))
        if self.pname is None:  return # db error
        self.cid = self.pname[0][1]
        self.pname = self.pname[0][0]
        self.csname = querydb(
            self,
            'select c_sname from clients where c_id=%s', (self.cid,))
        if self.csname is None:  return # db error
        self.csname = self.csname[0][0]
        self.w.patPb.setText(self.tr('&Pat: ') + self.pname)
        self.w.cliPb.setText(self.tr('&Cli: ') + self.csname)
        self.raise_()
        self.w.tLe.setFocus()

    def state_write(self, data=None):
        if self.parent:
            self.savestate.connect(self.parent.state_write)
        self.savestate.emit(data)
        if self.parent:
            self.savestate.disconnect(self.parent.state_write)
    
    def toggleshort(self, state):
        if state:
            self.w.durDd.clear()
            self.w.durDd.addItem('{:02}:00'.format(0))
            self.w.durDd.setEnabled(False)
        else:
            self.populdur()
            
    def update_disp(self, appid=None, appdt=None, apptxt=None, appcid=None,
                    apppid=None, appstf=None, appdur=None):
        """Set widgets on existing datefix."""
        if appdur:
            self.appdur = '0' + ':'.join(str(appdur).split(':')[:2])
        else:
            self.appdur = None
        self.populdur()
        if appid:
            self.action = 'e'
            appdate = appdt.date()
            apptime = appdt.strftime('%H:%M')
            self.w.tLe.setText(apptxt)
            self.w.staffDd.setCurrentIndex(
                self.w.staffDd.findData(appstf, 32))
            if apppid:
                self.setpat(apppid)
            if appcid and (self.cid != appcid):
                self.setcli(appcid)
            if self.appdur:
                self.w.durDd.setCurrentIndex(self.w.durDd.findText(
                    self.appdur))
                self.w.shortCb.setChecked(False)
            else:
                self.w.shortCb.setChecked(True)
        else:
            self.action = 'a'
            self.reset()
            appdate = appdt.date()
            if 'starttime' in self.options:
                apptime = self.options['starttime']
            else:
                apptime = '08:30'
            if len(apptime) == 4:
                apptime = '0' + apptime
            self.w.shortCb.setChecked(False)
        ch_conn(self, 'datede')
        self.w.dateDe.setDate(appdate)
        self.w.timeDd.setCurrentIndex(self.w.timeDd.findText(apptime))
        ## ch_conn(self, 'datede', self.w.dateDe.dateChanged, self.ck_app)

    def develf(self):
        print('selected staff: {} {}'.format(
            self.w.staffDd.currentIndex(), self.w.staffDd.currentText()))
        
if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    a = QApplication([])
    a.setStyle('plastique')
    b = Datefix(appdt=datetime.now())
    ## b.w.dateDe.setDate()
    ## b.w.timeDd.setCurrentIndex(15)
    b.show()
    exit(a.exec_())

    
