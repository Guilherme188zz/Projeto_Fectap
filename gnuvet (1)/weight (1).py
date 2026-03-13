"""The weight registry and chart."""
# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

# todo:
# target weight line?
# printing

from datetime import date, datetime
from decimal import Decimal, ROUND_UP, ROUND_DOWN
from psycopg2 import OperationalError
from PyQt4.QtCore import Qt, QPointF, pyqtSignal
from PyQt4.QtGui import (QMainWindow, QPainter, QPolygonF, QWidget)
from keycheck import Keycheck
from util import ch_conn, newaction, querydb
from weight_ui import Ui_Weight

def D(arg=0):
    return Decimal(str(arg)).quantize(Decimal('0.000'))

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class Scale:
    """Calculate and build the scale for y axis."""
    def __init__(self, start=0, stop=10, step=1, ymax=10):
        addon = D(0)
        start = D(start)
        self.step = step
        if start < 0:
            addon = D(0) - start
            start = start + addon
        stop  = D(stop) - addon
        step  = D(step)
        self.slist = [start]
        self.idx = -1
        count = int(D(stop)/D(self.step))
        count += 1
        iterand = start
        for i in xrange(count):
            iterand += self.step
            if iterand > ymax+step:
                break
            self.slist.append(iterand)

    def __getitem__(self, idx):
        return self.slist[idx]
    
    def __iter__(self):
        return self

    def next(self):
        self.idx += 1
        if self.idx == len(self.slist):
            raise StopIteration
        return self.slist[self.idx]

class Circle(QWidget):
    """Small red circle to indicate entry to delete."""
    def __init__(self, parent):
        super(Circle, self).__init__(parent)
        self.setAutoFillBackground(0)

    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.setPen(Qt.red)
        painter.drawEllipse(QPointF(3, 3), 3, 3)
        painter.end()
        
