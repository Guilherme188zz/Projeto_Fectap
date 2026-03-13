"""Search Add Edit patient interface."""
# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

# TODO:
# Add completer for petpassLe and idLe
# recheck all -- still functional, useful? connect.s? g|setattr(self, what)!!!
# switch off completers when adding patient?
# re-implement state_write and db_err and _changes_ and suchlike
# test pat_add things with client list (clis)
# edit -> name history!  check with self.today
# error on closing when children around
# TODO:
# remove invisible columns, use cell.data for p_id
# check all button connections
#
# pull out all connections related to other windows to those windows!

from datetime import date, timedelta
from psycopg2 import OperationalError
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import (QApplication, QMainWindow, QMenu)
import gv_qrc
from gcompleter import Gcompleter
from keycheck import Keycheck
from util import ch_conn, newaction, querydb
from saepat_ui import Ui_Saepat

class Saepat(QMainWindow):
    """Search|Add|Edit Patient."""
    # signals:
    gvquit = pyqtSignal(bool)
    cidsig   = pyqtSignal(int)
    dbstate   = pyqtSignal(bool)
    helpsig   = pyqtSignal(str)
    needcid  = pyqtSignal(tuple) # check this, makes sense?
    restoreme = pyqtSignal(tuple)
    savestate = pyqtSignal(tuple)
    pidsig    = pyqtSignal(int)

    # vars:
    adding = db_err = idok = nameok = False
    changes = currentspec = 0
    completed = ''
    curs = None
    gaia = None
    seen = None
    unsaved = False # unsaved changes anywhere?

    def __init__(self, parent=None, pid=0, cid=0, act='s'):
        super(Saepat, self).__init__(parent)
        self.parent = parent
        self.pid = pid
        self.act = act
        self.w = Ui_Saepat()
        self.w.setupUi(self)
        #    instance VARIABLES
        self.conns = {} # (py)qt bug: segfaults on disconnect() w/o arg
        self.sigs  = {}
        self.pids = []
        self.startv = {}
        #    ACTIONS
        self.dbA = newaction(self, '&Reconnect to database',
                              'Try to reconnect to database', 'Ctrl+R')
        self.clichangeA = newaction(
            self, '&Change Owner', 'Change owner of current patient')
        closeA = newaction(self, 'Close', 'Close this window', 'Ctrl+W')
        self.newpatA = newaction(
            self,'&Patient','create Patient record from entered data','Ctrl+P')
        self.newbreedA = newaction(
            self, '&Breed', 'create new Breed entry', 'Ctrl+B')
        self.newspecA = newaction(
            self, '&Species', 'create new Species entry', 'Ctrl+S')
        self.newcolA = newaction(
            self, 'C&olour', 'create new Colour entry', 'Ctrl+O')
        self.newlocA = newaction(
            self, 'Locatio&n', 'create new Location entry', 'Ctrl+N')
        self.newinsA = newaction(
            self, '&Insurance', 'create new Insurance entry', 'Ctrl+I')
        # devel:
        debugA = newaction(self, 'Debug', short='Ctrl+D')
        debugA.triggered.connect(self.debugf)
        self.addAction(debugA)
        # end devel
        helpA = newaction(self, '&Help', 'context sensitive help', 'F1')
        aboutA = newaction(self, 'About &GnuVet', 'GnuVet version info')
        quitA = newaction(self, '&Quit GnuVet', 'Quit GnuVet', 'Ctrl+Q')
        #    MENUES
        taskM = QMenu(self.w.menubar)
        taskM.setTitle(self.tr('&Task'))
        self.w.menubar.addAction(taskM.menuAction())
        self.newM = QMenu(self.w.menubar)
        self.newM.setTitle(self.tr('&New'))
        self.w.menubar.addAction(self.newM.menuAction())
        helpM = QMenu(self.w.menubar)
        helpM.setTitle(self.tr('&Help'))
        self.w.menubar.addAction(helpM.menuAction())
        #    SUBMENUES
        taskM.addAction(self.dbA)
        taskM.addSeparator()
        taskM.addAction(self.clichangeA)
        taskM.addSeparator()
        taskM.addAction(closeA)
        taskM.addAction(quitA)
        taskM.setSeparatorsCollapsible(True)
        self.newM.addAction(self.newpatA)
        self.newM.addSeparator()
        self.newM.addAction(self.newbreedA)
        self.newM.addAction(self.newspecA)
        self.newM.addAction(self.newcolA)
        self.newM.addSeparator()
        self.newM.addAction(self.newlocA)
        self.newM.addAction(self.newinsA)
        helpM.addAction(helpA)
        helpM.addSeparator()
        helpM.addAction(aboutA)
        self.w.pfindDd.adjustSize()
        #    DATEEDITS
        self.w.neutDe.setMinimumDate(date(1900, 1, 1))
        self.w.dobDe.setMaximumDate(date(2099, 12, 31))
        self.w.dobDe.setMinimumDate(date(1900, 1, 1))
        self.w.regDe.setMaximumDate(date(2099, 12, 31))
        self.w.regDe.setMinimumDate(date(1900, 1, 1))
        self.w.seenDe.setMinimumDate(date(1980, 1, 1))
        #    ACTION CONNECTIONS
        closeA.triggered.connect(self.close)
        self.clichangeA.triggered.connect(self.cli_change)
        helpA.triggered.connect(self.help_self)
        quitA.triggered.connect(self.gv_quitconfirm)
        self.newpatA.triggered.connect(self.pat_act)
        self.newbreedA.triggered.connect(self.add_breed)
        self.newspecA.triggered.connect(self.add_spec)
        self.newcolA.triggered.connect(self.add_col)
        self.newlocA.triggered.connect(self.add_loc)
        self.newinsA.triggered.connect(self.add_ins)
        #    PARENT CONNECTIONS
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
            self.gaia.dbstate.connect(self.db_state) # ? hierwei
            self.helpsig.connect(self.gaia.gv_help)
            self.savestate.connect(self.gaia.state_write)
            self.staffid = self.gaia.staffid
        else:
            from options import defaults as options
            self.options = options
            import dbmod
            dbh = dbmod.Db_handler('enno')
            self.db = dbh.db_connect()
            if type(self.db) is str:
                self.db_state(self.db)
                return # ?
            self.staffid = 1
            self.dbA.setEnabled(False)
            aboutA.setEnabled(False)
        if 'stdfind' in self.options:
            self.w.pfindDd.setCurrentIndex(self.options['stdfind'])
        #    BUTTON CONNECTIONS
        self.w.errOk.clicked.connect(self.err_ok)
        self.w.sbynameRb.setChecked(1)
        self.w.sbydateRb.toggled.connect(self.list_pats)
        self.w.cancelPb.clicked.connect(self.close)
        #    INIT
        self.plistheader = [
            self.tr('Patient'),
            self.tr('Breed'),
            self.tr('Sex'),
            self.tr('Colour'),
            self.tr('Age'),
            self.tr('Last Seen'),
            self.tr('Client'),
            self.tr('Address'),
            self.tr('Location'),
            self.tr('Annotation'),
            self.tr('Registered'),
            ]
        self.w.mixedcolCb.setEnabled(0)
        self.w.sexDd.addItem('', 0)
        self.w.sexDd.addItem(self.tr('male'), 'm')
        self.w.sexDd.addItem(self.tr('female'), 'f')
        self.w.sexDd.addItem(self.tr('hermaphrodite'), 'h')
        self.w.sexDd.addItem(self.tr('not applicable'), 'n')
        try:
            self.curs = self.db.cursor()
        except (OperationalError, AttributeError) as e: # (no db connection)
            self.db_state(e)
            return
        if self.curs:
            self.dbA.setVisible(0)
            self.dbA.setEnabled(0)
            logname = querydb(self,
                              'select stf_logname from staff where stf_id=%s',
                              (self.staffid,))
            if logname is None:  return # db error
            logname = logname[0][0]
        self.w.lLb.setText(logname)
        self.popul_species()
        self.popul_breeds()
        self.popul_colours()
        self.popul_locs()
        self.popul_ins()
        self.today = date.today()
        #    WIDGET CONNECTIONS
        self.w.agespecDd.currentIndexChanged.connect(self.age_toggle)
        self.w.breedDd.currentIndexChanged.connect(self.adapt_colours)
        self.w.seenCb.stateChanged.connect(self.seencb)
        self.w.seenDe.setDate(self.today - timedelta(1))
        ch_conn(self, 'coldd', self.w.colDd.currentIndexChanged,
                self.adapt2colours)
        self.w.specDd.currentIndexChanged.connect(self.adapt_breeds)
        self.w.plist.doubleclicked.connect(self.w_pat)
        self.w.regspecDd.currentIndexChanged.connect(self.regde_toggle)
        self.w.detailedCb.stateChanged.connect(self.details_toggle)
        if not pid:
            self.w.regDe.setEnabled(False)
        #    COMPLETERS
        self.cwidgets = []
        for w in ('breedDd', 'cfnameLe', 'colDd', 'csnameLe', 'idLe', 'insDd',
                  'locDd', 'pnameLe', 'petpassLe', 'specDd'):
            self.cwidgets.append(getattr(self.w, w))
        #    LISTFILL lEs:
        self.get_pnames()
        self.get_cfnames()
        self.get_csnames()
        self.get_ppass()
        self.get_ids()
        self.gc = Gcompleter(parent=self.w.saeFr)
        QApplication.instance().focusChanged.connect(self.focuschange)
        #    FURTHER WIDGET CONNECTIONS
        self.w.ageSb.valueChanged.connect(self.adapt_dob)
        self.w.ageuDd.currentIndexChanged.connect(self.adapt_dob)
        self.w.dobDe.dateChanged.connect(self.adapt_age)
        #    FINISH
        self.keycheck = Keycheck(self)
        self.installEventFilter(self.keycheck)
        ch_conn(self, 'esc', self.keycheck.esc, self.close)
        self.age_toggle()
        if act == 's':
            self.prep_s()
        elif act == 'a':
            self.pat_add(cid)
        elif act == 'e':
            self.pat_edit(pid)

    def actions_enable(self, yes=True):
        """En- or Disable actions."""
        if not yes:
            yes = False
        else:
            yes = True
        self.newM.setEnabled(yes)
        self.newpatA.setEnabled(yes)
        self.newbreedA.setEnabled(yes)
        self.newspecA.setEnabled(yes)
        self.newcolA.setEnabled(yes)
        self.newlocA.setEnabled(yes)
        self.newinsA.setEnabled(yes)
        #self.w.secondPb.setEnabled(yes)
        #self.w.mainPb.setDefault(yes)
    
    def adapt2colours(self, idx):
        """Adapt breed/spec Dds to selection [idx] in colours.
        Triggered by colDd.currentIndexChanged."""
        self.w.mixedcolCb.setEnabled(idx > 1)
        if self.w.specDd.currentIndex()>0 or self.w.breedDd.currentIndex()>0:
            return
        if idx > 0:
            scode = querydb(
                self,
                'select c_speccode from colours where col_id=%s',
                (self.w.colDd.itemData(idx, 32).toInt()[0],))
            if scode is None:  return # db error
            scode = scode[0][0] # e.g.1048543, or 0
        else:
            ## scode = 'a'
            scode = ''
        self.breed2spec = {}
        self.w.breedDd.currentIndexChanged.disconnect(self.adapt_colours)
        self.w.breedDd.clear()
        self.w.breedDd.addItem('', 0)
        self.w.breedDd.currentIndexChanged.connect(self.adapt_colours)
        ## codestring = ''
        ## if scode != 'a':
        ##     codestring += self.curs.mogrify(
        ##         ' and spec_code in %s', (tuple('a' + scode),))
        if scode:
            scode = ' and bool({}&(1<<b_spec-1))'.format(scode)
        else:
            scode = ''
        blist = []
        res = querydb( # not even at gunpoint?  Ha!
            self,
            ## 'select distinct breed_id,breed_name,b_spec from breeds,species '
            ## 'where spec_id=b_spec{} order by breed_name'.format(codestring))
            # hierwei: do we need species and spec_id here?
            'select distinct breed_id,breed_name,b_spec from breeds,species '
            'where spec_id=b_spec{} order by breed_name'.format(scode))
        if res is None:  return # db error
        for e in res:
            self.w.breedDd.addItem(e[1], e[0])
            blist.append(e[1])
            self.breed2spec[e[0]] = e[2]
        self.w.breedDd.list = blist

    def adapt_age(self):
        """Adapt ageDd to changes in dobDe."""
        if self.w.ageSb.hasFocus() or self.w.ageuDd.hasFocus():
            return
        age = self.w.dobDe.date().daysTo(self.today)
        if not age:
            return
        if age/365 > 1: # years #  and age%365 < 183
            self.w.ageuDd.setCurrentIndex(0)
            self.w.ageSb.setValue(age/365)
        elif age/30 > 1: # months
            self.w.ageuDd.setCurrentIndex(1)
            self.w.ageSb.setValue(age/30)
        elif age/7 > 1:  # weeks
            self.w.ageuDd.setCurrentIndex(2)
            self.w.ageSb.setValue(age/7)
        else:            # days
            self.w.ageuDd.setCurrentIndex(3)
            self.w.ageSb.setValue(age)
    
    def adapt_breeds(self, idx):
        """Adapt breedDd to spec change/breed addition.
        Triggered by specDd.activated, called by set_addedspec."""
        bdx = 0
        self.w.breedDd.currentIndexChanged.disconnect(self.adapt_colours)
        if idx:
            res = querydb(
                self,
                'select breed_id,breed_name,b_spec from breeds where '
                'b_spec=%s order by breed_name',
                (self.w.specDd.itemData(idx, 32).toInt()[0],))
        else:
            res = querydb(
                self,
                'select breed_id,breed_name,b_spec from breeds order by '
                'breed_name')
        if res is None:  return # db error
        self.breed2spec = {}
        blist = []
        bdx = self.w.breedDd.itemData(self.w.breedDd.currentIndex(), 32)
        self.w.breedDd.clear()
        self.w.breedDd.addItem('', 0)
        for e in res:
            self.w.breedDd.addItem(e[1], e[0])
            blist.append(e[1])
            self.breed2spec[e[0]] = e[2]
        self.w.breedDd.list = blist
        self.w.breedDd.setCurrentIndex(self.w.breedDd.findData(bdx, 32))
        self.adapt_colours(self.w.breedDd.currentIndex())
        self.w.breedDd.currentIndexChanged.connect(self.adapt_colours)

    def adapt_colours(self, idx=0):
        """Adapt colours to species chosen by selecting breed.  Triggered by
        breedDd.cIC [pat_edit]. Called by set_addedbreed."""
        if idx == -1:  return
        if idx:
            self.currentspec = self.breed2spec[
                self.w.breedDd.itemData(idx, 32).toInt()[0]]
        else:
            self.currentspec = 0
        self.popul_colours()

    def adapt_dob(self):
        """Adapt dob edit to changes in age selection things."""
        if not (self.w.ageSb.hasFocus() or self.w.ageuDd.hasFocus()):
            return
        self.today = date.today()
        t = self.w.ageuDd.currentIndex()
        if t == 1:   # months
            self.w.dobDe.setDate(
                self.today - timedelta(self.w.ageSb.value()*30))
        elif t == 2: # weeks
            self.w.dobDe.setDate(
                self.today - timedelta(self.w.ageSb.value()*7))
        elif t == 3: # days
            self.w.dobDe.setDate(
                self.today - timedelta(self.w.ageSb.value()))
        else:        # years, t should be 0 here
            self.w.dobDe.setDate(
                self.today - timedelta(self.w.ageSb.value()*365))

    def add_basecol(self):
        """Add a new base colour to the db."""
        if self.db_err:
            return
        if not hasattr(self, 'aebc'):
            import aebasecol
            self.aebc = aebasecol.Aebc(self)
            self.aebc.move(self.x()+237, self.y()+78) # self.x ?
        self.aebc.show()
        self.adding = True
        self.await_adding()
        ## self.aebc.addedbc.connect(self.addedbc) # signal(pyobj)
        ## self.aebc.nocc.connect(self.nocc) # signal(pyobj)

    def add_breed(self):
        """Add a new breed to the db."""
        if self.db_err:
            return
        if not hasattr(self, 'aebr'):
            import aebreed
            self.aebr = aebreed.Aebreed(self)
            self.aebr.move(self.x()+237, self.y()+158)
        self.aebr.show()
        self.adding = True
        self.await_adding()
        ## self.aebr.addedbreed.connect(self.set_addedbreed)

    def add_col(self):
        """Add a new colour to the db."""
        if self.db_err:
            return
        if not hasattr(self, 'aec'):
            import aecol
            self.aec = aecol.Aecol(self)
            self.aec.move(self.x()+237, self.y()+78)
        self.aec.show()
        self.adding = True
        self.await_adding()
        ## aec.addedcol.connect(self.set_addedcol)
        ## self.addedbc.connect(aec.update_cols)
        ## self.nocc.connect(aec.noc_c)

    def add_ins(self):
        """Add a new insurance to the db."""
        if self.db_err:
            return
        if not hasattr(self, 'aei'):
            import aeins
            self.aei = aeins.Aeins(self)
            self.aei.move(self.x()+127, self.y()+128)
        self.aei.show()
        self.adding = True
        self.await_adding()
        ## aei.addedins.connect(self.addedins)

    def add_loc(self):
        """Add a new location (stable, kennels, etc.) to the db."""
        if self.db_err:
            return
        if not hasattr(self, 'ael'):
            import aeloc
            self.ael = aeloc.Aeloc(self)
            self.ael.move(self.x()+128, self.y()+128)
        self.ael.show()
        self.adding = True
        self.await_adding()
        ## ael.addedloc.connect(self.set_addedloc)

    def add_spec(self): # hierwei: move this into aespec
        """Add a new 'species' to the db."""
        if self.db_err:
            return
        if not hasattr(self, 'aesp'):
            import aespec
            self.aesp = aespec.Aespec(self)
            self.aesp.move(self.x()+237, self.y()+78)
        self.aesp.show()
        self.adding = True
        self.await_adding()

    def ae_connect(self):
        """Set connections for add-edit."""
        ch_conn(self, 'enter', self.keycheck.enter, self.w.mainPb.click)
        # next line new 120521:
        ch_conn(self, 'mainpb', self.w.mainPb.clicked, self.pat_addck)
        self.w.neutdateRb.toggled.connect(self.neutde_toggle)

    def age_toggle(self, state=0):
        """Dis-Enable age-related inputs according to agespecDd."""
        # hierwei: add agesuDd/Lb check dobestCb re visibility!
        self.w.ageSb.setEnabled(state)
        self.w.ageLb.setEnabled(state)
        self.w.ageuDd.setEnabled(state)
        self.w.ageuLb.setEnabled(state)
        if self.w.dobestCb.isVisible():
            self.w.dobestCb.setEnabled(state)
        else:
            self.w.agesuDd.setEnabled(state)
            self.w.agesuLb.setEnabled(state)
        self.w.dobDe.setEnabled(state)
        self.w.dobLb.setEnabled(state)

    def await_adding(self):
        """Disable all user interaction -- while one interaction is going on."""
        self.actions_enable(False)
        self.w.saeFr.setEnabled(0)
        self.w.buttonBox.setEnabled(0)

    def changed(self):
        """Prevent insufficient data sets from being saved on adding patient."""
        self.minc = 3 # option this?  hierwei
        self.changes = 0
        for le in (self.w.pnameLe, self.w.idLe):
            if le.text():
                self.changes += 1
        for dd in (self.w.colDd, self.w.breedDd, self.w.sexDd, self.w.locDd,
                   self.w.insDd):
            if dd.currentIndex() > 0:
                self.changes += 1
        if self.w.annoTe.toPlainText().toLatin1():
            self.changes += 1
        if self.w.dobDe.date() != self.initdob:
            self.changes += 1
        if self.changes < (self.minc):
            self.w.mainPb.setToolTip(
                self.tr('There have to be at least ') +
                str(self.minc) +
                self.tr('entries to save a patient.'))
            self.w.mainPb.setEnabled(0)
        else:
            self.w.mainPb.setToolTip('')
            self.w.mainPb.setEnabled(1)

    def ck_neutdate(self, pid, neutdu=False, ndate=''):
        """Update or insert neutering date for pid on saving."""
        # only called from pat_save
        ndat = querydb(
            self,
            'select neut_id,neut_date from neuts where neut_id=%s', (pid,))
        if ndat is None:  return # db error
        if len(ndat):
            suc = querydb(
                self,
                'update neuts set neut_date=%s where neut_id=%s returning '
                'neut_id', (not neutdu and ndate or None, pid))
        else:
            suc = querydb(
                self,
                'insert into neuts(neut_id,neut_date)values(%s, %s)'
                'returning neut_id', (pid, not neutdu and ndate or None))
        if suc is None:  return # db error
        self.db.commit()

    def cli_change(self):
        """Change owner of edited patient."""
        print('saepat.cli_change: nyi')
    
    def closeEvent(self, ev): # hierwei: devel
        ## if self.unsaved:
        ##     self.state_write()
        if self.gaia and hasattr(self.gaia, 'xy_decr'):
            self.gaia.xy_decr()
        
    def db_state(self, db=None): # hierwei ck vs gaia from gnuv.py
        """Actions to be taken on db loss and gain."""
        errmsg = ''
        if isinstance(db, str):
            errmsg = db
            db = None
        self.db_err = not db
        self.w.no_dbconn.setVisible(self.db_err)
        self.dbA.setVisible(self.db_err)
        self.dbA.setEnabled(self.db_err)
        ##self.dbstate.emit(not self.db_err) # c'd 141120 shb done by gaia
        self.actions_enable(not self.db_err)
        if not errmsg:
            self.db = db
            try:
                self.curs = db.cursor()
            except (OperationalError, AttributeError) as e:
                if not hasattr(self, 'warning'):
                    from warn import Warning
                    self.warning = Warning(self, self.tr('Db Error'), e)
                else:
                    self.warning.showmsg('Db Error', e)
                    self.warning.raise_()
        
    def details_toggle(self, state):
        """Toggle between detailed and short search view."""
        if state:
            self.w.idLb.show()
            self.w.idLe.show()
            self.w.petpassLb.show()
            self.w.petpassLe.show()
            self.w.xbredCb.show()
            self.w.colDd.show()
            self.w.colLb.show()
            self.w.mixedcolCb.show()
            self.w.seenCb.show()
            self.w.seenDe.show()
            self.w.neuteredCb.show()
            self.w.agespecDd.show()
            self.w.agespecLb.show()
            self.w.ageSb.show()
            self.w.ageLb.show()
            self.w.ageuDd.show()
            self.w.ageuLb.show()
            self.w.dobDe.show()
            self.w.dobLb.show()
            self.w.agesuDd.show()
            self.w.agesuLb.show()
            self.w.locDd.show()
            self.w.locLb.show()
            self.w.viciousCb.show()
            self.w.regDe.show()
            self.w.regLb.show()
            self.w.regspecDd.show()
            self.w.regspecLb.show()
            self.w.insDd.show()
            self.w.insLb.show()
            self.w.annoTe.show()
            self.w.annoLb.show()
        else:
            self.w.idLb.hide()
            self.w.idLe.hide()
            self.w.petpassLb.hide()
            self.w.petpassLe.hide()
            self.w.xbredCb.hide()
            self.w.colDd.hide()
            self.w.colLb.hide()
            self.w.mixedcolCb.hide()
            self.w.seenCb.hide()
            self.w.seenDe.hide()
            self.w.neuteredCb.hide()
            self.w.agespecDd.hide()
            self.w.agespecLb.hide()
            self.w.ageSb.hide()
            self.w.ageLb.hide()
            self.w.ageuDd.hide()
            self.w.ageuLb.hide()
            self.w.dobDe.hide()
            self.w.dobLb.hide()
            self.w.agesuDd.hide()
            self.w.agesuLb.hide()
            self.w.annoTe.hide()
            self.w.annoLb.hide()
            self.w.locDd.hide()
            self.w.locLb.hide()
            self.w.viciousCb.hide()
            self.w.regDe.hide()
            self.w.regLb.hide()
            self.w.regspecDd.hide()
            self.w.regspecLb.hide()
            self.w.insDd.hide()
            self.w.insLb.hide()
        
    def dob_edited(self):
        """Check that dob (of new patient) has been set."""
        self.dobedited = True

    def err_ok(self):
        self.w.errFr.hide()

    def error_msg(self, err_msg=''): # obsolete? ck gaia re dberror
        """Display error message in errFr when: db-error or pat_exists."""
        self.w.saeFr.setEnabled(0)
        self.w.errLb.setText(self.tr(err_msg))
        ch_conn(self, 'enter', self.keycheck.enter, self.w.backPb.click)
        ch_conn(self, 'backpb')#, self.w.backPb.clicked)
        self.w.mainPb.setEnabled(0)
        self.w.mainPb.setDefault(0)
        self.w.mainPb.setAutoDefault(0)
        self.w.backPb.setDefault(1)
        self.w.backPb.setAutoDefault(1)
        self.w.backPb.setEnabled(1)
        self.w.backPb.show()
        self.w.errFr.show()

    def filltable(self, res):
        """Fill plist, res is one table row."""
        if res[15] in self.pids: # p_id already in table
            return
        self.pids.append(res[15])
        self.cids.append(res[16]) # scrap this rather get c_id anew from db?
        # tfields:
        # 0 p_name  1 breed_abbr  2 sex  3 colour  4 age  5 last_seen
        # 6 c_name  7 c_addr  8 l_name  9 p_anno  [10 p_reg]
        # qfields:
        # 0 p_name  1 breed_abbr  2 xbreed  3 sex  4 neutd  5:8 colour
        # 8:10 cname  10 caddrid  11:14 address  14 location  15 pid  16 cid
        # 17 p_anno  18 breed_name  19 dob  20 rip  21 p_last  [22 p_reg]
        data = []
        data.extend([res[0],
                     res[1]+(res[2] and '-X' or ''),
                     res[3]+(res[4] is None and '-n?' or res[4] and '-n' or ''),
                     '-'.join([e for e in res[5:8] if e]),
                     self.pat_age(res[19], res[20]),
                     res[21].strftime("%d.%m.%y %H:%M"),
                     ' '.join([e for e in res[8:10] if e]),
                     ', '.join([e for e in res[11:14] if e]),
                     res[14],
                     len(res[17]) > 19 and res[17][:18] + '...' or res[17],
                     ])
        if len(res) > 22 and self.w.regDe.isEnabled():
            data.append(res[22].strftime("%d.%m.%y %H:%M")) # p_reg 12
        else:
            data.append('')
        self.w.plist.append_row(data)
        if len(self.nch) and res[15] in self.nch:
            self.w.plist.cell(len(self.w.plist.lrows)-1, 0).setToolTip(
                self.tr('was') + ' ' + self.nch[data[10]]['name'] + ' ' +
                self.tr('until') + ' ' + self.nch[data[10]]['date'])
        if len(res[17]) > 19:
            self.w.plist.cell(len(self.w.plist.lrows)-1, 9).setToolTip(res[17])
        self.w.plist.cell(len(self.w.plist.lrows)-1, 1).setToolTip(
            res[18]) # breed

    def focuschange(self, old, new):
        if new in self.cwidgets:
            self.gc.setwidget(old=old, new=new, l=new.list)
    
    def get_cfnames(self):
        res = querydb(self,
                      'select distinct c_fname from clients order by c_fname')
        if res is None:  return # db error
        self.w.cfnameLe.list = [e[0] for e in res]
    
    def get_csnames(self):
        res = querydb(self,
                      'select distinct c_sname from clients order by c_sname')
        if res is None:  return # db error
        self.w.csnameLe.list = [e[0] for e in res]

    def get_ids(self):
        res = querydb(
            self,
            'select distinct identno from patients where identno is not null '
            'order by identno')
        if res is None:  return # db error
        self.w.idLe.list = [e[0] for e in res]
        
    def get_pnames(self):
        res = querydb(self,
                      'select distinct p_name from patients order by p_name')
        if res is None:  return # db error
        self.w.pnameLe.list = [e[0] for e in res]

    def get_ppass(self):
        res = querydb(
            self,
            'select distinct petpass from patients where petpass is not null '
            'order by petpass')
        if res is None:  return # db error
        self.w.petpassLe.list = [e[0] for e in res]

    def gv_quit(self, quitnow=False): # hierwei: cave action.checked=False
        """Signal children if quitting GnuVet or not.  Add self.shutdown?"""
        self.gvquit.emit(quitnow)
        if quitnow:
            self.close()

    def gv_quitconfirm(self): # hierwei devel
        if self.gaia:
            self.gaia.gv_quitconfirm()
        else:
            exit()

    def help_self(self):
        """Launch help window with help on saepat."""
        if self.w.saeFr.isVisible():
            if self.act == 'e':
                self.helpsig.emit('patedad.html')
            else:
                self.helpsig.emit('patsearch.html#search')
        elif self.w.noMFr.isVisible():
            self.helpsig.emit('patsearch.html#nomatches')
        elif self.w.matchFr.isVisible():
            self.helpsig.emit('patsearch.html#matches')

    def list_pats(self):
        """Build list of patients matching seach criteria."""
        if self.w.sbynameRb.isChecked():
            s_byname = True
        else:
            s_byname = False
        ch_conn(self, 'selch')
        self.w.plist.clear()
        if not self.w.plist.headers:
            self.w.plist.set_headers(self.plistheader)
        querytext = self.query_string(s_byname)
        result = querydb(self, querytext)
        if result is None:  return # db error
        self.pids = []
        self.cids = []
        finds = None
        for res in result:
            self.filltable(res)
            finds = True
        if (querytext.count("p_name ilike'") and
            not querytext.count("p_name ilike'%")):
            querytext = querytext.replace("p_name ilike'", "p_name ilike'%")
            result = querydb(self, querytext)
            if result is None:  return # db error
            for res in result:
                self.filltable(res)
                finds = True
        if finds:
            self.match_list(s_byname)
        else:
            self.no_matches()

    def match_list(self, s_byname=True):
        """Set widgets to states for successful search."""
        # check resize things!
        self.act = 'l' # was 2
        # mklabel for 'Searching patients seen ... [date]'
        if (self.width()-self.w.matchFr.width() > 20 or
                self.height()-self.w.matchFr.height() > 135):
            self.w.matchFr.resize(self.width()-20, self.height()-135)
            self.w.plist.resize(self.width()-20, self.height()-171)
            self.w.buttonBox.move(self.w.buttonBox.x()+(self.width()-870)/2,
                                   self.w.buttonBox.y()+(self.height()-626))
        matchtxt = (str(len(self.w.plist.lrows)) + # hierwei plural
                    self.tr(' match') +
                    (len(self.w.plist.lrows) != 1 and self.tr('es') or ''))
        if not self.w.seenCb.isHidden() and self.w.seenCb.isChecked():
            matchtxt += (self.tr(' seen: ') +
                         self.w.seenDe.date().toString('d.M.yyyy'))
        self.w.matchnLb.setText(matchtxt)
        self.w.saeFr.hide()
        self.w.noMFr.hide()
        self.w.plist.cols2contents()
        if s_byname:
            self.w.plist.col_hide(5) # last_seen
        else:
            self.w.plist.col_show(5)
        if self.w.regDe.isEnabled():
            self.w.plist.col_show(10) # p_reg
        else:
            self.w.plist.col_hide(10)
        self.actions_enable(False)
        self.w.secondPb.setEnabled(0)
        self.newM.setEnabled(0)
        self.w.backPb.setDefault(0)
        self.w.backPb.setAutoDefault(0)
        self.w.backPb.setEnabled(1)
        self.w.backPb.show()
        self.w.mainPb.setDefault(1)
        self.w.mainPb.setAutoDefault(1)
        self.w.mainPb.setText(self.tr('select &Patient'))
        self.w.secondPb.setEnabled(1)
        self.w.secondPb.setText(self.tr('select C&lient'))
        self.w.plist.installEventFilter(self.keycheck)
        ch_conn(self, 'enter', self.keycheck.enter, self.w.mainPb.click)
        ch_conn(self, 'backpb', self.w.backPb.clicked, self.prep_s)
        ch_conn(self, 'mainpb', self.w.mainPb.clicked, self.w_pat)
        ch_conn(self, '2ndpb', self.w.secondPb.clicked, self.w_cli)
        ch_conn(self, 'selch', self.w.plist.rowchanged, self.trackrow)
        self.w.plist.select_row(row=0)
        self.w.plist.setFocus()
        self.w.matchFr.show()

    def mixedcol_search(self):
        """Construct tuple for colour combination query part."""
        colours = []
        cols = querydb(
            self,
            'select col1,col2,col3 from colours where col_id=%s',
            (self.w.colDd.itemData(
                self.w.colDd.currentIndex(), 32).toInt()[0],))
        if cols is None:  return # db error
        (col1, col2, col3) = cols[0]
        scols = []
        for colour in (col1, col2, col3):
            if not colour == 1:
                scols.append(colour)
        if len(scols) == 1:
            qs = self.curs.mogrify(
                'select col_id from colours where col1=%s or col2=%s or '
                'col3=%s', (scols[0], scols[0], scols[0]))
        elif len(scols) == 2:
            qs = self.curs.mogrify(
                'select col_id from colours where'
                '(col1=%s and(col2=%s or col3=%s))or'
                '(col2=%s and(col1=%s or col3=%s))or'
                '(col3=%s and(col1=%s or col2=%s))', (
                    scols[0], scols[1], scols[1],
                    scols[0], scols[1], scols[1],
                    scols[0], scols[1], scols[1]))
        elif len(scols) == 3:
            qs = self.curs.mogrify(
                'select col_id from colours where'
                '(col1=%s and'
                '((col2=%s and col3=%s)or(col3=%s and col2=%s)))or'
                '(col2=%s and'
                '((col1=%s and col3=%s)or(col3=%s and col1=%s)))or'
                '(col3=%s and'
                '((col1=%s and col2=%s)or(col2=%s and col1=%s)))', (
                    scols[0], scols[1], scols[2],
                    scols[0], scols[1], scols[2],
                    scols[0], scols[1], scols[2],
                    scols[0], scols[1], scols[2],
                    scols[0], scols[1], scols[2]))
        res = querydb(self, qs)
        if res is None:  return # db error
        for e in res:
            colours.append(e[0])
        return tuple(colours)
            
    def neutde_toggle(self, checked=False):
        if checked:
            self.w.neutDe.setEnabled(1)
            self.w.neutDe.setMaximumDate(self.today)
        else:
            self.w.neutDe.setEnabled(0)

    def no_matches(self):
        # change: no q to add if not enough data entered?
        self.act = 'n' # was 1
        self.w.saeFr.hide()
        self.w.matchFr.hide()
        ch_conn(self, 'mainpb', self.w.mainPb.clicked, self.pat_act)
        ch_conn(self, 'backpb', self.w.backPb.clicked, self.prep_s)
        ch_conn(self, 'enter', self.keycheck.enter, self.w.backPb.click)
        if self.w.seenCb.isChecked():
            self.w.noMLb.setText(
                self.tr('No matches found searching for date ') +
                self.w.seenDe.date().toString('d.M.yy'))
        else:
            self.w.noMLb.setText(self.tr(
                'No matching patient entries found!<br><br>'
                'Do you want to register a new account with your entries?'))
            self.w.mainPb.setText(self.tr('New &Account'))
        self.w.mainPb.setDefault(0)
        self.w.mainPb.setAutoDefault(0)
        self.w.secondPb.setEnabled(0)
        self.w.secondPb.hide()
        self.w.backPb.setEnabled(1)
        self.w.backPb.setDefault(1)
        self.w.backPb.setAutoDefault(1)
        self.w.backPb.show()
        self.w.noMFr.show()

    def pat_act(self, trg=0): # trg: triggered(checked=False)
        """Wrapper for action signal."""
        self.pat_add()

    def pat_add(self, cid=0):
        """Add a new patient to the db."""
        self.cid = cid
        self.act = 'a'
        self.setWindowTitle('GnuVet: ' + self.tr('Add Patient'))
        self.prep_ae()
        if self.w.neuteredCb.isChecked():
            self.w.neutduRb.setChecked(1)
        if not self.w.agespecDd.currentIndex():
            self.w.dobDe.setDate(self.today - timedelta(56))
        if self.options['dobwarn']:
            self.dobedited = False
            self.w.dobDe.dateChanged.connect(self.dob_edited)
        self.w.regDe.setDate(self.today)
        if self.w.pnameLe.text():
            self.w.pnameLe.setText(' '.join(
                [p.capitalize() for p in
                 str(self.w.pnameLe.text().toLatin1()).split()]))
            self.w.mainPb.setEnabled(1)
        else:
            self.w.mainPb.setEnabled(0)
        if self.cid:
            if not self.set_cname():
                self.w.clientLb.setText(self.tr('Client unassigned'))
                return
        self.w.csnameLb.hide()
        self.clichangeA.setVisible(1)
        self.clichangeA.setEnabled(1)
        self.w.seenCb.hide()
        self.w.seenDe.hide()
        self.ae_connect()
        # disconnect all this stuff after finishing?
        # rather check after save_click or so?
        self.w.idLe.textEdited.connect(self.changed)
        self.w.pnameLe.textEdited.connect(self.changed)
        self.w.breedDd.currentIndexChanged.connect(self.changed)
        self.w.xbredCb.stateChanged.connect(self.changed)
        self.w.colDd.currentIndexChanged.connect(self.changed)
        self.w.sexDd.currentIndexChanged.connect(self.changed)
        self.w.neutnoRb.clicked.connect(self.changed)
        self.w.neutunRb.clicked.connect(self.changed)
        self.w.neutduRb.clicked.connect(self.changed)
        self.w.neutdateRb.clicked.connect(self.changed)
        self.w.neutDe.dateChanged.connect(self.changed)
        self.w.dobDe.dateChanged.connect(self.changed)
        self.w.locDd.currentIndexChanged.connect(self.changed)
        self.w.ripCb.stateChanged.connect(self.changed)
        self.w.viciousCb.stateChanged.connect(self.changed)
        self.w.insDd.currentIndexChanged.connect(self.changed)
        self.w.regDe.dateChanged.connect(self.changed)
        self.w.annoTe.textChanged.connect(self.changed)
        self.w.backPb.setAutoDefault(0)
        self.w.backPb.setDefault(0)
        ## if self.sender: # called from other window # hierwei No sender!
        ##     self.w.backPb.hide()
        ##     self.w.backPb.setEnabled(0)
        ## else:
        ##     self.w.backPb.setEnabled(1)
        ##     self.w.backPb.show()
        self.w.mainPb.setText(self.tr('&Save'))
        ch_conn(self, 'backpb', self.w.backPb.clicked, self.prep_s)
        if not self.w.pnameLe.text():
            self.w.pnameLe.setFocus()
        self.w.saeFr.show()

    def pat_addck(self):
        """Sanity checks on input."""
        # Does patient have a name?
        if not self.w.pnameLe.text():
            self.pat_addck_noname()
            return
        # Does the given id already exist (Tattoo!)?
        if self.w.idLe.text() and not self.idok:
            res = querydb(self, 'select p_id from patients where identno=%s',
                          (str(self.w.idLe.text().toLatin1()),))
            if res is None:  return # db error
            if res and res[0][0] != self.pid:
                self.w.errFr.show()
                self.w.errLb.setText(
                    self.tr('There is a different Patient with the ID ') +
                    self.w.idLe.text().toLatin1() + self.tr('!\nSave anyway?'))
                ch_conn(self, 'errok',
                        self.w.errOk.clicked, self.pat_addck_did)
            return
        # Is the dob OK?
        if not self.dobedited:
            self.w.errFr.show()
            self.w.errLb.setText(self.tr(
                "You haven't changed the date of birth.  Is it OK?"))
            ch_conn(self, 'errok', self.w.errOk.clicked, self.pat_addck_dob)
        # Is the client identified?  registered?
        clis = []
        if not self.cid:
            if self.w.csnameLe.text() or self.w.cfnameLe.text():
                if self.w.csnameLe.text() and self.w.cfnameLe.text():
                    res = querydb(
                        self,
                        'select c_id from clients where c_sname ilike %s '
                        'and c_fname ilike %s',
                        (str(self.w.csnameLe.text().toLatin1()) + '%',
                         str(self.w.cfnameLe.text().toLatin1()) + '%'))
                elif self.w.csnameLe.text():
                    res = querydb(
                        self,
                        'select c_id from clients where c_sname ilike %s',
                        (str(self.w.csnameLe.text().toLatin1()) + '%',))
                else:
                    res = querydb(
                        self,
                        'select c_id from clients where c_fname ilike %s',
                        (str(self.w.cfnameLe.text().toLatin1()) + '%',))
                if res is None:  return # db error
                if len(res) == 1:
                    self.cid = res[0][0]
                elif len(res):
                    clis = [e[0] for e in result]
        else:
            if not self.set_cname():
                self.w.clientLb.setText(self.tr('Client unassigned'))
                return
        if not self.cid: # hierwei c_id und signal?
            self.gaia.cid.connect(self.pat_addsetcli) # ? parent!
            self.needcid.connect(self.gaia.sae_cli)
            self.w.saeFr.setEnabled(0)
            if len(clis):
                self.needcid.emit(('c', self, clis))
            else:
                self.needcid.emit(('c', self))
            self.needcid.disconnect(self.gaia.sae_cli)
            return
        # Does this client have a(nother) living patient of same name?
        print('double name check')
        if not self.nameok:
            print('not nameok')
            # hierwei
            if self.act == 'e':
                res = querydb(
                    self,
                    'select p_id from patients where p_name=%s and p_cid='
                    '%s and not rip and p_id!=%s',
                    (str(self.w.pnameLe.text().toLatin1()),
                     self.cid, self.pid))
            else:
                res = querydb(
                    self,
                    'select p_id from patients where p_name=%s and p_cid='
                    '%s and not rip',
                    (str(self.w.pnameLe.text().toLatin1()), self.cid))
            if res is None:  return # db error
            if res:
                self.w.errFr.show()
                self.w.errLb.setText(
                    self.tr('There is already a Patient named ') + '<b>' +
                    self.w.pnameLe.text().toLatin1() + '</b>' +
                    self.tr('registered on this client\'s account.') + '<br>' +
                    self.tr('Please confirm to ') +
                    self.act=='e' and self.tr('save this further') or
                    self.tr('register this new') +
                    self.tr('Patient of the same name.'))
                ch_conn(self, 'errok',
                        self.w.errOk.clicked, self.pat_addck_name)
                return
        print('checks finished')
        self.pat_save()

    def pat_addck_did(self):
        """Check reaction to pre-existing ident no."""
        self.w.errFr.hide()
        self.idok = True
        ch_conn(self, 'errok', self.w.errOk.clicked, self.pat_addck_did)
        self.w.idLe.textEdited.connect(self.pat_addck_idok)
        self.w.idLe.setFocus()

    def pat_addck_dob(self):
        self.w.errFr.hide()
        self.dobedited = True
        ch_conn(self, 'errok')#, self.w.errOk.clicked)
        self.w.dobDe.setFocus()

    def pat_addck_idok(self):
        """Reset boolean check value if id# changed."""
        self.w.idLe.textEdited.disconnect(self.pat_addck_idok)
        self.idok = False
        
    def pat_addck_noname(self): # hierwei
        """Ascertain that patient has a name."""
        self.w.errFr.show()
        self.w.errLb.setText(self.tr(
            'A patient has to have a name.  If the name is unknown, please '
            "use an appropriate pseudonym such as 'nn'."))
        ch_conn(self, 'errok', self.w.errOk.clicked, self.pat_addck_nonameok)

    def pat_addck_nonameok(self):
        """Patient has a name."""
        self.w.errFr.hide()
        ch_conn(self, 'errok')#, self.w.errOk.clicked)
            
    def pat_addck_name(self):
        """Check reaction to double name."""
        self.w.errFr.hide()
        self.nameok = True
        ch_conn(self, 'errok')#, self.w.errOk.clicked)
        self.w.pnameLe.textEdited.connect(self.pat_addck_nameok)
        self.w.pnameLe.setFocus()

    def pat_addck_nameok(self):
        """Reset boolean check value if pname changed."""
        self.w.pnameLe.textEdited.disconnect(self.pat_addck_name)
        self.nameok = False

    def pat_addsetcli(self, args):
        """Set client id from cid signal."""
        self.w.saeFr.setEnabled(1)
        if len(args) > 1:
            sender = args[1]
            if sender != self:
                print('sender not me, returning') # hierwei sender unsinn
                return
        if len(args):
            self.cid = args[0]
        self.pat_addck()

    def pat_age(self, p_dob='', rip=False):
        """Calculate patient age from p_dob (ignoring leap years)."""
        if rip:
            return '+'
        if not p_dob:
            return ''
        self.today = date.today()
        days = (self.today - p_dob).days
        years = int(days/365)
        days  = days%365
        leaps = int(years/4)
        days -= leaps
        if days > 359:
            months = 11
        else:
            months = int(days/30)
        days  = days%30
        weeks = int(days/7)
        days  = days%7
        return ((years and (str(years) + self.tr(' a ')) or '') +
                (months and (str(months) + self.tr(' m')) or '') +
                ((weeks and not years) and
                 '{}{} weeks'.format(months and ' ' or '', weeks) or ''))

    def pat_edit(self, pid=0):
        """Edit patient, pid signalled from parent."""
        # Check breedDd.cIC.connected (self.adapt_colours)
        # check startv and self.startv ???
        self.act = 'e'
        startv = {}
        self.prep_ae()
        self.setWindowTitle('GnuVet: ' + self.tr('Edit Patient'))
        res = querydb(
            self,
            'select p_name,breed,xbreed,colour,sex,neutd,vicious,rip,identno,'
            'petpass,p_anno,dob,dobest,loc,p_reg,ins,p_last,chr,c_id,c_surname,'
            'c_forename from patients,clients where p_cid=c_id and p_id=%s',
            (pid,))
        if res is None:  return # db error
        if res:
            startv['name'] = res[0]
            startv['breed'] = res[1]
            startv['xbred'] = res[2]
            startv['colour'] = res[3]
            startv['sex'] = res[4]
            startv['neutd'] = res[5]
            startv['vicious'] = res[6]
            startv['rip'] = res[7]
            startv['ident'] = res[8]
            startv['petpass'] = res[9]
            startv['p_anno'] = res[10]
            startv['dob'] = res[11]
            startv['dobest'] = res[12]
            startv['loc'] = res[13]
            startv['p_reg'] = res[14]
            startv['insur'] = res[15]
            startv['p_last'] = res[16]
            startv['chron'] = res[17]
            startv['cid'] = res[18]
            startv['csname'] = res[19]
            startv['cfname'] = res[20]
        if startv['neutd']:
            res = querydb(
                self,
                'select neut_date from neuts where neut_id=%s', (pid,))
            if res is None:  return # db error
            startv['neutdate'] = res[0][0]
        if self.startv:
            self.w.pnameLe.setText(self.startv['pname'])
            self.w.breedDd.setCurrentIndex(
                self.w.breedDd.findData(self.startv['breed'], 32))
            self.w.xbredCb.setChecked(self.startv['xbred'])
            self.w.dobDe.setDate(self.startv['dob'])
            self.w.dobestCb.setChecked(self.startv['dobest'])
            self.w.colDd.setCurrentIndex(
                self.w.colDd.findData(self.startv['col'], 32))
            self.w.sexDd.setCurrentIndex(
                self.w.sexDd.findData(startv['sex'], 0))
            self.w.ripCb.setChecked(self.startv['rip'])
            self.w.viciousCb.setChecked(self.startv['vicious'])
            self.w.idLe.setText(startv['id'])
            self.w.regDe.setDate(self.startv['reg'])
            self.w.annoTe.setPlainText(self.startv['anno'])
            self.w.locDd.setCurrentIndex(
                self.w.locDd.findData(self.startv['loc'], 32))
            self.w.insDd.setCurrentIndex(
                self.w.insDd.findData(self.startv['ins'], 32))
            if startv['neut']:
                if startv['ndate']:
                    self.w.neutdateRb.setChecked(1)
                    self.w.neutdateDe.setDate(startv['ndate'])
                else:
                    self.w.neutduRb.setChecked(1)
            elif startv['neut'] is None:
                self.w.neutunRb.setChecked(1)
            else:
                self.w.neutnoRb.setChecked(1)
        else:
            result = querydb(
                self,
                'select p_name,breed,xbreed,dob,dobest,colour,sex,neutd,'
                'vicious,identno,p_reg,p_anno,loc,ins,rip,t_title,c_sname,'
                'c_mname,c_fname from patients,clients,titles where p_id=%s '
                'and p_cid=c_id and c_title=t_id', (self.pid,))
            if result is None:  return # db error
            res = result[0]
            self.w.pnameLe.setText(res[0])
            self.w.breedDd.setCurrentIndex(
                self.w.breedDd.findData(res[1], 32))
            self.w.xbredCb.setChecked(res[2])
            self.w.dobDe.setDate(res[3])
            self.adapt_age()
            self.w.dobestCb.setChecked(res[4])
            self.w.colDd.setCurrentIndex(
                self.w.colDd.findData(res[5], 32))
            self.w.sexDd.setCurrentIndex(
                self.w.sexDd.findData(res[6], 32))
            neut = res[7]
            self.w.viciousCb.setChecked(res[8])
            self.w.idLe.setText(res[9])
            if not res[10]:
                self.w.regDe.setDate(self.today)
            else:
                self.w.regDe.setDate(res[10])
            self.w.annoTe.setPlainText(res[11])
            self.w.locDd.setCurrentIndex(
                self.w.locDd.findData(res[12], 32))
            self.w.insDd.setCurrentIndex(
                self.w.insDd.findData(res[13], 32))
            self.w.ripCb.setChecked(res[14])
            tmp = (res[15],
                   ','.join([e for e in res[16:18] if (e or res[18])]),
                   res[18])
            tmp = ' '.join([e for e in tmp if e])
            self.w.clientLb.setText(tmp)
            startv['pname'] = res[0]
            startv['breed'] = res[1]
            startv['xbred'] = res[2]
            startv['dob'] = res[3]
            startv['dobest'] = res[4]
            startv['col'] = res[5]
            startv['sex'] = res[6]
            startv['neut'] = res[7]
            startv['vicious'] = res[8]
            startv['id'] = res[9]
            startv['reg'] = res[10]
            startv['anno'] = res[11]
            startv['loc'] = res[12]
            startv['ins'] = res[13]
            startv['rip'] = res[14]
            if neut:
                result = querydb(
                    self,
                    'select neut_id,neut_date from neuts where neut_id=%s',
                    (pid,))
                if result is None:  return # db error
                for res in result:
                    if res[1]:
                        self.w.neutdateRb.setChecked(1)
                        self.w.neutDe.setDate(res[1])
                        startv['ndate'] = res[1]
                    else:
                        self.w.neutduRb.setChecked(1)
                        startv['ndate'] = None
            elif neut is None:
                self.w.neutunRb.setChecked(1)
            else:
                self.w.neutnoRb.setChecked(1)
        self.clichangeA.setVisible(1)
        self.clichangeA.setEnabled(1)
        self.w.backPb.setEnabled(0)
        self.w.backPb.hide()
        self.w.mainPb.setText(self.tr('&Save Changes'))
        self.ae_connect()
        self.w.cancelPb.clicked.connect(self.w_pat)
        self.w.pnameLe.setFocus()
        self.w.saeFr.show()

    def pat_save(self):
        """Insert/Update changes to db."""
        ## ck update p set (col, col, ...) = (val, val, ...)
        ## signal finish, like via addpat, chdpat or suchlike
        neut = neutdu = False
        if self.act == 'a':
            query_s = (
                'insert into patients(p_name,p_cid,breed,xbreed,dob,dobest,'
                'colour,sex,neutd,vicious,p_reg,p_anno,loc,identno,rip,'
                'ins)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                'returning p_id')
            if self.w.neutdateRb.isChecked():
                neut = True
            elif self.w.neutduRb.isChecked():
                neut = neutdu = True
            if self.w.neutnoRb.isChecked():
                nentry = False
            elif self.w.neutunRb.isChecked():
                nentry = None
            elif self.w.neutduRb.istChecked() or self.w.neutdateRb.isChecked():
                nentry = True
            if not 'prep_txt' in locals():
                from util import prep_txt
            res = querydb(
                self,
                query_s, (
                    str(prep_txt(self.w.pnameLe.text().toLatin1())),
                    self.cid,
                    self.w.breedDd.itemData(
                        self.w.breedDd.currentIndex(), 32).toInt()[0],
                    self.w.xbredCb.isChecked(),
                    self.w.dobDe.date().toPyDate(),
                    self.w.dobestCb.isChecked(),
                    self.w.colDd.itemData(
                        self.w.colDd.currentIndex(), 32).toInt()[0],
                    str(self.w.sexDd.currentText()[0]),
                    nentry,
                    self.w.viciousPb.isChecked(),
                    self.w.regDe.date().toPyDate(),
                    str(prep_txt(self.w.annoTe.toPlainText().toLatin1())),
                    self.w.locDd.itemData(
                        self.w.locDd.currentIndex(), 32).toInt()[0],
                    str(prep_txt(self.w.idLe.text().toLatin1())),
                    self.w.ripCb.isChecked(),
                    self.w.insDd.itemData(
                        self.w.insDd.currentIndex(), 32).toInt()[0],
                    ))
            if res is None:  return # db error
        elif self.act == 'e':
            if (self.startv['pname'] != self.w.pnameLe.text().toLatin1() or
                self.startv['breed'] != self.w.itemData(
                    self.w.breedDd.currentIndex(), 32).toInt()[0] or
                self.startv['xbred'] != self.w.xbredCb.isChecked() or
                self.startv['dob'] != self.w.dobDe.date().toPyDate() or
                self.startv['dobest'] != self.w.dobestCb.isChecked() or
                self.startv['col'] != self.w.colDd.itemData(
                    self.w.colDd.currentIndex(), 32).toInt()[0] or
                self.startv['sex'] != str(
                    self.w.sexDd.currentText().toLatin1()) or
                self.startv['rip'] != self.w.ripCb.isChecked() or
                self.startv['vicious'] != self.w.viciousCb.isChecked() or
                self.startv['id'] != self.w.idLe.text().toLatin1() or
                self.startv['reg'] != self.w.regDe.date().toPyDate() or
                self.startv['anno'] != self.w.annoTe.toPlainText().toLatin1() or
                self.startv['loc'] != self.w.locDd.currentIndex() or
                self.startv['ins'] != self.w.insDd.currentIndex() or
                (self.startv['neut'] and
                 ((self.w.neuteredCb.isChecked() or
                   self.w.neutduRb.isChecked() or
                   self.w.neutdateRb.isChecked()) or
                  self.startv['ndate'] == self.w.neutdateDe.date().toPyDate()))
                or
                self.startv['neut'] is None and self.w.neutunRb.isChecked() or
                not self.startv['neut'] and self.w.neutnoRb.isChecked()):
                nochanges = True
            else:
                nochanges = False
            if nochanges:
                self.w.statusbar.showMessage('No changes to save.')
                return
            query_s = (
                'update patients set p_name=%s,breed=%s,xbreed=%s,dob=%s,'
                'dobest=%s,colour=%s,sex=%s,rip=%s,vicious=%s,identno=%s,'
                'p_reg=%s,p_anno=%s,loc=%s,ins=%s,neutd=%s where p_id=%s '
                'returning p_id')
            if self.w.neutdateRb.isChecked():
                neut = True
            res = querydb(
                self,
                query_s, (
                    str(self.w.pnameLe.text().toLatin1()),
                    self.w.breedDd.itemData(self.w.breedDd.currentIndex(),32),
                    self.w.xbredCb.isChecked(), self.w.dobDe.date().toPyDate(),
                    self.w.dobestCb.isChecked(),
                    self.w.colDd.itemData(self.w.colDd.currentIndex(), 32),
                    self.w.sexDd.currentText(), self.w.ripCb.isChecked(),
                    self.w.viciousCb.isChecked(),
                    str(self.w.idLe.text().toLatin1()),
                    self.w.regDe.date().toPyDate(),
                    str(self.w.annoTe.toPlainText().toLatin1()),
                    self.w.locDd.itemData(self.w.locDd.currentIndex(), 32),
                    self.w.insDd.itemData(self.w.insDd.currentIndex(), 32),
                    neut, self.pid))
            if res is None:  return # db error
        self.db.commit()
        if self.w.neutduRb.isChecked():
            neut = neutdu = True
        if neut:
            self.ck_neutdate(self.pid, neutdu,
                             self.w.neutDe.date().toPyDate())
        print('pat_save done.')
        ## if self.act == 'a': # hierwei implement, in gnuv too
        ##     self.newpat.emit(res[0][0])
        ## elif self.act == 'e':
        ##     self.chgpat.emit(res[0][0])

    def popul_breeds(self):
        """(Re-)Populate breed Dd."""
        if self.db_err:
            return
        result = querydb(
            self,
            'select breed_id,breed_name,b_spec from breeds order by breed_name')
        if result is None:  return # db error
        self.breed2spec = {}
        self.w.breedDd.clear()
        self.w.breedDd.addItem('', 0)
        blist = []
        for res in result:
            self.w.breedDd.addItem(res[1], res[0])
            blist.append(res[1])
            self.breed2spec[res[0]] = res[2]
        self.w.breedDd.list = blist

    def popul_colours(self):
        """(Re-)Populate colour Dd."""
        if self.db_err:
            return
        idx = 0
        if self.w.colDd.currentIndex() > 0:
            idx = self.w.colDd.itemData(self.w.colDd.currentIndex(), 32)
        clist = []
        ch_conn(self, 'coldd')#, self.w.colDd.currentIndexChanged)
        self.w.colDd.clear()
        self.w.colDd.addItem('', 0)
        scode = 0
        if self.w.specDd.currentIndex() > 0:
            scode = 1<<(self.w.specDd.itemData(
                self.w.specDd.currentIndex(), 32).toInt()[0]-1)
            # e.g. 1, 2, 4, 8, 16, 32, 64, ...
        elif self.currentspec:
            scode = 1<<(self.currentspec-1)
        if scode == 0:
            scode = ''
        else:
            scode = ' and ((c_speccode=0) or bool(c_speccode&'+str(scode)+'))'
        result = querydb(
            self,
            'select col_id,b1.bcol,b2.bcol,b3.bcol from basecolours b1,'
            'basecolours b2,basecolours b3,colours where b1.bcol_id=col1 '
            'and b2.bcol_id=col2 and b3.bcol_id=col3{} order by b1.bcol '
            'nulls first, b2.bcol nulls first, b3.bcol nulls first'.format(
                scode))
        if result is None:  return # db error
        for res in result:
            tmp = '-'.join([col for col in res[1:] if col])
            self.w.colDd.addItem(tmp, res[0])
            clist.append(tmp)
        if idx:
            self.w.colDd.setCurrentIndex(self.w.colDd.findData(idx, 32))
        ch_conn(self, 'coldd',
                self.w.colDd.currentIndexChanged, self.adapt2colours)
        self.w.colDd.list = clist
        
    def popul_ins(self):
        """(Re-)Populate insurance Dd."""
        if self.db_err:
            return
        result = querydb(self,
                         'select i_name,i_id from insurances order by i_name')
        if result is None:  return # db error
        ilist = []
        self.w.insDd.clear()
        self.w.insDd.addItem('', 0)
        for res in result:
            self.w.insDd.addItem(res[0], res[1])
            ilist.append(res[0])
        if len(result) < 2:
            self.w.insDd.setEnabled(0)
            self.w.insLb.setEnabled(0)
        else:
            self.w.insDd.setEnabled(1)
            self.w.insLb.setEnabled(1)
        self.w.insLb.list = ilist

    def popul_locs(self):
        """(Re-)Populate location Dd."""
        if self.db_err:
            return
        result = querydb(
            self,
            'select l_id,l_name,housen,street from locations,addresses where '
            'l_address=addr_id order by l_name,housen,street')
        if result is None:  return # db error
        llist = []
        self.w.locDd.clear()
        for res in result:
            self.w.locDd.addItem(', '.join([e for e in res[1:] if e]),
                                 res[0])
            llist.append(', '.join([e for e in res[1:] if e]))
        if len(result) < 2:
            self.w.locDd.setEnabled(0)
            self.w.locLb.setEnabled(0)
        else:
            self.w.locDd.setEnabled(1)
            self.w.locLb.setEnabled(1)
        self.w.locLb.list = llist

    def popul_species(self):
        """(Re-)Populate 'species' Dd."""
        if self.db_err:
            return
        result = querydb(
            self, 'select spec_id,spec_name from species order by '
            'spec_name')
        if result is None:  return # db error
        slist = []
        self.w.specDd.clear()
        self.w.specDd.addItem('', 0)
        for res in result:
            self.w.specDd.addItem(res[1], res[0])
            slist.append(res[1])
        self.w.specDd.list = slist
    
    def prep_ae(self):
        """Prepare A&E (add/edit) stage of search-add-edit patient window."""
        self.w.detailedCb.setChecked(1)
        self.w.detailedCb.hide()
        self.newpatA.setEnabled(0)
        self.w.agespecDd.hide()
        self.w.agespecLb.hide()
        self.age_toggle(1)
        self.w.agesuDd.hide()
        self.w.agesuLb.hide()
        self.w.dobestCb.show()
        self.w.regspecDd.hide()
        self.w.regspecLb.hide()
        self.w.pfindDd.hide()
        self.w.pfindLb.hide()
        self.w.cfnameLb.hide()
        self.w.cfnameLe.hide()
        self.w.clientLb.show()
        self.w.csnameLb.setText('C&lient')
        self.w.csnameLe.hide()
        self.today = date.today()
        if self.act == 'a':
            self.initdob = self.today-timedelta(56)
            self.w.dobDe.setDate(self.initdob)
        self.w.dobDe.setMaximumDate(self.today)
        self.w.mainPb.setAutoDefault(1)
        self.w.mainPb.setDefault(1)
        self.w.matchFr.hide()
        self.w.mixedcolCb.hide()
        self.w.neutDe.setEnabled(0)
        self.w.neutBox.show()
        self.w.neuteredCb.hide()
        self.w.noMFr.hide()
        self.w.regDe.setEnabled(1)
        self.w.regDe.setMaximumDate(self.today)
        self.w.regDe.show()
        self.w.regLb.show()
        self.w.ripCb.setEnabled(1)
        self.w.ripCb.show()
        self.w.saeFr.setEnabled(1)
        self.w.secondPb.hide()
        self.w.secondPb.setEnabled(0)
        ch_conn(self, 'enter')#, self.keycheck.enter)
        ch_conn(self, 'mainpb')#, self.w.mainPb.clicked)
        ch_conn(self, '2ndpb')#, self.w.secondPb.clicked)

    def prep_s(self):
        """Setup search stage of the search-add-edit patient window."""
        # todo: dob disable, hierwei
        self.act = 's' # was 0
        self.clichangeA.setEnabled(0)
        self.clichangeA.setVisible(0)
        self.w.sbynameRb.setChecked(1)
        self.setWindowTitle('GnuVet: ' + self.tr('Search Patient'))
        self.resize(870, 626)
        self.w.errFr.hide()
        self.w.noMFr.hide()
        self.w.matchFr.hide()
        self.w.saeFr.setEnabled(1)
        self.actions_enable()
        self.w.pfindLb.show()
        self.w.pfindDd.show()
        self.w.neutBox.hide()
        self.w.neuteredCb.setEnabled(1)
        self.w.neuteredCb.show()
        self.w.seenCb.show()
        self.w.seenDe.show()
        self.w.agespecLb.show()
        self.w.agespecDd.show()
        if not self.w.agespecDd.currentIndex():
            self.w.ageSb.setEnabled(0)
            self.w.ageuDd.setEnabled(0)
        self.w.dobestCb.hide()
        self.w.agesuDd.show()
        self.w.agesuLb.show()
        self.w.ripCb.hide()
        self.w.regDe.setEnabled(self.w.regspecDd.currentIndex())
        self.w.regLb.setEnabled(self.w.regspecDd.currentIndex())
        self.cs_name = ''
        self.w.csnameLe.show()
        self.w.csnameLb.setBuddy(self.w.csnameLe)
        self.w.csnameLb.setText('C&lient Surname')
        self.w.csnameLb.show()
        self.cf_name = ''
        self.w.cfnameLe.show()
        self.w.cfnameLb.show()
        self.w.clientLb.hide()
        self.w.backPb.setDefault(0)
        self.w.backPb.setAutoDefault(0)
        self.w.backPb.hide()
        self.w.mainPb.setText('Search')
        self.w.mainPb.setEnabled(1)
        self.w.mainPb.setDefault(1)
        self.w.mainPb.setAutoDefault(1)
        self.w.secondPb.show()
        self.w.secondPb.setEnabled(1)
        self.w.secondPb.setText('R&eset')
        # CONNECTIONS
        ch_conn(self, 'mainpb', self.w.mainPb.clicked, self.list_pats)
        ch_conn(self, 'enter', self.keycheck.enter, self.w.mainPb.click)
        ch_conn(self, '2ndpb', self.w.secondPb.clicked, self.reset)
        self.w.saeFr.setEnabled(1)
        self.w.saeFr.show()
        self.w.detailedCb.show()
        self.w.detailedCb.setChecked(self.options['srchdetails'])
        self.details_toggle(self.w.detailedCb.isChecked())
        self.w.pnameLe.setFocus()
    
    def query_string(self, s_byname):
        """Construct query string from user input."""
        self.nch = {} # namechange
        if not self.w.seenCb.isHidden() and self.w.seenCb.isChecked():
            self.seen = []
            res = querydb(
                self,
                'select seen_pid from seen where seen_date=%s',
                (str(self.w.seenDe.date().toString('yyyy-M-d')),))
            if res is None:  return # db error
            self.seen.extend(res)
            if not self.seen:
                self.no_matches()
                return None
        query_sel = (
            "p_name,breed_abbr,xbreed,sex,neutd,b1.bcol,b2.bcol,b3.bcol,"
            "c_sname,c_fname,c_address,housen,street,village,l_name,p_id,p_cid,"
            "p_anno,breed_name,dob,rip,p_last")
	query_from = ('patients,breeds,basecolours b1,basecolours b2,'
                      'basecolours b3,colours,clients,addresses,locations')
	query_order = 'p_name,c_sname,c_fname,housen,street,village,l_name'
        query_where = ''
        if not s_byname:
            query_order = 'p_last desc,' + query_order
        if not 'wildcard' in locals():
            from util import wildcard, prep_txt
        query_plus = ''
        if self.w.pnameLe.text():
            query_where += "p_name ilike'" + wildcard(prep_txt(
                str(self.w.pnameLe.text().toLatin1()), True)) + "'"
            result = querydb(
                self,
                'select nh_pid,nh_name,nh_date from namehist where '
                'nh_name ilike %s', (wildcard(prep_txt(
                    str(self.w.pnameLe.text().toLatin1()))),))
            if result is None:  return # db error
            for res in result:
                self.nch[res[0]] = dict(
                    name=res[1], date=res[2].strftime("%d.%m.%y"))
            if len(self.nch):
                query_plus += (
                    ' p_id in (' +
                    ','.join([str(i) for i in self.nch.keys()]) + ')')
        if self.w.breedDd.currentIndex() > 0:
            query_where += (
                (query_where and ' and ') +
                'breed=' + str(self.w.breedDd.itemData(
                    self.w.breedDd.currentIndex(), 32).toString().toLatin1()))
        if (self.w.specDd.currentIndex() > 0 and
            not self.w.breedDd.currentIndex() > 0):
            query_where += (
                (query_where and ' and ') +
                "breed=breed_id and b_spec=" +
                str(self.w.specDd.itemData(
                    self.w.specDd.currentIndex(), 32).toString().toLatin1()))
        if self.w.sexDd.currentIndex():
            query_where += (
                (query_where and ' and ') + "sex='" +
                str(self.w.sexDd.itemData(
                    self.w.sexDd.currentIndex(), 32).toString().toLatin1())
                + "'")
        if self.w.csnameLe.text():
            query_where += (
                (query_where and ' and ') + "c_sname ilike'" +
                wildcard(prep_txt(
                    str(self.w.csnameLe.text().toLatin1()), True)) + "'")
        if self.w.cfnameLe.text():
            query_where += (
                (query_where and ' and ') + "c_fname ilike'" +
                wildcard(prep_txt(
                    str(self.w.cfnameLe.text().toLatin1()), True)) + "'")
        if self.w.detailedCb.isChecked():
            if self.w.xbredCb.isChecked():
                query_where += ((query_where and ' and ') + "xbreed")
            if self.w.mixedcolCb.isChecked():
                colours = self.mixedcol_search()
                if colours:
                    query_where += (
                        (query_where and ' and ') +
                        self.curs.mogrify('colour in %s', (colours,)))
                else:
                    self.db_state()
                    return
            elif self.w.colDd.currentIndex() > 0:
                query_where += (
                    (query_where and ' and ') + 'colour=' +
                    str(self.w.colDd.itemData(
                        self.w.colDd.currentIndex(), 32).toString().toLatin1()))
            if self.w.neuteredCb.isChecked():
                query_where += (query_where and ' and ') + "neutd"
            if self.w.viciousCb.isChecked():
                query_where += (query_where and ' and ') + "vicious"
            if self.w.agespecDd.currentIndex():
                query_where += (query_where and ' and ') + "dob"
                t = self.w.agesuDd.currentIndex()
                if t == 0:
                    days = 0
                elif t == 1:
                    days = 30
                elif t == 2:
                    days = 7
                elif t == 3:
                    days = 1
                else:
                    days = 365
                d = str(self.w.dobDe.date().toString(1))
                if self.w.agespecDd.currentText() == '=':
                    query_where += (
                        " between date'{0}'-integer'{1}'and date'"
                        "{0}'+integer'{1}'".format(d, days))
                elif self.w.agespecDd.currentText() == '>':
                    query_where += "<'{}'".format(d)
                elif self.w.agespecDd.currentText() == '<':
                    query_where += ">'{}'".format(d)
            if self.w.locDd.currentIndex():
                query_where += (
                    (query_where and ' and ') + "loc=" +
                    str(self.w.locDd.itemData(
                        self.w.locDd.currentIndex(), 32).toString().toLatin1()))
            if self.w.regDe.isEnabled():
                query_order = 'p_reg desc,' + query_order
                d = self.w.regDe.date().toString(1)
                query_sel += ",p_reg"
                query_where += (query_where and ' and ') + "p_reg"
                if self.w.regspecDd.currentText() == '=':
                    query_where += (
                        " between date'{}'-integer'30'and date "
                        "'{}'+integer'30'".format(d, d))
                else:
                    query_where += str(self.w.regspecDd.currentText())
                    query_where += "'{}'".format(d)
            if self.w.insDd.currentIndex():
                query_where += (
                    (query_where and ' and ') + "ins=" +
                    str(self.w.insDd.itemData(
                        self.w.insDd.currentIndex(), 32).toString().toLatin1()))
            if self.w.idLe.text():
                query_where += (
                    (query_where and ' and ') + "identno ilike'" +
                    wildcard(prep_txt(
                        str(self.w.idLe.text().toLatin1()), True))+"'")
            if self.w.petpassLe.text():
                query_where += (
                    (query_where and ' and ') + "petpass ilike'" +
                    wildcard(prep_txt(
                        str(self.w.petpassLe.text().toLatin1()), True))+"'")
            if self.w.annoTe.toPlainText():
                query_where += (
                    (query_where and ' and ') + "p_anno ilike'" +
                    wildcard(prep_txt(
                        str(self.w.annoTe.toPlainText().toLatin1()), True))+"'")
        query_where += ((query_where and ' and ') +
                        "p_cid=c_id and breed=breed_id and colour=col_id"
                        " and b1.bcol_id=col1 and b2.bcol_id=col2 and "
                        "b3.bcol_id=col3 and c_address=addr_id and loc=l_id")
        if query_plus:
            query_where += (query_where and ' or') + query_plus
        t = self.w.pfindDd.currentIndex()
        if t == 1: # live
            query_where += ' and not rip' # was patients.rip
        elif t == 2: # rip
            query_where += ' and rip' # dto
        if self.w.seenCb.isChecked() and self.seen:
            query_where += (
                (query_where and ' and ') +
                self.curs.mogrify('p_id in %s', (tuple(self.seen),)))
        return  ('select ' + query_sel + ' from ' + query_from +
                 ' where ' + query_where + ' order by ' + query_order)

    def regde_toggle(self, state):
        self.w.regDe.setEnabled(state)

    def reset(self):
        """As the name suggests."""
        # check sequence of index setting to avoid unnec calls (colDd?)
        self.w.noMFr.hide()
        self.w.matchFr.hide()
        # DEVEL:
        # self.w.pfindDd.setCurrentIndex(0)
        #self.w.pfindDd.setCurrentIndex(2)
        # END DEVEL
        self.w.idLe.clear()
        self.w.pnameLe.clear()
        self.w.breedDd.setCurrentIndex(0)
        self.w.xbredCb.setChecked(0)
        self.w.specDd.setCurrentIndex(0)
        self.w.colDd.setCurrentIndex(0)
        self.w.mixedcolCb.setChecked(0)
        self.w.mixedcolCb.setEnabled(0)
        self.w.sexDd.setCurrentIndex(0)
        self.w.neuteredCb.setChecked(0)
        self.w.agespecDd.setCurrentIndex(0)
        self.w.ageSb.setValue(0)
        self.w.ageuDd.setCurrentIndex(0)
        self.w.locDd.setCurrentIndex(0)
        self.w.viciousCb.setChecked(0)
        self.w.regspecDd.setCurrentIndex(0)
        self.w.regDe.clear()
        self.w.csnameLe.clear()
        self.w.cfnameLe.clear()
        self.w.insDd.setCurrentIndex(0)
        self.w.annoTe.clear()
        self.age_toggle()
        self.w.pnameLe.setFocus()
        self.prep_s()

    def resizeEvent(self, event):
        if event.oldSize().width() == -1:
            return
        if not self.w.matchFr.isVisible():
            return
        n_width  = self.width()
        n_height = self.height()
        o_width  = event.oldSize().width()
        o_height = event.oldSize().height()
        self.w.buttonBox.move(self.w.buttonBox.x() + (n_width-o_width)/2,
                               self.w.buttonBox.y() + (n_height-o_height))
        self.w.matchFr.resize(self.w.matchFr.width() + (n_width-o_width),
                               self.w.matchFr.height() + (n_height-o_height))
        self.w.plist.resize(self.w.plist.width() + (n_width-o_width),
                             self.w.plist.height() + (n_height-o_height))

    def savedrestore(self):
        """Restore pre-crash (?) state from file."""
        # hierwei
        # ...
        #if self.adding:
        #    self.await_adding()
        pass

    def seencb(self, checked):
        if checked:
            self.w.seenDe.setEnabled(1)
        else:
            self.w.seenDe.setEnabled(0)
        
    def set_addedbreed(self, new_breed=0):
        """Select freshly added breed."""
        self.popul_breeds()
        tmp = self.w.breedDd.findData(new_breed, 32)
        self.w.breedDd.setCurrentIndex(tmp)
        self.adapt_colours(tmp)

    def set_addedcol(self, new_col=0):
        """Select freshly added colour."""
        self.popul_colours()
        self.w.colDd.setCurrentIndex(self.w.colDd.findData(new_col, 32))

    def set_addedins(self, new_ins=0):
        """Select freshly added insurance."""
        self.popul_ins()
        self.w.insDd.setCurrentIndex(self.w.insDd.findData(new_ins), 32)

    def set_addedloc(self, new_loc=0):
        """Select freshly added location."""
        self.popul_locs()
        self.w.locDd.setCurrentIndex(self.w.locDd.findData(new_loc), 32)

    def set_addedspec(self, new_spec=0):
        """Select freshly added 'species' in specDd."""
        self.popul_species()
        self.w.specDd.setCurrentIndex(self.w.specDd.findData(new_spec), 32)
        self.adapt_breeds(new_spec)
    
    def set_cname(self):
        """Set the client name."""
        res = querydb(
            self,
            'select t_title,c_sname,c_fname,c_mname from clients,titles where '
            'c_title=t_id and c_id=%s', (self.cid,))
        if res is None:  return # db error
        res = res[0]
        tmp = (res[0], ','.join([e for e in res[1:3] if (e or res[3])]),
               res[3])
        tmp = ' '.join([e for e in tmp if e])
        self.w.clientLb.setText(tmp)
        return True    
        
    def state_write(self):
        """Signal unsaved changes to parent for filing for later restoration."""
        # hierwei: UPDATE THIS, take care of string conversions etc
        meself = self.objectName()
        save_things = ['{}:act:{}'.format(meself, self.act)]
        if self.w.idLe.text():
            save_things.append('{}:idLe:{}'.format(
                meself, self.w.idLe.text().toLatin1().replace(':', '\t')))
        if self.w.pnameLe.text():
            save_things.append('{}:pnameLe:{}'.format(
                meself, self.w.pnameLe.text().toLatin1().replace(':', '\t')))
        if self.w.breedDd.currentIndex():
            save_things.append('{}:breedDd:{}'.format(
                meself, self.w.breedDd.itemData(
                    self.w.breedDd.currentIndex(), 32).toInt()[0]))
        if self.w.xbredCb.isChecked():
            save_things.append(meself + ':xbredCb:1')
        if (self.w.specDd.currentIndex() and not
                self.w.breedDd.currentIndex()):
            save_things.append('{}:pspecDd:{}'.format(
                meself, self.w.specDd.itemData(
                    self.w.specDd.currentIndex(), 32).toInt()[0]))
        if self.w.colDd.currentIndex():
            save_things.append('{}:pcolDd:{}'.format(
                meself, self.w.colDd.itemData(
                    self.w.colDd.currentIndex(), 32).toInt()[0]))
        if self.w.mixedcolCb.isChecked():
            save_things.append(meself + ':mixedcolCb:1')
        if self.w.sexDd.currentIndex():
            save_things.append('{}:psexDd:{}'.format(
                meself, self.w.sexDd.currentIndex()))
        if self.w.neuteredCb.isChecked():
            save_things.append(meself + ':neuteredCb:1')
        if self.w.neutnoRb.isChecked():
            save_things.append(meself + ':neutnoRb:1')
        if self.w.neutunRb.isChecked():
            save_things.append(meself + ':neutunRb:1')
        if self.w.neutduRb.isChecked():
            save_things.append(meself + ':neutduRb:1')
        if self.w.neutdateRb.isChecked():
            save_things.append(meself + ':neutdateRb:1')
            save_things.append(meself + ':neutDe:{}'.format(
                self.w.neutDe.date().toString('yyyyMMdd')))
        if self.w.agespecDd.currentIndex():
            save_things.append(meself + ':agespecDd:{}'.format(
                self.w.agespecDd.currentIndex()))
            save_things.append(meself + ':dobDe:{}'.format(
                self.w.dobDe.date().toString('yyyyMMdd')))
        if self.w.ageSb.value():
            save_things.append(meself + ':ageSb:{}'.format(
                self.w.ageSb.value()))
        if self.w.ageuDd.currentIndex():
            save_things.append(meself + ':ageuDd:{}'.format(
                self.w.ageuDd.currentIndex()))
        if self.w.dobestCb.isChecked():
            save_things.append(meself + ':dobestCb:1')
        if self.w.locDd.currentIndex():
            save_things.append(meself + ':plocDd:{}'.format(
                self.w.locDd.itemData(
                    self.w.locDd.currentIndex(), 32).toInt()[0]))
        if self.w.ripCb.isChecked():
            save_things.append(meself + ':ripCb:1')
        if self.w.viciousCb.isChecked():
            save_things.append(meself + ':viciousCb:1')
        if self.w.csnameLe.text():
            save_things.append(meself + ':csnameLe:{}'.format(
                self.csnameLe.text().toLatin1().replace(':', '\t')))
        if self.w.cfnameLe.text():
            save_things.append(meself + ':cfnameLe:{}'.format(
                self.w.cfnameLe.text().toLatin1().replace(':', '\t')))
        if self.cid:
            save_things.append(meself + ':c_id:{}'.format(self.cid))
        if self.pid:
            save_things.append(meself + ':p_id:{}'.format(self.pid))
        if self.w.insDd.currentIndex():
            save_things.append(meself + ':pinsDd:{}'.format(
                self.w.insDd.itemData(
                    self.w.insDd.currentIndex(), 32).toInt()[0]))
            save_things.append(meself + ':regDe:{}'.format(
                self.w.regDe.date().toString('yyyyMMdd')))
        if self.w.annoTe.toPlainText():
            save_things.append(meself + ':annoTe:{}'.format(
                self.w.annoTe.toPlainText().toLatin1().replace(':', '\t')))
        if self.w.pfindDd.currentIndex():
            save_things.append(meself + ':pfindDd:{}'.format(
                               self.w.pfindDd.currentIndex()))
        if len(self.p_data):
            save_things.append(meself + ':p_data:{}'.format(str(self.p_data)))
        self.savestate.emit(save_things)
        
    def trackrow(self, row=0):
        """Keep track of selected patient and client id."""
        self.pid = self.pids[row]
        self.cid = self.cids[row]

    def w_cli(self):
        self.cidsig.connect(self.gaia.w_cli)
        self.cidsig.emit(self.cid)
        self.cidsig.disconnect(self.gaia.w_cli)
        self.close()

    def w_pat(self):
        self.pidsig.connect(self.gaia.openpat)
        self.pidsig.emit(self.pid)
        self.pidsig.disconnect(self.gaia.openpat)
        self.close()

    def debugf(self):
        print('header[-1] width {}, sizeHint.width {}'.format(
            self.w.plist.headers[-1].width(),
            self.w.plist.headers[-1].sizeHint().width()))
        
if __name__ == '__main__':
    import dbmod
    a = QApplication([])
    a.setStyle('plastique')
    ding = Saepat(None)
    ding.show()
    exit(a.exec_())
