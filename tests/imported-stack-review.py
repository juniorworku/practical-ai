"""Rehearse the published local service case as a student, using synthetic data only."""
import json,os,subprocess,sys,time,urllib.request,urllib.error,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CAPSTONE=os.environ.get('ACADEMY_CAPSTONE_REVIEW')=='1'
STACK=ROOT/('backend/academy/content/capstones/genai-accelerator' if CAPSTONE else 'backend/academy/content/accelerator_stack')
COMPOSE=['docker','compose','--project-name',('capstone-accelerator' if CAPSTONE else 'accelerator-student-stack'),'-f',str(STACK/'compose.yaml')]
def compose(*args,input=None):
    return subprocess.run([*COMPOSE,*args],input=input,capture_output=True,check=True).stdout

def request(path,body=None,token='demo-one'):
    data=json.dumps(body).encode() if body is not None else None
    req=urllib.request.Request(('http://127.0.0.1:8215' if CAPSTONE else 'http://127.0.0.1:8012')+path,data=data,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=5) as response:return response.status,json.load(response),dict(response.headers)
    except urllib.error.HTTPError as error:return error.code,json.load(error),dict(error.headers)

def wait_ready():
    for i in range(60):
        try:
            if request('/health')[0]==200:return
        except (OSError,ValueError):pass
        time.sleep(.2)
    raise AssertionError('API did not recover')

def clear_quota():compose('exec','-T','redis','redis-cli','DEL','lab:request-quota:one','lab:request-quota:two')

report={}
clear_quota()
result=subprocess.run([sys.executable,str(STACK/'check.py')],text=True,capture_output=True,check=True)
report['full_flow']=json.loads(result.stdout);saved=report['full_flow']['document_id']
print('PASS actual HTTP, worker transformation, PostgreSQL readback, scoped denial, dedupe and abstention',flush=True)
compose('stop','worker')
try:
    code,row,_=request('/documents',{'text':'Worker recovery fixture '+uuid.uuid4().hex+'. Refund window is 7 days.'})
    assert code==202;pending=row['id']
    assert request('/documents/'+pending)[1]['state']=='accepted'
    assert request('/ask',{'document_id':pending,'question':'refund'})[0]==409
finally:compose('start','worker')
for i in range(60):
    status=request('/documents/'+pending)[1]
    if status['state']=='ready':break
    time.sleep(.2)
else:raise AssertionError('pending work did not recover')
assert status['chunks'];report['worker_outage_recovery']=True
compose('up','-d','--force-recreate','api','worker');wait_ready()
assert request('/documents/'+saved)[1]['state']=='ready'
assert request('/documents/'+saved,token='demo-two')[0]==404
report['recreated_process_readback']=True
print('PASS worker outage: accepted is pending, not success; restart consumes queued work; recreation retains source ID',flush=True)
compose('stop','db')
try:
    code,body,_=request('/health');assert code==503 and body=={'detail':'database_unavailable'}
    code,body,_=request('/documents/'+saved);assert code==503 and body=={'detail':'database_unavailable'}
finally:compose('start','db')
wait_ready();assert request('/documents/'+saved)[1]['state']=='ready'
report['database_outage_recovery']=True
print('PASS database outage returns sanitized 503 and recovers without inventing an answer',flush=True)
# Actual PostgreSQL backup into an independently created database, then content comparison.
suffix=uuid.uuid4().hex[:10];restore='restore_review_'+suffix
backup=compose('exec','-T','db','pg_dump','-U','learner','-d','accelerator_lab','-Fc')
compose('exec','-T','db','createdb','-U','learner',restore)
compose('exec','-T','db','pg_restore','-U','learner','--no-owner','-d',restore,input=backup)
queries=['SELECT id,org,digest,state,text FROM documents ORDER BY id','SELECT document_id,position,text FROM chunks ORDER BY document_id,position']
for sql in queries:
    source=compose('exec','-T','db','psql','-U','learner','-d','accelerator_lab','-At','-v','ON_ERROR_STOP=1','-c',sql)
    restored=compose('exec','-T','db','psql','-U','learner','-d',restore,'-At','-v','ON_ERROR_STOP=1','-c',sql)
    assert source==restored and source.strip()
report['postgres_restore_ids_and_content']=True
# Start at the first migration, insert old data, apply second and read preserved content/default metadata.
migration='migration_review_'+suffix
compose('exec','-T','db','createdb','-U','learner',migration)
url='postgresql://learner:synthetic-local-only@db:5432/'+migration
compose('exec','-T','api','env','DATABASE_URL='+url,'alembic','upgrade','001')
compose('exec','-T','db','psql','-U','learner','-d',migration,'-v','ON_ERROR_STOP=1','-c',"INSERT INTO documents(id,org,digest,text,state) VALUES ('old','one','old-hash','14 days','ready')")
compose('exec','-T','api','env','DATABASE_URL='+url,'alembic','upgrade','head')
row=compose('exec','-T','db','psql','-U','learner','-d',migration,'-At','-c','SELECT id,text,parser_version FROM documents')
assert row.strip()==b'old|14 days|sentence-v1'
report['incremental_migration_preserved_old_row']=True
print('PASS real fresh restore matches IDs and content; incremental migration retains existing row',flush=True)
clear_quota()
for n in range(61):
    code,body,headers=request('/documents/no-such-document',token='demo-two')
    assert code==(404 if n<60 else 429),(n,code,body)
assert {k.lower():v for k,v in headers.items()}.get('retry-after')=='60'
report['shared_redis_quota_429']=True
clear_quota()
compose('stop','redis')
try:
    assert request('/documents/'+saved)[0]==503
finally:compose('start','redis')
for i in range(60):
    if request('/documents/'+saved)[0]==200:break
    time.sleep(.2)
else:raise AssertionError('quota dependency did not recover')
report['quota_dependency_fails_closed_then_recovers']=True
(ROOT/('docs/accelerator-capstone-operations.json' if CAPSTONE else 'docs/imported-stack-review.json')).write_text(json.dumps(report,indent=2))
print('PASS shared quota=60; request 61 denied with Retry-After; quota outage fails closed and recovers',flush=True)
