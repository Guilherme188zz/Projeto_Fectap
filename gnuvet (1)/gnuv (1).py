#!/usr/bin/python
"""The GnuVet main program."""
# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

# TODO:
# add ch_conn?
# special search (medication, clin hist)
# adapt knowledge to login|gv_auth()
# Add group/institution in payment -- for TGD|Racetrack etc.?

from sys import argv, platform, stderr
from os import path as os_path
from getopt import gnu_getopt, GetoptError
from datetime import date
from PyQt4.QtGui import (QMainWindow, QLabel, QFont, QApplication)
from PyQt4.QtCore import pyqtSignal
from util import newaction, querydb

import dbmod
import gv_qrc
import gv_version
from keycheck import Keycheck
from main_ui import Ui_Mainform

class Gnuv_MainWin(QMainWindow):
    """The GnuVet Main Window."""
    # signals
    gvquit = pyqtSignal(bool)
    dbstate  = pyqtSignal(object)
    ##helpsig  = pyqtSignal(str) ?
    # addcli       = pyqtSignal(tuple)
    # addedcli     = pyqtSignal(tuple)
    # patid        = pyqtSignal(int)

    # instance vars
    cwins   = 0 # client windows
    db      = None
    dbhost  = None
    gaia  = 'gaia'
    staffid = None
    user    = None  # are we authenticated?
    x_pos, y_pos = 100, 50

    def __init__(self, options={}):
        super(Gnuv_MainWin, self).__init__(None)
        self.w = Ui_Mainform()
        self.w.setupUi(self)
        self.options = options
        self.offspring = []    # visible children for gv_quitconfirm
        ## self.syspath, self.userdir, self.optfile = None ?
        self.w.yesPb.clicked.connect(self.gv_exit)
        self.w.noPb.clicked.connect(self.gv_quitno)
        #    ACTIONS
        # devel:
        debugA = newaction(caller=self, short='Ctrl+D')
        self.addAction(debugA)
        debugA.triggered.connect(self.debugf)
        # end devel
        self.appointA = newaction(
            self, '&Appointments', 'Open appointment diary', 'Ctrl+A')
        self.dbA = newaction(
            self, '&Reconnect to db', 'Try to reconnect to database', 'Ctrl+R')
        self.cliA = newaction(self, '&Clients', 'Search for Clients', 'Ctrl+C')
        self.patA = newaction(
            self, '&Patients', 'Search for Patients', 'Ctrl+P')
        self.payconfA = newaction( # hierwei: implement
            self, 'Confirm Pa&yments',
            'Confirm deferred payments like Credit Card etc.', 'Ctrl+Y')
        self.ssearchA = newaction( # hierwei: implement
            self, '&Special Search',
            'Search in medication/clinical history/seen date etc.', 'Ctrl+S')
        self.vaccremA = newaction(
            self, '&Vacc. Reminders', 'Check vacc. reminders', 'Ctrl+V')
        #    ETC.PP.:
        # ordA jouA finA medA srvA sysA stkA
        chuserA = newaction(
            self, 'Change &User', 'Login as different user', 'Ctrl+U')
        quitA = newaction(self, '&Quit', 'Exit GnuVet', 'Ctrl+Q')
        helpA = newaction(self, '&Help', 'context sensitive Help', 'F1')
        aboutA = newaction(self, 'About &GnuVet', 'GnuVet version information')
        #    MENUS
        self.w.taskM.addAction(self.dbA)
        self.w.taskM.addSeparator()
        self.w.taskM.addAction(self.patA)
        self.w.taskM.addAction(self.cliA)
        self.w.taskM.addSeparator()
        self.w.taskM.addAction(self.appointA)
        self.w.taskM.addAction(self.payconfA)
        self.w.taskM.addAction(self.vaccremA)
        # ordA Sep jouA finA
        self.w.taskM.addSeparator()
        self.w.taskM.addAction(self.ssearchA)
        self.w.taskM.addSeparator()
        self.w.taskM.addAction(chuserA)
        self.w.taskM.addAction(quitA)
        self.w.taskM.setSeparatorsCollapsible(1)
        # maintM: medA srvA sysA stkA userA
        self.w.helpM.addAction(helpA)
        self.w.helpM.addSeparator()
        self.w.helpM.addAction(aboutA)
        #    CONNECTIONS
        self.dbA.triggered.connect(self.db_reconnect)
        self.patA.triggered.connect(self.sae_patwrap)
        self.cliA.triggered.connect(self.sae_cliwrap)
        self.vaccremA.triggered.connect(self.vacc_reminders)
        self.appointA.triggered.connect(self.openapp)
        # self.appointA ordA jouA finA medA srvA sysA stkA
        chuserA.triggered.connect(self.chuser)
        quitA.triggered.connect(self.gv_quitconfirm)
        helpA.triggered.connect(self.gv_helpself)
        aboutA.triggered.connect(self.about)
        #    INIT
        self.keycheck = Keycheck(self)
        self.installEventFilter(self.keycheck)
        #    LOGIN
        #self.gv_authq()
        # devel:
        self.user = 'enno'
        self.staffid = 1
        self.db_connect(self.user)
        if self.db:
            self.w.lLb.setText(self.user)
        if not(hasattr(self, 'warnw') and self.warnw.isVisible()):
            self.show()
        # end devel

    def about(self):
        """Launch 'About' window: quite useless but common."""
        if hasattr(self, 'aboutw'):
            self.aboutw.show()
        else:
            import gv_about
            lang = ('lang' in self.options and self.options['lang'] or 'en')
            self.aboutw = gv_about.About(self, lang)

    def chuser(self):
        """Login as different user, closing all open windows but main."""
        if self.db and not isinstance(self.db, str):
            if hasattr(self.db, 'close'):
                self.db.close()
        for window in self.findChildren(QMainWindow):
            window.close()
        self.user = None
        self.passwd = None
        self.w.lLb.setText(self.tr('no login'))
        self.w.no_dbconn.show()
        self.gv_authq()

    def closeEvent(self, event):
        event.ignore()
        self.gv_quitconfirm()

    def db_connect(self, user=None, passwd=None, dbhost=None):
        args = {}
        if user:
            args['user'] = user
            self.user = user
        if passwd:
            args['passwd'] = passwd
        if dbhost:
            args['host'] = dbhost
        self.dbh = dbmod.Db_handler(**args)
        ## # devel:
        ## self.user = user
        ## self.dbhost = dbhost
        ## # end devel
        self.db = self.dbh.db_connect()
        if not self.db or isinstance(self.db, str):
            self.db_state(self.db)
            return
        self.user = user
        self.dbhost = dbhost
        self.dbdep_enable()
        self.curs = self.db.cursor()
        res = querydb(
            self,
            'select stf_func,stf_id from staff where stf_logname=%s',
            (user,))
        if res is None:  return # db error, self.db_state has been called
        res = self.curs.fetchall()
        if not res:
            return
        self.staffrole, self.staffid = res[0]
        # devel:
        self.staffid = 1

    def db_reconnect(self):
        """Try reconnecting to db."""
        args = {}
        if self.user:
            args['user'] = self.user
        if self.dbhost:
            args['host'] = self.dbhost
        self.w.lognameLe.setText(self.user)
        self.w.logpassLe.setFocus()
        self.gv_authq()
        self.dbstate.emit(self.db)

    def db_state(self, msg=''):
        """Actions to be taken on db loss or gain."""
        dberr = msg and True or False
        self.w.no_dbconn.setVisible(dberr)
        self.dbdep_enable(not dberr)
        if dberr:
            self.db = None
            if not hasattr(self, 'warnw'):
                from warn import Warning
            self.warnw = Warning(self, self.tr('GnuVet: Db Error'), msg)
            if not self.isVisible():
                self.warnw.closed.connect(self.show)
            self.w.statusbar.clearMessage()
            self.dbstate.emit(None) # new 141120
    
    def dbdep_enable(self, yes=True):
        """En- or disable db dependent features, signal children of db state."""
        self.patA.setEnabled(yes)
        self.cliA.setEnabled(yes)
        self.ssearchA.setEnabled(yes)
        self.appointA.setEnabled(yes)
        # ordA jouA finA medA srvA sysA stkA
        self.w.maintM.setEnabled(yes)
        self.dbA.setVisible(not yes)
        self.dbA.setEnabled(not yes)
        if yes:
            self.w.statusbar.showMessage(self.tr('Ready ...'), 10000)
        self.w.no_dbconn.setVisible(not yes)

    def debugf(self):
        pass

    def gvdir_check(self):
        """Check working dir (at startup), create if necessary."""
        # win: (winApiPath, 'gnuvet')
        # mac: (homePath, 'Library/Preferences/gnuvet')
        # *nx: ('/usr/share/gnuvet' or '~' + /.gnuvet)
        if not 'sysinfo' in locals():
            from util import sysinfo
        self.syspath, self.userdir, self.optfile, self.system = sysinfo()
        # e.g. '/usr/share/gnuvet', '.gnuvet', '.options'
        if self.staffid == 1:
            self.userdir = self.syspath
        else:
            self.userdir = '~' + self.user
            if os_path.expanduser(home) != home:
                self.userdir = os_path.join(
                    os_path.expanduser(home), self.userdir)
            ## else: # no such user on system, shouldn't happen
            ##     self.userdir = None
        if not 'os_access' in locals():
            from os import access as os_access
        if not os_path.exists(self.userdir):
            if not 'os_mkdir' in locals():
                from os import mkdir as os_mkdir
            try:
                os_mkdir(self.userdir)
            except OSError as e:
                stderr.write('Couldn\'t create dir "{}"\n{}\n'.format(
                    self.userdir, e))
                exit(13)
        elif not os_path.isdir(self.userdir):
            if not 'os_rename' in locals():
                from os import rename as os_rename
            try:
                os_rename(self.userdir, self.userdir + '.bak')
                stderr.write('WARN: renamed existing file "{0}" to '
                             '"{0}.bak"\n'.format(self.userdir))
            except OSError as e:
                stderr.write('Couldn\'t rename "{0}" to "{0}.bak"\n{1}\n'.
                             format(self.userdir, e))
                exit(13)
            if not 'os_mkdir' in locals():
                from os import mkdir as os_mkdir
            try:
                os_mkdir(self.userdir)
            except OSError as e:
                stderr.write(
                    'Couldn\'t create dir "{}"!\n{}\n'.format(self.userdir, e))
                exit(13)
        elif not os_access(self.userdir, 7):
            stderr.write('WARN: Directory "{}" is not writeable!\n'.
                         format(self.userdir))
            exit(13)

    def gv_auth(self):
        """Try connecting to db with given user and pass."""
        user = str(self.w.lognameLe.text().toLatin1())
        passwd = str(self.w.logpassLe.text().toLatin1())
        self.w.lognameLe.setText('')
        self.w.logpassLe.setText('')
        self.w.lognameLe.setFocus()
        dbhost = 'dbhost' in self.options and self.options['dbhost'] or None
        self.db_connect(user, passwd, dbhost)
        if not self.db or isinstance(self.db, str):
            self.w.statusbar.showMessage(self.tr('Login incorrect'), 20000)
            self.staffid = None
        else:
            self.w.lFr.setEnabled(0)
            self.w.lFr.hide()
            self.w.lLb.setText(user)
            self.w.logokPb.clicked.disconnect(self.gv_auth)
            self.gvdir_check()
            self.optread()
            self.readsaved()
            self.user = user
            self.dbhost = dbhost

    def gv_authq(self):
        """Show login frame."""
        self.w.lFr.setEnabled(1)
        self.w.lFr.show()
        self.w.logokPb.clicked.connect(self.gv_auth)
        self.w.logokPb.setDefault(1)
        self.keycheck.enter.connect(self.w.logokPb.click)
        
    def gv_exit(self):
        """Say goodbye, dignified, signal offspring to save unsaved changes."""
        if self.db and not isinstance(self.db, str):
            self.dbh.db_close()
        self.gvquit.emit(True)
        #print self.tr('Thank You for using GnuVet.')
        exit()

    def gv_help(self, help_doc='toc.html'):
        """Launch help window and display help_doc."""
        if hasattr(self, 'helpw'):
            self.helpw.show()
            self.helpw.raise_()
            self.helpw.show_help(help_doc)
        else:
            import gv_help
            self.helpw = gv_help.Help(self, help_doc)

    def gv_helpself(self):
        """Launch help window and display mainform.html"""
        if hasattr(self, 'helpw'):
            self.helpw.show()
            self.helpw.raise_()
            self.helpw.show_help('mainform.html')
        else:
            import gv_help
            self.helpw = gv_help.Help(self, 'mainform.html')

    def gv_quitconfirm(self):
        """Ask for confirmation to quit GnuVet."""
        self.w.menubar.setEnabled(0)
        self.w.gnuLb.hide()
        self.w.lFr.hide()
        self.w.lFr.setEnabled(0)
        self.w.no_dbconn.hide()
        self.w.qFr.setEnabled(1)
        self.w.qFr.show()
        for window in self.findChildren(QMainWindow):
            if window.isVisible():
                self.offspring.append(window)
        for window in self.offspring:
            window.hide()
        if not self.isVisible():
            self.show()

    def gv_quitno(self):
        """Oops, no, don't quit!"""
        self.gvquit.emit(False)
        self.w.qFr.setEnabled(0)
        self.w.qFr.hide()
        self.w.gnuLb.show()
        if not self.db or isinstance(self.db, str):
            self.w.no_dbconn.show()
        self.w.menubar.setEnabled(1)
        for window in self.offspring:
            window.show()
        self.offspring = []

    def name_newwin(self, name='w', cnt=None):
        """Return unique name for a new window."""
        if not cnt:
            cnt = ('maxwinnum' in self.options and
                   self.options['maxwinnum'] or 3)
        startname = name[:]
        for i in xrange(cnt):
            if not hasattr(self, name+str(i+1)):
                name = name + str(i+1)
                new = True
                break
            elif not getattr(self, name+str(i+1)).isVisible():
                name = name + str(i+1)
                new = False
                break
            ## else:
            ##     continue
        if name != startname:
            return (name, new)
        return (None, False)

    def openapp(self):
        """Open appointment diary."""
        if not self.today:
            self.today = date.today()
        if not hasattr(self, 'appointw'):
            from appoint import Appointer
            self.appointw = Appointer(self, self.today)
        else:
            self.appointw.raise_()
        self.appointw.show()
        
    def opencli(self, cid=0):
        """Launch Client window."""
        if not cnt:
            cnt = ('maxwinnum' in self.options and
                   self.options['maxwinnum'] or 3)
        if self.cwins == cnt:
            self.w.statusbar.showMessage(self.tr(
                'Open client windows maximum count reached.'), 10000)
            return
        errmsg = self.dbh.db_check(self.curs)
        if errmsg:
            self.db_state(errmsg)
            return
        wc = 'wc{}'.format(cid)
        if hasattr(self, wc):
            self.wc.show()
            self.wc.raise_()
            return
        else:
            import client
            self.wc = client.Client(self, cid)
            self.xy_incr(self.wc)
        self.cwins += 1
        self.wc.show()

    def openfin(self):
        """Finalysis "dialog"."""
        pass

    def openjou(self):
        """Journal "dialog"."""
        # journals are just summaries of monies per time
        pass

    def openord(self):
        """Order "dialog"."""
        pass

    def openpat(self, pid=0):
        """Launch Patient window -- ids signalled from saepat."""
        errmsg = self.dbh.db_check(self.curs)
        if errmsg:
            self.db_state(errmsg)
            return
        wp = 'wp{}'.format(pid)
        if hasattr(self, wp):
            self.wp.show()
            self.wp.raise_()
            return
        else:
            import patient
            self.wp = patient.Patient(self, pid)
            self.xy_incr(self.wp)
            self.wp.show()

    def opensys(self):
        """System "dialog"."""
        pass

    def optread(self):
        """Read (optional) options file for customised settings."""
        if not 'read_options' in locals():
            from options import read_options
        self.options.update(read_options(self.userdir, self.optfile))

    def optwrite(self):
        """Write customised settings to user file."""
        if not 'write_options' in locals():
            from options import write_options
        write_options(self.userdir, self.optfile, self.options)

    def readsaved(self):
        """Read optional savedstate file on startup."""
        # hierwei implement
        ## if os_path.exists(os_path.join(self.userdir, 'savestate')):
        pass

    def sae_cliwrap(self, trg=0): # triggered(checked=False)
        """Wrapper for action signal."""
        self.sae_cli()
        
    def sae_cli(self, cid=0, act='s'):
        """Open Search-Add-Edit Client window."""
        errmsg = self.dbh.db_check(self.curs)
        if errmsg:
            self.db_state(errmsg)
            return
        cp, new = self.name_newwin('saecliw')
        if not cp:
            self.w.statusbar.showMessage(self.tr(
                'Open client windows maximum count reached.'), 10000)
            return
        if new:
            if not 'Saecli' in locals():
                from saecli import Saecli
            setattr(self, cp, Saecli(self, act, cid))
            self.xy_incr(getattr(self, cp))
            getattr(self, cp).show()
        else:
            cp = getattr(self, cp)
            cp.reset()
            cp.show()
            cp.raise_()
            
    def sae_patwrap(self, trg=0): # triggered(checked=False)
        """Wrapper for action signal."""
        self.sae_pat()
        
    def sae_pat(self, cid=0, pid=0, act='s'):
        """Search-Add-Edit Patient window."""
        errmsg = self.dbh.db_check(self.curs)
        if errmsg:
            self.db_state(errmsg)
            return
        sp, new = self.name_newwin('saepatw')
        if not sp:
            self.w.statusbar.showMessage(self.tr(
                'Open patient windows maximum count reached.'), 10000)
            return
        if new:
            if not 'Saepat' in locals():
                from saepat import Saepat
            setattr(self, sp, Saepat(self, cid=cid, pid=pid, act=act))
            self.xy_incr(getattr(self, sp))
            getattr(self, sp).show()
        else:
            sp = getattr(self, sp)
            sp.reset()
            sp.show()
            sp.raise_()
            
    def sae_med(self):
        """Search-Add-Edit Medication window."""
        pass

    def sae_srv(self):
        """Search-Add-Edit Service window."""
        pass

    def sae_stk(self):
        """Search-Add-Edit Stock window."""
        pass
        
    def state_write(self, save_things=[]):
        """Write unsaved changes to file for later restoration."""
        # hierwei
        if not save_things:
            return
        if hasattr(self, 'warnw'):
            try:
                self.warnw.closed.disconnect(self.show)
            except TypeError:
                pass
        sstring = '\n'.join(save_things)
        if not 'os_path' in locals():
            from os import path as os_path
        sfile = os_path.join(self.userdir, 'savestate')
        try:
            with open(sfile, 'w') as f:
                f.write(sstring)
        except IOError:
            if not hasattr(self, 'warnw'):
                from warn import Warning
            self.warnw = Warning(self, self.tr('GnuVet: Warning'), 
                                 self.tr("Couldn't save unsaved Changes!"))
            self.warning.setWindowModality(2) # be top of w-tree, works???
            #self.warning.show()

    def xy_decr(self):
        """Adjust position for new child window -- after closing another one.
        Called from children's closeEvent."""
        if self.x_pos > 25: # was 114:
            self.x_pos -= 25
        if self.y_pos > 20: # was 69:
            self.y_pos -= 20

    def xy_incr(self, child):
        """Move child window and increase x and y for next window."""
        child.move(self.x_pos, self.y_pos)
        self.x_pos += 25
        self.y_pos += 20

    def vacc_reminders(self):
        """Prepare printing of vacc reminder letters."""
        if not 'timedelta' in locals():
            from datetime import timedelta
        vw = 'vaccwarn' in self.options and self.options['vaccwarn'] or 7
        vday = date.today() + timedelta(vw)
        res = querydb(
            self,
            'select vd_pid,vt_type from vdues,vtypes,patients where vt_id='
            'vd_type and vd_pid=p_id and not rip and vd_vdue<%s', (vday,))
        if res is None:  return # db error
        if not 'vaccremindw' in locals():
            pass # hierwei: show list (w/ client data for calls)|print letters
        if len(res):
            pass
        pats = []
        types = []
        for e in res:
            pats.append(e[0])
            types.append(e[1])
        # hierwei: dict?

# ==================================================

def main():
    shopts = 'hV'
    lopts  = ['help', 'version']
    from options import defaults as options
    lang = 'lang' in options and options['lang'] or 'en'
    try:
        opts, args = gnu_getopt(argv[1:], shopts, lopts)
    except GetoptError as err:
        print(str(err))
        print(gv_version.help[lang])
        exit(2)
    ex = False
    for o, p in opts:
        if o in ('-h', '--help'):
            print(gv_version.help[lang])
            ex = True
        if o in ('-V', '--version'):
            print(gv_version.version)
            print(gv_version.copyleft[lang].format('\n'))
            ex = True
    if ex:
        exit(2)
    mw = Gnuv_MainWin(options)
    exit(a.exec_())

if __name__ == '__main__':
    a = QApplication(argv)
    a.setStyle('plastique')
    main()
