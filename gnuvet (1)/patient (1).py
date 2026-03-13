"""A test system to evolve a near-optimal way to deal with different input
visuals, to automate as far as desired, the entry of consultation, clinical
history and medication, payment etc.
rundt: running datetime.
startdt: datetime for entry -> this to save in db for one consid?
"""

# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

# TODO:
# remove count (1) from history
# see playground re payment and balance before continuing here
# add adding text w/o consult for e.g. calling information (vacc reminders etc)
#     s. products.add_hist()
# ck time not within constime?
#
# introduce serial id into tc for editing entries?
#
# move printing into confirm!  With all due buttontext-changes...
# vacc: note batchno somewhere!
# fix payment
# insert edit_line/edit_consult into menu
# adding|editing chronic condition
# add functions for sale, vacc (via products?)
# -> Payment
# -> estimate kostenvoranschlag, should work with products
# changed startdt to be propagated by products (done) and history visuals!
#     then -> unset consid and histd accordingly
# add number field for clinhist_id loaded from db for editing etc
# context menu: (copy?) delete details edit 
# add delete/edit htable things
# check all changed vars into self.dings to enable save_state on db error

    ## def ck_dt(self, cdt): # hierwei, implement warning
    ##     """Check if rundt-startdt > contime (default 1800).
    ##     If so, presume it's a new consultation, reset symptom and startdt."""
    ##     cdt = cdt.toPyDateTime()
    ##     if self.contime:
    ##     self.startdt = cdt
    ##     self.rundt = self.startdt
    ##     if self.options['usesymp']:
    ##         if ((abs(cdt - self.startdt).total_seconds()) >
    ##             self.contime and not self.symp):
    ##             self.w.sympDd.setCurrentIndex(0)

from datetime import date, datetime, timedelta
from decimal import Decimal
from psycopg2 import OperationalError
from PyQt4.QtCore import pyqtSignal, QString, Qt
from PyQt4.QtGui import (QMainWindow, QMenu, QScrollArea)
import gv_qrc
from keycheck import Keycheck
from util import ch_conn, gprice, money, newaction, querydb
from ticker import Ticker
from patient_ui import Ui_Patient