class Parea(QWidget):
    """Paint Area."""
    def __init__(self, parent=None, p_name=''):
        super(Parea, self).__init__(parent)
        self.p_name = p_name
        self.setBackgroundRole(9) # QPalette.Base
        self.setAutoFillBackground(1)

    adding = False # PAREA
    deleting = False
    xres   = 1
    yoffset = 20
    yres   = 1

    def calcvals(self): # PAREA
        """Calculate the points relative to (0, 0) and build the graph."""
        self.graph = QPolygonF()
        if not len(self.weights):
            return
        self.points = []
        graphndx = 0
        self.points.append(Point())
        ymax = D(max([d[1] for d in self.weights]))
        ymin = D(min([d[1] for d in self.weights]))
        if ymax == ymin:
            size = D(0)
        else:
            size = (ymax-ymin).log10()
        wround = ROUND_DOWN
        if size < 0:
            wround = ROUND_UP
        step = 10**size.quantize(Decimal(0), rounding=wround)
        self.yscale = Scale((ymin-step).quantize(step), # PAREA
                            (ymax+step).quantize(step),
                            step, ymax)
        if len(self.weights) == 1:
            self.graph.insert(0, QPointF(-5, -5))
            self.graph.insert(1, QPointF(5, 5))
            self.graph.insert(2, QPointF(0, 0))
            self.graph.insert(3, QPointF(5, -5))
            self.graph.insert(4, QPointF(-5, 5))
            self.xres = 1
            self.yres = D(self.ypxl-50)/(self.yscale[-1]-self.yscale[0])
            transheight = ((self.weights[0][1]-self.yscale[0])*self.yres
                           +self.yoffset)
            self.graph.translate(0, transheight)
            self.dtres = 'days'
            return
        self.resolution()
        startx = self.weights[0][0]
        starty = self.weights[0][1] # PAREA
        qx = QPointF(0, self.wy())
        self.graph.insert(graphndx, qx)
        graphndx += 1
        for entry in self.weights[1:]:
            self.points.append(
                Point((getattr(entry[0] - startx, self.dtres) * self.xres),
                      ((entry[1] - starty) * self.yres)))
            self.graph.insert(graphndx,
                              QPointF((getattr(entry[0]-startx, self.dtres)
                                       * self.xres),
                                      self.wy((entry[1]-starty) * self.yres)))
            graphndx += 1
        transheight = (self.weights[0][1]-self.yscale[0])*self.yres+self.yoffset
        self.graph.translate(0, -transheight)

    def paintEvent(self, ev): # PAREA
        self.weights = self.parent().weights
        painter = QPainter(self)
        if not len(self.weights):
            painter.drawText(self.width()/4-40, self.height()/2-20,
                             self.p_name + self.tr(' weight chart: ') +
                             self.tr('no entries'))
            self.parent().w.delPb.setEnabled(0)
            self.parent().w.printPb.setEnabled(0)
            return
        self.xpxl = self.width() - 40
        self.ypxl = self.height() - 50
        self.calcvals()
        if not self.adding:
            self.parent().w.wSb.setValue(self.weights[-1][1])
        painter.drawText(5, 15, 'kg')
        painter.save()
        nfont = painter.font()
        nfont.setBold(1) # PAREA
        painter.setFont(nfont)
        painter.drawText(70, 20, self.p_name + ' weight chart')
        painter.restore()
        # the coordinate system w/ arrows
        painter.save()
        painter.translate(30, 10)
        painter.drawLine(0, self.wy(), self.xpxl-10, self.wy()) # x
        painter.drawLine(self.xpxl-10, self.wy(), self.xpxl-15, self.wy(-5))
        painter.drawLine(self.xpxl-10, self.wy(), self.xpxl-15, self.wy(5)) #xar
        painter.drawLine(0, self.wy(), 0, self.wy(self.ypxl-10)) # y
        painter.drawLine(0, self.wy(self.ypxl-10),
                         -5, self.wy(self.ypxl-15)) # yarrow1
        painter.drawLine(0, self.wy(self.ypxl-10),
                         5, self.wy(self.ypxl-15)) # yarrow2
        # y ticks
        if self.yscale[-1]._isinteger():
            maxscale = str(int(self.yscale[-1])) # PAREA
        else:
            maxscale = str(self.yscale[-1].normalize())
        yrect = painter.boundingRect(-30, self.wy(12), 0, 0,  1,
                                       maxscale)
        yrect.translate(0, -yrect.height())
        painter.setPen(Qt.lightGray)
        painter.drawLine(-5, self.wy(self.yoffset),
                         self.xpxl,  self.wy(self.yoffset))
        painter.setPen(Qt.black)
        painter.drawText(yrect, 2,
                         str(self.yscale[0].quantize(self.yscale.step)))
        for val in self.yscale[1:]:
            painter.setPen(Qt.lightGray)
            painter.drawLine(-5, self.wy((val-self.yscale[0])
                                         * self.yres + self.yoffset),
                             self.xpxl,  self.wy((val-self.yscale[0])
                                                 * self.yres + self.yoffset))
            painter.setPen(Qt.black) # PAREA
            yrect.translate(0, -self.yscale.step*self.yres)
            painter.drawText(yrect, 2, str(val.quantize(self.yscale.step)))
        # first date legend
        painter.save()
        font = painter.font()
        font.setPointSize(6)
        painter.setFont(font)
        painter.translate(-3, self.wy()+10)
        painter.rotate(90)
        if self.dtres == 'days': # PAREA
            painter.drawText(0, 0, self.weights[0][0].strftime('%d.%m.%y'))
        else:
            datetxt = self.weights[0][0].strftime('%d.%m.%y\n%H:%M')
            xrect = painter.boundingRect(0, 0, 0, 0, 2, datetxt)
            xrect.translate(xrect.width(), -xrect.height())
            painter.drawText(xrect, 2, datetxt)
        painter.restore()
        # first weight
        painter.save()
        if self.weights[0][1]._isinteger():
            weight = str(int(self.weights[0][1]))
        else:
            weight = str(self.weights[0][1].normalize())
        if self.weights[0][2]:
            weight = '(' + weight + ')'
        rects = []
        lrect = painter.boundingRect(0, 0, 0, 0, 1, weight) # PAREA
        lrect.translate(1, self.graph[0].y()-20)
        rects.append(lrect)
        painter.drawText(lrect, 2, weight)
        painter.restore()
        # further ticks and legends
        for point in self.points[1:]:
            secs = False
            painter.drawLine(point.x, self.wy(-5), point.x, self.wy())
            idx = self.points.index(point)
            if (self.weights[idx][0].strftime('%y') ==
                self.weights[idx-1][0].strftime('%y')):
                if not (self.weights[idx][0] -
                        self.weights[idx-1][0]).days:
                    datetxt = (self.weights[idx][0].strftime('%d.%m.\n%H:%M'))
                    secs = True
                else:
                    datetxt = (self.weights[idx][0].strftime('%d.%m.'))
            else: # PAREA
                datetxt = (self.weights[idx][0].strftime('%d.%m.%y'))
            painter.save()
            painter.translate(point.x-3, self.wy()+10)
            painter.setFont(font)
            painter.rotate(90)
            if secs:
                xrect = painter.boundingRect(0, 0, 0, 0, 2, datetxt)
                xrect.translate(xrect.width(), -xrect.height())
                painter.drawText(xrect, 2, datetxt)
            else:
                painter.drawText(0, 0, datetxt)
            painter.restore()
            if self.weights[idx][1]._isinteger():
                weight = str(int(self.weights[idx][1]))
            else:
                weight = str(self.weights[idx][1].normalize())
            if self.weights[idx][2]:
                weight = '(' + weight + ')' # PAREA
            painter.save()
            nrect = painter.boundingRect(0, 0, 0, 0, 1, weight)
            nrect.translate(point.x-10,
                            self.graph[idx].y()-20)
            for rect in rects:
                while nrect.intersects(rect):
                    nrect.translate(0, -10)
            painter.drawText(nrect, 1, weight)
            lrect = nrect
            rects.append(lrect) # PAREA
            painter.restore()
        # curve
        painter.setPen(Qt.blue)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPolyline(self.graph)
        painter.restore()
        painter.end()

    def resolution(self): # PAREA
        """Calculate resolution for weight data."""
        if (self.weights[-1][0] - self.weights[0][0]).days:
            self.xres = (D(self.xpxl-20)/
                         ((self.weights[-1][0]-self.weights[0][0]).days))
            self.dtres = 'days'
        elif (self.weights[-1][0] - self.weights[0][0]).seconds:
            self.xres = (D(self.xpxl-20)/
                         ((self.weights[-1][0]-self.weights[0][0]).seconds))
            self.dtres = 'seconds'
        self.yres = D(self.ypxl-50)/(self.yscale[-1] - self.yscale[0])

    def wy(self, p=0): # PAREA
        return 240 - p

