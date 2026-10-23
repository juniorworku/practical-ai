import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

with tempfile.TemporaryDirectory() as folder:
    live=Path(folder)/'live.sqlite3';snapshot=Path(folder)/'snapshot.sqlite3'
    with closing(sqlite3.connect(live)) as db:
        db.execute('CREATE TABLE cache(owner TEXT, key TEXT, value TEXT, PRIMARY KEY(owner,key))')
        with db:db.execute('INSERT INTO cache VALUES(?,?,?)',('a','v1','14 days'))
        with closing(sqlite3.connect(snapshot)) as target:db.backup(target)
        try:
            with db:
                db.execute('INSERT INTO cache VALUES(?,?,?)',('a','v2','uncommitted'))
                raise RuntimeError('abort transaction')
        except RuntimeError:pass
        assert db.execute('SELECT count(*) FROM cache').fetchone()==(1,)
    with closing(sqlite3.connect(snapshot)) as restored:
        assert restored.execute('SELECT value FROM cache WHERE owner=? AND key=?',('a','v1')).fetchone()==('14 days',)
        assert restored.execute('SELECT value FROM cache WHERE owner=? AND key=?',('b','v1')).fetchone() is None
    print('Consistent backup restored and scoped reads passed; failed transaction rolled back')
