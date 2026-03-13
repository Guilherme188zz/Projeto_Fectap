"""Client window."""

# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

# TODO:
# see playground re payment before continuing here
# add buttons for patient: New MarkAsRIP
#     ChangeOwner only from patient window
#  and resp Actions/functions
#  and resp button connections...
# 
# check for things like card or cheque payment only be booked as payed when
# payment is confirmed from gnuv.py, s. below

from datetime import date
from decimal import Decimal as D
from psycopg2 import OperationalError
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QMainWindow, QMenu
import gv_qrc
from keycheck import Keycheck
from util import ch_conn, gprice, money, newaction, querydb
from client_ui import Ui_Client

class Client(QMainWindow):
    """The client window, from which to choose a patient and such."""
    # signals:
    gvquit   = pyqtSignal(bool)
    helpsig  = pyqtSignal(str)
    savestate = pyqtSignal(str)

    # vars:
    db_err = changes = shutdown = False

    def __init__(self, parent=None, cid=0):
        super(Client, self).__init__(parent)
        self.conns  = {} # pyqt bug, disconnect() w/o arg can segfault
        self.sigs   = {}
        self.cid = cid
        self.w = Ui_Client()
        self.w.setupUi(self)
        keych = Keycheck(self)
        self.installEventFilter(keych)
        #    LOCAL VARIABLES
        #    ACTIONS
        closeA = newaction(self, 'Close &Window', 'Close this window', 'Ctrl+W')
        self.dbA = newaction(self, '&Reconnect to database',
                             'Try to reconnect to database', 'Ctrl+R')
        aboutA = newaction(self, 'About &Gnuvet', 'GnuVet version info')
        helpA = newaction(self, '&Help', 'Context sensitive help', 'F1')
        quitA = newaction(self, '&Quit GnuVet', 'Quit GnuVet', 'Ctrl+Q')
        self.editA = newaction(
            self, '&Edit Client', 'Edit client record', 'Ctrl+E')
        self.mrgA = newaction(
            self, '&Merge Client',
            'Merge this client\'s accounts if you have more than one')
        self.newpatA = newaction(
            self, '&Patient', 'Add a patient to this client', 'Ctrl+P')
        self.newsaleA = newaction(
            self, 'S&ale', 'Enter patient-unrelated sale', 'Ctrl+A')
        self.newpayA = newaction(self, 'Pa&yment', 'Take payment', 'Ctrl+Y')
        self.rippatA = newaction(self, '&Mark patient deceased',
                                 'Mark selected patient as deceased', 'Ctrl+K')
        # ...
        #    MENUES
        taskM = QMenu(self.w.menubar)
        taskM.setTitle(self.tr('&Task'))
        self.w.menubar.addAction(taskM.menuAction())
        newM = QMenu(self.w.menubar)
        newM.setTitle(self.tr('&New'))
        self.w.menubar.addAction(newM.menuAction())
        helpM = QMenu(self.w.menubar)
        helpM.setTitle(self.tr('&Help'))
        self.w.menubar.addAction(helpM.menuAction())
        #    SUBMENUES
        taskM.addAction(self.dbA)
        taskM.addSeparator()
        taskM.addAction(self.editA)
        taskM.addAction(self.mrgA)
        taskM.addAction(self.rippatA)
        taskM.addSeparator()
        taskM.addAction(closeA)
        taskM.addAction(quitA)
        taskM.setSeparatorsCollapsible(1)
        newM.addAction(self.newpatA)
        newM.addAction(self.newsaleA)
        newM.addAction(self.newpayA)
        helpM.addAction(helpA)
        helpM.addSeparator()
        helpM.addAction(aboutA)
        #    ACTION CONNECTIONS
        closeA.triggered.connect(self.close)
        self.editA.triggered.connect(self.editc)
        helpA.triggered.connect(self.help_self)
        quitA.triggered.connect(self.gv_quitconfirm)
        self.mrgA.triggered.connect(self.merge)
        self.newpatA.triggered.connect(self.addpat)
        self.newsaleA.triggered.connect(self.sale)
        self.newpayA.triggered.connect(self.payment)
        self.rippatA.triggered.connect(self.rip)
        #    PARENT CONNECTIONS
        if parent: # devel if
            if parent.gaia == 'gaia':
                self.gaia = parent
            else:
                self.gaia = parent.gaia
            self.dbA.triggered.connect(self.gaia.db_connect)
            aboutA.triggered.connect(self.gaia.about)
            self.gaia.gvquit.connect(self.gv_quit)
            self.gaia.dbstate.connect(self.db_state)
            ## self.savestate.connect(self.gaia.state_write)
            self.helpsig.connect(self.gaia.gv_help)
            self.db = self.gaia.db
            self.staffid = self.gaia.staffid
            self.options = self.gaia.options
        else:
            import dbmod
            dbh = dbmod.Db_handler('enno')
            self.db = dbh.db_connect()
            # devel:
            ##self.db.set_client_encoding('UTF-8')
            self.staffid = 1
            from options import defaults as options
            self.options = options
        #    BUTTON CONNECTIONS
        self.w.cancelPb.clicked.connect(self.close)
        #    INIT
        #ch_conn(self, 'enter', self.keych.enter, self.w.mainPb.click)
        #self.w.mainPb.clicked.connect(self.whatever)
        self.dbA.setVisible(0)
        self.dbA.setEnabled(0)
        try:
            self.curs = self.db.cursor()
        except (OperationalError, AttributeError) as e: # no db connection
            self.db_state(e)
            return
        logname = 'no login' # neu
        lname = querydb(
            self,
            'select stf_logname from staff where stf_id=%s', (self.staffid,))
        if lname is None:  return # db error
        logname = lname[0][0]
        self.w.lLb.setText(logname)
        self.cli_data()
        self.get_pats()
        ## self.get_vats() # hierwei: make this dep on using product

    def addpat(self):
        print('client.addpat not yet implemented')
        self.origin.sae_pat(cid=self.cid, act='a')
        ch_conn(self, 'newpat', self.gaia.newpat, self.cli_data)
        # hierwei: could be ready
        
    def cli_data(self):
        """Collect client data including associated patients."""
        ch_conn(self, 'newpat')
        res = querydb(
            self,
            'select t_title,c_sname,c_mname,c_fname,housen,street,village,city,'
            'region,postcode,c_email,'
            'baddebt,c_reg,c_last,c_anno from clients,titles,addresses where '
            't_id=c_title and c_address=addr_id and c_id=%s',
            (self.cid,))
        if res is None:  return # db error
        for e in res:
            name = ' '.join([e[0], e[1]])
            if e[2]:
                name = ', '.join([name, e[2]])
            name = ' '.join([name, e[3]])
            self.w.nameLb.setText(name)
            self.w.addr1Lb.setText(', '.join([s for s in e[4:6] if s]))
            self.w.addr2Lb.setText(', '.join([s for s in e[6:8] if s]))
            self.w.addr3Lb.setText(e[9])
            self.w.emailLb.setText(e[10])
            self.w.bdPix.setVisible(e[11])
            self.w.regdateLb.setText(e[12].strftime('%d.%m.%y'))
            self.w.ldateLb.setText(e[13].strftime('%d.%m.%y'))
            if e[14]: # devel if
                self.w.annotxtLb.setText(e[14])
            else:
                self.w.annotxtLb.setText(
                    'This is our first client, being the first sentient being '
                    'to have brought patients to our GnuVet practice.')
        res = querydb(
            self,
            'select phone_num,phone_anno from phones ' # hierwei
            'where phone_clid=%s order by phone_opt', (self.cid,))
        if res is None:  return # db error
        if not res:
            self.w.telDd.addItem(self.tr('n/a'))
            self.w.telDd.setEnabled(False)
        else:
            addend = ' (best) '
            for p in res:
                self.w.telDd.addItem(p[0] + addend + p[1])
                if addend:
                    addend = ' '
        # hierwei here was table creation
        cbal = D('0.00')
        res = querydb(
            self,
            "select tablename from pg_tables where tablename like 'pay{}'"
            .format(self.cid))
        if res is None:  return # db error
        if not res or not res[0]:
            bal = querydb(
                self,
                'select sum(acc_npr*(1+vat_rate))from acc{},vats where acc_vat'
                '=vat_id'.format(self.cid))
        else:
            bal = querydb(
                self,
                'select sum(acc_npr*(1+vat_rate)-(select sum(pay_amount)from '
                'pay{0})from acc{0} where acc_vat=vat_id') # hierwei
        self.w.balanceLb.setText(D(str(cbal)))
        
    def closeEvent(self, ev):
        if hasattr(self, 'gaia') and self.gaia:
            self.gaia.xy_decr()

    def dbdep_enable(self, yes=True):
        """En- or disable db dependent actions."""
        for action in (self.editA, self.mrgA, self.payA, self.saleA):
            action.setEnabled(yes)
        self.dbA.setVisible(not yes)
        self.dbA.setEnabled(not yes)
        
    def db_state(self, msg=''):
        """Actions to be taken on db loss or gain."""
        self.dberr = msg and True or False
        self.w.no_dbconn.setVisible(self.dberr)
        self.dbstate.emit(not self.dberr)
        self.dbdep_enable(not self.dberr)
        if not hasattr(self, 'warnw'):
            from warn import Warning
        self.warnw = Warning(self, self.tr('GnuVet: Db Error'), msg)
        if not self.isVisible(): # ?
            self.warnw.closed.connect(self.show)

    def editc(self):
        print('editc not yet implemented.')
        self.gaia.saecli(self, act='e') # hierwei: to be implemented in saecli!
        pass

    def get_pats(self):
        """Collect this client's patients."""
        res = querydb(
            self,
            'select p_name,xbreed,breed_abbr,breed_name,sex,neutd,case when '
            "b1.bcol is not null then b1.bcol else '' end||case when b2.bcol "
            "is not null then '-'||b2.bcol else '' end||case when b3.bcol is "
            "not null then '-'||b3.bcol else '' end,dob,dobest,vicious,rip "
            'from patients,breeds,colours,basecolours b1,basecolours b2,'
            'basecolours b3 where p_cid=%s and breed=breed_id and colour='
            'col_id and b1.bcol_id=col1 and b2.bcol_id=col2 and b3.bcol_id='
            'col3 order by p_name', (self.cid,))
        if res is None:  return # db error
        if not res:
            self.w.plist.append_row(
                [self.tr('No patients on this clients record')])
            self.w.plist.set_colwidth(0, self.w.plist.width())
            return
        pheader = map(self.tr,
                      ['Name', 'Breed', 'Sex', 'Colour', 'dob', 'vic', 'rip'])
        self.w.plist.set_headers(pheader)
        for e in res:
            self.w.plist.append_row([
                e[0],
                e[1] and e[2] + '-X' or e[2], # breed
                e[4]+(e[5] is None and '-n?' or e[5] and '-n' or ''), #sex
                e[6], # colour
                e[8] and '({})'.format(e[7].strftime('%d.%m.%y')) or
                e[7].strftime('%d.%m.%y'), # dob
                e[9] and 'v' or '',
                e[10] and 'rip' or ''])
            self.w.plist.cell(len(self.w.plist.lrows)-1, 1).setToolTip(e[3])
        self.w.plist.set_colwidth(0, 100) # hierwei adjust width
        self.w.plist.set_colwidth(1, 100)
        self.w.plist.set_colwidth(2, 100)
        self.w.plist.set_colwidth(3, 200)
        self.w.plist.set_colwidth(4, 100)
        self.w.plist.set_colwidth(5, 50)
        self.w.plist.set_colwidth(6, 50)
        self.w.plist.setFocus()

    def get_vats(self):
        if not hasattr(self, 'vats'):
            self.vats = querydb(
                self,
                'select vat_id,vat_name,vat_rate from vats where not vat_obs')
            if self.vats is None:  return # db error
    
    def gv_quit(self, quitnow=False):
        """Signal children if quitting GnuVet or not."""
        self.shutdown = quitnow
        self.gvquit.emit(quitnow)
        if quitnow:
            self.close()
    
    def gv_quitconfirm(self):
        if self.gaia:
            self.gaia.gv_quitconfirm()
        else:
            exit()
        
    def help_self(self):
        self.helpsig.emit('client.html')

    def merge(self):
        print('client.merge not yet implemented')

    def payment(self): # hierwei:  moved here from patient
        if not hasattr(self, 'payment'):
            import payment
        self.paym = payment.Payment(self, self.db, self.options,
                                    self.cid, self.pid, self.staffid)
        self.paym.move(self.x()+50, self.y()+40)
        self.paym.show()
        invno = querydb(self,'select max(inv_no)from invoices')
        if invno is None:  return # db error
        ninvno = self.startdt.strftime('%Y%m%d0001')
        if ninvno > invno:
            invno = ninvno
        else:
            invno += 1
        self.invno_id = querydb(
            self,
            'insert into invoices(inv_no)values(%s)returning invoice_id',
            (invno,))
        if self.invno_id is None:  return # db error
        self.invno_id = self.invno_id[0][0]
        
    def rip(self):
        print('client.rip not yet implemented')

    def sale(self):
        print('client.sale not yet implemented')
        
if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    a = QApplication([])
    ding = Client(None, 2)
    ding.show()
    exit(a.exec_())

    ## self.confpayA = newaction(
    ##     self, '&Confirm payments',
    ##     'Confirm outstanding payments have been met', 'Ctrl+C')
