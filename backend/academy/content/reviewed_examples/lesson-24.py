from contextlib import closing
import sqlite3
with closing(sqlite3.connect(':memory:')) as db, db:
    db.execute('CREATE TABLE documents(id TEXT PRIMARY KEY)')
    db.execute("INSERT INTO documents VALUES ('a')")
    db.execute("ALTER TABLE documents ADD COLUMN state TEXT NOT NULL DEFAULT 'accepted'")
    db.execute('PRAGMA user_version=1')
    row=db.execute('SELECT id,state FROM documents').fetchone()
    version=db.execute('PRAGMA user_version').fetchone()[0]
    assert row==('a','accepted') and version==1
print('old row preserved; additive schema version=1')

# Bounded exercise variation
assert row[1]!='ready'
print("Exercise variation: PASS")
