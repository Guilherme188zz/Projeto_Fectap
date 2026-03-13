"""The appointment calendar."""

# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

# TODO:
# Errors: s. end of file
# Add Open_Patient button?

from datetime import date, datetime, time, timedelta
from locale import LC_ALL, resetlocale, setlocale
from psycopg2 import OperationalError
from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import (QMainWindow, QMenu)
from keycheck import Keycheck
from util import ch_conn, newaction, querydb
from appoint_ui import Ui_Appointer
from gtable import Gcell

class Appointer(QMainWindow):
    # signals
    gvquit = pyqtSignal(bool)
    dbstate = pyqtSignal(object) # False: err
    helpsig = pyqtSignal(str)
    
    # vars
    day_headss = """Gcell {
border: 1px solid darkgray;
border-radius: 3px;
}
"""
    othermonth = """Gcell {
background: lightblue;
color: gray;
border: 1px solid darkgray;
border-radius: 3px;
}
"""
    curs = None
    dberr = shutdown = False
    displayed = 0 # week  1 day  2 month
    gaia = None
    selstaff = ''
    ## start = True # unused (?)
    starttime = None

    def __init__(self, parent=None, today=None, pid=None):
        super(Appointer, self).__init__(parent)
        self.realday = datetime.today().date()
        self.pid = pid
        self.today = today
        if self.today is None:
            self.today = self.realday
        else:
            self.today = (type(today)==date and today or today.date())
        #    instance vars
        self.conns = {} # pyqt bug: disconnect() w/o arg can segfault
        self.sigs  = {}
        self.times = [] # holds the time values depending on settings
        self.savedata = None # holds data to save or re-edit
        #    setup
        self.w = Ui_Appointer()
        self.w.setupUi(self)
        #    ACTIONS
        # devel
        develA = newaction(self, '&Devel helper', short='Ctrl+B')
        # end devel
        closeA = newaction(self, 'Close &Window', 'Close this window', 'Ctrl+W')
        self.dbA = newaction(self, '&Reconnect to database',
                             'Try to reconnect to database', 'Ctrl+R')
        self.delA = newaction(
            self,'&Delete appointment','Delete selected appointment','Ctrl+D')
        self.editA = newaction(
            self, '&Edit appointment', 'Edit selected appointment', 'Ctrl+E')
        helpA = newaction(self, '&Help', 'Context sensitive help', 'F1')
        self.opencA = newaction(
            self, 'Open client', 'Open selected client', 'Ctrl+C')
        self.openpA = newaction(
            self, 'Open patient', 'Open selected patient', 'Ctrl+P')
        self.markM = QMenu(self.tr('&Mark appointment as'), self)
        markopenA = newaction(self, 'open', icon=':/images/markopen.png')
        markdoneA = newaction(self, 'done', icon=':/images/markdone.png')
        markmissedA = newaction(self, 'missed', ':/images/markmissed.png')
        self.newappA = newaction(
            self, '&Add new appointment', 'Set new appointment', 'Ctrl+N')
        quitA = newaction(
            self,'&Quit GnuVet','Close all windows and quit GnuVet.','Ctrl+Q')
        self.selectA = newaction(
            self, '&Select date', 'Select a specific date', 'Ctrl+S')
        aboutA = newaction(self, 'About &GnuVet', 'GnuVet version info')
        self.todayA = newaction(self, 'Select &Today', short='Ctrl+T')
        # hierwei further actions
        #    MENUES
        taskM = QMenu(self.w.menubar)
        taskM.setTitle(self.tr('&Task'))
        newM = QMenu(self.w.menubar)
        newM.setTitle(self.tr('&New'))
        helpM = QMenu(self.w.menubar)
        helpM.setTitle(self.tr('&Help'))
        self.calM = QMenu(self.w.calendar)
        #    MENU ENTRIES
        self.markM.addAction(markopenA)
        self.markM.addAction(markdoneA)
        self.markM.addAction(markmissedA)
        taskM.addAction(self.dbA)
        taskM.addSeparator()
        taskM.addAction(self.editA)
        taskM.addAction(self.delA)
        taskM.addAction(self.selectA)
        taskM.addAction(self.todayA)
        taskM.addSeparator()
        taskM.addAction(self.opencA)
        taskM.addAction(self.openpA)
        taskM.addSeparator()
        taskM.addMenu(self.markM)
        taskM.addSeparator()
        taskM.addAction(closeA)
        taskM.addAction(quitA)
        taskM.setSeparatorsCollapsible(True)
        newM.addAction(self.newappA)
        helpM.addAction(helpA)
        helpM.addAction(develA)
        helpM.addSeparator()
        helpM.addAction(aboutA)
        self.calM.addAction(self.newappA)
        self.calM.addAction(self.editA)
        self.calM.addAction(self.delA)
        self.calM.addAction(self.selectA)
        self.calM.addSeparator()
        self.calM.addAction(self.openpA)
        self.calM.addAction(self.opencA)
        self.calM.addSeparator()
        self.calM.addMenu(self.markM)
        self.w.menubar.addMenu(taskM)
        self.w.menubar.addMenu(newM)
        self.w.menubar.addMenu(helpM)
        #    ACTION CONNECTIONS
        closeA.triggered.connect(self.close)
        self.delA.triggered.connect(self.app_del)
        self.editA.triggered.connect(self.app_edit)
        helpA.triggered.connect(self.help_self)
        self.opencA.triggered.connect(self.opencli)
        self.openpA.triggered.connect(self.openpat)
        markopenA.triggered.connect(self.markopen)
        markdoneA.triggered.connect(self.markdone)
        markmissedA.triggered.connect(self.markmissed)
        self.newappA.triggered.connect(self.app_add)
        quitA.triggered.connect(self.gv_quitconfirm)
        self.selectA.triggered.connect(self.sel_date)
        self.todayA.triggered.connect(self.sel_today)
        develA.triggered.connect(self.develf)
        #    BUTTON CONNECTIONS
        self.w.yearbackPb.clicked.connect(self.backyear)
        self.w.monthbackPb.clicked.connect(self.backmonth)
        self.w.weekbackPb.clicked.connect(self.backweek)
        self.w.daybackPb.clicked.connect(self.backday)
        self.w.dayforePb.clicked.connect(self.foreday)
        self.w.weekforePb.clicked.connect(self.foreweek)
        self.w.monthforePb.clicked.connect(self.foremonth)
        self.w.yearforePb.clicked.connect(self.foreyear)
        self.w.closePb.clicked.connect(self.close)
        #    FURTHER CONNECTIONS
        self.w.calendar.selected.connect(self.sel_day)
        self.w.calendar.doubleclicked.connect(self.openpat)
        self.w.calendar.rightclicked.connect(self.calmenu)
        ch_conn(self, 'confirmok',
                self.w.confirmokPb.clicked, self.app_save)
        ch_conn(self, 'confirmedit',
                self.w.confirmeditPb.clicked, self.app_edit)
        ch_conn(self, 'confirmcc',
                self.w.confirmccPb.clicked, self.confhide)
        #    INIT
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
        if 'lang' in self.options and self.options['lang'] == 'en':
            setlocale(LC_ALL, 'C') # whats this?
        else:
            resetlocale()
        try:
            self.curs = self.db.cursor()
        except (OperationalError, AttributeError) as e: # no db
            self.db_state(e)
            return
        if 'starttime' in self.options and self.options['starttime']:
            starttime = map(int, self.options['starttime'].split(':'))
            if len(starttime) > 1:
                self.starttime = time(starttime[0], starttime[1])
            else:
                self.starttime = time(starttime[0])
        staff = querydb(
            self,
            'select stf_id,stf_short from staff order by stf_id')
        if staff is None:  return # db error
        self.staff = {}
        self.w.staffDd.addItem('All', 0)
        for e in staff:
            self.staff[e[0]] = e[1]
            self.w.staffDd.addItem(e[1], e[0])
        self.w.staffDd.activated.connect(self.set_staff)
        self.keycheck = Keycheck(self)
        self.installEventFilter(self.keycheck)
        self.w.calendar.installEventFilter(self.keycheck)
        ch_conn(self, 'esc', self.keycheck.esc, self.w.closePb.click)
        self.dbA.setVisible(False)
        self.dbA.setEnabled(False)
        if 'cal_disp' in self.options:
            self.disp = self.options['cal_disp']
        ## else:
        ## self.disp = 0 # week, should be standard
        ## self.disp = 1 # day
        self.disp = 2 # month
        self.get_basedata()
        self.show()
        if self.disp == 1:
            self.w.dayRb.setChecked(True)
        elif self.disp == 2:
            self.w.monthRb.setChecked(True)
        else:
            self.w.weekRb.setChecked(True)
        self.w.dayRb.clicked.connect(self.toggle)
        self.w.weekRb.clicked.connect(self.toggle)
        self.w.monthRb.clicked.connect(self.toggle)
        self.sel_display()

    def app_add(self):
        if not hasattr(self, 'datefixw'):
            from datefix import Datefix
            self.datefixw = Datefix(self, appdt=self.today)
        else:
            self.datefixw.update_disp(appdt=self.today)
        if self.w.calendar.selcell.parent == self.w.calendar.table:
            x, y = self.w.calendar.selcell.x(), self.w.calendar.selcell.y()
        else:
            x, y = (self.w.calendar.selcell.parent.x(),
                    self.w.calendar.selcell.parent.y())
        self.datefixw.move(x-10, y+10)
        ch_conn(self, 'datefix', self.datefixw.data, self.app_set)
        self.datefixw.show()

    def app_del_confirm(self):
        self.w.confirmeditPb.hide()
        self.w.confirm.msgLb.setText(self.tr(
            'Please confirm to delete appointment\n') +
                                     self.w.calendar.selcell.text())
        ch_conn(self, 'confirmok', self.w.confirmokPb.clicked, self.app_del)
        ch_conn(self, 'confirmcc',
                self.w.confirmccPb.clicked, self.w.confhide)
        self.w.confirm.show()

    def app_del(self):
        ch_conn(self, 'confirmok')
        suc = querydb(
            self,
            'delete from appointments where app_id=%s returning app_id',
            (self.w.calendar.selcell.data,))
        if suc is None:  return # db error
        self.db.commit()
        self.w.confirm.hide()
        self.sel_display()

    def app_edit(self):
        if not self.w.calendar.selcell.data:
            self.app_add()
            return
        self.w.confirm.hide()
        if self.savedata:
            self.appid = self.savedata[0]
            app = self.savedata[1:]
        else:
            self.appid = self.w.calendar.selcell.data
            app = querydb(
                self,
                'select app_dt,app_text,app_cid,app_pid,app_staffid,app_dur,'
                'app_status from appointments where app_id=%s', (self.appid,))
            if app is None:  return # db error
            app = app[0]
        if not hasattr(self, 'datefixw'):
            from datefix import Datefix
            self.datefixw = Datefix(
                self, appid=self.appid, appdt=app[0], apptxt=app[1],
                appcid=app[2], apppid=app[3], appstf=app[4], appdur=app[5])
        else:
            self.datefixw.update_disp(
                appid=self.appid, appdt=app[0], apptxt=app[1],
                appcid=app[2], apppid=app[3], appstf=app[4], appdur=app[5])
        if self.w.calendar.selcell.parent == self.w.calendar.table:
            x, y = self.w.calendar.selcell.x(), self.w.calendar.selcell.y()
        else:
            x, y = (self.w.calendar.selcell.parent.x(),
                    self.w.calendar.selcell.parent.y())
        self.datefixw.move(x-10, y+10)
        ch_conn(self, 'datefix', self.datefixw.data, self.app_set)
        self.datefixw.show()
        
    def app_save(self):
        self.w.confirm.hide()
        if self.savedata[6] == 'a':
            suc = querydb(
                self,
                'insert into appointments(app_dt,app_text,app_cid,app_pid,'
                'app_staffid,app_dur,app_status)values(%s,%s,%s,%s,%s,%s,%s)'
                'returning app_id',
                (self.savedata[0],self.savedata[1],self.savedata[2],
                 self.savedata[3],self.savedata[4],self.savedata[5],
                 self.savedata[7]))
        elif self.savedata[6] == 'e':
            suc = querydb(
                self,
                'update appointments set app_dt=%s,app_text=%s,app_cid=%s,'
                'app_pid=%s,app_staffid=%s,app_dur=%s,app_status=%s where '
                'app_id=%s returning app_id',
                (self.savedata[0],self.savedata[1],self.savedata[2],
                 self.savedata[3],self.savedata[4],self.savedata[5],
                 self.savedata[7],self.appid))
        if suc is None: return # db error
        self.db.commit()
        self.savedata = None
        self.sel_display()
        
    def app_set(self, data):
        ch_conn(self, 'datefix')
        # app_dt app_txt app_cid app_pid app_staff app_dur action
        self.savedata = data
        test = querydb(
            self,
            'select app_id,app_staffid,app_dt from appointments where '
            'app_staffid=%s and(date %s,interval %s)overlaps(app_dt,app_dur)',
            (data[4],data[0],data[5],))
        if test is None:  return # db error
        stf = querydb(
            self,
            'select stf_logname from staff where stf_id=%s', (data[4],))
        if stf is None:  return # db error
        stf = stf[0][0]
        if test: # hierwei
            self.w.confirm.msgLb.setText(
                self.tr('<b>Time slot occupied!</b><br>') +
                str(stf) +
                self.tr(' already has appointment on ') +
                data[0].strftime('%d.%m.%Y %H:%M'))
            self.w.confirm.show()
        else:
            self.app_save()
        
    def backday(self):
        self.today -= timedelta(1)
        self.sel_display()

    def backmonth(self):
        if self.today.day > 30 and self.today.month in (5,7,10,12): # not 1,3,8
            self.today = self.today.replace(day=30, month=self.today.month-1)
        elif self.today.month == 3 and self.today.day > 29:
            if self.isleap(self.today.year):
                self.today = self.today.replace(day=29, month=2)
            else:
                self.today = self.today.replace(day=28, month=2)
        elif self.today.month == 1:
            self.today = self.today.replace(year=self.today.year-1, month=12)
        else:
            self.today = self.today.replace(month=self.today.month-1)
        self.sel_display()

    def backweek(self):
        self.today -= timedelta(7)
        self.sel_display()
        
    def backyear(self):
        if (self.isleap(self.today.year) and self.today.month == 2 and
            self.today.day == 29):
            self.today = self.today-timedelta(1)
        self.today = self.today.replace(year=self.today.year-1)
        self.sel_display()

    def calmenu(self, where):
        self.calM.popup(where)

    def calres(self):
        """Set resolution of calendar: 0 60, 1 30, 2 15 minutes."""
        for i in xrange(24): # hierwei diff res: e.g. 15' inst/o 30?
            self.times.append(time(i))
            if 'cal_res' in self.options:
                if self.options['cal_res'] == 2:
                    self.times.append(time(i, 15))
                    self.times.append(time(i, 30))
                    self.times.append(time(i, 45))
                elif self.options['cal_res'] == 1:
                    self.times.append(time(i, 30))

        for a in (self.editA, self.newappA, self.delA, self.markM):
            a.setEnabled(yes)

    def ck_actions(self, c):
        toenable = [self.newappA]
        todisable = []
        if c.data:
            toenable.extend([self.delA, self.editA, self.markM])
            res = querydb(
                self,
                'select app_cid, app_pid from appointments where app_id=%s',
                (c.data,))
            if res is None:  return # db error
            if res[0][0]:
                toenable.append(self.opencA)
            else:
                todisable.append(self.opencA)
            if res[0][1]:
                toenable.append(self.openpA)
            else:
                todisable.append(self.openpA)
        else:
            todisable.extend([
                self.editA, self.delA, self.markM, self.opencA, self.openpA])
        for a in toenable:
            a.setEnabled(True)
        for a in todisable:
            a.setEnabled(False)

    def confhide(self):
        self.w.confirm.hide()

    # devel:
    def about(self):
        if hasattr(self, 'aboutw'):
            self.aboutw.show()
        else:
            import gv_about
            lang = ('lang' in self.options and self.options['lang'] or 'en')
            self.aboutw = gv_about.About(self, lang)
            
    def db_connect(self):
        pass

    def xy_decr(self):
        pass
    
    # end devel:
    
    def dbdep_enable(self, yes=True):
        """En- or disable db dependent actions."""
        if self.w.calendar.selcell.data:
            self.ck_actions(self.w.calendar.selcell)
        self.dbA.setVisible(not yes)
        self.dbA.setEnabled(not yes)
        
    def db_state(self, msg=''):
        """Actions to be taken on db loss or gain."""
        self.dberr = msg and True or False
        self.w.no_dbconn.setVisible(self.dberr)
        self.dbstate.emit(not self.dberr)
        self.dbdep_enable(not self.dberr)
        if not self.gaia:
            self.warning(msg=msg)
            if not self.isVisible(): # devel
                self.warnw.closed.connect(self.show)

    def dis_dayweek(self):
        self.w.calendar.clear_all()
        self.w.calendar.alter = True
        self.w.calendar.selnext = False
        self.w.calendar.scrollh = 1 # AlwaysOff
        self.w.calendar.adjust_scroll()
        if not self.times:
            self.calres()

    def display_day(self):
        self.dis_dayweek()
        if self.today == self.realday:
            a = '<b>'
        else:
            a = ''
        self.w.calendar.set_headers(
            ['week ' + self.today.strftime('%U'),
             self.today.strftime('{}%A %d.%m.%Y'.format(a))])
        self.w.calendar.align_header(1, 'c')
        self.w.calendar.set_colwidth(0, 80)
        self.w.calendar.set_colwidth(
            1, self.w.calendar.width() -
            (80 + self.w.calendar.verticalScrollBar().sizeHint().width()))
        for t in self.times:
            self.w.calendar.append_row([t.strftime('%H:%M'), ''])
        for c in self.w.calendar.column(0):
            c.selectable = False
        data = self.get_daydata()
        for e in data:
            csname, pname = self.getnames(e[3], e[4])
            entry = self.mkentry(
                (e[0], e[1], e[2], csname, pname, self.staff[e[5]]))
            for i, c in enumerate(self.w.calendar.column(0)):
                if e[1].strftime('%H:%M') == c.text():
                    cell = self.w.calendar.cell(i, 1)
                    ## if cell.entry:
                    self.mknewcell(cell, entry, e[0], e[6])
                    ## else:
                    ##     cell.setWordWrap(False)
                    ##     cell.elidetext(entry)
                    ##     cell.setToolTip(entry)
                    ##     cell.setdata(e[0])
        if self.starttime is not None:
            selrow=self.times.index(self.starttime)
            self.w.calendar.select_cell(
                self.w.calendar.cell(row=selrow, col=1))
            self.w.calendar.scrolltov(selrow)
        self.w.calendar.setFocus()

    def display_month(self):
        startday = date(self.today.year, self.today.month, 1)
        if startday.month == 12:
            enddt = datetime.fromordinal(
                startday.replace(month=1).toordinal())-timedelta(0, 1)
        else:
            enddt = datetime.fromordinal(
                startday.replace(
                    month=startday.month+1).toordinal())-timedelta(0, 1)
        tf = '%a %d.%m.%Y'
        monday = startday
        while monday.weekday():
            monday = monday+timedelta(-1)
        self.w.calendar.clear_all()
        self.w.calendar.alter = False
        self.w.calendar.selnext = True
        self.w.calendar.hscroll = 0
        self.w.calendar.adjust_scroll()
        dates = []
        for d in xrange(7):
            dates.append(
                [(monday+timedelta(d)).strftime(tf),
                 (monday+timedelta(d+7)).strftime(tf),
                 (monday+timedelta(d+14)).strftime(tf),
                 (monday+timedelta(d+21)).strftime(tf),
                 (monday+timedelta(d+28)).strftime(tf),
                 (monday+timedelta(d+35)).strftime(tf)])
        if datetime.strptime(dates[0][-1], tf).month != self.today.month:
            for e in dates:
                gbg = e.pop()
        for e in dates:
            self.w.calendar.append_row(e)
            othermonth = []
            for c in self.w.calendar.lrows[-1]:
                if datetime.strptime(
                    str(c.text()), tf).month == self.today.month:
                    c.setStyleSheet(self.day_headss)
                else:
                    c.setStyleSheet(self.othermonth)
                    othermonth.append(self.w.calendar.lrows[-1].index(c))
                c.setAlignment(Qt.AlignCenter) # sole use of Qt.!
                c.selectable = False
            self.w.calendar.append_row(len(dates[0]) * [''])
            for c in self.w.calendar.lrows[-1]:
                if self.w.calendar.lrows[-1].index(c) in othermonth:
                    c.setStyleSheet(self.othermonth)
                    c.selectable = False
                else:
                    c.setWordWrap(False)
        stop = False
        todaycell = None # hierwei
        for r in xrange(0, 14, 2):
            for c in self.w.calendar.lrows[r]:
                if c.text() == self.today.strftime(tf):
                    c.setText('<b>' + c.text())
                    todaycell = c
                    stop = True
                    break
            if stop:
                break
        for c in xrange(len(dates[0])):
            self.w.calendar.set_colwidth(c, 182)
        data = self.get_monthdata(startday, enddt)
        sizeref = self.w.calendar.cell(0, 0)
        for e in data:
            csname, pname = self.getnames(e[3], e[4])
            entry = self.mkentry(
                (e[0], e[1], e[2], csname, pname, self.staff[e[5]]), True)
            for col in xrange(5):
                for c in self.w.calendar.column(col):
                    if c.text().count(e[1].strftime(tf)):
                        cell = self.w.calendar.cell(
                            self.w.calendar.column(col).index(c)+1, col)
                        ## if cell.entry:
                        self.mknewcell(cell, entry, e[0], e[6])
                        ## else:
                        ##     cell.setWordWrap(False)
                        ##     cell.elidetext(entry)
                        ##     cell.setToolTip(entry)
                        ##     cell.setdata(e[0]) # hierwei:
        if todaycell:
            self.w.calendar.select_cell(
                self.w.calendar.cell(todaycell.row()+1, todaycell.col))
        self.w.calendar.setFocus()
        
    def display_week(self):
        self.dis_dayweek()
        startday = self.today - timedelta(self.today.weekday())
        weekheads = [self.tr('week ') + self.today.strftime('%U')]
        for w in xrange(7):
            if startday + timedelta(w) == self.realday:
                a = '<b>'
            else:
                a = ''
            weekheads.append((startday + timedelta(w)).strftime(
                '{}%a %d.%m.%Y'.format(a)))
        self.w.calendar.set_headers(weekheads)
        for t in self.times:
            self.w.calendar.append_row(
                [t.strftime('%H:%M'), '', '', '', '', '', '', ''])
        colw = (self.w.calendar.width() - 
                (80 + self.w.calendar.verticalScrollBar().sizeHint().width()))/7
        self.w.calendar.set_colwidth(0, 80)
        for w in xrange(1, 8):
            self.w.calendar.align_header(w, 'c')
            self.w.calendar.set_colwidth(w, colw)
        for c in self.w.calendar.column(0):
            c.selectable = False
        data = self.get_weekdata(startday)
        sizeref = self.w.calendar.cell(0, 1)
        # 0 id  1 dt  2 text  3 cid  4 pid  5 staffid  6 status
        for e in data:
            csname, pname = self.getnames(e[3], e[4])
            entry = self.mkentry(
                (e[0], e[1], e[2], csname, pname, self.staff[e[5]]))
            for h in xrange(1, 8):
                for i, c in enumerate(self.w.calendar.column(0)):
                    if (e[1].strftime('%H:%M') == c.text() and
                        self.w.calendar.headers[h].text().count(
                            e[1].strftime('%d.%m.%Y'))):
                        cell = self.w.calendar.cell(i, h)
                        ## if cell.entry:
                        self.mknewcell(cell, entry, e[0], e[6])
                        ## else:
                        ##     cell.setWordWrap(False)
                        ##     cell.elidetext(entry)
                        ##     cell.setToolTip(entry)
                        ##     cell.setdata(e[0])
        if self.starttime is not None:
            selrow=self.times.index(self.starttime)
            self.w.calendar.select_cell(
                self.w.calendar.cell(row=selrow, col=self.today.weekday()+1))
            self.w.calendar.scrolltov(selrow)
        self.w.calendar.setFocus()
        
    def foreday(self):
        self.today += timedelta(1)
        self.sel_display()

    def foremonth(self):
        if self.today.day > 30 and self.today.month in (3,5,8,10):
            self.today = self.today.replace(day=30, month=self.today.month+1)
        elif self.today.month == 1 and self.today.day > 29:
            if self.isleap(self.today.year):
                self.today.replace(day=29, month=2)
            else:
                self.today.replace(day=28, month=2)
        elif self.today.month == 12:
            self.today = self.today.replace(year=self.today.year+1, month=1)
        else:
            self.today = self.today.replace(month=self.today.month+1)
        self.sel_display()

    def foreweek(self):
        self.today += timedelta(7)
        self.sel_display()
        
    def foreyear(self):
        if (self.isleap(self.today.year) and self.today.month == 2 and
            self.today.day == 29):
            self.today = self.today-timedelta(1)
        self.today = self.today.replace(year=self.today.year+1)
        ## self.w.calendar.selrow = None
        ## self.w.calendar.selcell = None
        self.sel_display()

    def get_basedata(self):
        self.logname = 'no login'
        self.logname = querydb(
            self,
            'select stf_logname from staff where stf_id=%s',(self.staffid,))
        if self.logname is None:  return # db error
        self.logname = self.logname[0][0]
        self.w.lLb.setText(self.logname)

    ##def alldata(self): # three times same query w/just minor change? simplify!

    def get_daydata(self):
        data = querydb(
            self,
            'select app_id,app_dt,app_text,app_cid,app_pid,app_staffid,'
            'app_status from appointments where app_dt between %s and %s {}'
            'order by app_dt,app_dur'.format(self.selstaff),
            (self.today,
             datetime.fromordinal(self.today.toordinal())+timedelta(1, -1)))
        if data is None:  return # db error
        return data

    def get_monthdata(self, startday, enddt):
        data = querydb(
            self,
            'select app_id,app_dt,app_text,app_cid,app_pid,app_staffid,'
            'app_status from appointments where app_dt between %s and %s {}'
            'order by app_dt,app_dur'.format(self.selstaff),
            (startday, enddt))
        if data is None:  return # db error
        return data

    def get_weekdata(self, startday):
        data = querydb(
            self,
            'select app_id,app_dt,app_text,app_cid,app_pid,app_staffid,'
            'app_status from appointments where app_dt between %s and %s {}'
            'order by app_dt,app_dur'.format(self.selstaff),
            (startday,
             datetime.fromordinal(startday.toordinal())+timedelta(6, -1)))
        if data is None:  return # db error
        return data
                           
    def getnames(self, cid, pid):
        if cid:
            csname = querydb(
                self,
                'select c_sname from clients where c_id=%s', (cid,))
            if csname is None:  return # db error
            csname = csname[0][0]
        else:
            csname = None
        if pid:
            pname = querydb(
                self,
                'select p_name from patients where p_id=%s', (pid,))
            if pname is None:  return # db error
            pname = pname[0][0].split(' ')[0]
        else:
            pname = None
        return (csname, pname)

    def gv_help(self, about):
        self.helpsig.emit(about)
        
    def gv_quit(self, quitnow=False):
        """Signal children if quitting GnuVet or not."""
        self.shutdown = quitnow
        self.gvquit.emit(quitnow) # ?
        if quitnow:
            self.close()

    def gv_quitconfirm(self):
        if self.gaia:
            self.gaia.gv_quitconfirm()
        else:
            for w in self.findChildren(QMainWindow):
                w.close()
            self.close()
    
    def help_self(self):
        self.helpsig.emit('appointment.html')

    def isleap(self, year):
        return year%4 == 0 and (year%100 != 0 or not year%400)

    def markopen(self):
        self.w.calendar.selcell.setStyleSheet("background: white")
        self.w.calendar.prevss = self.w.calendar.selcell.styleSheet()
        suc = querydb(
            self,
            'update appointments set app_status=%s where app_id=%s '
            'returning app_id', ('o', self.w.calendar.selcell.data))
        if suc is None:  return # db error
        self.db.commit()

    def markdone(self):
        self.w.calendar.selcell.setStyleSheet("background: lightgreen")
        self.w.calendar.prevss = self.w.calendar.selcell.styleSheet()
        suc = querydb(
            self,
            'update appointments set app_status=%s where app_id=%s '
            'returning app_id', ('d', self.w.calendar.selcell.data))
        if suc is None:  return # db error
        self.db.commit()

    def markmissed(self):
        self.w.calendar.selcell.setStyleSheet("background: red")
        self.w.calendar.prevss = self.w.calendar.selcell.styleSheet()
        suc = querydb(
            self,
            'update appointments set app_status=%s where app_id=%s '
            'returning app_id', ('m', self.w.calendar.selcell.data))
        if suc is None:  return # db error
        self.db.commit()
    
    def mkentry(self, e, datum=False):
        """Creates a tuple with text entries for a calendar entry."""
        if datum:
            start = e[1].strftime('%H:%M:\t')
        else:
            start = ''
        return (start + 
                (e[5] and (e[5] + ':\t') or '') +  # stf_short
                (e[4] and e[4] or '') +           # pname
                ((e[3] and e[4]) and ' ' or '') +
                (e[3] and e[3] or '') +           # csname
                (((e[3] or e[4]) and e[2]) and ', ' or '') +
                e[2]) # app_text

    def mknewcell(self, cell, entry, appid, appstat):
        # hierwei this in2 gtable? as add_entry or suchlike?
        nc = self.w.calendar.create_entry_cell(cell, '', cell.col, appid)
        nc.setWordWrap(False)
        nc.elidetext(entry)
        nc.setToolTip(entry)
        if appstat == 'd': # done
            nc.setStyleSheet("background: lightgreen")
        elif appstat == 'm': # missed
            nc.setStyleSheet("background: red")
        elif appstat == 'w': # waiting
            nc.setStyleSheet("background: orange")

    def opencli(self, cell):
        """Open client window."""
        cli = querydb(
            self,
            'select app_cid from appointments where app_id=%s',
            (self.w.calendar.selcell.data,))
        if cli is None:  return # db error
        if cli[0][0] is None:
            self.app_edit()
            return
        cli = cli[0][0]
        if self.gaia:
            self.gaia.opencli(cli)
        else: # devel
            if hasattr(self, 'wc'):
                self.wc.cid = cli
                self.wc.cli_data()
                self.wc.show()
                self.wc.raise_()
            else:
                import client # from client import Client?  Well, only devel
                self.wc = client.Client(self, cli)
                self.wc.show()

    def openpat(self, cell): # 141017 hierwei
        """Open patient window."""
        if not self.w.calendar.selcell.data:
            self.app_add()
            return
        pat = querydb(
            self,
            'select app_pid from appointments where app_id=%s',
            (self.w.calendar.selcell.data,))
        if pat is None:  return # db error
        if pat[0][0] is None:
            self.app_edit()
            return
        pat = pat[0][0]
        if self.gaia:
            self.gaia.openpat(pat)
        else: # devel:
            if hasattr(self, 'wp'):
                self.wp.pid = pat
                self.wp.pat_data()
                self.wp.show()
                self.wp.raise_()
            else:
                import patient
                self.wp = patient.Patient(self, pat)
                self.wp.show()

    def sel_date(self):
        if not hasattr(self, 'dateselw'):
            from datesel import Datesel
            self.dateselw = Datesel(self, self.today)
            self.dateselw.datesig.connect(self.setdate)
        else:
            self.dateselw.update_disp(self.today)
        self.dateselw.move(self.x()-20, self.y())
        self.dateselw.show()
        self.dateselw.raise_()

    def sel_day(self, c): # hierwei: testen
        if self.disp == 0: # week
            self.today = datetime.strptime(
                str(self.w.calendar.headers[c.col].text()).replace('<b>', ''),
                '%a %d.%m.%Y')
        elif self.disp == 2: # month
            self.today = datetime.strptime(
                str(self.w.calendar.lrows[c.row()-1][c.col].text()
                    ).replace('<b>', ''), '%a %d.%m.%Y')
        ## if self.w.calendar.selcell.data:
        ##     for a in (self.delA, self.editA, self.markM):
        ##         a.setEnabled(True)
        ## else:
        ##     for a in (self.delA, self.editA, self.markM):
        ##         a.setEnabled(False)
        self.ck_actions(c)
        
    def sel_display(self):
        if self.disp == 1: # day
            for b in (self.w.daybackPb, self.w.dayforePb,
                      self.w.weekbackPb, self.w.weekforePb):
                b.setEnabled(True)
            self.display_day()
        elif self.disp == 2: # month
            for b in (self.w.daybackPb, self.w.dayforePb,
                      self.w.weekbackPb, self.w.weekforePb):
                b.setEnabled(False)
            self.display_month()
        else: # week
            for b in (self.w.daybackPb, self.w.dayforePb):
                b.setEnabled(False)
            for b in (self.w.weekbackPb, self.w.weekforePb):
                b.setEnabled(True)
            self.display_week()

    def sel_today(self):
        self.today = self.realday
        self.sel_display()
        
    def set_staff(self, id):
        if not id:
            self.selstaff = ''
        else:
            self.selstaff = 'and app_staffid={} '.format(
                self.w.staffDd.itemData(id, 32).toInt()[0])
        self.sel_display()

    def setdate(self, newdate):
        self.today = newdate
        self.sel_display()

    def testmove(self):
        for row in xrange(9):
            self.w.calendar.cell(row, 3).setText('First Lines {}'.format(row))
        for row in xrange(4, 10):
            self.w.calendar.cell(row, 4).setText('Something {}'.format(row))
        for row in xrange(14, 20):
            self.w.calendar.cell(row, 4).setText('And more {}'.format(row))
        for row in xrange(40, 48):
            self.w.calendar.cell(row, 3).setText('Last lines {}'.format(row))
        for col in xrange(2, 5):
            self.w.calendar.cell(12, col).setText('Column fill {}'.format(col))
        for col in xrange(6, 8):
            self.w.calendar.cell(12, col).setText('And more {}'.format(col))

    def toggle(self):
        if self.w.dayRb.isChecked():
            self.disp = 1
        elif self.w.monthRb.isChecked():
            self.disp = 2
        else:
            self.disp = 0 # week
        self.sel_display()

    def warning(self, heading='', msg=''): # devel function
        if not hasattr(self, 'warnw'):
            from warn import Warning
        if not msg:
            msg = self.tr('Unspecified db error.')
        if not heading:
            heading = self.tr('GnuVet: Db Error')
        self.warnw = Warning(self, heading, msg)
            
    def develf(self):
        ## self.w.calendar.append_row(
        ##     len(self.w.calendar.lrows[0]) * [''])
        print('cell data:', self.w.calendar.selcell.data)

if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    a = QApplication([])
    a.setStyle('plastique')
    b = Appointer(today=datetime(2013,5,20))
    ## b = Appointer(today=datetime(2014,6,20))
    exit(a.exec_())

## Traceback (most recent call last):
##   File "appoint.py", line 769, in setapp
##     self.datefixw.data.disconnect(self.setapp)
## TypeError: disconnect() failed between 'data' and 'unislot'
#### see: there seems to have been some work done on this
