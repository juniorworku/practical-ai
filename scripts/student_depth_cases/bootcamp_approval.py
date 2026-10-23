"""Transaction rollback and durable local approval, not remote exactly-once."""
from contextlib import closing
import sqlite3

def approve(db, owner, draft, reviewed_text, *, fail=False):
    # This single-connection teaching model does not implement concurrent locking.
    with db:
        row = db.execute('SELECT owner,text,state FROM drafts WHERE id=?', (draft,)).fetchone()
        if row is None or row[0] != owner:
            raise PermissionError('draft owner')
        if reviewed_text != row[1]:
            raise ValueError('stale review')
        if row[2] not in {'needs_review', 'approved'}:
            raise ValueError('draft not approvable')
        receipt = 'effect:' + draft
        db.execute('INSERT OR IGNORE INTO effects VALUES (?,?)', (receipt, row[1]))
        if fail:
            raise RuntimeError('failure before status update')
        db.execute('UPDATE drafts SET state=? WHERE id=?', ('approved', draft))
    return receipt

with closing(sqlite3.connect(':memory:')) as db:
    db.executescript('CREATE TABLE drafts(id TEXT PRIMARY KEY,owner TEXT,text TEXT,state TEXT);'
                     'CREATE TABLE effects(id TEXT PRIMARY KEY,text TEXT);')
    db.execute('INSERT INTO drafts VALUES (?,?,?,?)', ('d1', 'one', '14 days, unopened only', 'needs_review'))
    db.commit()  # Persist the setup separately from the transaction being tested.
    try:
        approve(db, 'one', 'd1', '14 days, unopened only', fail=True)
    except RuntimeError:
        pass
    assert db.execute('SELECT count(*) FROM effects').fetchone()[0] == 0
    assert db.execute('SELECT state FROM drafts').fetchone()[0] == 'needs_review'
    first = approve(db, 'one', 'd1', '14 days, unopened only')
    assert approve(db, 'one', 'd1', '14 days, unopened only') == first
    assert db.execute('SELECT count(*) FROM effects').fetchone()[0] == 1
print('rollback: no effect; retry and replay: one local receipt')
