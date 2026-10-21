from contextlib import closing
import sqlite3
with closing(sqlite3.connect(':memory:')) as db, db:
    db.executescript("CREATE TABLE jobs(id TEXT PRIMARY KEY,state TEXT,text TEXT); CREATE TABLE chunks(job TEXT UNIQUE,text TEXT); INSERT INTO jobs VALUES ('a','accepted','refund');")
    def worker(id):
        with db:
            state,text=db.execute('SELECT state,text FROM jobs WHERE id=?',(id,)).fetchone()
            if state=='ready': return
            db.execute('INSERT INTO chunks VALUES (?,?)',(id,text.upper()))
            db.execute("UPDATE jobs SET state='ready' WHERE id=?",(id,))
    assert db.execute('SELECT state FROM jobs').fetchone()[0]=='accepted'
    worker('a');worker('a')
    assert db.execute('SELECT state FROM jobs').fetchone()[0]=='ready'
    assert db.execute('SELECT text FROM chunks').fetchall()==[('REFUND',)]
print('worker performed persisted transition; replay produced one chunk')

# Bounded exercise variation
from contextlib import closing
with closing(sqlite3.connect(':memory:')) as variation_db, variation_db:
    variation_db.execute('CREATE TABLE job(id TEXT PRIMARY KEY,state TEXT,chunk TEXT)')
    variation_db.execute("INSERT INTO job VALUES ('b','accepted',NULL)")
    with variation_db:
        variation_db.execute('UPDATE job SET state=?,chunk=? WHERE id=?',('ready','UNUSED ONLY','b'))
    assert variation_db.execute('SELECT state,chunk FROM job').fetchone()==('ready','UNUSED ONLY')
print("Exercise variation: PASS")
