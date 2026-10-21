from contextlib import closing
import sqlite3,tempfile
from pathlib import Path
with tempfile.TemporaryDirectory() as folder:
    path=Path(folder)/'lab.db'
    with closing(sqlite3.connect(path)) as db, db:
        db.execute('CREATE TABLE docs(id TEXT PRIMARY KEY,org TEXT,text TEXT)')
        db.execute('INSERT INTO docs VALUES (?,?,?)',('a','one','14 days'))
    with closing(sqlite3.connect(path)) as db, db:
        def read(org): return db.execute('SELECT text FROM docs WHERE id=? AND org=?',('a',org)).fetchone()
        assert read('one')==('14 days',) and read('two') is None
print('new connection read committed data; other tenant denied')

# Bounded exercise variation
from contextlib import closing
# The complete variation creates its own disposable file and two connections.
with tempfile.TemporaryDirectory() as folder:
    path=Path(folder)/'reopen.db'
    with closing(sqlite3.connect(path)) as db, db: db.execute('CREATE TABLE result(value TEXT)');db.execute("INSERT INTO result VALUES ('observed')")
    with closing(sqlite3.connect(path)) as db, db: assert db.execute('SELECT count(*) FROM result').fetchone()[0]==1
print("Exercise variation: PASS")
