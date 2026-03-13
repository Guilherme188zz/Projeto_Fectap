"""Search Add Edit Client window."""
# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

# TODO:
# ck phone things
# should hide phone4, patient, somehow col_hide don't seem to work
# adapt to saepat.py
# check query_string (insb f qstring)
# action: a add  e edit  s search  c select

from datetime import date
from psycopg2 import OperationalError
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import (QMainWindow, QMenu, QPixmap, QStringListModel,)
import gv_qrc
from saecli_ui import Ui_Saecli
from gcompleter import Gcompleter
from keycheck import Keycheck
from util import ch_conn, newaction, querydb

class Saecli(QMainWindow):
    # signals:
    gvquit  = pyqtSignal(bool)
    cidsig   = pyqtSignal(int)
    dbstate   = pyqtSignal(bool)
    helpsig   = pyqtSignal(str)
    savestate = pyqtSignal(tuple) # currently unused

    # vars:
    db_err = changes = shutdown = False # self.adding?
    curs  = None
    gaia = None

    # queries for completer:
    cityq = ("select distinct city from addresses order by city")
    fnameq = ("select distinct c_fname from clients order by c_fname")
    housenq = ("select distinct housen from addresses order by housen")
    mnameq = ("select distinct c_mname from clients order by c_mname")
    pnameq = ("select distinct p_name from patients order by p_name")
    postcodeq = ("select distinct postcode from addresses order by postcode")
    regionq = ("select distinct region from addresses order by region")
    snameq = ("select distinct c_sname from clients order by c_sname")
    streetq = ("select distinct street from addresses order by street")
    villageq = ("select distinct village from addresses order by village")
    
    def __init__(self, parent=None, clid=0, act='s', clis=None):
        super(Saecli, self).__init__(parent)
        self.clid = clid
        self.act = act
        self.clis = clis
        self.w = Ui_Saecli()
        self.w.setupUi(self)
        #    instance vars
        self.cids = []
        self.conns = {} # pyqt bug: segfaults on disconnect() w/o arg
        self.sigs  = {}
        #    ACTIONS
        self.dbA = newaction(self, '&Reconnect to database',
                             'Try to reconnect to database', 'Ctrl+R')
        closeA = newaction(self, 'Close', 'Close this window', 'Ctrl+W')
        self.newcliA = newaction(
            self, '&Client',
            'create new Client record from entered data', 'Ctrl+C')
        # devel
        debugA = newaction(self, 'Debug', short='Ctrl+D')
        self.addAction(debugA)
        # end devel
        helpA = newaction(self, '&Help', 'context sensitive help', 'F1')
        aboutA = newaction(self, 'About &GnuVet', 'GnuVet version info')
        quitA = newaction(self, 'Quit GnuVet', 'Quit GnuVet', 'Ctrl+Q')
        #    MENUES
        taskM = QMenu(self.w.menubar)
        taskM.setTitle(self.tr('&Task'))
        self.newM = QMenu(self.w.menubar)
        self.newM.setTitle(self.tr("&New"))
        helpM = QMenu(self.w.menubar)
        helpM.setTitle(self.tr("&Help"))
        self.w.menubar.addAction(taskM.menuAction())
        self.w.menubar.addAction(self.newM.menuAction())
        self.w.menubar.addAction(helpM.menuAction())
        taskM.addAction(self.dbA)
        taskM.addSeparator()
        taskM.addSeparator()
        taskM.addAction(closeA)
        taskM.addAction(quitA)
        taskM.setSeparatorsCollapsible(1)
        self.newM.addAction(self.newcliA)
        helpM.addAction(helpA)
        helpM.addSeparator()
        helpM.addAction(aboutA)
        # DATEEDITS
        self.w.regDe.setMaximumDate(date(2099, 12, 31))
        self.w.regDe.setMinimumDate(date(1900, 1, 1))
        #    ACTION CONNECTIONS
        debugA.triggered.connect(self.develf)
        quitA.triggered.connect(self.gv_quitconfirm)
        helpA.triggered.connect(self.help_self)
        closeA.triggered.connect(self.close)
        self.newcliA.triggered.connect(self.cli_add)
        #    GAIA CONNECTIONS
        if parent: # devel if
            if parent.gaia == 'gaia':
                self.gaia = parent
            else:
                self.gaia = parent.gaia
            self.options = self.gaia.options
            self.staffid = self.gaia.staffid
            self.db = self.gaia.db
            self.dbA.triggered.connect(self.gaia.db_connect)
            aboutA.triggered.connect(self.gaia.about)
            self.gaia.gvquit.connect(self.gv_quit)
            self.gaia.dbstate.connect(self.db_state)
            self.helpsig.connect(self.gaia.gv_help)
            self.savestate.connect(self.gaia.state_write)
        else:
            self.gaia = self # test
            from options import defaults as options
            self.options = options
            import dbmod
            dbh = dbmod.Db_handler('enno')
            self.db = dbh.db_connect()
            # devel:
            self.db.set_client_encoding('UTF-8')
            self.staffid = 1
            self.dbA.setEnabled(False)
            aboutA.setEnabled(False)
        #    WIDGET CONNECTIONS
        ch_conn(self, 'dclick', self.w.clist.doubleclicked, self.w_cli)
        #    BUTTON CONNECTIONS
        self.w.errOk.clicked.connect(self.err_ok)
        self.w.sbynameRb.setChecked(1)
        self.w.sbydateRb.toggled.connect(self.list_clis)
        self.w.cancelPb.clicked.connect(self.close)
        #    INIT
        try:
            self.curs = self.db.cursor()
        except (OperationalError, AttributeError) as e: # no db connection
            self.db_state(e)
        if self.curs:
            self.dbdep_enable()
            logname = querydb(
                self, 'select stf_logname from staff where stf_id=%s',
                (self.staffid,))
            if logname is None:  return # db error
            logname = logname[0][0]
        self.w.lLb.setText(logname)
        self.w.bdPix.hide()
        self.w.ctitleDd.addItem("", 0)
        res = querydb(
            self, 'select t_id,t_title from titles order by t_id')
        if res is None:  return # db error
        for e in res:
            self.w.ctitleDd.addItem(e[1], e[0])
        #    GCOMPLETER
        self.lenames = ('city', 'fname', 'housen', 'mname', 'pname', 'postcode',
                        'region', 'sname', 'street', 'village')
        les = []
        for e in self.lenames:
            les.append(getattr(self.w, e + 'Le'))
        self.les = tuple(les)
        for le in self.les:
            setattr(le, 'name', self.lenames[self.les.index(le)])
            setattr(le, 'query', getattr(self, le.name + 'q'))
            setattr(le, 'list', [])
        self.gc = Gcompleter(self.w.saeFr)
        QApplication.instance().focusChanged.connect(self.focuschange)
        #    FINISH
        self.clistheader = []
        self.keycheck = Keycheck()
        self.installEventFilter(self.keycheck)
        if type(self.options['currency']) is int:
            if not 'QChar' in locals():
                from PyQt4.QtCore import QChar
            self.w.balSb.setPrefix(QChar(self.options['currency']) + ' ')
        else:
            self.w.balSb.setPrefix(self.options['currency'] + ' ')
        self.w.balSb.setMaximum(self.options['ballimit'])
        self.w.balSb.setMinimum(-self.options['ballimit'])
        if act == 's' or (act == 'c' and not clis): # full search
            self.cli_search()
        elif act == 'c': # choose: list clients from clis
            self.list_clis()
        elif act == 'a': # add a client
            pass
        elif act == 'e': # edit client
            pass

    def changed(self, change=0): # currently unused
        """Note if changes have been made for poss emerg save."""
        if change:
            self.changes = True

    def ck_email(self):
        if not self.w.emailLe.text():
            return True
        if not 'rematch' in locals:
            from re import match as rematch, compile as recompile
        if not 'emailre' in locals():
            emailre = recompile(
                r'([A-Z]|[a-z]|[0-9]){1,}([A-Z]|[a-z]|[0-9]|[\.])*([A-'
                'Z]|[a-z]|[0-9]){1,}@{1}([A-Z]|[a-z]|[0-9]){1,}([A-Z]|['
                'a-z]|[0-9]|[\.])*([A-Z]|[a-z]|[0-9]){1,}$')
        if not rematch(emailre, str(self.w.emailLe.text().toLatin1())):
            return False
        return True

    def ck_entries(self): # hierwei untested
        if not 'rematch' in locals:
            from re import match as rematch, compile as recompile
        # for non-english languages these have to be adapted:
        if not 'namere' in locals():
            namere = recompile(r"[A-Z][a-z']*([-\ ]?[A-Z][a-z']*)*$")
        if not 'mnamere' in locals():
            mnamere = recompile(r"([A-Z][a-z']*([-\ ]?[A-Z][a-z']*)*)|([A-"
                                  "Z][\.\ ]?)*$")
        if not 'housenre' in locals():
            housenre = recompile(r"(\d*[-]?(\d*|[\ ]?[A-Za-z]+))|([A-Z]["
                                  "a-z]*\b([-\ ]?\b[A-Z][a-z]*)*)$")
        errors = []
        txt = self.w.mnameLe.text().toLatin1()
        if txt:
            if not rematch(mnamere, txt):
                txt = fix_mname(txt)
                if rematch(mnamere, txt):
                    self.w.mnameLe.setText(txt)
                else:
                    errors.append('mname')
        for le in (self.w.snameLe, self.w.fnameLe, self.w.housenLe,
                   self.w.streetLe, self.w.villageLe, self.w.cityLe,
                   self.w.regionLe):
            txt = le.text().toLatin1()
            if txt:
                if not rematch(namere, txt):
                    txt = fix_name(txt)
                    if rematch(namere, txt):
                        le.setText(txt)
                    else:
                        errors.append(le.name)
        if not ck_postcode():
            errors.append('postcode')
        if not ck_email():
            errors.append('email')
        if errors: # hierwei this is still very devel
            print('AE Errors: {}'.format(errors))
            return 1

    def ck_postcode(self):
        if not self.w.postcodeLe.text():
            return
        if not 'cpostre' in locals():
            if self.options['ccode'] == 'uk':
                cpostre = recompile(
                    r"(GIR 0AA)|((([A-PR-UWYZ][0-9][0-9]?)|(([A-PR-"
                    "UWYZ][A-HK-Y][0-9][0-9]?)|(([A-PR-UWYZ][0-9][A"
                    "-HJKSTUW])|([A-PR-UWYZ][A-HK-Y][0-9][ABEHMNPRV"
                    "WXY])))) [0-9][ABD-HJLNP-UW-Z]{2})$")
            elif self.options['ccode'] == 'de':
                cpostre = recompile(r'\d{5}$')
            elif self.options['ccode'] == 'at':
                cpostre = recompile(r'\d{4}$')
        if rematch(cpostre, ' '.join(
            str(self.w.postcodeLe.text().toLatin1().toUpper()).split())):
            return True
        return False
    
    def cli_add(self):
        test = self.ck_entries()
        if test:  return # errors on entry check
        adr = []
        for le in (self.w.housenLe, self.w.streetLe, self.w.villageLe,
                   self.w.cityLe, self.w.regionLe, self.w.postcodeLe):
            adr.append(le.text().toLatin1())
        adr = tuple(adr)
        suc = querydb(self,
                      'select addr_id from addresses where housen=%s and '
                      'street=%s and village=%s and city=%s and region=%s and '
                      'postcode=%s', adr)
        if suc is None:  return # db error
        if suc[0][0]:
            adr = suc
        else:
            suc = querydb(
                self,
                'insert into addresses(housen,street,village,city,region,'
                'postcode)values(%s,%s,%s,%s,%s,%s)returning addr_id', adr)
            if suc is None:  return # db error
            if suc[0][0]:
                adr = suc
        cli = [self.w.ctitleDd.itemData(
            self.w.ctitleDd.currentIndex(), 32).toInt()[0]]
        for le in (self.w.snameLe,self.w.mnameLe,self.w.fnamele,self.w.emailLe):
            cli.append(le.text().toLatin1())
        cli.insert(4, adr)
        cli.append(date.today())
        cli.append(self.w.annoTe.toPlainText().toLatin1())
        cli = tuple(cli)
        suc = querydb( # leave out baddebt on new client?
            self,
            'insert into clients(c_title,c_sname,c_mname,c_fname,c_address,'
            'c_email,c_reg,c_anno)'
            'values(%s,%s,%s,%s,%s,%s,%s,%s)returning c_id', cli)
        if suc is None:  return # db error
        self.cid = suc[0][0]
        phones = []
        if self.w.phone1Le.text():
            phones.append('({},{},\'{}\',\'{}\')'.format(
                self.cid, self.phone1oSb.value(),
                self.w.phone1Le.text(), self.w.phone1annoLe.text()))
        if self.w.phone2Le.text():
            phones.append('({},{},\'{}\',\'{}\')'.format(
                self.cid, self.phone2oSb.value(),
                self.w.phone2Le.text(), self.w.phone2annoLe.text()))
        if self.w.phone3Le.text():
            phones.append('({},{},\'{}\',\'{}\')'.format(
                self.cid, self.phone3oSb.value(),
                self.w.phone3Le.text(), self.w.phone3annoLe.text()))
        if self.w.phone4Le.text():
            phones.append('({},{},\'{}\',\'{}\')'.format(
                self.cid, self.phone4oSb.value(),
                self.w.phone4Le.text(), self.w.phone4annoLe.text()))
        phones = ','.join(phones)
        if phones:
            suc = querydb(
                self,
                'insert into phones values{}returning phone_cid'.format(
                    phones))
            if suc is None:  return # db error
            self.db.commit()
    
    def cli_edit(self):
        self.stage = 4
        # hierwei
        pass

    def cli_search(self):
        """Setup search stage of the search-add-edit client window."""
        self.stage = 0
        # self.resize_l = True # ???
        self.w.sbynameRb.setChecked(1)
        self.resize(870, 626)
        self.w.errFr.hide()
        self.w.noMFr.hide()
        self.w.matchFr.hide()
        self.w.saeFr.setEnabled(1)
        if self.act == 's':
            self.setWindowTitle(self.tr('Search Client'))
        if self.act == 'c':
            self.setWindowTitle(self.tr('Select Client'))
        self.w.backPb.setDefault(0)
        self.w.backPb.setAutoDefault(0)
        self.w.backPb.hide()
        self.w.mainPb.setText('Search')
        self.w.mainPb.setEnabled(1)
        self.w.mainPb.setDefault(1)
        self.w.mainPb.setAutoDefault(1)
        self.w.secondPb.show()
        self.w.secondPb.setEnabled(1)
        self.w.secondPb.setText('R&eset') # change hotkey?
        # CONNECTIONS
        ch_conn(self, 'mainPb', self.w.mainPb.clicked, self.list_clis)
        ch_conn(self, 'enter', self.keycheck.enter, self.w.mainPb.click)
        ch_conn(self, 'backPb')#, self.w.backPb.clicked)
        ch_conn(self, '2ndPb', self.w.secondPb.clicked, self.reset_form)
        self.w.saeFr.setEnabled(1)
        self.w.saeFr.show()
        self.w.snameLe.setFocus()
        self.err_no = 0
    
    def closeEvent(self, ev): # ev.accept() seems to be unnec
        ## if self.shutdown:
        ##     if self.db_err:
        ##         self.state_write()
        if self.gaia and hasattr(self.gaia, 'xy_decr'):
            self.gaia.xy_decr()
        
    def dbdep_enable(self, yes=True):
        """En|Disable actions in case of db loss or gain."""
        #self.a_disabled = True
        self.newcliA.setEnabled(yes)
        self.w.secondPb.setEnabled(yes)
        self.w.mainPb.setDefault(yes)
        self.dbA.setVisible(not yes)
        self.dbA.setEnabled(not yes)
        
    def db_state(self, msg=''):
        """Actions to be taken on db loss and gain."""
        self.db_err = msg and True or False
        self.w.no_dbconn.setVisible(self.db_err)
        self.dbstate.emit(not self.db_err) # hierwei
        self.dbdep_enable(not self.db_err)
        # devel
        print('db error: {}'.format(msg))

    def err_ok(self): # hierwei mainPb.click?
        ch_conn(self, 'enter', self.keycheck.enter, self.w.mainPb.click)
        self.w.errFr.hide()

    def error_msg(self, err_msg=''): # currently unused?
        """Display error message in errFr when: db-error or client exists."""
        self.w.saeFr.setEnabled(0)
        self.w.errLb.setText(self.tr(err_msg))
        self.w.mainPb.setEnabled(0)
        self.w.mainPb.setDefault(0)
        self.w.mainPb.setAutoDefault(0)
        self.w.backPb.setEnabled(1)
        self.w.backPb.setAutoDefault(1)
        self.w.backPb.show()
        ch_conn(self, 'enter', self.keycheck.enter, self.w.errOk.click)
        self.w.errFr.show()

    def filltable(self, res):
        """Fill clist, res is one table row."""
        self.cids.append(res[19])
        # qfields: 0 c_title  1 c_sname  2 c_fname  3 c_mname  4 housen
        # 5 street  6 village  7 city  8 region  9 postcode
        # 10 c_telhome  11 c_telwork  12 c_mobile1  13 c_mobile2  14 c_email  
        # 15 baddebt  16 c_reg  17 c_last  18 c_anno  19 c_id  20 p_name
        #
        # tfields: 0 baddebt  1 c_name  2 address  3 c_telhome  4 c_telwork
        # 5 c_mobile1  6 c_mobile2  7 c_email  8 c_reg  9 c_last  10 c_anno
        # 11 p_name
        data = []
        tooltips = {}
        if res[15]: # data[0]
            data.append(QPixmap(":/images/redflag.png"))
        else:
            data.append('')
        comma = ''
        if res[1] and (res[2] or res[3]):
            comma = ','
        data.append(' '.join([res[0], res[1]+comma, res[2], res[3]])) # data[1]
        addr = ', '.join([e for e in res[4:10] if e!=''])
        if len(addr) > 20: # data[2]
            data.append(addr[:21]+'...')
            tooltips[2] = addr
        else:
            data.append(addr)
        for i in xrange(10, 15): # data[3:8]
            data.append(res[i])
            if not res[i]:
                self.hidecols[i-7] = True
        data.append(res[17].strftime('%d.%m.%y')) # data[8] last
        data.append(res[16].strftime('%d.%m.%y')) # data[9] regd
        data.append(len(res[18])>19 and res[18][:18]+'...' or res[18])#data[10]
        if len(res[18]) > 19:
            tooltips[10] = res[18]
        ## accX_state: money, to be updated from payX, if neg set bg red
        if len(res) > 20:
            data.append(res[20]) #data[11]
            self.pattoo = True
        else:
            data.append('')
            self.pattoo = False
        self.w.clist.append_row(data)
        for k in tooltips:
            self.w.clist.lrows[0][k].setToolTip(tooltips[k])
        
    def fix_housen(self, name): # currently unused
        """Try to avoid common typos in housen."""
        if not 'rematch' in locals:
            from re import match as rematch, compile as recompile
        if rematch(r'.*\d', name):
            name = ' '.join(name.split())
            if name.count('- ') or name.count(' -'):
                name = name.replace(' -', '-').replace('- ', '-')
            return name
        return fix_name(name)
        
    def fix_mname(self, name):
        """Try to avoid common typos in mname (initials usually)."""
        if name.count('.'):
            fixed = []
            for part in ' '.join(name.split()).split('.'):
                part = part.capitalize()
                fixed.append(part)
            return '.'.join(fixed)
        return fix_name(name)
        
    def fix_name(self, name):
        """Try to avoid common typos in Name."""
        fixed = []
        for part in name.split():
            inter = []
            for subpart in part.split('-'):
                subpart = subpart.capitalize()
                inter.append(subpart)
            part = '-'.join(inter)
            inter = []
            fixed.append(part)
        return ' '.join(fixed)

    def focuschange(self, old, new):
        if new and new in self.les:
            if not new.list:
                ## print('query: "{}"'.format(new.query))
                l = querydb(self, new.query)
                if l is None:  return # db error
                if l:
                    new.list = [e[0] for e in l]
            self.gc.setwidget(old=old, new=new, l=new.list)
                
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
        if self.act == 's':
            self.helpsig.emit('clisearch.html')
        elif self.act in ('e', 'a'):
            print('help on add and edit not yet implemented.')

    def list_clis(self):
        """Build list of clients matching search criteria."""
        if self.w.sbynameRb.isChecked():
            s_byname = True
        else:
            s_byname = False
        ch_conn(self, 'selch')
        self.w.clist.clear()
        if not self.clistheader:
            self.clistheader = [
                '', # for baddebt icon
                self.tr('Client'),
                self.tr('Address'),
                self.tr('Tel Home'),
                self.tr('Tel Work'),
                self.tr('Mobile 1'),
                self.tr('Mobile 2'),
                self.tr('email'),
                self.tr('Last Seen'),
                self.tr('Registered'),
                self.tr('Annotation'),
                ##self.tr('Balance'),
                self.tr('Patient') # can search for p_name here as well
                ]
        if not self.w.clist.headers:
            self.w.clist.set_headers(self.clistheader)
        result = querydb(self, self.query_string(s_byname))
        if result is None:  return # db error
        self.hidecols = {}
        for e in result:
            self.filltable(e)
        if result:
            self.match_list(s_byname)
        else:
            self.no_matches()

    def match_list(self, s_byname=True):
        """Set widgets to states for successful search."""
        self.stage = 'l' # was 2
        # ...
        count = len(self.w.clist.lrows)
        self.w.matchnLb.setText(self.tr('{} match{}'.format(
            count, count != 1 and self.tr('es') or '')))
        self.w.saeFr.hide()
        self.w.noMFr.hide()
        self.w.clist.cols2contents()
        if self.pattoo:
            self.w.clist.col_show(11)
        else:
            self.w.clist.col_hide(11)
        for entry in self.hidecols:
            if self.hidecols[entry]:
                self.w.clist.col_hide(entry)
            else:
                self.w.clist.col_show(entry)
        self.dbdep_enable(False)
        self.newM.setEnabled(0)
        self.w.backPb.setAutoDefault(0)
        self.w.backPb.setDefault(0)
        self.w.mainPb.setAutoDefault(1)
        self.w.mainPb.setDefault(1)
        self.w.mainPb.setText('select &Client')
        self.w.clist.installEventFilter(self.keycheck)
        ch_conn(self, 'enter', self.keycheck.enter, self.w.mainPb.click)
        self.w.backPb.setEnabled(1)
        self.w.backPb.setText('&back to Search')
        self.w.backPb.show()
        ch_conn(self, 'backPb', self.w.backPb.clicked, self.cli_search)
        ch_conn(self, 'mainPb', self.w.mainPb.clicked, self.w_cli)
        ch_conn(self, 'clist', self.w.clist.rowchanged, self.trackrow)
        self.w.clist.select_row(row=0)
        self.w.clist.setFocus()
        self.w.matchFr.show()

    def no_matches(self):
        self.stage = 'n' # was 1
        self.w.saeFr.hide()
        self.w.matchFr.hide()
        self.w.noMLb.setText(self.tr(
            'No matching client entries found!<br><br>'
            'Do you want to register a new account with your entries?'))
        self.w.mainPb.setText('&New Account')
        self.w.mainPb.setDefault(0)
        self.w.mainPb.setAutoDefault(0)
        self.w.secondPb.setEnabled(0)
        self.w.secondPb.hide()
        self.w.backPb.setText('&back to Search')
        self.w.backPb.setEnabled(1)
        self.w.backPb.setDefault(1)
        self.w.backPb.setAutoDefault(1)
        self.w.backPb.show()
        ch_conn(self, 'enter', self.keycheck.enter, self.w.backPb.click)
        ch_conn(self, 'backPb', self.w.backPb.clicked, self.cli_search)
        ch_conn(self, 'mainPb', self.w.mainPb.clicked, self.cli_add)
        self.w.noMFr.show()

    def query_string(self, s_byname):
        """Construct query string from user input."""
        # fields: 0 c_title  1 c_sname  2 c_fname  3 c_mname  4 housen
        # 5 street  6 village  7 city  8 region  9 postcode
        # 10 c_telhome  11 c_telwork  12 c_mobile1  13 c_mobile2  14 c_email  
        # 15 baddebt  16 c_reg  17 c_last  18 c_anno  19 c_id  [20 p_name]
        query_sel = (
            "t_title,c_sname,c_fname,c_mname,housen,street,village,"
                  "city,region,postcode,c_telhome,c_telwork,c_mobile1,"
                  "c_mobile2,c_email,baddebt,c_reg,c_last,c_anno,c_id")
        query_from = "clients,titles,addresses"
        query_order = ("c_sname,c_fname,c_mname,housen,street,village,"
                       "city,region,postcode,c_telhome,c_telwork,"
                       "c_mobile1,c_mobile2,c_email")
        query_walways = 'c_address=addr_id and c_title=t_id'
        if self.clis:
            query_where = 'where c_id in (' + ','.join(self.clis) + ') and '
            #print ('select ' + query_sel + ' from ' + query_from + ' where' +
            #       query_where + query_walways + ' order by ' + query_order)
            return ('select ' + query_sel + ' from ' + query_from + ' where' +
                    query_where + query_walways + ' order by ' + query_order)
        query_where = ''
        if not s_byname:
            query_order = 'c_last desc,' + query_order
        if not 'wildcard' in locals():
            from util import wildcard, prep_txt
        for le in ('sname', 'fname', 'mname', 'housen', 'street',
                   'village', 'city', 'region'):
            Le = getattr(self.w, le+'Le')
            if Le.text():
                q = le.endswith('name') and ('c_'+le) or le
                query_where += ((query_where and ' and ' or '') + q + " ilike '"
                                + wildcard(prep_txt(Le.text().toLatin1(),
                                                    True)) + "'")
        for le in ('phone1', 'phone2', 'phone3', 'phone4', 'email'):
            Le = getattr(self.w, le+'Le')
            if Le.text():
                q = 'c_' + le
                query_where += ((query_where and ' and ' or '') + q + " ilike '"
                                + wildcard(prep_txt(Le.text().toLatin1(),
                                                    True)) + "'")
        if self.w.annoTe.toPlainText():
            query_where += ((query_where and ' and ' or '') + "c_anno ilike '"
                            + wildcard(prep_txt(
                                self.w.annoTe.toPlainText().toLatin1(),
                                True)) + "'")
        if self.w.pnameLe.text():
            query_sel += ',p_name'
            query_from += ",patients"
            query_where += ((query_where and ' and ' or '')
                            + "p_cid=c_id and p_name ilike'" + wildcard(
                                prep_txt(self.w.pnameLe.text().toLatin1(),
                                         True)) + "'")
        if self.w.regspecDd.currentIndex():
            query_where += (query_where and ' and ' or '') + 'creg'
            d = self.w.regDe.date().toString(1)
            if self.w.regspecDd.currentText() == "=":
                query_where += (" between date '{}' - integer '30' and date "
                                "'{}' + integer '30'".format(d, d))
            else:
                query_where += self.w.regspecDd.currentText() + "'{}'".format(d)
        if self.w.lastspecDd.currentIndex():
            query_where += (query_where and ' and ' or '') + 'c_last'
            d = self.w.lastDe.date().toString(1)
            if self.w.lastspecDd.currentText() == '=':
                query_where += (" between date '{}' - integer '30' and date "
                                "'{}' + integer '30'".format(d, d))
            else:
                query_where += self.w.lastspecDd.currentText()+"'{}'".format(d)
        if self.w.balspecDd.currentIndex():
            query_where += ((query_where and ' and ' or '')
                            + self.w.balspecDd.currentText()
                            + self.w.balDb.cleanText())
        if self.w.baddebtCb.isChecked():
            query_where += (query_where and ' and ' or '') + 'baddebt=True'
        query_where += (query_where and ' and ' or '')
        return ('select ' + query_sel + ' from ' + query_from + ' where ' +
                query_where + query_walways + ' order by ' + query_order)
        
    def reset_form(self):
        self.w.ctitleDd.setCurrentIndex(0)
        self.w.snameLe.clear()
        self.w.fnameLe.clear()
        self.w.mnameLe.clear()
        self.w.baddebtCb.setChecked(0)
        #self.w.bdPix.hide()
        self.w.housenLe.clear()
        self.w.streetLe.clear()
        self.w.villageLe.clear()
        self.w.cityLe.clear()
        self.w.regionLe.clear()
        self.w.postcodeLe.clear()
        self.w.phone1Le.clear()
        self.w.phone2Le.clear()
        self.w.phone3Le.clear()
        self.w.phone4Le.clear()
        self.w.emailLe.clear()
        self.w.pnameLe.clear()
        self.w.annoTe.clear()
        self.w.regspecDd.setCurrentIndex(0)
        ##self.w.regDe.clear() #?
        self.w.lastspecDd.setCurrentIndex(0)
        ##self.w.lastDe.clear() #?
        self.w.balspecDd.setCurrentIndex(0)
        self.w.balSb.clear() #?
        self.w.snameLe.setFocus()

    def resizeEvent(self, ev):
        if ev.oldSize().width() == -1:
            return
        if not self.w.matchFr.isVisible():
            return
        n_width = self.width()
        n_height = self.height()
        o_width = ev.oldSize().width()
        o_height = ev.oldSize().height()
        self.w.buttonBox.move(self.w.buttonBox.x() + (n_width-o_width)/2,
                              self.w.buttonBox.y() + (n_height-o_height))
        self.w.matchFr.resize(self.w.matchFr.width() + (n_width-o_width),
                              self.w.matchFr.height() + (n_height-o_height))
        self.w.clist.resize(self.w.clist.width() + (n_width-o_width),
                            self.w.clist.height() + (n_height-o_height))
    
    def savedrestore(self, saved_things=[]):
        pass
        
    def state_write(self):
        """Signal unsaved changes to gaia for filing for later retrieval."""
        pass

    def save_cli(self):
        pass

    def trackrow(self, row=0):
        """Keep track of selected client."""
        self.cid = self.cids[row]
        
    def this_enable(self):
        """(Re-)Enable things after re-obtaining db connection."""
        pass
        
    def w_cli(self): # hierwei: func name?
        """Signal client ID to whom it may concern."""
        self.cidsig.connect(self.gaia.opencli)
        self.cidsig.emit(self.cid)
        self.cidsig.disconnect(self.gaia.opencli)
        self.close()

    def develf(self):
        if not hasattr(self, 'colhidden'):
            self.colhidden = True
        if self.colhidden:
            self.w.clist.col_show(11)
            self.colhidden = False
        else:
            self.w.clist.col_hide(11)
            self.colhidden = True
    
if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    import dbmod
    a = QApplication([])
    a.setStyle('plastique')
    ding = Saecli(None)
    ding.show()
    exit(a.exec_())

## db error: 'str' object has no attribute 'cursor'
## Traceback (most recent call last):
##   File "saecli.py", line 816, in <module>
##     ding = Saecli(None)
##   File "saecli.py", line 159, in __init__
##     self.w.lLb.setText(logname)
## UnboundLocalError: local variable 'logname' referenced before assignment