class Weight(QMainWindow):
    """GnuVet Patient Weight Chart."""
    ds = '%d.%m.%Y %H:%M:%S' # WEIGHT
    helpsig = pyqtSignal(str)
    logname = 'No login'
    lweight = None
    wbackup = None
    weightchanged = pyqtSignal(tuple)

    def __init__(self, parent=None, pid=0, rip=False):
        super(Weight, self).__init__(parent)
        self.conns = {} # disconnect() w/o arg segfaults
        self.sigs = {}
        self.pid = pid
        self.weights = []
        self.w = Ui_Weight()
        self.w.setupUi(self)
        if parent:
            if parent.gaia == 'gaia':
                self.gaia = parent
            else:
                self.gaia = parent.gaia
            parent.dbstate.connect(self.db_state)
            self.db = parent.db
            self.staffid = parent.staffid
            self.helpsig.connect(parent.gv_help)
        else:
            import dbmod
            dbh = dbmod.Db_handler('enno')
            self.db = dbh.db_connect()
            self.staffid = 1
        try:
            self.curs = self.db.cursor()
        except AttributeError: # no db connection
            self.db_state()
            return
        self.logname = querydb(
            self, 'select stf_logname from staff where stf_id=%s',
            (self.staffid,))
        if self.staffid is None:  return # db error
        self.logname = self.logname[0][0]
        self.w.lLb.setText(self.logname)
        pname = querydb(
            self, 'select p_name from patients where p_id=%s', (pid,))
        if pname is None:  return # db error
        pname = pname[0][0]
        self.fetchdata()
        self.ck_size()
        self.w.closePb.clicked.connect(self.close)
        self.w.addPb.setDefault(True)
        self.w.addPb.setAutoDefault(True)
        if rip:
            for w in (self.w.dLb, self.w.wDe, self.w.wLb, self.w.wSb,# WEIGHT
                         self.w.estCb, self.w.addPb, self.w.delPb):
                w.setEnabled(0)
        else:
            ch_conn(self, 'addpb', self.w.addPb.clicked, self.weight_addconfirm)
            self.w.delPb.clicked.connect(self.weight_delconfirm)
            self.w.confirmPb.clicked.connect(self.weight_add)
            self.w.confirm_cancelPb.clicked.connect(self.weight_add_cancel)
            self.ck_weight()
            self.w.wSb.valueChanged.connect(self.ck_weight)
            self.w.entrydel_cancelPb.clicked.connect(self.weight_del_cancel)
            self.w.periodPb.clicked.connect(self.date_select)
        dt = datetime.now() # WEIGHT
        self.w.wDe.setDateTime(dt)
        self.w.wDe.setMaximumDate(dt)
        closeA = newaction(self, short='Ctrl+W')
        helpA = newaction(self, short='F1')
        quitA = newaction(self, short='Ctrl+Q')
        self.addAction(closeA)
        self.addAction(helpA)
        self.addAction(quitA)
        closeA.triggered.connect(self.close)
        helpA.triggered.connect(self.help)
        quitA.triggered.connect(self.gv_quitconfirm)
        self.parea = Parea(self, pname)
        self.parea.setGeometry(20, 50, self.width()-40, 300)
        self.parea.setSizePolicy(0, 0)
        self.ck_dates()
        self.w.confirm.hide()
        self.w.confirm.raise_()
        self.w.datesel.hide()
        self.w.datesel.raise_()
        self.w.entrydelLb.hide()
        self.w.entrydelDd.hide()
        self.w.entrydelPb.hide() # WEIGHT
        self.w.entrydel_cancelPb.hide()
        self.circle = Circle(self)
        dip = 7
        self.circle.setGeometry(0, 0, dip, dip)
        self.circle.hide()
        self.w.dsel_cancelPb.clicked.connect(self.datesel_cancel)
        self.w.dselPb.clicked.connect(self.dates)
        self.keycheck = Keycheck(self)
        self.installEventFilter(self.keycheck)
        ch_conn(self, 'enter', self.keycheck.enter, self.w.addPb.click)
        ch_conn(self, 'esc', self.keycheck.esc, self.close)

    def adjust_circle(self, idx): # WEIGHT
        """Place red circle around entry to be deleted."""
        point = self.parea.graph[idx]
        point += QPointF(47, 56)
        point = point.toPoint()
        self.circle.move(point)
        self.circle.show()
        self.w.entrydelPb.setEnabled(
            self.staffid == self.weights[idx][3] and True
            or self.staffid == 1)
        if self.w.entrydelPb.isEnabled():
            self.w.entrydelPb.setToolTip(self.tr('Delete selected entry'))
        else:
            self.w.entrydelPb.setToolTip(
                self.tr('Only GnuVet Master can delete entry '
                        'from different staff member'))
    
    def ck_dates(self): # WEIGHT
        """If less than 5 entries, disable period selection.  Overkill?"""
        if self.wbackup is None:
            weights = self.weights
        else:
            weights = self.wbackup
        if len(weights) < 5:
            self.w.periodPb.setEnabled(0)
            return
        if self.w.closePb.isEnabled():
            self.w.periodPb.setEnabled(1)
                
    def ck_weight(self, val=False): # WEIGHT
        """Weight Zero -> no entry."""
        self.w.addPb.setEnabled(val)

    def ck_size(self):
        if 5 < len(self.weights) < 11:
            self.resize(100 * len(self.weights), 400)
        elif len(self.weights) > 10:
            self.resize(1000, 400)
        elif len(self.weights) < 6:
            self.resize(500, 400)
        if hasattr(self, 'parea'):
            self.parea.resize(self.width()-40, 300)

    def date_select(self): # WEIGHT
        """Prepare selection of date period to display."""
        self.enable(0)
        ch_conn(self, 'lodd')#, self.w.loDd.currentIndexChanged)
        ch_conn(self, 'hidd')#, self.w.hiDd.currentIndexChanged)
        ch_conn(self, 'enter', self.keycheck.enter, self.w.dselPb.click)
        ch_conn(self, 'esc', self.keycheck.esc, self.w.dsel_cancelPb.click)
        if self.wbackup is None:
            weights = self.weights
        else:
            weights = self.wbackup
        self.w.loDd.clear()
        self.w.hiDd.clear()
        self.lodates = []
        self.hidates = []
        for entry in weights:
            if entry != weights[-1]:
                self.w.loDd.addItem(entry[0].strftime('%d.%m.%Y %H:%M:%S'))
                self.lodates.append(entry[0])
            if entry != weights[0]:
                self.w.hiDd.addItem(entry[0].strftime('%d.%m.%Y %H:%M:%S'))
                self.hidates.append(entry[0])
        self.w.hiDd.setCurrentIndex(self.w.hiDd.count()-1)
        ch_conn(self, 'lodd',
                self.w.loDd.currentIndexChanged, self.dates_adjust_hi)
        ch_conn(self, 'hidd',
                self.w.hiDd.currentIndexChanged, self.dates_adjust_lo)
        self.w.datesel.show() # WEIGHT
        self.w.dselPb.setDefault(1)
        
    def dates(self): # WEIGHT
        """Display selected date range."""
        ch_conn(self, 'enter', self.keycheck.enter, self.w.addPb.click)
        ch_conn(self, 'esc', self.keycheck.esc, self.close)
        if self.wbackup is None:
            self.wbackup = self.weights
        self.weights = [] # new assignment, thus above works without [:]?
        for entry in self.wbackup:
            if (entry[0] >= self.lodates[self.w.loDd.currentIndex()]
                and
                entry[0] <= self.hidates[self.w.hiDd.currentIndex()]):
                self.weights.append(entry)
        self.w.datesel.hide()
        if self.wbackup == self.weights: # WEIGHT
            self.wbackup = None
        self.ck_size()
        self.enable()

    def dates_adjust_hi(self, idx): # WEIGHT
        """Adjust hiDd to selected date in loDd."""
        ch_conn(self, 'hidd')#, self.w.hiDd.currentIndexChanged)
        if self.wbackup is None:
            weights = self.weights
        else:
            weights = self.wbackup
        mem = self.w.hiDd.currentText()
        self.w.hiDd.clear()
        self.hidates = []
        for entry in weights:
            if entry[0] <= self.lodates[self.w.loDd.currentIndex()]:
                continue # WEIGHT
            self.w.hiDd.addItem(entry[0].strftime(self.ds))
            self.hidates.append(entry[0])
        nidx = self.w.hiDd.findText(mem)
        if nidx == -1:
            self.w.hiDd.setCurrentIndex(self.w.hiDd.count() - 1)
        else:
            self.w.hiDd.setCurrentIndex(nidx)
        ch_conn(self, 'hidd',
                self.w.hiDd.currentIndexChanged, self.dates_adjust_lo)

    def dates_adjust_lo(self, idx):
        """Adjust loDd to selected date in hiDd."""
        ch_conn(self, 'lodd')#, self.w.loDd.currentIndexChanged)
        if self.wbackup is None:
            weights = self.weights
        else:
            weights = self.wbackup
        mem = self.w.loDd.currentText()
        self.w.loDd.clear()
        self.lodates = []
        for entry in weights:
            if entry[0] < self.hidates[self.w.hiDd.currentIndex()]:
                self.w.loDd.addItem(entry[0].strftime(self.ds))
                self.lodates.append(entry[0])
            continue
        nidx = self.w.loDd.findText(mem)
        if nidx == -1:
            self.w.loDd.setCurrentIndex(0)
        else: # WEIGHT
            self.w.loDd.setCurrentIndex(self.w.loDd.findText(mem))
        ch_conn(self, 'lodd',
                self.w.loDd.currentIndexChanged, self.dates_adjust_hi)
    
    def datesel_cancel(self): # WEIGHT
        ch_conn(self, 'enter', self.keycheck.enter, self.w.addPb.click)
        ch_conn(self, 'esc', self.keycheck.esc, self.close)
        self.w.datesel.hide()
        self.enable()

    def db_state(self, db=None): # WEIGHT
        """Actions to take on db loss and gain."""
        self.db_err = not db and True or False
        for w in (self.w.dLb, self.w.wDe, self.w.wSb, self.w.wLb, self.w.estCb,
                  self.parea, self.w.delPb, self.w.periodPb):
            w.setEnabled(not self.db_err)
        self.db = db
        if self.db_err:
            self.w.addPb.setText(self.tr('&Reconnect'))
            ch_conn(self, 'addpb', self.w.addPb.clicked, self.reconnect)
            self.curs = None
        else:
            self.w.addPb.setText(self.tr('&Add'))
            ch_conn(self, 'addpb', self.w.addPb.clicked, self.weight_add)
            try:
                self.curs = self.db.cursor()
            except OperationalError:
                self.db = None
                self.curs = None

    def enable(self, ok=True):
        for w in (self.parea, self.w.addPb, self.w.delPb, self.w.periodPb,
                  self.w.printPb, self.w.closePb, self.w.dLb, self.w.wDe,
                  self.w.wSb, self.w.wLb, self.w.estCb):
            w.setEnabled(ok)
        self.w.addPb.setDefault(ok)
        self.ck_dates()
        
    def fetchdata(self): # WEIGHT
        self.weights = querydb(
            self,
            'select w_dt,w_weight,w_est,w_staff from weights where w_pid=%s '
            'order by w_dt', (self.pid,))
        if self.weights is None:  return # db error
        self.lweight = self.weights[-1][:3]

    def gv_quitconfirm(self):
        if self.parent():
            self.parent().gv_quitconfirm()
        else:
            exit()

    def help(self):
        self.helpsig.emit('weight.html')
        
    def resizeEvent(self, ev):
        self.w.lLb.move(self.width()-90, 5)

    def weight_add(self): # WEIGHT
        """Add weight entry to db and list."""
        wdt = self.w.wDe.dateTime().toPyDateTime()
        ## wdt = datetime(
        ##     wdt.year, wdt.month, wdt.day, wdt.hour, wdt.minute, wdt.second)
        suc = querydb(
            self,
            'insert into weights(w_pid,w_dt,w_est,w_weight,w_staff)values'
            '(%s, %s, %s, %s, %s)returning w_id',
            (self.pid, wdt, self.w.estCb.isChecked(),
             self.w.wSb.value(), self.staffid))
        if suc is None:  return # db error
        self.db.commit()
        addition = (wdt,
                    D(self.w.wSb.value()),
                    self.w.estCb.isChecked(), # WEIGHT
                    self.staffid)
        if self.wbackup == self.weights:
            self.wbackup = None
        if self.wbackup is None:
            weights = self.weights
        else:
            weights = self.wbackup
            # sort out if parea.weights should contain new entry:
            if (self.weights[0][0] < addition[0]
                and self.weights[-1][0] > addition[0]):
                self.weights.append(addition)
                self.weights.sort(key=lambda entry: entry[0])
        weights.append(addition)
        weights.sort(key=lambda entry: entry[0])
        self.parea.adding = False
        self.w.confirm.hide()
        self.enable() # WEIGHT
        ch_conn(self, 'enter', self.keycheck.enter, self.w.addPb.click)
        ch_conn(self, 'esc', self.keycheck.esc, self.close)
        self.ck_size()
        if self.lweight != weights[-1][:3]:
            self.weightchanged.emit(weights[-1][:3])
    
    def weight_addconfirm(self): # WEIGHT
        """Confirm adding weight."""
        ch_conn(self, 'enter', self.keycheck.enter, self.w.confirmPb.click)
        ch_conn(self, 'esc', self.keycheck.esc, self.w.confirm_cancelPb.click)
        self.parea.adding = True
        self.enable(0)
        self.w.confirmLb.setText(self.tr(
            self.w.wDe.dateTime().toString("d.M.yyyy hh:mm:ss") + '  ' + (
                self.w.wSb.value().is_integer() and
                str(int(self.w.wSb.value())) or
                str(self.w.wSb.value())) + ' kg'))
        self.w.confirm.show()
        self.w.confirmPb.setDefault(1)

    def weight_add_cancel(self): # WEIGHT
        ch_conn(self, 'enter', self.keycheck.enter, self.w.addPb.click)
        ch_conn(self, 'esc', self.keycheck.esc, self.close)
        self.parea.adding = False
        self.w.confirm.hide()
        self.enable()
        
    def weight_del(self): # WEIGHT
        """Delete selected entry from db and list."""
        self.circle.hide()
        wdt = self.delentries[self.w.entrydelDd.currentIndex()]
        weight = str(self.w.entrydelDd.currentText()).split()[2]
        suc = querydb(
            self,
            'delete from weights where w_pid=%s and w_dt=%s and w_weight=%s',
            (self.pid, wdt, D(weight)))
        if suc is None:  return # db error
        self.db.commit()
        self.weight_del_action(self.weights, wdt, weight)
        self.weight_del_action(self.wbackup, wdt, weight)
        self.ck_size()
        self.weight_del_cancel()

    def weight_del_action(self, weights, wdt, weight): # WEIGHT
        """Delete selected entry from internal lists."""
        if weights == None:
            return
        idx = None
        for entry in weights:
            if entry[0] == wdt and entry[1] == D(weight):
                idx = weights.index(entry)
                break
        if idx is None:
            pass
        else:
            weights.__delitem__(idx)
        if self.lweight != weights[-1][:3]:
            self.weightchanged.emit(weights[-1][:3])

    def weight_del_cancel(self): # WEIGHT
        ch_conn(self, 'enter', self.keycheck.enter, self.w.addPb.click)
        ch_conn(self, 'esc', self.keycheck.esc, self.close)
        self.w.entrydelLb.hide()
        self.w.entrydelDd.hide()
        self.w.entrydelPb.hide()
        self.w.entrydel_cancelPb.hide()
        self.circle.hide()
        self.w.dLb.show()
        self.w.wDe.show()
        self.w.wSb.show()
        self.w.wLb.show()
        self.w.estCb.show()
        self.parea.deleting = False
        self.enable()
    
    def weight_delconfirm(self): # WEIGHT
        """Prepare deleting an entry."""
        self.enable(0)
        self.parea.deleting = True
        ch_conn(self, 'edeldd')#, self.w.entrydelDd.currentIndexChanged)
        self.w.entrydelDd.clear()
        self.delentries = []
        ch_conn(self, 'edelpb', self.w.entrydelPb.clicked, self.weight_del)
        for entry in self.weights:
            if entry[1]._isinteger():
                weight = str(int(entry[1]))
            else:
                weight = str(entry[1].normalize())
            self.w.entrydelDd.addItem(
                entry[0].strftime(self.ds) + '  ' + weight + ' kg')
            self.delentries.append(entry[0]) # WEIGHT
        ch_conn(self, 'edeldd',
                self.w.entrydelDd.currentIndexChanged, self.adjust_circle)
        self.w.entrydelDd.setCurrentIndex(self.w.entrydelDd.count() - 1)
        self.w.dLb.hide()
        self.w.wDe.hide()
        self.w.wSb.hide()
        self.w.wLb.hide()
        self.w.estCb.hide()
        ch_conn(self, 'enter', self.keycheck.enter, self.w.entrydelPb.click)
        ch_conn(self, 'esc', self.keycheck.esc, self.w.entrydel_cancelPb.click)
        self.w.entrydelLb.show()
        self.w.entrydelDd.show()
        self.w.entrydelPb.show()
        self.w.entrydel_cancelPb.show()
        self.w.entrydelPb.setDefault(1) # WEIGHT

if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    a = QApplication([])
    a.setStyle('plastique')
    w = Weight(None, pid=1)
    w.show()
    exit(a.exec_())