class Patient(QMainWindow):
    """The Patient window, from which to organise the various entries."""
    # signals
    gvquit = pyqtSignal(bool)
    dbstate     = pyqtSignal(object) # False: err
    helpsig  = pyqtSignal(str)
    savestate = pyqtSignal(dict)
    #getprod = pyqtSignal(str)

    # vars
    dberr = adding = shutdown = False
    carrysymp = None
    consid = None
    curs = None
    lastdt = None
    markupid = 1
    prevdata = False
    previnv  = False
    prod_queue = None
    row = symp = None
    startdt = None # start time of booking
    ## typecons = 1 # id for cons type -> cons colour
    ## typehist = 1 # id for hist type -> hist colour
    # devel
    timer = None
    # end devel

    def __init__(self, parent=None, p_id=0):
        super(Patient, self).__init__(parent)
        self.parent = parent
        self.pid = p_id
        self.w = Ui_Patient()
        self.w.setupUi(self)
        #    instance vars
        self.conns = {} # pyqt bug: disconnect() w/o arg can segfault
        self.sigs = {} # dto
        self.row2data = [] # htable.row->(consid,okey,type,dt)  hierwei
        # only things used by now from row2data ar consid and dt...
        self.symptoms = {}
        self.w.htable.set_headers(
            [
                self.tr('date'),
                self.tr('text'),
                self.tr('#'), # tally
                self.tr('unit'),
                self.tr('symp'),
                self.tr('staff'),
                ])
        #    ACTIONS
        # devel
        debA = newaction(self, 'Debug', 'Current debug func', 'Ctrl+D')
        debA.triggered.connect(self.develf)
        # end devel
        closeA = newaction(self, 'Close &Window','Close this window','Ctrl+W')
        self.dbA = newaction(
            self, '&Reconnect to database',
            'Try to reconnect to database', 'Ctrl+R')
        self.aboutA = newaction(self, 'About &GnuVet', 'GnuVet version info')
        helpA = newaction(self, '&Help', 'context sensitive help', 'F1')
        quitA = newaction(self, '&Quit GnuVet', 'Exit GnuVet', 'Ctrl+Q')
        self.editA = newaction(
            self, '&Edit Patient', 'Edit patient description', 'Ctrl+E')
        self.histA = newaction(
            self, '&History', 
            'Add history entry to clinical history', 'Ctrl+H')
        self.saleA = newaction(
            self, 'S&ale', 'Add new sale (foods, goods)', 'Ctrl+A')
        self.mrgA = newaction(
            self, '&Merge Patient', 
            'Merge this account with additional account from same patient')
        self.toggleinsA = newaction(
            self, '&Insurance Info', 
            'Toggle full vs short insurance info', 'Ctrl+I')
        self.togglelocA = newaction(
            self,'&Location Info','Toggle full vs short location info','Ctrl+L')
        self.trtA = newaction(
            self, '&Treatment', 
            'Add treatment entry to clinical history', 'Ctrl+T')
        self.payA = newaction(self, 'Pa&yment', 'Take payment', 'Ctrl+Y')
        ## self.vaccA = newaction(self, short='Ctrl+V')) # ?
        #    MENUES
        taskM = QMenu(self.w.menubar)
        taskM.setTitle(self.tr('&Task'))
        self.w.menubar.addAction(taskM.menuAction())
        newM = QMenu(self.w.menubar)
        newM.setTitle(self.tr('&New'))
        self.w.menubar.addAction(newM.menuAction())
        debugM = QMenu(self.w.menubar)
        debugM.setTitle('&Debug')
        self.w.menubar.addAction(debugM.menuAction())
        debugM.addAction(debA)
        helpM = QMenu(self.w.menubar)
        helpM.setTitle(self.tr('&Help'))
        self.w.menubar.addAction(helpM.menuAction())
        #    SUBMENUES
        taskM.addAction(self.dbA)
        taskM.addSeparator()
        taskM.addAction(self.editA)
        taskM.addAction(self.mrgA)
        taskM.addSeparator()
        taskM.addAction(self.toggleinsA)
        taskM.addAction(self.togglelocA)
        taskM.addSeparator()
        taskM.addAction(closeA)
        taskM.addAction(quitA)
        taskM.setSeparatorsCollapsible(1)
        newM.addAction(self.trtA)
        repM = QMenu(newM)
        repM.setTitle(self.tr('&Repeat'))
        repM.setStatusTip(
            self.tr('Add repeat medication or diet to clinical history'))
        medA = newaction(self, 'Rep &medication',
                         'Add repeat medication to clinical history', 'Ctrl+M')
        dietA = newaction(
            self, 'Rep &diet', 'Add repeat diet to clinical history', 'Ctrl+D')
        repM.addAction(medA)
        repM.addAction(dietA)
        newM.addAction(repM.menuAction())
        newM.addAction(self.histA)
        newM.addAction(self.saleA)
        newM.addAction(self.payA)
        helpM.addAction(helpA)
        helpM.addSeparator()
        helpM.addAction(self.aboutA)
        #    right-click menu for htable
        self.rcM = QMenu(self.w.htable)
        rceditA = newaction(self, '&edit entry')
        rcdelA = newaction(self, '&delete entry')
        rcsrchA = newaction(self, '&search history')
        self.rcM.addAction(rceditA)
        self.rcM.addAction(rcdelA)
        self.rcM.addAction(rcsrchA)
        #    ACTION CONNECTIONS
        closeA.triggered.connect(self.close)
        helpA.triggered.connect(self.help_self)
        quitA.triggered.connect(self.gv_quitconfirm)
        rceditA.triggered.connect(self.rcedit)
        rcdelA.triggered.connect(self.rcdel)
        self.w.vacPb.clicked.connect(self.add_vac)
        ## self.saveA.triggered.connect(self.w.savePb.click)
        #    PARENT CONNECTIONS
        if parent: # devel if
            if parent.gaia == 'gaia':
                self.gaia = parent
            else:
                self.gaia = parent.gaia
            self.dbA.triggered.connect(parent.db_connect) # gaia?
            self.aboutA.triggered.connect(parent.about) # gaia?
            parent.gvquit.connect(self.gv_quit) # gaia?
            parent.dbstate.connect(self.db_state) # gaia?
            self.savestate.connect(parent.state_write) # gaia?
            self.helpsig.connect(parent.gv_help) # gaia?
            self.db = parent.db # gaia?
            self.staffid = parent.staffid # gaia?
        else:
            import dbmod
            dbh = dbmod.Db_handler('enno')
            self.db = dbh.db_connect()
            if type(self.db) is str:
                self.db_state(self.db)
                return # ?
            self.staffid = 1
            self.gaia = 'gaia'
            ##self.db.set_client_encoding('UTF-8')
        #    WIDGET CONNECTIONS # ?
        #    BUTTON CONNECTIONS
        self.w.closePb.clicked.connect(self.close)
        self.w.weightPb.clicked.connect(self.weight)
        self.w.addconsPb.clicked.connect(self.ck_autocon)
        #    INIT
        try:
            self.curs = self.db.cursor()
        except (OperationalError, AttributeError) as e: # no db connection
            self.db_state(e)
            return
        self.logname = 'no login'
        if self.curs:
            self.dbdep_enable(True)
            self.logname = querydb(
                self,
                'select stf_logname from staff where stf_id=%s',(self.staffid,))
            if self.logname is None:  return # db error
            self.logname = self.logname[0][0]
            self.logshort = querydb(
                self,
                'select stf_short from staff where stf_id=%s', (self.staffid,))
            if self.logshort is None:  return # db error
            self.logshort = self.logshort[0][0]
        self.w.lLb.setText(self.logname)
        self.get_chr()
        if self.dberr:  return
        self.timer = Ticker(self)
        self.rundt = datetime.now() - timedelta(0, .8)
        ch_conn(self, 'tick', self.timer.tick, self.update_time)
        self.timer.run()
        # devel:
        if parent:
            # end devel
            self.options = parent.options
        else:
            from options import defaults as options
            self.options = options
        self.contime = 0
        if 'contime' in self.options:
            self.contime = self.options['contime']
        self.get_ptypes()
        if self.dberr:  return
        self.keycheck = Keycheck(self)
        self.installEventFilter(self.keycheck)
        self.w.htable.installEventFilter(self.keycheck)
        ch_conn(self, 'enter', self.keycheck.enter, self.enter_hit)
        ch_conn(self, 'esc', self.keycheck.esc, self.w.closePb.click)
        self.w.addchPb.clicked.connect(self.add_hist)
        self.dbA.setVisible(0)
        self.dbA.setEnabled(0)
        self.symptoms[0] = dict(symp='',shrt='')
        self.units = {}
        res = querydb(self,'select u_id,u_name,u_pl,u_short,u_abbr from units')
        if res is None:  return # db error
        for e in res:
            if e[2]:
                self.units[e[0]] = dict(n=e[1], pl=e[2], sh=e[3], ab=e[4])
            else:
                self.units[e[0]] = dict(n=e[1], pl=e[1], sh=e[3], ab=e[4])
        if 'usesymp' in self.options and self.options['usesymp']:
            res = querydb(
                self,
                'select sy_id,symptom,sy_short from symptoms order by symptom')
            if res is None:  return # db error
            for e in res:
                self.symptoms[e[0]] = dict(symp=e[1], shrt=e[2])
        self.markups = {}
        if self.options['usemark']:
            res = querydb(
                self, 'select m_id,m_name,m_rate from markups where not m_obs')
            if res is None:  return # db error
            for e in res:
                self.markups[e[0]] = dict(n=e[1], r=e[2])
        if self.pid:
            self.pat_data()
            if self.dberr:  return
            self.show()
            if self.prevdata: # not work
                print
                self.w.htable.select_row(row=-1)
        else: # devel else
            print('No pid.')
        
    def add_hist(self): # hierwei: implement
        """Add additional clinical history independent of product cycle."""
        self.consid = self.row2data[self.row][0]
        self.add_prod(action='h')
        print('patient.add_hist: not yet implemented.')

    def add_prep(self, prod=None): # prod is str
        """Prepare addition of product.  Called by enter_hit."""
        if not self.prevdata: # no entry in hist tables
            self.ck_autocon(prod)
        elif self.contime: # check time diff from last entry to now
            consid = self.row2data[self.row][0]
            dbdt = querydb(
                self,
                'select max(dt)from prod{} where consid=%s'.format(
                    self.pid), (consid,))
            if dbdt is None:  return # db error
            dbdt = dbdt[0][0]
            if (abs((self.rundt-dbdt).total_seconds()) > self.contime):
                self.prod_queue = prod
                self.cons_newq()
            else:
                self.add_prod(prod)
        else:
            self.add_prod(prod)

    def add_prod(self, prod=None, action='p'):
        self.get_vats()
        if not hasattr(self, 'productw'):
            import products
            if action == 'hst':
                self.productw = products.Products(self, action='h')
            elif action == 'con':
                self.productw = products.Products(self, action='c')
            else:
                self.productw = products.Products(self, prod=prod)
            self.productw.move(self.x()+50, self.y()+40)
        else:
            if action == 'hst': # untested
                self.productw.action == 'h'
                self.productw.sel_hist()
            else:
                self.productw.update_disp(
                    self.startdt, self.rundt, self.symp, prod)
        ch_conn(self, 'prodclosed', self.productw.closed, self.pb_enable)
        self.productw.show() # this seems nec, put upward in if?

    def add_vac(self):
        """Add new vaccination."""
        self.get_vats()
        if not hasattr(self, 'productw'):
            import products
            self.productw = products.Products(self, action='v')
        else:
            self.productw.update_disp(
                self.startdt, self.rundt, symp=1, action='v')
        self.productw.move(self.x()+50, self.y()+40)
        ch_conn(self, 'prodclosed', self.productw.closed, self.pb_enable)
        self.productw.show()
        
    def addch_row(self, l, pos=None):
        """Construct list to insert one row of data into htable."""
        # 0 dt 1 txt 2 count 3 unit 4 symp 5 staff 6 consid 7 okey 8 type
        trow = []
        self.tt = ''
        for k, e in enumerate(l):
            if not k:
                trow.append(self.format_dt(e))
                self.lastdt = e
            elif k == 4:
                trow.append(self.format_symp(e))
            elif k < 6:
                if not e:
                    e = ''
                if k == 2:
                    if e != '':
                        e = self.ck_num(e)
                trow.append(str(e))
            elif k == 6:
                if pos is None:
                    pos = len(self.w.htable.lrows)
                toinsert = list(l[6:])
                toinsert.append(l[0])
                self.row2data.insert(pos, tuple(toinsert))
        self.w.htable.insert_row(trow, pos)
        if l[8] != 2:
            for c in self.w.htable.lrows[-1]:
                c.setStyleSheet(
                    self.w.htable.gcellss.format(
                        'white', self.ptypes[l[8]], 'lightgray'))
        if self.tt:
            self.w.htable.lrows[-1][4].setToolTip(self.tt)
    
    def book_cons(self, args):
        """Book consultation.  Called from products."""
        self.productw.close()
        if self.dberr:  return
        self.consid = self.ck_consid()
        if self.consid is None:  return # db error
        self.startdt = args[1] # rundt from productw
        self.rundt = args[0]
        self.symp = args[5]
        prodid = querydb(
            self,
            'insert into prods(prod_consid,prod_dt,prod_prid,prod_count,'
            'prod_symp,prod_staff)values(%s,%s,%s,%s,%s,%s)returning prod_id',
            (self.consid, self.rundt, args[2]['id'], # logically startdt but =
             args[4], args[5], self.staffid))
        if prodid is None:  return # db error
        prodid = prodid[0][0]
        chid = querydb(
            self,
            'insert into clinhists(ch_consid,ch_dt,ch_text,ch_symp,ch_staff)'
            'values(%s,%s,%s,%s,%s)returning ch_id',
            (self.consid, args[0], str(args[6]), args[5], self.staffid))
        if chid is None:  return # db error
        res = querydb(
            self,
            'insert into accs(acc_cid,acc_prid,acc_npr,acc_vat)values'
            '(%s,%s,%s,%s)returning acc_id',
            (self.cid, prodid, args[3][0], args[3][1]))
        if res is None:  return # db error
        self.update_balance(args[3][0], args[4], self.vats[args[3][1]][2])
        self.db.commit() # cons and hist booked
        if self.startdt < self.lastdt:
            pos = self.findrow(self.startdt)
        else:
            pos = None
        if not self.prevdata:
            self.w.htable.clear()
        nrow = [args[1]] # startdt
        res = querydb( # "prodid"
            self,
            'select pr_name from products where pr_id=%s', (args[2]['id'],))
        if res is None:  return # db error
        res = res[0][0]
        nrow.extend([res, args[4], '', args[5], self.logshort, self.consid,
                    prodid, 1])
        #startdt pr_name count symp stfshrt consid prod.id typecons
        self.addch_row(nrow, pos) # cons in htable
        if pos is not None:  pos += 1
        #rundt hist count=None symp stfshrt consid ch.id typehist
        self.addch_row(
            [args[1], args[6], None, '', args[5], self.logshort, # was args[0]
             self.consid, chid, 2], pos) # hist in htable
        self.w.htable.rows2contents(-2)
        if pos is None:  pos = -1
        self.w.htable.select_row(row=pos)
        self.prevdata = True
        if self.prod_queue and self.prod_queue != 'con':# hierwei ck prod_queue
            prod = self.prod_queue                      # and 'con'
            self.prod_queue = None
            self.add_prod(prod)
        else:
            self.reset()

    def book_event(self, args): # 150324
        # rundt startdt prinfo{id type uid instr mark}
        #     (nprice vat) amount symp insttxt
        self.productw.close()
        if self.dberr:  return # hierwei ck this set by productw? impl gaia
        self.consid = self.ck_consid()
        if self.consid is None:  return # db error
        self.startdt = args[1] # rundt from productw
        self.rundt   = args[0] # gets updated by ticker
        self.symp    = args[5]
        prodid = querydb(
            self,
            'insert into prods(prod_consid,prod_dt,prod_prid,prod_count,'
            'prod_symp,prod_staff)values(%s,%s,%s,%s,%s,%s)returning prod_id',
            (self.consid, self.rundt, args[2]['id'], args[4], args[5],
             self.staffid))
        if prodid is None:  return # db error
        prodid = prodid[0][0]
        res = None
        if args[2]['type'] == 1:
            res = self.book_event_cons(args[0], str(args[6]), args[5])
            if res is None:  return # db error
            chid = res[0][0]
        res = querydb(
            self,
            'insert into accs(acc_cid,acc_prid_acc_npr,acc_vat)values'
            '(%s,%s,%s,%s)returning acc_id',
            (self.cid, prodid, args[3][0], args[3][1]))
        if res is None:  return # db error
        if args[2]['type'] in (3, 5, 6):
            if 'usestock' in self.options and self.options['usestock']:
                res = querydb(
                    self,
                    'select pr_stock from products where pr_id=%s', (prodid,))
                if res is None:  return # db error
                if res[0][0]:
                    stock = querydb(
                        self,
                        'update products set pr_stock=pr_stock-%s where pr_id'
                        '=%s returning pr_stock', (args[4], prodid))
                    if stock is None:  return # db error
                    self.ck_stock(prodid, stock[0][0])
            # hierwei ckin book_prod if poss
        self.db.commit() # booked, now start display in htable
        self.update_balance(args[3][0], args[4], self.vats[args[3][1]][2])
        # hierwei: how this next when consid fixed?
        if self.startdt < self.lastdt:
            pos = self.findrow(self.startdt)
        else:
            pos = None
        if not self.prevdata: # prevdata unnec when building htab anew?
            self.w.htable.clear()
        ## nrow = [args[1]] # startdt  # hierwei cons and prod w startdt?
        res = querydb(
            self,
            'select pr_name,pr_type from products where pr_id=%s',
            (args[2]['id'],))
        if res is None:  return # db error
        # pr_name amount unit symp log consid okey ptype
        nrow = [args[1], res[0][0], args[4], '', args[5], self.logshort,
                self.consid, prodid, res[0][1]] ### fits cons, re unit HIERWEI
        #startdt pr_name count unit symp stfshrt consid prod.id type
        self.addch_row(nrow, pos) # cons in table
        if pos is not None:  pos += 1
        #rundt hist count=None symp stfshort consid ch.id histtype
        if (type == cons): hierwei
        self.addch_row([args[1], args[6], None, '', args[5], self.logshort,
                        self.consid, chid, 2], pos)
        # hist in htable ### fits cons+hist # hierwei ck this
        self.w.htable.rows2contents(-2)
        self.w.htable.select_row(pos and pos or -1)
        self.prevdata = True
        if self.prod_queue and self.prod_queue != 'cons':
            prod = self.prod_queue
            self.prod_queue = None
            self.add_prod(prod)
        else:
            self.reset() # hierwei

    def book_event_cons(self, dt, text, symp):
        return querydb(
            self,
            'insert into clinhists(ch_consid,ch_dt,ch_text,ch_symp,'
            'ch_staff)values(%s,%s,%s,%s,%s)returning ch_id',
            (self.consid, dt, text, symp, self.staffid))

    def book_hist(self, args):
        pass
    
    def book_prod(self, args):
        """Book product.  Called from products."""
        self.productw.close()
        if self.dberr:  return
        self.consid = self.ck_consid()
        if self.consid is None:  return # db error
        self.startdt = args[1]
        self.rundt = args[0]
        self.symp = args[5]
        prodid = querydb(
            self,
            'insert into prods(prod_consid,prod_dt,prod_prid,prod_count,'
            'prod_symp,prod_staff)values(%s,%s,%s,%s,%s,%s)returning prod_id',
            (self.consid, self.rundt, args[2]['id'],
             args[4], args[5], self.staffid))
        if prodid is None:  return # db error
        prodid = prodid[0][0]
        res = querydb(
            self,
            'insert into accs(acc_cid,acc_prid,acc_npr,acc_vat)values'
            '(%s,%s,%s,%s)returning acc_id',
            (self.cid, prodid, args[3][0], args[3][1]))
        if res is None:  return # db error
        if 'usestock' in self.options and self.options['usestock']:
            res = querydb(
                self,
                'select pr_stock from products where pr_id=%s', (prodid,))
            if res is None:  return # db error
            if res[0][0] is not None:
                stock = querydb(
                    self,
                    'update products set pr_stock=pr_stock-%s where pr_id=%s '
                    'returning pr_stock', (args[4], prodid))
                if stock is None:  return # db error
                self.ck_stock(prodid, stock[0][0])
        self.update_balance(args[3][0], args[4], self.vats[args[3][1]][2])
        res = querydb(
            self,
            'select pr_name,pr_u from products where pr_id=%s',
            (args[2]['id'],))
        if res is None:  return # db error
        res = res[0]
        self.addch_row(
            [self.rundt, res[0], args[4], self.units[res[1]]['ab'], args[5],
             self.logshort, self.consid, prodid, args[2]['type']], self.row+1)
        if args[6]:
            if self.dberr:  return
            okey = querydb(
                self,
                'insert into insts values(%s,%s)returning in_prodid', 
                (prodid, args[6]))
            if okey is None:  return # db error
            okey = okey[0][0]
            self.w.htable.insert_row(['',args[6],'','','~',''], self.row+2)
            self.row2data.insert(self.row+2, (self.consid,okey,0,self.rundt))
            self.productw.reset_instr()
        self.db.commit()
        self.w.htable.select_row(row=self.row+2)
        res = querydb(self, 'select a2p_prod from app2prod where a2p_prid=%s',
                      (args[2]['id'],))
        if res is None:  return # db error
        if res:
            res = querydb(self, 'select app_keyword from applications '
                          'where app_id=%s', (res[0][0],))
            if res is None:  return # db error
            self.add_prod(res[0][0])
        self.reset()

    def book_vac(self, args):
        """Book vaccination."""
        self.productw.close()
        self.get_vats()
        if self.dberr:  return
        if not self.consid:
            self.consid = self.ck_consid()
            if self.consid is None:  return # db error
        if not self.startdt:
            self.startdt = args[0]
            self.rundt = args[0]
        else:
            self.rundt = args[0]
        if not self.symp:
            self.symp = args[5] # should be 1, except for therapeutic vacc
        prodid = querydb(
            self,
            'insert into prods(prod_consid,prod_dt,prod_prid,prod_count,'
            'prod_symp,prod_staff)values(%s,%s,%s,%s,%s,%s)returning prod_id',
            (self.consid, self.startdt, args[2]['id'],
             args[4], args[5], self.staffid))
        if prodid is None:  return # db error
        prodid = prodid[0][0]
        chid = querydb(
            self,
            'insert into clinhists(ch_consid,ch_dt,ch_text,ch_symp,ch_staff)'
            'values(%s,%s,%s,%s,%s)returning ch_id',
            (self.consid, self.rundt, str(args[6]), args[5], self.staffid))
        if chid is None:  return # db error
        res = querydb(
            self,
            'insert into accs(acc_cid,acc_prid,acc_npr,acc_vat)values'
            '(%s,%s,%s,%s)returning acc_id',
            (self.cid, prodid, args[3][0], args[3][1]))
        if res is None:  return # db error
        vtype = querydb(
            self,
            'select vac_type,val_days from vaccinations,validities where '
            'vac_validity=val_id and vac_sid=%s', (args[2]['id'],))
        if vtype is None:  return # db error
        vtype, vval = vtype[0]
        vval = self.startdt + timedelta(vval)
        res = querydb(
            self,
            'select vd_type from vdues where vd_pid=%s', (self.pid,))
        if res is None:  return # db error
        if not res:
            succ = querydb(
                self,
                'insert into vdues values(%s,%s,%s)returning vd_vdue',
                (self.pid,vtype,vval))
        else:
            succ = querydb(
                self,
                'update vdues set vd_vdue=%s where vd_pid=%s and vd_type=%s '
                'returning vd_vdue', (vval, self.pid, vtype))
        if succ is None:  return # db error
        if 'usestock' in self.options and self.options['usestock']:
            prid = querydb(
                self,
                'select vac_prid from vaccinations where vac_sid=%s',
                (prodid,))
            if prid is None:  return # db error
            prid = prid[0][0]
            res = querydb(
                self,
                'select pr_stock from products where pr_id=%s', (prid,))
            if res is None:  return # db error
            if res[0][0] is not None:
                stock = querydb(
                    self,
                    'update products set pr_stock=pr_stock-%s where pr_id=%s '
                    'returning pr_stock', (args[4], prid))
                if stock is None:  return # db error
                self.ck_stock(prid, stock[0][0])
        self.update_balance(args[3][0], args[4], self.vats[args[3][1]][2])
        self.db.commit() # vacc booked
        if self.startdt < self.lastdt:
            pos = self.findrow(self.startdt)
        else:
            pos = None
        if not self.prevdata:
            self.w.htable.clear()
        res = querydb( # "prodid"
            self,
            'select pr_name,pr_u from products where pr_id=%s',
            (args[2]['id'],))
        if res is None:  return # db error
        res = res[0]
        nrow = [self.startdt, res[0], args[4], self.units[res[1]]['ab'],
                args[5], self.logshort, self.consid, prodid, 8]
        self.addch_row(nrow, pos)
        if pos is not None:  pos += 1
        self.addch_row(
            [self.rundt, args[6], None, '', args[5], self.logshort,
             self.consid, chid, 2], pos) # hist in htable
        self.w.htable.rows2contents(-2)
        if pos is None:  pos = -1
        self.w.htable.select_row(row=pos)
        self.prevdata = True
        self.get_vac()
        self.reset() # ?

    def ck_autocon(self, prod): # hierwei check False, '' and such
        """Check if to ask for new cons or not.
        Called by addconsPb, add_prep if not prevdata."""
        if prod is None or prod is False:
            self.add_prod(action='con')
            return
        if self.contime and (
            (self.startdt is None or
             abs(self.rundt-self.startdt) > timedelta(0, self.contime) or
             not self.consid)):
            self.prod_queue = prod
            self.add_prod(action='con')
        else:
            self.add_prod(prod)
    
    def ck_balance(self):
        """Calculate current balance of client and patient."""
        cbal = pbal = Decimal('0.00')
        addend = querydb(
            self,
            'select acc_npr,vat_rate,e_pid from accs,vats,prods,events where '
            'acc_cid=%s and acc_vat=vat_id and acc_prid=prod_id and '
            'e_id=prod_consid', (self.cid,))
        if addend is None:  return # db error
        for e in addend:
            if e[2] == self.pid:
                pbal += gprice(e[0], e[1])
            else:
                cbal += gprice(e[0], e[1])
        cbal += pbal
        self.w.pbalanceLb.setText(str(pbal))
        self.w.cbalanceLb.setText(str(cbal))

    def ck_ch(self): # Think this is overkill
        """Check if previous data present."""
        prev = querydb(
            self,
            'select max(ch_id)from clinhists,events where ch_consid=e_id '
            'and e_pid=%s', (self.pid,))
        if prev is None:  return # db error
        if prev[0] and prev[0][0]:  return True
        ##self.curs.execute("set client_encoding='UTF-8'")
        prev = querydb(
            self,
            'select max(prod_id)from prods,events where prod_consid=e_id '
            'and e_pid=%s', (self.pid,))
        if prev is None:  return # db error
        if prev[0] and prev[0][0]:  return True
        return False
    
    def ck_consid(self): # HIERWEI this should only be devel
        """Check: create new consid or use existing one w/o corresp entries."""
        if self.consid:  return
        consid = querydb(
            self,
            'select max(e_id)from events where e_pid=%s',(self.pid,))
        if consid is None:  return # db error
        if not consid[0][0]: # [(None,)] ???
            consid = querydb(
                self, 
                'insert into events(e_pid)values(%s)returning e_id',
                (self.pid,))
            if consid is None:  return # db error
            print('no consid, created and returning {}'.format(consid[0][0]))
            return consid[0][0]
        consid = consid[0][0]
        res = querydb(self,
                      'select count(prod_id)from prods where prod_consid=%s',
                      (consid,))
        if res is None:  return # db error
        res.extend(querydb(
            self,
            'select count(ch_id)from clinhists where ch_consid=%s',
            (consid,)))
        if res is None:  return # db error
        for e in res:
            if any(e): # consid is in use
                consid = querydb(
                    self,
                    'insert into events(e_pid)values(%s)returning e_id',
                    (self.pid,))
                if consid is None:  return # db error
                return consid[0][0]
        print('using unused consid: {}'.format(consid))
        return consid
            
    def ck_num(self, num=0):
        """Check format of num, if integer return int(num)."""
        if num//1 == num:
            return int(num)
        else:
            return num.normalize()
        
    def ck_stock(self, prodid, batch=None): # hierwei, check this
        """Check if prod has to be re-ordered."""
        if 'usestock' in self.options and self.options['usestock']:
            limit = querydb(
                self,
                'select pr_limit from products where pr_id=%s', (prodid,))
            if limit is None:  return # db error
            if not limit or not limit[0][0]:  return
            limit = limit[0][0]
            st = querydb(
                self,
                'select st_num from stocks where st_prid=%s{}'.format(
                    batch and ' and st_batch={}'.format(batch) or ''))
            if st is None:  return # db error
            st = st[0][0]
            if not st:  return
            if st < limit:
                res = querydb(
                    self,
                    'insert into toorder(o_prid,o_date)values(%s,%s)returning '
                    'o_prid', (prodid, date.today()))
                if res is None:  return # db error

    def ck_time(self):
        pass
    
    def closeEvent(self, ev):
        if self.shutdown: # state_write only on gv_quit?
            if self.dberr:
                self.state_write()
        self.timer.stop()
        ch_conn(self, 'tick') # hierwei use gaia insto parent
        if self.parent: # hierwei: parent is gnuvet mainwin, xy_decr sense?
            self.parent.xy_decr()
        # threading.Timer needs to be told
        if hasattr(self, 'productw'):
            self.productw.close()

    def cons_add2sel(self): # hierwei completely untested
        """Add prod to selected (default last) consultation."""
        self.consid = self.row2data[self.row][0]
        res = querydb(
            self,
            'select min(dt),max(dt)from prods where prod_consid=%s',
            (self.consid,))
        if res is None:  return # db error
        self.startdt = res[0][0]
        self.rundt   = res[0][1]
        res = querydb(
            self,
            'select max(dt)from clinhists where ch_consid=%s', (self.consid,))
        if res is None:  return # db error
        if res[0][0] > self.rundt:
            self.rundt = res[0][0]
        self.w.htable.setEnabled(True)
        self.w.newconsFr.hide()
        self.w.addchPb.hide()
        ch_conn(self, 'newconscc')
        ch_conn(self, 'esc', self.keycheck.esc, self.w.closePb.click)
        prod = self.prod_queue
        self.prod_queue = None
        self.add_prod(prod)

    def cons_cc(self):
        """Cancel -- don't add product."""
        self.w.newconsFr.hide()
        self.w.htable.setEnabled(True)
        ch_conn(self, 'newconscc')
        ch_conn(self, 'esc', self.keycheck.esc, self.w.closePb.click)
        self.pb_enable()
        self.w.addLe.setFocus()
        self.w.addLe.selectAll()

    def cons_new(self):
        """Start new cons hist prod etc cycle."""
        self.symp = None # hierwei: was 0
        self.startdt = None
        self.consid = None
        self.w.htable.setEnabled(True)
        self.w.newconsFr.hide()
        self.w.addchPb.hide()
        ch_conn(self, 'esc', self.keycheck.esc, self.w.closePb.click)
        self.add_prod(action='con')
        
    def cons_newq(self):
        """Ask for confirmation to book new cons."""
        self.pb_enable(False)
        self.w.htable.setEnabled(False)
        self.w.newconsFr.show()
        self.w.newcons_newPb.setDefault(True)
        self.w.newconsFr.setFocus()
        self.w.newcons_newPb.clicked.connect(self.cons_new)
        self.w.newcons_selPb.clicked.connect(self.cons_add2sel)
        ch_conn(self, 'esc', self.keycheck.esc, self.w.newcons_ccPb.click)
        ch_conn(self, 'newconscc', self.w.newcons_ccPb.clicked, self.cons_cc)

    def dbdep_enable(self, yes=True):
        """En- or disable db dependent actions."""
        for action in (self.editA, self.histA, self.mrgA, self.payA,
                       self.trtA):
            action.setEnabled(yes)
        self.dbA.setVisible(not yes)
        self.dbA.setEnabled(not yes)

    def db_state(self, msg=''):
        """Actions to be taken on db loss or gain."""
        # This should be signalled to prime ancestor
        self.dberr = msg and True or False
        self.w.no_dbconn.setVisible(self.dberr)
        self.dbstate.emit(not self.dberr)
        self.dbdep_enable(not self.dberr)
        if not self.parent:
            if not hasattr(self, 'warnw'):
                from warn import Warning
            if not msg:
                msg = self.tr('Unspecified db error.')
            self.warnw = Warning(self, self.tr('GnuVet: Db Error'), msg)
            if not self.isVisible(): # devel: if not parent...
                self.warnw.closed.connect(self.show)

    def develf(self):
        """Devel function."""
        ##print(repr(self.w.htable.lrows[self.w.htable.selrow][0].styleSheet()))
        ##print('prev: {}'.format(repr(self.w.htable.prevss)))
        if self.pid == 20:
            self.pid = 3
        elif self.pid == 3:
            self.pid = 20
        self.pat_data()
        
    def edit_entry(self):
        print('patient.edit_entry() not yet implemented.')

    def enter_hit(self):
        if self.w.addLe.hasFocus():
            self.add_prep(str(self.w.addLe.text().toLatin1()).lower())
        elif self.w.htable.hasFocus():
            self.edit_entry()
        elif self.w.newconsFr.isVisible():
            self.w.newcons_newPb.click()
            self.w.addLe.setFocus()

    def findrow(self, dt): # hierwei
        """Find row to insert new data into htable."""
        for tdt in [e[3] for e in self.row2data]:
            if tdt > dt:
                consid = self.row2data[self.row2data.index(e)][0]
                break
        for cid in [e[0] for e in self.row2data]:
            if cid == consid:
                return self.row2data.index(e)

    def format_dt(self, e):
        """Return appropriate dt."""
        if self.lastdt:
            if self.lastdt.date() == e.date():
                return ''
        return e.strftime('%d.%m.%y %H:%M')

    def format_symp(self, e):
        """Return appropriate symp."""
        if e is None or e == self.carrysymp:
            return '~'
        elif not self.symptoms[e]['shrt']:
            return ''
        else:
            self.carrysymp = e
            self.tt = self.symptoms[e]['symp']
            return self.symptoms[e]['shrt']

    def get_chr(self):
        """Get data for chronics."""
        self.chronics = []
        res = querydb(self,'select chr_name from chronics')
        if res is None:  return # db error
        for e in res:
            self.chronics.append(e[0])

    def get_inst(self, consid, okey):
        """Construct list to insert medication instructions into htable."""
        inst = querydb(
            self, 'select in_text from insts where in_prodid=%s', (okey,))
        if inst is None:  return # db error
        if not inst:  return # no entry
        inst = inst[0][0]
        self.w.htable.append_row(['', inst, '', '', '~', ''])
        self.row2data.append((consid, okey, 0, self.lastdt))

    def get_phones(self):
        res = querydb(
            self,
            'select phone_opt,phone_num,phone_anno from phones '
            'where phone_cid=%s order by phone_opt',
            (self.cid,))
        if res is None:  return # db error
        if not res or not res[0]:
            self.w.phoneDd.addItem('n/a')
            self.w.phoneDd.setEnabled(False)
            return
        addend = ''
        if min([e[0] for e in res]) != max([e[0] for e in res]):
            addend = ' (best) '
        for i in xrange(len(res)): # hierwei, elide?
            self.w.phoneDd.addItem(res[i][1] + addend + res[i][2])
            if addend:
                addend = ''
        
    def get_ptypes(self):
        """Get ptypes -> type colour for htable."""
        res = querydb(
            self,
            'select pt_col from ptypes order by pt_id')
        if res is None:  return # db error
        self.ptypes = [('')]
        if 'usehistcolours' in self.options and self.options['usehistcolours']:
            for e in res:
                self.ptypes.append(e[0])
        else:
            for e in res:
                self.ptypes.append('black')

    def get_vac(self): # hierwei adapt 2 new tables (vdues)
        """Check vaccinations of patient into vacLb."""
        res = querydb(
            self,
            'select vt_type,vd_vdue from vdues,vtypes where '
            'vd_type=vt_id and vd_pid=%s', (self.pid,))
        if res is None:  return # db error
        if not res:
            self.w.vachLb.setText(self.tr('n/a'))
            return
        vaccs = {} # '
        for e in res:
            vaccs[e[0]] = e[1]
        tmp = '<table border="0" cellpadding="2">'
        today = date.today()
        for e in sorted(vaccs.keys()):
            tmp += '<tr><td colspan="2">{}<tr><td><td>{} '.format(
                e, vaccs[e].strftime('%d.%m.%Y'))
            if not self.rip:
                if vaccs[e] > (today + timedelta(40)):
                    tmp += self.tr('ok')
                elif vaccs[e] >= today:
                    tmp += '<font color="green">'+self.tr('due')+'</font>'
                else:
                    tmp += '<font color="red">'+self.tr('overdue')+'</font>'
        tmp += '</table>'
        self.w.vachLb.setText(tmp)
        self.w.vachLb.adjustSize()
        self.w.vscrArea = QScrollArea(self.w.centralwidget)
        self.w.vscrArea.setGeometry(10, 210, 230, 81)
        self.w.vscrArea.setFrameShape(6) # StyledPanel
        self.w.vscrArea.setFrameShadow(48) # Sunken
        self.w.vscrArea.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self.w.vscrArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.w.vscrArea.setWidget(self.w.vachLb)
        self.w.vscrArea.show()

    def get_vats(self):
        if not hasattr(self, 'vats'):
            self.vats = querydb(
                self,
                'select vat_id,vat_name,vat_rate from vats '
                'where not vat_obs')
            if self.vats is None:  return # db error
            
    def gv_help(self, page=''):
        self.helpsig.emit(page)
        
    def gv_quit(self, quitnow=False):
        """Signal children if quitting GnuVet or not."""
        self.shutdown = quitnow
        self.gvquit.emit(quitnow)
        if quitnow:
            self.close()
            
    def gv_quitconfirm(self):
        if self.parent:
            self.parent.gv_quitconfirm()
        else:
            try:
                self.timer.stop()
            except AttributeError:
                pass
            self.close()

    def help_self(self):
        self.helpsig.emit('patient.html')

    def pat_age(self, dob, rip, pid):
        if rip:
            dday = querydb(
                self,
                'select rip_date from rips where rip_id=%s', (pid,))
            if dday is None:  return # db error
            dday = dday[0][0].date()
            pdays = (dday - dob).days
        else:
            pdays = (date.today() - dob).days
        weeks = pdays/7
        years = weeks/52
        months = weeks%52/4
        weeks = weeks%52/4
        age = '{}{}{}'.format(
            years and ('{} a '.format(years)) or '',
            months and ('{} m'.format(months)) or '',
            (weeks and not years) and
            ('{}{} w'.format(months and ' ' or '', weeks)) or '')
        return age
    
    def pat_data(self):
        """Load patient data, a real monster function."""
        self.w.htable.clear() # 141020
        tmp = '' # new 131015
        res = querydb(
            self,
            # 0 p_name 1 xbreed 2 breed_name 3 sex 4 neutd 5 dob 6 dobest
            # 7 vicious 8 rip 9 bc1 10  bc2 11 bc3 12 l_id 13 l_name 14 anno
            # 15 cid 16 title 17 csname 18 cfname 19 baddebt 20 housen
            # 21 street 22 village 23 city 24 postcode 25 chronics 26 ident
            # 27 petpass 28 insurance 29 lastseen
            "select p_name,xbreed,breed_name,sex,neutd,dob,dobest,vicious,"
            "rip,b1.bcol,b2.bcol,b3.bcol,l_id,l_name,p_anno,p_cid,t_title,"
            "c_sname,c_fname,baddebt,housen,street,village,city,postcode,chr,"
            "identno,petpass,ins,p_last "
            "from patients,breeds,clients,colours,addresses,titles,"
            "basecolours b1,basecolours b2,basecolours b3,locations where "
            "p_id=%s and p_cid=c_id and breed=breed_id and colour="
            "col_id and b1.bcol_id=col1 and b2.bcol_id=col2 and b3.bcol_id="
            "col3 and c_title=t_id and c_address=addr_id and loc=l_id",
            (self.pid,))
        if res is None:  return # db error
        if not res:
            print('No results')
        dobest = dob = rip = False
        ### sname = 'Elsa' # neu 131028 hierwei db problem?
        self.pat = []
        for r in res:
            nwidth = self.w.nameLb.width()
            self.w.nameLb.setText(r[0])#QString.fromLatin1(r[0])) # hierwei
            self.w.nameLb.adjustSize()
            self.pat.append(r[0])
            nwidth = self.w.nameLb.width() - nwidth
            self.w.warnLb.move(
                self.w.warnLb.pos().x()+nwidth,self.w.warnLb.y())
            self.w.ripLb.move(self.w.ripLb.pos().x()+nwidth,self.w.ripLb.y())
            self.pat.append('{}{}'.format(r[2], r[1] and ' Cross' or ''))
            self.w.breedLb.setText(self.pat[1])
            self.pat.append(r[3])
            self.w.sexLb.setText('{}{}'.format(
                r[3] == 'm' and self.tr('male') or
                r[3] == 'f' and self.tr('female') or
                r[3] == 'h' and self.tr('hermaphrodite') or
                self.tr('sex n/a'),
                (r[4] is None) and self.tr(' (n\'d?)') or
                r[4] and self.tr(' (n\'d)') or ''))
            self.pat[2] += r[4] is None and "-n'd?" or r[4] and "-n'd" or ''
            dob = r[5]
            dobest = r[6]
            self.w.warnLb.setVisible(r[7])
            rip = r[8]
            self.w.ripLb.setVisible(r[8])
            self.w.colourLb.setText('{}{}'.format(
                r[9].startswith(self.tr('according')) and
                self.tr('colour') + ' ' or '',
                '-'.join([e for e in r[9:12] if e])))
            self.l_id = r[12]
            if r[14]:
                self.w.annoLb.setText(r[14])
            else:
                self.w.aLb.setEnabled(False)
            self.cid = r[15]
            if self.cid == 1:
                self.w.cnameLb.setText(self.tr('Owner unknown'))
                sname = 'nn' # hierwei: sname ref'd before assignment???
            else:
                self.w.cnameLb.setText(' '.join([e for e in r[16:19] if e]))
                sname = r[17]
                if r[19]: # baddebt
                    nwidth = self.w.cnameLb.width()
                    self.w.cnameLb.adjustSize()
                    nwidth = self.w.cnameLb.width() - nwidth
                    self.w.bdLb.move(self.w.bdLb.pos().x()+nwidth,
                                     self.w.bdLb.y())
                    self.w.bdLb.show()
                else:
                    self.w.bdLb.hide()
                self.w.addr1Lb.setText(', '.join([e for e in r[20:22] if e]))
                self.w.addr2Lb.setText(', '.join([e for e in r[22:24] if e]))
                self.w.postcodeLb.setText(r[24])
                self.ck_balance()
                if self.dberr:  return
            tmp = ''
            if r[25]: # chronics
                for i in xrange(len(self.chronics)):
                    if r[25] & 2**i:
                        tmp += self.chronics[i] + '<br>'
                self.w.chrLb.setEnabled(1)
                self.w.chrhLb.setText(tmp)
                self.w.chrhLb.adjustSize()
                self.cscrArea = QScrollArea(self.w.centralwidget)
                self.cscrArea.setGeometry(10, 331, 161, 81)
                self.cscrArea.setFrameShape(6) # QFrame.StyledPanel
                self.cscrArea.setFrameShadow(48) # QFrame.Sunken
                self.cscrArea.setAlignment(Qt.AlignLeft|Qt.AlignTop)
                self.cscrArea.setHorizontalScrollBarPolicy(
                    Qt.ScrollBarAlwaysOff)
                self.cscrArea.setWidget(self.w.chrhLb)
                self.cscrArea.show()
            else:
                self.w.chrLb.setEnabled(0)
            tmp = r[26] # id
            if not tmp:
                tmp = self.tr('n/a')
                self.w.identLb.setEnabled(0)
            else:
                tmp = tmp
                self.w.identLb.setEnabled(1)
            self.w.identLb.setText(tmp)
            if r[27]: # petpass
                self.w.petpassnoLb.setText(r[27])
            else:
                self.w.petpassnoLb.setText(self.tr('n/a'))
                self.w.petpassnoLb.setEnabled(0)
            ins = r[28]
            self.w.lastseenLb.setText(r[29].date().strftime('%d.%m.%y'))
            if r[13]: # loc
                self.w.locLb.setText(self.tr('Loc: ') + r[13])
                self.locshort = 'Loc: ' + r[13]
                self.w.locLb.setEnabled(1)
                res = querydb(
                    self,
                    'select housen,street,village,city,region,postcode,l_tel,'
                    'l_mobile from locations,addresses '
                    'where l_address=addr_id and l_id=%s', (self.l_id,))
                if res is None:  return # db error
                res = res[0]
                self.locfull = (
                    '\n'.join([l for l in [
                        str(self.tr('Location:')),
                        ', '.join([e for e in res[:2] if e]),
                        ', '.join([e for e in res[2:4] if e]),
                        ', '.join([e for e in res[4:6] if e]),
                        ': '.join([e for e in ['Tel', res[6]] if res[6]]),
                        ': '.join(
                            [e for e in ['Mobile', res[7]] if res[7]]),
                        ] if l]))
                self.w.locLb.setToolTip(self.locfull)
                self.togglelocA.triggered.connect(self.toggleloc)
                self.loc_osize = self.w.locLb.size()
            else:
                self.w.locLb.setText(self.tr('Location: n/a'))
                self.w.locLb.setEnabled(0)
                self.togglelocA.setEnabled(0)
                self.togglelocA.setVisible(0)
            self.get_phones()
            if ins:
                res = querydb(
                    self,
                    'select i_name,i_rep,housen,street,village,city,region,'
                    'postcode,i_tel,i_email,i_anno from insurances,'
                    'addresses where i_address=addr.id and i_id=%s', (ins,))
                if res is None:  return # db error
                self.w.insLb.setText(res[0][0])
                self.insshort = res[0][0]
                self.ins_osize = self.w.insLb.size()
                self.w.insLb.setEnabled(1)
                self.toggleinsA.triggered.connect(self.toggleins)
                self.insfull = '\n'.join([e for e in res if e])
                self.w.insLb.setToolTip(self.insfull)
                self.insfull = self.tr('Insurance') + ':\n' + self.insfull
            else:
                self.w.insLb.setText(self.tr('not insured'))
                self.w.insLb.setEnabled(0)
                self.toggleinsA.setEnabled(0)
                self.toggleinsA.setVisible(0)
        if dob:
            tmp = self.pat_age(dob, rip, self.pid)
            if self.dberr:  return
        if dobest:
            tmp = 'ca. ' + tmp
        if rip:
            tmp = ('<font size="-1"><i>' + self.tr('was') +
                   '</i></font> ' + tmp)
        self.w.ageLb.setText(tmp)
        self.pat.append(tmp)
        self.rip = rip
        # weight
        res = querydb(
            self,
            'select w_weight,w_dt,w_est from weights where w_pid=%s '
            'order by w_dt desc limit 1', (self.pid,))
        if res is None:  return # db error
        if not res:
            self.w.weightPb.setText(self.tr('&weight: n/a'))
            self.pat.append('weight n/a')
        else:
            res = res[0]
            cdate = res[1].date().strftime('%d.%m.%y')
            weight = res[0] # Decimal
            if weight > 2:
                weight = weight.quantize(Decimal('2.0'))
            self.w.weightPb.setText(self.tr('&weight: ') +
                                    (res[2] and 'ca. ' or '') +
                                    str(weight) +
                                    self.tr(' kg on ') + cdate)
            self.w.weightPb.adjustSize()
            self.pat.append(str(weight) + ' kg')
        self.pat.append(sname)
        self.get_vac()
        if not self.prevdata:
            self.prevdata = self.ck_ch()
            if self.prevdata is None:  return # db error
        if self.prevdata:
            self.pat_data_ch()
            if self.dberr:  return
        else:
            self.w.htable.append_row(
                ['', self.tr('No clinical history'),'','','',''])
            self.setcolw()
        self.w.addLe.setFocus()

    def pat_data_ch(self):
        """Get patient clinical history if present."""
        try:
            self.curs.execute(
                'create temporary table tc(consid int not null,okey int not '
                'null default 0,dt timestamp not null,ptype int not null '
                'default %s,txt varchar(1024)not null,count numeric(8,2)not '
                "null default 0,symp int,unit varchar(5)not null default '',"
                'staff varchar(5),prid int not null default 0)',
                (2,))
            self.curs.execute(
                'insert into tc(consid,okey,dt,ptype,txt,count,symp,staff,'
                'prid,unit)select prod_consid,prod_id,prod_dt,pr_type,pr_name,'
                'prod_count,prod_symp,stf_short,pr_id,u_abbr from events,'
                'prods,products,units,staff where e_pid=%s and prod_consid='
                'e_id and prod_prid=pr_id and pr_u=u_id and prod_staff=stf_id',
                (self.pid,))
            self.curs.execute(
                'insert into tc(consid,okey,dt,txt,symp,staff)select '
                'ch_consid,ch_id,ch_dt,ch_text,ch_symp,stf_short from events,'
                'clinhists,staff where e_pid=%s and ch_consid=e_id and '
                'ch_staff=stf_id', (self.pid,))
        except (OperationalError, AttributeError) as e:
            self.db_state(e)
            return
        res = querydb(
            self,
            'select dt,txt,count,unit,symp,staff,consid,okey,ptype,prid from '
            'tc order by dt,ptype')
        if res is None:  return # db error
        # 0 dt 1 txt 2 count 3 u 4 symp 5 staff 6 consid 7 okey 8 type 9 prid
        for e in res:
            self.addch_row(e)
            if e[9]: # we might have instructions, too
                self.get_inst(e[6], e[7])
                if self.dberr:  return
        self.setcolw()
        self.w.htable.align_data(0, 'r')
        self.w.htable.align_data(2, 'r')
        self.w.htable.rows2contents()
        ch_conn(self, 'selch', self.w.htable.rowchanged, self.trackitem)
        self.w.htable.rightclicked.connect(self.rclick)

    def pb_enable(self, enable=True):
        for e in (self.w.addchPb, self.w.addconsPb, self.w.addLe):
            e.setEnabled(enable)
        
    def rcdel(self):
        print('rcdel nyi')
        
    def rcedit(self):
        print('rcedit nyi')
        
    def rclick(self, pos):
        """Popup edit menu for right-clicked line."""
        self.rcM.popup(pos)

    def reset(self):
        self.w.addLe.setEnabled(True)
        self.w.addLe.clear()
        self.w.addLe.setFocus()
        self.w.addchPb.show() # sense?
        self.w.addchPb.setEnabled(True)

    def resizeEvent(self, ev): # obsolete?
        if ev.oldSize().width() == -1:
             return
        n_width  = self.width()
        n_height = self.height()
        o_width  = ev.oldSize().width()
        o_height = ev.oldSize().height()
        self.w.addchPb.move(self.w.addchPb.x()+int((n_width-o_width)/2),
                           self.w.addchPb.y()+(n_height-o_height))
        self.w.addLe.move(self.w.addLe.x()+int((n_width-o_width)/2),
                          self.w.addLe.y()+(n_height-o_height))
        self.w.htable.resize(self.w.htable.width()+(n_width-o_width),
                            self.w.htable.height()+(n_height-o_height))

    def setcolw(self):
        self.w.htable.set_colwidth(0, 110) # dt
        self.w.htable.set_colwidth(1, 325) # txt
        self.w.htable.set_colwidth(2, 60)  # count
        self.w.htable.set_colwidth(3, 40)  # unit
        self.w.htable.set_colwidth(4, 55)  # symp
        self.w.htable.set_colwidth(5, 50)  # staff

    def toggleins(self):
        """Toggle insurance view."""
        if self.ins_osize == self.w.insLb.size():
            self.w.insLb.setText(self.insfull)
            self.w.insLb.adjustSize()
            self.w.insLb.raise_()
        else:
            self.w.insLb.setText(self.insshort)
            self.w.insLb.resize(self.ins_osize)
            self.w.insLb.lower()

    def toggleloc(self):
        """Toggle location view."""
        if self.loc_osize == self.w.locLb.size():
            self.w.locLb.setText(self.locfull)
            self.w.locLb.adjustSize()
            self.w.locLb.raise_()
        else:
            self.w.locLb.setText(self.locshort)
            self.w.locLb.resize(self.loc_osize)
            self.w.locLb.lower()

    def trackitem(self, row):
        """Track selected row."""
        self.row = row

    def update_balance(self, pr, count, vat):
        """Add price to balanceLbs."""
        addend = money(gprice(pr, vat), count)
        self.w.pbalanceLb.setText(
            str(Decimal(str(self.w.pbalanceLb.text())) + addend))
        self.w.cbalanceLb.setText(
            str(Decimal(str(self.w.cbalanceLb.text())) + addend))
    
    def update_time(self):
        """Update the clock upon tick from timer."""
        self.rundt += timedelta(0, 1)

    def weight(self):
        """Call weight chart window."""
        if not hasattr(self, 'weightw'):
            import weight
            self.weightw = weight.Weight(self, self.pid, self.rip)
            self.weightw.move(self.x()+50, self.y()+40)
            self.weightw.weightchanged.connect(self.weightchange)
            self.weightw.show()
        else:
            self.weightw.show()
            self.weightw.raise_()

    def weightchange(self, nweight):
        if nweight[1] > 2:
            weight = nweight[1].quantize(Decimal('0.0'))
        wdate = nweight[0].date().strftime('%d.%m.%y')
        self.w.weightPb.setText(self.tr('&weight: ') +
                                (nweight[2] and 'ca. ' or '') +
                                str(weight) +
                                self.tr(' kg on ') + wdate)
        self.w.weightPb.adjustSize()
    
if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    a = QApplication([])
    a.setStyle('plastique')
    c = Patient(None, 20) # Doenci 20
    exit(a.exec_())
