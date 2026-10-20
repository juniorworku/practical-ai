"""Durable local state machine with exact review and a fake effect destination.
python workspace_state.py; no real Slack/email/calendar calls occur.
"""
import hashlib,json,sqlite3,tempfile
from pathlib import Path

def digest(payload):return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def setup(db):
    db.executescript('''CREATE TABLE IF NOT EXISTS inbox(owner TEXT,event_id TEXT,payload TEXT,PRIMARY KEY(owner,event_id));
    CREATE TABLE IF NOT EXISTS proposals(id TEXT PRIMARY KEY,owner TEXT,payload TEXT,hash TEXT,approved_hash TEXT,state TEXT);
    CREATE TABLE IF NOT EXISTS effects(owner TEXT,operation TEXT,payload TEXT,PRIMARY KEY(owner,operation));''')

def receive(db,owner,event_id,payload):
    encoded=json.dumps(payload,sort_keys=True)
    with db:
        prior=db.execute('SELECT payload FROM inbox WHERE owner=? AND event_id=?',(owner,event_id)).fetchone()
        if prior:return 'duplicate' if prior[0]==encoded else 'content_conflict'
        db.execute('INSERT INTO inbox VALUES(?,?,?)',(owner,event_id,encoded))
    return 'accepted'

def propose(db,identifier,owner,payload):
    with db:db.execute('INSERT INTO proposals VALUES(?,?,?,?,?,?)',(identifier,owner,json.dumps(payload),digest(payload),None,'needs_review'))

def approve(db,identifier,owner,reviewed_digest,authorized):
    if not authorized:return False
    with db:
        changed=db.execute("UPDATE proposals SET approved_hash=?,state='approved' WHERE id=? AND owner=? AND hash=? AND state='needs_review'",(reviewed_digest,identifier,owner,reviewed_digest)).rowcount
    return changed==1

def execute_fake(db,identifier,owner):
    # Fake destination shares this DB, so the transaction can be atomic here.
    # A real remote side effect needs a separate durable outbox and reconciliation.
    with db:
        row=db.execute("SELECT payload,hash,approved_hash,state FROM proposals WHERE id=? AND owner=?",(identifier,owner)).fetchone()
        if not row:return 'inaccessible'
        payload,actual,approved,state=row
        if state=='committed':return 'already_committed'
        if state!='approved' or actual!=approved:return 'needs_review'
        db.execute('INSERT INTO effects VALUES(?,?,?)',(owner,identifier,payload))
        db.execute("UPDATE proposals SET state='committed' WHERE id=? AND owner=?",(identifier,owner))
    return 'committed'

if __name__=='__main__':
    with tempfile.TemporaryDirectory() as folder:
        path=Path(folder)/'workspace.sqlite';db=sqlite3.connect(path);setup(db)
        event={'channel':'synthetic-support','question':'Returns?'}
        assert receive(db,'acme','e1',event)=='accepted'
        assert receive(db,'acme','e1',event)=='duplicate'
        payload={'destination':'fake-calendar','start':'2026-11-03T10:00:00+03:00','revision':1}
        propose(db,'p1','acme',payload)
        assert execute_fake(db,'p1','acme')=='needs_review'
        assert not approve(db,'p1','other',digest(payload),True)
        assert approve(db,'p1','acme',digest(payload),True)
        db.close();db=sqlite3.connect(path)
        assert execute_fake(db,'p1','other')=='inaccessible'
        assert execute_fake(db,'p1','acme')=='committed'
        assert execute_fake(db,'p1','acme')=='already_committed'
        assert db.execute('SELECT count(*) FROM effects').fetchone()[0]==1
        db.close()
    print('durable inbox, scoped approval, restart/resume and one fake calendar effect passed')
