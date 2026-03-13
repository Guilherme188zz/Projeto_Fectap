"""dbmod2: Functions for connecting and live-checking the db."""
# Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
#
# This file is part of gnuvet, published under the GNU General Public License
# version 3 or later (GPLv3+ in short).  See the file LICENSE for information.

from psycopg2 import connect, OperationalError

class Db_handler:
    dbname = 'gnuvet'
    def __init__(self, user='enno', passwd=None, host=None, port=None):
        # production: user=None
        self.user = user
        self.passwd = passwd
        self.host = host
        self.port = port
        self.db = None

    def db_close(self):
        if self.db:
            if not self.db.closed:
                self.db.close()
            self.db = None

    def db_check(self, curs=None): # not obsolete!
        """Check if db is alive, return error string if not."""
        if not self.db:
            return 'no db connection'
        try:
            curs.execute('select 1')
            curs.fetchall()
        except OperationalError as e:
            self.db = None
            return (e or "Unspecified Db Error.")
        return
            
    def db_connect(self):
        """Connect to the db and return db handler."""
        if not self.db:
            args = {'database': self.dbname,
                    'user':     self.user}
            if self.passwd:
                    args['password'] = self.passwd
            if self.host:
                args['host'] = self.host
            if self.port:
                args['port'] = self.port
            try:
                self.db = connect(**args)
                cur = self.db.cursor()
                ## cur.execute("set NAMES 'LATIN1'") # this may be obsolete, as
                ## Qt's all Unicode?
                ## default seems to be LATIN9, is LATIN1 + "Euro" and accents
                ## or try UTF-8?
                ## cur.execute("set client_encoding='UTF-8'") # works 'upstream'
                #      but not down to Qt: Umlaut represented like in Eterm
                cur.execute("set client_encoding='LATIN9'") # seems 2 work well
            except OperationalError as e:
                return e.message
        return self.db
