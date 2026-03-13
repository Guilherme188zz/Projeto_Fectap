"""From scratch, a new product, amount, symptom and history recording dialog."""
# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

# TODO:
# reconsider markup things -- nec?
# implement gaia
# first startdt should be set from here by send_data set on confirm on consult
# ck startdt on using 'selected' cons

# implement quotation (estimate) # here or in patient?
# implement sel_hist for hist only
# should work: dberr?
# check all vars availability from parent?
# 130 x 160, 361 x 192: print preview size
# {:.1f}%  nn.n%

from datetime import datetime, timedelta
from decimal import Decimal
from psycopg2 import OperationalError
from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QMainWindow, QMenu, QWidget
from keycheck import Keycheck
from ticker import Ticker
from util import ch_conn, gprice, money, newaction, percent, querydb
from products_ui import Ui_Products

class Products(QMainWindow):
    dbstate = pyqtSignal(bool)
    dta = pyqtSignal(tuple)
    gvquit = pyqtSignal(bool)
    helpsig = pyqtSignal(str)
    closed = pyqtSignal()

    address = False
    dbg = True # devel var
    curs = None
    dberr = False
    gotinst = False
    histconf = True
    histd = False
    history = None
    insttxt = ''
    nidx = 0 # for code_work
    prod = ''
    rundt = None
    startdt = None
    symp = None
    timer = None
    
    def __init__(self, parent=None, prod=None, action='p'):
        # action: h history  o op  p products  q quotation  v vacc
        super(Products, self).__init__(parent)
        self.parent = parent
        self.action = action
        self.w = Ui_Products()
        self.w.setupUi(self)
        #    instance vars
        self.conns = {} # for ch_conn
        self.sigs  = {} # dto
        #    data
        logname = self.tr('no login')
        #    ACTIONS
        self.dbA = newaction(
            self, '&Reconnect to database',
            'Try to reconnect to database', 'Ctrl+R')
        aboutA = newaction(self, 'About &GnuVet', 'GnuVet version info')
        closeA = newaction(self, 'Close', 'Close this window', short='Ctrl+W')
        helpA = newaction(self, '&Help', 'context sensitive help', short='F1')
        quitA = newaction(self, '&Quit GnuVet', 'Quit GnuVet', short='Ctrl+Q')
        self.blkA = newaction(self, 'set text colour: blac&k', short='Ctrl+K')
        self.redA = newaction(self, 'set text colour: r&ed', short='Ctrl+E')
        self.bluA = newaction(self, 'set text colour: &blue', short='Ctrl+B')
        #    MENUES
        taskM = QMenu(self.w.menubar)
        taskM.setTitle(self.tr('&Task'))
        self.w.menubar.addAction(taskM.menuAction())
        helpM = QMenu(self.w.menubar)
        helpM.setTitle(self.tr('&Help'))
        self.w.menubar.addAction(helpM.menuAction())
        #    SUBMENUES
        taskM.addAction(self.dbA)
        taskM.addSeparator()
        taskM.addAction(self.blkA)
        taskM.addAction(self.redA)
        taskM.addAction(self.bluA)
        taskM.addSeparator()
        taskM.addAction(closeA)
        taskM.addAction(quitA)
        taskM.setSeparatorsCollapsible(1)
        helpM.addAction(helpA)
        helpM.addSeparator()
        helpM.addAction(aboutA)
        # develAction:
        debugA = newaction(self, 'devel help', short='Ctrl+D')
        debugA.triggered.connect(self.debugf)
        helpM.addSeparator()
        helpM.addAction(debugA)
        # end develAction
        #    ACTION CONNS
        self.blkA.triggered.connect(self.w.blkPb.click) #, Qt.UniqueConnection
        self.redA.triggered.connect(self.w.redPb.click)
        self.bluA.triggered.connect(self.w.bluPb.click)
        self.w.hTe.cursorPositionChanged.connect(self.ckcolour)
        self.colours_enable(0)
        closeA.triggered.connect(self.close)
        quitA.triggered.connect(self.gv_quitconfirm)
        helpA.triggered.connect(self.help_self)
        if parent: # devel if
            self.db = parent.db
            self.options = parent.options
            if 'usesymp' in self.options and self.options['usesymp']:
                self.options['usesymp'] = True
            else:
                self.options['usesymp'] = False
            self.pat = parent.pat # list of pat data
            self.staffid = parent.staffid
            self.symp = parent.symp
            self.symptoms = parent.symptoms
            self.units = parent.units
        else: # DEVEL: no parent
            self.symp = None
            import dbmod
            dbh = dbmod.Db_handler('enno')
            self.db = dbh.db_connect()
            if isinstance(self.db, str):
                from warn import Warning
                self.warning = Warning(self, 'db error', self.db)
                return
            self.curs = self.db.cursor()
            self.markups = {}
            from options import defaults as options
            self.options = options
            self.pat = ['Sophie', 'Boxer', 'f', '7 a', '18 kg', 'Deimel']
            self.staffid = 1
            self.symptoms = {}
            self.symptoms[0] = dict(symp='', shrt='')
            if 'usesymp' in self.options and self.options['usesymp']:
                res = querydb( # DEVEL: no parent
                    self,
                    'select sy_id,symptom,sy_short from symptoms '
                    'order by symptom')
                if res is None:  return # db error
                for e in res:
                    self.symptoms[e[0]] = dict(symp=e[1], shrt=e[2])
            else:
                self.options['usesymp'] = False # neu 130224
            self.units = {}
            res = querydb(self,'select u_id,u_name,u_pl,u_short from units')
            if res is None:  return # db error
            for e in res:
                if e[2]:
                    self.units[e[0]] = dict(n=e[1], pl=e[2], sh=e[3])
                else:
                    self.units[e[0]] = dict(n=e[1], pl=e[1], sh=e[3])
        for k, v in enumerate(
            [e['n'] for e in sorted(
                self.units.values(), key=lambda x: x['n'].lower())]):
            self.w.unitDd.addItem(v, k)
        self.w.patLb.setText(', '.join(self.pat[:5]))
        #    PARENT CONNECTIONS
        if parent: # devel if
            self.dbA.triggered.connect(parent.dbA.trigger)
            aboutA.triggered.connect(parent.aboutA.trigger)
            parent.gvquit.connect(self.gv_quit)
            parent.dbstate.connect(self.db_state)
            self.helpsig.connect(parent.helpsig)
            ## for e in parent.types.keys():
            ##     setattr(self, 'type' + e, parent.types[e])
            self.ptypes = parent.ptypes # take care client not yet impl!
            ## self.startdt = parent.startdt # nothing lost here
            self.rundt = parent.rundt
            self.timer = parent.timer
        else: # devel else
            self.ptypes = dict(
                other=7, med=3, serv=4, good=5, food=6, cons=1, hist=2, vac=8)
            self.rundt = datetime.now()
            self.timer = Ticker(self)
            self.timer.run()
        self.w.pDte.dateTimeChanged.connect(self.settime)
        ch_conn(self, 'tick', self.timer.tick, self.update_time)
        #    INIT
        if not self.curs:
            try:
                self.curs = self.db.cursor()
            except (OperationalError, AttributeError) as e:
                self.db_state(e)
                return
        self.dbA.setVisible(0)
        self.dbA.setEnabled(0)
        logname = querydb(
            self,
            'select stf_logname from staff where stf_id=%s', (self.staffid,))
        if logname is None:  return # db error
        logname = logname[0][0]
        self.w.lLb.setText(logname)
        if self.options['usesymp']:
            interim = {} # hierwei, geht das nicht einfacher?
            for i in xrange(1, len(self.symptoms)):
                interim[i] = self.symptoms[i]['symp']
            interim = sorted(
                [e for e in interim.items()], key=lambda k: k[1])
            for e in interim:
                self.w.sympDd.addItem(e[1], e[0])
            if self.symp:
                self.w.sympDd.setCurrentIndex(
                    self.w.sympDd.findData(self.symp, 32))
            else:
                self.w.sympDd.setCurrentIndex(0)
            if self.w.sympDd.count() < 2:
                self.w.sympDd.hide()
                self.w.sympLb.hide()
                self.symp = 1
            else:
                self.w.sympDd.activated.connect(self.set_symp)
        else:
            self.symp = 1
        self.w.tsysRb.clicked.connect(self.toggle_timer)
        self.w.trunRb.clicked.connect(self.toggle_timer)
        self.w.tstopRb.clicked.connect(self.toggle_timer)
        self.w.trunRb.setEnabled(0)
        self.w.okPb.setDefault(1)
        self.keycheck = Keycheck(self)
        self.installEventFilter(self.keycheck)
        self.w.plist.installEventFilter(self.keycheck)
        ch_conn(self, 'esc', self.keycheck.esc, self.w.ccPb.click)
        self.w.ccPb.clicked.connect(self.close)
        # markup unnec for history
        if 'usemark' in self.options and self.options['usemark']:
            if parent: # devel if
                self.markups = parent.markups
                self.markupid = parent.markupid
            else:
                self.markups = {}
                res = querydb(self,'select m_id,m_name,m_rate from markups '
                              'where not m_obs')
                if res is None:  return # db error
                for e in res:
                    self.markups[e[0]] = dict(n=e[1], r=e[2])
                self.markupid = 1
            self.markup = self.markups[self.markupid]['r']
            for i in sorted(self.markups.keys()):
                self.w.markupDd.insertItem(i, '{} ({}%)'.format(
                    self.markups[i]['n'], percent(self.markups[i]['r']*100)))
            self.w.markupDd.activated.connect(self.set_markup)
            self.w.markupDd.setCurrentIndex(self.markupid-1)
        else:
            self.markup = 0
            self.toggle_markup(0)
        self.vats = parent.vats
        self.vat = 0
        if len(self.vats) > 1: # a country in this world without vat? SA
            if 'stdvat' in self.options:
                self.vat = int(self.options['stdvat']) - 1
            for e in self.vats:
                self.w.vatDd.insertItem(e[0], '{} ({}%)'.format(
                    e[1], percent(e[2]*100)))
                self.w.avatDd.insertItem(e[0], '{} ({}%)'.format(
                    e[1], percent(e[2]*100)))
            self.w.vatDd.setCurrentIndex(self.vat)
            self.w.avatDd.setCurrentIndex(self.vat)
            self.w.vatDd.currentIndexChanged.connect(self.set_vat)
            self.w.avatDd.activated.connect(self.set_vat2)
        else:
            for w in (self.w.vatLb, self.w.vatDd, self.w.avatLb, self.w.avatDd):
                w.hide()
                w.setEnabled(False)
        self.prids = []
        self.row = -1
        self.w.hTe.textChanged.connect(self.hcount)
        self.w.blkPb.clicked.connect(self.setcolour_blk)
        self.w.redPb.clicked.connect(self.setcolour_red)
        self.w.bluPb.clicked.connect(self.setcolour_blu)
        self.w.noSb.valueChanged.connect(self.adapt_units)
        self.w.durSb.valueChanged.connect(self.ck_dur)
        self.w.durSb.valueChanged.connect(self.adapt_for)
        self.w.codeLe.textEdited.connect(self.code_work)
        self.w.freetxtCb.stateChanged.connect(self.freetext)
        self.w.applDd.currentIndexChanged.connect(self.code_text)
        self.w.noSb.valueChanged.connect(self.code_text)
        self.w.unitDd.currentIndexChanged.connect(self.code_text)
        self.w.freqDd.currentIndexChanged.connect(self.code_text)
        self.w.periodDd.currentIndexChanged.connect(self.code_text)
        self.w.regionDd.currentIndexChanged.connect(self.code_text)
        self.w.durSb.valueChanged.connect(self.code_text)
        self.w.durDd.currentIndexChanged.connect(self.code_text)
        self.w.precDd.currentIndexChanged.connect(self.code_text)
        self.w.alertLb.hide()
        if action == 'h':
            self.sel_hist()
        else:
            self.pheader = [
                self.tr('Description'),
                self.tr('Abbr'),
                self.tr('Unit'),
                self.tr('gr./U'),
                ]
            self.w.plist.set_headers(self.pheader)
            if parent: # devel if
                self.pid = parent.pid
            else:
                self.pid = 20
            self.instruct = False
            if action == 'c':
                self.list_cons()
            elif action == 'v':
                self.list_vaccs()
            else:
                self.list_prod(prod)

    def adapt_for(self, val):
        self.w.forLb.setEnabled(val)
        self.w.durDd.setEnabled(val)
    
    def adapt_units(self, val):
        if val == 1:
            for i in xrange(1, self.w.unitDd.count()):
                self.w.unitDd.setItemText(
                    i, self.units[
                        self.w.unitDd.itemData(i, 32).toInt()[0]]['n'])
        else:
            for i in xrange(1, self.w.unitDd.count()):
                idx = self.w.unitDd.itemData(i, 32).toInt()[0]
                if (self.units[idx]['n'] == self.units[i]['pl'] or
                    not self.units[idx]['pl']):
                    continue
                else:
                    self.w.unitDd.setItemText(i, self.units[idx]['pl'])

    def ck_dur(self, val):
        if val == 1:
            for i in xrange(self.w.durDd.count()):
                if self.w.durDd.itemText(i) == self.tr('days'):
                    self.w.durDd.setItemText(i, self.tr('day'))
                elif self.w.durDd.itemText(i) == self.tr('weeks'):
                    self.w.durDd.setItemText(i, self.tr('week'))
        else:
            for i in xrange(self.w.durDd.count()):
                if self.w.durDd.itemText(i) == self.tr('day'):
                    self.w.durDd.setItemText(i, self.tr('days'))
                elif self.w.durDd.itemText(i) == self.tr('week'):
                    self.w.durDd.setItemText(i, self.tr('weeks'))
    
    def ck_instr(self):
        """Check if instructions meet prescribed numbers."""
        self.w.histShow.hide()
        no = Decimal(str(self.w.noSb.value()))
        freq = (not self.w.freqDd.currentText() and 1 or
                self.w.freqDd.currentText()==self.tr('once') and 1 or
                self.w.freqDd.currentText()==self.tr('twice') and 2 or
                self.w.freqDd.currentText()==self.tr('three times') and 3 or
                self.w.freqDd.currentText().startsWith('3 ') and 3)
        period = (not self.w.periodDd.currentText() and 1 or
                  self.w.periodDd.currentText() == self.tr('daily') and 1 or
                  self.w.periodDd.currentText().startsWith(
                      self.tr('every other')) and Decimal('0.5') or
                  self.w.periodDd.currentText().startsWith(
                      self.tr('per w')) and Decimal(str(1/7)) or
                  self.w.periodDd.currentText().startsWith(
                      self.tr('per m')) and Decimal(str(1/30)) or
                  self.w.periodDd.currentText().startsWith(
                      self.tr('daily (every 12')) and 2 or
                  self.w.periodDd.currentText().startsWith(
                      self.tr('daily (every 8')) and 3)
        dur = Decimal(str(self.w.durSb.value()))
        days = (
            self.w.durDd.currentText().startsWith(self.tr('day')) and 1 or
            self.w.durDd.currentText().startsWith(self.tr('week')) and 7)
        amount = no * freq * period * dur * days
        if (self.w.durSb.value() and self.amount != amount and
            not self.w.freetxtCb.isChecked()):
            return self.tr(
                '<font color="red"><b>Instructions don\'t match prescribed '
                'amount: {} vs {}.</b></font color>'.format(
                    amount, self.amount))
        return ''

    def ck_text(self): # stupid hack for loquacious Qt colour management
        if (self.w.hTe.toHtml().count('<span style=" color:') and
            (self.w.hTe.toHtml().count('<span style=" color:#') !=
             self.w.hTe.toHtml().count('<span style=" color:#000000'))):
            text = ''
            for i, s in enumerate(
                self.w.hTe.toHtml().split('<span style=" color:#000000;">')):
                if not i%2:
                    text += s
                else:
                    text += s.replace('</span>', '', 1)
            return text
        return str(self.w.hTe.toPlainText().toLatin1()) # hierwei

    def ck_unit(self):
        if (self.units[self.u_id]['n'] == self.units[self.u_id]['pl'] or
            not self.units[self.u_id]['pl'] or
            self.w.amountSb.value() == 1):
            self.w.unitLb.setText(self.units[self.u_id]['n'])
        else:
            self.w.unitLb.setText(self.units[self.u_id]['pl'])
        self.w.okPb.setEnabled(self.w.amountSb.value())

    def ckcolour(self):
        col = self.w.hTe.textColor().name()
        if col == '#000000':
            self.w.redPb.setChecked(0)
            self.w.bluPb.setChecked(0)
            self.w.blkPb.setChecked(1)
        elif col == '#ff0000':
            self.w.blkPb.setChecked(0)
            self.w.bluPb.setChecked(0)
            self.w.redPb.setChecked(1)
        elif col == '#0000ff':
            self.w.blkPb.setChecked(0)
            self.w.redPb.setChecked(0)
            self.w.bluPb.setChecked(1)
            
    def closeEvent(self, ev):
        if not self.parent: # devel if
            self.timer.stop()
        ch_conn(self, 'tick')
        if hasattr(self, 'symptimer'):
            self.symptimer.stop()
            ch_conn(self, 'blink')
            ch_conn(self, 'symptimer')
        self.closed.emit()

    def code_text(self):
        txt = ' '.join(map(str,
                           (self.w.applDd.currentText(),
                            self.w.noSb.value() and
                            Decimal(str(self.w.noSb.value())).normalize() or
                            '',
                            self.w.unitDd.currentText(),
                            self.w.freqDd.currentText(),
                            self.w.periodDd.currentText(),
                            self.w.regionDd.currentText(),
                            self.w.forLb.isEnabled() and self.tr('for') or
                            '',
                            self.w.durSb.value() and
                            int(self.w.durSb.value()) or '',
                            self.w.durSb.value() and 
                            self.w.durDd.currentText() or '',
                            self.w.precDd.currentText() and
                            '<br>' + self.w.precDd.currentText() or '')))
        self.w.preview.setText(self.ltxt + txt)
        self.insttxt = txt
        
    def code_unset(self, which=0):
        for dd in (self.w.applDd, self.w.unitDd, self.w.freqDd,
                   self.w.periodDd, self.w.regionDd, self.w.durDd,
                   self.w.precDd)[which:]:
            dd.setCurrentIndex(0)
        for sb in (self.w.noSb, self.w.durSb)[
            (which and which<5) and 1 or which and 2 or 0:]:
            sb.setValue(0)
        self.code_text()
        
    def code_work(self, txt=''):
        """Set fields according to abbrev 'code'."""
        if not txt:
            self.code_unset()
            return
        if txt[0] in self.inst1:
            self.w.applDd.setCurrentIndex(self.inst1.index(txt[0])+1)
        else:
            self.code_unset()
            return
        if len(txt) < 2:
            return
        no = 0
        testit = txt[1:7]
        try:
            no = float(testit)
            self.nidx = len(testit)
        except ValueError:
            maxn = len(testit)
            for i in xrange(maxn):
                try:
                    no = float(testit)
                    self.nidx = len(testit)
                    break
                except ValueError:
                    testit = testit[:-1]
                    continue
        self.w.noSb.setValue(no)
        if len(txt) < self.nidx+2:
            self.code_unset(1)
            return
        for i in self.units:
            if txt[self.nidx+1] == self.units[i]['sh']:
                self.w.unitDd.setCurrentIndex(
                    self.w.unitDd.findData(i, 32))
                break
        if not self.w.unitDd.currentIndex():
            return
        if len(txt) < self.nidx+3:
            self.code_unset(2)
            return
        ftxt = self.nidx + 2
        if txt[ftxt:ftxt+3] in self.inst2:
            self.w.freqDd.setCurrentIndex(
                self.inst2.index(txt[ftxt:ftxt+3])+1)
            ftxt += 3
        elif txt[ftxt] in self.inst2:
            self.w.freqDd.setCurrentIndex(self.inst2.index(txt[ftxt])+1)
            ftxt += 1
        else:
            self.code_unset(3)
            return
        if len(txt) < ftxt+1:
            self.code_unset(3)
            return
        if txt[ftxt:ftxt+2] in self.inst3:
            self.w.periodDd.setCurrentIndex(
                self.inst3.index(txt[ftxt:ftxt+2])+1)
            ftxt += 2
        elif txt[ftxt] in self.inst3:
            self.w.periodDd.setCurrentIndex(self.inst3.index(txt[ftxt])+1)
            ftxt += 1
        else:
            self.code_unset(4)
            return
        if len(txt) < ftxt+1:
            self.code_unset(4)
            return
        if txt[ftxt:ftxt+2] in self.inst4:
            self.w.regionDd.setCurrentIndex(
                self.inst4.index(txt[ftxt:ftxt+2])+1)
            ftxt += 2
        else:
            self.w.regionDd.setCurrentIndex(0)
        if len(txt) < ftxt+1:
            if self.w.regionDd.currentIndex():
                self.w.durSb.setValue(0)
            else:
                self.code_unset(5)
            return
        testit = txt[ftxt:ftxt+2]
        no = 0
        try:
            no = int(testit)
            nidx = len(testit)
        except ValueError:
            testit = testit[0]
            try:
                no = int(testit)
                nidx = len(testit)
            except ValueError:
                return
        self.w.durSb.setValue(no)
        ftxt += nidx
        if len(txt) < ftxt+1:
            self.code_unset(5)
            return
        if txt[ftxt] in self.inst5:
            self.w.durDd.setCurrentIndex(self.inst5.index(txt[ftxt])+1)
            ftxt += 1
        else:
            self.w.durDd.setCurrentIndex(0)
        if len(txt) < ftxt+1:
            self.code_unset(6)
            return
        if txt[ftxt] in self.inst6:
            self.w.precDd.setCurrentIndex(self.inst6.index(txt[ftxt])+1)
        else:
            self.w.precDd.setCurrentIndex(0)
        
    def colours_enable(self, act=1):
        self.blkA.setVisible(act)
        self.redA.setVisible(act)
        self.bluA.setVisible(act)
        self.blkA.setEnabled(act)
        self.redA.setEnabled(act)
        self.bluA.setEnabled(act)

    def confirm(self):
        """Confirm (to save?) entered data."""
        ch_conn(self, 'hist')
        self.colours_enable(0)
        self.w.histShow.hide()
        self.w.skipPb.hide()
        self.w.skipPb.setEnabled(False)
        if self.w.hTe.toPlainText():
            self.history = self.ck_text() # check if html or not
        self.setWindowTitle('GnuVet: ' + self.tr('Confirm'))
        self.w.okPb.setText(self.tr('OK'))
        self.w.histFr.setEnabled(0)
        self.w.instFr.setEnabled(0)
        if self.startdt is None:
            self.startdt = self.w.pDte.dateTime().toPyDateTime()
        addtxt = self.startdt.strftime('%d.%m.%Y %H:%M<br>')
        msg = ''
        if self.instruct:
            msg = self.ck_instr()
            addtxt += self.insttxt
            if not msg:
                self.print_label()
        elif self.action in ('c', 'v'):
            if not self.symp:  self.symp = 1
            self.w.histShow.setHtml(
                (self.options['usesymp'] and
                 (self.tr('<i><center>lead symptom: ') +
                  (self.symptoms[self.symp]['symp'] and
                   self.symptoms[self.symp]['symp'] or 'none') +
                  '</i><br></center>') or '') +
                (self.histconf and self.history or '')) # HIERWEI
            self.w.histShow.show()
        self.w.msgLb.setText(msg)
        txt = ('<b>' + self.prodname + ':</b>&nbsp;&nbsp;' +
               (int(self.amount) == self.amount and
                str(int(self.amount)) or
                str(Decimal(str(self.amount)).normalize())) + ' ' +
               self.w.unitLb.text() + '<br>' + addtxt)
        self.w.instLb.setText(txt)
        self.w.confFr.setEnabled(1)
        self.w.confFr.show()
        ch_conn(self, 'ok', self.w.okPb.clicked, self.send_data)
        if self.prinfo[self.selrow]['instr']:
            ch_conn(self, 'back', self.w.backPb.clicked, self.sel_instr)
        elif self.action in ('c', 'h'):
            ch_conn(self, 'back', self.w.backPb.clicked, self.sel_hist)
        else:
            ch_conn(self, 'back', self.w.backPb.clicked, self.sel_amount)

    def dbdep_enable(self, yes=True):
        """En- or disable db dependent actions."""
        self.dbA.setVisible(not yes)
        self.dbA.setEnabled(not yes)
        self.w.pLe.setEnabled(yes)
        
    def db_state(self, msg=''):
        """Actions to be taken on db loss and gain."""
        # This should be signalled to prime ancestor
        self.dberr = msg and True or False
        self.w.no_dbconn.setVisible(self.dberr)
        self.dbstate.emit(not self.dberr)
        self.dbdep_enable(not self.dberr)
        if not hasattr(self, 'warnw'):
            from warn import Warning
        if not msg:
            msg = 'Unspecified db error.'
        self.warnw = Warning(self, self.tr('GnuVet: Db Error'), msg)
        if not self.isVisible(): # devel: if not parent...
            self.warnw.closed.connect(self.show)

    def fill_inst(self):
        """Fill in the various dropdowns for instructions."""
        res = querydb(self, 'select inst_id,inst_pos,inst_txt,inst_abbr '
                      'from instructions order by inst_pos,inst_txt')
        if res is None:  return # db error
        for e in res:
            if e[1] == 1:
                self.w.applDd.addItem(e[2], e[0])
                self.inst1.append(e[3])
            elif e[1] == 2:
                self.w.freqDd.addItem(e[2], e[0])
                self.inst2.append(e[3])
            elif e[1] == 3:
                self.w.periodDd.addItem(e[2], e[0])
                self.inst3.append(e[3])
            elif e[1] == 4:
                self.w.regionDd.addItem(e[2], e[0])
                self.inst4.append(e[3])
            elif e[1] == 5:
                self.w.durDd.addItem(e[2], e[0])
                self.inst5.append(e[3])
            elif e[1] == 6:
                self.w.precDd.addItem(e[2], e[0])
                self.w.precDd.setItemData(
                    self.w.precDd.count()-1, e[2], 3)
                self.inst6.append(e[3])
                    
    def fill_table(self, result):
        """Fill table from result list."""
        # 0 name 1 short 2 u_id 3 nprice 4 vat_id 5 id 6 type 7 instr 8 mark
        for res in result:
            if res[5] in self.prids:
                continue
            data = list(res[:2])
            data.append(self.units[res[2]]['n'])
            spr = res[3] * (1 + self.vats[res[4]-1][2]) # gr. price
            if len(res) == 9 and res[8] > 1:
                data.append(str(money(spr, 1 + self.markup)))
            else:
                data.append(str(money(spr)))
            self.prices.append((res[3], res[4]))
            self.prinfo[len(self.w.plist.lrows)] = dict(
                id=res[5],type=res[6],uid=res[2],instr=res[7],
                mark=('usemark' in self.options and
                      self.options['usemark']) and
                (len(res) == 9 and res[8]) and res[8] or 1)
            self.prids.append(res[5])
            self.w.plist.append_row(data)

    def freetext(self, state):
        self.w.freetxtTe.setVisible(state)
        for e in (self.w.codeLb, self.w.codeLe):
            e.setEnabled(not state)
        for e in (self.w.applDd, self.w.unitDd, self.w.freqDd, self.w.periodDd,
                  self.w.regionDd, self.w.durDd, self.w.precDd,
                  self.w.noSb, self.w.durSb):
            e.setEnabled(not state)
            e.setVisible(not state)
        if state:
            self.w.freetxtTe.textChanged.connect(self.setfreetxt)
            self.setfreetxt()
            self.w.freetxtTe.setFocus()
        else:
            self.w.freetxtTe.textChanged.disconnect(self.setfreetxt)
            self.code_text()
            self.w.applDd.setFocus()
                      
    def gv_quit(self, quitnow=False):
        self.gvquit.emit(quitnow)
        if quitnow:
            self.close()
            
    def gv_quitconfirm(self):
        if self.parent:
            self.parent.gv_quitconfirm()
        else:
            self.close()

    def hcount(self):
        self.w.hcharLb.setText(str(self.w.hTe.remainder()))
        ## self.w.okPb.setEnabled(self.w.hTe.remainder() > 0) # what's this?

    def help_self(self):
        """Launch help window."""
        self.helpsig.emit('products')

    def hok_enable(self):
        self.w.okPb.setEnabled(self.w.hTe.toPlainText() and True or False)
    
    def init_label(self):
        if not self.address:
            branch = ('branch' in self.options and self.options['branch'] or 1)
            addr = querydb(
                self, 'select branch_name,branch_tel,housen,street,village '
                'from branches,addresses where branch_address=addr_id and '
                'branch_id=%s', (branch,))
            if addr is None:  return # db error
            for l in addr:
                branch = l[0]
                tel    = l[1]
                housen = l[2]
                street = l[3]
                village= l[4]
            self.address = ', '.join([branch, housen, street, village, tel])
        self.ltxt = (
            '<center><font size="-2">' + self.address + '<br>' +
            self.rundt.strftime('%d.%m.%y %H:%M') + '</font size><br><br>' +
            ' '.join([self.pat[0], self.pat[-1]]) + '<br><b>' + self.prodname +
            '</b> ' + str(Decimal(str(self.amount))) + ' ' +
            self.w.unitLb.text() + '<br><br>')
        self.w.preview.setText(self.ltxt)

    def list_cons(self):
        """Query db for consultations."""
        self.startover()
        query = (
            'select pr_name,pr_short,pr_u,pr_nprice,vat_id,pr_id,pr_type,'
            'pr_instr from products,vats where not pr_obs and pr_vat=vat_id '
            'and pr_type=%s {}order by pr_name')
        addit = str(self.w.pLe.text().toLatin1()).lower()
        if not addit:
            query = query.format('')#HIERWEI
            res = querydb(self, query, (self.ptypes['cons'],))
        else:
            addit = '%{}%'.format(addit)
            query = query.format('and (pr_name ilike %s or pr_short ilike %s) ')
            res = querydb(self, query, (self.ptypes['cons'], addit, addit))
        self.waitstart()
        if res is None:  return # db error
        self.fill_table(res)
        self.setWindowTitle('GnuVet: ' + self.tr('book Consultation'))
        self.initaction = self.action
        self.sel_prod()
        self.w.backPb.setEnabled(0)
        self.w.okPb.setEnabled(1)
        if not len(self.w.plist.lrows):
            self.waitstop()
            err = self.tr('Consultation')
            if addit:
                err += (self.tr(' with ') + '"{}"'.format(addit))
            self.no_matches(err)
        else:
            self.w.plist.align_data(3, 'r')
            self.match_list()
    
    def list_goods(self, prod=''):
        """Query db for products foods/goods sale when no vs is nec."""
        if not prod:
            prod = str(self.w.pLe.text().toLatin1()).lower()
        self.startover()
        query = (
            'select pr_name,pr_short,pr_u,pr_nprice,vat_id,pr_id,pr_type,'
            'pr_instr from products,vats where not pr_obs and {0} ilike %s and '
            'pr_vat=vat_id and pr_type in(%s,%s)order by {0}')
        if not prod:
            query = query.format('pr_name')
            self.waitstart()
            self.curs.execute(
                query, ('%', self.ptypes['good'], self.ptypes['food']))
            self.fill_table(self.curs.fetchall())
        else:
            conds = (
                ('pr_name', '{}%'.format(prod)),
                ('pr_name', '_%{}%'.format(prod)),
                ('pr_short', '{}%'.format(prod)),
                ('pr_short', '_%{}%'.format(prod)),
                )
            self.waitstart()
            for tup in conds:
                try:
                    self.curs.execute(
                        query.format(tup[0]),
                        (tup[1], self.ptypes['good'], self.ptypes['food']))
                    self.fill_table(self.curs.fetchall())
                except OperationalError as e:
                    self.db_state(e)
                    return
        self.setWindowTitle('GnuVet: ' + self.tr('select Product'))
        self.sel_prod()
        if not len(self.w.plist.lrows):
            self.waitstop()
            self.no_matches(prod)
        else:
            self.w.plist.align_data(3, 'r')
            self.match_list()
        self.w.backPb.setEnabled(0)
        self.w.backPb.hide()
    
    def list_prod(self, prod=''):
        """Query db for products except vacc and cons."""
        if not prod: # called via Pb for addLe 
            prod = str(self.w.pLe.text().toLatin1()).lower()
        self.startover()
        query = (
            'select pr_name,pr_short,pr_u,pr_nprice,vat_id,pr_id,pr_type,'
            'pr_instr from products,vats where not pr_obs and {0} {1} %s and '
            'pr_vat=vat_id and pr_type not in(%s,%s)order by {0}')
        if prod.count('|'):
            likeword = 'similar to'
        else:
            likeword = 'ilike'
        query = query.format('{0}', likeword)
        # 0 name 1 short 2 u_id 3 nprice 4 vat_id 5 id 6 type 7 instr
        if not prod:
            query = query.format('pr_name')
            self.waitstart()
            self.curs.execute(query, ('%', 'vac', 'con')) # hierwei get from db?
            self.fill_table(self.curs.fetchall())
        else:
            conds = (
                ('pr_name', '{}%'.format(prod)),
                ('pr_name', '_%{}%'.format(prod)),
                ('pr_short', '{}%'.format(prod)),
                ('pr_short', '_%{}%'.format(prod)),
                )
            self.waitstart()
            for tup in conds:
                try:
                    self.curs.execute(
                        query.format(tup[0]),
                        (tup[1], self.typevacc, self.ptypes['cons']))
                    self.fill_table(self.curs.fetchall())
                except OperationalError as e:
                    self.db_state(e)
                    return
        self.setWindowTitle('GnuVet: ' + self.tr('select Product'))
        self.action = 'p'
        self.sel_prod()
        if not len(self.w.plist.lrows):
            self.waitstop()
            self.no_matches(prod)
        else:
            self.w.plist.align_data(3, 'r')
            self.match_list()
        self.w.backPb.setEnabled(1)
        self.w.backPb.show()

    def list_vaccs(self):
        """Query db for vaccs."""
        self.startover()
        spec = querydb(
            self,
            'select b_spec from breeds,patients where p_id=%s and '
            'breed=breed_id', (self.pid,))
        if spec is None:  return # db error
        spec = spec[0][0]
        query = (
            'select pr_name,pr_short,pr_u,pr_nprice,pr_vat,pr_id,pr_type,'
            'pr_instr from products,vats,vaccinations '
            'where not pr_obs and pr_vat=vat_id and '
            'pr_type=%s and vac_sid=pr_id and vac_spec=%s {}'
            'order by pr_name')
        addit = str(self.w.pLe.text().toLatin1()).lower()
        if not addit:
            query = query.format('')
            res = querydb(self, query, ('vac', spec))
        else:
            addit = '%{}%'.format(addit)
            query = query.format('and (pr_name ilike %s or pr_short ilike %s) ')
            res = querydb(self, query, ('vac', spec, addit, addit))
        self.waitstart()
        if res is None:  return # db error
        self.fill_table(res)
        self.setWindowTitle('GnuVet: ' + self.tr('select Vaccination'))
        self.sel_prod()
        if not len(self.w.plist.lrows):
            self.waitstop()
            err = self.tr('Vaccination')
            if addit:
                err += (self.tr(' with ') + '"{}"'.format(addit))
            self.no_matches(err)
        else:
            self.w.plist.align_data(3, 'r')
            self.match_list()
    
    def match_list(self):
        """Settings when matches are found."""
        self.w.nomatchLb.hide()
        self.w.plist.set_colwidth(0, 350)
        self.w.plist.set_colwidth(1, 80)
        self.w.plist.set_colwidth(2, 70)
        self.w.plist.set_colwidth(3, 70)
        ch_conn(self, 'dclick',
                self.w.plist.doubleclicked, self.sel_amount)
        ch_conn(self, 'cic', self.w.plist.rowchanged, self.trackp)
        ch_conn(self, 'enter', self.keycheck.enter, self.w.okPb.click)
        ch_conn(self, 'ok', self.w.okPb.clicked, self.sel_amount)
        self.w.plist.select_row(row=0)
        self.waitstop()
        self.w.plist.setFocus()
    
    def no_matches(self, prod=''):
        """When no matches are found."""
        self.w.plist.clear()
        self.w.nomatchLb.show()
        self.w.nomatchLb.raise_()
        self.w.nomatchLb.setText(self.tr('No matches found for ') +
                                 '"{}"'.format(prod))
        ch_conn(self, 'ok', self.w.okPb.clicked, self.list_prod)
        self.w.pLe.selectAll()
        self.w.pLe.setFocus()

    def print_label(self):
        if self.options['nolabels']:
            return
        print('Printing label...')

    def reset_instr(self):
        for e in (self.w.applDd, self.w.unitDd, self.w.freqDd, self.w.periodDd,
                  self.w.regionDd, self.w.durDd, self.w.precDd):
            e.setCurrentIndex(0)
        for e in (self.w.noSb, self.w.durSb):
            e.setValue(0)
        self.w.codeLe.clear()
        self.w.freetxtTe.clear()
        
    def sel_amount(self): # 3 was 2
        """Prepare selecting amount of product."""
        self.w.skipPb.hide()
        self.w.skipPb.setEnabled(False)
        self.w.okPb.setText(self.tr('OK'))
        for f in (self.w.confFr, self.w.histFr, self.w.instFr, self.w.prodFr):
            f.hide()
            f.setEnabled(False)
        self.w.amountFr.show()
        self.w.amountFr.setEnabled(1)
        self.colours_enable(0)
        self.setWindowTitle('GnuVet: ' + self.tr('select Amount'))
        self.w.prodLb.setText(self.prodname)
        self.set_amount()
        self.w.priceSb.setValue(
            gprice(self.prices[self.selrow][0]*(1+self.markup),
                   self.vats[self.vat][2]))
        ch_conn(self, 'enter', self.keycheck.enter, self.w.okPb.click)
        if self.action == 'v':
            ch_conn(self, 'ok', self.w.okPb.clicked, self.sel_hist)
        elif self.options['usesymp'] and self.symp is None:
            ch_conn(self, 'ok', self.w.okPb.clicked, self.sel_symp)
        elif self.action == 'c':
            ch_conn(self, 'ok', self.w.okPb.clicked, self.sel_hist)
        elif self.prinfo[self.selrow]['instr']:
            ch_conn(self, 'ok', self.w.okPb.clicked, self.sel_instr)
        else:
            ch_conn(self, 'ok', self.w.okPb.clicked, self.confirm)
        self.w.backPb.setEnabled(1)
        ch_conn(self, 'back', self.w.backPb.clicked, self.sel_prod)
        self.w.amountSb.setFocus()
        self.w.amountSb.selectAll()
        ch_conn(self, 'aSb', self.w.amountSb.valueChanged, self.set_amount)
    
    def sel_hist(self): # 1 was 4 hierwei
        """Prepare getting clinical history from user input."""
        # arg for adding history separate from product entry
        c = self.w.hTe.textCursor()
        c.movePosition(11) # end
        self.w.hTe.setTextCursor(c)
        self.w.okPb.setEnabled(self.w.hTe.toPlainText() and True or False)
        self.setWindowTitle('GnuVet: ' + self.tr('Clinical History'))
        self.w.okPb.setText(self.tr('OK'))
        for f in (self.w.amountFr, self.w.confFr, self.w.instFr, self.w.prodFr):
            f.hide()
            f.setEnabled(False)
        self.w.histFr.show()
        self.w.histFr.setEnabled(1)
        self.colours_enable()
        ch_conn(self, 'hist', self.w.hTe.textChanged, self.hok_enable)
        ch_conn(self, 'enter', self.keycheck.enter, self.w.okPb.click)
        if self.action == 'h':
            self.w.backPb.setEnabled(False)
            self.w.backPb.hide()
        else:
            self.w.backPb.setEnabled(True)
            self.w.backPb.show()
            ch_conn(self, 'back', self.w.backPb.clicked, self.sel_amount)
        ch_conn(self, 'ok', self.w.okPb.clicked, self.confirm)
        self.w.hTe.setFocus()

    def sel_instr(self): # 5
        """Prepare selecting instructions from user input."""
        self.instruct = True
        self.colours_enable(0)
        self.setWindowTitle('GnuVet: ' + self.tr('set Instructions'))
        self.w.okPb.setText(self.tr('Print'))
        self.w.skipPb.show()
        self.w.skipPb.setEnabled(True)
        for f in (self.w.amountFr, self.w.confFr, self.w.histFr, self.w.prodFr):
            f.hide()
            f.setEnabled(False)
        self.w.instFr.show()
        self.w.instFr.setEnabled(1)
        if not self.gotinst:
            self.inst1 = []
            self.inst2 = []
            self.inst3 = []
            self.inst4 = []
            self.inst5 = []
            self.inst6 = []
            self.fill_inst()
            if self.dberr:  return # db error
            self.gotinst = True
        self.init_label()
        if self.dberr:  return # db error
        ch_conn(self, 'ok', self.w.okPb.clicked, self.confirm)
        ch_conn(self, 'back', self.w.backPb.clicked, self.sel_amount)
        #self.w.skipPb.clicked.connect(self.confirm)
        ch_conn(self, 'skip', self.w.skipPb.clicked, self.confirm)
        if self.w.freetxtCb.isChecked():
            self.w.freetxtTe.show()
            self.setfreetxt()
        else:
            self.w.freetxtTe.hide()
            self.code_text()
        self.w.applDd.setFocus()

    def sel_prod(self): # 2 was 1
        """Prepare selecting product from user input via plist."""
        for f in (self.w.amountFr, self.w.confFr, self.w.histFr, self.w.instFr):
            f.hide()
            f.setEnabled(False)
        self.w.prodFr.show()
        self.w.prodFr.setEnabled(1)
        self.w.plist.setFocus()
        self.w.backPb.setEnabled(0)
        ch_conn(self, 'enter', self.keycheck.enter, self.w.okPb.click)
        ch_conn(self, 'ok', self.w.okPb.clicked, self.sel_amount)
        ch_conn(self, 'switch_keycheck',
                self.w.pLe.textEdited, self.switch_keycheck)
        self.keychecked = False
            
    def sel_symp(self): # 4 was 3
        """Alert to select lead symptom: start blinking the dropdown."""
        self.setWindowTitle('GnuVet: select lead symptom')
        self.alerted = False
        if not hasattr(self, 'symptimer'):
            self.symptimer = Ticker(self, 0.5, False)
            self.symptimer.run()
        else:
            self.symptimer.run()
        ch_conn(self, 'blink', self.symptimer.tick, self.symp_blink)
        ch_conn(self, 'symptimer',
                self.w.sympDd.activated, self.symp_blinkstop)
        if self.prinfo[self.selrow]['instr']:
            ch_conn(self, 'ok', self.w.okPb.clicked, self.sel_instr)
        elif self.action == 'c':
            ch_conn(self, 'ok', self.w.okPb.clicked, self.sel_hist)
        else:
            ch_conn(self, 'ok', self.w.okPb.clicked, self.confirm)
        self.w.sympDd.setFocus()

    def send_data(self): # hierwei: vacc!
        """Pack available data into nice signal, emit it."""
        if not self.parent: # devel if
            print('send_data, finished')
            return
        if not self.symp:
            self.symp = 1
        if self.action == 'c':
            txt = self.history
            ch_conn(self, 'dta', self.dta, self.parent.book_cons)
        elif self.action == 'h':
            txt = self.history
            ch_conn(self, 'dta', self.dta, self.parent.book_hist)
        elif self.action == 'v':
            txt = self.history
            ch_conn(self, 'dta', self.dta, self.parent.book_vac)
        else:
            txt = self.insttxt
            ch_conn(self, 'dta', self.dta, self.parent.book_prod)
        self.dta.emit(
            (self.rundt, self.startdt,
             self.prinfo[self.selrow],#'id''type''uid''instr''mark'
             (Decimal(str(self.w.priceSb.value())), self.vat+1),
             self.amount, self.symp, txt))
        ch_conn(self, 'dta')
        self.instruct = False
        self.w.hTe.clear()

    def set_amount(self):#, amount
        self.amount = Decimal(str(self.w.amountSb.value()))
        if self.amount%1:
            quant = '0.00'
        else:
            quant = '0'
        self.amount = self.amount.quantize(Decimal(quant))
        self.ck_unit()

    def set_markup(self, mark):
        """Display new gprices after changing markup."""
        if self.markup == self.markups[mark+1]['r']:
            return
        self.markup = self.markups[mark+1]['r']
        for row in xrange(len(self.prinfo)):
            if self.prinfo[row]['mark'] == 1:
                continue
            self.w.plist.lrows[row][3].setText(str(
                gprice(self.prices[row][0] * (1+self.markup),
                       self.vats[self.vat][2])))

    def set_symp(self):
        self.symp = self.w.sympDd.itemData(
            self.w.sympDd.currentIndex(), 32).toInt()[0]

    def set_vat(self, vat):
        """Display new gprices after changing vat."""
        self.vat = vat
        self.w.avatDd.setCurrentIndex(vat)
        for row in xrange(len(self.prinfo)):
            self.w.plist.lrows[row][3].setText(str(
                gprice(self.prices[row][0]*(1+self.markup),
                       self.vats[self.vat][2])))

    def set_vat2(self, vat):
        if vat == self.vat:
            return
        self.vat = vat
        self.w.vatDd.setCurrentIndex(vat)
        self.w.priceSb.setValue(
            gprice(self.prices[self.selrow][0]*(1+self.markup),
                   self.vats[self.vat][2])) # ???
        
    def setfreetxt(self):
        txt = self.w.freetxtTe.toPlainText().replace('\n', '<br>')
        self.w.preview.setText(
            self.ltxt + txt)
        self.insttxt = txt
    
    def setcolour(self, colour='black'):
        self.w.hTe.setTextColor(getattr(Qt, colour))

    def setcolour_blk(self):
        self.setcolour()
    
    def setcolour_blu(self):
        self.setcolour('blue')

    def setcolour_red(self):
        self.setcolour('red')

    def settime(self, time):
        """Set times on dateTimeChanged of pDte.""" # HIERWEI
        # add question if times diff too much to make sense within one cons?
        # or disable pDte after booking cons?
        if self.rundt != time.toPyDateTime():
            if not self.w.tstopRb.isChecked():
                self.w.trunRb.setEnabled(True)
                self.w.trunRb.setChecked(True)
            self.rundt = time.toPyDateTime()

    def skipprint(self):
        print('skipprint')
        
    def startover(self):
        """Start anew: hide all other frames, show product frame."""
        self.w.amountSb.setValue(1)
        self.w.amountFr.hide()
        self.w.histFr.hide()
        self.w.instFr.hide()
        self.w.confFr.setEnabled(0)
        self.w.confFr.hide()
        self.prodname = None
        self.insttxt = None
        ch_conn(self, 'dclick')
        ch_conn(self, 'cic')
        self.w.plist.clear()
        self.prids = []  # pr_id, to prevent double entries
        self.prinfo = {} # to hold invisible data: 'id''type''uid''instr'
        self.prices = [] # list of (net price, vat_id) incl markup
        
    def switch_keycheck(self):
        """Switch keycheck back to the LineEdit."""
        if self.keychecked:
            return
        ch_conn(self, 'switch_keycheck')
        if self.action == 'c':
            ch_conn(self, 'enter', self.keycheck.enter, self.list_cons)
        elif self.action == 'v':
            ch_conn(self, 'enter', self.keycheck.enter, self.list_vaccs)
        else:
            ch_conn(self, 'enter', self.keycheck.enter, self.list_prod)
        self.keychecked = True

    def symp_blink(self):
        """Blinks the blue symptom label."""
        if self.symp:
            return
        if self.alerted:
            self.w.alertLb.hide()
            self.alerted = False
        else:
            self.w.alertLb.show()
            self.alerted = True
        
    def symp_blinkstop(self):
        """Stops blinking timer of symptom label."""
        if hasattr(self, 'symptimer'):
            self.symptimer.stop()
            ch_conn(self, 'blink')
            ch_conn(self, 'symptimer')
        self.w.alertLb.hide()

    def toggle_markup(self, state):
        self.w.markupDd.setEnabled(state)
        self.w.markupDd.setVisible(state)
        self.w.markupLb.setEnabled(state)
        self.w.markupLb.setVisible(state)
        
    def toggle_timer(self):
        """Adapt the DateEdit to run|stop chosen via radiobuttons."""
        if self.w.tsysRb.isChecked():
            if self.parent: # devel if
                self.rundt = self.parent.rundt = datetime.now()
            else:
                self.rundt = datetime.now()
            self.w.pDte.setDateTime(self.rundt)
            self.w.trunRb.setEnabled(0)
            self.timer.run()
            ch_conn(self, 'tick', self.timer.tick, self.update_time)
        elif self.w.tstopRb.isChecked():
            self.timer.stop()
            self.w.trunRb.setEnabled(1)
        else:
            self.timer.run()
            ch_conn(self, 'tick', self.timer.tick, self.update_time)

    def trackp(self, row):
        """Keep track of selected item."""
        self.selrow = row
        self.prodname = self.w.plist.lrows[row][0].text()
        self.u_id = self.prinfo[row]['uid']

    def update_disp(self, sdt, rdt, symp, prod=None, action='p'):
        """Update display -- called from parent."""
        self.startover()
        ch_conn(self, 'tick', self.timer.tick, self.update_time)
        self.startdt = sdt
        self.rundt = rdt
        self.symp = symp
        self.toggle_timer()
        if prod == 'con':
            self.list_cons()
        elif action == 'v':
            self.list_vaccs()
        else:
            self.list_prod(prod)
    
    def update_time(self):
        """Update the clock."""
        self.rundt += timedelta(0, 1)
        self.w.pDte.dateTimeChanged.disconnect(self.settime)
        self.w.pDte.setDateTime(self.rundt)
        self.w.pDte.dateTimeChanged.connect(self.settime)

    def waitstart(self):
        """Wait for results."""
        self.setCursor(Qt.WaitCursor)
        self.w.pLe.setEnabled(0)
        self.w.plist.setEnabled(0)

    def waitstop(self):
        """Stop waiting as results are there."""
        self.w.pLe.setEnabled(1)
        self.w.plist.setEnabled(1)
        self.unsetCursor()
        
    def debugf(self):
        print(self.w.hTe.toHtml())
            
if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    a = QApplication([])
    a.setStyle('plastique')
    b = Products(None, prod='amoxi')
    b.show()
    exit(a.exec_())
