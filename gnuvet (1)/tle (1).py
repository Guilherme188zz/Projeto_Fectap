"""A QTextEdit with adjustable MaxLen.
QTextLEdit(parent=None, maxlen=0)
renders a QTextEdit with a size limit of maxlen characters.
When exceeding the limit the widget emits a 'filled' signal
and it won't accept any more characters.
If maxlen == 0, no text limitation takes place.
Alas, Qt doesn't know how to properly use the 'selection buffer'.
QTextLEdit.remainder() returns the number of remaining free chars.
"""
# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

# todo:
# hopefully nothing
from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QApplication, QTextEdit, QAction

class QTextLEdit(QTextEdit):

    filled = pyqtSignal()
    htmlstart = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n<html><head><meta name="qrichtext" content="1" /><style type="text/css">\np, li { white-space: pre-wrap; }\n</style></head><body style=" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;">\n<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">"""

    def __init__(self, parent=None, maxlen=0):
        super (QTextLEdit, self).__init__(parent)
        self.maxlen = maxlen
        ## debugA = QAction(self)
        ## debugA.setAutoRepeat(0)
        ## debugA.setShortcut('Ctrl+D')
        ## debugA.triggered.connect(self.develf)
        ## self.addAction(debugA)

    def has_colour(self, txt):
        if (txt.count('<span style=" color:#') and
            txt.count('<span style=" color:#') !=
            txt.count('<span style=" color:#000000;">')):
            return True
        return False
            
    def ck_text(self, cktxt=None):
        # stupid hack for most clever Qt colour management
        if cktxt is None:
            if not self.has_colour(self.toHtml()):
                return self.toPlainText()
            cktxt = self.toHtml()
        if self.has_colour(cktxt):
            txt = ''
            for i, s in enumerate( # prevent setting text color black
                self.toHtml().split('<span style=" color:#000000;">')):
                if not i%2:
                    txt += s
                else:
                    txt += s.replace('</span>', '', 1)
            return txt
        cktxt = str(cktxt)
        if cktxt.startswith('<!DOCTYPE HTML PUBLIC'):
            return cktxt.replace(self.htmlstart, '', 1)[:-18]
        return cktxt

    ## def develf(self):
    ##     pass
    
    def keyPressEvent(self, ev):
        if not self.maxlen:
            super(QTextLEdit, self).keyPressEvent(ev)
            return
        if ev.modifiers() == Qt.ControlModifier and ev.key() == Qt.Key_V:
            cbtxt = str(QApplication.clipboard().text().toLatin1())
            if not cbtxt:
                return # nothing to be done
            subtract = len(self.textCursor().selectedText())
            if (len(self.ck_text()) + len(self.ck_text(cbtxt)) - subtract >
                self.maxlen):
                chars = self.maxlen-len(self.ck_text())+subtract
                cbtxt = self.ck_text(cbtxt)[:chars]
                bt = self.textCursor() # cave: COPY of cursor
                bt.insertText(cbtxt)
                self.setTextCursor(bt)
            else:
                super(QTextLEdit, self).keyPressEvent(ev)
        elif ev.modifiers() == Qt.ControlModifier:
            super(QTextLEdit, self).keyPressEvent(ev)
        elif (len(self.ck_text())>=self.maxlen):
            if ev.key() == Qt.Key_Backspace or ev.key() == Qt.Key_Delete:
                super(QTextLEdit, self).keyPressEvent(ev)
        else:
            super(QTextLEdit, self).keyPressEvent(ev)

    def mousePressEvent(self, ev):
        if not self.maxlen or not QApplication.clipboard().supportsSelection():
            super(QTextLEdit, self).mousePressEvent(ev)
        elif ev.button() == Qt.MidButton:
            sltxt = str(QApplication.clipboard().text(1).toLatin1())
            if not sltxt:  return # nothing to be done
            if len(self.ck_text()+self.ck_text(sltxt)) > self.maxlen:
                sltxt = self.ck_text(sltxt)[
                    :self.maxlen-len(self.ck_text())]
                QApplication.clipboard().setText(sltxt, 1)
        else:
            super(QTextLEdit, self).mousePressEvent(ev)

    def remainder(self):
        if not self.maxlen:
            return
        return self.maxlen - len(self.ck_text())

if __name__ == '__main__':
    from PyQt4.QtGui import QMainWindow, QAction, QLabel
    class Pwersdf(QMainWindow):
        def __init__(self, parent=None):
            super(Pwersdf, self).__init__(parent)
            self.resize(180, 200)
            quitA = QAction(self)
            quitA.setShortcut('Ctrl+Q')
            self.addAction(quitA)
            quitA.triggered.connect(quit)
            ## showA = QAction(self)
            ## showA.setShortcut('Ctrl+S')
            ## self.addAction(showA)
            ## showA.triggered.connect(self.showf)
            self.b = QTextLEdit(self, maxlen=32)
            self.b.setGeometry(10, 10, 150, 150)
            self.c = QLabel('32', self)
            self.c.setGeometry(10, 160, 30, 30)
            self.b.textChanged.connect(self.disp_rest)
            self.show()

        def disp_rest(self):
            self.c.setText('{}'.format(self.b.remainder()))

        ## def showf(self):
        ##     print('\ncb content: {}'.format(QApplication.clipboard().text()))
        ##     print('pos now: {}'.format(self.b.textCursor().position()))

    a = QApplication([])
    b = Pwersdf()
    exit(a.exec_())
