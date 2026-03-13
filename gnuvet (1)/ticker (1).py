"""QTimer replacement.
Intended to deliver a sufficiently precise clock source for ch documentation.
Relies on system clock."""

# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

from threading import Timer
from datetime import datetime, timedelta
from PyQt4.QtCore import pyqtSignal, QObject

class Ticker(QObject):
    uid = 0
    count = 0
    criterion = timedelta(0, 0, 1e3)
    divisor = 10
    running = False
    tick = pyqtSignal()
    timediff = timedelta(0)
    
    def __init__(self, parent=None, timeout=1, counter=10):
        """timeout: seconds for tick, counter: timeouts for correction."""
        self.__class__.uid += 1 # this counts the instances of the class
        super(Ticker, self).__init__(parent)
        self.parent = parent
        self.timeout = timeout
        self.counter = counter # after counter: adjust timeout
        self.tc = 0 # time correction

    def run(self):
        if self.running:
            return
        self.running = True
        self.now = datetime.now()
        self.tick.connect(self.update_time)
        self.tickit()

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.tick.disconnect(self.update_time)
        self.count = 0
        if hasattr(self, 't'):
            self.t.cancel()

    def tickit(self):
        """Run a timer for timeout (imprecise), then start a new timer."""
        self.count += 1
        self.tick.emit()
        if self.count == self.counter:
            self.count = 0
            now = datetime.now()
            td = now - self.now
            if td > self.criterion: # self.now behind -> decrease timeout
                self.tc = -1e-6 * (td/self.divisor).microseconds
            elif abs(td) > self.criterion: # self.now ahead -> increase timeout
                self.tc = 1e-6 * (td/self.divisor).microseconds
            else:
                self.tc = 0
        self.t = Timer(self.timeout+self.tc, self.tickit)
        self.t.setName('Thread-' + str(self.uid))
        self.t.start()

    def update_time(self):
        self.now += timedelta(0, 1)

if __name__ == '__main__':
    from PyQt4.QtGui import QAction, QDateTimeEdit, QMainWindow, QRadioButton
    class Display(QMainWindow):
        def __init__(self, parent=None):
            super(QMainWindow, self).__init__(parent)
            self.resize(210, 80)
            self.dDte = QDateTimeEdit(self)
            self.dDte.setGeometry(5, 5, 200, 28)
            self.dDte.setDisplayFormat('dd.MM.yyyy hh:mm:ss')
            self.runRb = QRadioButton('&Run', self)
            self.runRb.setGeometry(5, 35, 80, 24)
            self.stopRb = QRadioButton('&Stop', self)
            self.stopRb.setGeometry(90, 35, 80, 24)
            quitA = QAction('quit', self)
            quitA.setAutoRepeat(0)
            quitA.setShortcut('Ctrl+Q')
            quitA.triggered.connect(self.killme)
            self.addAction(quitA)
            self.rtime = datetime.now() - timedelta(0, .8)
            self.rundt = self.rtime
            self.dDte.setDateTime(self.rundt)
            self.dDte.dateTimeChanged.connect(self.settime)
            self.ticker = Ticker(self, 1, 5)
            self.ticker.tick.connect(self.update_time)
            self.ticker.run(True)
            self.runRb.setChecked(1)
            self.runRb.clicked.connect(self.toggle)
            self.stopRb.clicked.connect(self.toggle)
            self.show()
            
        def killme(self):
            self.ticker.stop()
            self.close()
            print('Bye')

        def settime(self, time):
            time = time.toPyDateTime()
            self.ticker.stop()
            self.rundt = time
            self.ticker.timediff =  self.rundt - self.rtime
            self.ticker.run()

        def update_time(self):
            self.rtime += timedelta(0, 1)
            self.rundt = self.rtime + self.ticker.timediff
            self.dDte.dateTimeChanged.disconnect(self.settime)
            self.dDte.setDateTime(self.rundt)
            self.dDte.dateTimeChanged.connect(self.settime)

        def toggle(self):
            if self.stopRb.isChecked():
                self.ticker.stop()
            else:
                self.ticker.run()

    from PyQt4.QtGui import QApplication
    a = QApplication([])
    w = Display()
    exit(a.exec_())
