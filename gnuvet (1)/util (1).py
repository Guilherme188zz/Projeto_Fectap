"""Common utility functions."""
from psycopg2 import OperationalError
from PyQt4.QtGui import QAction

def ch_conn(caller=None, name='', sig=None, func=None):
    """Disconnect function conns[name] from signal sigs[name],
    if args provided make new connection, adapt dict.
    pyqt Bug: disconnect() w/o arg segfaults."""
    if name in caller.conns:
        try:
            caller.sigs[name].disconnect(caller.conns[name])
        except (TypeError, AttributeError) as e:
            print('disconn failed for "{}" sig {} func {}:\n{}'.format(
                name, sig, caller.conns[name], e))
            pass
        del caller.conns[name]
        del caller.sigs[name]
    if func:
        sig.connect(func)
        caller.conns[name] = func
        caller.sigs[name] = sig
    
def gprice(nprice=0, vatrate=0):
    if not 'Decimal' in locals():
        from decimal import Decimal
    return (nprice * (vatrate+1)).quantize(Decimal('0.00'))

def money(val, mult=1):
    if not 'Decimal' in locals():
        from decimal import Decimal
    val = val * mult
    return (Decimal(str(val)).quantize(Decimal('0.00')))

def newaction(caller=None, txt='', stip=None, short=None, icon=None):
    if icon:
        if not 'QIcon' in locals():
            from PyQt4.QtGui import QIcon
        action = QAction(QIcon(icon), caller.tr(txt), caller)
    else:
        action = QAction(caller.tr(txt), caller)
    action.setAutoRepeat(False)
    if stip:
        action.setStatusTip(caller.tr(stip))
    if short:
        action.setShortcut(caller.tr(short))
    return action

def percent(val):
    if int(val) == val:
        if not 'Decimal' in locals():
            from decimal import Decimal
        return Decimal(str(int(val)))
    else:
        return val.normalize()
    
def prep_txt(entry='', escape=False):
    """Prepare entry for sql query, quote 'dangerous' chars.
    escape=True for select, False for insert."""
    seps = ['\\', "'"]
    if escape:
        seps.extend(['%', '_'])
    entry=str(entry)
    for sep in seps:
        if escape and sep == '\\':
            entry = entry.replace(sep, '\\\\\\\\')
        else:
            entry = entry.replace(sep, '\\{}'.format(sep))
    return ' '.join(entry.split())

def querydb(caller, query, qtuple=None, debug=False):
    try:
        if qtuple:
            if debug:
                print(caller.curs.mogrify(query, qtuple))
            caller.curs.execute(query, qtuple)
        else:
            if debug:
                print(caller.curs.mogrify(query))
            caller.curs.execute(query)
        return caller.curs.fetchall()
    except OperationalError as e:
        caller.db_state(e)

def sysinfo():
    """Return sys-dependent syspath userpath and options_filename."""
    # needs some work i guess, for user paths on win32
    if not 'sys_platform' in locals():
        from sys import platform as sys_platform
    if sys_platform.startswith('linux'):
        syspath = '/usr/share/gnuvet'
        userdir = '.gnuvet'
        optfile = '.options'
        system  = 'linux'
    elif sys_platform.startswith('win32'):
        syspath = '/Program Files/gnuvet'
        userdir = 'gnuvet'
        optfile = 'options'
        system  = 'win32'
    else:
        syspath = 'Not implemented: {}'.format(sys_platform)
        userdir = ''
        optfile = ''
        system  = 'not supported'
    return syspath, userdir, optfile, system

def wildcard(entry='', ahead=False):
    """Add sql wildcards, replace *."""
    if not entry or entry == '*':
        return '%'
    while entry.count('**'):
        entry = entry.replace('**', '*')
    while entry.count('*'):
        entry = entry.replace('*', '%')
    if ahead:
        if not entry.startswith('%'):
            entry = '%' + entry
    if not entry.endswith('%'):
        entry += '%'
    return entry
