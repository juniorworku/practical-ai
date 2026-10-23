import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

with tempfile.TemporaryDirectory() as folder:
    path=Path(folder)/'cache.sqlite3'
    # closing owns resource lifetime; the inner db context owns its transaction.
    with closing(sqlite3.connect(path)) as db:
        with db:
            db.execute('CREATE TABLE cache(owner TEXT, key TEXT, result TEXT, PRIMARY KEY(owner,key))')
            db.execute('INSERT INTO cache VALUES(?,?,?)',('a','v1','14 days'))
    with closing(sqlite3.connect(path)) as reopened:
        assert reopened.execute('SELECT result FROM cache WHERE owner=? AND key=?',('a','v1')).fetchone()==('14 days',)
        assert reopened.execute('SELECT result FROM cache WHERE owner=? AND key=?',('b','v1')).fetchone() is None
    print('Committed owner-bound result survived connection replacement')
