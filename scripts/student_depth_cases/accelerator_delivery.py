"""Commit before enqueue: recover an accepted row without inventing readiness."""
from contextlib import closing
import sqlite3

def accept(db, key, text, enqueue):
    with db:
        existing = db.execute('SELECT text FROM jobs WHERE id=?', (key,)).fetchone()
        if existing is not None and existing[0] != text:
            raise ValueError('identity reused with changed content')
        db.execute('INSERT OR IGNORE INTO jobs VALUES (?,?,?)', (key, text, 'accepted'))
    # A broker call cannot be rolled back by this database transaction.
    try:
        enqueue(key)
    except OSError:
        return {'id': key, 'state': 'accepted', 'delivery': 'retry_required'}
    return {'id': key, 'state': 'accepted', 'delivery': 'queued'}

def consume(db, key):
    with db:
        row = db.execute('SELECT text,state FROM jobs WHERE id=?', (key,)).fetchone()
        if row is None:
            raise ValueError('unknown job')
        if row[1] == 'ready':
            return
        db.execute('INSERT INTO chunks VALUES (?,?)', (key, row[0].upper()))
        db.execute('UPDATE jobs SET state=? WHERE id=?', ('ready', key))

with closing(sqlite3.connect(':memory:')) as db:
    db.executescript('CREATE TABLE jobs(id TEXT PRIMARY KEY,text TEXT,state TEXT);'
                     'CREATE TABLE chunks(job TEXT UNIQUE,text TEXT);')
    def offline(key):
        raise OSError('synthetic broker outage')
    observed = accept(db, 'd1', 'unused items only', offline)
    assert observed['delivery'] == 'retry_required'
    assert db.execute('SELECT state FROM jobs').fetchone()[0] == 'accepted'
    queue = []
    assert accept(db, 'd1', 'unused items only', queue.append)['delivery'] == 'queued'
    assert queue == ['d1']
    consume(db, queue.pop());consume(db, 'd1')
    assert db.execute('SELECT count(*) FROM chunks').fetchone()[0] == 1
    assert db.execute('SELECT state FROM jobs').fetchone()[0] == 'ready'
print('broker failure retained accepted row; requeue and duplicate delivery produced one chunk')
