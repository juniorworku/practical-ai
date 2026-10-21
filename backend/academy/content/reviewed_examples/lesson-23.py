from contextlib import closing
import sqlite3
with closing(sqlite3.connect(':memory:')) as db, db:
    db.execute('CREATE TABLE documents(id TEXT PRIMARY KEY, org TEXT NOT NULL, digest TEXT NOT NULL, UNIQUE(org,digest))')
    db.execute('INSERT INTO documents VALUES (?,?,?)',('a','one','hash1'))
    try: db.execute('INSERT INTO documents VALUES (?,?,?)',('b','one','hash1'))
    except sqlite3.IntegrityError: pass
    else: raise AssertionError('duplicate accepted')
    db.execute('INSERT INTO documents VALUES (?,?,?)',('c','two','hash1'))
    count=db.execute('SELECT count(*) FROM documents').fetchone()[0]
    assert count==2
print('database uniqueness enforced; same content in separate tenants allowed')

# Bounded exercise variation
assert count==2
print("Exercise variation: PASS")
