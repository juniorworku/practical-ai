"""Synthetic local teaching API. Two fixed demo identities, not production authentication."""
import hashlib,json,os,uuid
import psycopg
import redis
from fastapi import FastAPI,Depends,Header,HTTPException
from pydantic import BaseModel,ConfigDict,Field,field_validator
from fastapi.responses import JSONResponse
from kombu.exceptions import OperationalError as BrokerError
from database import connect
from tasks import ingest
app=FastAPI(title='Accelerator persistence and worker lab')
@app.exception_handler(psycopg.Error)
def database_error(request,error):
    return JSONResponse(status_code=503,content={'detail':'database_unavailable'})
# Deliberate fixture credentials. A real system must validate sessions and enforce shared quotas.
DEMO_IDENTITIES={'demo-one':'one','demo-two':'two'}
quota_store=redis.Redis.from_url(os.environ['BROKER_URL'],socket_timeout=2,socket_connect_timeout=2)
QUOTA_SCRIPT="""local n=redis.call('INCR',KEYS[1]); if n==1 then redis.call('EXPIRE',KEYS[1],60) end; return n"""
def quota(org):
    try: count=quota_store.eval(QUOTA_SCRIPT,1,'lab:request-quota:'+org)
    except redis.RedisError: raise HTTPException(503,detail='quota_store_unavailable') from None
    if count>60: raise HTTPException(429,detail='request_quota_exceeded',headers={'Retry-After':'60'})
def identity(authorization:str|None=Header(default=None)):
    org=DEMO_IDENTITIES.get((authorization or '').removeprefix('Bearer '))
    if not org: raise HTTPException(401,detail='demo_identity_required')
    quota(org)
    return org
class Upload(BaseModel):
    model_config=ConfigDict(extra='forbid')
    text:str=Field(min_length=1,max_length=10000)
class Question(BaseModel):
    model_config=ConfigDict(extra='forbid')
    document_id:str=Field(min_length=1,max_length=36)
    question:str=Field(min_length=3,max_length=200)
    @field_validator('question')
    @classmethod
    def nonblank_question(cls,value):
        value=value.strip()
        if len(value)<3: raise ValueError('question must contain at least three non-padding characters')
        return value

def enqueue(id):
    try:
        ingest.apply_async(args=[id],retry=False)
    except (BrokerError,OSError):
        # The committed accepted row remains visible and can be explicitly requeued.
        raise HTTPException(503,detail={'code':'queue_unavailable','document_id':id}) from None

@app.get('/health')
def health():
    try:
        with connect() as db: db.execute('SELECT 1')
        return {'ready':True,'database':'postgresql'}
    except psycopg.Error: raise HTTPException(503,detail='database_unavailable') from None

@app.post('/documents',status_code=202)
def upload(body:Upload,org:str=Depends(identity)):
    if not body.text.strip(): raise HTTPException(422,detail='blank_document')
    digest=hashlib.sha256(body.text.encode()).hexdigest()
    with connect() as db:
        row=db.execute('''INSERT INTO documents(id,org,digest,text,state) VALUES (%s,%s,%s,%s,'accepted')
            ON CONFLICT (org,digest) DO UPDATE SET digest=EXCLUDED.digest RETURNING id,state''',
            [str(uuid.uuid4()),org,digest,body.text]).fetchone()
    if row['state']!='ready': enqueue(row['id'])
    return {'id':row['id'],'state':row['state']}

@app.get('/documents/{id}')
def status(id:str,org:str=Depends(identity)):
    with connect() as db:
        row=db.execute('SELECT id,state FROM documents WHERE id=%s AND org=%s',[id,org]).fetchone()
        if not row: raise HTTPException(404,detail='not_found')
        row['chunks']=db.execute('SELECT position,text FROM chunks WHERE document_id=%s ORDER BY position',[id]).fetchall()
        return row

@app.post('/documents/{id}/retry',status_code=202)
def retry(id:str,org:str=Depends(identity)):
    with connect() as db:
        row=db.execute('SELECT state FROM documents WHERE id=%s AND org=%s',[id,org]).fetchone()
        if not row: raise HTTPException(404,detail='not_found')
    enqueue(id);return {'id':id,'state':row['state']}

@app.post('/ask')
def ask(body:Question,org:str=Depends(identity)):
    # Authorization and ready-state checks happen before chunks enter context.
    with connect() as db:
        row=db.execute('SELECT state FROM documents WHERE id=%s AND org=%s',[body.document_id,org]).fetchone()
        if not row: raise HTTPException(404,detail='not_found')
        if row['state']!='ready': raise HTTPException(409,detail='document_not_ready')
        chunks=db.execute('SELECT position,text FROM chunks WHERE document_id=%s ORDER BY position',[body.document_id]).fetchall()
    terms=set(body.question.lower().split());selected=[];used=0
    for chunk in chunks:
        if not terms & set(chunk['text'].lower().split()): continue
        if used+len(chunk['text'])>1000: continue
        selected.append(chunk);used+=len(chunk['text'])
    return {'mode':'lexical_fixture','answer':' '.join(c['text'] for c in selected) or None,
            'citations':[f'{body.document_id}:{c["position"]}' for c in selected],
            'context_chars':used,'usage_tokens':None}
