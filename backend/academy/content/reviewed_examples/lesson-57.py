import sqlite3
source=sqlite3.connect(':memory:');restored=sqlite3.connect(':memory:')
try:
    source.execute('CREATE TABLE policies(id TEXT PRIMARY KEY,text TEXT)')
    source.execute("INSERT INTO policies VALUES ('p1','14 days')");source.commit()
    source.backup(restored)
    assert restored.execute('SELECT text FROM policies').fetchone()[0]=='14 days'
    source.execute("UPDATE policies SET text='7 days'");source.commit()
    assert restored.execute('SELECT text FROM policies').fetchone()[0]=='14 days'
finally: source.close();restored.close()
print('fresh database restored and queried; source edits do not mutate backup')

# Bounded exercise variation
source=sqlite3.connect(':memory:');restored=sqlite3.connect(':memory:')
try:
    source.execute('CREATE TABLE policy(id TEXT PRIMARY KEY,text TEXT)')
    source.executemany('INSERT INTO policy VALUES (?,?)',[('v1','14 days'),('v2','7 days')]);source.commit()
    source.backup(restored)
    expected=[('v1','14 days'),('v2','7 days')]
    assert restored.execute('SELECT id,text FROM policy ORDER BY id').fetchall()==expected
finally: source.close();restored.close()
print("Exercise variation: PASS")
