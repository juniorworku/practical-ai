from contextlib import closing
import sqlite3
with closing(sqlite3.connect(':memory:')) as db, db:
    db.executescript('CREATE TABLE docs(id TEXT PRIMARY KEY); CREATE TABLE chunks(doc TEXT,text TEXT);')
    def ingest(key,fail=False):
        with db:
            inserted=db.execute('INSERT OR IGNORE INTO docs VALUES (?)',(key,)).rowcount
            if inserted:
                if fail: raise RuntimeError('fixture failure')
                db.execute('INSERT INTO chunks VALUES (?,?)',(key,'14 days'))
    ingest('a');ingest('a')
    try: ingest('b',True)
    except RuntimeError: pass
    counts=(db.execute('SELECT count(*) FROM docs').fetchone()[0],db.execute('SELECT count(*) FROM chunks').fetchone()[0])
    assert counts==(1,1)
print('retry did not duplicate; partial ingestion rolled back')

# Bounded exercise variation
from contextlib import closing
with closing(sqlite3.connect(':memory:')) as retry_db, retry_db:
    retry_db.executescript('CREATE TABLE docs(id TEXT PRIMARY KEY); CREATE TABLE chunks(doc TEXT UNIQUE,text TEXT);')
    def retry_ingest(key,fail=False):
        with retry_db:
            inserted=retry_db.execute('INSERT OR IGNORE INTO docs VALUES (?)',(key,)).rowcount
            if inserted:
                if fail: raise RuntimeError('before chunk write')
                retry_db.execute('INSERT INTO chunks VALUES (?,?)',(key,'14 days'))
    try: retry_ingest('a',True)
    except RuntimeError: pass
    assert retry_db.execute('SELECT count(*) FROM docs').fetchone()[0]==0
    retry_ingest('a');retry_ingest('a')
    assert retry_db.execute('SELECT count(*) FROM docs').fetchone()[0]==1
    assert retry_db.execute('SELECT count(*) FROM chunks').fetchone()[0]==1
print("Exercise variation: PASS")
